# Resource Scheduling (Concurrent Job Slots)

**Run it:** `uv run python -m patterns.07_intervals.de_scenarios.resource_scheduling`

## Real-World Context

"How many Airflow worker slots do we need?" Scheduled jobs overlap in time. The peak number of concurrent jobs determines the minimum number of workers, database connections or compute slots needed.

## The Problem

Given a set of jobs with start and end times, find the peak number of concurrent jobs and report which jobs are running at that peak.

## Worked Example

How many parallel execution slots does a job scheduler need? Same algorithm as Meeting Rooms II applied to batch job windows.

```
Jobs: extract (00:00-02:00), transform_A (01:00-03:00),
      transform_B (01:30-04:00), load (03:30-05:00), report (05:00-06:00)

Sweep line events:
  00:00+1, 01:00+1, 01:30+1, 02:00-1, 03:00-1, 03:30+1, 04:00-1, 05:00-1, 05:00+1, 06:00-1

  Slots: 1→2→3→2→1→2→1→0→1→0
  Peak: 3 (between 01:30 and 02:00)

  Need 3 parallel slots. Adding a 4th concurrent job would require scaling.
```

## Why Intervals

Both the heap approach (Meeting Rooms II) and sweep line approach solve this in O(n log n). The sweep line additionally tells you when the peak occurs and which jobs are running.

## Production Considerations

- **Buffer capacity:** In practice, add 20-30% headroom above the peak to handle variance and delays.
- **Time-of-day patterns:** Peak concurrency often follows predictable patterns (morning ETL spike). Visualizing the concurrency curve helps capacity planning.
- **Priority scheduling:** When slots are limited, higher-priority jobs should preempt lower-priority ones. This combines with pattern 05 (heap-based priority scheduling).

## Connection to LeetCode

Direct application of problem 253 (Meeting Rooms II). The sweep line approach extends it with tracking which specific jobs are concurrent.

## Benchmark

For 10K jobs, peak concurrency calculation completes in milliseconds. The sweep line and heap approaches have equivalent performance.
