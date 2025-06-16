"""
Shared utilities for benchmark analysis scripts.
Contains common functions for parsing data and reading experiment results.
"""

import glob
import os
import pandas as pd

# Common experiment folder configuration
EXPERIMENT_FOLDERS = {
    "Enable Range Compaction": "100M-20:8:1:enable-range-compaction:disable-peridioc-full-compaction",
    "Disable Range Compaction": "100M-20:8:1:disable-range-compaction:disable-peridioc-full-compaction",
    "Disable Range Compaction + Periodic Full Compaction": "100M-20:8:1:disable-range-compaction:enable-peridioc-full-compaction",
}

# Standard magnitude targets for analysis
TARGET_MAGNITUDES = [10**5, 10**6, 10**7]  # 100K, 1M, 10M
MAGNITUDE_LABELS = ["10^5", "10^6", "10^7"]


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


def parse_bytes_value(value_str):
    """Parse byte value from string to MB"""
    if pd.isna(value_str) or value_str == "0" or value_str == 0:
        return 0

    value_str = str(value_str).strip()
    
    # Handle byte units (convert to MB for consistency)
    if "GB" in value_str or "G" in value_str:
        return float(value_str.replace(" GB", "").replace("GB", "").replace(" G", "").replace("G", "")) * 1024
    elif "MB" in value_str or "M" in value_str:
        return float(value_str.replace(" MB", "").replace("MB", "").replace(" M", "").replace("M", ""))
    elif "KB" in value_str or "kB" in value_str or " k" in value_str or value_str.endswith("k"):
        return float(value_str.replace(" KB", "").replace("KB", "").replace(" kB", "").replace("kB", "").replace(" k", "").replace("k", "")) / 1024
    elif "B" in value_str and "MB" not in value_str and "GB" not in value_str and "KB" not in value_str and "kB" not in value_str:
        return float(value_str.replace(" B", "").replace("B", "")) / (1024 * 1024)
    else:
        # Try to parse as plain number (assume bytes, convert to MB)
        try:
            return float(value_str) / (1024 * 1024)
        except ValueError:
            return 0


def parse_time_value(value_str):
    """Parse time value from string to seconds"""
    if pd.isna(value_str) or value_str == "0" or value_str == 0:
        return 0

    value_str = str(value_str).strip()
    
    # Handle time units (convert to seconds)
    if "ms" in value_str:
        return float(value_str.replace(" ms", "").replace("ms", "")) / 1000
    elif "µs" in value_str or "us" in value_str:
        return float(value_str.replace(" µs", "").replace("µs", "").replace(" us", "").replace("us", "")) / 1000000
    elif "ns" in value_str:
        return float(value_str.replace(" ns", "").replace("ns", "")) / 1000000000
    elif "s" in value_str and "ms" not in value_str and "µs" not in value_str and "us" not in value_str and "ns" not in value_str:
        return float(value_str.replace(" s", "").replace("s", ""))
    else:
        # Try to parse as plain number (assume seconds)
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


def get_key_count_data():
    """Get key count progression data (same across all experiments)"""
    key_count_folder = list(EXPERIMENT_FOLDERS.values())[0]
    key_count_df = read_csv_data(
        key_count_folder, "KeyTable Estimated number of keys*.csv"
    )
    
    if key_count_df is None:
        return None, None
        
    key_count_col = key_count_df.columns[1]
    return key_count_df, key_count_col


def find_magnitude_index(key_count_df, key_count_col, target_magnitude):
    """Find the closest index where key count reaches the target magnitude"""
    closest_idx = None
    min_diff = float("inf")

    key_counts = key_count_df[key_count_col].values
    for i, key_count in enumerate(key_counts):
        if key_count >= target_magnitude:
            diff = abs(key_count - target_magnitude)
            if diff < min_diff:
                min_diff = diff
                closest_idx = i
            break
    
    return closest_idx


def extract_magnitude_data(df, col_name, key_count_df, key_count_col, target_mag, parser_func):
    """Extract data at a specific magnitude, handling file length differences"""
    closest_idx = find_magnitude_index(key_count_df, key_count_col, target_mag)
    
    if closest_idx is not None and closest_idx < len(key_count_df):
        # Use the closest available index for the metric file
        metric_idx = min(closest_idx, len(df) - 1) if len(df) > 0 else None
        
        if metric_idx is not None:
            metric_val = parser_func(df[col_name].iloc[metric_idx])
            actual_key_count = key_count_df[key_count_col].iloc[closest_idx]
            
            return {
                "value": metric_val,
                "key_count": actual_key_count,
                "target_magnitude": target_mag,
            }
    
    return None


def create_magnitude_label(target_mag):
    """Create a magnitude label like '10^5' from a number like 100000"""
    return f"10^{len(str(target_mag)) - 1}"


def save_chart(filename, dpi=150):
    """Save matplotlib chart with standard settings"""
    import matplotlib.pyplot as plt
    
    plt.tight_layout()
    plt.savefig(filename, dpi=dpi, bbox_inches="tight")
    print(f"Chart saved as '{filename}'")
    plt.close()