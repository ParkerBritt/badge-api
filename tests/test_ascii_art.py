import drawsvg as draw

from src.draw.cards.terminal.components import draw_ascii_art, fit_ascii_art
from src.draw.cards.terminal.theme import ASCII_BOX_HEIGHT, ASCII_BOX_WIDTH


def tiny_art():
    return "●●\n●●"


def huge_art(cols=1000, rows=400):
    return "\n".join("●" * cols for _ in range(rows))


def test_art_of_any_grid_stays_inside_the_box():
    for art in (tiny_art(), huge_art(), "●", "●" * 500):
        _, width, height = fit_ascii_art(art.split("\n"))
        assert width <= ASCII_BOX_WIDTH + 1e-6
        assert height <= ASCII_BOX_HEIGHT + 1e-6


def test_art_fills_the_axis_it_runs_out_of_room_on():
    # A wide, short grid is limited by the box width.
    _, width, _ = fit_ascii_art(["●" * 200, "●" * 200])
    assert width == ASCII_BOX_WIDTH

    # A tall, narrow one is limited by its height.
    _, _, height = fit_ascii_art(["●"] * 200)
    assert height == ASCII_BOX_HEIGHT


def test_grid_aspect_ratio_survives_fitting():
    lines = ["●" * 40] * 20
    _, width, height = fit_ascii_art(lines)
    small = ["●" * 4] * 2
    _, small_width, small_height = fit_ascii_art(small)
    assert round(width / height, 6) == round(small_width / small_height, 6)


def test_drawn_art_is_clipped_to_the_same_box_whatever_its_size():
    for art in (tiny_art(), huge_art(50, 50)):
        svg = draw.Drawing(100, 100)
        draw_ascii_art(svg, art, 0, 0, delay=0)
        output = svg.as_svg()
        assert f'width="{ASCII_BOX_WIDTH}"' in output
        assert f'to="{ASCII_BOX_HEIGHT}"' in output


def test_empty_art_draws_nothing():
    for art in ("", "\n\n", "   \n   "):
        svg = draw.Drawing(100, 100)
        draw_ascii_art(svg, art, 0, 0, delay=0)
        assert "<text" not in svg.as_svg()


def test_art_renders_as_literal_characters():
    svg = draw.Drawing(300, 300)
    draw_ascii_art(svg, "◉◎○\n·●·", 0, 0, delay=0)
    output = svg.as_svg()
    assert "◉◎○" in output
    assert "data:image/png" not in output


def test_leading_spaces_are_preserved():
    svg = draw.Drawing(300, 300)
    draw_ascii_art(svg, "  ●●\n●●●●", 0, 0, delay=0)
    assert 'xml:space="preserve"' in svg.as_svg()
