from pathlib import Path
import argparse
import unicodedata

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = BASE_DIR / "emojis"
DEFAULT_FONT = Path("/System/Library/Fonts/Apple Color Emoji.ttc")
DEFAULT_FONT_SIZE = 160
DEFAULT_TARGET_SIZE = 96
DEFAULT_PADDING = 16

ZWJ = "\u200d"
VS16 = "\ufe0f"
KEYCAP = "\u20e3"
SKIN_TONE_RANGE = range(0x1F3FB, 0x1F400)
REGIONAL_RANGE = range(0x1F1E6, 0x1F200)


def split_graphemes(text):
    clusters = []
    current = ""
    regional_count = 0

    for char in text:
        codepoint = ord(char)

        if not current:
            current = char
            regional_count = 1 if codepoint in REGIONAL_RANGE else 0
            continue

        append_to_current = False
        previous = current[-1]

        if previous == ZWJ or char == ZWJ:
            append_to_current = True
        elif unicodedata.combining(char):
            append_to_current = True
        elif codepoint in SKIN_TONE_RANGE:
            append_to_current = True
        elif char == VS16 or char == KEYCAP:
            append_to_current = True
        elif codepoint in REGIONAL_RANGE and regional_count == 1:
            append_to_current = True

        if append_to_current:
            current += char
            if codepoint in REGIONAL_RANGE:
                regional_count += 1
            else:
                regional_count = 0
            continue

        clusters.append(current)
        current = char
        regional_count = 1 if codepoint in REGIONAL_RANGE else 0

    if current:
        clusters.append(current)

    return clusters


def cluster_to_codepoints(cluster):
    codepoints = []
    for char in cluster:
        codepoint = ord(char)
        if codepoint == 0xFE0E:
            continue
        codepoints.append("{:x}".format(codepoint))
    return "-".join(codepoints)


def render_emoji(cluster, font, target_size, padding):
    canvas_size = font.size + padding * 2
    image = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.text((padding, padding), cluster, font=font, embedded_color=True)

    bbox = image.getbbox()
    if bbox is None:
        raise ValueError("Could not render emoji: {}".format(cluster))

    cropped = image.crop(bbox)
    return cropped.resize((target_size, target_size), Image.Resampling.LANCZOS)


def create_emojis(text, output_dir, font_path, font_size, target_size, padding, overwrite):
    output_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype(str(font_path), font_size)

    created = []
    skipped = []

    for cluster in split_graphemes(text):
        codepoints = cluster_to_codepoints(cluster)
        output_path = output_dir / "{}.png".format(codepoints)

        if output_path.exists() and not overwrite:
            skipped.append((cluster, output_path))
            continue

        emoji = render_emoji(cluster, font, target_size, padding)
        emoji.save(output_path)
        created.append((cluster, output_path))

    return created, skipped


def main():
    parser = argparse.ArgumentParser(description="Create local emoji PNG files from unicode emoji on a Mac.")
    parser.add_argument("text", help='Example: "🥸🥳🕵🏻"')
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory where emoji PNG files are written")
    parser.add_argument("--font", default=str(DEFAULT_FONT), help="Color emoji font file to use")
    parser.add_argument("--font-size", type=int, default=DEFAULT_FONT_SIZE, help="Font size used during rendering")
    parser.add_argument("--target-size", type=int, default=DEFAULT_TARGET_SIZE, help="Final PNG size in pixels")
    parser.add_argument("--padding", type=int, default=DEFAULT_PADDING, help="Transparent padding before cropping")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing emoji PNG files")
    args = parser.parse_args()

    font_path = Path(args.font)
    if not font_path.exists():
        raise SystemExit("Emoji font not found: {}".format(font_path))

    created, skipped = create_emojis(
        text=args.text,
        output_dir=Path(args.output_dir),
        font_path=font_path,
        font_size=args.font_size,
        target_size=args.target_size,
        padding=args.padding,
        overwrite=args.overwrite,
    )

    for emoji, path in created:
        print("created  {}  {}".format(emoji, path))

    for emoji, path in skipped:
        print("skipped  {}  {}".format(emoji, path))


if __name__ == "__main__":
    main()
