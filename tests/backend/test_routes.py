"""
Tests for the game routes.
"""
from typing import Dict, Any
import pytest
from flask.testing import FlaskClient
from src.backend.app import app

@pytest.mark.unit
def test_index_route(client: FlaskClient) -> None:
    """Test that index route returns the index template."""
    response = client.get('/')
    assert response.status_code == 200
    # Since we're returning a rendered template, we expect text/html
    assert response.content_type == 'text/html; charset=utf-8'

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