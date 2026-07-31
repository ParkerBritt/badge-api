"""Measures and trims text to fit a fixed width."""


def get_char_width(_string: str, font_size=13):
    return len(_string) * 0.7 * font_size  # using mono font


def elide(text: str, recommended_length, font_size) -> str:
    """Returns as many whole words from the front of the text as fit the given width."""
    output = list()
    cur_length = -1
    for word in text.split():
        word_length = get_char_width(word, font_size)
        if cur_length + word_length > recommended_length:
            break

        cur_length += word_length + 1
        output.append(word)

    return " ".join(output)


def elide_lines(text, max_width, font_size, max_lines=2):
    """Returns the text wrapped to at most max_lines, ending in an ellipsis if it overflows."""
    text = text or ""
    lines = []
    while text and len(lines) < max_lines:
        line = elide(text, max_width, font_size)
        if not line:
            break
        lines.append(line)
        text = text[len(line) :].strip()
    if text and lines:
        lines[-1] += "..."
    return lines
