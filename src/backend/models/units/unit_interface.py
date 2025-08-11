"""Interface definition for game units."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from .types.unit_type import UnitType
from ..common.geometry.position import Position
from ..common.geometry.nautical_miles import NauticalMiles

class UnitInterface(ABC):
    @abstractmethod
    def perform_tick(self) -> None:
        """Perform unit updates during a game tick."""
        pass

    @abstractmethod
    def take_damage(self, amount: float) -> None:
        """Apply damage to the unit."""
        pass

    @abstractmethod
    def is_not_sunk(self) -> bool:
        """Check if the unit is not in a sunk state."""
        pass

    @abstractmethod
    def has_weapons(self) -> bool:
        """Check if the unit has weapons available."""
        pass

    @abstractmethod
    def perform_attack(self, detected_units: List['UnitInterface']) -> None:
        """Evaluate and perform attacks on detected units."""
        pass

    @abstractmethod
    def assign_to_task_force(self, task_force: Optional[str]) -> None:
        """Assign the unit to a task force."""
        pass
    
    @abstractmethod
    def get_unit_state(self) -> Dict[str, Any]:
        """Return a read-only dictionary of the unit's state."""
        pass