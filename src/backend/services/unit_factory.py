"""
Unit factory service for standardized unit creation.

This service provides factory methods for creating different types of units
with standardized attributes and validation. It ensures consistent unit
creation across the codebase and handles default values appropriately.
"""

from dataclasses import dataclass
from typing import Dict, Optional, ClassVar
from uuid import UUID

from src.backend.models.common import Position
from src.backend.models.common.geometry.nautical_miles import NauticalMiles
from src.backend.models.units import Unit
from src.backend.models.units.types import UnitType

@dataclass(frozen=True)
class UnitTemplate:
    """Standard template for unit type specifications"""
    max_speed: NauticalMiles  # Maximum speed in knots
    max_health: float
    max_fuel: float
    name_prefix: str

class UnitFactory:
    """Factory service for creating standardized units"""
    
    # Standard specifications for each unit type
    UNIT_SPECS: ClassVar[Dict[UnitType, UnitTemplate]] = {
        UnitType.DESTROYER: UnitTemplate(
            max_speed=NauticalMiles(35.0),  # Fletcher-class max speed
            max_health=100.0,
            max_fuel=1000.0,
            name_prefix="DD"
        ),
        UnitType.CRUISER: UnitTemplate(
            max_speed=NauticalMiles(33.0),  # Baltimore-class max speed
            max_health=150.0,
            max_fuel=1200.0,
            name_prefix="CA"
        ),
        UnitType.BATTLESHIP: UnitTemplate(
            max_speed=NauticalMiles(28.0),  # Iowa-class max speed
            max_health=250.0,
            max_fuel=1500.0,
            name_prefix="BB"
        ),
        UnitType.CARRIER: UnitTemplate(
            max_speed=NauticalMiles(33.0),  # Essex-class max speed
            max_health=175.0,
            max_fuel=2000.0,
            name_prefix="CV"
        ),
        UnitType.FIGHTER: UnitTemplate(
            max_speed=NauticalMiles(280.0),  # F6F Hellcat max speed
            max_health=50.0,
            max_fuel=300.0,
            name_prefix="VF"
        ),
        UnitType.DIVE_BOMBER: UnitTemplate(
            max_speed=NauticalMiles(240.0),  # SBD Dauntless max speed
            max_health=60.0,
            max_fuel=400.0,
            name_prefix="VB"
        ),
        UnitType.TORPEDO_BOMBER: UnitTemplate(
            max_speed=NauticalMiles(220.0),  # TBF Avenger max speed
            max_health=70.0,
            max_fuel=450.0,
            name_prefix="VT"
        ),
        UnitType.TRANSPORT: UnitTemplate(
            max_speed=NauticalMiles(16.0),  # Liberty ship max speed
            max_health=80.0,
            max_fuel=1800.0,
            name_prefix="AP"
        ),
        UnitType.BASE: UnitTemplate(
            max_speed=NauticalMiles(0.0),  # Stationary
            max_health=500.0,
            max_fuel=5000.0,
            name_prefix="NB"
        ),
    }
    
    @classmethod
    def create_unit(
        cls,
        unit_type: UnitType,
        position: Position,
        *,  # Force remaining arguments to be keyword-only
        hull_number: Optional[int] = None,
        task_force: Optional[str] = None,
        unit_id: Optional[UUID] = None,
        name: Optional[str] = None,
    ) -> Unit:
        """
        Create a new unit with standardized specifications.
        
        Args:
            unit_type: The type of unit to create
            position: Initial position of the unit
            hull_number: Optional hull/tail number for the unit
            task_force: Optional task force assignment
            unit_id: Optional UUID for the unit
            name: Optional custom name (if not provided, will be generated)
            
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
            hull_suffix = f"-{hull_number}" if hull_number is not None else ""
            name = f"{template.name_prefix}{hull_suffix}"
        
        return Unit(
            name=name,
            unit_type=unit_type,
            position=position,
            max_speed=template.max_speed,
            max_health=template.max_health,
            max_fuel=template.max_fuel,
            task_force=task_force,
            unit_id=unit_id
        )
    
    @classmethod
    def create_destroyer(
        cls,
        position: Position,
        hull_number: Optional[int] = None,
        **kwargs: Dict
    ) -> Unit:
        """Create a destroyer with standard specifications."""
        return cls.create_unit(UnitType.DESTROYER, position, hull_number=hull_number, **kwargs)
    
    @classmethod
    def create_cruiser(
        cls,
        position: Position,
        hull_number: Optional[int] = None,
        **kwargs: Dict
    ) -> Unit:
        """Create a cruiser with standard specifications."""
        return cls.create_unit(UnitType.CRUISER, position, hull_number=hull_number, **kwargs)
    
    @classmethod
    def create_battleship(
        cls,
        position: Position,
        hull_number: Optional[int] = None,
        **kwargs: Dict
    ) -> Unit:
        """Create a battleship with standard specifications."""
        return cls.create_unit(UnitType.BATTLESHIP, position, hull_number=hull_number, **kwargs)
    
    @classmethod
    def create_carrier(
        cls,
        position: Position,
        hull_number: Optional[int] = None,
        **kwargs: Dict
    ) -> Unit:
        """Create an aircraft carrier with standard specifications."""
        return cls.create_unit(UnitType.CARRIER, position, hull_number=hull_number, **kwargs)
    
    @classmethod
    def create_fighter(
        cls,
        position: Position,
        tail_number: Optional[int] = None,
        **kwargs: Dict
    ) -> Unit:
        """Create a fighter aircraft with standard specifications."""
        return cls.create_unit(UnitType.FIGHTER, position, hull_number=tail_number, **kwargs)
    
    @classmethod
    def create_dive_bomber(
        cls,
        position: Position,
        tail_number: Optional[int] = None,
        **kwargs: Dict
    ) -> Unit:
        """Create a dive bomber aircraft with standard specifications."""
        return cls.create_unit(UnitType.DIVE_BOMBER, position, hull_number=tail_number, **kwargs)
    
    @classmethod
    def create_torpedo_bomber(
        cls,
        position: Position,
        tail_number: Optional[int] = None,
        **kwargs: Dict
    ) -> Unit:
        """Create a torpedo bomber aircraft with standard specifications."""
        return cls.create_unit(UnitType.TORPEDO_BOMBER, position, hull_number=tail_number, **kwargs)
    
    @classmethod
    def create_transport(
        cls,
        position: Position,
        hull_number: Optional[int] = None,
        **kwargs: Dict
    ) -> Unit:
        """Create a transport ship with standard specifications."""
        return cls.create_unit(UnitType.TRANSPORT, position, hull_number=hull_number, **kwargs)
    
    @classmethod
    def create_base(
        cls,
        position: Position,
        base_number: Optional[int] = None,
        **kwargs: Dict
    ) -> Unit:
        """Create a naval base with standard specifications."""
        return cls.create_unit(UnitType.BASE, position, hull_number=base_number, **kwargs) 