"""Reads card settings a user publishes in their own repo."""

import time
from urllib.parse import urlparse

import yaml

from src.util.images import fetch_capped

# How long a fetched document stays cached before being read again.
CACHE_TTL = 30 * 60

# A failed fetch is retried sooner, so a blip doesn't stick for the full half hour.
FAILURE_TTL = 60

# URLs arrive with requests, so the cache has a ceiling.
MAX_CACHE_ENTRIES = 64

# The only hosts a request may point a card at, since a fetch runs with this server's reach.
ALLOWED_HOSTS = frozenset(
    {
        "raw.githubusercontent.com",
        "gist.githubusercontent.com",
    }
)

_cache = {}


def is_remote(source):
    """Returns whether a source is a URL rather than a path on disk."""
    return source.startswith(("http://", "https://"))


def is_allowed_source(source):
    """Returns whether a caller-supplied URL is one a card may be pointed at.

    e.g. "https://raw.githubusercontent.com/me/me/main/card.yaml" is allowed,
    while "http://169.254.169.254/latest/meta-data" is not.
    """
    parsed = urlparse(source or "")
    return parsed.scheme == "https" and parsed.hostname in ALLOWED_HOSTS


def fetch_text(source, ttl=CACHE_TTL):
    """Returns the text at a URL or local path, or None when it can't be read.

    Caching: only remote sources are cached, so a local file being edited shows
    its changes straight away. The cache holds MAX_CACHE_ENTRIES documents and
    drops the oldest to stay there.
    """
    if not is_remote(source):
        try:
            with open(source, encoding="utf-8") as f:
                return f.read()
        except OSError:
            return None

    cached = _cache.get(source)
    if cached and cached[0] > time.monotonic():
        return cached[1]

    data = fetch_capped(source)
    text = data.decode("utf-8", "replace") if data is not None else None
    _cache[source] = (time.monotonic() + (ttl if text is not None else FAILURE_TTL), text)
    while len(_cache) > MAX_CACHE_ENTRIES:
        del _cache[next(iter(_cache))]
    return text


def fetch_yaml(source, ttl=CACHE_TTL):
    """Returns the parsed mapping at a URL or local path, or None if it's missing or malformed."""
    text = fetch_text(source, ttl)
    if text is None:
        return None
    try:
        parsed = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    return parsed if isinstance(parsed, dict) else None
