"""Draws a minimal section divider: a numbered label over a hairline rule."""

import drawsvg as draw

from src.draw.theme import FONT_FAMILY

LINE_LENGTH = 500
FONT_SIZE = 12
LABEL_LINE_HEIGHT = 13
LETTER_SPACING = 2.5
MARGIN_TOP = 20
RULE_MARGIN_TOP = 10
RULE_THICKNESS = 1

LABEL_COLOR = "#7d8590"
RULE_COLOR = "#7d8590"
RULE_OPACITY = 0.18


def build_divider_card(label, line_length=LINE_LENGTH):
    """Returns the SVG for a minimal section divider, e.g. "01 — About Me" over a faint rule.

    The rule runs the full width of the card, so `line_length` sizes both.
    """
    height = MARGIN_TOP + LABEL_LINE_HEIGHT + RULE_MARGIN_TOP + RULE_THICKNESS

    svg = draw.Drawing(line_length, height, origin=(0, 0))

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
            line_length,
            RULE_THICKNESS,
            fill=RULE_COLOR,
            fill_opacity=RULE_OPACITY,
        )
    )

    return svg.as_svg()
