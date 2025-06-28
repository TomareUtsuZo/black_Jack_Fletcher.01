"""
Game state management.

This module provides centralized game state management through a singleton GameStateManager.
The manager is responsible for:
- Maintaining the single source of truth for game state
- Managing game time progression
- Managing all game units and their states
- Coordinating updates and state changes
"""

from typing import Dict, Optional, List, Any, ClassVar, TypedDict, Final
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
    # Singleton instance
    _instance: ClassVar[Optional['GameStateManager']] = None
    
    # Private init fields
    _time_manager: GameTimeManager = field(init=False)
    _time_rate: GameDuration = field(init=False)
    _units: Dict[str, Unit] = field(default_factory=dict, init=False)
    _paused: bool = field(default=False, init=False)
    _state: GameState = field(default=GameState.INITIALIZING, init=False)
    _scheduler: GameScheduler = field(init=False)
    
    # Constants
    DEFAULT_TIME_RATE: Final[int] = 1  # 1 minutes per tick
    TICK_INTERVAL: Final[float] = 1.0  # 1 second between ticks
    
    def __post_init__(self) -> None:
        """Initialize the manager's state."""
        if GameStateManager._instance is not None:
            raise RuntimeError("GameStateManager already instantiated")
        GameStateManager._instance = self
        
        # Initialize with default values
        self._time_manager = GameTimeManager()
        self._time_rate = GameDuration.from_minutes(self.DEFAULT_TIME_RATE)
        self._scheduler = GameScheduler(tick_interval=self.TICK_INTERVAL)
    
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
        """Get the current game time."""
        return self._time_manager.time_now
    
    @property
    def time_rate(self) -> GameDuration:
        """Get the current time rate (how much time advances per tick)."""
        return self._time_rate
    
    @property
    def is_paused(self) -> bool:
        """Check if the game is paused."""
        return self._paused
    
    @property
    def game_state(self) -> GameState:
        """Get the current game state."""
        return self._state
    
    def set_time_rate(self, new_rate: GameDuration) -> None:
        """
        Set a new time progression rate.
        
        Args:
            new_rate: How much game time should advance per tick
        """
        # TODO: Implement time rate change logic
        raise NotImplementedError
    
    def start(self) -> None:
        """
        Start the game state manager.
        
        This will:
        1. Set the game state to RUNNING
        2. Start the scheduler to trigger regular ticks
        """
        if self._state != GameState.INITIALIZING:
            raise RuntimeError("Game is already started")
            
        self._state = GameState.RUNNING
        self._paused = False
        self._scheduler.start(tick_handler=self.tick)
    
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
            self._paused = True
            self._state = GameState.PAUSED
    
    def unpause(self) -> None:
        """
        Resume the game.
        
        This will:
        1. Set the game state to RUNNING
        2. Allow tick updates to process
        """
        if self._state == GameState.PAUSED:
            self._paused = False
            self._state = GameState.RUNNING
    
    def tick(self) -> None:
        """
        Advance the game state by one tick.
        
        This:
        1. Checks if game is paused
        2. If not paused:
           a. Advances game time by the current time rate
           b. Processes any pending events/orders
           c. Updates all unit states
        """
        if self._state != GameState.RUNNING or self._paused:
            return
            
        # TODO: Implement tick logic
        raise NotImplementedError
    
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