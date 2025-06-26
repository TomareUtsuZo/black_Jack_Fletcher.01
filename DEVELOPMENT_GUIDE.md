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

## Pre-Development Setup and Planning

### 1. Project Structure Setup
```
project_root/
├── src/
│   ├── core/           # Core game mechanics and systems
│   ├── models/         # Data models and state management
│   ├── services/       # Business logic and services
│   └── utils/          # Utility functions and helpers
├── tests/
│   ├── functional/     # Feature behavior tests
│   ├── integration/    # System integration tests
│   └── unit/          # Individual component tests
├── docs/              # Documentation
│   ├── architecture/  # System design documents
│   ├── api/          # API documentation
│   └── features/     # Feature specifications
└── scripts/          # Development and deployment scripts
```

### 2. Development Environment Configuration
1. **IDE Setup**:
   - Configure auto-formatting (black)
   - Set up mypy integration
   - Configure test runner integration
   - Set up debugging configurations

2. **Git Hooks**:
   - Pre-commit hooks for linting
   - Pre-push hooks for tests
   - Commit message templates

3. **Virtual Environment**:
   - Python version management
   - Dependencies isolation
   - Development vs production requirements

### 3. Documentation Structure
1. **Architecture Documentation**:
   - System overview
   - Component interactions
   - Data flow diagrams
   - State management approach

2. **Feature Documentation**:
   - Feature request template
   - Implementation guidelines
   - Testing requirements
   - Acceptance criteria template

3. **API Documentation**:
   - API design principles
   - Endpoint documentation
   - Request/response formats
   - Authentication/authorization

### 4. Quality Assurance Setup
1. **Testing Framework**:
   - Test naming conventions
   - Test data management
   - Mocking strategies
   - Coverage requirements

2. **Code Quality Tools**:
   - Linting configuration
   - Code complexity limits
   - Documentation requirements
   - Performance benchmarks

### 5. Project Management
1. **Issue Tracking**:
   - Issue templates
   - Bug report format
   - Feature request format
   - Priority levels

2. **Version Control**:
   - Branch naming convention
   - PR template
   - Review checklist
   - Release process

### 6. Security Considerations
1. **Code Security**:
   - Secret management
   - Authentication flows
   - Authorization patterns
   - Input validation

2. **Data Security**:
   - Data storage
   - Encryption requirements
   - Privacy considerations
   - Backup strategies

### 7. Performance Planning
1. **Metrics**:
   - Performance KPIs
   - Monitoring setup
   - Logging strategy
   - Alert thresholds

2. **Optimization**:
   - Caching strategy
   - Database indexing
   - Resource management
   - Load handling

### 8. Deployment Strategy
1. **Environment Setup**:
   - Development
   - Staging
   - Production
   - Testing

2. **CI/CD Pipeline**:
   - Build process
   - Test automation
   - Deployment automation
   - Rollback procedures

## Architecture: MVVM Implementation

### 1. MVVM Overview
```
Game Architecture
├── Models/
│   ├── Game entities (units, resources, etc.)
│   ├── Game state
│   └── Business logic
├── Views/
│   ├── UI components
│   ├── Rendering systems
│   └── User input handlers
└── ViewModels/
    ├── State management
    ├── Command handling
    └── Data transformation
```

### 2. Layer Responsibilities

1. **Models**:
   - Pure game state and business logic
   - No UI or presentation logic
   - Examples:
     ```python
     class GameUnit:
         def __init__(self, unit_id: str, position: Position) -> None:
             self.unit_id: str = unit_id
             self.position: Position = position
             self._state: UnitState = UnitState.IDLE

         def update_state(self, new_state: UnitState) -> None:
             # Pure business logic
             self._state = new_state
     ```

2. **ViewModels**:
   - Transforms Model data for View consumption
   - Handles user commands
   - Manages UI state
   - Examples:
     ```python
     class GameUnitViewModel:
         def __init__(self, unit: GameUnit) -> None:
             self._unit = unit
             self.position = self._transform_position()
             self.commands = self._setup_commands()

         def _transform_position(self) -> DisplayPosition:
             # Transform game coordinates to screen coordinates
             return DisplayPosition(
                 x=self._unit.position.x * TILE_SIZE,
                 y=self._unit.position.y * TILE_SIZE
             )

         def _setup_commands(self) -> Dict[str, Command]:
             return {
                 "move": Command(self._handle_move),
                 "attack": Command(self._handle_attack)
             }
     ```

