# CC Prompt: Enrich Pattern 06 (Graph/Topological Sort) to Principal Level

## Context

Pattern 06 has 7 problems and 4 DE scenarios. Enrichment adds principal-level depth to .md files only.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Do NOT modify any .py files
- Only ADD content to .md files
- 3-8 sentences per "At Scale" section

---

## Task 1: Enrich README.md Trade-offs Section

In `patterns/06_graph_topological_sort/README.md`, find `## Trade-offs` and ADD:

```markdown
### Scale characteristics

Graph algorithms have memory and time costs that depend on both vertices (V) and edges (E):

| Representation | Memory | Edge lookup | Best for |
|---|---|---|---|
| Adjacency list | O(V + E) | O(degree) | Sparse graphs (most DE scenarios) |
| Adjacency matrix | O(V^2) | O(1) | Dense graphs (rare in DE) |

For a pipeline DAG with 1000 tasks and 3000 dependencies, the adjacency list uses ~32KB. For a social graph with 1B users and 100B connections, it uses ~800GB - requiring distributed graph systems (Pregel, GraphX, Neo4j).

**Distributed graph processing:** Graph algorithms are hard to distribute because they involve iterative message passing between neighbors. The Bulk Synchronous Parallel (BSP) model (used by Pregel, Giraph) splits vertices across machines. Each superstep: vertices process messages, send messages to neighbors, synchronize. The synchronization barrier is the bottleneck - straggler partitions slow everything down. Key skew is severe in graph processing: a vertex with 10M edges (a celebrity in a social graph) creates massive imbalance.

**Pipeline DAGs are small graphs.** Most DE graph problems (dependency resolution, lineage tracking, impact analysis) involve small graphs (hundreds to thousands of nodes). These fit easily in memory on a single machine. Don't over-engineer: a Python dict of adjacency lists is fine for pipeline DAGs. Save distributed graph processing for truly large graphs (social networks, web crawling, entity resolution across billions of records).

### SQL equivalent

Graph traversal maps to recursive CTEs in SQL. `WITH RECURSIVE` iterates through edges, building paths level by level. This is BFS in SQL form. Cycle detection requires tracking visited nodes (using arrays in Postgres, or iteration limits in BigQuery/Snowflake). Topological sort in SQL is possible but awkward - it's usually done in the orchestration layer (Airflow, dbt) rather than in SQL. The SQL section's recursive CTE subsection covers these patterns and explicitly bridges to this pattern section.
```

## Task 2: Add "At Scale" Section to Each Problem .md

### 200_number_of_islands.md
```markdown
## At Scale

BFS/DFS on a grid uses O(V) memory for the visited set. For a 10K x 10K grid (100M cells), that's ~400MB. For larger grids, connected component algorithms on distributed frameworks (GraphX, NetworkX on a single machine for millions of nodes) are needed. The practical DE equivalent is entity resolution: given records that might refer to the same entity, find connected components of matches. At 1B records with sparse connections, Union-Find (disjoint set) is more efficient than BFS because it processes edges without building the full adjacency list. Spark GraphX's connectedComponents uses the Pregel model for distributed component finding.
```

### 133_clone_graph.md
```markdown
## At Scale

Cloning uses O(V + E) memory for both the visited map and the cloned graph. For small graphs (pipeline DAGs, org charts), this is negligible. At 1M nodes with 5M edges, the clone takes ~200MB. Deep cloning a large graph is rarely done in production - instead you'd store the graph in a database and query it. The BFS/DFS traversal pattern here is more important than the cloning: traversing a graph while maintaining a visited map is the template for lineage tracking, impact analysis and dependency resolution.
```

### 207_course_schedule.md
```markdown
## At Scale

Cycle detection with DFS uses O(V + E) time and O(V) memory. For a pipeline DAG with 10K tasks and 30K dependencies, this runs in microseconds. In production, cycle detection is a critical safety check: Airflow runs it before executing any DAG. dbt runs it during model compilation. A cycle in a data pipeline means infinite execution. At scale, the interesting problem isn't cycle detection (the DAG is small) but managing DAG evolution: when someone adds a new dependency, check that it doesn't create a cycle BEFORE committing. This is an incremental graph algorithm problem.
```

### 210_course_schedule_ii.md
```markdown
## At Scale

Topological sort with Kahn's algorithm (BFS-based) naturally produces execution layers: all tasks with in-degree 0 form the first layer (can run in parallel), then the next layer, and so on. This is exactly how Airflow schedules tasks. For a DAG with 10K tasks, topological sort takes milliseconds. The parallelism insight matters at scale: "how many layers does the DAG have?" determines the minimum end-to-end execution time assuming unlimited workers. The critical path (longest path through the DAG) is the theoretical minimum execution time. Airflow's scheduler, dbt's multi-threading and Spark's DAG scheduler all use topological ordering internally.
```

### 323_connected_components.md
```markdown
## At Scale

Finding connected components with DFS/BFS uses O(V + E) time and O(V) memory. For the Union-Find approach, the memory is O(V) with near-O(1) amortized operations per edge. At 10M nodes and 50M edges, both approaches complete in seconds on a single machine. At 1B+ nodes, you need distributed algorithms: GraphX's connectedComponents or iterative label propagation. Entity resolution (matching duplicate records across datasets) is the most common large-scale connected components problem in DE. Spark's GraphFrames library provides connected components out of the box. The key challenge at scale is handling the "giant component" problem: if many records are transitively connected, one component dominates and creates partition skew.
```

