#!/usr/bin/env bash
#
# validate.sh — Repo integrity checker for navox-labs/agents
#
# Checks agent files, command files, frontmatter, handoff contracts,
# memory templates, plugin manifests, docs, and git hygiene.
#
# Run from repo root:  bash scripts/validate.sh
#
# Exit code 0 = all checks passed, 1 = failures found

set -euo pipefail

PASS=0
FAIL=0
WARN=0

pass() { PASS=$((PASS + 1)); printf "  ✓ %s\n" "$1"; }
fail() { FAIL=$((FAIL + 1)); printf "  ✗ %s\n" "$1"; }
warn() { WARN=$((WARN + 1)); printf "  ? %s\n" "$1"; }
section() { printf "\n━━━ %s\n" "$1"; }

# Ensure we're running from repo root
if [ ! -f "CLAUDE.md" ]; then
  echo "Error: run this script from the repo root (where CLAUDE.md lives)"
  exit 1
fi

# ─── Agent files ─────────────────────────────────────────────

section "Agent files (.claude/agents/)"

EXPECTED_AGENTS="architect context-manager devops fullstack installer investigator local-review qa retro reviewer security shipper spec-writer strategist ux"

for agent in $EXPECTED_AGENTS; do
  file=".claude/agents/${agent}.md"
  if [ -f "$file" ]; then
    pass "$file exists"
  else
    fail "$file MISSING"
  fi
done

# ─── Agent frontmatter ──────────────────────────────────────

section "Agent frontmatter"

for agent in $EXPECTED_AGENTS; do
  file=".claude/agents/${agent}.md"
  [ ! -f "$file" ] && continue

  # Check name field
  if grep -q "^name:" "$file"; then
    pass "$agent: has name field"
  else
    fail "$agent: MISSING name field"
  fi

  # Check description field
  if grep -q "^description:" "$file"; then
    pass "$agent: has description field"
  else
    fail "$agent: MISSING description field"
  fi

  # Check model field
  if grep -q "^model:" "$file"; then
    pass "$agent: has model field"
  else
    fail "$agent: MISSING model field"
  fi

  # Check tools field
  if grep -q "^tools:" "$file"; then
    pass "$agent: has tools field"
  else
    fail "$agent: MISSING tools field"
  fi
done

# ─── Model routing ────────────────────────────────────────────

section "Model routing"

# Opus agents: architect, security, strategist, reviewer
for agent in architect security strategist reviewer; do
  file=".claude/agents/${agent}.md"
  [ ! -f "$file" ] && continue
  if grep -q "claude-opus" "$file"; then
    pass "$agent: uses Opus"
  else
    fail "$agent: should use claude-opus model"
  fi
done

# Sonnet agents: everything else (except installer and local-review which are utility)
for agent in context-manager devops fullstack installer investigator local-review qa retro shipper spec-writer ux; do
  file=".claude/agents/${agent}.md"
  [ ! -f "$file" ] && continue
  if grep -q "claude-sonnet" "$file"; then
    pass "$agent: uses Sonnet"
  else
    fail "$agent: should use claude-sonnet model"
  fi
done

# ─── Command files ───────────────────────────────────────────

section "Command files (.claude/commands/)"

EXPECTED_COMMANDS="agency-run architect context-manager devops fullstack hire-team investigator qa retro reviewer security shipper spec-writer strategist ux"

for cmd in $EXPECTED_COMMANDS; do
  file=".claude/commands/${cmd}.md"
  if [ -f "$file" ]; then
    pass "$file exists"
  else
    fail "$file MISSING"
  fi
done

# ─── Handoff contracts ───────────────────────────────────────

section "Handoff contracts"

# installer doesn't need a handoff contract (utility agent)
HANDOFF_AGENTS="architect context-manager devops fullstack investigator local-review qa retro reviewer security shipper spec-writer strategist ux"

for agent in $HANDOFF_AGENTS; do
  file=".claude/agents/${agent}.md"
  [ ! -f "$file" ] && continue

  if grep -q "## Handoff Contract" "$file"; then
    pass "$agent: has Handoff Contract section"
  else
    fail "$agent: MISSING Handoff Contract section"
  fi

  if grep -q "Self-validation checklist" "$file"; then
    pass "$agent: has self-validation checklist"
  else
    fail "$agent: MISSING self-validation checklist"
  fi
