# DE Scenario: Binary Search on Answer - Resource Allocation

**Run it:** `uv run python -m patterns.03_binary_search.de_scenarios.search_on_answer`

## Real-World Context

You're planning a batch processing job. You know the workload (N records across M tables) and the deadline (must finish in H hours). How many workers do you need?

Each additional worker costs money. Too few and you miss the deadline. Too many and you waste budget. The optimal answer is the minimum number of workers that finishes on time.

This is "binary search on answer" - the same pattern as [LeetCode #875 (Koko Eating Bananas)](../../problems/875_koko_bananas.md).

## The Problem

Given a list of tasks with their processing times and a deadline, find the minimum number of parallel workers to finish everything on time.

## Why Binary Search

The feasibility check is monotonic: if K workers can finish in time, K+1 workers can too. That means binary search works over the range [1, len(tasks)].

The brute force approach (try 1 worker, 2 workers, ...) has the same O(n) feasibility check per candidate but tries every value linearly. Binary search reduces the number of candidates from max_workers to log(max_workers).

## Production Considerations

**Feasibility check complexity matters.** The binary search itself is O(log W) iterations where W is the max workers. But each feasibility check might involve simulating the schedule, which could be O(n log n) for a greedy assignment. Total complexity is O(n log n * log W).

**Discrete vs continuous.** Workers are integers. Binary search naturally handles this since we're searching over integers. For continuous resource allocation (memory, CPU percentage), you'd need to decide on a precision and search over that grid.

**Non-uniform tasks.** If tasks have wildly different sizes, the greedy assignment (assign each task to the worker with the earliest finish time) is optimal. This is equivalent to a min-heap scheduling simulation.

## Worked Example

"Binary search on the answer" applied to a real DE problem: finding the minimum number of workers needed to process a batch within a time budget. Same pattern as Koko Eating Bananas - the answer is a number in a range and we check feasibility for each candidate.

```
Problem: 1000 tasks, each taking between 1 and 60 minutes.
         Total work: 28,500 task-minutes.
         Deadline: 120 minutes.
         Each worker processes tasks sequentially.
         Minimize the number of workers.

  Min workers = 1 (if 28,500 min <= 120 min... no, that's too slow)
  Max workers = 1000 (one per task, guaranteed to finish)

  Binary search on [1, 1000]:

  mid=500: Assign tasks greedily. Each worker gets tasks until their
    total >= 120 min. Needs 245 workers. 245 <= 500 → works. Try fewer.
    right = 500.

  mid=250: Needs 245 workers. 245 <= 250 → works. right = 250.

  mid=125: Needs 245 workers. 245 > 125 → doesn't work. left = 126.

  mid=188: Needs 245 workers. 245 > 188 → doesn't work. left = 189.

  mid=219: Needs 245. 245 > 219 → left = 220.

  mid=235: Needs 245. left = 236.

  mid=243: 245 > 243 → left = 244.

  mid=246: Needs 245. 245 <= 246 → right = 246.

  mid=245: Needs 245. 245 <= 245 → right = 245.

  left=244... converges to 245 workers.

  ~10 binary search steps, each doing O(n) greedy assignment.
  Brute force: try 1, 2, 3, ..., up to 245 workers = 245 feasibility checks.
```

## Connection to LeetCode

This is [875. Koko Eating Bananas](../../problems/875_koko_bananas.md) in a data engineering context. Piles = tasks, eating speed = workers, hours = deadline.

## Benchmark

See the `.py` file for comparisons across different task counts and deadlines.
