"""Draws Parker's terminal-styled hero card for the top of a README."""

import os
from datetime import date
from io import BytesIO

import drawsvg as draw
from PIL import Image, ImageDraw

from src.draw.cards.terminal import theme
from src.draw.cards.terminal.components import (
    InfoRow,
    card_origin,
    draw_info_panel,
    draw_loading_bar,
    draw_prompt,
    draw_title_bar,
    new_terminal_card,
)
from src.draw.cards.terminal.primitives import wipe_reveal_down

_ASCII_ART_PATH = os.path.join(os.path.dirname(__file__), "assets", "terminal_hero_ascii.txt")
with open(_ASCII_ART_PATH, encoding="utf-8") as _f:
    DEFAULT_ASCII_ART = _f.read()

CONTENT_HEIGHT = 310

# Portrait
# The cell each character occupies, taller than it is wide like a terminal's.
ASCII_CELL_WIDTH = 1.9
ASCII_CELL_HEIGHT = 3.1
# Dots are drawn this many times over and shrunk back down, so they anti-alias smoothly.
ASCII_SUPERSAMPLE = 6

# How solid each portrait character reads, densest glyph to faintest.
ASCII_DENSITY = {"●": 1.0, "◉": 0.82, "◎": 0.5, "○": 0.32, "·": 0.16}
ASCII_DEFAULT_DENSITY = 0.3

# Displayed data
UPTIME_START_DATE = date(2021, 9, 20)

SWATCH_ROWS = [
    [
        "#0d1117",
        "#f85149",
        "#3fb950",
        "#e3b341",
        "#58a6ff",
        "#bc8cff",
        "#39c5cf",
        "#e6edf3",
    ],
    [
        "#484f58",
        "#ffa198",
        "#56d364",
        "#f2cc60",
        "#79c0ff",
        "#d2a8ff",
        "#56d4dd",
        "#f0f6fc",
    ],
]

# Pinned rather than measured from the labels, to hold this layout as it is.
INFO_LABEL_WIDTH = 68

# Panel layout
INFO_PANEL_OFFSET_X = 40
INFO_PANEL_OFFSET_Y = 0

ASCII_PANEL_OFFSET_X = 0
ASCII_PANEL_OFFSET_Y = 5


def _format_uptime(start_date):
    """Returns elapsed time since `start_date` as years and days, with a dim VFX tag.

    e.g. date(2021, 9, 20) -> "4y 319d {(VFX)}"
    """
    today = date.today()
    years = today.year - start_date.year
    if (today.month, today.day) < (start_date.month, start_date.day):
        years -= 1
    anniversary = start_date.replace(year=start_date.year + years)
    days = (today - anniversary).days
    return f"{years}y {days}d {{(VFX)}}"


def render_ascii_portrait(lines):
    """Bakes the portrait to a PNG of dots sized by each character's density, like a halftone print.

    e.g. "●" -> a dot filling its cell, "·" -> a faint dot a third that wide

    Why a raster: a cell here is about two pixels across, small enough that
    hinting and font substitution would have more say over the picture than the
    art does. Baked, it looks the same in every browser.
    """
    cols = max(len(line) for line in lines)
    rows = len(lines)
    cell_w = ASCII_CELL_WIDTH * ASCII_SUPERSAMPLE
    cell_h = ASCII_CELL_HEIGHT * ASCII_SUPERSAMPLE

    raster = Image.new("RGBA", (round(cols * cell_w), round(rows * cell_h)), (0, 0, 0, 0))
    artist = ImageDraw.Draw(raster)

    for row, line in enumerate(lines):
        for col, char in enumerate(line):
            if char == " ":
                continue
            density = ASCII_DENSITY.get(char, ASCII_DEFAULT_DENSITY)
            cx = col * cell_w + cell_w / 2
            cy = row * cell_h + cell_h / 2
            # A denser character is both a wider dot and a more opaque one.
            radius = min(cell_w, cell_h) / 2 * (0.35 + 0.65 * density)
            alpha = round(255 * (0.25 + 0.75 * density))
            artist.ellipse(
                (cx - radius, cy - radius, cx + radius, cy + radius),
                fill=(230, 237, 243, alpha),
            )

    width, height = cols * ASCII_CELL_WIDTH, rows * ASCII_CELL_HEIGHT
    raster = raster.resize((round(width), round(height)), Image.LANCZOS)

    buffer = BytesIO()
    raster.save(buffer, format="PNG")
    return buffer.getvalue(), width, height


