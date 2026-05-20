from io import BytesIO

from flask import Flask, Response, request
from PIL import Image

from renderer import DEFAULT_BACKGROUND, DEFAULT_TEXT_COLOR, parse_hex_color, render_banner


app = Flask(__name__)
SUPPORTED_FORMATS = ("png", "bmp", "bmp24")


def bad_request(message):
    return Response(message, status=400, mimetype="text/plain; charset=utf-8")


def make_header_safe(value):
    return value.encode("ascii", "backslashreplace").decode("ascii")


def parse_format(value):
    if value is None or value == "":
        return "png"

    output_format = value.strip().lower()
    if output_format not in SUPPORTED_FORMATS:
        raise ValueError("Format must be one of: {}".format(", ".join(SUPPORTED_FORMATS)))

    return output_format


def image_to_response_bytes(image, output_format):
    buffer = BytesIO()

    if output_format == "bmp":
        # BMP has no alpha channel. Use black as the LED-display-friendly matte.
        background = Image.new("RGBA", image.size, (0, 0, 0, 255))
        background.alpha_composite(image)
        paletted = background.convert("RGB").convert("P", palette="ADAPTIVE", colors=256)
        paletted.save(buffer, format="BMP")
        return buffer.getvalue(), "image/bmp"

    if output_format == "bmp24":
        background = Image.new("RGBA", image.size, (0, 0, 0, 255))
        background.alpha_composite(image)
        background.convert("RGB").save(buffer, format="BMP")
        return buffer.getvalue(), "image/bmp"

    image.save(buffer, format="PNG")
    return buffer.getvalue(), "image/png"


@app.get("/")
def render_image():
    try:
        output_format = parse_format(request.args.get("format"))
        image, unsupported = render_banner(
            text=request.args.get("text", "Banner"),
            width=request.args.get("width"),
            height=request.args.get("height", 32),
            padding=request.args.get("padding"),
            gap=request.args.get("gap"),
            font_name=request.args.get("font"),
            font_size=request.args.get("size"),
            text_color=parse_hex_color(request.args.get("color"), DEFAULT_TEXT_COLOR),
            background=parse_hex_color(request.args.get("background"), DEFAULT_BACKGROUND),
        )
    except ValueError as error:
        return bad_request(str(error))

    body, mimetype = image_to_response_bytes(image, output_format)

    response = Response(body, mimetype=mimetype)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"

    if unsupported:
        response.headers["X-Unsupported-Emoji"] = make_header_safe(" | ".join(unsupported))[:1000]

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
