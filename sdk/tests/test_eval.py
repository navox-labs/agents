"""Tests for Batch 5 — evaluation system."""

from pathlib import Path

import pytest

from navox.eval.scorer import (
    score_agent,
    score_all_agents,
    format_scores,
    AgentScore,
    PASS_THRESHOLD,
)
from navox.eval.runner import (
    AgentEvaluator,
    EvalResult,
    EvalTask,
    format_eval_results,
)
from navox.models.agent_config import AgentConfig

SDK_ROOT = Path(__file__).parent.parent
REPO_ROOT = SDK_ROOT.parent
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
REGISTRY_PATH = SDK_ROOT / "agents_registry.json"


# ── Layer 1: Static scorer ──────────────────────────────────


class TestScorer:
    def test_strategist_scores_10(self):
        config = AgentConfig.from_file(AGENTS_DIR / "strategist.md")
        score = score_agent(config)
        assert score.score == 10, (
            f"Strategist scored {score.score}/10. "
            f"Failed: {[c.name for c in score.failed_checks]}"
        )

    def test_all_agents_pass_threshold(self):
        scores = score_all_agents(AGENTS_DIR)
        for score in scores:
            assert score.passed, (
                f"{score.agent_id} scored {score.score}/10 "
                f"(threshold: {PASS_THRESHOLD}). "
                f"Failed: {[f'{c.name}: {c.detail}' for c in score.failed_checks]}"
            )

    def test_score_all_returns_correct_count(self):
        scores = score_all_agents(AGENTS_DIR)
        # 15 agents - 2 utility (installer) = at least 13
        # installer is utility, local-review may or may not be
        assert len(scores) >= 13

    def test_format_scores(self):
        scores = score_all_agents(AGENTS_DIR)
        report = format_scores(scores)
        assert "AGENT QUALITY EVAL" in report
        assert "Results:" in report


# ── Layer 2: Deterministic evaluator ─────────────────────────


class TestEvaluatorDeterministic:
    GOOD_OUTPUT = """
    <output>
      <agent>Raya Patel — Strategist</agent>
      <mode>DIAGNOSE</mode>
      <status>COMPLETE</status>
      <timestamp>2026-06-08 14:30</timestamp>
      <input-received>Direct from builder: Build an invoicing app for freelancers</input-received>
      <deliverable>
        ## Strategic Brief

        This is a comprehensive strategic analysis of the freelancer invoicing
        idea. The problem is real — solo freelancers waste time on Google Docs
        invoices. The market has Wave and FreshBooks but they're bloated for
        the target user. Recommended MVP: create invoice, send link, mark paid.
      </deliverable>
      <verdict>VALIDATED — with scope discipline</verdict>
      <handoff>
        <next-agent>Marcus Chen — Spec Writer</next-agent>
        <next-mode>WRITE</next-mode>
        <context-for-next>Key constraints: v1 manual payment only, no Stripe</context-for-next>
      </handoff>
      <self-validation>
        - [x] Asked at least 5 forcing questions
        - [x] Identified at least 3 risks
        - [x] Scope recommendation explicit
        - [x] No sycophantic language
        - [x] Verdict clear and justified
      </self-validation>
      <blockers>None</blockers>
    </output>
    """

    def test_good_output_scores_high(self):
        evaluator = AgentEvaluator(AGENTS_DIR, REGISTRY_PATH)
        result = evaluator.eval_deterministic(
            "strategist", "DIAGNOSE",
            "Build an invoicing app",
            self.GOOD_OUTPUT,
        )
        assert result.schema_score >= 7.0
        assert result.completeness_score >= 7.0
        assert result.combined_score >= 7.0

    def test_bad_output_scores_low(self):
        evaluator = AgentEvaluator(AGENTS_DIR, REGISTRY_PATH)
        result = evaluator.eval_deterministic(
            "strategist", "DIAGNOSE",
            "Build an invoicing app",
            "This is not XML at all.",
        )
        assert result.combined_score < 3.0

    def test_partial_output_scores_medium(self):
        partial_xml = """
        <output>
          <agent>Test Agent</agent>
          <mode>PLAN</mode>
          <status>COMPLETE</status>
          <timestamp>2026-06-08</timestamp>
          <input-received>test</input-received>
          <deliverable>Short</deliverable>
          <verdict>OK</verdict>
          <handoff>
            <next-agent>Next</next-agent>
            <next-mode>BUILD</next-mode>
            <context-for-next>ctx</context-for-next>
          </handoff>
          <self-validation></self-validation>
          <blockers>None</blockers>
        </output>
        """
        evaluator = AgentEvaluator(AGENTS_DIR, REGISTRY_PATH)
        result = evaluator.eval_deterministic(
            "test", "PLAN", "test task", partial_xml,
        )
        # Should score somewhere in the middle
        assert 2.0 <= result.combined_score <= 9.0

    def test_format_results(self):
        results = [
            EvalResult(
                agent_id="strategist", mode="DIAGNOSE",
                task="test", raw_output="test",
                schema_score=9.0, completeness_score=8.0,
                combined_score=8.5,
            ),
        ]
        report = format_eval_results(results)
        assert "PASS" in report
        assert "strategist" in report


# ── EvalTask ─────────────────────────────────────────────────


class TestEvalTask:
    def test_creates_task(self):
        task = EvalTask(
            agent_id="strategist",
            mode="DIAGNOSE",
            task="Build an invoicing app",
            expected_status="COMPLETE",
        )
        assert task.agent_id == "strategist"
        assert task.mode == "DIAGNOSE"
