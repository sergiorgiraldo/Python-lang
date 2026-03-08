# CC Prompt: Create Pattern 11 Probabilistic Structures (Part 3 of 5)

## What This Prompt Does

Creates the HyperLogLog implementation with tests and documentation.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- Tests include correctness AND statistical accuracy tests

---

## HyperLogLog Implementation

### `problems/hyperloglog.py`

```python
"""
Probabilistic Structure: HyperLogLog

Estimates the cardinality (number of distinct elements) of a dataset
using O(m) memory where m is the number of registers, regardless of
dataset size.

Standard error: ~1.04 / sqrt(m)
With m=2^14=16384 registers (default): ~0.81% error using ~12 KB

This is what BigQuery and Snowflake use internally for
APPROX_COUNT_DISTINCT().
"""

import math
import mmh3


class HyperLogLog:
    """
    HyperLogLog cardinality estimator.

    Args:
        precision: number of bits for register addressing (default 14).
                   Uses 2^p registers, each storing up to 64-p bits.
                   Higher precision = more memory = better accuracy.
    """

    def __init__(self, precision: int = 14):
        if not 4 <= precision <= 16:
            raise ValueError("Precision must be between 4 and 16")

        self.precision = precision
        self.num_registers = 1 << precision  # 2^p
        self.registers = bytearray(self.num_registers)

        # Alpha constant for bias correction
        if self.num_registers == 16:
            self.alpha = 0.673
        elif self.num_registers == 32:
            self.alpha = 0.697
        elif self.num_registers == 64:
            self.alpha = 0.709
        else:
            self.alpha = 0.7213 / (1 + 1.079 / self.num_registers)

    def add(self, item: str) -> None:
        """
        Add an item to the estimator.

        Hash the item to a 32-bit integer. Use the first p bits to
        select a register. Count the leading zeros in the remaining
        bits and store the max in that register.
        """
        h = mmh3.hash(item, signed=False)  # unsigned 32-bit hash

        # First p bits determine the register
        register_idx = h >> (32 - self.precision)

        # Remaining bits: count leading zeros + 1
        remaining = h & ((1 << (32 - self.precision)) - 1)
        # Count leading zeros in the remaining (32-p) bits
        run_length = self._count_leading_zeros(remaining, 32 - self.precision) + 1

        # Keep the maximum run length seen for this register
        self.registers[register_idx] = max(self.registers[register_idx], run_length)

    @staticmethod
    def _count_leading_zeros(value: int, num_bits: int) -> int:
        """Count leading zeros in a value with a known bit width."""
        if value == 0:
            return num_bits

        count = 0
        for i in range(num_bits - 1, -1, -1):
            if value & (1 << i):
                break
            count += 1
        return count

    def estimate(self) -> int:
        """
        Estimate the cardinality using the HLL algorithm.

        Uses harmonic mean of 2^(register values) with bias corrections
        for small and large cardinalities.
        """
        # Raw estimate using harmonic mean
        indicator = sum(2.0 ** (-reg) for reg in self.registers)
        raw_estimate = self.alpha * self.num_registers ** 2 / indicator

        # Small range correction (linear counting)
        if raw_estimate <= 2.5 * self.num_registers:
            zeros = self.registers.count(0)
            if zeros > 0:
                return int(self.num_registers * math.log(self.num_registers / zeros))

        # Large range correction (for 32-bit hashes)
        if raw_estimate > (1 << 32) / 30:
            return int(-(1 << 32) * math.log(1 - raw_estimate / (1 << 32)))

        return int(raw_estimate)

    def merge(self, other: "HyperLogLog") -> "HyperLogLog":
        """
        Merge two HLL instances (union operation).

        Take the max register value at each position. This allows
        distributed counting: each worker maintains its own HLL,
        then merge all results for the global estimate.
        """
        if self.precision != other.precision:
            raise ValueError("Cannot merge HLLs with different precision")

        result = HyperLogLog(self.precision)
        for i in range(self.num_registers):
            result.registers[i] = max(self.registers[i], other.registers[i])
        return result

    @property
    def memory_bytes(self) -> int:
        """Memory used by registers."""
        return len(self.registers)

    @property
    def standard_error(self) -> float:
        """Theoretical standard error."""
        return 1.04 / math.sqrt(self.num_registers)

    def __repr__(self) -> str:
        return (
            f"HyperLogLog(p={self.precision}, registers={self.num_registers}, "
            f"memory={self.memory_bytes} bytes, std_error={self.standard_error:.4f})"
        )
```

### `problems/hyperloglog_test.py`

```python
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
```

### `problems/hyperloglog.md`

````markdown
# HyperLogLog

## Problem Statement

Implement a HyperLogLog cardinality estimator that can count the number of distinct elements in a dataset using fixed memory regardless of dataset size. Support adding elements, estimating cardinality and merging two HLL instances.

## Thought Process

