# New Game Planning

## Overview
This document outlines the steps to implement a 'New Game' feature on the frontend using vanilla TypeScript. When the 'New Game' button is clicked, it should create a new game state via the backend (using src/backend/models/units/test_ships.py for initial units and positions around the islands' location) and transition to a view displaying the islands' location with units represented as small PNG tiles (e.g., images/ship-carrier-launching.png for ships) and simple HTML icons, using Leaflet for simplicity. This is a temporary setup until a more robust system is developed.

## Updated Decisions and Learnings

### Map Implementation
- Use Leaflet for map rendering due to its ease of integration, performance, and community support, focusing solely on displaying island locations as per simplified requirements.

### Unit Representation
- Utilize small PNG tiles (e.g., from the `images/` folder like `ship-carrier-launching.png`) for visualizing units on the map.

### Initial Game States
- Source initial game states from `src/backend/models/units/test_ships.py` as a temporary solution for populating units during new game initialization.

### Frontend Technology
- Stick with vanilla TypeScript for frontend logic, as seen in `src/frontend/views/static/js/main.ts`, to maintain consistency with the existing stack.

### Error Handling and Real-Time Updates
- Implement error handling using try-catch blocks in frontend logic to manage API responses.
- Ensure real-time updates by integrating with backend routes like `/start_game` for game state changes.

### Integration Guidelines
- Follow guidelines from `docs/how_to_access_unit.md` and `docs/how_to_access_time.md` when accessing unit and time modules to enforce restrictions and proper encapsulation.

## Impact of Leaflet on Development
Using Leaflet as our map library has several implications for the development process:
- **Installation**: Leaflet can be added via npm by running `npm install leaflet` in the project root, which will update package.json and make it easy to import in frontend scripts.
- **Integration**: It integrates seamlessly with vanilla TypeScript in src/frontend/views/static/js/main.ts, allowing us to add simple location plotting and unit displays with minimal code. For edge cases, implement basic error handling (e.g., try-catch for API calls) and real-time updates (e.g., via event listeners for game state changes).
- **Benefits**: Reduces custom coding needs, focuses on essential interactivity, and enhances performance, while vanilla TypeScript keeps the setup lightweight.
- **Potential Drawbacks**: May require manual handling of state in TypeScript, but this is manageable for the current scope.
- **Development Workflow**: Using vanilla TypeScript streamlines Tasks 3 and 4, with edge cases like errors handled through standard practices (e.g., logging) and real-time logic added as needed.

## Task List
1. **Create a new planning document**  
   - **Status:** Completed  
   - **Description:** This document outlines the steps for launching a new game from the frontend, including creating a new game state using src/backend/models/units/test_ships.py for initial units and positions, and transitioning to a view with the islands' location and units.  
   - **Dependencies:** None

2. **Verify and implement backend API endpoint**  
   - **Status:** Pending  
   - **Description:** Verify and implement a backend API endpoint in src/backend/app.py or routes to handle new game initialization, using src/backend/models/units/test_ships.py to set the initial game state with units and positions around the island's location.  
   - **Dependencies:** Task 1

3. **Add frontend UI elements**  
   - **Status:** Pending  
   - **Description:** Add frontend UI elements in src/frontend/views/templates/index.html or components to include a 'New Game' button that sends a request to the backend endpoint and transitions to a view plotting the islands' location using Leaflet, with units as PNG tiles (e.g., images/ship-carrier-launching.png).  
   - **Dependencies:** Task 2

4. **Implement frontend logic**  
   - **Status:** Pending  
   - **Description:** Implement frontend logic in src/frontend/views/static/js/main.ts (using vanilla TypeScript) to handle the backend response, plot the islands' location with units using Leaflet, and manage basic edge cases like error handling.  
   - **Dependencies:** Task 3

5. **Test the end-to-end flow**  
   - **Status:** Pending  
   - **Description:** Test the end-to-end flow to ensure starting a new game from the frontend successfully creates a new game state, transitions to the view, and displays units at the islands' location using Leaflet, including tests for edge cases like errors or updates.  
   - **Dependencies:** Task 4

## Resolved Questions Summary
For reference, all open questions have been resolved as follows:
1. What library or technology should be used for the map view? (Using Leaflet.)
2. How should units be represented on the map? (Using small PNG tiles like images/ship-carrier-launching.png for ships, combined with simple HTML icons.)
3. What should the initial game state include? (Using src/backend/models/units/test_ships.py as a temporary solution for units and positions.)
4. What frontend framework or tech stack should be used? (Using vanilla TypeScript to build on existing setup for simplicity.)
5. Are there any edge cases? (Handle with basic try-catch for errors and simple event-based updates if needed, keeping it minimal for now.) 