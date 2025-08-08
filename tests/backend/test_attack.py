import pytest
from src.backend.models.units.unit import Unit, UnitState, UnitType
from src.backend.models.common.geometry.nautical_miles import NauticalMiles
from src.backend.models.common.geometry.position import Position
import uuid

def test_attack() -> None:  # Added return type to fix mypy error
    # Set up test units
    unit1_position = Position(x=0, y=0)
    unit2_position = Position(x=1, y=1)
    unit1 = Unit(
        unit_id=uuid.uuid4(),
        name="Attacker",
        hull_number="A1",
        unit_type=UnitType.DESTROYER,
        task_force_assigned_to=None,
        ship_class="TestClass",
        faction="TestFaction",
        position=unit1_position,
        destination=None,
        max_speed=NauticalMiles(30),
        cruise_speed=NauticalMiles(20),
        current_speed=NauticalMiles(15),
        max_health=100.0,
        current_health=100.0,
        max_fuel=100.0,
        current_fuel=100.0,
        crew=50,
        visual_range=NauticalMiles(20),
        visual_detection_rate=0.5,
        tonnage=5000
    )
    
    unit2 = Unit(
        unit_id=uuid.uuid4(),
        name="Target",
        hull_number="T1",
        unit_type=UnitType.DESTROYER,
        task_force_assigned_to=None,
        ship_class="TestClass",
        faction="EnemyFaction",
        position=unit2_position,
        destination=None,
        max_speed=NauticalMiles(30),
        cruise_speed=NauticalMiles(20),
        current_speed=NauticalMiles(15),
        max_health=100.0,
        current_health=100.0,
        max_fuel=100.0,
        current_fuel=100.0,
        crew=50,
        visual_range=NauticalMiles(20),
        visual_detection_rate=0.5,
        tonnage=5000
    )
    
    # Test attack logic
    assert unit1.is_in_state(UnitState.OPERATING)  # Initial state check
    assert unit2.is_in_state(UnitState.OPERATING)  # Initial state check
    
    # Simulate an attack
    unit1.perform_attack(target=unit2)
    
    # Verify damage and state changes
    assert unit2.attributes.current_health == 90.0  # After taking default 10 damage
    assert unit2.is_in_state(UnitState.OPERATING)  # Should still be operating

    # Test that ship stays OPERATING until health reaches 0
    unit2.take_damage(75)  # This brings health to 15
    assert unit2.attributes.current_health == 15.0
    assert unit2.is_in_state(UnitState.OPERATING)  # Ship should still be operating above 0 health
    
    # Test transition to SINKING state when health reaches 0
    unit2.take_damage(15)  # This brings health to 0
    assert unit2.attributes.current_health == 0.0  # Verify health is exactly 0
    assert unit2.is_in_state(UnitState.SINKING)  # Ship should be sinking when health reaches 0