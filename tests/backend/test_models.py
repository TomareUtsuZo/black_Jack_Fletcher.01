"""
Tests for the game models type definitions.
"""
from typing import Dict, Any, cast
import pytest
from src.backend.models.common import Position
from src.backend.models import PlayerState, GameState

@pytest.mark.unit
def test_position_type_creation(sample_position: Dict[str, int]) -> None:
    """Test that Position can be created with correct types."""
    position = Position(x=sample_position["x"], y=sample_position["y"])
    assert isinstance(position.x, int)
    assert isinstance(position.y, int)

@pytest.mark.unit
def test_position_utility_methods() -> None:
    """Test Position's utility methods."""
    pos1 = Position(x=0.0, y=0.0)
    pos2 = Position(x=3.0, y=4.0)
    
    # Test distance calculation
    assert pos1.distance_to(pos2) == 5.0
    
    # Test tuple conversion
    assert pos1.to_tuple() == (0.0, 0.0)
    
    # Test from_tuple creation
    pos3 = Position.from_tuple((1.0, 2.0))
    assert pos3.x == 1.0
    assert pos3.y == 2.0
    
    # Test string representation
    assert str(pos1) == "Position(x=0.0, y=0.0)"

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