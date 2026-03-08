"""Tests for LeetCode 570: Managers with at Least 5 Direct Reports."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestManagersWith5Reports:

    def test_exactly_five(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId, managerId) VALUES
                (1, 'Boss', 100000, 1, NULL),
                (2, 'A', 50000, 1, 1),
                (3, 'B', 50000, 1, 1),
                (4, 'C', 50000, 1, 1),
                (5, 'D', 50000, 1, 1),
                (6, 'E', 50000, 1, 1);
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "570_managers_with_5_reports.sql"
        )
        names = {r["name"] for r in result}
        assert names == {"Boss"}

    def test_four_reports_excluded(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId, managerId) VALUES
                (1, 'Boss', 100000, 1, NULL),
                (2, 'A', 50000, 1, 1),
                (3, 'B', 50000, 1, 1),
                (4, 'C', 50000, 1, 1),
                (5, 'D', 50000, 1, 1);
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "570_managers_with_5_reports.sql"
        )
        assert len(result) == 0

    def test_ten_reports(self, db_employee) -> None:
        values = [(1, 'Boss', 100000, 1, None)]
        for i in range(2, 12):
            values.append((i, f'Emp{i}', 50000, 1, 1))
        sql_values = ", ".join(
            f"({v[0]}, '{v[1]}', {v[2]}, {v[3]}, {'NULL' if v[4] is None else v[4]})"
            for v in values
        )
        db_employee.execute(
            f"INSERT INTO Employee (id, name, salary, departmentId, managerId) VALUES {sql_values};"
        )
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "570_managers_with_5_reports.sql"
        )
        names = {r["name"] for r in result}
        assert names == {"Boss"}

    def test_no_reports(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId, managerId) VALUES
                (1, 'Boss', 100000, 1, NULL),
                (2, 'Lone', 50000, 1, NULL);
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "570_managers_with_5_reports.sql"
        )
        assert len(result) == 0

    def test_no_managers_meet_threshold(self, db_employee) -> None:
        db_employee.execute("""
            INSERT INTO Employee (id, name, salary, departmentId, managerId) VALUES
                (1, 'Boss1', 100000, 1, NULL),
                (2, 'Boss2', 100000, 1, NULL),
                (3, 'A', 50000, 1, 1),
                (4, 'B', 50000, 1, 1),
                (5, 'C', 50000, 1, 2),
                (6, 'D', 50000, 1, 2);
        """)
        result = run_sql_file_df(
            db_employee, PROBLEM_DIR / "570_managers_with_5_reports.sql"
        )
        assert len(result) == 0
