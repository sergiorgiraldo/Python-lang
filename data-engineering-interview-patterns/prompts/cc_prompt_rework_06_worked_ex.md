# CC Prompt: Rework Worked Examples - Pattern 06 Graph

## What This Prompt Does

Rewrites `## Worked Example` in all 7 problem files and 4 DE scenario files.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Only modify `.md` files. REPLACE `## Worked Example` sections only.
- NO Oxford commas, NO em dashes, NO exclamation points

---

### 200_number_of_islands.md

```markdown
## Worked Example

A grid of '1's (land) and '0's (water). Each connected group of land cells is an island. We count islands by scanning the grid. When we find an unvisited '1', that's a new island. We BFS/DFS from that cell to mark all connected land as visited. Each new unvisited '1' we encounter in the scan starts another island.

```
Input grid:
  1 1 0 0 1
  1 0 0 0 0
  0 0 1 1 0
  0 0 0 1 0

Scan left-to-right, top-to-bottom:
  (0,0)='1' unvisited → NEW ISLAND #1
    BFS: visit (0,0)→(0,1)→(1,0). All connected land marked.
  (0,1)='1' already visited → skip
  (0,2)='0' → skip
  (0,3)='0' → skip
  (0,4)='1' unvisited → NEW ISLAND #2
    BFS: visit (0,4). No connected land neighbors.
  (1,0)='1' already visited → skip
  ...
  (2,2)='1' unvisited → NEW ISLAND #3
    BFS: visit (2,2)→(2,3)→(3,3). All connected land marked.
  ...scan remaining, all visited or water.

Answer: 3 islands.
Each cell visited at most once during BFS + once during scan = O(m×n).
```
```

### 547_number_of_provinces.md

```markdown
## Worked Example

Same concept as Number of Islands but with an adjacency matrix instead of a grid. Each row/column represents a city. `isConnected[i][j]=1` means cities i and j are directly connected. A "province" is a connected component - a group of cities reachable from each other.

```
Input (adjacency matrix):
  [[1,1,0,0,0],
   [1,1,1,0,0],
   [0,1,1,0,0],
   [0,0,0,1,1],
   [0,0,0,1,1]]

Cities: 0,1,2,3,4

  City 0: unvisited → NEW PROVINCE #1
    BFS from 0: neighbors = {1}. From 1: neighbors = {0,2}. From 2: neighbors = {1}.
    Visited: {0, 1, 2}

  City 1: already visited → skip
  City 2: already visited → skip

  City 3: unvisited → NEW PROVINCE #2
    BFS from 3: neighbors = {4}. From 4: neighbors = {3}.
    Visited: {0, 1, 2, 3, 4}

  City 4: already visited → skip

Answer: 2 provinces. Province 1: {0,1,2}. Province 2: {3,4}.
```
```

### 133_clone_graph.md

```markdown
## Worked Example

Deep-copy a graph: create new node objects with the same connections. The tricky part is handling cycles and shared references. A dict maps original nodes to their clones. When we encounter a node we've already cloned, we reuse the existing clone instead of creating a duplicate.

```
Original graph:
  1 -- 2
  |    |
  4 -- 3

BFS clone:
  Start at node 1. Create clone of 1. Map: {1: clone_1}
  Queue: [1]

  Process 1: neighbors = [2, 4]
    Node 2: not cloned yet → create clone_2. Map: {1:c1, 2:c2}. Queue: [2]
    Connect clone_1 ↔ clone_2.
    Node 4: not cloned yet → create clone_4. Map: {1:c1, 2:c2, 4:c4}. Queue: [2, 4]
    Connect clone_1 ↔ clone_4.

  Process 2: neighbors = [1, 3]
    Node 1: already cloned → reuse clone_1. Connect clone_2 ↔ clone_1.
    Node 3: not cloned → create clone_3. Queue: [4, 3]
    Connect clone_2 ↔ clone_3.

  Process 4: neighbors = [1, 3]
    Both already cloned → connect clone_4 ↔ clone_1 and clone_4 ↔ clone_3.

  Process 3: neighbors = [2, 4]
    Both already cloned → connections already exist.

Result: complete deep copy. No shared references with original.
The dict prevents infinite loops on cycles and ensures each node is cloned exactly once.
```
```

### 207_course_schedule.md