3. **Views**:
   - Pure presentation logic
   - No business logic
   - Binds to ViewModel
   - Examples:
     ```python
     class UnitView:
         def __init__(self, view_model: GameUnitViewModel) -> None:
             self.view_model = view_model
             self._sprite = None

         def render(self, screen: Surface) -> None:
             # Pure rendering logic
             position = self.view_model.position
             screen.blit(self._sprite, position.to_tuple())

         def handle_click(self, position: Position) -> None:
             # Delegate to ViewModel
             self.view_model.commands["select"].execute()
     ```

### 3. MVVM Benefits for Game Development

1. **Separation of Concerns**:
   - Game logic isolated from presentation
   - UI can be changed without affecting game rules
   - Easier to test each component independently

2. **State Management**:
   - Clear data flow
   - Predictable state updates
   - Easy to implement save/load functionality

3. **Testability**:
   - Models: Pure business logic tests
   - ViewModels: State transformation tests
   - Views: UI interaction tests

### 4. Implementation Guidelines

1. **Data Flow**:
   ```
   User Input → View → ViewModel → Model
   Model → ViewModel → View → Display
   ```

2. **Communication Patterns**:
   - Views observe ViewModels
   - ViewModels transform Model data
   - Models are pure data and logic

3. **State Updates**:
   ```python
   # Example of state propagation
   class GameViewModel:
       def __init__(self, game_model: GameModel) -> None:
           self._model = game_model
           self._observers: List[Observer] = []
           self.game_state = self._transform_state()

       def update(self) -> None:
           # Transform model state for view consumption
           self.game_state = self._transform_state()
           self._notify_observers()

       def _transform_state(self) -> GameViewState:
           return GameViewState(
               units=self._transform_units(),
               resources=self._transform_resources(),
               current_phase=self._transform_phase()
           )
   ```

4. **Command Pattern Integration**:
   ```python
   class Command:
       def __init__(self, execute_func: Callable[[], None]) -> None:
           self._execute = execute_func

       def execute(self) -> None:
           self._execute()

   class UnitCommands:
       def __init__(self, view_model: UnitViewModel) -> None:
           self.move = Command(view_model.handle_move)
           self.attack = Command(view_model.handle_attack)
           self.defend = Command(view_model.handle_defend)
   ```

### 5. Testing Strategy

1. **Model Tests**:
   ```python
   def test_unit_movement():
       unit = GameUnit("unit1", Position(0, 0))
       unit.move(Position(1, 1))
       assert unit.position == Position(1, 1)
   ```

2. **ViewModel Tests**:
   ```python
   def test_position_transformation():
       unit = GameUnit("unit1", Position(1, 1))
       vm = GameUnitViewModel(unit)
       assert vm.position == DisplayPosition(32, 32)  # TILE_SIZE = 32
   ```

3. **View Tests**:
   ```python
   def test_click_handling():
       vm = GameUnitViewModel(mock_unit)
       view = UnitView(vm)
       view.handle_click(Position(10, 10))
       assert vm.selected  # Verify ViewModel state updated
   ```

---
This is a living document and will be updated as the project evolves. All changes to this guide must be explicitly approved.

## Architecture: MVVM with Flask and Browser Frontend

### 1. Distributed MVVM Architecture
```
Project Structure
├── Backend (Flask)
│   ├── Models/
│   │   ├── game_state.py        # Core game state and logic
│   │   ├── entities.py          # Game entities
│   │   └── persistence.py       # Database models
│   ├── ViewModels/
│   │   ├── state_transformer.py # Transform game state for API
│   │   ├── command_handler.py   # Process incoming commands
│   │   └── websocket_manager.py # Real-time state updates
│   └── Routes/
│       ├── api_routes.py        # REST endpoints
│       ├── websocket_routes.py  # WebSocket endpoints
│       └── view_routes.py       # Server-side rendered views
└── Frontend (Browser)
    ├── Models/
    │   ├── game_state.js        # Client-side state management
    │   └── entities.js          # Client-side entity models
    ├── ViewModels/
    │   ├── state_manager.js     # Manage UI state
    │   ├── command_sender.js    # Send commands to backend
    │   └── websocket_client.js  # Handle real-time updates
    └── Views/
        ├── components/          # UI components
        ├── templates/           # HTML templates
        └── static/             # CSS, images, etc.
```

