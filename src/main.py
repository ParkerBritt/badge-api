"""The API routes.

Note: the card routes are plain `def` rather than `async def`, since FastAPI threads them.
"""

import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response

from src.draw.badge import build_standard_badge
from src.draw.cards.button import BORDER_RADIUS as BUTTON_BORDER_RADIUS
from src.draw.cards.button import HEIGHT as BUTTON_HEIGHT
from src.draw.cards.button import build_button_card
from src.draw.cards.divider import build_divider_card
from src.draw.cards.image import build_image_card
from src.draw.cards.languages import build_languages_card
from src.draw.cards.repo import build_repo_card
from src.draw.cards.spacer import build_spacer_card
from src.draw.cards.streak import build_streak_card
from src.draw.cards.terminal_dani import build_terminal_dani_card
from src.draw.cards.terminal_hero import build_terminal_hero_card
from src.draw.cards.unavailable import build_unavailable_card
from src.util.cache import RenderCache
from src.util.github import DEFAULT_USER
from src.util.images import is_allowed_source

load_dotenv("conf.env")

DAY = 86400
HOUR = 3600

# Old cards expire quickly, so a broken card fixes itself instead of getting stuck in
# GitHub's image proxy.
STALE_MAX_AGE = 60

CARDS = RenderCache()

app = FastAPI()


def svg_response(svg, max_age=DAY):
    """Returns an SVG response the browser is allowed to cache."""
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": f"public, max-age={max_age}"},
    )


def card_response(build, max_age=DAY, **kwargs):
    """Returns a cached card, falling back to the last good copy instead of failing.

    e.g. `card_response(build_streak_card, user="parker")`, keyed by builder and arguments.

    Caching: if GitHub is unreachable the card just shows slightly old data, rather than
    an error that GitHub's image proxy would remember as a broken image.

    Note: routes that only use local data can't fail this way, so they call `svg_response`.
    """
    key = (build.__name__, tuple(sorted(kwargs.items())))
    card, fresh = CARDS.get(key, lambda: build(**kwargs))
    if card is None:
        return svg_response(build_unavailable_card(), max_age=STALE_MAX_AGE)
    return svg_response(card, max_age=max_age if fresh else STALE_MAX_AGE)


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

    svg = build_standard_badge(
        prefix="build ", label=status_text, color="2e3846", label_color=status_color
    )
    return svg_response(svg, max_age=HOUR)


@app.get("/badge")
def badge(label: str = "", icon: str = "", color: str = "FF4713"):
    return svg_response(build_standard_badge(label=label.upper(), icon=icon, color=color))


@app.get("/button")
def button(
    label: str = "",
    icon: Optional[str] = None,
    color: Optional[str] = None,
    border_color: Optional[str] = None,
    text_color: Optional[str] = None,
    border_radius: int = BUTTON_BORDER_RADIUS,
    height: int = BUTTON_HEIGHT,
):
    return svg_response(
        build_button_card(
            label=label,
            icon=icon,
            color=color,
            border_color=border_color,
            text_color=text_color,
            border_radius=border_radius,
            height=height,
        )
    )


@app.get("/spacer")
def spacer(width: int = 20, height: int = 1):
    return svg_response(build_spacer_card(width=width, height=height))


@app.get("/divider")
def divider(label: str = "", line_length: int = 500):
    return svg_response(build_divider_card(label=label, line_length=line_length))


@app.get("/image")
def image(image_url: str, width: int = 400, height: int = 120):
    # The image is fetched by the server and drawn into the reply, so the host is checked.
    if not is_allowed_source(image_url):
        raise HTTPException(status_code=400, detail="image_url host is not allowed")
    return card_response(build_image_card, image_url=image_url, width=width, height=height)


@app.get("/repo")
def repo(
    repo: str,
    user: Optional[str] = None,
    title: Optional[str] = None,
    image_url: Optional[str] = None,
):
    # A background from a host the server won't fetch falls back to the repo's own thumbnail.
    if image_url and not is_allowed_source(image_url):
        image_url = None

    return card_response(
        build_repo_card,
        user=user or DEFAULT_USER,
        repo=repo,
        title=title,
        image_url=image_url,
    )


@app.get("/languages")
def languages(user: Optional[str] = None):
    return card_response(build_languages_card, user=user or DEFAULT_USER)


@app.get("/streak")
def streak(user: Optional[str] = None):
    return card_response(build_streak_card, user=user or DEFAULT_USER)


@app.get("/terminal_hero")
def terminal_hero(
    name: Optional[str] = None,
    username: Optional[str] = None,
    role: Optional[str] = None,
    stack: Optional[str] = None,
    uptime: Optional[str] = None,
    contact: Optional[str] = None,
    terminal_title: Optional[str] = None,
    command: Optional[str] = None,
    info_offset_x: Optional[int] = None,
    info_offset_y: Optional[int] = None,
):
    kwargs = {
        "name": name,
        "username": username,
        "role": role,
        "stack": stack,
        "uptime": uptime,
        "contact": contact,
        "terminal_title": terminal_title,
        "command": command,
        "info_offset_x": info_offset_x,
        "info_offset_y": info_offset_y,
    }
    svg = build_terminal_hero_card(**{k: v for k, v in kwargs.items() if v is not None})
    return svg_response(svg)


@app.get("/terminal_dani")
def terminal_dani(config_url: Optional[str] = None, ascii_url: Optional[str] = None):
    # These are fetched by the server and drawn into the reply, so the host is checked.
    kwargs = {}
    if config_url and is_allowed_source(config_url):
        kwargs["config_source"] = config_url
    if ascii_url and is_allowed_source(ascii_url):
        kwargs["ascii_source"] = ascii_url
    return card_response(build_terminal_dani_card, max_age=HOUR, **kwargs)
