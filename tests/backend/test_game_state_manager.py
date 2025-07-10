"""
Tests for game state management functionality.

Tests the following:
- GameStateManager initialization
- Time rate management
- Game state transitions
- Time progression
- Unit management
- Error handling
"""

import pytest
from typing import Generator
from datetime import datetime, timezone
from src.backend.models.game_state_manager import GameStateManager, initialize_game_state, GameState
from src.backend.models.common.time import GameTimeManager, GameDuration, GameTime

def get_valid_game_time() -> GameTime:
    """Helper to get a datetime within valid game bounds."""
    return GameTime.from_datetime(
        datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)
    )

class TestGameStateManager:
    """Test suite for GameStateManager class."""

    @pytest.fixture(autouse=True)
    def cleanup_singleton(self) -> Generator[None, None, None]:
        """
        Reset the singleton instance before and after each test.
        
        This ensures each test starts with a fresh GameStateManager.
        """
        def reset_instance() -> None:
            if GameStateManager._instance is not None:
                try:
                    GameStateManager._instance._time_controller.stop_scheduler()
                except Exception:
                    pass
                # Clear all instance attributes
                for attr in list(GameStateManager._instance.__dict__.keys()):
                    delattr(GameStateManager._instance, attr)
                GameStateManager._instance = None
        
        # Reset before test
        reset_instance()
        
        yield
        
        # Reset after test
        reset_instance()

    def test_singleton_pattern(self) -> None:
        """Test that GameStateManager follows the singleton pattern."""
        manager1 = initialize_game_state()
        manager2 = initialize_game_state()
        assert manager1 is manager2

    def test_initial_state(self) -> None:
        """Test initial game state."""
        manager = initialize_game_state()
        assert manager.game_state == GameState.INITIALIZING

    def test_time_rate_bounds(self) -> None:
        """Test time rate bounds."""
        manager = initialize_game_state()
        assert manager.time_rate == GameDuration.from_minutes(1)  # Default rate
        
        # Test upper bound
        manager.set_time_rate(GameDuration.from_hours(1))  # 1 hour
        assert manager.time_rate == GameDuration.from_hours(1)
        
        # Test lower bound
        manager.set_time_rate(GameDuration.from_seconds(1))  # 1 second
        assert manager.time_rate == GameDuration.from_seconds(1)

    def test_state_transitions(self) -> None:
        """Test game state transitions."""
        manager = initialize_game_state()

        # Test initial state
        initial_state = manager.game_state
        assert initial_state == GameState.INITIALIZING

        # Test transition to running
        manager.start()
        running_state = manager.game_state
        assert running_state == GameState.RUNNING

        # Test transition to paused
        manager.pause()
        paused_state = manager.game_state
        assert paused_state == GameState.PAUSED

        # Test transition back to running
        manager.resume()
        final_state = manager.game_state
        assert final_state == GameState.RUNNING

        # Test transition to completed
        manager.complete()
        assert manager.game_state == GameState.COMPLETED

    def test_game_state_equality(self) -> None:
        """Test game state equality comparisons."""
        # Test that states are not equal to each other
        states = [GameState.INITIALIZING, GameState.RUNNING, GameState.PAUSED, GameState.COMPLETED]
        for i, state1 in enumerate(states):
            for j, state2 in enumerate(states):
                if i != j:
                    assert state1 != state2, f"States should not be equal: {state1} == {state2}"

    @pytest.mark.skip(reason="Unit operations not yet implemented")
    def test_unit_operations(self) -> None:
        """Test unit addition, removal, and queries."""
        pass

    def test_unit_movement_and_targeting(self) -> None:
        """Test unit movement and targeting."""
        manager = initialize_game_state()
        with pytest.raises(NotImplementedError):
            manager.set_unit_movement("test_id", {"waypoints": [], "speed": 0.0})
        with pytest.raises(NotImplementedError):
            manager.set_unit_targeting("test_id", {"target_id": "", "priority": 0})

    def test_time_limit_handling(self) -> None:
        """Test handling of time limit reached."""
        manager = initialize_game_state()
        manager.start()
        manager._handle_time_limit_reached(ValueError("Time limit reached"))
        assert manager.game_state == GameState.COMPLETED

    def test_load_default_scenario(self) -> None:
        """Test loading the default scenario."""
        game_state = initialize_game_state()
        
        # Test map center is set correctly
        assert game_state.map_center is not None, "Map center should not be None"
        assert game_state.map_center.x == -177.35, "Map center x coordinate should be -177.35"
        assert game_state.map_center.y == 28.2, "Map center y coordinate should be 28.2"
        
        # Test map boundaries are set correctly
        boundaries = game_state.map_boundaries
        assert 'north' in boundaries, "North boundary should be set"
        assert 'south' in boundaries, "South boundary should be set"
        assert 'east' in boundaries, "East boundary should be set"
        assert 'west' in boundaries, "West boundary should be set"
        
        # Test boundary relationships to center
        assert boundaries['north'].y > game_state.map_center.y, "North boundary should be above center"
        assert boundaries['south'].y < game_state.map_center.y, "South boundary should be below center"
        assert boundaries['east'].x > game_state.map_center.x, "East boundary should be right of center"
        assert boundaries['west'].x < game_state.map_center.x, "West boundary should be left of center" 