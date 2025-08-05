import pytest
from unittest.mock import MagicMock, patch
from typing import cast
from datetime import datetime, timezone
from src.backend.models.units.unit import Unit, UnitAttributes
from src.backend.models.units.modules.detection import DetectionModule
from src.backend.models.game_state_manager import GameStateManager
from src.backend.models.common.geometry.nautical_miles import NauticalMiles
from src.backend.models.common import Position
from src.backend.models.units.types.unit_type import UnitType
from src.backend.models.common.time.game_time import GameTime
from src.backend.models.common.time.day_night import DayNightState, DayNightCycle
from uuid import uuid4

@pytest.fixture
def mock_game_state_manager() -> MagicMock:
    gsm = MagicMock()
    gsm.get_all_units.return_value = []  # Default to empty, override as needed
    return gsm

@pytest.fixture
def unit_instance(mock_game_state_manager: MagicMock) -> Unit:
    attributes = UnitAttributes(
        unit_id=uuid4(),
        name="Test Unit",
        hull_number="TN-001",
        unit_type=UnitType.DESTROYER,
        task_force_assigned_to=None,
        ship_class="TestClass",
        faction="TestFaction",
        position=Position(0, 0),
        destination=None,
        max_speed=NauticalMiles(30),
        cruise_speed=NauticalMiles(20),
        current_speed=NauticalMiles(10),
        max_health=100.0,
        current_health=100.0,
        max_fuel=100.0,
        current_fuel=100.0,
        crew=50,
        visual_range=NauticalMiles(5),
        visual_detection_rate=0.8,
        tonnage=5000
    )
    unit = Unit(**attributes.__dict__)
    detection_module = DetectionModule(unit, mock_game_state_manager)
    unit.add_module('detection', detection_module)
    return unit

def test_daytime_detection(unit_instance: Unit) -> None:
    """Test that daytime detection uses the base visual range."""
    detection_module = cast(DetectionModule, unit_instance.get_module('detection'))
    base_range = NauticalMiles(15.0)
    base_rate = 0.8
    
    # Mock a daytime GameTime
    current_time = GameTime(datetime(2024, 6, 21, 12, 0, tzinfo=timezone.utc))  # Noon
    
    # Create a target unit within base range
    target_unit = MagicMock()
    target_unit.attributes.position = Position(0.1, 0.1)  # Close by
    
    with patch.object(detection_module._game_state_manager, 'get_all_units') as mock_get_units:
        mock_get_units.return_value = [unit_instance, target_unit]
        with patch('src.backend.models.units.modules.detection.calculate_vincenty_distance') as mock_distance:
            mock_distance.return_value = NauticalMiles(10.0)  # Within base range
            
            # Mock random to always succeed detection check
            with patch('random.random', return_value=0.0):  # Will be <= any valid detection rate
                detected = detection_module.perform_visual_detection(base_rate, base_range, current_time)
                assert len(detected) > 0, "Should detect units within base range during day"

def test_night_detection_full_moon(unit_instance: Unit) -> None:
    """Test that night detection with full moon has 5nm range."""
    detection_module = cast(DetectionModule, unit_instance.get_module('detection'))
    base_range = NauticalMiles(15.0)
    base_rate = 0.8
    
    # Mock a night time with full moon
    current_time = GameTime(datetime(2024, 6, 21, 0, 0, tzinfo=timezone.utc))  # Midnight
    
    # Mock DayNightCycle
    mock_cycle = MagicMock()
    mock_cycle.get_detection_range.return_value = NauticalMiles(5.0)
    with patch('src.backend.models.units.modules.detection.DayNightCycle', return_value=mock_cycle):
        
        # Test detection at exactly 5nm
        target_unit = MagicMock()
        target_unit.attributes.position = Position(0.1, 0.1)
        
        with patch.object(detection_module._game_state_manager, 'get_all_units') as mock_get_units:
            mock_get_units.return_value = [unit_instance, target_unit]
            with patch('src.backend.models.units.modules.detection.calculate_vincenty_distance') as mock_distance:
                mock_distance.return_value = NauticalMiles(5.0)  # At full moon night range
                
                # Mock random to always succeed detection check
                with patch('random.random', return_value=0.0):  # Will be <= any valid detection rate
                    detected = detection_module.perform_visual_detection(base_rate, base_range, current_time)
                    assert len(detected) > 0, "Should detect units at 5nm during full moon night"

