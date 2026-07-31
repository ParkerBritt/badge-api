from unittest import mock

import requests

from src.util.images import MAX_BACKGROUND_BYTES, fetch_capped


def fake_response(chunks, raises=None):
    resp = mock.Mock()
    resp.iter_content.return_value = iter(chunks)
    if raises:
        resp.raise_for_status.side_effect = raises
    return resp


def test_returns_body_under_cap():
    with mock.patch("src.util.images.requests.get", return_value=fake_response([b"ab", b"cd"])):
        assert fetch_capped("http://x") == b"abcd"


def test_drops_body_over_cap():
    oversized = [b"x" * (MAX_BACKGROUND_BYTES + 1)]
    with mock.patch("src.util.images.requests.get", return_value=fake_response(oversized)):
        assert fetch_capped("http://x") is None


def test_returns_none_on_request_failure():
    with mock.patch("src.util.images.requests.get", side_effect=requests.RequestException):
        assert fetch_capped("http://x") is None


def test_returns_none_on_error_status():
    bad = fake_response([], raises=requests.HTTPError)
    with mock.patch("src.util.images.requests.get", return_value=bad):
        assert fetch_capped("http://x") is None
