# CC Prompt: Create Pattern 12 Combined Patterns (Part 3 of 4)

## What This Prompt Does

Creates problems 3-4: Top K Frequent Elements (LeetCode 347) and Network Delay Time (LeetCode 743).

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- Approach explanations must emphasize HOW patterns combine

---

## Problem 3: Top K Frequent Elements (LeetCode #347)

### `problems/p347_top_k_frequent.py`

```python
"""
LeetCode 347: Top K Frequent Elements

Combined Patterns: Hash Map + Heap
Difficulty: Medium
Time Complexity: O(n log k) - count O(n) + heap operations O(n log k)
Space Complexity: O(n) for the frequency map
"""

import heapq
from collections import Counter


def top_k_frequent(nums: list[int], k: int) -> list[int]:
    """
    Return the k most frequent elements.

    Phase 1 (Hash Map): count frequencies in O(n).
    Phase 2 (Heap): extract top-k in O(n log k).

    Using a min-heap of size k: push each element, pop if heap
    exceeds k. The heap always holds the k largest frequencies.
    """
    counts = Counter(nums)

    # Min-heap of (frequency, value). Keep only top k.
    heap: list[tuple[int, int]] = []

    for num, freq in counts.items():
        heapq.heappush(heap, (freq, num))
        if len(heap) > k:
            heapq.heappop(heap)  # remove smallest frequency

    return [num for freq, num in heap]


def top_k_frequent_bucket_sort(nums: list[int], k: int) -> list[int]:
    """
    Alternative: bucket sort approach. O(n) time.

    Since frequencies range from 1 to n, use an array of buckets
    where bucket[i] holds elements with frequency i.
    Scan from highest bucket down to collect k elements.
    """
    counts = Counter(nums)

    # Bucket: index = frequency, value = list of elements with that frequency
    buckets: list[list[int]] = [[] for _ in range(len(nums) + 1)]

    for num, freq in counts.items():
        buckets[freq].append(num)

    result: list[int] = []
    for freq in range(len(buckets) - 1, 0, -1):
        for num in buckets[freq]:
            result.append(num)
            if len(result) == k:
                return result

    return result
```

### `problems/p347_top_k_frequent_test.py`

```python
"""Tests for LeetCode 347: Top K Frequent Elements."""

import pytest

from p347_top_k_frequent import top_k_frequent, top_k_frequent_bucket_sort


@pytest.mark.parametrize("func", [top_k_frequent, top_k_frequent_bucket_sort])
class TestTopKFrequent:
    """Test both approaches."""

    def test_example_1(self, func) -> None:
        result = set(func([1, 1, 1, 2, 2, 3], 2))
        assert result == {1, 2}

    def test_example_2(self, func) -> None:
        result = func([1], 1)
        assert result == [1]

    def test_all_same(self, func) -> None:
        result = func([5, 5, 5, 5], 1)
        assert result == [5]

    def test_k_equals_unique(self, func) -> None:
        result = set(func([1, 2, 3], 3))
        assert result == {1, 2, 3}

    def test_negative_numbers(self, func) -> None:
        result = set(func([-1, -1, 2, 2, 2, 3], 2))
        assert result == {-1, 2}

    def test_large_k(self, func) -> None:
        nums = list(range(100)) + [0] * 50 + [1] * 30
        result = set(func(nums, 2))
        assert 0 in result  # 0 appears 51 times
        assert 1 in result  # 1 appears 31 times

    def test_single_element_repeated(self, func) -> None:
        result = func([1, 1, 1], 1)
        assert result == [1]
```

### `problems/347_top_k_frequent.md`

````markdown
# Top K Frequent Elements (LeetCode #347)

## Problem Statement

Given an integer array and integer k, return the k most frequent elements. The answer is guaranteed to be unique.

## Thought Process

1. **Phase 1 - Count:** Need element frequencies. Hash map (Counter) in O(n).
2. **Phase 2 - Select:** Need top k from the frequency map. A min-heap of size k does this in O(n log k). Alternative: bucket sort in O(n).
3. **Why a min-heap?** A min-heap of size k keeps the k largest items. When you push a new item and the heap exceeds k, pop the smallest. After processing all items, the heap holds the k most frequent.

## Worked Example

