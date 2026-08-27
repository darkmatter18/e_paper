"""Compact date widget for datetime display screen."""

from PIL import ImageDraw, ImageFont

from settings.fonts import FONT_GEOMINI
from utils.datetime_util import DateTimeUtil
from widgets.base import Widget, WidgetRegion


class CompactDateWidget(Widget):
    """Compact date display for use with clock.

    Shows date in a single line with two colors:
    - Format: "WEDNESDAY, 27 AUGUST 2026"
    - Day number (27) in red
    - Rest in black (day of week, month, year)

    Layout:
    ┌────────────────────────────────────────┐
    │                                        │
    │      WEDNESDAY, 27 AUGUST 2026         │
    │                  (red)                 │
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
            red_draw: PIL ImageDraw for red channel (day number)
            **kwargs: Additional arguments (unused)
        """
        now = DateTimeUtil.now()

        # Get date components
        day_of_week = now.strftime("%A").upper()  # WEDNESDAY
        day_number = now.strftime("%d")  # 27
        month = now.strftime("%B").upper()  # AUGUST
        year = now.strftime("%Y")  # 2026

        # Font
        font = ImageFont.truetype(str(FONT_GEOMINI), 48)
        font.set_variation_by_axes([700])  # Bold

        # Build text parts
        part1 = f"{day_of_week}, "  # Black
        part2 = day_number  # Red
        part3 = f" {month} {year}"  # Black

        # Calculate total width to center the entire line
        bbox1 = black_draw.textbbox((0, 0), part1, font=font)
        width1 = bbox1[2] - bbox1[0]

        bbox2 = black_draw.textbbox((0, 0), part2, font=font)
        width2 = bbox2[2] - bbox2[0]

        bbox3 = black_draw.textbbox((0, 0), part3, font=font)
        width3 = bbox3[2] - bbox3[0]

        total_width = width1 + width2 + width3

        # Center coordinates
        center_x = self.region.x + self.region.width // 2
        center_y = self.region.y + self.region.height // 2

        # Starting x position (left edge of centered text)
        start_x = center_x - total_width // 2

        # Draw each part
        # Part 1: Day of week (black)
        black_draw.text(
            (start_x, center_y),
            part1,
            font=font,
            fill=0,
            anchor="lm",
        )

        # Part 2: Day number (red)
        if red_draw:
            red_draw.text(
                (start_x + width1, center_y),
                part2,
                font=font,
                fill=0,
                anchor="lm",
            )

        # Part 3: Month and year (black)
        black_draw.text(
            (start_x + width1 + width2, center_y),
            part3,
            font=font,
            fill=0,
            anchor="lm",
        )