def draw_ascii_portrait(svg, art, x, y, delay):
    """Draws the portrait, wiping in top to bottom like it's printing out, returning its size."""
    lines = art.strip("\n").split("\n")
    data, width, height = render_ascii_portrait(lines)

    reveal = wipe_reveal_down(svg, x, y, width, height, delay, theme.ASCII_REVEAL_DURATION)
    reveal.append(draw.Image(x, y, width, height, data=data, embed=True, mime_type="image/png"))
    return width, height


def build_terminal_hero_card(
    ascii_art=DEFAULT_ASCII_ART,
    name="Parker-Britt",
    username="github",
    role="Pipeline TD",
    stack="Houdini · USD · Python · C++",
    uptime=None,
    contact="parker@parkerbritt.com",
    terminal_title="parker-b@github: ~",
    command="fetch --github",
    info_offset_x=INFO_PANEL_OFFSET_X,
    info_offset_y=INFO_PANEL_OFFSET_Y,
    ascii_offset_x=ASCII_PANEL_OFFSET_X,
    ascii_offset_y=ASCII_PANEL_OFFSET_Y,
):
    """Returns the SVG for a terminal styled hero card introducing a README's author."""
    if uptime is None:
        uptime = _format_uptime(UPTIME_START_DATE)

    height = theme.HEADER_HEIGHT + CONTENT_HEIGHT
    x, y = card_origin()
    svg = new_terminal_card(theme.CARD_WIDTH, height)
    draw_title_bar(svg, x, y, theme.CARD_WIDTH, terminal_title)

    content_x = x + theme.CONTENT_PADDING_X
    content_y = y + theme.HEADER_HEIGHT + theme.CONTENT_PADDING_TOP

    # Typed command
    prompt_y = content_y + theme.PROMPT_SIZE / 2
    type_duration = max(0.4, len(command) * 0.12)
    bar_delay = 1.0 + type_duration + 0.25
    bar_duration = 1.1
    draw_prompt(
        svg,
        content_x,
        prompt_y,
        command,
        delay=1.0,
        duration=type_duration,
        hide_cursor_at=bar_delay,
    )

    # Loading bar
    row_top = content_y + theme.PROMPT_ROW_HEIGHT + theme.PROMPT_MARGIN_BOTTOM
    draw_loading_bar(svg, content_x, row_top + theme.PROMPT_SIZE / 2, bar_delay, bar_duration)

    result_delay = bar_delay + bar_duration + 0.25

    # ASCII portrait
    ascii_x = content_x + ascii_offset_x
    ascii_y = row_top + ascii_offset_y
    ascii_width, _ = draw_ascii_portrait(svg, ascii_art, ascii_x, ascii_y, result_delay + 0.4)

    # Info panel
    info_x = ascii_x + ascii_width + theme.ASCII_GAP + info_offset_x
    info_y = row_top + info_offset_y
    draw_info_panel(
        svg,
        info_x,
        info_y + theme.NAME_SIZE / 2,
        rows=[
            InfoRow("user-cog", "Role", role),
            InfoRow("layers", "Stack", stack),
            InfoRow("clock", "Uptime", uptime),
            InfoRow("mail", "Contact", contact),
        ],
        name=name,
        username=username,
        swatches=SWATCH_ROWS,
        label_width=INFO_LABEL_WIDTH,
        delay=result_delay,
    )

    return svg.as_svg()
