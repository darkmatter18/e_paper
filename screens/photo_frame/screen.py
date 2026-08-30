"""Photo frame screen - display dithered photos."""

from screens.photo_frame.widgets import PhotoWidget
from utils.screen import Screen
from widgets import StatusBarWidget, WidgetRegion


def create_photo_frame_screen() -> Screen:
    """Create photo frame screen with dithered photo display.

    Displays a photo using Floyd-Steinberg dithering for the e-paper display.
    The image path can be configured via the PHOTO_PATH environment variable,
    or defaults to demo_landscape.jpg in the project root.

    Features:
    - Black/white/red 3-color dithering
    - Automatic aspect ratio preservation
    - Status bar with WiFi and CPU temp

    Layout:
    ┌────────────────────────────────────────┐
    │  📶 ●●●●  Status Bar      🌡️ 45°C      │  30px
    ├────────────────────────────────────────┤
    │                                        │
    │                                        │
    │         [Dithered Photo]               │  450px
    │                                        │
    │                                        │
    └────────────────────────────────────────┘

    Environment Variables:
        PHOTO_PATH: Path to image file (default: demo_landscape.jpg)

    Returns:
        Screen with status bar and photo widget.
    """

    return Screen(
        key="photo_frame",
        name="Photo Frame",
        display_name="Photo Frame",
        icon="🖼️",
        widgets=[
            StatusBarWidget(WidgetRegion(x=0, y=0, width=800, height=30)),
            PhotoWidget(
                WidgetRegion(x=0, y=30, width=800, height=450)
            ),
        ],
    )
