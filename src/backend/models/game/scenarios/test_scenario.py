from typing import List, Tuple
import math

from src.backend.models.units.unit import Unit
from src.backend.models.units.test_ships import (
    USS_FLETCHER,
    IJN_YUKIKAZE,
)
from src.backend.models.units.modules.detection import DetectionModule
from src.backend.models.units.modules.attack import Attack
from src.backend.models.units.modules.movement import MovementModule
from src.backend.models.common.geometry.position import Position
from src.backend.models.common.geometry.nautical_miles import NauticalMiles
from src.backend.models.game_state_manager import GameStateManager
from src.backend.models.units.unit import UnitState
from src.backend.models.common.time.game_time import GameTime
from src.backend.models.common.geometry.vincenty import calculate_vincenty_distance


WAKE_X = 166.62
WAKE_Y = 19.29

# ANSI colors (works in most modern terminals including PowerShell 7)
RESET = "\x1b[0m"
COLOR_TIME = "\x1b[36m"      # cyan
COLOR_SEP = "\x1b[34m"       # blue
COLOR_DETECT = "\x1b[96m"    # bright cyan
COLOR_DMG = "\x1b[31m"       # red
COLOR_SINK = "\x1b[91m"      # bright red


def _spec_to_unit(spec) -> Unit:
    return Unit(
        unit_id=spec.unit_id,
        name=spec.name,
        hull_number=spec.hull_number,
        unit_type=spec.unit_type,
        task_force_assigned_to=spec.task_force_assigned_to,
        ship_class=spec.ship_class,
        faction=spec.faction,
        position=spec.position,
        destination=spec.destination,
        max_speed=spec.max_speed,
        cruise_speed=spec.cruise_speed,
        current_speed=spec.current_speed,
        max_health=spec.max_health,
        current_health=spec.current_health,
        max_fuel=spec.max_fuel,
        current_fuel=spec.current_fuel,
        crew=spec.crew,
        tonnage=spec.tonnage,
        visual_range=spec.visual_range,
        visual_detection_rate=spec.visual_detection_rate,
    )


def _nearest_enemy(unit: Unit, enemies: List[Unit]) -> Unit:
    ux, uy = unit.attributes.position.x, unit.attributes.position.y
    best: Tuple[float, Unit] | None = None
    for e in enemies:
        ex, ey = e.attributes.position.x, e.attributes.position.y
        d = (ux - ex) ** 2 + (uy - ey) ** 2
        if best is None or d < best[0]:
            best = (d, e)
    return best[1] if best else enemies[0]


def _label(u: Unit) -> str:
    return f"{u.attributes.name} ({u.attributes.hull_number}) [{u.attributes.faction}]"


def run_test_scenario(max_ticks: int = 60) -> None:
    gsm = GameStateManager.get_instance()

    us_units = [
        _spec_to_unit(USS_FLETCHER),
    ]
    ijn_units = [
        _spec_to_unit(IJN_YUKIKAZE),
    ]

    # Compute separation: 2 nm outside visual ranges for both sides
    # Use the smaller of the two ships' visual ranges for symmetric start
    us_vr = us_units[0].attributes.visual_range.value if us_units else 15.0
    ijn_vr = ijn_units[0].attributes.visual_range.value if ijn_units else 15.0
    min_visual_nm = min(us_vr, ijn_vr)
    start_sep_nm = (min_visual_nm + 2.0) * 2.0  # total gap so each is 2 nm outside own radius
    # Convert nm to degrees of longitude at WAKE_Y
    deg_per_nm_lon = 1.0 / (60.0 * max(math.cos(math.radians(WAKE_Y)), 1e-6))
    sep_deg = start_sep_nm * deg_per_nm_lon

    # Place ships along x-axis centered on WAKE_X
    if us_units:
        us_units[0].attributes.position = Position(WAKE_X + sep_deg / 2.0, WAKE_Y)
    if ijn_units:
        ijn_units[0].attributes.position = Position(WAKE_X - sep_deg / 2.0, WAKE_Y)

    # Attach modules and register
    for u in us_units + ijn_units:
        # Movement
        move = MovementModule()
        move.bind_unit_attributes(u.attributes)
        u.add_module('movement', move)
        u.add_module('detection', DetectionModule(u, gsm))
        u.add_module('attack', Attack(attacker=u))
        gsm._unit_manager.add_unit(u, {  # type: ignore[attr-defined]
            'unit_id': str(u.attributes.unit_id)
        })

    # Assign fixed reciprocal tracks: US westbound, IJN eastbound, with far destinations
    # Destinations are several degrees away to avoid early stopping
    for u in us_units:
        dest = Position(WAKE_X - 5.0, WAKE_Y)  # far west
        u.set_destination(dest)
        u.set_speed(NauticalMiles(20.0))

    for u in ijn_units:
        dest = Position(WAKE_X + 5.0, WAKE_Y)  # far east
        u.set_destination(dest)
        u.set_speed(NauticalMiles(20.0))

    # Run ticks and let units detect/attack via perform_tick
    # Ensure the state machine allows ticks to be processed
    # We avoid starting the real scheduler; just enable processing
    gsm._state_machine.start_game()  # type: ignore[attr-defined]

    # Track health and previous positions to report changes
    prev_health = {u.attributes.unit_id: u.attributes.current_health for u in (us_units + ijn_units)}
    prev_pos = {u.attributes.unit_id: (u.attributes.position.x, u.attributes.position.y) for u in (us_units + ijn_units)}

    for i in range(max_ticks):
        gsm.tick()
        # Show advanced game time after each tick
        print(f"{COLOR_TIME}After tick {i+1}: {gsm.current_time}{RESET}")
        # Update prev_pos silently (no lat/long print)
        for group in (us_units, ijn_units):
            for u in group:
                p = u.attributes.position
                uid = u.attributes.unit_id
                prev_pos[uid] = (p.x, p.y)

        # Show inter-ship separation (Euclidean in game units)
        if us_units and ijn_units:
            ux, uy = us_units[0].attributes.position.x, us_units[0].attributes.position.y
            ex, ey = ijn_units[0].attributes.position.x, ijn_units[0].attributes.position.y
            sep_units = ((ux - ex) ** 2 + (uy - ey) ** 2) ** 0.5
            sep_nm = calculate_vincenty_distance(us_units[0].attributes.position,
                                                 ijn_units[0].attributes.position)
            print(f"{COLOR_SEP}Separation: {sep_units:.6f} game units, {sep_nm.value:.2f} NM{RESET}")

        # Detection evidence
        current_time: GameTime = gsm.current_time
        for force_name, group, enemies in (
            ("US", us_units, ijn_units),
            ("IJN", ijn_units, us_units),
        ):
            for u in group:
                det = u.get_module('detection')
                if det is None:
                    continue
                detected = det.perform_visual_detection(
                    u.attributes.visual_detection_rate,
                    u.attributes.visual_range,
                    current_time,
                )
                if detected:
                    tags = ", ".join(_label(x) for x in detected)
                    print(f"{COLOR_DETECT}{force_name} {_label(u)} detected: {tags}{RESET}")

        # Damage and sinking evidence
        for u in (us_units + ijn_units):
            uid = u.attributes.unit_id
            h_prev = prev_health[uid]
            h_now = u.attributes.current_health
            if h_now < h_prev:
                print(f"{COLOR_DMG}{_label(u)} took damage: {h_prev:.1f} -> {h_now:.1f}{RESET}")
            if u.state == UnitState.SINKING and h_prev > 0 and h_now == 0:
                print(f"{COLOR_SINK}{_label(u)} is SINKING{RESET}")
            prev_health[uid] = h_now


