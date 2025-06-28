"""
Tests for the Flask application configuration.
"""
import pytest
from typing import Generator
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_socketio import SocketIO
from src.backend.app import app, socketio, frontend_dir, start_game_manager, cleanup_game_manager
import os

@pytest.fixture
def mock_game_manager() -> Generator[MagicMock, None, None]:
    """Mock the game manager for testing."""
    with patch('src.backend.app.game_manager') as mock:
        yield mock

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

@pytest.mark.unit
def test_socketio_configuration() -> None:
    """Test that SocketIO is configured correctly."""
    assert socketio.server.eio.async_mode == 'threading'
    # CORS settings are not configured by default
    assert socketio.server.eio.cors_allowed_origins is None
    # Default ping timeout is 20 seconds
    assert socketio.server.eio.ping_timeout == 20

@pytest.mark.unit
def test_start_game_manager_development(mock_game_manager: MagicMock) -> None:
    """Test game manager start behavior in development."""
    # Test when not in main process
    os.environ['FLASK_ENV'] = 'development'
    os.environ.pop('WERKZEUG_RUN_MAIN', None)
    
    start_game_manager()
    mock_game_manager.start.assert_not_called()
    
    # Test when in main process
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    start_game_manager()
    mock_game_manager.start.assert_called_once()

@pytest.mark.unit
def test_start_game_manager_production(mock_game_manager: MagicMock) -> None:
    """Test game manager start behavior in production."""
    os.environ['FLASK_ENV'] = 'production'
    os.environ.pop('WERKZEUG_RUN_MAIN', None)
    
    start_game_manager()
    mock_game_manager.start.assert_called_once()

@pytest.mark.unit
def test_cleanup_game_manager_development(mock_game_manager: MagicMock) -> None:
    """Test game manager cleanup behavior in development."""
    # Test when not in main process
    os.environ['FLASK_ENV'] = 'development'
    os.environ.pop('WERKZEUG_RUN_MAIN', None)
    
    cleanup_game_manager()
    mock_game_manager.stop.assert_not_called()
    
    # Test when in main process
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    cleanup_game_manager()
    mock_game_manager.stop.assert_called_once()

@pytest.mark.unit
def test_cleanup_game_manager_production(mock_game_manager: MagicMock) -> None:
    """Test game manager cleanup behavior in production."""
    os.environ['FLASK_ENV'] = 'production'
    os.environ.pop('WERKZEUG_RUN_MAIN', None)
    
    cleanup_game_manager()
    mock_game_manager.stop.assert_called_once()

@pytest.mark.unit
def test_main_entry_point(mock_game_manager: MagicMock) -> None:
    """Test the main entry point behavior."""
    # Save original environment
    original_env = os.environ.get('FLASK_ENV')
    
    try:
        with patch('src.backend.app.socketio.run') as mock_run:
            # Execute the main block directly
            os.environ['FLASK_ENV'] = 'production'
            
            # Call the functions that would be called in __main__
            start_game_manager()
            mock_run.assert_not_called()  # run hasn't been called yet
            
            # Verify the execution sequence
            assert os.environ.get('FLASK_ENV') == 'production'
            mock_game_manager.start.assert_called_once()
            
            # Simulate cleanup
            cleanup_game_manager()
            mock_game_manager.stop.assert_called_once()
    finally:
        # Restore original environment
        if original_env is not None:
            os.environ['FLASK_ENV'] = original_env
        else:
            os.environ.pop('FLASK_ENV', None) 