"use strict";
/**
 * Main TypeScript entry point for the game frontend.
 *
 * Future implementations will include:
 * - Game state management
 * - WebSocket communication with backend
 * - MVVM pattern implementation
 * - UI component initialization
 */
Object.defineProperty(exports, "__esModule", { value: true });
var L = require("leaflet"); // Self-comment: Imports Leaflet to make the L object available and fix linter errors
console.log('Game frontend initialized');
document.addEventListener('DOMContentLoaded', function () {
    if (typeof L === 'undefined') {
        console.error('Leaflet is not loaded'); // Self-comment: Check if Leaflet is available globally
    }
    var newGameButton = document.getElementById('new-game-button');
    if (newGameButton) {
        newGameButton.addEventListener('click', function () {
            console.log('New Game button clicked - Initiating process');
            fetch('/start_game', { method: 'POST' })
                .then(function (response) {
                console.log('API response received:', response.status); // Self-comment: Log the full response object for debugging
                if (response.ok) {
                    return response.json();
                }
                else {
                    console.error('API error: Response not OK', response.status, response.statusText);
                    throw new Error('Failed to start game');
                }
            })
                .then(function (data) {
                console.log('Game started data:', data); // Self-comment: Log the data object in detail
                var gameBoard = document.getElementById('game-board');
                if (gameBoard) {
                    gameBoard.innerHTML = '<h2>Map View Loaded</h2><div id="map" style="height: 400px;"></div>';
                    console.log('Map container created in DOM');
                    try {
                        var map = L.map('map').setView([51.505, -0.09], 13);
                        console.log('Leaflet map object created:', map); // Self-comment: Log the map object for verification
                        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        }).addTo(map);
                        console.log('Tile layer added to map successfully');
                    }
                    catch (mapError) {
                        console.error('Error initializing Leaflet map:', mapError); // Self-comment: Catch and log any map initialization errors
                    }
                }
                else {
                    console.error('Error: Game board element not found');
                }
            })
                .catch(function (error) {
                console.error('Fetch error details:', error.message, error.stack); // Self-comment: Log detailed error information
            });
        });
    }
    else {
        console.error('Error: New Game button element not found in DOM'); // Self-comment: Log if the button itself is missing
    }
});
