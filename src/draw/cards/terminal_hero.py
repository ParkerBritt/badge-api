"""Draws the terminal-styled hero card for the top of a README."""

import os
from io import BytesIO

import drawsvg as draw
from PIL import Image, ImageDraw

from src.draw.icons import get_file_icon
from src.draw.shapes import get_drop_shadow
from src.draw.theme import STYLE
from src.util.text import get_char_width

_ASCII_ART_PATH = os.path.join(os.path.dirname(__file__), "assets", "terminal_hero_ascii.txt")
with open(_ASCII_ART_PATH, encoding="utf-8") as _f:
    DEFAULT_ASCII_ART = _f.read()

# GitHub renders README images at up to ~800px before scaling down, so the
# card defaults to that width to fill the page without being downscaled.
CARD_WIDTH = 800
MARGIN = 10
BORDER_RADIUS = 10

HEADER_HEIGHT = 32
DOT_RADIUS = 5
DOT_GAP = 16
DOT_PADDING_X = 14
TITLE_GAP = 10
TITLE_SIZE = 12

CONTENT_PADDING_TOP = 22
CONTENT_PADDING_X = 28
CONTENT_HEIGHT = 310

PROMPT_SIZE = 14
PROMPT_ROW_HEIGHT = 24
PROMPT_MARGIN_BOTTOM = 10

BAR_CHARS = 20

INFO_PANEL_OFFSET_X = 40
INFO_PANEL_OFFSET_Y = 0

ASCII_PANEL_OFFSET_X = 0
ASCII_PANEL_OFFSET_Y = 5

ASCII_CELL_WIDTH = 1.9
ASCII_CELL_HEIGHT = 3.1
ASCII_SUPERSAMPLE = 6
ASCII_GAP = 26
ASCII_REVEAL_DURATION = 0.6

# How solid each portrait character reads, densest glyph to faintest.
ASCII_DENSITY = {"●": 1.0, "◉": 0.82, "◎": 0.5, "○": 0.32, "·": 0.16}
ASCII_DEFAULT_DENSITY = 0.3

NAME_SIZE = 16
DIVIDER_WIDTH = 168
DIVIDER_DASH_LENGTH = 6
DIVIDER_DASH_GAP = 3
DIVIDER_MARGIN_TOP = 12
DIVIDER_MARGIN_BOTTOM = 20
INFO_ROW_HEIGHT = 30
INFO_LABEL_WIDTH = 68
INFO_ICON_SIZE = 13
INFO_GAP = 8
INFO_FONT_SIZE = PROMPT_SIZE + 1
SWATCH_WIDTH = 22
SWATCH_HEIGHT = 11
SWATCH_MARGIN_TOP = 0

CURSOR_BLINK = "cursorBlink 1s step-end infinite"

# Google Fonts links don't load when a card is embedded as an <img>, so this
# sticks to the same system monospace stack every other card uses.
FONT_MONO = "Liberation Mono,Consolas,Menlo,Monaco,DejaVu Sans Mono,Courier New,monospace"

BACKGROUND_COLOR = STYLE["background"]

ORANGE = "#f78166"
BLUE = "#58a6ff"
DIM = "#7d8590"
TEXT_COLOR = "#e6edf3"

SWATCH_ROWS = [
    ["#0d1117", "#f85149", "#3fb950", "#e3b341", "#58a6ff", "#bc8cff", "#39c5cf", "#e6edf3"],
    ["#484f58", "#ffa198", "#56d364", "#f2cc60", "#79c0ff", "#d2a8ff", "#56d4dd", "#f0f6fc"],
]

INFO_ROWS = [
    ("user-cog", "Role"),
    ("layers", "Stack"),
    ("clock", "Uptime"),
    ("mail", "Contact"),
]


def _mono_text(svg, text, x, y, size, fill=TEXT_COLOR, weight=500, anim=None):
    svg.append(
        draw.Text(
            text,
            x=x,
            y=y,
            font_size=size,
            font_family=FONT_MONO,
            font_weight=weight,
            fill=fill,
            dominant_baseline="central",
            style=f"animation:{anim}" if anim else None,
        )
    )


