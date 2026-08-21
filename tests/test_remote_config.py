from unittest import mock

from src.util import remote_config
from src.util.images import is_allowed_source
from src.util.remote_config import MAX_CACHE_ENTRIES, fetch_text


def test_published_config_hosts_are_allowed():
    assert is_allowed_source("https://raw.githubusercontent.com/me/me/main/card.yaml")
    assert is_allowed_source("https://gist.githubusercontent.com/me/id/raw/card.yaml")


def test_urls_only_this_server_could_reach_are_refused():
    for url in (
        "http://169.254.169.254/latest/meta-data/",
        "https://169.254.169.254/latest/meta-data/",
        "http://localhost:8000/admin",
        "https://internal.example.com/secrets",
        "file:///etc/passwd",
        "",
        None,
    ):
        assert not is_allowed_source(url)


def test_lookalike_hosts_are_refused():
    for url in (
        "https://raw.githubusercontent.com.evil.test/card.yaml",
        "https://evil.test/raw.githubusercontent.com/card.yaml",
        "https://raw.githubusercontent.com@evil.test/card.yaml",
        "http://raw.githubusercontent.com/me/me/main/card.yaml",
    ):
        assert not is_allowed_source(url)


def test_cache_stops_growing_at_its_cap():
    remote_config._cache.clear()
    with mock.patch.object(remote_config, "fetch_capped", return_value=b"x"):
        for i in range(MAX_CACHE_ENTRIES * 3):
            fetch_text(f"https://raw.githubusercontent.com/{i}")
    assert len(remote_config._cache) == MAX_CACHE_ENTRIES


def test_oldest_entry_is_the_one_dropped():
    remote_config._cache.clear()
    with mock.patch.object(remote_config, "fetch_capped", return_value=b"x"):
        for i in range(MAX_CACHE_ENTRIES + 1):
            fetch_text(f"https://raw.githubusercontent.com/{i}")
    assert "https://raw.githubusercontent.com/0" not in remote_config._cache
    assert f"https://raw.githubusercontent.com/{MAX_CACHE_ENTRIES}" in remote_config._cache


def test_a_failed_fetch_is_retried_sooner_than_a_good_one():
    remote_config._cache.clear()
    with mock.patch.object(remote_config, "fetch_capped", return_value=None):
        assert fetch_text("https://raw.githubusercontent.com/gone") is None
    with mock.patch.object(remote_config, "fetch_capped", return_value=b"back"):
        assert fetch_text("https://raw.githubusercontent.com/gone") is None
        remote_config._cache.clear()
        assert fetch_text("https://raw.githubusercontent.com/gone") == "back"