### 269_alien_dictionary.md
```markdown
## At Scale

Building the character ordering graph from the word list is O(total characters). The topological sort is O(V + E) where V is the alphabet size (at most 26) and E is the ordering constraints (at most 26^2). This is a tiny graph regardless of how many words the dictionary has. At scale, the interesting application is schema inference: given sample data, infer column ordering, data types and constraints. This is a constraint satisfaction problem similar to inferring the alien alphabet from word ordering. For large datasets, sampling is sufficient - you don't need to examine every record to infer the schema.
```

### 743_network_delay.md
```markdown
## At Scale

Dijkstra's algorithm with a binary heap runs O((V + E) log V). For a network with 10K nodes and 100K edges, this takes milliseconds. For graphs with millions of nodes, the heap operations become the bottleneck: Fibonacci heaps improve the theoretical complexity to O(V log V + E) but are rarely used in practice due to high constant factors. At web scale (billions of nodes), single-source shortest path is computed with distributed BFS variants or approximate algorithms. In DE, the more common application is critical path analysis in pipeline DAGs: "what's the end-to-end execution time of my pipeline?" This is the longest (not shortest) path in a DAG, computed with a topological sort and dynamic programming in O(V + E).
```

## Task 3: Enrich Interview Tips with Evaluator Framing

### 200 (Islands):
```markdown
**What the interviewer evaluates:** Grid-as-graph recognition is the first test. BFS vs DFS choice and explaining the tradeoff (BFS is iterative and avoids stack overflow, DFS is simpler to write) shows maturity. The follow-up "what about very large grids?" tests whether you know Union-Find as an alternative. Mentioning entity resolution as the production equivalent shows DE depth.
```

### 133 (Clone Graph):
```markdown
**What the interviewer evaluates:** Managing the visited/cloned map to handle cycles tests graph traversal fundamentals. BFS vs DFS both work - the interviewer wants to see clean code with correct cycle handling. The follow-up "what if nodes have different types?" or "what about very large graphs?" pivots toward system design.
```

### 207 (Course Schedule):
```markdown
**What the interviewer evaluates:** Three-color DFS (white/gray/black) for cycle detection tests whether you understand graph theory beyond the template. Explaining what the gray state means (currently being processed, so encountering it again means a cycle) is the differentiator. Connecting to Airflow's DAG validation shows you've implemented this pattern in production.
```

### 210 (Course Schedule II):
```markdown
**What the interviewer evaluates:** Kahn's algorithm (iterative BFS with in-degree tracking) vs DFS with post-order reversal are both valid. Kahn's is more intuitive for explaining execution layers and parallelism. At principal level, discussing "how many tasks can run in parallel at each step?" demonstrates pipeline scheduling understanding. Mention that this is literally what Airflow and dbt do.
```

### 323 (Connected Components):
```markdown
**What the interviewer evaluates:** BFS/DFS on disconnected graphs (iterating over all nodes, starting new traversals for unvisited ones) tests completeness. The Union-Find alternative tests whether you know specialized data structures. At principal level, discussing entity resolution and the "giant component" problem shows you've dealt with real-world graph challenges.
```

### 269 (Alien Dictionary):
```markdown
**What the interviewer evaluates:** This problem combines graph construction (extracting ordering from word comparisons) with topological sort. The construction phase is where most bugs occur. Handling edge cases (like a word that's a prefix of another but appears after it, which means invalid input) tests thoroughness. This is one of the harder graph problems and is typically used for senior+ interviews.
```

### 743 (Network Delay):
```markdown
**What the interviewer evaluates:** Dijkstra's algorithm tests whether you can implement a standard algorithm under pressure. The "why not BFS?" question (answer: edges have different weights) tests understanding. The follow-up "what about negative weights?" (answer: Bellman-Ford) tests breadth. Connecting to pipeline critical path analysis shows you apply shortest-path thinking to DE problems.
```

## Task 4: Glossary Updates

Add to WORKING_GLOSSARY.md:

- **BSP (Bulk Synchronous Parallel)**: Computation model for distributed graph processing. Alternates between local computation, message passing and global synchronization. Used by Pregel and Giraph.
- **entity resolution**: Process of identifying records across datasets that refer to the same real-world entity. Often modeled as a connected components problem on a similarity graph.
- **critical path**: The longest path through a DAG, determining the minimum end-to-end execution time assuming unlimited parallelism. Computed with topological sort + dynamic programming.
- **label propagation**: Distributed algorithm for finding connected components or communities. Each node adopts the label of its most frequent neighbor iteratively.
- **giant component**: In graph theory, a connected component containing a significant fraction of all nodes. Creates partition skew in distributed graph processing.

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== At Scale sections ==="
for f in patterns/06_graph_topological_sort/problems/*.md; do
    name=$(basename "$f")
    has_scale=$(grep -q "## At Scale" "$f" && echo "Y" || echo "N")
    echo "  $name: At Scale=$has_scale"
done

echo ""
echo "=== README enriched ==="
grep -q "Scale characteristics" patterns/06_graph_topological_sort/README.md && echo "✅" || echo "❌"

echo ""
echo "=== Evaluator framing ==="
for f in patterns/06_graph_topological_sort/problems/*.md; do
    has_eval=$(grep -q "interviewer evaluates" "$f" && echo "Y" || echo "N")
    echo "  $(basename $f): evaluator=$has_eval"
done

echo ""
echo "=== Style + tests ==="
grep -rn "—" patterns/06_graph_topological_sort/ --include="*.md" && echo "❌" || echo "✅ No em dashes"
uv run pytest patterns/06_graph_topological_sort/ --tb=short -q 2>&1 | tail -3
```
