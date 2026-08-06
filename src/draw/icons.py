"""Turns icon sources into SVG elements."""

import os
import re

import drawsvg as draw
from simplepycons import all_icons


def get_simple_icon(icon_name, x=0, y=0, color="white", size=14, center=False):
    """Returns a SimpleIcons icon, or an empty element if the name is unknown."""
    icon_name = icon_name.lower()
    if icon_name not in all_icons.names():
        return draw.Raw("")
    return get_icon(all_icons[icon_name].raw_svg, x=x, y=y, color=color, size=size, center=center)


# Icon names can come from user-supplied config, so they're held to a plain slug.
ICON_NAME = re.compile(r"^[a-z0-9-]+$")


def find_icon_file(icon_name):
    """Returns the path to a named icon, preferring a hand-added one over the vendored Lucide set."""
    if not ICON_NAME.match(icon_name or ""):
        return None
    icons_root = os.path.join(os.path.dirname(__file__), "..", "..", "icons")
    for directory in (icons_root, os.path.join(icons_root, "lucide")):
        path = os.path.join(directory, icon_name + ".svg")
        if os.path.exists(path):
            return path
    return None


def get_file_icon(icon_name, x=0, y=0, color="white", size=14, center=False, fallback=None):
    """Returns an icon from the icons directory.

    An unknown name falls back to `fallback` when one is given, so a typo in a
    user-supplied name shows a placeholder rather than a hole in the layout.
    """
    icon_path = find_icon_file(icon_name)
    if icon_path is None and fallback:
        icon_path = find_icon_file(fallback)
    if icon_path is None:
        return draw.Raw("")
    with open(icon_path) as f:
        svg_content = f.read()
    return get_icon(svg_content, x=x, y=y, color=color, size=size, center=center)


def get_icon(raw_svg, x=0, y=0, color="white", size=14, center=False):
    """Returns the drawable innards of an icon's SVG, recolored and placed at the given spot.

    Everything inside the outer `<svg>` is kept, since an icon can be built from
    circles, lines or polylines just as well as paths.
    """
    match = re.search(r"<svg([^>]*)>([\S\s]*)</svg\s*>", raw_svg)
    attributes, body = match.groups() if match else ("", "")
    # Titles would show as a tooltip over whatever the icon happens to sit on.
    body = re.sub(r"<title>[\S\s]*?</title>", "", body)
    # Icon files are pretty-printed, and that layout whitespace is no use here.
    body = re.sub(r">\s+<", "><", body)
    body = re.sub(r"\s+", " ", body).strip()
    if center:
        x -= size / 2
        y -= size / 2
    stroke_only = 'fill="none"' in attributes
    style = (
        (
            f'fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round"'
        )
        if stroke_only
        else f'fill="{color}"'
    )
    return draw.Raw(
        f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24" {style}>{body}</svg>'
    )
