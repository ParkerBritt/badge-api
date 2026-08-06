from contextlib import contextmanager
from unittest import mock

from src.draw.cards.terminal.components import InfoRow
from src.draw.cards.terminal.theme import (
    DEFAULT_ROW_COLOR,
    FALLBACK_ICON,
    ROW_COLORS,
)
from src.draw.cards.terminal_dani import (
    DEFAULTS,
    MAX_LABEL_CHARS,
    MAX_ROWS,
    MAX_TEXT_CHARS,
    build_terminal_dani_card,
    load_config,
)


def with_config(document):
    return mock.patch("src.draw.cards.terminal_dani.fetch_yaml", return_value=document)


@contextmanager
def with_sources(document, art=""):
    """Stands in for both documents the card reads, so a render stays off the network."""
    with (
        with_config(document),
        mock.patch("src.draw.cards.terminal_dani.fetch_text", return_value=art),
    ):
        yield


def test_reads_a_full_config():
    document = {
        "name": "Dani",
        "username": "DanielaHz",
        "greeting": "Holaa, soy Dani",
        "terminal_title": "dani@github: ~",
        "command": "fetch --github",
        "rows": [
            {"icon": "globe", "label": "Site", "value": "graphicsjournal.com", "color": "green"}
        ],
    }
    with with_config(document):
        config = load_config("http://x")
    assert config["greeting"] == "Holaa, soy Dani"
    assert config["rows"] == [
        InfoRow("globe", "Site", "graphicsjournal.com", ROW_COLORS["green"])
    ]


def test_unreadable_config_falls_back_to_defaults():
    for document in (None, {}, {"rows": "not a list"}):
        with with_config(document):
            config = load_config("http://x")
        assert config["name"] == DEFAULTS["name"]
        assert config["terminal_title"] == DEFAULTS["terminal_title"]
        assert config["rows"] == []


def test_row_without_an_icon_gets_the_fallback():
    with with_config({"rows": [{"label": "Now", "value": "Robotics"}]}):
        assert load_config("http://x")["rows"] == [
            InfoRow(FALLBACK_ICON, "Now", "Robotics", DEFAULT_ROW_COLOR)
        ]


def test_unusable_rows_are_dropped():
    document = {
        "rows": [{"icon": "globe", "label": "Site", "value": "x"}, "nonsense", {}, {"icon": "bot"}]
    }
    with with_config(document):
        assert load_config("http://x")["rows"] == [InfoRow("globe", "Site", "x", DEFAULT_ROW_COLOR)]


def test_palette_names_and_hex_codes_both_set_a_row_colour():
    document = {
        "rows": [
            {"label": "A", "value": "x", "color": "purple"},
            {"label": "B", "value": "x", "color": "#ff00aa"},
            {"label": "C", "value": "x", "color": "YELLOW"},
        ]
    }
    with with_config(document):
        colors = [row.color for row in load_config("http://x")["rows"]]
    assert colors == [ROW_COLORS["purple"], "#ff00aa", ROW_COLORS["yellow"]]


def test_unusable_colour_falls_back_to_the_default():
    document = {
        "rows": [
            {"label": "A", "value": "x"},
            {"label": "B", "value": "x", "color": "chartreuse"},
            {"label": "C", "value": "x", "color": "#zzz"},
            {"label": "D", "value": "x", "color": 42},
        ]
    }
    with with_config(document):
        colors = {row.color for row in load_config("http://x")["rows"]}
    assert colors == {DEFAULT_ROW_COLOR}


def test_row_colours_reach_the_rendered_card():
    document = {"name": "Dani", "rows": [{"label": "A", "value": "x", "color": "purple"}]}
    with with_sources(document):
        svg = build_terminal_dani_card("http://x", "http://y")
    assert ROW_COLORS["purple"] in svg


def test_row_count_and_text_are_capped():
    document = {
        "name": "n" * 500,
        "rows": [{"label": "l" * 50, "value": "v" * 500} for _ in range(MAX_ROWS + 5)],
    }
    with with_config(document):
        config = load_config("http://x")
    assert len(config["name"]) == MAX_TEXT_CHARS
    assert len(config["rows"]) == MAX_ROWS
    assert len(config["rows"][0][1]) == MAX_LABEL_CHARS
    assert len(config["rows"][0][2]) == MAX_TEXT_CHARS


def test_card_renders_from_the_defaults():
    with with_sources(None):
        svg = build_terminal_dani_card("http://x", "http://y")
    assert svg.startswith("<?xml")
    assert DEFAULTS["username"] in svg


def test_card_grows_with_its_row_count():
    def height_of(rows):
        with with_sources({"name": "Dani", "rows": rows}):
            svg = build_terminal_dani_card("http://x", "http://y")
        return float(svg.split('height="')[1].split('"')[0])

    short = [{"icon": "globe", "label": "Site", "value": "x"}]
    tall = [{"icon": "globe", "label": f"Row {i}", "value": "x"} for i in range(MAX_ROWS)]
    assert height_of(tall) > height_of(short)


def test_card_still_renders_without_art():
    with with_sources({"name": "Dani", "username": "DanielaHz"}):
        svg = build_terminal_dani_card("http://x", "http://y")
    assert "DanielaHz" in svg
