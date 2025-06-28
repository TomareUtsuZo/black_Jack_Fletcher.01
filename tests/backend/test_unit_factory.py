"""Tests for the UnitFactory service."""

import pytest
from uuid import UUID

from src.backend.models.common import Position
from src.backend.models.common.geometry.nautical_miles import NauticalMiles
from src.backend.models.units import Unit
from src.backend.models.units.types import UnitType
from src.backend.services import UnitFactory

@pytest.mark.unit
def test_create_unit_with_defaults() -> None:
    """Test creating a unit with default values."""
    position = Position(x=0.0, y=0.0)
    unit = UnitFactory.create_unit(
        unit_type=UnitType.DESTROYER,
        position=position,
        hull_number="DD-445",
        ship_class="Fletcher",
        faction="USN"
    )
    
    assert isinstance(unit, Unit)
    assert unit.attributes.name.startswith("DD")
    assert unit.attributes.hull_number == "DD-445"
    assert unit.attributes.unit_type == UnitType.DESTROYER
    assert unit.attributes.ship_class == "Fletcher"
    assert unit.attributes.faction == "USN"
    assert unit.attributes.position == position
    assert unit.attributes.destination is None
    assert isinstance(unit.attributes.max_speed, NauticalMiles)
    assert unit.attributes.max_speed.value == 35.0  # Fletcher-class speed
    assert unit.attributes.cruise_speed.value == 15.0
    assert unit.attributes.current_speed.value == 0.0  # Starts stationary
    assert unit.attributes.max_health == 100.0
    assert unit.attributes.current_health == 100.0
    assert unit.attributes.max_fuel == 5500.0  # Fletcher-class fuel capacity
    assert unit.attributes.current_fuel == 5500.0
    assert unit.attributes.crew == 273  # Fletcher-class complement
    assert unit.attributes.tonnage == 2100.0  # Fletcher-class displacement

@pytest.mark.unit
def test_create_unit_with_custom_values() -> None:
    """Test creating a unit with custom values."""
    position = Position(x=10.0, y=10.0)
    unit_id = UUID('12345678-1234-5678-1234-567812345678')
    unit = UnitFactory.create_unit(
        unit_type=UnitType.CRUISER,
        position=position,
        hull_number="CA-68",
        task_force_assigned_to="TF-38",
        unit_id=unit_id,
        name="USS Custom",
        ship_class="Baltimore",
        faction="USN"
    )
    
    assert isinstance(unit, Unit)
    assert unit.attributes.name == "USS Custom"
    assert unit.attributes.hull_number == "CA-68"
    assert unit.attributes.unit_type == UnitType.CRUISER
    assert unit.attributes.task_force_assigned_to == "TF-38"
    assert unit.attributes.unit_id == unit_id
    assert unit.attributes.ship_class == "Baltimore"
    assert unit.attributes.faction == "USN"
    assert unit.attributes.position == position
    assert unit.attributes.destination is None
    assert isinstance(unit.attributes.max_speed, NauticalMiles)
    assert unit.attributes.max_speed.value == 33.0  # Baltimore-class speed
    assert unit.attributes.cruise_speed.value == 15.0
    assert unit.attributes.current_speed.value == 0.0  # Starts stationary
    assert unit.attributes.max_health == 150.0
    assert unit.attributes.current_health == 150.0
    assert unit.attributes.max_fuel == 1200.0
    assert unit.attributes.current_fuel == 1200.0
    assert unit.attributes.crew == 1142  # Baltimore-class complement
    assert unit.attributes.tonnage == 13600.0  # Baltimore-class displacement

@pytest.mark.unit
def test_create_unit_with_hull_number() -> None:
    """Test that hull numbers are properly incorporated into unit names."""
    position = Position(x=0.0, y=0.0)
    unit = UnitFactory.create_unit(
        unit_type=UnitType.BATTLESHIP,
        position=position,
        hull_number="BB-61",
        ship_class="Iowa",
        faction="USN"
    )
    
    assert unit.attributes.name == "BB-61"
    assert unit.attributes.hull_number == "BB-61"
    assert unit.attributes.unit_type == UnitType.BATTLESHIP
    assert unit.attributes.ship_class == "Iowa"
    assert unit.attributes.faction == "USN"

