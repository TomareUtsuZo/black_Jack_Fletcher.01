"""
Tests for game time zone functionality.

Tests the following:
- GameTimeZone creation and properties
- Timezone conversion
- String representation
- Common time zone constants
- Factory methods
"""

import dataclasses
import pytest
from datetime import timezone, timedelta
from src.backend.models.common.time.time_zone import (
    GameTimeZone,
    UTC,
    EST,
    CST,
    PST,
    GMT,
)

class TestGameTimeZone:
    """Tests for the GameTimeZone class."""
    
    def test_creation_and_properties(self) -> None:
        """Test creating time zones and accessing their properties."""
        # Test with name
        est = GameTimeZone(-5, "EST")
        assert est.offset_hours == -5
        assert est.name == "EST"
        
        # Test without name
        minus_three = GameTimeZone(-3)
        assert minus_three.offset_hours == -3
        assert minus_three.name is None
        
        # Test positive offset
        plus_two = GameTimeZone(2, "EET")  # Eastern European Time
        assert plus_two.offset_hours == 2
        assert plus_two.name == "EET"
        
        # Test zero offset
        utc = GameTimeZone(0)
        assert utc.offset_hours == 0
        assert utc.name is None
    
    def test_to_timezone_conversion(self) -> None:
        """Test conversion to Python's timezone."""
        # Test positive offset
        plus_one = GameTimeZone(1, "CET")
        tz = plus_one.to_timezone()
        assert isinstance(tz, timezone)
        assert tz.utcoffset(None) == timedelta(hours=1)
        
        # Test negative offset
        minus_eight = GameTimeZone(-8, "PST")
        tz = minus_eight.to_timezone()
        assert tz.utcoffset(None) == timedelta(hours=-8)
        
        # Test zero offset
        utc = GameTimeZone(0, "UTC")
        tz = utc.to_timezone()
        assert tz.utcoffset(None) == timedelta(0)
        
        # Test fractional offset
        half_hour = GameTimeZone(5.5, "IST")  # Indian Standard Time
        tz = half_hour.to_timezone()
        assert tz.utcoffset(None) == timedelta(hours=5, minutes=30)
    
    def test_string_representation(self) -> None:
        """Test string conversion of time zones."""
        # Test named zones
        est = GameTimeZone(-5, "EST")
        assert str(est) == "EST"
        
        utc = GameTimeZone(0, "UTC")
        assert str(utc) == "UTC"
        
        # Test unnamed zones
        plus_three = GameTimeZone(3)
        assert str(plus_three) == "UTC+3"
        
        minus_four = GameTimeZone(-4)
        assert str(minus_four) == "UTC-4"
        
        zero = GameTimeZone(0)
        assert str(zero) == "UTC+0"
        
        # Test fractional offsets
        half_hour = GameTimeZone(5.5)
        assert str(half_hour) == "UTC+5.5"
        
        quarter_hour = GameTimeZone(-3.75)
        assert str(quarter_hour) == "UTC-3.75"
    
    def test_factory_methods(self) -> None:
        """Test the factory methods for creating time zones."""
        # Test UTC factory
        utc = GameTimeZone.utc()
        assert utc.offset_hours == 0
        assert utc.name == "UTC"
        assert str(utc) == "UTC"
        
        # Test from_hours factory
        est = GameTimeZone.from_hours(-5, "EST")
        assert est.offset_hours == -5
        assert est.name == "EST"
        
        # Test from_hours without name
        plus_four = GameTimeZone.from_hours(4)
        assert plus_four.offset_hours == 4
        assert plus_four.name is None
        assert str(plus_four) == "UTC+4"
    
    def test_predefined_zones(self) -> None:
        """Test the predefined time zone constants."""
        # Test UTC
        assert UTC.offset_hours == 0
        assert UTC.name == "UTC"
        
        # Test EST
        assert EST.offset_hours == -5
        assert EST.name == "EST"
        
        # Test CST
        assert CST.offset_hours == -6
        assert CST.name == "CST"
        
        # Test PST
        assert PST.offset_hours == -8
        assert PST.name == "PST"
        
        # Test GMT
        assert GMT.offset_hours == 0
        assert GMT.name == "GMT"
    
    def test_immutability(self) -> None:
        """Test that GameTimeZone instances are immutable."""
        zone = GameTimeZone(1, "Test")
        
        with pytest.raises(dataclasses.FrozenInstanceError):
            zone._offset_hours = 2  # type: ignore
        
        with pytest.raises(dataclasses.FrozenInstanceError):
            zone._name = "Changed"  # type: ignore 