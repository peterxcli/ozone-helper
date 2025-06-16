"""
Compaction metrics analysis using shared utilities.
Analyzes compaction write bytes and time average across different orders of magnitude.
"""

import matplotlib.pyplot as plt
from benchmark_utils import (
    EXPERIMENT_FOLDERS,
    MAGNITUDE_LABELS,
    TARGET_MAGNITUDES,
    create_magnitude_label,
    extract_magnitude_data,
    find_magnitude_index,
    get_key_count_data,
    parse_bytes_value,
    parse_time_value,
    read_csv_data,
    save_chart,
)


def get_compaction_metrics_data():
    """Extract compaction metrics data at different magnitudes using shared utilities"""
    data = {}

    # Get shared key count data
    key_count_df, key_count_col = get_key_count_data()
    if key_count_df is None:
        return {}

    # Get compaction metrics for each experiment
    for experiment_name, folder_name in EXPERIMENT_FOLDERS.items():
        compaction_write_df = read_csv_data(folder_name, "Compaction write bytes*.csv")
        compaction_time_df = read_csv_data(folder_name, "Compaction time average*.csv")

        if compaction_write_df is None or compaction_time_df is None:
            continue

        compaction_write_col = compaction_write_df.columns[1]
        compaction_time_col = compaction_time_df.columns[1]
        
        # Calculate max compaction write bytes for each magnitude
        def get_max_write_bytes_at_magnitude(target_mag):
            closest_idx = find_magnitude_index(key_count_df, key_count_col, target_mag)
            if closest_idx is not None and closest_idx < len(key_count_df):
                # Get all values up to this point and find the max
                write_idx_end = min(closest_idx + 1, len(compaction_write_df))
                max_write_val = 0
                for i in range(write_idx_end):
                    val = parse_bytes_value(compaction_write_df[compaction_write_col].iloc[i])
                    max_write_val = max(max_write_val, val)
                return max_write_val
            return 0

        # Extract data at target magnitudes
        magnitude_data = {}

        for target_mag in TARGET_MAGNITUDES:
            mag_label = create_magnitude_label(target_mag)

            # Extract write bytes data
            write_data = extract_magnitude_data(
                compaction_write_df,
                compaction_write_col,
                key_count_df,
                key_count_col,
                target_mag,
                parse_bytes_value,
            )

            # Extract time data
            time_data = extract_magnitude_data(
                compaction_time_df,
                compaction_time_col,
                key_count_df,
                key_count_col,
                target_mag,
                parse_time_value,
            )

            # Get max write bytes up to this magnitude
            max_write_bytes = get_max_write_bytes_at_magnitude(target_mag)

            if write_data and time_data:
                magnitude_data[mag_label] = {
                    "write_bytes_mb": write_data["value"],
                    "max_write_bytes_mb": max_write_bytes,
                    "time_seconds": time_data["value"],
                    "key_count": write_data["key_count"],
                    "target_magnitude": target_mag,
                }

        data[experiment_name] = magnitude_data

    return data


