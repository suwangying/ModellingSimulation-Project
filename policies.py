# policies.py
# Dispatch policies live here. Person B will add zoning and up-peak bias later.
# Person A needs only a clean baseline policy + interface.

from typing import Dict, List, Optional
import math


def nearest_pickup_policy(
    elevator_floor: int,
    queue_lengths: List[int],
    assigned_pickups: Dict[int, int]
) -> Optional[int]:
    """
    Baseline policy:
    - Choose the closest floor that has waiting passengers.
    - Skip floors already reserved by another elevator (prevents duplicates in multi-elevator case).
    """
    best_floor = None
    best_dist = math.inf

    for floor, qlen in enumerate(queue_lengths):
        if qlen <= 0:
            continue
        if floor in assigned_pickups:
            continue  # someone else already committed to this pickup

        dist = abs(floor - elevator_floor)
        if dist < best_dist:
            best_dist = dist
            best_floor = floor

    return best_floor
