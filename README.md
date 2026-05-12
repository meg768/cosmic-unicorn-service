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

## Parameters

- `text`: message to render
- `height`: output height in pixels, default `32`
- `width`: optional minimum width in pixels
- `color`: text color in `RRGGBB`, default `FFD228`
- `background`: background color in `RRGGBB`, default `000000`
- `padding`: optional left/right padding in pixels
- `gap`: optional gap between text and emoji in pixels

## Notes

- Style is fixed to a yellow-on-black ticker look.
- Emoji PNG files live in `emojis/`.
- Font files live in `fonts/`.
- Unsupported emoji are left as text and reported in the `X-Unsupported-Emoji` response header.
