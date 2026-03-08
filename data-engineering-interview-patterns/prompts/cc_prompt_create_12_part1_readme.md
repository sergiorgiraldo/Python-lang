# CC Prompt: Create Pattern 12 Combined Patterns (Part 1 of 4)

## What This Prompt Does

Creates the foundation for pattern 12: directory structure, conftest.py and a deep-teaching README about recognizing and combining patterns.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Create all files as specified. If files already exist, REPLACE them.
- NO Oxford commas, NO em dashes, NO exclamation points
- Python code: typed, documented, clean

---

## Directory Setup

```
patterns/12_combined_patterns/
├── README.md
├── __init__.py
├── problems/
│   ├── conftest.py
│   └── (problems created in later prompts)
└── de_scenarios/
    └── __init__.py
```

Create any missing directories and `__init__.py` files.

## Create `problems/conftest.py`

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
```

## Replace `README.md`

```markdown
# Combined Patterns

## What Is It?

### Beyond single-pattern problems

Patterns 01-11 each teach one technique in isolation. Real interview problems rarely announce which pattern to use. More importantly, many problems require two or more patterns working together: sort the data, then binary search it. Count frequencies with a hash map, then extract the top-k with a heap. Build a graph, then traverse it with a priority queue.

This section practices the skill of pattern recognition and composition. Each problem requires identifying which patterns apply and combining them into a solution.

### How patterns combine

The most common combinations in data engineering interviews:

**Sort + Two Pointers (Patterns 02 + 05)**
Sort the data first, then use two pointers to efficiently scan for pairs or triplets. Sorting eliminates duplicates and enables the pointer movement logic. Example: 3Sum.

**Hash Map + Sliding Window (Patterns 01 + 04)**
The hash map tracks element frequencies within the window. As the window slides, update the map. Example: finding the smallest window containing all required elements.

**Hash Map + Heap (Patterns 01 + 05)**
First pass: count frequencies with a hash map. Second pass: extract the top-k using a heap. The hash map provides O(1) counting, the heap provides O(n log k) selection. Example: top-k frequent elements.

**Graph + Heap (Patterns 06 + 05)**
Dijkstra's algorithm: BFS on a weighted graph using a min-heap instead of a queue. The heap ensures you always process the shortest-path node next. Example: network delay time, pipeline critical path.

**Hash Map + Graph (Patterns 01 + 06)**
Build an adjacency list (a hash map of node → neighbors), then traverse with BFS or DFS. The hash map makes neighbor lookup O(1). This is how most graph problems are actually implemented.

### Pattern recognition in interviews

The hardest part of a coding interview isn't implementing the solution. It's figuring out which approach to use. Here are recognition signals:

| If you see... | Think... |
|---|---|
| "Find all pairs/triplets that sum to X" | Sort + two pointers |
| "Smallest window/substring containing..." | Sliding window + hash map |
| "Top K / most frequent / K largest" | Hash map + heap |
| "Shortest path / minimum cost" | Graph + heap (Dijkstra) |
| "Find connected components" | Graph + DFS/BFS |
| "Is this element in a large set?" | Hash set or Bloom filter |
| "Count distinct over huge data" | HyperLogLog |

When you don't immediately recognize the pattern, ask yourself:
1. What data structure would make the key operation fast?
2. Do I need to process things in a specific order?
3. Is there a preprocessing step that simplifies the main logic?

### Connection to data engineering

In DE work, you rarely solve problems with a single tool:
- **ETL pipelines** combine hashing (dedup) + sorting (merge joins) + graph traversal (dependency resolution)
- **Query optimization** combines hash joins + sort-merge joins + index lookups based on data characteristics
- **Data quality** combines frequency counting (hash maps) + anomaly detection (statistical thresholds) + lineage tracking (graphs)

The ability to recognize which technique applies where and compose them effectively is what separates senior from principal engineers.

### What the problems in this section cover

| Problem | Patterns Combined | What it teaches |
|---|---|---|
| 3Sum | Sort + Two Pointers | Preprocessing enables efficient scanning |
| Min Window Substring | Sliding Window + Hash Map | Tracking state within a moving window |
| Top K Frequent | Hash Map + Heap | Two-phase: count then select |
| Network Delay Time | Graph + Heap (Dijkstra) | Weighted graph traversal |

## When to Use It

This isn't a pattern you "use." It's a skill you develop. Every problem in patterns 01-11 is practice for the real interview, where problems combine multiple techniques and don't come with labels.

## Visual Aid

```
How combined patterns solve 3Sum (find triplets summing to 0):

Brute force: three nested loops → O(n^3)

Combined approach:
  Step 1: SORT the array                    ← Pattern 05
    [-1, 0, 1, 2, -1, -4] → [-4, -1, -1, 0, 1, 2]

  Step 2: For each element, TWO-POINTER scan ← Pattern 02
    Fix element at index i, scan [i+1, n-1] with two pointers

    i=0, nums[0]=-4, target=4
      L=1(-1), R=5(2): sum=1 < 4 → move L right
      L=2(-1), R=5(2): sum=1 < 4 → move L right
      ...no triplet found

    i=1, nums[1]=-1, target=1
      L=2(-1), R=5(2): sum=1 = 1 → FOUND [-1, -1, 2]
      L=3(0), R=4(1): sum=1 = 1 → FOUND [-1, 0, 1]
      ...

  Sorting enables two-pointer scan: O(n^2) total instead of O(n^3).
  Sorting also makes duplicate skipping trivial (skip equal adjacent).
```

## Trade-offs

**Preprocessing cost vs main loop efficiency:**
Sorting costs O(n log n) but enables O(n) two-pointer scans. Building a hash map costs O(n) but enables O(1) lookups. The preprocessing is always worth it when it reduces the main loop's complexity by a factor of n or more.

**Space vs time:**
Hash maps trade O(n) space for O(1) lookups. Heaps use O(k) space for top-k problems. Sometimes you can avoid extra space by sorting in-place, but this modifies the input.

## Problems in This Section

| # | Problem | Difficulty | Patterns Combined |
|---|---|---|---|
| 15 | [3Sum](problems/015_3sum.md) | Medium | Sort + Two Pointers |
| 76 | [Min Window Substring](problems/076_min_window_substring.md) | Hard | Sliding Window + Hash Map |
| 347 | [Top K Frequent](problems/347_top_k_frequent.md) | Medium | Hash Map + Heap |
| 743 | [Network Delay Time](problems/743_network_delay.md) | Medium | Graph + Heap |

## DE Scenarios

| Scenario | Patterns | Real-World Use |
|---|---|---|
| [Multi-Pattern Pipeline](de_scenarios/pipeline_analysis.md) | Hash + Graph + Heap | End-to-end pipeline optimization |
| [Pattern Recognition Practice](de_scenarios/pattern_recognition.md) | All | Interview simulation with unlabeled problems |
```

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Files created ==="
find patterns/12_combined_patterns/ -type f | sort

echo ""
echo "=== README subsections ==="
grep "^### " patterns/12_combined_patterns/README.md

echo ""
echo "=== Key teaching sections ==="
for section in "single-pattern" "patterns combine" "recognition" "Connection to data" "Visual Aid" "Trade-offs"; do
    grep -qi "$section" patterns/12_combined_patterns/README.md && echo "✅ $section" || echo "❌ $section"
done
```
