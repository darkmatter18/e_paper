"""Garden landscape widget - static peaceful scene."""

import math

from PIL import ImageDraw

from widgets.base import Widget, WidgetRegion


class GardenLandscapeWidget(Widget):
    """Peaceful garden landscape with tree, flowers, and nature elements.

    Static scene showing:
    - Tree with trunk and leafy crown
    - Scattered flowers (some in red)
    - Grass line at bottom
    - Stones
    - Garden path
    - Butterfly (red accent)

    Layout:
    ┌────────────────────────────────────────┐
    │    🦋                                   │
    │        🌳                               │
    │   🌸  🌸    🌸  🌸   🌸                 │
    │ ═══════════════════════════════════════│
    └────────────────────────────────────────┘

    Supports:
        Partial refresh: No (static scene, full refresh only)
    """

    def __init__(self, region: WidgetRegion):
        """Initialize garden landscape widget.

        Args:
            region: Widget region for positioning and sizing
        """
        super().__init__(region)
        self._supports_partial_refresh = False

    @property
    def supports_partial_refresh(self) -> bool:
        """Garden landscape does not support partial refresh."""
        return self._supports_partial_refresh

    def draw(
        self,
        black_draw: ImageDraw.ImageDraw,
        red_draw: ImageDraw.ImageDraw | None = None,
        **kwargs,
    ):
        """Draw peaceful garden landscape.

        Args:
            black_draw: PIL ImageDraw for black channel
            red_draw: PIL ImageDraw for red channel (red flowers, butterfly)
            **kwargs: Additional arguments (unused)
        """
        # Draw tree on left side
        self._draw_tree(black_draw, red_draw)

        # Draw flowers scattered across the garden
        self._draw_flowers(black_draw, red_draw)

        # Draw grass line
        self._draw_grass(black_draw)

        # Draw stones
        self._draw_stones(black_draw)

        # Draw garden path
        self._draw_path(black_draw)

        # Draw butterfly (red accent)
        if red_draw:
            self._draw_butterfly(red_draw)

    def _draw_tree(
        self,
        black_draw: ImageDraw.ImageDraw,
        red_draw: ImageDraw.ImageDraw | None,
    ):
        """Draw tree with trunk and leafy crown.

        Args:
            black_draw: PIL ImageDraw for black channel
            red_draw: PIL ImageDraw for red channel (unused)
        """
        # Tree trunk (left side of scene)
        trunk_x = self.region.x + 120
        trunk_y = self.region.y + 120
        trunk_width = 30
        trunk_height = 120

        black_draw.rectangle(
            [
                trunk_x,
                trunk_y,
                trunk_x + trunk_width,
                trunk_y + trunk_height,
            ],
            fill=0,
        )

        # Tree crown (organic shape with overlapping circles)
        crown_x = trunk_x + trunk_width // 2
        crown_y = trunk_y - 20

        # Multiple circles to create leafy crown
        crown_circles = [
            (crown_x - 40, crown_y - 30, 50),
            (crown_x + 20, crown_y - 35, 55),
            (crown_x - 10, crown_y - 60, 45),
            (crown_x - 50, crown_y, 40),
            (crown_x + 30, crown_y - 5, 42),
            (crown_x - 15, crown_y + 10, 38),
        ]

        for cx, cy, radius in crown_circles:
            black_draw.ellipse(
                [cx - radius, cy - radius, cx + radius, cy + radius],
                fill=0,
            )

    def _draw_flowers(
        self,
        black_draw: ImageDraw.ImageDraw,
        red_draw: ImageDraw.ImageDraw | None,
    ):
        """Draw scattered flowers across the garden.

        Args:
            black_draw: PIL ImageDraw for black channel
            red_draw: PIL ImageDraw for red channel (red flowers)
        """
        # Flower positions (x, y, size, is_red)
        flowers = [
            # Black flowers
            (self.region.x + 80, self.region.y + 200, 12, False),
            (self.region.x + 250, self.region.y + 180, 15, False),
            (self.region.x + 320, self.region.y + 210, 13, False),
            (self.region.x + 480, self.region.y + 190, 14, False),
            (self.region.x + 580, self.region.y + 200, 12, False),
            (self.region.x + 680, self.region.y + 185, 13, False),
            # Red flowers (accent)
            (self.region.x + 180, self.region.y + 195, 14, True),
            (self.region.x + 400, self.region.y + 205, 13, True),
            (self.region.x + 620, self.region.y + 175, 12, True),
        ]

        for x, y, size, is_red in flowers:
            draw = red_draw if (is_red and red_draw) else black_draw
            self._draw_flower(draw, x, y, size)

    def _draw_flower(self, draw: ImageDraw.ImageDraw, x: int, y: int, size: int):
        """Draw a single flower (5 petals + center).

        Args:
            draw: PIL ImageDraw object
            x: Flower center x
            y: Flower center y
            size: Flower size (petal radius)
        """
        # Draw 5 petals in a circle
        for i in range(5):
            angle = math.radians(i * 72)  # 360/5 = 72 degrees between petals
            petal_x = x + int(size * math.cos(angle))
            petal_y = y + int(size * math.sin(angle))

            # Draw petal (small circle)
            petal_radius = size // 2
            draw.ellipse(
                [
                    petal_x - petal_radius,
                    petal_y - petal_radius,
                    petal_x + petal_radius,
                    petal_y + petal_radius,
                ],
                fill=0,
            )

        # Draw center circle
        center_radius = size // 3
        draw.ellipse(
            [
                x - center_radius,
                y - center_radius,
                x + center_radius,
                y + center_radius,
            ],
            fill=0,
        )

    def _draw_grass(self, draw: ImageDraw.ImageDraw):
        """Draw grass line at bottom.

        Args:
            draw: PIL ImageDraw for black channel
        """
        grass_y = self.region.y + 260

        # Draw wavy grass line
        points = []
        for x in range(self.region.x, self.region.x + self.region.width, 8):
            wave_y = grass_y + int(5 * math.sin((x - self.region.x) / 40))
            points.append((x, wave_y))

        if len(points) > 1:
            draw.line(points, fill=0, width=2)

        # Draw grass blades (small vertical lines)
        for x in range(self.region.x + 20, self.region.x + self.region.width, 40):
            blade_y = grass_y + int(5 * math.sin((x - self.region.x) / 40))
            draw.line(
                [(x, blade_y), (x, blade_y + 15)],
                fill=0,
                width=2,
            )

    def _draw_stones(self, draw: ImageDraw.ImageDraw):
        """Draw decorative stones.

        Args:
            draw: PIL ImageDraw for black channel
        """
        # Stone positions (x, y, width, height)
        stones = [
            (self.region.x + 300, self.region.y + 240, 25, 18),
            (self.region.x + 520, self.region.y + 235, 22, 16),
            (self.region.x + 420, self.region.y + 245, 20, 15),
        ]

        for x, y, width, height in stones:
            # Draw stone as rounded rectangle (ellipse)
            draw.ellipse(
                [x, y, x + width, y + height],
                fill=0,
            )

    def _draw_path(self, draw: ImageDraw.ImageDraw):
        """Draw garden path (curved line).

        Args:
            draw: PIL ImageDraw for black channel
        """
        path_y = self.region.y + 280

        # Draw curved path line
        points = []
        for x in range(self.region.x, self.region.x + self.region.width, 8):
            curve_y = path_y + int(20 * math.sin((x - self.region.x) / 100))
            points.append((x, curve_y))

        if len(points) > 1:
            draw.line(points, fill=0, width=4)

    def _draw_butterfly(self, draw: ImageDraw.ImageDraw):
        """Draw butterfly (red accent).

        Args:
            draw: PIL ImageDraw for red channel
        """
        # Butterfly position (flying near flowers)
        butterfly_x = self.region.x + 450
        butterfly_y = self.region.y + 80

        # Wing size
        wing_size = 18

        # Left wings (top and bottom)
        draw.ellipse(
            [
                butterfly_x - wing_size,
                butterfly_y - wing_size,
                butterfly_x,
                butterfly_y - 2,
            ],
            fill=0,
        )
        draw.ellipse(
            [
                butterfly_x - wing_size + 3,
                butterfly_y + 2,
                butterfly_x,
                butterfly_y + wing_size - 3,
            ],
            fill=0,
        )

        # Right wings (top and bottom)
        draw.ellipse(
            [
                butterfly_x,
                butterfly_y - wing_size,
                butterfly_x + wing_size,
                butterfly_y - 2,
            ],
            fill=0,
        )
        draw.ellipse(
            [
                butterfly_x,
                butterfly_y + 2,
                butterfly_x + wing_size - 3,
                butterfly_y + wing_size - 3,
            ],
            fill=0,
        )

        # Body (small vertical line)
        draw.line(
            [
                (butterfly_x, butterfly_y - wing_size // 2),
                (butterfly_x, butterfly_y + wing_size // 2),
            ],
            fill=0,
            width=3,
        )
