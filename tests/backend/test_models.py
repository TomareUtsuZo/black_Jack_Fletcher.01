"""
Tests for the game models type definitions.
"""
from typing import Dict
import pytest
from src.backend.models import Position, PlayerState, GameState

@pytest.mark.unit
def test_position_type_creation(sample_position: Dict[str, int]) -> None:
    """Test that Position TypedDict can be created with correct types."""
    position: Position = sample_position
    assert isinstance(position["x"], int)
    assert isinstance(position["y"], int)

@pytest.mark.unit
def test_player_state_type_creation(sample_player: Dict[str, str]) -> None:
    """Test that PlayerState TypedDict can be created with correct types."""
    player: PlayerState = sample_player
    assert isinstance(player["id"], str)

@pytest.mark.unit
def test_game_state_type_creation(sample_game: Dict[str, object]) -> None:
    """Test that GameState TypedDict can be created with correct types."""
    game: GameState = sample_game
    assert isinstance(game["id"], str)
    assert isinstance(game["players"], dict)
    assert isinstance(game["players"]["test_player"]["id"], str) 