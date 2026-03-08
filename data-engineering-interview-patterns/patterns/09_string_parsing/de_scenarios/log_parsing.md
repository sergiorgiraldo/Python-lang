# DE Scenario: Log Line Parsing

## Real-World Context

Application logs are one of the most common data sources in DE pipelines. They arrive in various formats (standard log4j, syslog, custom formats) and must be parsed into structured columns (timestamp, level, logger, message) for querying.

The challenge: format inconsistency. A single application might produce logs in different formats depending on the library, version or configuration. A robust parser tries multiple patterns and falls back gracefully rather than crashing on unexpected input.

## Worked Example

Multi-pattern parsing with fallback. The parser tries regex patterns from most specific to most general. If none match, it preserves the raw line (never lose data) and flags it for review. In production, parsed records go to the main table and unparsed records go to a quarantine table.

```
Input lines:
  1: "2024-01-15 08:23:45.123 [INFO] com.app.service - Request processed in 45ms"
  2: "[2024-01-15 08:23:47] [WARN] [com.app.cache] Cache miss for key user:1234"
  3: "This line has no recognizable format at all"

Line 1: try "standard" pattern
  Regex: timestamp=2024-01-15 08:23:45.123, level=INFO,
         logger=com.app.service, message=Request processed in 45ms
  Match. → LogRecord(timestamp="2024-01-15 08:23:45.123", level="INFO", ...)

Line 2: try "standard" pattern → no match (different bracket format)
  Try "brackets" pattern
  Regex: timestamp=2024-01-15 08:23:47, level=WARN,
         logger=com.app.cache, message=Cache miss for key user:1234
  Match. → LogRecord(...)

Line 3: try all patterns → no match
  Fallback. → LogRecord(timestamp="", level="UNKNOWN", message=raw line)
  Flag for review. Don't drop it.

Stats: 2/3 parsed (67%), 1 failed, patterns used: {standard: 1, brackets: 1}
```

## Key Design Decisions

1. **Try multiple patterns, not one mega-regex.** Easier to maintain and debug.
2. **Most specific first.** Avoids false matches from overly general patterns.
3. **Always preserve the raw line.** Even if parsing fails, the data isn't lost.
4. **Track parse stats.** If the failure rate spikes, something changed upstream.
5. **Named capture groups** (`(?P<name>...)`) make the extracted fields self-documenting.
