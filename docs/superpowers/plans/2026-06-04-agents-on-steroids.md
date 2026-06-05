# Agents on Steroids — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand from 8 to 15 agents covering the full sprint cycle, add eval system, multi-platform install, and philosophy layer — zero dependencies.

**Architecture:** 7 new agents + 5 enhanced existing agents + ETHOS.md preamble + eval system (static + runtime) + bash setup script. All agents follow the existing 8-section prompt structure with handoff contracts and self-validation.

**Tech Stack:** Pure markdown, bash scripts. No dependencies.

---

## Task Overview

| # | Task | Type | Estimated Size |
|---|---|---|---|
| 1 | ETHOS.md — shared philosophy | New file | ~50 lines |
| 2 | strategist agent + command wrapper | New agent | ~280 lines |
| 3 | spec-writer agent + command wrapper | New agent | ~260 lines |
| 4 | investigator agent + command wrapper | New agent | ~270 lines |
| 5 | reviewer agent + command wrapper | New agent | ~290 lines |
| 6 | shipper agent + command wrapper | New agent | ~260 lines |
| 7 | retro agent + command wrapper | New agent | ~240 lines |
| 8 | context-manager agent + command wrapper | New agent | ~250 lines |
| 9 | Enhance existing agents (architect, ux, devops, qa, security) | Edits | ~150 lines added |
| 10 | Update agency-run with sprint modes | Edit | ~100 lines added |
| 11 | ARCHITECTURE.md | New file | ~120 lines |
| 12 | Eval system — rubric + quality script + runtime script | New files | ~400 lines |
| 13 | Multi-platform setup script | New file | ~200 lines |
| 14 | Update docs (modes.md, handoff-chain.md, install.md) | Edits | ~200 lines |
| 15 | Update hire-team.md | Edit | ~40 lines |
| 16 | Update README.md | Edit | ~150 lines |
| 17 | Update GETTING-STARTED.md | Edit | ~100 lines |
| 18 | Update validate.sh for 15 agents | Edit | ~50 lines |
| 19 | Update .gitignore | Edit | ~5 lines |
| 20 | Final validation run | Verification | — |

---

## Task 1: ETHOS.md — Shared Philosophy

**Files:**
- Create: `ETHOS.md`

- [ ] **Step 1: Create ETHOS.md**

Write the three-principle philosophy that every agent references in its preamble. Agnostic — no YC, no startup framing. Universal builder principles.

- [ ] **Step 2: Commit**

```bash
git add ETHOS.md
git commit -m "feat: add ETHOS.md — shared builder philosophy for all agents"
```

---

## Tasks 2-8: New Agents

Each new agent follows the EXACT same 8-section structure as existing agents:

1. `## Identity` — Who, voice, values (1 paragraph)
2. `## Role in the Team` — Pipeline position + `### Your slice of Authentication`
3. `## Operating Principles` — 5 numbered bold principles with elaboration
4. `## Task Modes` — `### [MODE: NAME]` subsections with `Deliver:` lists
5. `## Output Format` — Code block header template
6. `## Handoff Contract` — What I receive / What I deliver (table) / Self-validation checklist
7. `## What You Never Do` — 5-6 negations ending with HITL gate line
8. `## Project memory` — Read/write pattern with Current State + History

Plus a matching 8-line command wrapper in `.claude/commands/`.

### Task 2: strategist agent

**Files:**
- Create: `.claude/agents/strategist.md`
- Create: `.claude/commands/strategist.md`

- [ ] **Step 1: Write strategist agent prompt**

Frontmatter: `name: _strategist`, `model: claude-opus-4-6`, `tools: Read, Glob, Grep, WebSearch`

Modes: PLAN, DIAGNOSE, REVIEW, CHALLENGE

Key differentiator: anti-sycophancy rules baked into identity and every mode. References ETHOS.md.

- [ ] **Step 2: Write command wrapper**

Standard 8-line wrapper dispatching to `_strategist`.

- [ ] **Step 3: Commit**

```bash
git add .claude/agents/strategist.md .claude/commands/strategist.md
git commit -m "feat: add strategist agent — product strategy with anti-sycophancy"
```

### Task 3: spec-writer agent

**Files:**
- Create: `.claude/agents/spec-writer.md`
- Create: `.claude/commands/spec-writer.md`

- [ ] **Step 1: Write spec-writer agent prompt**

Frontmatter: `name: _spec-writer`, `model: claude-sonnet-4-6`, `tools: Read, Write, Edit, Glob, Grep, Bash`

Modes: PLAN, WRITE, REFINE, ISSUE

Key differentiator: enforces 7-section spec format, generates GitHub issues.

- [ ] **Step 2: Write command wrapper**
- [ ] **Step 3: Commit**

