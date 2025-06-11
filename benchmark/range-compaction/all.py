from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ==== Customize your experiment directories here ====
EXPERIMENT1 = "100M-20:8:1:enable-range-compaction:disable-peridioc-full-compaction"
EXPERIMENT1_NAME = "Enable Range Compaction"
EXPERIMENT2 = "100M-20:8:1:disable-range-compaction:disable-peridioc-full-compaction"
EXPERIMENT2_NAME = "Disable Range Compaction"
BASE_PATH: Path = Path(__file__).parent  # or set manually, e.g., Path("/path/to/data")
OUT_DIR = BASE_PATH / "comparison_charts"
OUT_DIR.mkdir(exist_ok=True)

# Metrics that need downsampling/smoothing
METRICS_NEED_SMOOTHING = {
    "Bytes read per second",
    "Bytes write per second",
    "Compaction read bytes",
    "Compaction write bytes",
    "Flush write bytes",
    "Flush write median latency",
    "Number of keys read per second",
    "Number of keys written per second",
    "Number of next per second",
    "Number of seeks per second",
}

# Metrics that need log scale
METRICS_NEED_LOG = {"Seek average latency (μs)"}

# Downsampling window size (in minutes)
SMOOTHING_WINDOW = 1  # 1 minute window for smoothing
# ===================================================


def size_to_mb(size_str):
    """Convert size string (supports GB, MB, kB, B) to MB."""
    if pd.isnull(size_str):
        return np.nan
    s = str(size_str).strip().strip('"')  # Remove quotes if present
    try:
        # Handle special case of "0 B"
        if s == "0 B":
            return 0.0

        # Extract number and unit
        parts = s.split()
        if len(parts) != 2:
            print(f"Invalid size format (expected 'number unit'): {s}")
            return np.nan

        num = float(parts[0])
        unit = parts[1].upper()  # Convert to uppercase for comparison
        # print(f"Converting size: {s} -> num={num}, unit={unit}")

        # Convert to MB
        if unit == "GB":
            return num * 1024
        elif unit == "MB":
            return num
        elif unit == "KB":  # This will match both KB and kB after upper()
            return num / 1024
        elif unit == "B":
            return num / (1024 * 1024)
        else:
            print(f"Unknown unit in size string: {s} (unit={unit})")
            return np.nan
    except Exception as e:
        print(f"Failed to convert size {size_str}: {e}")
        return np.nan


def duration_to_microseconds(val):
    """
    Convert a string with a time unit to microseconds (float).
    Supports: ns, us/µs, ms, s (case-insensitive)
    """
    if pd.isnull(val):
        return np.nan
    s = str(val).replace(" ", "").lower()  # µs -> us
    try:
        if s.endswith("ns"):
            return float(s[:-2]) / 1000  # ns to µs
        elif s.endswith("µs"):
            return float(s[:-2])
        elif s.endswith("ms"):
            return float(s[:-2]) * 1000
        elif s.endswith("s"):
            return float(s[:-1]) * 1_000_000
        else:
            return float(s)
    except Exception as e:
        print(f"Failed to convert {val} to microseconds: {s}, {e}")
        return np.nan


def is_duration_column(df, col):
    if df.empty or col not in df.columns:
        return False
    try:
        sample = str(df[col].iloc[0]).lower()
        return (
            any(x in sample for x in ["μs", "µs", "ms", "ns", "s"])
            or "latency" in sample
        )
    except Exception:
        return False


def is_size_column(df, col):
    if df.empty or col not in df.columns:
        return False
    try:
        sample = str(df[col].iloc[0]).lower()
        # print(f"Sample data for {col}: {sample}")
        return any(x in sample for x in ["mb", "gb", "kb", "b"])
    except Exception:
        return False


def get_adaptive_size_unit(values):
    """Determine the most appropriate size unit based on the data."""
    if values.empty:
        return "MB", 1.0

    max_val = values.max()
    if max_val >= 1024:  # GB
        return "GB", 1 / 1024
    elif max_val >= 1:  # MB
        return "MB", 1.0
    elif max_val >= 1 / 1024:  # KB
        return "KB", 1024
    else:  # B
        return "B", 1024 * 1024


