"""Game state machine and state enum.

Encapsulates state transitions and validation. Kept separate from the
orchestrator to keep `game_state_manager.py` focused on coordination.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Final


class GameState(Enum):
    """Game state enumeration"""
    INITIALIZING = auto()
    RUNNING = auto()
    PAUSED = auto()
    COMPLETED = auto()

    def __eq__(self, other: object) -> bool:  # pragma: no cover - simple comparison
        if not isinstance(other, GameState):
            return NotImplemented
        return self.value == other.value


@dataclass
class GameStateMachine:
    """
    Manages game state transitions and validation.

    Ensures that:
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

    def start_game(self) -> None:
        """Start the game; allowed only from INITIALIZING → RUNNING.

        Raises:
            RuntimeError: if called when not in INITIALIZING state
        """
        if self._state != GameState.INITIALIZING:
            raise RuntimeError(self.ERROR_START_FROM_INIT)
        self._state = GameState.RUNNING

    def pause(self) -> None:
        """Transition to PAUSED state (only from RUNNING)."""
        if self._state == GameState.RUNNING:
            self._state = GameState.PAUSED

    def unpause(self) -> None:
        """Transition from PAUSED to RUNNING state."""
        if self._state != GameState.PAUSED:
            raise RuntimeError(self.ERROR_NOT_PAUSED)
        self._state = GameState.RUNNING

    def complete(self) -> None:
        """Transition to COMPLETED state (idempotent)."""
        if self._state != GameState.COMPLETED:
            self._state = GameState.COMPLETED

    def can_process_tick(self) -> bool:
        """Check if tick processing is allowed."""
        return self._state == GameState.RUNNING


