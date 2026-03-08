"""
DE Scenario: Stack-based undo/redo for data transformations.

Real-world application: version tracking in data transformation
pipelines. Each transform pushes state, rollback pops it.

Run: uv run python -m patterns.08_stack.de_scenarios.undo_redo_operations
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TransformState:
    """Snapshot of a data transformation step."""

    name: str
    data: list[dict[str, Any]]
    description: str


class TransformPipeline:
    """
    Data transformation pipeline with undo/redo support.

    Uses two stacks: undo_stack holds past states, redo_stack holds
    states that were undone. Applying a new transform clears the
    redo stack (you branched from that point).
    """

    def __init__(self, initial_data: list[dict[str, Any]]) -> None:
        self.current = initial_data
        self.undo_stack: list[TransformState] = []
        self.redo_stack: list[TransformState] = []

    def apply_transform(
        self,
        name: str,
        transform_fn: Any,
        description: str = "",
    ) -> list[dict[str, Any]]:
        """Apply a transformation, saving the current state for undo."""
        # Save current state before transforming
        self.undo_stack.append(
            TransformState(name=name, data=self.current, description=description)
        )
        self.redo_stack.clear()  # new branch, discard redo history
        self.current = transform_fn(self.current)
        return self.current

    def undo(self) -> list[dict[str, Any]] | None:
        """Undo the last transformation. Returns the restored data or None."""
        if not self.undo_stack:
            return None
        state = self.undo_stack.pop()
        self.redo_stack.append(
            TransformState(name=state.name, data=self.current, description=state.description)
        )
        self.current = state.data
        return self.current

    def redo(self) -> list[dict[str, Any]] | None:
        """Redo the last undone transformation. Returns the restored data or None."""
        if not self.redo_stack:
            return None
        state = self.redo_stack.pop()
        self.undo_stack.append(
            TransformState(name=state.name, data=self.current, description=state.description)
        )
        self.current = state.data
        return self.current

    def history(self) -> list[str]:
        """Return the names of all transforms in the undo stack."""
        return [s.name for s in self.undo_stack]


if __name__ == "__main__":
    print("=== Undo/Redo Transform Pipeline ===")

    data = [
        {"name": "Alice", "age": 30, "dept": "eng"},
        {"name": "Bob", "age": 25, "dept": "sales"},
        {"name": "Carol", "age": 35, "dept": "eng"},
        {"name": "Dave", "age": 28, "dept": "sales"},
    ]

    pipeline = TransformPipeline(data)
    print(f"  Initial: {len(pipeline.current)} rows")

    # Transform 1: filter to eng dept
    pipeline.apply_transform(
        "filter_eng",
        lambda d: [r for r in d if r["dept"] == "eng"],
        "Keep only engineering rows",
    )
    print(f"  After filter_eng: {len(pipeline.current)} rows → {pipeline.current}")

    # Transform 2: add seniority column
    pipeline.apply_transform(
        "add_seniority",
        lambda d: [{**r, "senior": r["age"] >= 30} for r in d],
        "Add seniority flag",
    )
    print(f"  After add_seniority: {pipeline.current}")

    # Undo last transform
    pipeline.undo()
    print(f"  After undo: {pipeline.current}")

    # Undo again (back to original)
    pipeline.undo()
    print(f"  After second undo: {len(pipeline.current)} rows")

    # Redo
    pipeline.redo()
    print(f"  After redo: {len(pipeline.current)} rows → {pipeline.current}")

    print(f"\n  History (undo stack): {pipeline.history()}")
    print(f"  Redo available: {len(pipeline.redo_stack)} steps")