def get_adaptive_time_unit(values):
    """Determine the most appropriate time unit based on the data."""
    if values.empty:
        return "µs", 1.0

    max_val = values.max()
    if max_val >= 1_000_000:  # seconds
        return "s", 1 / 1_000_000
    elif max_val >= 1_000:  # milliseconds
        return "ms", 1 / 1_000
    elif max_val >= 1:  # microseconds
        return "µs", 1.0
    else:  # nanoseconds
        return "ns", 1_000


def auto_convert_column(df, col):
    if df.empty or col not in df.columns:
        return pd.Series([], dtype=float)
    # Size units
    if is_size_column(df, col):
        values = df[col].map(size_to_mb)
        if values.isna().all():
            print(f"Warning: All values in {col} were converted to NaN")
        return values
    # Time/duration units
    elif is_duration_column(df, col):
        values = df[col].map(duration_to_microseconds)
        if values.isna().all():
            print(f"Warning: All values in {col} were converted to NaN")
        return values
    else:
        try:
            values = pd.to_numeric(df[col], errors="coerce")
            if values.isna().all():
                print(f"Warning: All values in {col} were converted to NaN")
            return values
        except Exception as e:
            print(f"Failed to convert {col} to numeric: {e}")
            return df[col]  # fallback: keep as is


def get_metric_files(exp_dir):
    """Return a dict: {metric_name: path_to_csv}"""
    mapping = {}
    for f in Path(exp_dir).glob("*.csv"):
        metric_name = f.stem.split("-data-")[0]
        mapping[metric_name] = f
    return mapping


# Find all available metrics
metrics1 = get_metric_files(BASE_PATH / EXPERIMENT1)
metrics2 = get_metric_files(BASE_PATH / EXPERIMENT2)
common_metrics = sorted(set(metrics1.keys()) & set(metrics2.keys()))

# common_metrics = ["Bytes read per second"]

print(f"Found {len(common_metrics)} common metrics to compare.")

# Create a dictionary to store metrics by their first word category
metrics_by_category = {}
for metric in common_metrics:
    category = metric.split()[0]
    if category not in metrics_by_category:
        metrics_by_category[category] = []
    metrics_by_category[category].append(metric)

# Generate markdown content
markdown_content = [
    "# Range Compaction Benchmark Charts\n",
    "This document provides an overview of all the charts generated from the range compaction benchmark comparison.\n",
    "## Overview\n",
    "The benchmark compares two configurations:",
    f"- **{EXPERIMENT1_NAME}**: `{EXPERIMENT1}`",
    f"- **{EXPERIMENT2_NAME}**: `{EXPERIMENT2}`\n",
    "## Charts\n",
    "The following charts are available in the `comparison_charts` directory:\n",
]

# Add each category and its metrics
for category, metrics in sorted(metrics_by_category.items()):
    markdown_content.append(f"### {category} Metrics")
    for metric in sorted(metrics):
        chart_name = f"{metric.replace(' ', '_')}_comparison.png"
        markdown_content.append(f"- ![{metric}](comparison_charts/{chart_name})")
    markdown_content.append("")

# Add notes section
markdown_content.extend(
    [
        "## Notes\n",
        "- All throughput and rate metrics are smoothed using a 1-minute rolling window",
        "- The seek latency chart uses a logarithmic scale for better visualization",
        "- Time units are automatically adjusted based on the data range",
        "- Size units are automatically adjusted based on the data range",
    ]
)

# Write the markdown file
with open(BASE_PATH / "charts.md", "w") as f:
    f.write("\n".join(markdown_content))


