"""
Game state management.

This module provides centralized game state management through a singleton GameStateManager.
The manager coordinates between different subsystems:
- Time management (GameTimeController)
- Unit management (UnitManager)
- State management (GameStateMachine)
"""

from typing import Dict, Optional, List, Any, ClassVar, TypedDict, Final, Literal, Callable
from enum import Enum, auto
from dataclasses import dataclass, field
from .common.time import GameTime, GameDuration, GameTimeManager
from .common.time.game_scheduler import GameScheduler
from .units.unit import Unit
from .units.types.unit_type import UnitType
from src.backend.models.units.unit_interface import UnitInterface
from src.backend.models.common.time.time_interface import TimeInterface
import logging
import uuid

class GameState(Enum):
    """Game state enumeration"""
    INITIALIZING = auto()
    RUNNING = auto()
    PAUSED = auto()
    COMPLETED = auto()

    def __eq__(self, other: object) -> bool:
        """Compare game states."""
        if not isinstance(other, GameState):
            return NotImplemented
        return self.value == other.value

class UnitInitialState(TypedDict):
    """Type definition for unit initialization parameters"""
    # To be expanded based on requirements
    position: Dict[str, float]  # x, y coordinates
    orientation: float

class MovementOrders(TypedDict):
    """Type definition for unit movement orders"""
    # To be expanded based on requirements
    waypoints: List[Dict[str, float]]  # List of x,y coordinates
    speed: float

class TargetingParameters(TypedDict):
    """Type definition for unit targeting parameters"""
    # To be expanded based on requirements
    target_id: str
    priority: int

class DamageInfo(TypedDict):
    """Type definition for damage application"""
    # To be expanded based on requirements
    amount: float
    type: str
    source_id: str

@dataclass
class GameStateMachine:
    """
    Manages game state transitions and validation.
    
    This class ensures that:
    - State transitions are valid
    - State changes are properly logged
    - State-dependent operations are validated
    """
    _state: GameState = field(default_factory=lambda: GameState.INITIALIZING)
    
    # State transition error messages
    ERROR_START_FROM_INIT: Final[str] = "Game can only be started from INITIALIZING state"
    ERROR_NOT_PAUSED: Final[str] = "Game is not paused"
    
    @property
    def current_state(self) -> GameState:
        """Get the current game state."""
        return self._state
    
    @property
    def is_paused(self) -> bool:
        """Check if the game is paused."""
        return self._state == GameState.PAUSED
    
    def transition_to_running(self) -> None:
        """Transition to RUNNING state."""
        if self._state != GameState.INITIALIZING:
            raise RuntimeError(self.ERROR_START_FROM_INIT)
        self._state = GameState.RUNNING
    
    def pause(self) -> None:
        """Transition to PAUSED state."""
        if self._state == GameState.RUNNING:
            self._state = GameState.PAUSED
    
    def unpause(self) -> None:
        """Transition from PAUSED to RUNNING state."""
        if self._state != GameState.PAUSED:
            raise RuntimeError(self.ERROR_NOT_PAUSED)
        self._state = GameState.RUNNING
    
    def complete(self) -> None:
        """Transition to COMPLETED state."""
        if self._state != GameState.COMPLETED:
            self._state = GameState.COMPLETED
    
    def can_process_tick(self) -> bool:
        """Check if tick processing is allowed."""
        return self._state == GameState.RUNNING

