"""Caches rendered cards so requests don't have to wait on GitHub."""

import threading
import time
from collections import OrderedDict

# How long a card is used before it gets rebuilt in the background.
REFRESH_AFTER = 30 * 60

# Cards are big and callers choose the keys, so the cache needs a limit.
MAX_ENTRIES = 128


class RenderCache:
    """A store of rendered cards, keyed by the arguments used to build them."""

    def __init__(self, refresh_after=REFRESH_AFTER, max_entries=MAX_ENTRIES):
        self._refresh_after = refresh_after
        self._max_entries = max_entries
        self._entries = OrderedDict()
        self._refreshing = set()
        self._guard = threading.Lock()

    def get(self, key, render):
        """Returns a (card, fresh) pair, rebuilding in the background if the card is old.

        Note: (None, False) means there was no cached card and the build failed, so the
        caller should show a stand-in.
        """
        entry = self._entries.get(key)
        if entry is not None:
            rendered_at, card = entry
            self._entries.move_to_end(key)
            if time.monotonic() - rendered_at <= self._refresh_after:
                return card, True
            self._start_refresh(key, render)
            return card, False

        # Nothing cached yet, so this request has to wait for the build.
        try:
            card = render()
        except Exception:
            return None, False
        self._store(key, card)
        return card, True

    def _store(self, key, card):
        self._entries[key] = (time.monotonic(), card)
        self._entries.move_to_end(key)
        while len(self._entries) > self._max_entries:
            self._entries.popitem(last=False)

    def _start_refresh(self, key, render):
        with self._guard:
            if key in self._refreshing:
                return
            self._refreshing.add(key)
        threading.Thread(target=self._refresh, args=(key, render), daemon=True).start()

    def _refresh(self, key, render):
        try:
            self._store(key, render())
        except Exception:
            # If the rebuild fails, the old card stays in the cache.
            pass
        finally:
            with self._guard:
                self._refreshing.discard(key)
