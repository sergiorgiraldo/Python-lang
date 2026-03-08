"""
Hash Map Pattern Templates

Reusable code patterns for hash map-based problems. These templates cover
the most common variations you'll encounter in interviews and production code.
"""

from collections import defaultdict
from collections.abc import Callable, Hashable
from typing import TypeVar

# Hashable = any type usable as a dict key (implements __hash__)
T = TypeVar("T")


def complement_lookup(nums: list[int], target: int) -> list[int]:
    """
    Find two elements that satisfy a target condition using complement lookup.

    The classic "Two Sum" pattern. For each element, compute what value
    would complete the condition, then check if we've seen it.

    Time: O(n)  Space: O(n)
    """
    seen: dict[int, int] = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []


def frequency_count(items: list[Hashable]) -> dict[Hashable, int]:
    """
    Count occurrences of each item.

    Equivalent to collections.Counter but shows the pattern explicitly.
    Use Counter in production - use this to demonstrate understanding.

    Time: O(n)  Space: O(n)
    """
    counts: dict[Hashable, int] = defaultdict(int)
    for item in items:
        counts[item] += 1
    return dict(counts)


def group_by_key(
    records: list[T], key_func: Callable[[T], Hashable]
) -> dict[Hashable, list[T]]:
    """
    Group records by a computed key.

    This is the Python equivalent of SQL's GROUP BY. Pass a function
    that extracts the grouping key from each record.

    Time: O(n)  Space: O(n)
    """
    groups: dict[Hashable, list[T]] = defaultdict(list)
    for record in records:
        groups[key_func(record)].append(record)
    return dict(groups)


def find_duplicates(items: list[Hashable]) -> set[Hashable]:
    """
    Find all items that appear more than once.

    Uses a set for O(1) membership checks. Returns a set of
    duplicate values (not indices).

    Time: O(n)  Space: O(n)
    """
    seen: set[Hashable] = set()
    duplicates: set[Hashable] = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return duplicates


def existence_check(items: list[Hashable]) -> set[Hashable]:
    """
    Build a set for O(1) membership testing.

    When you only need to check "have we seen this?" without
    tracking counts or indices, a set is simpler and sufficient.

    Time: O(n)  Space: O(n)
    """
    return set(items)


# ============================================================
# Choosing the Right Dict Idiom
# ============================================================
#
# Python offers several ways to handle missing keys. We use
# different ones across this pattern's problems depending on
# what's clearest for each situation. Here's when to use each:
#
# 1. dict.get(key, default)
#    Best for: one-off lookups where you want a fallback value.
#    Example: complement = seen.get(target - num, -1)
#
# 2. defaultdict(factory)
#    Best for: accumulation patterns (counting, grouping) where
#    every key gets the same initial value.
#    Example: counts = defaultdict(int); counts[item] += 1
#    Example: groups = defaultdict(list); groups[key].append(val)
#
# 3. collections.Counter
#    Best for: frequency counting specifically. It's a defaultdict(int)
#    with extras: most_common(), subtraction, and initialization from
#    an iterable.
#    Example: counts = Counter(items)  # one line
#
# 4. dict.setdefault(key, default)
#    Best for: rare cases where you want to insert-if-missing and get
#    the value in one call. Less readable than defaultdict for most
#    accumulation patterns.
#    Example: d.setdefault(key, []).append(val)
#
# 5. Plain dict with `in` check
#    Best for: when the logic differs between "key exists" and "key
#    doesn't exist" (like Two Sum, where you check then insert).
#    Example: if complement in seen: return ...
#
# In interviews, use whatever is clearest. Interviewers care about
# the algorithm, not which dict method you picked. That said,
# knowing the tradeoffs shows depth if they ask.