@pytest.mark.unit
def test_create_unit_invalid_type() -> None:
    """Test that creating a unit with an invalid type raises an error."""
    position = Position(x=0.0, y=0.0)
    with pytest.raises(ValueError, match="Unknown unit type"):
        # Using type: ignore because we're intentionally testing invalid type
        UnitFactory.create_unit(
            "INVALID_TYPE",  # type: ignore
            position,
            hull_number="XX-99",
            ship_class="Invalid",
            faction="TEST"
        )

@pytest.mark.unit
def test_convenience_methods() -> None:
    """Test the convenience methods for creating specific unit types."""
    position = Position(x=0.0, y=0.0)
    
    # Test all convenience methods
    destroyer = UnitFactory.create_destroyer(
        position=position,
        hull_number="DD-445",
        ship_class="Fletcher",
        faction="USN"
    )
    assert destroyer.attributes.unit_type == UnitType.DESTROYER
    assert destroyer.attributes.name == "DD-445"
    assert destroyer.attributes.hull_number == "DD-445"
    assert destroyer.attributes.ship_class == "Fletcher"
    assert destroyer.attributes.max_speed.value == 35.0  # Fletcher-class speed
    
    cruiser = UnitFactory.create_cruiser(
        position=position,
        hull_number="CA-68",
        ship_class="Baltimore",
        faction="USN"
    )
    assert cruiser.attributes.unit_type == UnitType.CRUISER
    assert cruiser.attributes.name == "CA-68"
    assert cruiser.attributes.hull_number == "CA-68"
    assert cruiser.attributes.ship_class == "Baltimore"
    assert cruiser.attributes.max_speed.value == 33.0  # Baltimore-class speed
    
    battleship = UnitFactory.create_battleship(
        position=position,
        hull_number="BB-61",
        ship_class="Iowa",
        faction="USN"
    )
    assert battleship.attributes.unit_type == UnitType.BATTLESHIP
    assert battleship.attributes.name == "BB-61"
    assert battleship.attributes.hull_number == "BB-61"
    assert battleship.attributes.ship_class == "Iowa"
    assert battleship.attributes.max_speed.value == 28.0  # Iowa-class speed
    
    carrier = UnitFactory.create_carrier(
        position=position,
        hull_number="CV-6",
        ship_class="Essex",
        faction="USN"
    )
    assert carrier.attributes.unit_type == UnitType.CARRIER
    assert carrier.attributes.name == "CV-6"
    assert carrier.attributes.hull_number == "CV-6"
    assert carrier.attributes.ship_class == "Essex"
    assert carrier.attributes.max_speed.value == 33.0  # Essex-class speed
    
    fighter = UnitFactory.create_fighter(
        position=position,
        hull_number="VF-201",
        ship_class="F6F Hellcat",
        faction="USN"
    )
    assert fighter.attributes.unit_type == UnitType.FIGHTER
    assert fighter.attributes.name == "VF-201"
    assert fighter.attributes.hull_number == "VF-201"
    assert fighter.attributes.ship_class == "F6F Hellcat"
    assert fighter.attributes.max_speed.value == 280.0  # F6F Hellcat speed
    
    dive_bomber = UnitFactory.create_dive_bomber(
        position=position,
        hull_number="VB-3",
        ship_class="SBD Dauntless",
        faction="USN"
    )
    assert dive_bomber.attributes.unit_type == UnitType.DIVE_BOMBER
    assert dive_bomber.attributes.name == "VB-3"
    assert dive_bomber.attributes.hull_number == "VB-3"
    assert dive_bomber.attributes.ship_class == "SBD Dauntless"
    assert dive_bomber.attributes.max_speed.value == 240.0  # SBD Dauntless speed
    
    torpedo_bomber = UnitFactory.create_torpedo_bomber(
        position=position,
        hull_number="VT-8",
        ship_class="TBF Avenger",
        faction="USN"
    )
    assert torpedo_bomber.attributes.unit_type == UnitType.TORPEDO_BOMBER
    assert torpedo_bomber.attributes.name == "VT-8"
    assert torpedo_bomber.attributes.hull_number == "VT-8"
    assert torpedo_bomber.attributes.ship_class == "TBF Avenger"
    assert torpedo_bomber.attributes.max_speed.value == 220.0  # TBF Avenger speed
    
    transport = UnitFactory.create_transport(
        position=position,
        hull_number="AP-15",
        ship_class="Liberty",
        faction="USN"
    )
    assert transport.attributes.unit_type == UnitType.TRANSPORT
    assert transport.attributes.name == "AP-15"
    assert transport.attributes.hull_number == "AP-15"
    assert transport.attributes.ship_class == "Liberty"
    assert transport.attributes.max_speed.value == 16.0  # Liberty ship speed
    
    base = UnitFactory.create_base(
        position=position,
        hull_number="NB-7",
        ship_class="Naval Base",
        faction="USN"
    )
    assert base.attributes.unit_type == UnitType.BASE
    assert base.attributes.name == "NB-7"
    assert base.attributes.hull_number == "NB-7"
    assert base.attributes.ship_class == "Naval Base"
    assert base.attributes.max_speed.value == 0.0  # Stationary

