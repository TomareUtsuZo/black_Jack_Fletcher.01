"""
Game routes module.
Handles HTTP and WebSocket routes for the game.
"""

from typing import Dict, Any
from flask import Blueprint, render_template, jsonify, request, Response
from flask_socketio import emit, join_room, leave_room
from ..models.game_state_manager import GameStateManager, GameState
from ..services.game_service import game_manager
from src.backend.models.units.test_ships import get_all_test_ships
import logging  # Import logging for debugging
from threading import Lock

game_routes: Blueprint = Blueprint('game', __name__)
start_game_lock = Lock()  # Self-comment: Lock to prevent concurrent start_game requests

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

@game_routes.route('/start_game', methods=['POST'])
def start_game():
    # Acquire lock to prevent concurrent requests
    if not start_game_lock.acquire(blocking=False):
        logging.info('Another start_game request is in progress, returning...')
        return jsonify({"status": "Game start already in progress"}), 200

    try:
        logging.info('Received POST request to /start_game')
        gsm = GameStateManager.get_instance()
        current_state = gsm.game_state
        logging.info(f'Current game state before reset: {current_state}')
        
        # Always reset state for a new game
        logging.info('Resetting game state...')
        gsm.reset_state()
        logging.info(f'Game state after reset: {gsm.game_state}')
        
        # Start the game
        logging.info('Starting new game...')
        gsm.start()
        logging.info(f'Game started successfully. Current state: {gsm.game_state}')
        return jsonify({"status": "New game started successfully"}), 200
            
    except Exception as e:
        error_msg = f'Error in start_game: {str(e)}'
        logging.error(error_msg)
        return jsonify({"error": error_msg}), 500
    finally:
        # Always release the lock
        start_game_lock.release()
        logging.info('Released start_game lock') 