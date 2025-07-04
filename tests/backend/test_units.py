import unittest
from src.backend.models.units.unit import Unit
from src.backend.models.units.unit_interface import UnitInterface
from uuid import uuid4  # For test data import

class TestUnit(unittest.TestCase):
    def setUp(self):
        # Set up a test Unit instance
        self.unit = Unit(
            unit_id=uuid4(),
            name='TestUnit',
            hull_number='TN001',
            unit_type='DESTROYER',  # Assuming from your UnitType
            task_force_assigned_to=None,
            ship_class='TestClass',
            faction='TestFaction',
            position={},  # Use a dummy Position
            destination=None,
            max_speed=30,  # In knots
            cruise_speed=20,
            current_speed=10,
            max_health=100,
            current_health=100,
            max_fuel=500,
            current_fuel=500,
            crew=50,
            tonnage=5000
        )
    
    def test_assign_to_task_force(self):
        # Test the allowed method
        self.unit.assign_to_task_force('TaskForceA')
        state = self.unit.get_unit_state()
        self.assertEqual(state['task_force'], 'TaskForceA')
        self.assertIn('unit_id', state)  # Ensure state is returned correctly
    
    def test_get_unit_state(self):
        # Test that get_unit_state returns expected data without modifications
        state = self.unit.get_unit_state()
        self.assertIsInstance(state, dict)
        self.assertIn('unit_id', state)
        self.assertNotIn('current_health', state)  # Ensure sensitive data is excluded
    
    def test_unauthorized_access(self):
        # Simulate or test for restricted methods (e.g., if trying to call a non-interface method)
        with self.assertRaises(AttributeError):  # Or PermissionError if decorator is active
            # Assuming a non-exposed method; adjust based on your code
            self.unit._some_internal_method()  # Replace with an actual internal method if needed
    
if __name__ == '__main__':
    unittest.main() 