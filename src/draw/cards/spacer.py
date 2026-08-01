"""Draws a blank, transparent card used to add spacing between other cards in a README."""

import drawsvg as draw

DEFAULT_WIDTH = 20
DEFAULT_HEIGHT = 1


def build_spacer_card(width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
    """Returns an empty SVG of the given size, for spacing cards apart in a README."""
    svg = draw.Drawing(width, height, origin=(0, 0))
    return svg.as_svg()
