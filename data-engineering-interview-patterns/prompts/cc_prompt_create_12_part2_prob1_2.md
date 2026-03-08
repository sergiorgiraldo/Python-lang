# CC Prompt: Create Pattern 12 Combined Patterns (Part 2 of 4)

## What This Prompt Does

Creates problems 1-2: 3Sum (LeetCode 15) and Minimum Window Substring (LeetCode 76).

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- Approach explanations must emphasize HOW patterns combine

---

## Problem 1: 3Sum (LeetCode #15)

### `problems/p015_3sum.py`

```python
"""
LeetCode 15: 3Sum

Combined Patterns: Sort + Two Pointers
Difficulty: Medium
Time Complexity: O(n^2) - sort O(n log n) + nested two-pointer O(n^2)
Space Complexity: O(1) extra (excluding output and sort)
"""


def three_sum(nums: list[int]) -> list[list[int]]:
    """
    Find all unique triplets that sum to zero.

    Strategy: sort the array, then for each element, use two pointers
    to find pairs that complete the triplet. Sorting enables both
    the two-pointer technique and efficient duplicate skipping.
    """
    nums.sort()
    result: list[list[int]] = []

    for i in range(len(nums) - 2):
        # Skip duplicates for the first element
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        # Early termination: smallest possible sum is too large
        if nums[i] > 0:
            break

        target = -nums[i]
        left = i + 1
        right = len(nums) - 1

        while left < right:
            current_sum = nums[left] + nums[right]

            if current_sum == target:
                result.append([nums[i], nums[left], nums[right]])
                # Skip duplicates for both pointers
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif current_sum < target:
                left += 1
            else:
                right -= 1

    return result


def three_sum_hash(nums: list[int]) -> list[list[int]]:
    """
    Alternative: hash set approach.

    For each pair (i, j), check if -(nums[i] + nums[j]) exists.
    Uses more space but avoids sorting.
    """
    result_set: set[tuple[int, ...]] = set()

    for i in range(len(nums)):
        seen: set[int] = set()
        for j in range(i + 1, len(nums)):
            complement = -(nums[i] + nums[j])
            if complement in seen:
                triplet = tuple(sorted([nums[i], nums[j], complement]))
                result_set.add(triplet)
            seen.add(nums[j])

    return [list(t) for t in result_set]
```

### `problems/p015_3sum_test.py`

```python
"""Tests for LeetCode 15: 3Sum."""

import pytest

from p015_3sum import three_sum, three_sum_hash


def _normalize(result: list[list[int]]) -> list[list[int]]:
    """Sort each triplet and the overall list for comparison."""
    return sorted([sorted(t) for t in result])


@pytest.mark.parametrize("func", [three_sum, three_sum_hash])
class TestThreeSum:
    """Test both approaches."""

    def test_example(self, func) -> None:
        result = func([-1, 0, 1, 2, -1, -4])
        assert _normalize(result) == [[-1, -1, 2], [-1, 0, 1]]

    def test_no_triplet(self, func) -> None:
        assert func([0, 1, 1]) == []

    def test_all_zeros(self, func) -> None:
        result = func([0, 0, 0])
        assert _normalize(result) == [[0, 0, 0]]

    def test_all_zeros_extra(self, func) -> None:
        result = func([0, 0, 0, 0])
        assert _normalize(result) == [[0, 0, 0]]

    def test_empty(self, func) -> None:
        assert func([]) == []

    def test_two_elements(self, func) -> None:
        assert func([1, -1]) == []

    def test_negative_triplet(self, func) -> None:
        result = func([-2, -1, 0, 1, 2, 3])
        expected = [[-2, -1, 3], [-2, 0, 2], [-1, 0, 1]]
        assert _normalize(result) == expected

    def test_no_duplicates_in_result(self, func) -> None:
        result = func([-1, -1, -1, 0, 1, 1, 1])
        assert _normalize(result) == [[-1, 0, 1]]

    def test_large_range(self, func) -> None:
        result = func([-100, 0, 50, 50, 100])
        assert _normalize(result) == [[-100, 0, 100], [-100, 50, 50]]
```

### `problems/015_3sum.md`

````markdown
# 3Sum (LeetCode #15)

## Problem Statement

Given an integer array, return all unique triplets [a, b, c] such that a + b + c = 0.

