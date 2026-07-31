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
