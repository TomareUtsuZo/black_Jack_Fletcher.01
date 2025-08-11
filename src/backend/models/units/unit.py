"""Unit module containing the core Unit class."""

from dataclasses import dataclass, field
from src.backend.models.common import Position
from src.backend.models.common.geometry.nautical_miles import NauticalMiles
from typing import Dict, List, Optional, Any
from .protocols.unit_module_protocol import UnitModule
from uuid import UUID, uuid4

from .types.unit_type import UnitType as UnitType  # explicitly re-export
from .unit_interface import UnitInterface
import logging  # Import for logging functionality
from enum import Enum  # Import for state tracking

class UnitState(Enum):
    OPERATING = 'operating'
    SINKING = 'sinking'  # Unit is combat ineffective, dead in water, and taking on water, either the crew is still on board and/or heroic efforts might save ship. checks must be made each minute to discover if the ship has sunk. Damage control efforts must be tracked to determine if the ship will be sunk this time, and even possiblely the ship could be restored to operating. Further, the ship could be salavaged (by any side with the will and capability), and finally, the ships crew could be rescued or captured. The only weapons a sinking ship might be able to use are manual weapons, like 50 cal machine guns, small arms, and mechanical anti-aircraft weapons.
    SUNK = 'sunk' # this is destroyed, and may no longer do any active operations. At the most, we might track the state of the surviving crew, to determine if they are rescued/captured.



@dataclass
class UnitAttributes:
    """Core attributes that define a unit"""
    # Identity
    unit_id: UUID  # Unique identifier for the ship
    name: str  # Full name of the ship
    hull_number: str  # Hull number in proper naval format
    unit_type: UnitType
    task_force_assigned_to: Optional[str]  # Could be UUID if TaskForce gets its own type
    ship_class: str  # Class of the ship
    faction: str  # Faction of the ship

    # Position and Movement
    position: Position
    destination: Optional[Position]
    max_speed: NauticalMiles  # Maximum speed in knots (nautical miles per hour)
    cruise_speed: NauticalMiles  # Economical cruising speed in knots
    current_speed: NauticalMiles  # Current speed in knots

    # Resources
    max_health: float
    current_health: float
    max_fuel: float
    current_fuel: float
    crew: int  # Standard complement (probably not relevant, but good for stories)
    tonnage: int  # Tonnage of the ship (probably not relevant, but good for stories)
    visual_range: NauticalMiles  # Visual detection range in nautical miles
    visual_detection_rate: float  # Detection rate for visual detection, a float value (e.g., 0.0 to 1.0 representing probability)


