# monte_carlo.py
# Runs the simulation many times with different random seeds and summarizes results.
# This makes our conclusions more reliable than a single run.

import numpy as np
import config
from sim_engine import run_simulation


def run_trials(trials: int, elevators_count: int, lam: float,
               scenario: str = "up_peak", policy: str = "nearest",
               base_seed: int = 42):
    """
    Runs multiple trials while changing the seed each time.
    """
    old_lambda = config.LAMBDA
    config.LAMBDA = lam

    results = []
    for i in range(trials):
        seed = base_seed + i
        metrics = run_simulation(
            seed=seed,
            elevators_count=elevators_count,
            policy=policy,
            scenario=scenario
        )
        results.append(metrics)

    config.LAMBDA = old_lambda
    return results

def summarize(results):
    """
    Returns a compact summary table from a list of metric dicts.
    """
    mean_wait = np.mean([r["mean_wait"] for r in results])
    p95_wait = np.mean([r["p95_wait"] for r in results])
    max_queue = np.mean([r["max_queue"] for r in results])
    avg_util = np.mean([r["avg_util"] for r in results])

    return {
        "mean_wait": float(mean_wait),
        "p95_wait": float(p95_wait),
        "max_queue": float(max_queue),
        "avg_util": float(avg_util),
    }


if __name__ == "__main__":
    TRIALS = 30  # Person A sanity-level; Person C can bump to 100–1000 later

    cases = [
        ("Up-Peak Nearest", 1, 0.05, "up_peak", "nearest"),
        ("Midday Zoning", 2, 0.05, "midday", "zoning"),
        ("Evening Up-Peak Bias", 2, 0.05, "down_peak", "up_peak_bias"),
    ]

    print(f"Monte Carlo Summary (TRIALS={TRIALS})")
    print("Case | E | lambda | scenario | policy | mean_wait | p95_wait | maxQ | util")
    print("-" * 80)

    for name, E, lam, scenario, policy in cases:
        res = run_trials(TRIALS, elevators_count=E, lam=lam,
                        scenario=scenario, policy=policy,
                        base_seed=config.BASE_SEED)
        s = summarize(res)
        print(f"{name:20} | {E:1d} | {lam:>5.2f} | {scenario:8} | {policy:13} | "
            f"{s['mean_wait']:>9.2f} | {s['p95_wait']:>8.2f} | {s['max_queue']:>4.0f} | {s['avg_util']:.2f}")