```markdown
## Worked Example

Can you finish all courses given their prerequisites? This is cycle detection in a directed graph. If there's a cycle (Course A requires B, B requires C, C requires A), it's impossible.

```
Input: numCourses=6, prerequisites=[[1,0],[2,1],[3,2],[4,1],[5,3],[5,4]]
  Meaning: to take course 1, you need course 0 first. Etc.

Graph (edges point from prerequisite to dependent):
  0 → 1 → 2 → 3 → 5
       ↓       ↗
       4 ------

Kahn's algorithm (BFS topological sort):
  In-degrees: 0:0, 1:1, 2:1, 3:1, 4:1, 5:2
  Queue (in-degree 0): [0]

  Process 0: decrement 1's in-degree → 0. Add 1 to queue. Processed: [0]
  Process 1: decrement 2→0, 4→0. Queue: [2, 4]. Processed: [0, 1]
  Process 2: decrement 3→0. Queue: [4, 3]. Processed: [0, 1, 2]
  Process 4: decrement 5→1. Processed: [0, 1, 2, 4]
  Process 3: decrement 5→0. Queue: [5]. Processed: [0, 1, 2, 4, 3]
  Process 5: Processed: [0, 1, 2, 4, 3, 5]

  Processed 6 courses = numCourses → return True (all courses completable).

If there were a cycle, some nodes would never reach in-degree 0.
Processed count < numCourses → return False.
```
```

### 210_course_schedule_ii.md

```markdown
## Worked Example

Same as Course Schedule but return the actual ordering instead of just True/False. The processed order from Kahn's algorithm IS the topological sort.

```
Input: numCourses=4, prerequisites=[[1,0],[2,0],[3,1],[3,2]]

Graph: 0 → 1 → 3
       0 → 2 → 3

  In-degrees: 0:0, 1:1, 2:1, 3:2
  Queue: [0]

  Process 0: 1→0, 2→0. Queue: [1, 2]. Order: [0]
  Process 1: 3→1. Order: [0, 1]
  Process 2: 3→0. Queue: [3]. Order: [0, 1, 2]
  Process 3: Order: [0, 1, 2, 3]

  Return [0, 1, 2, 3]. (Also valid: [0, 2, 1, 3] - multiple valid orderings exist.)
  If cycle detected: return [].
```
```

### 269_alien_dictionary.md

```markdown
## Worked Example

Given a sorted list of words in an alien language, infer the character ordering. Compare adjacent words to find ordering rules (which character comes before which), then topological sort those rules.

```
Input: words = ["wrt", "wrf", "er", "ett", "rftt"]

Step 1 - Extract ordering rules by comparing adjacent words:
  "wrt" vs "wrf": first difference at index 2 → t < f (t comes before f)
  "wrf" vs "er":  first difference at index 0 → w < e
  "er" vs "ett":  first difference at index 1 → r < t
  "ett" vs "rftt": first difference at index 0 → e < r

  Rules: t→f, w→e, r→t, e→r

Step 2 - Topological sort:
  Graph: w→e→r→t→f
  In-degrees: w:0, e:1, r:1, t:1, f:1
  Queue: [w]

  Process w→e drops to 0. Process e→r drops to 0.
  Process r→t drops to 0. Process t→f drops to 0.

  Order: w, e, r, t, f

