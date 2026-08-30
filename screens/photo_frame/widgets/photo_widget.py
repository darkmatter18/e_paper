"""Photo widget - displays dithered image."""

from pathlib import Path

from PIL import Image, ImageDraw

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
        image_path: str | Path,
        use_red_channel: bool = True,
    ):
        """Initialize photo widget.

        Args:
            region: Widget region for positioning and sizing
            image_path: Path to image file
            use_red_channel: Use 3-color dithering (black/white/red) vs 2-color (black/white)
        """
        super().__init__(region)
        self._supports_partial_refresh = False
        self.image_path = Path(image_path)
        self.use_red_channel = use_red_channel

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
        red_draw: ImageDraw.ImageDraw | None = None,
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

        if self.use_red_channel and red_draw:
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

        else:
            # Dither to black/white only (2 colors)
            from utils.image import dither_to_bw

            bw_img = dither_to_bw(
                source_image,
                self.region.width,
                self.region.height,
            )

            # Paste onto black channel only
            black_draw._image.paste(bw_img, (self.region.x, self.region.y))
