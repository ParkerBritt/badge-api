"""Draws the small pill badge, the one with an icon and a label."""

import colorsys

import drawsvg as draw
from simplepycons import all_icons

from src.draw.icons import get_simple_icon
from src.draw.shapes import get_drop_shadow
from src.draw.theme import FONT_FAMILY
from src.util.color import hex_to_rgb, rgb_to_hex
from src.util.text import get_char_width


def build_standard_badge(
    prefix: str = "",
    label: str = "",
    icon: str = "",
    color: str = "FF4713",
    label_color: str = "FF4713",
    border_color: str = None,
) -> str:
    """Returns the SVG for a pill badge, optionally split into a prefix and a colored label."""
    display_text = prefix + label
    text_width = get_char_width(display_text)
    label_width = get_char_width(label)

    rect_height = 28
    icon_width = 14
    left_padding = 9

    has_icon = bool(icon) and icon.lower() in all_icons.names()
    has_label = prefix != ""

    if border_color:
        border_color = "#" + border_color

    text_x = (left_padding + icon_width) * has_icon + left_padding
    rect_width = text_x + text_width + left_padding
    if has_label:
        rect_width += 9  # prefix padding
    text_rect_width = label_width + left_padding * 2

    # Darker gradient stop
    bg_hex = "#" + color
    h, s, v = colorsys.rgb_to_hsv(*hex_to_rgb(bg_hex))
    bg_alt_hex = rgb_to_hex(colorsys.hsv_to_rgb(h, s, max(v * 0.75, 0)))

    output = draw.Drawing(rect_width, rect_height, origin=(0, 0))

    # Gradient
    gradient = draw.LinearGradient(
        rect_width * 0.2,
        0,
        rect_width * 0.2,
        rect_height,
    )
    gradient.add_stop(0, bg_hex)
    gradient.add_stop(1, bg_alt_hex)

    # Drop shadow
    shadow = get_drop_shadow()

    # Main background
    output.append(
        draw.Rectangle(
            0, 0, rect_width, rect_height, fill=gradient, rx=8, stroke=border_color, stroke_width=1
        )
    )

    # Label background (right side)
    if has_label:
        output.append(
            draw.Rectangle(
                rect_width - text_rect_width,
                0,
                text_rect_width,
                rect_height,
                fill=f"#{label_color}",
                rx=8,
            )
        )

    # Icon
    if has_icon:
        icon_group = draw.Group(filter=shadow)
        icon_group.append(
            get_simple_icon(
                icon, x=left_padding, y=rect_height / 2 - icon_width / 2, size=icon_width
            )
        )
        output.append(icon_group)

    # Text
    text_kwargs = dict(
        font_family=FONT_FAMILY,
        fill="white",
        dominant_baseline="central",
        text_rendering="geometricPrecision",
        font_weight="bold",
    )
    text_y = rect_height / 2 + 1

    if has_label:
        output.append(draw.Text(prefix, 13, text_x, text_y, **text_kwargs))
    output.append(
        draw.Text(
            label,
            13,
            rect_width - text_rect_width + left_padding,
            text_y,
            **text_kwargs,
        )
    )

    return output.as_svg()
