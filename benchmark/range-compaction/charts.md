# Range Compaction Benchmark Charts

This document provides an overview of all the charts generated from the range compaction benchmark comparison.

## Overview

The benchmark compares two configurations:
- **Enable Range Compaction**: `100M-20:8:1:enable-range-compaction:disable-peridioc-full-compaction`
- **Disable Range Compaction**: `100M-20:8:1:disable-range-compaction:disable-peridioc-full-compaction`

## Charts

The following charts are available in the `comparison_charts` directory:

### Bytes Metrics
- ![Bytes read per second](comparison_charts/Bytes_read_per_second_comparison.png)
- ![Bytes write per second](comparison_charts/Bytes_write_per_second_comparison.png)

### Compaction Metrics
- ![Compaction read bytes](comparison_charts/Compaction_read_bytes_comparison.png)
- ![Compaction time average](comparison_charts/Compaction_time_average_comparison.png)
- ![Compaction write bytes](comparison_charts/Compaction_write_bytes_comparison.png)

### DB Metrics
- ![DB get 95%-tile](comparison_charts/DB_get_95__tile_comparison.png)
- ![DB get 99%-tile](comparison_charts/DB_get_99__tile_comparison.png)
- ![DB get average latency](comparison_charts/DB_get_average_latency_comparison.png)
- ![DB get median](comparison_charts/DB_get_median_comparison.png)

### DeletedTable Metrics
- ![DeletedTable Estimated number of keys](comparison_charts/DeletedTable_Estimated_number_of_keys_comparison.png)

### Flush Metrics
- ![Flush time average](comparison_charts/Flush_time_average_comparison.png)
- ![Flush write bytes](comparison_charts/Flush_write_bytes_comparison.png)
- ![Flush write median latency](comparison_charts/Flush_write_median_latency_comparison.png)

### KeyTable Metrics
- ![KeyTable Estimated number of keys](comparison_charts/KeyTable_Estimated_number_of_keys_comparison.png)

### Number Metrics
- ![Number of keys read per second](comparison_charts/Number_of_keys_read_per_second_comparison.png)
- ![Number of keys written per second](comparison_charts/Number_of_keys_written_per_second_comparison.png)
- ![Number of next per second](comparison_charts/Number_of_next_per_second_comparison.png)
- ![Number of seeks per second](comparison_charts/Number_of_seeks_per_second_comparison.png)

### SST Metrics
- ![SST file total size](comparison_charts/SST_file_total_size_comparison.png)

### Seek Metrics
- ![Seek 95%-tile latency (μs)](comparison_charts/Seek_95__tile_latency__us__comparison.png)
- ![Seek 99%-tile latency (μs)](comparison_charts/Seek_99__tile_latency__us__comparison.png)
- ![Seek average latency (μs)](comparison_charts/Seek_average_latency__us__comparison.png)
- ![Seek max latency](comparison_charts/Seek_max_latency_comparison.png)
- ![Seek median latency](comparison_charts/Seek_median_latency_comparison.png)

## Notes

- All throughput and rate metrics are smoothed using a 1-minute rolling window
- The seek latency chart uses a logarithmic scale for better visualization
- Time units are automatically adjusted based on the data range
- Size units are automatically adjusted based on the data range