def _fade_up(svg, group, delay, duration=0.4):
    """Fades a group in while sliding it up slightly, freezing once it lands."""
    # Set as plain attributes rather than an animation "from", since SMIL only
    # applies those values once the animation begins.
    group.args["opacity"] = "0"
    group.args["transform"] = "translate(0 10)"
    group.append_anim(
        draw.Animate(
            "opacity",
            f"{duration}s",
            "0",
            to="1",
            begin=f"{delay}s",
            fill="freeze",
            calcMode="linear",
        )
    )
    group.append_anim(
        draw.AnimateTransform(
            "translate",
            f"{duration}s",
            "0 10",
            to="0 0",
            begin=f"{delay}s",
            fill="freeze",
            calcMode="spline",
            keySplines="0.33 1 0.68 1",
            keyTimes="0;1",
        )
    )
    svg.append(group)


def _char_positions(x, count, char_width):
    """Returns the x of each of `count` monospace cells starting at x, one wider for a trailer."""
    return [x + i * char_width for i in range(count + 1)]


def _reveal_chars(
    svg, text, x, y, font_size, delay, duration, fill=TEXT_COLOR, weight=500, hide_at=None
):
    """Draws a monospace string one character at a time, each popping in whole and instantly.

    Returns the per-character advance width, so a caller (like a trailing
    cursor) can line itself up with the same grid.
    """
    char_width = get_char_width("0", font_size)
    steps = max(1, len(text))
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        char = draw.Text(
            ch,
            x=x + i * char_width,
            y=y,
            font_size=font_size,
            font_family=FONT_MONO,
            font_weight=weight,
            fill=fill,
            dominant_baseline="central",
        )
        char.args["opacity"] = "0"
        step_time = delay + duration * i / steps
        char.append_anim(
            draw.Animate("opacity", "0.01s", "1", begin=f"{step_time}s", fill="freeze")
        )
        if hide_at is not None:
            char.append_anim(
                draw.Animate("opacity", "0.15s", "1", to="0", begin=f"{hide_at}s", fill="freeze")
            )
        svg.append(char)
    return char_width


def _wipe_reveal_down(svg, x, y, width, height, delay, duration):
    """Returns a clip path that reveals its contents top-to-bottom, like it's printing out."""
    clip_rect = draw.Rectangle(x, y, width, 0)
    clip_rect.append_anim(
        draw.Animate(
            "height", f"{duration}s", "0", to=str(height), begin=f"{delay}s", fill="freeze"
        )
    )
    clip = draw.ClipPath()
    clip.append(clip_rect)
    group = draw.Group(clip_path=clip)
    svg.append(group)
    return group


def draw_title_bar(svg, x, y, width, title):
    """Draws the terminal window's title bar: three traffic-light dots and a title."""
    svg.append(draw.Rectangle(x, y, width, HEADER_HEIGHT, fill="#0d1117"))
    svg.append(
        draw.Line(
            x,
            y + HEADER_HEIGHT,
            x + width,
            y + HEADER_HEIGHT,
            stroke="rgba(255,255,255,0.08)",
            stroke_width=1,
        )
    )

    dot_y = y + HEADER_HEIGHT / 2
    dot_x = x + DOT_PADDING_X + DOT_RADIUS
    for color in ("#ff5f57", "#febc2e", "#28c840"):
        svg.append(draw.Circle(dot_x, dot_y, DOT_RADIUS, fill=color))
        dot_x += DOT_GAP

    _mono_text(svg, title, dot_x - DOT_GAP + DOT_RADIUS + TITLE_GAP, dot_y, TITLE_SIZE, fill=DIM)