def smooth_data(df, window_minutes=SMOOTHING_WINDOW):
    """Apply rolling mean smoothing to the data."""
    if df.empty:
        return df

    # Calculate window size in terms of data points
    # Assuming data points are roughly evenly spaced
    time_diff = df["time_offset"].diff().mean()
    if pd.isna(time_diff) or time_diff == 0:
        window = 10  # fallback to 10 points if can't determine
    else:
        window = max(1, int(window_minutes / time_diff))

    # Apply rolling mean
    df["value"] = df["value"].rolling(window=window, min_periods=1, center=True).mean()
    return df


for metric in common_metrics:
    try:
        df1 = pd.read_csv(metrics1[metric], parse_dates=["Time"])
        df2 = pd.read_csv(metrics2[metric], parse_dates=["Time"])

        if df1.empty or df2.empty:
            print(f"Skipping {metric}: Empty DataFrame")
            continue

        # Get the value column (it's the last column)
        value_col = df1.columns[-1]
        if value_col not in df1.columns or value_col not in df2.columns:
            print(f"Skipping {metric}: Column {value_col} not found")
            continue

        # Print sample data for debugging
        # print(f"\nProcessing {metric}:")
        # print(f"Sample data from {EXPERIMENT1}:")
        # print(df1[[value_col]].head())
        # print(f"Sample data from {EXPERIMENT2}:")
        # print(df2[[value_col]].head())

        # Align by time offset
        df1["time_offset"] = (df1["Time"] - df1["Time"].iloc[0]).dt.total_seconds() / 60
        df2["time_offset"] = (df2["Time"] - df2["Time"].iloc[0]).dt.total_seconds() / 60

        # Auto-convert values
        df1["value"] = auto_convert_column(df1, value_col)
        df2["value"] = auto_convert_column(df2, value_col)

        # Drop missing
        df1 = df1.dropna(subset=["value"])
        df2 = df2.dropna(subset=["value"])

        if df1.empty or df2.empty:
            print(f"Skipping {metric}: No valid data after conversion")
            continue

        # Pretty y label and adaptive units
        y_label = metric
        if is_duration_column(df1, value_col):
            unit, scale = get_adaptive_time_unit(
                pd.concat([df1["value"], df2["value"]])
            )
            df1["value"] = df1["value"] * scale
            df2["value"] = df2["value"] * scale
            y_label = f"Time ({unit})"
        elif is_size_column(df1, value_col):
            unit, scale = get_adaptive_size_unit(
                pd.concat([df1["value"], df2["value"]])
            )
            df1["value"] = df1["value"] * scale
            df2["value"] = df2["value"] * scale
            y_label = f"Size ({unit})"

        # Apply smoothing if needed
        if metric in METRICS_NEED_SMOOTHING:
            print(f"Applying smoothing to {metric}")
            df1 = smooth_data(df1)
            df2 = smooth_data(df2)

        # Plot
        plt.figure(figsize=(10, 6))
        plt.plot(
            df1["time_offset"], df1["value"], label=f"{EXPERIMENT1_NAME}", linewidth=1
        )
        plt.plot(
            df2["time_offset"],
            df2["value"],
            label=f"{EXPERIMENT2_NAME}",
            linewidth=1,
            # linestyle="--",
        )
        plt.xlabel("Time Offset (minutes)", fontsize=13)
        plt.ylabel(y_label, fontsize=13)
        plt.title(f"{metric} Over Time", fontsize=15, fontweight="bold")
        plt.legend(fontsize=11)
        plt.grid(True, which="both", linestyle=":", linewidth=0.7)

        # Apply log scale if needed
        if metric in METRICS_NEED_LOG:
            print(f"Applying log scale to {metric}")
            plt.yscale("log")
            # Add minor grid lines for log scale
            plt.grid(True, which="minor", linestyle=":", linewidth=0.5)

        plt.tight_layout()

        # Save figure
        save_name = f"{metric.replace(' ', '_')}_comparison.png"
        plt.savefig(OUT_DIR / save_name, dpi=1000)
        plt.close()
        print(f"Saved {metric} to {OUT_DIR / save_name}")

    except Exception as e:
        print(f"Skipping {metric}: {str(e)}")
print("\nAll done!")
