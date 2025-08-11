"""Protocol definition for unit modules."""

from typing import List, Optional, Protocol, runtime_checkable
from ..unit_interface import UnitInterface

@runtime_checkable
class UnitModule(Protocol):
    """Base protocol that all unit modules must implement"""
    def initialize(self) -> None:
        """Initialize the module"""
        ...
        
    def determine_damage_effectiveness(self, target: UnitInterface, base_damage: float) -> float:
        """Determine the final damage effectiveness against the target"""
        ...
        
    def check_for_critical_result(self, target: UnitInterface, base_damage: float) -> None:
        """Check if the attack results in a critical hit and apply additional effects"""
        ...
        
    def delineate_legit_targets(self, detected_units: List[UnitInterface]) -> List[UnitInterface]:
        """Filter detected units to determine legitimate targets"""
        ...
        
    def choose_target_from_legit_options(self, legit_targets: List[UnitInterface]) -> Optional[UnitInterface]:
        """Choose a target from the list of legitimate targets"""
        ...
        
    def send_damage_to_target(self, target: UnitInterface, damage: float) -> None:
        """Apply calculated damage to the target unit"""
        ...
        
    def perform_upkeep(self) -> None:
        """Perform any necessary upkeep after an attack (cooldowns, ammunition, etc.)"""
        ...
        

