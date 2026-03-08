# DE Scenario: Monotonic Stack for Time-Series Analysis

## Real-World Context

Monitoring systems track metrics over time. A common question: "for each data point, when does the metric next exceed a threshold (or the current value)?" Scanning forward from each point is O(n^2). A monotonic stack answers this in O(n) by resolving multiple waiting points when a spike arrives.

## Worked Example

Same pattern as Daily Temperatures (problem 739). Points below the threshold sit on the stack, waiting. When a point above the threshold arrives, it resolves all waiting points at once.

```
Threshold: 50
Data: [(08:00, 45), (08:05, 52), (08:10, 48), (08:15, 41),
       (08:20, 55), (08:25, 38), (08:30, 60)]

  08:00 (45): below threshold. Push.    Stack: [08:00(45)]
  08:05 (52): above threshold. Resolves 08:00.
              result[08:00] = 08:05. Pop.
              08:05 itself is above → result[08:05] = None.  Stack: []
  08:10 (48): below. Push.              Stack: [08:10(48)]
  08:15 (41): below. Push.              Stack: [08:10(48), 08:15(41)]
  08:20 (55): above. Resolves 08:15 and 08:10.
              result[08:15] = 08:20. result[08:10] = 08:20.
              08:20 itself above → None.  Stack: []
  08:25 (38): below. Push.              Stack: [08:25(38)]
  08:30 (60): above. Resolves 08:25.
              result[08:25] = 08:30.     Stack: []

Results:
  08:00 → 08:05 (next breach 5 min later)
  08:05 → None (already above)
  08:10 → 08:20 (10 min wait)
  08:15 → 08:20 (5 min wait)
  08:20 → None (already above)
  08:25 → 08:30 (5 min wait)
  08:30 → None (no future data)

7 data points, 7 pushes + 4 pops = 11 operations. O(n).
```
