/**
 * Main TypeScript entry point for the game frontend.
 * 
 * Future implementations will include:
 * - Game state management
 * - WebSocket communication with backend
 * - MVVM pattern implementation
 * - UI component initialization
 */

// Declare L as a global variable from the Leaflet CDN
declare var L: any;

console.log('Game frontend initialized');

document.addEventListener('DOMContentLoaded', () => {
    const newGameButton = document.getElementById('new-game-button') as HTMLButtonElement;
    if (newGameButton) {
        newGameButton.addEventListener('click', () => {
            // Disable button to prevent double-clicks
            newGameButton.disabled = true;
            console.log('New Game button clicked - Initiating process');
            fetch('/start_game', { method: 'POST' })
                .then(response => {
                    console.log('API response received:', response.status);
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
                        gameBoard.innerHTML = '<h2>Map View Loaded</h2><div id="map" style="height: 400px;"></div>';
                        try {
                            const map = L.map('map').setView([51.505, -0.09], 13);
                            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                            }).addTo(map);
                        } catch (mapError) {
                            console.error('Error initializing Leaflet map:', mapError);
                        }
                    } else {
                        console.error('Error: Game board element not found');
                    }
                })
                .catch(error => {
                    console.error('Fetch error details:', error.message, error.stack);
                })
                .finally(() => {
                    // Re-enable button after request completes (success or failure)
                    newGameButton.disabled = false;
                });
        });
    } else {
        console.error('Error: New Game button element not found in DOM');
    }
}); 