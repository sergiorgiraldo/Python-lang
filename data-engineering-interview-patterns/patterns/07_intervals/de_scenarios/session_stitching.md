# Session Stitching (Merge Events into Sessions)

**Run it:** `uv run python -m patterns.07_intervals.de_scenarios.session_stitching`

## Real-World Context

Raw clickstream data has individual page views. Analytics needs sessions - contiguous periods of user activity separated by gaps of 30+ minutes. This is merge intervals with a gap threshold.

Google Analytics, Amplitude and every web analytics platform does session stitching. The SQL version is a gaps-and-islands problem. The Python version is merge intervals.

## The Problem

Given a list of page view events (each with a start and end time), merge events that are within 30 minutes of each other into sessions. Report the session start, end and event count.

## Worked Example

Merge overlapping user activity events into sessions. Same algorithm as Merge Intervals applied to clickstream data.

```
User events (sorted by timestamp):
  [10:01, 10:05]  page_view
  [10:03, 10:08]  click        ← overlaps, same session
  [10:07, 10:12]  page_view    ← overlaps, same session
  [10:30, 10:35]  page_view    ← gap > threshold, NEW session
  [10:33, 10:40]  click        ← overlaps, same session

Merge overlapping:
  [10:01, 10:05] + [10:03, 10:08] → [10:01, 10:08]
  [10:01, 10:08] + [10:07, 10:12] → [10:01, 10:12]
  Gap to [10:30, 10:35] → new session
  [10:30, 10:35] + [10:33, 10:40] → [10:30, 10:40]

  Sessions: [10:01-10:12] (11 min), [10:30-10:40] (10 min)
  5 events → 2 sessions.
```

## Why Intervals

This is exactly merge intervals (problem 56) with a configurable gap tolerance. Sort by start time, scan left to right, extend the current session if the next event is within the threshold.

## Production Considerations

- **Per-user grouping:** Always group by user ID first, then stitch within each user's events.
- **Gap threshold tuning:** 30 minutes is the standard for web analytics. Mobile apps often use shorter thresholds (5-10 minutes). The right value depends on the product.
- **Late-arriving events:** Events might arrive out of order. Either buffer and sort, or re-process sessions when late events arrive.
- **SQL implementation:** In SQL, this is a gaps-and-islands problem using LAG() and conditional SUM() for session IDs.

## Connection to LeetCode

Direct application of problem 56 (Merge Intervals) with a gap tolerance parameter added to the overlap condition.

## Benchmark

For 10K events, session stitching completes in under 10ms. The sort step (O(n log n)) dominates. The merge scan is a single O(n) pass.
