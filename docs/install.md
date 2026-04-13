# Installation Guide

## Plugin Install (recommended)

If you hit an SSH error, run this first (one time):
```bash
git config --global url."https://github.com/".insteadOf "git@github.com:"
```

Then install:
```
/plugin marketplace add https://github.com/navox-labs/agents
/plugin install navox-agents
/reload-plugins
```

> **Note:** Plugin commands are namespaced. Use `/navox-agents:agency-run` and `/navox-agents:hire-team` instead of `/agency-run` and `/hire-team`.

## Manual Install (for customization)

Install the agents globally so they're available in every Claude Code session:

```bash
# Clone the repo
git clone https://github.com/navox-labs/agents.git

# Create directories (safe if they already exist)
mkdir -p ~/.claude/agents ~/.claude/commands ~/.claude/templates

# Copy agents to your global Claude Code config
cp -r agents/.claude/agents/* ~/.claude/agents/

# Copy commands to your global Claude Code config
cp -r agents/.claude/commands/* ~/.claude/commands/

# Copy starter templates
cp -r agents/templates/* ~/.claude/templates/
```

## Verification

### Manual install

After installing, verify the agents are loaded:

```bash
# Check agent files are in place
ls ~/.claude/agents/
# Expected: architect.md  devops.md  fullstack.md  installer.md  local-review.md  qa.md  security.md  ux.md

ls ~/.claude/commands/
# Expected: agency-run.md  architect.md  devops.md  fullstack.md  hire-team.md  qa.md  security.md  ux.md
```

Then open Claude Code and run:
- `/hire-team` — should display the full team overview
- `/agency-run` — should prompt you for a task and orchestrate the team
- `/architect DIAGNOSE` — should activate the Architect agent

### Plugin install

Open Claude Code and run:
- `/navox-agents:hire-team` — should display the full team overview
- `/navox-agents:agency-run` — should prompt you for a task and orchestrate the team
- `/navox-agents:architect DIAGNOSE` — should activate the Architect agent

## Uninstall

### Plugin uninstall
```
/plugin uninstall navox-agents
/reload-plugins
```

### Manual uninstall
```bash
rm ~/.claude/agents/architect.md
rm ~/.claude/agents/devops.md
rm ~/.claude/agents/fullstack.md
rm ~/.claude/agents/installer.md
rm ~/.claude/agents/local-review.md
rm ~/.claude/agents/ux.md
rm ~/.claude/agents/qa.md
rm ~/.claude/agents/security.md
rm ~/.claude/commands/hire-team.md
rm ~/.claude/commands/agency-run.md
rm ~/.claude/commands/architect.md
rm ~/.claude/commands/devops.md
rm ~/.claude/commands/fullstack.md
rm ~/.claude/commands/qa.md
rm ~/.claude/commands/security.md
rm ~/.claude/commands/ux.md
```

## Listing in Anthropic's Plugin Directory

Navox Agents is available in the Anthropic plugin directory at [claude.com/plugins](https://claude.com/plugins).

To submit updates or new versions, use the [plugin directory submission form](https://clau.de/plugin-directory-submission).
