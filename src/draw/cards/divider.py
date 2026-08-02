"""Draws a minimal section divider: a numbered label over a hairline rule."""

import drawsvg as draw

from src.draw.theme import FONT_FAMILY

WIDTH = 830
FONT_SIZE = 12
LABEL_LINE_HEIGHT = 13
LETTER_SPACING = 2.5
MARGIN_TOP = 20
RULE_MARGIN_TOP = 10
RULE_THICKNESS = 1

LABEL_COLOR = "#7d8590"
RULE_COLOR = "#ffffff"
RULE_OPACITY = 0.06


def build_divider_card(label, width=WIDTH):
    """Returns the SVG for a minimal section divider, e.g. "01 — About Me" over a faint rule."""
    height = MARGIN_TOP + LABEL_LINE_HEIGHT + RULE_MARGIN_TOP + RULE_THICKNESS

    svg = draw.Drawing(width, height, origin=(0, 0))

    svg.append(
        draw.Text(
            label.upper(),
            x=0,
            y=MARGIN_TOP + LABEL_LINE_HEIGHT / 2,
            font_size=FONT_SIZE,
            font_family=FONT_FAMILY,
            font_weight=500,
            letter_spacing=LETTER_SPACING,
            fill=LABEL_COLOR,
            dominant_baseline="central",
        )
    )

    svg.append(
        draw.Rectangle(
            0,
            MARGIN_TOP + LABEL_LINE_HEIGHT + RULE_MARGIN_TOP,
            width,
            RULE_THICKNESS,
            fill=RULE_COLOR,
            fill_opacity=RULE_OPACITY,
        )
    )

    return svg.as_svg()
