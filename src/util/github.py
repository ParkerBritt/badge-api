"""Reads the repo data the cards are built from."""

import os
from functools import lru_cache

import github
from dotenv import load_dotenv

from src.util.images import fetch_capped

load_dotenv("conf.env")

DEFAULT_USER = os.getenv("DEFAULT_USER", "")

# Path a repo can commit an image to for it to show up behind its card.
THUMBNAIL_PATH = ".github/thumbnail.png"


# Built on first use so the package imports without a token in the environment.
@lru_cache(maxsize=1)
def _client():
    return github.Github(auth=github.Auth.Token(os.getenv("GITHUB_TOKEN")))


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
    totals = {}
    for repo in _client().get_user(user).get_repos():
        if repo.fork:
            continue
        for language, byte_count in repo.get_languages().items():
            # The API response includes a "url" field alongside the real languages.
            if not isinstance(byte_count, int):
                continue
            totals[language] = totals.get(language, 0) + byte_count

    top = sorted(totals.items(), key=lambda item: item[1], reverse=True)[:limit]
    total_bytes = sum(byte_count for _, byte_count in top)
    if not total_bytes:
        return []
    return [(language, byte_count / total_bytes * 100) for language, byte_count in top]
