"""Unit module containing the core Unit class."""

from dataclasses import dataclass, field
from src.backend.models.common import Position
from src.backend.models.common.geometry.nautical_miles import NauticalMiles
from typing import Dict, Optional, Protocol
from uuid import UUID, uuid4

from .types.unit_type import UnitType

class UnitModule(Protocol):
    """Base protocol that all unit modules must implement"""
    def initialize(self) -> None:
        """Initialize the module"""
        ...

@dataclass
class UnitAttributes:
    """Core attributes that define a unit"""
    # Identity
    name: str
    unit_id: UUID
    unit_type: UnitType
    task_force_assigned_to: Optional[str]  # Could be UUID if TaskForce gets its own type
    
    # Position and Movement
    position: Position
    destination: Optional[Position]
    max_speed: NauticalMiles  # Maximum speed in knots (nautical miles per hour)
    current_speed: NauticalMiles  # Current speed in knots
    
    # Resources
    max_health: float
    current_health: float
    max_fuel: float
    current_fuel: float

class Unit:
    """
    Core Unit class that manages unit state and coordinates between modules.
    Each specialized capability (attack, movement, etc.) is handled by a dedicated module.
    """
    def __init__(
        self,
        name: str,
        unit_type: UnitType,
        position: Position,
        max_speed: NauticalMiles,
        max_health: float,
        max_fuel: float,
        task_force: Optional[str] = None,
        unit_id: Optional[UUID] = None
    ) -> None:
        """
        Initialize a new Unit with the given attributes.
        
        Args:
            name: The unit's name
            unit_type: The type of unit (ship, submarine, etc.)
            position: Initial position
            max_speed: Maximum speed capability in knots (nautical miles per hour)
            max_health: Maximum health points
            max_fuel: Maximum fuel capacity
            task_force: Optional task force assignment
            unit_id: Optional UUID (will be generated if not provided)
        """
        self.attributes = UnitAttributes(
            name=name,
            unit_id=unit_id or uuid4(),
            unit_type=unit_type,
            task_force_assigned_to=task_force,
            position=position,
            destination=None,
            max_speed=max_speed,
            current_speed=NauticalMiles(0.0),  # Start stationary
            max_health=max_health,
            current_health=max_health,  # Start at full health
            max_fuel=max_fuel,
            current_fuel=max_fuel,  # Start with full fuel
        )
        self._modules: Dict[str, UnitModule] = {}
    
    def add_module(self, name: str, module: UnitModule) -> None:
        """
        Add a new capability module to the unit
        
        Args:
            name: Unique identifier for the module
            module: The module instance to add
        """
        if name in self._modules:
            raise ValueError(f"Module {name} already exists")
        
        module.initialize()
        self._modules[name] = module
    
    def get_module(self, name: str) -> Optional[UnitModule]:
        """
        Retrieve a module by name
        
        Args:
            name: The name of the module to retrieve
            
        Returns:
            The module if found, None otherwise
        """
        return self._modules.get(name)
    
    @property
    def is_alive(self) -> bool:
        """Check if the unit is still alive"""
        return self.attributes.current_health > 0
    
    @property
    def has_fuel(self) -> bool:
        """Check if the unit has any fuel remaining"""
        return self.attributes.current_fuel > 0
    
    def take_damage(self, amount: float) -> None:
        """
        Apply damage to the unit
        
        Args:
            amount: Amount of damage to apply
        """
        self.attributes.current_health = max(0.0, self.attributes.current_health - amount)
    
    def consume_fuel(self, amount: float) -> bool:
        """
        Consume fuel for an action
        
        Args:
            amount: Amount of fuel to consume
            
        Returns:
            True if fuel was consumed, False if insufficient fuel
        """
        if self.attributes.current_fuel < amount:
            return False
        
        self.attributes.current_fuel -= amount
        return True
    
    def set_destination(self, destination: Position) -> None:
        """
        Set a new destination for the unit
        
        Args:
            destination: The target position to move to
        """
        self.attributes.destination = destination
    
    def set_speed(self, speed: NauticalMiles) -> None:
        """
        Set the unit's current speed
        
        Args:
            speed: The desired speed in knots (nautical miles per hour)
            
        Raises:
            ValueError: If speed is negative or exceeds max_speed
        """
        if speed.value < 0:
            raise ValueError("Speed cannot be negative")
        if speed > self.attributes.max_speed:
            raise ValueError(f"Speed cannot exceed maximum speed of {self.attributes.max_speed}")
        self.attributes.current_speed = speed
    
    def assign_to_task_force(self, task_force: Optional[str]) -> None:
        """
        Assign the unit to a task force
        
        Args:
            task_force: The task force identifier, or None to remove from current task force
        """
        self.attributes.task_force_assigned_to = task_force 