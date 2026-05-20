# Banner

`banner` has one job: return a banner image from query parameters.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
.venv/bin/gunicorn --bind 127.0.0.1:3005 app:app
```

Then open:

```text
http://127.0.0.1:8000?text=Grattis%20på%20födelsedagen!%20🥳&height=32
http://127.0.0.1:8000?text=Grattis%20på%20födelsedagen!%20🥳&height=32&font=impact
http://127.0.0.1:8000?text=Grattis%20på%20födelsedagen!%20🥳&height=32&format=bmp
```

## Build Emojis

On your Mac, you can build local emoji PNG files with Apple Color Emoji and store them in `emojis/`:

```bash
python3 generate-emojis.py
```

Edit the `EMOJIS` constant in `emojis.py` and run the script again. It writes files such as `emojis/1f973.png` and `emojis/1f575-1f3fb.png`.
Existing files are always overwritten.

## Parameters

- `text`: message to render
  Inline style syntax is supported, for example `Detta är [color=blue]blått[/color]`, `[font=impact]detta[/font]` and `[size=48]stort[/size]`. Inline `size` only affects text. Emoji size stays consistent for the whole banner. Global directives can be set by prefixing the text with one or more opening tags such as `[size=10]`, `[font=impact]` or `[size=10,font=impact,color=red]`, and may also include properties such as `background`, `height`, `width`, `padding` and `gap`.
- `height`: output height in pixels, default `32`
- `width`: optional minimum width in pixels
- `color`: text color as CSS color name or hex like `RRGGBB`, default `FF0000`
- `background`: background color as CSS color name, `transparent`, or hex like `RRGGBB`; when omitted the PNG background is transparent
- `padding`: optional left/right padding in pixels
- `gap`: optional gap between text and emoji in pixels
- `size`: optional text size in pixels
- `font`: optional font name such as `arial-bold`, `impact`, `digital`, `gotham`, `prototype`
- `format`: output image format, either `png` or `bmp`, default `png`

## Notes

- Style is fixed to a red ticker look; the default PNG background is transparent unless a `background` is provided.
- BMP output is an 8-bit paletted `image/bmp` with transparent pixels flattened onto black, which makes it easier for small display clients to decode than PNG while still being readable in browsers.
- All text segments share one common baseline, even if inline `font` or `size` changes are used. Emojis are placed between text segments but do not change the text baseline.
- Emoji PNG files live in `emojis/`.
- Font files live in `fonts/`.
- Available fonts: `arial`, `arial-bold`, `arial-black`, `arial-rounded`, `calibri`, `century-gothic`, `century-gothic-italic`, `digital`, `djb-digital`, `gotham`, `impact`, `prototype`, `roboto`, `tahoma`, `verdana`, `verdana-bold`
- Unsupported emoji render as `⚠️` and are also reported in the `X-Unsupported-Emoji` response header.
