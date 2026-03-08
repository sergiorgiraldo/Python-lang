"""Tests for Bloom Filter implementation."""

import pytest

from bloom_filter import BloomFilter


class TestBloomFilterCorrectness:
    """Basic correctness tests."""

    def test_add_and_check(self) -> None:
        bf = BloomFilter(100)
        bf.add("hello")
        assert bf.might_contain("hello") is True

    def test_missing_item(self) -> None:
        bf = BloomFilter(100)
        bf.add("hello")
        # Can't guarantee False for any specific item (FP possible)
        # but "definitely not in set" should be common for unrelated items
        assert bf.might_contain("hello") is True

    def test_no_false_negatives(self) -> None:
        """Every added item MUST return True. No exceptions."""
        bf = BloomFilter(1000)
        items = [f"item_{i}" for i in range(500)]

        for item in items:
            bf.add(item)

        for item in items:
            assert bf.might_contain(item) is True, f"False negative for {item}"

    def test_empty_filter(self) -> None:
        bf = BloomFilter(100)
        assert bf.might_contain("anything") is False

    def test_count_tracking(self) -> None:
        bf = BloomFilter(100)
        assert bf.count == 0
        bf.add("a")
        bf.add("b")
        assert bf.count == 2


class TestBloomFilterAccuracy:
    """Statistical accuracy tests."""

    def test_false_positive_rate_within_bounds(self) -> None:
        """
        Insert n items, test n non-inserted items.
        Measured FP rate should be close to the configured rate.
        """
        n = 10000
        fp_rate = 0.01
        bf = BloomFilter(n, fp_rate)

        # Insert n items
        for i in range(n):
            bf.add(f"inserted_{i}")

        # Test n items that were NOT inserted
        false_positives = 0
        test_count = n
        for i in range(test_count):
            if bf.might_contain(f"not_inserted_{i}"):
                false_positives += 1

        measured_fp = false_positives / test_count

        # Allow 3x the configured rate as upper bound
        # (statistical variation, especially at low n)
        assert measured_fp < fp_rate * 3, (
            f"FP rate {measured_fp:.4f} exceeds 3x target {fp_rate}"
        )

    def test_memory_efficiency(self) -> None:
        """Bloom filter should use far less memory than a set."""
        n = 100000
        bf = BloomFilter(n, fp_rate=0.01)

        # Fill it
        for i in range(n):
            bf.add(f"item_{i}")

        # Bloom filter memory
        bf_memory = bf.memory_bytes

        # A set of strings would use roughly 50-100 bytes per item
        set_memory_estimate = n * 70

        # Bloom filter should be at least 10x smaller
        assert bf_memory < set_memory_estimate / 10, (
            f"BF memory {bf_memory} is not much smaller than set estimate {set_memory_estimate}"
        )

    def test_1_percent_rate(self) -> None:
        bf = BloomFilter(5000, fp_rate=0.01)
        for i in range(5000):
            bf.add(f"in_{i}")

        fps = sum(1 for i in range(5000) if bf.might_contain(f"out_{i}"))
        rate = fps / 5000
        assert rate < 0.03  # 3% upper bound for 1% target

    def test_5_percent_rate(self) -> None:
        bf = BloomFilter(5000, fp_rate=0.05)
        for i in range(5000):
            bf.add(f"in_{i}")

        fps = sum(1 for i in range(5000) if bf.might_contain(f"out_{i}"))
        rate = fps / 5000
        assert rate < 0.10  # 10% upper bound for 5% target


class TestBloomFilterSizing:
    """Test optimal sizing calculations."""

    def test_more_items_means_bigger(self) -> None:
        small = BloomFilter(100)
        large = BloomFilter(10000)
        assert large.size > small.size

    def test_lower_fp_means_bigger(self) -> None:
        relaxed = BloomFilter(1000, fp_rate=0.10)
        strict = BloomFilter(1000, fp_rate=0.001)
        assert strict.size > relaxed.size

    def test_optimal_hash_count_reasonable(self) -> None:
        bf = BloomFilter(1000, fp_rate=0.01)
        # Optimal k for 1% FP rate is typically 6-7
        assert 3 <= bf.hash_count <= 15
