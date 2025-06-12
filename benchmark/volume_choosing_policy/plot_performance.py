import matplotlib.pyplot as plt
import numpy as np

# Data for Avg Time/Op (ns)
avg_time_data = {
    'With Sync, With Thread Local': {
        'Capacity': [219220.33, 97574.13, 96381.87, 80319.32, 86205.67],
        'RoundRobin': [37832.11, 443.20, 19598.97, 18725.32, 12851.31]
    },
    'With Sync, Without Thread Local': {
        'Capacity': [231855.81, 114718.44, 101369.19, 81755.05, 88869.84],
        'RoundRobin': [22846.68, 11917.92, 4906.60, 12549.53, 14802.62]
    },
    'Without Sync, With Thread Local': {
        'Capacity': [309762.90, 22590.46, 40294.53, 16294.46, 27330.50],
        'RoundRobin': [4182.50, 2136.61, 758.19, 3259.56, 3103.94]
    },
    'Without Sync, Without Thread Local': {
        'Capacity': [105121.62, 16984.40, 19526.82, 17929.63, 18080.51],
        'RoundRobin': [4400.21, 2448.66, 2283.78, 2659.73, 1516.45]
    }
}

# Data for Ops/sec
ops_sec_data = {
    'With Sync, With Thread Local': {
        'Capacity': [4561.62, 10248.62, 10375.40, 12450.30, 11600.16],
        'RoundRobin': [26432.57, 2256300.74, 51023.10, 53403.64, 77813.05]
    },
    'With Sync, Without Thread Local': {
        'Capacity': [4313.03, 8716.99, 9864.93, 12231.66, 11252.41],
        'RoundRobin': [43770.04, 83907.28, 203806.99, 79684.23, 67555.62]
    },
    'Without Sync, With Thread Local': {
        'Capacity': [3228.28, 44266.48, 24817.26, 61370.56, 36589.16],
        'RoundRobin': [239091.64, 468031.59, 1318923.39, 306789.71, 322171.52]
    },
    'Without Sync, Without Thread Local': {
        'Capacity': [9512.79, 58877.57, 51211.62, 55773.59, 55308.16],
        'RoundRobin': [227262.01, 408386.00, 437871.19, 375978.72, 659432.70]
    }
}

def plot_metrics(data, title, ylabel, filename):
    plt.figure(figsize=(22, 8))
    n_tests = 5
    n_cfgs = 4
    barWidth = 0.18
    cfgs = [
        ('With Sync, With Thread Local', '#1f77b4'),
        ('With Sync, Without Thread Local', '#ff7f0e'),
        ('Without Sync, With Thread Local', '#2ca02c'),
        ('Without Sync, Without Thread Local', '#d62728'),
    ]
    
    # For each test, we have 8 bars: 4 for Capacity, 4 for RoundRobin
    x = np.arange(n_tests * 2)  # 2 types per test
    
    # For each config, collect bar heights for all test/type positions
    bar_vals = [[] for _ in range(n_cfgs)]
    for test in range(n_tests):
        for policy in ['Capacity', 'RoundRobin']:
            for i, (cfg, _) in enumerate(cfgs):
                bar_vals[i].append(data[cfg][policy][test])
    
    # Plot bars
    for i, (cfg, color) in enumerate(cfgs):
        plt.bar(x + (i - 1.5) * barWidth, bar_vals[i], width=barWidth, color=color, label=cfg)
    
    # X-tick labels
    xlabels = []
    for test in range(n_tests):
        xlabels.append(f'T{test+1} Cap')
        xlabels.append(f'T{test+1} RR')
    plt.xticks(x, xlabels, rotation=0)
    
    plt.xlabel('Test Run and Policy Type')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.yscale('log')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', dpi=300)
    plt.close()

# Create plots
plot_metrics(avg_time_data, 'Average Time per Operation (ns)', 'Time (ns)', 'avg_time_per_op.png')
plot_metrics(ops_sec_data, 'Operations per Second', 'Ops/sec', 'ops_per_sec.png') 