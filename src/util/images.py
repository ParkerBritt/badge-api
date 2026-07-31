from io import BytesIO

import requests
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Limits on background images, which can come from a caller-supplied URL.
MAX_BACKGROUND_BYTES = 16 * 1024 * 1024
MAX_BACKGROUND_PIXELS = 50_000_000

# The background is stored this many times smaller than the card and scaled back up on
# display. The averaging that involves is what clears out JPEG block artifacts.
BACKGROUND_DOWNSCALE = 4


def fetch_capped(url):
    """Returns the bytes at a URL, or None if it fails or exceeds the size cap.

    The cap is enforced while streaming, so an oversized image is abandoned partway
    through rather than held in memory in full.
    """
    try:
        resp = requests.get(url, timeout=5, stream=True)
        resp.raise_for_status()
        data = b""
        for chunk in resp.iter_content(64 * 1024):
            data += chunk
            if len(data) > MAX_BACKGROUND_BYTES:
                return None
        return data
    except requests.RequestException:
        return None


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
