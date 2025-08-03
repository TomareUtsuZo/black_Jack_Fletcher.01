"""
Pytest configuration and shared fixtures.
"""
import sys
import os
from typing import Dict, Generator
import pytest
from flask import Flask
from flask.testing import FlaskClient
from src.backend.app import app as flask_app

def pytest_configure(config):
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        src_path = os.path.join(project_root, 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        print(f'Added to sys.path: {src_path}')  # Debug print
    except Exception as e:
        print(f'Error adding path: {e}')

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