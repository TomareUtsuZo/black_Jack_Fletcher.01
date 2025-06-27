"""
Geometry package providing core geometric calculations and types.

This package provides fundamental geometric types and calculations used
throughout the game, including:

- Basic 2D positions
- Geographic positions (lat/lon)
- Distance calculations (Euclidean and Haversine)
- Nautical measurements
"""

from .position import Position
from .nautical_miles import NauticalMiles
from .haversine import GeoPosition, calculate_haversine_distance, bearing_between

__all__ = [
    'Position',
    'NauticalMiles',
    'GeoPosition',
    'calculate_haversine_distance',
    'bearing_between'
] 