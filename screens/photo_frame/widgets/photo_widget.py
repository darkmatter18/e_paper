"""Photo widget - displays dithered image."""

from PIL import Image, ImageDraw

from settings.settings import PHOTOS_DIR
from utils.image import dither_to_bwr
from widgets.base import Widget, WidgetRegion


class PhotoWidget(Widget):
    """Display a photo with Floyd-Steinberg dithering.

    Loads an image file and displays it with proper dithering for the
    black/white/red e-paper display. Image is automatically resized
    to fit the widget region while maintaining aspect ratio.

    Args:
        region: Widget region for positioning and sizing
        image_path: Path to image file (JPG, PNG, etc.)
        use_red_channel: If True, dither to black/white/red. If False, black/white only.

    Layout:
    ┌────────────────────────────────────────┐
    │                                        │
    │        [Dithered Photo]                │
    │                                        │
    └────────────────────────────────────────┘

    Supports:
        Partial refresh: No (photo is static)
    """

    def __init__(
        self,
        region: WidgetRegion,
    ):
        """Initialize photo widget.

        Args:
            region: Widget region for positioning and sizing
        """
        super().__init__(region)
        self._supports_partial_refresh = False
        self.image_path = PHOTOS_DIR / "image.jpg"

        # Validate image path
        if not self.image_path.exists():
            raise FileNotFoundError(f"Image not found: {self.image_path}")

    @property
    def supports_partial_refresh(self) -> bool:
        """Photo does not support partial refresh."""
        return self._supports_partial_refresh

    def draw(
        self,
        black_draw: ImageDraw.ImageDraw,
        red_draw: ImageDraw.ImageDraw,
        **kwargs,
    ):
        """Draw dithered photo.

        Args:
            black_draw: PIL ImageDraw for black channel
            red_draw: PIL ImageDraw for red channel
            **kwargs: Additional arguments (unused)
        """
        # Load source image
        source_image = Image.open(self.image_path)

        # Dither to black/white/red (3 colors)
        black_img, red_img = dither_to_bwr(
            source_image,
            self.region.width,
            self.region.height,
        )

        # Paste dithered images onto the draw contexts
        # Note: paste requires the actual image, not the draw context
        black_draw._image.paste(black_img, (self.region.x, self.region.y))
        red_draw._image.paste(red_img, (self.region.x, self.region.y))
