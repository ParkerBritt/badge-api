"""Draws the card showing a user's contribution streak."""

import math
import uuid

import drawsvg as draw

from src.draw.shapes import new_card
from src.draw.theme import STYLE, TEXT
from src.util import github

CARD_WIDTH = 495
PADDING_X = 24
PADDING_Y = 20
COL_GAP_Y = 6

NUMBER_SIZE = 23
LABEL_SIZE = 10
RANGE_SIZE = 10.5
RANGE_MARGIN_TOP = 3

RING_SIZE = 92
RING_STROKE = 8
RING_GAP = 30  # arc length, in the ring's own units, left open at the bottom
RING_MARGIN_BOTTOM = 2
CURRENT_NUMBER_SIZE = 26
FLAME_SIZE = 18
FLAME_PATH = (
    "M12 3q1 4 4 6.5t3 5.5a1 1 0 0 1-14 0 5 5 0 0 1 1-3 1 1 0 0 0 5 0c0-2-1.5-3-1.5-5q0-2 2.5-4"
)

DIVIDER_HEIGHT = 78

SIDE_COLUMN_HEIGHT = NUMBER_SIZE + COL_GAP_Y + LABEL_SIZE + COL_GAP_Y + RANGE_MARGIN_TOP + RANGE_SIZE
CENTER_COLUMN_HEIGHT = (
    RING_SIZE + RING_MARGIN_BOTTOM + COL_GAP_Y + LABEL_SIZE + COL_GAP_Y + RANGE_MARGIN_TOP + RANGE_SIZE
)
ROW_HEIGHT = max(SIDE_COLUMN_HEIGHT, CENTER_COLUMN_HEIGHT)


def draw_glow(svg, card_x, card_y, card_width, card_height, center_x, center_y, radius, color, stops):
    """Draws a soft radial glow, clipped to the card's rounded bounds."""
    gradient = draw.RadialGradient(center_x, center_y, radius)
    for offset, opacity in stops:
        gradient.add_stop(offset, color, opacity=opacity)

    clip = draw.ClipPath()
    clip.append(draw.Rectangle(card_x, card_y, card_width, card_height, rx=STYLE["border_radius"]))

    svg.append(draw.Circle(center_x, center_y, radius, fill=gradient, clip_path=clip))


def draw_divider(svg, x, center_y, height):
    """Draws the faint vertical rule that separates two stat columns."""
    gradient = draw.LinearGradient(x, center_y - height / 2, x, center_y + height / 2)
    gradient.add_stop(0, "#262629", opacity=0)
    gradient.add_stop(0.2, "#262629", opacity=1)
    gradient.add_stop(0.8, "#262629", opacity=1)
    gradient.add_stop(1, "#262629", opacity=0)
    svg.append(draw.Line(x, center_y - height / 2, x, center_y + height / 2, stroke=gradient, stroke_width=1))


def draw_flame(svg, x, y, size, color):
    """Draws the flame icon centered at (x, y)."""
    svg.append(
        draw.Raw(
            f'<svg x="{x - size / 2}" y="{y - size / 2}" width="{size}" height="{size}" viewBox="0 0 24 24" '
            f'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="{FLAME_PATH}"></path></svg>'
        )
    )


def draw_centered_text(svg, text, center_x, y, font_size, fill, font_weight=500, elem_id=None):
    """Draws a line of text horizontally centered on center_x."""
    extra = {"id": elem_id} if elem_id else {}
    svg.append(
        draw.Text(
            text,
            x=center_x,
            y=y,
            font_size=font_size,
            text_anchor="middle",
            **(TEXT | {"fill": fill, "font_weight": font_weight} | extra),
        )
    )


def draw_streak_ring(svg, center_x, center_y, current, longest):
    """Draws the circular progress ring showing the current streak's share of the longest."""
    outer_radius = RING_SIZE / 2
    r = outer_radius - RING_STROKE / 2
    circumference = 2 * math.pi * r
    usable = circumference - RING_GAP
    pct = min(1, current / longest) if longest else 0
    progress_len = usable * pct
    dash_offset = -RING_GAP / 2

    glow = draw.RadialGradient(center_x, center_y, outer_radius)
    glow.add_stop(0, "#ff8a3d", opacity=0.3)
    glow.add_stop(0.72, "#ff8a3d", opacity=0)
    svg.append(
        draw.Circle(
            center_x, center_y, outer_radius, fill=glow,
            style=f"animation: streakGlow 2.6s ease-in-out infinite; transform-origin: {center_x}px {center_y}px;",
        )
    )
    svg.append(draw.Circle(center_x, center_y, outer_radius - 6, fill="#171b21"))

    ring = draw.Group(transform=f"rotate(-90 {center_x} {center_y})")
    ring.append(
        draw.Circle(
            center_x, center_y, r, fill="none", stroke="#2a2118", stroke_width=RING_STROKE,
            stroke_linecap="round", stroke_dasharray=f"{usable:.2f} {RING_GAP:.2f}",
            stroke_dashoffset=f"{dash_offset:.2f}",
        )
    )
    progress_circle = draw.Circle(
        center_x, center_y, r, fill="none", stroke="#ff8a3d", stroke_width=RING_STROKE,
        stroke_linecap="round", stroke_dasharray=f"0 {circumference:.2f}",
        stroke_dashoffset=f"{dash_offset:.2f}",
    )
    progress_circle.append_anim(
        draw.Animate(
            "stroke-dasharray", "1.4s", f"0 {circumference:.2f}",
            to=f"{progress_len:.2f} {circumference - progress_len:.2f}", fill="freeze",
            calcMode="spline", keySplines="0.33 1 0.68 1", keyTimes="0;1",
        )
    )
    ring.append(progress_circle)
    svg.append(ring)

    draw_flame(svg, center_x, center_y - outer_radius + FLAME_SIZE / 2 - 3, FLAME_SIZE, "#ff8a3d")


