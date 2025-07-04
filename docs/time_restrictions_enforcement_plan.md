# Refined Plan to Enforce Restrictions for the Time Module

This document outlines a plan to limit access and modifications in the GameStateManager to specific parts of the time-related classes (e.g., GameTimeManager, GameTime), promoting encapsulation and stability in the codebase. The plan is based on reviewing src/backend/models/game_state_manager.py and src/backend/models/common/time/.

## Overview
[x] The goal is to ensure that GameStateManager can only perform certain tasks, such as querying time state, while preventing unintended access to other time-related methods. This is achieved using Python's built-in features like Abstract Base Classes (ABCs), decorators, and dependency injection, without adding or assuming any new functionality.

## Step-by-Step Plan

[x] 1. **Implement the Time Interface (e.g., TimeInterface)**
   - Create a restricted interface for time-related classes to expose only allowed methods.
   - **Detailed Sub-Plan for Step One**
     - **Rationale**: Implementing TimeInterface establishes a contract for what operations are allowed on time objects, preventing GameStateManager from accessing or modifying unintended methods. This promotes the Single Responsibility Principle and reduces coupling, making the codebase more maintainable and less error-prone, without assuming new features.
     - **Sub-Steps**:
       1. **Create the Interface File**: In a new file (e.g., src/backend/models/common/time/time_interface.py), define the ABC to include only essential methods like get_time_state.
       2. **Define Allowed Methods**: Limit the interface to methods that align with the restrictions, ensuring they are read-only or controlled where possible.
       3. **Update Time Classes**: Modify relevant files in src/backend/models/common/time/ (e.g., game_time.py) to inherit from TimeInterface and implement the required methods.
       4. **Handle Dependencies**: Ensure all imports are correctly managed to avoid circular dependencies.
       5. **Test the Implementation**: Write unit tests to verify that the time classes correctly implement TimeInterface and that only allowed methods work as expected. Use Python's unittest or pytest to check for method calls and raise errors on unauthorized access.
     - **Testing Example**: In tests/backend/test_time.py, add tests like:
       ```python
import unittest
from src.backend.models.common.time.time_interface import TimeInterface

class TestTimeInterface(unittest.TestCase):
    def test_get_time_state(self):
        # Assuming a time instance that implements TimeInterface
        time_instance = ...  # Create an instance
        time_instance.get_time_state()  # Should succeed
    
    def test_unauthorized_access(self):
        with self.assertRaises(AttributeError):  # Or PermissionError if decorated
            time_instance.some_unauthorized_method()  # Ensure this raises an error
```
     - **Integration Notes**: After testing, integrate with your CI/CD pipeline using pytest.ini to run these tests automatically.

[x] 2. **Add Access Controls and Decorators**
   - Use decorators to validate callers and ensure only authorized modules can invoke methods.
   - **Detailed Sub-Plan for Step Two**
     - **Rationale**: Decorators provide a dynamic way to enforce access at runtime, adding an extra layer of security without altering the core logic of the methods. This helps in maintaining the 'certain tasks' restriction for GameStateManager, without assuming new features.
     - **Sub-Steps**:
       1. **Define the Decorator**: Create the decorator in the relevant time file (e.g., game_time.py) to check the caller's module.
       2. **Apply to Methods**: Add the decorator to methods like get_time_state.
       3. **Handle Edge Cases**: Ensure the decorator doesn't interfere with testing or other authorized uses.
       4. **Test the Decorators**: Write tests to verify that unauthorized calls raise errors.
     - **Code Examples**:
       - In game_time.py (updated):
         ```python
def authorized_caller_only(func):
    def wrapper(self, *args, **kwargs):
        import inspect
        caller_frame = inspect.stack()[1]
        caller_module = inspect.getmodule(caller_frame[0])
        if caller_module and caller_module.__name__ != 'src.backend.models.game_state_manager':
            raise PermissionError("This method can only be called from authorized modules like GameStateManager")
        return func(self, *args, **kwargs)
    return wrapper

@authorized_caller_only
def get_time_state(self):
    # Existing method implementation
    pass
```
     - **Testing Example**: In tests/backend/test_time.py:
       ```python
def test_authorized_decorator(self):
    time_instance = ...  # Create instance
    try:
        time_instance.get_time_state()  # From authorized context
    except PermissionError:
        self.fail("Authorized call failed")
    with self.assertRaises(PermissionError):
        # Simulate unauthorized call
        pass
```
     - **Integration Notes**: After implementation, run tests and integrate with CI/CD. This step builds on step one by adding runtime enforcement.

[x] 3. **Refactor for Dependency Injection in GameStateManager**
   - Modify GameStateManager to work with TimeInterface instead of the full time classes.
   - **Code Sketch** (in game_state_manager.py):
     ```python
from src.backend.models.common.time.time_interface import TimeInterface

@dataclass
class GameStateManager:
    _time_controller: TimeInterface = field(init=False)  # Use interface
```

[x] 4. **Module Isolation and Static Checks**
   - Restructure imports and use static analysis tools like mypy to enforce restrictions.
   - **Detailed Sub-Plan for Step Four**
     - **Rationale**: This step isolates modules to prevent direct access and uses static tools to catch potential violations early, enhancing overall code security and maintainability, without assuming new features.
     - **Sub-Steps**:
       1. **Restructure Imports**: In game_state_manager.py, replace direct imports of time classes with TimeInterface.
       2. **Configure Static Analysis**: Update mypy.ini to enforce type checking for the models.
       3. **Handle Import Errors**: Ensure no circular dependencies exist.
       4. **Run Checks**: Integrate mypy into your development workflow.
     - **Code Examples**:
       - In game_state_manager.py:
         ```python
from src.backend.models.common.time.time_interface import TimeInterface
```
       - In mypy.ini:
         ```ini
[mypy]
check_untyped_defs = True
disallow_untyped_calls = True
[mypy-src.backend.models.common.time.*]
disallow_untyped_defs = True
strict_optional = True
```
     - **Testing Example**: Run mypy from the command line.
     - **Integration Notes**: After implementation, commit changes and add to CI/CD.

[x] 5. **Iterate and Test Existing Logic**
   - Review and add checks in methods like tick to ensure only allowed operations are performed.
   - **Detailed Sub-Plan for Step Five**
     - **Rationale**: Testing should validate existing restrictions without assuming future code.
     - **Sub-Steps**:
       1. **Run Tests on Implemented Code**: Test only methods that are fully coded.
       2. **Handle Failures**: Fix issues in implemented methods.
       3. **Expand Test Coverage Gradually**: Add tests as needed.
     - **Integration Notes**: Re-run tests and commit changes.

## Final Recommendations
Implement this plan incrementally, starting with the interface and decorators. If needed, run additional codebase searches for edge cases. 