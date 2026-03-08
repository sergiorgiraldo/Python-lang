# Task Scheduler (LeetCode #621)

🔗 [LeetCode 621: Task Scheduler](https://leetcode.com/problems/task-scheduler/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Given a list of tasks (represented by characters) and a cooldown period n, find the minimum number of intervals needed to execute all tasks. Between two executions of the same task, there must be at least n intervals.

## Thought Process

1. **The bottleneck:** The most frequent task determines the minimum time. If task A appears 3 times and cooldown is 2, A alone needs at least 7 intervals: A _ _ A _ _ A.
2. **Greedy insight:** Always run the most frequent available task. This fills cooldown gaps with useful work instead of idle time.
3. **Two approaches:** Simulate with a heap (pick most frequent each step) or calculate directly with math (the frame formula).

## Worked Example

The math approach reveals the structure. The most frequent task creates a "frame" of (max_freq - 1) chunks, each of size (n + 1). Other tasks slot into the gaps. If there are enough tasks to fill every gap, no idle time is needed and the answer is just the total task count.

```
Tasks: [A, A, A, B, B, B], n=2

Frequencies: A=3, B=3. max_freq=3, count_of_max=2.

Frame built around max_freq task(s):
  Chunk 1: A B _     (size n+1 = 3)
  Chunk 2: A B _     (size n+1 = 3)
  Final:   A B       (only tasks at max_freq)

  Total: (3-1) * 3 + 2 = 8

Simulation (heap approach):
  t=1: heap=[-3,-3]. Pop A(3->2). cooldown=[(4,-2)]. Run A.
  t=2: heap=[-3]. Pop B(3->2). cooldown=[(4,-2),(5,-2)]. Run B.
  t=3: heap empty, cooldown not ready. IDLE.
  t=4: A returns to heap. Pop A(2->1). Run A.
  t=5: B returns to heap. Pop B(2->1). Run B.
  t=6: heap empty. IDLE.
  t=7: A returns. Pop A(1->0). Run A.
  t=8: B returns. Pop B(1->0). Run B.

  Schedule: A B _ A B _ A B -> 8 intervals.
```

## Approaches

### Approach 1: Heap Simulation

<details>
<summary>📝 Explanation</summary>

**Pattern combination:** Hash map counts frequencies (Phase 1). Max-heap greedily selects the most frequent available task each interval (Phase 2). A cooldown queue tracks when tasks become available again.

Count frequencies with Counter. Build a max-heap of counts (negate for Python's min-heap). Each interval: if the cooldown queue's front task is ready, push it back to the heap. Pop the heap for the most frequent task. Decrement its count. If count remains, add to cooldown queue with its next available time.

The greedy choice (most frequent first) is optimal because it minimizes idle time. The most frequent task is the hardest to schedule, so handling it first gives the most flexibility for remaining tasks.

**Time:** O(n * 26) in the worst case. Each of n tasks is processed once, and heap operations are O(log 26) = O(1) since there are at most 26 task types.
**Space:** O(26) = O(1) for the heap and cooldown queue.

</details>

### Approach 2: Math Formula

<details>
<summary>📝 Explanation</summary>

**Pattern combination:** Hash map counts frequencies. Math computes the answer directly from the frequency distribution.

The most frequent task creates a frame: (max_freq - 1) chunks of (n + 1) slots each, plus a final partial chunk containing all tasks tied at max frequency. Any remaining tasks fit into the gaps within chunks.

Formula: max((max_freq - 1) * (n + 1) + count_of_max_freq, len(tasks))

The max with len(tasks) handles the case where there are so many different task types that all cooldown gaps are filled with useful work and no idle time is needed. In that case, the answer is simply the number of tasks.

**Time:** O(n) to count frequencies, O(1) to compute.
**Space:** O(1) - 26 possible task types.

This approach is elegant but less intuitive. The heap simulation is better for interviews because it's easier to explain step by step.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| Single task, n=0 | 1 | No cooldown, just run it |
| All same task, n=0 | len(tasks) | No cooldown, run sequentially |
| All different tasks | len(tasks) | Never need idle (each task runs once) |
| n larger than unique task count | Idle intervals required | Not enough different tasks to fill gaps |

## Interview Tips

> "The most frequent task is the bottleneck. I'll count frequencies with a hash map, then use a max-heap to greedily schedule the most frequent available task each interval. A cooldown queue tracks when tasks become available. Alternatively, there's a math formula based on the frame structure."

**Mention both approaches.** Start with the heap (demonstrates the pattern combination), then mention the math formula (shows deeper understanding).

**What the interviewer evaluates:** Recognizing the frequency counting + greedy scheduling decomposition tests pattern composition. Starting with the heap simulation (shows the process) and then mentioning the math formula (shows deeper understanding) is the ideal progression. The interviewer may ask "what if tasks have different durations?" - this breaks the math formula and requires the simulation approach. Handling follow-ups that invalidate your elegant solution gracefully shows maturity.

## DE Application

Pipeline task scheduling with resource constraints. If a transformation writes to a shared table, it needs a cooldown before the next write to avoid lock contention. Scheduling the most resource-intensive tasks first with appropriate spacing is the same greedy approach.

## At Scale

The counting phase processes all n tasks: O(n). For 1B tasks with 26 task types, the Counter uses ~2KB. The math formula computes the answer in O(1) after counting. At scale, task scheduling with cooldowns is a real production problem: Airflow's scheduler spaces out tasks that write to the same table to avoid lock contention. The greedy "most frequent first" strategy minimizes idle time. In distributed scheduling, the challenge is that the global view (all task frequencies) must be maintained centrally while execution happens across workers. Spark's task scheduler uses a similar priority queue internally, though the optimization target is data locality rather than cooldown constraints.

## Related Problems

- [358. Rearrange String k Distance Apart](https://leetcode.com/problems/rearrange-string-k-distance-apart/) - Same pattern, string output
- [767. Reorganize String](https://leetcode.com/problems/reorganize-string/) - Simplified version (k=2)
