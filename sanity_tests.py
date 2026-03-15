# sanity_tests.py
# Simple trend tests that show the simulation behaves logically.
# This is great evidence for your final report and helps catch bugs early.

import copy
import config
from sim_engine import run_simulation


def run_and_print(label: str, elevators_count: int):
    m = run_simulation(seed=config.BASE_SEED,
                       elevators_count=elevators_count, policy="nearest")
    print(f"\n{label}")
    print(
        f"  mean_wait={m['mean_wait']:.2f}s, p95_wait={m['p95_wait']:.2f}s, util={m['avg_util']:.2f}, maxQ={m['max_queue']:.0f}")


if __name__ == "__main__":
    # Baseline
    run_and_print("Baseline (E=1)", elevators_count=1)

    # More elevators should reduce wait time
    run_and_print("More elevators (E=2)", elevators_count=2)
    run_and_print("More elevators (E=3)", elevators_count=3)

    # Quick check: if we increase arrival rate, waits should go up.
    old_lambda = config.LAMBDA
    config.LAMBDA = 0.08
    run_and_print("Higher arrival rate (lambda=0.08, E=1)", elevators_count=1)
    config.LAMBDA = old_lambda
