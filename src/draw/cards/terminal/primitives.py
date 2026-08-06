"""The drawing and animation building blocks the terminal cards are made of."""

import re

import drawsvg as draw

from src.draw.cards.terminal import theme
from src.util.text import get_char_width


def mono_text(svg, text, x, y, size, fill=theme.TEXT_COLOR, weight=500, anim=None):
    """Draws a line of monospace text."""
    svg.append(
        draw.Text(
            text,
            x=x,
            y=y,
            font_size=size,
            font_family=theme.FONT_MONO,
            font_weight=weight,
            fill=fill,
            dominant_baseline="central",
            style=f"animation:{anim}" if anim else None,
        )
    )


def mono_text_dimmed(svg, text, x, y, size, fill=theme.TEXT_COLOR, weight=500):
    """Draws monospace text where `{...}` segments render dim, e.g. "4y 316d {VFX}" dims "VFX"."""
    node = draw.Text(
        "",
        x=x,
        y=y,
        font_size=size,
        font_family=theme.FONT_MONO,
        font_weight=weight,
        dominant_baseline="central",
    )
    for part in re.split(r"(\{[^}]*\})", text):
        if not part:
            continue
        if part[0] == "{" and part[-1] == "}":
            node.append(draw.TSpan(part[1:-1], fill=theme.DIM))
        else:
            node.append(draw.TSpan(part, fill=fill))
    svg.append(node)


def fade_up(svg, group, delay, duration=0.4):
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


def reveal_chars(
    svg,
    text,
    x,
    y,
    font_size,
    delay,
    duration,
    fill=theme.TEXT_COLOR,
    weight=500,
    hide_at=None,
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
            font_family=theme.FONT_MONO,
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


def wipe_reveal_down(svg, x, y, width, height, delay, duration):
    """Returns a clip path that reveals its contents top-to-bottom, like it's printing out."""
    clip_rect = draw.Rectangle(x, y, width, 0)
    clip_rect.append_anim(
        draw.Animate(
            "height",
            f"{duration}s",
            "0",
            to=str(height),
            begin=f"{delay}s",
            fill="freeze",
        )
    )
    clip = draw.ClipPath()
    clip.append(clip_rect)
    group = draw.Group(clip_path=clip)
    svg.append(group)
    return group
