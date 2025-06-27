"""
Geometry package providing core geometric calculations and types.

This package provides fundamental geometric types and calculations used
throughout the game, including:

- Basic 2D positions
- Geographic positions (lat/lon)
- Distance calculations (using Vincenty's formulae)
- Bearing calculations and cardinal directions
- Nautical measurements
"""

from .position import Position
from .nautical_miles import NauticalMiles
from .vincenty import GeoPosition, calculate_haversine_distance, bearing_between
from .bearing import (
    Bearing,
    CardinalDirection,
    NORTH,
    EAST,
    SOUTH,
    WEST,
)

__all__ = [
    'Position',
    'NauticalMiles',
    'GeoPosition',
    'calculate_haversine_distance',
    'bearing_between',
    'Bearing',
    'CardinalDirection',
    'NORTH',
    'EAST',
    'SOUTH',
    'WEST',
] 