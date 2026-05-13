from io import BytesIO

from flask import Flask, Response, request

from renderer import DEFAULT_BACKGROUND, DEFAULT_TEXT_COLOR, parse_hex_color, render_banner


app = Flask(__name__)


def bad_request(message):
    return Response(message, status=400, mimetype="text/plain; charset=utf-8")


def make_header_safe(value):
    return value.encode("ascii", "backslashreplace").decode("ascii")


@app.get("/")
def render_png():
    try:
        image, unsupported = render_banner(
            text=request.args.get("text", "Banner"),
            width=request.args.get("width"),
            height=request.args.get("height", 32),
            padding=request.args.get("padding"),
            gap=request.args.get("gap"),
            font_name=request.args.get("font"),
            text_color=parse_hex_color(request.args.get("color"), DEFAULT_TEXT_COLOR),
            background=parse_hex_color(request.args.get("background"), DEFAULT_BACKGROUND),
        )
    except ValueError as error:
        return bad_request(str(error))

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    response = Response(buffer.getvalue(), mimetype="image/png")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"

    if unsupported:
        response.headers["X-Unsupported-Emoji"] = make_header_safe(" | ".join(unsupported))[:1000]

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
