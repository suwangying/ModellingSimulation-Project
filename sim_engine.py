# sim_engine.py
# Discrete-event simulation engine using a priority queue (heap).
# Supports 1 elevator MVP and scales to multiple elevators (2–4).
#
# This is Person A's core deliverable.

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from collections import deque
import heapq
import numpy as np

import config
from models import Passenger, Elevator
from traffic import generate_up_peak_passengers
from policies import nearest_pickup_policy


@dataclass
class SimState:
    floor_queues: List[deque]           # passengers waiting per floor
    elevators: List[Elevator]           # elevator states
    assigned_pickups: Dict[int, int]    # floor -> elevator_id (reservation)


# Event tuple format: (time, seq, event_type, payload)
# seq makes ordering stable when two events share the same timestamp.
Event = Tuple[float, int, str, Any]


def run_simulation(
    seed: int,
    elevators_count: int = config.DEFAULT_ELEVATORS,
    policy: str = "nearest"
) -> Dict[str, float]:
    """
    Runs a single simulation trial and returns a dictionary of metrics.
    """

    rng = np.random.default_rng(seed)

    # Generate Poisson up-peak arrivals (matches progress report)
    passengers = generate_up_peak_passengers(
        config.SIM_TIME, config.LAMBDA, rng)

    # Initialize queues and elevators
    floor_queues = [deque() for _ in range(config.FLOORS)]
    elevators = [Elevator(eid=i, current_floor=config.LOBBY_FLOOR)
                 for i in range(elevators_count)]
    state = SimState(floor_queues=floor_queues,
                     elevators=elevators, assigned_pickups={})

    # Event heap
    events: List[Event] = []
    seq = 0

    def push_event(time: float, etype: str, payload: Any) -> None:
        nonlocal seq
        heapq.heappush(events, (time, seq, etype, payload))
        seq += 1

    # Add all passenger arrival events
    for p in passengers:
        push_event(p.arrival_time, "ARRIVAL", p)

    wait_times: List[float] = []
    queue_samples: List[int] = []

    def total_queue_len() -> int:
        return sum(len(q) for q in state.floor_queues)

    def queue_lengths_snapshot() -> List[int]:
        return [len(q) for q in state.floor_queues]

    def choose_pickup_floor(eid: int) -> Optional[int]:
        elev = state.elevators[eid]
        qlens = queue_lengths_snapshot()

        if policy == "nearest":
            return nearest_pickup_policy(elev.current_floor, qlens, state.assigned_pickups)

        raise ValueError(f"Unknown policy: {policy}")

    def schedule_wake(current_time: float) -> None:
        """
        Wake an elevator to try serving.
        We pick the one that becomes available soonest (simple and effective).
        """
        best_eid = min(range(len(state.elevators)),
                       key=lambda i: state.elevators[i].available_time)
        wake_time = max(current_time, state.elevators[best_eid].available_time)
        push_event(wake_time, "ELEV_WAKE", best_eid)

    def serve_one_request(current_time: float, eid: int) -> None:
        """
        If elevator is idle, pick a request and serve it:
        - reserve pickup floor (for multi-elevator case)
        - compute travel + stop time
        - update elevator state
        - record passenger wait
        """
        elev = state.elevators[eid]

        # If we woke up early, ignore (it isn't free yet)
        if current_time < elev.available_time:
            return

        pickup_floor = choose_pickup_floor(eid)
        if pickup_floor is None:
            return  # no requests

        # Reserve pickup so another elevator doesn't also choose it
        state.assigned_pickups[pickup_floor] = eid

        # Grab passenger from that floor
        passenger: Passenger = state.floor_queues[pickup_floor].popleft()

        # If floor queue is now empty, release reservation
        if len(state.floor_queues[pickup_floor]) == 0:
            state.assigned_pickups.pop(pickup_floor, None)

        # --- Time model (simple + consistent) ---
        travel_to_pickup = abs(elev.current_floor -
                               passenger.origin) / config.ELEVATOR_SPEED

        # Door + boarding time. (MVP: no detailed alighting model)
        stop_time = config.DOOR_TIME + config.BOARD_TIME_PER_PERSON * passenger.group_size

        travel_to_dest = abs(passenger.destination -
                             passenger.origin) / config.ELEVATOR_SPEED

        start_time = max(current_time, elev.available_time)

        # Define board_time as when elevator reaches the passenger's floor
        passenger.board_time = start_time + travel_to_pickup
        wait_times.append(passenger.board_time - passenger.arrival_time)

        service_duration = travel_to_pickup + stop_time + travel_to_dest

        elev.available_time = start_time + service_duration
        elev.busy_time += service_duration
        elev.current_floor = passenger.destination

        # If there are still passengers waiting, schedule this elevator again
        if total_queue_len() > 0:
            push_event(elev.available_time, "ELEV_WAKE", eid)

    # Main event loop
    while events:
        t, _, etype, payload = heapq.heappop(events)

        # Stop at simulation horizon
        if t > config.SIM_TIME:
            break

        if etype == "ARRIVAL":
            p: Passenger = payload
            state.floor_queues[p.origin].append(p)

            # Sample total queue size for queue metrics
            queue_samples.append(total_queue_len())

            # Wake an elevator to handle this request (if one is available now/soon)
            schedule_wake(t)

        elif etype == "ELEV_WAKE":
            eid: int = payload
            serve_one_request(t, eid)
            queue_samples.append(total_queue_len())

        else:
            raise ValueError(f"Unknown event type: {etype}")

    # Metrics
    if wait_times:
        mean_wait = float(np.mean(wait_times))
        median_wait = float(np.median(wait_times))
        p95_wait = float(np.percentile(wait_times, 95))
    else:
        mean_wait = median_wait = p95_wait = 0.0

    max_queue = float(max(queue_samples)) if queue_samples else 0.0
    avg_queue = float(np.mean(queue_samples)) if queue_samples else 0.0

    utilizations = [e.busy_time / config.SIM_TIME for e in state.elevators]
    avg_util = float(np.mean(utilizations)) if utilizations else 0.0

    return {
        "mean_wait": mean_wait,
        "median_wait": median_wait,
        "p95_wait": p95_wait,
        "max_queue": max_queue,
        "avg_queue": avg_queue,
        "avg_util": avg_util,
        "arrivals": float(len(passengers)),
        "served": float(len(wait_times)),
    }


if __name__ == "__main__":
    # Quick single-run check (MVP)
    metrics = run_simulation(
        seed=config.BASE_SEED, elevators_count=config.DEFAULT_ELEVATORS, policy="nearest")
    print("Single Run (Up-Peak, Poisson) Results:")
    for k, v in metrics.items():
        print(f"{k:>10}: {v:.3f}")
