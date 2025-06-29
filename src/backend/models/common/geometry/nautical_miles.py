"""
Module for handling nautical mile measurements and conversions.

This module provides a type-safe way to work with nautical miles and convert
between different units of measurement commonly used in naval operations.
"""

from dataclasses import dataclass
from typing import Union, ClassVar

@dataclass(frozen=True)
class NauticalMiles:
    """
    Represents a distance in nautical miles.
    
    This class provides type safety for nautical mile measurements and
    handles conversions to other units. It is immutable to prevent
    accidental modifications to distance values.
    
    1 nautical mile = 1852 meters exactly
    1 nautical mile ≈ 1.15078 statute miles
    1 nautical mile = 1/60th of a degree of latitude
    """
    
    # Standard conversion factors as class constants
    METERS_PER_NMILE: ClassVar[float] = 1852.0
    STATUTE_MILES_PER_NMILE: ClassVar[float] = 1.15078
    KILOMETERS_PER_NMILE: ClassVar[float] = METERS_PER_NMILE / 1000.0
    
    # Distance in nautical miles (1 NM = 1852 meters)
    _distance_nm: float
    
    @property
    def value(self) -> float:
        """The distance in nautical miles."""
        return self._distance_nm
    
    def __post_init__(self) -> None:
        """Validate the nautical mile value."""
        if not isinstance(self._distance_nm, (int, float)):
            raise TypeError("Nautical mile value must be a number")
        if self._distance_nm < 0:
            raise ValueError("Nautical mile value cannot be negative")
    
    @classmethod
    def from_meters(cls, meters: float) -> "NauticalMiles":
        """
        Create a NauticalMiles instance from a meter value.
        
        Args:
            meters: The distance in meters
            
        Returns:
            A new NauticalMiles instance
            
        Raises:
            ValueError: If meters is negative
        """
        if meters < 0:
            raise ValueError("Meter value cannot be negative")
        return cls(meters / cls.METERS_PER_NMILE)
    
    @classmethod
    def from_kilometers(cls, kilometers: float) -> "NauticalMiles":
        """
        Create a NauticalMiles instance from a kilometer value.
        
        Args:
            kilometers: The distance in kilometers
            
        Returns:
            A new NauticalMiles instance
            
        Raises:
            ValueError: If kilometers is negative
        """
        if kilometers < 0:
            raise ValueError("Kilometer value cannot be negative")
        return cls(kilometers / cls.KILOMETERS_PER_NMILE)
    
    @classmethod
    def from_statute_miles(cls, miles: float) -> "NauticalMiles":
        """
        Create a NauticalMiles instance from statute miles.
        
        Args:
            miles: The distance in statute miles
            
        Returns:
            A new NauticalMiles instance
            
        Raises:
            ValueError: If miles is negative
        """
        if miles < 0:
            raise ValueError("Mile value cannot be negative")
        return cls(miles / cls.STATUTE_MILES_PER_NMILE)
    
    def to_meters(self) -> float:
        """Convert to meters."""
        return self._distance_nm * self.METERS_PER_NMILE
    
    def to_kilometers(self) -> float:
        """Convert to kilometers."""
        return self._distance_nm * self.KILOMETERS_PER_NMILE
    
    def to_statute_miles(self) -> float:
        """Convert to statute miles."""
        return self._distance_nm * self.STATUTE_MILES_PER_NMILE
    
    def __add__(self, other: "NauticalMiles") -> "NauticalMiles":
        """Add two NauticalMiles values."""
        if not isinstance(other, NauticalMiles):
            return NotImplemented
        return NauticalMiles(self._distance_nm + other._distance_nm)
    
    def __sub__(self, other: "NauticalMiles") -> "NauticalMiles":
        """Subtract two NauticalMiles values."""
        if not isinstance(other, NauticalMiles):
            return NotImplemented
        return NauticalMiles(self._distance_nm - other._distance_nm)
    
    def __mul__(self, scalar: Union[int, float]) -> "NauticalMiles":
        """Multiply NauticalMiles by a scalar."""
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return NauticalMiles(self._distance_nm * scalar)
    
    def __truediv__(self, scalar: Union[int, float]) -> "NauticalMiles":
        """Divide NauticalMiles by a scalar."""
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return NauticalMiles(self._distance_nm / scalar)
    
    def __eq__(self, other: object) -> bool:
        """Check if two NauticalMiles values are equal."""
        if not isinstance(other, NauticalMiles):
            return NotImplemented
        return self._distance_nm == other._distance_nm
    
    def __lt__(self, other: "NauticalMiles") -> bool:
        """Check if this distance is less than another."""
        if not isinstance(other, NauticalMiles):
            return NotImplemented
        return self._distance_nm < other._distance_nm
    
    def __le__(self, other: "NauticalMiles") -> bool:
        """Check if this distance is less than or equal to another."""
        if not isinstance(other, NauticalMiles):
            return NotImplemented
        return self._distance_nm <= other._distance_nm
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"{self._distance_nm:.2f} NM"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"NauticalMiles({self._distance_nm})" 