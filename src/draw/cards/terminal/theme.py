"""The look shared by every terminal-styled card."""

from src.draw.theme import STYLE

# Card frame
# GitHub renders README images at up to ~800px before scaling them down.
CARD_WIDTH = 830
MARGIN = 10
BORDER_RADIUS = 10
BORDER_WIDTH = 1

# Colors
BACKGROUND_COLOR = STYLE["background"]
ORANGE = "#f78166"
BLUE = "#58a6ff"
DIM = "#7d8590"
TEXT_COLOR = "#e6edf3"

# Typography
# Google Fonts links don't load in an embedded <img>, so this stays a system stack.
FONT_MONO = "Liberation Mono,Consolas,Menlo,Monaco,DejaVu Sans Mono,Courier New,monospace"
TITLE_SIZE = 12
PROMPT_SIZE = 14
NAME_SIZE = 16
INFO_FONT_SIZE = PROMPT_SIZE + 1

# Title bar
HEADER_HEIGHT = 32
DOT_RADIUS = 5
DOT_GAP = 16
DOT_PADDING_X = 14
TITLE_GAP = 10

# Content area
CONTENT_PADDING_TOP = 22
CONTENT_PADDING_X = 28

# Command prompt
PROMPT_ROW_HEIGHT = 24
PROMPT_MARGIN_BOTTOM = 10

# Loading bar
BAR_CHARS = 20

# ASCII portrait
# Art is fitted into this box whatever its character grid measures.
ASCII_BOX_WIDTH = 176.7
ASCII_BOX_HEIGHT = 210.8
ASCII_LINE_HEIGHT = 1.14
ASCII_GAP = 26
ASCII_REVEAL_DURATION = 0.6

# Info panel
# The heading sits tight to the divider under it, so it claims less than its font size.
NAME_ROW_HEIGHT = 6
DIVIDER_WIDTH = 168
DIVIDER_DASH_LENGTH = 6
DIVIDER_DASH_GAP = 3
DIVIDER_MARGIN_TOP = 12
DIVIDER_MARGIN_BOTTOM = 20
INFO_ROW_HEIGHT = 30
INFO_LINE_HEIGHT = 19
INFO_VALUE_OFFSET = 14
INFO_ICON_SIZE = 13
INFO_GAP = 8
INFO_LABEL_PADDING = 8
INFO_VALUE_MAX_LINES = 2
FALLBACK_ICON = "circle-dot"

# Names a config can give a row's accent colour, drawn from the swatch palette.
ROW_COLORS = {
    "orange": ORANGE,
    "purple": "#bc8cff",
    "blue": BLUE,
    "green": "#3fb950",
    "yellow": "#e3b341",
    "red": "#f85149",
    "cyan": "#39c5cf",
    "white": TEXT_COLOR,
    "grey": DIM,
    "gray": DIM,
}
DEFAULT_ROW_COLOR = ORANGE

SWATCH_WIDTH = 22
SWATCH_HEIGHT = 11
SWATCH_MARGIN_TOP = 0

# How long each fact row waits behind the one above it.
ROW_STAGGER = 0.08

# Cursor animation
# The block that trails the command as it's typed.
CURSOR_WIDTH = 7
CURSOR_HEIGHT = 14
# How far the trailing cursor hangs below the panel's last row.
CURSOR_TRAIL = 23
# One blink, to be followed by a count or by "infinite".
CURSOR_BLINK = "cursorBlink 1s step-end"
CURSOR_KEYFRAMES = "<style>@keyframes cursorBlink{0%,49%{opacity:1}50%,100%{opacity:0}}</style>"
