"""Tests for the autonomous orchestrator and journal."""

import json
import tempfile
from pathlib import Path

import pytest

from navox.journal import Journal, JournalEntry
from navox.orchestrator import (
    Orchestrator,
    StepResult,
    ChainResult,
    format_chain_result,
)
from navox.models.output_schema import AgentOutput

SDK_ROOT = Path(__file__).parent.parent
REPO_ROOT = SDK_ROOT.parent
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
REGISTRY_PATH = SDK_ROOT / "agents_registry.json"


# ── Journal tests ─────────────────────────────────────────────


class TestJournal:
    def test_make_key_deterministic(self):
        key1 = Journal.make_key("strategist", "DIAGNOSE", "build X", "abc")
        key2 = Journal.make_key("strategist", "DIAGNOSE", "build X", "abc")
        assert key1 == key2

    def test_make_key_varies_with_input(self):
        key1 = Journal.make_key("strategist", "DIAGNOSE", "build X", "")
        key2 = Journal.make_key("architect", "DESIGN", "build X", "")
        assert key1 != key2

    def test_save_and_retrieve(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        journal = Journal(path)
        key = "test_key_001"
        entry = JournalEntry(
            key=key,
            agent_id="strategist",
            mode="DIAGNOSE",
            status="COMPLETE",
            raw_output="<output>test</output>",
            timestamp=1000.0,
            duration_ms=500,
            model="claude-sonnet-4-6",
        )
        journal.save(key, entry)

        assert journal.has(key)
        retrieved = journal.get(key)
        assert retrieved.agent_id == "strategist"
        assert retrieved.status == "COMPLETE"

        # Verify persistence
        journal2 = Journal(path)
        assert journal2.has(key)
        Path(path).unlink()

    def test_has_returns_false_for_errors(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        journal = Journal(path)
        key = "error_key"
        entry = JournalEntry(
            key=key, agent_id="test", mode="TEST",
            status="ERROR", raw_output="", timestamp=1000.0,
            error="something broke",
        )
        journal.save(key, entry)

        # has() returns False for errors (so they get retried)
        assert not journal.has(key)
        Path(path).unlink()

    def test_clear(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        journal = Journal(path)
        journal.save("k1", JournalEntry(
            key="k1", agent_id="test", mode="T",
            status="COMPLETE", raw_output="", timestamp=1.0,
        ))
        assert journal.has("k1")
        journal.clear()
        assert not journal.has("k1")

    def test_summary(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        journal = Journal(path)
        journal.save("k1", JournalEntry(
            key="k1", agent_id="a", mode="M",
            status="COMPLETE", raw_output="", timestamp=1.0,
            duration_ms=100,
        ))
        journal.save("k2", JournalEntry(
            key="k2", agent_id="b", mode="M",
            status="ERROR", raw_output="", timestamp=2.0,
            duration_ms=50,
        ))
        s = journal.summary()
        assert s["total"] == 2
        assert s["completed"] == 1
        assert s["failed"] == 1
        assert s["total_duration_ms"] == 150
        Path(path).unlink()


# ── Orchestrator tests ────────────────────────────────────────


class TestOrchestrator:
    def test_creates_orchestrator(self):
        orch = Orchestrator(
            agents_dir=AGENTS_DIR,
            registry_path=REGISTRY_PATH,
        )
        assert len(orch.agents) >= 13
        assert "full" in orch.registry.get("sprint_chains", {})

    def test_dry_run_full(self):
        orch = Orchestrator(
            agents_dir=AGENTS_DIR,
            registry_path=REGISTRY_PATH,
        )
        result = orch.dry_run("full", "Build an invoicing app")
        assert result.sprint_mode == "full"
        assert len(result.steps) >= 10  # Full sprint has 10+ agents
        assert all(s.status == "SKIPPED" for s in result.steps)
        assert all(s.model for s in result.steps)

    def test_dry_run_quick(self):
        orch = Orchestrator(
            agents_dir=AGENTS_DIR,
            registry_path=REGISTRY_PATH,
        )
        result = orch.dry_run("quick", "Add dark mode")
        assert len(result.steps) >= 5

    def test_dry_run_hotfix(self):
        orch = Orchestrator(
            agents_dir=AGENTS_DIR,
            registry_path=REGISTRY_PATH,
        )
        result = orch.dry_run("hotfix", "Fix login bug")
        assert len(result.steps) == 3
        agent_ids = [s.agent_id for s in result.steps]
        assert "investigator" in agent_ids
        assert "fullstack" in agent_ids
        assert "shipper" in agent_ids

    def test_dry_run_unknown_mode_raises(self):
        orch = Orchestrator(
            agents_dir=AGENTS_DIR,
            registry_path=REGISTRY_PATH,
        )
        with pytest.raises(ValueError, match="Unknown sprint mode"):
            orch.dry_run("invalid", "test")

    def test_dry_run_missing_agent_shows_error(self):
        """If registry references a non-existent agent, dry_run shows ERROR."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({
                "agents": [],
                "sprint_chains": {
                    "test": [{"group": 1, "agents": ["nonexistent"], "mode": "RUN"}]
                },
            }, f)
            path = f.name

        orch = Orchestrator(
            agents_dir=AGENTS_DIR,
            registry_path=path,
        )
        result = orch.dry_run("test", "test task")
        assert result.steps[0].status == "ERROR"
        assert "not found" in result.steps[0].error
        Path(path).unlink()


# ── StepResult tests ──────────────────────────────────────────


class TestStepResult:
    def test_ok_when_complete(self):
        step = StepResult(agent_id="test", mode="M", status="COMPLETE")
        assert step.ok

    def test_not_ok_when_error(self):
        step = StepResult(agent_id="test", mode="M", status="ERROR")
        assert not step.ok

    def test_context_for_next_uses_parsed(self):
        """If parsed output has context_for_next, use it."""
        step = StepResult(
            agent_id="test", mode="M", status="COMPLETE",
            raw_output="full output here",
        )
        # Without parsed output, falls back to raw
        assert step.context_for_next == "full output here"


# ── ChainResult tests ────────────────────────────────────────


class TestChainResult:
    def test_ok_when_all_complete(self):
        result = ChainResult(
            sprint_mode="full", task="test",
            steps=[
                StepResult(agent_id="a", mode="M", status="COMPLETE"),
                StepResult(agent_id="b", mode="M", status="COMPLETE"),
            ],
        )
        assert result.ok

    def test_not_ok_when_interrupted(self):
        result = ChainResult(
            sprint_mode="full", task="test",
            steps=[StepResult(agent_id="a", mode="M", status="COMPLETE")],
            interrupted=True,
            interrupt_reason="agent b failed",
        )
        assert not result.ok

    def test_summary(self):
        result = ChainResult(
            sprint_mode="full", task="test",
            steps=[
                StepResult(agent_id="a", mode="M", status="COMPLETE", duration_ms=100),
                StepResult(agent_id="b", mode="M", status="ERROR", duration_ms=50),
            ],
        )
        s = result.summary()
        assert s["completed"] == 1
        assert s["failed"] == 1
        assert s["total_duration_ms"] == 150

    def test_format_chain_result(self):
        result = ChainResult(
            sprint_mode="full", task="Build an app",
            steps=[
                StepResult(
                    agent_id="strategist", mode="DIAGNOSE",
                    status="COMPLETE", duration_ms=1500,
                ),
            ],
        )
        report = format_chain_result(result)
        assert "SPRINT REPORT" in report
        assert "strategist" in report
        assert "COMPLETE" in report

    def test_format_chain_result_with_eval_scores(self):
        result = ChainResult(
            sprint_mode="full", task="Build an app",
            steps=[
                StepResult(
                    agent_id="strategist", mode="DIAGNOSE",
                    status="COMPLETE", duration_ms=1500,
                    eval_score=8.5, retry_count=0,
                ),
                StepResult(
                    agent_id="architect", mode="DESIGN",
                    status="COMPLETE", duration_ms=2000,
                    eval_score=6.0, retry_count=1,
                ),
            ],
        )
        report = format_chain_result(result)
        assert "eval=8.5" in report
        assert "eval=6.0" in report
        assert "retried 1x" in report


# ── Eval integration tests ───────────────────────────────────


GOOD_OUTPUT_XML = """<output>
<agent>strategist</agent>
<mode>DIAGNOSE</mode>
<status>COMPLETE</status>
<timestamp>2024-01-01T00:00:00Z</timestamp>
<input-received>Build an invoicing app</input-received>
<deliverable>This is a detailed diagnosis of the problem that spans more than fifty characters to pass the substance check.</deliverable>
<verdict>The task is well-scoped and ready for architecture.</verdict>
<handoff>
  <next-agent>architect</next-agent>
  <next-mode>DESIGN</next-mode>
  <context-for-next>Diagnosis complete. Key findings: needs invoicing, payments, PDF export.</context-for-next>
</handoff>
<self-validation>
- [x] Diagnosis covers the core problem
- [x] Verdict is actionable
</self-validation>
<blockers>None</blockers>
</output>"""

WEAK_OUTPUT_XML = """<output>
<agent>strategist</agent>
<mode>DIAGNOSE</mode>
<status>COMPLETE</status>
<timestamp>2024-01-01T00:00:00Z</timestamp>
<input-received>Build an invoicing app</input-received>
<deliverable>Short.</deliverable>
<verdict></verdict>
<handoff>
  <next-agent></next-agent>
  <next-mode></next-mode>
  <context-for-next></context-for-next>
</handoff>
<self-validation>
- [ ] Not checked
</self-validation>
<blockers>None</blockers>
</output>"""


class TestEvalIntegration:
    def test_evaluate_good_output(self):
        orch = Orchestrator(
            agents_dir=AGENTS_DIR,
            registry_path=REGISTRY_PATH,
        )
        score, details = orch._evaluate_output(
            "strategist", "DIAGNOSE", "Build an app", GOOD_OUTPUT_XML,
        )
        assert score >= 8.0, f"Good output should score 8+, got {score}: {details}"
        assert details["xml_parses"] is True
        assert details["deliverable_substance"] is True
        assert details["handoff_present"] is True
        assert details["self_validation_present"] is True
        assert details["self_validation_passing"] is True

    def test_evaluate_weak_output(self):
        orch = Orchestrator(
            agents_dir=AGENTS_DIR,
            registry_path=REGISTRY_PATH,
        )
        score, details = orch._evaluate_output(
            "strategist", "DIAGNOSE", "Build an app", WEAK_OUTPUT_XML,
        )
        assert score < 7.0, f"Weak output should score <7, got {score}: {details}"
        assert details["deliverable_substance"] is False
        assert details["field_verdict"] is False

    def test_evaluate_unparseable_output(self):
        orch = Orchestrator(
            agents_dir=AGENTS_DIR,
            registry_path=REGISTRY_PATH,
        )
        score, details = orch._evaluate_output(
            "strategist", "DIAGNOSE", "Build an app", "not xml at all",
        )
        assert score == 0.0
        assert details["xml_parses"] is False

    def test_step_result_has_eval_fields(self):
        step = StepResult(
            agent_id="test", mode="M", status="COMPLETE",
            eval_score=7.5, eval_details={"xml_parses": True},
            retry_count=1,
        )
        assert step.eval_score == 7.5
        assert step.retry_count == 1
        assert step.eval_details["xml_parses"] is True

    def test_eval_threshold_constant(self):
        orch = Orchestrator(
            agents_dir=AGENTS_DIR,
            registry_path=REGISTRY_PATH,
        )
        assert orch.EVAL_THRESHOLD == 8.0
