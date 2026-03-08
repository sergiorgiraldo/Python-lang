# Contains Duplicate II (LeetCode #219)

🔗 [LeetCode 219: Contains Duplicate II](https://leetcode.com/problems/contains-duplicate-ii/)

> **Difficulty:** Easy | **Interview Frequency:** Occasional

## Problem Statement

Given an integer array `nums` and an integer `k`, return true if there are two distinct indices `i` and `j` such that `nums[i] == nums[j]` and `abs(i - j) <= k`.

**Example:**
```
Input: nums = [1, 2, 3, 1], k = 3
Output: true (indices 0 and 3, distance = 3 <= k)

Input: nums = [1, 2, 3, 1, 2, 3], k = 2
Output: false (duplicates exist but distance > 2)
```

**Constraints:**
- 1 <= nums.length <= 10^5
- -10^9 <= nums[i] <= 10^9
- 0 <= k <= 10^5

---

## Thought Process

1. **Brute force:** For each element, check the next k elements for a match. O(n * k).
2. **Hash map approach:** Store the last index of each value. For each element, check if we've seen it before within distance k. O(n) time, O(n) space. This works but stores more than we need.
3. **Sliding window:** Maintain a set of elements in the current window of size k. If a new element is already in the set, return True. When the window exceeds size k, remove the oldest element. O(n) time, O(k) space.

The sliding window approach uses O(k) space instead of O(n) - a meaningful difference when k is much smaller than n.

---

## Worked Example

This is Contains Duplicate (problem 217) with a distance constraint: duplicates must be within k positions of each other. A sliding window of size k+1 with a hash set tracks the elements currently in the window. If a new element is already in the set, we found a nearby duplicate. If the window grows past k+1, we remove the oldest element.

The set tracks "what's in the current window." Adding an element and removing the oldest are both O(1) set operations.

```
Input: nums = [1, 5, 3, 8, 5, 9, 2, 3], k = 3

  Window can hold at most k+1 = 4 elements.

  i=0: num=1, seen={}, 1 not in seen → add. seen={1}
  i=1: num=5, seen={1}, not in seen → add. seen={1,5}
  i=2: num=3, seen={1,5}, not in seen → add. seen={1,5,3}
  i=3: num=8, seen={1,5,3}, not in seen → add. seen={1,5,3,8}
       Window full (4 elements). Remove oldest: nums[0]=1. seen={5,3,8}
  i=4: num=5, seen={5,3,8}, 5 IS in seen → return True.
       The duplicate 5 is at index 1 and index 4. Distance = 3 <= k=3.

If we continued (no early exit):
  i=5: num=9, add. Remove nums[2]=3. seen={8,5,9}
  i=6: num=2, add. Remove nums[3]=8. seen={5,9,2}
  i=7: num=3, add. Remove nums[4]=5. seen={9,2,3}
       3 at index 7, nearest previous 3 was at index 2. Distance = 5 > k=3.
       Not in the current window, so no duplicate detected.
```

---

## Approaches

### Approach 1: Hash Map (Store Last Index)

<details>
<summary>📝 Explanation</summary>

Use a dict mapping each value to the most recent index where it appeared. For each element, check if it's in the dict and whether the stored index is within k positions.

1. For each index `i` and value `nums[i]`:
   - If `nums[i]` is in the dict and `i - dict[nums[i]] <= k`: return True.
   - Update `dict[nums[i]] = i` (store/overwrite with the latest index).
2. If no match found, return False.

We only store the most recent index because if there's a valid duplicate, it will be the closest one. If the closest previous occurrence is too far away, earlier occurrences are even farther.

**Time:** O(n) - single pass.
**Space:** O(n) - dict stores up to n entries (one per unique value).

</details>

<details>
<summary>💻 Code</summary>

```python
def contains_nearby_duplicate_map(nums: list[int], k: int) -> bool:
    last_seen = {}
    for i, num in enumerate(nums):
        if num in last_seen and i - last_seen[num] <= k:
            return True
        last_seen[num] = i
    return False
```

</details>

### Approach 2: Sliding Window + Hash Set (Optimal Space)

<details>
<summary>💡 Hint</summary>

You only care about elements within distance k. Why store indices for elements that are already too far away?

</details>

<details>
<summary>📝 Explanation</summary>

Maintain a set of elements currently in a window of size k+1. As the window slides, add the new element and remove the one that fell off. If the new element is already in the set before adding it, we found a duplicate within distance k.

1. For each index `i`:
   - If `nums[i]` is in the set: return True.
   - Add `nums[i]` to the set.
   - If the set size exceeds k: remove `nums[i - k]` (the element that's now outside the window).
2. Return False.

The set is bounded by size k+1, so space usage depends on k rather than n.

**Time:** O(n) - single pass. Each element is added and removed from the set at most once.
**Space:** O(k) - the set holds at most k+1 elements.

The space advantage over the hash map approach matters when k is much smaller than n (e.g., k=10 with n=1,000,000). The hash map stores all unique values; the sliding window only tracks what's nearby.

</details>

<details>
<summary>💻 Code</summary>

```python
def contains_nearby_duplicate(nums: list[int], k: int) -> bool:
    window = set()
    for i, num in enumerate(nums):
        if num in window:
            return True
        window.add(num)
        if len(window) > k:
            window.remove(nums[i - k])
    return False
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Duplicate within k | `[1,2,3,1], 3` | `True` | Standard case |
| Adjacent duplicate | `[1,0,1,1], 1` | `True` | Minimum distance |
| Duplicate outside k | `[1,2,3,1,2,3], 2` | `False` | Too far apart |
| k = 0 | `[1,1], 0` | `False` | Same index not counted |
| k larger than array | `[1,2,1], 10` | `True` | Entire array is the window |
| Exactly at k | `[1,2,3,4,1], 4` | `True` | Boundary: distance = k |
| At k + 1 | `[1,2,3,4,5,1], 4` | `False` | Boundary: distance = k+1 |
| No duplicates | `[1,2,3,4], 3` | `False` | All unique |

---

## Common Pitfalls

1. **Window size off by one** - The window should contain k+1 elements (the current element plus k previous ones). Remove when `len(window) > k`, not `>= k`.
2. **k = 0** - Distance 0 means same index, which isn't a valid pair. The window set approach handles this correctly because the set only has one element and can't contain duplicates.
3. **Removing the wrong element** - Remove `nums[i - k]`, not `nums[i - k - 1]`. This is the element that just fell out of the window.

---

## Interview Tips

**What to say:**
> "I'll maintain a sliding window of size k using a hash set. For each new element, I check if it's already in the window. The set gives O(1) lookup, and maintaining the window size keeps space at O(k)."

**Hash map vs set tradeoff:**
> "A hash map storing last-seen index works too, with O(n) space. The set approach trades a bit of complexity for O(k) space, which matters when k is much smaller than n."

**What the interviewer evaluates:** Combining a sliding window with a hash set tests whether you can compose patterns. The window maintains the distance constraint, the set maintains the uniqueness check. Mentioning streaming dedup shows you've internalized the production application.

---

## DE Application

Windowed duplicate detection shows up when:
- Deduplicating event streams where duplicates arrive within a time window
- Detecting repeated log entries within a short period (e.g., duplicate alerts)
- Rate limiting: "has this user/API key made this exact request within the last k seconds?"
- Any scenario where you only care about recent duplicates, not all-time duplicates

The "sliding window of recent items" approach maps directly to Redis's SISMEMBER with TTL-based key expiry.

## At Scale

The sliding window of size k uses O(k) memory (a hash set of the current window). For k=1000, that's negligible. For very large k (millions), the set grows proportionally. The brute force O(n*k) approach is unacceptable at scale: 1B elements with k=1M means 10^15 operations. The sliding window reduces this to O(n) regardless of k. In production, "find duplicates within a time window" is an event dedup problem. Streaming dedup with a window is standard in event pipelines: maintain a set of recently seen IDs, expire entries older than the window.

---

## Related Problems

- [217. Contains Duplicate](../../01_hash_map/problems/217_contains_duplicate.md) - Same problem without the distance constraint (hash set, simpler)
- [643. Maximum Average Subarray I](643_max_average_subarray.md) - Fixed window with sum instead of set
- [3. Longest Substring Without Repeating](003_longest_substring.md) - Variable window with uniqueness constraint
