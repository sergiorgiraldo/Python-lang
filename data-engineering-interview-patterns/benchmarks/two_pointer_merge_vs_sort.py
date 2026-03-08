"""
Benchmark: Two-Pointer Merge vs Concatenate-and-Sort

Compares two approaches for combining sorted sequences:
- Two-pointer merge: O(n+m) time, works as a generator with O(1) memory
- Concat + sort: O((n+m) log(n+m)) time, requires all data in memory

In Python, Timsort is C-implemented and specifically optimized for merging
sorted runs. So concat+sort is often faster in wall-clock time for in-memory
data. The two-pointer merge wins on a different axis: it works as a streaming
operation that never needs both full arrays in memory simultaneously.

This benchmark shows both the speed comparison (honest about Timsort's
advantage) and the memory comparison (where two-pointer merge wins).

Usage:
    uv run python benchmarks/two_pointer_merge_vs_sort.py
"""

# Three approaches compared:
#
# 1. merge_two_pointer (list) - Two pointers, builds result list in memory.
#    Same memory as concat+sort (both inputs + output). Pure Python, so
#    slower than Timsort's C implementation.
#
# 2. merge_generator - Two pointers, yields one element at a time. Holds
#    only two values in memory. When inputs are also iterators (file readers,
#    DB cursors), the entire operation runs in O(1) memory. This is the
#    production approach for data that doesn't fit in RAM.
#
# 3. merge_concat_sort - Concatenates into one list, then sorts. Requires
#    all data materialized in memory before sorting can begin. Fastest in
#    Python because Timsort is C-optimized and detects sorted runs, but
#    impossible to use when data exceeds available memory.

import random
import sys
import time
from collections.abc import Iterator


def merge_two_pointer(a: list[int], b: list[int]) -> list[int]:
    """O(n + m) - two pointer merge of sorted inputs."""
    result: list[int] = []
    i, j = 0, 0

    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1

    result.extend(a[i:])
    result.extend(b[j:])
    return result


def merge_generator(a: Iterator[int], b: Iterator[int]) -> Iterator[int]:
    """
    O(n + m) streaming merge. Memory: O(1) beyond the two current values.

    This is the production version. Each input can be a file reader,
    database cursor, or any iterator over sorted data. You never need
    both full sequences in memory.
    """
    val_a = next(a, None)
    val_b = next(b, None)

    while val_a is not None and val_b is not None:
        if val_a <= val_b:
            yield val_a
            val_a = next(a, None)
        else:
            yield val_b
            val_b = next(b, None)

    while val_a is not None:
        yield val_a
        val_a = next(a, None)
    while val_b is not None:
        yield val_b
        val_b = next(b, None)


def merge_concat_sort(a: list[int], b: list[int]) -> list[int]:
    """O((n+m) log(n+m)) - concatenate and re-sort."""
    combined = a + b
    combined.sort()
    return combined


def estimate_memory(n: int) -> dict[str, str]:
    """Estimate peak memory usage for each approach."""
    int_size = sys.getsizeof(0)  # ~28 bytes for small ints
    list_overhead = sys.getsizeof([])  # ~56 bytes

    # Concat+sort: needs a + b + combined (3 full copies at peak during concat)
    concat_peak = 3 * (list_overhead + n * int_size)

    # Two-pointer (list): needs a + b + result (same 3 copies)
    tp_list_peak = 3 * (list_overhead + n * int_size)

    # Two-pointer (generator): needs only 2 current values + output one at a time
    tp_gen_peak = 2 * int_size  # just two values in flight

    def fmt(bytes_val: int) -> str:
        if bytes_val < 1024:
            return f"{bytes_val} B"
        elif bytes_val < 1024**2:
            return f"{bytes_val / 1024:.1f} KB"
        elif bytes_val < 1024**3:
            return f"{bytes_val / 1024**2:.1f} MB"
        else:
            return f"{bytes_val / 1024**3:.1f} GB"

    return {
        "concat_sort": fmt(concat_peak),
        "two_pointer_list": fmt(tp_list_peak),
        "two_pointer_gen": fmt(tp_gen_peak),
    }


