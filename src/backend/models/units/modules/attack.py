import logging  # Import for logging errors or events
from typing import List, Optional
import numpy as np
from src.backend.models.units.unit import Unit, UnitState
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
        Calculate the effectiveness of an attack against the target based on range and normal distribution.
        
        The damage calculation follows these rules:
        1. At 1nm or less: Normal distribution of base damage with 25% standard deviation
        2. At optimal range: Normal distribution with 20% of base damage
        3. Linear interpolation between these points
        
        Args:
            target: The unit being attacked
            
        Returns:
            float: The calculated damage amount
        """
        # Get the distance to target
        distance = self.attacker.attributes.position.distance_to(target.attributes.position)
        base_damage = self.attacker.attributes.base_damage
        optimal_range = self.attacker.attributes.optimal_range.value
        
        # Calculate standard deviation based on range
        if distance <= 1.0:  # Within 1 nautical mile
            # Full damage with 25% standard deviation at close range
            mean_damage = base_damage
            std_dev = base_damage * 0.25
        elif distance >= optimal_range:  # At or beyond optimal range
            # 20% of base damage at optimal range and beyond
            mean_damage = base_damage * 0.2  # Reduced to 20% of base damage
            std_dev = base_damage * 0.25  # Keep same absolute std dev as close range
            # This means at long range, the variation is relatively larger compared to mean damage
        else:
            # Linear interpolation between 1nm and optimal range
            range_factor = (distance - 1.0) / (optimal_range - 1.0)
            # Interpolate between full damage at close range and 20% at optimal range
            mean_damage = base_damage * (1.0 - range_factor * 0.8)  # Linear reduction from 100% to 20%
            std_dev = mean_damage * 0.25  # Keep same relative std dev
            
        # Generate damage using normal distribution
        damage = float(np.random.normal(mean_damage, std_dev))
        
        # Ensure damage is not negative
        damage = max(0.0, damage)
        
        logging.debug(
            f"{self.attacker.attributes.name} attacking {target.attributes.name} "
            f"at range {distance:.1f}nm: {damage:.1f} damage "
            f"(mean: {mean_damage:.1f}, std: {std_dev:.1f})"
        )
        
        return damage
        
    def determine_damage_effectiveness(self, target: Unit, base_damage: float) -> float:
        """
        Determine the final damage effectiveness against the target.
        This will eventually consider factors like:
        - Armor effectiveness
        - Range penalties
        - Weather effects
        - Time of day modifiers
        
        Args:
            target: The unit being attacked
            base_damage: The initial damage amount to be modified
            
        Returns:
            float: The final calculated damage amount before critical hits
        """
        # For now, just return the base damage
        # This is a placeholder for more sophisticated calculations
        return base_damage
        
    def check_for_critical_result(self, target: Unit, base_damage: float) -> None:
        """
        Check if the attack results in a critical hit and apply additional effects.
        This will eventually consider factors like:
        - Critical hit chances based on weapon type
        - Target vulnerabilities
        - Special ammunition effects
        - Crew skill levels
        - Equipment status
        
        Args:
            target: The unit being attacked
            base_damage: The initial damage amount that may trigger critical effects
        """
        # For now, just pass
        # This is a placeholder for future critical hit system
        pass

    def send_damage_to_target(self, target: Unit, damage: float) -> None:
        """
        Send calculated damage to the target unit.
        This method focuses solely on the attacking unit's perspective - what damage it sends out.
        The actual effects of the damage (internal damage, crew effects, critical hits, etc.) 
        are handled by determining effectiveness and applying it to the target.
        
        TODO: This method will need to be updated when the damage system is fully defined.
        Future considerations:
        - Different damage types (kinetic, explosive, etc.)
        - Weapon characteristics (penetration, blast radius)
        - Range and accuracy effects
        - Environmental modifiers (weather, time of day)
        - Weapon reliability and maintenance state
        
        Args:
            target: The unit receiving the damage
            damage: Amount of damage to apply (currently a simple float value)
        """ 
        target.take_damage(damage)  # Use take_damage to ensure proper state transitions
        logging.info(f"{self.attacker.attributes.hull_number} attacked {target.attributes.hull_number} for {damage:g} damage")
        
    def attack(self, target: Unit) -> None:
        """
        Execute an attack against the target unit.
        This method ties together the damage calculation and application process.
        
        Args:
            target: The unit to attack
        """
        # Calculate damage based on range and other factors
        damage = self.calculate_attack_effectiveness(target)
        
        # Check for critical hits (currently a placeholder)
        self.check_for_critical_result(target, damage)
        
        # Apply the damage to the target
        self.send_damage_to_target(target, damage)
        
        # Perform any necessary post-attack upkeep
        self.perform_upkeep()
    
    def perform_upkeep(self) -> None:
        """
        Perform any necessary upkeep after an attack.
        This could include:
        - Resetting cooldowns
        - Updating ammunition counts
        - Applying weapon wear and tear (equipment failures, and crew exaustion, maybe.)
        - Updating combat statistics
        """
        # Currently a placeholder for future implementation
        logging.debug(f"{self.attacker.attributes.name} performing attack upkeep")