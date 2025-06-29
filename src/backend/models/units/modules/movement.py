"""
Movement module for handling unit movement logic.

This module provides the MovementModule class which implements the UnitModule protocol
and handles all movement-related calculations and state changes for units.
"""

import math
from dataclasses import dataclass
from typing import Optional, Protocol

from src.backend.models.common.geometry import (
    Position,
    Bearing,
    NauticalMiles,
    calculate_haversine_distance,
    bearing_between
)
from src.backend.models.units import UnitModule, UnitAttributes

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
    
    def update(self, time_delta: float) -> None:
        """
        Update the unit's position and movement state.
        
        Args:
            time_delta: Time elapsed since last update in current time rate
        """
        if not self._state.is_moving or self.unit_attributes.current_speed.value == 0:
            return
            
        # Calculate distance we can travel in this time step
        distance_can_travel_in_time_delta = self.unit_attributes.current_speed * time_delta
        
        # If we have a destination, check if it's closer than the distance we can travel
        if self.unit_attributes.destination is not None:
            distance_to_destination = calculate_cartesian_distance(
                self.unit_attributes.position,
                self.unit_attributes.destination
            )
            
            # If destination is closer than what we can travel, move directly to it and stop
            if distance_to_destination.value <= distance_can_travel_in_time_delta.value:
                # Move directly to destination
                self.unit_attributes.position = self.unit_attributes.destination
                self.stop()
                return
        
        # Calculate new position based on bearing and distance
        if self._state.current_bearing is not None:
            # Calculate movement vector components
            dx = distance_can_travel_in_time_delta.value * math.sin(math.radians(self._state.current_bearing.degrees))
            dy = distance_can_travel_in_time_delta.value * math.cos(math.radians(self._state.current_bearing.degrees))
            
            # Update position
            new_position = Position(
                self.unit_attributes.position.x + dx,
                self.unit_attributes.position.y + dy
            )
            self.unit_attributes.position = new_position
            
            # Check if we've reached the destination
            if self.unit_attributes.destination is not None:
                distance_to_destination = calculate_cartesian_distance(
                    self.unit_attributes.position,
                    self.unit_attributes.destination
                )
                if distance_to_destination.value < 0.1:  # Within 0.1 nautical miles
                    self.unit_attributes.position = self.unit_attributes.destination
                    self.stop() 