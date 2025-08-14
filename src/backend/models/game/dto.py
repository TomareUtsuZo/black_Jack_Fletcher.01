"""Game-level DTOs (transport shapes) used at API/test boundaries.

These types are JSON-friendly and should be converted to domain objects
(`Position`, `NauticalMiles`, etc.) at the system boundary.
"""

from typing import TypedDict, List

__all__ = [
    "PositionDict",
    "UnitInitialState",
    "MovementOrders",
    "TargetingParameters",
]


class PositionDict(TypedDict):
    """JSON-friendly position shape used at API/test boundaries.

    Fields:
    - x: float — X coordinate in world/game units
    - y: float — Y coordinate in world/game units

    Note:
    - This is a DTO shape. Internal systems should convert this to
      `src.backend.models.common.geometry.position.Position`.
    """

    x: float
    y: float


class UnitInitialState(TypedDict):
    """Startup parameters for creating/registering a unit (DTO layer).

    Fields:
    - position: PositionDict — world coordinates as floats (x, y)
    - orientation: float — initial heading in degrees [0, 360)

    Intent:
    - Keep this JSON-serializable for external inputs/tests.
    - Convert to domain objects (e.g., `Position`) inside unit creation.
    """

    position: PositionDict
    orientation: float


class MovementOrders(TypedDict):
    """Movement orders for a unit (DTO layer).

    Fields:
    - waypoints: List[PositionDict] — ordered path in world coordinates (x, y)
    - speed: float — desired speed in knots (nautical miles per hour)

    Intent:
    - Keep JSON-serializable for API/tests.
    - Convert to domain types (e.g., `Position`, `NauticalMiles`) inside the movement layer.
    - Waypoints are absolute positions; heading is computed by movement logic per segment.
    """

    waypoints: List[PositionDict]
    speed: float


class TargetingParameters(TypedDict):
    """Targeting configuration for a unit (DTO layer).

    Fields:
    - target_id: str — identifier of the target unit (stringified UUID returned by unit registration)
    - priority: int — targeting priority as an integer (policy-defined; higher means more urgent unless specified otherwise)

    Intent:
    - Keep JSON-serializable for API/tests.
    - The movement/attack subsystems interpret priority consistently with game rules.
    - `target_id` should match the unit ID keys used by `UnitManager`.
    """

    target_id: str
    priority: int


