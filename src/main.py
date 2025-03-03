from fastapi import FastAPI, Response
import colorsys, os
from typing import Optional

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
         "hyprland" : "hyprland.svg"
         }


def get_char_width(_string: str):
    return len(_string)*7.83 # using mono font

def get_icon(icon_name: str) -> str:
    icon_name = icon_name.lower()
    if(icon_name not in icons):
        print(f"WARNING: invalid icon name '{icon_name}'")
        return ""
    file_name = icons[icon_name]
    icon_path = os.path.join(os.path.dirname(__file__), "../icons", file_name)
    if not os.path.exists(icon_path):
        print(f"WARNING: invalid path '{icon_path}'")
        return ""
    else:
        print(f"path valid: {icon_path}")
    with open(icon_path, "rt") as file:
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
    bg_alt_hsv = (bg_alt_hsv[0], bg_alt_hsv[1], max(bg_alt_hsv[2]*0.75,0))

    bg_alt_hex = rgb_to_hex(colorsys.hsv_to_rgb(*bg_alt_hsv))

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
