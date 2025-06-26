# Game Development Guide

## Core Development Principles

### 1. Feature Implementation Policy
- **STRICT FEATURE SCOPE**: No functionality will be implemented without explicit request and approval
- When a feature is requested, only the exact requested functionality will be implemented
- Related or dependent features will be documented as recommendations but NOT implemented
- Example:
  ```
  Request: "Add attack functionality to units"
  Allowed: Implement only the attack action
  Not Allowed: Automatically adding health/damage tracking without explicit request
  ```

### 2. SOLID Principles Priority
We will strictly adhere to SOLID principles in our implementation:
- **S**ingle Responsibility Principle: Each class has one job
- **O**pen/Closed Principle: Open for extension, closed for modification
- **L**iskov Substitution Principle: Derived classes must be substitutable for base classes
- **I**nterface Segregation: Many specific interfaces over one general interface
- **D**ependency Inversion: Depend on abstractions, not concretions

Only when no viable SOLID solution can be found will we consider breaking these principles, and such decisions must be explicitly documented.

### 3. Code Style and Readability

#### Naming Conventions
- **Snake Case**: All variable, function, and method names must use Pythonic snake_case
- **Pascal Case**: All class names must use PascalCase, following Python standards
- **Descriptive Identifiers**: Use verbose, clear names that convey purpose
  ```python
  # GOOD
  fetch_user_profile_data()
  
  # BAD
  getData()
  f_upd()
  usrDb
  ```

#### Code Atomization and Statement-Like Functions
1. **Logic Block Elimination**:
   ```python
   # BAD - Complex logic block
   def process_turn():
       if player.has_resources():
           if player.can_take_action():
               if not player.is_stunned():
                   if player.has_valid_target():
                       # More nested logic...
                       perform_action()

   # GOOD - Break down into clear, atomic functions
   def process_turn():
       if can_player_act():
           perform_action()

   def can_player_act():
       return (
           has_sufficient_resources() and
           action_is_available() and
           player_is_not_stunned() and
           target_is_valid()
       )
   ```

2. **Function Size Principle**:
   - Each function should do ONE thing
   - If you see logic blocks (if/else chains, nested conditions), break them into separate functions
   - Complex conditions should become their own predicate functions
   - Logic operations should be composed of smaller, clear functions

3. **Examples of Breaking Down Logic**:
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

   def target_is_vulnerable():
       return (
           target_is_in_range() and
           not target_has_shield()
       )

   def execute_attack():
       if attack_hits():
           apply_damage(calculate_damage())
   ```

4. **Benefits**:
   - Each function has a clear, single purpose
   - Logic is easier to follow and modify
   - Conditions become self-documenting
   - Testing is simplified - each function tests one thing
   - Changes are isolated to specific functions
   - Code reads like a story instead of a puzzle

#### Type Hints and Static Checking

1. **Mandatory Type Annotations**:
   ```python
   # BAD - No type hints
   def calculate_damage(base_damage, multiplier):
       return base_damage * multiplier

   # GOOD - Full type hints
   from typing import Optional, List, Dict, TypedDict, Union

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

2. **Type Hint Requirements**:
   - All function parameters must be typed
   - All function return values must be typed
   - All class attributes must be typed
   - Use dataclasses and TypedDicts for structured data
   - Type all collections (List, Dict, Set, etc.)
   - Include Optional/Union types where appropriate

3. **Static Type Checking**:
   - Mypy will be used for static type checking
   - All code must pass mypy validation with strict settings
   - Type checking will be part of the CI pipeline
   - Configuration in `mypy.ini`:
     ```ini
     [mypy]
     python_version = 3.11
     strict = True
     disallow_untyped_defs = True
     disallow_incomplete_defs = True
     check_untyped_defs = True
     disallow_untyped_decorators = True
     no_implicit_optional = True
     warn_redundant_casts = True
     warn_return_any = True
     warn_unused_ignores = True
     ```

4. **Type Hint Best Practices**:
   ```python
   from typing import Sequence, Optional, TypeVar, Generic

   T = TypeVar('T')

   class GameState(Generic[T]):
       def __init__(self, initial_state: T) -> None:
           self.state: T = initial_state

       def update(self, new_state: Optional[T] = None) -> None:
           if new_state is not None:
               self.state = new_state

   class Unit:
       def __init__(
           self,
           name: str,
           health: float,
           abilities: Sequence[str]
       ) -> None:
           self.name: str = name
           self.health: float = health
           self.abilities: List[str] = list(abilities)
   ```

5. **Benefits and Enforcement**:
   - Single source of truth for type information
   - Compiler-style guarantees
   - Better IDE support and autocompletion
   - Catches type-related bugs before runtime
   - Self-documenting code
   - No need for manual type documentation

6. **Type Checking in Development**:
   - Run mypy locally before committing
   - IDE integration for real-time type checking
   - Type checking is part of the test suite
   - Failed type checks block merges

