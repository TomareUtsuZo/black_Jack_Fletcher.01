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

def get_valid_game_time() -> datetime:
    """Helper to get a datetime within valid game bounds."""
    return datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)  # Mid-2024

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
        valid_dt = get_valid_game_time()
        game_time = GameTime.from_datetime(valid_dt)
        assert game_time.to_datetime() == valid_dt
        
        # Time before game start
        with pytest.raises(ValueError, match="Game time must be between"):
            GameTime.from_datetime(
                datetime(2023, 1, 1, tzinfo=timezone.utc)
            )
        
        # Time after game end
        with pytest.raises(ValueError, match="Game time must be between"):
            GameTime.from_datetime(
                datetime(2025, 2, 1, tzinfo=timezone.utc)
            )
        
        # Time without timezone
        with pytest.raises(ValueError, match="datetime must have timezone"):
            GameTime.from_datetime(
                datetime(2024, 6, 1)  # No tzinfo
            )
    
    def test_time_arithmetic_validation(self) -> None:
        """Test that arithmetic operations respect game time bounds."""
        mid_game = GameTime.from_datetime(get_valid_game_time())
        one_year = GameDuration.from_days(365)
        
        # Adding too much time
        with pytest.raises(ValueError, match="Game time must be between"):
            mid_game + one_year
        
        # Subtracting too much time
        with pytest.raises(ValueError, match="Game time must be between"):
            mid_game - one_year
        
        # Valid additions and subtractions should work
        one_day = GameDuration.from_days(1)
        next_day = mid_game + one_day
        result = next_day - mid_game
        duration = cast(GameDuration, result)  # Ensure we got GameDuration, not GameTime
        assert duration.days == 1
    
    def test_time_zone_handling(self) -> None:
        """Test handling of different time zones."""
        utc_time = GameTime.from_datetime(get_valid_game_time())
        
        # Convert to EST (UTC-5)
        est_zone = GameTimeZone.from_hours(-5, "EST")
        est_time = utc_time.in_zone(est_zone)
        
        # Check that the underlying timestamp is the same
        assert est_time.timestamp == utc_time.timestamp
        # But the formatted time reflects the zone difference
        assert est_time.to_datetime().hour == 7  # 12 UTC = 7 EST

class TestGameTimeManager:
    """Tests for the GameTimeManager class."""
    
    def test_initialization(self) -> None:
        """Test GameTimeManager initialization."""
        # Test with specific start time
        start_time = GameTime.from_datetime(get_valid_game_time())
        manager = GameTimeManager(start_time)
        assert manager.time_now == start_time
    
    def test_time_advancement(self) -> None:
        """Test advancing time by different durations."""
        start_time = GameTime.from_datetime(get_valid_game_time())
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
        start_time = GameTime.from_datetime(get_valid_game_time())
        manager = GameTimeManager(start_time)
        
        # Make several time advancements
        durations = [
            GameDuration.from_minutes(5),
            GameDuration.from_hours(1),
            GameDuration.from_minutes(30)
        ]
        
        expected_time = start_time
        for duration in durations:
            expected_time = expected_time + duration
            actual_time = manager.advance_time(duration)
            assert actual_time == expected_time
            assert manager.time_now == expected_time 