def draw_prompt(svg, x, y, command, delay, duration, hide_cursor_at):
    """Draws the typed command prompt, with a cursor that tracks the last typed character."""
    prompt_x = x
    _mono_text(svg, ">", prompt_x, y, PROMPT_SIZE, fill=ORANGE, weight=600)
    command_x = prompt_x + get_char_width(">  ", PROMPT_SIZE)

    char_width = _reveal_chars(svg, command, command_x, y, PROMPT_SIZE, delay, duration)

    cursor_width = 7
    cursor = draw.Rectangle(command_x, y - 7, cursor_width, 14, fill=TEXT_COLOR)
    # Blinks while idle, then goes solid once typing starts.
    if delay > 0:
        blink_steps = max(2, round(delay / 0.5))
        if blink_steps % 2:
            blink_steps += 1
        blink_values = ";".join("1" if i % 2 == 0 else "0" for i in range(blink_steps + 1))
        blink_key_times = ";".join(str(i / blink_steps) for i in range(blink_steps + 1))
        cursor.append_anim(
            draw.Animate(
                "opacity",
                f"{delay}s",
                blink_values,
                begin="0s",
                fill="freeze",
                calcMode="discrete",
                keyTimes=blink_key_times,
            )
        )
    steps = max(1, len(command))
    positions = _char_positions(command_x, steps, char_width)
    x_values = ";".join(str(p) for p in positions)
    key_times = ";".join(str(i / steps) for i in range(steps + 1))
    cursor.append_anim(
        draw.Animate(
            "x",
            f"{duration}s",
            x_values,
            begin=f"{delay}s",
            fill="freeze",
            calcMode="discrete",
            keyTimes=key_times,
        )
    )
    cursor.append_anim(
        draw.Animate("visibility", "0.01s", "hidden", begin=f"{hide_cursor_at}s", fill="freeze")
    )
    svg.append(cursor)


def draw_loading_bar(svg, x, y, delay, duration):
    """Draws the ASCII progress bar (`[████░░░░] 42%`) that plays between the command and its results."""
    group = draw.Group()
    group.args["opacity"] = "0"
    group.append_anim(
        draw.Animate("opacity", "0.15s", "0", to="1", begin=f"{delay}s", fill="freeze")
    )
    group.append_anim(
        draw.Animate("opacity", "0.15s", "1", to="0", begin=f"{delay + duration}s", fill="freeze")
    )

    # Empty track and filled blocks are separate layers on the same character
    # grid, so the fill can't drift out of alignment with the brackets.
    char_width = get_char_width("0", PROMPT_SIZE)
    for i, ch in enumerate("[" + "░" * BAR_CHARS + "]"):
        group.append(
            draw.Text(
                ch,
                x=x + i * char_width,
                y=y,
                font_size=PROMPT_SIZE,
                font_family=FONT_MONO,
                font_weight=500,
                fill=TEXT_COLOR,
                dominant_baseline="central",
            )
        )

    fill_x = x + char_width
    _reveal_chars(
        svg, "█" * BAR_CHARS, fill_x, y, PROMPT_SIZE, delay, duration, hide_at=delay + duration
    )

    percent_x = x + (BAR_CHARS + 3) * char_width
    for step in range(BAR_CHARS + 1):
        frame = draw.Text(
            f"{step * 100 // BAR_CHARS}%",
            x=percent_x,
            y=y,
            font_size=PROMPT_SIZE,
            font_family=FONT_MONO,
            font_weight=500,
            fill=TEXT_COLOR,
            dominant_baseline="central",
        )
        frame.args["opacity"] = "0"
        step_time = delay + duration * step / BAR_CHARS
        frame.append_anim(
            draw.Animate("opacity", "0.01s", "1", begin=f"{step_time}s", fill="freeze")
        )
        if step < BAR_CHARS:
            next_time = delay + duration * (step + 1) / BAR_CHARS
            frame.append_anim(
                draw.Animate("opacity", "0.01s", "0", begin=f"{next_time}s", fill="freeze")
            )
        else:
            frame.append_anim(
                draw.Animate(
                    "opacity", "0.15s", "1", to="0", begin=f"{delay + duration}s", fill="freeze"
                )
            )
        group.append(frame)

    svg.append(group)


