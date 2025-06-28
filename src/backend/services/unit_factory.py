"""
Unit factory service for standardized unit creation.

This service provides factory methods for creating different types of units
with standardized attributes and validation. It ensures consistent unit
creation across the codebase and handles default values appropriately.
"""

from dataclasses import dataclass
from typing import Dict, Optional, ClassVar
from uuid import UUID, uuid4

from src.backend.models.common import Position
from src.backend.models.common.geometry.nautical_miles import NauticalMiles
from src.backend.models.units import Unit
from src.backend.models.units.types import UnitType

@dataclass(frozen=True)
class UnitTemplate:
    """Standard template for unit type specifications"""
    max_speed: NauticalMiles  # Maximum speed in knots
    cruise_speed: NauticalMiles  # Economical cruise speed
    max_health: float
    max_fuel: float
    crew: int
    tonnage: float
    name_prefix: str

class UnitFactory:
    """Factory service for creating standardized units"""
    
    # Standard specifications for each unit type
    UNIT_SPECS: ClassVar[Dict[UnitType, UnitTemplate]] = {
        UnitType.DESTROYER: UnitTemplate(
            max_speed=NauticalMiles(35.0),  # Fletcher-class max speed
            cruise_speed=NauticalMiles(15.0),  # Fletcher-class cruise speed
            max_health=100.0,
            max_fuel=5500.0,  # Range at cruise speed
            crew=273,  # Fletcher-class complement
            tonnage=2100.0,  # Fletcher-class displacement
            name_prefix="DD"
        ),
        UnitType.CRUISER: UnitTemplate(
            max_speed=NauticalMiles(33.0),  # Baltimore-class max speed
            cruise_speed=NauticalMiles(15.0),  # Baltimore-class cruise speed
            max_health=150.0,
            max_fuel=1200.0,
            crew=1142,  # Baltimore-class complement
            tonnage=13600.0,  # Baltimore-class displacement
            name_prefix="CA"
        ),
        UnitType.BATTLESHIP: UnitTemplate(
            max_speed=NauticalMiles(28.0),  # Iowa-class max speed
            cruise_speed=NauticalMiles(15.0),  # Iowa-class cruise speed
            max_health=250.0,
            max_fuel=1500.0,
            crew=2788,  # Iowa-class complement
            tonnage=45000.0,  # Iowa-class displacement
            name_prefix="BB"
        ),
        UnitType.CARRIER: UnitTemplate(
            max_speed=NauticalMiles(33.0),  # Essex-class max speed
            cruise_speed=NauticalMiles(15.0),  # Essex-class cruise speed
            max_health=175.0,
            max_fuel=2000.0,
            crew=2600,  # Essex-class complement
            tonnage=27100.0,  # Essex-class displacement
            name_prefix="CV"
        ),
        UnitType.FIGHTER: UnitTemplate(
            max_speed=NauticalMiles(280.0),  # F6F Hellcat max speed
            cruise_speed=NauticalMiles(168.0),  # F6F Hellcat cruise speed
            max_health=50.0,
            max_fuel=300.0,
            crew=1,
            tonnage=4.0,  # F6F Hellcat empty weight in tons
            name_prefix="VF"
        ),
        UnitType.DIVE_BOMBER: UnitTemplate(
            max_speed=NauticalMiles(240.0),  # SBD Dauntless max speed
            cruise_speed=NauticalMiles(185.0),  # SBD Dauntless cruise speed
            max_health=60.0,
            max_fuel=400.0,
            crew=2,
            tonnage=3.0,  # SBD Dauntless empty weight in tons
            name_prefix="VB"
        ),
        UnitType.TORPEDO_BOMBER: UnitTemplate(
            max_speed=NauticalMiles(220.0),  # TBF Avenger max speed
            cruise_speed=NauticalMiles(147.0),  # TBF Avenger cruise speed
            max_health=70.0,
            max_fuel=450.0,
            crew=3,
            tonnage=4.5,  # TBF Avenger empty weight in tons
            name_prefix="VT"
        ),
        UnitType.TRANSPORT: UnitTemplate(
            max_speed=NauticalMiles(16.0),  # Liberty ship max speed
            cruise_speed=NauticalMiles(11.0),  # Liberty ship cruise speed
            max_health=80.0,
            max_fuel=1800.0,
            crew=41,  # Liberty ship complement
            tonnage=14245.0,  # Liberty ship displacement
            name_prefix="AP"
        ),
        UnitType.BASE: UnitTemplate(
            max_speed=NauticalMiles(0.0),  # Stationary
            cruise_speed=NauticalMiles(0.0),  # Stationary
            max_health=500.0,
            max_fuel=5000.0,
            crew=1000,  # Base personnel
            tonnage=0.0,  # Not applicable
            name_prefix="NB"
        ),
    }
    
    @classmethod
    def create_unit(
        cls,
        unit_type: UnitType,
        position: Position,
        *,  # Force remaining arguments to be keyword-only
        hull_number: str,
        ship_class: str,
        faction: str,
        task_force_assigned_to: Optional[str] = None,
        unit_id: Optional[UUID] = None,
        name: Optional[str] = None,
    ) -> Unit:
        """
        Create a new unit with standardized specifications.
        
        Args:
            unit_type: The type of unit to create
            position: Initial position of the unit
            hull_number: Hull/tail number for the unit (e.g. "DD-445")
            ship_class: Class of the ship (e.g. "Fletcher", "Baltimore")
            faction: Faction the unit belongs to (e.g. "USN", "IJN")
            task_force_assigned_to: Optional task force assignment
            unit_id: Optional UUID for the unit
            name: Optional custom name (if not provided, will use hull number)
            
        Returns:
            A new Unit instance with standardized attributes
            
        Raises:
            ValueError: If unit_type is not recognized
        """
        try:
            template = cls.UNIT_SPECS[unit_type]
        except KeyError:
            raise ValueError(f"Unknown unit type: {unit_type}")
        
        # Generate standard name if not provided
        if name is None:
            name = hull_number
        
        # Generate UUID if not provided
        if unit_id is None:
            unit_id = uuid4()
        
        return Unit(
            unit_id=unit_id,
            name=name,
            hull_number=hull_number,
            unit_type=unit_type,
            task_force_assigned_to=task_force_assigned_to,
            ship_class=ship_class,
            faction=faction,
            position=position,
            destination=None,
            max_speed=template.max_speed,
            cruise_speed=template.cruise_speed,
            current_speed=NauticalMiles(0.0),
            max_health=template.max_health,
            current_health=template.max_health,
            max_fuel=template.max_fuel,
            current_fuel=template.max_fuel,
            crew=template.crew,
            tonnage=template.tonnage
        )
    
    @classmethod
    def create_destroyer(
        cls,
        position: Position,
        hull_number: str,
        ship_class: str,
        faction: str,
        **kwargs: Dict
    ) -> Unit:
        """Create a destroyer with standard specifications."""
        return cls.create_unit(
            UnitType.DESTROYER,
            position,
            hull_number=hull_number,
            ship_class=ship_class,
            faction=faction,
            **kwargs
        )
    
    @classmethod
    def create_cruiser(
        cls,
        position: Position,
        hull_number: str,
        ship_class: str,
        faction: str,
        **kwargs: Dict
    ) -> Unit:
        """Create a cruiser with standard specifications."""
        return cls.create_unit(
            UnitType.CRUISER,
            position,
            hull_number=hull_number,
            ship_class=ship_class,
            faction=faction,
            **kwargs
        )
    
    @classmethod
    def create_battleship(
        cls,
        position: Position,
        hull_number: str,
        ship_class: str,
        faction: str,
        **kwargs: Dict
    ) -> Unit:
        """Create a battleship with standard specifications."""
        return cls.create_unit(
            UnitType.BATTLESHIP,
            position,
            hull_number=hull_number,
            ship_class=ship_class,
            faction=faction,
            **kwargs
        )
    
    @classmethod
    def create_carrier(
        cls,
        position: Position,
        hull_number: str,
        ship_class: str,
        faction: str,
        **kwargs: Dict
    ) -> Unit:
        """Create an aircraft carrier with standard specifications."""
        return cls.create_unit(
            UnitType.CARRIER,
            position,
            hull_number=hull_number,
            ship_class=ship_class,
            faction=faction,
            **kwargs
        )
    
    @classmethod
    def create_fighter(
        cls,
        position: Position,
        hull_number: str,
        ship_class: str,
        faction: str,
        **kwargs: Dict
    ) -> Unit:
        """Create a fighter aircraft with standard specifications."""
        return cls.create_unit(
            UnitType.FIGHTER,
            position,
            hull_number=hull_number,
            ship_class=ship_class,
            faction=faction,
            **kwargs
        )
    
    @classmethod
    def create_dive_bomber(
        cls,
        position: Position,
        hull_number: str,
        ship_class: str,
        faction: str,
        **kwargs: Dict
    ) -> Unit:
        """Create a dive bomber aircraft with standard specifications."""
        return cls.create_unit(
            UnitType.DIVE_BOMBER,
            position,
            hull_number=hull_number,
            ship_class=ship_class,
            faction=faction,
            **kwargs
        )
    
    @classmethod
    def create_torpedo_bomber(
        cls,
        position: Position,
        hull_number: str,
        ship_class: str,
        faction: str,
        **kwargs: Dict
    ) -> Unit:
        """Create a torpedo bomber aircraft with standard specifications."""
        return cls.create_unit(
            UnitType.TORPEDO_BOMBER,
            position,
            hull_number=hull_number,
            ship_class=ship_class,
            faction=faction,
            **kwargs
        )
    
    @classmethod
    def create_transport(
        cls,
        position: Position,
        hull_number: str,
        ship_class: str,
        faction: str,
        **kwargs: Dict
    ) -> Unit:
        """Create a transport ship with standard specifications."""
        return cls.create_unit(
            UnitType.TRANSPORT,
            position,
            hull_number=hull_number,
            ship_class=ship_class,
            faction=faction,
            **kwargs
        )
    
    @classmethod
    def create_base(
        cls,
        position: Position,
        hull_number: str,
        ship_class: str,
        faction: str,
        **kwargs: Dict
    ) -> Unit:
        """Create a naval base with standard specifications."""
        return cls.create_unit(
            UnitType.BASE,
            position,
            hull_number=hull_number,
            ship_class=ship_class,
            faction=faction,
            **kwargs
        ) 