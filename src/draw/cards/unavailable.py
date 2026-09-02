"""Draws the placeholder card shown when a card has no data behind it yet."""

import drawsvg as draw

from src.draw.shapes import new_card
from src.draw.theme import STYLE, TEXT

CARD_WIDTH = STYLE["card_width"]
CARD_HEIGHT = 120

MESSAGE = "temporarily unavailable"
MESSAGE_OPACITY = 0.5


def build_unavailable_card(width=CARD_WIDTH, height=CARD_HEIGHT, message=MESSAGE):
    """Returns an empty card with a short message on it, the same size as a real one.

    Note: this is used when a card has never been built and its data can't be reached, so
    the reply is still an image rather than an error GitHub remembers as broken.
    """
    svg, x, y = new_card(width, height)

    svg.append(
        draw.Text(
            message,
            x=x + width / 2,
            y=y + height / 2,
            font_size=STYLE["text_size"],
            text_anchor="middle",
            opacity=MESSAGE_OPACITY,
            **TEXT,
        )
    )

    return svg.as_svg()
