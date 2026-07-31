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
