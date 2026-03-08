"""
DE Scenario: Monotonic stack for time-series analysis.

Real-world application: finding the next threshold breach for each
data point in a monitoring stream. Same pattern as Daily Temperatures.

Run: uv run python -m patterns.08_stack.de_scenarios.monotonic_time_series
"""

from dataclasses import dataclass


@dataclass
class TimeSeriesPoint:
    """A single time-series data point."""

    timestamp: str
    value: float


def next_threshold_breach(
    data: list[TimeSeriesPoint], threshold: float
) -> dict[str, str | None]:
    """
    For each data point, find the next point that exceeds the threshold.

    Returns a dict mapping each timestamp to the timestamp of the
    next breach, or None if no future breach exists.

    Uses a monotonic stack: points waiting for a breach are on the stack.
    When a breach arrives, it resolves all waiting points.
    """
    result: dict[str, str | None] = {}
    stack: list[int] = []  # indices of unresolved points

    for i, point in enumerate(data):
        while stack and point.value > threshold:
            idx = stack.pop()
            result[data[idx].timestamp] = point.timestamp
        if point.value <= threshold:
            stack.append(i)
        else:
            result[point.timestamp] = None  # already above threshold

    # Remaining unresolved points
    while stack:
        idx = stack.pop()
        result[data[idx].timestamp] = None

    return result


def next_greater_value(data: list[TimeSeriesPoint]) -> dict[str, tuple[str, float] | None]:
    """
    For each data point, find the next point with a strictly greater value.

    Classic "next greater element" applied to time series. Same as
    Daily Temperatures but with timestamps instead of indices.
    """
    result: dict[str, tuple[str, float] | None] = {}
    stack: list[int] = []

    for i, point in enumerate(data):
        while stack and point.value > data[stack[-1]].value:
            idx = stack.pop()
            result[data[idx].timestamp] = (point.timestamp, point.value)
        stack.append(i)

    while stack:
        idx = stack.pop()
        result[data[idx].timestamp] = None

    return result


if __name__ == "__main__":
    print("=== Next Threshold Breach ===")

    data = [
        TimeSeriesPoint("08:00", 45),
        TimeSeriesPoint("08:05", 52),
        TimeSeriesPoint("08:10", 48),
        TimeSeriesPoint("08:15", 41),
        TimeSeriesPoint("08:20", 55),
        TimeSeriesPoint("08:25", 38),
        TimeSeriesPoint("08:30", 60),
    ]

    breaches = next_threshold_breach(data, threshold=50)
    for ts, breach_ts in sorted(breaches.items()):
        print(f"  {ts}: next breach at {breach_ts}")

    print("\n=== Next Greater Value ===")

    greater = next_greater_value(data)
    for ts, result in sorted(greater.items()):
        if result:
            print(f"  {ts} ({data[[p.timestamp for p in data].index(ts)].value})"
                  f" -> {result[0]} ({result[1]})")
        else:
            print(f"  {ts}: no greater value found")
