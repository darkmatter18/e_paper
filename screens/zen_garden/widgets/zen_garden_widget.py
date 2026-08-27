"""Zen garden patterns widget - daily rotating minimalist patterns."""

import math

from PIL import ImageDraw, ImageFont

from settings.fonts import FONT_GEOMINI
from utils.datetime_util import DateTimeUtil
from widgets.base import Widget, WidgetRegion


class ZenGardenWidget(Widget):
    """Zen garden patterns with daily word of wisdom.

    Displays a different minimalist pattern each day of the week:
    - Monday: Enso circle (zen circle)
    - Tuesday: Wave patterns (flowing curves)
    - Wednesday: Parallel lines (raked sand)
    - Thursday: Spiral pattern (inward journey)
    - Friday: Concentric circles (ripples)
    - Saturday: Rock garden (stones with halos)
    - Sunday: Bamboo stalks (vertical strength)

    Each pattern includes a word of wisdom at the bottom in red.

    Layout:
    ┌────────────────────────────────────────┐
    │                                        │
    │                                        │
    │           [Pattern Area]               │
    │                                        │
    │                                        │
    │              WORD                      │
    └────────────────────────────────────────┘

    Supports:
        Partial refresh: No (updates once per day)
    """

    # Daily patterns and words (indexed by day of week: 0=Monday, 6=Sunday)
    PATTERNS = {
        0: ("enso", "PRESENCE"),
        1: ("waves", "FLOW"),
        2: ("lines", "STILLNESS"),
        3: ("spiral", "GROWTH"),
        4: ("circles", "BALANCE"),
        5: ("rocks", "SIMPLICITY"),
        6: ("bamboo", "CLARITY"),
    }

    def __init__(self, region: WidgetRegion):
        """Initialize zen garden widget.

        Args:
            region: Widget region for positioning and sizing
        """
        super().__init__(region)
        self._supports_partial_refresh = False

    @property
    def supports_partial_refresh(self) -> bool:
        """Zen garden does not support partial refresh."""
        return self._supports_partial_refresh

    def draw(
        self,
        black_draw: ImageDraw.ImageDraw,
        red_draw: ImageDraw.ImageDraw | None = None,
        **kwargs,
    ):
        """Draw zen garden pattern and word.

        Args:
            black_draw: PIL ImageDraw for black channel
            red_draw: PIL ImageDraw for red channel (word of wisdom)
            **kwargs: Additional arguments (unused)
        """
        now = DateTimeUtil.now()
        day_of_week = now.weekday()  # 0=Monday, 6=Sunday

        pattern_type, word = self.PATTERNS[day_of_week]

        # Draw the pattern
        if pattern_type == "enso":
            self._draw_enso(black_draw)
        elif pattern_type == "waves":
            self._draw_waves(black_draw)
        elif pattern_type == "lines":
            self._draw_lines(black_draw)
        elif pattern_type == "spiral":
            self._draw_spiral(black_draw)
        elif pattern_type == "circles":
            self._draw_circles(black_draw)
        elif pattern_type == "rocks":
            self._draw_rocks(black_draw)
        elif pattern_type == "bamboo":
            self._draw_bamboo(black_draw)

        # Draw word of wisdom at bottom (in red)
        self._draw_word(word, red_draw if red_draw else black_draw)

    def _draw_enso(self, draw: ImageDraw.ImageDraw):
        """Draw Enso circle - zen circle with slight gap.

        Args:
            draw: PIL ImageDraw object
        """
        center_x = self.region.x + self.region.width // 2
        center_y = self.region.y + (self.region.height - 100) // 2
        radius = 140

        # Draw circle with small gap (0-350 degrees instead of full 360)
        bbox = [
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
        ]
        draw.arc(bbox, start=10, end=350, fill=0, width=12)

    def _draw_waves(self, draw: ImageDraw.ImageDraw):
        """Draw wave patterns - flowing curves.

        Args:
            draw: PIL ImageDraw object
        """
        pattern_height = self.region.height - 120
        num_waves = 8
        spacing = pattern_height // num_waves

        for i in range(num_waves):
            y = self.region.y + 20 + i * spacing
            points = []

            # Create smooth wave using sine curve
            for x in range(self.region.x, self.region.x + self.region.width, 8):
                wave_y = y + int(
                    30 * math.sin((x - self.region.x) / 60 + i * 0.5)
                )
                points.append((x, wave_y))

            if len(points) > 1:
                draw.line(points, fill=0, width=3)

    def _draw_lines(self, draw: ImageDraw.ImageDraw):
        """Draw parallel horizontal lines - raked sand.

        Args:
            draw: PIL ImageDraw object
        """
        pattern_height = self.region.height - 120
        num_lines = 12
        spacing = pattern_height // num_lines

        for i in range(num_lines):
            y = self.region.y + 40 + i * spacing
            draw.line(
                [
                    (self.region.x + 40, y),
                    (self.region.x + self.region.width - 40, y),
                ],
                fill=0,
                width=3,
            )

    def _draw_spiral(self, draw: ImageDraw.ImageDraw):
        """Draw spiral pattern - inward journey.

        Args:
            draw: PIL ImageDraw object
        """
        center_x = self.region.x + self.region.width // 2
        center_y = self.region.y + (self.region.height - 100) // 2

        points = []
        max_radius = 160
        turns = 4

        # Generate spiral points
        for i in range(0, 360 * turns, 3):
            angle = math.radians(i)
            radius = max_radius * (i / (360 * turns))
            x = center_x + int(radius * math.cos(angle))
            y = center_y + int(radius * math.sin(angle))
            points.append((x, y))

        if len(points) > 1:
            draw.line(points, fill=0, width=3)

    def _draw_circles(self, draw: ImageDraw.ImageDraw):
        """Draw concentric circles - ripples.

        Args:
            draw: PIL ImageDraw object
        """
        center_x = self.region.x + self.region.width // 2
        center_y = self.region.y + (self.region.height - 100) // 2

        num_circles = 7
        max_radius = 180
        spacing = max_radius // num_circles

        for i in range(1, num_circles + 1):
            radius = i * spacing
            bbox = [
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
            ]
            draw.arc(bbox, start=0, end=360, fill=0, width=3)

    def _draw_rocks(self, draw: ImageDraw.ImageDraw):
        """Draw rock garden - stones with rake patterns.

        Args:
            draw: PIL ImageDraw object
        """
        center_y = self.region.y + (self.region.height - 100) // 2

        # Three rocks at different positions
        rocks = [
            (self.region.x + 200, center_y - 40, 45),
            (self.region.x + 500, center_y + 20, 35),
            (self.region.x + 350, center_y + 60, 40),
        ]

        for rock_x, rock_y, rock_radius in rocks:
            # Draw rock (filled circle)
            bbox = [
                rock_x - rock_radius,
                rock_y - rock_radius,
                rock_x + rock_radius,
                rock_y + rock_radius,
            ]
            draw.ellipse(bbox, fill=0)

            # Draw concentric lines around rock (rake marks)
            for i in range(1, 4):
                halo_radius = rock_radius + i * 20
                halo_bbox = [
                    rock_x - halo_radius,
                    rock_y - halo_radius,
                    rock_x + halo_radius,
                    rock_y + halo_radius,
                ]
                draw.arc(halo_bbox, start=0, end=360, fill=0, width=2)

    def _draw_bamboo(self, draw: ImageDraw.ImageDraw):
        """Draw bamboo stalks - vertical strength.

        Args:
            draw: PIL ImageDraw object
        """
        pattern_height = self.region.height - 120
        num_stalks = 5
        stalk_spacing = self.region.width // (num_stalks + 1)

        for i in range(1, num_stalks + 1):
            x = self.region.x + i * stalk_spacing

            # Draw vertical stalk
            draw.line(
                [(x, self.region.y + 20), (x, self.region.y + pattern_height)],
                fill=0,
                width=8,
            )

            # Draw bamboo joints (horizontal segments)
            num_joints = 5
            joint_spacing = pattern_height // num_joints

            for j in range(1, num_joints):
                joint_y = self.region.y + 20 + j * joint_spacing
                draw.line(
                    [(x - 20, joint_y), (x + 20, joint_y)],
                    fill=0,
                    width=3,
                )

    def _draw_word(self, word: str, draw: ImageDraw.ImageDraw):
        """Draw word of wisdom at bottom.

        Args:
            word: Word to display
            draw: PIL ImageDraw object (red channel for color accent)
        """
        font = ImageFont.truetype(str(FONT_GEOMINI), 52)
        font.set_variation_by_axes([800])  # Extra bold

        center_x = self.region.x + self.region.width // 2
        word_y = self.region.y + self.region.height - 70

        draw.text(
            (center_x, word_y),
            word,
            font=font,
            fill=0,
            anchor="mm",
        )
