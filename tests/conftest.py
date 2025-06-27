"""
Pytest configuration and shared fixtures.
"""
from typing import Dict, Generator
import pytest
from flask import Flask
from flask.testing import FlaskClient
from src.backend.app import app as flask_app

@pytest.fixture
def app() -> Flask:
    """Create a Flask application for testing."""
    flask_app.config.update({
        "TESTING": True,
    })
    return flask_app

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the Flask application."""
    return app.test_client()

@pytest.fixture
def sample_position() -> Dict[str, int]:
    """Create a sample Position for testing."""
    return {"x": 0, "y": 0}

@pytest.fixture
def sample_player() -> Dict[str, str]:
    """Create a sample PlayerState for testing."""
    return {"id": "test_player"}

@pytest.fixture
def sample_game(sample_player: Dict[str, str]) -> Dict[str, object]:
    """Create a sample GameState for testing."""
    return {
        "id": "test_game",
        "players": {"test_player": sample_player}
    } 