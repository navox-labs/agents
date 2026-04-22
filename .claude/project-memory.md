# Project Memory

This file is the shared institutional memory for the engineering team.
Updated automatically after every /agency-run.

Three sections, three update rules:
- **Current State** — overwrite with latest truth (authoritative)
- **Active Decisions** — add new, remove resolved (living document)
- **History** — prepend new entries, never delete (append-only, newest first)

---

## Current State

- **Project:** navox-labs/agents — open-source Claude Code plugin providing 8 specialist AI engineering agents with HITL checkpoints and /agency-run orchestrator
- **Stack:** Zero runtime dependencies — pure markdown agent prompts
- **Distribution:** Claude Code plugin marketplace (navox-agents-marketplace)
- **Version:** 1.6.0
- **Status:** active development
- **Live URL:** N/A (this is a plugin, not a deployed app)
- **Last run:** N/A
- **Last verdict:** N/A

---

## Active Decisions

No open decisions.

---

## History

### 2026-04-13 — Underscore-prefix pattern (commit a1f395e)
- **Problem:** Claude Code deduplicates by `name` field across agents and commands within a plugin. If both have `name: architect`, one gets dropped — so plugin slash commands like `/navox-agents:architect` didn't work.
- **Failed approaches (reverted):** 5 attempts (commits c4c6a5f..d04c3d6) tried skills/ directory, removing name fields, etc. All failed.
- **Solution:** Prefix agent `name` fields with underscore: `.claude/agents/architect.md` → `name: _architect` (internal), `.claude/commands/architect.md` → `name: architect` (exposed as `/navox-agents:architect`). Command wrappers read the agent file and pass `$ARGUMENTS`.
- **Pattern for new agents:** Agent file gets `name: _agentname`, command wrapper gets `name: agentname`. Add both to plugin.json arrays.
- **Context for next run:** Plugin cache lives at `~/.claude/plugins/cache/navox-agents-marketplace/navox-agents/`. Copy updated files there and restart Claude Code for local testing.
