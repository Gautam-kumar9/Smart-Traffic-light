"""
Run a SUMO simulation controlled by the project's fuzzy traffic controller.

Usage:
  python sumo_fuzzy_simulation.py
  python sumo_fuzzy_simulation.py --gui
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

import traci
from traci.exceptions import FatalTraCIError

from fuzzy_controller import FuzzyTrafficController


PROJECT_DIR = Path(__file__).resolve().parent
SCENARIO_DIR = PROJECT_DIR / "sumo_scenario"
SUMO_CONFIG = SCENARIO_DIR / "intersection.sumocfg"


def classify_lane_direction(lane_shape):
    """Classify lane approach as NS or EW using lane geometry."""
    if not lane_shape or len(lane_shape) < 2:
        return "EW"

    x0, y0 = lane_shape[0]
    x1, y1 = lane_shape[-1]
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    return "EW" if dx >= dy else "NS"


def get_phase_mapping(tls_id):
    """Infer which TLS phases primarily serve NS and EW movements."""
    controlled_links = traci.trafficlight.getControlledLinks(tls_id)

    signal_direction = []
    for signal_links in controlled_links:
        direction = "EW"
        if signal_links:
            in_lane = signal_links[0][0]
            lane_shape = traci.lane.getShape(in_lane)
            direction = classify_lane_direction(lane_shape)
        signal_direction.append(direction)

    logic = traci.trafficlight.getAllProgramLogics(tls_id)[0]
    phases = logic.phases

    ns_phase = 0
    ew_phase = 0
    best_ns = -1
    best_ew = -1

    for phase_index, phase in enumerate(phases):
        state = phase.state
        ns_green = 0
        ew_green = 0

        for i, signal_state in enumerate(state):
            if signal_state in ("g", "G"):
                if i < len(signal_direction) and signal_direction[i] == "NS":
                    ns_green += 1
                else:
                    ew_green += 1

        if ns_green > best_ns:
            best_ns = ns_green
            ns_phase = phase_index
        if ew_green > best_ew:
            best_ew = ew_green
            ew_phase = phase_index

    return ns_phase, ew_phase


def get_yellow_phase_after(tls_id, phase_index):
    """Return immediate yellow-transition phase after a main phase if available."""
    logic = traci.trafficlight.getAllProgramLogics(tls_id)[0]
    phases = logic.phases
    next_idx = (phase_index + 1) % len(phases)
    next_state = phases[next_idx].state
    if "y" in next_state.lower():
        return next_idx
    return None


def get_directional_queues(tls_id):
    """Estimate queue pressure near a TLS by grouping incoming lanes into NS/EW."""
    incoming_lanes = set(traci.trafficlight.getControlledLanes(tls_id))
    ns_queue = 0
    ew_queue = 0

    for lane_id in incoming_lanes:
        lane_shape = traci.lane.getShape(lane_id)
        direction = classify_lane_direction(lane_shape)
        halted = traci.lane.getLastStepHaltingNumber(lane_id)

        if direction == "NS":
            ns_queue += halted
        else:
            ew_queue += halted

    return ns_queue, ew_queue


def get_time_slot_from_hour(hour):
    """Match project time-slot definition from traffic_simulator.py."""
    if 23 <= hour or hour < 5:
        return 0  # night
    if 7 <= hour < 10:
        return 2  # morning_peak
    if 17 <= hour < 20:
        return 3  # evening_peak
    return 1  # normal


def setup_gui_view(tls_id):
    """Center and zoom the SUMO GUI around the controlled intersection."""
    try:
        view_ids = traci.gui.getIDList()
        if not view_ids:
            return
        view_id = view_ids[0]
        x, y = traci.junction.getPosition(tls_id)
        traci.gui.setOffset(view_id, x, y)
        traci.gui.setZoom(view_id, 1800)
    except Exception:
        # Keep simulation robust even if GUI API varies by SUMO version.
        pass


def run_sumo_fuzzy(gui=False, duration_seconds=900, start_hour=8, is_weekday=True, delay_ms=120):
    if not SUMO_CONFIG.exists():
        raise FileNotFoundError(f"Missing SUMO config: {SUMO_CONFIG}")

    sumo_binary = "sumo-gui" if gui else "sumo"
    sumo_cmd = [
        sumo_binary,
        "-c",
        str(SUMO_CONFIG),
        "--start",
        "--quit-on-end",
    ]

    if gui:
        sumo_cmd.extend(["--delay", str(max(0, int(delay_ms)))])

    traci.start(sumo_cmd)

    try:
        fuzzy = FuzzyTrafficController()
        tls_ids = list(traci.trafficlight.getIDList())
        if not tls_ids:
            raise RuntimeError("No traffic lights found in SUMO network.")

        # Pick the most connected signal (usually the central intersection in grid networks).
        tls_id = max(tls_ids, key=lambda tid: len(set(traci.trafficlight.getControlledLanes(tid))))
        ns_phase, ew_phase = get_phase_mapping(tls_id)
        ns_yellow_phase = get_yellow_phase_after(tls_id, ns_phase)
        ew_yellow_phase = get_yellow_phase_after(tls_id, ew_phase)

        if gui:
            setup_gui_view(tls_id)

        current_time = datetime(2026, 4, 9, start_hour, 0, 0)
        next_decision_time = 0
        active_direction = None
        pending_switch = None
        same_direction_count = 0
        max_same_direction = 3
        yellow_transition_seconds = 3

        print(f"Using TLS: {tls_id}")
        print(f"NS phase index: {ns_phase} | EW phase index: {ew_phase}")
        print(f"NS yellow: {ns_yellow_phase} | EW yellow: {ew_yellow_phase}")
        print("Legend: dir=selected direction, ns_q/ew_q=halted vehicles, density=queue-based density")
        print("Running fuzzy SUMO control...")

        while traci.simulation.getMinExpectedNumber() > 0:
            try:
                traci.simulationStep()
            except FatalTraCIError:
                print("SUMO GUI was closed. Ending simulation cleanly.")
                break
            sim_time = int(traci.simulation.getTime())

            if sim_time > duration_seconds:
                break

            if pending_switch and sim_time >= next_decision_time:
                target_phase = pending_switch["target_phase"]
                target_direction = pending_switch["target_direction"]
                target_green = pending_switch["target_green"]
                ns_queue = pending_switch["ns_queue"]
                ew_queue = pending_switch["ew_queue"]
                active_density = pending_switch["active_density"]

                traci.trafficlight.setPhase(tls_id, target_phase)
                traci.trafficlight.setPhaseDuration(tls_id, max(10, int(target_green)))

                next_decision_time = sim_time + max(10, int(target_green))
                current_time += timedelta(seconds=max(10, int(target_green)))

                if active_direction == target_direction:
                    same_direction_count += 1
                else:
                    same_direction_count = 1
                active_direction = target_direction
                pending_switch = None

                print(
                    f"t={sim_time:4d}s | dir={target_direction} | "
                    f"ns_q={ns_queue:2d} ew_q={ew_queue:2d} | "
                    f"density={active_density:3d} | green={target_green:3d}s"
                )
                continue

            if sim_time >= next_decision_time:
                ns_queue, ew_queue = get_directional_queues(tls_id)

                # Convert queue to density-like scale expected by fuzzy controller.
                ns_density = min(100, ns_queue * 6)
                ew_density = min(100, ew_queue * 6)

                desired_direction = "NS" if ns_queue >= ew_queue else "EW"

                # Anti-starvation: force service to opposite direction if it has queue.
                if (
                    active_direction == "NS"
                    and same_direction_count >= max_same_direction
                    and ew_queue > 0
                ):
                    desired_direction = "EW"
                elif (
                    active_direction == "EW"
                    and same_direction_count >= max_same_direction
                    and ns_queue > 0
                ):
                    desired_direction = "NS"

                active_density = ns_density if desired_direction == "NS" else ew_density
                time_slot = get_time_slot_from_hour(current_time.hour)

                green_time = fuzzy.compute_green_time(
                    density=active_density,
                    is_weekday=is_weekday,
                    time_period=time_slot,
                )

                target_phase = ns_phase if desired_direction == "NS" else ew_phase
                yellow_phase = None
                if active_direction and active_direction != desired_direction:
                    yellow_phase = ns_yellow_phase if active_direction == "NS" else ew_yellow_phase

                if yellow_phase is not None:
                    traci.trafficlight.setPhase(tls_id, yellow_phase)
                    traci.trafficlight.setPhaseDuration(tls_id, yellow_transition_seconds)
                    next_decision_time = sim_time + yellow_transition_seconds
                    pending_switch = {
                        "target_phase": target_phase,
                        "target_direction": desired_direction,
                        "target_green": max(10, int(green_time)),
                        "ns_queue": ns_queue,
                        "ew_queue": ew_queue,
                        "active_density": active_density,
                    }
                    print(
                        f"t={sim_time:4d}s | switching {active_direction}->{desired_direction} "
                        f"with yellow={yellow_transition_seconds}s"
                    )
                else:
                    traci.trafficlight.setPhase(tls_id, target_phase)
                    traci.trafficlight.setPhaseDuration(tls_id, max(10, int(green_time)))

                    next_decision_time = sim_time + max(10, int(green_time))
                    current_time += timedelta(seconds=max(10, int(green_time)))

                    if active_direction == desired_direction:
                        same_direction_count += 1
                    else:
                        same_direction_count = 1
                    active_direction = desired_direction

                    print(
                        f"t={sim_time:4d}s | dir={desired_direction} | "
                        f"ns_q={ns_queue:2d} ew_q={ew_queue:2d} | "
                        f"density={active_density:3d} | green={green_time:3d}s"
                    )

        print("SUMO fuzzy simulation completed.")
    finally:
        traci.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Run fuzzy control in SUMO")
    parser.add_argument("--gui", action="store_true", help="Run with SUMO GUI")
    parser.add_argument("--duration", type=int, default=900, help="Simulation duration in seconds")
    parser.add_argument("--start-hour", type=int, default=8, help="Start hour [0-23]")
    parser.add_argument("--weekend", action="store_true", help="Run as weekend scenario")
    parser.add_argument("--delay-ms", type=int, default=120, help="GUI playback delay in milliseconds")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_sumo_fuzzy(
        gui=args.gui,
        duration_seconds=args.duration,
        start_hour=args.start_hour,
        is_weekday=not args.weekend,
        delay_ms=args.delay_ms,
    )
