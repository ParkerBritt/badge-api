"""The pieces a terminal card is assembled from: its frame, prompt, portrait and info panel."""

from typing import NamedTuple

import drawsvg as draw

from src.draw.cards.terminal import theme
from src.draw.cards.terminal.primitives import (
    fade_up,
    mono_text,
    mono_text_dimmed,
    reveal_chars,
    wipe_reveal_down,
)
from src.draw.icons import get_file_icon
from src.draw.shapes import get_drop_shadow
from src.util.text import elide_lines, get_char_width


class InfoRow(NamedTuple):
    """One labelled fact in the info panel, its icon and label drawn in the accent colour."""

    icon: str
    label: str
    value: str
    color: str = theme.DEFAULT_ROW_COLOR


def card_origin():
    """Returns the top-left corner of a terminal card's frame, for laying out before it exists."""
    offset = theme.MARGIN + theme.BORDER_WIDTH / 2
    return offset, offset


def new_terminal_card(width, height):
    """Returns a drawing holding an empty terminal window, its frame set at `card_origin`."""
    x, y = card_origin()

    svg = draw.Drawing(width + theme.MARGIN * 2, height + theme.MARGIN * 2, origin=(0, 0))
    svg.append(draw.Raw(theme.CURSOR_KEYFRAMES))
    svg.append(
        draw.Rectangle(
            x,
            y,
            width,
            height,
            fill=theme.BACKGROUND_COLOR,
            rx=theme.BORDER_RADIUS,
            stroke="rgba(255,255,255,0.12)",
            stroke_width=theme.BORDER_WIDTH,
            filter=get_drop_shadow(opacity=0.4, blur=6, x=0, y=2),
        )
    )
    return svg


def draw_title_bar(svg, x, y, width, title):
    """Draws the terminal window's title bar: three traffic-light dots and a title."""
    r = theme.BORDER_RADIUS
    bar = draw.Path(fill="#0d1117")
    bar.M(x + r, y)
    bar.H(x + width - r)
    bar.A(r, r, 0, 0, 1, x + width, y + r)
    bar.V(y + theme.HEADER_HEIGHT)
    bar.H(x)
    bar.V(y + r)
    bar.A(r, r, 0, 0, 1, x + r, y)
    bar.Z()
    svg.append(bar)
    svg.append(
        draw.Line(
            x,
            y + theme.HEADER_HEIGHT,
            x + width,
            y + theme.HEADER_HEIGHT,
            stroke="rgba(255,255,255,0.08)",
            stroke_width=1,
        )
    )

    dot_y = y + theme.HEADER_HEIGHT / 2
    dot_x = x + theme.DOT_PADDING_X + theme.DOT_RADIUS
    for color in ("#ff5f57", "#febc2e", "#28c840"):
        svg.append(draw.Circle(dot_x, dot_y, theme.DOT_RADIUS, fill=color))
        dot_x += theme.DOT_GAP

    mono_text(
        svg,
        title,
        dot_x - theme.DOT_GAP + theme.DOT_RADIUS + theme.TITLE_GAP,
        dot_y,
        theme.TITLE_SIZE,
        fill=theme.DIM,
    )


def draw_comment(svg, x, y, text, delay):
    """Draws a dim shell comment, the greeting that can sit above the prompt."""
    comment = draw.Group()
    mono_text(comment, f"# {text}", x, y, theme.PROMPT_SIZE, fill=theme.DIM, weight=500)
    fade_up(svg, comment, delay)


def draw_prompt(svg, x, y, command, delay, duration, hide_cursor_at):
    """Draws the typed command prompt, with a cursor that tracks the last typed character."""
    prompt_x = x
    mono_text(svg, ">", prompt_x, y, theme.PROMPT_SIZE, fill=theme.ORANGE, weight=600)
    command_x = prompt_x + get_char_width(">  ", theme.PROMPT_SIZE)

    char_width = reveal_chars(svg, command, command_x, y, theme.PROMPT_SIZE, delay, duration)

    # Blinks while idle, then sits solid once typing starts.
    cursor = draw.Rectangle(
        command_x,
        y - theme.CURSOR_HEIGHT / 2,
        theme.CURSOR_WIDTH,
        theme.CURSOR_HEIGHT,
        fill=theme.TEXT_COLOR,
        style=f"animation:{theme.CURSOR_BLINK} {round(delay)}",
    )
    steps = max(1, len(command))
    x_values = ";".join(str(command_x + i * char_width) for i in range(steps + 1))
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
    char_width = get_char_width("0", theme.PROMPT_SIZE)
    for i, ch in enumerate("[" + "░" * theme.BAR_CHARS + "]"):
        group.append(
            draw.Text(
                ch,
                x=x + i * char_width,
                y=y,
                font_size=theme.PROMPT_SIZE,
                font_family=theme.FONT_MONO,
                font_weight=500,
                fill=theme.TEXT_COLOR,
                dominant_baseline="central",
            )
        )

    fill_x = x + char_width
    reveal_chars(
        svg,
        "█" * theme.BAR_CHARS,
        fill_x,
        y,
        theme.PROMPT_SIZE,
        delay,
        duration,
        hide_at=delay + duration,
    )

    percent_x = x + (theme.BAR_CHARS + 3) * char_width
    for step in range(theme.BAR_CHARS + 1):
        frame = draw.Text(
            f"{step * 100 // theme.BAR_CHARS}%",
            x=percent_x,
            y=y,
            font_size=theme.PROMPT_SIZE,
            font_family=theme.FONT_MONO,
            font_weight=500,
            fill=theme.TEXT_COLOR,
            dominant_baseline="central",
        )
        frame.args["opacity"] = "0"
        step_time = delay + duration * step / theme.BAR_CHARS
        frame.append_anim(
            draw.Animate("opacity", "0.01s", "1", begin=f"{step_time}s", fill="freeze")
        )
        # The last frame stays up, and the group's own fade carries it out.
        if step < theme.BAR_CHARS:
            next_time = delay + duration * (step + 1) / theme.BAR_CHARS
            frame.append_anim(
                draw.Animate("opacity", "0.01s", "0", begin=f"{next_time}s", fill="freeze")
            )
        group.append(frame)

    svg.append(group)


