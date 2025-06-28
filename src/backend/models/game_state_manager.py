"""
Game state management.

This module provides centralized game state management through a singleton GameStateManager.
The manager is responsible for:
- Maintaining the single source of truth for game state
- Managing game time progression
- Managing all game units and their states
- Coordinating updates and state changes
"""

from typing import Dict, Optional, List, Any, ClassVar, TypedDict, Final, Literal
from enum import Enum, auto
from dataclasses import dataclass, field
from .common.time import GameTime, GameDuration, GameTimeManager
from .common.time.game_scheduler import GameScheduler
from .units.unit import Unit
from .units.types.unit_type import UnitType

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
class GameStateManager:
    """
    Singleton manager for game state.
    
    This class is responsible for:
    - Maintaining the single source of truth for game state
    - Managing game time and time progression
    - Managing all units and their states
    - Processing game events and updates
    
    The manager enforces singleton pattern - only one instance can exist.
    Use GameStateManager.get_instance() to access the manager.
    """
    # Private init fields
    _time_manager: GameTimeManager
    _time_rate: GameDuration
    _units: Dict[str, Unit]
    _state: GameState
    _scheduler: GameScheduler
    
    # Singleton instance
    _instance: ClassVar[Optional['GameStateManager']] = None
    
    # Constants for time rate bounds
    DEFAULT_TIME_RATE: Final[GameDuration] = GameDuration.from_minutes(1)  # 1 minute per tick
    TICK_INTERVAL: Final[float] = 1.0  # 1 second between ticks
    MIN_TIME_RATE: Final[GameDuration] = GameDuration.from_seconds(1)  # Min 1 second per tick
    MAX_TIME_RATE: Final[GameDuration] = GameDuration.from_hours(1)  # Max 1 hour per tick
    
    def __init__(self, time_manager: Optional[GameTimeManager] = None) -> None:
        """
        Initialize the manager.
        
        Args:
            time_manager: Optional GameTimeManager instance. If None, creates a new one.
        """
        if GameStateManager._instance is not None:
            raise RuntimeError("GameStateManager already instantiated")
        
        # Initialize all fields
        print("\nInitializing GameStateManager...")
        self._time_manager = time_manager if time_manager is not None else GameTimeManager()
        print(f"Initial game time set to: {self._time_manager.time_now.to_datetime().isoformat()}")
        
        self._time_rate = self.DEFAULT_TIME_RATE
        print(f"Default time rate set to: {self._time_rate.minutes} minutes per tick")
        
        self._units = {}
        self._state = GameState.INITIALIZING
        self._scheduler = GameScheduler(tick_delay=1.0)  # 1 second between ticks
        
        GameStateManager._instance = self
        
    def start(self) -> None:
        """Start the game."""
        if self._state != GameState.INITIALIZING:
            raise RuntimeError("Game can only be started from INITIALIZING state")
            
        print("\nStarting game...")
        print(f"Starting time: {self._time_manager.time_now.to_datetime().isoformat()}")
        print(f"Time rate: {self._time_rate.minutes} minutes per tick")
            
        self._state = GameState.RUNNING
        self._scheduler.start(self.tick)
    
    @classmethod
    def get_instance(cls) -> 'GameStateManager':
        """
        Get the singleton instance of the manager.
        
        Creates the instance if it doesn't exist.
        
        Returns:
            The singleton GameStateManager instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    def current_time(self) -> GameTime:
        """
        Get the current game time.
        
        Returns:
            Current point in game time
        """
        return self._time_manager.time_now
    
    @property
    def time_rate(self) -> GameDuration:
        """
        Get the current time rate.
        
        Returns:
            Current time advancement rate per tick as a GameDuration
        """
        return self._time_rate
    
    @property
    def is_paused(self) -> bool:
        """Check if the game is paused."""
        return self._state == GameState.PAUSED
    
    @property
    def game_state(self) -> GameState:
        """Get the current game state."""
        return self._state
    
    def set_time_rate(self, new_rate: GameDuration) -> None:
        """
        Set a new time progression rate.
        
        This determines how much game time advances per real-time tick.
        For example:
        - set_time_rate(GameDuration.from_seconds(1)) -> 1 game second per tick
        - set_time_rate(GameDuration.from_minutes(1)) -> 1 game minute per tick
        
        Args:
            new_rate: How much game time should advance per tick
            
        Raises:
            ValueError: If new_rate is outside allowed range
        """
        if new_rate < self.MIN_TIME_RATE or new_rate > self.MAX_TIME_RATE:
            raise ValueError(
                f"Time rate must be between {self.MIN_TIME_RATE.seconds} seconds and "
                f"{self.MAX_TIME_RATE.seconds} seconds per tick"
            )
        self._time_rate = new_rate
    
    def set_time_rate_seconds(self, seconds_per_tick: float) -> None:
        """
        Set time rate in seconds per tick.
        
        Convenience method for setting time rate using seconds.
        
        Args:
            seconds_per_tick: Number of game seconds that should pass per tick
            
        Raises:
            ValueError: If rate is outside allowed range
        """
        self.set_time_rate(GameDuration.from_seconds(seconds_per_tick))
    
    def set_time_rate_minutes(self, minutes_per_tick: float) -> None:
        """
        Set time rate in minutes per tick.
        
        Convenience method for setting time rate using minutes.
        
        Args:
            minutes_per_tick: Number of game minutes that should pass per tick
            
        Raises:
            ValueError: If rate is outside allowed range
        """
        self.set_time_rate(GameDuration.from_minutes(minutes_per_tick))
    
    @property
    def time_rate_seconds(self) -> float:
        """Get the current time rate in seconds per tick."""
        return self._time_rate.seconds
    
    @property
    def time_rate_minutes(self) -> float:
        """Get the current time rate in minutes per tick."""
        return self._time_rate.minutes
    
    def stop(self) -> None:
        """
        Stop the game state manager.
        
        This will:
        1. Stop the scheduler
        2. Set the game state to COMPLETED
        """
        if self._state == GameState.COMPLETED:
            return
            
        self._scheduler.stop()
        self._state = GameState.COMPLETED
    
    def pause(self) -> None:
        """
        Pause the game.
        
        This will:
        1. Set the game state to PAUSED
        2. Prevent tick updates from processing
        """
        if self._state == GameState.RUNNING:
            self._state = GameState.PAUSED
    
    def unpause(self) -> None:
        """
        Unpause the game.
        
        This will:
        1. Set the game state to RUNNING
        2. Resume time progression
        
        Raises:
            RuntimeError: If game is not in PAUSED state
        """
        if self._state != GameState.PAUSED:
            raise RuntimeError("Game is not paused")
        self._state = GameState.RUNNING
    
    def tick(self) -> None:
        """
        Advance the game state by one tick.
        
        This:
        1. Checks if game is paused or not running
        2. If game is running:
           a. Advances game time by the current time rate
           b. Processes any pending events/orders
           c. Updates all unit states
        """
        if self._state != GameState.RUNNING:
            return
            
        try:
            # Advance game time
            new_time = self._time_manager.advance_time(self._time_rate)
            print(f"Tick - Game time: {new_time.to_datetime().isoformat()}")
            
            # TODO: Process events and update units
            # For now, just advance time
            
        except ValueError as e:
            # Handle case where time advancement would exceed game bounds
            print(f"\nGame time limit reached: {e}")
            print(f"Final game time: {self._time_manager.time_now.to_datetime().isoformat()}")
            self._state = GameState.COMPLETED
            self._scheduler.stop()  # Stop the scheduler when game is completed
    
    def add_unit(self, unit_type: UnitType, initial_state: UnitInitialState) -> str:
        """
        Add a new unit to the game state.
        
        Args:
            unit_type: The type of unit to create
            initial_state: Initial state values for the unit
            
        Returns:
            The ID of the newly created unit
        """
        # TODO: Implement unit creation logic
        raise NotImplementedError
    
    def remove_unit(self, unit_id: str) -> None:
        """
        Remove a unit from the game state.
        
        Args:
            unit_id: ID of the unit to remove
        """
        # TODO: Implement unit removal logic
        raise NotImplementedError
    
    def get_unit(self, unit_id: str) -> Optional[Unit]:
        """
        Get a unit by its ID.
        
        Args:
            unit_id: ID of the unit to get
            
        Returns:
            The unit if found, None otherwise
        """
        return self._units.get(unit_id)
    
    def get_all_units(self) -> List[Unit]:
        """
        Get all units in the game state.
        
        Returns:
            List of all units
        """
        return list(self._units.values())
    
    def update_unit_state(self, unit_id: str, state_changes: Dict[str, Any]) -> None:
        """
        Update a unit's state.
        
        Args:
            unit_id: ID of the unit to update
            state_changes: Dictionary of state changes to apply
        """
        # TODO: Implement unit state update logic
        raise NotImplementedError
    
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