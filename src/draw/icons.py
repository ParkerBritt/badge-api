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


def get_file_icon(icon_name, x=0, y=0, color="white", size=14, center=False):
    """Returns an icon from the icons directory, or an empty element if there is no such file."""
    icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "icons", icon_name + ".svg")
    if not os.path.exists(icon_path):
        return draw.Raw("")
    with open(icon_path) as f:
        svg_content = f.read()
    return get_icon(svg_content, x=x, y=y, color=color, size=size, center=center)


def get_icon(raw_svg, x=0, y=0, color="white", size=14, center=False):
    """Returns the path out of an icon's SVG, recolored and placed at the given spot."""
    match = re.search(r"<path[\S\s]*\/>", raw_svg)
    path = match.group() if match else ""
    if center:
        x -= size / 2
        y -= size / 2
    stroke_only = 'fill="none"' in raw_svg
    style = (
        (
            f'fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round"'
        )
        if stroke_only
        else f'fill="{color}"'
    )
    return draw.Raw(
        f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24" {style}>{path}</svg>'
    )
