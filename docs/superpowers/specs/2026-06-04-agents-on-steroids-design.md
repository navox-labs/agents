# Agents on Steroids — Design Spec

> Turn navox-labs/agents from an 8-agent build-phase toolkit into a 15-agent full-sprint-cycle engineering team that overtakes gstack in depth, coverage, and quality — with zero dependencies.

## Problem

The current agent roster covers only the BUILD phase of the software lifecycle. Strategic thinking, spec writing, investigation, code review, shipping, retrospectives, and context persistence are all missing. Competing frameworks (gstack) cover the full cycle but require heavy dependencies (Bun, Playwright, TypeScript) and are locked to a single ecosystem.

## Success Criteria

1. 15 agents covering Think → Plan → Build → Review → Test → Ship → Reflect
2. Zero dependencies — pure markdown, bash-only tooling
3. Every agent scores 8/10+ on the quality eval rubric
4. Runtime eval passes for all sample tasks
5. Three sprint modes on agency-run: FULL, QUICK, HOTFIX
6. Shared preamble system (ETHOS.md) injected into every agent
7. Multi-platform install support (Claude Code, Cursor, Copilot CLI, Codex)

## Out of Scope

- Bundled browser (agents leverage user's existing browser MCP)
- Supabase/cloud sync (project memory is file-based)
- TypeScript build pipeline (no build step)
- Chrome extension

---

## Architecture

### Sprint Cycle

```
FULL SPRINT:
  THINK ──→ PLAN ──→ BUILD ──→ REVIEW ──→ TEST ──→ SHIP ──→ REFLECT
    │         │        │         │          │        │         │
 strategist  spec   fullstack  reviewer   qa     shipper    retro
 architect   writer  devops   local-rev  security
    ux

QUICK SPRINT:
  PLAN ──→ BUILD ──→ TEST ──→ SHIP

HOTFIX SPRINT:
  INVESTIGATE ──→ BUILD ──→ SHIP
```

### Agent Architecture

All agents share:
- ETHOS.md preamble (three principles)
- Handoff contracts (what they receive, what they output)
- Memory integration (read from + write to project memory)
- PLAN mode (every agent can assess feasibility before acting)

### File Format

Agents use `.claude/agents/` with extended frontmatter:

```yaml
---
name: _agent-name
description: One sentence with trigger keywords.
model: claude-opus-4-6 | claude-sonnet-4-6
tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, Agent
---
```

Commands use `.claude/commands/` as wrappers that dispatch to the agent.

---

## New Agents (7)

### 1. strategist

**Purpose:** Product strategy, forcing questions, anti-sycophancy. Challenges assumptions before any code is written.

**Modes:**
- DIAGNOSE — Forcing questions: what's the real problem? Who's the user? What's the metric?
- REVIEW — Strategic review of existing plan/product: gaps, risks, positioning
- CHALLENGE — Adversarial mode: tries to kill the idea. If it survives, it's worth building.
- PLAN — Output a strategic brief: problem, audience, success criteria, risks, priorities

**Anti-sycophancy rules:**
- Never say "great idea" or "love it"
- Must identify at least 3 risks for any proposal
- Push once, then push again
- If the builder can't answer a forcing question, that IS the answer

**Handoff:** Outputs strategic brief → spec-writer or architect

---

### 2. spec-writer

**Purpose:** Turn vague intent into precise, buildable specifications.

**Modes:**
- WRITE — Interactive spec creation with targeted questions, structured output with acceptance criteria
- REFINE — Take existing spec, find gaps/ambiguities/contradictions, fix them
- ISSUE — Generate GitHub issues from spec: one issue per deliverable, labeled and prioritized
- PLAN — Assess spec feasibility, estimate complexity, flag unknowns

**Output format (every spec must include):**
- Problem statement
- Success criteria (measurable)
- Technical constraints
- Out of scope (explicit)
- Acceptance criteria (testable)
- Edge cases
- Dependencies

**Handoff:** Outputs spec → architect

---

### 3. investigator

**Purpose:** Root-cause debugging. No fixes without diagnosis. Ever.

**Modes:**
- INVESTIGATE — Reproduce → isolate → trace → identify cause. Outputs investigation report with evidence before any fix.
- AUTOPSY — Post-incident analysis: what broke, why, timeline, contributing factors, prevention measures
- TRACE — Follow a specific code path end-to-end, document every step
- PLAN — Propose fix strategy based on investigation findings

**Core discipline:**
- Must output "Investigation Report" with evidence before proposing any fix
- No guessing. No "try this and see."
- Must reproduce the bug before diagnosing
- Must identify root cause, not just symptoms

**Handoff:** Outputs investigation report + fix strategy → fullstack

---

### 4. reviewer

**Purpose:** Code review with parallel specialist army.

**Modes:**
- REVIEW — Full review army: spawns 7 parallel specialist checks
- QUICK — Single-pass review, fast feedback
- SECURITY — Security-focused review only
- PLAN — Assess review scope, estimate review effort

**Review army specialists (parallel during REVIEW mode):**
1. Security — injection, auth bypass, data exposure
2. Performance — N+1 queries, memory leaks, unnecessary computation
3. Maintainability — naming, structure, complexity, dead code
4. API contracts — breaking changes, backwards compatibility
5. Data integrity — migrations, race conditions, edge cases
6. Test coverage — untested paths, missing edge cases
7. Error handling — unhandled exceptions, silent failures

**Each specialist outputs:** PASS / WARN / BLOCK with evidence and line references.

**Final output:** Consolidated review with severity ranking.

**Handoff:** Outputs review report → fullstack (for fixes) or shipper (if LGTM)

---

### 5. shipper

**Purpose:** The last mile — from "code works" to "code is shipped."

**Modes:**
- SHIP — Full pipeline: run tests → lint → review check → version bump → changelog → create PR
- CHANGELOG — Generate changelog from commits since last release
- VERSION — Bump version (major/minor/patch) with rationale
- PLAN — Pre-ship checklist: what's ready, what's blocking

**Ship pipeline steps:**
1. Verify all tests pass
2. Run linter (if configured)
3. Check for uncommitted changes
4. Generate changelog entry
5. Bump version
6. Create PR with structured description
7. Output ship report

**Handoff:** Outputs PR URL + ship report → retro

---

### 6. retro

**Purpose:** Learn from every sprint. Compound improvements over time.

**Modes:**
- RETRO — Full retrospective: what worked, what didn't, what to change. Writes to project memory.
- LEARN — Record a single learning from the current session
- REVIEW — Surface past learnings relevant to current task
- PLAN — Propose process improvements based on accumulated learnings

**Memory integration:**
- Reads from `.claude/memory/retro.md` and `.claude/project-memory.md`
- Writes new learnings with timestamp, context, and category
- Categories: process, technical, communication, tooling

**Handoff:** Terminal — retro is the last step in a full sprint

---

### 7. context-manager

**Purpose:** Session continuity. Pause any sprint, resume later.

**Modes:**
- SAVE — Snapshot current context: task state, decisions made, files changed, next steps
- RESTORE — Load saved context, brief agent on where things left off
- LIST — Show all saved contexts with timestamps and summaries
- PLAN — Assess what context is needed for task handoff

**Context snapshot format:**
- Task description
- Sprint phase (which step in the cycle)
- Decisions made (with rationale)
- Files created/modified
- Next steps (ordered)
- Open questions
- Blockers

**Storage:** `.claude/memory/context/YYYY-MM-DD-HH-MM-<task-slug>.md`

**Handoff:** Outputs context file → any agent (via RESTORE)

---

## Enhancements to Existing Agents

### architect
- Add REVIEW mode: architecture lock-in checkpoint (eng review). Validates tech stack decisions, identifies coupling risks, confirms scalability approach.

### ux
- Add AUDIT mode: design dimension ratings 0-10 across: clarity, consistency, accessibility, responsiveness, error states, empty states, loading states, delight.

### devops
- Add DEPLOY mode: deploy to target environment + verify health checks
- Add CANARY mode: post-deploy monitoring — watch logs, check error rates, verify key flows

### qa
- Add BROWSER mode: browser-based QA testing via user's MCP browser tools
- Add REPORT mode: report-only — document issues without fixing them

### security
- Add AUDIT mode: full OWASP Top 10 + STRIDE threat model audit with severity ratings

### agency-run (command)
- Three sprint modes: FULL, QUICK, HOTFIX
- Full sprint orchestration with handoff contracts between each phase
- Context auto-save between phases

---

## New Docs

### ETHOS.md (repo root)
Three agnostic principles injected into every agent's preamble:

1. **Do the Complete Thing** — Don't cut corners. Don't ship half-done work. If you start it, finish it properly. Every edge case, every error state, every test.

2. **Investigate Before Acting** — Three layers: (1) check what already exists, (2) understand why it exists, (3) then decide what to build. Never build blind.

3. **Builder Sovereignty** — AI recommends, humans decide. Never take irreversible action without confirmation. Present options with trade-offs. The builder is always in control.

### ARCHITECTURE.md (repo root)
- Agent types and their roles
- Sprint cycle with phase descriptions
- Handoff contract system
- Memory architecture (project memory + per-agent memory + context snapshots)
- Eval system overview
- Multi-platform support model

---

## Eval System

### Layer 1: Agent Quality Eval (scripts/eval.sh)

Scores each agent 0-10 against rubric:

| # | Check | Points |
|---|---|---|
| 1 | Frontmatter completeness (name, description, model, tools) | 1 |
| 2 | Mode coverage (PLAN + 2 operational modes minimum) | 1 |
| 3 | Anti-hallucination rules (explicit "verify first" instructions) | 1 |
| 4 | Handoff contracts (receives X, outputs Y) | 1 |
| 5 | Anti-sycophancy (won't agree blindly — strategist, reviewer especially) | 1 |
| 6 | Error handling instructions (what to do when things go wrong) | 1 |
| 7 | Structured output format (not open-ended prose) | 1 |
| 8 | Scope boundaries (explicit "does NOT do" section) | 1 |
| 9 | Preamble reference (references ETHOS.md or includes principles) | 1 |
| 10 | Memory integration (reads/writes project memory) | 1 |

Minimum passing score: 8/10.

### Layer 2: Runtime Eval (scripts/eval-runtime.sh)

Sample tasks with assertions:

| Test | Agent | Assertion |
|---|---|---|
| Strategic clarity | strategist | Must ask 3+ forcing questions, must NOT contain sycophantic phrases |
| Spec completeness | spec-writer | Output must contain all 7 required sections |
| Investigation discipline | investigator | Must output investigation report BEFORE any fix |
| Review thoroughness | reviewer | Must cover all 7 specialist areas |
| Ship readiness | shipper | Must verify tests pass before creating PR |
| Learning persistence | retro | Must write to memory file |
| Context accuracy | context-manager | Saved context must contain all required fields |

### Eval file structure

```
scripts/
  eval.sh              ← Layer 1: agent quality scoring
  eval-runtime.sh      ← Layer 2: runtime testing

eval/
  rubric.md            ← scoring criteria
  tasks/               ← sample tasks for runtime eval
    strategist-clarity.md
    spec-completeness.md
    investigator-discipline.md
    reviewer-thoroughness.md
    shipper-readiness.md
    retro-persistence.md
    context-accuracy.md
  results/             ← eval output (gitignored)
```

---

## Multi-Platform Install

### Setup script (scripts/setup.sh)

Zero dependencies. Bash only. Supports:
- Claude Code (`.claude/agents/` + `.claude/commands/`)
- Cursor (`.cursor/agents/`)
- Copilot CLI (`~/.copilot/skills/`)
- Codex (`agents/` directory)

Features:
- `--platform claude|cursor|copilot|codex` — target platform
- `--agents all|agent1,agent2,...` — pick individual agents or full team
- `--global` — install to home directory (available in all projects)
- `--local` — install to current project (default)
- Idempotent — safe to run multiple times

---

## Updated Files

| File | Changes |
|---|---|
| README.md | 15-agent team table, sprint cycle section, eval section, multi-platform install |
| GETTING-STARTED.md | Updated for new agents, sprint cycle walkthrough, eval instructions |
| docs/modes.md | All new agent modes added |
| docs/handoff-chain.md | Full sprint chain with all 15 agents |
| docs/install.md | Multi-platform install instructions |
| .claude/commands/hire-team.md | Updated for 15-agent team |
| .claude/commands/agency-run.md | Three sprint modes |
| .claude/commands/ | 7 new command wrappers |
| scripts/validate.sh | Updated checks for new files |
| .gitignore | Add eval/results/ |
