"""The look every card shares."""

FONT_FAMILY = (
    "Liberation Mono,Consolas,Menlo,Monaco,"
    "Lucida Console,DejaVu Sans Mono,Bitstream Vera Sans Mono,"
    "Courier New,serif"
)

STYLE = dict(
    card_width=421,
    background="#12161c",
    border="#262629",
    border_width=1,
    border_radius=20,
    margin=10,  # makes room for the shadow
    padding=18,  # separates the card edge from its inner content
    title_size=23,
    text_size=12,
    text_color="#c4c4c4",
    shadow_opacity=0.5,
    shadow_blur=7,
)

# Text attributes shared by every string drawn on a card.
TEXT = dict(
    font_family=FONT_FAMILY,
    fill="white",
    dominant_baseline="central",
    font_weight=100,
)
