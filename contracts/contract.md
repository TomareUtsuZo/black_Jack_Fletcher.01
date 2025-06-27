# Development Contract

To the AI Agent: Refer to DEVELOPMENT_GUIDE.md for more details about these principles.

## 1. Naming Conventions
- **Snake Case**: All variable, function, and method names must use snake_case
- **Pascal Case**: All class names must use PascalCase
- **Descriptive Identifiers**: Use verbose, clear names that convey purpose
```python
# GOOD
fetch_user_profile_data()

# BAD
getData()
f_upd()
usrDb
```

## 2. Code Atomization & Function Size
- Each function must do ONE thing
- Break down complex logic blocks into separate functions
- Complex conditions should become predicate functions
- Functions should read like a story, not a puzzle

Example:
```python
# BAD - Logic heavy function
def handle_combat():
    if attacker.is_alive and attacker.has_weapon:
        if target.is_in_range and not target.has_shield:
            if random.random() > 0.2:  # 80% hit chance
                damage = calculate_damage()
                target.health -= damage

# GOOD - Broken into atomic functions
def handle_combat():
    if can_perform_attack():
        execute_attack()

def can_perform_attack():
    return (
        attacker_is_capable() and
        target_is_vulnerable()
    )

def attacker_is_capable():
    return (
        attacker.is_alive and
        attacker.has_weapon
    )
```

## 3. Type Hints & Static Checking
- All function parameters must be typed
- All function return values must be typed
- All class attributes must be typed
- Use dataclasses and TypedDicts for structured data
- Mypy validation with strict settings required

Example:
```python
from typing import Optional, Dict, TypedDict

class UnitStats(TypedDict):
    health: int
    armor: float
    resistances: Dict[str, float]

def calculate_damage(
    base_damage: float,
    multiplier: float,
    target_stats: UnitStats
) -> float:
    return base_damage * multiplier * (1 - target_stats['armor'])
```

## 4. Self-Commenting Code
- Code must clearly convey intent through naming and structure
- Functions must be single-purpose with descriptive names
- Replace magic numbers and strings with named constants
- Comments explain "why" not "what"
- Documentation focuses on high-level concepts and integration points

Example:
```python
# BAD
x = y * 1.5  # Multiply by 1.5

# GOOD
DAMAGE_MULTIPLIER = 1.5
adjusted_damage = base_damage * DAMAGE_MULTIPLIER
```

## Enforcement
- All code must pass mypy validation with strict settings
- Pre-commit hooks will enforce these standards
- Code reviews will verify adherence to these principles
- CI pipeline will automatically check compliance
- Failed checks will block PR merges 