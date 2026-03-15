# traffic.py
# Generates passenger arrivals for our scenario.
# Progress report says: morning up-peak (most passengers start at lobby and go up).
# Arrivals are Poisson => exponential interarrival times.

from typing import List
import numpy as np
import config
from models import Passenger


def generate_up_peak_passengers(
    sim_time: int,
    lam: float,
    rng: np.random.Generator
) -> List[Passenger]:
    """
    Up-peak generator:
      - origin = lobby
      - destination = random floor above lobby
      - arrivals follow Poisson process
    """
    passengers: List[Passenger] = []
    t = 0.0

    upper_floors = list(range(config.LOBBY_FLOOR + 1, config.FLOORS))
    if not upper_floors:
        raise ValueError(
            "No floors above lobby. Check FLOORS/LOBBY_FLOOR in config.py")

    while t < sim_time:
        # Exponential interarrival time for Poisson process
        t += rng.exponential(1.0 / lam)
        if t >= sim_time:
            break

        origin = config.LOBBY_FLOOR
        destination = int(rng.choice(upper_floors))
        passengers.append(Passenger(arrival_time=t, origin=origin,
                          destination=destination, group_size=1))

    return passengers
