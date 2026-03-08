"""Tests for change detection with window functions scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestChangeDetection:
    """Test LAG-based change detection on user status history."""

    def _setup(self, db: duckdb.DuckDBPyConnection) -> None:
        """Create and populate the user_status_log table."""
        sql = (SQL_DIR / "change_detection.sql").read_text()
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

    def test_change_events_flagged_correctly(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """Correct rows are flagged as changed vs unchanged."""
        self._setup(db)
        result = db.execute("""
            WITH with_prev AS (
                SELECT *,
                       LAG(status) OVER (
                           PARTITION BY user_id ORDER BY recorded_at
                       ) AS prev_status
                FROM user_status_log
            )
            SELECT log_id, user_id,
                   CASE
                       WHEN prev_status IS NULL THEN 'initial'
                       WHEN prev_status != status THEN 'changed'
                       ELSE 'unchanged'
                   END AS change_type
            FROM with_prev
            ORDER BY user_id, recorded_at
        """).fetchall()
        change_types = {r[0]: r[2] for r in result}
        # User 100: initial, unchanged, changed, unchanged, changed
        assert change_types[1] == "initial"
        assert change_types[2] == "unchanged"
        assert change_types[3] == "changed"
        assert change_types[4] == "unchanged"
        assert change_types[5] == "changed"
        # User 200: initial, unchanged, changed
        assert change_types[6] == "initial"
        assert change_types[7] == "unchanged"
        assert change_types[8] == "changed"

    def test_total_change_count(self, db: duckdb.DuckDBPyConnection) -> None:
        """Correct number of actual status changes detected."""
        self._setup(db)
        result = db.execute("""
            WITH with_prev AS (
                SELECT *,
                       LAG(status) OVER (
                           PARTITION BY user_id ORDER BY recorded_at
                       ) AS prev_status
                FROM user_status_log
            )
            SELECT COUNT(*) FROM with_prev
            WHERE prev_status IS NOT NULL AND prev_status != status
        """).fetchone()
        # 3 changes total: user 100 has 2, user 200 has 1
        assert result[0] == 3

    def test_scd2_validity_ranges(self, db: duckdb.DuckDBPyConnection) -> None:
        """SCD Type 2 ranges have correct valid_from/valid_to for user 100."""
        self._setup(db)
        result = db.execute("""
            WITH with_prev AS (
                SELECT *,
                       LAG(status) OVER (
                           PARTITION BY user_id ORDER BY recorded_at
                       ) AS prev_status
                FROM user_status_log
            ),
            changes_only AS (
                SELECT user_id, status, recorded_at
                FROM with_prev
                WHERE prev_status IS NULL OR prev_status != status
            )
            SELECT user_id, status, recorded_at AS valid_from,
                   LEAD(recorded_at) OVER (
                       PARTITION BY user_id ORDER BY recorded_at
                   ) AS valid_to
            FROM changes_only
            WHERE user_id = 100
            ORDER BY valid_from
        """).fetchall()
        # User 100: active -> inactive -> churned
        assert len(result) == 3
        assert result[0][1] == "active"
        assert result[1][1] == "inactive"
        assert result[2][1] == "churned"
        # Last period has NULL valid_to (current)
        assert result[2][3] is None

    def test_initial_records_detected(self, db: duckdb.DuckDBPyConnection) -> None:
        """Each user's first record is flagged as initial."""
        self._setup(db)
        result = db.execute("""
            WITH with_prev AS (
                SELECT *,
                       LAG(status) OVER (
                           PARTITION BY user_id ORDER BY recorded_at
                       ) AS prev_status
                FROM user_status_log
            )
            SELECT user_id FROM with_prev
            WHERE prev_status IS NULL
            ORDER BY user_id
        """).fetchall()
        user_ids = [r[0] for r in result]
        assert user_ids == [100, 200]
