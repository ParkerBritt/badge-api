"""Utilities for drawing cards."""

import drawsvg as draw

from src.draw.theme import STYLE


def get_drop_shadow(opacity=0.3, color="black", blur=1.8, x=2, y=2):
    """Returns a filter that casts a soft shadow behind whatever it is applied to."""
    shadow = draw.Filter(width=120, height=120)
    for item in (
        draw.FilterItem("feOffset", in_="SourceAlpha", dx=x, dy=y, result="offsetOut"),
        draw.FilterItem("feGaussianBlur", in_="offsetOut", stdDeviation=blur, result="blurOut"),
        draw.FilterItem("feFlood", flood_color=color, flood_opacity=opacity, result="colorOut"),
        draw.FilterItem(
            "feComposite", in_="colorOut", in2="blurOut", operator="in", result="shadow"
        ),
    ):
        shadow.append(item)
    merge = draw.FilterItem("feMerge")
    merge.append(draw.FilterItem("feMergeNode", in_="shadow"))
    merge.append(draw.FilterItem("feMergeNode", in_="SourceGraphic"))
    shadow.append(merge)

    return shadow


def card_clip(card_x, card_y, width, height):
    """Returns a clip path matching a card's rounded rectangle bounds."""
    clip = draw.ClipPath()
    clip.append(draw.Rectangle(card_x, card_y, width, height, rx=STYLE["border_radius"]))
    return clip


def draw_glow(svg, clip_path, center, radius, color, opacity=0.15):
    """Draws a soft radial glow of the given color, clipped to `clip_path`.

    The glow fades from `opacity` at its center to fully transparent at its edge.
    """
    center_x, center_y = center
    gradient = draw.RadialGradient(center_x, center_y, radius)
    gradient.add_stop(0, color, opacity=opacity)
    gradient.add_stop(0.55, color, opacity=opacity * 0.3)
    gradient.add_stop(1, color, opacity=0)

    svg.append(draw.Circle(center_x, center_y, radius, fill=gradient, clip_path=clip_path))


def new_card(width, height):
    """Returns a drawing with the card's rounded background in place, plus its top left corner."""
    border_width = STYLE["border_width"]
    margin = STYLE["margin"]
    half_border = border_width // 2

    svg = draw.Drawing(
        width + border_width + margin * 2,
        height + border_width + margin * 2,
        origin=(0, 0),
    )

    x = margin + half_border
    y = margin + half_border

    svg.append(
        draw.Rectangle(
            x,
            y,
            width,
            height,
            fill=STYLE["background"],
            rx=STYLE["border_radius"],
            stroke=STYLE["border"],
            stroke_width=border_width,
            filter=get_drop_shadow(
                opacity=STYLE["shadow_opacity"], blur=STYLE["shadow_blur"], x=0, y=0
            ),
        )
    )

    return svg, x, y
