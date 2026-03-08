#!/bin/bash
# Comprehensive audit of all patterns 01-07
# Run from ~/dev/projects/data-engineering-interview-patterns/

cd ~/dev/projects/data-engineering-interview-patterns/ || exit 1

echo "=========================================="
echo "  PATTERNS 01-07 COMPREHENSIVE AUDIT"
echo "=========================================="
echo ""

# Discover pattern directories
PATTERNS=(
    "patterns/01_hash_map"
    "patterns/02_two_pointers"
    "patterns/03_binary_search"
    "patterns/04_sliding_window"
    "patterns/05_heap_priority_queue"
    "patterns/06_graph_topological_sort"
    "patterns/07_intervals"
)

# Check dirs exist
echo "=== CHECK 1: Pattern directories exist ==="
for dir in "${PATTERNS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir"
    else
        echo "  ❌ $dir MISSING"
    fi
done
echo ""

# README teaching sections
echo "=== CHECK 2: README has deep teaching subsections ==="
for dir in "${PATTERNS[@]}"; do
    name=$(basename "$dir")
    readme="$dir/README.md"
    if [ ! -f "$readme" ]; then
        echo "  ❌ $name: no README.md"
        continue
    fi
    count=$(grep -c "^### " "$readme")
    has_what=$(grep -qi "what is it\|the basics\|core idea" "$readme" && echo "Y" || echo "N")
    has_visual=$(grep -qi "visual aid" "$readme" && echo "Y" || echo "N")
    has_tradeoffs=$(grep -qi "trade.off" "$readme" && echo "Y" || echo "N")
    has_de=$(grep -qi "data engineering\|connection to" "$readme" && echo "Y" || echo "N")
    if [ "$has_what" = "Y" ] && [ "$has_visual" = "Y" ] && [ "$has_tradeoffs" = "Y" ] && [ "$has_de" = "Y" ]; then
        echo "  ✅ $name: $count subsections (What/Visual/Tradeoffs/DE all present)"
    else
        echo "  ⚠️  $name: $count subsections (What=$has_what Visual=$has_visual Tradeoffs=$has_tradeoffs DE=$has_de)"
    fi
done
echo ""

# Problem and DE scenario counts
echo "=== CHECK 3: Problem + DE scenario file counts ==="
for dir in "${PATTERNS[@]}"; do
    name=$(basename "$dir")
    prob_count=$(find "$dir/problems" -name "*.md" 2>/dev/null | wc -l)
    de_count=$(find "$dir/de_scenarios" -name "*.md" 2>/dev/null | wc -l)
    echo "  $name: $prob_count problems, $de_count DE scenarios"
done
echo ""

