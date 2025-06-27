"""
Time package providing time-related calculations and types.

This package provides fundamental time types and calculations used
throughout the game, including:

- Game time representation
- Time intervals and durations
- Time zone handling
- Time-based calculations and conversions
"""

from .game_time import GameTime, GameDuration
from .time_zone import GameTimeZone

__all__ = [
    'GameTime',
    'GameDuration',
    'GameTimeZone',
] 