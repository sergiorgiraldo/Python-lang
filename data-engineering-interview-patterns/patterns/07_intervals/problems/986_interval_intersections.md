# Interval List Intersections (LeetCode #986)

🔗 [LeetCode 986: Interval List Intersections](https://leetcode.com/problems/interval-list-intersections/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Given two lists of sorted, non-overlapping intervals, return their intersection. Each interval in the result represents a time range present in both lists.

**Example:**
```
Input:
  firstList  = [[0,2],[5,10],[13,23],[24,25]]
  secondList = [[1,5],[8,12],[15,24],[25,26]]
Output: [[1,2],[5,5],[8,10],[15,23],[24,24],[25,25]]
```

**Constraints:**
- Both lists are sorted and non-overlapping within themselves
- 0 <= firstList.length, secondList.length <= 1000

---

## Thought Process

1. **Clarify** - Both lists are already sorted and non-overlapping. We need to find all overlapping segments between the two lists.
2. **Two pointers** - Since both lists are sorted, use two pointers (pattern 02). Advance the pointer pointing to the interval that ends first.
3. **Intersection formula** - Two intervals overlap if `max(starts) <= min(ends)`. The intersection is `[max(starts), min(ends)]`.

---

## Worked Example

Find the intersection of two sorted lists of intervals. Two pointers, one per list. At each step, check if the current pair overlaps. If yes, the intersection is [max of starts, min of ends]. Advance whichever pointer has the earlier end.

```
Input:
  A = [[0,2], [5,10], [13,23], [24,25]]
  B = [[1,5], [8,12], [15,24], [25,26]]

  pA=0, pB=0

  A=[0,2] vs B=[1,5]: overlap? max(0,1)=1 ≤ min(2,5)=2. YES.
    Intersection: [1,2]. A ends first (2<5) → advance pA.

  A=[5,10] vs B=[1,5]: overlap? max(5,1)=5 ≤ min(10,5)=5. YES (touching).
    Intersection: [5,5]. B ends first (5<10) → advance pB.

  A=[5,10] vs B=[8,12]: overlap? max(5,8)=8 ≤ min(10,12)=10. YES.
    Intersection: [8,10]. A ends first → advance pA.

  A=[13,23] vs B=[8,12]: overlap? max(13,8)=13 ≤ min(23,12)=12. NO.
    B ends first → advance pB.

  A=[13,23] vs B=[15,24]: overlap? max(13,15)=15 ≤ min(23,24)=23. YES.
    Intersection: [15,23]. A ends first → advance pA.

  A=[24,25] vs B=[15,24]: overlap? max(24,15)=24 ≤ min(25,24)=24. YES.
    Intersection: [24,24]. B ends first → advance pB.

  A=[24,25] vs B=[25,26]: overlap? max(24,25)=25 ≤ min(25,26)=25. YES.
    Intersection: [25,25]. A ends first → advance pA. A exhausted.

  Result: [[1,2], [5,5], [8,10], [15,23], [24,24], [25,25]]
  O(n + m), one pass through both lists.
```

---

## Approaches

### Approach 1: Two Pointers (Optimal)

<details>
<summary>💡 Hint</summary>

Both lists are sorted. Use two pointers and advance the one pointing to the earlier-ending interval.

</details>

<details>
<summary>📝 Explanation</summary>

Both input lists are sorted by start time. Use one pointer per list. At each step:

1. Check if the current pair overlaps: `max(a_start, b_start) ≤ min(a_end, b_end)`.
2. If yes, the intersection is `[max(a_start, b_start), min(a_end, b_end)]`. Add it to the result.
3. Advance the pointer whose current interval ends first. That interval can't overlap with anything later in the other list (since both lists are sorted).

**Time:** O(n + m) where n and m are the lengths of the two lists. Each pointer advances at most n or m times.
**Space:** O(1) extra (not counting the output).

This is the same two-pointer merge pattern from Pattern 02, adapted for intersection instead of union.

</details>

<details>
<summary>💻 Code</summary>

```python
def interval_intersection(first_list, second_list):
    result = []
    i = j = 0
    while i < len(first_list) and j < len(second_list):
        start = max(first_list[i][0], second_list[j][0])
        end = min(first_list[i][1], second_list[j][1])
        if start <= end:
            result.append([start, end])
        if first_list[i][1] < second_list[j][1]:
            i += 1
        else:
            j += 1
    return result
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| No intersection | `[[1,3]], [[5,7]]` | `[]` | Completely disjoint |
| One empty | `[], [[1,5]]` | `[]` | Nothing to intersect |
| Point intersection | `[[1,3]], [[3,5]]` | `[[3,3]]` | Single point overlap |
| Full overlap | `[[0,10]], [[0,10]]` | `[[0,10]]` | Identical intervals |
| Contained | `[[0,10]], [[3,5]]` | `[[3,5]]` | One inside the other |

---

## Common Pitfalls

1. **Advancing the wrong pointer** - Always advance the one with the earlier end time. Advancing the other one might skip valid intersections.
2. **Forgetting point intersections** - `[1,3]` and `[3,5]` intersect at the single point 3. Use `<=` not `<`.

---

## Interview Tips

**What to say:**
> "Both lists are sorted, so I'll use two pointers. At each step, I check if the current intervals overlap using max(starts) <= min(ends). Then I advance the pointer with the earlier end time."

**What the interviewer evaluates:** The two-pointer approach on two sorted lists tests merge logic. Deciding which pointer to advance (the one with the earlier end time) is the key insight. Clean implementation without edge case bugs shows precision. Mentioning time-range joins as the production equivalent connects this to real work.

---

## DE Application

Interval intersection finds common time windows:
- "When were both system A and system B online?" (availability intersection)
- "What time ranges are covered by both the US and EU data retention policies?"
- Finding overlapping partition ranges across two datasets for join optimization

This connects directly to two-pointer merge from pattern 02, applied to intervals instead of individual elements.

See: [Interval Intersection DE Scenario](../de_scenarios/interval_intersection.md)

## At Scale

Two-pointer merge of two sorted interval lists: O(n + m) time, O(1) extra memory. For two lists of 10M intervals each, this takes ~1 second. The output can be as large as n + m. At scale, interval intersection is the algorithmic basis of time-range joins: "for each user session, find all events that occurred during that session." This is an O(n + m) merge join on sorted intervals, but SQL engines often can't optimize it this way (they use nested loops or hash joins with range conditions). Implementing the two-pointer merge in a UDF or in application code can be orders of magnitude faster than the SQL equivalent for large datasets.

---

## Related Problems

- [56. Merge Intervals](056_merge_intervals.md) - Union instead of intersection
- [252. Meeting Rooms](252_meeting_rooms.md) - Overlap detection
