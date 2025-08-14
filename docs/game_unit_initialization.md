# Game Unit Initialization: Step-by-Step Plan

This document outlines a pragmatic, three-step process to stand up playable scenarios, from a fast, code-based setup to JSON-driven scenarios and minimal HTTP control.

## Step 1: Code-based Wake Island Scenario (fast path)

Goal: Use `test_ships` to set up opposing forces around Wake Island and drive them toward each other, logging detection events, attacks, and sinking.

Estimated effort: 30–90 minutes

Implementation steps:
1. Create `src/backend/models/game/scenarios/wake_battle.py` and a function `run_wake_battle(max_ticks: int = 60)`.
   - Wake Island approx coords: `WAKE_X = 166.62`, `WAKE_Y = 19.29`.
   - Import ships from `src.backend.models.units.test_ships` (e.g., `USS_FLETCHER`, `IJN_YUKIKAZE`).
   - Convert each `ShipSpecification` to a `Unit` (preserve tonnage as int; copy speed/health/faction/position).
2. Wire modules per unit:
   - Detection: `unit.add_module('detection', DetectionModule(unit, gsm))` so each unit can detect enemies.
   - Attack: optionally pre-attach `Attack(attacker=unit)`; `Unit.perform_attack` will lazily create it if missing.
3. Register units with the runtime:
   - `gsm = GameStateManager.get_instance()` and add units to the unit manager (internal helper or direct if available).
4. Movement setup:
   - For each unit, set a destination roughly toward the nearest enemy (simple nearest-neighbor using positions) and set a reasonable speed (`NauticalMiles(10.0)` default).
5. Event logging (telemetry):
   - After each `gsm.tick()`, for each unit:
     - Invoke its detection module to list detected enemies and log detections.
     - Compare previous health/state to current; log any damage events and transitions to SINKING.
   - Maintain a simple in-memory event list for test assertions or console output.
6. Runner loop:
   - For `t` in `range(max_ticks)`: call `gsm.tick()` then perform the event logging above.

Acceptance criteria:
- Units from `test_ships` are spawned near Wake and registered.
- Units move toward each other; detections occur once within range; attacks apply damage; SINKING triggers at 0 health.
- Logs (or a captured event list) include detection, attack, and sinking events across ticks without errors.

## Step 2: DTO/JSON Scenario Loading

Goal: Define scenarios as JSON (DTOs) and load them into the game at runtime using the existing schema scaffolding.

Estimated effort: 2–4 hours

Implementation steps:
1. Define/confirm DTO schema in `scenario_schema.py` (minimal fields):
   - Units: type, hull number, ship class, faction, position (x, y), optional destination/speed.
   - Optional: starting modules, time rate.
2. Implement `scenario_loader.py`:
   - Parse JSON into DTOs.
   - Map DTOs to `UnitFactory` calls to build `Unit` instances.
   - Attach default modules (detection, attack); ensure module `initialize()` is called.
   - Register units into GSM/UnitManager.
3. Add validation:
   - Schema validation (types, required fields).
   - Semantic checks (valid unit type, numeric ranges where applicable).
4. Tests:
   - Unit tests for loader: valid file -> units created and registered.
   - Negative tests: missing fields, bad types -> clear error.

Acceptance criteria:
- A sample JSON scenario loads successfully and produces the same result as Step 1.
- Invalid JSON is rejected with actionable errors.

## Step 3: Minimal HTTP Endpoints (optional control layer)

Goal: Expose simple endpoints to load/start/pause scenarios without a frontend.

Estimated effort: 2–3 hours

Implementation steps:
1. Introduce a minimal routes module (e.g., `routes/game_routes.py`):
   - `POST /api/scenario/load` body: scenario JSON or file reference -> calls Step 2 loader.
   - `POST /api/game/start` -> `GameStateManager.start()`
   - `POST /api/game/pause` / `POST /api/game/unpause`
   - `GET /api/game/state` -> returns current game time/state summary.
2. Register the blueprint in `app.py` (keep it minimal and decoupled from core logic).
3. Tests:
   - Route-level tests that mock loader/GSM and assert status codes and side effects.

Acceptance criteria:
- Scenarios can be loaded and the simulation started/paused via HTTP.
- No tight coupling of app routes to domain logic (all orchestration remains in GSM/loader).

---

## References
- `src/backend/services/unit_factory.py` — standardized unit creation
- `src/backend/models/game_state_manager.py` — orchestration (`tick`, start/pause)
- `src/backend/models/units/unit.py` — unit composition and module management
- `src/backend/models/units/modules/attack.py`, `.../detection.py` — combat/detection modules
- `src/backend/models/game/scenarios/` — recommended location for scenario code/loader

## Notes
- Keep Step 1 small and runnable in tests; it serves as a golden baseline for Step 2.
- Step 2/3 should reuse Step 1 building blocks; avoid duplicating creation logic.
