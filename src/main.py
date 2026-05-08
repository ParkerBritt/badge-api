from fastapi import FastAPI, Response
import os
import re
import colorsys, os
from typing import Optional
from simplepycons import all_icons
import httpx
import colorsys
import drawsvg as draw
import requests
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import github
import yaml

load_dotenv("conf.env")


def load_language_colors():
    path = os.path.join(os.path.dirname(__file__), "languages.yml")
    with open(path) as f:
        languages = yaml.safe_load(f)

    colors = {}
    for name, data in languages.items():
        if isinstance(data, dict) and data.get("color"):
            colors[name] = data["color"]
    return colors


LANGUAGE_COLORS = load_language_colors()

auth = github.Auth.Token(os.getenv("GITHUB_TOKEN"))
git = github.Github(auth=auth)

FONT_FAMILY = (
    "Liberation Mono,Consolas,Menlo,Monaco,"
    "Lucida Console,DejaVu Sans Mono,Bitstream Vera Sans Mono,"
    "Courier New,serif"
)

app = FastAPI()


def get_char_width(_string: str, font_size=13):
    return len(_string) * 0.7*font_size  # using mono font


def get_simple_icon(icon_name, x=0, y=0, color="white", size=14, center=False):
    icon_name = icon_name.lower()
    if icon_name not in all_icons.names():
        return draw.Raw("")
    return get_icon(all_icons[icon_name].raw_svg, x=x, y=y, color=color, size=size, center=center)

def get_file_icon(icon_name, x=0, y=0, color="white", size=14, center=False):
    icon_path = os.path.join(os.path.dirname(__file__), "..", "icons", icon_name+".svg")
    if not os.path.exists(icon_path):
        return draw.Raw("")
    with open(icon_path) as f:
        svg_content = f.read()
    return get_icon(svg_content, x=x, y=y, color=color, size=size, center=center)

def get_icon(raw_svg, x=0, y=0, color="white", size=14, center=False):
    match = re.search(r"<path[\S\s]*\/>", raw_svg)
    path = match.group() if match else ""
    if center:
        x -= size / 2
        y -= size / 2
    stroke_only = 'fill="none"' in raw_svg
    style = (
        f'fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round"'
    ) if stroke_only else f'fill="{color}"'
    return draw.Raw(
        f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24" {style}>{path}</svg>'
    )


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
    request_str = f"http://{jenkins_ip}:{jenkins_port}/job/{job}/{build}/api/json?pretty=true"

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


@app.get("/repo")
async def repo():

    # generate image
    svg = build_repo_badge(title="Enzo", image_url="https://github.com/ParkerBritt/website/raw/main/screenshots/home_page.png")

    # return response
    response = Response(content=svg, media_type="image/svg+xml")
    response.headers["Cache-Control"] = "public, max-age=86400"
    return response


@app.get("/button")
async def badge(label: str = "", color: str = "2f2f2f", border_color: str = "717171"):

    # generate image
    svg = build_standard_badge(label=label, color=color, border_color=border_color)

    # return response
    response = Response(content=svg, media_type="image/svg+xml")
    response.headers["Cache-Control"] = "public, max-age=86400"
    return response

def blur_filter(blur=5):
    b_filter = draw.Filter(x='-10%', y='-10%', width='120%', height='120%')
    b_filter.append(draw.FilterItem('feGaussianBlur', in_='SourceGraphic', stdDeviation=blur))
    return b_filter

def elide(text: str, recommended_length,font_size) -> str:
    output = list()
    cur_length = -1
    for word in text.split():
        word_length = get_char_width(word, font_size)
        if(cur_length+word_length>recommended_length):
            break
        
        cur_length += word_length+1
        output.append(word)

    return " ".join(output)


def elide_lines(text, max_width, font_size, max_lines=2):
    text = text or ""
    lines = []
    while text and len(lines) < max_lines:
        line = elide(text, max_width, font_size)
        if not line:
            break
        lines.append(line)
        text = text[len(line):].strip()
    if text and lines:
        lines[-1] += "..."
    return lines