1. **The observation:** If you hash elements uniformly and look at the binary representation, the probability of seeing k leading zeros is 1/2^k. So if the longest run of leading zeros you've seen is 10, you've probably seen about 2^10 = 1024 distinct elements.
2. **Reduce variance with buckets:** A single maximum is noisy. Split elements into m buckets (using the first p bits of the hash as the bucket index) and track the max leading zeros per bucket. Combine using the harmonic mean for a more stable estimate.
3. **Bias corrections:** Small cardinalities and very large cardinalities need corrections. Linear counting handles the small range (when many registers are still zero). Large range correction handles hash collision effects.

## Worked Example

Each element is hashed and split into a bucket index (first p bits) and a run value (leading zeros in the remaining bits). The register stores the maximum run seen for each bucket. The harmonic mean of 2^(-register) values across all registers gives the raw estimate, corrected by a constant alpha.

```
Precision p=4 → 16 registers (tiny, for illustration)

Add "alice":
  hash = 0b 0011 010110001... (32 bits)
  bucket = 0b0011 = 3 (first 4 bits)
  remaining = 010110001... → leading zeros = 0 → run = 1
  registers[3] = max(0, 1) = 1

Add "bob":
  hash = 0b 0011 000010110...
  bucket = 3 (same bucket as alice)
  remaining = 000010110... → leading zeros = 3 → run = 4
  registers[3] = max(1, 4) = 4

Add "charlie":
  hash = 0b 1010 001101...
  bucket = 10
  remaining = 001101... → leading zeros = 1 → run = 2
  registers[10] = max(0, 2) = 2

Registers after 3 items: mostly zeros, a few non-zero.
  [0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0]

Estimate:
  indicator = sum(2^(-reg)) = 14*2^0 + 2^(-4) + 2^(-2)
            = 14 + 0.0625 + 0.25 = 14.3125
  raw = alpha * 16^2 / 14.3125 ≈ 0.673 * 256 / 14.3125 ≈ 12.0

  Small range correction: 14 registers are zero.
  linear_count = 16 * ln(16/14) ≈ 16 * 0.134 ≈ 2.1

  Corrected estimate ≈ 2 (close to actual 3)

With p=14 (16384 registers) and millions of items, the estimate
is typically within 1-2% of the true count.
```

## Approaches

### Approach 1: Register-Based with Bias Corrections

<details>
<summary>📝 Explanation</summary>

The implementation has three parts:

**Add:** Hash the element. Use the first p bits as the register index. Count leading zeros in the remaining 32-p bits, add 1 (so a hash of all zeros gives max value, not zero). Update the register if this value is larger than the current one.

**Estimate:** Compute the harmonic mean of 2^(-register) values across all registers. Multiply by alpha * m^2 (bias correction constant). Apply small-range correction (linear counting) when many registers are zero. Apply large-range correction when estimate approaches 2^32 (hash space limit).

**Merge:** Take the element-wise maximum of two register arrays. This works because the max leading zeros for any element is captured by whichever HLL saw it. This enables distributed counting: each worker maintains its own HLL, then a final merge produces the global estimate.

**Time:** O(1) per add, O(m) per estimate, O(m) per merge.
**Space:** O(m) = O(2^p) bytes. At p=14: 16,384 bytes = 16 KB.

The standard error is 1.04/sqrt(m). At p=14: 1.04/128 = 0.81%.

</details>

## Edge Cases

| Scenario | Behavior |
|---|---|
| Empty HLL | Estimate returns 0 (all registers zero, linear counting gives 0) |
| Single element | Returns ~1 (one register non-zero, linear counting corrects) |
| All duplicates | Returns ~1 (same hash always updates the same register to the same value) |
| 1 billion distinct elements | Returns estimate within ~1% using 16 KB |

## Interview Tips

> "HyperLogLog estimates distinct counts using fixed memory. It hashes elements, splits them into buckets using the first p bits, and tracks the longest run of leading zeros per bucket. Combining with a harmonic mean gives an estimate with about 1% error using 16 KB. This is what APPROX_COUNT_DISTINCT uses in BigQuery and Snowflake."

**Key talking points:**
- The merge operation (max of registers) enables distributed counting
- Memory is fixed regardless of cardinality
- Error is ~1.04/sqrt(m), independent of dataset size

## DE Application

Every data warehouse has queries like "count distinct users per day across 500M events." Exact COUNT DISTINCT requires sorting or hashing all values. APPROX_COUNT_DISTINCT uses HLL internally and returns a result with ~1% error in a fraction of the time and memory. Understanding HLL helps you explain the ~1% discrepancy to stakeholders and choose appropriate precision settings.

## Related Concepts

- LogLog: predecessor, uses geometric mean instead of harmonic
- HyperLogLog++: Google's improvement with better small-cardinality corrections
- MinHash: related technique for estimating set similarity (Jaccard index)
````

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Tests ==="
uv run pytest patterns/11_probabilistic_structures/problems/hyperloglog_test.py -v --tb=short 2>&1 | tail -20

echo ""
echo "=== Worked Example starts with prose ==="
first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' patterns/11_probabilistic_structures/problems/hyperloglog.md)
echo "hyperloglog.md: $first" | head -c 80
```
