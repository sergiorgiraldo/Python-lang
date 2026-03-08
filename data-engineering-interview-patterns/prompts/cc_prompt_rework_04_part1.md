# CC Prompt: Full Rework - Pattern 04 Sliding Window (Part 1 of 2)

## What This Prompt Does

Rewrites the README "What Is It?", "Visual Aid" and "Trade-offs" sections, plus `## Worked Example` and `📝 Explanation` blocks for the first 3 problems.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

Same as all previous patterns. Only `.md` files. NO Oxford commas, NO em dashes, NO exclamation points.

---

## Task 1: Rewrite README Sections

### Replace `## What Is It?` (everything up to `## When to Use It`)

```markdown
## What Is It?

### The basics

A sliding window is a technique for processing subarrays or substrings by maintaining a "window" (a contiguous range) that slides across the data. Instead of recomputing everything for every possible subarray (O(n²) or worse), the window moves one step at a time, adding a new element on one end and removing an old element from the other. This incremental update keeps the total work at O(n).

Think of it like looking through a train window. As the train moves forward, new scenery appears on the right side while old scenery disappears on the left. You don't need to re-examine everything in view - you just process what's new and forget what's gone.

### The two types

**1. Fixed-size window**

The window has a predetermined size k. It slides one position at a time, always containing exactly k elements.

```python
# fixed window of size k
window_sum = sum(arr[:k])  # initialize with first k elements
for i in range(k, len(arr)):
    window_sum += arr[i]       # add new element entering the window
    window_sum -= arr[i - k]   # remove element leaving the window
    # process window_sum
```

The key operation: when the window slides right by one position, we add one element and remove one element. Each slide costs O(1) instead of re-summing all k elements.

Use this when: the problem says "subarray of size k" or "window of length k." Maximum average subarray, Contains Duplicate II.

**2. Variable-size window**

The window expands and contracts based on some condition. A right pointer extends the window, and a left pointer shrinks it when a constraint is violated.

```python
left = 0
for right in range(len(arr)):
    # expand: add arr[right] to window state
    while window_violates_constraint():
        # contract: remove arr[left] from window state
        left += 1
    # process current valid window [left..right]
```

The right pointer always moves forward (expands). The left pointer only moves forward (contracts). Since both pointers only move in one direction and each visits at most n positions, the total work is O(n) despite the nested loop.

Use this when: "longest substring/subarray that satisfies..." or "smallest window that contains..." Longest Substring Without Repeating Characters, Longest Repeating Character Replacement.

### Why it's O(n) with a nested loop

The variable-size window has an inner while loop, which looks like it could be O(n²). But consider: the left pointer starts at 0 and can only move forward to at most n-1. Each iteration of the inner loop advances left by 1. Across ALL iterations of the outer loop, left moves at most n times total. So the inner loop doesn't run n times per outer iteration - it runs n times *total* across the entire algorithm.

Think of it this way: each element enters the window once (when right passes over it) and leaves the window once (when left passes over it). That's at most 2n operations total = O(n).

### Tracking window state with a hash map

Most sliding window problems track what's inside the window using a hash map (dict or Counter). When an element enters the window, update the map. When an element leaves, update the map again.

```python
from collections import defaultdict
counts = defaultdict(int)

left = 0
for right in range(len(s)):
    counts[s[right]] += 1       # element enters window
    while window_invalid():
        counts[s[left]] -= 1    # element leaves window
        if counts[s[left]] == 0:
            del counts[s[left]]  # clean up zero-count entries
        left += 1
