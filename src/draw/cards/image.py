"""Draws a card that's just a single image, filling the standard card border and radius."""

import drawsvg as draw

from src.draw.shapes import card_clip, new_card
from src.draw.theme import STYLE
from src.util.images import fetch_capped, prepare_image

WIDTH = STYLE["card_width"]
HEIGHT = 250

# Drawn slightly oversized before clipping to avoid black edges.
OVERFLOW = 1

BORDER_OPACITY = 0.85


def build_image_card(image_url, width=WIDTH, height=HEIGHT):
    """Returns the SVG for a card showing a single image, cropped to fill it."""
    svg, card_x, card_y = new_card(width, height)

    data = fetch_capped(image_url)
    if data:
        image = prepare_image(data, width + OVERFLOW * 2, height + OVERFLOW * 2)
        svg.append(
            draw.Image(
                card_x - OVERFLOW,
                card_y - OVERFLOW,
                width + OVERFLOW * 2,
                height + OVERFLOW * 2,
                data=image,
                embed=True,
                mime_type="image/png",
                preserveAspectRatio="none",
                clip_path=card_clip(card_x, card_y, width, height),
            )
        )

        # Draw border
        svg.append(
            draw.Rectangle(
                card_x,
                card_y,
                width,
                height,
                fill="none",
                rx=STYLE["border_radius"],
                stroke=STYLE["border"],
                stroke_width=STYLE["border_width"],
                stroke_opacity=BORDER_OPACITY,
            )
        )

    return svg.as_svg()
