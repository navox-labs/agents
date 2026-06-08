"""Tests for Batch 2 — validators."""

from pathlib import Path

import pytest

from navox.models.agent_config import AgentConfig
from navox.validators.frontmatter import validate_frontmatter
from navox.validators.prompt_linter import lint_prompt
from navox.validators.output_validator import (
    validate_output,
    validate_few_shot_examples,
)

SDK_ROOT = Path(__file__).parent.parent
REPO_ROOT = SDK_ROOT.parent
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"


# ── Frontmatter validation ──────────────────────────────────


class TestFrontmatterValidator:
    def test_strategist_passes(self):
        config = AgentConfig.from_file(AGENTS_DIR / "strategist.md")
        result = validate_frontmatter(config)
        assert result.ok, f"Failures: {result.failed}"

    def test_all_agents_pass_frontmatter(self):
        for f in AGENTS_DIR.glob("*.md"):
            config = AgentConfig.from_file(f)
            result = validate_frontmatter(config)
            assert result.ok, f"{f.name} failed: {result.failed}"

    def test_detects_missing_name(self):
        config = AgentConfig(
            name="", description="test", model="claude-sonnet-4-6",
            tools=["Read"], file_path="test.md",
        )
        result = validate_frontmatter(config)
        assert not result.ok
        assert any("name" in f for f in result.failed)

    def test_detects_invalid_model(self):
        config = AgentConfig(
            name="_test", description="A test agent for testing",
            model="gpt-4", tools=["Read"], file_path="test.md",
        )
        result = validate_frontmatter(config)
        assert not result.ok
        assert any("model" in f for f in result.failed)

    def test_detects_wrong_model_routing(self):
        # Strategist should use Opus
        config = AgentConfig(
            name="_strategist", description="A strategist agent for testing",
            model="claude-sonnet-4-6", tools=["Read"], file_path="test.md",
        )
        result = validate_frontmatter(config)
        assert any("Opus" in f for f in result.failed)


# ── Prompt linter ────────────────────────────────────────────


class TestPromptLinter:
    def test_strategist_passes(self):
        config = AgentConfig.from_file(AGENTS_DIR / "strategist.md")
        result = lint_prompt(config)
        assert result.ok, f"Failures: {result.failed}"

    def test_all_non_utility_agents_pass(self):
        for f in AGENTS_DIR.glob("*.md"):
            config = AgentConfig.from_file(f)
            if config.is_utility:
                continue
            result = lint_prompt(config)
            assert result.ok, f"{f.name} failed: {result.failed}"

    def test_utility_agents_exempt(self):
        config = AgentConfig.from_file(AGENTS_DIR / "installer.md")
        result = lint_prompt(config)
        assert result.ok

    def test_detects_missing_plan_mode(self):
        config = AgentConfig(
            name="_test", description="test", model="claude-sonnet-4-6",
            tools=["Read"], file_path="test.md", modes=["BUILD", "REVIEW"],
            has_handoff_contract=True, has_self_validation=True,
            has_output_format=True, has_error_protocol=True,
            has_memory=True, has_ethos_ref=True,
            raw_content="## Identity\n## What You Never Do\nevidence verify\n<output></output>",
        )
        result = lint_prompt(config)
        assert any("PLAN" in f for f in result.failed)


# ── Output validator ─────────────────────────────────────────


class TestOutputValidator:
    VALID_OUTPUT = """
    <output>
      <agent>Raya Patel — Strategist</agent>
      <mode>DIAGNOSE</mode>
      <status>COMPLETE</status>
      <timestamp>2026-06-08 14:30</timestamp>
      <input-received>Direct from builder: test</input-received>
      <deliverable>Strategic brief</deliverable>
      <verdict>VALIDATED</verdict>
      <handoff>
        <next-agent>Marcus Chen — Spec Writer</next-agent>
        <next-mode>WRITE</next-mode>
        <context-for-next>Context here</context-for-next>
      </handoff>
      <self-validation>
        - [x] All checks pass
      </self-validation>
      <blockers>None</blockers>
    </output>
    """

    def test_valid_output_passes(self):
        result = validate_output(self.VALID_OUTPUT)
        assert result.ok, f"Failures: {result.failed}"

    def test_missing_fields_detected(self):
        xml = """
        <output>
          <agent>Test</agent>
          <mode>PLAN</mode>
          <status>COMPLETE</status>
          <timestamp></timestamp>
          <input-received></input-received>
          <deliverable></deliverable>
          <verdict></verdict>
          <handoff>
            <next-agent></next-agent>
            <next-mode></next-mode>
            <context-for-next></context-for-next>
          </handoff>
          <self-validation></self-validation>
          <blockers></blockers>
        </output>
        """
        result = validate_output(xml)
        assert not result.ok
        assert len(result.failed) > 0

    def test_invalid_status_detected(self):
        xml = """
        <output>
          <agent>Test</agent>
          <mode>PLAN</mode>
          <status>INVALID</status>
          <timestamp>2026-06-08</timestamp>
          <input-received>test</input-received>
          <deliverable>test</deliverable>
          <verdict>test</verdict>
          <handoff>
            <next-agent>Next</next-agent>
            <next-mode>PLAN</next-mode>
            <context-for-next>ctx</context-for-next>
          </handoff>
          <self-validation>
            - [x] check
          </self-validation>
          <blockers>None</blockers>
        </output>
        """
        result = validate_output(xml)
        assert any("status" in f.lower() for f in result.failed)

    def test_blocked_with_none_blockers_fails(self):
        xml = """
        <output>
          <agent>Test</agent>
          <mode>PLAN</mode>
          <status>BLOCKED</status>
          <timestamp>2026-06-08</timestamp>
          <input-received>test</input-received>
          <deliverable>need more</deliverable>
          <verdict>N/A</verdict>
          <handoff>
            <next-agent>None</next-agent>
            <next-mode>N/A</next-mode>
            <context-for-next>N/A</context-for-next>
          </handoff>
          <self-validation>
            - [ ] blocked
          </self-validation>
          <blockers>None</blockers>
        </output>
        """
        result = validate_output(xml)
        assert any("BLOCKED" in f and "None" in f for f in result.failed)


# ── Few-shot example validator ───────────────────────────────


class TestFewShotValidator:
    def test_strategist_examples_valid(self):
        config = AgentConfig.from_file(AGENTS_DIR / "strategist.md")
        result = validate_few_shot_examples(config.raw_content)
        assert result.ok, f"Failures: {result.failed}"
        assert any("2 example" in p for p in result.passed)

    def test_agents_with_examples_pass(self):
        for f in AGENTS_DIR.glob("*.md"):
            config = AgentConfig.from_file(f)
            if not config.has_few_shot:
                continue
            result = validate_few_shot_examples(config.raw_content)
            assert result.ok, f"{f.name} few-shot failed: {result.failed}"
