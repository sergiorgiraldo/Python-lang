"""Tests for bill of materials explosion with recursive CTE scenario."""

from pathlib import Path
from decimal import Decimal

import duckdb

SQL_DIR = Path(__file__).parent


class TestBillOfMaterials:
    """Test recursive BOM explosion with quantity multiplication."""

    def _setup(self, db: duckdb.DuckDBPyConnection) -> None:
        """Create and populate the bom table."""
        sql = (SQL_DIR / "bill_of_materials.sql").read_text()
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

    def _explode(self, db: duckdb.DuckDBPyConnection) -> list[tuple]:
        """Run the BOM explosion query for Bicycle."""
        return db.execute("""
            WITH RECURSIVE explosion AS (
                SELECT parent_id, component_id, quantity AS total_quantity,
                       unit_cost, 1 AS depth
                FROM bom
                WHERE parent_id = 'Bicycle'

                UNION ALL

                SELECT b.parent_id, b.component_id,
                       e.total_quantity * b.quantity AS total_quantity,
                       b.unit_cost, e.depth + 1
                FROM bom b
                JOIN explosion e ON b.parent_id = e.component_id
            )
            SELECT component_id, total_quantity, unit_cost,
                   total_quantity * unit_cost AS total_cost, depth
            FROM explosion
            WHERE unit_cost IS NOT NULL
            ORDER BY depth, component_id
        """).fetchall()

    def test_total_bicycle_cost(self, db: duckdb.DuckDBPyConnection) -> None:
        """Total cost of a Bicycle is correct."""
        self._setup(db)
        result = self._explode(db)
        total_cost = sum(float(r[3]) for r in result)
        # Chain: 1 * 15 = 15
        # Steel Tube: 1 * 3 * 8 = 24
        # Weld: 1 * 6 * 0.50 = 3
        # Rim: 2 * 1 * 25 = 50
        # Spoke: 2 * 32 * 0.75 = 48
        # Tire: 2 * 1 * 20 = 40
        # Total = 15 + 24 + 3 + 50 + 48 + 40 = 180
        assert total_cost == 180.0

    def test_leaf_components_only(self, db: duckdb.DuckDBPyConnection) -> None:
        """Only leaf components (with unit_cost) appear in the result."""
        self._setup(db)
        result = self._explode(db)
        components = {r[0] for r in result}
        # Frame and Wheel are intermediate, not leaf
        assert "Frame" not in components
        assert "Wheel" not in components
        # Leaf components
        assert "Chain" in components
        assert "Steel Tube" in components
        assert "Spoke" in components

    def test_quantity_multiplication(self, db: duckdb.DuckDBPyConnection) -> None:
        """Quantities multiply across levels (Bicycle needs 2 Wheels, each has 32 Spokes = 64)."""
        self._setup(db)
        result = self._explode(db)
        spoke_row = [r for r in result if r[0] == "Spoke"][0]
        assert spoke_row[1] == 64  # 2 wheels * 32 spokes

    def test_depth_values(self, db: duckdb.DuckDBPyConnection) -> None:
        """Chain is depth 1 (direct), Steel Tube is depth 2 (via Frame)."""
        self._setup(db)
        result = self._explode(db)
        depth_map = {r[0]: r[4] for r in result}
        assert depth_map["Chain"] == 1
        assert depth_map["Steel Tube"] == 2
        assert depth_map["Rim"] == 2
