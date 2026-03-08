"""Tests for anti-join patterns scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestAntiJoins:
    """Test anti-join approaches for finding missing partitions."""

    def _setup(self, db: duckdb.DuckDBPyConnection) -> None:
        """Create expected_dates and actual_partitions tables."""
        sql = (SQL_DIR / "anti_joins.sql").read_text()
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if not stmt:
                continue
            upper = stmt.upper().lstrip()
            if upper.startswith("SELECT") or upper.startswith("--"):
                continue
            stripped = "\n".join(
                line for line in stmt.split("\n")
                if not line.strip().startswith("--") and not line.strip().startswith("/*")
            ).strip()
            if not stripped:
                continue
            db.execute(stmt)

    def test_left_join_finds_missing_dates(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """LEFT JOIN + IS NULL finds the two missing dates."""
        self._setup(db)
        result = db.execute("""
            SELECT e.partition_date AS missing_date
            FROM expected_dates e
            LEFT JOIN actual_partitions a ON e.partition_date = a.partition_date
            WHERE a.partition_date IS NULL
            ORDER BY missing_date
        """).fetchall()
        missing = [str(r[0]) for r in result]
        assert missing == ["2024-01-04", "2024-01-06"]

    def test_not_exists_finds_missing_dates(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """NOT EXISTS finds the same missing dates."""
        self._setup(db)
        result = db.execute("""
            SELECT e.partition_date AS missing_date
            FROM expected_dates e
            WHERE NOT EXISTS (
                SELECT 1 FROM actual_partitions a
                WHERE a.partition_date = e.partition_date
            )
            ORDER BY missing_date
        """).fetchall()
        missing = [str(r[0]) for r in result]
        assert missing == ["2024-01-04", "2024-01-06"]

    def test_not_in_finds_missing_dates(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """NOT IN finds the same missing dates."""
        self._setup(db)
        result = db.execute("""
            SELECT partition_date AS missing_date
            FROM expected_dates
            WHERE partition_date NOT IN (
                SELECT partition_date FROM actual_partitions
                WHERE partition_date IS NOT NULL
            )
            ORDER BY missing_date
        """).fetchall()
        missing = [str(r[0]) for r in result]
        assert missing == ["2024-01-04", "2024-01-06"]

    def test_all_approaches_match(self, db: duckdb.DuckDBPyConnection) -> None:
        """All three anti-join approaches return identical results."""
        self._setup(db)
        left_join = db.execute("""
            SELECT e.partition_date
            FROM expected_dates e
            LEFT JOIN actual_partitions a ON e.partition_date = a.partition_date
            WHERE a.partition_date IS NULL
            ORDER BY e.partition_date
        """).fetchall()
        not_exists = db.execute("""
            SELECT e.partition_date
            FROM expected_dates e
            WHERE NOT EXISTS (
                SELECT 1 FROM actual_partitions a
                WHERE a.partition_date = e.partition_date
            )
            ORDER BY e.partition_date
        """).fetchall()
        not_in = db.execute("""
            SELECT partition_date
            FROM expected_dates
            WHERE partition_date NOT IN (
                SELECT partition_date FROM actual_partitions
                WHERE partition_date IS NOT NULL
            )
            ORDER BY partition_date
        """).fetchall()
        assert left_join == not_exists == not_in
