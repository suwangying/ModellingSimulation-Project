from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Passenger:
    arrival_time: float
    origin: int
    destination: int
    group_size: int = 1
    board_time: Optional[float] = None


@dataclass
class Elevator:
    eid: int
    current_floor: int
    available_time: float = 0.0
    busy_time: float = 0.0
    capacity: int = 8
    passengers: List[Passenger] = field(default_factory=list)