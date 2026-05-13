from pathlib import Path
import unicodedata

from PIL import Image, ImageColor, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parent
FONT_PATH = BASE_DIR / "fonts" / "arial-bold.ttf"
EMOJI_DIR = BASE_DIR / "emojis"
WARNING_EMOJI_CODE = "26A0-FE0F"
FONT_ALIASES = {
    "arial": "arial.ttf",
    "arial-bold": "arial-bold.ttf",
    "arial-black": "arial-black.ttf",
    "arial-rounded": "arial-rounded-bold.ttf",
    "calibri": "calibri-bold.ttf",
    "century-gothic": "century-gothic-bold.ttf",
    "century-gothic-italic": "century-gothic-bold-italic.ttf",
    "digital": "digital.ttf",
    "djb-digital": "djb-get-digital.ttf",
    "gotham": "gotham-bold.ttf",
    "impact": "impact.ttf",
    "prototype": "prototype.ttf",
    "roboto": "roboto.ttf",
    "tahoma": "tahoma-bold.ttf",
    "verdana": "verdana.ttf",
    "verdana-bold": "verdana-bold.ttf",
}

DEFAULT_TEXT = "Banner"
DEFAULT_HEIGHT = 32
DEFAULT_WIDTH = None
DEFAULT_TEXT_COLOR = (255, 0, 0)
DEFAULT_BACKGROUND = (0, 0, 0)
DEFAULT_PADDING_RATIO = 0.375
DEFAULT_GAP_RATIO = 0.1
DEFAULT_FONT_RATIO = 18 / 32
DEFAULT_EMOJI_RATIO = 1.5
MIN_FONT_SIZE = 8
MAX_FONT_SIZE = 512

ZWJ = "\u200d"
VS16 = "\ufe0f"
KEYCAP = "\u20e3"
SKIN_TONE_RANGE = range(0x1F3FB, 0x1F400)
REGIONAL_RANGE = range(0x1F1E6, 0x1F200)
EMOJI_SYMBOL_RANGES = (
    range(0x2300, 0x2800),
    range(0x1F000, 0x20000),
)


def clamp_int(value, minimum, maximum, default):
    if value is None:
        return default
    value = int(value)
    return max(minimum, min(maximum, value))


def parse_hex_color(value, default):
    if value is None:
        return default

    value = value.strip()
    if not value:
        return default

    if not value.startswith("#") and len(value) in (3, 6):
        hex_chars = "0123456789abcdefABCDEF"
        if all(char in hex_chars for char in value):
            value = "#" + value

    return parse_color_value(value)


def parse_color_value(value):
    value = value.strip()
    if not value:
        raise ValueError("Color must use CSS color names or hex like RRGGBB")

    if not value.startswith("#") and len(value) in (3, 6):
        hex_chars = "0123456789abcdefABCDEF"
        if all(char in hex_chars for char in value):
            value = "#" + value

    try:
        color = ImageColor.getrgb(value)
    except ValueError:
        raise ValueError("Color must use CSS color names or hex like RRGGBB")

    return color[:3]


def resolve_font_path(font_name):
    if font_name is None or font_name == "":
        return FONT_PATH

    key = font_name.strip().lower()
    filename = FONT_ALIASES.get(key)

    if filename is None:
        supported = ", ".join(sorted(FONT_ALIASES))
        raise ValueError(f"Unknown font '{font_name}'. Supported fonts: {supported}")

    return BASE_DIR / "fonts" / filename


def default_font_size_for_height(height):
    return max(12, round(height * DEFAULT_FONT_RATIO))


def normalize_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if "\n" not in text:
        return text

    parts = [part.strip() for part in text.split("\n") if part.strip()]
    if not parts:
        return ""

    return " ".join(parts)


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


def is_emoji_like_cluster(cluster):
    for char in cluster:
        codepoint = ord(char)

        if char in (ZWJ, VS16, KEYCAP):
            return True

        if unicodedata.combining(char):
            return True

        if codepoint in SKIN_TONE_RANGE or codepoint in REGIONAL_RANGE:
            return True

        for emoji_range in EMOJI_SYMBOL_RANGES:
            if codepoint in emoji_range:
                return True

    return False


def load_emojis():
    emojis = {}

    for path in sorted(EMOJI_DIR.glob("*.png")):
        emojis[path.stem.upper()] = path

    return emojis


EMOJIS = load_emojis()
WARNING_EMOJI_PATH = EMOJIS.get(WARNING_EMOJI_CODE)

if WARNING_EMOJI_PATH is None:
    raise RuntimeError("Missing fallback emoji: {}".format(WARNING_EMOJI_CODE))


def resolve_emoji_path(code):
    emoji_path = EMOJIS.get(code)
    if emoji_path is not None:
        return emoji_path

    if "FE0F" not in code:
        emoji_path = EMOJIS.get(code + "-FE0F")
        if emoji_path is not None:
            return emoji_path

    normalized = "-".join(part for part in code.split("-") if part != "FE0F")
    if normalized != code:
        emoji_path = EMOJIS.get(normalized)
        if emoji_path is not None:
            return emoji_path

    return None


def measure_text(draw, text, font):
    if not text:
        return 0, 0
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def measure_text_width(draw, text, font):
    if not text:
        return 0
    return round(draw.textlength(text, font=font))


def load_emoji_image(emoji_path, emoji_size):
    image = Image.open(emoji_path).convert("RGBA")
    return image.resize((emoji_size, emoji_size), Image.Resampling.LANCZOS)


