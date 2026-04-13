# config.py
# Central place for all simulation constants so the model matches our report/proposal.

FLOORS = 10
LOBBY_FLOOR = 0


SIM_TIME = 3600  # 1 hour (seconds)

# Poisson arrival rate (passengers / second) — matches progress report
LAMBDA = 0.05

# Elevator model (simple but reasonable for MVP)
ELEVATOR_SPEED = 1.0  # floors per second
DOOR_TIME = 6.0       # seconds total for open+close (combined for MVP)
BOARD_TIME_PER_PERSON = 1.0  # seconds/person
ELEVATOR_CAPACITY = 5

# MVP starts with 1 elevator; later set 2–4 in experiments
DEFAULT_ELEVATORS = 3

# Reproducibility
BASE_SEED = 42
