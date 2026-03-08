# 3Sum (LeetCode #15)

🔗 [LeetCode 15: 3Sum](https://leetcode.com/problems/3sum/)

> **Difficulty:** Medium | **Interview Frequency:** Common

## Problem Statement

Given an array of integers, find all unique triplets `[a, b, c]` such that `a + b + c = 0`.

The solution set must not contain duplicate triplets.

**Example:**
```
Input: nums = [-1, 0, 1, 2, -1, -4]
Output: [[-1, -1, 2], [-1, 0, 1]]
```

**Constraints:**
- 3 <= nums.length <= 3000
- -10^5 <= nums[i] <= 10^5

---

## Thought Process

1. **Brute force is O(n³)** - Three nested loops checking every triplet. Way too slow.
2. **Reduce to Two Sum** - Fix one element, then find a pair in the remaining that sums to its negation. That's O(n) per fixed element using two pointers.
3. **Sort first** - Enables two pointers and makes duplicate skipping possible.
4. **Handle duplicates** - Skip duplicate values at each level (the fixed element and both pointers) to avoid duplicate triplets.
5. **Total: O(n²)** - One loop for the fixed element × O(n) two-pointer scan.

---

## Worked Example

Three Sum reduces to Two Sum. Sort the array, then for each element, use two pointers on the rest to find a pair summing to the negative of the fixed element. The sorting enables both the two-pointer search and duplicate skipping (identical values become adjacent).

```
Input: nums = [-3, -1, 0, 1, 2, -1, -4]
Sorted: [-4, -3, -1, -1, 0, 1, 2]

  i=0, fix=-4, need pair summing to 4:
    left=1(-3), right=6(2): -3+2=-1 < 4 → move left
    left=2(-1), right=6(2): -1+2=1 < 4 → move left
    ...eventually left >= right. No triplet with -4.

  i=1, fix=-3, need pair summing to 3:
    left=2(-1), right=6(2): -1+2=1 < 3 → move left
    left=3(-1), right=6(2): -1+2=1 < 3 → move left
    left=4(0), right=6(2):  0+2=2 < 3 → move left
    left=5(1), right=6(2):  1+2=3 = 3 → FOUND [-3, 1, 2]
      Skip duplicates. left=6 >= right → done with -3.

  i=2, fix=-1, need pair summing to 1:
    left=3(-1), right=6(2): -1+2=1 → FOUND [-1, -1, 2]
      Skip left to 4(0), right to 5(1).
    left=4(0), right=5(1): 0+1=1 → FOUND [-1, 0, 1]
      Done.

  i=3, fix=-1 = same as nums[2] → SKIP (duplicate)

  i=4, fix=0: left=5(1), right=6(2): 1+2=3 > 0 → no triplet.

  Result: [[-3, 1, 2], [-1, -1, 2], [-1, 0, 1]]

O(n²) total: sort O(n log n) + n outer iterations × O(n) inner scan.
```

---

## Approaches

### Approach: Sort + Two Pointers

<details>
<summary>💡 Hint 1</summary>

If you fix one number, the problem reduces to Two Sum on the rest of the array.

</details>

<details>
<summary>💡 Hint 2</summary>

Sorting lets you skip duplicates easily: if `nums[i] == nums[i-1]`, skip it.

</details>

<details>
<summary>📝 Explanation</summary>

Sort the array. For each element at index i (the "fixed" element), use opposite-end two pointers (left=i+1, right=n-1) to find a pair summing to `-nums[i]`.

Skip duplicates at three levels:
- Skip fixed element if `nums[i] == nums[i-1]`
- After finding a triplet, advance left past duplicate values
- After finding a triplet, retreat right past duplicate values

Early exit: if `nums[i] > 0`, stop. Three positive numbers can't sum to zero.

**Time:** O(n²) - sort is O(n log n), outer loop × inner two-pointer = O(n²).
**Space:** O(1) extra (or O(n) for the sort).

Reduces O(n³) brute force to O(n²) by replacing the inner two loops with a single two-pointer scan.

</details>

<details>
<summary>💻 Code</summary>

```python
def three_sum(nums: list[int]) -> list[list[int]]:
    nums.sort()
    result: list[list[int]] = []
    n = len(nums)

    for i in range(n - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        if nums[i] > 0:
            break

        left, right = i + 1, n - 1
        target = -nums[i]

        while left < right:
            current = nums[left] + nums[right]
            if current == target:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif current < target:
                left += 1
            else:
                right -= 1

    return result
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Basic | `[-1,0,1,2,-1,-4]` | `[[-1,-1,2],[-1,0,1]]` | Multiple triplets |
| All zeros | `[0,0,0]` | `[[0,0,0]]` | Valid triplet |
| No solution | `[0,1,1]` | `[]` | No triplet sums to zero |
| All negative | `[-3,-2,-1]` | `[]` | Can't reach zero |
| Heavy duplicates | `[-1,-1,-1,0,1,1,1]` | `[[-1,0,1]]` | Duplicate skipping at all levels |
| Too short | `[1,-1]` | `[]` | Need at least 3 elements |

---

## Common Pitfalls

1. **Duplicate triplets** - The hardest part of this problem. You must skip duplicates at the outer loop AND the inner pointer moves. Missing either produces duplicates.
2. **Skipping logic off-by-one** - The outer skip checks `nums[i] == nums[i-1]`, not `nums[i] == nums[i+1]`. Checking forward would skip valid first occurrences.
3. **Not sorting first** - Two pointers need sorted input. Without sorting, duplicate detection also becomes harder.
4. **Forgetting to advance both pointers after finding a match** - After finding a triplet, advance both left and right (not just one).

---

## Interview Tips

**What to say:**
> "I'll sort the array first, then iterate through each element and use two pointers on the remaining elements to find pairs summing to its negation. Sorting makes duplicate handling clean - I skip consecutive identical values at each level."

**This is one of the most common medium interview questions.** The key insight is reducing 3Sum to Two Sum. If you can articulate that reduction clearly, you're in good shape.

**Follow-up: "What about 4Sum?"**
→ Same pattern, one more nested loop. Fix two elements, Two Sum on the rest. O(n³). Generalized k-Sum is O(n^(k-1)).

**What the interviewer evaluates:** Reducing 3Sum to Two Sum (fix one element, two-pointer the rest) tests decomposition skill. Duplicate handling tests attention to detail. The O(n^2) lower bound discussion tests theoretical understanding - you can't do better for the general case.

---

## DE Application

Multi-way matching problems appear in data engineering when:
- Finding records across three or more tables that satisfy a combined constraint
- Reconciliation across multiple data sources (three-way matching in accounting)
- Entity resolution where matches require agreement across multiple attributes

The "reduce to a simpler problem" approach is more broadly applicable than the specific algorithm.

---

## At Scale

Sort + two pointers gives O(n^2) time with O(1) extra memory. For n=10K, that's 100M operations (~0.1 seconds). For n=100K, that's 10B operations (~10 seconds). For n=1M+, O(n^2) is too slow regardless of approach. The hash set alternative trades memory for slightly simpler code but is still O(n^2) time. At scale, 3Sum-type problems (find matching triplets across datasets) become join problems: a three-way join with a filter condition. In SQL: `SELECT a.val, b.val, c.val FROM t a JOIN t b JOIN t c WHERE a.val + b.val + c.val = 0`. The optimizer decides whether to use hash joins or sort-merge joins based on data size.

---

## Related Problems

- [1. Two Sum](../../01_hash_map/problems/001_two_sum.md) - The building block
- [167. Two Sum II](167_two_sum_ii.md) - The inner loop of 3Sum
- [18. 4Sum](https://leetcode.com/problems/4sum/) - Next level generalization
