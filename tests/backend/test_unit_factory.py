"""Tests for the UnitFactory service."""

import pytest
from uuid import UUID

from src.backend.models.common import Position
from src.backend.models.units import Unit
from src.backend.models.units.types import UnitType
from src.backend.services import UnitFactory

@pytest.mark.unit
def test_create_unit_with_defaults() -> None:
    """Test creating a unit with default values."""
    position = Position(x=0.0, y=0.0)
    unit = UnitFactory.create_unit(UnitType.DESTROYER, position)
    
    assert isinstance(unit, Unit)
    assert unit.attributes.name.startswith("DD")
    assert unit.attributes.unit_type == UnitType.DESTROYER
    assert unit.attributes.position == position
    assert unit.attributes.max_speed == 35.0
    assert unit.attributes.max_health == 100.0
    assert unit.attributes.max_fuel == 1000.0
    assert unit.attributes.task_force_assigned_to is None
    assert isinstance(unit.attributes.unit_id, UUID)

@pytest.mark.unit
def test_create_unit_with_custom_values() -> None:
    """Test creating a unit with custom values."""
    position = Position(x=10.0, y=10.0)
    unit_id = UUID('12345678-1234-5678-1234-567812345678')
    unit = UnitFactory.create_unit(
        unit_type=UnitType.CRUISER,
        position=position,
        hull_number=42,
        task_force="TF-38",
        unit_id=unit_id,
        name="USS Custom"
    )
    
    assert unit.attributes.name == "USS Custom"
    assert unit.attributes.unit_type == UnitType.CRUISER
    assert unit.attributes.position == position
    assert unit.attributes.task_force_assigned_to == "TF-38"
    assert unit.attributes.unit_id == unit_id

@pytest.mark.unit
def test_create_unit_with_hull_number() -> None:
    """Test that hull numbers are properly incorporated into unit names."""
    position = Position(x=0.0, y=0.0)
    unit = UnitFactory.create_unit(UnitType.BATTLESHIP, position, hull_number=61)
    
    assert unit.attributes.name == "BB-61"
    assert unit.attributes.unit_type == UnitType.BATTLESHIP

@pytest.mark.unit
def test_create_unit_invalid_type() -> None:
    """Test that creating a unit with an invalid type raises an error."""
    position = Position(x=0.0, y=0.0)
    with pytest.raises(ValueError, match="Unknown unit type"):
        # Using type: ignore because we're intentionally testing invalid type
        UnitFactory.create_unit("INVALID_TYPE", position)  # type: ignore

@pytest.mark.unit
def test_convenience_methods() -> None:
    """Test the convenience methods for creating specific unit types."""
    position = Position(x=0.0, y=0.0)
    
    # Test all convenience methods
    destroyer = UnitFactory.create_destroyer(position, hull_number=21)
    assert destroyer.attributes.unit_type == UnitType.DESTROYER
    assert destroyer.attributes.name == "DD-21"
    
    cruiser = UnitFactory.create_cruiser(position, hull_number=35)
    assert cruiser.attributes.unit_type == UnitType.CRUISER
    assert cruiser.attributes.name == "CA-35"
    
    battleship = UnitFactory.create_battleship(position, hull_number=63)
    assert battleship.attributes.unit_type == UnitType.BATTLESHIP
    assert battleship.attributes.name == "BB-63"
    
    carrier = UnitFactory.create_carrier(position, hull_number=6)
    assert carrier.attributes.unit_type == UnitType.CARRIER
    assert carrier.attributes.name == "CV-6"
    
    fighter = UnitFactory.create_fighter(position, tail_number=201)
    assert fighter.attributes.unit_type == UnitType.FIGHTER
    assert fighter.attributes.name == "VF-201"
    
    dive_bomber = UnitFactory.create_dive_bomber(position, tail_number=3)
    assert dive_bomber.attributes.unit_type == UnitType.DIVE_BOMBER
    assert dive_bomber.attributes.name == "VB-3"
    
    torpedo_bomber = UnitFactory.create_torpedo_bomber(position, tail_number=8)
    assert torpedo_bomber.attributes.unit_type == UnitType.TORPEDO_BOMBER
    assert torpedo_bomber.attributes.name == "VT-8"
    
    transport = UnitFactory.create_transport(position, hull_number=15)
    assert transport.attributes.unit_type == UnitType.TRANSPORT
    assert transport.attributes.name == "AP-15"
    assert transport.attributes.max_speed == 20.0  # Verify transport-specific stats
    
    base = UnitFactory.create_base(position, base_number=7)
    assert base.attributes.unit_type == UnitType.BASE
    assert base.attributes.name == "NB-7"
    assert base.attributes.max_speed == 0.0  # Verify base is stationary

@pytest.mark.unit
def test_unit_specs_completeness() -> None:
    """Test that all unit types have specifications defined."""
    for unit_type in UnitType:
        assert unit_type in UnitFactory.UNIT_SPECS
        specs = UnitFactory.UNIT_SPECS[unit_type]
        assert isinstance(specs.max_speed, float)
        assert isinstance(specs.max_health, float)
        assert isinstance(specs.max_fuel, float)
        assert isinstance(specs.name_prefix, str)

@pytest.mark.unit
def test_transport_specifications() -> None:
    """Test that transport ships have appropriate specifications."""
    position = Position(x=0.0, y=0.0)
    transport = UnitFactory.create_transport(position)
    
    assert transport.attributes.max_speed == 20.0  # Slower than combat ships
    assert transport.attributes.max_health == 80.0  # Less armored
    assert transport.attributes.max_fuel == 1800.0  # Large fuel capacity
    assert transport.attributes.name.startswith("AP")

@pytest.mark.unit
def test_base_specifications() -> None:
    """Test that bases have appropriate specifications."""
    position = Position(x=0.0, y=0.0)
    base = UnitFactory.create_base(position)
    
    assert base.attributes.max_speed == 0.0  # Stationary
    assert base.attributes.max_health == 500.0  # Very durable
    assert base.attributes.max_fuel == 5000.0  # Large fuel storage
    assert base.attributes.name.startswith("NB") 