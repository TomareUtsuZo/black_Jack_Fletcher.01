"""
Tests for game time functionality.

Tests the following classes:
- GameTime: Point in time representation
- GameDuration: Time interval representation
- GameTimeManager: Time progression management
"""

import pytest
from datetime import datetime, timezone, timedelta
from typing import cast
from src.backend.models.common.time import GameTime, GameDuration, GameTimeManager, GameTimeZone

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
    
    def test_creation_and_conversion(self) -> None:
        """Test creating GameTime and converting between formats."""
        # Create a specific datetime for testing
        dt = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        game_time = GameTime.from_datetime(dt)
        
        # Convert back to datetime and check equality
        converted_dt = game_time.to_datetime()
        assert converted_dt == dt
    
    def test_time_arithmetic(self) -> None:
        """Test arithmetic operations with GameTime and GameDuration."""
        start_time = GameTime.from_datetime(
            datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        )
        duration = GameDuration.from_hours(2)
        
        # Addition
        new_time = start_time + duration
        assert new_time.to_datetime().hour == 14
        
        # Subtraction of duration
        result = new_time - duration
        back_in_time = cast(GameTime, result)  # Ensure we got GameTime, not GameDuration
        assert back_in_time.to_datetime().hour == 12
        
        # Subtraction of times
        result = new_time - start_time
        time_passed = cast(GameDuration, result)  # Ensure we got GameDuration, not GameTime
        assert time_passed.hours == 2
    
    def test_timezone_handling(self) -> None:
        """Test handling of different time zones."""
        utc_time = GameTime.from_datetime(
            datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        )
        
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
        # Test with default (current) time
        manager = GameTimeManager()
        assert isinstance(manager.time_now, GameTime)
        
        # Test with specific start time
        start_time = GameTime.from_datetime(
            datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        )
        manager = GameTimeManager(start_time)
        assert manager.time_now == start_time
    
    def test_time_advancement(self) -> None:
        """Test advancing time by different durations."""
        start_time = GameTime.from_datetime(
            datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        )
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
        start_time = GameTime.from_datetime(
            datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        )
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