## Thought Process

1. **Brute force:** Three nested loops. O(n^3). Too slow.
2. **Reduce to Two Sum:** Fix one element, then find pairs that sum to its negation. That's Two Sum, which we can solve in O(n) with either a hash set or two pointers.
3. **Why sort first?** Sorting enables two things: the two-pointer technique (which requires sorted data) and easy duplicate skipping (duplicates are adjacent after sorting).

## Worked Example

Sort first, then for each element fix it as the first value of the triplet and use two pointers on the remaining array to find pairs that complete the sum. Sorting reduces a three-way search to a two-pointer scan and makes duplicate skipping trivial since equal values are adjacent.

```
Input: [-1, 0, 1, 2, -1, -4]

Step 1: Sort → [-4, -1, -1, 0, 1, 2]

Step 2: For each element i, two-pointer scan [i+1, n-1]

  i=0, nums[0]=-4, target=4
    L=1(-1), R=5(2): -1+2=1 < 4 → L++
    L=2(-1), R=5(2): -1+2=1 < 4 → L++
    L=3(0), R=5(2): 0+2=2 < 4 → L++
    L=4(1), R=5(2): 1+2=3 < 4 → L++
    L=5 >= R → done. No triplet with -4.

  i=1, nums[1]=-1, target=1
    L=2(-1), R=5(2): -1+2=1 = target → FOUND [-1, -1, 2]
      Skip duplicate L: nums[2]==nums[3]? -1!=0, stop. L=3.
      Skip duplicate R: nums[5]==nums[4]? 2!=1, stop. R=4.
    L=3(0), R=4(1): 0+1=1 = target → FOUND [-1, 0, 1]
      L=4, R=3 → done.

  i=2, nums[2]=-1: same as nums[1] → skip (duplicate first element).

  i=3, nums[3]=0, target=0
    L=4(1), R=5(2): 1+2=3 > 0 → R--
    L=4 >= R → done.

Result: [[-1, -1, 2], [-1, 0, 1]]
```

## Approaches

### Approach 1: Sort + Two Pointers

<details>
<summary>📝 Explanation</summary>

**Pattern combination:** Sorting (preprocessing) enables the two-pointer technique (main logic).

Sort the array. For each index i from 0 to n-3, set target = -nums[i]. Use two pointers L=i+1 and R=n-1 to find pairs summing to target. Move L right if sum is too small, R left if too large.

Duplicate handling: skip adjacent equal values for i (to avoid duplicate triplets). After finding a match, skip adjacent equal values for L and R.

