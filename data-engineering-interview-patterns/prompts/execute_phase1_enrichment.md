# CC Prompt: Execute All Phase 1 Enrichments

## Overview

Run enrichment prompts for all 12 patterns in sequence. Each prompt adds principal-level content to .md files only (no code changes). After all 12 are complete, run the final verification.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Execution Order

Execute these prompts one at a time. After each, verify tests still pass before proceeding.

1. `prompts/cc_prompt_enrich_pattern_01.md`
2. `prompts/cc_prompt_enrich_pattern_02.md`
3. `prompts/cc_prompt_enrich_pattern_03.md`
4. `prompts/cc_prompt_enrich_pattern_04.md`
5. `prompts/cc_prompt_enrich_pattern_05.md`
6. `prompts/cc_prompt_enrich_pattern_06.md`
7. `prompts/cc_prompt_enrich_pattern_07.md`
8. `prompts/cc_prompt_enrich_pattern_08.md`
9. `prompts/cc_prompt_enrich_pattern_09.md`
10. `prompts/cc_prompt_enrich_pattern_10.md`
11. `prompts/cc_prompt_enrich_pattern_11.md`
12. `prompts/cc_prompt_enrich_pattern_12.md`

## Important Notes

- Each prompt specifies exact content to add to specific files
- Filenames in the prompts are best guesses - CC should find the actual filenames in each pattern's problems/ directory and match by LeetCode number
- If a section already exists (e.g., Pattern 11 may already have scale content), don't duplicate - add only what's missing
- The glossary updates are cumulative - each prompt adds terms. Make sure the glossary at the end contains ALL terms from all 12 prompts
- Tests must pass after each pattern (1142 total)

## After All 12 Complete: Final Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "============================================"
echo "PHASE 1 ENRICHMENT FINAL VERIFICATION"
echo "============================================"

echo ""
echo "=== 1. All tests still pass ==="
uv run pytest --tb=short -q 2>&1 | tail -3

echo ""
echo "=== 2. At Scale sections (every problem .md) ==="
total=0
missing=0
for f in $(find patterns/ -path "*/problems/*.md" -o -path "*/de_scenarios/*.md" | sort); do
    total=$((total + 1))
    if ! grep -q "## At Scale" "$f"; then
        # DE scenarios don't need At Scale - only problem .md files
        if echo "$f" | grep -q "problems/"; then
            echo "  ❌ MISSING: $f"
            missing=$((missing + 1))
        fi
    fi
done
echo "  Total problem .md files checked: $total"
echo "  Missing At Scale: $missing"

echo ""
echo "=== 3. README Scale sections (all 12 patterns) ==="
for dir in patterns/*/; do
    name=$(basename "$dir")
    if grep -q "Scale characteristics\|Production deployment\|scale characteristics\|meta-skill" "$dir/README.md" 2>/dev/null; then
        echo "  ✅ $name"
    else
        echo "  ❌ $name: no scale section in README"
    fi
done

echo ""
echo "=== 4. Interviewer evaluation framing ==="
total=0
missing=0
for f in $(find patterns/ -path "*/problems/*.md" | sort); do
    total=$((total + 1))
    if ! grep -q "interviewer evaluates" "$f"; then
        echo "  ❌ MISSING: $(echo $f | sed 's|patterns/||')"
        missing=$((missing + 1))
    fi
done
echo "  Total: $total, Missing: $missing"

echo ""
echo "=== 5. SQL forward references (in READMEs) ==="
for dir in patterns/*/; do
    name=$(basename "$dir")
    if grep -qi "SQL\|sql section\|sql equivalent" "$dir/README.md" 2>/dev/null; then
        echo "  ✅ $name"
    else
        echo "  ⚠️  $name: no SQL forward reference"
    fi
done

echo ""
echo "=== 6. Glossary completeness ==="
for term in "broadcast join" "key skew" "external merge sort" "B-tree" "zone maps" \
    "tumbling window" "session window" "k-way merge" "t-digest" "BSP" "entity resolution" \
    "critical path" "sweep line" "interval tree" "monotonic stack" "streaming parser" \
    "adjacency list" "nested sets" "Euler tour" "heavy hitter" "sketch mergeability" \
    "pattern composition" "length-prefix" "vectorized UDF" "data quarantine"; do
    if grep -qi "$term" WORKING_GLOSSARY.md 2>/dev/null; then
        echo "  ✅ $term"
    else
        echo "  ❌ $term MISSING from glossary"
    fi
done

echo ""
echo "=== 7. No style violations introduced ==="
em_dashes=$(grep -rn "—" patterns/ --include="*.md" | wc -l)
echo "  Em dashes: $em_dashes (should be 0)"

echo ""
echo "=== 8. Final test count ==="
uv run pytest --co -q 2>&1 | tail -1
```

## Summary Report

After verification, provide:
1. How many "At Scale" sections were added
2. How many README trade-off sections were enriched
3. How many interviewer evaluation paragraphs were added
4. How many glossary terms were added
5. Total test count (should still be 1142)
6. Any issues found and fixed
