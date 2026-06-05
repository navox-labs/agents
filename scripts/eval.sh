#!/usr/bin/env bash
# Agent Quality Eval — Layer 1: Static Analysis
# Scores each agent prompt 0-10 against the quality rubric.
# Usage: bash scripts/eval.sh

set -euo pipefail

AGENTS_DIR=".claude/agents"
PASS_THRESHOLD=8
TOTAL_PASS=0
TOTAL_FAIL=0
TOTAL_SKIP=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "======================================"
echo "  AGENT QUALITY EVAL — Layer 1"
echo "  Static Analysis (10-point rubric)"
echo "======================================"
echo ""

# Skip list — agents that don't follow the standard structure
SKIP_LIST="installer.md"

for agent_file in "$AGENTS_DIR"/*.md; do
    filename=$(basename "$agent_file")
    score=0
    issues=""

    # Skip utility agents
    if echo "$SKIP_LIST" | grep -q "$filename"; then
        echo -e "${YELLOW}SKIP${NC}  $filename (utility agent, exempt from rubric)"
        TOTAL_SKIP=$((TOTAL_SKIP + 1))
        continue
    fi

    # 1. Frontmatter completeness
    if grep -q "^name:" "$agent_file" && \
       grep -q "^description:" "$agent_file" && \
       grep -q "^model:" "$agent_file" && \
       grep -q "^tools:" "$agent_file"; then
        score=$((score + 1))
    else
        issues="$issues\n  - Missing frontmatter field(s)"
    fi

    # 2. Mode coverage (PLAN + 2 operational modes)
    mode_count=$(grep -c "\[MODE:" "$agent_file" 2>/dev/null || echo "0")
    has_plan=$(grep -c "\[MODE: PLAN\]" "$agent_file" 2>/dev/null || echo "0")
    if [ "$filename" = "local-review.md" ]; then
        # local-review is exempt from PLAN mode requirement
        if [ "$mode_count" -ge 1 ]; then
            score=$((score + 1))
        else
            issues="$issues\n  - No modes defined"
        fi
    elif [ "$has_plan" -ge 1 ] && [ "$mode_count" -ge 3 ]; then
        score=$((score + 1))
    else
        issues="$issues\n  - Needs PLAN + 2 operational modes (found $mode_count modes)"
    fi

    # 3. Anti-hallucination rules
    if grep -qi "evidence\|verify\|reproduce\|never guess\|investigate before\|proven" "$agent_file"; then
        score=$((score + 1))
    else
        issues="$issues\n  - No anti-hallucination rules found"
    fi

    # 4. Handoff contracts
    if grep -q "## Handoff Contract" "$agent_file" && \
       grep -q "Self-validation checklist" "$agent_file"; then
        score=$((score + 1))
    else
        issues="$issues\n  - Missing Handoff Contract or self-validation checklist"
    fi

    # 5. Anti-sycophancy (check for absence of agreement-first patterns)
    if grep -qi "never say.*great idea\|anti-sycophancy\|not a cheerleader\|do not agree" "$agent_file" || \
       ! echo "$filename" | grep -qE "strategist|reviewer"; then
        score=$((score + 1))
    else
        issues="$issues\n  - Strategist/reviewer missing anti-sycophancy rules"
    fi

    # 6. Error handling instructions
    if grep -qi "if.*fail\|when.*wrong\|stop.*failure\|missing.*input\|flag.*missing" "$agent_file"; then
        score=$((score + 1))
    else
        issues="$issues\n  - No error handling instructions found"
    fi

    # 7. Structured output format
    if grep -q "## Output Format" "$agent_file"; then
        score=$((score + 1))
    else
        issues="$issues\n  - Missing ## Output Format section"
    fi

    # 8. Scope boundaries
    if grep -q "## What You Never Do" "$agent_file"; then
        score=$((score + 1))
    else
        issues="$issues\n  - Missing ## What You Never Do section"
    fi

    # 9. Preamble reference (ETHOS.md)
    if grep -qi "ETHOS.md\|ethos" "$agent_file"; then
        score=$((score + 1))
    else
        issues="$issues\n  - No ETHOS.md reference in Identity"
    fi

    # 10. Memory integration
    if grep -q "## Project memory" "$agent_file" && \
       grep -q "Current State" "$agent_file" && \
       grep -q "History" "$agent_file"; then
        score=$((score + 1))
    else
        issues="$issues\n  - Missing Project memory section with Current State + History"
    fi

    # Report
    if [ "$score" -ge "$PASS_THRESHOLD" ]; then
        echo -e "${GREEN}PASS${NC}  $filename — $score/10"
        TOTAL_PASS=$((TOTAL_PASS + 1))
    else
        echo -e "${RED}FAIL${NC}  $filename — $score/10"
        echo -e "$issues"
        TOTAL_FAIL=$((TOTAL_FAIL + 1))
    fi
done

echo ""
echo "======================================"
echo -e "  Results: ${GREEN}$TOTAL_PASS passed${NC}, ${RED}$TOTAL_FAIL failed${NC}, ${YELLOW}$TOTAL_SKIP skipped${NC}"
echo "  Threshold: $PASS_THRESHOLD/10"
echo "======================================"

if [ "$TOTAL_FAIL" -gt 0 ]; then
    exit 1
fi
