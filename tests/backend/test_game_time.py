"""
Tests for game time functionality.

Tests the following:
- GameTime: Point in time representation
- GameDuration: Time interval representation
- GameTimeManager: Time progression management
"""

import pytest
from datetime import datetime, timezone, timedelta
from typing import cast
from src.backend.models.common.time import GameTime, GameDuration, GameTimeManager, GameTimeZone

def get_valid_game_time() -> GameTime:
    """Helper to get a valid game time."""
    return GameTime.from_datetime(
        datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)  # Mid-2024
    )

class TestGameDuration:
    """Tests for the GameDuration class."""
    
    def test_creation_from_different_units(self) -> None:
        """Test creating durations using different time units."""
        one_hour = GameDuration.from_hours(1)
        assert one_hour.seconds == 3600
        
        five_minutes = GameDuration.from_minutes(5)
        assert five_minutes.seconds == 300
        
        two_days = GameDuration.from_days(2)
        assert two_days.seconds == 172800
    
    def test_duration_arithmetic(self) -> None:
        """Test arithmetic operations between durations."""
        duration1 = GameDuration.from_minutes(30)  # 30 minutes
        duration2 = GameDuration.from_minutes(15)  # 15 minutes
        
        # Addition
        total = duration1 + duration2
        assert total.minutes == 45
        
        # Subtraction
        difference = duration1 - duration2
        assert difference.minutes == 15
        
        # Multiplication
        doubled = duration1 * 2
        assert doubled.minutes == 60
        
        # Division by scalar
        result = duration1 / 2
        halved = cast(GameDuration, result)  # Ensure we got GameDuration, not float
        assert halved.minutes == 15
        
        # Division by another duration
        ratio = duration1 / duration2
        assert isinstance(ratio, float)  # Division by GameDuration always gives float
        assert ratio == 2.0

class TestGameTime:
    """Tests for the GameTime class."""
    
    def test_creation_and_validation(self) -> None:
        """Test creating GameTime with validation."""
        # Valid time
        valid_dt = datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)
        game_time = GameTime.from_datetime(valid_dt)
        assert game_time.to_datetime() == valid_dt
        
        # Time before game start
        with pytest.raises(ValueError, match="Game time must be between"):
            GameTime.from_datetime(
                datetime(1899, 12, 31, tzinfo=timezone.utc)  # Before game start
            )
        
        # Time without timezone
        with pytest.raises(ValueError, match="datetime must have timezone"):
            GameTime.from_datetime(
                datetime(2024, 6, 1)  # No tzinfo
            )
    
    def test_time_comparisons(self) -> None:
        """Test time comparison operations."""
        time1 = GameTime.from_datetime(datetime(2024, 1, 1, tzinfo=timezone.utc))
        time2 = GameTime.from_datetime(datetime(2024, 1, 2, tzinfo=timezone.utc))
        time3 = GameTime.from_datetime(datetime(2024, 1, 1, tzinfo=timezone.utc))
        
        # Equality
        assert time1 == time3
        assert time1 != time2
        
        # Less than
        assert time1 < time2
        assert not (time2 < time1)
        
        # Less than or equal
        assert time1 <= time2
        assert time1 <= time3
        assert not (time2 <= time1)
        
        # Greater than
        assert time2 > time1
        assert not (time1 > time2)
        
        # Greater than or equal
        assert time2 >= time1
        assert time1 >= time3
        assert not (time1 >= time2)

class TestGameTimeManager:
    """Tests for the GameTimeManager class."""
    
    def test_initialization(self) -> None:
        """Test GameTimeManager initialization."""
        # Test with specific start time
        start_time = get_valid_game_time()
        manager = GameTimeManager(start_time)
        assert manager.time_now == start_time
    
    def test_time_advancement(self) -> None:
        """Test advancing time by different durations."""
        start_time = get_valid_game_time()
        manager = GameTimeManager(start_time)
        
        # Advance by 5 minutes
        five_min = GameDuration.from_minutes(5)
        new_time = manager.advance_time(five_min)
        assert new_time.to_datetime().minute == 5
        
        # Advance by 1 hour
        one_hour = GameDuration.from_hours(1)
        new_time = manager.advance_time(one_hour)
        assert new_time.to_datetime().hour == 13
        assert new_time.to_datetime().minute == 5
    
    def test_time_consistency(self) -> None:
        """Test that time advances consistently and maintains state."""
        start_time = get_valid_game_time()
        manager = GameTimeManager(start_time)
        
        # Make multiple time advancements
        one_min = GameDuration.from_minutes(1)
        for _ in range(5):
            manager.advance_time(one_min)
            
        # Check final time is correct
        final_time = manager.time_now
        time_diff = final_time - start_time
        assert isinstance(time_diff, GameDuration)
        assert time_diff.minutes == 5.0 