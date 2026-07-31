"""Draws the card showing a user's most-used languages across their repos."""

import drawsvg as draw

from src.draw.icons import get_simple_icon
from src.draw.shapes import new_card
from src.draw.theme import STYLE, TEXT
from src.util import github
from src.util.languages import LANGUAGE_COLORS
from src.util.text import get_char_width

CARD_WIDTH = 421
PADDING_X = 24
PADDING_Y = 18
TITLE_SIZE = 15
TITLE_MARGIN_BOTTOM = 14
BAR_HEIGHT = 10
BAR_MARGIN_BOTTOM = 16
BAR_GAP = 3
ROW_GAP = 12
COL_GAP = 20
ICON_SIZE = 17
TEXT_SIZE = 12
MAX_LANGUAGES = 6

# Controls for the corner glow's size and softness.
GLOW_RADIUS = 140
GLOW_BLUR = 0

# SimpleIcons names for languages GitHub spells differently, or where the
# obvious slug collides with an unrelated brand (e.g. "shell" is a gas company).
ICON_NAMES = {"c++": "cplusplus", "shell": "gnubash"}


def draw_glow(svg, card_x, card_y, card_width, card_height, radius=140, blur=0):
    """Draws the soft blue glow behind the card's top left corner, clipped to its rounded bounds."""
    center_x = card_x - 80 + radius
    center_y = card_y - 100 + radius

    gradient = draw.RadialGradient(center_x, center_y, radius)
    gradient.add_stop(0, "#58a6ff", opacity=0.16)
    gradient.add_stop(0.55, "#58a6ff", opacity=0.05)
    gradient.add_stop(1, "#58a6ff", opacity=0)

    clip = draw.ClipPath()
    clip.append(draw.Rectangle(card_x, card_y, card_width, card_height, rx=STYLE["border_radius"]))

    extra = {}
    if blur:
        blur_filter = draw.Filter(x="-50%", y="-50%", width="200%", height="200%")
        blur_filter.append(draw.FilterItem("feGaussianBlur", stdDeviation=blur))
        extra["filter"] = blur_filter

    svg.append(draw.Circle(center_x, center_y, radius, fill=gradient, clip_path=clip, **extra))


def draw_language_bar(svg, languages, x, y, width):
    """Draws a row of rounded segments sized to each language's share."""
    gap_count = len(languages) - 1
    segment_total = width - gap_count * BAR_GAP
    seg_x = x
    for name, pct in languages:
        seg_width = segment_total * pct / 100
        svg.append(
            draw.Rectangle(
                seg_x,
                y,
                seg_width,
                BAR_HEIGHT,
                rx=BAR_HEIGHT / 2,
                fill=LANGUAGE_COLORS.get(name, "white"),
            )
        )
        seg_x += seg_width + BAR_GAP


def draw_language_row(svg, name, pct, x, y, width):
    """Draws one language's icon, name and percentage within its grid cell."""
    color = LANGUAGE_COLORS.get(name, "white")
    icon_name = ICON_NAMES.get(name.lower(), name.lower())
    svg.append(
        get_simple_icon(icon_name, x=x + ICON_SIZE / 2, y=y, size=ICON_SIZE, color=color, center=True)
    )

    text_x = x + ICON_SIZE + 9
    svg.append(
        draw.Text(
            name,
            x=text_x,
            y=y,
            font_size=TEXT_SIZE,
            **(TEXT | {"fill": STYLE["text_color"], "font_weight": 400}),
        )
    )

    pct_text = f"{pct:.2f}%"
    pct_width = get_char_width(pct_text, TEXT_SIZE)
    svg.append(
        draw.Text(
            pct_text,
            x=x + width - pct_width,
            y=y,
            font_size=TEXT_SIZE,
            **(TEXT | {"fill": "#8a8f98", "font_weight": 400}),
        )
    )


def build_languages_card(user):
    """Returns the SVG for a card showing a user's most-used languages as a bar and list."""
    languages = github.get_top_languages(user, limit=MAX_LANGUAGES)

    rows = -(-len(languages) // 2)  # ceil division
    height = PADDING_Y * 2 + int(TITLE_SIZE * 1.3)
    if languages:
        height += (
            TITLE_MARGIN_BOTTOM
            + BAR_HEIGHT
            + BAR_MARGIN_BOTTOM
            + rows * ICON_SIZE
            + max(rows - 1, 0) * ROW_GAP
        )

    svg, card_x, card_y = new_card(CARD_WIDTH, height)
    draw_glow(svg, card_x, card_y, CARD_WIDTH, height, radius=GLOW_RADIUS, blur=GLOW_BLUR)

    content_x = card_x + PADDING_X
    content_width = CARD_WIDTH - PADDING_X * 2
    title_y = card_y + PADDING_Y + TITLE_SIZE / 2

    svg.append(
        draw.Text(
            "Most Used Languages",
            x=content_x,
            y=title_y,
            font_size=TITLE_SIZE,
            **(TEXT | {"fill": "#e8e8ea", "font_weight": 600}),
        )
    )

    if languages:
        bar_y = title_y + TITLE_SIZE / 2 + TITLE_MARGIN_BOTTOM
        draw_language_bar(svg, languages, content_x, bar_y, content_width)

        col_width = (content_width - COL_GAP) / 2
        row_y = bar_y + BAR_HEIGHT + BAR_MARGIN_BOTTOM + ICON_SIZE / 2
        for i, (name, pct) in enumerate(languages):
            col, row = i % 2, i // 2
            row_x = content_x + col * (col_width + COL_GAP)
            draw_language_row(svg, name, pct, row_x, row_y + row * (ICON_SIZE + ROW_GAP), col_width)

    return svg.as_svg()