def run_speed_benchmark(sizes: list[int]) -> None:
    """Compare wall-clock speed of all three approaches."""
    random.seed(42)

    print("Speed Comparison")
    print("=" * 75)
    print(
        f"{'n (each)':>12}  {'Merge (list)':>13}  {'Merge (gen)':>13}  "
        f"{'Concat+Sort':>13}  {'Note':>8}"
    )
    print("-" * 75)

    for n in sizes:
        a = sorted(random.randint(0, n * 10) for _ in range(n))
        b = sorted(random.randint(0, n * 10) for _ in range(n))

        # Two-pointer merge (list)
        start = time.perf_counter()
        result_merge = merge_two_pointer(a, b)
        merge_time = time.perf_counter() - start

        # Two-pointer merge (generator, consumed into count)
        start = time.perf_counter()
        count = 0
        for _ in merge_generator(iter(a), iter(b)):
            count += 1
        gen_time = time.perf_counter() - start

        # Concat + sort
        start = time.perf_counter()
        result_sort = merge_concat_sort(a, b)
        sort_time = time.perf_counter() - start

        assert result_merge == result_sort
        assert count == len(result_merge)

        # Note which is fastest
        fastest = min(merge_time, gen_time, sort_time)
        if fastest == sort_time:
            note = "sort*"
        elif fastest == gen_time:
            note = "gen*"
        else:
            note = "merge*"

        print(
            f"{n:>12,}  {merge_time:>12.4f}s  {gen_time:>12.4f}s  "
            f"{sort_time:>12.4f}s  {note:>8}"
        )

    print("-" * 75)
    print("* = fastest for that input size")


def run_memory_comparison(sizes: list[int]) -> None:
    """Show estimated peak memory for each approach."""
    print("\nPeak Memory Comparison (estimated)")
    print("=" * 70)
    print(
        f"{'n (each)':>12}  {'Concat+Sort':>14}  "
        f"{'Merge (list)':>14}  {'Merge (gen)':>14}"
    )
    print("-" * 70)

    for n in sizes:
        mem = estimate_memory(n)
        print(
            f"{n:>12,}  {mem['concat_sort']:>14}  "
            f"{mem['two_pointer_list']:>14}  {mem['two_pointer_gen']:>14}"
        )

    print("-" * 70)


def test_merge_basic() -> None:
    a = [1, 3, 5]
    b = [2, 4, 6]
    assert merge_two_pointer(a, b) == [1, 2, 3, 4, 5, 6]


def test_generator_basic() -> None:
    a = [1, 3, 5]
    b = [2, 4, 6]
    assert list(merge_generator(iter(a), iter(b))) == [1, 2, 3, 4, 5, 6]


def test_concat_sort_basic() -> None:
    a = [1, 3, 5]
    b = [2, 4, 6]
    assert merge_concat_sort(a, b) == [1, 2, 3, 4, 5, 6]


def test_all_approaches_agree() -> None:
    random.seed(123)
    a = sorted(random.randint(0, 1000) for _ in range(200))
    b = sorted(random.randint(0, 1000) for _ in range(200))
    expected = merge_two_pointer(a, b)
    assert merge_concat_sort(a, b) == expected
    assert list(merge_generator(iter(a), iter(b))) == expected


def test_empty_inputs() -> None:
    assert merge_two_pointer([], [1, 2]) == [1, 2]
    assert merge_two_pointer([1, 2], []) == [1, 2]
    assert list(merge_generator(iter([]), iter([1, 2]))) == [1, 2]


if __name__ == "__main__":
    sizes = [1_000, 10_000, 100_000, 500_000, 1_000_000, 5_000_000]

    run_speed_benchmark(sizes)

    print()
    run_memory_comparison(sizes)

    print()
    print("Takeaway:")
    print("  Python's Timsort is C-implemented and detects sorted runs,")
    print("  making concat+sort surprisingly fast for in-memory sorted data.")
    print()
    print("  The two-pointer merge wins on a different axis: the generator")
    print("  version processes data in O(1) memory. When merging sorted files")
    print("  that don't fit in RAM, or streaming from Kafka partitions,")
    print("  concat+sort isn't even an option. Two-pointer merge is the only")
    print("  approach that works.")
    print()
    print("  In interviews, know both: mention Timsort's optimization for")
    print("  in-memory work, but explain that two-pointer merge is essential")
    print("  for streaming and out-of-core processing.")
