"""Tests for hierarchy traversal with recursive CTE scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestHierarchyTraversal:
    """Test recursive CTE for org chart traversal."""

    def _setup(self, db: duckdb.DuckDBPyConnection) -> None:
        """Create and populate the org_chart table."""
        sql = (SQL_DIR / "hierarchy_traversal.sql").read_text()
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

    def test_all_descendants_found(self, db: duckdb.DuckDBPyConnection) -> None:
        """VP Engineering (id=2) has 5 descendants total."""
        self._setup(db)
        result = db.execute("""
            WITH RECURSIVE reports AS (
                SELECT emp_id, name, manager_id, 1 AS depth
                FROM org_chart
                WHERE manager_id = 2

                UNION ALL

                SELECT o.emp_id, o.name, o.manager_id, r.depth + 1
                FROM org_chart o
                JOIN reports r ON o.manager_id = r.emp_id
            )
            SELECT COUNT(*) FROM reports
        """).fetchone()
        # Direct: Director Backend(4), Director Frontend(5)
        # Under 4: Manager API(6) -> Senior IC(7), Junior IC(8)
        assert result[0] == 5

    def test_correct_depth_values(self, db: duckdb.DuckDBPyConnection) -> None:
        """Depth values are correct for each level under VP Engineering."""
        self._setup(db)
        result = db.execute("""
            WITH RECURSIVE reports AS (
                SELECT emp_id, name, manager_id, 1 AS depth
                FROM org_chart
                WHERE manager_id = 2

                UNION ALL

                SELECT o.emp_id, o.name, o.manager_id, r.depth + 1
                FROM org_chart o
                JOIN reports r ON o.manager_id = r.emp_id
            )
            SELECT name, depth FROM reports ORDER BY depth, name
        """).fetchall()
        depth_map = {r[0]: r[1] for r in result}
        assert depth_map["Director Backend"] == 1
        assert depth_map["Director Frontend"] == 1
        assert depth_map["Manager API"] == 2
        assert depth_map["Junior IC"] == 3
        assert depth_map["Senior IC"] == 3

    def test_sales_branch_not_included(self, db: duckdb.DuckDBPyConnection) -> None:
        """VP Sales branch is not included in VP Engineering's reports."""
        self._setup(db)
        result = db.execute("""
            WITH RECURSIVE reports AS (
                SELECT emp_id, name, manager_id, 1 AS depth
                FROM org_chart
                WHERE manager_id = 2

                UNION ALL

                SELECT o.emp_id, o.name, o.manager_id, r.depth + 1
                FROM org_chart o
                JOIN reports r ON o.manager_id = r.emp_id
            )
            SELECT name FROM reports
        """).fetchall()
        names = {r[0] for r in result}
        assert "VP Sales" not in names
        assert "Sales Lead" not in names

    def test_max_depth(self, db: duckdb.DuckDBPyConnection) -> None:
        """Maximum depth under VP Engineering is 3."""
        self._setup(db)
        result = db.execute("""
            WITH RECURSIVE reports AS (
                SELECT emp_id, name, manager_id, 1 AS depth
                FROM org_chart
                WHERE manager_id = 2

                UNION ALL

                SELECT o.emp_id, o.name, o.manager_id, r.depth + 1
                FROM org_chart o
                JOIN reports r ON o.manager_id = r.emp_id
            )
            SELECT MAX(depth) FROM reports
        """).fetchone()
        assert result[0] == 3
