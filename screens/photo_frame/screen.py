"""Photo frame screen - display dithered photos."""

import os
from pathlib import Path

from screens.photo_frame.widgets import PhotoWidget
from settings.settings import BASE_DIR
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
    # Get image path from environment or use demo
    photo_path = os.getenv("PHOTO_PATH")

    if photo_path:
        photo_path = Path(photo_path)
        if not photo_path.exists():
            # Fall back to demo if specified path doesn't exist
            print(f"Warning: PHOTO_PATH '{photo_path}' not found, using demo image")
            photo_path = BASE_DIR / "demo_landscape.jpg"
    else:
        # Default to demo image
        photo_path = BASE_DIR / "demo_landscape.jpg"

    # Check if demo exists
    if not photo_path.exists():
        # Create a placeholder error message
        # In production, you'd handle this more gracefully
        raise FileNotFoundError(
            f"Photo not found: {photo_path}. "
            "Set PHOTO_PATH environment variable to specify an image."
        )

    return Screen(
        key="photo_frame",
        name="Photo Frame",
        display_name="Photo Frame",
        icon="🖼️",
        widgets=[
            StatusBarWidget(WidgetRegion(x=0, y=0, width=800, height=30)),
            PhotoWidget(
                WidgetRegion(x=0, y=30, width=800, height=450),
                image_path=photo_path,
                use_red_channel=True,  # Use 3-color dithering
            ),
        ],
    )
