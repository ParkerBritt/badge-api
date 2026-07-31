"""GitHub's per-language brand colors, read from the linguist data in languages.yml."""

import os

import yaml


def load_language_colors():
    path = os.path.join(os.path.dirname(__file__), "languages.yml")
    with open(path) as f:
        languages = yaml.safe_load(f)

    colors = {}
    for name, data in languages.items():
        if isinstance(data, dict) and data.get("color"):
            colors[name] = data["color"]
    return colors


LANGUAGE_COLORS = load_language_colors()
