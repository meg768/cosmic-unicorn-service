# Project Context

This repo is the server-side rendering service for the Cosmic Unicorn displays.

The project used to be called `banner`, but it is now `cosmic-unicorn-service`.

## Purpose

The service is a dedicated backend for the Pico-based Cosmic Unicorn displays.

It returns:

- rendered text as PNG or 24-bit BMP
- GIF animation previews for a normal browser
- CUF animation files for the Pico runtime

This keeps text rendering, emoji rendering, fonts, GIF storage, and CUF generation on the server instead of on the Pico.

## Live Host

Primary host:

```text
http://cosmic-unicorn.egelberg.se/
https://cosmic-unicorn.egelberg.se/
```

`banner.egelberg.se` may still point at the same Apache backend for compatibility, but the project name and intended hostname are now Cosmic Unicorn-specific.

## API

Text endpoint:

```text
/text?text=Hello&height=32&format=bmp
```

Animation endpoint:

```text
/animation
```

Animation format rules:

- GIF is default, so `/animation?name=tree` opens in a browser.
- CUF is explicit, so `/animation?name=tree&format=cuf` is for the Pico.
- If `name` is omitted, the service chooses a random animation.
- `name=random` is not special.
- There are no `/animation.gif` or `/animation.cuf` routes.

Examples:

```text
http://cosmic-unicorn.egelberg.se/animation?name=tree
http://cosmic-unicorn.egelberg.se/animation?name=tree&format=cuf
http://cosmic-unicorn.egelberg.se/animation
http://cosmic-unicorn.egelberg.se/animation?format=cuf
```

## CUF Generation

CUF files are generated ahead of time, not during requests.

Run:

```bash
python3 generate-cufs.py
```

The script:

- reads GIFs from `gifs/`
- deletes existing `cufs/*.cuf`
- writes generated CUF files into `cufs/`

Runtime request handling only reads existing files.

## CUF Format

CUF is a custom compact format for this project.

It currently stores:

- `CUF3` magic
- width and height
- frame count
- frame delay
- RGB565 palette
- RLE-compressed frame data

The Pico reads CUF directly and renders each frame.

## Deployment

Production server:

```text
pi-kato
```

Production path:

```text
/home/pi/cosmic-unicorn-service
```

PM2 process:

```text
cosmic-unicorn-service
```

Gunicorn bind:

```text
127.0.0.1:3005
```

PM2 start command pattern:

```bash
sudo pm2 start .venv/bin/gunicorn --name cosmic-unicorn-service --interpreter none -- app:app --bind 127.0.0.1:3005
```

Important: use `--interpreter none`. Otherwise PM2 may try to run the Python entrypoint through Node.

If the project directory is moved, rebuild `.venv`; Python entrypoints such as `gunicorn` can contain absolute shebang paths.

## Apache

Apache reverse-proxies both HTTP and HTTPS to:

```text
http://127.0.0.1:3005/
```

The vhost has:

```apache
ServerName banner.egelberg.se
ServerAlias cosmic-unicorn.egelberg.se
```

The Let's Encrypt certificate currently covers both:

```text
banner.egelberg.se
cosmic-unicorn.egelberg.se
```

## Useful Checks

Browser GIF:

```bash
curl -I "http://cosmic-unicorn.egelberg.se/animation?name=tree"
```

Pico CUF:

```bash
curl -I "http://cosmic-unicorn.egelberg.se/animation?name=tree&format=cuf"
```

PM2:

```bash
ssh pi@pi-kato 'sudo pm2 list | grep cosmic-unicorn-service'
```

## Related Repo

The Pico-side project is:

```text
/Users/magnus/Documents/GitHub/cosmic-unicorn
```

It downloads text images and CUF animations from this service.
