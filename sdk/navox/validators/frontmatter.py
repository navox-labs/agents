"""Frontmatter validator — validates agent YAML frontmatter fields."""

from __future__ import annotations

from dataclasses import dataclass, field

from navox.models.agent_config import AgentConfig

# Agents that must use Opus
OPUS_AGENTS = {"_architect", "_security", "_strategist", "_reviewer"}

# Valid model names
VALID_MODELS = {"claude-opus-4-6", "claude-sonnet-4-6"}

# Valid tool names
VALID_TOOLS = {"Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebSearch", "Agent"}


@dataclass
class ValidationResult:
    """Result of validating a single agent."""

    agent_name: str
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.failed) == 0

    @property
    def score(self) -> int:
        total = len(self.passed) + len(self.failed)
        return len(self.passed) if total > 0 else 0

    @property
    def total(self) -> int:
        return len(self.passed) + len(self.failed)


def validate_frontmatter(config: AgentConfig) -> ValidationResult:
    """Validate an agent's frontmatter fields."""
    result = ValidationResult(agent_name=config.name)

    # 1. Name field exists and follows convention
    if config.name:
        if config.is_utility or config.name.startswith("_") or config.name == "local-review":
            result.passed.append("name: valid format")
        else:
            result.failed.append(f"name: '{config.name}' should start with underscore or be a utility")
    else:
        result.failed.append("name: missing")

    # 2. Description exists and is meaningful
    if config.description and len(config.description) > 20:
        result.passed.append("description: present and meaningful")
    elif config.description:
        result.failed.append("description: too short (< 20 chars)")
    else:
        result.failed.append("description: missing")

    # 3. Model is valid
    if config.model in VALID_MODELS:
        result.passed.append(f"model: valid ({config.model})")
    elif config.model:
        result.failed.append(f"model: unknown model '{config.model}'")
    else:
        result.failed.append("model: missing")

    # 4. Model routing (Opus vs Sonnet)
    if config.name in OPUS_AGENTS:
        if "opus" in config.model:
            result.passed.append("model routing: correctly uses Opus")
        else:
            result.failed.append(f"model routing: {config.name} should use Opus, not {config.model}")
    elif not config.is_utility and config.name != "local-review":
        if "sonnet" in config.model:
            result.passed.append("model routing: correctly uses Sonnet")
        else:
            result.failed.append(f"model routing: {config.name} should use Sonnet, not {config.model}")

    # 5. Tools are valid
    if config.tools:
        invalid = [t for t in config.tools if t not in VALID_TOOLS]
        if invalid:
            result.failed.append(f"tools: unknown tools {invalid}")
        else:
            result.passed.append(f"tools: valid ({', '.join(config.tools)})")
    else:
        result.failed.append("tools: missing")

    return result