def parse_style_segments(text, default_color, default_font_name):
    segments = []
    current_color = default_color
    current_font_name = default_font_name
    color_stack = []
    font_stack = []
    buffer = []
    index = 0

    while index < len(text):
        if text.startswith("[/color]", index):
            if buffer:
                segments.append((current_color, current_font_name, "".join(buffer)))
                buffer = []

            current_color = color_stack.pop() if color_stack else default_color
            index += len("[/color]")
            continue

        if text.startswith("[color=", index):
            close_index = text.find("]", index + 7)
            if close_index == -1:
                buffer.append(text[index:])
                break

            color_value = text[index + 7:close_index].strip()
            if not color_value:
                raise ValueError("Color tag must use [color=name]...[/color]")

            if buffer:
                segments.append((current_color, current_font_name, "".join(buffer)))
                buffer = []

            try:
                next_color = parse_color_value(color_value)
            except ValueError:
                raise ValueError("Unknown inline color '{}'".format(color_value))

            color_stack.append(current_color)
            current_color = next_color
            index = close_index + 1
            continue

        if text.startswith("[/font]", index):
            if buffer:
                segments.append((current_color, current_font_name, "".join(buffer)))
                buffer = []

            current_font_name = font_stack.pop() if font_stack else default_font_name
            index += len("[/font]")
            continue

        if text.startswith("[font=", index):
            close_index = text.find("]", index + 6)
            if close_index == -1:
                buffer.append(text[index:])
                break

            font_value = text[index + 6:close_index].strip()
            if not font_value:
                raise ValueError("Font tag must use [font=name]...[/font]")

            if buffer:
                segments.append((current_color, current_font_name, "".join(buffer)))
                buffer = []

            resolve_font_path(font_value)
            font_stack.append(current_font_name)
            current_font_name = font_value
            index = close_index + 1
            continue

        buffer.append(text[index])
        index += 1

    if buffer:
        segments.append((current_color, current_font_name, "".join(buffer)))

    return segments


def tokenize(text, default_color, default_font_name):
    unsupported = []
    tokens = []

    for segment_color, segment_font_name, segment_text in parse_style_segments(text, default_color, default_font_name):
        buffer = []

        for cluster in split_graphemes(segment_text):
            code = cluster_to_codepoints(cluster)
            emoji_path = resolve_emoji_path(code)

            if emoji_path is not None:
                if buffer:
                    tokens.append(("text", "".join(buffer), segment_color, segment_font_name))
                    buffer = []
                tokens.append(("emoji", emoji_path))
                continue

            if is_emoji_like_cluster(cluster):
                if buffer:
                    tokens.append(("text", "".join(buffer), segment_color, segment_font_name))
                    buffer = []
                unsupported.append("{} ({})".format(cluster, code))
                tokens.append(("emoji", WARNING_EMOJI_PATH))
                continue

            buffer.append(cluster)

        if buffer:
            tokens.append(("text", "".join(buffer), segment_color, segment_font_name))

    return tokens, unsupported


def render_banner(
    text=DEFAULT_TEXT,
    height=DEFAULT_HEIGHT,
    width=DEFAULT_WIDTH,
    text_color=DEFAULT_TEXT_COLOR,
    background=DEFAULT_BACKGROUND,
    padding=None,
    gap=None,
    font_name=None,
    font_size=None,
):
    text = normalize_text(text or DEFAULT_TEXT)
    height = clamp_int(height, 16, 256, DEFAULT_HEIGHT)
    width = None if width in (None, "") else clamp_int(width, 16, 4096, DEFAULT_HEIGHT)
    padding = clamp_int(padding, 0, 512, round(height * DEFAULT_PADDING_RATIO)) if padding is not None else round(height * DEFAULT_PADDING_RATIO)
    gap = clamp_int(gap, 0, 128, max(1, round(height * DEFAULT_GAP_RATIO))) if gap is not None else max(1, round(height * DEFAULT_GAP_RATIO))

    default_font_size = default_font_size_for_height(height)

    if font_size is None:
        font_size = default_font_size
    else:
        font_size = clamp_int(font_size, MIN_FONT_SIZE, MAX_FONT_SIZE, default_font_size)

    emoji_size = max(12, min(height, round(font_size * DEFAULT_EMOJI_RATIO)))

    font_cache = {}

    def get_font(name):
        key = name or ""
        if key not in font_cache:
            font_cache[key] = ImageFont.truetype(str(resolve_font_path(name)), size=font_size)
        return font_cache[key]

    probe = Image.new("RGBA", (1, 1), background + (255,))
    draw = ImageDraw.Draw(probe)

    tokens, unsupported = tokenize(text, text_color, font_name)

    content_width = 0
    for token in tokens:
        token_type = token[0]
        if token_type == "text":
            token_font = get_font(token[3])
            token_width = measure_text_width(draw, token[1], token_font)
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
    text_center_y = height / 2
    for token in tokens:
        token_type = token[0]
        if token_type == "text":
            content = token[1]
            token_color = token[2]
            token_font = get_font(token[3])
            draw.text((x, text_center_y), content, font=token_font, fill=token_color, anchor="lm")
            x += measure_text_width(draw, content, token_font)
        else:
            content = token[1]
            emoji = load_emoji_image(content, emoji_size)
            y = (height - emoji.height) // 2
            canvas.alpha_composite(emoji, (x, y))
            x += emoji.width
        x += gap

    return canvas.convert("RGB"), unsupported
