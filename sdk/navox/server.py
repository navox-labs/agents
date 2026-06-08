"""AgentServer — orchestration engine for running agent chains.

Follows Anthropic's course patterns:
- chat() wrapper as single API boundary
- Mutable message list as conversation state
- Tool loop (call model → check stop_reason → execute → feed back)
- Prefill + stop_sequences for structured output
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from navox.models.agent_config import AgentConfig
from navox.models.output_schema import AgentOutput
from navox.validators.output_validator import validate_output


class AgentServer:
    """Orchestration engine that loads agents and runs them in chains."""

    def __init__(
        self,
        agents_dir: str | Path = ".claude/agents",
        registry_path: str | Path = "agents_registry.json",
    ):
        self.agents_dir = Path(agents_dir)
        self.registry_path = Path(registry_path)
        self.agents: dict[str, AgentConfig] = {}
        self.registry: dict = {}
        self._client = None
        self._load_agents()
        self._load_registry()

    def _load_agents(self) -> None:
        """Load all agent configs from disk."""
        if not self.agents_dir.exists():
            return
        for f in self.agents_dir.glob("*.md"):
            config = AgentConfig.from_file(f)
            self.agents[config.slug] = config

    def _load_registry(self) -> None:
        """Load agent registry from JSON."""
        if self.registry_path.exists():
            with open(self.registry_path) as f:
                self.registry = json.load(f)

    @property
    def client(self):
        """Lazy-load Anthropic client."""
        if self._client is None:
            try:
                from anthropic import Anthropic
                self._client = Anthropic()
            except ImportError:
                raise RuntimeError(
                    "anthropic package not installed. "
                    "Run: pip install anthropic"
                )
        return self._client

    # ── Core API (follows Anthropic course pattern) ──────────

    def chat(
        self,
        messages: list[dict],
        system: str | None = None,
        model: str = "claude-sonnet-4-6",
        max_tokens: int = 8192,
        temperature: float = 1.0,
        stop_sequences: list[str] | None = None,
        tools: list[dict] | None = None,
    ) -> dict:
        """Universal chat wrapper — single point of API configuration.

        Returns the full message object from the API.
        """
        params = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
        }
        if system:
            params["system"] = system
        if stop_sequences:
            params["stop_sequences"] = stop_sequences
        if tools:
            params["tools"] = tools

        response = self.client.messages.create(**params)
        return response

    def text_from_message(self, message) -> str:
        """Extract text content from a message response."""
        return "\n".join(
            block.text for block in message.content if block.type == "text"
        )

    # ── Agent execution ──────────────────────────────────────

    def run_agent(
        self,
        agent_id: str,
        mode: str,
        task: str,
        context: str = "",
        project_memory: str = "",
    ) -> AgentRunResult:
        """Run a single agent in a specific mode.

        Args:
            agent_id: Agent slug (e.g., "strategist")
            mode: Agent mode (e.g., "DIAGNOSE")
            task: The task description
            context: Context from previous agents in the chain
            project_memory: Contents of project-memory.md

        Returns:
            AgentRunResult with parsed output and validation
        """
        config = self.agents.get(agent_id)
        if not config:
            raise ValueError(f"Unknown agent: {agent_id}")

        # Build the system prompt from the agent's markdown
        system_prompt = config.raw_content

        # Build the user message
        user_message = self._build_user_message(mode, task, context, project_memory)

        # Run the conversation
        messages = []
        _add_user_message(messages, user_message)

        response = self.chat(
            messages=messages,
            system=system_prompt,
            model=config.model,
            max_tokens=8192,
        )

        raw_output = self.text_from_message(response)

        # Parse and validate the output
        parsed = None
        validation = None
        try:
            parsed = AgentOutput.from_xml(raw_output)
            validation = validate_output(raw_output)
        except ValueError:
            pass  # Output didn't follow XML schema

        return AgentRunResult(
            agent_id=agent_id,
            mode=mode,
            raw_output=raw_output,
            parsed_output=parsed,
            validation=validation,
            model=config.model,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def run_chain(
        self,
        sprint_mode: str,
        task: str,
        project_memory: str = "",
        gate_callback=None,
    ) -> list[AgentRunResult]:
        """Run a full sprint chain (FULL, QUICK, or HOTFIX).

        Args:
            sprint_mode: "full", "quick", or "hotfix"
            task: The task to accomplish
            project_memory: Contents of project-memory.md
            gate_callback: Optional callable for hard gates.
                           Signature: (gate_name, result) -> bool
                           Returns True to continue, False to stop.

        Returns:
            List of AgentRunResults in execution order
        """
        chain = self.registry.get("sprint_chains", {}).get(sprint_mode)
        if not chain:
            raise ValueError(f"Unknown sprint mode: {sprint_mode}")

        results = []
        context = ""

        for group in chain:
            agent_ids = group["agents"]
            modes = group["mode"]
            gate = group.get("gate")

            # Normalize mode to list for parallel groups
            if isinstance(modes, str):
                modes = [modes] * len(agent_ids)

            # Run agents in this group
            group_results = []
            for agent_id, mode in zip(agent_ids, modes):
                result = self.run_agent(
                    agent_id=agent_id,
                    mode=mode,
                    task=task,
                    context=context,
                    project_memory=project_memory,
                )
                group_results.append(result)

            results.extend(group_results)

            # Update context with outputs from this group
            for r in group_results:
                if r.parsed_output:
                    context += f"\n\n--- {r.agent_id} ({r.mode}) ---\n"
                    context += r.raw_output

            # Check gate
            if gate and gate_callback:
                last_result = group_results[-1]
                if not gate_callback(gate, last_result):
                    break  # Gate rejected — stop the chain

            # Check for blocked/error status
            for r in group_results:
                if r.parsed_output and (
                    r.parsed_output.is_blocked or r.parsed_output.is_error
                ):
                    break  # Agent blocked — stop the chain

        return results

    # ── Agent info ───────────────────────────────────────────

    def list_agents(self) -> list[dict]:
        """List all agents with their metadata from the registry."""
        return self.registry.get("agents", [])

    def get_agent(self, agent_id: str) -> dict | None:
        """Get a single agent's registry entry."""
        for agent in self.registry.get("agents", []):
            if agent["id"] == agent_id:
                return agent
        return None

    def get_sprint_chain(self, mode: str) -> list[dict] | None:
        """Get a sprint chain definition."""
        return self.registry.get("sprint_chains", {}).get(mode)

    # ── Helpers ──────────────────────────────────────────────

    def _build_user_message(
        self,
        mode: str,
        task: str,
        context: str,
        project_memory: str,
    ) -> str:
        parts = [f"[MODE: {mode}]", "", f"## Task\n{task}"]

        if project_memory:
            parts.append(f"\n## Project Memory\n{project_memory}")

        if context:
            parts.append(f"\n## Context from previous agents\n{context}")

        return "\n".join(parts)