Two phases, two patterns. The hash map converts the "frequency" problem into a "top k" problem. The heap solves top-k efficiently. Neither pattern alone solves the problem; they compose naturally because the hash map's output (element-frequency pairs) is exactly the heap's input.

```
Input: [1, 1, 1, 2, 2, 3], k=2

Phase 1: Hash Map (Counter)
  {1: 3, 2: 2, 3: 1}
  O(n) - one pass through the array.

Phase 2: Min-Heap of size k=2
  Process (1, 3): heap = [(3, 1)]. Size 1 <= k.
  Process (2, 2): heap = [(2, 2), (3, 1)]. Size 2 <= k.
  Process (3, 1): push → heap = [(1, 3), (3, 1), (2, 2)]. Size 3 > k.
    Pop min → removes (1, 3). heap = [(2, 2), (3, 1)].

  Heap holds: [(2, 2), (3, 1)] → elements [2, 1]

  Answer: [1, 2] (order doesn't matter)

Alternative Phase 2: Bucket Sort
  buckets[3] = [1]    (element 1 appears 3 times)
  buckets[2] = [2]    (element 2 appears 2 times)
  buckets[1] = [3]    (element 3 appears 1 time)

  Scan from highest: buckets[3] → [1], buckets[2] → [2]
  Collected 2 elements = k. Done.

  O(n) total. Better than heap for this problem specifically,
  but heap is more general (works for top-k of anything).
```

## Approaches

### Approach 1: Hash Map + Min-Heap

<details>
<summary>📝 Explanation</summary>

**Pattern combination:** Hash map (Pattern 01) for O(1) frequency counting, min-heap (Pattern 05) for O(log k) top-k selection.

Count frequencies with Counter. Push (frequency, element) tuples into a min-heap. Maintain heap size at k by popping when it exceeds k. The pop removes the least frequent element, leaving the k most frequent.

Why min-heap (not max)? A min-heap of size k is O(n log k). A max-heap approach (heapify all n elements, pop k times) is O(n + k log n). For small k, the min-heap approach is faster. For k close to n, they're similar.

**Time:** O(n log k). Counter is O(n). Each of at most n heap operations is O(log k).
**Space:** O(n) for the counter, O(k) for the heap.

</details>

### Approach 2: Hash Map + Bucket Sort

<details>
<summary>📝 Explanation</summary>

**Pattern combination:** Hash map for counting, then bucket sort exploiting the fact that frequencies are bounded by n.

Create an array of n+1 buckets. Bucket[i] holds all elements with frequency i. Scan from highest bucket down, collecting elements until you have k.

This is O(n) total: O(n) counting, O(n) bucket construction, O(n) scanning. It beats the heap approach asymptotically but only works when frequencies are bounded integers.

**Time:** O(n).
**Space:** O(n) for both the counter and buckets.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| All same element, k=1 | That element | Single frequency |
| k = number of unique elements | All elements | Return everything |
| Negative numbers | Works the same | Counter handles any hashable |

## Interview Tips

> "I'll solve this in two phases: count frequencies with a hash map, then extract the top k using a min-heap of size k. The heap approach is O(n log k). If the interviewer wants O(n), I'll switch to bucket sort."

**Mention both approaches.** Starting with the heap shows pattern knowledge. Mentioning bucket sort shows optimization awareness. Let the interviewer choose which to implement.

## DE Application

Finding the most common error codes, top customers by order count, most frequent queries. The two-phase approach (count then rank) is the standard pattern for any "top N" analysis. In SQL: `GROUP BY + ORDER BY count DESC + LIMIT k`. The heap approach is what makes this efficient in streaming contexts where you can't sort.

## Related Problems

