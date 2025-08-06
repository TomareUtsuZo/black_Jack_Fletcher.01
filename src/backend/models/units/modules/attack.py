import logging  # Import for logging errors or events

# Define a basic Attack class for handling combat logic
class Attack:
    def __init__(self, attacker, target, damage=10):  # Initialize with attacker, target, and default damage
        self.attacker = attacker  # The unit performing the attack
        self.target = target  # The unit being attacked
        self.damage = damage  # Amount of damage to apply
        
    def perform_attack(self):  # Method to execute the attack
        # Check if attacker can attack (simple condition for now)
        if self.attacker.is_active():  # Assume is_active method exists in unit interface
            self.target.apply_damage(self.damage)  # Apply damage to target
            logging.info(f"{self.attacker.name} attacked {self.target.name} for {self.damage} damage")  # Log the attack event
        else:
            logging.warning(f"{self.attacker.name} cannot attack")  # Warn if attacker is not active