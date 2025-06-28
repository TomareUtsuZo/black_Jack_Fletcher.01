"""
Tests for game state management functionality.

Tests the following:
- GameStateManager initialization
- Time rate management
- Game state transitions
- Time progression
"""

import pytest
from datetime import datetime, timezone
from typing import Generator
from src.backend.models.game_state_manager import GameStateManager, GameState
from src.backend.models.common.time import GameTime, GameDuration, GameTimeManager
from src.backend.models.common.time.time_zone import GameTimeZone

def get_valid_game_time() -> GameTime:
    """Helper to get a datetime within valid game bounds."""
    return GameTime.from_datetime(
        datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)
    )

class TestGameStateManager:
    """Tests for the GameStateManager class."""
    
    @pytest.fixture(autouse=True)
    def cleanup_singleton(self) -> Generator[None, None, None]:
        """
        Reset the singleton instance before and after each test.
        
        This ensures each test starts with a fresh GameStateManager.
        """
        GameStateManager._instance = None
        yield
        GameStateManager._instance = None
    
    @pytest.fixture
    def game_time_manager(self) -> GameTimeManager:
        """Fixture to create GameTimeManager with valid time."""
        return GameTimeManager(start_time=get_valid_game_time())
    
    def test_singleton_pattern(self, game_time_manager: GameTimeManager) -> None:
        """Test that GameStateManager enforces singleton pattern."""
        # First instance should work
        instance1 = GameStateManager(time_manager=game_time_manager)
        assert instance1 is not None
        
        # Second instance should raise error
        with pytest.raises(RuntimeError, match="GameStateManager already instantiated"):
            GameStateManager(time_manager=game_time_manager)
        
        # get_instance should return same instance
        instance2 = GameStateManager.get_instance()
        assert instance2 is instance1
    
    def test_initial_state(self, game_time_manager: GameTimeManager) -> None:
        """Test initial state of GameStateManager."""
        manager = GameStateManager(time_manager=game_time_manager)
        
        # Check initial values
        assert manager.game_state == GameState.INITIALIZING
        assert not manager.is_paused
        assert manager.time_rate == GameStateManager.DEFAULT_TIME_RATE
        assert isinstance(manager.current_time, GameTime)
    
    def test_time_rate_bounds(self, game_time_manager: GameTimeManager) -> None:
        """Test time rate validation bounds."""
        manager = GameStateManager(time_manager=game_time_manager)
        
        # Test minimum bound
        with pytest.raises(ValueError, match="Time rate must be between"):
            manager.set_time_rate(GameDuration.from_seconds(0.5))  # Too small
        
        # Test maximum bound
        with pytest.raises(ValueError, match="Time rate must be between"):
            manager.set_time_rate(GameDuration.from_hours(2))  # Too large
        
        # Test valid values
        manager.set_time_rate(GameStateManager.MIN_TIME_RATE)  # Should work
        manager.set_time_rate(GameStateManager.MAX_TIME_RATE)  # Should work
        manager.set_time_rate(GameDuration.from_minutes(30))  # Should work
    
    def test_time_rate_convenience_methods(self, game_time_manager: GameTimeManager) -> None:
        """Test the convenience methods for setting time rate."""
        manager = GameStateManager(time_manager=game_time_manager)
        
        # Test seconds
        manager.set_time_rate_seconds(30)
        assert manager.time_rate.seconds == 30
        
        # Test minutes
        manager.set_time_rate_minutes(0.5)  # 30 seconds
        assert manager.time_rate.seconds == 30
        
        # Test invalid values
        with pytest.raises(ValueError):
            manager.set_time_rate_seconds(0)  # Too small
        
        with pytest.raises(ValueError):
            manager.set_time_rate_minutes(61)  # Too large
    
    def test_state_transitions(self, game_time_manager: GameTimeManager) -> None:
        """
        Test game state transitions.
        
        Note: We intentionally do not test unpausing a completed game as it's an edge case
        that doesn't affect gameplay. A completed game is done and any attempts to unpause
        will naturally fail with "Game is not paused" since a completed game is not paused.
        """
        manager = GameStateManager(time_manager=game_time_manager)
        
        # Initial state
        assert manager.game_state == GameState.INITIALIZING
        
        # Test: INITIALIZING -> RUNNING
        manager.start()
        assert manager.game_state == GameState.RUNNING
        assert not manager.is_paused
        
        # Test: RUNNING -> PAUSED
        manager.pause()
        assert manager.game_state == GameState.PAUSED
        assert manager.is_paused
        
        # Test: PAUSED -> RUNNING
        manager.unpause()  # type: ignore[unreachable]
        assert manager.game_state == GameState.RUNNING
        assert not manager.is_paused
        
        # Test: RUNNING -> COMPLETED
        manager.stop()
        assert manager.game_state == GameState.COMPLETED
    
    def test_manual_tick(self, game_time_manager: GameTimeManager) -> None:
        """Test manual tick advancement."""
        manager = GameStateManager(time_manager=game_time_manager)
        manager.set_time_rate_minutes(1)  # 1 minute per tick
        
        # Set state to RUNNING without starting scheduler
        manager._state = GameState.RUNNING
        initial_time = manager.current_time
        
        # Manually trigger tick
        manager.tick()
        
        # Check time advanced by exactly one minute
        time_diff = manager.current_time - initial_time
        assert isinstance(time_diff, GameDuration)  # Type check for mypy
        assert time_diff.minutes == 1.0  # Should advance exactly one minute
        
        manager.stop() 