"""
DE Scenario: Priority-Based Task Scheduling

Processing tasks by priority using a heap-based priority queue.
Higher priority tasks run first. Among equal priorities, earlier
submissions run first (FIFO within priority level).
"""

import heapq
import random
import time
from dataclasses import dataclass, field


@dataclass(order=True)
class Task:
    """A schedulable task with priority and metadata."""

    priority: int  # lower number = higher priority
    submitted_at: float = field(compare=True)
    name: str = field(compare=False)
    duration_s: float = field(compare=False)


def schedule_priority_heap(tasks: list[Task]) -> list[Task]:
    """
    Process tasks by priority using a min-heap.

    Lower priority number = higher priority = processed first.
    Ties broken by submission time (FIFO).

    Time: O(n log n)  Space: O(n)
    """
    heap = list(tasks)
    heapq.heapify(heap)

    execution_order: list[Task] = []
    while heap:
        task = heapq.heappop(heap)
        execution_order.append(task)
    return execution_order


def schedule_sort(tasks: list[Task]) -> list[Task]:
    """
    Brute force: sort by priority, then submission time.

    Time: O(n log n)  Space: O(n)
    """
    return sorted(tasks, key=lambda t: (t.priority, t.submitted_at))


def schedule_with_arrivals(
    initial_tasks: list[Task], arriving_tasks: list[tuple[float, Task]]
) -> list[Task]:
    """
    Simulate dynamic scheduling where tasks arrive over time.

    This is the realistic version: tasks arrive while others are running.
    A heap lets us efficiently insert new tasks and always pick the
    highest priority next.

    Args:
        initial_tasks: Tasks available at time 0.
        arriving_tasks: (arrival_time, task) pairs sorted by arrival_time.

    Returns:
        Tasks in execution order.
    """
    heap: list[Task] = list(initial_tasks)
    heapq.heapify(heap)

    arrival_idx = 0
    current_time = 0.0
    execution_order: list[Task] = []

    while heap or arrival_idx < len(arriving_tasks):
        # Add any tasks that have arrived by current_time
        while arrival_idx < len(arriving_tasks):
            arrival_time, task = arriving_tasks[arrival_idx]
            if arrival_time <= current_time:
                heapq.heappush(heap, task)
                arrival_idx += 1
            else:
                break

        if heap:
            task = heapq.heappop(heap)
            execution_order.append(task)
            current_time += task.duration_s
        elif arrival_idx < len(arriving_tasks):
            # Jump to next arrival
            current_time = arriving_tasks[arrival_idx][0]

    return execution_order


def generate_tasks(n: int) -> list[Task]:
    """Generate random tasks with varying priorities."""
    priorities = [1, 1, 2, 2, 2, 3, 3, 3, 3, 4]  # skewed toward lower priority
    tasks = []
    for i in range(n):
        tasks.append(
            Task(
                priority=random.choice(priorities),
                submitted_at=random.uniform(0, 100),
                name=f"task_{i:06d}",
                duration_s=random.uniform(0.1, 5.0),
            )
        )
    return tasks


if __name__ == "__main__":
    random.seed(42)

    for n in [1_000, 10_000, 100_000]:
        tasks = generate_tasks(n)

        start = time.perf_counter()
        result_heap = schedule_priority_heap(list(tasks))
        heap_time = time.perf_counter() - start

        start = time.perf_counter()
        result_sort = schedule_sort(list(tasks))
        sort_time = time.perf_counter() - start

        # Verify same order
        assert [t.name for t in result_heap] == [t.name for t in result_sort]

        print(f"\n--- n={n:,} ---")
        print(f"Heap:  {heap_time:.4f}s")
        print(f"Sort:  {sort_time:.4f}s")

    # Show sample execution order
    print("\nSample execution (first 10 tasks from n=1000):")
    tasks = generate_tasks(20)
    result = schedule_priority_heap(tasks)
    for task in result[:10]:
        print(
            f"  [{task.priority}] {task.name} "
            f"(submitted={task.submitted_at:.1f}, duration={task.duration_s:.1f}s)"
        )
