"""Tests for LeetCode 981: Time Based Key-Value Store."""

import pytest
from p981_time_map import TimeMap, TimeMapManual


class TestTimeMap:
    """Test the bisect-based implementation."""

    def test_exact_timestamp(self):
        tm = TimeMap()
        tm.set("foo", "bar", 1)
        assert tm.get("foo", 1) == "bar"

    def test_later_timestamp(self):
        tm = TimeMap()
        tm.set("foo", "bar", 1)
        assert tm.get("foo", 3) == "bar"

    def test_multiple_values(self):
        tm = TimeMap()
        tm.set("foo", "bar", 1)
        tm.set("foo", "bar2", 4)
        assert tm.get("foo", 4) == "bar2"
        assert tm.get("foo", 5) == "bar2"

    def test_between_timestamps(self):
        tm = TimeMap()
        tm.set("foo", "bar", 1)
        tm.set("foo", "bar2", 4)
        assert tm.get("foo", 3) == "bar"

    def test_before_all(self):
        tm = TimeMap()
        tm.set("foo", "bar", 1)
        assert tm.get("foo", 0) == ""

    def test_missing_key(self):
        tm = TimeMap()
        assert tm.get("missing", 1) == ""

    def test_multiple_keys(self):
        tm = TimeMap()
        tm.set("a", "val_a", 1)
        tm.set("b", "val_b", 2)
        assert tm.get("a", 5) == "val_a"
        assert tm.get("b", 5) == "val_b"

    def test_many_timestamps(self):
        tm = TimeMap()
        for i in range(1, 101):
            tm.set("k", f"v{i}", i * 10)
        assert tm.get("k", 10) == "v1"
        assert tm.get("k", 55) == "v5"
        assert tm.get("k", 1000) == "v100"
        assert tm.get("k", 5) == ""

    def test_overwrite_semantic(self):
        """Different from a regular dict - both values exist at different times."""
        tm = TimeMap()
        tm.set("key", "old", 1)
        tm.set("key", "new", 2)
        assert tm.get("key", 1) == "old"
        assert tm.get("key", 2) == "new"


class TestTimeMapManual:
    """Manual binary search should match bisect version."""

    def test_basic_operations(self):
        tm = TimeMapManual()
        tm.set("foo", "bar", 1)
        tm.set("foo", "bar2", 4)
        assert tm.get("foo", 1) == "bar"
        assert tm.get("foo", 3) == "bar"
        assert tm.get("foo", 4) == "bar2"
        assert tm.get("foo", 5) == "bar2"
        assert tm.get("foo", 0) == ""

    @pytest.mark.parametrize(
        "timestamp,expected",
        [
            (1, "bar"),
            (3, "bar"),
            (4, "bar2"),
            (5, "bar2"),
            (0, ""),
        ],
    )
    def test_matches_bisect(self, timestamp, expected):
        """Both implementations should agree."""
        tm_bisect = TimeMap()
        tm_manual = TimeMapManual()

        tm_bisect.set("foo", "bar", 1)
        tm_bisect.set("foo", "bar2", 4)
        tm_manual.set("foo", "bar", 1)
        tm_manual.set("foo", "bar2", 4)

        assert tm_bisect.get("foo", timestamp) == tm_manual.get("foo", timestamp)
