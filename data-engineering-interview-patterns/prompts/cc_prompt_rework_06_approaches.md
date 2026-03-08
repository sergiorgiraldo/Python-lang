# CC Prompt: Rework Approach Explanations - Pattern 06 Graph

## What This Prompt Does

Rewrites every `📝 Explanation` block in all 7 problem files.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Replace content inside `<details>` blocks containing `📝 Explanation` only.
- Leave `💡 Hint` and `💻 Code` blocks untouched.
- NO Oxford commas, NO em dashes, NO exclamation points

---

### 200_number_of_islands.md - BFS approach

```
Scan the grid cell by cell. When you find an unvisited '1' (land), that's a new island. Start BFS from that cell: add it to a queue, mark it visited, then process the queue by checking all four neighbors (up/down/left/right). Any neighbor that's '1' and unvisited gets added to the queue and marked visited. When the queue empties, you've marked the entire island.

Continue scanning. The next unvisited '1' starts another island. Cells already visited (from earlier BFS runs) are skipped.

**Time:** O(m × n) - every cell visited at most once during scanning, at most once during BFS. Total work proportional to grid size.
**Space:** O(m × n) - the visited set. The BFS queue holds at most O(min(m, n)) entries (the diagonal of the grid).

DFS works identically - just use a stack instead of a queue (or use recursion). The choice doesn't affect correctness or complexity, only visit order.
```

### 200_number_of_islands.md - DFS approach

```
Same logic as BFS but uses a stack (or recursion). When you find an unvisited '1', explore as deep as possible in one direction before backtracking. Mark each cell visited as you go.

Recursive DFS is the most concise implementation: call dfs(row, col), which marks the cell visited and recursively calls itself on all valid unvisited neighbors.

**Time:** O(m × n). **Space:** O(m × n) for visited set plus O(m × n) worst-case recursion depth (a grid that's all '1's).

Watch for recursion depth limits on large grids. Python's default recursion limit is 1000. For grids larger than ~30×30, use iterative DFS or BFS.
```

### 547_number_of_provinces.md - BFS/DFS approach

```
Same connected-component counting as Number of Islands, but the input is an adjacency matrix instead of a grid. For each unvisited city, start BFS/DFS and mark all reachable cities as visited. Each time you start a new traversal, that's a new province.

The adjacency matrix tells you neighbors directly: city j is a neighbor of city i if `isConnected[i][j] == 1`.

**Time:** O(n²) - checking the adjacency matrix for each city's neighbors is O(n), and we do this for each of n cities.
**Space:** O(n) - visited set and queue/stack.
```

### 133_clone_graph.md - BFS approach

```
BFS through the original graph. Maintain a dict mapping original nodes to their clones. When visiting a node:
1. For each neighbor of the original node, check if it's in the dict (already cloned).
2. If not, create a clone and add the mapping.
3. Connect the current clone to the neighbor's clone.

The dict serves two purposes: it tracks visited nodes (preventing infinite loops on cycles) and stores the clone references (so we can wire up connections).

**Time:** O(V + E) - visit every node and edge once.
**Space:** O(V) - the clone map holds one entry per node.

The DFS version is the same logic with a stack or recursion instead of a queue.
```

### 207_course_schedule.md - Cycle Detection (Kahn's BFS)

```
Model courses as a directed graph: an edge from A to B means "A is a prerequisite for B." If there's a cycle, some courses can never be taken (each one requires another in the cycle to be completed first).

Kahn's algorithm detects cycles as a side effect of topological sort:
1. Compute in-degree (number of prerequisites) for each course.
2. Add all courses with in-degree 0 to a queue (no prerequisites).
3. Process the queue: for each course, decrement the in-degree of all courses that depend on it. If any drops to 0, add it to the queue.
4. Count how many courses were processed. If count == numCourses, no cycle exists (all courses are completable). If count < numCourses, there's a cycle.

**Time:** O(V + E) where V = number of courses and E = number of prerequisite pairs.
**Space:** O(V + E) for the graph and in-degree array.
```

