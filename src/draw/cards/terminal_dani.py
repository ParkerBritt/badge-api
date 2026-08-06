"""Draws Dani's terminal-styled hero card, with its contents read from a config she publishes."""

import os
import re

import drawsvg as draw

from src.draw.cards.terminal import theme
from src.draw.cards.terminal.components import (
    InfoRow,
    card_origin,
    draw_ascii_art,
    draw_comment,
    draw_info_panel,
    draw_loading_bar,
    draw_prompt,
    draw_title_bar,
    measure_label_width,
    new_terminal_card,
)
from src.util.remote_config import fetch_text, fetch_yaml

# A row's colour can be a palette name or a plain hex code.
HEX_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")

_ASSETS = os.path.join(os.path.dirname(__file__), "assets")

# Copies of Dani's published files, to point the card at while working on it.
LOCAL_CONFIG_SOURCE = os.path.join(_ASSETS, "terminal_dani_config.yaml")
LOCAL_ASCII_SOURCE = os.path.join(_ASSETS, "terminal_dani_ascii.txt")

# The versions Dani publishes in her own repo.
REMOTE_CONFIG_URL = (
    "https://raw.githubusercontent.com/DanielaHz/DanielaHz/main/terminal_config.yaml"
)
REMOTE_ASCII_URL = "https://raw.githubusercontent.com/DanielaHz/DanielaHz/main/terminal_art"

DEFAULT_CONFIG_SOURCE = REMOTE_CONFIG_URL
DEFAULT_ASCII_SOURCE = REMOTE_ASCII_URL

# Caps on config text, which comes from outside this repo.
MAX_ROWS = 8
MAX_TEXT_CHARS = 200
MAX_LABEL_CHARS = 20
MAX_ICON_CHARS = 40
MAX_COLOR_CHARS = 20

# The plain text settings, alongside what stands in when the config omits one.
DEFAULTS = {
    "name": "Dani",
    "username": "DanielaHz",
    "greeting": "",
    "terminal_title": "dani@github: ~",
    "command": "fetch --github",
}

# Layout
GREETING_ROW_HEIGHT = 26
CONTENT_BOTTOM_PADDING = 34
INFO_PANEL_OFFSET_X = 40
INFO_PANEL_OFFSET_Y = 0
ASCII_PANEL_OFFSET_X = 0
ASCII_PANEL_OFFSET_Y = 5
MIN_VALUE_WIDTH = 120


def _clean_text(value, limit=MAX_TEXT_CHARS, default=""):
    """Returns a config value as trimmed, length-capped text, or the default when it isn't usable."""
    # A bool is an int in Python, and "True" is not a value anyone meant to write.
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        return default
    return str(value).strip()[:limit] or default


def _clean_color(value):
    """Returns a row's accent colour from a palette name or hex code, e.g. "purple" -> "#bc8cff"."""
    name = _clean_text(value, MAX_COLOR_CHARS).lower()
    if HEX_COLOR.match(name):
        return name
    return theme.ROW_COLORS.get(name, theme.DEFAULT_ROW_COLOR)


def _clean_rows(raw):
    """Returns the config's fact rows as `InfoRow`s, dropping unusable entries."""
    rows = []
    for entry in raw if isinstance(raw, list) else []:
        if not isinstance(entry, dict):
            continue
        label = _clean_text(entry.get("label"), MAX_LABEL_CHARS)
        value = _clean_text(entry.get("value"))
        if not label and not value:
            continue
        icon = _clean_text(entry.get("icon"), MAX_ICON_CHARS, theme.FALLBACK_ICON)
        rows.append(InfoRow(icon, label, value, _clean_color(entry.get("color"))))
        if len(rows) >= MAX_ROWS:
            break
    return rows


