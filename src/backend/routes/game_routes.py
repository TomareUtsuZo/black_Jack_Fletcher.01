"""
Game routes module.
Handles HTTP and WebSocket routes for the game.
"""

from typing import Dict, Any
from flask import Blueprint, render_template, jsonify, request, Response
from flask_socketio import emit, join_room, leave_room
from ..models import GameState, PlayerState
from ..services.game_service import game_manager

game_routes: Blueprint = Blueprint('game', __name__)

@game_routes.route('/')
def index() -> str:
    """Render the main game page."""
    return render_template('index.html')

@game_routes.route('/api/game/status')
def get_game_status() -> Response:
    """Get the current game status."""
    return jsonify({
        'state': game_manager.game_state.name,
        'is_paused': game_manager.is_paused,
        'current_time': str(game_manager.current_time),
        'time_rate': str(game_manager.time_rate)
    })

@game_routes.route('/api/game/pause', methods=['POST'])
def pause_game() -> Response:
    """Pause the game."""
    game_manager.pause()
    return jsonify({'status': 'paused'})

@game_routes.route('/api/game/unpause', methods=['POST'])
def unpause_game() -> Response:
    """Unpause the game."""
    game_manager.unpause()
    return jsonify({'status': 'running'})

@game_routes.route('/api/game/time-rate', methods=['POST'])
def set_time_rate() -> Response:
    """Set the game time rate."""
    data = request.get_json()
    if 'minutes' in data:
        game_manager.set_time_rate_minutes(float(data['minutes']))
    elif 'seconds' in data:
        game_manager.set_time_rate_seconds(float(data['seconds']))
    return jsonify({
        'time_rate': str(game_manager.time_rate)
    })

@game_routes.route('/api/game/<game_id>')
def get_game_state(game_id: str) -> Response:
    """Get the current state of a game."""
    # Implementation will be added later
    return jsonify({'game_id': game_id})

@game_routes.route('/api/game', methods=['POST'])
def create_game() -> Response:
    """Create a new game."""
    # Implementation will be added later
    return jsonify({'status': 'created'})

@game_routes.route('/api/game/<game_id>/join', methods=['POST'])
def join_game(game_id: str) -> Response:
    """Join an existing game."""
    # Implementation will be added later
    return jsonify({'status': 'joined'}) 