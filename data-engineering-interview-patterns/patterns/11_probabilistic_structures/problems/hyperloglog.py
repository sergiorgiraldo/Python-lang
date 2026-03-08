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