def load_config(source):
    """Returns the card's settings, falling back to the defaults wherever the config can't be used.

    A missing, unreachable or malformed document leaves every default in place,
    so the card still renders while the source is being edited.
    """
    raw = fetch_yaml(source) or {}
    config = {key: _clean_text(raw.get(key), default=default) for key, default in DEFAULTS.items()}
    config["rows"] = _clean_rows(raw.get("rows"))
    return config


def build_terminal_dani_card(
    config_source=DEFAULT_CONFIG_SOURCE,
    ascii_source=DEFAULT_ASCII_SOURCE,
):
    """Returns the SVG for Dani's terminal styled hero card.

    The card grows to fit however many rows the config lists, and the portrait
    fills the same box whatever the size of her art's character grid.
    """
    config = load_config(config_source)
    art = fetch_text(ascii_source) or ""
    rows = config["rows"]
    has_art = bool(art.strip())

    x, y = card_origin()
    content_x = x + theme.CONTENT_PADDING_X
    content_y = y + theme.HEADER_HEIGHT + theme.CONTENT_PADDING_TOP

    info_x = content_x + INFO_PANEL_OFFSET_X
    if has_art:
        info_x += theme.ASCII_BOX_WIDTH + theme.ASCII_GAP

    label_width = measure_label_width(rows)
    value_x = info_x + theme.INFO_ICON_SIZE + theme.INFO_GAP + label_width + theme.INFO_VALUE_OFFSET
    value_width = max(MIN_VALUE_WIDTH, x + theme.CARD_WIDTH - theme.CONTENT_PADDING_X - value_x)

    greeting_height = GREETING_ROW_HEIGHT if config["greeting"] else 0
    prompt_y = content_y + greeting_height
    row_top = prompt_y + theme.PROMPT_ROW_HEIGHT + theme.PROMPT_MARGIN_BOTTOM

    command = config["command"]
    type_duration = max(0.4, len(command) * 0.12)
    bar_delay = 1.0 + type_duration + 0.25
    bar_duration = 1.1
    result_delay = bar_delay + bar_duration + 0.25

    # The panel is drawn loose so the card can take its height before building the frame.
    panel = draw.Group()
    panel_height = draw_info_panel(
        panel,
        info_x,
        row_top + INFO_PANEL_OFFSET_Y + theme.NAME_SIZE / 2,
        rows=rows,
        name=config["name"],
        username=config["username"],
        label_width=label_width,
        value_width=value_width,
        delay=result_delay,
    )

    results_height = INFO_PANEL_OFFSET_Y + theme.NAME_SIZE / 2 + panel_height + theme.CURSOR_TRAIL
    if has_art:
        results_height = max(results_height, ASCII_PANEL_OFFSET_Y + theme.ASCII_BOX_HEIGHT)

    height = (
        theme.HEADER_HEIGHT
        + theme.CONTENT_PADDING_TOP
        + greeting_height
        + theme.PROMPT_ROW_HEIGHT
        + theme.PROMPT_MARGIN_BOTTOM
        + results_height
        + CONTENT_BOTTOM_PADDING
    )

    svg = new_terminal_card(theme.CARD_WIDTH, height)
    draw_title_bar(svg, x, y, theme.CARD_WIDTH, config["terminal_title"])

    if config["greeting"]:
        draw_comment(
            svg,
            content_x,
            content_y + theme.PROMPT_SIZE / 2,
            config["greeting"],
            delay=0.3,
        )

    draw_prompt(
        svg,
        content_x,
        prompt_y + theme.PROMPT_SIZE / 2,
        command,
        delay=1.0,
        duration=type_duration,
        hide_cursor_at=bar_delay,
    )
    draw_loading_bar(svg, content_x, row_top + theme.PROMPT_SIZE / 2, bar_delay, bar_duration)

    if has_art:
        draw_ascii_art(
            svg,
            art,
            content_x + ASCII_PANEL_OFFSET_X,
            row_top + ASCII_PANEL_OFFSET_Y,
            result_delay + 0.4,
        )

    svg.append(panel)
    return svg.as_svg()
