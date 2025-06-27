"""
Tests for the Flask application configuration.
"""
import pytest
from flask import Flask
from flask_socketio import SocketIO
from src.backend.app import app, socketio, frontend_dir
import os

@pytest.mark.unit
def test_app_configuration() -> None:
    """Test that Flask app is configured correctly."""
    assert isinstance(app, Flask)
    assert isinstance(socketio, SocketIO)
    
    # Test template and static folder configuration
    expected_template_dir = os.path.join(frontend_dir, 'views', 'templates')
    expected_static_dir = os.path.join(frontend_dir, 'views', 'static')
    
    assert app.template_folder == expected_template_dir
    assert app.static_folder == expected_static_dir

@pytest.mark.unit
def test_blueprint_registration() -> None:
    """Test that game routes blueprint is registered."""
    assert 'game' in app.blueprints
    
    # Test some known routes are registered
    rules = [str(rule) for rule in app.url_map.iter_rules()]
    assert '/' in rules
    assert '/api/game/<game_id>' in rules
    assert '/api/game' in rules
    assert '/api/game/<game_id>/join' in rules 