@dataclass
class GameTimeController:
    """
    Controls game time progression and scheduling.
    
    This class manages:
    - Time rate configuration
    - Time advancement
    - Tick scheduling
    
    Design Pattern:
    - Acts as a higher-level controller over GameTimeManager
    - Separates time rate control from basic time tracking
    - Allows for dependency injection of time management
    """
    # The GameTimeManager can be injected for testing or advanced usage
    _init_time_manager: Optional[GameTimeManager]
    
    # Time rate constants
    DEFAULT_TIME_RATE: Final[GameDuration] = GameDuration.from_minutes(1)
    MIN_TIME_RATE: Final[GameDuration] = GameDuration.from_seconds(1)
    MAX_TIME_RATE: Final[GameDuration] = GameDuration.from_hours(1)
    
    # Scheduler configuration
    DEFAULT_TICK_DELAY: Final[float] = 1.0
    
    # Fields with defaults must come after fields without defaults
    _time_manager: GameTimeManager = field(init=False)  # Will be set in __post_init__
    _time_rate: GameDuration = field(default_factory=lambda: GameTimeController.DEFAULT_TIME_RATE)
    _scheduler: GameScheduler = field(default_factory=lambda: GameScheduler(tick_delay=GameTimeController.DEFAULT_TICK_DELAY))
    
    def __post_init__(self) -> None:
        """
        Initialize after dataclass fields are set.
        
        This ensures all fields are properly initialized before we use them.
        The _init_time_manager is either used or replaced with a new instance,
        allowing for both simple usage and testing scenarios.
        """
        # Initialize _time_manager with the stored value or create a new one
        self._time_manager = self._init_time_manager if self._init_time_manager is not None else GameTimeManager()
        
        # Clean up the temporary storage
        del self._init_time_manager
    
    @property
    def current_time(self) -> GameTime:
        """Get the current game time."""
        return self._time_manager.time_now
    
    @property
    def time_rate(self) -> GameDuration:
        """Get the current time rate."""
        return self._time_rate
    
    def set_time_rate(self, new_rate: GameDuration) -> None:
        """Set a new time progression rate."""
        if new_rate < self.MIN_TIME_RATE or new_rate > self.MAX_TIME_RATE:
            raise ValueError(
                f"Time rate must be between {self.MIN_TIME_RATE.seconds} seconds and "
                f"{self.MAX_TIME_RATE.seconds} seconds per tick"
            )
        self._time_rate = new_rate
    
    def set_time_rate_seconds(self, seconds_per_tick: float) -> None:
        """Set time rate in seconds per tick."""
        self.set_time_rate(GameDuration.from_seconds(seconds_per_tick))
    
    def set_time_rate_minutes(self, minutes_per_tick: float) -> None:
        """Set time rate in minutes per tick."""
        self.set_time_rate(GameDuration.from_minutes(minutes_per_tick))
    
    def advance_time(self) -> GameTime:
        """Advance game time by one tick."""
        return self._time_manager.advance_time(self._time_rate)
    
    def start_scheduler(self, tick_handler: Any) -> None:
        """Start the game scheduler."""
        self._scheduler.start(tick_handler)
    
    def stop_scheduler(self) -> None:
        """Stop the game scheduler."""
        self._scheduler.stop()

@dataclass
class UnitManager:
    """
    Manages game units and their states.
    
    This class handles:
    - Unit creation and removal
    - Unit state updates
    - Unit queries and lookups
    """
    _units: Dict[str, UnitInterface] = field(default_factory=dict)
    
    def add_unit(self, unit: UnitInterface, initial_state: UnitInitialState) -> str:
        """Add a new unit."""
        # TODO: Implement unit creation
        raise NotImplementedError
    
    def remove_unit(self, unit_id: str) -> None:
        """Remove a unit."""
        # TODO: Implement unit removal
        raise NotImplementedError
    
    def get_unit(self, unit_id: str) -> Optional[UnitInterface]:
        """Get a unit by ID."""
        return self._units.get(unit_id)
    
    def get_all_units(self) -> List[UnitInterface]:
        """Get all units."""
        return list(self._units.values())
    
    def update_unit_states(self) -> None:
        """Update all unit states."""
        # TODO: Implement unit state updates
        pass

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
        self._state_machine.transition_to_running()
        self._time_controller.start_scheduler(self.tick)
    
    def stop(self) -> None:
        """Stop the game."""
        if self._state_machine.current_state == GameState.COMPLETED:
            return
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
    
    def reset_state(self) -> None:
        # Self-comment: Stops the scheduler if running, then resets the game state to initial conditions
        try:
            self._time_controller.stop_scheduler()  # Self-comment: Stop the scheduler to avoid conflicts
        except Exception as e:
            logging.warning(f'Warning: Failed to stop scheduler during reset: {str(e)}')  # Self-comment: Log any issues but continue
        self._state_machine._state = GameState.INITIALIZING
        self._unit_manager._units = {}  # Clear all units
        logging.info('Game state reset to initial conditions')  # Log the reset for debugging
    
    def add_unit(self, unit_type: UnitType, initial_state: UnitInitialState) -> str:
        # Note: Keeping this method for future use, but not calling it in start_game
        try:
            new_unit = Unit(unit_type, initial_state)  # Assuming Unit is the class from units/unit.py
            unit_id = str(uuid.uuid4())  # Generate a unique ID for the unit
            self._unit_manager.add_unit(new_unit, initial_state)  # Add to the unit manager
            logging.info(f'Unit added successfully with ID: {unit_id}')  # Log success for debugging
            return unit_id
        except Exception as e:
            logging.error(f'Error adding unit: {str(e)}')  # Log any errors
            raise  # Re-raise the error for the caller to handle
    
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
    
    def apply_damage(self, unit_id: str, damage_info: DamageInfo) -> None:
        """
        Apply damage to a unit.
        
        Args:
            unit_id: ID of the unit to damage
            damage_info: Damage type and amount information
        """
        # TODO: Implement damage application logic
        raise NotImplementedError 