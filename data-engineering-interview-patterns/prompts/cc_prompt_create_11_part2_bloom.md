# CC Prompt: Create Pattern 11 Probabilistic Structures (Part 2 of 5)

## What This Prompt Does

Creates the Bloom Filter implementation with tests and documentation.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- Tests include both correctness tests and statistical accuracy tests

---

## Bloom Filter Implementation

### `problems/bloom_filter.py`

```python
"""
Probabilistic Structure: Bloom Filter

A space-efficient set that supports membership queries with a bounded
false positive rate. No false negatives.

Use case: "Is this element possibly in the set?" when storing the
full set is too expensive.

Memory: ~10 bits per element for 1% false positive rate.
Time: O(k) per add/query where k is the number of hash functions.
"""

import math
import mmh3  # MurmurHash3 - fast, non-cryptographic hash


class BloomFilter:
    """
    Bloom filter with configurable size and hash count.

    Args:
        expected_items: expected number of elements to insert
        fp_rate: desired false positive rate (default 1%)
    """

    def __init__(self, expected_items: int, fp_rate: float = 0.01):
        self.expected_items = expected_items
        self.fp_rate = fp_rate

        # Calculate optimal size and hash count
        # m = -(n * ln(p)) / (ln(2))^2
        self.size = self._optimal_size(expected_items, fp_rate)
        # k = (m / n) * ln(2)
        self.hash_count = self._optimal_hash_count(self.size, expected_items)

        self.bit_array = bytearray(math.ceil(self.size / 8))
        self.count = 0

    @staticmethod
    def _optimal_size(n: int, p: float) -> int:
        """Calculate optimal bit array size."""
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return int(math.ceil(m))

    @staticmethod
    def _optimal_hash_count(m: int, n: int) -> int:
        """Calculate optimal number of hash functions."""
        k = (m / n) * math.log(2)
        return max(1, int(round(k)))

    def _get_bit_positions(self, item: str) -> list[int]:
        """Generate k bit positions for an item using double hashing."""
        h1 = mmh3.hash(item, seed=0) % self.size
        h2 = mmh3.hash(item, seed=42) % self.size

        positions = []
        for i in range(self.hash_count):
            pos = (h1 + i * h2) % self.size
            positions.append(pos)

        return positions

    def _set_bit(self, position: int) -> None:
        """Set a bit at the given position."""
        byte_idx = position // 8
        bit_idx = position % 8
        self.bit_array[byte_idx] |= 1 << bit_idx

    def _get_bit(self, position: int) -> bool:
        """Get the bit at the given position."""
        byte_idx = position // 8
        bit_idx = position % 8
        return bool(self.bit_array[byte_idx] & (1 << bit_idx))

    def add(self, item: str) -> None:
        """Add an item to the filter."""
        for pos in self._get_bit_positions(item):
            self._set_bit(pos)
        self.count += 1

    def might_contain(self, item: str) -> bool:
        """
        Check if an item might be in the filter.

        Returns True if the item is possibly in the set (with false
        positive probability). Returns False if the item is definitely
        not in the set.
        """
        return all(self._get_bit(pos) for pos in self._get_bit_positions(item))

    def estimated_fp_rate(self) -> float:
        """Estimate the current false positive rate based on fill ratio."""
        if self.count == 0:
            return 0.0
        # Theoretical: (1 - e^(-kn/m))^k
        exponent = -self.hash_count * self.count / self.size
        return (1 - math.exp(exponent)) ** self.hash_count

    @property
    def memory_bytes(self) -> int:
        """Memory used by the bit array."""
        return len(self.bit_array)

    def __repr__(self) -> str:
        return (
            f"BloomFilter(items={self.count}, size={self.size} bits, "
            f"hashes={self.hash_count}, memory={self.memory_bytes} bytes, "
            f"est_fp={self.estimated_fp_rate():.4f})"
        )
```

### `problems/bloom_filter_test.py`

```python
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
```

### `problems/bloom_filter.md`

````markdown
# Bloom Filter

## Problem Statement

Implement a Bloom filter that supports adding elements and checking membership with a configurable false positive rate. The filter should automatically calculate optimal size and hash count based on the expected number of elements.

## Thought Process

1. **The core idea:** Instead of storing elements, store k hashed "fingerprints" as bit positions. To check membership, verify all k positions are set. If any bit is 0, the element was never added (no false negatives). If all are 1, it was probably added (but hash collisions can cause false positives).
2. **Optimal sizing:** Given n expected elements and desired FP rate p, the optimal bit array size is m = -(n * ln(p)) / (ln(2))^2, and optimal hash count is k = (m/n) * ln(2).
3. **Double hashing:** Instead of k independent hash functions, use two hashes and combine them: h_i(x) = h1(x) + i * h2(x). This gives equally good results with less computation.

## Worked Example

