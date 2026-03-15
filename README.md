# Elevator Simulation (Person A Core Engine)

## What this does
This folder contains the core **discrete-event simulation engine** for our elevator project.  
Instead of simulating every second, the program jumps between important events (passenger arrivals and elevator service) using a **priority queue** ordered by time.

The MVP matches our progress report assumptions:
- **10 floors**, **1 elevator**, **1-hour** simulation
- **Morning up-peak** traffic (most passengers start at the lobby and go up)
- **Poisson passenger arrivals** with **λ = 0.05 passengers/sec**
- Outputs the main metrics we care about: **wait time**, **queue length stats**, and **utilization**

## File overview (what each file is for)
- `config.py` — All constants/parameters (floors, λ, speed, door time, boarding time, sim length)
- `models.py` — Data classes for `Passenger` and `Elevator`
- `traffic.py` — Passenger arrival generator for the up-peak scenario (Poisson arrivals)
- `policies.py` — Dispatch rules (baseline nearest-pickup policy; Person B adds zoning/up-peak bias)
- `sim_engine.py` — The main simulation engine (event queue, state updates, metrics)
- `sanity_tests.py` — Quick trend checks to confirm the engine behaves logically
- `monte_carlo.py` — Runs multiple seeds and summarizes results (more reliable than a single run)

## How to run
From this folder:
- Single run (prints one set of metrics):
  - `python sim_engine.py`
- Quick sanity checks (expected trend behavior like more elevators → lower wait):
  - `python sanity_tests.py`
- Monte Carlo summary (averages over many seeds):
  - `python monte_carlo.py`

## What the output means (quick)
- `mean_wait`: average passenger wait time (arrival → elevator reaches pickup)
- `p95_wait`: 95th percentile wait time (only worst 5% wait longer)
- `max_queue` / `avg_queue`: queue size stats sampled during the run
- `avg_util`: elevator utilization = busy_time ÷ simulation_time

## How to change things
- Change simulation settings (floors, λ, speed, door/boarding time, duration): edit `config.py`
- Change passenger traffic patterns (add midday/evening scenarios, weighted destinations): edit `traffic.py`
- Add/modify dispatch strategies (zoning, up-peak bias, etc.): edit `policies.py`
- Run more trials / compare cases: edit `TRIALS` and case list in `monte_carlo.py`

## How to extend (next steps)
- Set elevators to 2–4 and compare policies under the same traffic
- Add additional dispatch strategies in `policies.py` (zoning, up-peak bias)
- Add more scenarios in `traffic.py` (midday inter-floor, evening down-peak)
- Use Kaggle data later to calibrate λ(t), destination distributions, and group sizes