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
        # epsilon = e/width = 2.718/2000 ~ 0.00136
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
