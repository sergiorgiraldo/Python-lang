"""
DE Scenario: Compare memory usage of exact vs approximate approaches.

Real-world application: choosing between exact and approximate data
structures based on cardinality, accuracy requirements and memory budget.

Run: uv run python -m patterns.11_probabilistic_structures.de_scenarios.memory_budget
"""

import math
import sys
sys.path.insert(0, "patterns/11_probabilistic_structures/problems")


def estimate_exact_memory(n_items: int, avg_item_bytes: int = 40) -> int:
    """Estimate memory for a Python set of strings."""
    # Python set overhead: ~200 bytes base + 8 bytes per bucket
    # Each string: ~50 bytes overhead + string content
    set_overhead = 200 + n_items * 8
    item_memory = n_items * (50 + avg_item_bytes)
    return set_overhead + item_memory


def estimate_bloom_memory(n_items: int, fp_rate: float = 0.01) -> int:
    """Estimate Bloom filter memory."""
    m = int(math.ceil(-(n_items * math.log(fp_rate)) / (math.log(2) ** 2)))
    return math.ceil(m / 8)


def estimate_hll_memory(precision: int = 14) -> int:
    """HLL memory is fixed regardless of cardinality."""
    return 1 << precision


def estimate_cms_memory(width: int = 2000, depth: int = 5) -> int:
    """CMS memory is fixed."""
    return width * depth * 8  # 8 bytes per counter


def comparison_table(cardinalities: list[int]) -> list[dict]:
    """Build comparison table across cardinalities."""
    results = []

    for n in cardinalities:
        results.append({
            "cardinality": n,
            "exact_set_bytes": estimate_exact_memory(n),
            "bloom_1pct_bytes": estimate_bloom_memory(n, 0.01),
            "bloom_01pct_bytes": estimate_bloom_memory(n, 0.001),
            "hll_bytes": estimate_hll_memory(14),
            "cms_bytes": estimate_cms_memory(2000, 5),
        })

    return results


def format_bytes(b: int) -> str:
    """Format bytes as human-readable."""
    if b < 1024:
        return f"{b} B"
    elif b < 1024 ** 2:
        return f"{b / 1024:.1f} KB"
    elif b < 1024 ** 3:
        return f"{b / 1024**2:.1f} MB"
    else:
        return f"{b / 1024**3:.1f} GB"


if __name__ == "__main__":
    print("=== Memory Budget Analysis ===\n")
    print("  Comparing exact vs approximate data structure memory usage\n")

    cardinalities = [1_000, 10_000, 100_000, 1_000_000, 10_000_000, 100_000_000]

    results = comparison_table(cardinalities)

    header = f"  {'Cardinality':>15s}  {'Exact Set':>10s}  {'Bloom 1%':>10s}  {'Bloom 0.1%':>10s}  {'HLL':>10s}  {'CMS':>10s}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for r in results:
        print(
            f"  {r['cardinality']:>15,}  "
            f"{format_bytes(r['exact_set_bytes']):>10s}  "
            f"{format_bytes(r['bloom_1pct_bytes']):>10s}  "
            f"{format_bytes(r['bloom_01pct_bytes']):>10s}  "
            f"{format_bytes(r['hll_bytes']):>10s}  "
            f"{format_bytes(r['cms_bytes']):>10s}"
        )

    print(f"\n  Key takeaway:")
    print(f"    At 100M items:")
    r = results[-1]
    print(f"      Exact set:   {format_bytes(r['exact_set_bytes'])}")
    print(f"      Bloom (1%):  {format_bytes(r['bloom_1pct_bytes'])} "
          f"({r['exact_set_bytes'] / r['bloom_1pct_bytes']:.0f}x smaller)")
    print(f"      HLL:         {format_bytes(r['hll_bytes'])} "
          f"({r['exact_set_bytes'] / r['hll_bytes']:.0f}x smaller)")
