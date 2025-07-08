# New Game Planning

## Overview
This document outlines the steps to implement a 'New Game' feature on the frontend, allowing users to start a new game and transition to a map view of the ocean around Midway Island.

## Task List
1. **Create a new planning document**  
   - **Status:** In Progress  
   - **Description:** Create this document to outline the steps for launching a new game from the frontend and transitioning to the map view.  
   - **Dependencies:** None

2. **Verify and implement backend API endpoint**  
   - **Status:** Pending  
   - **Description:** Verify and implement a backend API endpoint in src/backend/app.py or routes to handle new game initialization, ensuring it updates the GameStateManager appropriately.  
   - **Dependencies:** Task 1

3. **Add frontend UI elements**  
   - **Status:** Pending  
   - **Description:** Add frontend UI elements in src/frontend/views/templates/index.html or components to include a 'New Game' button that sends a request to the backend endpoint.  
   - **Dependencies:** Task 2

4. **Implement frontend logic**  
   - **Status:** Pending  
   - **Description:** Implement frontend logic in src/frontend/views/static/js/main.ts to handle the response from the backend and transition to the map view, fetching necessary game state data.  
   - **Dependencies:** Task 3

5. **Test the end-to-end flow**  
   - **Status:** Pending  
   - **Description:** Test the end-to-end flow to ensure starting a new game from the frontend successfully transitions to the map view and reflects the game state.  
   - **Dependencies:** Task 4 