def render_ascii_portrait(lines):
    """Bakes the ASCII portrait to a PNG of dots sized by each character's density, like a halftone print."""
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
            radius = min(cell_w, cell_h) / 2 * (0.35 + 0.65 * density)
            alpha = round(255 * (0.25 + 0.75 * density))
            artist.ellipse(
                (cx - radius, cy - radius, cx + radius, cy + radius),
                fill=(230, 237, 243, alpha),
            )

    # Downsample from supersampled resolution so the dots anti-alias smoothly.
    width, height = cols * ASCII_CELL_WIDTH, rows * ASCII_CELL_HEIGHT
    raster = raster.resize((round(width), round(height)), Image.LANCZOS)

    buffer = BytesIO()
    raster.save(buffer, format="PNG")
    return buffer.getvalue(), width, height


def draw_ascii_art(svg, lines, x, y, delay):
    """Draws the ASCII portrait, wiping in top to bottom like it's printing out."""
    data, width, height = render_ascii_portrait(lines)

    reveal = _wipe_reveal_down(svg, x, y, width, height, delay, ASCII_REVEAL_DURATION)
    reveal.append(draw.Image(x, y, width, height, data=data, embed=True, mime_type="image/png"))

    return width, height


def draw_info_row(svg, icon, label, value, x, y, delay):
    """Draws one labelled fact row (its icon, label and value) fading up into place."""
    row = draw.Group()
    row.append(
        get_file_icon(
            icon, x=x + INFO_ICON_SIZE / 2, y=y, size=INFO_ICON_SIZE, color=ORANGE, center=True
        )
    )
    label_x = x + INFO_ICON_SIZE + INFO_GAP
    _mono_text(row, label, label_x, y, INFO_FONT_SIZE, fill=ORANGE, weight=500)
    _mono_text(row, value, label_x + INFO_LABEL_WIDTH, y, INFO_FONT_SIZE, weight=500)
    _fade_up(svg, row, delay)


def draw_info_panel(svg, name, username, role, stack, uptime, contact, x, y, delay):
    """Draws the info panel: name, a divider, labelled facts and a row of color swatches."""
    row_y = y

    # Name and handle
    name_text = draw.Text(
        "",
        x=x,
        y=row_y,
        font_size=NAME_SIZE,
        font_family=FONT_MONO,
        font_weight=700,
        dominant_baseline="central",
    )
    name_text.append(draw.TSpan(name, fill=TEXT_COLOR))
    name_text.append(draw.TSpan("@", fill=DIM))
    name_text.append(draw.TSpan(username, fill=BLUE))
    name_row = draw.Group()
    name_row.append(name_text)
    _fade_up(svg, name_row, delay)
    row_y += TITLE_SIZE / 2 + DIVIDER_MARGIN_TOP

    # Dashed divider
    dash_count = round(
        (DIVIDER_WIDTH + DIVIDER_DASH_GAP) / (DIVIDER_DASH_LENGTH + DIVIDER_DASH_GAP)
    )
    divider_width = dash_count * DIVIDER_DASH_LENGTH + (dash_count - 1) * DIVIDER_DASH_GAP
    divider = draw.Group()
    divider.append(
        draw.Line(
            x,
            row_y,
            x + divider_width,
            row_y,
            stroke="#30363d",
            stroke_width=1.2,
            stroke_dasharray=f"{DIVIDER_DASH_LENGTH},{DIVIDER_DASH_GAP}",
        )
    )
    _fade_up(svg, divider, delay + 0.08)
    row_y += DIVIDER_MARGIN_BOTTOM + PROMPT_SIZE / 2

    # Labelled fact rows
    values = [role, stack, uptime, contact]
    for i, ((icon, label), value) in enumerate(zip(INFO_ROWS, values)):
        draw_info_row(svg, icon, label, value, x, row_y, delay + 0.16 + i * 0.08)
        row_y += INFO_ROW_HEIGHT

    # Color swatch grid
    swatch_top = row_y + SWATCH_MARGIN_TOP
    row_y = swatch_top + SWATCH_HEIGHT / 2
    for r, colors in enumerate(SWATCH_ROWS):
        swatch_row = draw.Group()
        swatch_x = x
        for color in colors:
            swatch_row.append(
                draw.Rectangle(
                    swatch_x, row_y - SWATCH_HEIGHT / 2, SWATCH_WIDTH, SWATCH_HEIGHT, fill=color
                )
            )
            swatch_x += SWATCH_WIDTH
        _fade_up(svg, swatch_row, delay + 0.16 + len(INFO_ROWS) * 0.08 + r * 0.08)
        row_y += SWATCH_HEIGHT

    # Trailing blinking cursor
    cursor = draw.Rectangle(
        x,
        row_y + 8,
        8,
        15,
        fill=TEXT_COLOR,
        opacity=0,
        style=f"animation:{CURSOR_BLINK};animation-delay:"
        f"{delay + 0.16 + len(INFO_ROWS) * 0.08 + len(SWATCH_ROWS) * 0.08 + 0.15}s",
    )
    svg.append(cursor)


