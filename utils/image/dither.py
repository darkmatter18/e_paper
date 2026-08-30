"""Image dithering utilities for e-paper display.

Provides Floyd-Steinberg dithering for converting color images to the
black/white/red palette of the Waveshare 7.5" B/V2 e-paper display.
"""

from PIL import Image


def dither_to_bwr(
    source_image: Image.Image,
    target_width: int,
    target_height: int,
) -> tuple[Image.Image, Image.Image]:
    """Dither color image to black/white/red and split into two channels.

    Uses Floyd-Steinberg dithering to convert a color image to the 3-color
    palette (black, white, red) of the e-paper display, then separates into
    two binary images for the dual-channel display.

    Args:
        source_image: Source PIL Image (any mode)
        target_width: Target width in pixels
        target_height: Target height in pixels

    Returns:
        Tuple of (black_channel, red_channel):
        - black_channel: 1-bit PIL Image (0=black, 1=white)
        - red_channel: 1-bit PIL Image (0=red, 1=white)

    Example:
        >>> from PIL import Image
        >>> photo = Image.open("photo.jpg")
        >>> black_img, red_img = dither_to_bwr(photo, 800, 480)
        >>> # black_img and red_img ready to draw on display
    """
    # Resize image to target size (maintain aspect ratio with letterboxing)
    source_image = source_image.convert("RGB")
    source_image.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

    # Create canvas at target size with white background
    canvas = Image.new("RGB", (target_width, target_height), (255, 255, 255))

    # Center the thumbnail on the canvas
    offset_x = (target_width - source_image.width) // 2
    offset_y = (target_height - source_image.height) // 2
    canvas.paste(source_image, (offset_x, offset_y))

    # Create 3-color palette image (black, white, red)
    palette_img = Image.new("P", (1, 1))
    palette_colors = [
        0,
        0,
        0,  # Index 0: Black
        255,
        255,
        255,  # Index 1: White
        255,
        0,
        0,  # Index 2: Red
    ]
    # Pad palette to 768 bytes (256 colors × 3 channels)
    palette_colors.extend([0] * (768 - len(palette_colors)))
    palette_img.putpalette(palette_colors)

    # Quantize with Floyd-Steinberg dithering
    dithered = canvas.quantize(palette=palette_img, dither=Image.Dither.FLOYDSTEINBERG)

    # Convert to RGB to read pixel colors
    dithered_rgb = dithered.convert("RGB")

    # Create two 1-bit images for black and red channels
    black_channel = Image.new("1", (target_width, target_height), 1)  # Start white
    red_channel = Image.new("1", (target_width, target_height), 1)  # Start white

    # Separate colors into channels
    pixels_rgb = dithered_rgb.load()
    pixels_black = black_channel.load()
    pixels_red = red_channel.load()

    for y in range(target_height):
        for x in range(target_width):
            r, g, b = pixels_rgb[x, y]

            # Check if pixel is black (r,g,b close to 0)
            if r < 50 and g < 50 and b < 50:
                pixels_black[x, y] = 0  # Black pixel

            # Check if pixel is red (r high, g and b low)
            elif r > 200 and g < 50 and b < 50:
                pixels_red[x, y] = 0  # Red pixel

            # Otherwise it's white (both channels stay 1)

    return black_channel, red_channel


def dither_to_bw(
    source_image: Image.Image,
    target_width: int,
    target_height: int,
) -> Image.Image:
    """Dither color image to black/white only.

    Uses Floyd-Steinberg dithering to convert a color image to pure
    black and white (no red channel).

    Args:
        source_image: Source PIL Image (any mode)
        target_width: Target width in pixels
        target_height: Target height in pixels

    Returns:
        1-bit PIL Image (0=black, 1=white) with Floyd-Steinberg dithering

    Example:
        >>> from PIL import Image
        >>> photo = Image.open("photo.jpg")
        >>> bw_img = dither_to_bw(photo, 800, 480)
    """
    # Resize image to target size (maintain aspect ratio with letterboxing)
    source_image = source_image.convert("RGB")
    source_image.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

    # Create canvas at target size with white background
    canvas = Image.new("RGB", (target_width, target_height), (255, 255, 255))

    # Center the thumbnail on the canvas
    offset_x = (target_width - source_image.width) // 2
    offset_y = (target_height - source_image.height) // 2
    canvas.paste(source_image, (offset_x, offset_y))

    # Convert to grayscale then to 1-bit with Floyd-Steinberg dithering
    grayscale = canvas.convert("L")
    dithered = grayscale.convert("1", dither=Image.Dither.FLOYDSTEINBERG)

    return dithered
