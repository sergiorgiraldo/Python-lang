"""
DE Scenario: Extract structured fields from unstructured text using regex.

Real-world application: parsing URLs, emails, IP addresses, phone numbers
and other structured data from free-text columns, log messages, or
user-generated content.

Run: uv run python -m patterns.09_string_parsing.de_scenarios.regex_extraction
"""

import re
from dataclasses import dataclass


@dataclass
class ExtractionResult:
    """Result of extracting fields from text."""

    original: str
    extracted: dict[str, list[str]]


# Compiled patterns for common field types
PATTERNS = {
    "email": re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    ),
    "ipv4": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
        r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
    ),
    "url": re.compile(
        r"https?://[^\s<>\"']+[^\s<>\"'.,;:!?)]"
    ),
    "phone_us": re.compile(
        r"(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}"
    ),
    "timestamp_iso": re.compile(
        r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?"
    ),
    "uuid": re.compile(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    ),
}


def extract_fields(text: str, field_types: list[str] | None = None) -> ExtractionResult:
    """
    Extract structured fields from unstructured text.

    Args:
        text: The text to extract from.
        field_types: Which field types to extract. None = all.
    """
    patterns_to_use = PATTERNS
    if field_types:
        patterns_to_use = {k: v for k, v in PATTERNS.items() if k in field_types}

    extracted: dict[str, list[str]] = {}
    for name, pattern in patterns_to_use.items():
        matches = pattern.findall(text)
        if matches:
            extracted[name] = matches

    return ExtractionResult(original=text, extracted=extracted)


def extract_with_named_groups(text: str, pattern: str) -> list[dict[str, str]]:
    """
    Extract fields using a regex with named capture groups.

    Named groups make the extraction self-documenting:
    (?P<timestamp>...) (?P<method>...) (?P<path>...) (?P<status>...)
    """
    compiled = re.compile(pattern)
    results = []
    for match in compiled.finditer(text):
        results.append(match.groupdict())
    return results


def build_extraction_pipeline(
    texts: list[str], field_types: list[str] | None = None
) -> list[ExtractionResult]:
    """
    Run extraction on a batch of texts.

    In production, this would be a UDF applied to a DataFrame column
    or a step in a streaming pipeline.
    """
    return [extract_fields(text, field_types) for text in texts]


if __name__ == "__main__":
    print("=== Regex Field Extraction ===\n")

    sample_texts = [
        "User admin@company.com logged in from 192.168.1.100 at 2024-01-15T08:30:00Z",
        "Error connecting to https://api.example.com/v2/users - timeout after 30s",
        "Contact support at support@example.com or call (555) 123-4567",
        "Transaction a1b2c3d4-e5f6-7890-abcd-ef1234567890 failed for user bob@test.org",
    ]

    for text in sample_texts:
        result = extract_fields(text)
        print(f"  Text: {text[:70]}...")
        for field_type, values in result.extracted.items():
            print(f"    {field_type}: {values}")
        print()

    print("=== Named Group Extraction (Access Log) ===\n")

    access_log = """
    192.168.1.1 - - [15/Jan/2024:08:30:00 +0000] "GET /api/users HTTP/1.1" 200 1234
    10.0.0.5 - admin [15/Jan/2024:08:30:01 +0000] "POST /api/login HTTP/1.1" 401 89
    192.168.1.2 - - [15/Jan/2024:08:30:02 +0000] "GET /api/health HTTP/1.1" 200 15
    """

    pattern = (
        r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s+-\s+(?P<user>\S+)\s+'
        r'\[(?P<timestamp>[^\]]+)\]\s+'
        r'"(?P<method>\w+)\s+(?P<path>\S+)\s+\S+"\s+'
        r'(?P<status>\d+)\s+(?P<bytes>\d+)'
    )

    records = extract_with_named_groups(access_log, pattern)
    for r in records:
        print(f"  {r['ip']:15s} {r['method']:6s} {r['path']:20s} → {r['status']}")
