"""AgentConfig — parsed representation of an agent's frontmatter and structure."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AgentConfig:
    """Represents a single agent parsed from its markdown file."""

    name: str
    description: str
    model: str
    tools: list[str]
    file_path: str
    modes: list[str] = field(default_factory=list)
    has_handoff_contract: bool = False
    has_self_validation: bool = False
    has_output_format: bool = False
    has_error_protocol: bool = False
    has_memory: bool = False
    has_ethos_ref: bool = False
    has_few_shot: bool = False
    raw_content: str = ""

    @classmethod
    def from_file(cls, path: str | Path) -> AgentConfig:
        """Parse an agent markdown file into an AgentConfig."""
        path = Path(path)
        content = path.read_text(encoding="utf-8")

        # Parse frontmatter
        fm = _parse_frontmatter(content)
        if not fm:
            raise ValueError(f"No valid frontmatter in {path}")

        name = fm.get("name", "")
        description = fm.get("description", "")
        model = fm.get("model", "")
        tools = [t.strip() for t in fm.get("tools", "").split(",") if t.strip()]

        # Parse structural elements
        modes = re.findall(r"\[MODE:\s*([A-Z_]+)\]", content)
        has_handoff = "## Handoff Contract" in content
        has_validation = "Self-validation checklist" in content
        has_output = "## Output Format" in content
        has_error = "## Error Protocol" in content
        has_memory = "## Project memory" in content
        has_ethos = "ETHOS.md" in content
        has_examples = "<examples>" in content or "## Few-Shot" in content

        return cls(
            name=name,
            description=description,
            model=model,
            tools=tools,
            file_path=str(path),
            modes=modes,
            has_handoff_contract=has_handoff,
            has_self_validation=has_validation,
            has_output_format=has_output,
            has_error_protocol=has_error,
            has_memory=has_memory,
            has_ethos_ref=has_ethos,
            has_few_shot=has_examples,
            raw_content=content,
        )

    @property
    def is_opus(self) -> bool:
        return "opus" in self.model

    @property
    def is_utility(self) -> bool:
        return self.name in ("_installer", "local-review")

    @property
    def slug(self) -> str:
        """Agent slug without underscore prefix."""
        return self.name.lstrip("_")


def _parse_frontmatter(content: str) -> dict[str, str] | None:
    """Parse YAML-like frontmatter between --- delimiters."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    result = {}
    for line in match.group(1).strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result
