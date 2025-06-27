"""
Time package providing time-related calculations and types.

This package provides fundamental time types and calculations used
throughout the game, including:

- Game time representation
- Time intervals and durations
- Time zone handling
- Time-based calculations and conversions
- Time progression management
"""

from .game_time import GameTime, GameDuration, GameTimeManager
from .time_zone import GameTimeZone

__all__ = [
    'GameTime',
    'GameDuration',
    'GameTimeZone',
    'GameTimeManager',
] 