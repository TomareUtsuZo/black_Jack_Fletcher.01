"""
Game state management.

This module provides centralized game state management through a singleton
GameStateManager. The manager coordinates between different subsystems:
- Time management (GameTimeController)
- Unit management (UnitManager)
- State management (GameStateMachine)
"""

from typing import Dict, Optional, List, Any, ClassVar, Final, Literal, Callable
from enum import Enum, auto
from dataclasses import dataclass, field
from .common.time import GameTime, GameDuration, GameTimeManager  # Core time value objects
from .common.time.game_scheduler import GameScheduler  # Real-time tick scheduler (used by controller)

from .units.types.unit_type import UnitType  # Enum/type for unit categories
from src.backend.models.units.unit_interface import UnitInterface  # Protocol for units consumed by managers
from src.backend.models.common.time.time_interface import TimeInterface  # Protocol for time-like objects
import logging

from .game.state_machine import GameState, GameStateMachine  # State rules and transitions

# Re-export for compatibility with tests and external imports
__all__ = [
    "GameStateManager",
    "GameState",
]

from .game.dto import (
    PositionDict,  # JSON-friendly coordinate DTO
    UnitInitialState,  # DTO for initial unit setup
    MovementOrders,  # DTO for movement commands
    TargetingParameters,  # DTO for targeting intent
)
"""
Design notes: DTOs at the boundary
- This module accepts JSON-friendly data transfer objects (DTOs) for inputs
  that naturally originate outside the domain layer (e.g., API payloads,
  WebSocket messages, test fixtures). See `src.backend.models.game.dto`:
  - PositionDict: {"x": float, "y": float}
  - UnitInitialState: initial unit setup data
  - MovementOrders: waypoints + speed
  - TargetingParameters: target identifier + priority

- Purpose: Keep GSM orchestration-only. GSM owns sequencing (time, unit
  ticks, state transitions), not the mechanics of movement/attack. DTOs
  allow GSM's public API to be simple, JSON-serializable, and stable across
  layers.

- Conversion: Convert DTOs to domain objects at the appropriate layer:
  - API/controllers: parse request JSON → DTO → domain types when calling
    deeper subsystems.
  - Movement/Attack subsystems: consume domain types (e.g., Position,
    NauticalMiles) — do not depend on DTOs.

- Outputs: When emitting data to clients, serialize domain objects at the
  API/serialization layer (e.g., Position.to_dict()). GSM itself does not
  perform serialization.
  """
 

from .game.time_controller import GameTimeController  # Time rate and scheduler orchestration

from .game.unit_manager import UnitManager  # Registry and per-tick iteration of units

