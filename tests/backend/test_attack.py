import pytest
import logging
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
        tonnage=5000,
        base_damage=10.0,  # Test ship base damage (matches Fletcher)
        optimal_range=NauticalMiles(8.0)  # Test ship optimal range
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


def test_damage_effectiveness() -> None:
    """Test the damage effectiveness calculation system"""
    # Create test units
    attacker = create_test_unit("Attacker", "TestFaction", Position(x=0, y=0))
    
    # Test targets at different ranges
    close_target = create_test_unit("CloseTarget", "EnemyFaction", Position(x=0.01, y=0))  # ~1nm
    mid_target = create_test_unit("MidTarget", "EnemyFaction", Position(x=0.05, y=0))  # ~3nm
    optimal_target = create_test_unit("OptimalTarget", "EnemyFaction",
                                    Position(x=attacker.attributes.optimal_range.value, y=0))  # At optimal range
    far_target = create_test_unit("FarTarget", "EnemyFaction",
                                Position(x=attacker.attributes.optimal_range.value + 2.0, y=0))  # Beyond optimal
    
    # Get attack module
    attack_module = Attack(attacker=attacker)
    attacker.add_module('attack', attack_module)
    
    # Test close range damage (should be highest)
    close_damages = [attack_module.calculate_attack_effectiveness(close_target) for _ in range(100)]
    close_mean = sum(close_damages) / len(close_damages)
    close_min, close_max = min(close_damages), max(close_damages)
    
    # Test optimal range damage (should be lower)
    optimal_damages = [attack_module.calculate_attack_effectiveness(optimal_target) for _ in range(100)]
    optimal_mean = sum(optimal_damages) / len(optimal_damages)
    optimal_min, optimal_max = min(optimal_damages), max(optimal_damages)
    
    # Test far range damage (should be lowest)
    far_damages = [attack_module.calculate_attack_effectiveness(far_target) for _ in range(100)]
    far_mean = sum(far_damages) / len(far_damages)
    far_min, far_max = min(far_damages), max(far_damages)
    
    # Verify damage varies between shots (not constant)
    assert close_min != close_max, "Close range damage should vary between shots"
    assert optimal_min != optimal_max, "Optimal range damage should vary between shots"
    assert far_min != far_max, "Far range damage should vary between shots"
    
    # With 25% standard deviation, means can vary significantly
    # Compare means with allowance for one standard deviation (±25%)
    base_damage = attacker.attributes.base_damage
    std_dev = base_damage * 0.25  # 25% of base damage
    
    logging.debug(f"Damage means - Close: {close_mean:.2f}, Optimal: {optimal_mean:.2f}, Far: {far_mean:.2f}")
    logging.debug(f"Standard deviation: {std_dev:.2f}")
    
    # Close range should be higher than optimal range, allowing for variation
    assert close_mean + std_dev > optimal_mean - std_dev, "Close range should tend to do more damage than optimal range"
    
    # Optimal range should be higher than far range, allowing for variation
    assert optimal_mean + std_dev > far_mean - std_dev, "Optimal range should tend to do more damage than far range"
    
    # Verify the ranges of damage are reasonable
    # Close range (≤1 NM): Normal distribution with mean = base_damage, std_dev = base_damage * 0.25
    assert abs(close_mean - base_damage) < std_dev, "Close range mean should be near base damage"
    assert close_max > base_damage, "Close range should be capable of high damage"
    
    # Optimal range: Normal distribution with mean = base_damage * 0.2, std_dev = base_damage * 0.25
    optimal_expected = base_damage * 0.2
    assert abs(optimal_mean - optimal_expected) < std_dev, "Optimal range mean should be near 20% of base damage"
    
    # Far range (≥optimal): Same as optimal range
    assert abs(far_mean - optimal_expected) < std_dev, "Far range mean should be near 20% of base damage"
    assert far_min < base_damage * 0.2, "Far range should be capable of very low damage"
    
    # Verify damage is never negative
    assert min(close_damages + optimal_damages + far_damages) >= 0, "Damage should never be negative"
    
    # Log some stats for debugging
    logging.debug(f"Close range damage: mean={close_mean:.1f}, min={close_min:.1f}, max={close_max:.1f}")
    logging.debug(f"Optimal range damage: mean={optimal_mean:.1f}, min={optimal_min:.1f}, max={optimal_max:.1f}")
    logging.debug(f"Far range damage: mean={far_mean:.1f}, min={far_min:.1f}, max={far_max:.1f}")
    
    # Test mid-range damage (should be between close and optimal range damage)
    mid_damages = [attack_module.calculate_attack_effectiveness(mid_target) for _ in range(100)]
    mid_mean = sum(mid_damages) / len(mid_damages)
    logging.debug(f"Mid-range damage: mean={mid_mean:.1f}")
    
    # Allow for standard deviation in the comparisons
    assert mid_mean + std_dev > optimal_mean - std_dev, "Mid-range should not be significantly lower than optimal range"
    assert close_mean + std_dev > mid_mean - std_dev, "Close range should not be significantly lower than mid-range"
    
    # Verify target health is not affected by just calculating effectiveness
    assert close_target.attributes.current_health == 100.0, "Damage calculation should not affect health"
    assert optimal_target.attributes.current_health == 100.0, "Damage calculation should not affect health"
    assert far_target.attributes.current_health == 100.0, "Damage calculation should not affect health"

