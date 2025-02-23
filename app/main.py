from fastapi import FastAPI, Response
import colorsys

app = FastAPI()

icons = {"maya" : """<path d="M4.348 0 .69 2.203v16.875l3.657-2.203h17.297V1.219c0-.67-.551-1.219-1.22-1.219H4.349zm18.297 3.75v14.125H4.627l-1.943 1.17v3.736c0 .67.55 1.219 1.218 1.219H23.31V3.75h-.664zm-14.471.025h2.937l1.885 7.508 1.977-7.48-.012-.028h2.857v9.354h-2.216v-6.04l-1.565 6.026v.014h-2.203l-1.656-6.28v6.28H8.174V3.775zm1.33 14.762h1.18l1.068 3.543h-.902l-.217-.773H9.568l-.197.773h-.88l1.013-3.543zm1.918 0h.932l.648 1.494.643-1.494h.894l-1.113 2.133v1.41h-.887v-1.406l-1.117-2.137zm3.826 0h1.18l1.068 3.543h-.9l-.217-.773h-1.065l-.197.773h-.88l1.011-3.543zm-5.156.582-.362 1.53h.73l-.368-1.53zm5.744 0-.36 1.53h.73l-.37-1.53z"/> """,
         "c" : """<path d="M16.5921 9.1962s-.354-3.298-3.627-3.39c-3.2741-.09-4.9552 2.474-4.9552 6.14 0 3.6651 1.858 6.5972 5.0451 6.5972 3.184 0 3.5381-3.665 3.5381-3.665l6.1041.365s.36 3.31-2.196 5.836c-2.552 2.5241-5.6901 2.9371-7.8762 2.9201-2.19-.017-5.2261.034-8.1602-2.97-2.938-3.0101-3.436-5.9302-3.436-8.8002 0-2.8701.556-6.6702 4.047-9.5502C7.444.72 9.849 0 12.254 0c10.0422 0 10.7172 9.2602 10.7172 9.2602z"/>""",
         "houdini" : """<path d="M0 19.635V24h3.824A8.662 8.662 0 0 1 0 19.635zm16.042-4.555c0-4.037-3.253-7.92-8.111-8.089C4.483 6.873 1.801 8.136 0 10.005v4.209c1.224-3.549 4.595-5.158 7.419-5.128 3.531.041 6.251 2.703 6.275 5.72 0 2.878-1.183 4.992-4.436 5.516-1.774.296-4.548-.754-4.436-3.434.065-1.381 1.138-2.162 2.366-2.106-1.207 1.618.39 2.801 1.52 2.561a2.51 2.51 0 0 0 1.966-2.502c0-1.017-.958-2.662-3.333-2.6-2.936.068-4.785 2.183-4.85 4.797-.071 3.28 3.007 5.457 6.174 5.483 4.633.059 7.395-2.984 7.377-7.441zM0 0v6.906a12.855 12.855 0 0 1 7.931-2.609c6.801 0 11.134 4.762 11.131 10.765 0 4.17-1.946 7.308-4.995 8.938H24V0H0z"/>""",
         "python" : """<path d="M14.25.18l.9.2.73.26.59.3.45.32.34.34.25.34.16.33.1.3.04.26.02.2-.01.13V8.5l-.05.63-.13.55-.21.46-.26.38-.3.31-.33.25-.35.19-.35.14-.33.1-.3.07-.26.04-.21.02H8.77l-.69.05-.59.14-.5.22-.41.27-.33.32-.27.35-.2.36-.15.37-.1.35-.07.32-.04.27-.02.21v3.06H3.17l-.21-.03-.28-.07-.32-.12-.35-.18-.36-.26-.36-.36-.35-.46-.32-.59-.28-.73-.21-.88-.14-1.05-.05-1.23.06-1.22.16-1.04.24-.87.32-.71.36-.57.4-.44.42-.33.42-.24.4-.16.36-.1.32-.05.24-.01h.16l.06.01h8.16v-.83H6.18l-.01-2.75-.02-.37.05-.34.11-.31.17-.28.25-.26.31-.23.38-.2.44-.18.51-.15.58-.12.64-.1.71-.06.77-.04.84-.02 1.27.05zm-6.3 1.98l-.23.33-.08.41.08.41.23.34.33.22.41.09.41-.09.33-.22.23-.34.08-.41-.08-.41-.23-.33-.33-.22-.41-.09-.41.09zm13.09 3.95l.28.06.32.12.35.18.36.27.36.35.35.47.32.59.28.73.21.88.14 1.04.05 1.23-.06 1.23-.16 1.04-.24.86-.32.71-.36.57-.4.45-.42.33-.42.24-.4.16-.36.09-.32.05-.24.02-.16-.01h-8.22v.82h5.84l.01 2.76.02.36-.05.34-.11.31-.17.29-.25.25-.31.24-.38.2-.44.17-.51.15-.58.13-.64.09-.71.07-.77.04-.84.01-1.27-.04-1.07-.14-.9-.2-.73-.25-.59-.3-.45-.33-.34-.34-.25-.34-.16-.33-.1-.3-.04-.25-.02-.2.01-.13v-5.34l.05-.64.13-.54.21-.46.26-.38.3-.32.33-.24.35-.2.35-.14.33-.1.3-.06.26-.04.21-.02.13-.01h5.84l.69-.05.59-.14.5-.21.41-.28.33-.32.27-.35.2-.36.15-.36.1-.35.07-.32.04-.28.02-.21V6.07h2.09l.14.01zm-6.47 14.25l-.23.33-.08.41.08.41.23.33.33.23.41.08.41-.08.33-.23.23-.33.08-.41-.08-.41-.23-.33-.33-.23-.41-.08-.41.08z"/>""",
         "fastapi" : """<path d="M12 .0387C5.3729.0384.0003 5.3931 0 11.9988c-.001 6.6066 5.372 11.9628 12 11.9625 6.628.0003 12.001-5.3559 12-11.9625-.0003-6.6057-5.3729-11.9604-12-11.96m-.829 5.4153h7.55l-7.5805 5.3284h5.1828L5.279 18.5436q2.9466-6.5444 5.892-13.0896"/>""",
         }


