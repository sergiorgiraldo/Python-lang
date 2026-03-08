# Car Fleet (LeetCode #853)

🔗 [LeetCode 853: Car Fleet](https://leetcode.com/problems/car-fleet/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

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

**What the interviewer evaluates:** The sort-by-position + arrival-time-stack combination tests multi-step reasoning. Understanding that a slower car ahead blocks faster cars behind it (forming a fleet) tests physical intuition. Connecting this to pipeline dependency bottlenecks shows engineering judgment.

## DE Application

Job scheduling with dependencies: tasks have estimated completion times and can't "pass" tasks they depend on. A slow upstream task becomes the bottleneck that downstream tasks queue behind, forming a "fleet" with the upstream task's completion time.

## At Scale

Sort + stack: O(n log n) time, O(n) memory. For 10M cars, sorting takes ~3 seconds, the stack pass takes ~50ms. The sorting step dominates. At scale, car fleet is an abstraction for task scheduling with dependencies: "which tasks catch up to (are blocked by) slower tasks ahead?" In pipeline scheduling, a fast task following a slow dependency is effectively in a "fleet" with the slow task - it can't finish faster than its predecessor. Understanding this bottleneck analysis helps with pipeline optimization: the fleet count tells you how many independent execution streams exist, which is your maximum parallelism.

## Related Problems

- [853 variant: Car Fleet II](https://leetcode.com/problems/car-fleet-ii/) - When do cars collide
