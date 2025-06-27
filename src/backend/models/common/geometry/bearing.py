"""
Bearing calculations and utilities.

This module provides the Bearing type and associated utilities for working with
directional angles in the game. It handles bearing arithmetic, normalization,
and conversions between different angle representations.
"""

import math
from dataclasses import dataclass
from enum import Enum, auto
from typing import Union, Optional

@dataclass(frozen=True)
class Bearing:
    """
    Represents a bearing/heading in degrees.
    
    The bearing is always normalized to the range [0, 360).
    0° represents North, 90° East, 180° South, and 270° West.
    """
    _value: float  # Internal storage, always normalized to [0, 360)
    
    def __init__(self, degrees: float) -> None:
        """
        Create a new bearing from an angle in degrees.
        
        Args:
            degrees: Angle in degrees. Will be normalized to [0, 360).
        """
        # Use object.__setattr__ since this is a frozen dataclass
        object.__setattr__(self, '_value', self.normalize_degrees(degrees))
    
    @property
    def degrees(self) -> float:
        """Get the bearing in degrees [0, 360)."""
        return self._value
    
    @property
    def radians(self) -> float:
        """Get the bearing in radians [0, 2π)."""
        return math.radians(self._value)
    
    @property
    def signed_degrees(self) -> float:
        """Get the bearing in degrees [-180, 180)."""
        value = self._value
        if value > 180:
            value -= 360
        return value
    
    def __add__(self, other: Union['Bearing', float]) -> 'Bearing':
        """Add two bearings or add degrees to a bearing."""
        if isinstance(other, Bearing):
            return Bearing(self._value + other._value)
        return Bearing(self._value + other)
    
    def __sub__(self, other: Union['Bearing', float]) -> 'Bearing':
        """Subtract two bearings or subtract degrees from a bearing."""
        if isinstance(other, Bearing):
            return Bearing(self._value - other._value)
        return Bearing(self._value - other)
    
    def __eq__(self, other: object) -> bool:
        """Check if two bearings are equal."""
        if not isinstance(other, Bearing):
            return NotImplemented
        # Compare normalized values with small tolerance for float comparison
        return abs(self._value - other._value) < 1e-10
    
    @staticmethod
    def normalize_degrees(degrees: float) -> float:
        """Normalize degrees to [0, 360) range."""
        # Faster than using modulo for small angles
        while degrees >= 360:
            degrees -= 360
        while degrees < 0:
            degrees += 360
        return degrees
    
    @staticmethod
    def from_radians(radians: float) -> 'Bearing':
        """Create a bearing from an angle in radians."""
        return Bearing(math.degrees(radians))
    
    def relative_to(self, reference: 'Bearing') -> 'Bearing':
        """
        Calculate relative bearing from a reference bearing.
        
        Args:
            reference: The reference bearing to calculate from
            
        Returns:
            Relative bearing where:
            - 0° is straight ahead
            - +90° is to the right
            - -90° is to the left
            - 180° or -180° is directly behind
        """
        relative = self._value - reference._value
        if relative > 180:
            relative -= 360
        elif relative <= -180:
            relative += 360
        return Bearing(relative)
    
    def reciprocal(self) -> 'Bearing':
        """Get the reciprocal (opposite) bearing."""
        return Bearing(self._value + 180)

class CardinalDirection(Enum):
    """Cardinal and intercardinal directions."""
    N = auto()    # North (0°)
    NE = auto()   # Northeast (45°)
    E = auto()    # East (90°)
    SE = auto()   # Southeast (135°)
    S = auto()    # South (180°)
    SW = auto()   # Southwest (225°)
    W = auto()    # West (270°)
    NW = auto()   # Northwest (315°)
    
    @staticmethod
    def from_bearing(bearing: Bearing) -> 'CardinalDirection':
        """Convert a bearing to the nearest cardinal/intercardinal direction."""
        # Normalize to [0, 360) and add 22.5° to center on sectors
        sector = (bearing.degrees + 22.5) % 360
        # Integer divide by 45° to get sector number (0-7)
        sector_num = int(sector / 45)
        return [
            CardinalDirection.N,
            CardinalDirection.NE,
            CardinalDirection.E,
            CardinalDirection.SE,
            CardinalDirection.S,
            CardinalDirection.SW,
            CardinalDirection.W,
            CardinalDirection.NW
        ][sector_num]
    
    def to_bearing(self) -> Bearing:
        """Convert cardinal direction to its corresponding bearing."""
        return Bearing(45 * (self.value - 1))
    
    def __str__(self) -> str:
        """Return the cardinal direction's name."""
        return self.name

# Common bearings
NORTH = Bearing(0)
EAST = Bearing(90)
SOUTH = Bearing(180)
WEST = Bearing(270)

def normalize_degrees(degrees: float) -> float:
    """
    Normalize degrees to [0, 360) range.
    
    This is a convenience function that uses Bearing's normalization
    but doesn't create a Bearing object.
    """
    return Bearing.normalize_degrees(degrees)

def normalize_radians(radians: float) -> float:
    """
    Normalize radians to [0, 2π) range.
    
    This is a convenience function that converts to degrees,
    normalizes, and converts back to radians.
    """
    return math.radians(normalize_degrees(math.degrees(radians))) 