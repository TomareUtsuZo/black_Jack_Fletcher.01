import pytest
from src.backend.models.units.unit import Unit, UnitState, UnitType
from src.backend.models.units.modules.attack import Attack
from src.backend.models.common.geometry.nautical_miles import NauticalMiles
from src.backend.models.common.geometry.position import Position
import uuid

def create_test_unit(name: str, faction: str, position: Position) -> Unit:
    """Helper function to create test units with standard attributes"""
    return Unit(
        unit_id=uuid.uuid4(),
        name=name,
        hull_number=f"{name[0]}1",
        unit_type=UnitType.DESTROYER,
        task_force_assigned_to=None,
        ship_class="TestClass",
        faction=faction,
        position=position,
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

def test_protocol_implementation() -> None:
    """Test that Attack properly implements UnitModule protocol"""
    from src.backend.models.units.protocols.unit_module_protocol import UnitModule
    from src.backend.models.units.modules.attack import Attack
    
    # Create a simple unit for testing
    unit = Unit(
        unit_id=uuid.uuid4(),
        name="Test Unit",
        hull_number="T1",
        unit_type=UnitType.DESTROYER,
        task_force_assigned_to=None,
        ship_class="TestClass",
        faction="TestFaction",
        position=Position(x=0, y=0),
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
    
    # Verify Attack implements UnitModule
    attack_module = Attack(attacker=unit)
    assert isinstance(attack_module, UnitModule), "Attack should implement UnitModule protocol"
    
    # Verify all protocol methods are implemented
    assert hasattr(attack_module, 'initialize')
    assert hasattr(attack_module, 'calculate_attack_effectiveness')
    assert hasattr(attack_module, 'delineate_legit_targets')
    assert hasattr(attack_module, 'choose_target_from_legit_options')
    assert hasattr(attack_module, 'send_damage_to_target')


def test_attack() -> None:  # Added return type to fix mypy error
    # Set up test units
    unit1_position = Position(x=0, y=0)
    unit2_position = Position(x=1, y=1)
    friendly_unit_position = Position(x=2, y=2)
    sunk_unit_position = Position(x=3, y=3)
    
    # Create attacker unit
    attacker = Unit(
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
    
    # Create enemy target unit
    enemy_target = Unit(
        unit_id=uuid.uuid4(),
        name="Enemy Target",
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
    
    # Create friendly unit (same faction as attacker)
    friendly_unit = Unit(
        unit_id=uuid.uuid4(),
        name="Friendly Unit",
        hull_number="F1",
        unit_type=UnitType.DESTROYER,
        task_force_assigned_to=None,
        ship_class="TestClass",
        faction="TestFaction",  # Same faction as attacker
        position=friendly_unit_position,
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
    
    # Create sunk enemy unit
    sunk_enemy = Unit(
        unit_id=uuid.uuid4(),
        name="Sunk Enemy",
        hull_number="S1",
        unit_type=UnitType.DESTROYER,
        task_force_assigned_to=None,
        ship_class="TestClass",
        faction="EnemyFaction",
        position=sunk_unit_position,
        destination=None,
        max_speed=NauticalMiles(30),
        cruise_speed=NauticalMiles(20),
        current_speed=NauticalMiles(15),
        max_health=100.0,
        current_health=0.0,  # Start with 0 health
        max_fuel=100.0,
        current_fuel=100.0,
        crew=50,
        visual_range=NauticalMiles(20),
        visual_detection_rate=0.5,
        tonnage=5000
    )
    sunk_enemy.take_damage(1)  # This will trigger the transition to SINKING state
    
    # Test initial states
    assert attacker.is_in_state(UnitState.OPERATING)
    assert enemy_target.is_in_state(UnitState.OPERATING)
    assert friendly_unit.is_in_state(UnitState.OPERATING)
    assert sunk_enemy.is_in_state(UnitState.SINKING)
    
    # Test targeting logic - should only attack enemy_target (not friendly or sunk units)
    # Create a farther enemy unit
    far_enemy = Unit(
        unit_id=uuid.uuid4(),
        name="Far Enemy",
        hull_number="F1",
        unit_type=UnitType.DESTROYER,
        task_force_assigned_to=None,
        ship_class="TestClass",
        faction="EnemyFaction",
        position=Position(x=10, y=10),  # Much farther away
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
    
    # Test with multiple valid targets at different distances
    detected_units = [far_enemy, enemy_target, friendly_unit, sunk_enemy]
    
    # Get attack module to test damage calculation directly
    attack_module = attacker.get_module('attack')
    if not attack_module:
        from src.backend.models.units.modules.attack import Attack
        attack_module = Attack(attacker=attacker)
        attacker.add_module('attack', attack_module)
    
    # Test damage calculation
    calculated_damage = attack_module.calculate_attack_effectiveness(enemy_target)
    assert calculated_damage == 10.0, "Base damage calculation should be 10.0"
    
    # Test attack execution with target selection
    attacker.perform_attack(detected_units)
    
    # Verify closest enemy (enemy_target) took calculated damage, others did not
    assert enemy_target.attributes.current_health == 90.0  # Took 10 damage (closest at position 1,1)
    assert far_enemy.attributes.current_health == 100.0  # No damage (farther at position 10,10)
    assert friendly_unit.attributes.current_health == 100.0  # No damage (friendly)
    assert sunk_enemy.attributes.current_health == 0.0  # No change (sunk)
    
    # Verify states remained appropriate
    assert enemy_target.is_in_state(UnitState.OPERATING)
    assert friendly_unit.is_in_state(UnitState.OPERATING)
    assert sunk_enemy.is_in_state(UnitState.SINKING)

    # Test that ship stays OPERATING until health reaches 0
    enemy_target.take_damage(75)  # This brings health to 15
    assert enemy_target.attributes.current_health == 15.0
    assert enemy_target.is_in_state(UnitState.OPERATING)  # Ship should still be operating above 0 health
    
    # Test transition to SINKING state when health reaches 0
    enemy_target.take_damage(15)  # This brings health to 0
    assert enemy_target.attributes.current_health == 0.0  # Verify health is exactly 0
    assert enemy_target.is_in_state(UnitState.SINKING)  # Ship should be sinking when health reaches 0
    
    # Test direct damage application
    test_target = Unit(
        unit_id=uuid.uuid4(),
        name="Test Target",
        hull_number="TT1",
        unit_type=UnitType.DESTROYER,
        task_force_assigned_to=None,
        ship_class="TestClass",
        faction="EnemyFaction",
        position=Position(x=0, y=0),
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
    
    # Test sending specific damage amount
    attack_module.send_damage_to_target(test_target, 25.0)
    assert test_target.attributes.current_health == 75.0, "Direct damage application should reduce health by exact amount"
    assert test_target.is_in_state(UnitState.OPERATING), "Unit should remain operating above 0 health"
    
    # Test sending lethal damage
    attack_module.send_damage_to_target(test_target, 75.0)
    assert test_target.attributes.current_health == 0.0, "Lethal damage should reduce health to 0"
    assert test_target.is_in_state(UnitState.SINKING), "Unit should transition to sinking state at 0 health"

def test_empty_detected_units() -> None:
    """Test behavior when no units are detected"""
    attacker = create_test_unit("Attacker", "TestFaction", Position(x=0, y=0))
    
    # Get attack module
    attack_module = Attack(attacker=attacker)
    attacker.add_module('attack', attack_module)
    
    # Should handle empty list gracefully
    attacker.perform_attack([])
    
    # No exceptions should be raised and attacker should be unaffected
    assert attacker.attributes.current_health == 100.0
    assert attacker.is_in_state(UnitState.OPERATING)

def test_equal_distance_targets() -> None:
    """Test target selection when multiple enemies are at equal distance"""
    attacker = create_test_unit("Attacker", "TestFaction", Position(x=0, y=0))
    enemy1 = create_test_unit("Enemy1", "EnemyFaction", Position(x=1, y=0))
    enemy2 = create_test_unit("Enemy2", "EnemyFaction", Position(x=0, y=1))
    
    # Get attack module
    attack_module = Attack(attacker=attacker)
    attacker.add_module('attack', attack_module)
    
    # Both enemies are at distance 1, should pick one consistently
    detected_units = [enemy1, enemy2]
    attacker.perform_attack(detected_units)
    
    # Verify exactly one target was damaged
    damaged_count = sum(
        1 for unit in [enemy1, enemy2]
        if unit.attributes.current_health < 100.0
    )
    assert damaged_count == 1, "Exactly one target should be damaged"
    
    # Both units should still be operating
    assert enemy1.is_in_state(UnitState.OPERATING)
    assert enemy2.is_in_state(UnitState.OPERATING)

def test_attack_module_initialization() -> None:
    """Test attack module initialization and reinitialization"""
    unit = create_test_unit("Test", "TestFaction", Position(x=0, y=0))
    
    # Test first initialization
    attack_module = Attack(attacker=unit)
    unit.add_module('attack', attack_module)
    assert unit.get_module('attack') is attack_module
    
    # Test attempting to add duplicate module
    with pytest.raises(ValueError, match="Module attack already exists"):
        unit.add_module('attack', Attack(attacker=unit))
    
    # Verify original module is still in place
    assert unit.get_module('attack') is attack_module

def test_weaponless_attack() -> None:
    """Test attack behavior when unit has no weapons"""
    attacker = create_test_unit("Attacker", "TestFaction", Position(x=0, y=0))
    target = create_test_unit("Target", "EnemyFaction", Position(x=1, y=0))
    
    # Get attack module
    attack_module = Attack(attacker=attacker)
    attacker.add_module('attack', attack_module)
    
    # Mock has_weapons to return False
    original_has_weapons = attacker.has_weapons
    attacker.has_weapons = lambda: False  # type: ignore
    
    try:
        attacker.perform_attack([target])
        assert target.attributes.current_health == 100.0, "Weaponless unit should not deal damage"
        assert target.is_in_state(UnitState.OPERATING), "Target should remain operating"
    finally:
        # Restore original method
        attacker.has_weapons = original_has_weapons  # type: ignore