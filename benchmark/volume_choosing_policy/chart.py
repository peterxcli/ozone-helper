import matplotlib.pyplot as plt
import numpy as np

# Data for each case (sync and non-sync)
# Format: (Time, Ops per second) for (Capacity, RoundRobin)
non_sync = [
    (233289, 4286.517532376812, 4447, 224846.598239716),
    (22574, 44298.03188885434, 2535, 394353.1966356877),
    (30423, 32869.0475190318, 2161, 462604.95170582406),
    (22998, 43481.84577760322, 560, 1785098.108099472),
    (21025, 47562.31456547484, 1218, 820817.6225078304),
]

sync = [
    (23017, 4344.568282773283, 4631, 21592.024036045965),
    (12646, 7907.254542514636, 1964, 50904.15421681072),
    (10471, 9549.418600746729, 1846, 54168.80648348698),
    (9374, 10667.336723333296, 1344, 74358.9398678661),
    (8875, 11267.223609540817, 1139, 87727.48052615956),
]

# Extracting the individual values for plotting
non_sync_capacity_time = [r[0] for r in non_sync]
non_sync_capacity_ops = [r[1] for r in non_sync]
non_sync_rr_time = [r[2] for r in non_sync]
non_sync_rr_ops = [r[3] for r in non_sync]

sync_capacity_time = [r[0] for r in sync]
sync_capacity_ops = [r[1] for r in sync]
sync_rr_time = [r[2] for r in sync]
sync_rr_ops = [r[3] for r in sync]

# Define bar width and positions for each group
bar_width = 0.2
index = np.arange(5)  # 5 groups of runs

# Create subplots with more space at the top for run labels
fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
fig.subplots_adjust(top=0.9)  # Add more space at the top

# Plot Time Spent (Bar Chart)
axs[0].bar(index - 0.5*bar_width, non_sync_capacity_time, bar_width, color="orange", label="Capacity (no sync)")
axs[0].bar(index + 0.5*bar_width, sync_capacity_time, bar_width, color="yellow", label="Capacity (sync)")
axs[0].bar(index + 1.5*bar_width, non_sync_rr_time, bar_width, color="red", label="RoundRobin (no sync)")
axs[0].bar(index + 2.5*bar_width, sync_rr_time, bar_width, color="pink", label="RoundRobin (sync)")

# Add run numbers above each group
for i in range(5):
    axs[0].text(i + bar_width, axs[0].get_ylim()[1], f"Run {i+1}", 
                ha='center', va='bottom', rotation=0)

axs[0].set_ylabel("Time (ns)")
axs[0].set_title("Time Spent per Run (Sync vs Non-Sync)")
axs[0].set_xticks(index + bar_width)
axs[0].set_xticklabels([])  # Remove x-tick labels since we have run numbers above
axs[0].legend()
axs[0].grid(True)
axs[0].set_yscale('log')  # Set logarithmic scale for y-axis

# Plot Operations per Second (Bar Chart)
axs[1].bar(index - 0.5*bar_width, non_sync_capacity_ops, bar_width, color="orange", label="Capacity (no sync)")
axs[1].bar(index + 0.5*bar_width, sync_capacity_ops, bar_width, color="yellow", label="Capacity (sync)")
axs[1].bar(index + 1.5*bar_width, non_sync_rr_ops, bar_width, color="red", label="RoundRobin (no sync)")
axs[1].bar(index + 2.5*bar_width, sync_rr_ops, bar_width, color="pink", label="RoundRobin (sync)")

# Add run numbers above each group
for i in range(5):
    axs[1].text(i + bar_width, axs[1].get_ylim()[1], f"Run {i+1}", 
                ha='center', va='bottom', rotation=0)

axs[1].set_ylabel("Operations per Second")
axs[1].set_xlabel("Run Number")
axs[1].set_xticks(index + bar_width)
axs[1].set_xticklabels([])  # Remove x-tick labels since we have run numbers above
axs[1].legend()
axs[1].grid(True)
axs[1].set_yscale('log')  # Set logarithmic scale for y-axis

plt.tight_layout()
plt.show()
