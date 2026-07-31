"""The API routes."""

import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Response

from src.draw.badge import build_standard_badge
from src.draw.cards.repo import build_repo_card
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
async def button(label: str = "", color: str = "2f2f2f", border_color: str = "717171"):
    return svg_response(build_standard_badge(label=label, color=color, border_color=border_color))


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
