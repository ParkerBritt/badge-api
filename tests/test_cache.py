import threading

from src.util.cache import RenderCache


def test_a_built_card_is_served_without_building_it_again():
    calls = []
    cache = RenderCache()

    for _ in range(3):
        card, fresh = cache.get("k", lambda: calls.append(1) or "card")

    assert (card, fresh) == ("card", True)
    assert len(calls) == 1


def test_a_card_past_its_refresh_window_is_served_while_it_rebuilds():
    cache = RenderCache(refresh_after=0)
    cache.get("k", lambda: "old")

    rebuilt = threading.Event()

    def render():
        rebuilt.set()
        return "new"

    # The waiting request gets the card already on hand, not the rebuild.
    assert cache.get("k", render) == ("old", False)
    assert rebuilt.wait(timeout=5)
    assert cache.get("k", lambda: "unused")[0] == "new"


def test_a_stale_card_rebuilds_once_however_many_requests_arrive():
    cache = RenderCache(refresh_after=0)
    cache.get("k", lambda: "old")

    calls = []
    release = threading.Event()

    def render():
        calls.append(1)
        release.wait(timeout=5)
        return "new"

    for _ in range(8):
        assert cache.get("k", render) == ("old", False)
    release.set()

    assert len(calls) == 1


def test_a_failed_rebuild_leaves_the_last_good_card_serving():
    cache = RenderCache(refresh_after=0)
    cache.get("k", lambda: "good")

    failed = threading.Event()

    def render():
        failed.set()
        raise RuntimeError("github is down")

    assert cache.get("k", render) == ("good", False)
    assert failed.wait(timeout=5)
    assert cache.get("k", lambda: "unused")[0] == "good"


def test_a_card_that_has_never_built_reports_nothing_to_serve():
    cache = RenderCache()

    def render():
        raise RuntimeError("github is down")

    assert cache.get("k", render) == (None, False)


def test_cache_stops_growing_at_its_cap():
    cache = RenderCache(max_entries=4)
    for i in range(20):
        cache.get(i, lambda: "card")

    assert len(cache._entries) == 4
    assert 0 not in cache._entries
    assert 19 in cache._entries