# Worked examples present in every .md
echo "=== CHECK 4: Every problem + DE scenario has a Worked Example ==="
missing=0
for dir in "${PATTERNS[@]}"; do
    name=$(basename "$dir")
    for f in "$dir"/problems/*.md "$dir"/de_scenarios/*.md; do
        [ -f "$f" ] || continue
        fname=$(basename "$f")
        if ! grep -q "## Worked Example" "$f"; then
            echo "  ❌ $name/$fname: MISSING Worked Example"
            missing=$((missing + 1))
        fi
    done
done
if [ $missing -eq 0 ]; then
    echo "  ✅ All files have Worked Examples"
fi
echo ""

# Worked examples start with plain English (not code fence)
echo "=== CHECK 5: Worked Examples start with prose (not code fence) ==="
bad=0
for dir in "${PATTERNS[@]}"; do
    name=$(basename "$dir")
    for f in "$dir"/problems/*.md "$dir"/de_scenarios/*.md; do
        [ -f "$f" ] || continue
        fname=$(basename "$f")
        first_line=$(awk '/## Worked Example/{found=1; next} found && /\S/{print; exit}' "$f")
        if echo "$first_line" | grep -q '^\s*```'; then
            echo "  ❌ $name/$fname: starts with code fence"
            bad=$((bad + 1))
        fi
    done
done
if [ $bad -eq 0 ]; then
    echo "  ✅ All Worked Examples start with plain English"
fi
echo ""

# Approach explanation depth
echo "=== CHECK 6: Approach explanations are substantial (>3 lines) ==="
thin=0
total=0
for dir in "${PATTERNS[@]}"; do
    name=$(basename "$dir")
    for f in "$dir"/problems/*.md; do
        [ -f "$f" ] || continue
        fname=$(basename "$f")
        while IFS= read -r line_count; do
            total=$((total + 1))
            if [ "$line_count" -lt 4 ]; then
                thin=$((thin + 1))
            fi
        done < <(awk '/📝 Explanation/{found=1; lines=0; next} found && /<\/details>/{print lines; found=0} found && /\S/{lines++}' "$f")
    done
done
echo "  Total explanation blocks: $total"
echo "  Substantial (4+ lines): $((total - thin))"
echo "  Thin (<4 lines): $thin"
if [ $thin -gt 0 ]; then
    echo "  (Thin blocks are typically brute force approaches - acceptable)"
fi
echo ""

# Style violations
echo "=== CHECK 7: Style violations ==="
echo "  --- Oxford commas (', and ' or ', or ') ---"
ox_count=0
for dir in "${PATTERNS[@]}"; do
    name=$(basename "$dir")
    for f in "$dir"/problems/*.md "$dir"/de_scenarios/*.md "$dir"/README.md; do
        [ -f "$f" ] || continue
        fname=$(basename "$f")
        # Skip code blocks and look for ", and " or ", or " patterns
        hits=$(grep -n ", and \|, or " "$f" | grep -v '^\s*#' | grep -v '```' | grep -v 'left, and right\|push, and pop' | head -3)
        if [ -n "$hits" ]; then
            echo "  ⚠️  $name/$fname:"
            echo "$hits" | sed 's/^/      /'
            ox_count=$((ox_count + 1))
        fi
    done
done
if [ $ox_count -eq 0 ]; then
    echo "  ✅ No Oxford commas found"
fi
echo ""

echo "  --- Em dashes (—) ---"
em_count=0
for dir in "${PATTERNS[@]}"; do
    for f in "$dir"/problems/*.md "$dir"/de_scenarios/*.md "$dir"/README.md; do
        [ -f "$f" ] || continue
        if grep -q "—" "$f"; then
            echo "  ❌ $(basename $(dirname "$f"))/$(basename "$f"): contains em dash"
            em_count=$((em_count + 1))
        fi
    done
done
if [ $em_count -eq 0 ]; then
    echo "  ✅ No em dashes found"
fi
echo ""

echo "  --- Exclamation points (outside code) ---"
ex_count=0
for dir in "${PATTERNS[@]}"; do
    for f in "$dir"/problems/*.md "$dir"/de_scenarios/*.md "$dir"/README.md; do
        [ -f "$f" ] || continue
        # Find ! that aren't != or inside code blocks
        hits=$(grep -n '!' "$f" | grep -v '!=' | grep -v '^\s*```' | grep -v '^\s*#!' | head -3)
        if [ -n "$hits" ]; then
            echo "  ⚠️  $(basename $(dirname "$f"))/$(basename "$f"):"
            echo "$hits" | sed 's/^/      /'
            ex_count=$((ex_count + 1))
        fi
    done
done
if [ $ex_count -eq 0 ]; then
    echo "  ✅ No exclamation points found"
fi
echo ""

# Duplicate Worked Example sections
echo "=== CHECK 8: No duplicate Worked Example sections ==="
dupes=0
for dir in "${PATTERNS[@]}"; do
    name=$(basename "$dir")
    for f in "$dir"/problems/*.md "$dir"/de_scenarios/*.md; do
        [ -f "$f" ] || continue
        fname=$(basename "$f")
        count=$(grep -c "## Worked Example" "$f")
        if [ "$count" -gt 1 ]; then
            echo "  ❌ $name/$fname: $count Worked Example sections (should be 1)"
            dupes=$((dupes + 1))
        fi
    done
done
if [ $dupes -eq 0 ]; then
    echo "  ✅ All files have exactly 1 Worked Example"
fi
echo ""

# Required sections in problem files
echo "=== CHECK 9: Problem files have all required sections ==="
required_sections=("Problem Statement" "Thought Process" "Worked Example" "Approaches" "Edge Cases" "Common Pitfalls" "Interview Tips")
missing_sections=0
for dir in "${PATTERNS[@]}"; do
    name=$(basename "$dir")
    for f in "$dir"/problems/*.md; do
        [ -f "$f" ] || continue
        fname=$(basename "$f")
        for section in "${required_sections[@]}"; do
            if ! grep -qi "## $section\|## .*$section" "$f"; then
                echo "  ❌ $name/$fname: missing '$section'"
                missing_sections=$((missing_sections + 1))
            fi
        done
    done
done
if [ $missing_sections -eq 0 ]; then
    echo "  ✅ All problem files have all required sections"
fi
echo ""

# Tests
echo "=== CHECK 10: Full test suite ==="
uv run pytest --tb=short 2>&1 | tail -5
echo ""

# No .py files accidentally modified
echo "=== CHECK 11: Git status (should only show .md changes) ==="
non_md=$(git diff --name-only | grep -v '\.md$' | head -10)
if [ -n "$non_md" ]; then
    echo "  ❌ Non-.md files modified:"
    echo "$non_md" | sed 's/^/      /'
else
    echo "  ✅ Only .md files modified (or no uncommitted changes)"
fi
echo ""

echo "=========================================="
echo "  AUDIT COMPLETE"
echo "=========================================="
