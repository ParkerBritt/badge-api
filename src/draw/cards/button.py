"""Draws a card that's just a button shape holding centered text."""

import drawsvg as draw

from src.draw.shapes import get_drop_shadow
from src.draw.theme import STYLE, TEXT
from src.util.text import get_char_width

HEIGHT = 30
FONT_SIZE = 13
BORDER_RADIUS = 15
MARGIN_X = 13
MARGIN_Y = 5
SHADOW_BLUR = 3
SHADOW_OPACITY = 0.4


def build_button_card(label):
    """Returns the SVG for a button shaped card showing a single line of centered text."""
    padding = STYLE["padding"]
    width = int(get_char_width(label, FONT_SIZE) + padding * 2)

    svg = draw.Drawing(width + MARGIN_X * 2, HEIGHT + MARGIN_Y * 2, origin=(0, 0))

    svg.append(
        draw.Rectangle(
            MARGIN_X,
            MARGIN_Y,
            width,
            HEIGHT,
            fill=STYLE["background"],
            rx=BORDER_RADIUS,
            stroke=STYLE["border"],
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
            **(TEXT | {"fill": STYLE["text_color"], "font_weight": 600}),
        )
    )

    return svg.as_svg()
