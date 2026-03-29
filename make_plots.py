# make_plots.py
# PERSON C
#
# Purpose:
# Read simulation results and processed Kaggle summaries, then generate
# plot files for the report/demo.
#
# Plots created:
# 1. mean_wait_by_case.png
# 2. p95_wait_by_case.png
# 3. avg_util_by_case.png
# 4. avg_queue_by_case.png
# 5. kaggle_hourly_calls.png
# 6. kaggle_floor_distribution.png
#
# Important note:
# This script only creates plots that are supported by the current outputs.
# Some future plots such as passenger wait histograms, per-elevator utilization,
# and queue-over-time traces would require extra data to be returned by sim_engine.py.

import os
import csv
from collections import defaultdict

import matplotlib.pyplot as plt


# Input file paths
RESULTS_PATH = "results.csv"
KAGGLE_HOURLY_PATH = os.path.join("KaggleDatasets", "processed", "kaggle_hourly_calls.csv")
KAGGLE_FLOOR_PATH = os.path.join("KaggleDatasets", "processed", "kaggle_floor_distribution.csv")

# Folder where all generated plot images will be saved
PLOTS_DIR = "plots"


def ensure_plots_dir(path):
    """
    Create the plots folder if it does not already exist.

    Why this matters:
    - matplotlib can save files only if the parent folder exists
    - using exist_ok=True makes the script safe to rerun many times
    """
    os.makedirs(path, exist_ok=True)


def read_csv(path):
    """
    Read a CSV file into a list of dictionaries.

    This keeps the script flexible and simple:
    - results.csv and processed Kaggle files can both be loaded with the same function
    - we convert types later inside the specific processing functions
    """
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def aggregate_results_by_case(rows):
    """
    Group simulation rows by Case and compute average metrics for each case.

    Why this step is needed:
    - results.csv contains one row per Monte Carlo trial
    - the bar charts should compare the average performance of each case
    - so we aggregate all trial rows for the same case into one summary row

    Returns:
    - a list of dictionaries, one per case, containing averaged metrics
    """
    grouped = defaultdict(list)

    for row in rows:
        grouped[row["Case"]].append(row)

    summary_rows = []

    for case_name, case_rows in grouped.items():
        mean_wait_values = [float(r["mean_wait"]) for r in case_rows]
        p95_wait_values = [float(r["p95_wait"]) for r in case_rows]
        avg_util_values = [float(r["avg_util"]) for r in case_rows]
        avg_queue_values = [float(r["avg_queue"]) for r in case_rows]

        summary_rows.append({
            "Case": case_name,
            "mean_wait": sum(mean_wait_values) / len(mean_wait_values),
            "p95_wait": sum(p95_wait_values) / len(p95_wait_values),
            "avg_util": sum(avg_util_values) / len(avg_util_values),
            "avg_queue": sum(avg_queue_values) / len(avg_queue_values),
        })

    # Sort the summaries by case name so plots are deterministic
    summary_rows.sort(key=lambda x: x["Case"])
    return summary_rows


def make_bar_chart(labels, values, title, ylabel, output_path, color):
    """
    Create and save a simple bar chart.

    Parameters:
    - labels: x-axis category labels
    - values: numeric values for each bar
    - title: chart title
    - ylabel: y-axis label
    - output_path: file path for saving the PNG
    - color: bar color

    Why this helper is useful:
    - mean_wait, p95_wait, avg_util, and avg_queue charts all share the same layout
    - using one helper keeps the script shorter and easier to maintain
    """
    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color=color)
    plt.title(title)
    plt.xlabel("Case")
    plt.ylabel(ylabel)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def make_mean_wait_plot(summary_rows):
    """
    Create a bar chart of average mean_wait by case.
    """
    labels = [row["Case"] for row in summary_rows]
    values = [row["mean_wait"] for row in summary_rows]

    make_bar_chart(
        labels=labels,
        values=values,
        title="Average Mean Wait by Case",
        ylabel="Mean Wait (seconds)",
        output_path=os.path.join(PLOTS_DIR, "mean_wait_by_case.png"),
        color="steelblue"
    )


def make_p95_wait_plot(summary_rows):
    """
    Create a bar chart of average p95_wait by case.

    Why this plot matters:
    - mean wait shows typical performance
    - p95 wait shows worst-case passenger experience
    """
    labels = [row["Case"] for row in summary_rows]
    values = [row["p95_wait"] for row in summary_rows]

    make_bar_chart(
        labels=labels,
        values=values,
        title="Average P95 Wait by Case",
        ylabel="P95 Wait (seconds)",
        output_path=os.path.join(PLOTS_DIR, "p95_wait_by_case.png"),
        color="darkorange"
    )


def make_avg_util_plot(summary_rows):
    """
    Create a bar chart of average utilization by case.

    Why this plot matters:
    - utilization helps show how busy the elevator system is
    - it supports discussion of efficiency vs passenger wait tradeoffs
    """
    labels = [row["Case"] for row in summary_rows]
    values = [row["avg_util"] for row in summary_rows]

    make_bar_chart(
        labels=labels,
        values=values,
        title="Average Utilization by Case",
        ylabel="Average Utilization",
        output_path=os.path.join(PLOTS_DIR, "avg_util_by_case.png"),
        color="seagreen"
    )


def make_avg_queue_plot(summary_rows):
    """
    Create a bar chart of average queue length by case.

    Why this plot matters:
    - queue length is a direct measure of congestion
    - it helps explain why waits rise under heavier load or weaker policies
    """
    labels = [row["Case"] for row in summary_rows]
    values = [row["avg_queue"] for row in summary_rows]

    make_bar_chart(
        labels=labels,
        values=values,
        title="Average Queue Length by Case",
        ylabel="Average Queue Length",
        output_path=os.path.join(PLOTS_DIR, "avg_queue_by_case.png"),
        color="mediumpurple"
    )


def make_kaggle_hourly_calls_plot(rows):
    """
    Create a line plot of Kaggle hourly call counts.

    Why this plot matters:
    - it visualizes demand intensity over time
    - it can later be used to justify or estimate lambda values for simulation
    """
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
    """
    Create a bar chart of requested floor distribution from the Kaggle dataset.

    Why this plot matters:
    - it shows how demand is distributed across floors
    - it provides a direct comparison target for future simulation calibration
    """
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
    # Step 1: Make sure the plots output folder exists before saving anything.
    ensure_plots_dir(PLOTS_DIR)

    # Step 2: Load the simulation results.
    # This file must already exist, so run monte_carlo.py first.
    results_rows = read_csv(RESULTS_PATH)

    # Step 3: Convert per-trial Monte Carlo rows into one summary row per case.
    # This makes the simulation comparison bar charts readable.
    summary_rows = aggregate_results_by_case(results_rows)

    # Step 4: Generate the simulation-result plots.
    make_mean_wait_plot(summary_rows)
    make_p95_wait_plot(summary_rows)
    make_avg_util_plot(summary_rows)
    make_avg_queue_plot(summary_rows)

    # Step 5: Load processed Kaggle summary data.
    # These files must already exist, so run kaggle_extract.py first.
    kaggle_hourly_rows = read_csv(KAGGLE_HOURLY_PATH)
    kaggle_floor_rows = read_csv(KAGGLE_FLOOR_PATH)

    # Step 6: Generate the Kaggle comparison plots.
    make_kaggle_hourly_calls_plot(kaggle_hourly_rows)
    make_kaggle_floor_distribution_plot(kaggle_floor_rows)

    print("Generated 6 plot files in the plots folder.")