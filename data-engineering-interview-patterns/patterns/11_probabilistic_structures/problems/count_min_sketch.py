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
            f"total={self.total_count}, memory~{self.memory_bytes} bytes)"
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
