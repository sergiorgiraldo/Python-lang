# CC Prompt: Create Pattern 11 Probabilistic Structures (Part 4 of 5)

## What This Prompt Does

Creates the Count-Min Sketch implementation with tests and documentation.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- Tests include correctness AND statistical accuracy tests

---

## Count-Min Sketch Implementation

### `problems/count_min_sketch.py`

```python
"""
Probabilistic Structure: Count-Min Sketch

Estimates the frequency of individual elements in a data stream
using fixed memory. Over-counts are possible, under-counts are not.

Use case: "How often does element X appear?" when storing exact
counts per element is too expensive.

Parameters:
- width (w): number of columns. Larger = more accurate.
- depth (d): number of rows/hash functions. Larger = higher confidence.

Error guarantee: with probability 1 - delta, the over-count is
at most epsilon * N, where epsilon = e/w, delta = e^(-d), N = total count.
"""

import math
import mmh3


class CountMinSketch:
    """
    Count-Min Sketch for frequency estimation.

    Args:
        width: number of columns (higher = more accurate)
        depth: number of rows/hash functions (higher = more confident)
    """

    def __init__(self, width: int = 1000, depth: int = 5):
        self.width = width
        self.depth = depth
        self.table: list[list[int]] = [[0] * width for _ in range(depth)]
        self.total_count = 0

    @classmethod
    def from_error_bounds(cls, epsilon: float, delta: float) -> "CountMinSketch":
        """
        Create a CMS with specific error bounds.

        Args:
            epsilon: error factor (over-count <= epsilon * N)
            delta: probability of exceeding error bound

        Example: epsilon=0.001, delta=0.01 means:
        with 99% probability, over-count is at most 0.1% of total count.
        """
        width = int(math.ceil(math.e / epsilon))
        depth = int(math.ceil(math.log(1 / delta)))
        return cls(width=width, depth=depth)

    def _get_positions(self, item: str) -> list[int]:
        """Get the column position in each row for an item."""
        return [
            mmh3.hash(item, seed=i) % self.width
            for i in range(self.depth)
        ]

    def add(self, item: str, count: int = 1) -> None:
        """Add an item to the sketch (increment its count)."""
        for row, col in enumerate(self._get_positions(item)):
            self.table[row][col] += count
        self.total_count += count

    def estimate(self, item: str) -> int:
        """
        Estimate the frequency of an item.

        Returns the minimum count across all rows. The minimum is
        the best estimate because it has the least collision noise.
        The true count is always <= the estimate.
        """
        return min(
            self.table[row][col]
            for row, col in enumerate(self._get_positions(item))
        )

    def find_heavy_hitters(self, threshold: float) -> list[tuple[str, int]]:
        """
        Find items that appear more than threshold fraction of total.

        Note: this requires maintaining a candidate list externally.
        CMS alone can't enumerate its contents. This method checks
        provided candidates.
        """
        raise NotImplementedError(
            "CMS cannot enumerate elements. Use with a candidate set "
            "from another source (e.g., a small heap of top-k items)."
        )

    @property
    def memory_bytes(self) -> int:
        """Approximate memory used by the table."""
        # Each cell is a Python int (28 bytes), but in practice
        # you'd use numpy or a C array for efficiency
        return self.width * self.depth * 8  # assuming 8 bytes per counter

    def __repr__(self) -> str:
        return (
            f"CountMinSketch(width={self.width}, depth={self.depth}, "
            f"total={self.total_count}, memory≈{self.memory_bytes} bytes)"
        )


class CountMinSketchWithHeavyHitters:
    """
    CMS paired with a heap for tracking heavy hitters.

    The CMS estimates frequencies. The heap tracks the top-k
    candidates. Together they identify elements that appear
    more than a threshold fraction of the total.
    """

    def __init__(self, width: int = 1000, depth: int = 5, top_k: int = 100):
        self.cms = CountMinSketch(width, depth)
        self.top_k = top_k
        self.candidates: dict[str, int] = {}

    def add(self, item: str, count: int = 1) -> None:
        """Add an item and update heavy hitter candidates."""
        self.cms.add(item, count)
        estimated = self.cms.estimate(item)

        # Track as candidate if frequent enough
        self.candidates[item] = estimated

        # Prune to top_k candidates
        if len(self.candidates) > self.top_k * 2:
            sorted_items = sorted(
                self.candidates.items(), key=lambda x: x[1], reverse=True
            )
            self.candidates = dict(sorted_items[: self.top_k])

    def heavy_hitters(self, threshold: float) -> list[tuple[str, int]]:
        """
        Get items appearing more than threshold fraction of total.

        Returns (item, estimated_count) pairs.
        """
        min_count = int(threshold * self.cms.total_count)
        return [
            (item, count)
            for item, count in self.candidates.items()
            if count >= min_count
        ]
```

### `problems/count_min_sketch_test.py`

