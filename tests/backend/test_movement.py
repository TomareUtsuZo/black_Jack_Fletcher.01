"""Tests for the movement module."""

import math
import pytest
from uuid import uuid4

from src.backend.models.common.geometry import Position, NauticalMiles, Bearing
from src.backend.models.units import UnitAttributes
from src.backend.models.units.types.unit_type import UnitType
from src.backend.models.units.modules.movement import MovementModule

@pytest.fixture
def test_unit_attributes() -> UnitAttributes:
    """Create test unit attributes."""
    return UnitAttributes(
        unit_id=uuid4(),
        name="Test Ship",
        hull_number="TST-001",
        unit_type=UnitType.DESTROYER,
        task_force_assigned_to=None,
        ship_class="Test Class",
        faction="TEST",
        position=Position(0.0, 0.0),
        destination=None,
        max_speed=NauticalMiles(30.0),
        cruise_speed=NauticalMiles(15.0),
        current_speed=NauticalMiles(0.0),
        max_health=100.0,
        current_health=100.0,
        max_fuel=1000.0,
        current_fuel=1000.0,
        crew=100,
        tonnage=1000.0
    )

@pytest.fixture
def movement_module(test_unit_attributes: UnitAttributes) -> MovementModule:
    """Create a movement module with bound test attributes."""
    module = MovementModule()
    module.bind_unit_attributes(test_unit_attributes)
    return module

def test_initialization() -> None:
    """Test movement module initialization."""
    module = MovementModule()
    assert module._unit_attributes is None
    assert module._state.is_moving is False
    assert module._state.current_bearing is None

def test_bind_unit_attributes(movement_module: MovementModule) -> None:
    """Test binding unit attributes."""
    assert movement_module._unit_attributes is not None

def test_set_speed_valid(movement_module: MovementModule) -> None:
    """Test setting valid speed."""
    speed = NauticalMiles(10.0)
    movement_module.set_speed(speed)
    assert movement_module.unit_attributes.current_speed == speed

def test_set_speed_invalid(movement_module: MovementModule) -> None:
    """Test setting invalid speed."""
    with pytest.raises(ValueError):
        movement_module.set_speed(NauticalMiles(-1.0))
    with pytest.raises(ValueError):
        movement_module.set_speed(NauticalMiles(31.0))  # Greater than max_speed

def test_set_destination(movement_module: MovementModule) -> None:
    """Test setting destination."""
    dest = Position(1.0, 1.0)
    movement_module.set_destination(dest)
    assert movement_module.unit_attributes.destination == dest
    assert movement_module._state.is_moving is True
    assert movement_module._state.current_bearing is not None

def test_stop(movement_module: MovementModule) -> None:
    """Test stopping movement."""
    movement_module.stop()
    assert movement_module.unit_attributes.current_speed == NauticalMiles(0)
    assert movement_module.unit_attributes.destination is None
    assert movement_module._state.is_moving is False
    assert movement_module._state.current_bearing is None

def test_straight_movement(movement_module: MovementModule) -> None:
    """Test moving in a straight line."""
    # Set up movement north at 10 knots
    movement_module.set_destination(Position(0.0, 10.0))
    movement_module.set_speed(NauticalMiles(10.0))

    # Move for 1 time unit
    movement_module.update(1.0)

    # Should have moved 10 units north
    assert math.isclose(movement_module.unit_attributes.position.y, 10.0, rel_tol=1e-10)
    assert math.isclose(movement_module.unit_attributes.position.x, 0.0, rel_tol=1e-10)

def test_diagonal_movement(movement_module: MovementModule) -> None:
    """Test moving diagonally."""
    # Set up diagonal movement at 10 knots
    expected_x = 7.071067811865475  # 10 * sin(45°)
    expected_y = 7.071067811865475  # 10 * cos(45°)
    movement_module.set_destination(Position(10.0, 10.0))
    movement_module.set_speed(NauticalMiles(10.0))

    # Move for 1 time unit
    movement_module.update(1.0)

    # Should have moved equal distance in x and y
    assert math.isclose(movement_module.unit_attributes.position.x, expected_x, rel_tol=1e-10)
    assert math.isclose(movement_module.unit_attributes.position.y, expected_y, rel_tol=1e-10)

def test_reach_destination_exact(movement_module: MovementModule) -> None:
    """Test reaching destination exactly."""
    # Set up movement north at 10 knots
    dest = Position(0.0, 10.0)
    movement_module.set_destination(dest)
    movement_module.set_speed(NauticalMiles(10.0))

    # Move for 1 time unit - should reach destination exactly
    movement_module.update(1.0)

    assert movement_module.unit_attributes.position == dest
    assert movement_module.unit_attributes.destination is None

def test_reach_destination_shorter(movement_module: MovementModule) -> None:
    """Test reaching destination when it's closer than what we could travel."""
    # Set up movement north at 10 knots
    dest = Position(0.0, 5.0)  # 5 units north
    movement_module.set_destination(dest)
    movement_module.set_speed(NauticalMiles(10.0))

    # Move for 1 time unit - should reach destination and stop early
    movement_module.update(1.0)

    assert movement_module.unit_attributes.position == dest
    assert movement_module.unit_attributes.destination is None

def test_no_movement_when_stopped(movement_module: MovementModule) -> None:
    """Test that unit doesn't move when stopped."""
    initial_pos = Position(1.0, 1.0)
    movement_module.unit_attributes.position = initial_pos
    movement_module.stop()

    movement_module.update(1.0)

    assert movement_module.unit_attributes.position == initial_pos

def test_no_movement_at_zero_speed(movement_module: MovementModule) -> None:
    """Test that unit doesn't move at zero speed."""
    initial_pos = Position(1.0, 1.0)
    movement_module.unit_attributes.position = initial_pos
    movement_module.unit_attributes.current_speed = NauticalMiles(0.0)

    movement_module.update(1.0)

    assert movement_module.unit_attributes.position == initial_pos 