done

# ─── Structured memory templates ─────────────────────────────

section "Structured memory templates"

for agent in $HANDOFF_AGENTS; do
  file=".claude/agents/${agent}.md"
  [ ! -f "$file" ] && continue

  if grep -q "## Current State\|### Current State" "$file"; then
    pass "$agent: has Current State in memory template"
  else
    fail "$agent: MISSING Current State in memory template"
  fi

  if grep -q "## History\|### History" "$file"; then
    pass "$agent: has History in memory template"
  else
    fail "$agent: MISSING History in memory template"
  fi
done

# ─── ETHOS.md reference ──────────────────────────────────────

section "ETHOS.md integration"

if [ -f "ETHOS.md" ]; then
  pass "ETHOS.md exists"
else
  fail "ETHOS.md MISSING"
fi

# Check that all non-utility agents reference ETHOS.md
for agent in $HANDOFF_AGENTS; do
  file=".claude/agents/${agent}.md"
  [ ! -f "$file" ] && continue

  if grep -qi "ETHOS.md" "$file"; then
    pass "$agent: references ETHOS.md"
  else
    fail "$agent: does NOT reference ETHOS.md"
  fi
done

# ─── Project memory structure ────────────────────────────────

section "Project memory structure"

if [ -f ".claude/project-memory.md" ]; then
  pass "project-memory.md exists"

  if grep -q "## Current State" ".claude/project-memory.md"; then
    pass "project-memory: has Current State section"
  else
    fail "project-memory: MISSING Current State section"
  fi

  if grep -q "## Active Decisions" ".claude/project-memory.md"; then
    pass "project-memory: has Active Decisions section"
  else
    fail "project-memory: MISSING Active Decisions section"
  fi

  if grep -q "## History" ".claude/project-memory.md"; then
    pass "project-memory: has History section"
  else
    fail "project-memory: MISSING History section"
  fi
else
  warn "project-memory.md does not exist (created at runtime)"
fi

# ─── Plugin manifests ────────────────────────────────────────

section "Plugin manifests"

if [ -f ".claude-plugin/plugin.json" ]; then
  pass "plugin.json exists"
else
  fail "plugin.json MISSING"
fi

if [ -f ".claude-plugin/marketplace.json" ]; then
  pass "marketplace.json exists"
else
  fail "marketplace.json MISSING"
fi

# Version sync
if [ -f ".claude-plugin/plugin.json" ] && [ -f ".claude-plugin/marketplace.json" ]; then
  V_PLUGIN=$(grep '"version"' .claude-plugin/plugin.json | head -1 | sed 's/.*: *"\(.*\)".*/\1/')
  V_MARKET=$(grep '"version"' .claude-plugin/marketplace.json | head -1 | sed 's/.*: *"\(.*\)".*/\1/')

  if [ "$V_PLUGIN" = "$V_MARKET" ]; then
    pass "plugin versions match: $V_PLUGIN"
  else
    fail "plugin version mismatch: plugin.json=$V_PLUGIN, marketplace.json=$V_MARKET"
  fi
fi

# Plugin agent count
if [ -f ".claude-plugin/plugin.json" ]; then
  PLUGIN_AGENT_COUNT=$(grep -c '\.claude/agents/' .claude-plugin/plugin.json || echo "0")
  if [ "$PLUGIN_AGENT_COUNT" -eq 19 ]; then
    pass "plugin.json: lists 19 agents"
  else
    fail "plugin.json: lists $PLUGIN_AGENT_COUNT agents (expected 19)"
  fi

  PLUGIN_CMD_COUNT=$(grep -c '\.claude/commands/' .claude-plugin/plugin.json || echo "0")
  if [ "$PLUGIN_CMD_COUNT" -eq 19 ]; then
    pass "plugin.json: lists 19 commands"
  else
    fail "plugin.json: lists $PLUGIN_CMD_COUNT commands (expected 19)"
  fi
fi

