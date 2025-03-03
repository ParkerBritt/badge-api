from fastapi import FastAPI, Response
import colorsys, os

app = FastAPI()

icons = {"maya" : "maya.svg",
         "c" : "c.svg",
         "cpp": "cpp.svg",
         "houdini" : "houdini.svg",
         "python" : "python.svg",
         "fastapi" : "fastapi.svg",
         "linux" : "linux.svg",
         "fedora_linux" : "fedora_linux.svg",
         "rocky_linux" : "rocky_linux.svg",
         }


def get_char_width(_string: str):
    return len(_string)*7.83
    # WIDTH_DICT={'0': 9, '1': 7, '2': 9, '3': 10, '4': 10, '5': 9, '6': 9, '7': 9, '8': 9, '9': 9, 'a': 8, 'b': 9, 'c': 8, 'd': 9, 'e': 9, 'f': 6, 'g': 9, 'h': 9, 'i': 4, 'j': 5, 'k': 8, 'l': 4, 'm': 13, 'n': 9, 'o': 9, 'p': 9, 'q': 9, 'r': 6, 's': 8, 't': 5, 'u': 9, 'v': 8, 'w': 12, 'x': 8, 'y': 8, 'z': 8, 'A': 10, 'B': 10, 'C': 11, 'D': 11, 'E': 9, 'F': 9, 'G': 11, 'H': 11, 'I': 4, 'J': 8, 'K': 10, 'L': 8, 'M': 13, 'N': 11, 'O': 11, 'P': 10, 'Q': 11, 'R': 10, 'S': 10, 'T': 10, 'U': 11, 'V': 10, 'W': 14, 'X': 10, 'Y': 10, 'Z': 9, '!': 4, '"': 6, '#': 10, '$': 10, '%': 12, '&': 10, "'": 3, '(': 5, ')': 5, '*': 8, '+': 10, ',': 4, '-': 7, '.': 4, '/': 5, ':': 4, ';': 4, '<': 10, '=': 10, '>': 10, '?': 8, '@': 14, '[': 5, '\\': 5, ']': 5, '^': 7, '_': 8, '`': 7, '{': 5, '|': 5, '}': 5, '~': 10, ' ': 4}
    # width = 0
    # for char in _string:
    #     width+=WIDTH_DICT[char]

    # return width

def get_icon(icon_name: str) -> str:
    icon_name = icon_name.lower()
    if(icon_name not in icons):
        return ""
    file_name = icons[icon_name]
    with open(os.path.join(os.path.dirname(__file__), "../icons", file_name), "rt") as file:
        return file.read()


def hex_to_rgb(hex_color):
    """
    Convert a hex color string to an RGB tuple.
    
    Args:
        hex_color (str): A hex string (e.g., "#FF5733" or "FF5733")
    
    Returns:
        tuple: An (R, G, B) tuple where each value is 0-255.
    """
    hex_color = hex_color.lstrip('#')  # Remove '#' if present
    if len(hex_color) != 6:
        raise ValueError("Invalid hex color format. Must be 6 characters long.")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    """
    Convert an RGB tuple to a hex color string.
    
    Args:
        rgb (tuple): An (R, G, B) tuple where each value is 0-255.
    
    Returns:
        str: A hex color string (e.g., "#FF5733").
    """
    if not all(0 <= val <= 255 for val in rgb):
        raise ValueError(f"RGB values must be in the range 0-255. {rgb}")
    return "#{:02X}{:02X}{:02X}".format(*map(int, rgb))



@app.get("/badge")
async def generate_svg(label: str = "", icon: str = "", color: str = "#FF4713"):
    label = label.upper()
    label_width = get_char_width(label)
    char_height = 1
    rect_height = 28
    icon_width = 14
    icon_svg = get_icon(icon)
    is_icon = icon_svg == ""
    left_padding = 9
    text_x = (left_padding+icon_width)*(not is_icon)+left_padding
    rect_width = text_x+label_width+left_padding

    bg_hex = "#"+color

    bg_alt_hsv = colorsys.rgb_to_hsv(*hex_to_rgb(bg_hex))
    bg_alt_hsv = (bg_alt_hsv[0], bg_alt_hsv[1], max(bg_alt_hsv[2]-20,0))

    bg_alt_hex = rgb_to_hex(colorsys.hsv_to_rgb(*bg_alt_hsv))
    # bg_alt_hex = bg_hex
    # bg_alt_hex = "#006E95"

    svg=f"""
<svg
    width="{rect_width}"
    height="28"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
>
    <defs>
        <linearGradient id="bg_grad" x1="20%" y1="0%" x2="80%" y2="100%">
            <stop offset="0%" stop-color="{bg_hex}" />
            <stop offset="100%" stop-color="{bg_alt_hex}" />
        </linearGradient>

        <filter id="drop_shadow_1" width="120" height="120">
            <!-- Offset shadow -->
            <feOffset in="SourceAlpha" dx="2" dy="2" result="offsetOut" />
            <!-- Blur the shadow -->
            <feGaussianBlur in="offsetOut" stdDeviation="1.8" result="blurOut" />
            <!-- Set shadow color -->
            <feFlood flood-color="black" flood-opacity="0.3" result="colorOut" />
            <!-- Apply shadow color -->
            <feComposite in="colorOut" in2="blurOut" operator="in" result="shadow" />
            <!-- Merge shadow with original shape -->
            <feMerge>
                <feMergeNode in="shadow" />
                <feMergeNode in="SourceGraphic" />
            </feMerge>
        </filter>
    </defs>

    <rect x="0" y="0" width="{rect_width}" height="{rect_height}" fill="url(#bg_grad)" rx="8"/>
  
  
    <g transform="translate({left_padding},{rect_height/2-icon_width/2})" fill="white" filter="url(#drop_shadow_1)">  
        <svg role="img" width="{icon_width}" height="{icon_width}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            {icon_svg}
        </svg>
    </g>
    <text
        x="{text_x}"
        y="{rect_height/2+char_height}"
        font-family="monospace,Liberation Mono,Consolas,Menlo,Monaco,Lucida Console,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New,serif"
        font-size="13"
        fill="white"
        dominant-baseline="middle"
        text-rendering="geometricPrecision"
        font-weight="bold"
    >
        {label}
    </text>
</svg>
"""
    return Response(content=svg, media_type="image/svg+xml")
