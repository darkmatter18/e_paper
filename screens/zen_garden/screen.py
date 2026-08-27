"""Zen garden screen - daily rotating minimalist patterns."""

from screens.zen_garden.widgets import ZenGardenWidget
from utils.screen import Screen
from widgets import StatusBarWidget, WidgetRegion


def create_zen_garden_screen() -> Screen:
    """Create zen garden screen with daily pattern rotation.

    Displays a different minimalist pattern each day of the week:
    - Monday: Enso circle with "PRESENCE"
    - Tuesday: Wave patterns with "FLOW"
    - Wednesday: Parallel lines with "STILLNESS"
    - Thursday: Spiral pattern with "GROWTH"
    - Friday: Concentric circles with "BALANCE"
    - Saturday: Rock garden with "SIMPLICITY"
    - Sunday: Bamboo stalks with "CLARITY"

    Layout:
    - Status bar: 800x30 at top (WiFi, CPU temp)
    - Zen pattern: 800x450 main area (pattern + word)

    Returns:
        Screen with status bar and zen garden widget.
    """
    return Screen(
        key="zen_garden",
        name="Zen Garden",
        display_name="Zen Garden",
        icon="🪨",
        widgets=[
            StatusBarWidget(WidgetRegion(x=0, y=0, width=800, height=30)),
            ZenGardenWidget(WidgetRegion(x=0, y=30, width=800, height=450)),
        ],
    )
