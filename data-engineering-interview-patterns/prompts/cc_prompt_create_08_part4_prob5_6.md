# CC Prompt: Create Pattern 08 Stack (Part 4 of 5)

## What This Prompt Does

Creates problems 5-6: Car Fleet (LeetCode 853) and Largest Rectangle in Histogram (LeetCode 84).

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- Every approach explanation teaches the "why" not just the "what"

---

## Problem 5: Car Fleet (LeetCode #853)

### `problems/p853_car_fleet.py`

```python
"""
LeetCode 853: Car Fleet

Pattern: Stack - Monotonic (by arrival time)
Difficulty: Medium
Time Complexity: O(n log n) due to sorting
Space Complexity: O(n)
"""


def car_fleet(target: int, position: list[int], speed: list[int]) -> int:
    """
    Count car fleets arriving at target.

    A car fleet forms when a faster car catches up to a slower car
    ahead of it. Once caught, they travel together at the slower speed.
    Cars cannot pass each other.

    Sort by position (descending = closest to target first). Calculate
    each car's time to reach the target. If a car behind takes less
    time than the car ahead, it catches up and joins that fleet.
    Use a stack: only push arrival times that are strictly greater
    than the current fleet's time.
    """
    pairs = sorted(zip(position, speed), reverse=True)
    stack: list[float] = []

    for pos, spd in pairs:
        time = (target - pos) / spd
        if not stack or time > stack[-1]:
            stack.append(time)

    return len(stack)
```

### `problems/p853_car_fleet_test.py`

```python
"""Tests for LeetCode 853: Car Fleet."""

import pytest

from .p853_car_fleet import car_fleet


class TestCarFleet:
    """Core car fleet tests."""

    def test_example(self) -> None:
        assert car_fleet(12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3]) == 3

    def test_single_car(self) -> None:
        assert car_fleet(10, [3], [3]) == 1

    def test_no_cars(self) -> None:
        assert car_fleet(10, [], []) == 0

    def test_all_same_speed(self) -> None:
        # Same speed, different positions: no one catches up, each is its own fleet
        assert car_fleet(10, [0, 2, 4], [2, 2, 2]) == 3

    def test_all_merge_into_one(self) -> None:
        # Car at 0 going fast catches everyone
        assert car_fleet(10, [6, 8], [3, 2]) == 1

    def test_two_cars_no_merge(self) -> None:
        # Slower car behind faster car
        assert car_fleet(10, [0, 5], [1, 3]) == 2

    def test_exact_same_arrival(self) -> None:
        # Same arrival time = same fleet
        assert car_fleet(10, [0, 5], [2, 1]) == 1

    def test_cars_at_target(self) -> None:
        assert car_fleet(10, [10], [1]) == 1

    def test_three_fleets(self) -> None:
        assert car_fleet(20, [0, 5, 10, 15], [4, 3, 2, 1]) == 4
```

### `problems/853_car_fleet.md`

````markdown
# Car Fleet (LeetCode #853)

## Problem Statement

N cars are driving toward a target. Each car has a starting position and speed. A car can never pass another car ahead of it. When a faster car catches a slower car, they form a fleet and travel at the slower car's speed. Return the number of fleets arriving at the target.

## Thought Process

