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
