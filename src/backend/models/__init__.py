"""
Game models package.
Contains core game state and business logic.
"""

from typing import Dict, List, Optional, TypedDict, Union

# Common type definitions
class Position(TypedDict):
    x: int
    y: int

class EntityState(TypedDict):
    id: str
    position: Position
    state: str

class PlayerState(TypedDict):
    id: str
    resources: Dict[str, int]
    entities: List[EntityState]
    status: str

class GameState(TypedDict):
    id: str
    players: Dict[str, PlayerState]
    current_turn: str
    phase: str
    timestamp: float 