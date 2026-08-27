"""Sky with drifting clouds widget - animated every minute."""

from PIL import ImageDraw

from utils.datetime_util import DateTimeUtil
from widgets.base import Widget, WidgetRegion


class SkyCloudsWidget(Widget):
    """Sky with drifting clouds that move every minute.

    Clouds drift horizontally across the sky, with positions calculated
    from current minute. Creates a peaceful, living animation.

    Layout:
    ┌────────────────────────────────────────┐
    │  ☁️      ☁️         ☁️                  │
    │     ☁️           ☁️       ☁️            │
    └────────────────────────────────────────┘

    Supports:
        Partial refresh: Yes (clouds update every minute)
    """

    # Cloud definitions (y_offset, width, height, speed_multiplier)
    CLOUDS = [
        (20, 120, 40, 1.0),  # Top-left cloud
        (50, 100, 35, 0.7),  # Middle cloud (slower)
        (25, 90, 30, 1.3),  # Top-right cloud (faster)
        (70, 110, 38, 0.9),  # Bottom cloud
    ]

    def __init__(self, region: WidgetRegion):
        """Initialize sky clouds widget.

        Args:
            region: Widget region for positioning and sizing
        """
        super().__init__(region)
        self._supports_partial_refresh = True

    @property
    def supports_partial_refresh(self) -> bool:
        """Sky clouds support partial refresh for animation."""
        return self._supports_partial_refresh

    def draw(
        self,
        black_draw: ImageDraw.ImageDraw,
        red_draw: ImageDraw.ImageDraw | None = None,
        **kwargs,
    ):
        """Draw sky with drifting clouds.

        Args:
            black_draw: PIL ImageDraw for black channel
            red_draw: PIL ImageDraw for red channel (unused)
            **kwargs: Additional arguments (unused)
        """
        now = DateTimeUtil.now()
        minute = now.minute

        # Draw each cloud at position based on current minute
        for cloud_idx, (y_offset, width, height, speed) in enumerate(self.CLOUDS):
            # Calculate cloud position (drifts across screen)
            # Each cloud has different speed multiplier for varied movement
            progress = (minute * speed + cloud_idx * 15) % 100  # 0-100
            x_position = int(
                self.region.x + (self.region.width + width) * progress / 100 - width
            )
            y_position = self.region.y + y_offset

            # Draw cloud (3 overlapping circles)
            self._draw_cloud(black_draw, x_position, y_position, width, height)

    def _draw_cloud(
        self,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        width: int,
        height: int,
    ):
        """Draw a single cloud using overlapping circles.

        Args:
            draw: PIL ImageDraw object
            x: Cloud x position
            y: Cloud y position
            width: Cloud width
            height: Cloud height
        """
        # Cloud is made of 3 overlapping ellipses
        circle_radius = height // 2

        # Left circle
        draw.ellipse(
            [x, y, x + circle_radius * 2, y + height],
            fill=0,
            outline=0,
        )

        # Middle circle (larger)
        middle_x = x + width // 2 - circle_radius
        middle_radius = int(circle_radius * 1.3)
        draw.ellipse(
            [
                middle_x,
                y - circle_radius // 3,
                middle_x + middle_radius * 2,
                y + height,
            ],
            fill=0,
            outline=0,
        )

        # Right circle
        right_x = x + width - circle_radius * 2
        draw.ellipse(
            [right_x, y, right_x + circle_radius * 2, y + height],
            fill=0,
            outline=0,
        )
