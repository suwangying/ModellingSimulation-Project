# monte_carlo.py
# Runs the simulation many times with different random seeds and summarizes results.
# This makes our conclusions more reliable than a single run.

import csv
import numpy as np
import config
from sim_engine import run_simulation

# Names of the columns that will appear in results.csv (PERSON C)
FIELDNAMES = [
    "Trial",
    "Case",
    "Elevator",
    "lambda",
    "scenario",
    "policy",
    "mean_wait",
    "median_wait",
    "p95_wait",
    "max_queue",
    "avg_queue",
    "avg_util",
]


def run_trials(trials: int, elevators_count: int, lam: float,
               scenario: str = "up_peak", policy: str = "nearest",
               case_name: str = "Baseline-upPeak-E1",
               base_seed: int = 42):
    """
    Runs multiple trials while changing the seed each time.

    (PERSON C) Added case_name so each CSV row can identify the scenario
        (will be changed dynamically for later milestones)
    """
    old_lambda = config.LAMBDA
    config.LAMBDA = lam

    results = []

    try:
        for i in range(trials):
            seed = base_seed + i
            metrics = run_simulation(
                seed=seed,
                elevators_count=elevators_count,
                policy=policy,
                scenario=scenario
            )
            # Builds one CSV row for this trial into an array to be put into an Excel sheet
            results.append({
                "Trial": i + 1,
                "Case": case_name,
                "Elevator": elevators_count,
                "lambda": lam,
                "scenario": scenario,
                "policy": policy,
                "mean_wait": round(metrics["mean_wait"],2),
                "median_wait": round(metrics["median_wait"],2),
                "p95_wait": round(metrics["p95_wait"],2),
                "max_queue": metrics["max_queue"],
                "avg_queue": round(metrics["avg_queue"],2),
                "avg_util": round(metrics["avg_util"],2),
            })
    finally:
        config.LAMBDA = old_lambda

    return results

def summarize(results):
    """
    Returns a compact summary table from a list of metric dicts.
    """
    mean_wait = np.mean([r["mean_wait"] for r in results])
    median_wait = np.median([r["median_wait"] for r in results])
    p95_wait = np.mean([r["p95_wait"] for r in results])
    max_queue = np.mean([r["max_queue"] for r in results])
    avg_queue = np.mean([r["avg_queue"] for r in results])
    avg_util = np.mean([r["avg_util"] for r in results])

    return {
        "mean_wait": float(mean_wait),
        "median_wait": float(median_wait),
        "p95_wait": float(p95_wait),
        "max_queue": float(max_queue),
        "avg_queue": float(avg_queue),
        "avg_util": float(avg_util),
    }

def write_results_csv(results, output_path="results.csv"):
    """
    Writes all per-trial Monte Carlo rows to results.csv
    """

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    TRIALS = 30  # Person A sanity-level; Person C can bump to 100–1000 later

    cases = [
        # UP-PEAK
        ("UpPeak Nearest", 5, 0.05, "up_peak", "nearest"),
        ("UpPeak Zoning", 5, 0.05, "up_peak", "zoning"),
        ("UpPeak Bias", 5, 0.05, "up_peak", "up_peak_bias"),

        # MIDDAY
        ("Midday Nearest", 5, 0.05, "midday", "nearest"),
        ("Midday Zoning", 5, 0.05, "midday", "zoning"),
        ("Midday Bias", 5, 0.05, "midday", "up_peak_bias"),

        # DOWN-PEAK
        ("DownPeak Nearest", 5, 0.05, "down_peak", "nearest"),
        ("DownPeak Zoning", 5, 0.05, "down_peak", "zoning"),
        ("DownPeak Bias", 5, 0.05, "down_peak", "up_peak_bias"),
    ]

    all_results = []

    print(f"Monte Carlo Summary (TRIALS={TRIALS})")
    print("Case | E | lambda | scenario | policy | mean_wait | median_wait | p95_wait | maxQ | avgQ | util")
    print("-" * 110)

    for name, E, lam, scenario, policy in cases:
        res = run_trials(
            TRIALS,
            elevators_count=E,
            lam=lam,
            scenario=scenario,
            policy=policy,
            case_name=name,
            base_seed=config.BASE_SEED
        )
        all_results.extend(res)
        s = summarize(res)

        print(f"{name:20} | {E:1d} | {lam:>5.2f} | {scenario:8} | {policy:13} | "
            f"{s['mean_wait']:>9.2f} | {s['median_wait']:>11.2f} | {s['p95_wait']:>8.2f} | "
            f"{s['max_queue']:>4.0f} | {s['avg_queue']:>4.2f} | {s['avg_util']:.2f}")

    # save one row per trial for plotting and reporting for later
    write_results_csv(all_results, output_path="results.csv")
    print(f'\nWrote {len(all_results)} trial rows to results.csv')