"""DateTime display screen - digital clock with date below."""

from screens.datetime_display.widgets import CompactDateWidget
from screens.digital_clock.widgets import ColonWidget, HoursWidget, MinutesWidget
from utils.screen import Screen
from widgets import StatusBarWidget, WidgetRegion


def create_datetime_display_screen() -> Screen:
    """Create datetime display screen with clock and date.

    Layout:
    - Status bar: 800x30 at top (WiFi, CPU temp)
    - Digital clock: HH:MM in center-upper area
      - Hours (red): large Orbitron font
      - Colon (black): separator
      - Minutes (black): large Orbitron font, partial refresh
    - Date display: Centered below clock
      - Day of week and day number
      - Month and year

    Returns:
        Screen with status bar, clock widgets, and date widget.
    """
    return Screen(
        key="datetime_display",
        name="DateTime Display",
        display_name="Clock & Date",
        icon="🕐",
        widgets=[
            # Status bar at top
            StatusBarWidget(WidgetRegion(x=0, y=0, width=800, height=30)),
            # Clock components - ALIGNED TO 8-PIXEL BOUNDARIES
            HoursWidget(WidgetRegion(x=16, y=120, width=344, height=176)),
            ColonWidget(WidgetRegion(x=360, y=128, width=88, height=176)),
            MinutesWidget(WidgetRegion(x=440, y=120, width=344, height=176)),
            # Date below clock
            CompactDateWidget(WidgetRegion(x=0, y=320, width=800, height=160)),
        ],
    )
