"""
Tests for the game models type definitions.
"""
from typing import Dict, Any, cast
import pytest
from src.backend.models import Position, PlayerState, GameState

@pytest.mark.unit
def test_position_type_creation(sample_position: Dict[str, int]) -> None:
    """Test that Position TypedDict can be created with correct types."""
    position: Position = {"x": sample_position["x"], "y": sample_position["y"]}
    assert isinstance(position["x"], int)
    assert isinstance(position["y"], int)

@pytest.mark.unit
def test_player_state_type_creation(sample_player: Dict[str, str]) -> None:
    """Test that PlayerState TypedDict can be created with correct types."""
    player: PlayerState = {"id": sample_player["id"]}
    assert isinstance(player["id"], str)

@pytest.mark.unit
def test_game_state_type_creation(sample_game: Dict[str, Any]) -> None:
    """Test that GameState TypedDict can be created with correct types."""
    raw_players = cast(Dict[str, Dict[str, Any]], sample_game["players"])
    players: Dict[str, PlayerState] = {
        player_id: {"id": str(player_data["id"])}
        for player_id, player_data in raw_players.items()
    }
    game: GameState = {
        "id": str(sample_game["id"]),
        "players": players
    }
    assert isinstance(game["id"], str)
    assert isinstance(game["players"], dict)
    assert isinstance(game["players"]["test_player"]["id"], str) 