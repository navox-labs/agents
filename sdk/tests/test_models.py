"""Tests for Batch 1 — models and registry."""

import json
from pathlib import Path

import pytest

from navox.models.agent_config import AgentConfig, _parse_frontmatter
from navox.models.output_schema import AgentOutput, ValidationItem
from navox.models.handoff_contract import HandoffContract

SDK_ROOT = Path(__file__).parent.parent
REPO_ROOT = SDK_ROOT.parent
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
REGISTRY_PATH = SDK_ROOT / "agents_registry.json"


# ── AgentConfig tests ────────────────────────────────────────


class TestFrontmatterParser:
    def test_parses_valid_frontmatter(self):
        content = "---\nname: _test\ndescription: A test agent\nmodel: claude-sonnet-4-6\ntools: Read, Write\n---\n# Content"
        result = _parse_frontmatter(content)
        assert result["name"] == "_test"
        assert result["description"] == "A test agent"
        assert result["model"] == "claude-sonnet-4-6"
        assert result["tools"] == "Read, Write"

    def test_returns_none_for_no_frontmatter(self):
        assert _parse_frontmatter("# No frontmatter here") is None

    def test_returns_none_for_empty_string(self):
        assert _parse_frontmatter("") is None


class TestAgentConfig:
    def test_loads_strategist(self):
        path = AGENTS_DIR / "strategist.md"
        if not path.exists():
            pytest.skip("strategist.md not found")

        config = AgentConfig.from_file(path)
        assert config.name == "_strategist"
        assert "opus" in config.model
        assert config.is_opus
        assert not config.is_utility
        assert "PLAN" in config.modes
        assert "DIAGNOSE" in config.modes
        assert config.has_handoff_contract
        assert config.has_self_validation
        assert config.has_output_format
        assert config.has_error_protocol
        assert config.has_memory
        assert config.has_ethos_ref
        assert config.has_few_shot

    def test_loads_all_15_agents(self):
        if not AGENTS_DIR.exists():
            pytest.skip("agents dir not found")

        agent_files = list(AGENTS_DIR.glob("*.md"))
        assert len(agent_files) == 15

        for f in agent_files:
            config = AgentConfig.from_file(f)
            assert config.name, f"Missing name in {f.name}"
            assert config.description, f"Missing description in {f.name}"
            assert config.model, f"Missing model in {f.name}"

    def test_slug_strips_underscore(self):
        path = AGENTS_DIR / "strategist.md"
        if not path.exists():
            pytest.skip("strategist.md not found")

        config = AgentConfig.from_file(path)
        assert config.slug == "strategist"

    def test_utility_agents_identified(self):
        installer = AGENTS_DIR / "installer.md"
        if not installer.exists():
            pytest.skip("installer.md not found")

        config = AgentConfig.from_file(installer)
        assert config.is_utility


# ── AgentOutput tests ────────────────────────────────────────