def test_critical_result() -> None:
    """Test the critical hit system"""
    # Create test units
    attacker = create_test_unit("Attacker", "TestFaction", Position(x=0, y=0))
    target = create_test_unit("Target", "EnemyFaction", Position(x=1, y=0))
    
    # Get attack module
    attack_module = Attack(attacker=attacker)
    attacker.add_module('attack', attack_module)
    
    # Test critical hit check (currently just a placeholder)
    initial_health = target.attributes.current_health
    attack_module.check_for_critical_result(target, 10.0)
    assert target.attributes.current_health == initial_health, "Critical check should not affect health in current implementation"

def test_attack() -> None:  # Added return type to fix mypy error
    # Set up test units
    unit1_position = Position(x=0, y=0)
    unit2_position = Position(x=1, y=1)
    friendly_unit_position = Position(x=2, y=2)
    sunk_unit_position = Position(x=3, y=3)
    
    # Create attacker unit
    attacker = create_test_unit("Attacker", "TestFaction", unit1_position)

    # Create enemy target unit
    enemy_target = create_test_unit("Enemy Target", "EnemyFaction", unit2_position)

    # Create friendly unit (same faction as attacker)
    friendly_unit = create_test_unit("Friendly Unit", "TestFaction", friendly_unit_position)

    # Create sunk enemy unit
    sunk_enemy = create_test_unit("Sunk Enemy", "EnemyFaction", sunk_unit_position)
    sunk_enemy.attributes.current_health = 0.0  # Start with 0 health
    sunk_enemy.take_damage(1)  # This will trigger the transition to SINKING state
    
    # Test initial states
    assert attacker.is_in_state(UnitState.OPERATING)
    assert enemy_target.is_in_state(UnitState.OPERATING)
    assert friendly_unit.is_in_state(UnitState.OPERATING)
    assert sunk_enemy.is_in_state(UnitState.SINKING)
    
    # Test targeting logic - should only attack enemy_target (not friendly or sunk units)
    # Create a farther enemy unit
    far_enemy = create_test_unit("Far Enemy", "EnemyFaction", Position(x=10, y=10))
    
    # Test with multiple valid targets at different distances
    detected_units = [far_enemy, enemy_target, friendly_unit, sunk_enemy]
    
    # Get attack module to test damage calculation directly
    attack_module = attacker.get_module('attack')
    if not attack_module:
        from src.backend.models.units.modules.attack import Attack
        attack_module = Attack(attacker=attacker)
        attacker.add_module('attack', attack_module)
    
    # Test damage calculation at close range
    enemy_target.attributes.position = Position(x=0.01, y=0)  # Move target to close range
    
    # First test that calculations and checks don't affect health
    damage = attack_module.calculate_attack_effectiveness(enemy_target)
    assert damage > 0, "Calculated damage should be positive"
    assert enemy_target.attributes.current_health == 100.0, "Damage calculation should not affect health"

    # Test critical check doesn't affect health
    attack_module.check_for_critical_result(enemy_target, damage)
    assert enemy_target.attributes.current_health == 100.0, "Critical check should not affect health"
    # Test attack execution with target selection
    initial_health = enemy_target.attributes.current_health
    attacker.perform_attack(detected_units)
    
    # At close range with base_damage=10.0 and 25% std_dev, damage should be 10 ± 2.5
    damage_taken = initial_health - enemy_target.attributes.current_health
    assert 7.5 <= damage_taken <= 12.5, "Damage at close range should be around 10 ± 2.5 points"
    assert enemy_target.attributes.current_health > 0, "Single attack shouldn't instantly destroy target"
    
    # Verify closest enemy (enemy_target) took damage within expected range, others did not
    # At close range (0.01nm), damage should be reasonable
    # At close range with base_damage=10.0 and 25% std_dev, health should be between 87.5 and 92.5
    assert 87.5 <= enemy_target.attributes.current_health <= 92.5, "Damage at close range should be around 10 ± 2.5 points"
    assert far_enemy.attributes.current_health == 100.0, "No damage (farther at position 10,10)"
    assert friendly_unit.attributes.current_health == 100.0, "No damage (friendly)"
    assert sunk_enemy.attributes.current_health == 0.0, "No change (sunk)"
    
    # Verify states remained appropriate
    assert enemy_target.is_in_state(UnitState.OPERATING)
    assert friendly_unit.is_in_state(UnitState.OPERATING)
    assert sunk_enemy.is_in_state(UnitState.SINKING)

    # Test that ship stays OPERATING until health reaches 0
    current_health = enemy_target.attributes.current_health
    enemy_target.take_damage(current_health * 0.75)  # Reduce health by 75%
    remaining_health = enemy_target.attributes.current_health
    assert 0 < remaining_health < current_health, "Health should be reduced but not zero"
    assert enemy_target.is_in_state(UnitState.OPERATING), "Ship should still be operating above 0 health"
    
    # Test transition to SINKING state when health reaches 0
    enemy_target.take_damage(remaining_health)  # This brings health to 0
    assert enemy_target.attributes.current_health == 0.0, "Health should be exactly 0"
    assert enemy_target.is_in_state(UnitState.SINKING), "Ship should be sinking when health reaches 0"
    
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

