"""FastAPI application factory."""

import logging
import shutil
from contextlib import asynccontextmanager

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from process import EngineProcessManager
from screens import AVAILABLE_SCREENS, DEFAULT_SCREEN, get_screens
from settings import BASE_DIR, PHOTOS_DIR, TEMPLATES_DIR, get_settings

logger = logging.getLogger(__name__)

# Configure templates directory
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Get settings
settings = get_settings()

# Password hasher
ph = PasswordHasher()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against Argon2 hash.

    Args:
        password: Plain text password to verify
        password_hash: Argon2 hash from AUTH_PASSWORD

    Returns:
        True if password matches, False otherwise
    """
    try:
        ph.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False
    except Exception as e:  # noqa: BLE001
        logger.error(f"Password verification error: {e}")
        return False


def check_auth(request: Request) -> bool:
    """Check if request is authenticated.

    Args:
        request: FastAPI request object

    Returns:
        True if authenticated, False otherwise
    """
    # If no password is set in settings, auth is disabled
    if not settings.auth.password:
        return True

    return request.session.get("authenticated", False)


def require_auth(request: Request):
    """Dependency to require authentication.

    Args:
        request: FastAPI request object

    Raises:
        HTTPException: 401 if not authenticated
    """
    if not check_auth(request):
        raise HTTPException(status_code=401, detail="Not authenticated")


class ScreenSwitchRequest(BaseModel):
    """Request body for switching screens."""

    screen: str


class ScreenSwitchResponse(BaseModel):
    """Response for screen switch operation."""

    success: bool
    screen: str
    message: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    engine_running: bool
    current_screen: str
    current_mode: str


class InfoResponse(BaseModel):
    """API info response."""

    name: str
    version: str
    available_screens: list[str]
    current_screen: str


class ModeSwitchRequest(BaseModel):
    """Request body for switching display modes."""

    mode: str  # "photo" or "screen"


class ModeSwitchResponse(BaseModel):
    """Response for mode switch operation."""

    success: bool
    mode: str
    message: str


class PhotoUploadResponse(BaseModel):
    """Response for photo upload operation."""

    success: bool
    filename: str
    message: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan handler for startup/shutdown."""
    # Startup
    logger.info("Starting engine process...")
    manager = EngineProcessManager(initial_screen=DEFAULT_SCREEN)
    manager.start_engine()
    app.state.engine_manager = manager
    app.state.current_screen = DEFAULT_SCREEN
    # Track current mode: "photo" or "screen"
    # Default is "photo" since DEFAULT_SCREEN is "photo_frame"
    app.state.current_mode = "photo" if DEFAULT_SCREEN == "photo_frame" else "screen"

    yield

    # Shutdown
    logger.info("Stopping engine process...")
    manager.stop_engine()


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI app instance
    """
    app = FastAPI(
        title="Darshan API",
        description="A sacred glimpse - Control display screens via REST API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Add session middleware for authentication
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.auth.secret_key,
        session_cookie="epaper_session",
        max_age=86400,  # 24 hours
    )

    # Mount static files directory
    static_dir = BASE_DIR / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/login", response_class=HTMLResponse)
    def login_page(request: Request):
        """Render login page."""
        # If already authenticated, redirect to home
        if check_auth(request):
            return RedirectResponse(url="/", status_code=302)

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={},
        )

    @app.post("/login", response_class=HTMLResponse)
    def login(request: Request, password: str = Form(...)):
        """Handle login form submission."""
        # If no password is configured, allow access
        if not settings.auth.password:
            request.session["authenticated"] = True
            return RedirectResponse(url="/", status_code=302)

        # Verify password against Argon2 hash
        if verify_password(password, settings.auth.password):
            request.session["authenticated"] = True
            return RedirectResponse(url="/", status_code=302)

        # Invalid password
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Invalid password"},
        )

    @app.get("/logout")
    def logout(request: Request):
        """Logout and clear session."""
        request.session.clear()
        return RedirectResponse(url="/login", status_code=302)

    @app.get("/", response_class=HTMLResponse)
    def root(request: Request):
        """Render web UI control panel."""
        # Check authentication
        if not check_auth(request):
            return RedirectResponse(url="/login", status_code=302)

        manager: EngineProcessManager = app.state.engine_manager
        screens = get_screens()

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "health_status": "healthy",
                "engine_running": manager.is_alive(),
                "current_screen": app.state.current_screen,
                "current_mode": app.state.current_mode,
                "screens": screens,
            },
        )

    @app.get("/health", response_model=HealthResponse)
    def health(request: Request):
        """Health check endpoint."""
        # Require authentication
        if not check_auth(request):
            raise HTTPException(status_code=401, detail="Not authenticated")

        manager: EngineProcessManager = app.state.engine_manager
        return HealthResponse(
            status="healthy",
            engine_running=manager.is_alive(),
            current_screen=app.state.current_screen,
            current_mode=app.state.current_mode,
        )

    @app.put("/api/v1/screen", response_model=ScreenSwitchResponse)
    def switch_screen(screen_request: ScreenSwitchRequest, request: Request):
        """Switch to a different screen.

        Args:
            screen_request: Screen name to switch to
            request: FastAPI request object for auth check

        Returns:
            Success response with new screen name

        Raises:
            HTTPException: If screen name invalid or engine not running
        """
        # Require authentication
        if not check_auth(request):
            raise HTTPException(status_code=401, detail="Not authenticated")

        if screen_request.screen not in AVAILABLE_SCREENS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown screen '{screen_request.screen}'. Available: {list(AVAILABLE_SCREENS.keys())}",
            )

        # Check if already on requested screen
        if app.state.current_screen == screen_request.screen:
            return ScreenSwitchResponse(
                success=True,
                screen=screen_request.screen,
                message=f"Already on '{screen_request.screen}' screen",
            )

        manager: EngineProcessManager = app.state.engine_manager

        if not manager.is_alive():
            raise HTTPException(
                status_code=503, detail="Engine process is not running"
            )

        try:
            manager.switch_screen(screen_request.screen)
            app.state.current_screen = screen_request.screen

            return ScreenSwitchResponse(
                success=True,
                screen=screen_request.screen,
                message=f"Switched to '{screen_request.screen}' screen",
            )
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to switch screen: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to switch screen: {str(e)}"
            )

    @app.put("/api/v1/mode", response_model=ModeSwitchResponse)
    def switch_mode(mode_request: ModeSwitchRequest, request: Request):
        """Switch between photo mode and screen mode.

        Args:
            mode_request: Mode to switch to ("photo" or "screen")
            request: FastAPI request object for auth check

        Returns:
            Success response with new mode

        Raises:
            HTTPException: If mode invalid or engine not running
        """
        # Require authentication
        if not check_auth(request):
            raise HTTPException(status_code=401, detail="Not authenticated")

        if mode_request.mode not in ["photo", "screen"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode '{mode_request.mode}'. Must be 'photo' or 'screen'",
            )

        # Check if already in requested mode
        if app.state.current_mode == mode_request.mode:
            return ModeSwitchResponse(
                success=True,
                mode=mode_request.mode,
                message=f"Already in {mode_request.mode} mode",
            )

        manager: EngineProcessManager = app.state.engine_manager

        if not manager.is_alive():
            raise HTTPException(
                status_code=503, detail="Engine process is not running"
            )

        try:
            # Switch to appropriate screen based on mode
            if mode_request.mode == "photo":
                target_screen = "photo_frame"
            else:
                # Switch to last used screen, or default to first non-photo screen
                target_screen = (
                    app.state.current_screen
                    if app.state.current_screen != "photo_frame"
                    else next(
                        (s.key for s in get_screens() if s.key != "photo_frame"),
                        "digital_clock",
                    )
                )

            manager.switch_screen(target_screen)
            app.state.current_screen = target_screen
            app.state.current_mode = mode_request.mode

            return ModeSwitchResponse(
                success=True,
                mode=mode_request.mode,
                message=f"Switched to {mode_request.mode} mode (screen: {target_screen})",
            )
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to switch mode: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to switch mode: {str(e)}"
            )

    @app.post("/api/v1/upload-photo", response_model=PhotoUploadResponse)
    async def upload_photo(request: Request, file: UploadFile = File(...)):
        """Upload a photo to be displayed in photo mode.

        Args:
            request: FastAPI request object for auth check
            file: Uploaded image file

        Returns:
            Success response with filename

        Raises:
            HTTPException: If file invalid or upload fails
        """
        # Require authentication
        if not check_auth(request):
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Must be an image (JPEG, PNG, etc.)",
            )

        try:
            # Save uploaded file as image.jpg
            photo_path = PHOTOS_DIR / "image.jpg"
            with photo_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # If currently in photo mode, trigger a screen refresh
            if app.state.current_mode == "photo":
                manager: EngineProcessManager = app.state.engine_manager
                if manager.is_alive():
                    manager.switch_screen("photo_frame")

            return PhotoUploadResponse(
                success=True,
                filename="image.jpg",
                message="Photo uploaded successfully",
            )
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to upload photo: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to upload photo: {str(e)}"
            )

    @app.get("/api/v1/current-photo")
    def get_current_photo(request: Request):
        """Get the current photo displayed in photo mode.

        Args:
            request: FastAPI request object for auth check

        Returns:
            Current photo file

        Raises:
            HTTPException: If photo not found or access denied
        """
        # Require authentication
        if not check_auth(request):
            raise HTTPException(status_code=401, detail="Not authenticated")

        photo_path = PHOTOS_DIR / "image.jpg"
        if not photo_path.exists():
            raise HTTPException(status_code=404, detail="Photo not found")

        return FileResponse(
            photo_path,
            media_type="image/jpeg",
            filename="current-photo.jpg",
        )

    return app