def create_compaction_visualization(experiment_data):
    """Create visualization for compaction metrics"""
    _, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

    # Prepare data arrays
    enable_write_bytes = []
    enable_max_write_bytes = []
    enable_time_seconds = []
    disable_write_bytes = []
    disable_max_write_bytes = []
    disable_time_seconds = []
    disable_with_periodic_write_bytes = []
    disable_with_periodic_max_write_bytes = []
    disable_with_periodic_time_seconds = []

    enable_data = experiment_data.get("Enable Range Compaction", {})
    disable_no_data = experiment_data.get("Disable Range Compaction", {})
    disable_with_data = experiment_data.get(
        "Disable Range Compaction + Periodic Full Compaction", {}
    )

    for mag in MAGNITUDE_LABELS:
        # Get metrics for each configuration at this magnitude
        enable_write = enable_data.get(mag, {}).get("write_bytes_mb", 0)
        enable_max_write = enable_data.get(mag, {}).get("max_write_bytes_mb", 0)
        enable_time = enable_data.get(mag, {}).get("time_seconds", 0)

        disable_write = disable_no_data.get(mag, {}).get("write_bytes_mb", 0)
        disable_max_write = disable_no_data.get(mag, {}).get("max_write_bytes_mb", 0)
        disable_time = disable_no_data.get(mag, {}).get("time_seconds", 0)

        disable_with_write = disable_with_data.get(mag, {}).get("write_bytes_mb", 0)
        disable_with_max_write = disable_with_data.get(mag, {}).get("max_write_bytes_mb", 0)
        disable_with_time = disable_with_data.get(mag, {}).get("time_seconds", 0)

        # Store values for plotting (use tiny value for true zeros to make them barely visible)
        enable_write_bytes.append(0.0001 if enable_write == 0 else enable_write)
        enable_max_write_bytes.append(0.0001 if enable_max_write == 0 else enable_max_write)
        enable_time_seconds.append(max(enable_time, 0.001))
        disable_write_bytes.append(0.0001 if disable_write == 0 else disable_write)
        disable_max_write_bytes.append(0.0001 if disable_max_write == 0 else disable_max_write)
        disable_time_seconds.append(max(disable_time, 0.001))
        disable_with_periodic_write_bytes.append(0.0001 if disable_with_write == 0 else disable_with_write)
        disable_with_periodic_max_write_bytes.append(0.0001 if disable_with_max_write == 0 else disable_with_max_write)
        disable_with_periodic_time_seconds.append(max(disable_with_time, 0.001))

    # Store original values for multiplier calculations (before log scale adjustment)
    orig_enable_write = [enable_data.get(mag, {}).get("write_bytes_mb", 0) for mag in MAGNITUDE_LABELS]
    orig_enable_max_write = [enable_data.get(mag, {}).get("max_write_bytes_mb", 0) for mag in MAGNITUDE_LABELS]
    orig_enable_time = [enable_data.get(mag, {}).get("time_seconds", 0) for mag in MAGNITUDE_LABELS]
    orig_disable_write = [disable_no_data.get(mag, {}).get("write_bytes_mb", 0) for mag in MAGNITUDE_LABELS]
    orig_disable_max_write = [disable_no_data.get(mag, {}).get("max_write_bytes_mb", 0) for mag in MAGNITUDE_LABELS]
    orig_disable_time = [disable_no_data.get(mag, {}).get("time_seconds", 0) for mag in MAGNITUDE_LABELS]
    orig_disable_with_write = [disable_with_data.get(mag, {}).get("write_bytes_mb", 0) for mag in MAGNITUDE_LABELS]
    orig_disable_with_max_write = [disable_with_data.get(mag, {}).get("max_write_bytes_mb", 0) for mag in MAGNITUDE_LABELS]
    orig_disable_with_time = [disable_with_data.get(mag, {}).get("time_seconds", 0) for mag in MAGNITUDE_LABELS]

    # Plot settings
    width = 0.25
    x = range(len(MAGNITUDE_LABELS))
    colors = {"enable": "blue", "disable": "red", "periodic": "green"}

    # Plot 1: Compaction Write Bytes (Average)
    # Use different alpha for zero values to distinguish them
    enable_alphas = [0.3 if orig_enable_write[i] == 0 else 0.7 for i in range(len(x))]
    disable_alphas = [0.3 if orig_disable_write[i] == 0 else 0.7 for i in range(len(x))]
    periodic_alphas = [0.3 if orig_disable_with_write[i] == 0 else 0.7 for i in range(len(x))]
    
    for i in range(len(x)):
        ax1.bar(
            i - width,
            enable_write_bytes[i],
            width,
            color=colors["enable"],
            alpha=enable_alphas[i],
            label="Enable Range Compaction" if i == 0 else "",
        )
        ax1.bar(
            i,
            disable_write_bytes[i],
            width,
            color=colors["disable"],
            alpha=disable_alphas[i],
            label="Disable Range Compaction" if i == 0 else "",
        )
        ax1.bar(
            i + width,
            disable_with_periodic_write_bytes[i],
            width,
            color=colors["periodic"],
            alpha=periodic_alphas[i],
            label="Disable Range Compaction + Periodic Full Compaction" if i == 0 else "",
        )

    # Add multiplier annotations for write bytes
    for i in range(len(MAGNITUDE_LABELS)):
        # Handle Disable Range Compaction multiplier
        if orig_enable_write[i] > 0:
            if orig_disable_write[i] > 0:
                multiplier_no = orig_disable_write[i] / orig_enable_write[i]
                ax1.text(
                    i,
                    disable_write_bytes[i],
                    f"{multiplier_no:.1f}x",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    color=colors["disable"],
                )
            else:
                # Show that it's much smaller (approaching 0)
                ax1.text(
                    i,
                    disable_write_bytes[i] * 2,
                    "0",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    fontsize=10,
                    color=colors["disable"],
                )
        elif orig_disable_write[i] > 0:
            # Enable is 0 but Disable has value - show as much larger
            ax1.text(
                i,
                disable_write_bytes[i],
                "∞x",
                ha="center",
                va="center",  # Center vertically on the bar
                fontweight="bold",
                fontsize=10,
                color="white",  # White text on colored bar
                bbox=dict(boxstyle="round,pad=0.2", facecolor=colors["disable"], alpha=0.8),
            )

        # Handle Disable Range Compaction + Periodic multiplier
        if orig_enable_write[i] > 0:
            if orig_disable_with_write[i] > 0:
                multiplier_with = orig_disable_with_write[i] / orig_enable_write[i]
                ax1.text(
                    i + width,
                    disable_with_periodic_write_bytes[i],
                    f"{multiplier_with:.1f}x",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    color=colors["periodic"],
                )
            else:
                # Show that it's much smaller (approaching 0)
                ax1.text(
                    i + width,
                    disable_with_periodic_write_bytes[i] * 2,
                    "0",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    fontsize=10,
                    color=colors["periodic"],
                )
        elif orig_disable_with_write[i] > 0:
            # Enable is 0 but Disable+Periodic has value - show as much larger
            ax1.text(
                i + width,
                disable_with_periodic_write_bytes[i],
                "∞x",
                ha="center",
                va="center",  # Center vertically on the bar
                fontweight="bold",
                fontsize=10,
                color="white",  # White text on colored bar
                bbox=dict(boxstyle="round,pad=0.2", facecolor=colors["periodic"], alpha=0.8),
            )

    ax1.set_xlabel("Key Count Magnitude")
    ax1.set_ylabel("Compaction Write Bytes (MB)")
    ax1.set_title("Average Compaction Write Bytes by Order of Magnitude")
    ax1.set_xticks(x)
    ax1.set_xticklabels(MAGNITUDE_LABELS)
    ax1.set_yscale("log")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Max Compaction Write Bytes
    # Use different alpha for zero values to distinguish them
    enable_max_alphas = [0.3 if orig_enable_max_write[i] == 0 else 0.7 for i in range(len(x))]
    disable_max_alphas = [0.3 if orig_disable_max_write[i] == 0 else 0.7 for i in range(len(x))]
    periodic_max_alphas = [0.3 if orig_disable_with_max_write[i] == 0 else 0.7 for i in range(len(x))]
    
    for i in range(len(x)):
        ax2.bar(
            i - width,
            enable_max_write_bytes[i],
            width,
            color=colors["enable"],
            alpha=enable_max_alphas[i],
            label="Enable Range Compaction" if i == 0 else "",
        )
        ax2.bar(
            i,
            disable_max_write_bytes[i],
            width,
            color=colors["disable"],
            alpha=disable_max_alphas[i],
            label="Disable Range Compaction" if i == 0 else "",
        )
        ax2.bar(
            i + width,
            disable_with_periodic_max_write_bytes[i],
            width,
            color=colors["periodic"],
            alpha=periodic_max_alphas[i],
            label="Disable Range Compaction + Periodic Full Compaction" if i == 0 else "",
        )

    # Add multiplier annotations for max write bytes
    for i in range(len(MAGNITUDE_LABELS)):
        # Handle Disable Range Compaction multiplier
        if orig_enable_max_write[i] > 0:
            if orig_disable_max_write[i] > 0:
                multiplier_no = orig_disable_max_write[i] / orig_enable_max_write[i]
                ax2.text(
                    i,
                    disable_max_write_bytes[i],
                    f"{multiplier_no:.1f}x",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    color=colors["disable"],
                )
            else:
                # Show that it's much smaller (approaching 0)
                ax2.text(
                    i,
                    disable_max_write_bytes[i] * 2,
                    "0",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    fontsize=10,
                    color=colors["disable"],
                )
        elif orig_disable_max_write[i] > 0:
            # Enable is 0 but Disable has value - show as much larger
            ax2.text(
                i,
                disable_max_write_bytes[i],
                "∞x",
                ha="center",
                va="center",  # Center vertically on the bar
                fontweight="bold",
                fontsize=10,
                color="white",  # White text on colored bar
                bbox=dict(boxstyle="round,pad=0.2", facecolor=colors["disable"], alpha=0.8),
            )

        # Handle Disable Range Compaction + Periodic multiplier
        if orig_enable_max_write[i] > 0:
            if orig_disable_with_max_write[i] > 0:
                multiplier_with = orig_disable_with_max_write[i] / orig_enable_max_write[i]
                ax2.text(
                    i + width,
                    disable_with_periodic_max_write_bytes[i],
                    f"{multiplier_with:.1f}x",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    color=colors["periodic"],
                )
            else:
                # Show that it's much smaller (approaching 0)
                ax2.text(
                    i + width,
                    disable_with_periodic_max_write_bytes[i] * 2,
                    "0",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    fontsize=10,
                    color=colors["periodic"],
                )
        elif orig_disable_with_max_write[i] > 0:
            # Enable is 0 but Disable+Periodic has value - show as much larger
            ax2.text(
                i + width,
                disable_with_periodic_max_write_bytes[i],
                "∞x",
                ha="center",
                va="center",  # Center vertically on the bar
                fontweight="bold",
                fontsize=10,
                color="white",  # White text on colored bar
                bbox=dict(boxstyle="round,pad=0.2", facecolor=colors["periodic"], alpha=0.8),
            )

    ax2.set_xlabel("Key Count Magnitude")
    ax2.set_ylabel("Max Compaction Write Bytes (MB)")
    ax2.set_title("Max Compaction Write Bytes by Order of Magnitude")
    ax2.set_xticks(x)
    ax2.set_xticklabels(MAGNITUDE_LABELS)
    ax2.set_yscale("log")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Plot 3: Compaction Time Average
    ax3.bar(
        [i - width for i in x],
        enable_time_seconds,
        width,
        label="Enable Range Compaction",
        color=colors["enable"],
        alpha=0.7,
    )
    ax3.bar(
        x,
        disable_time_seconds,
        width,
        label="Disable Range Compaction",
        color=colors["disable"],
        alpha=0.7,
    )
    ax3.bar(
        [i + width for i in x],
        disable_with_periodic_time_seconds,
        width,
        label="Disable Range Compaction + Periodic Full Compaction",
        color=colors["periodic"],
        alpha=0.7,
    )

    # Add multiplier annotations for time
    for i in range(len(MAGNITUDE_LABELS)):
        if orig_enable_time[i] > 0:
            if orig_disable_time[i] > 0:
                multiplier_no = orig_disable_time[i] / orig_enable_time[i]
                ax3.text(
                    i,
                    disable_time_seconds[i],
                    f"{multiplier_no:.1f}x",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    color=colors["disable"],
                )

            if orig_disable_with_time[i] > 0:
                multiplier_with = orig_disable_with_time[i] / orig_enable_time[i]
                ax3.text(
                    i + width,
                    disable_with_periodic_time_seconds[i],
                    f"{multiplier_with:.1f}x",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    color=colors["periodic"],
                )

    ax3.set_xlabel("Key Count Magnitude")
    ax3.set_ylabel("Compaction Time Average (seconds)")
    ax3.set_title("Compaction Time Average by Order of Magnitude")
    ax3.set_xticks(x)
    ax3.set_xticklabels(MAGNITUDE_LABELS)
    ax3.set_yscale("log")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Plot 4: Leave empty or add summary text
    ax4.axis('off')
    ax4.text(0.5, 0.5, "Compaction Metrics Analysis\nAcross Key Count Orders of Magnitude\n\n• Average Write Bytes (top-left)\n• Max Write Bytes (top-right)\n• Average Time (bottom-left)", 
             ha='center', va='center', fontsize=12, transform=ax4.transAxes)

    save_chart("compaction_metrics_over_key_count.png")


