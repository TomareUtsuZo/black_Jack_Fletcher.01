"""
Position module defining core geometric positioning.

This module provides the fundamental Position class used throughout the game
for representing locations in 2D space. This is a core type that will be used
by many different systems including:

- Units (ships, aircraft)
- Map features (ports, islands)
- Combat calculations (range checks)
- Movement planning
- Task force formations
- Strategic objectives

Note: Pure geometric calculations (like distance) will be moved to a separate
geometric calculations module to maintain single responsibility principle.
"""

from dataclasses import dataclass
from typing import Tuple, Dict, Mapping

@dataclass(frozen=True)
class Position:
    """
    Represents an immutable position in 2D space.
    
    This class is frozen (immutable) to prevent accidental modifications
    and to allow it to be used as a dictionary key or in sets.
    
    Attributes:
        x: The x-coordinate in game space
        y: The y-coordinate in game space
    """
    x: float
    y: float

    def to_tuple(self) -> Tuple[float, float]:
        """Convert position to a tuple representation."""
        return (self.x, self.y)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert position to a JSON-friendly dictionary with explicit keys.

        Returns:
            Dict[str, float]: {"x": <float>, "y": <float>}
        """
        return {"x": float(self.x), "y": float(self.y)}
    
    def distance_to(self, other: 'Position') -> float:
        """
        Calculate Euclidean distance to another position.
        
        Note: This method will be moved to a geometric calculations module
        in the future to maintain single responsibility principle.
        
        Args:
            other: The position to calculate distance to
            
        Returns:
            float: The Euclidean distance between the positions
        """
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    @classmethod
    def from_tuple(cls, coords: Tuple[float, float]) -> 'Position':
        """
        Create a Position from a tuple of coordinates.
        
        Args:
            coords: Tuple of (x, y) coordinates
            
        Returns:
            Position: A new Position instance
        """
        return cls(x=coords[0], y=coords[1])

    @classmethod
    def from_dict(cls, data: Mapping[str, float]) -> 'Position':
        """Create a Position from a dict-like mapping with 'x' and 'y' keys.

        Args:
            data: Mapping containing numeric 'x' and 'y'. Extra keys ignored.

        Returns:
            Position: A new Position instance.
        """
        return cls(x=float(data["x"]), y=float(data["y"]))

    def __str__(self) -> str:
        """Return string representation of position."""
        return f"Position(x={self.x:.1f}, y={self.y:.1f})" 