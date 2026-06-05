# Contributing to Navox Agents

Thanks for your interest in contributing. The prompts are the product — every word matters. This guide explains how to contribute without breaking things.

---

## Before you start

1. Read [CLAUDE.md](CLAUDE.md) — it contains the non-negotiable rules for this repo
2. Read [ETHOS.md](ETHOS.md) — every agent follows these three principles
3. Read [ARCHITECTURE.md](ARCHITECTURE.md) — understand how the agent system works
4. Run `bash scripts/validate.sh` — make sure the repo is clean before you start
5. Run `bash scripts/eval.sh` — make sure all agents pass the quality rubric

---

## What you can contribute

### Improve an existing agent prompt
The highest-impact contribution. If you've used an agent and found its output lacking — vague instructions, missing edge cases, weak handoff contract — improve it.

**How:**
1. Open `.claude/agents/[agent].md`
2. Make your change
3. Verify frontmatter is still valid
4. Run `bash scripts/eval.sh` — agent must still score 8/10+
5. Run `bash scripts/validate.sh` — must pass
6. Update `docs/modes.md` if you added or renamed a mode

### Report a prompt quality issue
If an agent produces bad output for a reasonable input, open an issue with:
- Which agent and mode
- What you asked it to do
- What it produced (the bad output)
- What you expected instead

### Add a runtime eval task
The eval system needs more test cases. Each task lives in `eval/tasks/` and defines:
- An input scenario
- The agent and mode to test
- Assertions on the output

### Add a starter template
Templates in `templates/` help users bootstrap new projects. If your stack isn't covered, add a `templates/[stack].CLAUDE.md` file.

### Fix a documentation gap
If any doc is out of date or unclear — README, GETTING-STARTED, modes.md, handoff-chain.md — fix it.

---

## What to avoid

- **Don't add dependencies.** This repo has zero by design. No package.json, no requirements.txt, no Bun, no Node.
- **Don't change agent `name` fields.** The name field becomes the slash command. Changing it breaks every user who installed globally.
- **Don't flatten the folder structure.** Every file has a specific location for a reason.
- **Don't create subdirectories inside `.claude/agents/`.** Agents are flat files.
- **Don't modify two agent files in the same PR** unless the change is coordinated (e.g., updating a shared handoff contract).

---

## Agent prompt structure

Every agent follows this exact 8-section structure. Don't deviate.

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

Every agent must:
- Have a `PLAN` mode (except installer and local-review)
- Reference ETHOS.md in the Identity section
- Include a handoff contract with a self-validation checklist
- End "What You Never Do" with the HITL gate line

---

## Frontmatter rules

```yaml
---
name: _agent-name          # underscore prefix for agents, plain for commands
description: One sentence with trigger keywords.
tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, Agent
model: claude-opus-4-6     # Opus for: architect, security, strategist, reviewer
       claude-sonnet-4-6   # Sonnet for: all others
---
```

---

## How to submit a PR

1. Fork the repo
2. Create a branch: `git checkout -b feat/improve-reviewer-army`
3. Make your changes
4. Run both validation scripts:
   ```bash
   bash scripts/validate.sh   # 210+ structural checks, must pass
   bash scripts/eval.sh       # Agent quality scoring, all must score 8/10+
   ```
5. Commit with a descriptive message:
   ```
   prompt: reviewer — add database migration safety check to data integrity specialist
   ```
6. Open a PR with:
   - What you changed and why
   - Which agent(s) are affected
   - Validation results (paste output of both scripts)

---

## Commit message format

```
feat: add [agent-name] agent
fix: [agent-name] — fix [mode] mode [issue]
docs: update [file] [what changed]
prompt: [agent-name] — improve [mode] output quality
eval: add [test-name] runtime eval task
```

---

## Quality bar

This repo's audience is senior engineers. Every prompt is scrutinized. The bar is:

> Would a senior engineer actually use and trust this output?

If the answer is "it's fine, I guess" — it's not good enough. If the answer is "yes, this saves me real time" — ship it.

---

## Questions?

Open an issue or start a discussion. We'd rather you ask first than submit a PR that doesn't fit.
