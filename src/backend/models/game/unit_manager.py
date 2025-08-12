"""Unit registry and tick coordination for units.

Provides creation/registration hooks and iteration for per-tick updates.
Separated from the orchestrator to keep `game_state_manager.py` focused on
coordination and API surface.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List

from ..units.unit_interface import UnitInterface
from .dto import UnitInitialState


@dataclass
class UnitManager:
    """
    Manages game units and their states.

    Responsibilities:
    - Unit creation and removal (registration lifecycle)
    - Unit state updates per tick
    - Unit queries and lookups
    """

    _units: Dict[str, UnitInterface] = field(default_factory=dict)

    def add_unit(self, unit: UnitInterface, initial_state: UnitInitialState) -> str:
        """Register a new unit and return its ID.

        Note: actual construction/wiring should be handled by a factory; this
        method only registers and returns the ID.
        """
        unit_id = str(unit.get_unit_state()['unit_id'])
        self._units[unit_id] = unit
        return unit_id

    def remove_unit(self, unit_id: str) -> None:
        """Remove a unit (not yet implemented)."""
        # TODO: Implement unit removal (deregistration + cleanup hooks)
        raise NotImplementedError

    def get_unit(self, unit_id: str) -> Optional[UnitInterface]:
        """Get a unit by ID if present."""
        return self._units.get(unit_id)

    def get_all_units(self) -> List[UnitInterface]:
        """Return all registered units as a list."""
        return list(self._units.values())

    def update_unit_states(self) -> None:
        """Perform per-tick updates for all units (movement, detection, combat).

        Delegates to each unit's `perform_tick()` to keep concerns localized
        to the unit and its modules.
        """
        for unit in self._units.values():
            unit.perform_tick()


