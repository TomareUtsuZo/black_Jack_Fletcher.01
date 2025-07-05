import unittest
from src.backend.models.units.unit import Unit
from src.backend.models.units.unit_interface import UnitInterface
from uuid import uuid4  # For test data import
from src.backend.models.units.types.unit_type import UnitType  # Import for type correction
from src.backend.models.common.geometry.position import Position  # Import for Position
from src.backend.models.common.geometry.nautical_miles import NauticalMiles  # Import for NauticalMiles

class TestUnit(unittest.TestCase):
    def setUp(self) -> None:
        # Set up a test Unit instance
        self.unit = Unit(
            unit_id=uuid4(),
            name='TestUnit',
            hull_number='TN001',
            unit_type=UnitType.DESTROYER,  # Corrected to use UnitType enum
            task_force_assigned_to=None,
            ship_class='TestClass',
            faction='TestFaction',
            position=Position(x=0, y=0),  # Corrected to use x and y
            destination=None,
            max_speed=NauticalMiles(30),  # Wrap in NauticalMiles
            cruise_speed=NauticalMiles(20),  # Wrap in NauticalMiles
            current_speed=NauticalMiles(10),  # Wrap in NauticalMiles
            max_health=100,
            current_health=100,
            max_fuel=500,
            current_fuel=500,
            crew=50,
            tonnage=5000
        )
    
    def test_assign_to_task_force(self) -> None:
        # Test the allowed method
        self.unit.assign_to_task_force('TaskForceA')
        state = self.unit.get_unit_state()
        self.assertEqual(state['task_force'], 'TaskForceA')
        self.assertIn('unit_id', state)  # Ensure state is returned correctly
    
    def test_get_unit_state(self) -> None:
        # Test that get_unit_state returns expected data without modifications
        state = self.unit.get_unit_state()
        self.assertIsInstance(state, dict)
        self.assertIn('unit_id', state)
        self.assertNotIn('current_health', state)  # Ensure sensitive data is excluded
    

if __name__ == '__main__':
    unittest.main() 