def test_night_detection_new_moon(unit_instance: Unit) -> None:
    """Test that night detection with new moon has 1nm range."""
    detection_module = cast(DetectionModule, unit_instance.get_module('detection'))
    base_range = NauticalMiles(15.0)
    base_rate = 0.8
    
    # Mock a night time with new moon
    current_time = GameTime(datetime(2024, 6, 21, 0, 0, tzinfo=timezone.utc))  # Midnight
    
    # Mock DayNightCycle
    mock_cycle = MagicMock()
    mock_cycle.get_detection_range.return_value = NauticalMiles(1.0)
    with patch('src.backend.models.units.modules.detection.DayNightCycle', return_value=mock_cycle):
        
        # Test detection at 1.5nm (should fail) and 0.9nm (should succeed)
        target_unit = MagicMock()
        target_unit.attributes.position = Position(0.1, 0.1)
        
        with patch.object(detection_module._game_state_manager, 'get_all_units') as mock_get_units:
            mock_get_units.return_value = [unit_instance, target_unit]
            with patch('src.backend.models.units.modules.detection.calculate_vincenty_distance') as mock_distance:
                # Test beyond new moon range
                mock_distance.return_value = NauticalMiles(1.5)
                # Mock random to always succeed detection check (but should still fail due to range)
                with patch('random.random', return_value=0.0):
                    detected = detection_module.perform_visual_detection(base_rate, base_range, current_time)
                    assert len(detected) == 0, "Should not detect units beyond 1nm during new moon"
                
                # Test within new moon range
                mock_distance.return_value = NauticalMiles(0.9)
                # Mock random to always succeed detection check
                with patch('random.random', return_value=0.0):  # Will be <= any valid detection rate
                    detected = detection_module.perform_visual_detection(base_rate, base_range, current_time)
                    assert len(detected) > 0, "Should detect units within 1nm during new moon"

def test_dawn_dusk_detection(unit_instance: Unit) -> None:
    """Test that dawn/dusk detection has 10nm range."""
    detection_module = cast(DetectionModule, unit_instance.get_module('detection'))
    base_range = NauticalMiles(15.0)
    base_rate = 0.8
    
    # Mock dawn time
    current_time = GameTime(datetime(2024, 6, 21, 5, 45, tzinfo=timezone.utc))  # Just before sunrise
    
    # Mock DayNightCycle
    mock_cycle = MagicMock()
    mock_cycle.get_detection_range.return_value = NauticalMiles(10.0)
    with patch('src.backend.models.units.modules.detection.DayNightCycle', return_value=mock_cycle):
        target_unit = MagicMock()
        target_unit.attributes.position = Position(0.1, 0.1)
        
        with patch.object(detection_module._game_state_manager, 'get_all_units') as mock_get_units:
            mock_get_units.return_value = [unit_instance, target_unit]
            with patch('src.backend.models.units.modules.detection.calculate_vincenty_distance') as mock_distance:
                # Test at exactly 10nm
                mock_distance.return_value = NauticalMiles(10.0)
                # Mock random to always succeed detection check
                with patch('random.random', return_value=0.0):  # Will be <= any valid detection rate
                    detected = detection_module.perform_visual_detection(base_rate, base_range, current_time)
                    assert len(detected) > 0, "Should detect units at 10nm during dawn/dusk"
                
                # Test beyond 10nm
                mock_distance.return_value = NauticalMiles(10.1)
                # Mock random to always succeed detection check (but should still fail due to range)
                with patch('random.random', return_value=0.0):
                    detected = detection_module.perform_visual_detection(base_rate, base_range, current_time)
                    assert len(detected) == 0, "Should not detect units beyond 10nm during dawn/dusk"