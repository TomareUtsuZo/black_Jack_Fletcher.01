import logging  # Import for logging errors or events
from typing import List, Optional
from src.backend.models.units.unit import Unit
from src.backend.models.units.protocols.unit_module_protocol import UnitModule

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

    def choose_target_from_legit_options(self, legit_targets: List[Unit]) -> Optional[Unit]:
        """
        Choose a target from the list of legitimate targets.
        Currently selects the closest target based on straight-line distance.
        
        Args:
            legit_targets: List of valid targets to choose from
            
        Returns:
            The chosen target, or None if no valid targets
        """
        if not legit_targets:
            return None
            
        # Get attacker's position
        attacker_pos = self.attacker.attributes.position
        
        # Find the closest target
        closest_target = min(
            legit_targets,
            key=lambda target: attacker_pos.distance_to(target.attributes.position)
        )
        
        logging.info(f"{self.attacker.attributes.name} selected {closest_target.attributes.name} as closest target")
        return closest_target

    def calculate_attack_effectiveness(self, target: Unit) -> float:
        """
        Calculate the effectiveness of an attack against the target.
        Currently returns a fixed damage value, but can be expanded to include:
        - Distance-based effectiveness
        - Weapon types and capabilities
        - Target armor/defense
        - Environmental conditions
        - Critical hit chances
        
        Args:
            target: The unit being attacked
            
        Returns:
            float: The calculated damage amount
        """
        # For now, return fixed damage value
        # This is a placeholder for more sophisticated calculations
        base_damage = 10.0
        
        logging.debug(
            f"{self.attacker.attributes.name} calculating attack effectiveness against "
            f"{target.attributes.name}: {base_damage} damage"
        )
        
        return base_damage
        
    def send_damage_to_target(self, target: Unit, damage: float) -> None:
        """
        Apply calculated damage to the target unit.
        
        Args:
            target: The unit receiving the damage
            damage: Amount of damage to apply
        """
        target.take_damage(damage)
        logging.info(f"{self.attacker.attributes.name} dealt {damage} damage to {target.attributes.name}")

    def execute_attack(self, target: Unit) -> None:
        """
        Execute an attack against a specific target.
        
        Args:
            target: The unit to attack
        """
        if self.attacker.has_weapons():
            # Calculate damage
            damage = self.calculate_attack_effectiveness(target)
            # Apply the damage
            self.send_damage_to_target(target, damage)
            logging.info(f"{self.attacker.attributes.name} attacked {target.attributes.name}")
        else:
            logging.warning(f"{self.attacker.attributes.name} has no weapons")
