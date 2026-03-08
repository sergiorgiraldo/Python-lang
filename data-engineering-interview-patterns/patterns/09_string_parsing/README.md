# String Parsing Pattern

## What Is It?

### The basics

String parsing is the process of extracting structured information from unstructured or semi-structured text. In Python, this ranges from simple `str.split()` calls to complex state machines that track context as they walk through each character.

Unlike the algorithmic patterns (hash maps, binary search, etc.), string parsing doesn't have one core data structure. Instead, it's a toolkit of techniques:

```python
# Level 1: Split and strip
fields = line.split(",")
name = fields[0].strip()

# Level 2: Regex extraction
match = re.search(r'(\d{4}-\d{2}-\d{2}) (\w+): (.+)', line)
timestamp, level, message = match.groups()

# Level 3: Character-by-character with state
for char in text:
    if state == "normal" and char == '"':
        state = "quoted"
    elif state == "quoted" and char == '"':
        state = "normal"
    # ... handle each character based on current state

# Level 4: Stack-based for nested structures
for char in text:
    if char == '{':
        stack.append(current_object)
    elif char == '}':
        completed = stack.pop()
```

Each level handles progressively more complex input. Simple delimited data needs Level 1. Log files with known formats need Level 2. Data with quoting, escaping or nesting needs Levels 3-4.

### Why parsing matters more for DEs than SWEs

Most software engineers deal with well-structured data: JSON from APIs, protocol buffers, typed database results. Data engineers deal with whatever arrives: malformed CSVs with embedded delimiters, log files from systems you don't control, vendor exports with inconsistent quoting, semi-structured JSON with schema drift.

The ability to parse messy data reliably and efficiently is a core DE skill. It's not glamorous, but a single unhandled edge case (a comma inside a quoted field, a newline in a JSON string, a null byte in a log line) can corrupt millions of rows.

### The four parsing approaches

**1. Split/Join (Level 1)**
Use when: data has consistent delimiters and no quoting/escaping.

`line.split(",")` handles simple CSVs. `"|".join(fields)` reconstructs them. Fast (C implementation in CPython) and readable. Falls apart when fields contain the delimiter.

**2. Regex (Level 2)**
Use when: data has a known format and you need to extract specific fields.

Regular expressions handle extraction well but are dangerous for parsing complex grammars. They handle log lines, URLs, timestamps and email addresses well. They handle nested structures (JSON, XML, HTML) poorly. The rule of thumb: if your regex needs lookahead/lookbehind or has more than 3 capture groups, consider a different approach.

```python
# Good regex use: extract fields from a known log format
pattern = r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(?P<level>\w+)\] (?P<message>.+)'

# Bad regex use: parse nested JSON
# Don't. Use json.loads() or a proper parser.
```

**3. Character-by-character with state (Level 3)**
Use when: data has quoting, escaping or context-dependent delimiters.

Walk through each character, maintaining state (am I inside quotes? Did I just see a backslash?). This is how CSV parsers work internally. More code than regex but handles edge cases that regex can't.

**4. Stack-based parsing (Level 4)**
Use when: data has nesting (brackets, tags, nested JSON).

Same stack mechanics as Pattern 08 but applied to parsing rather than validation. Push context when entering a nested structure, pop when leaving. This is how JSON parsers and XML parsers work internally.

### Connection to data engineering

Parsing shows up in almost every pipeline:

- **Ingestion:** Raw files arrive in CSV, JSON, XML, log formats or proprietary exports. Parsing is the first transformation step.
- **Data quality:** Detecting malformed records requires understanding the expected format well enough to identify violations.
- **Schema inference:** Examining sample data to determine column types, nullable fields and nested structure requires parsing.
- **Log analysis:** Extracting metrics from application logs, audit trails and system events.
- **CDC parsing:** Change data capture events from databases arrive as structured-but-complex payloads that need field extraction.

### What the problems in this section cover

| Problem | Parsing technique | What it models |
|---|---|---|
| Encode/Decode Strings | Delimiter design + length prefixing | Data serialization |
| Decode String | Stack-based nested expansion | Template/config expansion |
| Remove Comments | State machine (normal/string/comment) | Code/config preprocessing |
| Validate IP Address | Structured validation with rules | Input validation |

| DE Scenario | Parsing technique | What it models |
|---|---|---|
| Log line parsing | Regex + fallback | Ingestion from mixed-format logs |
| Malformed CSV handling | Character-by-character with state | Handling real-world dirty data |
| Schema inference | Type detection + sampling | Automated pipeline setup |
| Regex field extraction | Named capture groups | Unstructured text to columns |

## When to Use It

**Recognition signals in interviews:**
- "Parse this string..."
- "Extract fields from..."
- "Handle escaped/quoted characters..."
- "Validate this format..."
- Anything involving nested or structured text

**Recognition signals in DE work:**
- Raw file ingestion with inconsistent formats
- Log analysis and metric extraction
- Data validation before loading
- Schema detection for new data sources