class Unit(UnitInterface):
    """
    Core Unit class that manages unit state and coordinates between modules.
    Each specialized capability (attack, movement, etc.) is handled by a dedicated module.
    """
    state: UnitState  # Type annotation for state attribute
    def __init__(
        self,
        unit_id: UUID,
        name: str,
        hull_number: str,
        unit_type: UnitType,
        task_force_assigned_to: Optional[str],
        ship_class: str,
        faction: str,
        position: Position,
        destination: Optional[Position],
        max_speed: NauticalMiles,
        cruise_speed: NauticalMiles,
        current_speed: NauticalMiles,
        max_health: float,
        current_health: float,
        max_fuel: float,
        current_fuel: float,
        crew: int,
        visual_range: NauticalMiles,
        visual_detection_rate: float,  # Detection rate for visual detection
        tonnage: int
    ) -> None:
        """
        Initialize a new Unit with the given attributes.
        
        Args:
            unit_id: Unique identifier for the ship
            name: The unit's name
            hull_number: Hull number in proper naval format
            unit_type: The type of unit (ship, submarine, etc.)
            task_force_assigned_to: Optional task force assignment
            ship_class: Class of the ship
            faction: Faction the unit belongs to
            position: Initial position
            destination: Optional destination position
            max_speed: Maximum speed capability in knots
            cruise_speed: Economical cruising speed in knots
            current_speed: Current speed in knots
            max_health: Maximum health points
            current_health: Current health points
            max_fuel: Maximum fuel capacity
            current_fuel: Current fuel level
            crew: Standard complement
            visual_range: Visual detection range in nautical miles
            visual_detection_rate: Detection rate for visual detection, a float value           (e.g., 0.0 to 1.0)
            tonnage: Ship's tonnage
        """
        self.attributes = UnitAttributes(
            unit_id=unit_id,
            name=name,
            hull_number=hull_number,
            unit_type=unit_type,
            task_force_assigned_to=task_force_assigned_to,
            ship_class=ship_class,
            faction=faction,
            position=position,
            destination=destination,
            max_speed=max_speed,
            cruise_speed=cruise_speed,
            current_speed=current_speed,
            max_health=max_health,
            current_health=current_health,
            max_fuel=max_fuel,
            current_fuel=current_fuel,
            crew=crew,
            visual_range=visual_range,
            visual_detection_rate=visual_detection_rate,
            tonnage=tonnage
        )
        self.state: UnitState = UnitState.OPERATING  # Default state
        self.crew_status = 'surviving'  # Default crew status; can be 'surviving', 'rescued', 'captured', etc.
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
    def is_not_sunk(self) -> bool:
        """Check if the unit is not in a sunk state"""
        return self.state != UnitState.SUNK
        
    @property
    def is_alive(self) -> bool:
        """Check if the unit is still alive (alias for is_not_sunk for backward compatibility)"""
        return self.is_not_sunk
        
    def is_in_state(self, state: UnitState) -> bool:
        """Check if the unit is in a specific state"""
        return self.state == state
    
    @property
    def has_fuel(self) -> bool:
        """Check if the unit has any fuel remaining"""
        return self.attributes.current_fuel > 0
    
    def take_damage(self, amount: float) -> None:
        """
        Apply damage to the unit. This is a legacy method that will be deprecated.
        New code should use the Attack module's damage system instead.
        
        Args:
            amount: Amount of damage to apply
        """
        # Get or create attack module
        attack_module = self.get_module('attack')
        if not attack_module:
            from src.backend.models.units.modules.attack import Attack
            attack_module = Attack(attacker=self)
            self.add_module('attack', attack_module)
        
        # Use the new damage system
        base_damage = attack_module.determine_damage_effectiveness(self, amount)
        attack_module.apply_damage_to_current_health(self, base_damage)
        attack_module.check_for_critical_result(self, base_damage)
        
        # Check for state changes after all damage is applied
        if self.attributes.current_health <= 0 and self.state != UnitState.SINKING:
            self.state = UnitState.SINKING
            logging.info(f"{self.attributes.name} has been sunk, crew status: {self.crew_status}")
    
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
    
    def perform_tick(self) -> None:
        """
        Perform internal tasks for the unit during a game tick.
        
        This method handles all unit-specific updates, such as detection and movement,
        to encapsulate behavior and reduce conflicts.
        """
        # Handle movement if the module is present
        movement_module = self.get_module('movement')
        if movement_module:
            # Assuming the movement module has a method to perform movement
            movement_module.perform_movement()  # Call the movement logic
    
        # Handle detection if the module is present
        detection_module = self.get_module('detection')
        if detection_module:
            detection_rate = self.attributes.visual_detection_rate
            visual_range = self.attributes.visual_range
            # detected_units would be called if needed
            detected_units = detection_module.perform_visual_detection(detection_rate, visual_range)  
            self.perform_attack(detected_units)
        

    def perform_attack(self, detected_units: List['Unit']) -> None:
        """
        Evaluate detected units and perform attacks on legitimate targets.
        
        Args:
            detected_units: List of units that have been detected
        """
        # Get or create attack module
        attack_module = self.get_module('attack')
        if not attack_module:
            from src.backend.models.units.modules.attack import Attack
            attack_module = Attack(attacker=self)
            self.add_module('attack', attack_module)
        
        # Get legitimate targets
        legit_targets = attack_module.delineate_legit_targets(detected_units)
        
        # Choose the best target from legitimate options
        chosen_target = attack_module.choose_target_from_legit_options(legit_targets)
        
        if not chosen_target:
            logging.info(f"{self.attributes.name} found no legitimate targets")
            return
            
        # Calculate and apply damage if we have weapons
        if self.has_weapons():
            # Calculate damage
            damage = attack_module.calculate_attack_effectiveness(chosen_target)
            # Apply the damage
            attack_module.send_damage_to_target(chosen_target, damage)
            logging.info(f"{self.attributes.name} attacked {chosen_target.attributes.name}")
        else:
            logging.warning(f"{self.attributes.name} has no weapons")
    
    def update_crew_status(self, status: str) -> None:  # New method for updating crew status
        """Update the crew status (e.g., 'surviving', 'rescued', 'captured')."""
        if status in ['surviving', 'rescued', 'captured']:
            self.crew_status = status
        else:
            logging.warning(f"Invalid crew status: {status}")

    def _validate_task_force(self, task_force: Optional[str]) -> bool:
        # Basic validation: Ensure task_force is a non-empty string if provided
        if task_force is not None and not isinstance(task_force, str):
            return False
        if task_force and not task_force.strip():  # Check for non-empty string
            return False
        return True  # Valid if it passes checks
    
    def assign_to_task_force(self, task_force: Optional[str]) -> None:
        if task_force is not None and not self._validate_task_force(task_force):
            raise ValueError("Invalid task force")
        self.attributes.task_force_assigned_to = task_force
    
    def get_unit_state(self) -> Dict[str, Any]:
        return {
            'unit_id': str(self.attributes.unit_id),
            'task_force': self.attributes.task_force_assigned_to,
        } 

    def has_weapons(self) -> bool:
        """Temporarily check if the unit has weapons; always returns true for now."""
        return True  # Placeholder to always allow attacks 