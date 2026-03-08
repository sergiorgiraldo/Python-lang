# Sliding Window Maximum (LeetCode #239)

🔗 [LeetCode 239: Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/)

> **Difficulty:** Hard | **Interview Frequency:** Common

## Problem Statement

Given an array `nums` and a sliding window of size `k`, return the maximum value in each window as it slides from left to right.

**Example:**
```
Input: nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3
Output: [3, 3, 5, 5, 6, 7]

Window position                Max
[1  3  -1] -3  5  3  6  7      3
 1 [3  -1  -3] 5  3  6  7      3
 1  3 [-1  -3  5] 3  6  7      5
 1  3  -1 [-3  5  3] 6  7      5
 1  3  -1  -3 [5  3  6] 7      6
 1  3  -1  -3  5 [3  6  7]     7
```

**Constraints:**
- 1 <= nums.length <= 10^5
- -10^4 <= nums[i] <= 10^4
- 1 <= k <= nums.length

---

## Thought Process

1. **Brute force:** For each window, compute `max()`. O(n * k).
2. **Heap:** Keep a max-heap of window elements. But removing elements that leave the window is O(k), still not great.
3. **Monotonic deque:** Maintain a deque of indices where values are in decreasing order. The front is always the maximum. Elements that can never be a future maximum get discarded immediately.

The deque approach is the standard solution. Each element enters and exits the deque at most once, giving O(n) total.

---

## Approaches

### Approach 1: Brute Force

<details>
<summary>📝 Explanation</summary>

For each window position, extract the subarray and compute its maximum. This recomputes the max from scratch for every window, even though adjacent windows share k-1 elements.

For n elements with window size k, there are n-k+1 windows, each costing O(k) to scan. With large k (e.g., k = n/2), this becomes slow.

**Time:** O(n * k) - each window scans k elements.
**Space:** O(1) - no auxiliary data structures.

</details>

<details>
<summary>💻 Code</summary>

```python
def max_sliding_window_brute(nums: list[int], k: int) -> list[int]:
    return [max(nums[i:i+k]) for i in range(len(nums) - k + 1)]
```

</details>

### Approach 2: Monotonic Deque (Optimal)

<details>
<summary>💡 Hint 1</summary>

When a new element enters the window and it's larger than some elements already in the window, those smaller elements can never be the maximum of any future window. Why keep them?

</details>

<details>
<summary>💡 Hint 2</summary>

Store indices (not values) in the deque so you can tell when an element has left the window.

</details>

<details>
<summary>📝 Explanation</summary>

Maintain a deque of indices. The values at these indices are always in **decreasing** order (a "monotonic decreasing deque").

For each new element at index i:

1. **Remove expired indices:** While the front of the deque is outside the window (index <= i - k), remove it.
2. **Remove smaller elements:** While the back of the deque has values <= nums[i], remove them. These elements are smaller than the new one AND older - they can't be the maximum of any current or future window.
3. **Add the new index** to the back.
4. **Record the answer:** The front of the deque is the maximum for the current window.

**Why it's O(n):** Each index is added to the deque once and removed at most once. Total operations across all iterations: 2n.

**Why store indices instead of values:** We need to know when an element has left the window. Indices tell us that directly.

**Time:** O(n)
**Space:** O(k) - deque never exceeds window size

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import deque

def max_sliding_window(nums: list[int], k: int) -> list[int]:
    dq = deque()  # Stores indices, values are decreasing
    result = []
    for i in range(len(nums)):
        while dq and dq[0] <= i - k:
            dq.popleft()
        while dq and nums[dq[-1]] <= nums[i]:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

</details>

---

## Worked Example

Finding the maximum in each window of size k. The brute force checks all k elements per window (O(nk)). The optimal approach uses a monotonic deque where values are always in decreasing order. The front is always the current window's maximum. When a new element arrives, remove everything from the back that's smaller - those values can never be a future window's maximum because the new element is both larger and newer.

