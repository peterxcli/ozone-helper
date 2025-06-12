import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Extrapolated + measured data
data = {
    "Magnitude": ["10^5", "10^6", "10^7"],
    "Seek Latency Max / Enable range compaction": [
        "52.6 µs",
        "868 µs",
        "2.15 ms",
    ],
    "Seek Latency Max / Disable range compaction": [
        "77.5 µs",
        "991 µs",
        "7.75 ms",
    ],
    "Seek Latency Average / Enable range compaction": [
        "58.2 µs",
        "110.0 µs",
        "216.6 µs",
    ],
    "Seek Latency Average / Disable range compaction": [
        "1584 µs",
        "5740 µs",
        "45606 µs",
    ],
}

df = pd.DataFrame(data)


# Convert latency string to milliseconds (for plotting)
def parse_latency(s):
    if "µs" in s:
        return float(s.replace(" µs", "")) * 1e-3
    elif "ms" in s:
        return float(s.replace(" ms", ""))
    else:
        return float(s)


# Max
df["Max_Enable"] = df["Seek Latency Max / Enable range compaction"].apply(parse_latency)
df["Max_Disable"] = df["Seek Latency Max / Disable range compaction"].apply(
    parse_latency
)
df["Max_Ratio"] = df["Max_Disable"] / df["Max_Enable"]
# Average
df["Avg_Enable"] = df["Seek Latency Average / Enable range compaction"].apply(
    parse_latency
)
df["Avg_Disable"] = df["Seek Latency Average / Disable range compaction"].apply(
    parse_latency
)
df["Avg_Ratio"] = df["Avg_Disable"] / df["Avg_Enable"]

x = np.arange(len(df))
bar_width = 0.35

# Convert cm to inches (1 inch = 2.54 cm)
scale = 0.8
width_cm = 16.61
height_cm = 9.96
width_inches = width_cm * scale
height_inches = height_cm * scale

fig, axes = plt.subplots(
    1, 2, figsize=(width_inches * scale, height_inches * scale), sharey=True
)

# --- Max plot ---
ax = axes[0]
bars1 = ax.bar(
    x - bar_width / 2,
    df["Max_Enable"],
    width=bar_width,
    label="Enable range compaction",
)
bars2 = ax.bar(
    x + bar_width / 2,
    df["Max_Disable"],
    width=bar_width,
    label="Disable range compaction",
)
for i, ratio in enumerate(df["Max_Ratio"]):
    ax.text(
        i,
        df["Max_Disable"][i],
        f"{ratio:.1f}x",
        ha="center",
        va="bottom",
        color="red",
        fontweight="bold",
        fontsize=16,
    )
ax.set_xticks(x)
ax.set_xticklabels(df["Magnitude"])
ax.set_yscale("log")
ax.set_ylabel("Max Seek Latency (ms)")
ax.set_xlabel("Key Count Magnitude")
ax.set_title("Max Seek Latency vs Key Count Magnitude")
ax.legend()

# --- Average plot ---
ax = axes[1]
bars1 = ax.bar(
    x - bar_width / 2,
    df["Avg_Enable"],
    width=bar_width,
    label="Enable range compaction",
)
bars2 = ax.bar(
    x + bar_width / 2,
    df["Avg_Disable"],
    width=bar_width,
    label="Disable range compaction",
)
for i, ratio in enumerate(df["Avg_Ratio"]):
    ax.text(
        i,
        df["Avg_Disable"][i],
        f"{ratio:.1f}x",
        ha="center",
        va="bottom",
        color="red",
        fontweight="bold",
        fontsize=16,
    )
ax.set_xticks(x)
ax.set_xticklabels(df["Magnitude"])
ax.set_yscale("log")
ax.set_ylabel("Average Seek Latency (ms)")
ax.set_xlabel("Key Count Magnitude")
ax.set_title("Average Seek Latency vs Key Count Magnitude")
ax.legend()

plt.tight_layout()
# Save with high DPI
plt.savefig("seek_latency_comparison.png", dpi=1000, bbox_inches="tight")
plt.show()
