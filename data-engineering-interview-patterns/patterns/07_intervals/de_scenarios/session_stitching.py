"""
DE Scenario: Session Stitching

Merging raw events into sessions by combining overlapping
or closely-spaced events. This is merge intervals applied
to time-series data.
"""

import random
import time
from datetime import datetime, timedelta


def stitch_sessions(
    events: list[tuple[str, datetime, datetime]],
    gap_threshold: timedelta = timedelta(minutes=30),
) -> list[tuple[datetime, datetime, int]]:
    """
    Merge events into sessions. Events within gap_threshold of each
    other are considered the same session.

    Returns list of (session_start, session_end, event_count).

    Time: O(n log n)  Space: O(n)
    """
    if not events:
        return []

    sorted_events = sorted(events, key=lambda x: x[1])

    sessions: list[tuple[datetime, datetime, int]] = []
    session_start = sorted_events[0][1]
    session_end = sorted_events[0][2]
    count = 1

    for _, start, end in sorted_events[1:]:
        if start <= session_end + gap_threshold:
            session_end = max(session_end, end)
            count += 1
        else:
            sessions.append((session_start, session_end, count))
            session_start = start
            session_end = end
            count = 1

    sessions.append((session_start, session_end, count))
    return sessions


def stitch_sessions_brute(
    events: list[tuple[str, datetime, datetime]],
    gap_threshold: timedelta = timedelta(minutes=30),
) -> list[tuple[datetime, datetime, int]]:
    """
    Brute force: repeatedly merge overlapping events.

    Time: O(n^2)  Space: O(n)
    """
    if not events:
        return []

    groups: list[list[tuple[str, datetime, datetime]]] = [[e] for e in events]
    changed = True

    while changed:
        changed = False
        new_groups: list[list[tuple[str, datetime, datetime]]] = []
        used = [False] * len(groups)

        for i in range(len(groups)):
            if used[i]:
                continue
            current = list(groups[i])
            c_start = min(e[1] for e in current)
            c_end = max(e[2] for e in current)

            for j in range(i + 1, len(groups)):
                if used[j]:
                    continue
                g_start = min(e[1] for e in groups[j])
                g_end = max(e[2] for e in groups[j])

                if (
                    g_start <= c_end + gap_threshold
                    and c_start <= g_end + gap_threshold
                ):
                    current.extend(groups[j])
                    c_start = min(c_start, g_start)
                    c_end = max(c_end, g_end)
                    used[j] = True
                    changed = True

            new_groups.append(current)
        groups = new_groups

    sessions = []
    for group in groups:
        start = min(e[1] for e in group)
        end = max(e[2] for e in group)
        sessions.append((start, end, len(group)))

    return sorted(sessions, key=lambda x: x[0])


def generate_browsing_events(
    n: int, base: datetime
) -> list[tuple[str, datetime, datetime]]:
    """Generate simulated browsing events with session clusters."""
    events = []
    current_time = base
    for i in range(n):
        if random.random() < 0.15:
            current_time += timedelta(minutes=random.randint(45, 180))
        else:
            current_time += timedelta(seconds=random.randint(5, 300))
        duration = timedelta(seconds=random.randint(10, 120))
        events.append((f"page_{i}", current_time, current_time + duration))
    return events


if __name__ == "__main__":
    random.seed(42)
    base = datetime(2024, 3, 15, 9, 0)

    for n in [100, 1_000, 10_000]:
        events = generate_browsing_events(n, base)

        start = time.perf_counter()
        sessions = stitch_sessions(events)
        sort_time = time.perf_counter() - start

        print(f"\nn={n:,}: sessions={len(sessions)}, time={sort_time:.4f}s")

    # Show sample sessions
    events = generate_browsing_events(50, base)
    sessions = stitch_sessions(events)
    print(f"\nSample sessions (from 50 events → {len(sessions)} sessions):")
    for s_start, s_end, count in sessions[:5]:
        duration = (s_end - s_start).total_seconds() / 60
        print(
            f"  {s_start.strftime('%H:%M')} - {s_end.strftime('%H:%M')} "
            f"({duration:.0f}min, {count} events)"
        )
