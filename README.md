# cosmic-unicorn-service

`cosmic-unicorn-service` is a small rendering service for Cosmic Unicorn displays.

It can return:

- text banners as PNG or 24-bit BMP
- 32 x 32 animations as CUF files

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
http://127.0.0.1:8000/text?text=Grattis%20på%20födelsedagen!%20🥳&height=32
http://127.0.0.1:8000/text?text=Grattis%20på%20födelsedagen!%20🥳&height=32&font=impact
http://127.0.0.1:8000/text?text=Grattis%20på%20födelsedagen!%20🥳&height=32&format=bmp
http://127.0.0.1:8000/animation?name=tree
http://127.0.0.1:8000/animation?name=tree&format=cuf
http://127.0.0.1:8000/animation
```

## Build Emojis

On your Mac, you can build local emoji PNG files with Apple Color Emoji and store them in `emojis/`:

```bash
python3 generate-emojis.py
```

Edit the `EMOJIS` constant in `emojis.py` and run the script again. It writes files such as `emojis/1f973.png` and `emojis/1f575-1f3fb.png`.
Existing files are always overwritten.

## Build Animations

Generate CUF animation files from GIF files before deploying:

```bash
python3 generate-cufs.py
```

Source GIF files live in `gifs/`.

Generated CUF files live in `cufs/`.

Existing `.cuf` files are deleted before new files are generated.

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

## Animations

Animation CUF files live in `cufs/`.
Source GIF files live in `gifs/`.

The animation endpoint is:

```text
/animation?name=tree
```

It returns GIF by default so it can be opened in a browser.

For Cosmic Unicorn, request CUF explicitly:

```text
/animation?name=tree&format=cuf
```

The `name` parameter can be:

- a GIF/CUF base name, such as `tree`
- a CUF filename, such as `tree.cuf`
- a GIF filename, such as `tree.gif`
- omitted for a random animation

Examples:

```text
/animation
/animation?name=fireplace
/animation?name=fireplace&format=cuf
/animation?name=fireplace.cuf&format=cuf
```

The service never generates CUF files while handling requests. Run `python3 generate-cufs.py` before deploying when GIF files have changed.

## Notes

- Style is fixed to a red ticker look; the default PNG background is transparent unless a `background` is provided.
- BMP output is a 24-bit RGB `image/bmp` with transparent pixels flattened onto black.
- All text segments share one common baseline, even if inline `font` or `size` changes are used. Emojis are placed between text segments but do not change the text baseline.
- Emoji PNG files live in `emojis/`.
- Font files live in `fonts/`.
- Available fonts: `arial`, `arial-bold`, `arial-black`, `arial-rounded`, `calibri`, `century-gothic`, `century-gothic-italic`, `digital`, `djb-digital`, `gotham`, `impact`, `prototype`, `roboto`, `tahoma`, `verdana`, `verdana-bold`
- Unsupported emoji render as `⚠️` and are also reported in the `X-Unsupported-Emoji` response header.
