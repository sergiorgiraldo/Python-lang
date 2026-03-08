# DE Scenario: Regex Field Extraction

## Real-World Context

Unstructured text columns are everywhere in data: log messages, user comments, support tickets, email bodies. Extracting structured fields (emails, IPs, URLs, timestamps) from these columns is a core DE task. Regex is the right tool when the data has consistent patterns but isn't formally structured.

The key principle: compile patterns once, apply them many times. Pre-compiled regex patterns are significantly faster than re-compiling per row.

## Worked Example

Apply a library of pre-compiled regex patterns to each text value. Each pattern targets a specific field type (email, IP, URL, etc.). The extraction runs independently for each type - a single text might yield an email, an IP and a timestamp.

```
Input: "User admin@company.com logged in from 192.168.1.100 at 2024-01-15T08:30:00Z"

Apply patterns:
  email:         admin@company.com matches [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
  ipv4:          192.168.1.100 matches \b(?:(?:25[0-5]|...)\.){3}...\b
  timestamp_iso: 2024-01-15T08:30:00Z matches \d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}...
  url:           no match
  phone:         no match
  uuid:          no match

Extracted: {
    "email": ["admin@company.com"],
    "ipv4": ["192.168.1.100"],
    "timestamp_iso": ["2024-01-15T08:30:00Z"]
}

For a batch of 1M rows, the compiled patterns run in a single pass
per pattern. Pre-compilation avoids re-parsing the regex for each row.
```

## Key Design Decisions

1. **Pre-compile patterns.** `re.compile()` once at module level, not per row. The compilation cost is significant for complex patterns.
2. **Named capture groups for complex formats.** `(?P<ip>...)` makes the extracted fields self-documenting. Essential when the extraction is part of a pipeline that others maintain.
3. **Keep it simple.** Email regex doesn't need to handle every RFC 5322 edge case. Match the 99% case and quarantine the rest.
4. **Return all matches, not just the first.** A text might contain multiple emails or IPs. Use `findall` or `finditer`, not `search`.
5. **Separate extraction from validation.** Extract with regex, then validate the extracted values (is this IP in a valid range? Is this email domain active?).
