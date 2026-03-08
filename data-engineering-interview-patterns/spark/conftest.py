"""
Shared fixtures for PySpark tests.

All fixtures use pytest.importorskip so tests are skipped
(not failed) when PySpark is not installed.
"""

import pathlib

import pytest

SPARK_DIR = pathlib.Path(__file__).parent


def pytest_collect_file(parent, file_path):
    """Collect all .py files under spark/ as test modules.

    The main test suite uses specific python_files patterns in pyproject.toml.
    Spark files use descriptive names (broadcast_join.py, etc.) that don't
    match those patterns, so we collect them explicitly here.
    """
    if (
        file_path.suffix == ".py"
        and file_path.name not in ("conftest.py", "__init__.py")
        and str(file_path).startswith(str(SPARK_DIR))
    ):
        return pytest.Module.from_parent(parent, path=file_path)
    return None


@pytest.fixture(scope="session")
def spark():
    """Create a local SparkSession for testing.

    Session-scoped: one SparkSession for all tests (creating is expensive).
    Local mode: runs entirely in-process, no cluster needed.
    """
    pyspark = pytest.importorskip("pyspark")
    from pyspark.sql import SparkSession

    session = (
        SparkSession.builder
        .master("local[2]")
        .appName("interview-patterns-tests")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .getOrCreate()
    )
    yield session
    session.stop()