## Visual Aid

```
State machine for parsing code with comments:

  Input: "int x = 1; // comment\nint y = 2;"

  State: NORMAL
    'i' → output 'i'    (normal character)
    'n' → output 'n'
    't' → output 't'
    ' ' → output ' '
    ...
    ';' → output ';'
    ' ' → output ' '
    '/' → peek ahead...
    '/' → it's "//" → switch to LINE_COMMENT state

  State: LINE_COMMENT
    'c' → skip           (inside comment, ignore everything)
    'o' → skip
    ...
    '\n' → switch back to NORMAL, output '\n'

  State: NORMAL (again)
    'i' → output 'i'
    ...

  Output: "int x = 1; \nint y = 2;"

  For block comments (/* ... */), add a BLOCK_COMMENT state that
  only exits when it sees "*/". The state machine handles all
  combinations cleanly.
```

## Trade-offs

**When to use each parsing approach:**
- `str.split()` vs regex: split is 5-10x faster for simple delimiters. Use regex only when split can't express the pattern.
- Regex vs state machine: regex is more concise for flat patterns. State machines handle context and nesting that regex can't.
- Custom parser vs library: Use `csv.reader`, `json.loads`, `xml.etree` when the format is standard. Write custom parsers only when the data deviates from the standard (which in DE, it often does).
- Strict vs lenient parsing: strict parsing rejects malformed input (safe but loses data). Lenient parsing attempts recovery (keeps more data but risks corruption). In pipelines, parse leniently but log everything you had to fix.

### Scale characteristics

String parsing is typically O(n) time and O(n) space (for the output string or intermediate structures). The constants matter: string operations in Python are slower than in C-based parsers.

| Approach | Speed for 1GB file | Memory | Use case |
|---|---|---|---|
| Python string methods | ~30 seconds | O(line) per line | Simple field extraction |
| Regex (re module) | ~20 seconds | O(line) per line | Pattern matching |
| Compiled parser (json, csv) | ~5 seconds | O(line) per line | Structured formats |
| Streaming parser (ijson, csv reader) | ~5 seconds | O(1) | Files too large for memory |

**Production parsing at scale:** In data pipelines, raw string parsing is rarely done in Python. Instead, Spark reads structured formats (JSON, CSV, Parquet) with built-in parsers that are optimized in JVM code. Custom parsing (log formats, proprietary encodings) uses Spark UDFs, which are 10-100x slower than built-in functions because data crosses the JVM-Python boundary per row. For custom parsing at scale, write it in Scala/Java or use vectorized UDFs (pandas UDFs in PySpark).

**Encoding issues at scale:** Real-world data has encoding inconsistencies: mixed UTF-8 and Latin-1 in the same file, null bytes, invalid Unicode sequences. Production parsers need fallback strategies (replace invalid bytes, skip malformed rows, log and quarantine). The Python `errors='replace'` parameter handles this per-file, but at pipeline scale you need metrics: "how many rows had encoding errors?" This is a data quality concern that string parsing algorithms don't address.

### SQL equivalent

String parsing in SQL uses functions like SPLIT, REGEXP_EXTRACT, SUBSTR, TRIM, JSON_EXTRACT and PARSE_JSON. BigQuery's REGEXP_EXTRACT and Snowflake's REGEXP_SUBSTR handle pattern matching. JSON parsing is built into all modern SQL engines. For complex multi-step parsing (like Decode String with nested brackets), SQL is the wrong tool - do it in a UDF or pre-processing step. The SQL section's optimization subsection discusses when to parse in SQL vs preprocessing.

## Problems in This Section

| # | Problem | Difficulty | Key Concept |
|---|---|---|---|
| [271](https://leetcode.com/problems/encode-and-decode-strings/) | [Encode and Decode Strings](problems/271_encode_decode_strings.md) | Medium | Length-prefix serialization |
| [394](https://leetcode.com/problems/decode-string/) | [Decode String](problems/394_decode_string.md) | Medium | Stack-based nested expansion |
| [722](https://leetcode.com/problems/remove-comments/) | [Remove Comments](problems/722_remove_comments.md) | Medium | State machine parsing |
| [468](https://leetcode.com/problems/validate-ip-address/) | [Validate IP Address](problems/468_validate_ip_address.md) | Medium | Structured validation |

## DE Scenarios

| Scenario | Parsing Technique | Real-World Use |
|---|---|---|
| [Log Line Parsing](de_scenarios/log_parsing.md) | Regex + fallback | Extract fields from application logs |
| [Malformed CSV Handling](de_scenarios/malformed_csv.md) | Char-by-char with state | Handle real-world dirty CSV files |
| [Schema Inference](de_scenarios/schema_inference.md) | Type detection + sampling | Auto-detect column types from samples |
| [Regex Field Extraction](de_scenarios/regex_extraction.md) | Named capture groups | Parse URLs, emails, IPs from text |
