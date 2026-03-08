# Koko Eating Bananas (LeetCode #875)

🔗 [LeetCode 875: Koko Eating Bananas](https://leetcode.com/problems/koko-eating-bananas/)

> **Difficulty:** Medium | **Interview Frequency:** Common

## Problem Statement

Koko has `n` piles of bananas with `piles[i]` bananas in each pile. She has `h` hours to eat them all. Each hour, she picks one pile and eats up to `k` bananas from it. If the pile has fewer than `k`, she eats the whole pile and waits for the next hour.

Find the minimum integer `k` such that she can eat all bananas within `h` hours.

**Example:**
```
Input: piles = [3, 6, 7, 11], h = 8
Output: 4
Explanation: At speed 4, she needs ceil(3/4)+ceil(6/4)+ceil(7/4)+ceil(11/4) = 1+2+2+3 = 8 hours.
```

**Constraints:**
- 1 <= piles.length <= 10^4
- piles.length <= h <= 10^9
- 1 <= piles[i] <= 10^9

---

## Thought Process

1. **What's the search space?** The minimum possible speed is 1. The maximum useful speed is `max(piles)` (eating faster than the largest pile doesn't help). So we're searching in [1, max(piles)].
2. **Is it monotonic?** If speed k is fast enough, then k+1 is also fast enough. That monotonic property means binary search works.
3. **What's the feasibility check?** At speed k, each pile takes `ceil(pile / k)` hours. Sum across all piles. If total <= h, speed k is feasible.
4. **This is "binary search on the answer."** We're not searching an array. We're searching over possible answers and testing each one.

---

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

---

## Approaches

### Approach: Binary Search on Answer

<details>
<summary>💡 Hint 1</summary>

Don't think about this as an array problem. Think about it as: "given a candidate speed k, can I check whether it works in O(n)?"

</details>

<details>
<summary>💡 Hint 2</summary>

If speed k works, do I need to try anything larger? If speed k doesn't work, do I need to try anything smaller?

</details>

<details>
<summary>📝 Explanation</summary>

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

</details>

<details>
<summary>💻 Code</summary>

```python
import math

def min_eating_speed(piles: list[int], h: int) -> int:
    left, right = 1, max(piles)
    while left < right:
        mid = (left + right) // 2
        hours_needed = sum(math.ceil(pile / mid) for pile in piles)
        if hours_needed <= h:
            right = mid
        else:
            left = mid + 1
    return left
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Standard | `[3,6,7,11], 8` | `4` | Basic case |
| Tight deadline | `[30,11,23,4,20], 5` | `30` | h = len(piles), must eat max pile at once |
| Relaxed deadline | `[30,11,23,4,20], 6` | `23` | One extra hour allows slower speed |
| Single pile | `[1], 1` | `1` | Minimum input |
| Large pile, many hours | `[100], 10` | `10` | ceil(100/10) = 10 hours |
| All same size | `[5,5,5,5], 4` | `5` | Each pile in exactly one hour |
| Plenty of time | `[3,6,7,11], 100` | `1` | Speed 1 is enough |

---

## Common Pitfalls

1. **Integer division instead of ceiling** - `pile / k` rounds down in Python 3 floor division. Use `math.ceil(pile / k)` or the trick `(pile + k - 1) // k` to get ceiling division.
2. **Search range starting at 0** - Speed 0 causes division by zero. Start at 1.
3. **Search range ending at sum(piles)** - Wastes search space. `max(piles)` is the maximum useful speed.
4. **Not recognizing the pattern** - This problem looks nothing like binary search at first glance. The recognition signal is "minimize something subject to a constraint" where the feasibility check is monotonic.

---

## Interview Tips

**What to say:**
> "The answer must be between 1 and max(piles). For any candidate speed, I can check feasibility in O(n) by summing the hours per pile. Since faster speeds always work if slower ones do, the feasibility is monotonic, so I can binary search on the answer."

**The "binary search on answer" pattern is a favorite interview topic.** It tests whether you can recognize binary search in a non-obvious setting. The template is always the same: define the search range, write a feasibility check and binary search for the boundary.

**Ceiling division shortcut:**
> "I'm using `math.ceil(pile / k)` for clarity. The integer-only version is `(pile + k - 1) // k`, which avoids floating point."

**What the interviewer evaluates:** "Binary search the answer" is a more advanced pattern than "binary search the array." Recognizing the monotonic property in the solution space (not the data) is the insight. The feasibility check function is where most implementation bugs occur. At principal level, connecting this to capacity planning and resource estimation is a differentiator.

---

## DE Application

"Binary search on answer" shows up in data engineering when:
- **Resource allocation** - "What's the minimum number of workers/partitions to process this batch in under X minutes?" The check function runs a simulation or calculation.
- **Batch size optimization** - "What's the largest batch size that keeps memory under Y GB?" Test each candidate batch size.
- **Rate limit planning** - "What's the minimum delay between API calls to stay under the rate limit while finishing the backfill in Z hours?"

The pattern is always the same: a range of possible answers, a monotonic feasibility check and binary search to find the optimal answer.

See: [Binary Search on Answer (DE Scenario)](../de_scenarios/search_on_answer.md)

---

## At Scale

"Binary search the answer" is the key pattern here: instead of searching the data, search the solution space. The solution space has a monotonic property (if speed k works, k+1 also works), enabling binary search. At scale, this pattern is everywhere: "what's the minimum number of Spark executors to finish this job in under 1 hour?" Binary search executor count, simulate the workload at each candidate. "What's the minimum batch size for this API that keeps latency under 100ms?" Same structure. The simulation step (checking if a candidate works) is the bottleneck, not the binary search itself.

---

## Related Problems

- [35. Search Insert Position](035_search_insert.md) - Same convergence logic, simpler setting
- [162. Find Peak Element](162_find_peak.md) - Another non-sorted binary search
- [1011. Capacity to Ship Packages](https://leetcode.com/problems/capacity-to-ship-packages-within-d-days/) - Nearly identical "search on answer" structure
- [410. Split Array Largest Sum](https://leetcode.com/problems/split-array-largest-sum/) - Harder variant, same pattern
