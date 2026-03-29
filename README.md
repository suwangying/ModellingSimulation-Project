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


# ------------------------------------------------------------------------------------------------------------------------------------------------

# Elevator Simulation — Person B: Policies & Scenarios

This folder contains the **policies and scenario extensions** for the elevator simulation project.  
It allows comparing multiple dispatch strategies under different traffic patterns to analyze performance metrics such as wait time, queue length, and elevator utilization.

---

## What This Does

Person B’s contributions extend the MVP simulation by enabling **meaningful comparisons**:

- **Traffic Scenarios**
  - `up_peak`: Morning rush (baseline)
  - `midday`: Inter-floor traffic
  - `down_peak`: Evening lobby-to-exit traffic

- **Dispatch Policies**
  - `nearest`: Baseline nearest-request / nearest-available
  - `zoning`: Elevators assigned to specific floor ranges
  - `up_peak_bias`: Keeps one elevator near lobby and prioritizes lobby pickups

- **Experiment Questions**
  - Define which metrics to compare across policies and scenarios
  - Examples: mean wait, 95th percentile wait, utilization vs wait trade-offs

---

## File Overview

1. `traffic.py` | Generates passenger arrivals for all scenarios (`up_peak`, `midday`, `down_peak`)
2. `policies.py` | Implements dispatch strategies (`nearest`, `zoning`, `up_peak_bias`) 
3. `experiment_questions.md` | Lists questions to guide experiments and report analysis 
4. `sim_engine.py` | Core simulation engine (Person A) now supports scenario & policy selection 
5. `monte_carlo.py` | Runs multiple simulation trials to summarize scenario-policy performance 
6. `sanity_tests.py` | Checks logical trends for policies and scenarios (e.g., more elevators → lower wait) 

---

## How to extend (next steps)
- Use Kaggle data later to calibrate λ(t), destination distributions, and group sizes
- Test combinations of multiple policies + multiple scenarios
- Compare number of elevators vs policy performance under each scenario
- Collect results to answer experiment_questions.md and generate report tables/plots

#-------------------------------------------------------------------------------------------------------------------------------------

# Elevator Simulation Project - Person C (Monte Carlo Experiments, Kaggle Validation, Plots)

## What This Does
This folder contains the **results pipeline and analysis tools** for the elevator simulation project.
It allows running repeated simulation trials, extracting comparable summaries from a Kaggle dataset, and generating plots for the report/demo

**Monte Carlo Experiments**
- *'monte_carlo.py'* runs repeated simulation trials using different random seeds
- saves per-trial outputs into *results.csv* (can be changed by changing amount of trials in line 103)
- supports comparing cases across elevator counts, policies and scenarios

**Kaggle Dataset Extraction**
- *kaggle_extract.py* reads the kaggle elevator dataset and generates processed summary files
- Extracts hourly call counts (from 6am-8pm OR 6:00-20:00), requested floor distribution, people count distribution, and wait time summmaries
- Creates outputs that can later be compared against simulation assumptions/results

**Plots for Demo / Report**
- *make_plots.py* reads *results.csv* and the extracted kaggle files to generate figures
- Creates plots for wait time, queue length, utilization, hourly demand, p95 wait by case and requested floor distribution
- All plots are saved to *plots/* folder

## File Overview
1. 'monte_carlo.py' | Runs repeated simulation trials and writes per-trial results to 'results.csv'
2. 'results.csv' | Stores Monte Carlo output rows for each trial/case combination
     - Trial, Case, Elevator, Lambda, Scenario, Policy, mean_wait, median_wait, p95_wait, max_queue, avg_queue, avg_util
3. 'kaggle_extract.py' | Processes the kaggle elevator dataset into summary files
4. 'KaggleDatasets/' | Contains the initial Kaggle Dataset along with 'processed/' where all the summarized files are
    - Kaggle_floor_dsitribution.csv, kaggle_hourly_calls.csv, kaggle_people_count_distribution.csv, kaggle_wait_time_summary.csv
5. 'make_plots.py' | Generates plot files from simulation results and Kaggle summmaries
6. 'plots/' | Stores generated '.png' figures for analysis (overridden each run)
    - mean_wait_by_case, avg_queue_by_case, avg_util_by_case, kaggle_floor_dsitribution, kaggle_hourly_calls, p95_wait_by_case

## How to Run
Run the files in this order:
1. `python monte_carlo.py`
2. `python kaggle_extract.py`
3. `python make_plots.py`

## How to Extend (next steps)
- Increase Monte Carlo trials from `20` to `100+` for stronger statistical stability
- Add more experiment cases in `monte_carlo.py` for additional elevator counts, policies, and scenarios
- Use Kaggle hourly demand to calibrate `lambda(t)` more directly
- Add richer simulation outputs such as raw wait-time lists, per-elevator utilization, and queue traces
- Generate additional figures such as wait-time histograms, utilization per elevator, and queue length over time
