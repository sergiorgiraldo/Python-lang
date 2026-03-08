# DE Scenario: Malformed CSV Handling

## Real-World Context

CSV is the most common data exchange format and also the most frequently broken. Vendor exports, legacy system dumps and user uploads routinely violate the RFC 4180 spec in creative ways: mixed quoting styles, embedded newlines, inconsistent delimiters, BOM characters, null bytes, and field counts that vary row to row.

Python's `csv.reader` handles well-formed CSVs. For the rest, you need a combination of preprocessing (cleaning known issues) and a fallback state-machine parser for cases the standard library can't handle.

## Worked Example

The robust approach: preprocess the text to fix known issues (BOM, null bytes, line endings), then use the standard csv.reader with error handling. Track field count inconsistencies separately - too many fields get truncated, too few get padded with empty strings. Never silently drop records.

```
Input (messy vendor export):
  Line 1: '\ufeffname,city,note'      ← BOM at start
  Line 2: 'Alice,New York,"likes ""pizza""'  ← escaped quotes
  Line 3: 'Charlie,"San Francisco, CA",has comma'  ← comma in quoted field
  Line 4: 'Frank,Boston'               ← only 2 fields (expected 3)
  Line 5: 'Grace,Denver,note,extra'    ← 4 fields (expected 3)

Preprocessing:
  Strip BOM (\ufeff) from start
  Remove null bytes (\x00)
  Normalize line endings to \n

Parse with csv.reader (max_fields=3):
  Line 1: ["name", "city", "note"] → header, 3 fields ✓
  Line 2: ["Alice", "New York", 'likes "pizza"'] → 3 fields ✓
           (csv.reader handles "" → " automatically)
  Line 3: ["Charlie", "San Francisco, CA", "has comma"] → 3 fields ✓
           (quoted field with comma handled correctly)
  Line 4: ["Frank", "Boston"] → 2 fields, expected 3
           Error logged. Pad to: ["Frank", "Boston", ""]
  Line 5: ["Grace", "Denver", "note", "extra"] → 4 fields, expected 3
           Error logged. Truncate to: ["Grace", "Denver", "note"]

Result: 5 records parsed, 2 with field count warnings.
No data lost. Errors logged for review.
```

## Key Design Decisions

1. **Preprocess then parse.** Fix the known issues (BOM, null bytes, line endings) before handing to csv.reader. Don't try to handle everything in one pass.
2. **Pad and truncate, don't drop.** Inconsistent field counts are warnings, not fatal errors. Pad short rows with empty strings. Truncate long rows. Log both.
3. **Track field width distribution.** If 99% of rows have 5 fields and 1% have 4, the 4-field rows are probably malformed. If it's 50/50, the format might have changed mid-file.
4. **Keep the raw line.** Always preserve the original data alongside the parsed result. You'll need it for debugging.
5. **State machine for the hard cases.** When csv.reader fails (e.g., unescaped quotes mid-field), a manual character-by-character parser with explicit state transitions can recover.
