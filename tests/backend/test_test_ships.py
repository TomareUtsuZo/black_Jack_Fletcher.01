"""
Tests for test ship specifications.

These tests verify that our test ships have accurate historical specifications
and that the lookup functionality works correctly.
"""

import pytest
from src.backend.models.units.test_ships import (
    get_fletcher_class_ships,
    get_ship_by_hull_number,
    get_all_test_ships,
    get_kagero_class_ships
)
from src.backend.models.units.types.unit_type import UnitType
from src.backend.models.common.geometry.nautical_miles import NauticalMiles
from src.backend.models.common.geometry.position import Position

@pytest.mark.unit
def test_fletcher_specifications() -> None:
    """Test that Fletcher-class ships have correct specifications."""
    ships = get_fletcher_class_ships()
    assert len(ships) == 2  # We have two Fletcher-class ships defined
    
    # Check USS Fletcher (DD-445)
    fletcher = get_ship_by_hull_number("DD-445")
    assert fletcher is not None
    assert fletcher.name == "USS Fletcher"
    assert fletcher.hull_number == "DD-445"
    assert fletcher.ship_class == "Fletcher"
    assert fletcher.faction == "USN"
    assert fletcher.crew == 273
    assert fletcher.tonnage == 2100.0

    # Check USS Talen (DD-666)
    talen = get_ship_by_hull_number("DD-666")
    assert talen is not None
    assert talen.name == "USS Talen"
    assert talen.hull_number == "DD-666"
    assert talen.ship_class == "Fletcher"
    assert talen.faction == "USN"
    assert talen.crew == 273
    assert talen.tonnage == 2100.0

@pytest.mark.unit
def test_kagero_specifications() -> None:
    """Test that Kagero-class ships have correct specifications."""
    ships = get_kagero_class_ships()
    assert len(ships) == 1  # We have one Kagero-class ship defined
    
    # Check IJN Yukikaze (DD-516)
    yukikaze = get_ship_by_hull_number("DD-516")
    assert yukikaze is not None
    assert yukikaze.name == "IJN Yukikaze"
    assert yukikaze.hull_number == "DD-516"
    assert yukikaze.ship_class == "Kagero"
    assert yukikaze.faction == "IJN"
    assert yukikaze.crew == 240
    assert yukikaze.tonnage == 2033.0

@pytest.mark.unit
def test_all_ships_have_consistent_class_specs() -> None:
    """Test that all ships of the same class have consistent specifications."""
    fletcher_ships = get_fletcher_class_ships()
    kagero_ships = get_kagero_class_ships()
    
    # Check Fletcher-class consistency
    first_fletcher = fletcher_ships[0]
    for ship in fletcher_ships[1:]:
        assert ship.max_speed == first_fletcher.max_speed
        assert ship.cruise_speed == first_fletcher.cruise_speed
        assert ship.max_fuel == first_fletcher.max_fuel
        assert ship.crew == first_fletcher.crew
        assert ship.tonnage == first_fletcher.tonnage

    # Check Kagero-class consistency (only one ship for now)
    assert len(kagero_ships) == 1
    kagero = kagero_ships[0]
    assert kagero.max_speed.value == 35.5  # Historical max speed
    assert kagero.cruise_speed.value == 18.0  # Historical cruise speed
    assert kagero.max_fuel == 5000.0  # Historical fuel capacity
    assert kagero.crew == 240  # Historical crew complement
    assert kagero.tonnage == 2033.0  # Historical displacement

@pytest.mark.unit
def test_ship_lookup() -> None:
    """Test that ships can be looked up by hull number."""
    assert get_ship_by_hull_number("DD-445") is not None  # USS Fletcher
    assert get_ship_by_hull_number("DD-666") is not None  # USS Talen
    assert get_ship_by_hull_number("DD-516") is not None  # IJN Yukikaze
    assert get_ship_by_hull_number("PRV-001") is not None  # Queen Anne's Revenge II
    assert get_ship_by_hull_number("NONEXISTENT") is None

@pytest.mark.unit
def test_all_ships_have_unique_identifiers() -> None:
    """Test that all ships have unique unit_ids."""
    ships = get_all_test_ships()
    unit_ids = [ship.unit_id for ship in ships]
    assert len(unit_ids) == len(set(unit_ids))  # No duplicates

@pytest.mark.unit
def test_specifications_are_immutable() -> None:
    """Test that ship specifications cannot be modified after creation."""
    ship = get_ship_by_hull_number("DD-445")
    assert ship is not None
    
    with pytest.raises(Exception):
        ship.name = "New Name"  # type: ignore
    
    with pytest.raises(Exception):
        ship.position = ship.position  # type: ignore 