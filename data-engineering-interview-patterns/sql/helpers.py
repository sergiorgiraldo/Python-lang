"""Helper functions for SQL tests."""

from pathlib import Path

import duckdb


def run_sql_file(
    conn: duckdb.DuckDBPyConnection,
    sql_path: str | Path,
) -> list[tuple]:
    """
    Read a .sql file and execute it against the connection.
    Returns the result rows as a list of tuples.
    """
    sql = Path(sql_path).read_text()
    return conn.execute(sql).fetchall()


def run_sql_file_df(
    conn: duckdb.DuckDBPyConnection,
    sql_path: str | Path,
) -> list[dict]:
    """
    Read a .sql file and execute it, returning a list of dicts
    for easier assertion (column names preserved).
    """
    sql = Path(sql_path).read_text()
    result = conn.execute(sql)
    columns = [desc[0] for desc in result.description]
    rows = result.fetchall()
    return [dict(zip(columns, row)) for row in rows]