def draw_stat_column(svg, value, label, date_range, center_x, top_y, elem_id=None):
    """Draws a plain stat column: a big number over its label and date range."""
    y = top_y + NUMBER_SIZE / 2
    draw_centered_text(svg, value, center_x, y, NUMBER_SIZE, "#e8e8ea", font_weight=700, elem_id=elem_id)

    y += NUMBER_SIZE / 2 + COL_GAP_Y + LABEL_SIZE / 2
    draw_centered_text(svg, label.upper(), center_x, y, LABEL_SIZE, "#8a8f98", font_weight=600)

    y += LABEL_SIZE / 2 + COL_GAP_Y + RANGE_MARGIN_TOP + RANGE_SIZE / 2
    draw_centered_text(svg, date_range, center_x, y, RANGE_SIZE, "#565d66")


def draw_current_streak_column(svg, stats, center_x, top_y, elem_id=None):
    """Draws the current streak column: its progress ring over a label and date range."""
    ring_center_y = top_y + RING_SIZE / 2
    draw_streak_ring(svg, center_x, ring_center_y, stats["current_streak"], stats["longest_streak"])
    draw_centered_text(
        svg, str(stats["current_streak"]), center_x, ring_center_y, CURRENT_NUMBER_SIZE, "#ff8a3d",
        font_weight=700, elem_id=elem_id,
    )

    y = top_y + RING_SIZE + RING_MARGIN_BOTTOM + COL_GAP_Y + LABEL_SIZE / 2
    draw_centered_text(svg, "CURRENT STREAK", center_x, y, LABEL_SIZE, "#c98a56", font_weight=600)

    y += LABEL_SIZE / 2 + COL_GAP_Y + RANGE_MARGIN_TOP + RANGE_SIZE / 2
    draw_centered_text(svg, stats["current_range"], center_x, y, RANGE_SIZE, "#565d66")


def build_streak_card(user):
    """Returns the SVG for a card showing a user's total, current and longest contribution streaks."""
    stats = github.get_streak_stats(user)

    height = int(PADDING_Y * 2 + ROW_HEIGHT)
    svg, card_x, card_y = new_card(CARD_WIDTH, height)
    svg.append(
        draw.Raw(
            "<style>"
            "@keyframes streakGlow{0%,100%{opacity:.55;transform:scale(1)}"
            "50%{opacity:1;transform:scale(1.08)}}"
            "</style>"
        )
    )

    draw_glow(
        svg, card_x, card_y, CARD_WIDTH, height, card_x + CARD_WIDTH + 50, card_y + 50, 150,
        "#ff8a3d", [(0, 0.08), (0.55, 0.025), (0.75, 0)],
    )
    draw_glow(
        svg, card_x, card_y, CARD_WIDTH, height, card_x + 60, card_y + height - 30, 140,
        "#58a6ff", [(0, 0.055), (0.55, 0.015), (0.75, 0)],
    )

    content_x = card_x + PADDING_X
    content_width = CARD_WIDTH - PADDING_X * 2
    col_width = content_width / 3
    row_top = card_y + PADDING_Y
    divider_center_y = row_top + ROW_HEIGHT / 2
    side_top = row_top + (ROW_HEIGHT - SIDE_COLUMN_HEIGHT) / 2

    col1_x = content_x + col_width / 2
    divider1_x = content_x + col_width
    col2_x = content_x + col_width + col_width / 2
    divider2_x = content_x + 2 * col_width
    col3_x = content_x + 2 * col_width + col_width / 2

    uid = uuid.uuid4().hex[:8]
    total_id, current_id, longest_id = f"total-{uid}", f"current-{uid}", f"longest-{uid}"

    draw_stat_column(
        svg, f"{stats['total_contributions']:,}", "Total Contributions", stats["total_range"], col1_x, side_top,
        elem_id=total_id,
    )
    draw_divider(svg, divider1_x, divider_center_y, DIVIDER_HEIGHT)
    draw_current_streak_column(svg, stats, col2_x, row_top, elem_id=current_id)
    draw_divider(svg, divider2_x, divider_center_y, DIVIDER_HEIGHT)
    draw_stat_column(
        svg, str(stats["longest_streak"]), "Longest Streak", stats["longest_range"], col3_x, side_top,
        elem_id=longest_id,
    )

    svg.append(draw.Raw(_count_up_script(total_id, current_id, longest_id, stats)))

    return svg.as_svg()


def _count_up_script(total_id, current_id, longest_id, stats):
    """Returns a script that counts each stat number up from zero on load, like the reference."""
    return f"""
<script><![CDATA[
(function() {{
  var duration = 1400;
  var targets = {{
    "{total_id}": {stats['total_contributions']},
    "{current_id}": {stats['current_streak']},
    "{longest_id}": {stats['longest_streak']},
  }};
  var els = {{}};
  for (var id in targets) els[id] = document.getElementById(id);
  function ease(t) {{ return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }}
  var start = null;
  function tick(now) {{
    if (!start) start = now;
    var t = Math.min(1, (now - start) / duration);
    var e = ease(t);
    for (var id in targets) {{
      if (els[id]) els[id].textContent = Math.round(targets[id] * e).toLocaleString();
    }}
    if (t < 1) requestAnimationFrame(tick);
  }}
  requestAnimationFrame(tick);
}})();
]]></script>
"""
