"""
Test ship definitions.

This module defines specific test ships with historically accurate specifications.
These ships serve as reference implementations for the ship factory.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from .types.unit_type import UnitType
from ..common.geometry.nautical_miles import NauticalMiles
from uuid import UUID, uuid4
from typing import Optional
from ..common.geometry.position import Position

@dataclass(frozen=True)
class ShipSpecification:
    """
    Complete specification for a ship.
    All values should be historically accurate.
    """
    # Identity
    unit_id: UUID  # Unique identifier for the ship
    name: str  # Full name of the ship
    hull_number: str  # Hull number in proper naval format
    unit_type: UnitType
    task_force_assigned_to: Optional[str]  # Could be UUID if TaskForce gets its own type
    ship_class: str  # Class of the ship
    faction: str  # Faction of the ship

    # Position and Movement
    position: Position
    destination: Optional[Position]
    max_speed: NauticalMiles  # Maximum speed in knots (nautical miles per hour)
    cruise_speed: NauticalMiles  # Economical cruising speed in knots
    current_speed: NauticalMiles  # Current speed in knots
    
    # Resources
    max_health: float
    current_health: float
    max_fuel: float
    current_fuel: float
    crew: int  # Standard complement (probably not relevant, but good for stories)
    tonnage: int  # Tonnage of the ship (probably not relevant, but good for stories)

    # Detection
    visual_range: NauticalMiles  # Range for visual detection in nautical miles
    visual_detection_rate: float  # Probability rate for visual detection (e.g., 0.0 to 1.0)

# Test Ships - Using real Fletcher-class destroyers and other historical ships as examples

# Midway position: approximately 177.35°W, 28.2°N
# We'll place ships within 10nm of this point
MIDWAY_X = -177.35  # West longitude is negative
MIDWAY_Y = 28.2

USS_FLETCHER = ShipSpecification(
    unit_id=uuid4(),
    name="USS Fletcher",
    hull_number="DD-445",
    unit_type=UnitType.DESTROYER,
    task_force_assigned_to=None,
    ship_class="Fletcher",
    faction="USN",
    position=Position(x=MIDWAY_X + 0.1, y=MIDWAY_Y + 0.05),  # ~5-6nm ENE of Midway
    destination=None,
    max_speed=NauticalMiles(36.5),  # Max speed achieved during trials
    cruise_speed=NauticalMiles(15.0),  # Economic cruise speed
    current_speed=NauticalMiles(0.0),  # Start stationary
    max_health=100.0,
    current_health=100.0,  # Start at full health
    max_fuel=5500.0,  # Range at 15 knots
    current_fuel=5500.0,  # Start with full fuel
    crew=273,  # Standard complement
    tonnage=2100,  # Updated to integer
    visual_range=NauticalMiles(5),
    visual_detection_rate=0.8,
)

USS_TALEN = ShipSpecification(
    unit_id=uuid4(),
    name="USS Talen",
    hull_number="DD-666",
    unit_type=UnitType.DESTROYER,
    task_force_assigned_to=None,
    ship_class="Fletcher",
    faction="USN",
    position=Position(x=MIDWAY_X - 0.08, y=MIDWAY_Y + 0.07),  # ~7nm NW of Midway
    destination=None,
    max_speed=NauticalMiles(36.5),
    cruise_speed=NauticalMiles(15.0),
    current_speed=NauticalMiles(0.0),
    max_health=100.0,
    current_health=100.0,
    max_fuel=5500.0,
    current_fuel=5500.0,
    crew=273,
    tonnage=2100,  # Updated to integer
    visual_range=NauticalMiles(5),
    visual_detection_rate=0.8,
)

# IJN Yukikaze - Kagero-class destroyer
IJN_YUKIKAZE = ShipSpecification(
    unit_id=uuid4(),
    name="IJN Yukikaze",
    hull_number="DD-516",  # Historical hull number
    unit_type=UnitType.DESTROYER,
    task_force_assigned_to=None,
    ship_class="Kagero",
    faction="IJN",
    position=Position(x=MIDWAY_X - 0.12, y=MIDWAY_Y - 0.06),  # ~8nm SW of Midway
    destination=None,
    max_speed=NauticalMiles(35.5),  # Historical max speed
    cruise_speed=NauticalMiles(18.0),  # Historical cruise speed
    current_speed=NauticalMiles(0.0),
    max_health=100.0,
    current_health=100.0,
    max_fuel=5000.0,  # Historical range at 18 knots
    current_fuel=5000.0,
    crew=240,  # Historical crew complement
    tonnage=2033,  # Updated to integer
    visual_range=NauticalMiles(6),  # Adjusted slightly for historical accuracy if needed
    visual_detection_rate=0.7,
)

# Fictional pirate ship based on historical pirate vessels
PIRATE_QUEEN = ShipSpecification(
    unit_id=uuid4(),
    name="Queen Anne's Revenge II",  # Named after Blackbeard's famous ship
    hull_number="PRV-001",  # Pirate Vessel designation
    unit_type=UnitType.DESTROYER,  # Using destroyer type for game mechanics
    task_force_assigned_to=None,
    ship_class="Privateer",
    faction="UNALIGNED",
    position=Position(x=MIDWAY_X + 0.06, y=MIDWAY_Y - 0.08),  # ~6nm SE of Midway
    destination=None,
    max_speed=NauticalMiles(28.0),  # Fast for a pirate vessel
    cruise_speed=NauticalMiles(12.0),
    current_speed=NauticalMiles(0.0),
    max_health=80.0,  # Less armored than military vessels
    current_health=80.0,
    max_fuel=3000.0,  # Smaller fuel capacity
    current_fuel=3000.0,
    crew=150,  # Typical pirate crew size
    tonnage=1500,  # Updated to integer
    visual_range=NauticalMiles(4),  # Lower for a fictional pirate ship
    visual_detection_rate=0.6,
)

# Dictionary of all test ships for easy lookup
TEST_SHIPS: Dict[str, ShipSpecification] = {
    "DD-445": USS_FLETCHER,
    "DD-666": USS_TALEN,
    "DD-516": IJN_YUKIKAZE,
    "PRV-001": PIRATE_QUEEN
}

def get_test_ship(hull_number: str) -> Optional[ShipSpecification]:
    """
    Get a test ship by hull number.
    
    Args:
        hull_number: The hull number of the ship to retrieve
        
    Returns:
        The ship specification if found, None otherwise
    """
    return TEST_SHIPS.get(hull_number)

def get_fletcher_class_ships() -> List[ShipSpecification]:
    """
    Get all Fletcher-class test ships.
    
    Returns:
        List of Fletcher-class ship specifications
    """
    return [ship for ship in TEST_SHIPS.values() if ship.ship_class == "Fletcher"]

def get_kagero_class_ships() -> List[ShipSpecification]:
    """
    Get all Kagero-class test ships.
    
    Returns:
        List of Kagero-class ship specifications
    """
    return [ship for ship in TEST_SHIPS.values() if ship.ship_class == "Kagero"]

def get_ship_by_hull_number(hull_number: str) -> Optional[ShipSpecification]:
    """
    Get a ship by hull number.
    
    Args:
        hull_number: The hull number of the ship to retrieve
        
    Returns:
        The ship specification if found, None otherwise
    """
    return TEST_SHIPS.get(hull_number)

def get_all_test_ships() -> List[ShipSpecification]:
    """
    Get all test ships.
    
    Returns:
        List of all ship specifications
    """
    return list(TEST_SHIPS.values()) 