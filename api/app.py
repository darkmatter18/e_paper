"""FastAPI application factory."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from process import EngineProcessManager
from screens import AVAILABLE_SCREENS, DEFAULT_SCREEN
from settings import TEMPLATES_DIR, get_settings

logger = logging.getLogger(__name__)

# Configure templates directory
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Get settings
settings = get_settings()


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


class InfoResponse(BaseModel):
    """API info response."""

    name: str
    version: str
    available_screens: list[str]
    current_screen: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan handler for startup/shutdown."""
    # Startup
    logger.info("Starting engine process...")
    manager = EngineProcessManager(initial_screen=DEFAULT_SCREEN)
    manager.start_engine()
    app.state.engine_manager = manager
    app.state.current_screen = DEFAULT_SCREEN

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
        title="E-Paper Display API",
        description="Control e-paper display screens via REST API",
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

        # Check password
        if password == settings.auth.password:
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
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "health_status": "healthy",
                "engine_running": manager.is_alive(),
                "current_screen": app.state.current_screen,
                "available_screens": list(AVAILABLE_SCREENS.keys()),
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

    return app
