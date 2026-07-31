"""Reads the repo data the cards are built from."""

import os
import time
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import github
import requests
from dotenv import load_dotenv

from src.util.images import fetch_capped

load_dotenv("conf.env")

DEFAULT_USER = os.getenv("DEFAULT_USER", "")

# Path a repo can commit an image to for it to show up behind its card.
THUMBNAIL_PATH = ".github/thumbnail.png"

GRAPHQL_URL = "https://api.github.com/graphql"

# How long a user's queried results stay cached before being re-fetched.
CACHE_TTL = 30 * 60

_cache = {}

# Every owned, non-fork repo's languages, fetched in one paginated round trip
# instead of one REST call per repo.
_TOP_LANGUAGES_QUERY = """
query($login: String!, $after: String) {
  user(login: $login) {
    repositories(first: 100, after: $after, ownerAffiliations: OWNER, isFork: false) {
      pageInfo { hasNextPage endCursor }
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""

_CREATED_AT_QUERY = """
query($login: String!) {
  user(login: $login) { createdAt }
}
"""

# The contribution calendar can only be queried a year at a time, so getting
# a user's whole history means walking their account age in yearly windows.
_CONTRIBUTIONS_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


# Built on first use so the package imports without a token in the environment.
@lru_cache(maxsize=1)
def _client():
    return github.Github(auth=github.Auth.Token(os.getenv("GITHUB_TOKEN")))


def _graphql(query, variables):
    """Runs a query against GitHub's GraphQL API and returns its "data" payload."""
    resp = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers={"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"},
        timeout=10,
    )
    resp.raise_for_status()
    body = resp.json()
    if "errors" in body:
        raise RuntimeError(body["errors"])
    return body["data"]


def get_repo(user, repo):
    return _client().get_user(user).get_repo(repo)


def get_thumbnail(g_repo):
    """Returns the bytes of a repo's committed thumbnail, or None when it has none."""
    try:
        thumbnail = g_repo.get_contents(THUMBNAIL_PATH)
    except github.GithubException:
        return None
    return fetch_capped(thumbnail.download_url)


def get_top_languages(user, limit=6):
    """Returns a user's most-used languages, as (name, percent) pairs summing to 100.

    Percentages are relative to the returned languages only.
    """
    cache_key = ("top_languages", user)
    cached = _cache.get(cache_key)
    if cached and cached[0] > time.monotonic():
        return cached[1]

    totals = {}
    after = None
    while True:
        data = _graphql(_TOP_LANGUAGES_QUERY, {"login": user, "after": after})
        repos = data["user"]["repositories"]
        for repo in repos["nodes"]:
            for edge in repo["languages"]["edges"]:
                name = edge["node"]["name"]
                totals[name] = totals.get(name, 0) + edge["size"]

        if not repos["pageInfo"]["hasNextPage"]:
            break
        after = repos["pageInfo"]["endCursor"]

    top = sorted(totals.items(), key=lambda item: item[1], reverse=True)[:limit]
    total_bytes = sum(byte_count for _, byte_count in top)
    result = (
        []
        if not total_bytes
        else [(language, byte_count / total_bytes * 100) for language, byte_count in top]
    )

    _cache[cache_key] = (time.monotonic() + CACHE_TTL, result)
    return result


def get_streak_stats(user):
    """Returns a user's contribution totals and streaks, aggregated over their whole history.

    The result has `total_contributions`, `current_streak` and `longest_streak` counts,
    alongside a human-readable date range for each (`total_range`, `current_range`,
    `longest_range`).
    """
    cache_key = ("streak_stats", user)
    cached = _cache.get(cache_key)
    if cached and cached[0] > time.monotonic():
        return cached[1]

    created_at = _parse_datetime(_graphql(_CREATED_AT_QUERY, {"login": user})["user"]["createdAt"])
    now = datetime.now(timezone.utc)

    days = {}
    window_start = created_at
    while window_start < now:
        window_end = min(window_start + timedelta(days=365), now)
        data = _graphql(
            _CONTRIBUTIONS_QUERY,
            {"login": user, "from": window_start.isoformat(), "to": window_end.isoformat()},
        )
        calendar = data["user"]["contributionsCollection"]["contributionCalendar"]
        for week in calendar["weeks"]:
            for day in week["contributionDays"]:
                date = datetime.strptime(day["date"], "%Y-%m-%d").date()
                days[date] = day["contributionCount"]
        window_start = window_end

    ordered_days = sorted(days.items())
    longest_streak, longest_start, longest_end = _longest_run(ordered_days)
    current_streak, current_start, current_end = _current_run(ordered_days)

    result = {
        "total_contributions": sum(count for _, count in ordered_days),
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_range": _format_range(created_at.date(), now.date(), present=True),
        "current_range": _format_range(current_start, current_end) if current_streak else "",
        "longest_range": _format_range(longest_start, longest_end) if longest_streak else "",
    }

    _cache[cache_key] = (time.monotonic() + CACHE_TTL, result)
    return result


def _parse_datetime(iso_string):
    return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))


def _longest_run(ordered_days):
    """Returns the length, start date and end date of the longest run of contributed days."""
    best_length, best_start, best_end = 0, None, None
    run_length, run_start = 0, None
    for date, count in ordered_days:
        if count > 0:
            if run_length == 0:
                run_start = date
            run_length += 1
            if run_length > best_length:
                best_length, best_start, best_end = run_length, run_start, date
        else:
            run_length = 0
    return best_length, best_start, best_end


def _current_run(ordered_days):
    """Returns the length, start date and end date of the streak ending today.

    Today is skipped when it has no contributions yet, since the day isn't over.
    """
    index = len(ordered_days) - 1
    if index >= 0 and ordered_days[index][1] == 0:
        index -= 1

    length, start, end = 0, None, ordered_days[index][0] if index >= 0 else None
    while index >= 0 and ordered_days[index][1] > 0:
        start = ordered_days[index][0]
        length += 1
        index -= 1
    return length, start, end


def _format_range(start, end, present=False):
    """Formats a date range, showing the year only where it isn't the current one.

    e.g. (2024-01-03, 2024-04-24) -> "Jan 3 – Apr 24, 2024"
    """
    this_year = datetime.now(timezone.utc).year

    def fmt(date, force_year):
        text = date.strftime("%b %-d")
        return f"{text}, {date.year}" if force_year else text

    if present:
        return f"{fmt(start, start.year != this_year)} – Present"
    return f"{fmt(start, start.year != end.year)} – {fmt(end, end.year != this_year)}"
