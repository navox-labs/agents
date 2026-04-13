# Project memory

This file is the shared institutional memory for the engineering team.
Updated automatically after every /agency-run.

## Project overview
navox-labs/agents — open-source Claude Code plugin providing specialist AI engineering agents (architect, fullstack, ux, qa, security, devops) with HITL checkpoints and /agency-run orchestrator. Zero dependencies, everything is markdown.

## Stack decisions
- No runtime dependencies — pure markdown agent prompts
- Plugin distributed via Claude Code marketplace (navox-agents-marketplace)
- Plugin cache lives at ~/.claude/plugins/cache/navox-agents-marketplace/navox-agents/1.3.0/

## Key architectural decisions

### Underscore-prefix pattern (2026-04-13, commit a1f395e)
**Problem:** Claude Code deduplicates by `name` field across agents and commands within a plugin. If both have `name: architect`, one gets dropped — so plugin slash commands like `/navox-agents:architect` didn't work.

**Failed approaches (reverted):** 5 attempts (commits c4c6a5f..d04c3d6) tried skills/ directory, removing name fields, etc. All failed.

**Solution:** Prefix agent `name` fields with underscore:
- `.claude/agents/architect.md` → `name: _architect` (internal, auto-dispatched by Claude)
- `.claude/commands/architect.md` → `name: architect` (exposed as `/navox-agents:architect`)

Command wrappers read the agent file and pass `$ARGUMENTS`. This avoids name collision while keeping both registered in plugin.json.

**Pattern for new agents:** Agent file gets `name: _agentname`, command wrapper gets `name: agentname`. Add both to plugin.json arrays.

### Local testing shortcut
Copy updated files to `~/.claude/plugins/cache/navox-agents-marketplace/navox-agents/1.3.0/` and restart Claude Code. No need to uninstall/reinstall.