```bash
git add .claude/agents/spec-writer.md .claude/commands/spec-writer.md
git commit -m "feat: add spec-writer agent — vague intent to precise specs"
```

### Task 4: investigator agent

**Files:**
- Create: `.claude/agents/investigator.md`
- Create: `.claude/commands/investigator.md`

- [ ] **Step 1: Write investigator agent prompt**

Frontmatter: `name: _investigator`, `model: claude-sonnet-4-6`, `tools: Read, Glob, Grep, Bash`

Modes: PLAN, INVESTIGATE, AUTOPSY, TRACE

Key differentiator: enforces "investigation report before any fix" discipline.

- [ ] **Step 2: Write command wrapper**
- [ ] **Step 3: Commit**

```bash
git add .claude/agents/investigator.md .claude/commands/investigator.md
git commit -m "feat: add investigator agent — root-cause debugging, no fixes without diagnosis"
```

### Task 5: reviewer agent

**Files:**
- Create: `.claude/agents/reviewer.md`
- Create: `.claude/commands/reviewer.md`

- [ ] **Step 1: Write reviewer agent prompt**

Frontmatter: `name: _reviewer`, `model: claude-opus-4-6`, `tools: Read, Glob, Grep, Bash, Agent`

Modes: PLAN, REVIEW, QUICK, SECURITY

Key differentiator: REVIEW mode spawns 7 parallel specialist checks via Agent tool. Needs `Agent` in tools list.

- [ ] **Step 2: Write command wrapper**
- [ ] **Step 3: Commit**

```bash
git add .claude/agents/reviewer.md .claude/commands/reviewer.md
git commit -m "feat: add reviewer agent — code review with parallel specialist army"
```

### Task 6: shipper agent

**Files:**
- Create: `.claude/agents/shipper.md`
- Create: `.claude/commands/shipper.md`

- [ ] **Step 1: Write shipper agent prompt**

Frontmatter: `name: _shipper`, `model: claude-sonnet-4-6`, `tools: Read, Write, Edit, Bash, Glob, Grep`

Modes: PLAN, SHIP, CHANGELOG, VERSION

Key differentiator: full ship pipeline with verification gates.

- [ ] **Step 2: Write command wrapper**
- [ ] **Step 3: Commit**

```bash
git add .claude/agents/shipper.md .claude/commands/shipper.md
git commit -m "feat: add shipper agent — tests to PR in one command"
```

### Task 7: retro agent

**Files:**
- Create: `.claude/agents/retro.md`
- Create: `.claude/commands/retro.md`

- [ ] **Step 1: Write retro agent prompt**

Frontmatter: `name: _retro`, `model: claude-sonnet-4-6`, `tools: Read, Write, Edit, Glob, Grep`

Modes: PLAN, RETRO, LEARN, REVIEW

Key differentiator: writes learnings to project memory, compounds over time.

- [ ] **Step 2: Write command wrapper**
- [ ] **Step 3: Commit**

```bash
git add .claude/agents/retro.md .claude/commands/retro.md
git commit -m "feat: add retro agent — sprint retrospectives with persistent learnings"
```

### Task 8: context-manager agent

**Files:**
- Create: `.claude/agents/context-manager.md`
- Create: `.claude/commands/context-manager.md`

- [ ] **Step 1: Write context-manager agent prompt**

Frontmatter: `name: _context-manager`, `model: claude-sonnet-4-6`, `tools: Read, Write, Edit, Glob, Grep, Bash`

Modes: PLAN, SAVE, RESTORE, LIST

Key differentiator: context snapshot format with all required fields, stored in `.claude/memory/context/`.

- [ ] **Step 2: Write command wrapper**
- [ ] **Step 3: Commit**

```bash
git add .claude/agents/context-manager.md .claude/commands/context-manager.md
git commit -m "feat: add context-manager agent — session persistence and context handoff"
```

---

## Task 9: Enhance Existing Agents

**Files:**
- Modify: `.claude/agents/architect.md` — add REVIEW mode
- Modify: `.claude/agents/ux.md` — add AUDIT mode
- Modify: `.claude/agents/devops.md` — add CANARY mode
- Modify: `.claude/agents/qa.md` — add BROWSER and REPORT modes
- Modify: `.claude/agents/security.md` — add AUDIT mode

- [ ] **Step 1: Add REVIEW mode to architect**

Architecture lock-in checkpoint. Validates tech stack, coupling risks, scalability.

- [ ] **Step 2: Add AUDIT mode to ux**

Design dimension ratings 0-10 across 8 dimensions.

- [ ] **Step 3: Add CANARY mode to devops**

Post-deploy monitoring: watch logs, check error rates, verify key flows.

- [ ] **Step 4: Add BROWSER and REPORT modes to qa**

BROWSER: browser-based QA via MCP. REPORT: report-only, no fixes.

