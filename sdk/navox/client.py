"""AgentClient — interface for interacting with the agent server.

Provides a clean API for:
- Listing and querying agents
- Running individual agents
- Running sprint chains
- Validating outputs
"""

from __future__ import annotations

import json
from pathlib import Path

from navox.server import AgentServer, AgentRunResult
from navox.models.agent_config import AgentConfig
from navox.validators.frontmatter import validate_frontmatter, ValidationResult
from navox.validators.prompt_linter import lint_prompt
from navox.validators.output_validator import (
    validate_output,
    validate_few_shot_examples,
)
from navox.validators.contract_checker import (
    validate_contracts,
    validate_registry_contracts,
)


class AgentClient:
    """Client interface for the Navox agent system."""

    def __init__(
        self,
        agents_dir: str | Path = ".claude/agents",
        registry_path: str | Path = "agents_registry.json",
    ):
        self.server = AgentServer(
            agents_dir=agents_dir,
            registry_path=registry_path,
        )

    # ── Agent queries ────────────────────────────────────────

    def list_agents(self) -> list[dict]:
        """List all agents with their metadata."""
        return self.server.list_agents()

    def get_agent(self, agent_id: str) -> dict | None:
        """Get a single agent by ID."""
        return self.server.get_agent(agent_id)

    def get_team_roster(self) -> list[dict]:
        """Get a formatted team roster."""
        agents = self.server.list_agents()
        return [
            {
                "name": a["name"],
                "role": a["role"],
                "experience": a.get("experience_years"),
                "command": a.get("command"),
                "modes": a.get("modes", []),
            }
            for a in agents
            if a.get("experience_years")  # Skip utility agents
        ]

    def get_sprint_chain(self, mode: str) -> list[dict] | None:
        """Get a sprint chain definition."""
        return self.server.get_sprint_chain(mode)

    # ── Agent execution ──────────────────────────────────────

    def run(
        self,
        agent_id: str,
        mode: str,
        task: str,
        context: str = "",
    ) -> AgentRunResult:
        """Run a single agent."""
        return self.server.run_agent(
            agent_id=agent_id,
            mode=mode,
            task=task,
            context=context,
        )

    def run_sprint(
        self,
        mode: str,
        task: str,
        gate_callback=None,
    ) -> list[AgentRunResult]:
        """Run a full sprint chain."""
        return self.server.run_chain(
            sprint_mode=mode,
            task=task,
            gate_callback=gate_callback,
        )

    # ── Validation ───────────────────────────────────────────

    def validate_all(self) -> dict[str, ValidationResult]:
        """Run all validators across all agents. Returns results by category."""
        results = {}

        # Frontmatter validation
        for slug, config in self.server.agents.items():
            key = f"frontmatter:{slug}"
            results[key] = validate_frontmatter(config)

        # Prompt linting
        for slug, config in self.server.agents.items():
            key = f"lint:{slug}"
            results[key] = lint_prompt(config)

        # Few-shot validation
        for slug, config in self.server.agents.items():
            if config.has_few_shot:
                key = f"few-shot:{slug}"
                results[key] = validate_few_shot_examples(config.raw_content)

        # Contract validation (registry-aware)
        results["contracts"] = validate_contracts(
            self.server.agents_dir,
            registry_path=self.server.registry_path,
        )

        # Registry validation
        results["registry-contracts"] = validate_registry_contracts(
            self.server.agents_dir,
            self.server.registry_path,
        )

        return results

    def validate_agent(self, agent_id: str) -> dict[str, ValidationResult]:
        """Run all validators for a single agent."""
        config = self.server.agents.get(agent_id)
        if not config:
            raise ValueError(f"Unknown agent: {agent_id}")

        results = {
            "frontmatter": validate_frontmatter(config),
            "lint": lint_prompt(config),
        }

        if config.has_few_shot:
            results["few-shot"] = validate_few_shot_examples(config.raw_content)

        return results

    def validate_output(self, xml_text: str) -> ValidationResult:
        """Validate an XML output string."""
        return validate_output(xml_text)

    # ── Summary ──────────────────────────────────────────────

    def summary(self) -> dict:
        """Get a summary of the agent system."""
        agents = self.server.list_agents()
        return {
            "version": self.server.registry.get("version", "unknown"),
            "team_name": self.server.registry.get("team_name", "unknown"),
            "total_agents": len(agents),
            "human_agents": sum(
                1 for a in agents if a.get("experience_years")
            ),
            "utility_agents": sum(
                1 for a in agents if not a.get("experience_years")
            ),
            "sprint_modes": list(
                self.server.registry.get("sprint_chains", {}).keys()
            ),
            "hard_gates": list(
                self.server.registry.get("hard_gates", {}).keys()
            ),
        }