@dataclass
class GameStateManager:
    """
    Singleton manager coordinating game subsystems.
    
    This class:
    - Maintains the single source of truth for game state
    - Coordinates between different subsystems
    - Provides a unified interface for game operations
    
    Time Management Design:
    The time management system uses a layered approach:
    1. GameTimeManager (lowest): Basic time tracking and validation
    2. GameTimeController (middle): Time rate control and scheduling
    3. GameStateManager (highest): System coordination and state management
    
    This layered design allows for:
    - Simple usage: Just create GameStateManager() and everything works
    - Testing: Inject a mock time manager for controlled testing
    - Advanced: Share time manager between multiple systems if needed
    - Clean separation: Each layer has a single responsibility
    """
    # Optional time manager injection for testing or advanced usage
    # If None (default), GameTimeController will create its own GameTimeManager
    time_manager: Optional[GameTimeManager] = field(default=None)
    
    # Error messages
    ERROR_ALREADY_INSTANTIATED: Final[str] = "GameStateManager already instantiated"
    
    # Time rate constants (for backward compatibility with tests)
    DEFAULT_TIME_RATE: Final[GameDuration] = GameTimeController.DEFAULT_TIME_RATE
    MIN_TIME_RATE: Final[GameDuration] = GameTimeController.MIN_TIME_RATE
    MAX_TIME_RATE: Final[GameDuration] = GameTimeController.MAX_TIME_RATE
    
    # Singleton instance
    _instance: ClassVar[Optional['GameStateManager']] = None
    
    # Subsystems - initialized in __post_init__
    # Each subsystem is created in a specific order to maintain dependencies
    _state_machine: GameStateMachine = field(init=False)
    _time_controller: GameTimeController = field(init=False)
    _unit_manager: UnitManager = field(init=False)
    
    def __post_init__(self) -> None:
        """
        Initialize after dataclass fields are set.
        
        The initialization order is important:
        1. State machine (no dependencies)
        2. Time controller (optional time_manager dependency)
        3. Unit manager (depends on time being available)
        """
        if GameStateManager._instance is not None:
            raise RuntimeError(self.ERROR_ALREADY_INSTANTIATED)
            
        # Initialize subsystems in dependency order
        self._state_machine = GameStateMachine()
        self._time_controller = GameTimeController(self.time_manager)
        self._unit_manager = UnitManager()
        
        GameStateManager._instance = self
    
    @classmethod
    def get_instance(cls) -> 'GameStateManager':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def start(self) -> None:
        """Start the game."""
        self._state_machine.start_game()
        self._time_controller.start_scheduler(self.tick)
    
    def stop(self) -> None:
        """Stop the game (idempotent).

        Always stops the scheduler and asks the state machine to complete.
        The state machine handles redundant transitions internally.
        """
        self._time_controller.stop_scheduler()
        self._state_machine.complete()
    
    def pause(self) -> None:
        """Pause the game."""
        self._state_machine.pause()
    
    def unpause(self) -> None:
        """Unpause the game."""
        self._state_machine.unpause()
    
    def _handle_time_limit_reached(self, error: ValueError) -> None:
        """Handle time limit reached error."""
        self.stop()
    
    def tick(self) -> None:
        """
        Process one game tick.
        
        This orchestrates:
        1. State validation
        2. Time advancement
        3. Unit updates
        """
        # Log a message for each game tick to indicate it has occurred
        print(f"Game tick occurred at {self.current_time}")
        if not self._state_machine.can_process_tick():
            return
        
        try:
            self._time_controller.advance_time()
            self._unit_manager.update_unit_states()
        except ValueError as e:
            self._handle_time_limit_reached(e)
    
    # Delegate unit operations to UnitManager
    def add_unit(self, unit_type: UnitType, initial_state: UnitInitialState) -> str:
        """Add a new unit.

        Currently not implemented at the GSM layer. Unit creation and wiring
        will be handled via a unit factory and registered into the UnitManager.
        """
        raise NotImplementedError
    
    def remove_unit(self, unit_id: str) -> None:
        """Remove a unit."""
        self._unit_manager.remove_unit(unit_id)
    
    def get_unit(self, unit_id: str) -> Optional[UnitInterface]:
        """Get a unit by ID."""
        return self._unit_manager.get_unit(unit_id)
    
    def get_all_units(self) -> List[UnitInterface]:
        """Get all units."""
        return self._unit_manager.get_all_units()
    
    # Delegate time operations to TimeController
    @property
    def current_time(self) -> GameTime:
        """Get current game time."""
        return self._time_controller.current_time
    
    @property
    def time_rate(self) -> GameDuration:
        """Get current time rate."""
        return self._time_controller.time_rate
    
    def set_time_rate(self, new_rate: GameDuration) -> None:
        """Set new time rate."""
        self._time_controller.set_time_rate(new_rate)
    
    def set_time_rate_seconds(self, seconds_per_tick: float) -> None:
        """Set time rate in seconds per tick."""
        self._time_controller.set_time_rate_seconds(seconds_per_tick)
    
    def set_time_rate_minutes(self, minutes_per_tick: float) -> None:
        """Set time rate in minutes per tick."""
        self._time_controller.set_time_rate_minutes(minutes_per_tick)
    
    # State queries and access
    @property
    def game_state(self) -> GameState:
        """Get current game state."""
        return self._state_machine.current_state
    
    @property
    def is_paused(self) -> bool:
        """Check if game is paused."""
        return self._state_machine.is_paused
    
    @property
    def _state(self) -> GameState:
        """Direct state access for testing."""
        return self._state_machine.current_state
    
    @_state.setter
    def _state(self, value: GameState) -> None:
        """Direct state setting for testing."""
        self._state_machine._state = value
    
    def set_unit_movement(self, unit_id: str, movement_orders: MovementOrders) -> None:
        """
        Set movement orders for a unit.
        
        Args:
            unit_id: ID of the unit to move
            movement_orders: Movement parameters and waypoints
        """
        # TODO: Implement movement order logic
        raise NotImplementedError
    
    def set_unit_targeting(self, unit_id: str, targeting_params: TargetingParameters) -> None:
        """
        Set targeting parameters for a unit.
        
        Args:
            unit_id: ID of the unit
            targeting_params: Targeting priorities and parameters
        """
        # TODO: Implement targeting logic
        raise NotImplementedError
    
    