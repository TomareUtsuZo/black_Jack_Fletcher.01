import uuid
from dataclasses import dataclass
from typing import List, Optional, Dict
from .units.test_ships import TEST_SHIPS, ShipSpecification  # Import existing ships
from .common.geometry.position import Position
from .common.geometry.nautical_miles import NauticalMiles  # If needed for calculations
import math

@dataclass(frozen=True)
class Scenario:
    """
    Represents a game scenario, including ships and map area.
    """
    scenario_id: uuid.UUID  # Unique ID for the scenario
    name: str  # Name of the scenario (e.g., 'Default Test Scenario')
    ships: List[ShipSpecification]  # List of ships in the scenario
    center_position: Position  # Center point of the map (e.g., Midway)
    map_extension_nm: float  # Extension in nautical miles (e.g., 1000 NM in each direction)

    # Method to calculate map boundaries
    def get_map_boundaries(self) -> Dict[str, Position]:
        # Simple calculation: Extend 1000 NM N, S, E, W from center
        # Note: This is a basic implementation; actual calculations might need to account for Earth's curvature.
        return {
            'north': Position(x=self.center_position.x, y=self.center_position.y + self.map_extension_nm / 60),  # Latitude change (1 degree ≈ 60 NM)
            'south': Position(x=self.center_position.x, y=self.center_position.y - self.map_extension_nm / 60),
            'east': Position(x=self.center_position.x + self.map_extension_nm / (60 * math.cos(math.radians(self.center_position.y))), y=self.center_position.y),  # Longitude change adjusted for latitude
            'west': Position(x=self.center_position.x - self.map_extension_nm / (60 * math.cos(math.radians(self.center_position.y))), y=self.center_position.y)
        }

    # Static method to create a default scenario
    @staticmethod
    def create_default_scenario() -> 'Scenario':
        return Scenario(
            scenario_id=uuid.uuid4(),
            name='Default Test Scenario',
            ships=list(TEST_SHIPS.values()),  # Load existing test ships
            center_position=Position(x=-177.35, y=28.2),  # Midway coordinates
            map_extension_nm=1000.0  # 1000 NM extension
        ) 