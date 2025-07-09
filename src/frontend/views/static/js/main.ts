/**
 * Main TypeScript entry point for the game frontend.
 * 
 * Future implementations will include:
 * - Game state management
 * - WebSocket communication with backend
 * - MVVM pattern implementation
 * - UI component initialization
 */

console.log('Game frontend initialized');

document.addEventListener('DOMContentLoaded', () => {
    const newGameButton = document.getElementById('new-game-button');
    if (newGameButton) {
        newGameButton.addEventListener('click', () => {
            console.log('New Game button clicked - Initiating process');
            fetch('/start_game', { method: 'POST' })
                .then(response => {
                    console.log('API response received:', response.status);  // Self-comment: Log the full response object for debugging
                    if (response.ok) {
                        return response.json();
                    } else {
                        console.error('API error: Response not OK', response.status, response.statusText);
                        throw new Error('Failed to start game');
                    }
                })
                .then(data => {
                    console.log('Game started data:', data);
                    const gameBoard = document.getElementById('game-board');
                    if (gameBoard) {
                        gameBoard.innerHTML = '<h2>Map View Loaded</h2>';
                    } else {
                        console.error('Error: Game board element not found');
                    }
                })
                .catch(error => {
                    console.error('Fetch error details:', error.message, error.stack);  // Self-comment: Log detailed error information
                });
        });
    } else {
        console.error('Error: New Game button element not found in DOM');  // Self-comment: Log if the button itself is missing
    }
}); 