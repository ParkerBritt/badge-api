from fastapi import FastAPI, Response
import os
import re
import colorsys, os
from typing import Optional
from simplepycons import all_icons
import requests

app = FastAPI()

def get_char_width(_string: str):
    return len(_string)*7.83 # using mono font

def get_icon(icon_name: str) -> str:
    """
    Fetch the svg path for the desired simple icon

    Args:
        icon_name (str): The string name for the desired icon

    Returns:
        string: svg path for the desired simple icon
    """

    icon_name = icon_name.lower()
    if(icon_name not in all_icons.names()):
        print(f"WARNING: invalid icon name '{icon_name}'")
        return ""

    # isolate path
    svg_str = all_icons[icon_name].raw_svg
    svg_path_match = re.search(r"<path[\S\s]*\/>", svg_str)
    if not svg_path_match:
        print(f"WARNING: could not parse svg for icon '{icon_name}'")
        return ""

    svg_path = svg_path_match.group()
    return svg_path



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


@app.get("/jenkins_badge")
async def jenkins_badge(job: str = "", build: str = "lastBuild"):

    print(f"fetching job {job} number {build}")

    jenkins_ip = os.getenv("JENKINS_IP", "0.0.0.0")
    jenkins_port = os.getenv("JENKINS_PORT", "80")
    request_str = f"http://{jenkins_ip}:{jenkins_port}/job/{job}/{build}/api/json?pretty=true"

    print(f"making request: {request_str}")
    try:
        jenkins_response = requests.get(request_str)
        jenkins_response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return
    except requests.exceptions.Timeout as timeout_err:
        print(f"Request timed out: {timeout_err}")
        return
    

    job_data = jenkins_response.json()
    if("result" not in job_data):
        print("ERROR: no result in jenkins json")

    job_status = job_data["result"]
    print("job status: {job_status}")


    status_names = {
        "SUCCESS":"passing",
        "FAILURE":"failing",
    }

    status_colors = {
        "SUCCESS":"44cc11",
        "FAILURE":"ff3e3e",
    }

    status_text = status_names.get(job_status, "NULL")
    status_color = status_colors.get(job_status, "2e3846")

    # generate image
    svg = build_standard_badge(prefix="build ", label=status_text, color="2e3846", label_color=status_color)

    # return response
    response = Response(content=svg, media_type="image/svg+xml")
    response.headers["Cache-Control"] = "public, max-age=86400"
    return response

@app.get("/badge")
async def badge(label: str = "", icon: str = "", color: str = "FF4713"):

    # generate image
    svg = build_standard_badge(label=label.upper(), icon=icon, color=color)

    # return response
    response = Response(content=svg, media_type="image/svg+xml")
    response.headers["Cache-Control"] = "public, max-age=86400"
    return response

def build_standard_badge(
        prefix: str = "", 
        label: str = "",
        icon: str = "",
        color: str = "FF4713",
        label_color: str = "FF4713"
    ) -> str:

    display_text = prefix+label

    text_width = get_char_width(display_text)
    label_width = get_char_width(label)

        

    char_height = 1
    rect_height = 28
    icon_width = 14
    left_padding = 9

    icon_svg = get_icon(icon)
    is_icon = icon_svg == ""
    text_x = (left_padding+icon_width)*(not is_icon)+left_padding
    rect_width = text_x+text_width+left_padding

    has_label = prefix!=""

    if(has_label):
        prefix_padding = 9
        rect_width += prefix_padding

    text_rect_width = label_width+left_padding*2

    bg_hex = "#"+color

    bg_alt_hsv = colorsys.rgb_to_hsv(*hex_to_rgb(bg_hex))
    bg_alt_hsv = (bg_alt_hsv[0], bg_alt_hsv[1], max(bg_alt_hsv[2]*0.75,0))

    bg_alt_hex = rgb_to_hex(colorsys.hsv_to_rgb(*bg_alt_hsv))

    # header
    svg=f"""
<svg
    width="{rect_width}"
    height="28"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
>
"""

    # gradient
    svg += f"""
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

"""

    # main background
    svg += f"""
    <rect x="0" y="0" width="{rect_width}" height="{rect_height}" fill="url(#bg_grad)" rx="8"/>
"""

    # label background
    # only if there's a prefix
    if(has_label):
        svg += f"""
        <rect x="{rect_width-text_rect_width}" width="{text_rect_width}" height="{rect_height}" fill="#{label_color}" rx="8"/>
  
  
"""

    # icon
    svg += f"""
    <g transform="translate({left_padding},{rect_height/2-icon_width/2})" fill="white" filter="url(#drop_shadow_1)">  
        <svg role="img" width="{icon_width}" height="{icon_width}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            {icon_svg}
        </svg>
    </g>

"""

    # prefix text
    if(has_label):
        svg += f"""
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
            {prefix}
        </text>

    """

    # label text
    svg += f"""
    <text
        x="{rect_width-text_rect_width+left_padding}"
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
"""

    # footer
    svg += """
</svg>
"""

    return svg

