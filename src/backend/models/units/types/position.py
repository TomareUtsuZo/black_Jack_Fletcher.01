from dataclasses import dataclass
from typing import Optional

@dataclass
class Position:
    """Represents a position in 2D space"""
    x: float
    y: float
    
    def distance_to(self, other: 'Position') -> float:
        """Calculate distance to another position, move to the geolocation module"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5 