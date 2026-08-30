# ARCHITECTURE — How the Agent System Works

This document explains how the 19-agent engineering team operates: how agents are structured, how they communicate, and how the sprint cycle orchestrates them.

---

## Agent Types

| Type | Count | Purpose | Examples |
|---|---|---|---|
| **Strategic** | 2 | Validate ideas and create specs before building | strategist, spec-writer |
| **Design** | 2 | System and UX architecture | architect, ux |
| **Critique** | 1 | Adversarially review the plan before code exists | critic |
| **Build** | 3 | Write code and deploy infrastructure | fullstack, mobile, devops |
| **Quality** | 4 | Review, test, secure, and de-identify | reviewer, qa, security, privacy |
| **Ship** | 1 | Release engineering — tests to PR | shipper |
| **Operations** | 3 | Debug, learn, and persist context | investigator, retro, context-manager |
| **Utility** | 3 | Install agents, visual review, device review | installer, local-review, device-review |

## Agent Prompt Structure

Every agent follows an 8-section structure:

```
1. ## Identity        — Who the agent is, voice, values, ETHOS.md reference
2. ## Role in the Team — Pipeline position + auth ownership slice
3. ## Operating Principles — 5 numbered action-oriented principles
4. ## Task Modes       — MODE sections with Deliver: lists
5. ## Output Format    — Code block header template
6. ## Handoff Contract — Receive / Deliver table / Self-validation checklist
7. ## What You Never Do — 5-6 negations + HITL gate
8. ## Project Memory    — Read/write pattern with Current State + History
```

## Sprint Cycle

Three modes of execution:

### FULL Sprint (10 groups)
```
THINK    → strategist DIAGNOSE
PLAN     → spec-writer WRITE → architect DESIGN → parallel(ux, security)
BUILD    → fullstack BUILD → local-review CHECKPOINT
REVIEW   → reviewer REVIEW (7 specialist army)
TEST     → parallel(qa TEST-RUN, security CODE-AUDIT)
SHIP     → shipper SHIP
REFLECT  → retro RETRO
```

### QUICK Sprint (6 groups)
```
PLAN  → spec-writer → architect
BUILD → fullstack → local-review
TEST  → qa
SHIP  → shipper
```

### HOTFIX Sprint (3 groups)
```
INVESTIGATE → investigator
BUILD       → fullstack
SHIP        → shipper
```

### MOBILE Sprint (12 groups)
Full rigour, tuned for React Native / Expo. Adds the plan critic, a privacy
gate at both design and launch, and a dual-platform device checkpoint in place
of the browser-based one.
```
THINK    → strategist DIAGNOSE
PLAN     → spec-writer WRITE → architect DESIGN → critic CRITIQUE *
DESIGN   → parallel(ux, security, privacy) *
BUILD    → mobile BUILD → device-review REVIEW *
REVIEW   → reviewer REVIEW *
TEST     → parallel(qa TEST-RUN, security CODE-AUDIT)
GATE     → privacy LAUNCH-REVIEW *
SHIP     → shipper SHIP → retro RETRO
```
`*` marks groups the orchestrator may not skip. An orchestrator improvising a
chain will drop review agents first, because they produce findings rather than
artifacts — which is exactly backwards.

## Why a plan critic

The `critic` agent sits between design and build for one reason: the author of
a plan is invested in it, and a second model reading it cold catches
contradictions the author cannot see. It reviews the plan, never the code —
`reviewer` does that later, when changes are expensive. Findings are separated
into contradictions (two sections disagree), gaps (nothing says), and risks
(it says something and it may be wrong), because those need different fixes.

## Unattended operation

Three modules make a run safe to leave alone. See `docs/unattended.md`.

| Module | Problem it solves |
|---|---|
| `sdk/navox/notify.py` | A run you cannot see is a run you cannot supervise. Telegram, Slack, and email fan-out. Escalations carry the exact question and valid replies so a chain can be unblocked from a phone. Never raises into the chain |
| `sdk/navox/budget.py` | An advisory token budget is not a budget. Hard USD and token caps, warnings at 50/75/90%, chain halt at 100%. Thread-safe, because parallel groups charge concurrently |
| `sdk/navox/worktree.py` | Parallel agents sharing one checkout silently overwrite each other. Each gets an isolated git worktree; merge conflicts **raise** rather than auto-resolve, because unattended conflict resolution loses work |

## Model selection

Agents declare a `model_tier` (`opus` / `sonnet`). The registry's `model_tiers`
map resolves a tier to a concrete model id in one place, so a model refresh is
a single-line change rather than an edit to every agent file.

## Handoff Contract System

Every agent declares:
- **What it receives** — named upstream agents with required sections
- **What it delivers** — a table: Required section | Consumed by | Must contain
- **Self-validation** — checkbox list verified before completing

This creates a typed contract between agents. If agent A's output is missing a section that agent B requires, the handoff fails visibly — not silently.

## Memory Architecture

Three layers of persistent memory:

### 1. Project Memory (`.claude/project-memory.md`)
Shared across all agents. Updated after every agency-run. Contains:
- Current State (overwritten each run)
- Active Decisions (unresolved items)
- History (append-only log)

### 2. Agent Memory (`.claude/memory/[agent].md`)
Per-agent memory. Each agent reads and writes its own file. Contains:
- Current State (agent-specific fields, overwritten)
- History (append-only, 50-line cap with compression)

### 3. Context Snapshots (`.claude/memory/context/`)
Created by the context-manager agent. Full session snapshots for pause/resume:
- Task description, sprint phase, decisions with rationale
- Files changed, next steps, open questions, blockers, auth state

## Eval System

### Layer 1: Static Quality (scripts/eval.sh)
Scores each agent 0-10 against a rubric checking: frontmatter, modes, anti-hallucination, handoff contracts, anti-sycophancy, error handling, output format, scope boundaries, preamble reference, memory integration.

### Layer 2: Runtime Testing (scripts/eval-runtime.sh)
Runs agents against sample tasks and asserts output structure. Tests: strategist clarity, spec completeness, investigation discipline, review thoroughness, ship readiness, learning persistence, context accuracy.

## Philosophy Layer

ETHOS.md defines three principles referenced by every agent:
1. **Do the Complete Thing** — no half-done work
2. **Investigate Before Acting** — understand before changing
3. **Builder Sovereignty** — AI recommends, humans decide

## File Layout

```
.claude/agents/      — 15 agent prompt files
.claude/commands/    — 15 command wrappers (slash commands)
.claude/memory/      — per-agent memory (runtime)
.claude/memory/context/ — context snapshots (runtime)
.claude/project-memory.md — shared team memory (runtime)
ETHOS.md             — builder philosophy (referenced by all agents)
ARCHITECTURE.md      — this file
eval/                — eval rubric and test tasks
scripts/             — validate.sh, eval.sh, eval-runtime.sh, setup.sh
```
