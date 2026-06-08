"""CLI entry point — `navox` command.

Usage:
    navox validate              Run all validators (frontmatter, lint, contracts)
    navox validate <agent_id>   Validate a single agent
    navox score                 Score all agents against 10-point rubric
    navox score <agent_id>      Score a single agent
    navox team                  Show team roster
    navox info <agent_id>       Show agent details
    navox sprint <mode>         Show sprint chain for a mode
    navox summary               Show system summary
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from navox_agents.client import AgentClient
from navox_agents.eval.scorer import score_agent, score_all_agents, format_scores
from navox_agents.models.agent_config import AgentConfig


def main():
    parser = argparse.ArgumentParser(
        prog="navox",
        description="Navox Agents — validation, evaluation, and orchestration",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # validate
    p_validate = sub.add_parser("validate", help="Run validators")
    p_validate.add_argument("agent_id", nargs="?", help="Agent to validate (or all)")

    # score
    p_score = sub.add_parser("score", help="Score agents against rubric")
    p_score.add_argument("agent_id", nargs="?", help="Agent to score (or all)")

    # team
    sub.add_parser("team", help="Show team roster")

    # info
    p_info = sub.add_parser("info", help="Show agent details")
    p_info.add_argument("agent_id", help="Agent ID")

    # sprint
    p_sprint = sub.add_parser("sprint", help="Show sprint chain")
    p_sprint.add_argument("mode", choices=["full", "quick", "hotfix"])

    # summary
    sub.add_parser("summary", help="Show system summary")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # Find repo root (where CLAUDE.md lives)
    repo_root = _find_repo_root()
    agents_dir = repo_root / ".claude" / "agents"
    registry_path = repo_root / "agents_registry.json"

    client = AgentClient(agents_dir, registry_path)

    if args.command == "validate":
        _cmd_validate(client, agents_dir, args.agent_id)
    elif args.command == "score":
        _cmd_score(agents_dir, args.agent_id)
    elif args.command == "team":
        _cmd_team(client)
    elif args.command == "info":
        _cmd_info(client, args.agent_id)
    elif args.command == "sprint":
        _cmd_sprint(client, args.mode)
    elif args.command == "summary":
        _cmd_summary(client)


def _cmd_validate(client: AgentClient, agents_dir: Path, agent_id: str | None):
    if agent_id:
        results = client.validate_agent(agent_id)
        total_passed = sum(len(r.passed) for r in results.values())
        total_failed = sum(len(r.failed) for r in results.values())

        print(f"\n  Validation: {agent_id}")
        print("=" * 50)
        for category, result in results.items():
            status = "PASS" if result.ok else "FAIL"
            print(f"  {status}  {category} — {result.score}/{result.total}")
            for f in result.failed:
                print(f"    - {f}")
        print(f"\n  Total: {total_passed} passed, {total_failed} failed")
    else:
        results = client.validate_all()
        total_passed = sum(len(r.passed) for r in results.values())
        total_failed = sum(len(r.failed) for r in results.values())

        print(f"\n  Full Validation")
        print("=" * 50)

        # Group by agent
        by_agent = {}
        other = {}
        for key, result in results.items():
            if ":" in key:
                category, agent = key.split(":", 1)
                by_agent.setdefault(agent, []).append((category, result))
            else:
                other[key] = result

        for agent, checks in sorted(by_agent.items()):
            all_ok = all(r.ok for _, r in checks)
            status = "PASS" if all_ok else "FAIL"
            print(f"  {status}  {agent}")
            for category, result in checks:
                if not result.ok:
                    for f in result.failed:
                        print(f"    - [{category}] {f}")

        for key, result in other.items():
            status = "PASS" if result.ok else "FAIL"
            print(f"  {status}  {key}")
            for f in result.failed:
                print(f"    - {f}")

        print(f"\n  Total: {total_passed} passed, {total_failed} failed")

        if total_failed > 0:
            sys.exit(1)


def _cmd_score(agents_dir: Path, agent_id: str | None):
    if agent_id:
        path = agents_dir / f"{agent_id}.md"
        if not path.exists():
            print(f"Agent not found: {agent_id}")
            sys.exit(1)
        config = AgentConfig.from_file(path)
        score = score_agent(config)
        print(f"\n  {score.agent_id}: {score.score}/{score.total}")
        for check in score.checks:
            status = "PASS" if check.passed else "FAIL"
            print(f"    {status}  {check.name} — {check.detail}")
    else:
        scores = score_all_agents(agents_dir)
        print(format_scores(scores))

        if any(not s.passed for s in scores):
            sys.exit(1)


def _cmd_team(client: AgentClient):
    roster = client.get_team_roster()
    print(f"\n  {'Name':<20} {'Role':<20} {'Exp':<6} {'Command':<20} Modes")
    print("  " + "-" * 90)
    for r in roster:
        modes = ", ".join(r["modes"][:3])
        if len(r["modes"]) > 3:
            modes += f" +{len(r['modes']) - 3}"
        exp = f"{r['experience']}yr" if r["experience"] else "-"
        cmd = r["command"] or "-"
        print(f"  {r['name']:<20} {r['role']:<20} {exp:<6} {cmd:<20} {modes}")


def _cmd_info(client: AgentClient, agent_id: str):
    agent = client.get_agent(agent_id)
    if not agent:
        print(f"Agent not found: {agent_id}")
        sys.exit(1)

    print(f"\n  {agent['name']} — {agent['role']}")
    print("=" * 50)
    print(f"  Experience: {agent.get('experience_years', 'N/A')} years")
    print(f"  Background: {agent.get('background', 'N/A')}")
    print(f"  Model: {agent['model']}")
    print(f"  Command: {agent.get('command', 'N/A')}")
    print(f"  Modes: {', '.join(agent.get('modes', []))}")
    print(f"  Auth: {agent.get('auth_ownership', 'N/A')}")

    persona = agent.get("persona", {})
    if persona:
        print(f"\n  Style: {persona.get('style', 'N/A')}")
        print(f"  Strengths: {', '.join(persona.get('strengths', []))}")
        anti = persona.get("anti_patterns", [])
        if anti:
            print(f"  Anti-patterns: {', '.join(anti)}")

    handoff = agent.get("handoff", {})
    if handoff:
        print(f"\n  Receives from: {', '.join(handoff.get('receives_from', []))}")
        print(f"  Delivers to: {', '.join(handoff.get('delivers_to', []))}")


def _cmd_sprint(client: AgentClient, mode: str):
    chain = client.get_sprint_chain(mode)
    if not chain:
        print(f"Unknown sprint mode: {mode}")
        sys.exit(1)

    print(f"\n  Sprint Chain: {mode.upper()}")
    print("=" * 50)
    for group in chain:
        agents = ", ".join(group["agents"])
        modes = group["mode"]
        if isinstance(modes, list):
            modes = ", ".join(modes)
        gate = f" [GATE: {group['gate']}]" if group.get("gate") else ""
        parallel = " (parallel)" if group.get("parallel") else ""
        print(f"  Group {group['group']}: {agents} — {modes}{parallel}{gate}")


def _cmd_summary(client: AgentClient):
    s = client.summary()
    print(f"\n  Navox Agents v{s['version']}")
    print("=" * 50)
    print(f"  Team: {s['team_name']}")
    print(f"  Total agents: {s['total_agents']}")
    print(f"  Human agents: {s['human_agents']}")
    print(f"  Utility agents: {s['utility_agents']}")
    print(f"  Sprint modes: {', '.join(s['sprint_modes'])}")
    print(f"  Hard gates: {', '.join(s['hard_gates'])}")


def _find_repo_root() -> Path:
    """Walk up from cwd to find the repo root (where CLAUDE.md lives)."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / "CLAUDE.md").exists():
            return parent
    # Fallback to cwd
    return current


if __name__ == "__main__":
    main()
