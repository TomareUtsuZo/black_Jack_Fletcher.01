"""
Game viewmodels package.
Handles state transformation and API responses.
"""

from typing import Dict, List, Any, Optional, Protocol
from ..models import GameState, PlayerState, EntityState

class GameStateTransformer(Protocol):
    """Protocol defining the interface for game state transformation."""
    
    def transform_game_state(self, game_state: GameState) -> Dict[str, Any]:
        """Transform game state for API response."""
        ...

    def transform_player_state(self, player_state: PlayerState) -> Dict[str, Any]:
        """Transform player state for API response."""
        ...

    def transform_entity_state(self, entity_state: EntityState) -> Dict[str, Any]:
        """Transform entity state for API response."""
        ...

class CommandHandler(Protocol):
    """Protocol defining the interface for handling game commands."""
    
    def handle_command(self, command: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle a game command and return response if needed."""
        ... 