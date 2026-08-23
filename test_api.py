"""Test script for FastAPI endpoints (without hardware).

This script tests the API endpoints without actually starting the display engine.
Useful for verifying API structure before deployment to Raspberry Pi.
"""

import os
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# Disable auth for testing by setting empty password
os.environ["AUTH_PASSWORD"] = ""

load_dotenv()

# Mock the engine process for testing
import sys
from unittest.mock import Mock, patch

# Mock hardware modules
sys.modules["lib.waveshare_epd"] = Mock()
sys.modules["lib.waveshare_epd.epd7in5b_V2"] = Mock()

# Now import the app
from api import create_app


def test_api():
    """Test API endpoints."""
    print("=" * 60)
    print("Testing FastAPI Endpoints (Mock Mode)")
    print("=" * 60)

    # Patch EngineProcessManager to not actually start the process
    with patch("api.app.EngineProcessManager") as MockManager:
        # Setup mock manager
        mock_manager = Mock()
        mock_manager.is_alive.return_value = True
        mock_manager.current_screen = "datetime_weather_forecast"
        MockManager.return_value = mock_manager

        # Create app
        app = create_app()

        # Manually set app.state since TestClient doesn't fully initialize lifespan
        app.state.engine_manager = mock_manager
        app.state.current_screen = "datetime_weather_forecast"

        client = TestClient(app)

        # Test 1: Root endpoint (Web UI)
        print("\n1. Testing GET / (Web UI)")
        response = client.get("/")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "E-Paper Display" in response.text
        assert "Available Screens" in response.text
        print("   ✓ Web UI renders successfully")

        # Test 2: Health endpoint
        print("\n2. Testing GET /health")
        response = client.get("/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        print("   ✓ Health endpoint works")

        # Test 3: Switch screen (valid)
        print("\n3. Testing PUT /api/v1/screen (valid screen)")
        response = client.put(
            "/api/v1/screen", json={"screen": "todays_weather"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["screen"] == "todays_weather"
        assert "Switched" in response.json()["message"]
        print("   ✓ Screen switch works")

        # Test 4: Switch to same screen (no-op)
        print("\n4. Testing PUT /api/v1/screen (same screen)")
        response = client.put(
            "/api/v1/screen", json={"screen": "todays_weather"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["screen"] == "todays_weather"
        assert "Already on" in response.json()["message"]
        print("   ✓ Duplicate screen switch properly handled")

        # Test 5: Switch screen (invalid)
        print("\n5. Testing PUT /api/v1/screen (invalid screen)")
        response = client.put(
            "/api/v1/screen", json={"screen": "nonexistent"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 400
        print("   ✓ Invalid screen properly rejected")

        # Test 6: Available screens
        print("\n6. Checking available screens")
        from screens import AVAILABLE_SCREENS
        screens = list(AVAILABLE_SCREENS.keys())
        print(f"   Available: {screens}")
        assert "datetime_weather_forecast" in screens
        assert "todays_weather" in screens
        assert "digital_clock" in screens
        print("   ✓ All screens registered")

    print("\n" + "=" * 60)
    print("✅ All API tests passed!")
    print("\nAPI Endpoints:")
    print("  GET  /              - Web UI control panel")
    print("  GET  /health        - Health check (JSON)")
    print("  PUT  /api/v1/screen - Switch screen (JSON)")
    print("\nUsage:")
    print("  Web UI: Open http://localhost:8000 in your browser")
    print("  API:    curl -X PUT http://localhost:8000/api/v1/screen \\")
    print('               -H "Content-Type: application/json" \\')
    print('               -d \'{"screen": "todays_weather"}\'')
    print("=" * 60)


if __name__ == "__main__":
    test_api()