1. **Key insight:** Cars can't pass each other. So the car closest to the target determines whether cars behind it catch up or not. Process cars from closest to target (right) to farthest (left).
2. **Arrival time:** For each car, compute `(target - position) / speed`. This is how long it would take if driving alone.
3. **Fleet formation:** If a car behind has a shorter arrival time than the car ahead, it catches up and joins that fleet (its effective arrival time becomes the slower car's time). If it has a longer arrival time, it forms a new fleet.

## Worked Example

Sort cars by position (closest to target first). Calculate each car's solo arrival time. Walk through them: if a car's arrival time is longer than the current fleet's time, it can't catch up and starts a new fleet. If it's shorter or equal, it joins the current fleet.

```
Input: target=12, position=[10,8,0,5,3], speed=[2,4,1,1,3]

Pair and sort by position descending (closest to target first):
  pos=10, speed=2: time = (12-10)/2 = 1.0
  pos=8,  speed=4: time = (12-8)/4  = 1.0
  pos=5,  speed=1: time = (12-5)/1  = 7.0
  pos=3,  speed=3: time = (12-3)/3  = 3.0
  pos=0,  speed=1: time = (12-0)/1  = 12.0

Stack (tracks fleet arrival times):
  time=1.0: stack empty. New fleet. Push.       Stack: [1.0]
  time=1.0: 1.0 <= 1.0. Catches up. Same fleet. Stack: [1.0]
  time=7.0: 7.0 > 1.0. Can't catch up. New fleet. Stack: [1.0, 7.0]
  time=3.0: 3.0 <= 7.0. Catches up to the 7.0 fleet. Stack: [1.0, 7.0]
  time=12.0: 12.0 > 7.0. New fleet.            Stack: [1.0, 7.0, 12.0]

Answer: len(stack) = 3 fleets.

Fleet 1: cars at positions 10 and 8 (both arrive at time 1.0)
Fleet 2: cars at positions 5 and 3 (car at 3 catches car at 5)
Fleet 3: car at position 0 (too slow to catch anyone)
```

## Approaches

### Approach 1: Sort + Stack

<details>
<summary>📝 Explanation</summary>

1. Pair each car's position with its speed. Sort by position descending (closest to target first).
2. For each car, calculate its solo arrival time: `(target - position) / speed`.
3. Use a stack to track fleet arrival times. If the current car's time is strictly greater than the stack top, it's a new fleet (push it). If not, it catches up to the fleet ahead (skip it).
4. The stack size at the end is the number of fleets.

Why sort descending? We process from closest to target first. This means "the car ahead" is always the most recent stack entry. A car behind can only join a fleet that's closer to the target (ahead in position).

Why strict greater-than? If arrival times are equal, the cars meet exactly at the target (or en route). They form one fleet.

**Time:** O(n log n) - sorting dominates.
**Space:** O(n) - the stack and sorted pairs.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| Empty arrays | 0 | No cars |
| Single car | 1 | One car = one fleet |
| Same speed, different positions | n fleets | No one catches up |
| Same arrival time | 1 fleet | Meet at or before target |
| Car already at target | 1 fleet | Arrival time = 0 |

## Common Pitfalls

- **Sorting ascending instead of descending:** Must process closest-to-target first.
- **Using >= instead of >:** Equal arrival times mean they're in the same fleet, not a new one.
- **Integer division:** Use float division. `(12-10) // 3 = 0` but `(12-10) / 3 = 0.667`.

## Interview Tips

> "I'll sort cars by position, closest to target first. For each car, I compute arrival time. If it's slower than the fleet ahead, it's a new fleet. If faster, it catches up and merges. The stack tracks fleet arrival times."

## DE Application

Job scheduling with dependencies: tasks have estimated completion times and can't "pass" tasks they depend on. A slow upstream task becomes the bottleneck that downstream tasks queue behind, forming a "fleet" with the upstream task's completion time.

## Related Problems

- [853 variant: Car Fleet II](https://leetcode.com/problems/car-fleet-ii/) - When do cars collide
````

---

## Problem 6: Largest Rectangle in Histogram (LeetCode #84)

### `problems/p084_largest_rectangle.py`

```python
"""
LeetCode 84: Largest Rectangle in Histogram

Pattern: Stack - Monotonic increasing stack
Difficulty: Hard
Time Complexity: O(n)
Space Complexity: O(n)
"""


def largest_rectangle_area(heights: list[int]) -> int:
    """
    Find the largest rectangular area in a histogram.

    Use a monotonic increasing stack of indices. When a bar shorter
    than the stack top appears, the topped bar can no longer extend
    right. Pop it and calculate its area using:
    - height = the popped bar's height
    - width = distance from the new stack top to the current index - 1

    A sentinel value of 0 is appended to flush all remaining bars.
    """
    stack: list[int] = []  # indices
    max_area = 0
    heights = heights + [0]  # sentinel to force final cleanup

    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)

    return max_area


def largest_rectangle_brute(heights: list[int]) -> int:
    """Brute force: for each bar, expand left and right. O(n^2)."""
    max_area = 0
    n = len(heights)

    for i in range(n):
        h = heights[i]
        left = i
        right = i
        while left > 0 and heights[left - 1] >= h:
            left -= 1
        while right < n - 1 and heights[right + 1] >= h:
            right += 1
        max_area = max(max_area, h * (right - left + 1))

    return max_area
```

### `problems/p084_largest_rectangle_test.py`

```python
"""Tests for LeetCode 84: Largest Rectangle in Histogram."""

import pytest

from .p084_largest_rectangle import largest_rectangle_area, largest_rectangle_brute


@pytest.mark.parametrize("func", [largest_rectangle_area, largest_rectangle_brute])
class TestLargestRectangle:
    """Test both implementations."""

    def test_example(self, func) -> None:
        assert func([2, 1, 5, 6, 2, 3]) == 10

    def test_increasing(self, func) -> None:
        assert func([1, 2, 3, 4, 5]) == 9  # 3*3 at indices 2-4

    def test_decreasing(self, func) -> None:
        assert func([5, 4, 3, 2, 1]) == 9

    def test_single_bar(self, func) -> None:
        assert func([5]) == 5

    def test_equal_heights(self, func) -> None:
        assert func([3, 3, 3, 3]) == 12

    def test_two_bars(self, func) -> None:
        assert func([2, 4]) == 4

    def test_valley(self, func) -> None:
        assert func([6, 2, 5, 4, 5, 1, 6]) == 12

    def test_all_ones(self, func) -> None:
        assert func([1, 1, 1, 1, 1]) == 5

    def test_spike(self, func) -> None:
        assert func([1, 100, 1]) == 100

    def test_empty(self, func) -> None:
        assert func([]) == 0
```

### `problems/084_largest_rectangle.md`

````markdown
# Largest Rectangle in Histogram (LeetCode #84)

## Problem Statement

Given an array of integers `heights` representing a histogram where each bar has width 1, find the area of the largest rectangle that fits within the histogram.

Example: `[2, 1, 5, 6, 2, 3]` → 10 (rectangle of height 5 spanning indices 2-3)

## Thought Process

1. **Brute force:** For each bar, expand left and right as far as the bar's height allows. Area = height × width. O(n²).
2. **The insight:** For each bar, we need to know how far it can extend left and right before hitting a shorter bar. That's "previous smaller element" (left boundary) and "next smaller element" (right boundary).
3. **Monotonic increasing stack:** Maintain a stack of indices with increasing heights. When a shorter bar arrives, it's the right boundary for everything in the stack that's taller. Pop those bars and calculate their areas.

## Worked Example

A monotonic increasing stack of bar indices. When a shorter bar arrives, it "closes off" all taller bars in the stack. For each popped bar, we know its right boundary (the current shorter bar) and its left boundary (the new stack top after popping). Width = right boundary - left boundary - 1.

```
Input: heights = [2, 1, 5, 6, 2, 3]
Append sentinel 0: [2, 1, 5, 6, 2, 3, 0]

i=0 (h=2): Stack empty. Push 0.          Stack: [0(2)]
i=1 (h=1): 1 < 2. Pop 0.
           height=2, width=1 (no stack left, so width=i=1).
           area = 2×1 = 2. max=2.
           Push 1.                        Stack: [1(1)]
i=2 (h=5): 5 > 1. Push 2.               Stack: [1(1), 2(5)]
i=3 (h=6): 6 > 5. Push 3.               Stack: [1(1), 2(5), 3(6)]
i=4 (h=2): 2 < 6. Pop 3.
           height=6, width=4-2-1=1. area=6. max=6.
           2 < 5. Pop 2.
           height=5, width=4-1-1=2. area=10. max=10.
           2 > 1. Push 4.                Stack: [1(1), 4(2)]
i=5 (h=3): 3 > 2. Push 5.               Stack: [1(1), 4(2), 5(3)]
i=6 (h=0): sentinel. Pop 5.
           height=3, width=6-4-1=1. area=3.
           Pop 4. height=2, width=6-1-1=4. area=8.
           Pop 1. height=1, width=6 (stack empty). area=6.
           max stays 10.

Answer: 10 (height 5, spanning indices 2-3).

The sentinel (height 0) at the end forces all remaining bars to be
popped and evaluated. Without it, bars remaining in the stack at
the end would be missed.
```

## Approaches

### Approach 1: Brute Force (Expand from Each Bar)

<details>
<summary>📝 Explanation</summary>

For each bar at index i, use its height as the rectangle height. Expand left while adjacent bars are at least as tall. Expand right similarly. The width is the total span. Area = height × width. Track the maximum.

**Time:** O(n²) - each bar can expand up to n positions.
**Space:** O(1).

State it, note the complexity, then optimize.

</details>

### Approach 2: Monotonic Increasing Stack

<details>
<summary>📝 Explanation</summary>

Maintain a stack of indices where `heights[stack[i]]` is in increasing order. When a bar shorter than the stack top arrives:

1. Pop the top. The popped bar's height is the rectangle height.
2. The right boundary is the current index `i` (the shorter bar that caused the pop).
3. The left boundary is the new stack top (the first bar to the left that's shorter than the popped bar). If the stack is empty, the popped bar extends all the way to the left edge.
4. Width = right - left - 1 (or just `i` if the stack is empty).
5. Area = height × width. Update the maximum.

Repeat until the stack top is shorter than the current bar (or the stack is empty). Then push the current bar.

A sentinel value of 0 appended to the end ensures all bars get popped and evaluated. Without it, you'd need a separate cleanup loop for bars remaining in the stack.

**Time:** O(n) - each bar is pushed once and popped once.
**Space:** O(n) - the stack.

This is one of the hardest standard stack problems. The width calculation is the tricky part. Practice computing `i - stack[-1] - 1` with concrete examples until it clicks.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| `[]` | 0 | Empty histogram |
| `[5]` | 5 | Single bar |
| `[3, 3, 3]` | 9 | All equal - rectangle spans everything |
| `[1, 2, 3, 4, 5]` | 9 | Increasing - best is 3×3 at the end |
| `[5, 4, 3, 2, 1]` | 9 | Decreasing - best is 3×3 from the start |
| `[1, 100, 1]` | 100 | Tall spike - height=100, width=1 |

## Common Pitfalls

- **Width calculation when stack is empty:** When the stack is empty after popping, the popped bar extends from index 0 to i-1. Width = i, not i-1.
- **Forgetting the sentinel:** Without appending 0 at the end, bars remaining in the stack are never evaluated. Common source of wrong answers.
- **Off-by-one in width formula:** `i - stack[-1] - 1` is the width between the current index and the new stack top. Draw it out with specific numbers.

## Interview Tips

> "Each bar's maximum rectangle depends on how far it can extend left and right before hitting a shorter bar. A monotonic increasing stack gives me both boundaries in O(n): the left boundary is the previous stack entry, the right boundary is whatever causes the bar to be popped."

**Common follow-up:** "Explain the width calculation." Walk through a specific example: when we pop index 2 (height=5) at index 4, the new stack top is index 1. Width = 4 - 1 - 1 = 2. The rectangle spans indices 2 and 3.

## DE Application

Resource utilization analysis: given a histogram of concurrent connections over time buckets, what's the largest sustained capacity window? Same structure as largest rectangle. Also applies to finding the widest time range where throughput exceeded a threshold.

## Related Problems

- [85. Maximal Rectangle](https://leetcode.com/problems/maximal-rectangle/) - 2D version (apply this per row)
- [42. Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/) - Related histogram problem
- [739. Daily Temperatures](https://leetcode.com/problems/daily-temperatures/) - Same monotonic stack pattern
````

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Tests ==="
uv run pytest patterns/08_stack/problems/p853* patterns/08_stack/problems/p084* -v --tb=short 2>&1 | tail -15

echo ""
echo "=== Worked Examples ==="
for f in patterns/08_stack/problems/853_car_fleet.md patterns/08_stack/problems/084_largest_rectangle.md; do
    first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' "$f")
    echo "$(basename $f): $first" | head -c 80
    echo ""
done
```