@pytest.mark.unit
def test_unit_specs_completeness() -> None:
    """Test that all unit types have specifications defined."""
    for unit_type in UnitType:
        assert unit_type in UnitFactory.UNIT_SPECS
        specs = UnitFactory.UNIT_SPECS[unit_type]
        assert isinstance(specs.max_speed, NauticalMiles)
        assert isinstance(specs.max_health, float)
        assert isinstance(specs.max_fuel, float)
        assert isinstance(specs.name_prefix, str)

@pytest.mark.unit
def test_speed_operations() -> None:
    """Test speed-related operations on units."""
    position = Position(x=0.0, y=0.0)
    destroyer = UnitFactory.create_destroyer(
        position=position,
        hull_number="DD-445",
        ship_class="Fletcher",
        faction="USN"
    )
    
    # Test initial speed
    assert destroyer.attributes.current_speed.value == 0.0
    
    # Test setting speed
    new_speed = NauticalMiles(20.0)
    destroyer.set_speed(new_speed)
    assert destroyer.attributes.current_speed == new_speed
    
    # Test setting invalid speeds
    with pytest.raises(ValueError):
        destroyer.set_speed(NauticalMiles(-5.0))  # Negative speed
    
    with pytest.raises(ValueError):
        destroyer.set_speed(NauticalMiles(40.0))  # Exceeds max speed

@pytest.mark.unit
def test_transport_specifications() -> None:
    """Test that transport ships have appropriate specifications."""
    position = Position(x=0.0, y=0.0)
    transport = UnitFactory.create_transport(
        position=position,
        hull_number="AP-15",
        ship_class="Liberty",
        faction="USN"
    )
    
    assert transport.attributes.max_speed.value == 16.0  # Liberty ship speed
    assert transport.attributes.max_health == 80.0  # Less armored
    assert transport.attributes.max_fuel == 1800.0  # Large fuel capacity
    assert transport.attributes.name.startswith("AP")
    assert transport.attributes.hull_number == "AP-15"
    assert transport.attributes.ship_class == "Liberty"

@pytest.mark.unit
def test_base_specifications() -> None:
    """Test that bases have appropriate specifications."""
    position = Position(x=0.0, y=0.0)
    base = UnitFactory.create_base(
        position=position,
        hull_number="NB-7",
        ship_class="Naval Base",
        faction="USN"
    )
    
    assert base.attributes.max_speed.value == 0.0  # Stationary
    assert base.attributes.max_health == 500.0  # Very durable
    assert base.attributes.max_fuel == 5000.0  # Large fuel storage
    assert base.attributes.name.startswith("NB")
    assert base.attributes.hull_number == "NB-7"
    assert base.attributes.ship_class == "Naval Base" 