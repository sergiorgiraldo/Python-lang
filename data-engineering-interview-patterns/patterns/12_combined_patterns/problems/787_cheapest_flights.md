# Cheapest Flights Within K Stops (LeetCode #787)

🔗 [LeetCode 787: Cheapest Flights Within K Stops](https://leetcode.com/problems/cheapest-flights-within-k-stops/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Given n cities, a list of flights [from, to, price], a source, destination and maximum number of stops k, find the cheapest price. Return -1 if no such route exists.

## Thought Process

1. **Why not standard Dijkstra?** Dijkstra finds the globally shortest path, but here a shorter path might exceed k stops. We need to consider paths that are more expensive but use fewer stops.
2. **Bellman-Ford fits naturally:** Bellman-Ford relaxes all edges in rounds. After round i, we have the cheapest prices using at most i edges. After k+1 rounds, we have the answer for at most k stops.
3. **Modified Dijkstra also works:** Track stops alongside cost. Allow revisiting nodes if we arrive with fewer stops (a more expensive but shorter path might lead to a cheaper final route).

## Worked Example

Bellman-Ford processes edges in rounds. Each round extends paths by one hop. After k+1 rounds, every node's price reflects the cheapest reachable cost using at most k intermediate stops. The copy-before-update trick prevents using paths discovered within the same round (which would allow extra stops).

```
n=3, flights=[[0,1,100], [1,2,100], [0,2,500]], src=0, dst=2, k=1

Initial prices: [0, inf, inf]

Round 1 (at most 1 edge = 0 stops):
  Edge 0->1: prices[0]+100=100 < inf -> temp[1]=100
  Edge 1->2: prices[1]=inf, skip
  Edge 0->2: prices[0]+500=500 < inf -> temp[2]=500
  prices = [0, 100, 500]

Round 2 (at most 2 edges = 1 stop):
  Edge 0->1: 0+100=100, temp[1] already 100, no change
  Edge 1->2: prices[1]=100, 100+100=200 < 500 -> temp[2]=200
  Edge 0->2: 0+500=500 > 200, no change
  prices = [0, 100, 200]

Answer: prices[2] = 200 (route 0->1->2, 1 stop)

If k=0 (0 stops allowed, meaning direct flights only):
  After round 1: prices = [0, 100, 500]
  Answer: 500 (direct route 0->2)
```

## Approaches

### Approach 1: Bellman-Ford Variant

<details>
<summary>📝 Explanation</summary>

**Pattern combination:** Graph representation (edge list) + iterative relaxation with a constraint (max rounds = k+1).

Initialize distances to infinity except source (0). Run k+1 rounds. Each round: copy the current prices array, then for each edge (u, v, w), if prices[u] + w < temp[v], update temp[v]. After the round, replace prices with temp.

The copy is critical: without it, updates within a round could chain together, effectively allowing more stops than intended. By reading from the old prices and writing to temp, each round extends paths by exactly one edge.

**Time:** O(K * E) where K is max stops and E is number of flights.
**Space:** O(V) for the prices array.

This is simpler and more robust than modified Dijkstra. It naturally handles the stop constraint without special tracking.

</details>

### Approach 2: Modified Dijkstra

<details>
<summary>📝 Explanation</summary>

**Pattern combination:** Graph adjacency list (hash map) + priority queue (heap) with an additional dimension (stops).

Build an adjacency list. Push (0, src, 0) to a min-heap. Pop the cheapest entry. If it's the destination, return cost. If stops exceed k, skip. Track the best (fewest) stops to reach each node; skip if we've already visited with fewer stops. Push all neighbors with incremented stops.

The key difference from standard Dijkstra: we track stops per visit and allow revisiting nodes with different stop counts. Standard Dijkstra would skip a node once visited, but here a more expensive path with fewer stops might lead to a cheaper result when the stop constraint matters.

**Time:** O(V * K * log(V * K)) in the worst case.
**Space:** O(V * K) for the heap entries.

More complex to implement correctly but can be faster in practice due to early termination when the destination is reached.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| src == dst | 0 | Already there |
| No route within k stops | -1 | Constraint makes route impossible |
| k=0 | Direct flight price or -1 | Only non-stop flights allowed |
| Multiple routes, different costs and stops | Cheapest within limit | Must compare cost-vs-stops tradeoff |

## Interview Tips

> "Standard Dijkstra doesn't work here because it ignores the stop constraint. I'll use a Bellman-Ford variant: relax all edges K+1 times. After round i, I have the cheapest prices reachable in at most i hops. The copy-before-update prevents using paths from the same round."

**Key insight to mention:** Why the copy matters. Without it, edge 0->1->2 could be processed in a single round, effectively using 2 edges (1 stop) even in round 1 (which should only allow 1 edge, 0 stops).

**What the interviewer evaluates:** Recognizing that standard Dijkstra fails (and explaining WHY - it doesn't track hop count) is the first hurdle. Choosing Bellman-Ford over modified Dijkstra shows judgment: Bellman-Ford is simpler and more robust for this variant. Explaining the copy-per-round trick (preventing same-round chaining) is the implementation detail that separates correct from incorrect solutions. The follow-up "what about negative edge weights?" (answer: Bellman-Ford already handles them) shows algorithmic breadth.

## DE Application

Pipeline routing with constraints. "Find the cheapest cloud region path for data replication, but the data can traverse at most 2 intermediate regions." Same structure: weighted graph, shortest path, hop limit.

## At Scale

Bellman-Ford variant runs O(K * E) where K is the stop limit. For a network with 10K nodes and 100K edges with K=5, that's 500K edge relaxations - milliseconds. For larger graphs (1M nodes, 10M edges), it's still fast because K is usually small. The copy-per-round technique uses O(V) memory per round. At scale, constrained shortest path is a real routing problem: "transfer data through at most 3 intermediate regions to minimize latency and cost." Cloud network routing (selecting the cheapest path between data centers with hop limits) uses similar algorithms. The distributed version partitions the graph and uses iterative message passing (Pregel model), with each superstep corresponding to one Bellman-Ford round.

## Related Problems

- [743. Network Delay Time](https://leetcode.com/problems/network-delay-time/) - Standard Dijkstra (no hop limit)
- [1334. Find the City With Smallest Number of Neighbors](https://leetcode.com/problems/find-the-city-with-the-smallest-number-of-neighbors-at-a-threshold-distance/) - Distance threshold variant
