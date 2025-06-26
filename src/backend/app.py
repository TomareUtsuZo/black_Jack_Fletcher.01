"""
Main Flask application entry point.
Sets up the Flask app with SocketIO and configures routes.
"""

from typing import Any
from flask import Flask
from flask_socketio import SocketIO
import os

# Get the absolute path to the frontend directory
frontend_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app: Flask = Flask(__name__,
           template_folder=os.path.join(frontend_dir, 'views', 'templates'),
           static_folder=os.path.join(frontend_dir, 'views', 'static'))
socketio: SocketIO = SocketIO(app)

# Import routes after app creation to avoid circular imports
from src.backend.routes.game_routes import game_routes

app.register_blueprint(game_routes)

if __name__ == '__main__':
    socketio.run(app, debug=True) 