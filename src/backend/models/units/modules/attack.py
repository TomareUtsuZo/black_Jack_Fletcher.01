import logging  # Import for logging errors or events
from typing import List
from src.backend.models.units.unit import Unit, UnitModule

# Define a basic Attack class for handling combat logic
class Attack(UnitModule):
    def __init__(self, attacker: Unit, damage: float = 10):  # Initialize with attacker and default damage
        self.attacker = attacker  # The unit performing the attack
        self.damage = damage  # Amount of damage to apply
        
    def initialize(self) -> None:
        """Initialize the attack module"""
        logging.info(f"Initializing attack module for {self.attacker.attributes.name}")

    def delineate_legit_targets(self, detected_units: List[Unit]) -> List[Unit]:
        """
        Filter detected units to determine legitimate targets based on combat rules.
        
        Args:
            detected_units: List of units that have been detected
            
        Returns:
            List of units that are valid targets for attack
        """
        legit_targets = []
        
        for unit in detected_units:
            # Skip if unit is from same faction
            if unit.attributes.faction == self.attacker.attributes.faction:
                continue
                
            # Skip if unit is sunk
            if not unit.is_not_sunk:
                continue
                
            # Add unit to legitimate targets if it passes all checks
            legit_targets.append(unit)
            
        logging.info(f"{self.attacker.attributes.name} identified {len(legit_targets)} legitimate targets")
        return legit_targets

    def execute_attack(self, target: Unit) -> None:
        """
        Execute an attack against a specific target.
        
        Args:
            target: The unit to attack
        """
        if self.attacker.has_weapons():
            target.take_damage(self.damage)
            logging.info(f"{self.attacker.attributes.name} attacked {target.attributes.name} for {self.damage} damage")
        else:
            logging.warning(f"{self.attacker.attributes.name} has no weapons")