def fit_ascii_art(lines, box_width=theme.ASCII_BOX_WIDTH, box_height=theme.ASCII_BOX_HEIGHT):
    """Returns the font size and drawn size that fit a character grid inside a box.

    e.g. a 93x68 grid in the default box gives a 2.7px font, and a 4x3 grid in
    that same box gives a 44px one, so both drawings take up the same room.
    """
    # Measured at a font size of 1, so the numbers scale straight to whatever fits.
    grid_width = get_char_width("0" * max(len(line.rstrip()) for line in lines), 1)
    grid_height = len(lines) * theme.ASCII_LINE_HEIGHT
    font_size = min(box_width / grid_width, box_height / grid_height)
    return font_size, grid_width * font_size, grid_height * font_size


def draw_ascii_art(
    svg,
    art,
    x,
    y,
    delay,
    box_width=theme.ASCII_BOX_WIDTH,
    box_height=theme.ASCII_BOX_HEIGHT,
):
    """Draws ASCII art as literal characters, wiping in top to bottom like it's printing out.

    The art fills the box whatever its character grid measures, so the layout
    around it never has to move.
    """
    lines = art.strip("\n").split("\n")
    if not any(line.strip() for line in lines):
        return

    font_size, art_width, art_height = fit_ascii_art(lines, box_width, box_height)
    # Centred, since a grid can only fill whichever axis it runs out of room on first.
    art_x = x + (box_width - art_width) / 2
    art_y = y + (box_height - art_height) / 2
    line_height = font_size * theme.ASCII_LINE_HEIGHT
    advance = get_char_width("0", font_size)

    reveal = wipe_reveal_down(svg, x, y, box_width, box_height, delay, theme.ASCII_REVEAL_DURATION)
    for row, line in enumerate(lines):
        line = line.rstrip()
        if not line:
            continue
        text = draw.Text(
            line,
            x=art_x,
            y=art_y + (row + 0.5) * line_height,
            font_size=font_size,
            font_family=theme.FONT_MONO,
            fill=theme.TEXT_COLOR,
            dominant_baseline="central",
        )
        # Held to our own grid so the art measures the same in every renderer.
        text.args["xml:space"] = "preserve"
        text.args["textLength"] = len(line) * advance
        text.args["lengthAdjust"] = "spacing"
        reveal.append(text)


def measure_label_width(rows):
    """Returns the column width that fits every row's label."""
    if not rows:
        return 0
    widest = max(get_char_width(row.label, theme.INFO_FONT_SIZE) for row in rows)
    return widest + theme.INFO_LABEL_PADDING


def wrap_value(value, value_width):
    """Returns the lines a row's value occupies, kept on one line when no width is given."""
    if not value_width:
        return [value]
    return elide_lines(value, value_width, theme.INFO_FONT_SIZE, theme.INFO_VALUE_MAX_LINES) or [
        value
    ]


def draw_info_row(svg, info_row, x, y, delay, label_width, value_width=None):
    """Draws one labelled fact row, its icon, label and value fading up into place.

    A value too long for `value_width` wraps onto further lines, and the row's
    height grows to match. Returns that height.
    """
    row = draw.Group()
    row.append(
        get_file_icon(
            info_row.icon,
            x=x + theme.INFO_ICON_SIZE / 2,
            y=y,
            size=theme.INFO_ICON_SIZE,
            color=info_row.color,
            center=True,
            fallback=theme.FALLBACK_ICON,
        )
    )
    label_x = x + theme.INFO_ICON_SIZE + theme.INFO_GAP
    value_x = label_x + label_width + theme.INFO_VALUE_OFFSET
    mono_text(
        row,
        info_row.label,
        label_x,
        y,
        theme.INFO_FONT_SIZE,
        fill=info_row.color,
        weight=500,
    )

    lines = wrap_value(info_row.value, value_width)
    for i, line in enumerate(lines):
        mono_text_dimmed(
            row,
            line,
            value_x,
            y + i * theme.INFO_LINE_HEIGHT,
            theme.INFO_FONT_SIZE,
            weight=500,
        )

    fade_up(svg, row, delay)
    return theme.INFO_ROW_HEIGHT + (len(lines) - 1) * theme.INFO_LINE_HEIGHT


