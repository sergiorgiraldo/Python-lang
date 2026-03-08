"""
DE Scenario: Parse application log lines into structured records.

Real-world application: ingesting logs from applications, load balancers,
web servers and databases into a structured analytics table.

The challenge: log formats vary. Some lines match the expected format,
some don't. A robust parser handles known formats with regex and falls
back gracefully for unknown formats.

Run: uv run python -m patterns.09_string_parsing.de_scenarios.log_parsing
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class LogRecord:
    """Structured log record."""

    timestamp: str
    level: str
    logger: str
    message: str
    raw: str  # original line, always preserved


@dataclass
class ParseResult:
    """Result of parsing a log line."""

    record: Optional[LogRecord]
    parsed: bool
    pattern_used: str


# Common log patterns, ordered from most specific to most general
LOG_PATTERNS = [
    (
        "standard",
        re.compile(
            r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)"
            r"\s+\[(?P<level>\w+)\]\s+"
            r"(?P<logger>[\w.]+)\s*[-:]\s*"
            r"(?P<message>.+)"
        ),
    ),
    (
        "brackets",
        re.compile(
            r"\[(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]"
            r"\s*\[(?P<level>\w+)\]\s*"
            r"\[(?P<logger>[\w.]+)\]\s*"
            r"(?P<message>.+)"
        ),
    ),
    (
        "syslog",
        re.compile(
            r"(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"
            r"\s+(?P<logger>\S+)"
            r"\s+(?P<level>\w+):\s*"
            r"(?P<message>.+)"
        ),
    ),
]


def parse_log_line(line: str) -> ParseResult:
    """
    Parse a single log line, trying multiple patterns.

    Tries patterns from most specific to most general.
    Falls back to a raw record if no pattern matches.
    """
    line = line.rstrip("\n")

    for name, pattern in LOG_PATTERNS:
        match = pattern.match(line)
        if match:
            groups = match.groupdict()
            record = LogRecord(
                timestamp=groups["timestamp"],
                level=groups["level"].upper(),
                logger=groups["logger"],
                message=groups["message"].strip(),
                raw=line,
            )
            return ParseResult(record=record, parsed=True, pattern_used=name)

    # Fallback: couldn't parse, preserve raw line
    return ParseResult(
        record=LogRecord(
            timestamp="",
            level="UNKNOWN",
            logger="",
            message=line,
            raw=line,
        ),
        parsed=False,
        pattern_used="fallback",
    )


def parse_log_batch(lines: list[str]) -> dict:
    """
    Parse a batch of log lines and return stats.

    In production, this would write to a structured table
    with a separate error/quarantine table for unparsed lines.
    """
    results = []
    stats = {"total": 0, "parsed": 0, "failed": 0, "by_pattern": {}}

    for line in lines:
        if not line.strip():
            continue

        stats["total"] += 1
        result = parse_log_line(line)
        results.append(result)

        if result.parsed:
            stats["parsed"] += 1
            stats["by_pattern"][result.pattern_used] = (
                stats["by_pattern"].get(result.pattern_used, 0) + 1
            )
        else:
            stats["failed"] += 1

    return {"records": results, "stats": stats}


if __name__ == "__main__":
    sample_logs = [
        '2024-01-15 08:23:45.123 [INFO] com.app.service - Request processed in 45ms',
        '2024-01-15 08:23:46 [ERROR] com.app.db - Connection timeout after 30s',
        '[2024-01-15 08:23:47] [WARN] [com.app.cache] Cache miss for key user:1234',
        'Jan 15 08:23:48 appserver INFO: Health check passed',
        'This line has no recognizable format at all',
        '2024-01-15 08:23:50.789 [DEBUG] com.app.auth: Token validated for user admin@corp.com',
    ]

    print("=== Log Line Parsing ===\n")

    batch = parse_log_batch(sample_logs)

    for result in batch["records"]:
        r = result.record
        status = "PARSED" if result.parsed else "FAILED"
        print(f"  [{status}] pattern={result.pattern_used}")
        print(f"    timestamp: {r.timestamp}")
        print(f"    level:     {r.level}")
        print(f"    logger:    {r.logger}")
        print(f"    message:   {r.message[:60]}")
        print()

    stats = batch["stats"]
    print(f"  Stats: {stats['parsed']}/{stats['total']} parsed, "
          f"{stats['failed']} failed")
    print(f"  Patterns used: {stats['by_pattern']}")
