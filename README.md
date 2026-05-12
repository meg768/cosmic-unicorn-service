# ticker

`ticker` has one job: return a PNG in ticker style from query parameters.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 app.py
```

Then open:

```text
http://127.0.0.1:8000?text=Grattis%20på%20födelsedagen!%20🥳&height=32
```

## Build Emojis

On your Mac, you can build local emoji PNG files with Apple Color Emoji and store them in `emojis/`:

```bash
python3 create-emojis.py "🥸🥳🕵🏻"
```

This writes files such as `emojis/1f973.png` and `emojis/1f575-1f3fb.png`.

If you want to replace existing files:

```bash
python3 create-emojis.py "🥳" --overwrite
```

## Parameters

- `text`: message to render
- `height`: output height in pixels, default `32`
- `width`: optional minimum width in pixels
- `color`: text color in `RRGGBB`, default `FF0000`
- `background`: background color in `RRGGBB`, default `000000`
- `padding`: optional left/right padding in pixels
- `gap`: optional gap between text and emoji in pixels

## Notes

- Style is fixed to a red-on-black ticker look.
- Emoji PNG files live in `emojis/`.
- Font files live in `fonts/`.
- Unsupported emoji are left as text and reported in the `X-Unsupported-Emoji` response header.
