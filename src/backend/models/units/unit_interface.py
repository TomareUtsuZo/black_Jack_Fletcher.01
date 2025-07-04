# Import necessary modules
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class UnitInterface(ABC):
    @abstractmethod
    def assign_to_task_force(self, task_force: Optional[str]) -> None:
        '''Assign the unit to a task force. This method should include validation for security.'''
        pass
    
    @abstractmethod
    def get_unit_state(self) -> Dict[str, Any]:
        '''Return a read-only dictionary of the unit\'s state, excluding sensitive attributes.'''
        pass 