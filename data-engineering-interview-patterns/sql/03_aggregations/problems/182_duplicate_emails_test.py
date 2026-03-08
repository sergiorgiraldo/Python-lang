"""Tests for LeetCode 182: Duplicate Emails."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestDuplicateEmails:

    def test_basic_one_duplicate(self, db_email) -> None:
        db_email.execute("""
            INSERT INTO Person_Email (id, email) VALUES
                (1, 'a@b.com'),
                (2, 'c@d.com'),
                (3, 'a@b.com');
        """)
        result = run_sql_file_df(db_email, PROBLEM_DIR / "182_duplicate_emails.sql")
        emails = {r["email"] for r in result}
        assert emails == {"a@b.com"}

    def test_no_duplicates(self, db_email) -> None:
        db_email.execute("""
            INSERT INTO Person_Email (id, email) VALUES
                (1, 'a@b.com'),
                (2, 'c@d.com'),
                (3, 'e@f.com');
        """)
        result = run_sql_file_df(db_email, PROBLEM_DIR / "182_duplicate_emails.sql")
        assert len(result) == 0

    def test_all_duplicates(self, db_email) -> None:
        db_email.execute("""
            INSERT INTO Person_Email (id, email) VALUES
                (1, 'a@b.com'),
                (2, 'a@b.com'),
                (3, 'c@d.com'),
                (4, 'c@d.com');
        """)
        result = run_sql_file_df(db_email, PROBLEM_DIR / "182_duplicate_emails.sql")
        emails = {r["email"] for r in result}
        assert emails == {"a@b.com", "c@d.com"}

    def test_three_plus_occurrences(self, db_email) -> None:
        db_email.execute("""
            INSERT INTO Person_Email (id, email) VALUES
                (1, 'a@b.com'),
                (2, 'a@b.com'),
                (3, 'a@b.com'),
                (4, 'c@d.com');
        """)
        result = run_sql_file_df(db_email, PROBLEM_DIR / "182_duplicate_emails.sql")
        emails = {r["email"] for r in result}
        assert emails == {"a@b.com"}

    def test_case_sensitivity(self, db_email) -> None:
        db_email.execute("""
            INSERT INTO Person_Email (id, email) VALUES
                (1, 'a@b.com'),
                (2, 'A@b.com'),
                (3, 'a@b.com');
        """)
        result = run_sql_file_df(db_email, PROBLEM_DIR / "182_duplicate_emails.sql")
        emails = {r["email"] for r in result}
        # DuckDB is case-sensitive by default, so 'a@b.com' and 'A@b.com' are distinct
        assert emails == {"a@b.com"}
