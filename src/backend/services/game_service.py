"""
Game service module.
Provides centralized access to the game state manager.
"""

from ..models.game_state_manager import GameStateManager

# Global game manager instance
game_manager: GameStateManager = GameStateManager() 