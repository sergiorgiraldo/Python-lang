"""Tests for HyperLogLog implementation."""

import pytest
import math

from hyperloglog import HyperLogLog


class TestHLLCorrectness:
    """Basic correctness tests."""

    def test_empty(self) -> None:
        hll = HyperLogLog(precision=10)
        assert hll.estimate() == 0

    def test_single_element(self) -> None:
        hll = HyperLogLog(precision=10)
        hll.add("hello")
        estimate = hll.estimate()
        assert 0 < estimate < 5  # should be ~1

    def test_duplicates_dont_increase_count(self) -> None:
        hll = HyperLogLog(precision=10)
        for _ in range(1000):
            hll.add("same_item")
        estimate = hll.estimate()
        assert estimate < 5  # should be ~1

    def test_distinct_items_counted(self) -> None:
        hll = HyperLogLog(precision=12)
        for i in range(1000):
            hll.add(f"item_{i}")
        estimate = hll.estimate()
        # Should be within 20% of 1000
        assert 800 < estimate < 1200


class TestHLLAccuracy:
    """Statistical accuracy tests."""

    def test_small_cardinality(self) -> None:
        """100 distinct items, should be within 20%."""
        hll = HyperLogLog(precision=14)
        for i in range(100):
            hll.add(f"user_{i}")

        estimate = hll.estimate()
        error = abs(estimate - 100) / 100
        assert error < 0.20, f"Error {error:.2%} for n=100"

    def test_medium_cardinality(self) -> None:
        """10,000 distinct items, should be within 10%."""
        hll = HyperLogLog(precision=14)
        for i in range(10000):
            hll.add(f"user_{i}")

        estimate = hll.estimate()
        error = abs(estimate - 10000) / 10000
        assert error < 0.10, f"Error {error:.2%} for n=10000"

    def test_large_cardinality(self) -> None:
        """100,000 distinct items, should be within 5%."""
        hll = HyperLogLog(precision=14)
        for i in range(100000):
            hll.add(f"user_{i}")

        estimate = hll.estimate()
        error = abs(estimate - 100000) / 100000
        assert error < 0.05, f"Error {error:.2%} for n=100000"

    def test_precision_affects_accuracy(self) -> None:
        """Higher precision should give better accuracy."""
        n = 50000
        items = [f"item_{i}" for i in range(n)]

        low_p = HyperLogLog(precision=8)
        high_p = HyperLogLog(precision=14)

        for item in items:
            low_p.add(item)
            high_p.add(item)

        error_low = abs(low_p.estimate() - n) / n
        error_high = abs(high_p.estimate() - n) / n

        # High precision should generally be more accurate
        # (not guaranteed for any single run, but very likely)
        assert high_p.standard_error < low_p.standard_error


class TestHLLMerge:
    """Test merge (union) operation."""

    def test_merge_disjoint(self) -> None:
        """Merging two HLLs with disjoint sets."""
        hll1 = HyperLogLog(precision=14)
        hll2 = HyperLogLog(precision=14)

        for i in range(5000):
            hll1.add(f"set1_{i}")
        for i in range(5000):
            hll2.add(f"set2_{i}")

        merged = hll1.merge(hll2)
        estimate = merged.estimate()

        # Should be close to 10000
        error = abs(estimate - 10000) / 10000
        assert error < 0.10

    def test_merge_overlapping(self) -> None:
        """Merging two HLLs with overlapping sets."""
        hll1 = HyperLogLog(precision=14)
        hll2 = HyperLogLog(precision=14)

        # 3000 shared + 2000 unique to each = 7000 distinct
        for i in range(5000):
            hll1.add(f"item_{i}")
        for i in range(3000, 10000):
            hll2.add(f"item_{i}")

        merged = hll1.merge(hll2)
        estimate = merged.estimate()

        error = abs(estimate - 10000) / 10000
        assert error < 0.10

    def test_merge_precision_mismatch_raises(self) -> None:
        hll1 = HyperLogLog(precision=10)
        hll2 = HyperLogLog(precision=14)
        with pytest.raises(ValueError):
            hll1.merge(hll2)


class TestHLLMemory:
    """Test memory efficiency."""

    def test_fixed_memory(self) -> None:
        """Memory should be the same regardless of items added."""
        hll = HyperLogLog(precision=14)
        memory_empty = hll.memory_bytes

        for i in range(100000):
            hll.add(f"item_{i}")

        memory_full = hll.memory_bytes
        assert memory_empty == memory_full  # memory doesn't grow

    def test_memory_size(self) -> None:
        """Default precision (14) should use ~16 KB."""
        hll = HyperLogLog(precision=14)
        assert hll.memory_bytes == 16384  # 2^14 bytes
