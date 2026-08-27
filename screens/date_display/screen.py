"""Date display screen - large centered date display."""

from screens.date_display.widgets import DateDisplayWidget
from utils.screen import Screen


def create_date_display_screen() -> Screen:
    """Create date display screen with large date widget.

    Layout:
    - Full screen date display: 800x480
      - Day of week (e.g., WEDNESDAY)
      - Day number in red (e.g., 27)
      - Month and year (e.g., AUGUST 2026)

    Returns:
        Screen with full-screen date display widget.
    """
    return Screen(
        key="date_display",
        name="Date Display",
        display_name="Date Display",
        icon="📅",
        widgets=[
            DateDisplayWidget(),
        ],
    )