Edge case: if "abc" comes before "ab" in the word list, that's
invalid (a longer prefix can't come before a shorter one). Return "".
```
```

### 743_network_delay_time.md

```markdown
## Worked Example

Shortest path with weighted edges. Dijkstra's algorithm uses a min-heap: always process the node with the smallest known distance. When we process a node, its distance is finalized (can't be improved).

```
Input: times=[[1,2,1],[1,3,4],[2,3,2],[3,4,1]], n=4, k=1
  (edge from node 1 to 2 costs 1, etc.)

Graph:
  1 --(1)--> 2 --(2)--> 3 --(1)--> 4
  1 --(4)--> 3

Dijkstra from node 1:
  dist = {1:0, 2:inf, 3:inf, 4:inf}
  heap = [(0, node1)]

  Pop (0, 1): process neighbors
    2: dist[2] = min(inf, 0+1) = 1. Push (1, 2).
    3: dist[3] = min(inf, 0+4) = 4. Push (4, 3).

  Pop (1, 2): process neighbors
    3: dist[3] = min(4, 1+2) = 3. Push (3, 3). (shorter path found)

  Pop (3, 3): process neighbors
    4: dist[4] = min(inf, 3+1) = 4. Push (4, 4).

  Pop (4, 3): already processed at distance 3. Skip.
  Pop (4, 4): process. No outgoing edges.

  Final distances: {1:0, 2:1, 3:3, 4:4}
  All nodes reachable. Max distance = 4. Answer: 4.

The key: the path 1→2→3 (cost 3) is shorter than 1→3 (cost 4).
The heap ensures we discover this shorter path first.
```
```

---

## DE Scenarios

### de_scenarios/pipeline_execution_order.md

```markdown
## Worked Example

Determining the execution order of pipeline tasks with dependencies. This is a direct application of topological sort (Kahn's algorithm).

```
Pipeline tasks and dependencies:
  extract_users → transform_users → load_users
  extract_orders → transform_orders → load_orders
  transform_users → build_user_orders (needs both)
  transform_orders → build_user_orders
  build_user_orders → export_report

Topological sort:
  In-degree 0: [extract_users, extract_orders] → run in parallel
  After completion: [transform_users, transform_orders] → run in parallel
  After both transforms: [load_users, load_orders, build_user_orders]
    load_users and load_orders can run in parallel with build_user_orders
  After build_user_orders: [export_report]

Execution waves:
  Wave 1: extract_users, extract_orders (parallel)
  Wave 2: transform_users, transform_orders (parallel)
  Wave 3: load_users, load_orders, build_user_orders
  Wave 4: export_report

Same algorithm Airflow uses to schedule DAG tasks.
```
```

### de_scenarios/dependency_resolution.md

```markdown
## Worked Example

Installing packages in the right order. If package A depends on B, B must be installed first. Topological sort over the dependency graph.

```
Dependencies:
  pandas → numpy, python-dateutil
  scikit-learn → numpy, scipy
  scipy → numpy
  python-dateutil → six

Graph (arrows mean "depends on"):
  pandas → numpy, python-dateutil → six
  scikit-learn → numpy, scipy → numpy

Topological sort:
  In-degree 0: [numpy, six] → install first
  After: python-dateutil→0, scipy→0 → install next
  After: pandas→0, scikit-learn→0 → install last

Install order: numpy, six, python-dateutil, scipy, pandas, scikit-learn

If there's a circular dependency (A needs B, B needs A),
topological sort detects it: not all packages reach in-degree 0.
```
```

### de_scenarios/impact_analysis.md

```markdown
## Worked Example

"If I change table X, what downstream tables/reports break?" BFS from the changed node, following dependency edges forward. Every reachable node is impacted.

```
Table lineage graph:
  raw_events → clean_events → daily_aggregates → executive_dashboard
                            → hourly_metrics → alerts_pipeline
               user_dim → daily_aggregates

Question: what breaks if raw_events schema changes?

BFS from raw_events:
  Level 1 (direct dependents): [clean_events]
  Level 2: [daily_aggregates, hourly_metrics]
  Level 3: [executive_dashboard, alerts_pipeline]

Impact: 5 downstream objects affected.
user_dim is NOT impacted (no path from raw_events to user_dim).

The level information is useful: level 1 impacts are immediate,
level 3 impacts might not surface until later pipeline stages.
```
```

### de_scenarios/cycle_detection.md

```markdown
## Worked Example

Detecting circular dependencies in a pipeline DAG. If task A depends on B, B depends on C, and C depends on A, the pipeline can never execute.

```
Tasks and dependencies:
  ingest → clean → validate → publish
  validate → audit
  audit → clean  ← THIS CREATES A CYCLE

DFS with three-state coloring:
  Start at ingest (WHITE → GRAY)
    Visit clean (WHITE → GRAY)
      Visit validate (WHITE → GRAY)
        Visit publish (WHITE → GRAY → BLACK, leaf node)
        Visit audit (WHITE → GRAY)
          Visit clean → GRAY (already in progress)
          *** CYCLE DETECTED: clean → validate → audit → clean ***

Report: circular dependency involving [clean, validate, audit].
Pipeline cannot execute until this cycle is broken.
```
```

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns
git diff --name-only | grep -v '.md$'
uv run pytest patterns/06_graph_topological_sort/ -v --tb=short 2>&1 | tail -5

echo "=== Worked Example count ==="
grep -rl "## Worked Example" patterns/06_graph_topological_sort/ | wc -l
echo "(should be 11: 7 problems + 4 DE scenarios)"
```
