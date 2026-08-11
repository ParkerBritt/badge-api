def hex_to_rgb(hex_color):
    """Returns the 0-255 (R, G, B) tuple for a hex color, so "FF5733" gives (255, 87, 51)."""
    hex_color = hex_color.lstrip("#")  # Remove '#' if present
    if len(hex_color) != 6:
        raise ValueError("Invalid hex color format. Must be 6 characters long.")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    """Returns the hex color for a 0-255 (R, G, B) tuple, so (255, 87, 51) gives "#FF5733"."""
    if not all(0 <= val <= 255 for val in rgb):
        raise ValueError(f"RGB values must be in the range 0-255. {rgb}")
    return "#{:02X}{:02X}{:02X}".format(*map(int, rgb))


def get_relative_luminance(hex_color):
    """Returns the WCAG relative luminance of a hex color, from 0 (black) to 1 (white).

    This is the brightness measure contrast ratios are built on, so it's what
    decides whether black or white text will read clearly against a given color.
    """

    def linearize(channel):
        value = channel / 255
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4

    r, g, b = (linearize(c) for c in hex_to_rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_readable_text_color(hex_color):
    """Returns near-black or near-white, whichever contrasts more with the given background."""
    luminance = get_relative_luminance(hex_color)
    contrast_with_white = 1.05 / (luminance + 0.05)
    contrast_with_black = (luminance + 0.05) / 0.05
    return "#f5f5f5" if contrast_with_white >= contrast_with_black else "#1a1a1a"
