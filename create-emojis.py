from pathlib import Path
import argparse
import unicodedata

from PIL import Image, ImageDraw, ImageFont
from emojis import EMOJIS


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = BASE_DIR / "emojis"
DEFAULT_FONT = Path("/System/Library/Fonts/Apple Color Emoji.ttc")
DEFAULT_FONT_SIZE = 256
DEFAULT_TARGET_SIZE = 160
DEFAULT_PADDING = 0

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


def load_font_exact(font_path, font_size):
    try:
        return ImageFont.truetype(str(font_path), font_size)
    except OSError:
        return None


def measure_emoji(cluster, font):
    probe = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(probe)
    bbox = draw.textbbox((0, 0), cluster, font=font, embedded_color=True)
    if bbox is None:
        raise ValueError("Could not render emoji: {}".format(cluster))
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    if width <= 0 or height <= 0:
        raise ValueError("Could not render emoji: {}".format(cluster))
    return bbox, width, height


def fit_font(cluster, font_path, max_font_size, inner_size, font_cache):
    for size in range(max_font_size, 0, -1):
        if size not in font_cache:
            font_cache[size] = load_font_exact(font_path, size)

        font = font_cache[size]
        if font is None:
            continue

        bbox, width, height = measure_emoji(cluster, font)
        if width <= inner_size and height <= inner_size:
            return font, bbox, width, height

    raise ValueError("Could not fit emoji: {}".format(cluster))


def render_emoji(cluster, font_path, max_font_size, target_size, padding, font_cache):
    image = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    inner_size = target_size - padding * 2
    if inner_size <= 0:
        raise ValueError("Padding too large for target size")

    font, bbox, width, height = fit_font(cluster, font_path, max_font_size, inner_size, font_cache)
    offset_x = round((target_size - width) / 2 - bbox[0])
    offset_y = round((target_size - height) / 2 - bbox[1])
    draw.text((offset_x, offset_y), cluster, font=font, embedded_color=True)
    return image


def create_emojis(text, output_dir, font_path, font_size, target_size, padding):
    output_dir.mkdir(parents=True, exist_ok=True)
    font_cache = {}
    created = []
    skipped = []

    for cluster in split_graphemes(text):
        codepoints = cluster_to_codepoints(cluster)
        output_path = output_dir / "{}.png".format(codepoints)

        try:
            emoji = render_emoji(cluster, font_path, font_size, target_size, padding, font_cache)
        except ValueError:
            skipped.append((cluster, output_path))
            continue

        emoji.save(output_path)
        created.append((cluster, output_path))

    return created, skipped


def main():
    parser = argparse.ArgumentParser(description="Create local emoji PNG files from emojis.py on a Mac.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory where emoji PNG files are written")
    parser.add_argument("--font", default=str(DEFAULT_FONT), help="Color emoji font file to use")
    parser.add_argument("--font-size", type=int, default=DEFAULT_FONT_SIZE, help="Maximum Apple emoji font size to try during fitting")
    parser.add_argument("--target-size", type=int, default=DEFAULT_TARGET_SIZE, help="Final PNG size in pixels")
    parser.add_argument("--padding", type=int, default=DEFAULT_PADDING, help="Transparent padding to keep around the fitted emoji")
    args = parser.parse_args()

    font_path = Path(args.font)
    if not font_path.exists():
        raise SystemExit("Emoji font not found: {}".format(font_path))

    created, skipped = create_emojis(
        text=EMOJIS,
        output_dir=Path(args.output_dir),
        font_path=font_path,
        font_size=args.font_size,
        target_size=args.target_size,
        padding=args.padding,
    )

    for emoji, path in created:
        print("created  {}  {}".format(emoji, path))

    for emoji, path in skipped:
        print("skipped  {}  {}".format(emoji, path))


if __name__ == "__main__":
    main()
