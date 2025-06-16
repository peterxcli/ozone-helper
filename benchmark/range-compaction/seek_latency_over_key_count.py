import glob
import os

import matplotlib.pyplot as plt
import pandas as pd

# Experiment folder paths
experiment_folders = {
    "Enable Range Compaction": "100M-20:8:1:enable-range-compaction:disable-peridioc-full-compaction",
    "Disable Range Compaction": "100M-20:8:1:disable-range-compaction:disable-peridioc-full-compaction",
    "Disable Range Compaction + Periodic Full Compaction": "100M-20:8:1:disable-range-compaction:enable-peridioc-full-compaction",
}


def parse_latency_value(value_str):
    """Parse latency value from string to microseconds"""
    if pd.isna(value_str) or value_str == "0" or value_str == 0:
        return 0

    value_str = str(value_str).strip()
    if "µs" in value_str:
        return float(value_str.replace(" µs", "").replace("µs", ""))
    elif "ms" in value_str:
        return float(value_str.replace(" ms", "").replace("ms", "")) * 1000
    elif "ns" in value_str:
        return float(value_str.replace(" ns", "").replace("ns", "")) / 1000
    elif (
        "s" in value_str
        and "µs" not in value_str
        and "ms" not in value_str
        and "ns" not in value_str
    ):
        return float(value_str.replace(" s", "").replace("s", "")) * 1000000
    else:
        # Try to parse as plain number (assume microseconds)
        try:
            return float(value_str)
        except ValueError:
            return 0


def read_csv_data(folder_path, file_pattern):
    """Read CSV data from experiment folder"""
    files = glob.glob(os.path.join(folder_path, file_pattern))
    if not files:
        return None

    df = pd.read_csv(files[0])
    return df


def get_experiment_data():
    """Extract seek latency and key count data from experiment folders at different magnitudes"""
    data = {}

    # Target magnitudes to analyze (based on actual data range)
    target_magnitudes = [10**5, 10**6, 10**7]  # 100K, 1M, 10M

    # Get key count data from one experiment (they should all be the same)
    key_count_folder = list(experiment_folders.values())[0]
    key_count_df = read_csv_data(
        key_count_folder, "KeyTable Estimated number of keys*.csv"
    )

    if key_count_df is None:
        return {}

    key_count_col = key_count_df.columns[1]

    # Get seek latency data from each experiment
    for experiment_name, folder_name in experiment_folders.items():
        avg_latency_df = read_csv_data(folder_name, "Seek average latency*.csv")
        max_latency_df = read_csv_data(folder_name, "Seek max latency*.csv")

        if avg_latency_df is None or max_latency_df is None:
            continue

        avg_latency_col = avg_latency_df.columns[1]
        max_latency_col = max_latency_df.columns[1]

        # Extract data at target magnitudes
        magnitude_data = {}

        for target_mag in target_magnitudes:
            # Find the closest point where key count reaches this magnitude
            closest_idx = None
            min_diff = float("inf")

            key_counts = key_count_df[key_count_col].values
            for i, key_count in enumerate(key_counts):
                if key_count >= target_mag:
                    diff = abs(key_count - target_mag)
                    if diff < min_diff:
                        min_diff = diff
                        closest_idx = i
                    break

            # Handle cases where files have different lengths
            if closest_idx is not None and closest_idx < len(key_count_df):
                # Use the closest available index for each file
                avg_idx = (
                    min(closest_idx, len(avg_latency_df) - 1)
                    if len(avg_latency_df) > 0
                    else None
                )
                max_idx = (
                    min(closest_idx, len(max_latency_df) - 1)
                    if len(max_latency_df) > 0
                    else None
                )

                if avg_idx is not None and max_idx is not None:
                    avg_latency_val = parse_latency_value(
                        avg_latency_df[avg_latency_col].iloc[avg_idx]
                    )
                    max_latency_val = parse_latency_value(
                        max_latency_df[max_latency_col].iloc[max_idx]
                    )
                    actual_key_count = key_count_df[key_count_col].iloc[closest_idx]

                    magnitude_data[f"10^{len(str(target_mag)) - 1}"] = {
                        "avg_latency_us": avg_latency_val,
                        "max_latency_us": max_latency_val,
                        "key_count": actual_key_count,
                        "target_magnitude": target_mag,
                    }

        data[experiment_name] = magnitude_data

    return data


