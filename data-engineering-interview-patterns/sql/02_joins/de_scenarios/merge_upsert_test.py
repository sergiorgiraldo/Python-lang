"""Tests for merge/upsert patterns scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestMergeUpsert:
    """Test INSERT ON CONFLICT upsert behavior."""

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
        """Create dim_customer and staging_customer, then run upsert."""
        sql = (SQL_DIR / "merge_upsert.sql").read_text()
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if not stmt:
                continue
            keyword = self._first_keyword(stmt)
            if keyword in ("CREATE", "INSERT"):
                db.execute(stmt)

    def test_new_row_inserted(self, db: duckdb.DuckDBPyConnection) -> None:
        """Customer 4 (Dave) is inserted as a new row."""
        self._setup(db)
        result = db.execute("""
            SELECT name, email FROM dim_customer WHERE customer_id = 4
        """).fetchone()
        assert result is not None
        assert result[0] == "Dave"
        assert result[1] == "dave@example.com"

    def test_existing_row_updated(self, db: duckdb.DuckDBPyConnection) -> None:
        """Customer 1 (Alice) has email updated from old to new."""
        self._setup(db)
        result = db.execute("""
            SELECT email FROM dim_customer WHERE customer_id = 1
        """).fetchone()
        assert result[0] == "alice@new.com"

    def test_unchanged_row_preserved(self, db: duckdb.DuckDBPyConnection) -> None:
        """Customer 2 (Bob) remains unchanged after upsert."""
        self._setup(db)
        result = db.execute("""
            SELECT name, email FROM dim_customer WHERE customer_id = 2
        """).fetchone()
        assert result[0] == "Bob"
        assert result[1] == "bob@example.com"

    def test_total_row_count(self, db: duckdb.DuckDBPyConnection) -> None:
        """After upsert, dim_customer has 4 rows (3 original + 1 new)."""
        self._setup(db)
        result = db.execute("SELECT COUNT(*) FROM dim_customer").fetchone()
        assert result[0] == 4

    def test_unstaged_row_not_deleted(self, db: duckdb.DuckDBPyConnection) -> None:
        """Customer 3 (Carol) not in staging is still in dim (upsert does not delete)."""
        self._setup(db)
        result = db.execute("""
            SELECT name FROM dim_customer WHERE customer_id = 3
        """).fetchone()
        assert result is not None
        assert result[0] == "Carol"
