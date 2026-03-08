# CC Prompt: Full Rework - Pattern 03 Binary Search (Part 2 of 2)

## What This Prompt Does

Continues from Part 1. Rewrites `## Worked Example` and `📝 Explanation` blocks for problems 5-8, plus all 4 DE scenario worked examples.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

Same as Part 1. Only `.md` files. REPLACE specified sections only. NO Oxford commas, NO em dashes, NO exclamation points.

---

## Problem 5: 033_search_rotated.md

**Worked Example:**

```markdown
## Worked Example

Unlike "find minimum in rotated array" (which searches for the rotation point), this problem searches for a specific target value. The insight: in a rotated sorted array, at least one half is always sorted normally. We can check which half is sorted and determine if the target falls within that sorted range. If it does, search there. If not, search the other half.

```
Input: nums = [6, 7, 9, 11, 15, 2, 3, 5], target = 3

  left=0, right=7, mid=3 → nums[3] = 11
  Is the left half [6,7,9,11] sorted? nums[0]=6 <= nums[3]=11 → yes.
  Is target 3 in the range [6, 11]? 3 < 6 → no.
  So target must be in the right half. left = 4.

  left=4, right=7, mid=5 → nums[5] = 2
  Is the left half [15,2] sorted? nums[4]=15 <= nums[5]=2? No → right half is sorted.
  Is the right half [2,3,5] sorted? Yes. Is target 3 in range [2, 5]? 2 <= 3 <= 5 → yes.
  Search right half: left = 6.

  Wait, let me redo this more carefully:
  left=4, right=7, mid=5 → nums[5] = 2
  Check left half: nums[left]=nums[4]=15, nums[mid]=2. 15 > 2 → left half NOT sorted.
  So right half [2, 3, 5] IS sorted.
  Is target 3 in [nums[mid+1]..nums[right]] = [3, 5]? 3 >= 3 and 3 <= 5 → yes.
  left = mid + 1 = 6.

  left=6, right=7, mid=6 → nums[6] = 3
  3 == 3 → found it. Return index 6.

3 steps for 8 elements.

Not-found case: target = 10
  left=0, right=7, mid=3 → 11. Left [6,7,9,11] sorted. 6 <= 10 <= 11 → target in left half.
  right=3. left=0, right=3, mid=1 → 7. Left [6,7] sorted. 6 <= 10? yes. 10 <= 7? no.
  Target not in left [6,7]. Go right: left=2.
  left=2, right=3, mid=2 → 9. Left [9] sorted. 9 <= 10? yes. But right = 3, mid = 2.
  nums[left]=9 <= nums[mid]=9. Sorted left. 9 <= 10 <= 9? No (10 > 9). Go right: left=3.
  left=3, right=3, mid=3 → 11. 11 != 10. 11 > 10 → right=2.
  left=3 > right=2 → not found. Return -1.
```
```

**Approach 1: Single-Pass Binary Search - replace explanation:**

```
At each step, determine which half of the array is sorted (at least one half always is in a rotated sorted array). Then check if the target falls within the sorted half's range. If yes, search that half. If no, search the other half.

The decision process at each step:
1. Check if the left half `[left..mid]` is sorted: `nums[left] <= nums[mid]`.
2. If the left half is sorted, check if target is in range `[nums[left], nums[mid]]`. If yes, go left (`right = mid - 1`). If no, go right (`left = mid + 1`).
3. If the left half is NOT sorted, the right half must be sorted. Check if target is in range `[nums[mid], nums[right]]`. If yes, go right. If no, go left.

This works because one half is always sorted (the rotation break can only be in one half). By checking the sorted half's range, we reliably determine where the target could be.

**Time:** O(log n) - halving the search space each step.
**Space:** O(1).

The tricky part is getting the comparisons right. Draw out examples with the rotation in the left half vs the right half to build intuition.
```

**Approach 2: Find Pivot Then Search - replace explanation:**