# ─── Agent count consistency ─────────────────────────────────

section "Agent count consistency"

# Count actual agent files
ACTUAL_COUNT=$(ls -1 .claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ')

if [ "$ACTUAL_COUNT" -eq 19 ]; then
  pass "19 agent files found"
else
  fail "expected 19 agent files, found $ACTUAL_COUNT"
fi

# Count actual command files
ACTUAL_CMD_COUNT=$(ls -1 .claude/commands/*.md 2>/dev/null | wc -l | tr -d ' ')

if [ "$ACTUAL_CMD_COUNT" -eq 19 ]; then
  pass "19 command files found"
else
  fail "expected 19 command files, found $ACTUAL_CMD_COUNT"
fi

# ─── New root files ──────────────────────────────────────────

section "Required root files"

for file in CLAUDE.md README.md GETTING-STARTED.md LICENSE ETHOS.md ARCHITECTURE.md .gitignore; do
  if [ -f "$file" ]; then
    pass "$file exists"
  else
    fail "$file MISSING"
  fi
done

# ─── Docs files ──────────────────────────────────────────────

section "Docs files"

EXPECTED_DOCS="auth-ownership handoff-chain hitl install modes parallel-execution"

for doc in $EXPECTED_DOCS; do
  file="docs/${doc}.md"
  if [ -f "$file" ]; then
    if [ -s "$file" ]; then
      pass "$file exists and is non-empty"
    else
      fail "$file exists but is EMPTY"
    fi
  else
    fail "$file MISSING"
  fi
done

# ─── Eval system ─────────────────────────────────────────────

section "Eval system"

if [ -f "scripts/eval.sh" ]; then
  pass "scripts/eval.sh exists"
else
  fail "scripts/eval.sh MISSING"
fi

if [ -f "eval/rubric.md" ]; then
  pass "eval/rubric.md exists"
else
  fail "eval/rubric.md MISSING"
fi

EVAL_TASK_COUNT=$(ls -1 eval/tasks/*.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$EVAL_TASK_COUNT" -ge 7 ]; then
  pass "eval/tasks: $EVAL_TASK_COUNT task files found"
else
  fail "eval/tasks: expected 7+ task files, found $EVAL_TASK_COUNT"
fi

# ─── Setup script ────────────────────────────────────────────

section "Setup script"

if [ -f "scripts/setup.sh" ]; then
  pass "scripts/setup.sh exists"
  if [ -x "scripts/setup.sh" ]; then
    pass "scripts/setup.sh is executable"
  else
    fail "scripts/setup.sh is NOT executable"
  fi
else
  fail "scripts/setup.sh MISSING"
fi

# ─── Git hygiene ─────────────────────────────────────────────

section "Git hygiene"

# Check for tracked .DS_Store files
if git ls-files | grep -q "\.DS_Store" 2>/dev/null; then
  fail ".DS_Store files are tracked in git"
else
  pass "no .DS_Store files tracked"
fi

# Check for tracked local settings
if git ls-files | grep -q "settings.local.json" 2>/dev/null; then
  fail "settings.local.json is tracked in git"
else
  pass "settings.local.json not tracked"
fi

# Check .gitignore covers eval results
if [ -f ".gitignore" ]; then
  if grep -q "\.DS_Store" ".gitignore"; then
    pass ".gitignore covers .DS_Store"
  else
    warn ".gitignore does not cover .DS_Store"
  fi

  if grep -q "settings.local.json" ".gitignore"; then
    pass ".gitignore covers settings.local.json"
  else
    warn ".gitignore does not cover settings.local.json"
  fi

  if grep -q "eval/results" ".gitignore"; then
    pass ".gitignore covers eval/results/"
  else
    warn ".gitignore does not cover eval/results/"
  fi
fi

# ─── Summary ─────────────────────────────────────────────────

printf "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
printf "  RESULTS: %d passed, %d failed, %d warnings\n" "$PASS" "$FAIL" "$WARN"
printf "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

if [ "$FAIL" -gt 0 ]; then
  printf "  STATUS: FAIL\n"
  exit 1
else
  printf "  STATUS: PASS\n"
  exit 0
fi
