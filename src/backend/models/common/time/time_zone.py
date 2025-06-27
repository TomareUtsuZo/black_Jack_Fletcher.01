"""
Game time zone handling.

This module provides time zone support for the game, allowing different
regions to have their own local time. It supports both fixed offsets
and named time zones.
"""

from dataclasses import dataclass
from datetime import timezone, timedelta
from typing import Union, Optional

@dataclass(frozen=True)
class GameTimeZone:
    """
    Represents a time zone in the game world.
    
    Time zones can be specified either by:
    - A fixed offset from UTC in hours
    - A name that maps to a real-world time zone
    
    The game uses simplified time zones that don't change with daylight
    saving time to keep the game mechanics consistent.
    """
    _offset_hours: float
    _name: Optional[str] = None
    
    @property
    def offset_hours(self) -> float:
        """Get the offset from UTC in hours."""
        return self._offset_hours
    
    @property
    def name(self) -> Optional[str]:
        """Get the time zone name, if any."""
        return self._name
    
    def to_timezone(self) -> timezone:
        """Convert to Python timezone."""
        return timezone(timedelta(hours=self._offset_hours))
    
    def __str__(self) -> str:
        """Convert to string."""
        if self._name:
            return self._name
        
        sign = '+' if self._offset_hours >= 0 else ''
        return f'UTC{sign}{self._offset_hours:g}'
    
    @classmethod
    def utc(cls) -> 'GameTimeZone':
        """Get UTC time zone."""
        return cls(0, 'UTC')
    
    @classmethod
    def from_hours(cls, hours: float, name: Optional[str] = None) -> 'GameTimeZone':
        """Create time zone from hours offset."""
        return cls(hours, name)

# Common time zones
UTC = GameTimeZone.utc()
EST = GameTimeZone.from_hours(-5, 'EST')  # Eastern Standard Time
CST = GameTimeZone.from_hours(-6, 'CST')  # Central Standard Time
PST = GameTimeZone.from_hours(-8, 'PST')  # Pacific Standard Time
GMT = GameTimeZone.from_hours(0, 'GMT')   # Greenwich Mean Time 