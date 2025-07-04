"""
Main Flask application entry point.
Sets up the Flask app with SocketIO and configures routes.
"""

from typing import Any
from flask import Flask
from flask_socketio import SocketIO
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))  # Add project root to PATH
from src.backend.services.game_service import game_manager

# Get the absolute path to the frontend directory
frontend_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app: Flask = Flask(__name__,
           template_folder=os.path.join(frontend_dir, 'views', 'templates'),
           static_folder=os.path.join(frontend_dir, 'views', 'static'))
socketio: SocketIO = SocketIO(app, async_mode='threading')

# Import routes after app creation to avoid circular imports
from src.backend.routes.game_routes import game_routes

app.register_blueprint(game_routes)

def start_game_manager() -> None:
    """Start the game manager if we're in the main process."""
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or os.environ.get('FLASK_ENV') != 'development':
        game_manager.start()

def cleanup_game_manager() -> None:
    """Clean up the game manager if we're in the main process."""
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or os.environ.get('FLASK_ENV') != 'development':
        game_manager.stop()

if __name__ == '__main__':
    try:
        # Set environment to production to disable reloader
        os.environ['FLASK_ENV'] = 'production'
        start_game_manager()
        socketio.run(app, host='127.0.0.1', port=5000)
    finally:
        cleanup_game_manager() 