- [692. Top K Frequent Words](https://leetcode.com/problems/top-k-frequent-words/) - Same pattern with string sorting
- [215. Kth Largest Element](https://leetcode.com/problems/kth-largest-element-in-an-array/) - Pattern 05 core
````

---

## Problem 4: Network Delay Time (LeetCode #743)

### `problems/p743_network_delay.py`

```python
"""
LeetCode 743: Network Delay Time

Combined Patterns: Graph + Heap (Dijkstra's Algorithm)
Difficulty: Medium
Time Complexity: O((V + E) log V) with min-heap
Space Complexity: O(V + E) for adjacency list and distance map
"""

import heapq
from collections import defaultdict


def network_delay_time(times: list[list[int]], n: int, k: int) -> int:
    """
    Find the time for a signal to reach all nodes from source k.

    Dijkstra's algorithm: BFS with a priority queue (min-heap).
    Instead of processing nodes in FIFO order (BFS), process
    them in order of shortest distance (Dijkstra). This guarantees
    that when we first visit a node, we've found the shortest path.

    Returns -1 if not all nodes are reachable.
    """
    # Build adjacency list (graph pattern)
    graph: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))

    # Dijkstra's algorithm (heap pattern)
    dist: dict[int, int] = {}
    heap = [(0, k)]  # (distance, node)

    while heap:
        d, node = heapq.heappop(heap)

        if node in dist:
            continue  # already found shorter path

        dist[node] = d

        for neighbor, weight in graph[node]:
            if neighbor not in dist:
                heapq.heappush(heap, (d + weight, neighbor))

    if len(dist) == n:
        return max(dist.values())
    return -1


def network_delay_bellman_ford(
    times: list[list[int]], n: int, k: int
) -> int:
    """
    Alternative: Bellman-Ford algorithm.

    Simpler but slower. Relax all edges V-1 times.
    Handles negative weights (Dijkstra doesn't).
    """
    dist = [float("inf")] * (n + 1)
    dist[k] = 0

    for _ in range(n - 1):
        for u, v, w in times:
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    max_dist = max(dist[1:])
    return int(max_dist) if max_dist != float("inf") else -1
```

### `problems/p743_network_delay_test.py`

```python
"""Tests for LeetCode 743: Network Delay Time."""

import pytest

from p743_network_delay import network_delay_time, network_delay_bellman_ford


@pytest.mark.parametrize("func", [network_delay_time, network_delay_bellman_ford])
class TestNetworkDelay:
    """Test both approaches."""

    def test_example(self, func) -> None:
        times = [[2, 1, 1], [2, 3, 1], [3, 4, 1]]
        assert func(times, 4, 2) == 2

    def test_unreachable(self, func) -> None:
        times = [[1, 2, 1]]
        assert func(times, 2, 2) == -1  # node 1 unreachable from 2

    def test_single_node(self, func) -> None:
        assert func([], 1, 1) == 0

    def test_two_nodes(self, func) -> None:
        times = [[1, 2, 5]]
        assert func(times, 2, 1) == 5

    def test_multiple_paths(self, func) -> None:
        # Direct path 1→3 costs 10, path 1→2→3 costs 3
        times = [[1, 2, 1], [2, 3, 2], [1, 3, 10]]
        assert func(times, 3, 1) == 3  # shorter path through 2

    def test_all_reachable(self, func) -> None:
        times = [[1, 2, 1], [1, 3, 2], [2, 4, 3], [3, 4, 1]]
        assert func(times, 4, 1) == 3  # path 1→3→4 = 3

    def test_star_topology(self, func) -> None:
        times = [[1, 2, 1], [1, 3, 2], [1, 4, 3]]
        assert func(times, 4, 1) == 3  # max distance to any node
```

### `problems/743_network_delay.md`

````markdown
# Network Delay Time (LeetCode #743)

## Problem Statement

You are given a network of n nodes (labeled 1 to n) and a list of travel times as directed edges [u, v, w] (from u to v takes w time). Given a starting node k, find the minimum time for a signal to reach ALL nodes. Return -1 if not all nodes are reachable.

## Thought Process

1. **This is shortest path.** We need the maximum of all shortest paths from k (because the signal spreads simultaneously; the last node to receive it determines the total time).
2. **Dijkstra's algorithm:** BFS but using a priority queue (min-heap) instead of a regular queue. This processes nodes in order of increasing distance, guaranteeing that the first time we visit a node, we've found the shortest path.
3. **Pattern combination:** Build the graph as an adjacency list (graph pattern), traverse with a min-heap (heap pattern).

## Worked Example

Dijkstra's algorithm is BFS with a twist: instead of processing nodes in the order they're discovered, it processes them in order of shortest distance. The min-heap ensures we always expand the closest unvisited node. This greedy approach guarantees optimal shortest paths.

```
times = [[2,1,1], [2,3,1], [3,4,1]], n=4, k=2

Graph (adjacency list):
  2 → [(1, 1), (3, 1)]
  3 → [(4, 1)]

Dijkstra from node 2:
  heap = [(0, 2)]   dist = {}

  Pop (0, 2). 2 not in dist → dist[2] = 0.
    Push neighbors: (0+1, 1) = (1, 1), (0+1, 3) = (1, 3)
    heap = [(1, 1), (1, 3)]

  Pop (1, 1). 1 not in dist → dist[1] = 1.
    No neighbors of 1.
    heap = [(1, 3)]

  Pop (1, 3). 3 not in dist → dist[3] = 1.
    Push neighbor: (1+1, 4) = (2, 4)
    heap = [(2, 4)]

  Pop (2, 4). 4 not in dist → dist[4] = 2.
    No neighbors of 4.
    heap = []

  dist = {2: 0, 1: 1, 3: 1, 4: 2}
  All 4 nodes reached. max(dist.values()) = 2.

  Answer: 2 (node 4 is the last to receive the signal)
```

## Approaches

### Approach 1: Dijkstra's Algorithm (Graph + Heap)

<details>
<summary>📝 Explanation</summary>

**Pattern combination:** Adjacency list (graph, Pattern 06) for O(1) neighbor lookup, min-heap (Pattern 05) for processing nodes in distance order.

Build the adjacency list from the edge list. Initialize a heap with (0, source). Maintain a `dist` map of finalized shortest distances.

On each iteration: pop the node with smallest distance. If already in dist, skip (we found a shorter path earlier). Otherwise, record its distance and push all neighbors with updated distances.

The `if node in dist: continue` check is critical: the heap may contain multiple entries for the same node (from different paths). We only process the first (shortest) one.

**Time:** O((V + E) log V). Each node is popped from the heap once: O(V log V). Each edge creates one heap push: O(E log V).
**Space:** O(V + E) for the adjacency list and distance map.

Dijkstra's doesn't work with negative weights. For that, use Bellman-Ford (O(V * E), simpler but slower).

</details>

### Approach 2: Bellman-Ford

<details>
<summary>📝 Explanation</summary>

Initialize all distances to infinity except the source (0). Repeat V-1 times: for each edge (u, v, w), if dist[u] + w < dist[v], update dist[v].

Simpler than Dijkstra (no heap, no adjacency list needed) but slower: O(V * E). Handles negative weights. Useful as a fallback or when the graph is dense.

**Time:** O(V * E).
**Space:** O(V) for the distance array.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| Single node, no edges | 0 | Signal already at source |
| Unreachable node | -1 | Not all nodes can be reached |
| Multiple paths to same node | Shortest distance | Heap handles path selection |
| Self-loop | Ignored | dist check skips re-processing |

## Interview Tips

> "This is a shortest path problem. I'll use Dijkstra's algorithm: build an adjacency list, then BFS with a min-heap. The heap ensures I process nodes in distance order. The answer is the maximum shortest distance to any node."

**Key follow-up:** "When would you use Bellman-Ford instead?" → Negative edge weights, or when the graph representation doesn't easily support adjacency lists.

## DE Application

Pipeline dependency analysis with execution times. "If I trigger a full refresh of the raw_orders table, how long until the executive dashboard is updated?" Model the pipeline as a weighted graph where edge weights are task execution times. Dijkstra (or simply critical path analysis) gives the answer. The max distance from source to any target is the total pipeline execution time.

## Related Problems

- [787. Cheapest Flights Within K Stops](https://leetcode.com/problems/cheapest-flights-within-k-stops/) - Dijkstra with constraint
- [1514. Path with Maximum Probability](https://leetcode.com/problems/path-with-maximum-probability/) - Max-heap variant
````

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Tests ==="
uv run pytest patterns/12_combined_patterns/problems/ -v --tb=short 2>&1 | tail -20

echo ""
echo "=== Worked Examples start with prose ==="
for f in patterns/12_combined_patterns/problems/347_top_k_frequent.md patterns/12_combined_patterns/problems/743_network_delay.md; do
    first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' "$f")
    echo "$(basename $f): $first" | head -c 80
    echo ""
done
```
