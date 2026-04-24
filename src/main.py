from fastapi import FastAPI, Response
import os
import re
import colorsys, os
from typing import Optional
from simplepycons import all_icons
import httpx
import colorsys
import drawsvg as draw

app = FastAPI()


def get_char_width(_string: str):
    return len(_string) * 7.83  # using mono font


def get_icon(icon_name: str) -> str:
    """
    Fetch the svg path for the desired simple icon

    Args:
        icon_name (str): The string name for the desired icon

    Returns:
        string: svg path for the desired simple icon
    """

    icon_name = icon_name.lower()
    if icon_name not in all_icons.names():
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
    hex_color = hex_color.lstrip("#")  # Remove '#' if present
    if len(hex_color) != 6:
        raise ValueError("Invalid hex color format. Must be 6 characters long.")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


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
    status_names = {
        "SUCCESS": "passing",
        "FAILURE": "failing",
    }

    status_colors = {
        "SUCCESS": "44cc11",
        "FAILURE": "ff3e3e",
    }

    # Default status
    job_status = None

    print(f"fetching job {job} number {build}")

    jenkins_ip = os.getenv("JENKINS_IP", "0.0.0.0")
    jenkins_port = os.getenv("JENKINS_PORT", "80")
    request_str = (
        f"http://{jenkins_ip}:{jenkins_port}/job/{job}/{build}/api/json?pretty=true"
    )

    print(f"making request: {request_str}")
    try:
        async with httpx.AsyncClient() as client:
            jenkins_response = await client.get(request_str, timeout=5)
            jenkins_response.raise_for_status()

        job_data = jenkins_response.json()
        if "result" not in job_data:
            print("ERROR: no result in jenkins json")

        job_status = job_data["result"]
        print("job status: {job_status}")

    except httpx.HTTPStatusError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except httpx.ConnectError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except httpx.TimeoutException as timeout_err:
        print(f"Request timed out: {timeout_err}")

    status_text = status_names.get(job_status, "Null")
    status_color = status_colors.get(job_status, "2e3846")

    # generate image
    svg = build_standard_badge(
        prefix="build ", label=status_text, color="2e3846", label_color=status_color
    )

    # return response
    response = Response(content=svg, media_type="image/svg+xml")
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response


@app.get("/badge")
async def badge(label: str = "", icon: str = "", color: str = "FF4713"):

    # generate image
    svg = build_standard_badge(label=label.upper(), icon=icon, color=color)

    # return response
    response = Response(content=svg, media_type="image/svg+xml")
    response.headers["Cache-Control"] = "public, max-age=86400"
    return response


@app.get("/button")
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
    label_color: str = "FF4713",
) -> str:
    display_text = prefix + label
    text_width = get_char_width(display_text)
    label_width = get_char_width(label)

    rect_height = 28
    icon_width = 14
    left_padding = 9

    icon_svg = get_icon(icon)
    has_icon = icon_svg != ""
    has_label = prefix != ""

    text_x = (left_padding + icon_width) * has_icon + left_padding
    rect_width = text_x + text_width + left_padding
    if has_label:
        rect_width += 9  # prefix padding
    text_rect_width = label_width + left_padding * 2

    # Darker gradient stop
    bg_hex = "#" + color
    h, s, v = colorsys.rgb_to_hsv(*hex_to_rgb(bg_hex))
    bg_alt_hex = rgb_to_hex(colorsys.hsv_to_rgb(h, s, max(v * 0.75, 0)))

    output = draw.Drawing(rect_width, rect_height, origin=(0, 0))

    # Gradient
    gradient = draw.LinearGradient(
        rect_width * 0.2,
        0,
        rect_width * 0.2,
        rect_height,
    )
    gradient.add_stop(0, bg_hex)
    gradient.add_stop(1, bg_alt_hex)

    # Drop shadow
    shadow = draw.Filter(width=120, height=120)
    for item in (
        draw.FilterItem("feOffset", in_="SourceAlpha", dx=2, dy=2, result="offsetOut"),
        draw.FilterItem(
            "feGaussianBlur", in_="offsetOut", stdDeviation=1.8, result="blurOut"
        ),
        draw.FilterItem(
            "feFlood", flood_color="black", flood_opacity=0.3, result="colorOut"
        ),
        draw.FilterItem(
            "feComposite", in_="colorOut", in2="blurOut", operator="in", result="shadow"
        ),
    ):
        shadow.append(item)
    merge = draw.FilterItem("feMerge")
    merge.append(draw.FilterItem("feMergeNode", in_="shadow"))
    merge.append(draw.FilterItem("feMergeNode", in_="SourceGraphic"))
    shadow.append(merge)

    # Main background
    output.append(draw.Rectangle(0, 0, rect_width, rect_height, fill=gradient, rx=8))

    # Label background (right side)
    if has_label:
        output.append(
            draw.Rectangle(
                rect_width - text_rect_width,
                0,
                text_rect_width,
                rect_height,
                fill=f"#{label_color}",
                rx=8,
            )
        )

    # Icon
    if has_icon:
        group = draw.Group(
            transform=f"translate({left_padding},{rect_height / 2 - icon_width / 2})",
            fill="white",
            filter=shadow,
        )
        group.append(
            draw.Raw(
                f'<svg role="img" width="{icon_width}" height="{icon_width}" '
                f'viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">{icon_svg}</svg>'
            )
        )
        output.append(group)

    # Text
    # TODO: move to constant
    font_family = (
        "monospace,Liberation Mono,Consolas,Menlo,Monaco,"
        "Lucida Console,DejaVu Sans Mono,Bitstream Vera Sans Mono,"
        "Courier New,serif"
    )
    text_kwargs = dict(
        font_family=font_family,
        fill="white",
        dominant_baseline="middle",
        text_rendering="geometricPrecision",
        font_weight="bold",
    )
    text_y = rect_height / 2 + 1

    if has_label:
        output.append(draw.Text(prefix, 13, text_x, text_y, **text_kwargs))
    output.append(
        draw.Text(
            label,
            13,
            rect_width - text_rect_width + left_padding,
            text_y,
            **text_kwargs,
        )
    )

    return output.as_svg()
