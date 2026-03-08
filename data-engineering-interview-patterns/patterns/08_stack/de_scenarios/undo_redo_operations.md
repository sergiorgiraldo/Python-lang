# DE Scenario: Undo/Redo for Data Transformations

## Real-World Context

Data transformation pipelines often need rollback capability. When a transform produces unexpected results, you need to revert to the previous state. Two stacks handle this naturally: an undo stack holds previous states and a redo stack holds undone states. Each transform pushes the current state onto the undo stack before applying. Undo pops from the undo stack and pushes to redo. Applying a new transform clears the redo stack (you've branched).

## Worked Example

Two stacks working together. The undo stack grows with each transform. Undo moves states from the undo stack to the redo stack. Redo moves them back. A new transform after an undo clears the redo stack because the old future is no longer reachable.

```
Initial data: 4 rows [Alice, Bob, Carol, Dave]
Undo stack: []    Redo stack: []

Apply "filter_eng" (keep only dept=eng):
  Push current (4 rows) to undo.
  Current = 2 rows [Alice, Carol].
  Undo: [4 rows]    Redo: []

Apply "add_seniority" (add senior flag):
  Push current (2 rows) to undo.
  Current = 2 rows with senior flag.
  Undo: [4 rows, 2 rows]    Redo: []

Undo:
  Pop 2 rows from undo. Push current (2+flag) to redo.
  Current = 2 rows [Alice, Carol] (no flag).
  Undo: [4 rows]    Redo: [2+flag]

Undo again:
  Pop 4 rows from undo. Push current (2 rows) to redo.
  Current = 4 rows (original).
  Undo: []    Redo: [2+flag, 2 rows]

Redo:
  Pop 2 rows from redo. Push current (4 rows) to undo.
  Current = 2 rows [Alice, Carol].
  Undo: [4 rows]    Redo: [2+flag]

Each operation is O(1) for the stack manipulation (though the
data copy itself is O(n) where n is the dataset size).
```
