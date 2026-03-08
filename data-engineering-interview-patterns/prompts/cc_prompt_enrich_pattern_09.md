# CC Prompt: Enrich Pattern 09 (String Parsing) to Principal Level

## Context

Pattern 09 has 4 problems and 4 DE scenarios. Enrichment adds principal-level depth to .md files only.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Do NOT modify any .py files. Only ADD content to .md files.
- 3-8 sentences per "At Scale" section

---

## Task 1: Enrich README.md Trade-offs Section

In `patterns/09_string_parsing/README.md`, find `## Trade-offs` and ADD:

```markdown
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
```

## Task 2: Add "At Scale" Section to Each Problem .md

### 125_valid_palindrome.md
```markdown
## At Scale

Two-pointer palindrome check uses O(1) memory and O(n) time. For a 1GB string, this takes ~10 seconds and uses no extra memory beyond the input. The reversed-string approach creates a copy: O(n) memory, which is 1GB wasted for a 1GB input. At scale, palindrome checks are rarely done on enormous strings. The more relevant pattern is the two-pointer technique on cleaned/normalized data: filtering out non-alphanumeric characters while processing is a streaming transformation. In production, data cleaning (strip whitespace, normalize case, remove special characters) happens at ingestion time, not query time. Doing it at query time repeatedly is a performance anti-pattern.
```

### 271_encode_decode_strings.md
```markdown
## At Scale

Length-prefix encoding (write length, then delimiter, then string) produces output of size O(total characters + n * delimiter overhead). For 10M strings averaging 50 characters, the encoded form is ~510MB (500MB for strings + ~10MB for length prefixes). This is the same encoding that network protocols use (TCP length-prefixed frames, Protobuf varint-prefixed fields). At scale, serialization format choice matters enormously: JSON is human-readable but 2-5x larger than binary formats. Protobuf, Avro, Parquet and MessagePack are production choices that use length-prefixed or schema-based encoding for efficiency. Understanding the algorithmic basis (length-prefixed encoding) helps you reason about why binary formats are faster and smaller.
```

### 394_decode_string.md
```markdown
## At Scale

The stack holds nested multiplier/string pairs. Memory is O(nesting depth * average string length). For shallow nesting (2-3 levels) with short patterns, this is negligible. The risk: deeply nested patterns with high multipliers produce exponentially large output. `3[3[3[3[a]]]]` expands to 81 characters. `100[100[100[a]]]` expands to 1M characters. In production, template expansion (Jinja in dbt, variable substitution in configs) has the same risk. Always set expansion limits to prevent accidental memory bombs. The stack-based decoder is O(output size) - the output itself can be the bottleneck, not the algorithm.
```

### 722_remove_comments.md
```markdown
## At Scale

The state machine approach (tracking whether you're inside a block comment) is O(n) and processes line by line: O(1) memory per line. For a 100K-line source file, this is instant. At scale, the relevant application is processing structured text files in pipelines: stripping headers, removing metadata lines, extracting content from markup. These are streaming operations that don't need the full file in memory. In production, comment removal and text cleanup are pre-processing steps before indexing or analysis. The state machine pattern (tracking "am I inside X?") generalizes to any delimited-region processing: SQL string literals, HTML tags, XML CDATA sections.
```

## Task 3: Enrich Interview Tips with Evaluator Framing

### 125 (Valid Palindrome):
```markdown
**What the interviewer evaluates:** This is a warm-up testing two things: string cleaning (removing non-alphanumeric characters) and the two-pointer technique. Using `char.isalnum()` and `char.lower()` shows Python fluency. The two-pointer O(1)-space solution is preferred over reversing the string. Finishing quickly earns time for harder problems.
```

### 271 (Encode and Decode):
```markdown
**What the interviewer evaluates:** Designing a serialization scheme that handles arbitrary strings (including the delimiter character) tests protocol design thinking. The length-prefix approach is the standard solution. Mentioning that this is how real protocols work (TCP framing, Protobuf) shows systems knowledge. The follow-up "what about streaming?" (answer: the length prefix tells you exactly how many bytes to read next) connects to network programming.
```

### 394 (Decode String):
```markdown
**What the interviewer evaluates:** Stack-based nested processing tests implementation precision. Handling the multiplier (which can be multi-digit) and the nesting (stack push on `[`, pop and multiply on `]`) correctly is the challenge. Off-by-one errors in character processing are common. Mentioning output size limits and template expansion safety shows production awareness.
```

### 722 (Remove Comments):
```markdown
**What the interviewer evaluates:** State machine design (tracking in_block_comment state) tests systematic thinking. Handling the interaction between line comments and block comments (a `//` inside a `/* */` is not a line comment) tests attention to edge cases. Clean state transition logic with clear variable names is more important than clever tricks.
```

## Task 4: Glossary Updates

Add to WORKING_GLOSSARY.md:

- **length-prefix encoding**: Serialization technique where each value is preceded by its byte length. Enables unambiguous parsing without delimiter escaping. Used in TCP, Protobuf, Avro.
- **vectorized UDF**: User-defined function that processes data in batches (pandas DataFrames) rather than row-by-row. 10-100x faster than scalar UDFs in PySpark because it minimizes JVM-Python serialization overhead.
- **state machine (parsing)**: Parser that tracks a current state and transitions between states based on input characters. Handles context-dependent parsing (e.g., "am I inside a quoted string?").
- **data quarantine**: Pattern for isolating malformed or unparseable records in a separate storage location for later investigation, rather than failing the entire pipeline.

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== At Scale sections ==="
for f in patterns/09_string_parsing/problems/*.md; do
    name=$(basename "$f")
    has_scale=$(grep -q "## At Scale" "$f" && echo "Y" || echo "N")
    echo "  $name: At Scale=$has_scale"
done

echo ""
echo "=== README enriched ==="
grep -q "Scale characteristics" patterns/09_string_parsing/README.md && echo "✅" || echo "❌"

echo ""
echo "=== Evaluator framing ==="
for f in patterns/09_string_parsing/problems/*.md; do
    has_eval=$(grep -q "interviewer evaluates" "$f" && echo "Y" || echo "N")
    echo "  $(basename $f): evaluator=$has_eval"
done

echo ""
echo "=== Style + tests ==="
grep -rn "—" patterns/09_string_parsing/ --include="*.md" && echo "❌" || echo "✅ No em dashes"
uv run pytest patterns/09_string_parsing/ --tb=short -q 2>&1 | tail -3
```
