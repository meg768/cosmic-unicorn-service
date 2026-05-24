#!/usr/bin/env python3
from pathlib import Path
import argparse
import struct

from PIL import Image, ImageSequence


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT_DIR = BASE_DIR / "gifs"
DEFAULT_OUTPUT_DIR = BASE_DIR / "cufs"


def rgb_to_565(red, green, blue):
    return ((red & 0xF8) << 8) | ((green & 0xFC) << 3) | (blue >> 3)


def convert_gif(input_path, output_path):
    image = Image.open(input_path)
    width, height = image.size
    frames = []
    durations = []

    for frame in ImageSequence.Iterator(image):
        rgba = frame.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
        background.alpha_composite(rgba)
        rgb = background.convert("RGB")
        frames.append(rgb)
        durations.append(frame.info.get("duration", image.info.get("duration", 60)) or 60)

    if not frames:
        raise ValueError("GIF contains no frames: {}".format(input_path))

    delay_ms = round(sum(durations) / len(durations))

    palette_source = Image.new("RGB", (width, height * len(frames)))
    for index, frame in enumerate(frames):
        palette_source.paste(frame, (0, index * height))

    paletted_source = palette_source.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    palette_bytes = paletted_source.getpalette()[: 256 * 3]
    palette = []
    for index in range(0, len(palette_bytes), 3):
        palette.append(tuple(palette_bytes[index : index + 3]))

    paletted_frames = []
    for frame in frames:
        paletted_frames.append(frame.quantize(palette=paletted_source))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(".new.cuf")

    with open(temp_path, "wb") as target:
        target.write(b"CUF3")
        target.write(struct.pack("<HHHHH", width, height, len(frames), delay_ms, len(palette)))

        for red, green, blue in palette:
            target.write(struct.pack("<H", rgb_to_565(red, green, blue)))

        for frame in paletted_frames:
            indexes = frame.tobytes()
            encoded = bytearray()
            run_value = indexes[0]
            run_length = 1

            for value in indexes[1:]:
                if value == run_value and run_length < 255:
                    run_length += 1
                else:
                    encoded.append(run_length)
                    encoded.append(run_value)
                    run_value = value
                    run_length = 1

            encoded.append(run_length)
            encoded.append(run_value)
            target.write(struct.pack("<H", len(encoded)))
            target.write(encoded)

    temp_path.replace(output_path)
    return width, height, len(frames), delay_ms


def generate_cufs(input_dir, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)

    for cuf_path in output_dir.glob("*.cuf"):
        cuf_path.unlink()

    gif_paths = sorted(input_dir.glob("*.gif"))
    if not gif_paths:
        raise ValueError("No GIF files found in {}".format(input_dir))

    for gif_path in gif_paths:
        cuf_path = output_dir / (gif_path.stem + ".cuf")
        width, height, frame_count, delay_ms = convert_gif(gif_path, cuf_path)
        print("{}: {}x{}, {} frames, {} ms/frame".format(cuf_path, width, height, frame_count, delay_ms))


def main():
    parser = argparse.ArgumentParser(description="Generate CUF animation files from GIF files.")
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR), help="Directory containing source GIF files")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory where CUF files are written")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    if not input_dir.exists():
        raise SystemExit("Input directory does not exist: {}".format(input_dir))

    generate_cufs(input_dir, output_dir)


if __name__ == "__main__":
    main()
