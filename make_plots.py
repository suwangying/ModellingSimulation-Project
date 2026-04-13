# make_plots.py
# PERSON C
#
# Purpose:
# Read simulation results and processed Kaggle summaries, then generate
# plot files for the report/demo.
#
# Plots created:
# 1. mean_wait_grouped.png
# 2. p95_wait_grouped.png
# 3. avg_util_grouped.png
# 4. avg_queue_grouped.png
# 5. kaggle_hourly_calls.png
# 6. kaggle_floor_distribution.png

import os
import csv
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt


# Input file paths
RESULTS_PATH = "results.csv"
KAGGLE_HOURLY_PATH = os.path.join("KaggleDatasets", "processed", "kaggle_hourly_calls.csv")
KAGGLE_FLOOR_PATH = os.path.join("KaggleDatasets", "processed", "kaggle_floor_distribution.csv")

# Folder where all generated plot images will be saved
PLOTS_DIR = "plots"


def ensure_plots_dir(path):
    os.makedirs(path, exist_ok=True)


def read_csv(path):
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def aggregate_results(rows):
    """
    Aggregate Monte Carlo rows by (scenario, policy).
    """
    grouped = defaultdict(list)

    for row in rows:
        key = (row["scenario"], row["policy"])
        grouped[key].append(row)

    summary_rows = []

    for (scenario, policy), case_rows in grouped.items():
        summary_rows.append({
            "scenario": scenario,
            "policy": policy,
            "mean_wait": np.mean([float(r["mean_wait"]) for r in case_rows]),
            "p95_wait": np.mean([float(r["p95_wait"]) for r in case_rows]),
            "avg_util": np.mean([float(r["avg_util"]) for r in case_rows]),
            "avg_queue": np.mean([float(r["avg_queue"]) for r in case_rows]),
        })

    return summary_rows

def make_elevator_scaling_plot(rows):
    """
    Plot mean wait vs number of elevators (Q3)
    """

    data = {}

    for row in rows:
        if row["scenario"] == "up_peak" and row["policy"] == "nearest":
            e = int(row["Elevator"])
            data.setdefault(e, []).append(float(row["mean_wait"]))

    elevators = sorted(data.keys())
    mean_waits = [sum(data[e]) / len(data[e]) for e in elevators]

    plt.figure(figsize=(8, 5))
    plt.plot(elevators, mean_waits, marker="o")
    plt.title("Mean Wait vs Number of Elevators (Up-Peak, Nearest)")
    plt.xlabel("Number of Elevators")
    plt.ylabel("Mean Wait (seconds)")
    plt.xticks(elevators)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "elevator_scaling.png"))
    plt.close()

def make_lambda_vs_queue_plot(rows):
    """
    Plot average queue length vs lambda (Q8)
    """
    data = {}

    for row in rows:
        if row["scenario"] == "up_peak" and row["policy"] == "nearest":
            lam = float(row["lambda"])
            data.setdefault(lam, []).append(float(row["avg_queue"]))

    lambdas = sorted(data.keys())
    avg_queues = [sum(data[lam]) / len(data[lam]) for lam in lambdas]

    plt.figure(figsize=(8, 5))
    plt.plot(lambdas, avg_queues, marker="o", linewidth=2)
    plt.title("Queue Length vs Arrival Rate (Up-Peak, Nearest)")
    plt.xlabel("Arrival Rate (lambda)")
    plt.ylabel("Average Queue Length")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.margins(x=0.05, y=0.12)

    for x, y in zip(lambdas, avg_queues):
        plt.text(x, y + max(avg_queues) * 0.02, f"{y:.1f}", ha="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "lambda_vs_queue.png"), dpi=200, bbox_inches="tight")
    plt.close()

def make_grouped_bar_chart(summary_rows, metric, title, ylabel, filename, ylim=None, label_offset_ratio=0.02):
    """
    Create grouped bar chart:
    X-axis = scenario
    Bars = policy
    """

    scenario_order = ["up_peak", "midday", "down_peak"]
    policy_order = ["nearest", "zoning", "up_peak_bias"]

    scenarios = [s for s in scenario_order if any(row["scenario"] == s for row in summary_rows)]
    policies = [p for p in policy_order if any(row["policy"] == p for row in summary_rows)]

    data = {s: {p: 0 for p in policies} for s in scenarios}
    for row in summary_rows:
        data[row["scenario"]][row["policy"]] = row[metric]

    pretty_scenarios = {
        "up_peak": "Up-Peak",
        "midday": "Midday",
        "down_peak": "Down-Peak",
    }

    pretty_policies = {
        "nearest": "Nearest",
        "zoning": "Zoning",
        "up_peak_bias": "Bias",
    }

    x = np.arange(len(scenarios))
    width = 0.22

    plt.figure(figsize=(10, 6))
    offsets = np.linspace(-width, width, len(policies))

    # collect all values first so we can compute nice limits
    all_values = []
    bar_groups = []

    for i, policy in enumerate(policies):
        values = [data[s][policy] for s in scenarios]
        all_values.extend(values)
        bars = plt.bar(x + offsets[i], values, width, label=pretty_policies[policy])
        bar_groups.append(bars)

    # axis scaling
    if ylim is not None:
        y_min, y_max = ylim
    else:
        y_min = 0
        y_max = max(all_values) * 1.15 if all_values else 1

    plt.ylim(y_min, y_max)

    # label bars with sensible spacing
    label_offset = (y_max - y_min) * label_offset_ratio
    for bars in bar_groups:
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height + label_offset,
                f"{height:.2f}",
                ha="center",
                va="bottom",
                fontsize=9
            )

    plt.xticks(x, [pretty_scenarios[s] for s in scenarios])
    plt.xlabel("Scenario")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, filename), dpi=200, bbox_inches="tight")
    plt.close()