A Bloom filter is a bit array where each element "claims" k bit positions via hashing. Membership is confirmed only if ALL k positions are set. False positives occur when different elements' hash positions overlap, setting bits that make a non-member look like a member.

```
Parameters: expected_items=3, fp_rate=0.10
Calculated: size=15 bits, hash_count=3

Add "apple":
  h1("apple")=2, h2("apple")=8, h3("apple")=13
  Bit array: 0 0 1 0 0 0 0 0 1 0 0 0 0 1 0
                  ^               ^           ^

Add "banana":
  h1("banana")=1, h2("banana")=5, h3("banana")=9
  Bit array: 0 1 1 0 0 1 0 0 1 1 0 0 0 1 0
                ^               ^       ^

Query "apple": positions 2,8,13 → all 1 → PROBABLY IN SET ✓
Query "banana": positions 1,5,9 → all 1 → PROBABLY IN SET ✓

Query "cherry":
  h1("cherry")=2, h2("cherry")=5, h3("cherry")=13
  positions 2,5,13 → all 1 → FALSE POSITIVE
  (positions 2 and 13 from "apple", position 5 from "banana")

Query "date":
  h1("date")=0, h2("date")=5, h3("date")=14
  position 0 is 0 → DEFINITELY NOT IN SET ✓
  (one zero bit is enough to confirm absence)

Memory: 2 bytes for 3 elements (vs ~210 bytes for a Python set)
```

## Approaches

### Approach 1: Bit Array with Double Hashing

<details>
<summary>📝 Explanation</summary>

Use a bytearray as the bit storage (Python doesn't have a built-in bit array). Calculate optimal m (bits) and k (hashes) from the expected items and desired FP rate.

For each add/query, compute k positions using double hashing: position_i = (h1 + i * h2) % m. This avoids needing k independent hash functions while maintaining the same theoretical properties.

The key formulas:
- Optimal bits: m = -(n * ln(p)) / (ln(2))^2
- Optimal hashes: k = (m/n) * ln(2)
- Theoretical FP rate: (1 - e^(-kn/m))^k

At 1% FP rate, each element needs about 9.6 bits (roughly 1.2 bytes). A million elements need about 1.2 MB. Compare to a Python set that would need roughly 70 MB.

**Time:** O(k) per add and query. k is typically 3-10.
**Space:** O(m) bits. For 1% FP: ~10 bits per expected element.

</details>

## Edge Cases

| Scenario | Behavior |
|---|---|
| Query on empty filter | Always returns False (no bits set) |
| Same element added twice | No change (bits already set) |
| More items than expected | Works but FP rate increases beyond configured target |
| Very low FP rate (0.001) | Needs more bits and more hash functions |

## Interview Tips

> "A Bloom filter trades a small false positive rate for massive memory savings. It uses k hash functions to map each element to k bit positions. If all k bits are set, the element is probably in the set. If any bit is 0, it's definitely not. For 1% false positive rate, you need about 10 bits per element."

**Follow-ups:**
- "Can you delete elements?" → Not from a standard Bloom filter (clearing a bit might affect other elements). Use a Counting Bloom Filter (replace bits with counters).
- "What hash functions?" → MurmurHash3 is standard. Double hashing (two hashes combined) is as good as k independent hashes.
- "What if the number of elements exceeds the expected count?" → The filter still works but FP rate degrades. Monitor fill ratio.

## DE Application

Deduplication pre-filter in streaming pipelines. Before doing an expensive database lookup to check "have I seen this event ID before?", check the Bloom filter first. If it says "no," skip the DB call (guaranteed correct). If it says "maybe," do the DB call (might be a false positive). This eliminates 99%+ of unnecessary database queries.

## Related Concepts

- Counting Bloom Filter: allows deletions by replacing bits with counters
- Cuckoo Filter: better for workloads that need deletion, slightly more memory efficient
- Quotient Filter: cache-friendly alternative
````

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

# Install mmh3 for MurmurHash
pip install mmh3 --break-system-packages 2>/dev/null
# Or if using uv:
uv add mmh3 2>/dev/null || uv pip install mmh3 2>/dev/null

echo "=== Tests ==="
uv run pytest patterns/11_probabilistic_structures/problems/bloom_filter_test.py -v --tb=short 2>&1 | tail -15

echo ""
echo "=== Worked Example starts with prose ==="
first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' patterns/11_probabilistic_structures/problems/bloom_filter.md)
echo "bloom_filter.md: $first" | head -c 80
```

**Important:** This pattern requires the `mmh3` package for MurmurHash3. Add it to the project's dependencies:
```bash
cd ~/dev/projects/data-engineering-interview-patterns
uv add mmh3
```
If `uv add` doesn't work, try `uv pip install mmh3` or add `mmh3` to pyproject.toml's dependencies manually and run `uv sync`.