def build_repo_badge(user="parkerbritt", repo="enzo", title=None, image_url=None):
    width = 421
    height = 200
    border_width = 1
    half_border = border_width // 2
    border_radius = 15
    bottom_padding = 45

    text_kwargs = dict(
        font_family=FONT_FAMILY,
        fill="white",
        dominant_baseline="central",
        font_weight=100,
    )

    g_repo = git.get_user(user).get_repo(repo)

    svg = draw.Drawing(width + border_width, height + border_width, origin=(0, 0))
    svg.append(
        draw.Rectangle(
            half_border,
            half_border,
            width,
            height,
            fill="#121215",
            rx=border_radius,
            stroke="#262629",
            stroke_width=border_width,
        )
    )

    resp = requests.get(image_url)
    resp.raise_for_status()

    data = resp.content
    w, h = Image.open(BytesIO(data)).size

    image_padding = 20
    image_x = half_border+image_padding//2
    image_y = half_border+image_padding//2
    image_width = width - half_border - image_padding
    image_full_height = image_width * h / w
    image_height = min(height - bottom_padding, image_full_height) - image_padding//2

    title_font_size = 23
    subtitle_font_size = 12

    icon_map = {
        "c++":"cplusplus"
    }

    # Background
    svg.append(
        draw.Rectangle(
            half_border,
            half_border,
            width,
            height,
            fill="#121215",
            rx=border_radius,
            stroke="#2b2c30",
            stroke_width=border_width,
        )
    )

    # Image mask
    clip = draw.ClipPath()
    clip.append(
        draw.Rectangle(
            image_x,
            image_y,
            image_width,
            image_height,
            rx=border_radius,
        )
    )

    # Image Background
    svg.append(
        draw.Rectangle(
            image_x,
            image_y,
            image_width,
            image_height,
            rx=border_radius,
            filter=get_drop_shadow(opacity=0.3, color="black", blur=4,x=4,y=7)
        )
    )


    # Image
    svg.append(
        draw.Image(
            image_x, image_y, image_width, image_full_height, data=data, embed=True,
            clip_path=clip,
            filter=blur_filter(8)
        )
    )

    # Title text
    title_height = 20
    subtitle_height = 10

    svg.append(
        draw.Text(
            title or repo,
            x=image_x+image_width//2,
            y=image_y+image_height//2,
            font_size=title_font_size,
            filter=get_drop_shadow(opacity=0.8, blur=4,x=4,y=2),
            text_anchor='middle',
            **(text_kwargs | {"font_weight":600}),
        )
    )

    # Info items (rendered right-to-left)
    icon_size = 13
    icon_padding = 4
    info_gap = 10
    info_y = height - subtitle_font_size // 2 - subtitle_height

    info_items = [
        {
            "icon": g_repo.language.lower(),
            "icon_fn": get_simple_icon,
            "text": g_repo.language,
            "color": LANGUAGE_COLORS.get(g_repo.language, "white"),
        },
        {
            "icon": "star",
            "icon_fn": get_file_icon,
            "text": g_repo.stargazers_count,
            "skip_if": g_repo.stargazers_count == 0,
            "color":"#ffb300"
        },
        {
            "icon": "git-branch",
            "icon_fn": get_file_icon,
            "text": g_repo.forks_count,
            "skip_if": not g_repo.forks_count,
            "color":"#4893ff"
        },
    ]

    info_x = image_x + image_width
    for item in info_items:
        if item.get("skip_if"):
            continue

        # Text
        text_width = get_char_width(str(item["text"]), subtitle_font_size)
        text_x = info_x - text_width
        color=item.get("color", "white")
        svg.append(
            draw.Text(
                str(item["text"]),
                x=text_x,
                y=info_y,
                font_size=subtitle_font_size,
                **(text_kwargs | {"fill": color}),
                opacity=0.8,
            )
        )

        # Icon
        icon_name = icon_map.get(item["icon"], item["icon"])
        icon_x = text_x - icon_size // 2 - icon_padding
        svg.append(item["icon_fn"](icon_name, size=icon_size, x=icon_x, y=info_y, center=True, color=color))

        info_x = icon_x - icon_size // 2 - info_gap

    # Subtitle (up to 2 lines, fits in space left by info items)
    subtitle_x = 6 + image_padding // 2
    line_height = int(subtitle_font_size * 1.3)
    y = info_y
    for line in reversed(elide_lines(g_repo.description, info_x - subtitle_x, subtitle_font_size)):
        svg.append(draw.Text(line, x=subtitle_x, y=y, font_size=subtitle_font_size, **text_kwargs))
        y -= line_height

    return svg.as_svg()


def get_drop_shadow(opacity=0.3, color="black", blur=1.8, x=2, y=2):
    # Drop shadow
    shadow = draw.Filter(width=120, height=120)
    for item in (
        draw.FilterItem("feOffset", in_="SourceAlpha", dx=x, dy=y, result="offsetOut"),
        draw.FilterItem("feGaussianBlur", in_="offsetOut", stdDeviation=blur, result="blurOut"),
        draw.FilterItem("feFlood", flood_color=color, flood_opacity=opacity, result="colorOut"),
        draw.FilterItem(
            "feComposite", in_="colorOut", in2="blurOut", operator="in", result="shadow"
        ),
    ):
        shadow.append(item)
    merge = draw.FilterItem("feMerge")
    merge.append(draw.FilterItem("feMergeNode", in_="shadow"))
    merge.append(draw.FilterItem("feMergeNode", in_="SourceGraphic"))
    shadow.append(merge)

    return shadow


# TODO: convert to builder design pattern
def build_standard_badge(
    prefix: str = "",
    label: str = "",
    icon: str = "",
    color: str = "FF4713",
    label_color: str = "FF4713",
    border_color: str = None,
) -> str:
    display_text = prefix + label
    text_width = get_char_width(display_text)
    label_width = get_char_width(label)

    rect_height = 28
    icon_width = 14
    left_padding = 9

    has_icon = bool(icon) and icon.lower() in all_icons.names()
    has_label = prefix != ""

    if border_color:
        border_color = "#" + border_color

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
    shadow = get_drop_shadow()

    # Main background
    output.append(
        draw.Rectangle(
            0, 0, rect_width, rect_height, fill=gradient, rx=8, stroke=border_color, stroke_width=1
        )
    )

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
        icon_group = draw.Group(filter=shadow)
        icon_group.append(get_simple_icon(icon, x=left_padding, y=rect_height / 2 - icon_width / 2, size=icon_width))
        output.append(icon_group)

    # Text
    text_kwargs = dict(
        font_family=FONT_FAMILY,
        fill="white",
        dominant_baseline="central",
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
