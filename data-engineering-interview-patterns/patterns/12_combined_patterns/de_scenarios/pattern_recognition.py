"""
DE Scenario: Pattern recognition practice.

This module presents interview-style problems WITHOUT pattern labels.
The challenge: identify which pattern(s) apply before solving.

Run: uv run python -m patterns.12_combined_patterns.de_scenarios.pattern_recognition
"""


def practice_problems() -> list[dict]:
    """
    Return a list of practice problems for pattern recognition.
    Each has a description, hints, and the patterns involved.
    """
    return [
        {
            "title": "Event Session Windows",
            "description": (
                "Given a stream of user events (user_id, timestamp), group events "
                "into sessions. A session ends when there's a gap of more than "
                "30 minutes between events. Return the session count per user."
            ),
            "hints": [
                "Sort events by user and timestamp",
                "Track the gap between consecutive events",
                "What pattern handles consecutive-element comparisons?",
            ],
            "patterns": ["Sort", "Two Pointers / Sliding Window", "Hash Map"],
            "approach": (
                "Sort by (user_id, timestamp). For each user, iterate through "
                "events tracking the current session. When the gap exceeds 30 "
                "minutes, start a new session. Hash map stores session count "
                "per user."
            ),
        },
        {
            "title": "Data Quality Anomaly Detection",
            "description": (
                "Given daily record counts for 100 data tables over the past "
                "year, find tables where today's count deviates by more than "
                "3 standard deviations from the rolling 30-day average."
            ),
            "hints": [
                "What pattern computes rolling statistics?",
                "How do you efficiently track a 30-day window?",
            ],
            "patterns": ["Sliding Window", "Hash Map"],
            "approach": (
                "For each table, maintain a sliding window of the last 30 "
                "days of counts. Compute the mean and standard deviation "
                "within the window. Compare today's count against the "
                "threshold. Hash map stores per-table window state."
            ),
        },
        {
            "title": "Find Circular Dependencies",
            "description": (
                "Given a list of table dependencies (table_a depends on "
                "table_b), detect if any circular dependencies exist. "
                "Return the cycle if found."
            ),
            "hints": [
                "What data structure represents dependencies?",
                "What algorithm detects cycles in a directed graph?",
            ],
            "patterns": ["Graph", "DFS / Topological Sort"],
            "approach": (
                "Build a directed graph from the dependency list. Run DFS "
                "with three states (unvisited, in-progress, completed). "
                "If you visit an in-progress node, you've found a cycle. "
                "Alternatively, attempt topological sort - if it fails "
                "(not all nodes processed), a cycle exists."
            ),
        },
        {
            "title": "Optimal Batch Size",
            "description": (
                "Given a sorted list of file sizes and a maximum batch size, "
                "find the maximum number of files that can fit in one batch. "
                "Files must be consecutive in the sorted order."
            ),
            "hints": [
                "The data is sorted. What pattern works on sorted data?",
                "You need a contiguous range that satisfies a constraint.",
            ],
            "patterns": ["Sliding Window", "Binary Search"],
            "approach": (
                "Sliding window: maintain a running sum. Expand right until "
                "the sum exceeds the batch size, then shrink left. Track "
                "the maximum window size. Alternatively, binary search on "
                "the answer: for a given window size k, check if any k "
                "consecutive files fit."
            ),
        },
        {
            "title": "Top Error Producers",
            "description": (
                "Given a stream of 10 million log entries, find the top 10 "
                "error messages by frequency. Memory is limited to 100 MB."
            ),
            "hints": [
                "What pattern counts frequencies?",
                "What pattern extracts top-k efficiently?",
                "Could you use an approximate approach?",
            ],
            "patterns": ["Hash Map + Heap", "Count-Min Sketch (approximate)"],
            "approach": (
                "Exact: Hash map for frequency counting + min-heap of size "
                "10 for top-k extraction. If error messages are long and "
                "diverse, the hash map might exceed 100 MB. Approximate: "
                "Count-Min Sketch for frequency estimation + heap for "
                "candidates. Fixed memory regardless of cardinality."
            ),
        },
    ]


if __name__ == "__main__":
    print("=== Pattern Recognition Practice ===\n")
    print("  Try to identify the pattern(s) before reading the hints.\n")

    for i, problem in enumerate(practice_problems(), 1):
        print(f"  Problem {i}: {problem['title']}")
        print(f"  {problem['description']}")
        print()
        print(f"  Hints:")
        for hint in problem["hints"]:
            print(f"    - {hint}")
        print(f"  Patterns: {', '.join(problem['patterns'])}")
        print(f"  Approach: {problem['approach']}")
        print()
        print("  " + "-" * 60)
        print()
