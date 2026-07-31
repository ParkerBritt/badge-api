"""Reads the repo data the cards are built from."""

import os
import time
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
