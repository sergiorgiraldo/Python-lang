"""Tests for LeetCode 146: LRU Cache."""

from p146_lru_cache import LRUCache, LRUCacheManual


class TestLRUCache:
    """Test the OrderedDict-based implementation."""

    def test_basic_operations(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        assert cache.get(1) == 1

    def test_eviction(self):
        """Adding beyond capacity evicts least recently used."""
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(3, 3)  # evicts key 1
        assert cache.get(1) == -1
        assert cache.get(3) == 3

    def test_get_updates_recency(self):
        """Accessing a key makes it most recently used."""
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.get(1)  # key 1 is now most recent
        cache.put(3, 3)  # evicts key 2, not key 1
        assert cache.get(1) == 1
        assert cache.get(2) == -1

    def test_update_existing_key(self):
        """Putting an existing key updates value and recency."""
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(1, 10)  # update key 1
        assert cache.get(1) == 10
        cache.put(3, 3)  # should evict key 2, not key 1
        assert cache.get(2) == -1

    def test_miss(self):
        cache = LRUCache(1)
        assert cache.get(999) == -1

    def test_capacity_one(self):
        cache = LRUCache(1)
        cache.put(1, 1)
        cache.put(2, 2)  # evicts key 1
        assert cache.get(1) == -1
        assert cache.get(2) == 2

    def test_sequence_of_operations(self):
        """Full sequence matching LeetCode example."""
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        assert cache.get(1) == 1
        cache.put(3, 3)
        assert cache.get(2) == -1
        cache.put(4, 4)
        assert cache.get(1) == -1
        assert cache.get(3) == 3
        assert cache.get(4) == 4


class TestLRUCacheManual:
    """Verify manual implementation matches OrderedDict version."""

    def test_basic_operations(self):
        cache = LRUCacheManual(2)
        cache.put(1, 1)
        cache.put(2, 2)
        assert cache.get(1) == 1

    def test_eviction(self):
        cache = LRUCacheManual(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(3, 3)
        assert cache.get(1) == -1
        assert cache.get(3) == 3

    def test_get_updates_recency(self):
        cache = LRUCacheManual(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.get(1)
        cache.put(3, 3)
        assert cache.get(1) == 1
        assert cache.get(2) == -1

    def test_update_existing_key(self):
        cache = LRUCacheManual(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(1, 10)
        assert cache.get(1) == 10
        cache.put(3, 3)
        assert cache.get(2) == -1

    def test_full_sequence(self):
        """Same sequence as OrderedDict test."""
        cache = LRUCacheManual(2)
        cache.put(1, 1)
        cache.put(2, 2)
        assert cache.get(1) == 1
        cache.put(3, 3)
        assert cache.get(2) == -1
        cache.put(4, 4)
        assert cache.get(1) == -1
        assert cache.get(3) == 3
        assert cache.get(4) == 4
