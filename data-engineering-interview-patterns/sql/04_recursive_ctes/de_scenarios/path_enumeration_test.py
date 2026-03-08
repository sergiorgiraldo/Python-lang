"""Tests for path enumeration with recursive CTE scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestPathEnumeration:
    """Test building full paths from root to each node in hierarchy."""

    def _setup(self, db: duckdb.DuckDBPyConnection) -> None:
        """Create and populate the org_chart table."""
        sql = (SQL_DIR / "path_enumeration.sql").read_text()
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if not stmt:
                continue
            upper = stmt.upper().lstrip()
            if upper.startswith("SELECT") or upper.startswith("WITH"):
                continue
            stripped = "\n".join(
                line for line in stmt.split("\n")
                if not line.strip().startswith("--") and not line.strip().startswith("/*")
            ).strip()
            if not stripped:
                continue
            db.execute(stmt)

    def _get_paths(self, db: duckdb.DuckDBPyConnection) -> list[tuple]:
        """Run the path enumeration query."""
        return db.execute("""
            WITH RECURSIVE paths AS (
                SELECT emp_id, name, manager_id,
                       name AS full_path,
                       1 AS depth
                FROM org_chart
                WHERE manager_id IS NULL

                UNION ALL

                SELECT o.emp_id, o.name, o.manager_id,
                       p.full_path || ' / ' || o.name AS full_path,
                       p.depth + 1
                FROM org_chart o
                JOIN paths p ON o.manager_id = p.emp_id
            )
            SELECT emp_id, name, full_path, depth
            FROM paths
            ORDER BY full_path
        """).fetchall()

    def test_root_path_is_just_name(self, db: duckdb.DuckDBPyConnection) -> None:
        """CEO's path is just 'CEO'."""
        self._setup(db)
        paths = self._get_paths(db)
        ceo = [r for r in paths if r[1] == "CEO"][0]
        assert ceo[2] == "CEO"

    def test_leaf_node_full_path(self, db: duckdb.DuckDBPyConnection) -> None:
        """Junior IC's path is 'CEO / VP Engineering / Director Backend / Manager API / Junior IC'."""
        self._setup(db)
        paths = self._get_paths(db)
        junior = [r for r in paths if r[1] == "Junior IC"][0]
        expected = "CEO / VP Engineering / Director Backend / Manager API / Junior IC"
        assert junior[2] == expected

    def test_all_nodes_have_paths(self, db: duckdb.DuckDBPyConnection) -> None:
        """Every employee in org_chart has a path."""
        self._setup(db)
        paths = self._get_paths(db)
        total = db.execute("SELECT COUNT(*) FROM org_chart").fetchone()[0]
        assert len(paths) == total

    def test_depth_matches_path_segments(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """Depth equals the number of segments in the path for each node."""
        self._setup(db)
        paths = self._get_paths(db)
        for row in paths:
            path_segments = row[2].count(" / ") + 1
            assert row[3] == path_segments
