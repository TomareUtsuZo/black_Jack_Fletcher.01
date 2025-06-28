import pytest
from typing import Optional
from uuid import UUID, uuid4

from src.backend.models.common import Position
from src.backend.models.common.geometry.nautical_miles import NauticalMiles
from src.backend.models.units import Unit, UnitAttributes
from src.backend.models.units.types import UnitType
from src.backend.models.units import UnitModule

class TestUnit:
    """Test suite for the Unit class"""
    
    @pytest.fixture
    def basic_unit(self) -> Unit:
        """Fixture providing a basic unit for testing"""
        return Unit(
            unit_id=uuid4(),
            name="Test Destroyer",
            hull_number="DD-445",
            unit_type=UnitType.DESTROYER,
            task_force_assigned_to=None,
            ship_class="Fletcher",
            faction="USN",
            position=Position(x=0.0, y=0.0),
            destination=None,
            max_speed=NauticalMiles(30.0),
            cruise_speed=NauticalMiles(15.0),
            current_speed=NauticalMiles(0.0),
            max_health=100.0,
            current_health=100.0,
            max_fuel=1000.0,
            current_fuel=1000.0,
            crew=273,
            tonnage=2100.0
        )
    
    @pytest.fixture
    def task_force_unit(self) -> Unit:
        """Fixture providing a unit assigned to a task force"""
        return Unit(
            unit_id=uuid4(),
            name="Task Force Ship",
            hull_number="CA-68",
            unit_type=UnitType.CRUISER,
            task_force_assigned_to="TF-38",
            ship_class="Baltimore",
            faction="USN",
            position=Position(x=10.0, y=10.0),
            destination=None,
            max_speed=NauticalMiles(25.0),
            cruise_speed=NauticalMiles(15.0),
            current_speed=NauticalMiles(0.0),
            max_health=150.0,
            current_health=150.0,
            max_fuel=1200.0,
            current_fuel=1200.0,
            crew=1142,
            tonnage=13600.0
        )

    def test_unit_initialization(self, basic_unit: Unit) -> None:
        """Test that a unit is properly initialized with default values"""
        assert basic_unit.attributes.name == "Test Destroyer"
        assert basic_unit.attributes.hull_number == "DD-445"
        assert basic_unit.attributes.unit_type == UnitType.DESTROYER
        assert basic_unit.attributes.ship_class == "Fletcher"
        assert basic_unit.attributes.faction == "USN"
        assert basic_unit.attributes.position == Position(0.0, 0.0)
        assert basic_unit.attributes.current_health == basic_unit.attributes.max_health
        assert basic_unit.attributes.current_fuel == basic_unit.attributes.max_fuel
        assert basic_unit.attributes.current_speed.value == 0.0
        assert basic_unit.attributes.destination is None
        assert basic_unit.attributes.task_force_assigned_to is None
        assert isinstance(basic_unit.attributes.unit_id, UUID)

    def test_unit_with_task_force(self, task_force_unit: Unit) -> None:
        """Test that a unit can be initialized with a task force"""
        assert task_force_unit.attributes.task_force_assigned_to == "TF-38"
        assert task_force_unit.attributes.position == Position(10.0, 10.0)
        assert task_force_unit.attributes.ship_class == "Baltimore"
        assert task_force_unit.attributes.hull_number == "CA-68"

    def test_unit_takes_damage(self, basic_unit: Unit) -> None:
        """Test unit damage handling"""
        initial_health = basic_unit.attributes.current_health
        damage_amount = 30.0
        
        basic_unit.take_damage(damage_amount)
        assert basic_unit.attributes.current_health == initial_health - damage_amount
        assert basic_unit.is_alive

        # Test that health cannot go below 0
        basic_unit.take_damage(initial_health)
        assert basic_unit.attributes.current_health == 0.0
        assert not basic_unit.is_alive

    def test_unit_fuel_consumption(self, basic_unit: Unit) -> None:
        """Test unit fuel management"""
        initial_fuel = basic_unit.attributes.current_fuel
        fuel_amount = 100.0

        # Test successful fuel consumption
        assert basic_unit.consume_fuel(fuel_amount)
        assert basic_unit.attributes.current_fuel == initial_fuel - fuel_amount
        assert basic_unit.has_fuel

        # Test attempting to consume more fuel than available
        remaining_fuel = basic_unit.attributes.current_fuel
        assert not basic_unit.consume_fuel(remaining_fuel + 1.0)
        assert basic_unit.attributes.current_fuel == remaining_fuel  # Fuel shouldn't change
        
        # Test consuming exactly remaining fuel
        assert basic_unit.consume_fuel(remaining_fuel)
        assert basic_unit.attributes.current_fuel == 0.0
        assert not basic_unit.has_fuel

    def test_unit_destination_setting(self, basic_unit: Unit) -> None:
        """Test setting unit destination"""
        new_position = Position(100.0, 100.0)
        
        basic_unit.set_destination(new_position)
        assert basic_unit.attributes.destination == new_position
        
        # Test updating destination
        another_position = Position(200.0, 200.0)
        basic_unit.set_destination(another_position)
        assert basic_unit.attributes.destination == another_position

    def test_unit_speed_setting(self, basic_unit: Unit) -> None:
        """Test setting unit speed"""
        # Test initial speed
        assert basic_unit.attributes.current_speed.value == 0.0
        
        # Test setting valid speed
        new_speed = NauticalMiles(20.0)
        basic_unit.set_speed(new_speed)
        assert basic_unit.attributes.current_speed == new_speed
        
        # Test setting negative speed
        with pytest.raises(ValueError):
            basic_unit.set_speed(NauticalMiles(-5.0))
        
        # Test exceeding max speed
        with pytest.raises(ValueError):
            basic_unit.set_speed(NauticalMiles(35.0))

    def test_task_force_assignment(self, basic_unit: Unit) -> None:
        """Test assigning unit to task forces"""
        # Test assigning to a task force
        task_force = "TF-38"
        basic_unit.assign_to_task_force(task_force)
        assert basic_unit.attributes.task_force_assigned_to == task_force
        
        # Test reassigning to different task force
        new_task_force = "TF-58"
        basic_unit.assign_to_task_force(new_task_force)
        assert basic_unit.attributes.task_force_assigned_to == new_task_force
        
        # Test removing from task force
        basic_unit.assign_to_task_force(None)
        assert basic_unit.attributes.task_force_assigned_to is None

    def test_module_management(self, basic_unit: Unit) -> None:
        """Test adding and retrieving modules"""
        class TestModule(UnitModule):
            def __init__(self) -> None:
                self.initialized = False
                
            def initialize(self) -> None:
                self.initialized = True

        # Test adding a module
        test_module = TestModule()
        basic_unit.add_module("test", test_module)
        assert test_module.initialized
        assert basic_unit.get_module("test") == test_module

        # Test adding duplicate module
        with pytest.raises(ValueError):
            basic_unit.add_module("test", TestModule())

        # Test retrieving non-existent module
        assert basic_unit.get_module("nonexistent") is None 