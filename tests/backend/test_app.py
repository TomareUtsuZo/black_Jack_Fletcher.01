"""
Tests for the Flask application configuration matching the current architecture:
- No SocketIO instance
- No registered routes/blueprints in this module
"""
import pytest
from typing import Generator
from unittest.mock import patch, MagicMock
from flask import Flask
from src.backend.app import app, frontend_dir, start_game_manager, cleanup_game_manager
import os

@pytest.fixture
def mock_game_manager() -> Generator[MagicMock, None, None]:
    """Mock the game manager for testing."""
    with patch('src.backend.app.game_manager') as mock:
        yield mock

@pytest.mark.unit
def test_app_configuration() -> None:
    """Test that Flask app is configured correctly without SocketIO or routes."""
    assert isinstance(app, Flask)

    # Template and static folder configuration
    expected_template_dir = os.path.join(frontend_dir, 'views', 'templates')
    expected_static_dir = os.path.join(frontend_dir, 'views', 'static')

    assert app.template_folder == expected_template_dir
    assert app.static_folder == expected_static_dir

# No blueprint/route assertions; app currently does not register routes here

# No SocketIO assertions; app does not provide a SocketIO instance

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
    """Test the main entry point behavior using Flask's app.run."""
    original_env = os.environ.get('FLASK_ENV')

    try:
        with patch('src.backend.app.app.run') as mock_run:
            os.environ['FLASK_ENV'] = 'production'

            # Call the functions that would be called in __main__
            start_game_manager()
            mock_run.assert_not_called()  # run hasn't been called yet in this context

            # Verify the execution sequence
            assert os.environ.get('FLASK_ENV') == 'production'
            mock_game_manager.start.assert_called_once()

            # Simulate cleanup
            cleanup_game_manager()
            mock_game_manager.stop.assert_called_once()
    finally:
        if original_env is not None:
            os.environ['FLASK_ENV'] = original_env
        else:
            os.environ.pop('FLASK_ENV', None)