class AgentRunResult:
    """Result of running a single agent."""

    def __init__(
        self,
        agent_id: str,
        mode: str,
        raw_output: str,
        parsed_output: AgentOutput | None,
        validation,
        model: str,
        timestamp: str,
    ):
        self.agent_id = agent_id
        self.mode = mode
        self.raw_output = raw_output
        self.parsed_output = parsed_output
        self.validation = validation
        self.model = model
        self.timestamp = timestamp

    @property
    def ok(self) -> bool:
        """True if output parsed successfully and passed validation."""
        return (
            self.parsed_output is not None
            and self.validation is not None
            and self.validation.ok
        )

    @property
    def status(self) -> str:
        if self.parsed_output:
            return self.parsed_output.status
        return "PARSE_ERROR"

    def to_dict(self) -> dict:
        """Serialize result for storage or transmission."""
        return {
            "agent_id": self.agent_id,
            "mode": self.mode,
            "status": self.status,
            "ok": self.ok,
            "model": self.model,
            "timestamp": self.timestamp,
            "raw_output": self.raw_output,
            "validation": {
                "passed": self.validation.passed if self.validation else [],
                "failed": self.validation.failed if self.validation else [],
            },
        }


# ── Message helpers (from Anthropic course pattern) ──────────

def _add_user_message(messages: list[dict], content: str) -> None:
    messages.append({"role": "user", "content": content})


def _add_assistant_message(messages: list[dict], content: str) -> None:
    messages.append({"role": "assistant", "content": content})
