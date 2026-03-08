"""Tests for sessionization with window functions scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestSessionization:
    """Test clickstream sessionization with 30-minute idle timeout."""

    def _setup(self, db: duckdb.DuckDBPyConnection) -> None:
        """Create and populate the clickstream table."""
        sql = (SQL_DIR / "sessionization.sql").read_text()
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if not stmt or stmt.upper().lstrip().startswith("SELECT"):
                continue
            if stmt.upper().lstrip().startswith("WITH"):
                continue
            stripped = "\n".join(
                line for line in stmt.split("\n")
                if not line.strip().startswith("--") and not line.strip().startswith("/*")
            ).strip()
            if not stripped:
                continue
            db.execute(stmt)

    def _sessionize(self, db: duckdb.DuckDBPyConnection) -> list[tuple]:
        """Run the sessionization query and return results."""
        return db.execute("""
            WITH with_gaps AS (
                SELECT *,
                       LAG(event_time) OVER (
                           PARTITION BY user_id ORDER BY event_time
                       ) AS prev_event_time,
                       EXTRACT(EPOCH FROM (
                           event_time - LAG(event_time) OVER (
                               PARTITION BY user_id ORDER BY event_time
                           )
                       )) / 60.0 AS gap_minutes
                FROM clickstream
            ),
            with_flags AS (
                SELECT *,
                       CASE
                           WHEN gap_minutes IS NULL THEN 1
                           WHEN gap_minutes > 30 THEN 1
                           ELSE 0
                       END AS new_session_flag
                FROM with_gaps
            )
            SELECT user_id, event_time, page, gap_minutes,
                   new_session_flag,
                   SUM(new_session_flag) OVER (
                       PARTITION BY user_id ORDER BY event_time
                   ) AS session_id
            FROM with_flags
            ORDER BY user_id, event_time
        """).fetchall()

    def test_total_sessions_per_user(self, db: duckdb.DuckDBPyConnection) -> None:
        """User 1 has 2 sessions, user 2 has 2 sessions."""
        self._setup(db)
        result = self._sessionize(db)
        user1_sessions = {r[5] for r in result if r[0] == 1}
        user2_sessions = {r[5] for r in result if r[0] == 2}
        assert len(user1_sessions) == 2
        assert len(user2_sessions) == 2

    def test_session_boundary_at_gap(self, db: duckdb.DuckDBPyConnection) -> None:
        """New session starts after a gap > 30 minutes."""
        self._setup(db)
        result = self._sessionize(db)
        # User 1's event at 12:00 (after 2-hour gap) should be session 2
        user1_noon = [r for r in result if r[0] == 1 and "12:00:00" in str(r[1])]
        assert len(user1_noon) == 1
        assert user1_noon[0][5] == 2  # session_id = 2

    def test_events_within_session_share_id(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """Events within the same session share a session_id."""
        self._setup(db)
        result = self._sessionize(db)
        # User 1's first 4 events (10:00 to 10:15) should all be session 1
        user1_session1 = [r for r in result if r[0] == 1 and r[5] == 1]
        assert len(user1_session1) == 4

    def test_all_events_accounted_for(self, db: duckdb.DuckDBPyConnection) -> None:
        """Sessionization produces a row for every input event."""
        self._setup(db)
        result = self._sessionize(db)
        total_events = db.execute("SELECT COUNT(*) FROM clickstream").fetchone()[0]
        assert len(result) == total_events