```

This combination of sliding window + hash map is one of the most common patterns in interviews. The window handles the "contiguous subarray" constraint. The hash map handles the "what's in the window?" tracking.

### Connection to data engineering

Sliding windows are everywhere in data engineering:
- **Moving averages** - compute the average of the last k data points as new data arrives
- **Sessionization** - group events into sessions based on time gaps (variable window)
- **Anomaly detection** - flag values that deviate from a sliding window of recent values
- **Rate limiting** - count requests within a sliding time window
- **Stream processing** - Spark Streaming and Flink both have native sliding window operations

The SQL equivalent is window functions: `AVG(value) OVER (ORDER BY ts ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` is a fixed-size sliding window.
```

### Replace `## Visual Aid` (up to `## Template`)

```markdown
## Visual Aid

```
Fixed-size window: Maximum sum of 3 consecutive elements

Array: [2, 1, 5, 1, 3, 2, 8, 4]

Window [2, 1, 5] → sum=8
       [1, 5, 1] → sum=7  (added 1, removed 2: 8+1-2=7)
          [5, 1, 3] → sum=9  (added 3, removed 1: 7+3-1=9)
             [1, 3, 2] → sum=6
                [3, 2, 8] → sum=13  ← maximum
                   [2, 8, 4] → sum=14  ← new maximum

Each slide: add one element, remove one element. O(1) per slide.
Total: O(n) for the entire array. Without the window: O(n×k) re-summing.
```

```
Variable-size window: Longest substring without repeating characters

String: "abcdbefa"

  a         → {a} valid, length 1
  ab        → {a,b} valid, length 2
  abc       → {a,b,c} valid, length 3
  abcd      → {a,b,c,d} valid, length 4
  abcdb     → {a,b,c,d,b} duplicate 'b'! Contract from left:
   bcdb     → still has duplicate 'b'. Contract:
    cdb     → {c,d,b} valid, length 3
    cdbe    → {c,d,b,e} valid, length 4
    cdbef   → {c,d,b,e,f} valid, length 5  ← longest
    cdbefa  → duplicate 'a'? No, first 'a' was removed. 
     Wait: {c,d,b,e,f,a} valid, length 6  ← new longest

Right pointer always advances. Left pointer only advances to fix violations.
Total movement of both pointers combined: O(n).
```
```

### Replace `## Trade-offs` (up to `## Problems in This Section`)

```markdown
## Trade-offs

**Sliding window gives O(n) time for contiguous subarray/substring problems.** Without it, checking every subarray is O(n²) (or O(n²k) if you re-compute for each). The window's incremental update avoids redundant work.

**When sliding window works:**
- The problem asks about contiguous subarrays or substrings (not subsequences)
- You can define a clear condition for when the window is valid/invalid
- Adding and removing elements from the window state is O(1)

**When sliding window doesn't work:**
- The problem asks about subsequences (elements don't need to be contiguous)
- The valid/invalid condition can't be maintained incrementally (e.g., you need to re-examine all elements to decide)
- The data isn't sequential (graphs, trees, etc.)

**Sliding window vs two pointers:** There's significant overlap. A variable-size sliding window IS a two-pointer technique (left and right pointers moving forward). The distinction: "sliding window" emphasizes tracking state inside the window (usually with a hash map). "Two pointers" emphasizes the pointer movement logic. Same mechanics, different emphasis.
```

---

## Task 2: Problems 1-3

### 643_max_average_subarray.md

**Worked Example:**

```markdown
## Worked Example

The simplest sliding window problem: find the maximum average of any subarray of length k. Since the length is fixed, the window just slides one position at a time. For each slide, add the new element and subtract the one that fell off. Track the maximum sum (dividing by k at the end gives the average).

```
Input: nums = [1, 12, -5, -6, 50, 3, 8, -2], k = 4

  Initialize: window = [1, 12, -5, -6], sum = 2

  Slide right, add 50, remove 1:  sum = 2 + 50 - 1 = 51.  [12, -5, -6, 50]  max_sum=51
  Slide right, add 3, remove 12:  sum = 51 + 3 - 12 = 42. [-5, -6, 50, 3]   max_sum=51
  Slide right, add 8, remove -5:  sum = 42 + 8 - (-5) = 55. [-6, 50, 3, 8]  max_sum=55
  Slide right, add -2, remove -6: sum = 55 + (-2) - (-6) = 59. [50, 3, 8, -2] max_sum=59

  Maximum average = 59 / 4 = 14.75

5 window positions checked in O(n) total. Each slide was one addition
and one subtraction. The brute force approach (re-sum all k elements for
each position) would do 4 additions per position × 5 positions = 20 additions.
Small savings here, but for k=10,000 the difference is dramatic.
```
```

**Approach 1: Brute Force - replace explanation:**

```
For every possible starting position (0 through n-k), sum the k elements in that subarray and compute the average. Track the maximum.

Two nested loops: outer loop over starting positions, inner loop sums k elements.

**Time:** O(n × k) - n-k+1 windows, each requiring k additions.
**Space:** O(1).

For large k, this is slow. If n = 100,000 and k = 10,000, that's a billion operations.
```

**Approach 2: Sliding Window - replace explanation:**

```
Compute the sum of the first k elements. Then slide the window one position at a time: add the new element entering the window on the right and subtract the element leaving on the left. Each slide updates the sum in O(1) instead of re-summing all k elements.

1. `window_sum = sum(nums[:k])` - initial window.
2. `max_sum = window_sum`.
3. For i from k to n-1:
   - `window_sum += nums[i] - nums[i - k]` (add new, subtract old)
   - Update `max_sum` if window_sum is larger.
4. Return `max_sum / k`.

**Time:** O(n) - one pass. Each element is added once and subtracted once.
**Space:** O(1) - just the running sum.

The key insight: consecutive windows overlap by k-1 elements. Re-summing all k elements wastes work on the k-1 elements that didn't change. The sliding window only processes the one element that changed on each end.
```

### 219_contains_duplicate_ii.md

**Worked Example:**

```markdown
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
```

**Approach 1: Hash Map (Store Last Index) - replace explanation:**

```
Use a dict mapping each value to the most recent index where it appeared. For each element, check if it's in the dict and whether the stored index is within k positions.

1. For each index `i` and value `nums[i]`:
   - If `nums[i]` is in the dict and `i - dict[nums[i]] <= k`: return True.
   - Update `dict[nums[i]] = i` (store/overwrite with the latest index).
2. If no match found, return False.

We only store the most recent index because if there's a valid duplicate, it will be the closest one. If the closest previous occurrence is too far away, earlier occurrences are even farther.

**Time:** O(n) - single pass.
**Space:** O(n) - dict stores up to n entries (one per unique value).
```

**Approach 2: Sliding Window + Hash Set - replace explanation:**

```
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
```

### 003_longest_substring.md

**Worked Example:**

```markdown
## Worked Example

Find the longest substring with no repeating characters. This is a variable-size window problem. The right pointer expands the window one character at a time. When a duplicate character enters, the left pointer contracts the window until the duplicate is gone.

We use a set to track characters currently in the window. When the new character is already in the set, we shrink from the left, removing characters from the set, until the duplicate is gone.

```
Input: s = "abcdbefa"

  left=0

  right=0: char='a', seen={}, 'a' not in seen → add. seen={a}. Length=1.
  right=1: char='b', not in seen → add. seen={a,b}. Length=2.
  right=2: char='c', not in seen → add. seen={a,b,c}. Length=3.
  right=3: char='d', not in seen → add. seen={a,b,c,d}. Length=4. max=4.

  right=4: char='b', 'b' IS in seen → duplicate. Contract from left:
    Remove s[0]='a'. left=1. seen={b,c,d}. 'b' still in seen.
    Remove s[1]='b'. left=2. seen={c,d}. 'b' gone. Stop contracting.
    Add 'b'. seen={c,d,b}. Length=3.

  right=5: char='e', not in seen → add. seen={c,d,b,e}. Length=4. max=4.
  right=6: char='f', not in seen → add. seen={c,d,b,e,f}. Length=5. max=5.
  right=7: char='a', not in seen → add. seen={c,d,b,e,f,a}. Length=6. max=6.

  Answer: 6 (the substring "cdbefa").

Both pointers moved a total of 8+2 = 10 positions combined for an
8-character string. The brute force approach (check all 36 substrings)
would do much more work, especially on longer strings.
```
```

**Approach 1: Set-Based Variable Window - replace explanation:**

```
Use a set to track characters in the current window. The right pointer expands the window by adding characters. When the new character is already in the set (duplicate), shrink the window from the left by removing characters until the duplicate is gone.

1. Initialize `left = 0`, `seen = set()`, `max_len = 0`.
2. For each `right` from 0 to n-1:
   - While `s[right]` is in `seen`: remove `s[left]` from seen, increment left.
   - Add `s[right]` to seen.
   - Update `max_len = max(max_len, right - left + 1)`.

The inner while loop removes characters one by one from the left until the duplicate is gone. In the worst case (like "abcabc"), each character is added once and removed once, so the total work is O(n).

**Time:** O(n) - each character enters and leaves the set at most once.
**Space:** O(min(n, alphabet_size)) - the set holds at most one of each character. For lowercase English letters, that's at most 26.
```

**Approach 2: Hash Map with Jump - replace explanation:**

```
An optimization: instead of removing characters one by one from the left, use a dict that maps each character to its most recent index. When a duplicate is found, jump `left` directly past the previous occurrence.

1. Initialize `left = 0`, `char_index = {}`, `max_len = 0`.
2. For each `right`:
   - If `s[right]` is in `char_index` AND `char_index[s[right]] >= left`:
     Jump `left` to `char_index[s[right]] + 1` (one past the previous occurrence).
   - Update `char_index[s[right]] = right`.
   - Update `max_len`.

The `>= left` check is important: the character might be in the dict from before the current window (left has moved past it). Only jump if the previous occurrence is actually inside the current window.

**Time:** O(n) - single pass. No inner loop because `left` jumps instead of walking.
**Space:** O(min(n, alphabet_size)) - the dict stores one entry per unique character.

The time complexity is the same O(n) as the set approach (both visit each element at most twice), but the jump avoids the inner while loop, making the code slightly simpler and potentially faster in practice.
```

---

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

git diff --name-only | grep -v '.md$'
uv run pytest patterns/04_sliding_window/ -v --tb=short 2>&1 | tail -5

echo "=== README teaches basics ==="
for section in "The basics" "The two types" "Fixed-size" "Variable-size" "Why it.*O(n)" "Tracking window state" "Connection to data"; do
    grep -q "$section" patterns/04_sliding_window/README.md && echo "✅ $section" || echo "❌ $section"
done

grep "Input: s" patterns/04_sliding_window/problems/003_longest_substring.md
```
