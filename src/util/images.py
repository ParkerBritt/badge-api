from io import BytesIO
from posixpath import normpath
from urllib.parse import unquote, urljoin, urlparse

import requests
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Limits on background images, which can come from a caller-supplied URL.
MAX_BACKGROUND_BYTES = 16 * 1024 * 1024
MAX_BACKGROUND_PIXELS = 50_000_000

# The background is stored this many times smaller than the card and scaled back up on
# display. The averaging that involves is what clears out JPEG block artifacts.
BACKGROUND_DOWNSCALE = 4

# The only hosts a fetch may be pointed at, since a request runs with this server's reach.
# Each maps to the path prefix it is held to, and an empty prefix opens the whole host.
ALLOWED_HOSTS = {
    "raw.githubusercontent.com": "",
    "gist.githubusercontent.com": "",
    "user-images.githubusercontent.com": "",
    "avatars.githubusercontent.com": "",
    # github.com serves far more than assets, so only this one corner of it is allowed.
    "github.com": "/user-attachments/",
}

# The signed bucket a user-attachments link redirects to. GitHub numbers these buckets,
# so the name is matched at both ends rather than in full.
ASSET_BUCKET_PREFIX = "github-production-user-asset"
ASSET_BUCKET_SUFFIX = ".s3.amazonaws.com"

# How many redirects a fetch follows, with every hop held to the same rules.
MAX_REDIRECTS = 3


def _is_asset_bucket(host):
    """Returns whether a host is one of GitHub's numbered attachment buckets.

    e.g. "github-production-user-asset-6210df.s3.amazonaws.com"
    """
    return host.startswith(ASSET_BUCKET_PREFIX) and host.endswith(ASSET_BUCKET_SUFFIX)


def _resolved_path(path):
    """Returns the path a request actually lands on, with "." and ".." resolved.

    e.g. "/user-attachments/../private" -> "/private"

    Note: the HTTP client resolves these segments before sending, so the prefix in
    ALLOWED_HOSTS is matched against the resolved path rather than the raw one.
    """
    resolved = normpath(unquote(path or "/"))
    return resolved + "/" if not resolved.endswith("/") and path.endswith("/") else resolved


def is_allowed_source(source):
    """Returns whether a caller-supplied URL is one this server may fetch.

    e.g. "https://raw.githubusercontent.com/me/me/main/card.png" is allowed,
    while "http://169.254.169.254/latest/meta-data" is not.

    Note: a host may be allowed for only part of its paths, so the path counts
    as much as the host does.
    """
    parsed = urlparse(source or "")
    if parsed.scheme != "https" or not parsed.hostname:
        return False
    if _is_asset_bucket(parsed.hostname):
        return True
    prefix = ALLOWED_HOSTS.get(parsed.hostname)
    return prefix is not None and _resolved_path(parsed.path).startswith(prefix)


def fetch_capped(url):
    """Returns the bytes at a URL, or None if it fails or exceeds the size cap.

    Only a source is_allowed_source accepts can be reached. Redirects are followed
    one hop at a time and each new location is checked the same way, so an allowed
    host can't bounce the request onto a private address.

    The cap is enforced while streaming, so an oversized image is abandoned partway
    through rather than held in memory in full.
    """
    try:
        for _ in range(MAX_REDIRECTS + 1):
            if not is_allowed_source(url):
                return None

            resp = requests.get(url, timeout=5, stream=True, allow_redirects=False)
            if resp.is_redirect and resp.headers.get("location"):
                url = urljoin(url, resp.headers["location"])
                resp.close()
                continue

            resp.raise_for_status()
            data = b""
            for chunk in resp.iter_content(64 * 1024):
                data += chunk
                if len(data) > MAX_BACKGROUND_BYTES:
                    return None
            return data
    except requests.RequestException:
        return None
    return None

def prepare_image(data, width, height):
    """Returns PNG bytes of an image cropped to fill a width by height box, full sharpness."""
    image = Image.open(BytesIO(data))
    if image.width * image.height > MAX_BACKGROUND_PIXELS:
        raise ValueError(f"image too large: {image.width}x{image.height}")

    image = ImageOps.fit(image.convert("RGB"), (width, height), method=Image.LANCZOS)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def prepare_background_image(data, width, height, blur=6, saturation=1.4):
    """Returns PNG bytes of an image cropped, blurred and saturated to sit behind a card.

    Note: blur is in card pixels, so it means the same thing whatever
    BACKGROUND_DOWNSCALE is.
    """
    image = Image.open(BytesIO(data))
    if image.width * image.height > MAX_BACKGROUND_PIXELS:
        raise ValueError(f"background image too large: {image.width}x{image.height}")

    image = ImageOps.fit(
        image.convert("RGB"),
        (width // BACKGROUND_DOWNSCALE, height // BACKGROUND_DOWNSCALE),
        method=Image.LANCZOS,
    )
    image = image.filter(ImageFilter.GaussianBlur(blur / BACKGROUND_DOWNSCALE))
    image = ImageEnhance.Color(image).enhance(saturation)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
