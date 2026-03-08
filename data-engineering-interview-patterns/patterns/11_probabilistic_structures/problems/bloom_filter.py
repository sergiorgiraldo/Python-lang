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
