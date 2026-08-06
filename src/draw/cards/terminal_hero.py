"""Draws Parker's terminal-styled hero card for the top of a README."""

import os
from datetime import date

from src.draw.cards.terminal import theme
from src.draw.cards.terminal.components import (
    InfoRow,
    card_origin,
    draw_ascii_art,
    draw_info_panel,
    draw_loading_bar,
    draw_prompt,
    draw_title_bar,
    new_terminal_card,
)

_ASCII_ART_PATH = os.path.join(os.path.dirname(__file__), "assets", "terminal_hero_ascii.txt")
with open(_ASCII_ART_PATH, encoding="utf-8") as _f:
    DEFAULT_ASCII_ART = _f.read()

CONTENT_HEIGHT = 310

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
    draw_ascii_art(svg, ascii_art, ascii_x, ascii_y, result_delay + 0.4)

    # Info panel
    info_x = ascii_x + theme.ASCII_BOX_WIDTH + theme.ASCII_GAP + info_offset_x
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