```
nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3
deque stores INDICES, shown as [index:value]

i=0: dq=[] → add 0 → dq=[0:1]
i=1: 1 <= 3 → pop 0 → dq=[] → add 1 → dq=[1:3]
i=2: -1 < 3 → keep → add 2 → dq=[1:3, 2:-1] → window full → max=3
i=3: -3 < -1 → keep → add 3 → dq=[1:3, 2:-1, 3:-3] → max=3
i=4: 1 expired (4-3=1) → pop front → dq=[2:-1, 3:-3]
     -3 <= 5 → pop → -1 <= 5 → pop → dq=[] → add 4 → dq=[4:5] → max=5
i=5: 3 < 5 → keep → add 5 → dq=[4:5, 5:3] → max=5
i=6: 3 <= 6 → pop → 5 <= 6 → pop → dq=[] → add 6 → dq=[6:6] → max=6
i=7: 6 <= 7 → pop → dq=[] → add 7 → dq=[7:7] → max=7

Result: [3, 3, 5, 5, 6, 7]
```

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Standard | `[1,3,-1,-3,5,3,6,7], 3` | `[3,3,5,5,6,7]` | Basic case |
| Descending | `[9,8,7,6,5], 3` | `[9,8,7]` | Max always at left edge |
| Ascending | `[1,2,3,4,5], 3` | `[3,4,5]` | Max always at right edge |
| k = 1 | `[1,-1], 1` | `[1,-1]` | Each element is its own window |
| k = n | `[3,1,2], 3` | `[3]` | Single window |
| All same | `[5,5,5,5], 2` | `[5,5,5]` | Deque behavior with ties |
| All negative | `[-1,-3,-5,-2,-4], 3` | `[-1,-2,-2]` | Max of negatives |

---

## Common Pitfalls

1. **Using `<=` vs `<` when popping from back** - Use `<=` (pop elements equal to the new value too). If you keep equal elements, the deque might hold stale indices for the same value, but functionally both work. Using `<=` keeps the deque shorter.
2. **Forgetting to check if the window is full** - Only append to result when `i >= k - 1`.
3. **Storing values instead of indices** - You need indices to know when elements expire from the window.

---

## Interview Tips

**What to say:**
> "Brute force recomputes max for each window in O(k). I can do better with a monotonic deque. The idea is: when a new element is larger than elements already in the deque, those smaller elements can never be a future maximum, so I discard them. The front of the deque is always the current max."

**If asked "what is a monotonic deque?":**
> "It's a deque where the values are maintained in sorted order - in this case, decreasing. We enforce the ordering by removing elements from the back that violate it. It's not a separate data structure, just a regular deque with a maintenance invariant."

**This problem is hard to come up with from scratch.** If you haven't seen it before, the deque approach isn't obvious. The brute force is fine for a first pass. If the interviewer pushes for O(n), mention "I think there's a deque-based approach" - they'll often guide you from there.

**What the interviewer evaluates:** The monotonic deque is a non-obvious data structure choice. This tests whether you know data structures beyond arrays and hash maps. Explaining WHY the deque maintains a decreasing order (because elements that are both older and smaller can never be the maximum) is the key insight. This problem is frequently used for senior+ interviews.

---

## DE Application

Monotonic deques are the algorithmic basis for:
- **Rolling max/min** in streaming systems (Flink, Spark Structured Streaming)
- **Anomaly detection** - detecting when a metric exceeds its rolling maximum by some threshold
- **SLA monitoring** - "what was the peak latency in each 5-minute window?"
- **Capacity planning** - tracking peak resource usage across time windows

SQL's `MAX() OVER (ORDER BY ts ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` computes the same thing. The database engine uses a similar deque-based algorithm internally.

## At Scale

The monotonic deque approach uses O(k) memory and O(n) time. For k=1000 and n=1B, that's negligible memory and ~10 seconds of processing. The brute force O(n*k) approach would take hours. The deque maintains the invariant that elements are decreasing from front to back. This same structure appears in stream processing as a "sliding window max/min" aggregate. Flink and Kafka Streams implement this internally for time-windowed aggregations. At scale, the deque-based approach is cache-friendly because it processes elements sequentially. The practical concern is window alignment: in time-series data, windows are aligned to clock boundaries (every minute, every hour), not to arbitrary positions.

---

## Related Problems

- [643. Maximum Average Subarray I](643_max_average_subarray.md) - Fixed window with sum (simpler)
- [76. Minimum Window Substring](076_min_window_substring.md) - Variable window (different concept)
- [155. Min Stack](https://leetcode.com/problems/min-stack/) - Related concept: tracking running min with O(1) access
