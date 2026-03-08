"""Tests for LeetCode 297: Serialize and Deserialize Binary Tree."""

import pytest

from tree_node import build_tree, tree_to_list
from p297_serialize_deserialize import Codec, CodecBFS


@pytest.mark.parametrize("CodecClass", [Codec, CodecBFS])
class TestSerializeDeserialize:
    """Test both serialization approaches."""

    def test_roundtrip_basic(self, CodecClass) -> None:
        codec = CodecClass()
        root = build_tree([1, 2, 3, None, None, 4, 5])
        serialized = codec.serialize(root)
        restored = codec.deserialize(serialized)
        assert tree_to_list(restored) == tree_to_list(root)

    def test_roundtrip_empty(self, CodecClass) -> None:
        codec = CodecClass()
        serialized = codec.serialize(None)
        restored = codec.deserialize(serialized)
        assert restored is None

    def test_roundtrip_single(self, CodecClass) -> None:
        codec = CodecClass()
        root = build_tree([1])
        serialized = codec.serialize(root)
        restored = codec.deserialize(serialized)
        assert tree_to_list(restored) == [1]

    def test_roundtrip_left_skewed(self, CodecClass) -> None:
        codec = CodecClass()
        root = build_tree([1, 2, None, 3])
        serialized = codec.serialize(root)
        restored = codec.deserialize(serialized)
        assert tree_to_list(restored) == tree_to_list(root)

    def test_roundtrip_right_skewed(self, CodecClass) -> None:
        codec = CodecClass()
        root = build_tree([1, None, 2, None, 3])
        serialized = codec.serialize(root)
        restored = codec.deserialize(serialized)
        assert tree_to_list(restored) == tree_to_list(root)

    def test_roundtrip_balanced(self, CodecClass) -> None:
        codec = CodecClass()
        root = build_tree([1, 2, 3, 4, 5, 6, 7])
        serialized = codec.serialize(root)
        restored = codec.deserialize(serialized)
        assert tree_to_list(restored) == [1, 2, 3, 4, 5, 6, 7]

    def test_negative_values(self, CodecClass) -> None:
        codec = CodecClass()
        root = build_tree([-1, -2, -3])
        serialized = codec.serialize(root)
        restored = codec.deserialize(serialized)
        assert tree_to_list(restored) == [-1, -2, -3]

    def test_large_values(self, CodecClass) -> None:
        codec = CodecClass()
        root = build_tree([1000, 999, 1001])
        serialized = codec.serialize(root)
        restored = codec.deserialize(serialized)
        assert tree_to_list(restored) == [1000, 999, 1001]
