"""Tests for incremental load detection scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestIncrementalLoad:
    """Test CDC-style detection of new, changed and deleted records."""

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
        """Create source_customers and target_customers tables."""
        sql = (SQL_DIR / "incremental_load.sql").read_text()
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if not stmt:
                continue
            keyword = self._first_keyword(stmt)
            if keyword in ("CREATE", "INSERT"):
                db.execute(stmt)

    def test_new_records_detected(self, db: duckdb.DuckDBPyConnection) -> None:
        """Customer 4 (Dave) is detected as new."""
        self._setup(db)
        result = db.execute("""
            SELECT s.customer_id, s.name
            FROM source_customers s
            LEFT JOIN target_customers t ON s.customer_id = t.customer_id
            WHERE t.customer_id IS NULL
        """).fetchall()
        assert len(result) == 1
        assert result[0][0] == 4
        assert result[0][1] == "Dave"

    def test_changed_records_detected(self, db: duckdb.DuckDBPyConnection) -> None:
        """Customer 1 (Alice) is detected as changed."""
        self._setup(db)
        result = db.execute("""
            SELECT s.customer_id, s.name
            FROM source_customers s
            INNER JOIN target_customers t ON s.customer_id = t.customer_id
            WHERE s.updated_at > t.updated_at
        """).fetchall()
        assert len(result) == 1
        assert result[0][0] == 1
        assert result[0][1] == "Alice"

    def test_deleted_records_detected(self, db: duckdb.DuckDBPyConnection) -> None:
        """Customer 5 (Eve) is detected as deleted."""
        self._setup(db)
        result = db.execute("""
            SELECT t.customer_id, t.name
            FROM target_customers t
            LEFT JOIN source_customers s ON t.customer_id = s.customer_id
            WHERE s.customer_id IS NULL
        """).fetchall()
        assert len(result) == 1
        assert result[0][0] == 5
        assert result[0][1] == "Eve"

    def test_unchanged_records_not_flagged(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """Customers 2 and 3 are unchanged and not flagged in any category."""
        self._setup(db)
        # Unchanged = in both, same updated_at
        result = db.execute("""
            SELECT s.customer_id
            FROM source_customers s
            INNER JOIN target_customers t ON s.customer_id = t.customer_id
            WHERE s.updated_at = t.updated_at
            ORDER BY s.customer_id
        """).fetchall()
        ids = [r[0] for r in result]
        assert ids == [2, 3]
