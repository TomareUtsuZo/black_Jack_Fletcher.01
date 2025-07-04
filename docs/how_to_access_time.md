# How to Access the Time Module in Black Jack Fletcher

This document provides guidelines on how to access and interact with the time-related features in the project, ensuring compliance with the enforced restrictions. It focuses on the `TimeInterface` for controlled access, promoting encapsulation and stability.

## Introduction
The time module, located in `src/backend/models/common/time/`, manages game time functionalities such as scheduling and state queries. Due to restrictions, direct access to time classes is limited. Instead, use the `TimeInterface` to perform allowed operations.

## Key Concepts
- **TimeInterface**: An abstract base class that defines only the permitted methods, such as querying time state. This prevents unauthorized modifications.
- **Access Restrictions**: Only specific modules (e.g., `GameStateManager`) can call certain methods, enforced via decorators.

## Steps to Access Time Safely
1. **Import the Interface**: Always import from `src/backend/models/common/time/time_interface.py`.
2. **Obtain an Instance**: Get an instance of a time class that implements `TimeInterface`, such as `GameTime`.
3. **Call Allowed Methods**: Use methods like `get_time_state()` for read-only operations.

## Code Examples
Here are self-commented examples demonstrating safe access:

### Example 1: Querying Time State
```python
# Import the TimeInterface to ensure restricted access
from src.backend.models.common.time.time_interface import TimeInterface
import src.backend.models.common.time.game_time as game_time  # Assuming this implements TimeInterface

def safe_time_query():
    # Create an instance of a class that implements TimeInterface
    time_instance: TimeInterface = game_time.GameTime()  # Self-comment: This uses the interface for type safety
    
    try:
        # Call an allowed method; this is restricted to authorized callers
        current_state = time_instance.get_time_state()  # Self-comment: Retrieves the current time state without modifications
        print(f"Current game time state: {current_state}")  # Output for verification
    except PermissionError as e:
        print(f"Access denied: {e}")  # Self-comment: Handles errors if called from unauthorized context
```

### Example 2: Handling Potential Errors
```python
# Self-comment: This example shows how to wrap time access in a try-except block for robustness
from src.backend.models.common.time.time_interface import TimeInterface

# Hypothetical function in an authorized module
def authorized_time_access(time_obj: TimeInterface):
    # Self-comment: Only proceed if the object adheres to the interface
    if hasattr(time_obj, 'get_time_state'):
        try:
            result = time_obj.get_time_state()  # Self-comment: Calls the method; decorator will enforce restrictions
            return result
        except AttributeError:
            raise ValueError("Method not available; ensure interface is implemented correctly")
```

## Warnings and Best Practices
- **Do Not Access Directly**: Avoid importing or using time classes directly (e.g., from `game_time.py`) to prevent violations.
- **Testing**: Always test access in a controlled environment using tests in `tests/backend/`.
- **Edge Cases**: If you encounter permission errors, verify your module's authorization via decorators.
- **Updates**: Refer to `docs/time_restrictions_enforcement_plan.md` for more on enforcement.

This approach ensures the backend remains stable while allowing necessary interactions. 