#### CI Pipeline for Type Checking

1. **Local Development Setup**:
   ```bash
   # Install development dependencies
   pip install mypy pytest pytest-mypy

   # Run type checking locally
   mypy .
   
   # Run tests with type checking
   pytest --mypy
   ```

2. **GitHub Actions Workflow**:
   ```yaml
   # .github/workflows/type-check.yml
   name: Type Check

   on:
     push:
       branches: [ main ]
     pull_request:
       branches: [ main ]

   jobs:
     typecheck:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         
         - name: Set up Python 3.11
           uses: actions/setup-python@v5
           with:
             python-version: '3.11'
             
         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             pip install -r requirements.txt
             pip install mypy pytest pytest-mypy
             
         - name: Run mypy
           run: mypy .
           
         - name: Run tests with type checking
           run: pytest --mypy

   ```

3. **Pre-commit Hook Setup**:
   ```yaml
   # .pre-commit-config.yaml
   repos:
   - repo: https://github.com/pre-commit/mirrors-mypy
     rev: v1.8.0
     hooks:
     - id: mypy
       additional_dependencies: [types-all]
       args: [--strict]
   ```

4. **Type Checking Workflow**:
   - Developers run mypy locally before commits
   - Pre-commit hook catches type issues before commit
   - CI pipeline runs full type check on push/PR
   - Failed type checks block PR merges
   - Type check reports are added to PR comments

5. **Error Handling and Exceptions**:
   - Type ignore comments require justification:
     ```python
     # Example of acceptable type ignore
     import third_party_lib  # type: ignore  # Third-party library lacks type hints
     
     # Example of unacceptable type ignore
     def unsafe_function():  # type: ignore  # Don't ignore missing return type
     ```
   - Create custom type stubs for untyped third-party libraries
   - Document any type-checking exceptions in code reviews

6. **Monitoring and Maintenance**:
   - Regular updates of mypy and related tools
   - Periodic review of type ignore comments
   - Type coverage reports in CI pipeline
   - Gradual elimination of legacy untyped code

#### Self-Commenting Code Principles
1. **Intent Through Design**:
   - Code should clearly convey intent through naming and structure
   - Functions should be single-purpose with names that describe that purpose
   - Avoid unnecessary comments by making the code self-documenting

2. **Clean Code Practices**:
   - Replace magic numbers and strings with named constants
   - Strive for maximum readability
   - Make code as obvious as possible
   - Break complex operations into well-named helper functions

3. **Comment Philosophy**:
   - Comments should explain "why" not "what" when needed
   - Code should tell its own story through structure and naming
   - Minimize reliance on inline comments
   - Documentation should focus on high-level concepts and integration points

The goal is to maintain clean, readable, and maintainable code that is self-documenting through careful naming and structure.

## Feature Documentation Structure

### Current Features
Each implemented feature will be documented here with:
- Description
- Implementation details
- Current limitations
- Test coverage

### Feature Recommendations
When related features are identified but not implemented, they will be documented here:
```markdown
Feature: [Name]
Related to: [Existing Feature]
Description: [Brief description]
Potential Implementation: [High-level approach]
Dependencies: [Required features/systems]
Considerations: [Technical/Design considerations]
```

## Development Process

### 1. Feature Request
- Clear description of requested functionality - AI agent will let me know when I am not being clear, and help me to be more clear.
- Explicit scope boundaries - AI agent will ask when scope is not clear
- Acceptance criteria - a test proving the feature works.

### 2. Design Review
- SOLID principles compliance check
- Identification of potential related features (to be documented only)
- Interface design
- Test strategy

### 3. Implementation
- Strict adherence to requested scope
- Documentation of design decisions
- Unit test implementation
- Integration test implementation (when applicable)

### 4. Feature Documentation
- Update Current Features section
- Document any identified future recommendations
- Update relevant test documentation

## Project Structure Guidelines

### Code Organization
- Clear separation of concerns
- Feature-based organization
- Interface-first design
- Test organization mirrors source code

### Testing Strategy
- Functional tests for that test a feature without looking at the implimentation of the feature. 
    If that way if there are any changes, we can ensure that the intent is still being met, even if the 
    way things are being done is different.
- Integration tests for feature interactions
- Clear test naming convention
- Test documentation requirements

## Feature Recommendation Template
```markdown
# Feature Recommendation

## Overview
- Name: [Feature Name]
- Related Feature: [Existing Feature]
- Priority: [Low/Medium/High]

## Technical Details
- Proposed Implementation:
- Required Components:
- Potential Challenges:

## Integration Points
- Systems Affected:
- Required Modifications:
- Dependencies:

## Considerations
- Performance Impact:
- Scalability:
- Maintenance:

## Notes
[Additional context or thoughts]
```

## Version Control Guidelines
- Feature branches
- Commit message format
- PR review requirements
- Documentation update requirements

---
This is a living document and will be updated as the project evolves. All changes to this guide must be explicitly approved. 