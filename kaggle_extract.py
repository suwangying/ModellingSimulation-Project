# kaggle_extract.py
# PERSON C
#
# Purpose:
# Read the raw Kaggle elevator dataset and generate cleaned summary CSV files
# that can be compared against simulation results later.
#
# Outputs created in KaggleDatasets/processed:
# - kaggle_hourly_calls.csv
# - kaggle_floor_distribution.csv
# - kaggle_people_count_distribution.csv
# - kaggle_wait_time_summary.csv

import csv
import os
import math
from collections import Counter, defaultdict
from datetime import datetime
from statistics import mean, median


# Input dataset path
INPUT_PATH = os.path.join("KaggleDatasets", "elevator_traffic_dataset.csv")

# Folder where processed summary files will be saved
OUTPUT_DIR = os.path.join("KaggleDatasets", "processed")


def percentile(values, p):
    """
    Compute the pth percentile using a simple linear interpolation method.

    Example:
    - p = 95 returns the 95th percentile
    - values must be a non-empty list of numbers
    """
    if not values:
        return 0.0

    sorted_vals = sorted(values)

    if len(sorted_vals) == 1:
        return float(sorted_vals[0])

    # Position of the percentile in the sorted list
    k = (len(sorted_vals) - 1) * (p / 100.0)
    lower = math.floor(k)
    upper = math.ceil(k)

    if lower == upper:
        return float(sorted_vals[int(k)])

    # Linear interpolation between neighboring values
    lower_value = sorted_vals[lower]
    upper_value = sorted_vals[upper]
    return float(lower_value + (upper_value - lower_value) * (k - lower))


def load_dataset(path):
    """
    Load the raw dataset from CSV and convert important fields into the right types.

    Converted fields:
    - timestamp -> datetime
    - floor_requested -> int
    - wait_time_seconds -> float
    - people_count -> int
    """
    rows = []

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            cleaned_row = {
                "timestamp": datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M"),
                "floor_requested": int(row["floor_requested"]),
                "wait_time_seconds": float(row["wait_time_seconds"]),
                "direction": row["direction"].strip(),
                "people_count": int(row["people_count"]),
                "peak_hour": row["peak_hour"].strip(),
                "load_percent": float(row["load_percent"]),
            }
            rows.append(cleaned_row)

    return rows


def ensure_output_dir(path):
    """
    Create the output directory if it does not already exist.
    """
    os.makedirs(path, exist_ok=True)


def write_csv(path, fieldnames, rows):
    """
    Write a list of dictionaries to a CSV file.
    Overwrites the file each time the script is run.
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def extract_hourly_calls(rows):
    """
    Build hourly demand summary from timestamps.

    Output columns:
    - hour
    - call_count
    - calls_per_hour
    - lambda_per_second

    Since this dataset appears to cover one day, call_count and calls_per_hour
    are effectively the same value.
    """
    hourly_counts = Counter()

    for row in rows:
        hour = row["timestamp"].hour
        hourly_counts[hour] += 1

    output_rows = []

    # data set is only from 6am-8pm (6-20) so if you want full 24 hours
    # set hourly_counts (below inside ForLoop) to 24
    for hour in sorted(hourly_counts):
        call_count = hourly_counts[hour]
        output_rows.append({
            "hour": hour,
            "call_count": call_count,
            "calls_per_hour": call_count,
            "lambda_per_second": round(call_count / 3600.0, 6),
        })

    return output_rows


def extract_floor_distribution(rows):
    """
    Summarize how often each floor was requested.

    Output columns:
    - floor_requested
    - count
    - probability
    """
    floor_counts = Counter()
    total_calls = len(rows)

    for row in rows:
        floor_counts[row["floor_requested"]] += 1

    output_rows = []
    for floor in sorted(floor_counts):
        count = floor_counts[floor]
        output_rows.append({
            "floor_requested": floor,
            "count": count,
            "probability": round(count / total_calls, 4),
        })

    return output_rows


def extract_people_count_distribution(rows):
    """
    Summarize how many people are in each request/group.

    Output columns:
    - people_count
    - count
    - probability
    """
    people_counts = Counter()
    total_calls = len(rows)

    for row in rows:
        people_counts[row["people_count"]] += 1

    output_rows = []
    for people_count in sorted(people_counts):
        count = people_counts[people_count]
        output_rows.append({
            "people_count": people_count,
            "count": count,
            "probability": round(count / total_calls, 4),
        })

    return output_rows


def build_wait_summary_row(scope_name, wait_values):
    """
    Build one summary row for a given set of wait times.

    Output columns:
    - scope
    - mean_wait
    - median_wait
    - p95_wait
    - min_wait
    - max_wait
    - sample_size
    """
    if not wait_values:
        return {
            "scope": scope_name,
            "mean_wait": 0.0,
            "median_wait": 0.0,
            "p95_wait": 0.0,
            "min_wait": 0.0,
            "max_wait": 0.0,
            "sample_size": 0,
        }

    return {
        "scope": scope_name,
        "mean_wait": round(mean(wait_values), 2),
        "median_wait": round(median(wait_values), 2),
        "p95_wait": round(percentile(wait_values, 95), 2),
        "min_wait": round(min(wait_values), 2),
        "max_wait": round(max(wait_values), 2),
        "sample_size": len(wait_values),
    }


def extract_wait_time_summary(rows):
    """
    Build wait-time summary rows for:
    - all data
    - peak_yes
    - peak_no

    This gives a compact comparison target for simulation output metrics.
    """
    all_waits = []
    peak_yes_waits = []
    peak_no_waits = []

    for row in rows:
        wait = row["wait_time_seconds"]
        all_waits.append(wait)

        if row["peak_hour"].lower() == "yes":
            peak_yes_waits.append(wait)
        else:
            peak_no_waits.append(wait)

    output_rows = [
        build_wait_summary_row("all", all_waits),
        build_wait_summary_row("peak_yes", peak_yes_waits),
        build_wait_summary_row("peak_no", peak_no_waits),
    ]

    return output_rows


if __name__ == "__main__":
    # Make sure the processed output folder exists
    ensure_output_dir(OUTPUT_DIR)

    # Load and clean the raw Kaggle dataset
    rows = load_dataset(INPUT_PATH)

    # Generate each summary table
    hourly_calls = extract_hourly_calls(rows)
    floor_distribution = extract_floor_distribution(rows)
    people_distribution = extract_people_count_distribution(rows)
    wait_summary = extract_wait_time_summary(rows)

    # Write all processed CSV outputs
    write_csv(
        os.path.join(OUTPUT_DIR, "kaggle_hourly_calls.csv"),
        ["hour", "call_count", "calls_per_hour", "lambda_per_second"],
        hourly_calls
    )

    write_csv(
        os.path.join(OUTPUT_DIR, "kaggle_floor_distribution.csv"),
        ["floor_requested", "count", "probability"],
        floor_distribution
    )

    write_csv(
        os.path.join(OUTPUT_DIR, "kaggle_people_count_distribution.csv"),
        ["people_count", "count", "probability"],
        people_distribution
    )

    write_csv(
        os.path.join(OUTPUT_DIR, "kaggle_wait_time_summary.csv"),
        ["scope", "mean_wait", "median_wait", "p95_wait", "min_wait", "max_wait", "sample_size"],
        wait_summary
    )

    print("Wrote 4 processed Kaggle summary files to KaggleDatasets/processed")