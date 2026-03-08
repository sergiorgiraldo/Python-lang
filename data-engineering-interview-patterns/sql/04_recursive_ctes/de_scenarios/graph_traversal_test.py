"""Tests for graph traversal with recursive CTE scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestGraphTraversal:
    """Test BFS shortest path and connected components via recursive CTE."""

    @staticmethod
    def _first_keyword(stmt: str) -> str:
        """Return the first SQL keyword after stripping comments."""
        in_block = False
        for line in stmt.split("\n"):
            line = line.strip()
            if in_block:
                if "*/" in line:
                    in_block = False
                continue
            if not line or line.startswith("--"):
                continue
            if line.startswith("/*"):
                if "*/" not in line:
                    in_block = True
                continue
            return line.split()[0].upper() if line.split() else ""
        return ""

    def _setup(self, db: duckdb.DuckDBPyConnection) -> None:
        """Create the edges table with bidirectional edges."""
        sql = (SQL_DIR / "graph_traversal.sql").read_text()
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if not stmt:
                continue
            keyword = self._first_keyword(stmt)
            if keyword in ("CREATE", "INSERT"):
                db.execute(stmt)

    def test_bfs_shortest_distances(self, db: duckdb.DuckDBPyConnection) -> None:
        """BFS from node 1 produces correct shortest distances."""
        self._setup(db)
        result = db.execute("""
            WITH RECURSIVE bfs AS (
                SELECT 1 AS node, 0 AS distance, [1] AS path

                UNION ALL

                SELECT e.dst AS node, b.distance + 1,
                       list_append(b.path, e.dst)
                FROM edges e
                JOIN bfs b ON e.src = b.node
                WHERE NOT list_contains(b.path, e.dst)
            )
            SELECT node, MIN(distance) AS shortest_distance
            FROM bfs
            GROUP BY node
            ORDER BY node
        """).fetchall()
        dist_map = {r[0]: r[1] for r in result}
        assert dist_map[1] == 0  # start node
        assert dist_map[2] == 1  # direct neighbor
        assert dist_map[3] == 2  # 1->2->3
        assert dist_map[4] == 3  # 1->2->3->4

    def test_unreachable_nodes(self, db: duckdb.DuckDBPyConnection) -> None:
        """Nodes 5 and 6 are unreachable from node 1."""
        self._setup(db)
        result = db.execute("""
            WITH RECURSIVE bfs AS (
                SELECT 1 AS node, 0 AS distance, [1] AS path

                UNION ALL

                SELECT e.dst AS node, b.distance + 1,
                       list_append(b.path, e.dst)
                FROM edges e
                JOIN bfs b ON e.src = b.node
                WHERE NOT list_contains(b.path, e.dst)
            )
            SELECT DISTINCT node FROM bfs
        """).fetchall()
        reachable = {r[0] for r in result}
        assert 5 not in reachable
        assert 6 not in reachable

    def test_connected_components(self, db: duckdb.DuckDBPyConnection) -> None:
        """Graph has two connected components: {1,2,3,4} and {5,6}."""
        self._setup(db)
        result = db.execute("""
            WITH RECURSIVE reachable AS (
                SELECT src AS node, src AS reachable_node
                FROM (SELECT DISTINCT src FROM edges) nodes

                UNION

                SELECT r.node, e.dst AS reachable_node
                FROM reachable r
                JOIN edges e ON r.reachable_node = e.src
            )
            SELECT node, MIN(reachable_node) AS component_id
            FROM reachable
            GROUP BY node
            ORDER BY component_id, node
        """).fetchall()
        comp_map = {r[0]: r[1] for r in result}
        # Component 1: nodes 1,2,3,4 all have component_id = 1
        assert comp_map[1] == 1
        assert comp_map[2] == 1
        assert comp_map[3] == 1
        assert comp_map[4] == 1
        # Component 2: nodes 5,6 both have component_id = 5
        assert comp_map[5] == 5
        assert comp_map[6] == 5

    def test_two_components_total(self, db: duckdb.DuckDBPyConnection) -> None:
        """There are exactly 2 connected components."""
        self._setup(db)
        result = db.execute("""
            WITH RECURSIVE reachable AS (
                SELECT src AS node, src AS reachable_node
                FROM (SELECT DISTINCT src FROM edges) nodes

                UNION

                SELECT r.node, e.dst AS reachable_node
                FROM reachable r
                JOIN edges e ON r.reachable_node = e.src
            )
            SELECT COUNT(DISTINCT component_id) FROM (
                SELECT node, MIN(reachable_node) AS component_id
                FROM reachable
                GROUP BY node
            )
        """).fetchone()
        assert result[0] == 2
