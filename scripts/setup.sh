#!/usr/bin/env bash
# Setup script for navox-labs/agents
# Installs agents and commands into Claude Code
#
# Usage:
#   bash scripts/setup.sh                          # Install all agents (local project)
#   bash scripts/setup.sh --global                 # Install to home directory (all projects)
#   bash scripts/setup.sh --agents strategist,reviewer  # Install specific agents
#   bash scripts/setup.sh --list                   # List available agents

set -euo pipefail

AGENTS="all"
SCOPE="local"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    echo "Usage: bash scripts/setup.sh [options]"
    echo ""
    echo "Options:"
    echo "  --agents <all|agent1,agent2,...>  Agents to install (default: all)"
    echo "  --global                          Install to home directory (all projects)"
    echo "  --local                           Install to current project (default)"
    echo "  --list                            List available agents"
    echo "  --help                            Show this help"
}

list_agents() {
    echo ""
    echo "Available agents:"
    echo ""
    for f in "$REPO_DIR/.claude/agents/"*.md; do
        name=$(basename "$f" .md)
        desc=$(grep "^description:" "$f" | head -1 | sed 's/^description: //')
        printf "  %-20s %s\n" "$name" "$desc"
    done
    echo ""
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --agents) AGENTS="$2"; shift 2 ;;
        --global) SCOPE="global"; shift ;;
        --local) SCOPE="local"; shift ;;
        --list) list_agents; exit 0 ;;
        --help) usage; exit 0 ;;
        *) echo -e "${RED}Unknown option: $1${NC}"; usage; exit 1 ;;
    esac
done

# Determine target directories
if [ "$SCOPE" = "global" ]; then
    AGENTS_TARGET="$HOME/.claude/agents"
    COMMANDS_TARGET="$HOME/.claude/commands"
else
    AGENTS_TARGET=".claude/agents"
    COMMANDS_TARGET=".claude/commands"
fi

echo ""
echo -e "${BLUE}navox-labs/agents setup${NC}"
echo "========================"
echo -e "Scope:     ${GREEN}$SCOPE${NC}"
echo -e "Agents:    ${GREEN}$AGENTS${NC}"
echo -e "Target:    ${GREEN}$AGENTS_TARGET${NC}"
echo ""

# Create target directories
mkdir -p "$AGENTS_TARGET"
mkdir -p "$COMMANDS_TARGET"

# Build agent list
if [ "$AGENTS" = "all" ]; then
    AGENT_FILES=("$REPO_DIR/.claude/agents/"*.md)
else
    IFS=',' read -ra AGENT_NAMES <<< "$AGENTS"
    AGENT_FILES=()
    for name in "${AGENT_NAMES[@]}"; do
        file="$REPO_DIR/.claude/agents/$name.md"
        if [ -f "$file" ]; then
            AGENT_FILES+=("$file")
        else
            echo -e "${RED}Agent not found: $name${NC}"
            exit 1
        fi
    done
fi

# Install agents
INSTALLED=0
for agent_file in "${AGENT_FILES[@]}"; do
    name=$(basename "$agent_file")
    cp "$agent_file" "$AGENTS_TARGET/$name"

    # Install matching command wrapper if it exists
    command_file="$REPO_DIR/.claude/commands/$name"
    if [ -f "$command_file" ]; then
        cp "$command_file" "$COMMANDS_TARGET/$name"
    fi

    INSTALLED=$((INSTALLED + 1))
    echo -e "  ${GREEN}+${NC} $name"
done

# Copy ETHOS.md to target (agents reference it)
if [ "$SCOPE" = "global" ]; then
    ETHOS_TARGET="$HOME/.claude/ETHOS.md"
else
    ETHOS_TARGET="ETHOS.md"
fi
if [ -f "$REPO_DIR/ETHOS.md" ] && [ ! -f "$ETHOS_TARGET" ]; then
    cp "$REPO_DIR/ETHOS.md" "$ETHOS_TARGET"
    echo -e "  ${GREEN}+${NC} ETHOS.md"
fi

echo ""
echo -e "${GREEN}Done!${NC} Installed $INSTALLED agents to $AGENTS_TARGET"
echo ""
echo "Try it:"
echo "  /hire-team              — see the full team"
echo "  /strategist DIAGNOSE    — validate an idea"
echo "  /agency-run FULL <task> — run a full sprint"
echo ""
