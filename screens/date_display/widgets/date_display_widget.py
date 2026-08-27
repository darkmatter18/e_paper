"""Full-screen date display widget."""

from PIL import ImageDraw, ImageFont

from settings.fonts import FONT_GEOMINI, FONT_ORBITRON
from utils.datetime_util import DateTimeUtil
from widgets.base import Widget, WidgetRegion


class DateDisplayWidget(Widget):
    """Large full-screen date display.

    Shows:
    - Day of week (large, top)
    - Day number (very large, center, red)
    - Month and year (large, bottom)

    Layout:
    ┌────────────────────────────────────────┐
    │                                        │
    │            WEDNESDAY                   │
    │                                        │
    │               27                       │  (red, very large)
    │                                        │
    │          AUGUST 2026                   │
    │                                        │
    └────────────────────────────────────────┘

    Supports:
        Partial refresh: Yes (updates daily at midnight)
    """

    def __init__(self):
        """Initialize date display widget with full screen region."""
        super().__init__(WidgetRegion(x=0, y=0, width=800, height=480))
        self._supports_partial_refresh = True

    @property
    def supports_partial_refresh(self) -> bool:
        """Date display supports partial refresh for daily updates."""
        return self._supports_partial_refresh

    def draw(
        self,
        black_draw: ImageDraw.ImageDraw,
        red_draw: ImageDraw.ImageDraw | None = None,
        **kwargs,
    ):
        """Draw the date display.

        Args:
            black_draw: PIL ImageDraw for black channel
            red_draw: PIL ImageDraw for red channel (day number)
            **kwargs: Additional arguments (unused)
        """
        now = DateTimeUtil.now()

        # Get date components
        day_of_week = now.strftime("%A").upper()  # WEDNESDAY
        day_number = now.strftime("%d")  # 27
        month = now.strftime("%B").upper()  # AUGUST
        year = now.strftime("%Y")  # 2026

        # Center coordinates
        center_x = self.region.width // 2
        center_y = self.region.height // 2

        # Day of week (top)
        day_font = ImageFont.truetype(str(FONT_GEOMINI), 48)
        day_font.set_variation_by_axes([700])  # Bold
        black_draw.text(
            (center_x, center_y - 120),
            day_of_week,
            font=day_font,
            fill=0,
            anchor="mm",
        )

        # Day number (center, red if available)
        day_num_font = ImageFont.truetype(str(FONT_ORBITRON), 220)
        day_num_font.set_variation_by_axes([900])  # Black weight
        if red_draw:
            red_draw.text(
                (center_x, center_y + 10),
                day_number,
                font=day_num_font,
                fill=0,
                anchor="mm",
            )
        else:
            # Fallback to black if no red channel
            black_draw.text(
                (center_x, center_y + 10),
                day_number,
                font=day_num_font,
                fill=0,
                anchor="mm",
            )

        # Month and year (bottom)
        month_year_text = f"{month} {year}"
        month_font = ImageFont.truetype(str(FONT_GEOMINI), 42)
        month_font.set_variation_by_axes([600])  # Semibold
        black_draw.text(
            (center_x, center_y + 150),
            month_year_text,
            font=month_font,
            fill=0,
            anchor="mm",
        )
