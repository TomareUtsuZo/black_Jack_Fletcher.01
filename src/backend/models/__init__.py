"""
Game models package.
Contains core game state and business logic.
"""

from typing import Dict, List, Optional, TypedDict, Union

# Common type definitions
class Position(TypedDict):
    x: int
    y: int

class PlayerState(TypedDict):
    id: str

class GameState(TypedDict):
    id: str
    players: Dict[str, PlayerState]