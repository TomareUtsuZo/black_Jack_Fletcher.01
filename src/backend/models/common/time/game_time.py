"""
Game time representation and calculations.

This module provides classes for working with time in the game world:
- GameTime: A specific point in game time
- GameDuration: A duration or interval of game time
- GameTimeManager: Manages game time progression

The game time system supports:
- Time scale factors (game time can run faster than real time)
- Time zone awareness
- Common time arithmetic operations
- Conversion to/from real time
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Union, Optional
from .time_zone import GameTimeZone

@dataclass(frozen=True)
class GameDuration:
    """
    Represents a duration of game time.
    
    This can be used for:
    - Time intervals between game events
    - Mission or task durations
    - Time-based calculations
    
    The duration is stored internally in seconds but provides
    convenient access in various units (hours, minutes, etc).
    """
    _seconds: float
    
    @property
    def seconds(self) -> float:
        """Get the total duration in seconds."""
        return self._seconds
    
    @property
    def minutes(self) -> float:
        """Get the total duration in minutes."""
        return self._seconds / 60
    
    @property
    def hours(self) -> float:
        """Get the total duration in hours."""
        return self._seconds / 3600
    
    @property
    def days(self) -> float:
        """Get the total duration in days."""
        return self._seconds / 86400
    
    def __add__(self, other: 'GameDuration') -> 'GameDuration':
        """Add two durations."""
        return GameDuration(self._seconds + other._seconds)
    
    def __sub__(self, other: 'GameDuration') -> 'GameDuration':
        """Subtract two durations."""
        return GameDuration(self._seconds - other._seconds)
    
    def __mul__(self, factor: float) -> 'GameDuration':
        """Multiply duration by a factor."""
        return GameDuration(self._seconds * factor)
    
    def __truediv__(self, divisor: Union[float, 'GameDuration']) -> Union['GameDuration', float]:
        """
        Divide duration by a number or another duration.
        
        Returns:
            - GameDuration when dividing by a number
            - float when dividing by another GameDuration
        """
        if isinstance(divisor, GameDuration):
            return self._seconds / divisor._seconds
        return GameDuration(self._seconds / divisor)
    
    @classmethod
    def from_seconds(cls, seconds: float) -> 'GameDuration':
        """Create duration from seconds."""
        return cls(seconds)
    
    @classmethod
    def from_minutes(cls, minutes: float) -> 'GameDuration':
        """Create duration from minutes."""
        return cls(minutes * 60)
    
    @classmethod
    def from_hours(cls, hours: float) -> 'GameDuration':
        """Create duration from hours."""
        return cls(hours * 3600)
    
    @classmethod
    def from_days(cls, days: float) -> 'GameDuration':
        """Create duration from days."""
        return cls(days * 86400)

@dataclass(frozen=True)
class GameTime:
    """
    Represents a specific point in game time.
    
    Game time can run at a different rate than real time using
    a time scale factor. It also supports time zone awareness
    for proper handling of local times in different game regions.
    """
    _timestamp: float  # Unix timestamp in game time
    _time_zone: Optional[GameTimeZone] = None
    
    @property
    def timestamp(self) -> float:
        """Get the Unix timestamp in game time."""
        return self._timestamp
    
    @property
    def time_zone(self) -> Optional[GameTimeZone]:
        """Get the time zone, if any."""
        return self._time_zone
    
    def in_zone(self, zone: GameTimeZone) -> 'GameTime':
        """Get this time in a different time zone."""
        return GameTime(self._timestamp, zone)
    
    def to_datetime(self) -> datetime:
        """Convert to Python datetime."""
        tz = timezone.utc if self._time_zone is None else self._time_zone.to_timezone()
        return datetime.fromtimestamp(self._timestamp, tz)
    
    def __add__(self, other: GameDuration) -> 'GameTime':
        """Add a duration to this time."""
        return GameTime(self._timestamp + other.seconds, self._time_zone)
    
    def __sub__(self, other: Union[GameDuration, 'GameTime']) -> Union['GameTime', GameDuration]:
        """
        Subtract duration or another time.
        
        Returns:
            - GameTime when subtracting a duration
            - GameDuration when subtracting another GameTime
        """
        if isinstance(other, GameDuration):
            return GameTime(self._timestamp - other.seconds, self._time_zone)
        return GameDuration(self._timestamp - other._timestamp)
    
    @classmethod
    def from_datetime(cls, dt: datetime, time_zone: Optional[GameTimeZone] = None) -> 'GameTime':
        """Create game time from Python datetime."""
        return cls(dt.timestamp(), time_zone)
    
    @classmethod
    def now(cls, time_zone: Optional[GameTimeZone] = None) -> 'GameTime':
        """Get current game time."""
        return cls.from_datetime(datetime.now(timezone.utc), time_zone)
    
    def strftime(self, format: str) -> str:
        """Format time according to format string."""
        return self.to_datetime().strftime(format)
    
    def __str__(self) -> str:
        """Convert to string using ISO format."""
        return self.to_datetime().isoformat()

@dataclass
class GameTimeManager:
    """
    Manages game time progression.
    
    This class is responsible for:
    - Tracking current game time
    - Advancing time by specified durations
    - Providing time-related utilities
    
    Note: Time rate management is handled by the game state manager,
    which uses this class to advance time appropriately.
    """
    _current_time: GameTime
    
    def __init__(self, start_time: Optional[GameTime] = None) -> None:
        """
        Initialize the time manager.
        
        Args:
            start_time: Initial game time (defaults to current UTC time if None)
        """
        self._current_time = start_time if start_time is not None else GameTime.now()
    
    @property
    def time_now(self) -> GameTime:
        """Get the current game time."""
        return self._current_time
    
    def advance_time(self, duration: GameDuration) -> GameTime:
        """
        Advance the game time by the specified duration.
        
        Args:
            duration: Amount of time to advance
            
        Returns:
            The new game time after advancement
        """
        self._current_time = self._current_time + duration
        return self._current_time 