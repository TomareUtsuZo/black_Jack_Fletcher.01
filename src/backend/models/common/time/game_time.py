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

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Union, Optional, ClassVar, Dict, Any
from threading import Lock
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
    
    def __lt__(self, other: 'GameDuration') -> bool:
        """Compare if this duration is less than another."""
        return self._seconds < other._seconds
    
    def __le__(self, other: 'GameDuration') -> bool:
        """Compare if this duration is less than or equal to another."""
        return self._seconds <= other._seconds
    
    def __gt__(self, other: 'GameDuration') -> bool:
        """Compare if this duration is greater than another."""
        return self._seconds > other._seconds
    
    def __ge__(self, other: 'GameDuration') -> bool:
        """Compare if this duration is greater than or equal to another."""
        return self._seconds >= other._seconds
    
    def __eq__(self, other: object) -> bool:
        """Compare if two durations are equal."""
        if not isinstance(other, GameDuration):
            return NotImplemented
        return self._seconds == other._seconds
    
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
    
    The game time is always validated to ensure it falls within
    the valid game time range (between GAME_START and current UTC time).
    """
    # Historical reference points as datetime objects
    GAME_START: ClassVar[datetime] = datetime(1900, 1, 1, tzinfo=timezone.utc)
    PEARL_HARBOR_ATTACK: ClassVar[datetime] = datetime(1941, 12, 7, 17, 48, tzinfo=timezone.utc)
    
    _time: datetime  # The actual datetime object
    _time_zone: Optional[GameTimeZone] = None
    
    def __post_init__(self) -> None:
        """Validate the time is within game bounds."""
        if self._time.tzinfo is None:
            raise ValueError("Game time must have timezone information")
            
        # Convert all times to UTC for comparison
        game_time_utc = self._time.astimezone(timezone.utc)
        current_utc = datetime.now(timezone.utc)
            
        # Compare using UTC datetimes to avoid recursion
        if not (self.GAME_START <= game_time_utc <= current_utc):
            raise ValueError(
                f"Game time must be between {self.GAME_START.isoformat()} "
                f"and {current_utc.isoformat()}"
            )
    
    @property
    def time_zone(self) -> Optional[GameTimeZone]:
        """Get the time zone, if any."""
        return self._time_zone
    
    def in_zone(self, zone: GameTimeZone) -> 'GameTime':
        """Get this time in a different time zone."""
        return GameTime(self._time, zone)
    
    def to_datetime(self) -> datetime:
        """Get the underlying datetime object."""
        if self._time_zone is not None:
            return self._time.astimezone(self._time_zone.to_timezone())
        return self._time
    
    def __add__(self, other: GameDuration) -> 'GameTime':
        """Add a duration to this time."""
        new_time = self._time + timedelta(seconds=other.seconds)
        return GameTime(new_time, self._time_zone)
    
    def __sub__(self, other: Union[GameDuration, 'GameTime']) -> Union['GameTime', GameDuration]:
        """
        Subtract duration or another time.
        
        Returns:
            - GameTime when subtracting a duration
            - GameDuration when subtracting another GameTime
        """
        if isinstance(other, GameDuration):
            new_time = self._time - timedelta(seconds=other.seconds)
            return GameTime(new_time, self._time_zone)
        
        # When subtracting two GameTimes, return the duration between them
        delta = self._time - other._time
        return GameDuration(delta.total_seconds())
    
    def __lt__(self, other: 'GameTime') -> bool:
        """Compare if this time is earlier than another."""
        return self._time < other._time
    
    def __le__(self, other: 'GameTime') -> bool:
        """Compare if this time is earlier than or equal to another."""
        return self._time <= other._time
    
    def __gt__(self, other: 'GameTime') -> bool:
        """Compare if this time is later than another."""
        return self._time > other._time
    
    def __ge__(self, other: 'GameTime') -> bool:
        """Compare if this time is later than or equal to another."""
        return self._time >= other._time
    
    def __eq__(self, other: object) -> bool:
        """Compare if two times are equal."""
        if not isinstance(other, GameTime):
            return NotImplemented
        return self._time == other._time
    
    @classmethod
    def from_datetime(cls, dt: datetime, time_zone: Optional[GameTimeZone] = None) -> 'GameTime':
        """
        Create game time from Python datetime.
        
        Args:
            dt: The datetime to convert (must have tzinfo)
            time_zone: Optional game time zone to use
            
        Raises:
            ValueError: If dt has no timezone info or is outside game bounds
        """
        if dt.tzinfo is None:
            raise ValueError("datetime must have timezone information")
        return cls(dt, time_zone)
    
    @classmethod
    def now(cls, time_zone: Optional[GameTimeZone] = None) -> 'GameTime':
        """
        Get current game time.
        
        This will raise ValueError if the current time is outside
        game bounds. In production, you should typically use a
        GameTimeManager instead of this method.
        """
        return cls.from_datetime(datetime.now(timezone.utc), time_zone)
    
    def strftime(self, format: str) -> str:
        """Format time according to format string."""
        return self._time.strftime(format)
    
    def __str__(self) -> str:
        """Convert to string using ISO format."""
        return self._time.isoformat()
    
    @classmethod
    def default_start_time(cls) -> 'GameTime':
        """Get the default game start time (Pearl Harbor attack)."""
        print("\nCreating default start time...")
        print(f"Using Pearl Harbor attack time: {cls.PEARL_HARBOR_ATTACK.isoformat()}")
        time = cls(cls.PEARL_HARBOR_ATTACK)
        print(f"Created GameTime object with time: {time}")
        return time

@dataclass(init=False)
class GameTimeManager:
    """
    Manages game time progression.
    
    This class is responsible for:
    - Tracking current game time
    - Advancing time by specified durations
    - Providing time-related utilities
    
    Note: Time rate management is handled by the game state manager,
    which uses this class to advance time appropriately.
    
    This class is thread-safe to handle concurrent access from the
    scheduler thread and main thread.
    """
    _current_time: GameTime
    _lock: Lock = field(default_factory=Lock, init=False)
    
    def __init__(self, start_time: Optional[GameTime] = None) -> None:
        """
        Initialize the time manager.
        
        Args:
            start_time: Initial game time (defaults to Pearl Harbor attack time if None)
        """
        print("\nInitializing GameTimeManager...")
        self._lock = Lock()
        
        if start_time is not None:
            print(f"Using provided start time: {start_time.to_datetime().isoformat()}")
            self._current_time = start_time
        else:
            print("No start time provided, using Pearl Harbor attack time...")
            default_time = GameTime.default_start_time()
            print(f"Default start time set to: {default_time.to_datetime().isoformat()}")
            self._current_time = default_time
    
    @property
    def time_now(self) -> GameTime:
        """Get the current game time."""
        with self._lock:
            return self._current_time
    
    def advance_time(self, duration: GameDuration) -> GameTime:
        """
        Advance the game time by the specified duration.
        
        Args:
            duration: Amount of time to advance
            
        Returns:
            The new game time after advancement
            
        Raises:
            ValueError: If advancing time would exceed game bounds
        """
        with self._lock:
            try:
                print(f"Current time before advance: {self._current_time.to_datetime().isoformat()}")
                print(f"Advancing by: {duration.minutes} minutes")
                self._current_time = self._current_time + duration
                print(f"New time after advance: {self._current_time.to_datetime().isoformat()}")
                return self._current_time
            except ValueError as e:
                print(f"Failed to advance time: {e}")
                raise 