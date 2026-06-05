#!/usr/bin/env bash
# Multi-platform setup script for navox-labs/agents
# Zero dependencies — bash + git only
#
# Usage:
#   bash scripts/setup.sh                          # Install all agents for Claude Code (local)
#   bash scripts/setup.sh --platform cursor         # Install for Cursor
#   bash scripts/setup.sh --agents strategist,reviewer  # Install specific agents
#   bash scripts/setup.sh --global                  # Install to home directory
#
# Supported platforms: claude, cursor, copilot, codex

set -euo pipefail

# Defaults
PLATFORM="claude"
AGENTS="all"
SCOPE="local"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    echo "Usage: bash scripts/setup.sh [options]"
    echo ""
    echo "Options:"
    echo "  --platform <claude|cursor|copilot|codex>  Target platform (default: claude)"
    echo "  --agents <all|agent1,agent2,...>           Agents to install (default: all)"
    echo "  --global                                   Install to home directory"
    echo "  --local                                    Install to current project (default)"
    echo "  --list                                     List available agents"
    echo "  --help                                     Show this help"
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
        --platform) PLATFORM="$2"; shift 2 ;;
        --agents) AGENTS="$2"; shift 2 ;;
        --global) SCOPE="global"; shift ;;
        --local) SCOPE="local"; shift ;;
        --list) list_agents; exit 0 ;;
        --help) usage; exit 0 ;;
        *) echo -e "${RED}Unknown option: $1${NC}"; usage; exit 1 ;;
    esac
done

# Validate platform
case $PLATFORM in
    claude|cursor|copilot|codex) ;;
    *) echo -e "${RED}Unsupported platform: $PLATFORM${NC}"; echo "Supported: claude, cursor, copilot, codex"; exit 1 ;;
esac

# Determine target directories
case $PLATFORM in
    claude)
        if [ "$SCOPE" = "global" ]; then
            AGENTS_TARGET="$HOME/.claude/agents"
            COMMANDS_TARGET="$HOME/.claude/commands"
        else
            AGENTS_TARGET=".claude/agents"
            COMMANDS_TARGET=".claude/commands"
        fi
        ;;
    cursor)
        if [ "$SCOPE" = "global" ]; then
            AGENTS_TARGET="$HOME/.cursor/agents"
            COMMANDS_TARGET="$HOME/.cursor/commands"
        else
            AGENTS_TARGET=".cursor/agents"
            COMMANDS_TARGET=".cursor/commands"
        fi
        ;;
    copilot)
        if [ "$SCOPE" = "global" ]; then
            AGENTS_TARGET="$HOME/.copilot/skills/navox-agents"
            COMMANDS_TARGET="$HOME/.copilot/skills/navox-agents/commands"
        else
            AGENTS_TARGET=".copilot/skills/navox-agents"
            COMMANDS_TARGET=".copilot/skills/navox-agents/commands"
        fi
        ;;
    codex)
        if [ "$SCOPE" = "global" ]; then
            AGENTS_TARGET="$HOME/agents"
            COMMANDS_TARGET="$HOME/agents/commands"
        else
            AGENTS_TARGET="agents"
            COMMANDS_TARGET="agents/commands"
        fi
        ;;
esac

echo ""
echo -e "${BLUE}navox-labs/agents setup${NC}"
echo "========================"
echo -e "Platform:  ${GREEN}$PLATFORM${NC}"
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

# Verification
echo "Verify installation:"
echo "  ls $AGENTS_TARGET"
if [ "$PLATFORM" = "claude" ]; then
    echo ""
    echo "Try it:"
    echo "  /hire-team          — see the full team"
    echo "  /strategist DIAGNOSE — validate an idea"
    echo "  /agency-run FULL <task> — run a full sprint"
fi
echo ""