```
Split the problem into two simpler steps:
1. Find the rotation point (minimum element) using the technique from problem 153.
2. Determine which sorted half the target is in, then do a standard binary search on that half.

After finding the minimum at index `pivot`:
- Left sorted half: `nums[0..pivot-1]`
- Right sorted half: `nums[pivot..n-1]`
- If `target >= nums[0]`, it's in the left half (or the array isn't rotated).
- Otherwise, it's in the right half.

**Time:** O(log n) - two binary searches, each O(log n).
**Space:** O(1).

This is conceptually simpler (two standard binary searches instead of one modified one) but requires two passes. Most interviewers are fine with either approach.
```

---

## Problem 6: 162_find_peak.md

**Worked Example:**

```markdown
## Worked Example

A peak element is larger than both its neighbors. The array is guaranteed to have at least one peak (because the boundaries are treated as negative infinity). We can find a peak with binary search by "climbing uphill": compare the middle element with its right neighbor. If the right neighbor is larger, a peak must exist to the right (we're on an ascending slope). If the middle is larger, a peak must exist at mid or to the left.

This is a boundary-finding problem: we're looking for where the array switches from ascending to descending.

```
Input: nums = [1, 3, 5, 8, 6, 4, 2, 7, 9]

  left=0, right=8, mid=4 → nums[4]=6, nums[5]=4
  6 > 4 → we're descending to the right. Peak is at mid or to the left. right = 4.

  left=0, right=4, mid=2 → nums[2]=5, nums[3]=8
  5 < 8 → ascending to the right. Peak is to the right. left = 3.

  left=3, right=4, mid=3 → nums[3]=8, nums[4]=6
  8 > 6 → peak at mid or left. right = 3.

  left=3 == right=3 → converged. nums[3] = 8 is a peak.
  Check: 8 > nums[2]=5 and 8 > nums[4]=6. Confirmed.

3 steps for 9 elements. Note: index 8 (value 9) is also a peak
(since the right boundary is treated as -∞), but binary search
found index 3 first. Any peak is a valid answer.
```
```

**Approach: Binary Search on Slope - replace explanation:**

```
Compare `nums[mid]` to `nums[mid + 1]` to determine the slope direction:

- If `nums[mid] < nums[mid + 1]`: we're on an ascending slope. A peak must exist to the right of mid (either the ascent ends at a peak, or we reach the right boundary which counts as a peak since `nums[n] = -∞`). Set `left = mid + 1`.
- If `nums[mid] > nums[mid + 1]`: we're on a descending slope (or at a peak). A peak is at mid or to the left. Set `right = mid`.

Loop condition: `while left < right`. When left == right, we've found a peak.

Why is a peak guaranteed to exist in the chosen direction? Because `nums[-1] = nums[n] = -∞` (virtual negative infinity at both boundaries). If we're ascending toward the right, either we find a descent (peak) or we reach the boundary (peak, since the boundary is -∞). Either way, a peak exists.

**Time:** O(log n) - halving each step.
**Space:** O(1).

This only finds one peak, not all peaks. But the problem only asks for any one. If the array has multiple peaks (like a mountain range), binary search finds whichever peak the halving path leads to.
```

---

## Problem 7: 875_koko_bananas.md

**Worked Example:**