def make_utilization_scenario_plot(summary_rows):
    """
    Simpler utilization plot:
    average utilization by scenario, averaged across policies.
    This avoids awkward duplicate-looking bars.
    """
    scenario_order = ["up_peak", "midday", "down_peak"]
    pretty_scenarios = {
        "up_peak": "Up-Peak",
        "midday": "Midday",
        "down_peak": "Down-Peak",
    }

    scenario_to_vals = {s: [] for s in scenario_order}
    for row in summary_rows:
        scenario_to_vals[row["scenario"]].append(row["avg_util"])

    scenarios = [s for s in scenario_order if scenario_to_vals[s]]
    values = [np.mean(scenario_to_vals[s]) for s in scenarios]

    plt.figure(figsize=(8, 5))
    bars = plt.bar([pretty_scenarios[s] for s in scenarios], values)

    plt.ylim(0, 0.7)
    for bar, val in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            val + 0.015,
            f"{val:.2f}",
            ha="center",
            va="bottom",
            fontsize=9
        )

    plt.title("Average Utilization by Scenario")
    plt.xlabel("Scenario")
    plt.ylabel("Average Utilization")
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "avg_util_by_scenario.png"), dpi=200, bbox_inches="tight")
    plt.close()

def make_kaggle_hourly_calls_plot(rows):
    hours = [int(row["hour"]) for row in rows]
    call_counts = [int(row["call_count"]) for row in rows]

    plt.figure(figsize=(10, 6))
    plt.plot(hours, call_counts, marker="o", linewidth=2, color="crimson")
    plt.title("Kaggle Hourly Elevator Calls")
    plt.xlabel("Hour of Day")
    plt.ylabel("Call Count")
    plt.xticks(hours)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "kaggle_hourly_calls.png"))
    plt.close()


def make_kaggle_floor_distribution_plot(rows):
    floors = [int(row["floor_requested"]) for row in rows]
    probabilities = [float(row["probability"]) for row in rows]

    plt.figure(figsize=(10, 6))
    plt.bar([str(floor) for floor in floors], probabilities, color="slateblue")
    plt.title("Kaggle Floor Request Distribution")
    plt.xlabel("Requested Floor")
    plt.ylabel("Probability")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "kaggle_floor_distribution.png"))
    plt.close()


if __name__ == "__main__":
    ensure_plots_dir(PLOTS_DIR)

    results_rows = read_csv(RESULTS_PATH)
    summary_rows = aggregate_results(results_rows)
    make_elevator_scaling_plot(results_rows)
    
    make_grouped_bar_chart(
        summary_rows,
        metric="mean_wait",
        title="Mean Wait by Scenario and Policy",
        ylabel="Mean Wait (seconds)",
        filename="mean_wait_grouped.png",
        ylim=(3, 8)
    )

    make_grouped_bar_chart(
        summary_rows,
        metric="p95_wait",
        title="P95 Wait by Scenario and Policy",
        ylabel="P95 Wait (seconds)",
        filename="p95_wait_grouped.png",
        ylim=(8, 19)
    )

    make_grouped_bar_chart(
        summary_rows,
        metric="avg_util",
        title="Utilization by Scenario and Policy",
        ylabel="Average Utilization",
        filename="avg_util_grouped.png",
        ylim=(0, 0.5)
    )

    make_grouped_bar_chart(
        summary_rows,
        metric="avg_queue",
        title="Average Queue Length by Scenario and Policy",
        ylabel="Average Queue Length",
        filename="avg_queue_grouped.png"
    )

    kaggle_hourly_rows = read_csv(KAGGLE_HOURLY_PATH)
    kaggle_floor_rows = read_csv(KAGGLE_FLOOR_PATH)

    make_kaggle_hourly_calls_plot(kaggle_hourly_rows)
    make_kaggle_floor_distribution_plot(kaggle_floor_rows)
    make_lambda_vs_queue_plot(results_rows)

    print("Generated 6 plot files in the plots folder.")