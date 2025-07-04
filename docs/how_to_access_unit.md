# How to Access unit.py in the Project

This document provides step-by-step instructions on how to access and use the `unit.py` module, which is part of the project's backend models.

## File Location
- The `unit.py` file is located at: `src/backend/models/units/unit.py`.
- To navigate to it in your file system, use your IDE or terminal to go to the project root and follow the path.

## Prerequisites
- Ensure you are working in the project's virtual environment to have all dependencies installed. Activate it using: `.\venv\Scripts\Activate.ps1` on Windows.
- Make sure your Python environment is set up correctly, as `unit.py` relies on other modules in the `src/backend/models` directory.

## How to Import unit.py
To use classes or functions from `unit.py` in your code, you can import them as follows:

### Relative Imports (within the backend)
If you're importing from another file in the same package (e.g., in `src/backend/models/game_state_manager.py`):
```python
from .units.unit import Unit  # Import the Unit class specifically
```

### Absolute Imports (from anywhere in the project)
For broader access, use an absolute import relative to the project structure:
```python
from src.backend.models.units.unit import Unit  # Assuming your Python path includes the project root
```

If you encounter import errors, ensure the project root is in your Python path. You can add it temporarily in your script:
```python
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))  # Add project root
from src.backend.models.units.unit import Unit
```

## Example Usage
Here's a simple example of how to use the `Unit` class after importing:
```python
from src.backend.models.units.unit import Unit

# Create an instance of Unit (assuming it has an appropriate constructor)
my_unit = Unit(position={'x': 0, 'y': 0}, orientation=90)  # Example parameters
print(my_unit.get_position())  # Call a method if available
```

## Troubleshooting
- **ModuleNotFoundError**: Double-check your virtual environment and ensure `unit.py` is in the correct location. If needed, run tests with `pytest` to verify.
- **Permissions or Access Issues**: Ensure your IDE or terminal is pointed to the project root (D:\black_Jack_Fletcher.01).

This guide helps maintain consistency across the project. Update it as the codebase evolves. 