### 2. Communication Flow
```
Browser (View) ←→ Frontend (ViewModel) ←→ API/WebSocket ←→ Backend (ViewModel) ←→ Backend (Model)
```

### 3. Implementation Examples

1. **Backend Model**:
   ```python
   from dataclasses import dataclass
   from typing import Dict, List, Optional

   @dataclass
   class GameState:
       game_id: str
       players: Dict[str, Player]
       current_turn: str
       
       def process_turn(self, player_id: str, action: GameAction) -> None:
           # Pure game logic
           if self._is_valid_action(player_id, action):
               self._apply_action(action)
               self._update_turn()

   class GameStateService:
       def __init__(self) -> None:
           self._games: Dict[str, GameState] = {}
           
       def get_game_state(self, game_id: str) -> Optional[GameState]:
           return self._games.get(game_id)
```

2. **Backend ViewModel**:
   ```python
   from flask_socketio import emit
   from typing import Dict, Any

   class GameStateViewModel:
       def __init__(self, game_service: GameStateService):
           self._service = game_service
           
       def transform_game_state(self, game_id: str) -> Dict[str, Any]:
           """Transform game state for API response"""
           game = self._service.get_game_state(game_id)
           return {
               'gameId': game.game_id,
               'players': self._transform_players(game.players),
               'currentTurn': game.current_turn,
               'validActions': self._get_valid_actions(game)
           }
           
       def handle_action(self, game_id: str, action_data: Dict[str, Any]) -> None:
           """Process action from frontend"""
           game = self._service.get_game_state(game_id)
           action = self._parse_action(action_data)
           game.process_turn(action_data['playerId'], action)
           # Emit updated state to all clients
           emit('game_state_update', self.transform_game_state(game_id), room=game_id)
```

3. **Flask Routes**:
   ```python
   from flask import Blueprint, jsonify
   from flask_socketio import join_room

   game_routes = Blueprint('game', __name__)
   
   @game_routes.route('/api/game/<game_id>')
   def get_game_state(game_id: str):
       state = game_state_viewmodel.transform_game_state(game_id)
       return jsonify(state)

   @socketio.on('join_game')
   def on_join(data):
       game_id = data['gameId']
       join_room(game_id)
       state = game_state_viewmodel.transform_game_state(game_id)
       emit('game_state_update', state, room=game_id)
```

4. **Frontend ViewModel**:
   ```javascript
   class GameViewModel {
       constructor(gameId) {
           this.gameId = gameId;
           this.socket = io();
           this.state = null;
           this.observers = new Set();
           
           // Setup WebSocket listeners
           this.socket.on('game_state_update', (state) => {
               this.updateState(state);
           });
       }
       
       async initialize() {
           // Get initial state from REST API
           const response = await fetch(`/api/game/${this.gameId}`);
           const state = await response.json();
           this.updateState(state);
       }
       
       updateState(newState) {
           this.state = newState;
           this.notifyObservers();
       }
       
       sendAction(action) {
           this.socket.emit('game_action', {
               gameId: this.gameId,
               action: action
           });
       }
   }
   ```

5. **Frontend View**:
   ```javascript
   class GameView {
       constructor(viewModel) {
           this.viewModel = viewModel;
           this.viewModel.observers.add(this);
           this.setupEventListeners();
       }
       
       update() {
           // Update UI based on viewModel state
           this.renderGameBoard();
           this.updatePlayerInfo();
           this.highlightCurrentTurn();
       }
       
       setupEventListeners() {
           document.querySelector('.game-board').addEventListener('click', 
               (e) => this.handleBoardClick(e));
       }
       
       handleBoardClick(event) {
           const action = this.parseClickToAction(event);
           if (action) {
               this.viewModel.sendAction(action);
           }
       }
   }
   ```

### 4. Key Benefits of This Architecture

1. **Separation of Concerns**:
   - Backend handles game logic and state
   - Frontend handles UI and user interaction
   - ViewModels handle data transformation and communication

2. **Real-time Updates**:
   - WebSocket integration for live game state
   - Consistent state across all clients
   - Efficient updates without polling

3. **Scalability**:
   - Independent scaling of frontend and backend
   - Clear boundaries for distributed system
   - Easy to add new features without breaking existing ones

4. **Testing**:
   - Backend logic can be tested independently
   - Frontend components can be tested in isolation
   - Integration tests can verify communication flow

---
This is a living document and will be updated as the project evolves. All changes to this guide must be explicitly approved. 