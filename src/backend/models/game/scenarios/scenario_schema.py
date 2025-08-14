"""DTOs describing scenario files.

These are transport-layer shapes for YAML/JSON scenarios. Convert to domain
objects (Position, UnitType, NauticalMiles, etc.) at load time.
"""

from typing import TypedDict, List, Optional


class ScenarioUnitDTO(TypedDict, total=False):
    """Unit entry in a scenario file (JSON/YAML).

    Fields are intentionally permissive (total=False) to allow progressive
    enrichment while keeping loaders tolerant and self-explanatory.
    """

    name: str
    hull_number: str
    unit_type: str
    task_force_assigned_to: Optional[str]
    ship_class: str
    faction: str
    position: dict  # {x: float, y: float}
    destination: Optional[dict]
    max_speed: float
    cruise_speed: float
    current_speed: float
    max_health: float
    current_health: float
    max_fuel: float
    current_fuel: float
    crew: int
    tonnage: int
    visual_range: float
    visual_detection_rate: float


class ScenarioDTO(TypedDict, total=False):
    """Scenario file root DTO (JSON/YAML)."""

    name: str
    description: str
    time: dict
    units: List[ScenarioUnitDTO]