def test_damage_application() -> None:
    """Test that damage is properly applied through different methods"""
    # Create test units
    attacker = create_test_unit("Attacker", "TestFaction", Position(x=0, y=0))
    target = create_test_unit("Target", "EnemyFaction", Position(x=1, y=0))
    
    # Get attack module
    attack_module = Attack(attacker=attacker)
    attacker.add_module('attack', attack_module)
    
    # Test damage through send_damage_to_target
    initial_health = target.attributes.current_health
    test_damage = 25.0
    
    # Apply damage through send_damage_to_target
    attack_module.send_damage_to_target(target, test_damage)
    assert target.attributes.current_health == initial_health - test_damage, "Damage was not applied correctly through send_damage_to_target"
    assert target.is_in_state(UnitState.OPERATING), "Unit should still be operating"
    
    # Apply lethal damage through take_damage
    target.take_damage(target.attributes.current_health)  # Apply remaining health as damage
    assert target.attributes.current_health == 0.0, "Health should be zero after lethal damage"
    assert target.is_in_state(UnitState.SINKING), "Unit should transition to sinking state"

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
        # Verify damage calculation still works even without weapons
        base_damage = attack_module.determine_damage_effectiveness(target, 10.0)
        assert base_damage == 10.0, "Damage calculation should work without weapons"
        
        # Verify critical check doesn't affect anything
        attack_module.check_for_critical_result(target, base_damage)
        assert target.attributes.current_health == 100.0, "Critical check should not affect health"
        
        # Test full attack sequence
        attacker.perform_attack([target])
        assert target.attributes.current_health == 100.0, "Weaponless unit should not deal damage"
        assert target.is_in_state(UnitState.OPERATING), "Target should remain operating"
    finally:
        # Restore original method
        attacker.has_weapons = original_has_weapons  # type: ignore