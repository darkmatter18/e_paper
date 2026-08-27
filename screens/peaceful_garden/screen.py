"""Peaceful garden screen - animated clouds over static garden landscape."""

from screens.peaceful_garden.widgets import GardenLandscapeWidget, SkyCloudsWidget
from utils.screen import Screen
from widgets import WidgetRegion


def create_peaceful_garden_screen() -> Screen:
    """Create peaceful garden screen with animated clouds.

    Two-widget design for serene, living scene:
    1. Sky & Clouds (top, dynamic) - clouds drift every minute (partial refresh)
    2. Garden Landscape (bottom, static) - tree, flowers, grass, butterfly

    Layout:
    ┌────────────────────────────────────────┐
    │  ☁️      ☁️         ☁️       (Sky)      │  150px - Dynamic
    ├────────────────────────────────────────┤
    │    🦋        🌳                         │
    │   🌸  🌸    🌸  🌸   🌸    (Garden)    │  330px - Static
    │ ═══════════════════════════════════════│
    └────────────────────────────────────────┘

    The clouds update every minute with partial refresh, creating gentle
    movement while the garden below remains serene and constant.

    Returns:
        Screen with animated sky and static garden widgets.
    """
    return Screen(
        key="peaceful_garden",
        name="Peaceful Garden",
        display_name="Peaceful Garden",
        icon="🌸",
        widgets=[
            SkyCloudsWidget(WidgetRegion(x=0, y=0, width=800, height=150)),
            GardenLandscapeWidget(WidgetRegion(x=0, y=150, width=800, height=330)),
        ],
    )
