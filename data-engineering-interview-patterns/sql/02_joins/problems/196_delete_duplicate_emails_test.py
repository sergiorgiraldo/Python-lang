"""Tests for LeetCode 196: Delete Duplicate Emails."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


def _remaining_rows(conn):
    """Query the table after deletion to see what remains."""
    result = conn.execute("SELECT id, email FROM Person_Email ORDER BY id")
    columns = [desc[0] for desc in result.description]
    return [dict(zip(columns, row)) for row in result.fetchall()]


class TestDeleteDuplicateEmails:

    def test_basic_dedup(self, db_email) -> None:
        db_email.execute("""
            INSERT INTO Person_Email (id, email) VALUES
                (1, 'john@example.com'),
                (2, 'bob@example.com'),
                (3, 'john@example.com');
        """)
        run_sql_file_df(db_email, PROBLEM_DIR / "196_delete_duplicate_emails.sql")
        remaining = _remaining_rows(db_email)
        assert len(remaining) == 2
        ids = {r["id"] for r in remaining}
        assert ids == {1, 2}

    def test_no_duplicates(self, db_email) -> None:
        db_email.execute("""
            INSERT INTO Person_Email (id, email) VALUES
                (1, 'john@example.com'),
                (2, 'bob@example.com');
        """)
        run_sql_file_df(db_email, PROBLEM_DIR / "196_delete_duplicate_emails.sql")
        remaining = _remaining_rows(db_email)
        assert len(remaining) == 2

    def test_all_same_email(self, db_email) -> None:
        db_email.execute("""
            INSERT INTO Person_Email (id, email) VALUES
                (1, 'john@example.com'),
                (2, 'john@example.com'),
                (3, 'john@example.com');
        """)
        run_sql_file_df(db_email, PROBLEM_DIR / "196_delete_duplicate_emails.sql")
        remaining = _remaining_rows(db_email)
        assert len(remaining) == 1
        assert remaining[0]["id"] == 1

    def test_keeps_smallest_id(self, db_email) -> None:
        db_email.execute("""
            INSERT INTO Person_Email (id, email) VALUES
                (5, 'a@test.com'),
                (2, 'a@test.com'),
                (9, 'a@test.com');
        """)
        run_sql_file_df(db_email, PROBLEM_DIR / "196_delete_duplicate_emails.sql")
        remaining = _remaining_rows(db_email)
        assert len(remaining) == 1
        assert remaining[0]["id"] == 2


class TestDeleteDuplicateEmailsAlt:

    def test_basic_dedup(self, db_email) -> None:
        db_email.execute("""
            INSERT INTO Person_Email (id, email) VALUES
                (1, 'john@example.com'),
                (2, 'bob@example.com'),
                (3, 'john@example.com');
        """)
        run_sql_file_df(db_email, PROBLEM_DIR / "196_delete_duplicate_emails_alt.sql")
        remaining = _remaining_rows(db_email)
        assert len(remaining) == 2
        ids = {r["id"] for r in remaining}
        assert ids == {1, 2}

    def test_all_same_email(self, db_email) -> None:
        db_email.execute("""
            INSERT INTO Person_Email (id, email) VALUES
                (1, 'john@example.com'),
                (2, 'john@example.com'),
                (3, 'john@example.com');
        """)
        run_sql_file_df(db_email, PROBLEM_DIR / "196_delete_duplicate_emails_alt.sql")
        remaining = _remaining_rows(db_email)
        assert len(remaining) == 1
        assert remaining[0]["id"] == 1