- [ ] **Step 5: Add AUDIT mode to security**

Full OWASP Top 10 + STRIDE threat model audit.

- [ ] **Step 6: Add ETHOS.md reference to all existing agents**

Add preamble reference in Identity section of all 8 existing agents.

- [ ] **Step 7: Commit**

```bash
git add .claude/agents/architect.md .claude/agents/ux.md .claude/agents/devops.md .claude/agents/qa.md .claude/agents/security.md
git commit -m "feat: enhance 5 existing agents with new modes + ETHOS.md preamble"
```

---

## Task 10: Update agency-run with Sprint Modes

**Files:**
- Modify: `.claude/commands/agency-run.md`

- [ ] **Step 1: Add FULL, QUICK, HOTFIX sprint modes**

FULL: strategist → spec-writer → architect → parallel(ux, security) → fullstack → reviewer → local-review → parallel(qa, security) → shipper → retro

QUICK: spec-writer → architect → fullstack → qa → shipper

HOTFIX: investigator → fullstack → shipper

- [ ] **Step 2: Add context auto-save between phases**
- [ ] **Step 3: Commit**

```bash
git add .claude/commands/agency-run.md
git commit -m "feat: agency-run — add FULL, QUICK, HOTFIX sprint modes"
```

---

## Task 11: ARCHITECTURE.md

**Files:**
- Create: `ARCHITECTURE.md`

- [ ] **Step 1: Write ARCHITECTURE.md**

Covers: agent types, sprint cycle, handoff contracts, memory architecture, eval system, multi-platform model.

- [ ] **Step 2: Commit**

```bash
git add ARCHITECTURE.md
git commit -m "docs: add ARCHITECTURE.md — system design overview"
```

---

## Task 12: Eval System

**Files:**
- Create: `eval/rubric.md`
- Create: `eval/tasks/strategist-clarity.md`
- Create: `eval/tasks/spec-completeness.md`
- Create: `eval/tasks/investigator-discipline.md`
- Create: `eval/tasks/reviewer-thoroughness.md`
- Create: `eval/tasks/shipper-readiness.md`
- Create: `eval/tasks/retro-persistence.md`
- Create: `eval/tasks/context-accuracy.md`
- Create: `scripts/eval.sh`
- Create: `scripts/eval-runtime.sh`

- [ ] **Step 1: Write eval rubric**
- [ ] **Step 2: Write 7 runtime eval task files**
- [ ] **Step 3: Write eval.sh (Layer 1: static quality scoring)**
- [ ] **Step 4: Write eval-runtime.sh (Layer 2: runtime testing)**
- [ ] **Step 5: Commit**

```bash
git add eval/ scripts/eval.sh scripts/eval-runtime.sh
git commit -m "feat: add eval system — agent quality scoring + runtime testing"
```

---

## Task 13: Multi-Platform Setup Script

**Files:**
- Create: `scripts/setup.sh`

- [ ] **Step 1: Write setup.sh**

Supports: `--platform claude|cursor|copilot|codex`, `--agents all|list`, `--global`, `--local`. Zero dependencies.

- [ ] **Step 2: Commit**

```bash
git add scripts/setup.sh
git commit -m "feat: add multi-platform setup script — zero-dep bash installer"
```

---

## Tasks 14-19: Update All Docs

### Task 14: Update docs/

- [ ] **Step 1: Update docs/modes.md** — add all new agent modes
- [ ] **Step 2: Update docs/handoff-chain.md** — full sprint chain with 15 agents
- [ ] **Step 3: Update docs/install.md** — multi-platform install instructions
- [ ] **Step 4: Commit**

### Task 15: Update hire-team.md

- [ ] **Step 1: Update .claude/commands/hire-team.md** — 15-agent team
- [ ] **Step 2: Commit**

### Task 16: Update README.md

- [ ] **Step 1: Update team table** — 15 rows
- [ ] **Step 2: Add sprint cycle section**
- [ ] **Step 3: Add eval section**
- [ ] **Step 4: Update install section**
- [ ] **Step 5: Commit**

### Task 17: Update GETTING-STARTED.md

- [ ] **Step 1: Add new agents with real-world equivalents**
- [ ] **Step 2: Add sprint cycle walkthrough**
- [ ] **Step 3: Commit**

### Task 18: Update validate.sh

- [ ] **Step 1: Add checks for 15 agents, new docs, eval files**
- [ ] **Step 2: Commit**

### Task 19: Update .gitignore

- [ ] **Step 1: Add eval/results/**
- [ ] **Step 2: Commit**

---

## Task 20: Final Validation

- [ ] **Step 1: Run validate.sh**
- [ ] **Step 2: Run eval.sh**
- [ ] **Step 3: Fix any failures**
- [ ] **Step 4: Final commit + push + create PR**
