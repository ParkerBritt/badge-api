from unittest import mock

import requests

from src.util.images import MAX_BACKGROUND_BYTES, fetch_capped, is_allowed_source

ALLOWED_URL = "https://raw.githubusercontent.com/me/me/main/card.png"


def fake_response(chunks, raises=None):
    resp = mock.Mock()
    resp.is_redirect = False
    resp.iter_content.return_value = iter(chunks)
    if raises:
        resp.raise_for_status.side_effect = raises
    return resp


def fake_redirect(location):
    resp = mock.Mock()
    resp.is_redirect = True
    resp.headers = {"location": location}
    return resp


def test_returns_body_under_cap():
    with mock.patch("src.util.images.requests.get", return_value=fake_response([b"ab", b"cd"])):
        assert fetch_capped(ALLOWED_URL) == b"abcd"


def test_drops_body_over_cap():
    oversized = [b"x" * (MAX_BACKGROUND_BYTES + 1)]
    with mock.patch("src.util.images.requests.get", return_value=fake_response(oversized)):
        assert fetch_capped(ALLOWED_URL) is None


def test_returns_none_on_request_failure():
    with mock.patch("src.util.images.requests.get", side_effect=requests.RequestException):
        assert fetch_capped(ALLOWED_URL) is None


def test_returns_none_on_error_status():
    bad = fake_response([], raises=requests.HTTPError)
    with mock.patch("src.util.images.requests.get", return_value=bad):
        assert fetch_capped(ALLOWED_URL) is None


def test_refuses_a_host_off_the_allowlist():
    with mock.patch("src.util.images.requests.get") as get:
        assert fetch_capped("http://169.254.169.254/latest/meta-data/") is None
    get.assert_not_called()


def test_follows_a_redirect_within_the_allowlist():
    hops = [
        fake_redirect("https://gist.githubusercontent.com/me/id/raw/card.png"),
        fake_response([b"ab", b"cd"]),
    ]
    with mock.patch("src.util.images.requests.get", side_effect=hops):
        assert fetch_capped(ALLOWED_URL) == b"abcd"


def test_refuses_a_redirect_off_the_allowlist():
    hops = [fake_redirect("http://169.254.169.254/latest/meta-data/")]
    with mock.patch("src.util.images.requests.get", side_effect=hops) as get:
        assert fetch_capped(ALLOWED_URL) is None
    assert get.call_count == 1


def test_gives_up_on_a_redirect_loop():
    loop = fake_redirect(ALLOWED_URL)
    with mock.patch("src.util.images.requests.get", return_value=loop):
        assert fetch_capped(ALLOWED_URL) is None


def test_allows_a_user_attachment():
    url = "https://github.com/user-attachments/assets/0c0b427b-b0b9-41fe"
    assert is_allowed_source(url)


def test_refuses_the_rest_of_github():
    assert not is_allowed_source("https://github.com/ParkerBritt/badge-api/settings")


def test_allows_the_bucket_a_user_attachment_redirects_to():
    url = "https://github-production-user-asset-6210df.s3.amazonaws.com/77124738/389315218.png"
    assert is_allowed_source(url)


def test_refuses_an_unrelated_bucket():
    assert not is_allowed_source("https://someone-elses-bucket.s3.amazonaws.com/payload.png")


def test_refuses_a_path_that_walks_out_of_its_corner():
    url = "https://github.com/user-attachments/../../ParkerBritt/private/secret"
    assert not is_allowed_source(url)


def test_refuses_an_encoded_path_that_walks_out_of_its_corner():
    url = "https://github.com/user-attachments/%2e%2e/ParkerBritt/secret"
    assert not is_allowed_source(url)


def test_refuses_a_lookalike_host():
    assert not is_allowed_source("https://github.com.evil.com/user-attachments/x")
