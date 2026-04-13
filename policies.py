from typing import Dict, List, Optional
import math


def nearest_pickup_policy(
    elevator_floor: int,
    queue_lengths: List[int],
    assigned_pickups: Dict[int, int]
) -> Optional[int]:
    """
    Baseline policy:
    Choose the nearest floor with waiting passengers.
    Ignore floors already assigned to another elevator.
    """
    best_floor = None
    best_dist = math.inf

    for floor, qlen in enumerate(queue_lengths):
        if qlen <= 0:
            continue
        if floor in assigned_pickups:
            continue

        dist = abs(floor - elevator_floor)
        if dist < best_dist:
            best_dist = dist
            best_floor = floor

    return best_floor


def zoning_policy(
    elevator_floor: int,
    queue_lengths: List[int],
    assigned_pickups: Dict[int, int],
    eid: int,
    num_elevators: int
) -> Optional[int]:
    """
    Zoning policy:
    Each elevator first tries to serve requests in its own floor zone.
    Inside the zone, it prefers the floor with the largest queue.
    If tied, it chooses the nearer floor.
    If no requests exist in the zone, it falls back to global help.
    """

    floors = len(queue_lengths)
    zone_size = math.ceil(floors / num_elevators)

    start = eid * zone_size
    end = min(start + zone_size, floors)

    best_floor = None
    best_queue = -1
    best_dist = math.inf

    # Step 1: search inside assigned zone
    for floor in range(start, end):
        qlen = queue_lengths[floor]

        if qlen <= 0:
            continue
        if floor in assigned_pickups:
            continue

        dist = abs(floor - elevator_floor)

        # Prefer largest queue, then nearest distance
        if qlen > best_queue:
            best_queue = qlen
            best_dist = dist
            best_floor = floor
        elif qlen == best_queue and dist < best_dist:
            best_dist = dist
            best_floor = floor

    if best_floor is not None:
        return best_floor

    # Step 2: if no requests in zone, help globally
    best_floor = None
    best_queue = -1
    best_dist = math.inf

    for floor, qlen in enumerate(queue_lengths):
        if qlen <= 0:
            continue
        if floor in assigned_pickups:
            continue

        dist = abs(floor - elevator_floor)

        # Prefer largest queue globally, then nearest distance
        if qlen > best_queue:
            best_queue = qlen
            best_dist = dist
            best_floor = floor
        elif qlen == best_queue and dist < best_dist:
            best_dist = dist
            best_floor = floor

    return best_floor


def up_peak_bias_policy(
    elevator_floor: int,
    queue_lengths: List[int],
    assigned_pickups: Dict[int, int]
) -> Optional[int]:
    """
    Up-peak bias policy:
    Strongly prioritizes lobby demand.
    If the lobby has waiting passengers, always serve the lobby first.
    Otherwise, choose the floor with the largest queue.
    If tied, choose the nearer floor.
    """

    lobby = 0

    # Step 1: always prioritize lobby if it has demand
    if queue_lengths[lobby] > 0 and lobby not in assigned_pickups:
        return lobby

    # Step 2: otherwise prefer the largest queue in the building
    best_floor = None
    best_queue = -1
    best_dist = math.inf

    for floor, qlen in enumerate(queue_lengths):
        if qlen <= 0:
            continue
        if floor in assigned_pickups:
            continue

        dist = abs(floor - elevator_floor)

        # Prefer largest queue, then nearest distance
        if qlen > best_queue:
            best_queue = qlen
            best_dist = dist
            best_floor = floor
        elif qlen == best_queue and dist < best_dist:
            best_dist = dist
            best_floor = floor

    return best_floor