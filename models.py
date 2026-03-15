# models.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class Passenger:
    # Stores what we need to compute wait time accurately.
    arrival_time: float
    origin: int
    destination: int
    group_size: int = 1
    board_time: Optional[float] = None  # set when elevator arrives for pickup


@dataclass
class Elevator:
    # Minimal elevator state for discrete-event simulation.
    eid: int
    current_floor: int
    available_time: float = 0.0  # when this elevator becomes free again
    busy_time: float = 0.0       # time moving + stopping (for utilization)
