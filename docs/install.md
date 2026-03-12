# Installation Guide

## Global Install (recommended)

Install the agents globally so they're available in every Claude Code session:

```bash
# Clone the repo
git clone https://github.com/navox-labs/agents.git

# Copy agents to your global Claude Code config
cp -r agents/.claude/agents/* ~/.claude/agents/

# Copy commands to your global Claude Code config
cp -r agents/.claude/commands/* ~/.claude/commands/
```

## Project Install

Install the agents into a specific project only:

```bash
# From your project root
git clone https://github.com/navox-labs/agents.git /tmp/navox-agents

# Copy agents into your project
cp -r /tmp/navox-agents/.claude/agents/* .claude/agents/

# Copy commands into your project
cp -r /tmp/navox-agents/.claude/commands/* .claude/commands/

# Clean up
rm -rf /tmp/navox-agents
```

## Verification

After installing, verify the agents are loaded:

```bash
# Check agent files are in place
ls ~/.claude/agents/
# Expected: architect.md  fullstack.md  qa.md  security.md  ux.md

ls ~/.claude/commands/
# Expected: hire-team.md
```

Then open Claude Code and run:
- `/hire-team` — should display the full team overview
- `/architect DIAGNOSE` — should activate the Architect agent

## Uninstall

### Global uninstall
```bash
rm ~/.claude/agents/architect.md
rm ~/.claude/agents/fullstack.md
rm ~/.claude/agents/ux.md
rm ~/.claude/agents/qa.md
rm ~/.claude/agents/security.md
rm ~/.claude/commands/hire-team.md
```

### Project uninstall
```bash
rm .claude/agents/architect.md
rm .claude/agents/fullstack.md
rm .claude/agents/ux.md
rm .claude/agents/qa.md
rm .claude/agents/security.md
rm .claude/commands/hire-team.md
```