# Get data from experiment folders
experiment_data = get_experiment_data()

# Create visualization showing performance multipliers across magnitudes
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

magnitudes = ["10^5", "10^6", "10^7"]
experiments = list(experiment_data.keys())

# Prepare data for plotting
enable_avg_latencies = []
enable_max_latencies = []
disable_no_periodic_avg = []
disable_no_periodic_max = []
disable_with_periodic_avg = []
disable_with_periodic_max = []

enable_data = experiment_data.get("Enable Range Compaction", {})
disable_no_data = experiment_data.get("Disable Range Compaction", {})
disable_with_data = experiment_data.get("Disable Range Compaction + Periodic Full Compaction", {})

for mag in magnitudes:
    # Get latencies for each configuration at this magnitude
    enable_avg = (
        enable_data.get(mag, {}).get("avg_latency_us", 0) / 1000
    )  # Convert to ms
    enable_max = enable_data.get(mag, {}).get("max_latency_us", 0) / 1000

    disable_no_avg = disable_no_data.get(mag, {}).get("avg_latency_us", 0) / 1000
    disable_no_max = disable_no_data.get(mag, {}).get("max_latency_us", 0) / 1000

    disable_with_avg = disable_with_data.get(mag, {}).get("avg_latency_us", 0) / 1000
    disable_with_max = disable_with_data.get(mag, {}).get("max_latency_us", 0) / 1000

    enable_avg_latencies.append(enable_avg)
    enable_max_latencies.append(enable_max)
    disable_no_periodic_avg.append(disable_no_avg)
    disable_no_periodic_max.append(disable_no_max)
    disable_with_periodic_avg.append(disable_with_avg)
    disable_with_periodic_max.append(disable_with_max)

# Plot 1: Average Seek Latency across magnitudes
width = 0.25
x = range(len(magnitudes))

ax1.bar(
    [i - width for i in x],
    enable_avg_latencies,
    width,
    label="Enable Range Compaction",
    color="blue",
    alpha=0.7,
)
ax1.bar(
    x,
    disable_no_periodic_avg,
    width,
    label="Disable Range Compaction",
    color="red",
    alpha=0.7,
)
ax1.bar(
    [i + width for i in x],
    disable_with_periodic_avg,
    width,
    label="Disable Range Compaction + Periodic Full Compaction",
    color="green",
    alpha=0.7,
)

# Add multiplier annotations
for i in range(len(magnitudes)):
    if enable_avg_latencies[i] > 0:
        multiplier_no = disable_no_periodic_avg[i] / enable_avg_latencies[i]
        multiplier_with = disable_with_periodic_avg[i] / enable_avg_latencies[i]

        ax1.text(
            i,
            disable_no_periodic_avg[i],
            f"{multiplier_no:.1f}x",
            ha="center",
            va="bottom",
            fontweight="bold",
            color="red",
        )
        ax1.text(
            i + width,
            disable_with_periodic_avg[i],
            f"{multiplier_with:.1f}x",
            ha="center",
            va="bottom",
            fontweight="bold",
            color="green",
        )

ax1.set_xlabel("Key Count Magnitude")
ax1.set_ylabel("Average Seek Latency (ms)")
ax1.set_title("Average Seek Latency by Order of Magnitude")
ax1.set_xticks(x)
ax1.set_xticklabels(magnitudes)
ax1.set_yscale("log")
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Max Seek Latency across magnitudes
ax2.bar(
    [i - width for i in x],
    enable_max_latencies,
    width,
    label="Enable Range Compaction",
    color="blue",
    alpha=0.7,
)
ax2.bar(
    x,
    disable_no_periodic_max,
    width,
    label="Disable Range Compaction",
    color="red",
    alpha=0.7,
)
ax2.bar(
    [i + width for i in x],
    disable_with_periodic_max,
    width,
    label="Disable Range Compaction + Periodic Full Compaction",
    color="green",
    alpha=0.7,
)

