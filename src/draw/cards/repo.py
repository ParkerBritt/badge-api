"""Draws the card for a single repo."""

import drawsvg as draw

from src.draw.icons import get_file_icon, get_simple_icon
from src.draw.shapes import new_card
from src.draw.theme import STYLE, TEXT
from src.util import github
from src.util.images import fetch_capped, prepare_background_image
from src.util.languages import LANGUAGE_COLORS
from src.util.text import elide_lines, get_char_width

CARD_WIDTH = 421
CARD_HEIGHT = 120

# SimpleIcons names for languages GitHub spells differently.
ICON_NAMES = {"c++": "cplusplus"}


def draw_background_image(svg, data, x, y, width, height, opacity=0.3):
    """Draws a photo across the whole card, clipped to its rounded corners."""
    try:
        background = prepare_background_image(data, width, height)
    except (OSError, ValueError):
        return

    clip = draw.ClipPath()
    clip.append(draw.Rectangle(x, y, width, height, rx=STYLE["border_radius"]))

    svg.append(
        draw.Image(
            x,
            y,
            width,
            height,
            data=background,
            embed=True,
            mime_type="image/png",
            preserveAspectRatio="none",
            clip_path=clip,
            opacity=opacity,
        )
    )


def draw_info_row(svg, items, right_x, y, font_size):
    """Draws icon and text pairs in a row, filling right to left from right_x."""
    icon_size = 13
    icon_padding = 4
    info_gap = 10

    for item in items:
        text_width = get_char_width(str(item["text"]), font_size)
        text_x = right_x - text_width
        color = item.get("color", "white")
        svg.append(
            draw.Text(
                str(item["text"]),
                x=text_x,
                y=y,
                font_size=font_size,
                **(TEXT | {"fill": color}),
                opacity=0.8,
            )
        )

        icon_name = ICON_NAMES.get(item["icon"], item["icon"])
        icon_x = text_x - icon_size // 2 - icon_padding
        svg.append(
            item["icon_fn"](icon_name, size=icon_size, x=icon_x, y=y, center=True, color=color)
        )

        right_x = icon_x - icon_size // 2 - info_gap

    return right_x


def build_repo_card(user, repo, title=None, image_url=None):
    """Returns the SVG for a card showing a repo's name, description and stats."""
    width = CARD_WIDTH
    height = CARD_HEIGHT
    padding = STYLE["padding"]
    title_font_size = STYLE["title_size"]
    subtitle_font_size = STYLE["text_size"]
    max_subtitle_lines = 2

    g_repo = github.get_repo(user, repo)

    svg, card_x, card_y = new_card(width, height)

    # Background image, falling back to a repo's own committed thumbnail.
    data = fetch_capped(image_url) if image_url else github.get_thumbnail(g_repo)
    if data:
        draw_background_image(svg, data, card_x, card_y, width, height)

    subtitle_x = card_x + padding
    line_height = int(subtitle_font_size * 1.3)
    title_gap = 12

    # The subtitle always reserves a fixed two-line-tall block, so the title above it lands
    # in the same place whether the description wraps to one line or two.
    subtitle_block_top = (
        card_y + height - padding - subtitle_font_size // 2 - max_subtitle_lines * line_height
    )
    title_y = subtitle_block_top - (title_font_size - subtitle_font_size) // 2 - title_gap

    # Subtitle, full width since info items now sit on the title's row.
    subtitle_lines = elide_lines(
        g_repo.description,
        card_x + width - padding - subtitle_x,
        subtitle_font_size,
        max_lines=max_subtitle_lines,
    )
    y = subtitle_block_top + line_height
    for line in subtitle_lines:
        svg.append(
            draw.Text(
                line,
                x=subtitle_x,
                y=y,
                font_size=subtitle_font_size,
                **(TEXT | {"fill": STYLE["text_color"]}),
            )
        )
        y += line_height

    # Info items, bottom-aligned with the title
    info_y = title_y + (title_font_size - subtitle_font_size) // 4

    info_items = []
    if g_repo.language:
        info_items.append(
            {
                "icon": g_repo.language.lower(),
                "icon_fn": get_simple_icon,
                "text": g_repo.language,
                "color": LANGUAGE_COLORS.get(g_repo.language, "white"),
            }
        )
    if g_repo.stargazers_count:
        info_items.append(
            {
                "icon": "star",
                "icon_fn": get_file_icon,
                "text": g_repo.stargazers_count,
                "color": "#ffb300",
            }
        )
    if g_repo.forks_count:
        info_items.append(
            {
                "icon": "git-branch",
                "icon_fn": get_file_icon,
                "text": g_repo.forks_count,
                "color": "#4893ff",
            }
        )

    info_x = draw_info_row(
        svg, info_items, card_x + width - padding, info_y, subtitle_font_size
    )

    # Title, on the info row and shrunk to fit whatever space the info items left
    title_text = title or repo
    title_width = info_x - subtitle_x
    fitted_font_size = min(title_font_size, title_width / get_char_width(title_text, 1))
    svg.append(
        draw.Text(
            title_text,
            x=subtitle_x,
            y=title_y,
            font_size=fitted_font_size,
            **(TEXT | {"font_weight": 600}),
        )
    )

    return svg.as_svg()
