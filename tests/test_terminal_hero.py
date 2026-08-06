from io import BytesIO

import drawsvg as draw
from PIL import Image

from src.draw.cards.terminal_hero import (
    ASCII_CELL_HEIGHT,
    ASCII_CELL_WIDTH,
    ASCII_DENSITY,
    build_terminal_hero_card,
    draw_ascii_portrait,
    render_ascii_portrait,
)


def test_portrait_measures_its_character_grid():
    lines = ["●●●●", "●●●●", "●●●●"]
    _, width, height = render_ascii_portrait(lines)
    assert width == 4 * ASCII_CELL_WIDTH
    assert height == 3 * ASCII_CELL_HEIGHT


def test_denser_characters_lay_down_more_ink():
    def ink(char):
        data, _, _ = render_ascii_portrait([char])
        alpha = Image.open(BytesIO(data)).convert("RGBA").getchannel("A")
        return sum(alpha.histogram()[level] * level for level in range(256))

    by_density = sorted(ASCII_DENSITY, key=ASCII_DENSITY.get)
    weights = [ink(char) for char in by_density]
    assert weights == sorted(weights)


def test_portrait_goes_out_as_an_embedded_raster():
    svg = draw.Drawing(300, 300)
    draw_ascii_portrait(svg, "●◉◎\n○·○", 0, 0, delay=0)
    output = svg.as_svg()
    assert "data:image/png" in output
    # The characters themselves never reach the reader, so no font has to carry them.
    for char in "●◉◎○·":
        assert char not in output


def test_card_renders():
    svg = build_terminal_hero_card(uptime="4y 319d {(VFX)}")
    assert svg.startswith("<?xml")
    assert "Parker-Britt" in svg
