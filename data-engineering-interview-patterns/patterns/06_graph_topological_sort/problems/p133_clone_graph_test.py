"""Tests for LeetCode 133: Clone Graph."""

from p133_clone_graph import (
    Node,
    build_graph,
    clone_graph_bfs,
    clone_graph_dfs,
    graph_to_adj_list,
)


def verify_clone(original, cloned, adj_list):
    """Verify clone is correct and independent of original."""
    assert cloned is not original
    assert graph_to_adj_list(cloned) == adj_list

    # Verify no shared node objects
    orig_nodes = collect_nodes(original)
    clone_nodes = collect_nodes(cloned)
    for cn in clone_nodes:
        assert cn not in orig_nodes


def collect_nodes(node):
    """Collect all node objects reachable from a starting node."""
    if not node:
        return set()
    visited = set()
    stack = [node]
    while stack:
        n = stack.pop()
        if n not in visited:
            visited.add(n)
            stack.extend(n.neighbors)
    return visited


class TestCloneGraphBFS:
    def test_example(self):
        adj = [[2, 4], [1, 3], [2, 4], [1, 3]]
        original = build_graph(adj)
        cloned = clone_graph_bfs(original)
        verify_clone(original, cloned, adj)

    def test_single_node(self):
        node = Node(1)
        cloned = clone_graph_bfs(node)
        assert cloned is not node
        assert cloned.val == 1
        assert cloned.neighbors == []

    def test_none(self):
        assert clone_graph_bfs(None) is None

    def test_two_nodes(self):
        adj = [[2], [1]]
        original = build_graph(adj)
        cloned = clone_graph_bfs(original)
        verify_clone(original, cloned, adj)

    def test_self_loop(self):
        node = Node(1)
        node.neighbors = [node]
        cloned = clone_graph_bfs(node)
        assert cloned is not node
        assert cloned.val == 1
        assert len(cloned.neighbors) == 1
        assert cloned.neighbors[0] is cloned


class TestCloneGraphDFS:
    def test_example(self):
        adj = [[2, 4], [1, 3], [2, 4], [1, 3]]
        original = build_graph(adj)
        cloned = clone_graph_dfs(original)
        verify_clone(original, cloned, adj)

    def test_single_node(self):
        node = Node(1)
        cloned = clone_graph_dfs(node)
        assert cloned is not node
        assert cloned.val == 1

    def test_none(self):
        assert clone_graph_dfs(None) is None

    def test_self_loop(self):
        node = Node(1)
        node.neighbors = [node]
        cloned = clone_graph_dfs(node)
        assert cloned.neighbors[0] is cloned
