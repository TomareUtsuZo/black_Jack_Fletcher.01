"""
Tests for the game routes.
"""
from typing import Dict, Any, Generator
import pytest
from flask.testing import FlaskClient
from src.backend.app import app
from src.backend.models.game_state_manager import GameState
from src.backend.services.game_service import game_manager

@pytest.fixture(autouse=True)
def setup_game_state() -> Generator[None, None, None]:
    """Setup game state before each test."""
    # Start in INITIALIZING state
    game_manager._state_machine._state = GameState.INITIALIZING
    # Transition to RUNNING state
    game_manager.start()
    yield
    # Clean up after test
    game_manager.stop()

@pytest.mark.unit
def test_index_route(client: FlaskClient) -> None:
    """Test that index route returns the index template."""
    response = client.get('/')
    assert response.status_code == 200
    # Since we're returning a rendered template, we expect text/html
    assert response.content_type == 'text/html; charset=utf-8'

@pytest.mark.unit
def test_get_game_status_route(client: FlaskClient) -> None:
    """Test that get_game_status route returns current game status."""
    response = client.get('/api/game/status')
    assert response.status_code == 200
    data = response.get_json()
    assert 'state' in data
    assert 'is_paused' in data
    assert 'current_time' in data
    assert 'time_rate' in data
    assert isinstance(data['state'], str)
    assert isinstance(data['is_paused'], bool)
    assert isinstance(data['current_time'], str)
    assert isinstance(data['time_rate'], str)

@pytest.mark.unit
def test_pause_game_route(client: FlaskClient) -> None:
    """Test that pause_game route pauses the game."""
    response = client.post('/api/game/pause')
    assert response.status_code == 200
    data = response.get_json()
    assert data == {'status': 'paused'}

    # Verify game status after pause
    status = client.get('/api/game/status').get_json()
    assert status['is_paused'] is True

@pytest.mark.unit
def test_unpause_game_route(client: FlaskClient) -> None:
    """Test that unpause_game route unpauses the game."""
    # First pause the game
    client.post('/api/game/pause')
    
    # Then unpause
    response = client.post('/api/game/unpause')
    assert response.status_code == 200
    data = response.get_json()
    assert data == {'status': 'running'}

    # Verify game status after unpause
    status = client.get('/api/game/status').get_json()
    assert status['is_paused'] is False

@pytest.mark.unit
def test_set_time_rate_route(client: FlaskClient) -> None:
    """Test that set_time_rate route sets the game time rate."""
    # Test setting minutes
    response = client.post('/api/game/time-rate', json={'minutes': 5})
    assert response.status_code == 200
    data = response.get_json()
    assert 'time_rate' in data
    assert isinstance(data['time_rate'], str)

    # Test setting seconds
    response = client.post('/api/game/time-rate', json={'seconds': 30})
    assert response.status_code == 200
    data = response.get_json()
    assert 'time_rate' in data
    assert isinstance(data['time_rate'], str)

@pytest.mark.unit
def test_get_game_state_route(client: FlaskClient) -> None:
    """Test that get_game_state route returns game state."""
    game_id = "test_game"
    response = client.get(f'/api/game/{game_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data == {'game_id': game_id}

@pytest.mark.unit
def test_create_game_route(client: FlaskClient) -> None:
    """Test that create_game route creates a game."""
    response = client.post('/api/game')
    assert response.status_code == 200
    data = response.get_json()
    assert data == {'status': 'created'}

@pytest.mark.unit
def test_join_game_route(client: FlaskClient) -> None:
    """Test that join_game route allows joining a game."""
    game_id = "test_game"
    response = client.post(f'/api/game/{game_id}/join')
    assert response.status_code == 200
    data = response.get_json()
    assert data == {'status': 'joined'}