```markdown
## Worked Example

This is a "binary search on the answer" problem. There's no sorted array to search. Instead, the answer (eating speed) is a number in a range, and we binary search for the minimum speed that lets Koko finish all bananas within h hours.

The monotonic property: if speed k works (finishes within h hours), then any speed > k also works (faster eating means finishing sooner). If speed k doesn't work, any speed < k also fails. This monotonic yes/no boundary is what makes binary search applicable.

For each candidate speed, a helper function calculates the total hours needed. For each pile, the hours = ceil(pile_size / speed). If total hours <= h, the speed works.

```
Input: piles = [3, 6, 7, 11], h = 8

  Min speed = 1 (eat 1 banana/hour, slowest possible)
  Max speed = 11 (largest pile, any faster is pointless)

  Binary search on speed [1, 11]:

  left=1, right=11, mid=6
    Hours at speed 6: ceil(3/6)=1 + ceil(6/6)=1 + ceil(7/6)=2 + ceil(11/6)=2 = 6
    6 <= 8 → speed 6 works. But maybe slower also works. right = 6.

  left=1, right=6, mid=3
    Hours at speed 3: ceil(3/3)=1 + ceil(6/3)=2 + ceil(7/3)=3 + ceil(11/3)=4 = 10
    10 > 8 → too slow. Need to eat faster. left = 4.

  left=4, right=6, mid=5
    Hours at speed 5: ceil(3/5)=1 + ceil(6/5)=2 + ceil(7/5)=2 + ceil(11/5)=3 = 8
    8 <= 8 → speed 5 works. Try slower: right = 5.

  left=4, right=5, mid=4
    Hours at speed 4: ceil(3/4)=1 + ceil(6/4)=2 + ceil(7/4)=2 + ceil(11/4)=3 = 8
    8 <= 8 → speed 4 works. right = 4.

  left=4, right=4 → converged. Minimum speed = 4.

4 binary search steps, each doing O(n) work (scanning all piles).
Brute force would try speeds 1, 2, 3, ..., 11 (linear scan).
For max_pile=10^9, binary search does ~30 steps vs 10^9 linear steps.
```
```

**Approach: Binary Search on Answer - replace explanation:**

```
The "answer" is the eating speed, which falls in the range [1, max(piles)]. Speed 1 is the slowest possible, and max(piles) is the fastest useful speed (eating faster than the largest pile doesn't help since Koko finishes one pile per hour regardless).

Binary search for the minimum speed that finishes within h hours:
1. Set `left = 1`, `right = max(piles)`.
2. Compute `mid = (left + right) // 2`.
3. Check if speed `mid` works: for each pile, compute `ceil(pile / mid)` and sum the hours. If total <= h, the speed works.
4. If it works, try slower: `right = mid` (mid might be the answer, so include it).
5. If it doesn't work, must go faster: `left = mid + 1`.
6. When `left == right`, we've found the minimum speed.

The `ceil(pile / speed)` calculation in Python: `(pile + speed - 1) // speed` or `math.ceil(pile / speed)`. The integer arithmetic version avoids floating-point issues.

**Time:** O(n × log(max_pile)) - each binary search step does O(n) work (checking all piles), and there are O(log(max_pile)) steps.
**Space:** O(1).

This "binary search on the answer" pattern is the hardest to recognize because there's no explicit sorted array. The trigger is: "find the minimum/maximum value that satisfies a condition" where the condition has a monotonic yes/no threshold.
```

---

## Problem 8: 981_time_map.md

**Worked Example:**

```markdown
## Worked Example

TimeMap stores key-value pairs with timestamps and retrieves the value at the largest timestamp <= the query timestamp. This is a boundary-finding binary search: for a given key, find the rightmost timestamp that doesn't exceed the query.

The data structure uses a dict mapping each key to a list of (timestamp, value) pairs. Since timestamps for the same key are set in increasing order (per the problem guarantee), the list is already sorted. Binary search finds the right entry without scanning the full history.

