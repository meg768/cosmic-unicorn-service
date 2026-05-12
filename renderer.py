from pathlib import Path
import unicodedata

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parent
FONT_PATH = BASE_DIR / "fonts" / "Arial-Bold.ttf"
EMOJI_DIR = BASE_DIR / "emojis"

DEFAULT_TEXT = "Ticker"
DEFAULT_HEIGHT = 32
DEFAULT_WIDTH = None
DEFAULT_TEXT_COLOR = (255, 0, 0)
DEFAULT_BACKGROUND = (0, 0, 0)
DEFAULT_PADDING_RATIO = 0.375
DEFAULT_GAP_RATIO = 0.1
DEFAULT_FONT_RATIO = 0.75
DEFAULT_EMOJI_RATIO = 0.95

ZWJ = "\u200d"
VS16 = "\ufe0f"
KEYCAP = "\u20e3"
SKIN_TONE_RANGE = range(0x1F3FB, 0x1F400)
REGIONAL_RANGE = range(0x1F1E6, 0x1F200)


def clamp_int(value, minimum, maximum, default):
    if value is None:
        return default
    value = int(value)
    return max(minimum, min(maximum, value))


def parse_hex_color(value, default):
    if value is None:
        return default

    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError("Color must use RRGGBB format")

    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


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
        codepoints.append("{:x}".format(codepoint).upper())
    return "-".join(codepoints)


def load_emojis():
    emojis = {}

    for path in sorted(EMOJI_DIR.glob("*.png")):
        emojis[path.stem.upper()] = path

    return emojis


EMOJIS = load_emojis()


def measure_text(draw, text, font):
    if not text:
        return 0, 0
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def load_emoji_image(emoji_path, emoji_size):
    image = Image.open(emoji_path).convert("RGBA")
    return image.resize((emoji_size, emoji_size), Image.Resampling.LANCZOS)


def tokenize(text):
    unsupported = []
    tokens = []
    buffer = []

    for cluster in split_graphemes(text):
        code = cluster_to_codepoints(cluster)
        emoji_path = EMOJIS.get(code)

        if emoji_path is not None:
            if buffer:
                tokens.append(("text", "".join(buffer)))
                buffer = []
            tokens.append(("emoji", emoji_path))
            continue

        if any(unicodedata.category(char) == "So" for char in cluster):
            unsupported.append("{} ({})".format(cluster, code))

        buffer.append(cluster)

    if buffer:
        tokens.append(("text", "".join(buffer)))

    return tokens, unsupported


def render_banner(
    text=DEFAULT_TEXT,
    height=DEFAULT_HEIGHT,
    width=DEFAULT_WIDTH,
    text_color=DEFAULT_TEXT_COLOR,
    background=DEFAULT_BACKGROUND,
    padding=None,
    gap=None,
):
    text = text or DEFAULT_TEXT
    height = clamp_int(height, 16, 256, DEFAULT_HEIGHT)
    width = None if width in (None, "") else clamp_int(width, 16, 4096, DEFAULT_HEIGHT)
    padding = clamp_int(padding, 0, 512, round(height * DEFAULT_PADDING_RATIO)) if padding is not None else round(height * DEFAULT_PADDING_RATIO)
    gap = clamp_int(gap, 0, 128, max(1, round(height * DEFAULT_GAP_RATIO))) if gap is not None else max(1, round(height * DEFAULT_GAP_RATIO))

    font_size = max(12, round(height * DEFAULT_FONT_RATIO))
    emoji_size = max(12, min(height - 4, round(font_size * DEFAULT_EMOJI_RATIO)))

    font = ImageFont.truetype(str(FONT_PATH), size=font_size)
    probe = Image.new("RGBA", (1, 1), background + (255,))
    draw = ImageDraw.Draw(probe)

    tokens, unsupported = tokenize(text)

    content_width = 0
    for token_type, content in tokens:
        if token_type == "text":
            token_width, _ = measure_text(draw, content, font)
        else:
            token_width = emoji_size
        content_width += token_width
        content_width += gap

    if content_width > 0:
        content_width -= gap

    canvas_width = max(width or 0, content_width + padding * 2, height)
    canvas = Image.new("RGBA", (canvas_width, height), background + (255,))
    draw = ImageDraw.Draw(canvas)

    x = padding
    for token_type, content in tokens:
        if token_type == "text":
            bbox = draw.textbbox((0, 0), content, font=font)
            y = (height - (bbox[3] - bbox[1])) // 2 - bbox[1]
            draw.text((x, y), content, font=font, fill=text_color)
            x += bbox[2] - bbox[0]
        else:
            emoji = load_emoji_image(content, emoji_size)
            y = (height - emoji.height) // 2
            canvas.alpha_composite(emoji, (x, y))
            x += emoji.width
        x += gap

    return canvas.convert("RGB"), unsupported
