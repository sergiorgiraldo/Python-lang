# Execute Pattern 09 (String Parsing) Creation Prompts

Read and execute the following prompt files in order, one at a time. Each file creates new files in the repo. After completing each file, run its verification section and confirm it passes before moving to the next.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

**Important:** Pattern 09 has an existing skeleton (README.md with placeholder content, possibly __init__.py files). Replace any existing files with the new content. Do NOT merge with existing content.

## Execution Order

1. `prompts/create_09_part1_readme.md` - Directory setup, conftest, template, README
2. `prompts/create_09_part2_prob1_2.md` - Encode/Decode Strings (271), Decode String (394)
3. `prompts/create_09_part3_prob3_4.md` - Remove Comments (722), Validate IP Address (468)
4. `prompts/create_09_part4_de1_2.md` - Log Parsing, Malformed CSV Handling
5. `prompts/create_09_part5_de3_4.md` - Schema Inference, Regex Extraction

## After All 5 Files Are Complete

Run the comprehensive audit:

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== PATTERN 09 CREATION SUMMARY ==="

echo ""
echo "=== Full test suite ==="
uv run pytest patterns/09_string_parsing/ -v --tb=short 2>&1 | tail -20

echo ""
echo "=== File inventory ==="
echo "Python files:"
find patterns/09_string_parsing/ -name "*.py" | sort
echo ""
echo "Markdown files:"
find patterns/09_string_parsing/ -name "*.md" | sort

echo ""
echo "=== README quality ==="
grep "^### " patterns/09_string_parsing/README.md

echo ""
echo "=== Worked Example check ==="
for f in patterns/09_string_parsing/problems/*.md patterns/09_string_parsing/de_scenarios/*.md; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    has_we=$(grep -q "## Worked Example" "$f" && echo "Y" || echo "N")
    first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' "$f")
    starts_prose=$(echo "$first" | grep -q '```' && echo "CODE" || echo "PROSE")
    echo "  $name: present=$has_we, starts=$starts_prose"
done

echo ""
echo "=== Approach explanation quality ==="
for f in patterns/09_string_parsing/problems/*.md; do
    name=$(basename "$f")
    awk '/📝 Explanation/{found=1; lines=0; next} found && /<\/details>/{if(lines<4) printf "  ❌ %s: only %d lines\n", "'"$name"'", lines; else printf "  ✅ %s: %d lines\n", "'"$name"'", lines; found=0} found && /\S/{lines++}' "$f"
done

echo ""
echo "=== DE scenarios run ==="
uv run python -m patterns.09_string_parsing.de_scenarios.log_parsing 2>&1 | tail -3
uv run python -m patterns.09_string_parsing.de_scenarios.malformed_csv 2>&1 | tail -3
uv run python -m patterns.09_string_parsing.de_scenarios.schema_inference 2>&1 | tail -3
uv run python -m patterns.09_string_parsing.de_scenarios.regex_extraction 2>&1 | tail -3

echo ""
echo "=== Style violations ==="
grep -r "—" patterns/09_string_parsing/ && echo "❌ Em dashes" || echo "✅ No em dashes"
grep -rn "## Visual Walkthrough" patterns/09_string_parsing/ && echo "❌ Wrong section names" || echo "✅ Correct section names"

echo ""
echo "=== Cross-pattern test suite ==="
uv run pytest --tb=short 2>&1 | tail -3
```

Provide a comprehensive summary of what was created, test results, and any issues encountered.