def build_terminal_hero_card(
    ascii_art=DEFAULT_ASCII_ART,
    name="Parker-Britt",
    username="github",
    role="Pipeline TD",
    stack="Houdini · USD · Python · C++",
    uptime="5y (VFX)",
    contact="parker@parkerbritt.com",
    terminal_title="parker-b@github: ~",
    command="fetch --github",
    info_offset_x=INFO_PANEL_OFFSET_X,
    info_offset_y=INFO_PANEL_OFFSET_Y,
    ascii_offset_x=ASCII_PANEL_OFFSET_X,
    ascii_offset_y=ASCII_PANEL_OFFSET_Y,
):
    """Returns the SVG for a terminal styled hero card introducing a README's author."""
    lines = ascii_art.strip("\n").split("\n")

    height = HEADER_HEIGHT + CONTENT_HEIGHT
    border_width = 1
    half_border = border_width / 2

    svg = draw.Drawing(CARD_WIDTH + MARGIN * 2, height + MARGIN * 2, origin=(0, 0))
    svg.append(
        draw.Raw("<style>@keyframes cursorBlink{0%,49%{opacity:1}50%,100%{opacity:0}}</style>")
    )

    x = MARGIN + half_border
    y = MARGIN + half_border

    # Card frame
    svg.append(
        draw.Rectangle(
            x,
            y,
            CARD_WIDTH,
            height,
            fill=BACKGROUND_COLOR,
            rx=BORDER_RADIUS,
            stroke="rgba(255,255,255,0.12)",
            stroke_width=border_width,
            filter=get_drop_shadow(opacity=0.4, blur=6, x=0, y=2),
        )
    )

    draw_title_bar(svg, x, y, CARD_WIDTH, terminal_title)

    content_x = x + CONTENT_PADDING_X
    content_y = y + HEADER_HEIGHT + CONTENT_PADDING_TOP

    # Typed command
    prompt_y = content_y + PROMPT_SIZE / 2
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
    row_top = content_y + PROMPT_ROW_HEIGHT + PROMPT_MARGIN_BOTTOM
    draw_loading_bar(svg, content_x, row_top + PROMPT_SIZE / 2, bar_delay, bar_duration)

    result_delay = bar_delay + bar_duration + 0.25

    # ASCII portrait
    ascii_x = content_x + ascii_offset_x
    ascii_y = row_top + ascii_offset_y
    ascii_width, _ = draw_ascii_art(svg, lines, ascii_x, ascii_y, result_delay + 0.4)

    # Info panel
    info_x = ascii_x + ascii_width + ASCII_GAP + info_offset_x
    info_y = row_top + info_offset_y
    draw_info_panel(
        svg,
        name,
        username,
        role,
        stack,
        uptime,
        contact,
        info_x,
        info_y + NAME_SIZE / 2,
        result_delay,
    )

    return svg.as_svg()
