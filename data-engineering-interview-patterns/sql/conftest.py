"""
SQL section test infrastructure.

Provides DuckDB connections with schema fixtures loaded.
Each test gets a fresh in-memory database.
"""

import sys
from pathlib import Path

import duckdb
import pytest

# Ensure sql/ is importable
sys.path.insert(0, str(Path(__file__).parent))

SQL_DIR = Path(__file__).parent
FIXTURES_DIR = SQL_DIR / "fixtures"


@pytest.fixture
def db() -> duckdb.DuckDBPyConnection:
    """Fresh in-memory DuckDB connection. No schemas loaded."""
    conn = duckdb.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def db_employee(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with Employee + Department schemas loaded."""
    _load_fixture(db, "employee_department.sql")
    return db


@pytest.fixture
def db_person_address(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with Person + Address schemas loaded."""
    _load_fixture(db, "person_address.sql")
    return db


@pytest.fixture
def db_customer_orders(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with Customers + Orders schemas loaded."""
    _load_fixture(db, "customer_orders.sql")
    return db


@pytest.fixture
def db_activity(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with Activity schema loaded."""
    _load_fixture(db, "activity.sql")
    return db


@pytest.fixture
def db_logs(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with Logs schema loaded."""
    _load_fixture(db, "logs.sql")
    return db


@pytest.fixture
def db_weather(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with Weather schema loaded."""
    _load_fixture(db, "weather.sql")
    return db


@pytest.fixture
def db_stadium(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with Stadium schema loaded."""
    _load_fixture(db, "stadium.sql")
    return db


@pytest.fixture
def db_trips(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with Trips + Users schemas loaded."""
    _load_fixture(db, "trips_users.sql")
    return db


@pytest.fixture
def db_candidate(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with Candidate + Vote schemas loaded."""
    _load_fixture(db, "candidate_vote.sql")
    return db


@pytest.fixture
def db_insurance(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with Insurance schema loaded."""
    _load_fixture(db, "insurance.sql")
    return db


@pytest.fixture
def db_friend_request(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with RequestAccepted schema loaded."""
    _load_fixture(db, "friend_request.sql")
    return db


@pytest.fixture
def db_student(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with Student schema loaded."""
    _load_fixture(db, "student.sql")
    return db


@pytest.fixture
def db_email(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with Person_Email schema loaded."""
    _load_fixture(db, "email.sql")
    return db


def _load_fixture(conn: duckdb.DuckDBPyConnection, filename: str) -> None:
    """Load a SQL fixture file into the connection."""
    fixture_path = FIXTURES_DIR / filename
    sql = fixture_path.read_text()
    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            conn.execute(statement)