```python
"""Tests for Count-Min Sketch implementation."""

import pytest

from count_min_sketch import CountMinSketch, CountMinSketchWithHeavyHitters


class TestCMSCorrectness:
    """Basic correctness tests."""

    def test_empty_sketch(self) -> None:
        cms = CountMinSketch()
        assert cms.estimate("anything") == 0

    def test_single_add(self) -> None:
        cms = CountMinSketch()
        cms.add("hello")
        assert cms.estimate("hello") >= 1

    def test_multiple_adds(self) -> None:
        cms = CountMinSketch()
        for _ in range(100):
            cms.add("frequent")
        estimate = cms.estimate("frequent")
        assert estimate >= 100  # never under-counts

    def test_never_undercounts(self) -> None:
        """Estimates must always be >= true count."""
        cms = CountMinSketch(width=500, depth=5)
        true_counts = {"a": 100, "b": 50, "c": 200, "d": 10}

        for item, count in true_counts.items():
            for _ in range(count):
                cms.add(item)

        for item, true_count in true_counts.items():
            estimate = cms.estimate(item)
            assert estimate >= true_count, (
                f"{item}: estimate {estimate} < true count {true_count}"
            )

    def test_total_count(self) -> None:
        cms = CountMinSketch()
        cms.add("a", 5)
        cms.add("b", 3)
        assert cms.total_count == 8

    def test_add_with_count(self) -> None:
        cms = CountMinSketch()
        cms.add("bulk", count=1000)
        assert cms.estimate("bulk") >= 1000


class TestCMSAccuracy:
    """Statistical accuracy tests."""

    def test_estimates_close_to_true_counts(self) -> None:
        """For a moderate dataset, estimates should be reasonably close."""
        cms = CountMinSketch(width=2000, depth=5)

        # Add items with known frequencies
        items = {}
        for i in range(1000):
            key = f"item_{i}"
            count = (i % 50) + 1
            items[key] = count
            cms.add(key, count)

        # Check that estimates are close
        max_overcount = 0
        for key, true_count in items.items():
            estimate = cms.estimate(key)
            overcount = estimate - true_count
            assert overcount >= 0  # never undercounts
            max_overcount = max(max_overcount, overcount)

        # Max overcount should be bounded by epsilon * N
        # epsilon = e/width = 2.718/2000 ≈ 0.00136
        # N = total count
        total = sum(items.values())
        epsilon = 2.718 / cms.width
        expected_bound = epsilon * total

        # Most items should be within the bound
        within_bound = sum(
            1
            for key, tc in items.items()
            if cms.estimate(key) - tc <= expected_bound
        )
        ratio = within_bound / len(items)
        assert ratio > 0.90, f"Only {ratio:.0%} within error bound"

    def test_wider_sketch_more_accurate(self) -> None:
        """A wider sketch should give better estimates."""
        narrow = CountMinSketch(width=100, depth=5)
        wide = CountMinSketch(width=5000, depth=5)

        for i in range(10000):
            key = f"item_{i % 100}"
            narrow.add(key)
            wide.add(key)

        # Compare overcounts for a specific item
        true_count = 100  # each of 100 items appears 100 times
        narrow_error = narrow.estimate("item_0") - true_count
        wide_error = wide.estimate("item_0") - true_count

        # Wide should generally have less error
        assert wide_error <= narrow_error or wide_error < 10

    def test_from_error_bounds(self) -> None:
        """CMS created with error bounds should meet them."""
        cms = CountMinSketch.from_error_bounds(epsilon=0.001, delta=0.01)
        assert cms.width >= 2718  # e / 0.001
        assert cms.depth >= 5  # ceil(ln(1/0.01))


class TestHeavyHitters:
    """Test heavy hitter detection."""

    def test_finds_frequent_items(self) -> None:
        hh = CountMinSketchWithHeavyHitters(width=2000, depth=5, top_k=20)

        # Add one very frequent item and many rare ones
        for _ in range(10000):
            hh.add("hot_key")
        for i in range(1000):
            hh.add(f"rare_{i}")

        results = hh.heavy_hitters(threshold=0.01)
        heavy_names = [name for name, _ in results]
        assert "hot_key" in heavy_names

    def test_excludes_rare_items(self) -> None:
        hh = CountMinSketchWithHeavyHitters(width=2000, depth=5, top_k=20)

        for _ in range(10000):
            hh.add("hot_key")
        for i in range(100):
            hh.add(f"rare_{i}")

        results = hh.heavy_hitters(threshold=0.05)
        # At 5% threshold, only hot_key qualifies
        heavy_names = [name for name, _ in results]
        assert "hot_key" in heavy_names
        assert not any(name.startswith("rare_") for name in heavy_names)
```

### `problems/count_min_sketch.md`

````markdown
# Count-Min Sketch

## Problem Statement

Implement a Count-Min Sketch that tracks approximate frequency counts for elements in a data stream using fixed memory. Support adding elements with counts, estimating frequencies and detecting heavy hitters.

## Thought Process

