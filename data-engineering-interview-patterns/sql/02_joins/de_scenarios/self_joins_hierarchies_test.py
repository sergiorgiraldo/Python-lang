"""Tests for self-joins hierarchies scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestSelfJoinsHierarchies:
    """Test two-level self-join for org chart traversal."""

    def _setup(self, db: duckdb.DuckDBPyConnection) -> None:
        """Create and populate the org_chart table."""
        sql = (SQL_DIR / "self_joins_hierarchies.sql").read_text()
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if not stmt:
                continue
            upper = stmt.upper().lstrip()
            if upper.startswith("SELECT"):
                continue
            stripped = "\n".join(
                line for line in stmt.split("\n")
                if not line.strip().startswith("--") and not line.strip().startswith("/*")
            ).strip()
            if not stripped:
                continue
            db.execute(stmt)

    def test_ceo_has_no_manager(self, db: duckdb.DuckDBPyConnection) -> None:
        """CEO (Alice) has NULL manager and director."""
        self._setup(db)
        result = db.execute("""
            SELECT e.name AS employee, m.name AS manager, d.name AS director
            FROM org_chart e
            LEFT JOIN org_chart m ON e.manager_id = m.emp_id
            LEFT JOIN org_chart d ON m.manager_id = d.emp_id
            WHERE e.name = 'Alice'
        """).fetchone()
        assert result[1] is None  # no manager
        assert result[2] is None  # no director

    def test_two_level_chain(self, db: duckdb.DuckDBPyConnection) -> None:
        """Frank's manager is Dave, director is Bob."""
        self._setup(db)
        result = db.execute("""
            SELECT e.name AS employee, m.name AS manager, d.name AS director
            FROM org_chart e
            LEFT JOIN org_chart m ON e.manager_id = m.emp_id
            LEFT JOIN org_chart d ON m.manager_id = d.emp_id
            WHERE e.name = 'Frank'
        """).fetchone()
        assert result[1] == "Dave"
        assert result[2] == "Bob"

    def test_all_employees_present(self, db: duckdb.DuckDBPyConnection) -> None:
        """Self-join result includes all 9 employees."""
        self._setup(db)
        result = db.execute("""
            SELECT COUNT(*)
            FROM org_chart e
            LEFT JOIN org_chart m ON e.manager_id = m.emp_id
            LEFT JOIN org_chart d ON m.manager_id = d.emp_id
        """).fetchone()
        assert result[0] == 9

    def test_deepest_employee_chain(self, db: duckdb.DuckDBPyConnection) -> None:
        """Ivy (deepest) has Frank as manager and Dave as director."""
        self._setup(db)
        result = db.execute("""
            SELECT e.name AS employee, m.name AS manager, d.name AS director
            FROM org_chart e
            LEFT JOIN org_chart m ON e.manager_id = m.emp_id
            LEFT JOIN org_chart d ON m.manager_id = d.emp_id
            WHERE e.name = 'Ivy'
        """).fetchone()
        assert result[1] == "Frank"
        assert result[2] == "Dave"