### 207_course_schedule.md - DFS 3-State Coloring

```
DFS with three states per node: UNVISITED, IN_PROGRESS, COMPLETED.

Start DFS from each unvisited node. When entering a node, mark it IN_PROGRESS. Visit all its neighbors recursively. When all neighbors are done, mark it COMPLETED.

If we ever reach a node that's IN_PROGRESS, we've found a back edge (a cycle). We followed a path from that node and arrived back at it.

**Time:** O(V + E). **Space:** O(V) for the state array plus recursion stack.

The three states are critical. Two-state (visited/unvisited) doesn't distinguish between "I'm currently exploring this path" and "I finished exploring this node earlier from a different starting point."
```

### 210_course_schedule_ii.md - Topological Sort (Kahn's)

```
Identical to Course Schedule (207) but instead of returning True/False, return the processing order. The order in which nodes are dequeued from Kahn's algorithm IS the topological sort.

1. Build the graph and compute in-degrees.
2. Initialize queue with all in-degree-0 nodes.
3. Process queue, appending each node to the result list.
4. If result length == numCourses, return result. Otherwise return [] (cycle exists).

**Time:** O(V + E). **Space:** O(V + E).

Multiple valid orderings may exist when several nodes have in-degree 0 simultaneously. Any valid topological order is acceptable.
```

### 269_alien_dictionary.md - Topological Sort from Ordering Rules

```
Two-phase approach:

**Phase 1 - Extract ordering rules:** Compare each pair of adjacent words in the list. Find the first character position where they differ. That gives one ordering rule: `word1[pos] < word2[pos]` in the alien alphabet. If word1 is a prefix of word2, no rule is extracted. If word2 is a prefix of word1, the input is invalid (a shorter word can't come after its own prefix in a sorted list).

**Phase 2 - Topological sort:** Build a directed graph from the extracted rules. Run Kahn's algorithm. The result is the alien character order.

Edge cases: if topological sort detects a cycle, the ordering rules are contradictory. Return "". If some characters appear in words but have no ordering constraints relative to each other, they can appear in any position (multiple valid orderings exist).

**Time:** O(C) where C is the total length of all words (for extracting rules) plus O(V + E) for topological sort where V = unique characters and E = rules.
**Space:** O(V + E).
```

### 743_network_delay_time.md - Dijkstra's Algorithm

```
Dijkstra finds the shortest weighted path from a source to all other nodes. It's BFS with a priority queue (min-heap) instead of a regular queue. Always process the node with the smallest known distance next. Once a node is processed, its distance is final.

1. Initialize distances: source = 0, all others = infinity.
2. Push (0, source) onto the min-heap.
3. Pop the minimum. If we've already finalized this node, skip it. Otherwise, for each neighbor, check if `current_dist + edge_weight < known_dist[neighbor]`. If so, update and push the new distance.
4. After the heap is empty, all reachable nodes have final distances. The answer (time for signal to reach all nodes) is the maximum distance. If any node is still infinity, return -1 (unreachable).

**Time:** O(E log V) - each edge causes at most one heap operation.
**Space:** O(V + E) for the graph and heap.

Important: Dijkstra only works with non-negative edge weights. Negative weights require Bellman-Ford (rarely asked in interviews).
```

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns
git diff --name-only | grep -v '.md$'
uv run pytest patterns/06_graph_topological_sort/ -v --tb=short 2>&1 | tail -3

for f in patterns/06_graph_topological_sort/problems/*.md; do
    name=$(basename "$f")
    awk '/📝 Explanation/{found=1; lines=0; next} found && /<\/details>/{if(lines<4) printf "❌ %s: %d lines\n", "'"$name"'", lines; found=0} found && /\S/{lines++}' "$f"
done
echo "(no output = all substantial)"
```
