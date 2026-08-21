from io import BytesIO
from urllib.parse import urljoin, urlparse

import requests
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Limits on background images, which can come from a caller-supplied URL.
MAX_BACKGROUND_BYTES = 16 * 1024 * 1024
MAX_BACKGROUND_PIXELS = 50_000_000

# The background is stored this many times smaller than the card and scaled back up on
# display. The averaging that involves is what clears out JPEG block artifacts.
BACKGROUND_DOWNSCALE = 4

# The only hosts a fetch may be pointed at, since a request runs with this server's reach.
ALLOWED_HOSTS = frozenset(
    {
        "raw.githubusercontent.com",
        "gist.githubusercontent.com",
        "user-images.githubusercontent.com",
        "avatars.githubusercontent.com",
    }
)

# How many redirects a fetch follows, with every hop held to ALLOWED_HOSTS.
MAX_REDIRECTS = 3


def is_allowed_source(source):
    """Returns whether a caller-supplied URL is one this server may fetch.

    e.g. "https://raw.githubusercontent.com/me/me/main/card.png" is allowed,
    while "http://169.254.169.254/latest/meta-data" is not.
    """
    parsed = urlparse(source or "")
    return parsed.scheme == "https" and parsed.hostname in ALLOWED_HOSTS


def fetch_capped(url):
    """Returns the bytes at a URL, or None if it fails or exceeds the size cap.

    Only the hosts in ALLOWED_HOSTS can be reached. Redirects are followed one hop
    at a time and each new location is checked the same way, so an allowed host
    can't bounce the request onto a private address.

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
