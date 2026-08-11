"""Draws a card that's just a button shape holding centered text."""

import colorsys

import drawsvg as draw

from src.draw.shapes import get_drop_shadow
from src.draw.theme import STYLE, TEXT
from src.util.color import get_readable_text_color, hex_to_rgb, rgb_to_hex
from src.util.text import get_char_width

HEIGHT = 29
FONT_SIZE = 13
BORDER_RADIUS = 10
MARGIN_X = 11
MARGIN_Y = 5
SHADOW_BLUR = 3
SHADOW_OPACITY = 0.4


def build_button_card(label, color=None):
    """Returns the SVG for a button shaped card showing a single line of centered text.

    `color` is a hex string (e.g. `"FF4713"`)
    """
    padding = STYLE["padding"]
    width = int(get_char_width(label, FONT_SIZE) + padding * 2)

    if color:
        background = f"#{color}"
        text_color = get_readable_text_color(background)
        h, s, v = colorsys.rgb_to_hsv(*hex_to_rgb(background))
        border_color = rgb_to_hex(colorsys.hsv_to_rgb(h, s, v * 0.7))
    else:
        background = STYLE["background"]
        text_color = STYLE["text_color"]
        border_color = STYLE["border"]

    svg = draw.Drawing(width + MARGIN_X * 2, HEIGHT + MARGIN_Y * 2, origin=(0, 0))

    svg.append(
        draw.Rectangle(
            MARGIN_X,
            MARGIN_Y,
            width,
            HEIGHT,
            fill=background,
            rx=BORDER_RADIUS,
            stroke=border_color,
            stroke_width=STYLE["border_width"],
            filter=get_drop_shadow(opacity=SHADOW_OPACITY, blur=SHADOW_BLUR, x=0, y=0),
        )
    )
    svg.append(
        draw.Text(
            label,
            x=MARGIN_X + width / 2,
            y=MARGIN_Y + HEIGHT / 2 + 1,
            font_size=FONT_SIZE,
            text_anchor="middle",
            **(TEXT | {"fill": text_color, "font_weight": 600}),
        )
    )

    return svg.as_svg()
