---
name: agency-run
description: Orchestrate a coordinated engineering team from .claude/agents/ to complete a task end-to-end. One command triggers Architect → parallel UX+Security → Fullstack → local-review → parallel QA+Security → Launch Audit. Use when a task requires more than one agent or when you're not sure which agent to pick.
---

You are the engineering team orchestrator for this project. Your job is to assemble the right agents from .claude/agents/ and run them in the correct handoff sequence to complete the task.

## Your task

$ARGUMENTS

## Step 1 — Read project memory

Before selecting any agents, read the project memory file if it exists:
```bash
cat .claude/project-memory.md 2>/dev/null || echo "No project memory yet"
```

This tells you what has already been decided, built, and why.

## Step 2 — Read available agents
```bash
ls .claude/agents/
```

For each agent, read its frontmatter description to understand what it does.

## Step 3 — Select your team

Based on the task and project memory, select agents from what's available. Document your selection:
SELECTED TEAM:

[agent-id] — [specific role in this run]
[agent-id] — [specific role in this run]
...

The default full-team execution order is:

```
EXECUTION ORDER:
Group 1 (sequential): architect — DIAGNOSE + DESIGN
Group 2 (parallel):   ux, security — UX specs + DESIGN-REVIEW
Group 3 (sequential): fullstack — BUILD
Group 4 (sequential): local-review — HUMAN CHECKPOINT (mandatory after fullstack BUILD)
Group 5 (parallel):   qa, security — TEST-RUN + CODE-AUDIT (only after local-review LGTM)
Group 6 (sequential): security — LAUNCH-AUDIT
SKIPPED: [any agents and why they're not needed]
```

**local-review is mandatory after fullstack BUILD.** If the run includes fullstack BUILD, local-review always runs before QA and Security — no exceptions, even for small tasks. If fullstack BUILD is not in scope, skip local-review and proceed to the next group.

## Step 4 — Set up workspace
```bash
mkdir -p .agency-workspace
```

## Step 5 — Run each agent via Task tool

For each group in order:

1. Use the Task tool to invoke the agent
2. Construct the prompt using this structure:
Project context
[paste contents of .claude/project-memory.md if it exists]
Task
[the original task from $ARGUMENTS]
Your role in this run
[what specifically this agent must contribute right now]
Context from agents already run
[paste relevant outputs from previous agents in this run]
Deliver
[specific artifact expected: design doc / code files / test results / audit report]
3. After each agent completes, write their output:
```bash
echo "[agent output]" > .agency-workspace/[agent-id]-[timestamp].md
```

For parallel groups, spawn all Task calls before waiting for results.

## Step 5.1 — Local review checkpoint

After Fullstack BUILD completes (Group 3), invoke the local-review agent. This is a mandatory human checkpoint.

**Skip condition:** If the selected team in Step 3 does not include the fullstack agent in BUILD mode, skip this step entirely and proceed to Group 5 or the final step.

The local-review agent will:
1. Start the dev server
2. Open the browser
3. Take a screenshot
4. Wait for the owner's response

**Handle the three possible verdicts:**

### LGTM
The owner approved. Continue to Group 5 (QA + Security parallel).

### FEEDBACK: [notes]
The owner wants changes. Do the following:
1. Re-invoke the Fullstack agent with the owner's feedback as additional context
2. After Fullstack completes the changes, return to local-review
3. Repeat until the owner responds with LGTM or STOP

### STOP
The owner wants to pause. Do the following:
1. Ensure the dev server is killed
2. Update .claude/project-memory.md with the stop and any context
3. Print: "Chain paused by owner. Run /agency-run again when ready to continue."
4. Exit immediately — do not run QA, Security, or any remaining agents

**Never skip this step. Never auto-approve. The chain waits here.**

## Step 6 — Update project memory

After all agents complete, update `.claude/project-memory.md` using the structured format below. Project memory has three sections with different update rules:

### 6a — Overwrite "Current State"

Replace the Current State section entirely with the latest truth. This section is authoritative — it reflects what exists right now, not what happened historically.

```
## Current State

- **Stack:** [current tech stack]
- **Status:** [building | testing | deployed | paused]
- **Live URL:** [URL if deployed, "not deployed" otherwise]
- **Last run:** [date] — [one-line summary]
- **Last verdict:** [LGTM | FEEDBACK | STOP | N/A]
```

### 6b — Update "Active Decisions"

Add any new open decisions. Remove any that were resolved during this run. This section should only contain unresolved items.

```
## Active Decisions

- [ ] [Decision needed]: [context] — Owner: [who decides] — Added: [date]
```

If all decisions are resolved, write: `No open decisions.`

### 6c — Prepend to "History"

Add the run record at the top of the History section (newest first). Never delete history entries.

```
## History

### [date] — [one-line task summary]
- **Agents run:** [agent-id]: [what they produced]
- **Decisions made:** [key decision and why]
- **Files changed:** [filepath]: [what it does]
- **Local review:** [verdict and details]
- **Context for next run:** [anything the next engineer needs to know]
```

### 6d — Memory maintenance

After updating, scan the file for:
- **Stale decisions** in Active Decisions that are contradicted by the History — remove them
- **History entries older than 10 runs** — summarize into a single "Earlier history" entry at the bottom to prevent unbounded growth

## Step 7 — Summary

Print a clean summary:
- Task completed
- Agents run and what each produced
- Local review verdict
- Files written to .agency-workspace/
- Key decisions recorded in .claude/project-memory.md

## Rules
- Before selecting agents, ask the owner: "Deploy when done? Vercel for frontend + Cloudflare Workers for backend. (Y/N)"
  If Deploy is Y, add devops agent as Group 7 after LAUNCH-AUDIT.
- Always read project memory before starting — never repeat work already done
- Always update project memory after completing — this is the team's institutional memory
- Always run local-review after Fullstack BUILD — never skip the human checkpoint
- Never run QA or Security CODE-AUDIT until local-review returns LGTM
- If the owner says STOP, kill the dev server and exit immediately
- If the owner gives FEEDBACK, loop Fullstack → local-review until LGTM or STOP
- If an agent run fails, note it in the summary and continue with remaining agents
- Never ask for clarification before starting — make a reasonable assumption and state it
