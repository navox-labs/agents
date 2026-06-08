"""Tests for Batch 4 — server and client (no API calls)."""

from pathlib import Path

import pytest

from navox.server import AgentServer, _add_user_message, _add_assistant_message
from navox.client import AgentClient

SDK_ROOT = Path(__file__).parent.parent
REPO_ROOT = SDK_ROOT.parent
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
REGISTRY_PATH = SDK_ROOT / "agents_registry.json"


# ── Server tests ─────────────────────────────────────────────


class TestAgentServer:
    def test_loads_agents(self):
        server = AgentServer(AGENTS_DIR, REGISTRY_PATH)
        assert len(server.agents) == 15

    def test_loads_registry(self):
        server = AgentServer(AGENTS_DIR, REGISTRY_PATH)
        assert server.registry["version"] == "3.0.0"
        assert len(server.registry["agents"]) == 15

    def test_list_agents(self):
        server = AgentServer(AGENTS_DIR, REGISTRY_PATH)
        agents = server.list_agents()
        assert len(agents) == 15
        names = {a["name"] for a in agents}
        assert "Raya Patel" in names
        assert "Dmitri Volkov" in names

    def test_get_agent(self):
        server = AgentServer(AGENTS_DIR, REGISTRY_PATH)
        agent = server.get_agent("strategist")
        assert agent is not None
        assert agent["name"] == "Raya Patel"
        assert agent["experience_years"] == 16

    def test_get_agent_not_found(self):
        server = AgentServer(AGENTS_DIR, REGISTRY_PATH)
        assert server.get_agent("nonexistent") is None

    def test_get_sprint_chain(self):
        server = AgentServer(AGENTS_DIR, REGISTRY_PATH)
        chain = server.get_sprint_chain("full")
        assert chain is not None
        assert len(chain) == 10  # 10 groups in FULL sprint

        chain_quick = server.get_sprint_chain("quick")
        assert len(chain_quick) == 6

        chain_hotfix = server.get_sprint_chain("hotfix")
        assert len(chain_hotfix) == 3

    def test_build_user_message(self):
        server = AgentServer(AGENTS_DIR, REGISTRY_PATH)
        msg = server._build_user_message(
            mode="DIAGNOSE",
            task="Build an invoicing app",
            context="",
            project_memory="Stack: Next.js",
        )
        assert "[MODE: DIAGNOSE]" in msg
        assert "Build an invoicing app" in msg
        assert "Stack: Next.js" in msg

    def test_unknown_agent_raises(self):
        server = AgentServer(AGENTS_DIR, REGISTRY_PATH)
        with pytest.raises(ValueError, match="Unknown agent"):
            server.run_agent("nonexistent", "PLAN", "test")

    def test_unknown_sprint_mode_raises(self):
        server = AgentServer(AGENTS_DIR, REGISTRY_PATH)
        with pytest.raises(ValueError, match="Unknown sprint mode"):
            server.run_chain("turbo", "test")


# ── Message helpers ──────────────────────────────────────────


class TestMessageHelpers:
    def test_add_user_message(self):
        messages = []
        _add_user_message(messages, "hello")
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "hello"

    def test_add_assistant_message(self):
        messages = []
        _add_assistant_message(messages, "hi there")
        assert len(messages) == 1
        assert messages[0]["role"] == "assistant"
        assert messages[0]["content"] == "hi there"

    def test_conversation_flow(self):
        messages = []
        _add_user_message(messages, "hello")
        _add_assistant_message(messages, "hi")
        _add_user_message(messages, "how are you")
        assert len(messages) == 3
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
        assert messages[2]["role"] == "user"


# ── Client tests ─────────────────────────────────────────────


class TestAgentClient:
    def test_creates_client(self):
        client = AgentClient(AGENTS_DIR, REGISTRY_PATH)
        assert client.server is not None

    def test_list_agents(self):
        client = AgentClient(AGENTS_DIR, REGISTRY_PATH)
        agents = client.list_agents()
        assert len(agents) == 15

    def test_get_team_roster(self):
        client = AgentClient(AGENTS_DIR, REGISTRY_PATH)
        roster = client.get_team_roster()
        # Should exclude utility agents (installer, local-review)
        assert len(roster) == 13
        names = {r["name"] for r in roster}
        assert "Raya Patel" in names
        assert "Installer" not in names

    def test_summary(self):
        client = AgentClient(AGENTS_DIR, REGISTRY_PATH)
        summary = client.summary()
        assert summary["version"] == "3.0.0"
        assert summary["total_agents"] == 15
        assert summary["human_agents"] == 13
        assert summary["utility_agents"] == 2
        assert "full" in summary["sprint_modes"]
        assert "strategy" in summary["hard_gates"]

    def test_validate_all(self):
        client = AgentClient(AGENTS_DIR, REGISTRY_PATH)
        results = client.validate_all()
        assert len(results) > 0

        # Count passes and failures
        total_passed = sum(len(r.passed) for r in results.values())
        total_failed = sum(len(r.failed) for r in results.values())
        assert total_passed > 0
        print(f"\nValidation: {total_passed} passed, {total_failed} failed")

    def test_validate_single_agent(self):
        client = AgentClient(AGENTS_DIR, REGISTRY_PATH)
        results = client.validate_agent("strategist")
        assert "frontmatter" in results
        assert "lint" in results
        assert results["frontmatter"].ok
        assert results["lint"].ok

    def test_validate_unknown_agent_raises(self):
        client = AgentClient(AGENTS_DIR, REGISTRY_PATH)
        with pytest.raises(ValueError, match="Unknown agent"):
            client.validate_agent("nonexistent")

    def test_validate_output(self):
        client = AgentClient(AGENTS_DIR, REGISTRY_PATH)
        xml = """
        <output>
          <agent>Test</agent>
          <mode>PLAN</mode>
          <status>COMPLETE</status>
          <timestamp>2026-06-08</timestamp>
          <input-received>test</input-received>
          <deliverable>test</deliverable>
          <verdict>VALIDATED</verdict>
          <handoff>
            <next-agent>Next Agent</next-agent>
            <next-mode>BUILD</next-mode>
            <context-for-next>context</context-for-next>
          </handoff>
          <self-validation>
            - [x] check passed
          </self-validation>
          <blockers>None</blockers>
        </output>
        """
        result = client.validate_output(xml)
        assert result.ok, f"Failures: {result.failed}"
