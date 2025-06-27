from enum import Enum, auto

class UnitType(Enum):
    """
    Enumeration of possible unit types.
    Using auto() to automatically assign values - the actual values
    don't matter, we just need them to be unique.
    """
    DESTROYER = auto()
    CRUISER = auto()
    BATTLESHIP = auto()
    CARRIER = auto()
    FIGHTER = auto()
    DIVE_BOMBER = auto()
    TORPEDO_BOMBER = auto()
    TRANSPORT = auto()
    BASE = auto()
    # Add more unit types as needed 