def draw_swatches(svg, swatch_rows, x, y, delay):
    """Draws the grid of terminal colour swatches, returning its height."""
    row_y = y + theme.SWATCH_MARGIN_TOP + theme.SWATCH_HEIGHT / 2
    for r, colors in enumerate(swatch_rows):
        swatch_row = draw.Group()
        swatch_x = x
        for color in colors:
            swatch_row.append(
                draw.Rectangle(
                    swatch_x,
                    row_y - theme.SWATCH_HEIGHT / 2,
                    theme.SWATCH_WIDTH,
                    theme.SWATCH_HEIGHT,
                    fill=color,
                )
            )
            swatch_x += theme.SWATCH_WIDTH
        fade_up(svg, swatch_row, delay + r * theme.ROW_STAGGER)
        row_y += theme.SWATCH_HEIGHT
    return theme.SWATCH_MARGIN_TOP + len(swatch_rows) * theme.SWATCH_HEIGHT


def draw_name(svg, name, username, x, y, delay):
    """Draws the `name@username` heading, returning the room it takes above the divider."""
    name_text = draw.Text(
        "",
        x=x,
        y=y,
        font_size=theme.NAME_SIZE,
        font_family=theme.FONT_MONO,
        font_weight=700,
        dominant_baseline="central",
    )
    name_text.append(draw.TSpan(name, fill=theme.TEXT_COLOR))
    name_text.append(draw.TSpan("@", fill=theme.DIM))
    name_text.append(draw.TSpan(username, fill=theme.BLUE))
    name_row = draw.Group()
    name_row.append(name_text)
    fade_up(svg, name_row, delay)
    return theme.NAME_ROW_HEIGHT


def draw_divider(svg, x, y, delay, width=theme.DIVIDER_WIDTH):
    """Draws the dashed rule under the heading."""
    dash_count = round(
        (width + theme.DIVIDER_DASH_GAP) / (theme.DIVIDER_DASH_LENGTH + theme.DIVIDER_DASH_GAP)
    )
    dashed_width = (
        dash_count * theme.DIVIDER_DASH_LENGTH + (dash_count - 1) * theme.DIVIDER_DASH_GAP
    )
    divider = draw.Group()
    divider.append(
        draw.Line(
            x,
            y,
            x + dashed_width,
            y,
            stroke="#30363d",
            stroke_width=1.2,
            stroke_dasharray=f"{theme.DIVIDER_DASH_LENGTH},{theme.DIVIDER_DASH_GAP}",
        )
    )
    fade_up(svg, divider, delay)


def draw_info_panel(
    svg,
    x,
    y,
    rows,
    name=None,
    username=None,
    swatches=None,
    label_width=None,
    value_width=None,
    divider_width=theme.DIVIDER_WIDTH,
    delay=0,
):
    """Draws the info panel: a heading, a divider, labelled fact rows and optional colour swatches.

    Rows are `InfoRow`s, and the label column sizes itself to the widest label
    unless `label_width` says otherwise.

    Returns the height the panel occupies. Drawing into a detached group puts
    that measurement in a card's hands before it has to pick its own height.
    """
    if label_width is None:
        label_width = measure_label_width(rows)

    top = y
    row_y = y

    if name:
        row_y += draw_name(svg, name, username, x, row_y, delay)
        row_y += theme.DIVIDER_MARGIN_TOP
        draw_divider(svg, x, row_y, delay + theme.ROW_STAGGER, divider_width)
        row_y += theme.DIVIDER_MARGIN_BOTTOM + theme.PROMPT_SIZE / 2

    row_delay = delay + theme.ROW_STAGGER * 2
    for row in rows:
        row_y += draw_info_row(svg, row, x, row_y, row_delay, label_width, value_width)
        row_delay += theme.ROW_STAGGER

    if swatches:
        row_y += draw_swatches(svg, swatches, x, row_y, row_delay)
        row_delay += len(swatches) * theme.ROW_STAGGER

    # Trailing blinking cursor
    svg.append(
        draw.Rectangle(
            x,
            row_y + 8,
            8,
            15,
            fill=theme.TEXT_COLOR,
            opacity=0,
            style=f"animation:{theme.CURSOR_BLINK} infinite;animation-delay:{row_delay + 0.15}s",
        )
    )

    return row_y - top