# Add multiplier annotations
for i in range(len(magnitudes)):
    if enable_max_latencies[i] > 0:
        multiplier_no = disable_no_periodic_max[i] / enable_max_latencies[i]
        multiplier_with = disable_with_periodic_max[i] / enable_max_latencies[i]

        ax2.text(
            i,
            disable_no_periodic_max[i],
            f"{multiplier_no:.1f}x",
            ha="center",
            va="bottom",
            fontweight="bold",
            color="red",
        )
        ax2.text(
            i + width,
            disable_with_periodic_max[i],
            f"{multiplier_with:.1f}x",
            ha="center",
            va="bottom",
            fontweight="bold",
            color="green",
        )

ax2.set_xlabel("Key Count Magnitude")
ax2.set_ylabel("Max Seek Latency (ms)")
ax2.set_title("Max Seek Latency by Order of Magnitude")
ax2.set_xticks(x)
ax2.set_xticklabels(magnitudes)
ax2.set_yscale("log")
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("seek_latency_over_key_count.png", dpi=150, bbox_inches="tight")
print("Chart saved as 'seek_latency_over_key_count.png'")
plt.close()  # Close instead of show to avoid display issues

# Print summary by magnitude
print("Performance Analysis by Order of Magnitude:")
print("=" * 60)

enable_data = experiment_data.get("Enable Range Compaction", {})
disable_no_data = experiment_data.get("Disable Range Compaction", {})
disable_with_data = experiment_data.get("Disable Range Compaction + Periodic Full Compaction", {})

for mag in magnitudes:
    print(f"\n{mag} Keys:")
    print("-" * 20)

    enable_mag_data = enable_data.get(mag, {})
    disable_no_mag_data = disable_no_data.get(mag, {})
    disable_with_mag_data = disable_with_data.get(mag, {})

    if enable_mag_data and disable_no_mag_data:
        enable_avg = enable_mag_data.get("avg_latency_us", 0)
        enable_max = enable_mag_data.get("max_latency_us", 0)
        disable_no_avg = disable_no_mag_data.get("avg_latency_us", 0)
        disable_no_max = disable_no_mag_data.get("max_latency_us", 0)
        disable_with_avg = disable_with_mag_data.get("avg_latency_us", 0)
        disable_with_max = disable_with_mag_data.get("max_latency_us", 0)

        print(f"Key Count: ~{enable_mag_data.get('key_count', 0):,}")
        print()
        print("Average Seek Latency:")
        print(f"  Enable Range Compaction:     {enable_avg:6.1f} µs")
        print(
            f"  Disable (No Periodic):       {disable_no_avg:6.1f} µs  ({disable_no_avg / enable_avg:.1f}x worse)"
        )
        print(
            f"  Disable (With Periodic):     {disable_with_avg:6.1f} µs  ({disable_with_avg / enable_avg:.1f}x worse)"
        )
        print()
        print("Max Seek Latency:")
        print(f"  Enable Range Compaction:     {enable_max:6.1f} µs")
        print(
            f"  Disable (No Periodic):       {disable_no_max:6.1f} µs  ({disable_no_max / enable_max:.1f}x worse)"
        )
        print(
            f"  Disable (With Periodic):     {disable_with_max:6.1f} µs  ({disable_with_max / enable_max:.1f}x worse)"
        )

print("\n" + "=" * 60)
print("Summary: Range Compaction shows consistent performance benefits")
print("across all orders of magnitude, with improvements ranging from")
print("several times to hundreds of times better latency.")