```
TimeMap()

set("weather", "sunny",  1)
set("weather", "cloudy", 4)
set("weather", "rainy",  7)
set("weather", "sunny",  12)

Internal state:
  data["weather"] = [(1, "sunny"), (4, "cloudy"), (7, "rainy"), (12, "sunny")]

get("weather", timestamp=5):
  Binary search for rightmost timestamp <= 5 in [1, 4, 7, 12]:
    left=0, right=3, mid=1 → timestamp 4 <= 5 → candidate. Go right: left=2.
    left=2, right=3, mid=2 → timestamp 7 > 5 → too late. right=1.
    left=2 > right=1 → done. Best candidate was index 1.
  Return "cloudy" (the value at timestamp 4, the latest timestamp <= 5).

get("weather", timestamp=7):
  Binary search for rightmost timestamp <= 7:
    left=0, right=3, mid=1 → 4 <= 7 → left=2.
    left=2, right=3, mid=2 → 7 <= 7 → exact match. left=3.
    left=3, right=3, mid=3 → 12 > 7 → right=2.
    left=3 > right=2. Best candidate was index 2.
  Return "rainy" (exact match at timestamp 7).

get("weather", timestamp=0):
  Binary search: all timestamps > 0. No valid candidate. Return "".

Each get is O(log m) where m is the number of entries for that key,
vs O(m) for a linear scan through the history.
```
```

**Approach 1: Using bisect (Production) - replace explanation:**

```
Store each key's history as a sorted list of (timestamp, value) pairs. For get operations, use `bisect_right` to find where the query timestamp would be inserted, then return the entry just before that insertion point (which is the latest timestamp <= query).

```python
import bisect
idx = bisect.bisect_right(timestamps, query_ts)
if idx == 0:
    return ""  # all timestamps are after the query
return values[idx - 1]
```

`bisect_right` returns the insertion point that keeps the list sorted. If it returns index `i`, all elements before `i` have timestamps <= query. So `i - 1` is the one we want.

**Time:** O(1) for set (append to list), O(log m) for get (binary search on m entries for that key).
**Space:** O(total entries across all keys).

This is the production approach. The bisect module is well-tested and handles edge cases correctly.
```

**Approach 2: Manual Binary Search (Interview) - replace explanation:**

```
Same logic as above but implementing the binary search by hand. This is what interviewers typically want to see.

Maintain a dict of key → list of (timestamp, value). For get, binary search the list for the rightmost timestamp <= query:

1. `left = 0`, `right = len(entries) - 1`.
2. Track `result = ""` (best answer so far).
3. While `left <= right`:
   - If `entries[mid].timestamp <= query_ts`: this is a valid candidate. Update `result` and search right for a later valid timestamp: `left = mid + 1`.
   - If `entries[mid].timestamp > query_ts`: too late. Go left: `right = mid - 1`.
4. Return result.

The "track best so far" pattern is common in binary search boundary problems. We don't stop at the first valid answer - we keep searching for a better (later) one.

**Time:** O(1) for set, O(log m) for get.
**Space:** O(total entries).
```

---

## DE Scenario Worked Examples

### de_scenarios/partition_boundaries.md

```markdown
## Worked Example

When splitting sorted data into partitions (by date range, value range or size budget), binary search finds the boundary indices in O(log n) per boundary instead of scanning the entire dataset.

This is boundary-finding binary search: "where is the first element >= this value?"

```
Sorted dataset of 10M records by timestamp:
  [2024-01-01 00:00, ..., 2024-12-31 23:59]

Need quarterly partition boundaries (Q1, Q2, Q3, Q4):
  Q2 starts at first record >= 2024-04-01
  Q3 starts at first record >= 2024-07-01
  Q4 starts at first record >= 2024-10-01

Binary search for each boundary:
  Q2 boundary: bisect_left(timestamps, "2024-04-01")
    ~24 comparisons for 10M records (log₂(10M) ≈ 23.3)
    Result: index 2,478,301 → Q1 is records [0..2,478,300]

  Q3 boundary: bisect_left(timestamps, "2024-07-01")
    ~24 comparisons → index 4,982,100

  Q4 boundary: bisect_left(timestamps, "2024-10-01")
    ~24 comparisons → index 7,513,422

Total: ~72 comparisons to partition 10M records.
Linear scan for each boundary would take ~25M comparisons total.
```
```

### de_scenarios/log_lookup.md

```markdown
## Worked Example

Looking up the first log entry at or after a specific timestamp in a sorted log file. This is the same operation as TimeMap's get, applied to production log analysis.

