"""
Movement module for handling unit movement logic.

This module provides the MovementModule class which implements the UnitModule protocol
and handles all movement-related calculations and state changes for units.
"""

import math
from dataclasses import dataclass
from typing import Optional, Protocol, Tuple

from src.backend.models.common.geometry import (
    Position,
    Bearing,
    NauticalMiles,
    calculate_haversine_distance,
    bearing_between
)
from src.backend.models.units import UnitModule, UnitAttributes

# Constants for movement calculations
DESTINATION_REACHED_THRESHOLD = NauticalMiles(0.1)  # Within 0.1 nautical miles considered "at destination"

def calculate_cartesian_distance(pos1: Position, pos2: Position) -> NauticalMiles:
    """Calculate straight-line distance between two positions using Cartesian geometry."""
    dx = pos2.x - pos1.x
    dy = pos2.y - pos1.y
    return NauticalMiles(math.sqrt(dx * dx + dy * dy))

def calculate_cartesian_bearing(pos1: Position, pos2: Position) -> Bearing:
    """Calculate bearing between two positions using Cartesian geometry."""
    dx = pos2.x - pos1.x
    dy = pos2.y - pos1.y
    angle_rad = math.atan2(dx, dy)  # atan2 returns angle in radians
    angle_deg = math.degrees(angle_rad)
    if angle_deg < 0:
        angle_deg += 360
    return Bearing(angle_deg)

@dataclass
class MovementState:
    """
    Encapsulates the movement state of a unit.
    
    This class maintains movement-specific state that shouldn't be
    part of the core unit attributes.
    """
    is_moving: bool = False
    current_bearing: Optional[Bearing] = None

class MovementModule:
    """
    Handles unit movement logic.
    
    This module is responsible for:
    - Calculating movement vectors
    - Updating unit position
    - Managing speed changes
    - Fuel consumption calculations
    """
    
    def __init__(self) -> None:
        """Initialize the movement module."""
        self._unit_attributes: Optional[UnitAttributes] = None
        self._state = MovementState()
    
    @property
    def unit_attributes(self) -> UnitAttributes:
        """
        Get the unit attributes, raising an error if they haven't been bound.
        
        Returns:
            The bound unit attributes
            
        Raises:
            RuntimeError: If unit attributes haven't been bound
        """
        if self._unit_attributes is None:
            raise RuntimeError("Unit attributes not bound")
        return self._unit_attributes
    
    def initialize(self) -> None:
        """Initialize the module (required by UnitModule protocol)."""
        pass
    
    def bind_unit_attributes(self, attributes: UnitAttributes) -> None:
        """
        Bind unit attributes to the module.
        
        Args:
            attributes: The unit attributes to bind
        """
        self._unit_attributes = attributes
        # Initialize current bearing based on destination if it exists
        if attributes.destination is not None:
            self._state.current_bearing = calculate_cartesian_bearing(
                attributes.position,
                attributes.destination
            )
    
    def set_destination(self, destination: Position) -> None:
        """
        Set a new destination and calculate bearing.
        
        Args:
            destination: The target position to move to
        """
        self.unit_attributes.destination = destination
        self._state.current_bearing = calculate_cartesian_bearing(
            self.unit_attributes.position,
            destination
        )
        self._state.is_moving = True
    
    def set_speed(self, speed: NauticalMiles) -> None:
        """
        Set the unit's speed.
        
        Args:
            speed: The desired speed in knots
            
        Raises:
            ValueError: If speed is negative or exceeds max_speed
        """
        if speed.value < 0:
            raise ValueError("Speed cannot be negative")
        if speed.value > self.unit_attributes.max_speed.value:
            raise ValueError(f"Speed cannot exceed maximum speed of {self.unit_attributes.max_speed}")
        
        self.unit_attributes.current_speed = speed
        
    def stop(self) -> None:
        """Stop the unit's movement."""
        self.unit_attributes.current_speed = NauticalMiles(0)
        self.unit_attributes.destination = None
        self._state.is_moving = False
        self._state.current_bearing = None

    def _should_update_position(self) -> bool:
        """
        Check if the unit's position should be updated.
        
        Returns:
            bool: True if the unit should move, False otherwise
        """
        return (
            self._state.is_moving and 
            self.unit_attributes.current_speed.value > 0
        )

    def _calculate_distance_to_destination(self) -> Optional[NauticalMiles]:
        """
        Calculate distance to current destination if one exists.
        
        Returns:
            Optional[NauticalMiles]: Distance to destination or None if no destination
        """
        if self.unit_attributes.destination is None:
            return None
            
        return calculate_cartesian_distance(
            self.unit_attributes.position,
            self.unit_attributes.destination
        )

    def _calculate_movement_vector(self, distance: NauticalMiles) -> Tuple[float, float]:
        """
        Calculate the x and y components of movement based on bearing and distance.
        
        Args:
            distance: Distance to move
            
        Returns:
            Tuple[float, float]: The x and y components of movement
        """
        if self._state.current_bearing is None:
            return (0.0, 0.0)
            
        bearing_rad = math.radians(self._state.current_bearing.degrees)
        dx = distance.value * math.sin(bearing_rad)
        dy = distance.value * math.cos(bearing_rad)
        return (dx, dy)

    def _update_position(self, dx: float, dy: float) -> None:
        """
        Update the unit's position based on movement vector.
        
        Args:
            dx: Change in x position
            dy: Change in y position
        """
        new_position = Position(
            self.unit_attributes.position.x + dx,
            self.unit_attributes.position.y + dy
        )
        self.unit_attributes.position = new_position

    def _check_destination_reached(self) -> bool:
        """
        Check if unit has reached its destination.
        
        Returns:
            bool: True if destination reached, False otherwise
        """
        if self.unit_attributes.destination is None:
            return False
            
        distance = self._calculate_distance_to_destination()
        if distance is None:
            return False
            
        return distance.value < DESTINATION_REACHED_THRESHOLD.value

    def update(self, time_delta: float) -> None:
        """
        Update the unit's position and movement state.
        
        Args:
            time_delta: Time elapsed since last update in current time rate
        """
        if not self._should_update_position():
            return
            
        # Calculate distance we can travel in this time step
        distance_can_travel = self.unit_attributes.current_speed * time_delta
        
        # Check if destination is closer than what we can travel
        distance_to_destination = self._calculate_distance_to_destination()
        if distance_to_destination is not None:
            if distance_to_destination.value <= distance_can_travel.value:
                # Move directly to destination and stop
                self.unit_attributes.position = self.unit_attributes.destination
                self.stop()
                return
        
        # Calculate and apply movement
        dx, dy = self._calculate_movement_vector(distance_can_travel)
        self._update_position(dx, dy)
        
        # Check if we've reached destination after movement
        if self._check_destination_reached():
            self.unit_attributes.position = self.unit_attributes.destination
            self.stop() 