def get_char_width(_string: str):
    return len(_string)*7.83
    # WIDTH_DICT={'0': 9, '1': 7, '2': 9, '3': 10, '4': 10, '5': 9, '6': 9, '7': 9, '8': 9, '9': 9, 'a': 8, 'b': 9, 'c': 8, 'd': 9, 'e': 9, 'f': 6, 'g': 9, 'h': 9, 'i': 4, 'j': 5, 'k': 8, 'l': 4, 'm': 13, 'n': 9, 'o': 9, 'p': 9, 'q': 9, 'r': 6, 's': 8, 't': 5, 'u': 9, 'v': 8, 'w': 12, 'x': 8, 'y': 8, 'z': 8, 'A': 10, 'B': 10, 'C': 11, 'D': 11, 'E': 9, 'F': 9, 'G': 11, 'H': 11, 'I': 4, 'J': 8, 'K': 10, 'L': 8, 'M': 13, 'N': 11, 'O': 11, 'P': 10, 'Q': 11, 'R': 10, 'S': 10, 'T': 10, 'U': 11, 'V': 10, 'W': 14, 'X': 10, 'Y': 10, 'Z': 9, '!': 4, '"': 6, '#': 10, '$': 10, '%': 12, '&': 10, "'": 3, '(': 5, ')': 5, '*': 8, '+': 10, ',': 4, '-': 7, '.': 4, '/': 5, ':': 4, ';': 4, '<': 10, '=': 10, '>': 10, '?': 8, '@': 14, '[': 5, '\\': 5, ']': 5, '^': 7, '_': 8, '`': 7, '{': 5, '|': 5, '}': 5, '~': 10, ' ': 4}
    # width = 0
    # for char in _string:
    #     width+=WIDTH_DICT[char]

    # return width

def get_icon(icon_name: str) -> str:
    if(icon_name.lower() not in icons):
        return ""
    return icons[icon_name.lower()]

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
