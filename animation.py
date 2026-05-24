from pathlib import Path
import random


ROOT_DIR = Path(__file__).resolve().parent
CUF_DIR = ROOT_DIR / "cufs"
RESERVED_RANDOM_NAMES = ("", "random", "random.cuf")


def clean_animation_name(value):
    if value is None:
        return "random.cuf"

    name = value.strip().lower()
    if name in RESERVED_RANDOM_NAMES:
        return "random.cuf"

    if "/" in name or "\\" in name:
        raise ValueError("Animation name must not contain path separators")

    if name.endswith(".gif"):
        name = name[:-4]
    elif name.endswith(".cuf"):
        name = name[:-4]

    if not name:
        return "random.cuf"

    return name


def list_animation_names():
    if not CUF_DIR.exists():
        return []

    return sorted(path.stem.lower() for path in CUF_DIR.glob("*.cuf"))


def choose_animation_name():
    names = list_animation_names()
    if not names:
        raise FileNotFoundError("No animations are available")

    return random.choice(names)


def resolve_animation(name):
    animation_name = clean_animation_name(name)
    if animation_name == "random.cuf":
        animation_name = choose_animation_name()

    cuf_path = CUF_DIR / (animation_name + ".cuf")
    if cuf_path.exists():
        return animation_name, cuf_path

    raise FileNotFoundError("Animation not found: {}".format(animation_name))
