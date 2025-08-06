from src.backend.models.units.unit import UnitModule, Unit
from src.backend.models.game_state_manager import GameStateManager
from src.backend.models.common.geometry.nautical_miles import NauticalMiles
from src.backend.models.common.geometry.vincenty import calculate_vincenty_distance
from typing import List
import random
from src.backend.models.common.time.game_time import GameTime
from src.backend.models.common.time.day_night import DayNightCycle

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
    
    def perform_visual_detection(self, base_detection_rate: float, base_visual_detection_range: NauticalMiles, current_time: GameTime) -> List[Unit]:
        """
        Perform visual detection using environmental conditions to determine range.
        
        Args:
            base_detection_rate: Base probability of detection (0.0 to 1.0)
            base_visual_detection_range: Base visual range (used for daytime)
            current_time: Current game time for environmental calculations
            
        Returns:
            List of detected units
        """
        # Create DayNightCycle for this ship's position
        # Use position.y as latitude and position.x as longitude
        day_night = DayNightCycle(self._unit.attributes.position.y, self._unit.attributes.position.x)
        
        # Get the environmentally-adjusted detection range
        detection_range = day_night.get_detection_range(current_time, base_visual_detection_range)
        
        detected_units = []
        for other_unit in self._game_state_manager.get_all_units():
            if other_unit != self._unit:
                distance = calculate_vincenty_distance(self._unit.attributes.position, other_unit.attributes.position)
                if distance.value <= detection_range.value and random.random() <= base_detection_rate:
                    detected_units.append(other_unit)
        return detected_units


