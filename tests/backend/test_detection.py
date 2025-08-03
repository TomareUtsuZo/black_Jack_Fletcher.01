import pytest
from unittest.mock import MagicMock, patch
from typing import cast
from src.backend.models.units.unit import Unit, UnitAttributes
from src.backend.models.units.modules.detection import DetectionModule
from src.backend.models.game_state_manager import GameStateManager
from src.backend.models.common.geometry.nautical_miles import NauticalMiles
from src.backend.models.common import Position
from src.backend.models.units.types.unit_type import UnitType  # Added missing import
from uuid import uuid4

# Assuming UnitType is an Enum with SHIP as a member
@pytest.fixture
def mock_game_state_manager() -> MagicMock:  # Added return type for mypy
    gsm = MagicMock()
    gsm.get_all_units.return_value = []  # Default to empty, override as needed
    return gsm

@pytest.fixture
def unit_instance(mock_game_state_manager: MagicMock) -> Unit:  # Added return type
    attributes = UnitAttributes(
        unit_id=uuid4(),
        name="Test Unit",
        hull_number="TN-001",
        unit_type=UnitType.DESTROYER,  # Using a valid unit type
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
    unit = Unit(**attributes.__dict__)  # Direct init for testing
    detection_module = DetectionModule(unit, mock_game_state_manager)
    unit.add_module('detection', detection_module)
    return unit

@pytest.mark.usefixtures('mock_game_state_manager')
def test_detection_through_unit_perform_tick(unit_instance: Unit) -> None:  # Added return type
    # Set up mocks for dependencies
    mock_other_unit = MagicMock()
    mock_other_unit.attributes.unit_id = uuid4()
    mock_other_unit.attributes.position = Position(1, 1)  # Within range
    detection_module = cast(DetectionModule, unit_instance.get_module('detection'))
    if detection_module:
        # Use patch to properly mock the method
        with patch.object(detection_module, 'perform_visual_detection', autospec=True) as mock_detect:
            mock_detect.return_value = []  # Empty list of detected units
            # Mock the game state manager's get_all_units method
            # Set up the mock game state manager's behavior
            with patch.object(detection_module._game_state_manager, 'get_all_units', 
                            new_callable=MagicMock) as mock_get_units:
                mock_get_units.return_value = [unit_instance, mock_other_unit]
                
                # Mock distance calculation
                with patch('src.backend.models.common.geometry.vincenty.calculate_vincenty_distance', 
                          autospec=True) as mock_distance:
                    mock_distance.return_value = NauticalMiles(2)  # Mock to be within visual_range
                    
                    # Call perform_tick and assert within all patch contexts
                    unit_instance.perform_tick()
                    mock_detect.assert_called_once()
    # Add more assertions as needed, e.g., for detected units