"""Compact date widget for datetime display screen."""

from PIL import ImageDraw, ImageFont

from settings.fonts import FONT_GEOMINI
from utils.datetime_util import DateTimeUtil
from widgets.base import Widget, WidgetRegion


class CompactDateWidget(Widget):
    """Compact date display for use with clock.

    Shows date in two lines:
    - Line 1: Day of week, Day number (e.g., "WEDNESDAY, 27")
    - Line 2: Month Year (e.g., "AUGUST 2026")

    Layout:
    ┌────────────────────────────────────────┐
    │                                        │
    │         WEDNESDAY, 27                  │
    │          AUGUST 2026                   │
    │                                        │
    └────────────────────────────────────────┘

    Supports:
        Partial refresh: No (updates only on full refresh)
    """

    def __init__(self, region: WidgetRegion):
        """Initialize compact date widget.

        Args:
            region: Widget region for positioning and sizing
        """
        super().__init__(region)
        self._supports_partial_refresh = False

    @property
    def supports_partial_refresh(self) -> bool:
        """Compact date does not support partial refresh."""
        return self._supports_partial_refresh

    def draw(
        self,
        black_draw: ImageDraw.ImageDraw,
        red_draw: ImageDraw.ImageDraw | None = None,
        **kwargs,
    ):
        """Draw the compact date display.

        Args:
            black_draw: PIL ImageDraw for black channel
            red_draw: PIL ImageDraw for red channel (unused)
            **kwargs: Additional arguments (unused)
        """
        now = DateTimeUtil.now()

        # Get date components
        day_of_week = now.strftime("%A").upper()  # WEDNESDAY
        day_number = now.strftime("%d")  # 27
        month = now.strftime("%B").upper()  # AUGUST
        year = now.strftime("%Y")  # 2026

        # Center coordinates
        center_x = self.region.x + self.region.width // 2
        center_y = self.region.y + self.region.height // 2

        # Line 1: Day of week, day number
        day_text = f"{day_of_week}, {day_number}"
        day_font = ImageFont.truetype(str(FONT_GEOMINI), 56)
        day_font.set_variation_by_axes([700])  # Bold
        black_draw.text(
            (center_x, center_y - 40),
            day_text,
            font=day_font,
            fill=0,
            anchor="mm",
        )

        # Line 2: Month and year
        month_year_text = f"{month} {year}"
        month_font = ImageFont.truetype(str(FONT_GEOMINI), 44)
        month_font.set_variation_by_axes([600])  # Semibold
        black_draw.text(
            (center_x, center_y + 40),
            month_year_text,
            font=month_font,
            fill=0,
            anchor="mm",
        )
