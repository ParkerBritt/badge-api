"""The API routes."""

import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Response

from src.draw.badge import build_standard_badge
from src.draw.cards.button import build_button_card
from src.draw.cards.languages import build_languages_card
from src.draw.cards.repo import build_repo_card
from src.draw.cards.spacer import build_spacer_card
from src.draw.cards.streak import build_streak_card
from src.draw.cards.terminal_hero import build_terminal_hero_card
from src.util.github import DEFAULT_USER

load_dotenv("conf.env")

app = FastAPI()

DAY = 86400
HOUR = 3600


def svg_response(svg, max_age=DAY):
    """Returns an SVG response the browser is allowed to cache."""
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": f"public, max-age={max_age}"},
    )


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
async def badge(label: str = "", icon: str = "", color: str = "FF4713"):
    return svg_response(build_standard_badge(label=label.upper(), icon=icon, color=color))


@app.get("/button")
async def button(label: str = ""):
    return svg_response(build_button_card(label=label))


@app.get("/spacer")
async def spacer(width: int = 20, height: int = 1):
    return svg_response(build_spacer_card(width=width, height=height))


@app.get("/repo")
async def repo(
    repo: str,
    user: Optional[str] = None,
    title: Optional[str] = None,
    image_url: Optional[str] = None,
):
    svg = build_repo_card(
        user=user or DEFAULT_USER,
        repo=repo,
        title=title,
        image_url=image_url,
    )
    return svg_response(svg)


@app.get("/languages")
async def languages(user: Optional[str] = None):
    svg = build_languages_card(user or DEFAULT_USER)
    return svg_response(svg)


@app.get("/streak")
async def streak(user: Optional[str] = None):
    svg = build_streak_card(user or DEFAULT_USER)
    return svg_response(svg)


@app.get("/terminal_hero")
async def terminal_hero(
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