1. **The structure:** A 2D table with d rows and w columns. Each row has its own hash function. To increment, hash the item with each function and increment those d cells. To query, hash and return the minimum across all d rows.
2. **Why minimum?** Each cell accumulates counts from all items that hash to that position. The true count for an item is always <= each cell's value. Taking the minimum across rows gives the cell with the least collision noise.
3. **Error bounds:** The over-count is at most epsilon * N (total count) with probability at least 1 - delta, where epsilon = e/w and delta = e^(-d).

## Worked Example

The Count-Min Sketch is a grid where each row uses a different hash function. Adding an element increments one cell per row. Querying returns the minimum across rows. The minimum gives the tightest upper bound because it includes the least collision noise from other elements.

```
CMS with width=8, depth=3 (tiny, for illustration)

Add "apple" x 5:
  Row 0: h0("apple") = 3 → table[0][3] += 5
  Row 1: h1("apple") = 1 → table[1][1] += 5
  Row 2: h2("apple") = 6 → table[2][6] += 5

Add "banana" x 3:
  Row 0: h0("banana") = 3 → table[0][3] += 3  (collision with apple in row 0)
  Row 1: h1("banana") = 5 → table[1][5] += 3
  Row 2: h2("banana") = 2 → table[2][2] += 3

Table:
  Row 0: [0, 0, 0, 8, 0, 0, 0, 0]   ← cell 3 has apple(5) + banana(3)
  Row 1: [0, 5, 0, 0, 0, 3, 0, 0]   ← no collisions in this row
  Row 2: [0, 0, 3, 0, 0, 0, 5, 0]   ← no collisions in this row

Estimate "apple":
  Row 0, col 3: 8  (inflated by banana collision)
  Row 1, col 1: 5  (exact)
  Row 2, col 6: 5  (exact)
  min(8, 5, 5) = 5 ✓ exact

Estimate "banana":
  Row 0, col 3: 8  (inflated)
  Row 1, col 5: 3  (exact)
  Row 2, col 2: 3  (exact)
  min(8, 3, 3) = 3 ✓ exact

Estimate "cherry" (never added):
  Row 0, col 1: 0
  → min includes 0 → estimate = 0 ✓

The minimum operation "routes around" collisions. As long as at least
one row has no collision for a given item, the estimate is exact.
With more rows (depth), the probability of collision in ALL rows drops
exponentially.
```

## Approaches

### Approach 1: 2D Array with Multiple Hash Functions

<details>
<summary>📝 Explanation</summary>

The table is a list of d lists, each of width w. Use MurmurHash3 with different seeds for each row.

**Add(item, count):** For each row i, compute h_i(item) % w and increment that cell by count.

**Estimate(item):** For each row i, compute h_i(item) % w and read that cell. Return the minimum.

The minimum is the best estimate because:
- Each cell value >= true count (counts are only added, never subtracted)
- The cell with the fewest collisions is closest to the true count
- The minimum across all rows selects the least-collided cell

**Sizing:**
- Width w controls accuracy: epsilon = e/w
- Depth d controls confidence: delta = e^(-d)
- For epsilon=0.1% and delta=1%: w=2719, d=5 → ~108 KB

**Time:** O(d) per add and estimate.
**Space:** O(w * d) counters.

</details>

## Edge Cases

| Scenario | Behavior |
|---|---|
| Never-added item | Returns 0 (all cells for that item are 0 unless collisions) |
| Item added once | Returns >= 1 (exact unless extreme collision) |
| Very frequent item | Accurate (its own count dominates any collision noise) |
| All unique items | Accuracy degrades (many collisions, cells fill up) |

## Interview Tips

> "A Count-Min Sketch is a 2D array with d hash functions. To add an item, hash it with each function and increment those cells. To query, return the minimum cell value. The minimum gives the tightest upper bound. It never under-counts but can over-count by at most epsilon times the total count."

**Key talking points:**
- It's a frequency estimator, not a set membership test (that's Bloom filter)
- The "sketch" name comes from the fact that it's a compressed summary of the data
- Heavy hitter detection pairs CMS with a small heap of candidates

## DE Application

Hot key detection in streaming pipelines. When events flow through a system at millions per second, identifying which keys are "hot" (appearing much more than average) helps diagnose skew, set up targeted caching or trigger alerts. A Count-Min Sketch tracks approximate frequencies for all keys using fixed memory, flagging any key whose estimated count exceeds a threshold percentage of total traffic.

## Related Concepts

- Count Sketch: allows both over and under-estimation, uses random signs for unbiased estimates
- Space Saving: deterministic heavy hitter algorithm, exact for items above threshold
- Misra-Gries: classic streaming frequency algorithm, relates to CMS
````

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Tests ==="
uv run pytest patterns/11_probabilistic_structures/problems/count_min_sketch_test.py -v --tb=short 2>&1 | tail -20

echo ""
echo "=== Worked Example starts with prose ==="
first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' patterns/11_probabilistic_structures/problems/count_min_sketch.md)
echo "count_min_sketch.md: $first" | head -c 80
```