def print_compaction_summary(experiment_data):
    """Print detailed summary of compaction metrics"""
    print("Compaction Performance Analysis by Order of Magnitude:")
    print("=" * 70)

    enable_data = experiment_data.get("Enable Range Compaction", {})
    disable_no_data = experiment_data.get("Disable Range Compaction", {})
    disable_with_data = experiment_data.get(
        "Disable Range Compaction + Periodic Full Compaction", {}
    )

    for mag in MAGNITUDE_LABELS:
        print(f"\n{mag} Keys:")
        print("-" * 20)

        enable_mag_data = enable_data.get(mag, {})
        disable_no_mag_data = disable_no_data.get(mag, {})
        disable_with_mag_data = disable_with_data.get(mag, {})

        if enable_mag_data:
            enable_write = enable_mag_data.get("write_bytes_mb", 0)
            enable_time = enable_mag_data.get("time_seconds", 0)
            disable_no_write = disable_no_mag_data.get("write_bytes_mb", 0)
            disable_no_time = disable_no_mag_data.get("time_seconds", 0)
            disable_with_write = disable_with_mag_data.get("write_bytes_mb", 0)
            disable_with_time = disable_with_mag_data.get("time_seconds", 0)

            enable_max_write = enable_mag_data.get("max_write_bytes_mb", 0)
            disable_no_max_write = disable_no_mag_data.get("max_write_bytes_mb", 0)
            disable_with_max_write = disable_with_mag_data.get("max_write_bytes_mb", 0)

            print(f"Key Count: ~{enable_mag_data.get('key_count', 0):,}")
            print()
            print("Average Compaction Write Bytes:")
            print(f"  Enable Range Compaction:     {enable_write:8.1f} MB")
            if enable_write > 0:
                print(
                    f"  Disable Range Compaction:    {disable_no_write:8.1f} MB  ({disable_no_write / enable_write:.1f}x)"
                )
                print(
                    f"  Disable + Periodic Full:     {disable_with_write:8.1f} MB  ({disable_with_write / enable_write:.1f}x)"
                )
            print()
            print("Max Compaction Write Bytes:")
            print(f"  Enable Range Compaction:     {enable_max_write:8.1f} MB")
            if enable_max_write > 0:
                print(
                    f"  Disable Range Compaction:    {disable_no_max_write:8.1f} MB  ({disable_no_max_write / enable_max_write:.1f}x)"
                )
                print(
                    f"  Disable + Periodic Full:     {disable_with_max_write:8.1f} MB  ({disable_with_max_write / enable_max_write:.1f}x)"
                )
            print()
            print("Compaction Time Average:")
            print(f"  Enable Range Compaction:     {enable_time:8.1f} sec")
            if enable_time > 0:
                print(
                    f"  Disable Range Compaction:    {disable_no_time:8.1f} sec  ({disable_no_time / enable_time:.1f}x)"
                )
                print(
                    f"  Disable + Periodic Full:     {disable_with_time:8.1f} sec  ({disable_with_time / enable_time:.1f}x)"
                )

    print("\n" + "=" * 70)
    print("Summary: Range Compaction shows different resource usage patterns")
    print("for compaction operations across different key count magnitudes.")


if __name__ == "__main__":
    # Get experiment data
    experiment_data = get_compaction_metrics_data()

    # Create visualization
    create_compaction_visualization(experiment_data)

    # Print summary
    print_compaction_summary(experiment_data)
