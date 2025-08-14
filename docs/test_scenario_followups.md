### Test scenario follow-ups and recommended tasks

This document captures issues observed in `test_scenario` runs and the recommended work items to improve fidelity, clarity, and test coverage.

### Observations from current scenario output

- **Stop-on-sink missing**: Units continue moving/engaging after reaching sinking conditions.
- **State/health gating not enforced everywhere**: Movement, detection, and attack sometimes process for units that should be disabled (sinking or health ≤ 0).
- **Detection vs. attack inconsistency**: We sometimes log detections the same tick a side reports “no legitimate targets.”
- **Initial separation derivation**: The observed initial separation (~13 NM) implies `visual_range` differs from assumptions; ensure start gap is truly 2 NM outside each side’s effective range.
- **Logging signal-to-noise**: Mixed INFO logs from modules interleave with scenario output; separation shown in both “game units” and NM (NM is sufficient).

### Recommended changes (implementation)

- **Stop-on-sink behavior**
  - On transition to `UnitState.SINKING` (health ≤ 0):
    - Set speed to 0; clear destination.
    - Mark unit as non-participating for movement, detection, and attack.
    - Optionally schedule removal from `UnitManager` after a grace period.

- **State/health gating**
  - **Movement**: In `MovementModule.update`, early-return if unit state is `SINKING` or health ≤ 0.
  - **Attack**: Attacker must not attack if state is `SINKING` or health ≤ 0. Exclude targets that are `SINKING` or health ≤ 0.
  - **Detection**: Do not emit detections for units that are `SINKING` or health ≤ 0; do not include such units as detectable targets.

- **Align detection and targeting**
  - Ensure “legitimate targets” logic is consistent with detection results and weapon range/arc constraints.
  - If detection has probabilistic elements, surface the probability/threshold in logs for transparency or make it deterministic for the scenario test.

- **Initial geometry and range**
  - Confirm `visual_range` for each `test_ships` spec and compute the start separation as exactly (visual_range + 2 NM) per side on reciprocal tracks.
  - Keep conversion consistent with latitude scaling (lon degrees scaled by cos(latitude)).

- **Scenario logging**
  - Prefer NM-only separation (drop “game units”).
  - Group per-tick outputs in this order for readability: time → separation → detections → attacks/damage → sinking/removal.
  - Colorize only high-signal items (time, separation, detections, damage, sinking) as currently implemented.

### Tests to add (unit/integration)

- **Movement conversion**
  - Given latitude Y and distance D nm at bearing B, verify updated position reflects correct degrees delta (lon uses cos(Y)).

- **Stop-on-sink**
  - When health transitions to 0, assert speed becomes 0, destination clears, movement/attack/detection are disabled, and optional removal is scheduled.

- **Gating by state/health**
  - Movement update ignored for `SINKING`/0-health units.
  - Attack cannot originate from `SINKING`/0-health units; such targets are excluded.
  - Detection excludes `SINKING`/0-health units as sources and targets.

- **Detection threshold/regression**
  - Around visual range (±ε): detections just outside range should be none; just inside should be present (deterministically for test).

- **Scenario-level assertions**
  - With 20 kt each on reciprocal tracks: closure ≈ 0.67 NM/min (within tolerance).
  - Crossing occurs within N ticks; separation exceeds 30 NM by M ticks (tunable bounds).

### Acceptance criteria (per item)

- Stop-on-sink: movement, detection, attack do not fire post-sink; speed 0; destination None; sinking log emitted once.
- Gating: module methods short-circuit; no detections/attacks logged for `SINKING`/0-health.
- Detection/attack alignment: No tick reports “no legitimate targets” when detections for the same pair are logged; decisions are consistent.
- Geometry: Start separation matches 2 NM outside each side’s visual radius (validated via NM prints).
- Logging: Per-tick output is ordered and minimal; distances shown only in NM.
- Tests: New unit/integration tests pass and guard against regressions.

### Next steps (suggested order)

1. Implement stop-on-sink and module gating (movement/attack/detection) in `Unit`, `MovementModule`, `Attack`, and `DetectionModule`.
2. Align detection and “legitimate target” selection; make scenario detection deterministic.
3. Adjust scenario start separation using actual `visual_range` from `test_ships`.
4. Tidy logging (drop game units; maintain colorized high-signal lines).
5. Add the proposed tests and run full suite.

Related files: `src/backend/models/units/unit.py`, `src/backend/models/units/modules/movement.py`, `src/backend/models/units/modules/attack.py`, `src/backend/models/units/modules/detection.py`, `src/backend/models/game/scenarios/test_scenario.py`.