Early termination: if nums[i] > 0, no valid triplet exists (all remaining values are positive, sum can't be zero).

**Time:** O(n^2). Sort is O(n log n). The outer loop runs n times, inner two-pointer scan is O(n). Total: O(n log n + n^2) = O(n^2).
**Space:** O(1) extra (the sort is in-place, output doesn't count).

This is the standard approach. The sort + two-pointer combination is a fundamental pattern that appears in many problems.

</details>

### Approach 2: Hash Set

<details>
<summary>📝 Explanation</summary>

**Pattern combination:** Hash map (O(1) lookup) replaces the two-pointer scan.

For each pair (i, j), compute complement = -(nums[i] + nums[j]) and check if it exists in a hash set of previously seen values. Use a set of sorted tuples to avoid duplicates.

Simpler to implement but uses O(n) extra space and the duplicate handling is less elegant (relies on the set of tuples). In practice, the sort + two-pointer approach is preferred for interviews because it's more efficient and demonstrates more technique.

**Time:** O(n^2). Two nested loops, O(1) hash lookups.
**Space:** O(n) for the hash set.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| `[0, 0, 0]` | `[[0, 0, 0]]` | All zeros sum to zero |
| `[0, 0, 0, 0]` | `[[0, 0, 0]]` | Duplicates in output must be avoided |
| `[-1, -1, 0, 1, 1]` | `[[-1, 0, 1]]` | Multiple duplicates, one unique triplet |
| `[1, 2, 3]` | `[]` | All positive, no triplet sums to zero |

## Common Pitfalls

- **Duplicate triplets:** Without skipping duplicates, [-1, -1, 2] might appear multiple times. Skip equal adjacent values for all three positions.
- **Off-by-one in early termination:** Stop the outer loop at n-3 (need at least 3 elements for a triplet).

## Interview Tips

> "I'll sort first to enable the two-pointer technique and easy duplicate skipping. For each element, I use two pointers on the remaining array to find pairs summing to its negation. Total: O(n^2)."

## DE Application

Finding matching records across datasets. "Find all combinations of transactions from three accounts that net to zero" is structurally identical. The sort + scan pattern also appears in merge-based deduplication and reconciliation.

## Related Problems

- [1. Two Sum](https://leetcode.com/problems/two-sum/) - The building block (single pair)
- [16. 3Sum Closest](https://leetcode.com/problems/3sum-closest/) - Find triplet closest to target
- [18. 4Sum](https://leetcode.com/problems/4sum/) - Extension to four elements
````

---

## Problem 2: Minimum Window Substring (LeetCode #76)

### `problems/p076_min_window_substring.py`

```python
"""
LeetCode 76: Minimum Window Substring

Combined Patterns: Sliding Window + Hash Map
Difficulty: Hard
Time Complexity: O(n + m) where n = len(s), m = len(t)
Space Complexity: O(m) for the frequency maps
"""

from collections import Counter


def min_window(s: str, t: str) -> str:
    """
    Find the minimum window in s that contains all characters of t.

    Strategy: sliding window where the hash map tracks how many
    characters of t are satisfied within the current window.

    Expand the right pointer to include more characters.
    Once all of t is covered, shrink the left pointer to minimize.
    """
    if not t or not s:
        return ""

    need = Counter(t)  # characters we need and their counts
    have = 0  # number of UNIQUE characters satisfied
    required = len(need)  # number of unique characters to satisfy

    window_counts: dict[str, int] = {}
    best = (float("inf"), 0, 0)  # (length, left, right)

    left = 0
    for right in range(len(s)):
        char = s[right]
        window_counts[char] = window_counts.get(char, 0) + 1

        # Check if this character's requirement is now met
        if char in need and window_counts[char] == need[char]:
            have += 1

        # Shrink window while all requirements are met
        while have == required:
            window_len = right - left + 1
            if window_len < best[0]:
                best = (window_len, left, right)

            # Remove leftmost character
            left_char = s[left]
            window_counts[left_char] -= 1
            if left_char in need and window_counts[left_char] < need[left_char]:
                have -= 1
            left += 1

    length, start, end = best
    return s[start : end + 1] if length != float("inf") else ""
```

### `problems/p076_min_window_substring_test.py`

```python
"""Tests for LeetCode 76: Minimum Window Substring."""

import pytest

from p076_min_window_substring import min_window


class TestMinWindow:
    """Core min window tests."""

    def test_example(self) -> None:
        assert min_window("ADOBECODEBANC", "ABC") == "BANC"

    def test_exact_match(self) -> None:
        assert min_window("a", "a") == "a"

    def test_no_match(self) -> None:
        assert min_window("a", "aa") == ""

    def test_entire_string(self) -> None:
        assert min_window("abc", "abc") == "abc"

    def test_duplicate_chars_in_t(self) -> None:
        assert min_window("aab", "aab") == "aab"

    def test_window_at_start(self) -> None:
        assert min_window("abc", "ab") == "ab"

    def test_window_at_end(self) -> None:
        assert min_window("cab", "ab") == "ab"

    def test_empty_t(self) -> None:
        assert min_window("abc", "") == ""

    def test_empty_s(self) -> None:
        assert min_window("", "abc") == ""

    def test_repeated_chars(self) -> None:
        result = min_window("aaaaaaaaab", "ab")
        assert result == "ab"

    def test_multiple_valid_windows(self) -> None:
        # Multiple valid windows, return the first minimum
        result = min_window("ABCABC", "ABC")
        assert len(result) == 3  # any 3-char window with A, B, C
```

### `problems/076_min_window_substring.md`

````markdown
# Minimum Window Substring (LeetCode #76)

## Problem Statement

Given strings s and t, find the minimum window in s that contains all characters of t (including duplicates). Return "" if no such window exists.

## Thought Process

1. **Sliding window:** Expand the right boundary to include more characters, shrink the left boundary to minimize the window.
2. **Hash map for tracking:** A Counter tracks what characters we need from t and how many. A second map tracks character frequencies in the current window.
3. **"Have" counter:** Instead of comparing maps every step (O(m)), track how many unique characters are fully satisfied. When have == required, the window is valid.

## Worked Example

The hash map tracks character requirements; the sliding window finds the minimum range that satisfies them. The "have" counter avoids recomputing the full map comparison at every step, keeping the inner loop O(1).

```
s = "ADOBECODEBANC", t = "ABC"
need = {A:1, B:1, C:1}, required = 3

Expand right:
  right=0 'A': window={A:1}. A count met → have=1.
  right=1 'D': window={A:1, D:1}. have=1.
  right=2 'O': have=1.
  right=3 'B': window={..., B:1}. B count met → have=2.
  right=4 'E': have=2.
  right=5 'C': window={..., C:1}. C count met → have=3.

  have == required (3) → window "ADOBEC" is valid (length 6).
  Record best = (6, 0, 5).

Shrink left:
  left=0 remove 'A': window={A:0}. A drops below need → have=2.
  left=1. Window no longer valid → stop shrinking.

Continue expanding:
  right=6 'O': have=2.
  right=7 'D': have=2.
  right=8 'E': have=2.
  right=9 'B': have=2.
  right=10 'A': window={A:1}. A count met → have=3.

  Window s[1:11] = "DOBECODEBA" (length 10) > best. Don't update.

  Shrink left:
    left=1 remove 'D': still have=3. Window = "OBECODEBA" (9).
    left=2 remove 'O': still have=3. Window = "BECODEBA" (8).
    ...continue shrinking...
    left=5 remove 'C': C drops → have=2. Stop.

  right=11 'N': have=2.
  right=12 'C': window={C:1}. have=3.
    Window s[9:13] = "BANC" (length 4) < best (6). Update best.
    Shrink: remove 'B' → have=2. Stop.

Result: "BANC" (length 4)
```

## Approaches

### Approach 1: Sliding Window + Hash Map

<details>
<summary>📝 Explanation</summary>

**Pattern combination:** The sliding window (Pattern 04) manages the search range. The hash map (Pattern 01) tracks character frequencies within the window and what's needed from t.

Two maps: `need` (from Counter(t)) and `window_counts` (current window). A `have` counter tracks how many unique characters are fully satisfied. When `have == required`, the window is valid.

Expand right to include characters. When valid, try shrinking left to find a smaller valid window. Track the best window found.

The `have` counter is the key optimization: instead of comparing the two maps (O(26) for lowercase) at every step, we maintain a running count of satisfied characters. Each character satisfaction change is O(1).

**Time:** O(n + m) where n = len(s), m = len(t). Each character in s is added and removed at most once. Building the Counter for t is O(m).
**Space:** O(m) for the character maps.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| t has duplicate chars "aa" | Must have 2 a's in window | Count matters, not just presence |
| s shorter than t | "" | Can't possibly contain all of t |
| Exact match | Return entire s | Window = whole string |
| t is single char | Find first occurrence | Minimum window is length 1 |

## Common Pitfalls

- **Tracking counts not just presence:** If t = "aa", one 'a' in the window isn't enough. The window must have at least 2.
- **Not shrinking enough:** After finding a valid window, keep shrinking left until the window becomes invalid. The first valid window isn't necessarily the smallest.

## Interview Tips

> "I'll use a sliding window with a hash map to track character frequencies. Expand right to cover all of t's characters, then shrink left to minimize. A 'have' counter tracks how many unique characters are fully satisfied, making each step O(1)."

## DE Application

Finding the smallest time window containing all required events. "What's the shortest period in which a user performed sign-up, first purchase and first support ticket?" Same structure: sliding window over time-sorted events with a set of required event types.

## Related Problems

- [567. Permutation in String](https://leetcode.com/problems/permutation-in-string/) - Fixed window with same character matching
- [438. Find All Anagrams](https://leetcode.com/problems/find-all-anagrams-in-a-string/) - All windows of size len(t) matching
````

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Tests ==="
uv run pytest patterns/12_combined_patterns/problems/ -v --tb=short 2>&1 | tail -15

echo ""
echo "=== Worked Examples start with prose ==="
for f in patterns/12_combined_patterns/problems/015_3sum.md patterns/12_combined_patterns/problems/076_min_window_substring.md; do
    first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' "$f")
    echo "$(basename $f): $first" | head -c 80
    echo ""
done
```
