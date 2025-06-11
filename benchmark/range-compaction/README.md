# Range Compaction Benchmark

## Diagram

![Range Compaction Architecture](ozone_range_compaction_architecture_dense.png)

## Benchmark

### Steup

1. build ozone
2. clean old cluster and 

```bash
export COMPOSE_FILE=docker-compose.yaml:monitoring.yaml:profiling.yaml
OZONE_DATANODES=3 ./run.sh -d
```

### Run

#### 100M-20:8:1:enable-range-compaction:disable-peridioc-full-compaction

1. append to: `hadoop-ozone/dist/target/ozone-2.1.0-SNAPSHOT/compose/ozone/docker-config`
```
OZONE-SITE.XML_ozone.om.range.compaction.service.enabled=true
OZONE-SITE.XML_ozone.om.range.compaction.service.max.compaction.entries=3000000
```

2. start testing with mixed workload

```bash
ozone sh volume create vol1
ozone sh bucket create /vol1/bucket1 --layout OBJECT_STORE
ozone freon omkeybench -n 100000000 -t 100 --size=0 --volume vol1 --bucket bucket1 --weights create:20,delete:8,list:1 --max-live-keys 25000
```

3. result
```bash
 84.95% |?????????????????????????????      |  84952175/100000000 Time: 14:41:27|  live=25000/25000 created=58592882 deleted=23415201 [LIMIT_REACHED] CREATE: rate 1584 max 1827 DELETE: rate 640 max 765 LIST: rate 67 max 117^C6/10/25, 5:45:13?PM ============================================================

-- Timers ----------------------------------------------------------------------
CREATE
             count = 58593186
         mean rate = 1107.92 calls/second
     1-minute rate = 971.33 calls/second
     5-minute rate = 1092.89 calls/second
    15-minute rate = 1111.86 calls/second
               min = 41.27 milliseconds
               max = 2299.82 milliseconds
              mean = 103.17 milliseconds
            stddev = 222.31 milliseconds
            median = 51.70 milliseconds
              75% <= 56.23 milliseconds
              95% <= 635.08 milliseconds
              98% <= 975.32 milliseconds
              99% <= 1092.38 milliseconds
            99.9% <= 2161.26 milliseconds
DELETE
             count = 23430361
         mean rate = 443.04 calls/second
     1-minute rate = 387.40 calls/second
     5-minute rate = 437.36 calls/second
    15-minute rate = 444.54 calls/second
               min = 17.24 milliseconds
               max = 2133.06 milliseconds
              mean = 47.69 milliseconds
            stddev = 153.30 milliseconds
            median = 24.91 milliseconds
              75% <= 27.03 milliseconds
              95% <= 33.94 milliseconds
              98% <= 595.95 milliseconds
              99% <= 1015.15 milliseconds
            99.9% <= 2133.06 milliseconds
LIST
             count = 2929047
         mean rate = 55.39 calls/second
     1-minute rate = 48.36 calls/second
     5-minute rate = 54.45 calls/second
    15-minute rate = 55.52 calls/second
               min = 2.71 milliseconds
               max = 224.15 milliseconds
              mean = 35.20 milliseconds
            stddev = 11.97 milliseconds
            median = 34.10 milliseconds
              75% <= 37.52 milliseconds
              95% <= 44.80 milliseconds
              98% <= 50.49 milliseconds
              99% <= 53.08 milliseconds
            99.9% <= 218.51 milliseconds


Total execution time (sec): 52888
Failures: 0
Successful executions: 84952642
```
#### 100M-20:8:1:disable-range-compaction:disable-peridioc-full-compaction

1. remove all additional config in: `hadoop-ozone/dist/target/ozone-2.1.0-SNAPSHOT/compose/ozone/docker-config`
2. start testing with mixed workload
```bash
ozone sh volume create vol1
ozone sh bucket create /vol1/bucket1 --layout OBJECT_STORE
ozone freon omkeybench -n 100000000 -t 100 --size=0 --volume vol1 --bucket bucket1 --weights create:20,delete:8,list:1 --max-live-keys 25000
```

3. result

```bash
 86.22% |?????????????????????????????     |  86216505/100000000 Time: 14:57:58|  live=25000/25000 created=59461613 deleted=23765495 [LIMIT_REACHED] CREATE: rate 1362 max 1833 DELETE: rate 519 max 781 LIST: rate 64 max

-- Timers ----------------------------------------------------------------------
CREATE
             count = 59462027
         mean rate = 1103.67 calls/second
     1-minute rate = 1310.73 calls/second
     5-minute rate = 1161.31 calls/second
    15-minute rate = 1105.73 calls/second
               min = 41.91 milliseconds
               max = 1399.99 milliseconds
              mean = 59.52 milliseconds
            stddev = 84.32 milliseconds
            median = 50.06 milliseconds
              75% <= 54.26 milliseconds
              95% <= 62.51 milliseconds
              98% <= 72.90 milliseconds
              99% <= 244.92 milliseconds
            99.9% <= 1356.15 milliseconds
DELETE
             count = 23780956
         mean rate = 441.40 calls/second
     1-minute rate = 524.92 calls/second
     5-minute rate = 464.70 calls/second
    15-minute rate = 442.04 calls/second
               min = 17.94 milliseconds
               max = 1375.04 milliseconds
              mean = 31.57 milliseconds
            stddev = 63.75 milliseconds
            median = 24.31 milliseconds
              75% <= 26.45 milliseconds
              95% <= 30.87 milliseconds
              98% <= 59.64 milliseconds
              99% <= 191.86 milliseconds
            99.9% <= 739.98 milliseconds
LIST
             count = 2974075
         mean rate = 55.20 calls/second
     1-minute rate = 64.50 calls/second
     5-minute rate = 57.72 calls/second
    15-minute rate = 55.15 calls/second
               min = 1.79 milliseconds
               max = 243.03 milliseconds
              mean = 32.84 milliseconds
            stddev = 11.82 milliseconds
            median = 31.56 milliseconds
              75% <= 35.07 milliseconds
              95% <= 42.64 milliseconds
              98% <= 46.73 milliseconds
              99% <= 49.98 milliseconds
            99.9% <= 190.79 milliseconds


Total execution time (sec): 53879
Failures: 0
Successful executions: 86217148
```
#### 100M-20:8:1:disable-range-compaction:enable-peridioc-full-compaction

1. append config to: `hadoop-ozone/dist/target/ozone-2.1.0-SNAPSHOT/compose/ozone/docker-config`
```
OZONE-SITE.XML_ozone.compaction.service.enabled=true
OZONE-SITE.XML_ozone.om.compaction.service.run.interval=1h
```

2. start testing with mixed workload
```bash
ozone sh volume create vol1
ozone sh bucket create /vol1/bucket1 --layout OBJECT_STORE
ozone freon omkeybench -n 100000000 -t 100 --size=0 --volume vol1 --bucket bucket1 --weights create:20,delete:8,list:1 --max-live-keys 25000
```