class TestAgentOutput:
    SAMPLE_XML = """
    <output>
      <agent>Raya Patel — Strategist</agent>
      <mode>DIAGNOSE</mode>
      <status>COMPLETE</status>
      <timestamp>2026-06-08 14:30</timestamp>
      <input-received>Direct from builder: test idea</input-received>
      <deliverable>Strategic brief here</deliverable>
      <verdict>VALIDATED</verdict>
      <handoff>
        <next-agent>Marcus Chen — Spec Writer</next-agent>
        <next-mode>WRITE</next-mode>
        <context-for-next>Key context for Marcus</context-for-next>
      </handoff>
      <self-validation>
        - [x] Asked at least 5 forcing questions
        - [x] Identified at least 3 risks
        - [ ] Scope recommendation is explicit
      </self-validation>
      <blockers>None</blockers>
    </output>
    """

    def test_parses_complete_output(self):
        output = AgentOutput.from_xml(self.SAMPLE_XML)
        assert output.agent == "Raya Patel — Strategist"
        assert output.mode == "DIAGNOSE"
        assert output.status == "COMPLETE"
        assert output.is_complete
        assert not output.is_blocked
        assert output.verdict == "VALIDATED"
        assert output.next_agent == "Marcus Chen — Spec Writer"
        assert output.next_mode == "WRITE"
        assert "Key context" in output.context_for_next

    def test_parses_validation_items(self):
        output = AgentOutput.from_xml(self.SAMPLE_XML)
        assert len(output.self_validation) == 3
        assert output.self_validation[0].checked is True
        assert output.self_validation[2].checked is False
        assert not output.all_validations_pass
        assert len(output.failed_validations) == 1

    def test_blocked_output(self):
        xml = """
        <output>
          <agent>Test Agent</agent>
          <mode>PLAN</mode>
          <status>BLOCKED</status>
          <timestamp>2026-06-08</timestamp>
          <input-received>None</input-received>
          <deliverable>Need more info</deliverable>
          <verdict>N/A</verdict>
          <handoff>
            <next-agent>None</next-agent>
            <next-mode>N/A</next-mode>
            <context-for-next>N/A</context-for-next>
          </handoff>
          <self-validation>
            - [ ] Missing input
          </self-validation>
          <blockers>Builder must provide context</blockers>
        </output>
        """
        output = AgentOutput.from_xml(xml)
        assert output.is_blocked
        assert not output.is_complete
        assert "Builder must provide" in output.blockers

    def test_raises_on_no_output_block(self):
        with pytest.raises(ValueError, match="No <output> block"):
            AgentOutput.from_xml("just some text without xml")

    def test_raises_on_malformed_xml(self):
        with pytest.raises(ValueError):
            AgentOutput.from_xml("<output><unclosed></output>")


# ── HandoffContract tests ────────────────────────────────────


class TestHandoffContract:
    SAMPLE_CONTENT = """
## Handoff Contract

### What I expect to receive

From **Dmitri** (architect):
- Auth model
- System overview

| Source | Agent | Requirements |
|---|---|---|
| **System design** | Dmitri (architect) | Data model, auth, API |

### What I must deliver

| Required section | Consumed by | Must contain |
|---|---|---|
| **User flows** | Jordan (fullstack) | Step-by-step journeys |
| **Design tokens** | Jordan (fullstack) | Colors, typography |

### Self-validation checklist

- [ ] Every screen has all 5 states
- [ ] Auth flows cover login, signup
"""

    def test_parses_contract(self):
        contract = HandoffContract.from_content("Lena", self.SAMPLE_CONTENT)
        assert contract.agent_name == "Lena"
        assert len(contract.delivers_to) >= 1
        assert len(contract.validation_items) == 2


# ── Registry tests ───────────────────────────────────────────


class TestRegistry:
    def test_registry_loads(self):
        if not REGISTRY_PATH.exists():
            pytest.skip("registry not found")

        with open(REGISTRY_PATH) as f:
            registry = json.load(f)

        assert registry["version"] == "3.0.0"
        assert len(registry["agents"]) == 15

    def test_all_agents_have_required_fields(self):
        if not REGISTRY_PATH.exists():
            pytest.skip("registry not found")

        with open(REGISTRY_PATH) as f:
            registry = json.load(f)

        required = ["id", "name", "role", "model", "file", "modes", "handoff"]
        for agent in registry["agents"]:
            for field in required:
                assert field in agent, f"Agent {agent.get('id', '?')} missing field: {field}"

    def test_registry_matches_agent_files(self):
        if not REGISTRY_PATH.exists() or not AGENTS_DIR.exists():
            pytest.skip("registry or agents dir not found")

        with open(REGISTRY_PATH) as f:
            registry = json.load(f)

        registry_ids = {a["id"] for a in registry["agents"]}
        file_slugs = {f.stem for f in AGENTS_DIR.glob("*.md")}

        # Every file should have a registry entry
        for slug in file_slugs:
            assert slug in registry_ids or slug == "local-review", (
                f"Agent file {slug}.md has no registry entry"
            )

    def test_sprint_chains_reference_valid_agents(self):
        if not REGISTRY_PATH.exists():
            pytest.skip("registry not found")

        with open(REGISTRY_PATH) as f:
            registry = json.load(f)

        agent_ids = {a["id"] for a in registry["agents"]}

        for chain_name, chain in registry["sprint_chains"].items():
            for group in chain:
                for agent_id in group["agents"]:
                    assert agent_id in agent_ids, (
                        f"Sprint chain '{chain_name}' group {group['group']} "
                        f"references unknown agent: {agent_id}"
                    )
