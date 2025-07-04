# Refined Plan to Enforce Restrictions Within Python

This document outlines a plan to limit access and modifications in the GameStateManager to specific parts of the Unit class, promoting encapsulation and stability in the codebase. The plan is based on reviewing src/backend/models/game_state_manager.py and src/backend/models/units/unit.py.

## Overview
The goal is to ensure that GameStateManager (via UnitManager) can only perform certain tasks, such as assigning to a task force or querying state, while preventing unintended access to other Unit methods. This is achieved using Python's built-in features like Abstract Base Classes (ABCs), decorators, and dependency injection.

## Step-by-Step Plan

1. **Implement the Unit Interface (UnitInterface)**
   - Create a restricted interface for Unit to expose only allowed methods.
   - **Detailed Sub-Plan for Step One**
     - **Rationale**: Implementing UnitInterface establishes a contract for what operations are allowed on Unit objects, preventing GameStateManager from accessing or modifying unintended methods. This promotes the Single Responsibility Principle and reduces coupling, making the codebase more maintainable and less error-prone.
     - **Sub-Steps**:
       1. **Create the Interface File**: In a new file (src/backend/models/units/unit_interface.py), define the ABC to include only essential methods like assign_to_task_force and get_unit_state.
       2. **Define Allowed Methods**: Limit the interface to methods that align with the restrictions, ensuring they are read-only or controlled where possible.
       3. **Update the Unit Class**: Modify src/backend/models/units/unit.py to inherit from UnitInterface and implement the required methods.
       4. **Handle Dependencies**: Ensure all imports are correctly managed to avoid circular dependencies.
       5. **Test the Implementation**: Add unit tests to verify that only interface methods can be called successfully.
     - **Code Examples**:
       - In unit_interface.py:
         ```python
from abc import ABC, abstractmethod
from typing import Optional, Dict

class UnitInterface(ABC):
    @abstractmethod
    def assign_to_task_force(self, task_force: Optional[str]) -> None:
        '''Assign the unit to a task force. This method should include validation for security.'''
        pass
    
    @abstractmethod
    def get_unit_state(self) -> Dict[str, Any]:
        '''Return a read-only dictionary of the unit\'s state, excluding sensitive attributes.'''
        pass
```
       - In unit.py (partial update):
         ```python
from .unit_interface import UnitInterface  # Import the new interface

class Unit(UnitInterface):  # Inherit from UnitInterface
    def assign_to_task_force(self, task_force: Optional[str]) -> None:
        # Implementation with checks
        if task_force is not None and not self._validate_task_force(task_force):
            raise ValueError("Invalid task force")
        self.attributes.task_force_assigned_to = task_force
    
    def get_unit_state(self) -> Dict[str, Any]:
        return {
            'unit_id': str(self.attributes.unit_id),
            'task_force': self.attributes.task_force_assigned_to,
            # Include only safe, read-only data
        }
```
     - **Integration Notes**: After implementing this, update UnitManager in game_state_manager.py to use UnitInterface types. This step sets the foundation for subsequent steps, like adding decorators, by ensuring all Unit interactions are funneled through the interface. Test for compatibility and run mypy checks to catch any issues.

2. **Add Access Controls and Decorators**
   - Use decorators to validate callers and ensure only authorized modules (e.g., UnitManager) can invoke methods.
   - **Code Sketch** (in unit.py):
     ```python
def authorized_caller_only(func):
    def wrapper(self, *args, **kwargs):
        import inspect
        caller_frame = inspect.stack()[1]
        caller_module = inspect.getmodule(caller_frame[0])
        if caller_module and caller_module.__name__ != 'src.backend.models.game_state_manager':
            raise PermissionError("This method can only be called from authorized modules like UnitManager")
        return func(self, *args, **kwargs)
    return wrapper

class Unit(UnitInterface):
    @authorized_caller_only
    def assign_to_task_force(self, task_force: Optional[str]) -> None:
        self.attributes.task_force_assigned_to = task_force
```

3. **Refactor UnitManager for Dependency Injection**
   - Modify UnitManager to work with UnitInterface instead of the full Unit class.
   - **Code Sketch** (in game_state_manager.py):
     ```python
from src.backend.models.units.unit_interface import UnitInterface

@dataclass
class UnitManager:
    _units: Dict[str, UnitInterface] = field(default_factory=dict)

    def add_unit(self, unit: UnitInterface, ...) -> str:
        pass  # Implementation details
```

4. **Module Isolation and Static Checks**
   - Restructure imports and use static analysis tools like mypy to enforce restrictions.
   - **Configuration** (in mypy.ini):
     ```ini
     [mypy-src.backend.models.*]
     disallow_untyped_calls = True
     ```

5. **Iterate and Test Across GameStateManager Logic**
   - Review and add checks in methods like tick to ensure only allowed operations are performed.
   - Add tests in tests/backend/ to validate the restrictions.

## Final Recommendations
Implement this plan incrementally, starting with the interface and decorators. If needed, run additional codebase searches for edge cases. 