```
Sorted log file (by timestamp, 5M entries):
  [2024-01-15 00:00:01.123, 2024-01-15 00:00:01.456, ..., 2024-01-15 23:59:59.987]

Query: "Show me the first log entry at or after 14:30:00"

  bisect_left(timestamps, "2024-01-15 14:30:00.000")
  ~23 comparisons (log₂(5M) ≈ 22.3)
  Result: index 3,021,445 → first entry at 14:30:00.012

From there, read forward for all entries in the time range.

Without binary search: scan from the beginning, checking each entry.
Average case: scan ~3M entries to reach the 14:30 mark.
With binary search: 23 comparisons to jump directly there.
```
```

### de_scenarios/search_on_answer.md

```markdown
## Worked Example

"Binary search on the answer" applied to a real DE problem: finding the minimum number of workers needed to process a batch within a time budget. Same pattern as Koko Eating Bananas - the answer is a number in a range and we check feasibility for each candidate.

```
Problem: 1000 tasks, each taking between 1 and 60 minutes.
         Total work: 28,500 task-minutes.
         Deadline: 120 minutes.
         Each worker processes tasks sequentially.
         Minimize the number of workers.

  Min workers = 1 (if 28,500 min <= 120 min... no, that's too slow)
  Max workers = 1000 (one per task, guaranteed to finish)

  Binary search on [1, 1000]:

  mid=500: Assign tasks greedily. Each worker gets tasks until their
    total >= 120 min. Needs 245 workers. 245 <= 500 → works. Try fewer.
    right = 500.

  mid=250: Needs 245 workers. 245 <= 250 → works. right = 250.

  mid=125: Needs 245 workers. 245 > 125 → doesn't work. left = 126.

  mid=188: Needs 245 workers. 245 > 188 → doesn't work. left = 189.

  mid=219: Needs 245. 245 > 219 → left = 220.

  mid=235: Needs 245. left = 236.

  mid=243: 245 > 243 → left = 244.

  mid=246: Needs 245. 245 <= 246 → right = 246.

  mid=245: Needs 245. 245 <= 245 → right = 245.

  left=244... converges to 245 workers.

  ~10 binary search steps, each doing O(n) greedy assignment.
  Brute force: try 1, 2, 3, ..., up to 245 workers = 245 feasibility checks.
```
```

### de_scenarios/metric_change_detection.md

```markdown
## Worked Example

Finding when a metric changed significantly in sorted time-series data. Binary search on the time axis to find the change point: the first timestamp where the metric crosses a threshold.

```
Daily revenue data, sorted by date (365 days):
  [Jan 1: $45K, Jan 2: $47K, ..., Jun 15: $52K, ..., Jun 16: $31K, ..., Dec 31: $33K]

  Revenue was ~$45-55K for the first half, then dropped to ~$28-35K.
  Find the first day where revenue dropped below $40K.

  Binary search for the change point:
    left=0 (Jan 1), right=364 (Dec 31)

    mid=182 (Jul 1): revenue = $32K < $40K → change happened before this. right=182.
    mid=91 (Apr 1): revenue = $48K >= $40K → change is after this. left=92.
    mid=137 (May 17): revenue = $51K >= $40K → left=138.
    mid=160 (Jun 9): revenue = $50K >= $40K → left=161.
    mid=171 (Jun 20): revenue = $29K < $40K → right=171.
    mid=166 (Jun 15): revenue = $52K >= $40K → left=167.
    mid=168 (Jun 17): revenue = $33K < $40K → right=168.
    mid=167 (Jun 16): revenue = $31K < $40K → right=167.
    left=167 == right=167 → change point is Jun 16.

  9 steps to find the change point in a year of daily data.
  Linear scan would check up to 167 days from the start.
```
```

---

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

git diff --name-only | grep -v '.md$'
uv run pytest patterns/03_binary_search/ -v --tb=short 2>&1 | tail -5

# Spot-check Koko
grep "Input: piles" patterns/03_binary_search/problems/875_koko_bananas.md

# Spot-check DE scenario
grep "partition\|quarterly" patterns/03_binary_search/de_scenarios/partition_boundaries.md | head -3
```
