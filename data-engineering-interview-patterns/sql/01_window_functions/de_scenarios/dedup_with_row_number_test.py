"""Tests for deduplication with ROW_NUMBER scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestDedupWithRowNumber:
    """Test ROW_NUMBER-based deduplication of raw events."""

    def _setup_and_run(self, db: duckdb.DuckDBPyConnection) -> None:
        """Execute the full scenario SQL to set up tables and data."""
        sql = (SQL_DIR / "dedup_with_row_number.sql").read_text()
        # Execute everything except the final SELECT (CREATE, INSERT)
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        for stmt in statements:
            if stmt.upper().lstrip().startswith("SELECT"):
                continue
            # Skip comments-only blocks
            stripped = "\n".join(
                line for line in stmt.split("\n")
                if not line.strip().startswith("--") and not line.strip().startswith("/*")
            ).strip()
            if not stripped:
                continue
            db.execute(stmt)

    def test_correct_unique_combinations(self, db: duckdb.DuckDBPyConnection) -> None:
        """Dedup produces the correct number of unique (user_id, event_type) pairs."""
        self._setup_and_run(db)
        result = db.execute("""
            SELECT COUNT(*) FROM (
                SELECT * FROM (
                    SELECT *,
                           ROW_NUMBER() OVER (
                               PARTITION BY user_id, event_type
                               ORDER BY received_at DESC
                           ) AS rn
                    FROM raw_events
                ) ranked
                WHERE rn = 1
            )
        """).fetchone()
        # 3 unique combos: (100, purchase), (100, login), (200, purchase)
        assert result[0] == 3

    def test_kept_row_is_most_recent(self, db: duckdb.DuckDBPyConnection) -> None:
        """Dedup keeps the most recent row for each (user_id, event_type)."""
        self._setup_and_run(db)
        result = db.execute("""
            SELECT user_id, event_type, received_at FROM (
                SELECT *,
                       ROW_NUMBER() OVER (
                           PARTITION BY user_id, event_type
                           ORDER BY received_at DESC
                       ) AS rn
                FROM raw_events
            ) ranked
            WHERE rn = 1
            ORDER BY user_id, event_type
        """).fetchall()
        # user 100 login: only one record at 09:00
        assert str(result[0][2]) == "2024-01-15 09:00:00"
        # user 100 purchase: latest is 10:00:02
        assert str(result[1][2]) == "2024-01-15 10:00:02"
        # user 200 purchase: latest is 11:00:01
        assert str(result[2][2]) == "2024-01-15 11:00:01"

    def test_no_duplicates_remain(self, db: duckdb.DuckDBPyConnection) -> None:
        """After dedup, no duplicate (user_id, event_type) pairs exist."""
        self._setup_and_run(db)
        result = db.execute("""
            SELECT user_id, event_type, COUNT(*) AS cnt FROM (
                SELECT *,
                       ROW_NUMBER() OVER (
                           PARTITION BY user_id, event_type
                           ORDER BY received_at DESC
                       ) AS rn
                FROM raw_events
            ) ranked
            WHERE rn = 1
            GROUP BY user_id, event_type
            HAVING COUNT(*) > 1
        """).fetchall()
        assert len(result) == 0

    def test_original_data_has_duplicates(self, db: duckdb.DuckDBPyConnection) -> None:
        """Raw data has more rows than unique combinations, confirming duplicates exist."""
        self._setup_and_run(db)
        total_rows = db.execute("SELECT COUNT(*) FROM raw_events").fetchone()[0]
        unique_combos = db.execute(
            "SELECT COUNT(DISTINCT (user_id, event_type)) FROM raw_events"
        ).fetchone()[0]
        assert total_rows == 6
        assert unique_combos == 3
