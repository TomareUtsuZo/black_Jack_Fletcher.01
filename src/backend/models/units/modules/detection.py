from src.backend.models.units.unit import UnitModule, Unit
from src.backend.models.game_state_manager import GameStateManager
from src.backend.models.common.geometry.nautical_miles import NauticalMiles
from src.backend.models.common.geometry.vincenty import calculate_vincenty_distance
from typing import List
import random

class DetectionModule(UnitModule):
    """
    This class represents the detection module for a unit, responsible for handling detection of other units.
    It will interact with the GameStateManager to access the list of units and check for those within range.
    At this time, only visual detection is implemented here, as per requirements.
    """
    
    def __init__(self, unit: Unit, game_state_manager: GameStateManager) -> None:
        """
        Initialize the detection module with references to its unit and the game state.
        
        Args:
            unit: The unit this module belongs to
            game_state_manager: Reference to the game state manager for accessing other units
        """
        self._unit = unit
        self._game_state_manager = game_state_manager
    
    def initialize(self) -> None:
        """
        Initialize the detection module.
        This method is part of the UnitModule protocol and will be called when the module is added to a unit.
        """
        pass  # No additional initialization needed
    
    def perform_visual_detection(self, detection_rate: float, visual_detection_range: NauticalMiles) -> List[Unit]:
        """
        Perform visual detection to identify other units within the specified visual detection range.
        
        Args:
            detection_rate: A float representing the rate or probability factor for successful detection (e.g., 0.0 to 1.0)
            visual_detection_range: A NauticalMiles value representing the maximum range in which units can be visually detected
        
        Returns:
            A list of detected units that are within the visual range and pass the detection rate check
        """
        detected_units: List[Unit] = []
        
        # Get all units from the game state manager
        all_units = self._game_state_manager.get_all_units()
        
        # Get current unit's position
        current_position = self._unit.attributes.position
        
        # Check each unit for detection
        for other_unit in all_units:
            # Skip if it's the same unit
            if other_unit.attributes.unit_id == self._unit.attributes.unit_id:
                continue
            
            # Calculate distance to the other unit using Vincenty's formula
            distance = calculate_vincenty_distance(
                current_position,
                other_unit.attributes.position
            )
            
            # Check if unit is within visual range
            if distance <= visual_detection_range:
                # Apply detection probability
                if random.random() <= detection_rate:
                    detected_units.append(other_unit)
        
        return detected_units
