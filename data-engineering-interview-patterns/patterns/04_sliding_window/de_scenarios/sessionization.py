"""
DE Scenario: Sessionization

Group timestamped events into sessions based on inactivity gaps.

Usage:
    uv run python -m patterns.04_sliding_window.de_scenarios.sessionization
"""

import random
import time
from dataclasses import dataclass


@dataclass
class Event:
    user_id: str
    timestamp: float  # Unix timestamp
    action: str


@dataclass
class Session:
    user_id: str
    start_time: float
    end_time: float
    event_count: int
    events: list[Event]


def sessionize(
    events: list[Event],
    timeout: float,
) -> list[Session]:
    """
    Group events into sessions. A new session starts when the gap
    between consecutive events exceeds timeout.

    Events must be sorted by (user_id, timestamp).

    Time: O(n)
    Space: O(n) for output sessions
    """
    if not events:
        return []

    sessions = []
    current_events = [events[0]]
    session_start = events[0].timestamp

    for i in range(1, len(events)):
        event = events[i]
        prev = events[i - 1]

        # New user or gap exceeds timeout - close current session
        if event.user_id != prev.user_id or event.timestamp - prev.timestamp > timeout:
            sessions.append(
                Session(
                    user_id=prev.user_id,
                    start_time=session_start,
                    end_time=prev.timestamp,
                    event_count=len(current_events),
                    events=current_events,
                )
            )
            current_events = [event]
            session_start = event.timestamp
        else:
            current_events.append(event)

    # Close the last session
    if current_events:
        sessions.append(
            Session(
                user_id=current_events[-1].user_id,
                start_time=session_start,
                end_time=current_events[-1].timestamp,
                event_count=len(current_events),
                events=current_events,
            )
        )

    return sessions


def sessionize_per_user(
    events: list[Event],
    timeout: float,
) -> dict[str, list[Session]]:
    """
    Sessionize events grouped by user.

    Sorts events by (user_id, timestamp) first, then uses the
    single-pass sessionize function.
    """
    sorted_events = sorted(events, key=lambda e: (e.user_id, e.timestamp))
    all_sessions = sessionize(sorted_events, timeout)

    # Group by user
    by_user: dict[str, list[Session]] = {}
    for session in all_sessions:
        by_user.setdefault(session.user_id, []).append(session)

    return by_user


if __name__ == "__main__":
    # Demo
    events = [
        Event("user_a", 1000, "page_view"),
        Event("user_a", 1010, "click"),
        Event("user_a", 1025, "page_view"),
        # 45-minute gap
        Event("user_a", 3700, "page_view"),
        Event("user_a", 3710, "click"),
        # Different user
        Event("user_b", 1005, "page_view"),
        Event("user_b", 1200, "click"),
    ]

    timeout = 1800  # 30 minutes

    sessions_by_user = sessionize_per_user(events, timeout)

    print("Demo: Sessionization with 30-minute timeout")
    print(f"Events: {len(events)}")
    for user_id, sessions in sorted(sessions_by_user.items()):
        print(f"\n  {user_id}: {len(sessions)} session(s)")
        for i, s in enumerate(sessions):
            duration = s.end_time - s.start_time
            print(
                f"    Session {i + 1}: {s.event_count} events, {duration:.0f}s duration"
            )
    print()

    # Benchmark at scale
    print("--- Benchmark ---")
    random.seed(42)
    for n_events in [10_000, 100_000, 1_000_000]:
        n_users = n_events // 100  # ~100 events per user on average
        bench_events = []
        for _ in range(n_events):
            uid = f"user_{random.randint(0, n_users - 1)}"
            ts = random.uniform(0, 86400 * 30)  # 30 days
            bench_events.append(Event(uid, ts, "action"))

        start_time = time.perf_counter()
        result = sessionize_per_user(bench_events, 1800)
        elapsed = time.perf_counter() - start_time

        total_sessions = sum(len(s) for s in result.values())
        print(
            f"Events: {n_events:>10,} | Users: {n_users:>6,} | "
            f"Sessions: {total_sessions:>8,} | Time: {elapsed:.3f}s"
        )
