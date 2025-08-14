"""Game time controller and scheduler integration.

Encapsulates time rate configuration, advancement, and scheduler wiring.
Separated from the orchestrator to keep `game_state_manager.py` focused on
coordination and API surface.
"""

from dataclasses import dataclass, field
from typing import Optional, Final, Any

from ..common.time import GameTime, GameDuration, GameTimeManager
from ..common.time.game_scheduler import GameScheduler


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

    # Time rate constants (game-time advanced per tick)
    # - DEFAULT_TIME_RATE: Sensible gameplay default where each tick advances 1 in‑game minute
    # - MIN_TIME_RATE: Lower bound for very fine‑grained simulations (1 second per tick)
    # - MAX_TIME_RATE: Upper bound for time compression (1 hour per tick)
    DEFAULT_TIME_RATE: Final[GameDuration] = GameDuration.from_minutes(1)
    MIN_TIME_RATE: Final[GameDuration] = GameDuration.from_seconds(1)
    MAX_TIME_RATE: Final[GameDuration] = GameDuration.from_hours(1)

    # Scheduler configuration (real-time pacing of ticks)
    # - DEFAULT_TICK_DELAY: Real seconds between scheduler callbacks
    #   Example: 1.0 ⇒ call tick() once per real second; the amount of time advanced
    #   in game is controlled separately by _time_rate.
    DEFAULT_TICK_DELAY: Final[float] = 1.0

    # Fields with defaults must come after fields without defaults
    # - _time_manager: Source of truth for current game time; injected or created in __post_init__
    # - _time_rate: How much game time to advance on each tick (bounded by MIN/MAX)
    # - _scheduler: Calls the tick handler on a wall‑clock cadence (DEFAULT_TICK_DELAY)
    _time_manager: GameTimeManager = field(init=False)
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


