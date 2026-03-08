"""
DE Scenario: Org chart traversal using recursive processing.

Real-world application: reporting hierarchies, management chains,
headcount rollups. Shows the Python equivalent of SQL recursive CTEs.

Run: uv run python -m patterns.10_recursion_trees.de_scenarios.org_chart
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Employee:
    """An employee in an org chart."""

    id: int
    name: str
    title: str
    manager_id: int | None = None
    reports: list[Employee] = field(default_factory=list)


def build_org_tree(employees: list[dict]) -> Employee | None:
    """
    Build an org tree from a flat list of employee records.

    This is the Python equivalent of converting a parent-child table
    into a tree. In SQL, you'd use a recursive CTE. Here, we use
    a hash map (O(n)) to build parent-child links.
    """
    emp_map: dict[int, Employee] = {}

    # First pass: create all Employee objects
    for e in employees:
        emp_map[e["id"]] = Employee(
            id=e["id"],
            name=e["name"],
            title=e["title"],
            manager_id=e.get("manager_id"),
        )

    # Second pass: link children to parents
    root = None
    for emp in emp_map.values():
        if emp.manager_id is None:
            root = emp
        elif emp.manager_id in emp_map:
            emp_map[emp.manager_id].reports.append(emp)

    return root


def get_full_chain(root: Employee, target_id: int) -> list[str]:
    """
    Get the management chain from root to a specific employee.

    SQL equivalent: recursive CTE walking UP from the employee to the root.
    """

    def _find_path(node: Employee, target: int) -> list[str] | None:
        if node.id == target:
            return [node.name]

        for report in node.reports:
            path = _find_path(report, target)
            if path is not None:
                return [node.name] + path

        return None

    return _find_path(root, target_id) or []


def get_all_reports(employee: Employee) -> list[str]:
    """
    Get all direct and indirect reports (flattened).

    SQL equivalent: recursive CTE walking DOWN from a manager.
    """
    result: list[str] = []

    for report in employee.reports:
        result.append(report.name)
        result.extend(get_all_reports(report))

    return result


def headcount_rollup(employee: Employee) -> dict[str, int]:
    """
    Compute headcount rollup (each manager's total org size).

    For each manager: count = direct reports + all indirect reports.
    This is a post-order traversal: compute children's counts first,
    then sum for the parent.
    """

    def _count(emp: Employee) -> int:
        total = len(emp.reports)
        for report in emp.reports:
            total += _count(report)
        return total

    rollup: dict[str, int] = {}

    def _build_rollup(emp: Employee) -> None:
        rollup[emp.name] = _count(emp)
        for report in emp.reports:
            _build_rollup(report)

    _build_rollup(employee)
    return rollup


if __name__ == "__main__":
    employees = [
        {"id": 1, "name": "Alice", "title": "CEO", "manager_id": None},
        {"id": 2, "name": "Bob", "title": "VP Engineering", "manager_id": 1},
        {"id": 3, "name": "Charlie", "title": "VP Sales", "manager_id": 1},
        {"id": 4, "name": "Diana", "title": "Senior Engineer", "manager_id": 2},
        {"id": 5, "name": "Eve", "title": "Engineer", "manager_id": 2},
        {"id": 6, "name": "Frank", "title": "Sales Lead", "manager_id": 3},
        {"id": 7, "name": "Grace", "title": "Junior Engineer", "manager_id": 4},
    ]

    root = build_org_tree(employees)

    print("=== Org Chart Traversal ===\n")

    print("  Management chain to Grace:")
    chain = get_full_chain(root, 7)
    print(f"    {' -> '.join(chain)}")

    print(f"\n  All reports under Bob:")
    reports = get_all_reports(root.reports[0])  # Bob
    print(f"    {reports}")

    print(f"\n  Headcount rollup:")
    rollup = headcount_rollup(root)
    for name, count in sorted(rollup.items(), key=lambda x: -x[1]):
        print(f"    {name}: {count}")
