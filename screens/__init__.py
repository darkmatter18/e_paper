from screens.date_display import create_date_display_screen
from screens.datetime_display import create_datetime_display_screen
from screens.datetime_weather_forecast import create_datetime_weather_forecast_screen
from screens.digital_clock import create_digital_clock_screen
from screens.todays_weather import create_todays_weather_screen
from screens.zen_garden import create_zen_garden_screen
from utils.screen import Screen

# List of all available screens (single source of truth)
_SCREENS: list[Screen] = [
    create_digital_clock_screen(),
    create_date_display_screen(),
    create_datetime_display_screen(),
    create_datetime_weather_forecast_screen(),
    create_todays_weather_screen(),
    create_zen_garden_screen(),
]

# Screen registry - maps screen keys to Screen instances
AVAILABLE_SCREENS: dict[str, Screen] = {screen.key: screen for screen in _SCREENS}

# Default screen key
DEFAULT_SCREEN = "zen_garden"


def get_screen(key: str) -> Screen:
    """Get a screen instance by key.

    Args:
        key: Screen key from AVAILABLE_SCREENS.

    Returns:
        Screen instance with configured widgets.

    Raises:
        KeyError: If screen key not found in AVAILABLE_SCREENS.
    """
    if key not in AVAILABLE_SCREENS:
        raise KeyError(
            f"Unknown screen '{key}'. Available: {list(AVAILABLE_SCREENS.keys())}"
        )

    return AVAILABLE_SCREENS[key]


def get_screens() -> list[Screen]:
    """Get list of all available screens.

    Returns:
        List of Screen objects with metadata and widgets.
        Each Screen includes key, name, display_name, icon, and widgets.
    """
    return _SCREENS.copy()


__all__ = [
    "AVAILABLE_SCREENS",
    "DEFAULT_SCREEN",
    "get_screen",
    "get_screens",
]
