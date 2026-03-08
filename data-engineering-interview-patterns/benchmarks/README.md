# Benchmarks

Performance comparisons demonstrating why algorithmic complexity matters.
Each script compares a brute-force approach to an optimized one using
real timing data on progressively larger inputs.

## Running

```bash
# Run all benchmarks
uv run python benchmarks/binary_search_vs_linear.py
uv run python benchmarks/hash_map_vs_nested_loop.py
uv run python benchmarks/heap_vs_sort.py
uv run python benchmarks/sliding_window_vs_recompute.py
uv run python benchmarks/graph_topo_sort.py
uv run python benchmarks/interval_merge.py
uv run python benchmarks/two_pointer_merge_vs_sort.py

# Run as tests (verify correctness)
uv run pytest benchmarks/ -v
```

## Results

Results vary by machine. The relative differences are what matter,
not the absolute times.

## Connection to Patterns

| Benchmark | Pattern | What it shows |
|---|---|---|
| binary_search_vs_linear | 03_binary_search | O(log n) vs O(n): 1000x faster at n=10M |
| hash_map_vs_nested_loop | 01_hash_map | O(n) vs O(n^2): minutes vs milliseconds |
| heap_vs_sort | 05_heap | O(n log k) vs O(n log n): heap wins when k << n |
| sliding_window_vs_recompute | 04_sliding_window | O(n) vs O(n*k): single pass vs redundant work |
| graph_topo_sort | 06_graph_topological_sort | Kahn's vs DFS vs brute force on DAGs |
| interval_merge | 07_intervals | Sort+scan vs brute force merge + peak concurrent count |
| two_pointer_merge_vs_sort | 02_two_pointers | Streaming merge vs Timsort for sorted sequences |
