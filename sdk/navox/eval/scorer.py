"""Scorer — deterministic scoring of agent prompts against the quality rubric.

This is Layer 1 evaluation: static analysis without API calls.
Replaces scripts/eval.sh with proper Python validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from navox.models.agent_config import AgentConfig
from navox.validators.frontmatter import validate_frontmatter
from navox.validators.prompt_linter import lint_prompt
from navox.validators.output_validator import validate_few_shot_examples


PASS_THRESHOLD = 8  # Minimum score to pass


@dataclass
class AgentScore:
    """Score for a single agent against the quality rubric."""

    agent_id: str
    agent_name: str
    checks: list[ScoreCheck] = field(default_factory=list)

    @property
    def score(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def passed(self) -> bool:
        return self.score >= PASS_THRESHOLD

    @property
    def failed_checks(self) -> list[ScoreCheck]:
        return [c for c in self.checks if not c.passed]


@dataclass
class ScoreCheck:
    """A single rubric check."""

    name: str
    passed: bool
    detail: str = ""


def score_agent(config: AgentConfig) -> AgentScore:
    """Score an agent against the 10-point quality rubric.

    Rubric (from eval/rubric.md):
    1. Frontmatter completeness
    2. Mode coverage (PLAN + 2 operational)
    3. Anti-hallucination rules
    4. Handoff contracts
    5. Anti-sycophancy
    6. Error handling
    7. Structured output format
    8. Scope boundaries
    9. Preamble reference (ETHOS.md)
    10. Memory integration
    """
    # Get registry info for agent name
    agent_name = config.slug

    result = AgentScore(agent_id=config.slug, agent_name=agent_name)

    # 1. Frontmatter completeness
    fm = validate_frontmatter(config)
    result.checks.append(ScoreCheck(
        name="Frontmatter completeness",
        passed=fm.ok,
        detail="; ".join(fm.failed) if fm.failed else "All fields valid",
    ))

    # 2. Mode coverage
    if config.name == "local-review":
        has_modes = len(config.modes) >= 1
    else:
        has_modes = "PLAN" in config.modes and len(config.modes) >= 3
    result.checks.append(ScoreCheck(
        name="Mode coverage",
        passed=has_modes,
        detail=f"Modes: {', '.join(config.modes)}",
    ))

    # 3. Anti-hallucination
    content_lower = config.raw_content.lower()
    anti_terms = ["evidence", "verify", "reproduce", "never guess",
                  "investigate before", "proven", "confirm"]
    has_anti = any(t in content_lower for t in anti_terms)
    result.checks.append(ScoreCheck(
        name="Anti-hallucination rules",
        passed=has_anti,
        detail="Found verification language" if has_anti else "No verification rules",
    ))

    # 4. Handoff contracts
    has_handoff = config.has_handoff_contract and config.has_self_validation
    result.checks.append(ScoreCheck(
        name="Handoff contracts",
        passed=has_handoff,
        detail="Contract + validation present" if has_handoff else "Missing",
    ))

    # 5. Anti-sycophancy
    import re
    if config.slug in ("strategist", "reviewer"):
        terms = ["never say.*great idea", "anti-sycophancy", "not a cheerleader",
                 "never sound like", "looks good.*but"]
        has_anti_syc = any(re.search(t, content_lower) for t in terms)
    else:
        has_anti_syc = True  # Non-strategist/reviewer get a pass
    result.checks.append(ScoreCheck(
        name="Anti-sycophancy",
        passed=has_anti_syc,
        detail="Rules present" if has_anti_syc else "Missing for strategist/reviewer",
    ))

    # 6. Error handling
    error_terms = ["error protocol", "status: blocked", "status: error",
                   "missing.*input", "flag.*missing", "if.*fail"]
    has_error = any(re.search(t, content_lower) for t in error_terms)
    result.checks.append(ScoreCheck(
        name="Error handling",
        passed=has_error,
        detail="Error protocol present" if has_error else "No error handling",
    ))

    # 7. Structured output format
    result.checks.append(ScoreCheck(
        name="Structured output format",
        passed=config.has_output_format,
        detail="## Output Format present" if config.has_output_format else "Missing",
    ))

    # 8. Scope boundaries
    has_scope = "## What You Never Do" in config.raw_content
    result.checks.append(ScoreCheck(
        name="Scope boundaries",
        passed=has_scope,
        detail="What You Never Do present" if has_scope else "Missing",
    ))

    # 9. Preamble reference
    result.checks.append(ScoreCheck(
        name="Preamble reference (ETHOS.md)",
        passed=config.has_ethos_ref,
        detail="ETHOS.md referenced" if config.has_ethos_ref else "Missing",
    ))

    # 10. Memory integration
    has_memory = (config.has_memory
                  and "Current State" in config.raw_content
                  and "History" in config.raw_content)
    result.checks.append(ScoreCheck(
        name="Memory integration",
        passed=has_memory,
        detail="Memory with Current State + History" if has_memory else "Missing",
    ))

    return result


def score_all_agents(agents_dir: str | Path) -> list[AgentScore]:
    """Score all agents in a directory."""
    agents_dir = Path(agents_dir)
    scores = []

    for f in sorted(agents_dir.glob("*.md")):
        config = AgentConfig.from_file(f)

        # Skip utility agents
        if config.is_utility:
            continue

        scores.append(score_agent(config))

    return scores


def format_scores(scores: list[AgentScore]) -> str:
    """Format scores as a human-readable report."""
    lines = [
        "=" * 50,
        "  AGENT QUALITY EVAL — Python Scorer",
        "  10-point rubric, threshold: 8/10",
        "=" * 50,
        "",
    ]

    total_pass = 0
    total_fail = 0

    for score in scores:
        status = "PASS" if score.passed else "FAIL"
        if score.passed:
            total_pass += 1
        else:
            total_fail += 1

        lines.append(f"{status}  {score.agent_id} — {score.score}/{score.total}")

        if not score.passed:
            for check in score.failed_checks:
                lines.append(f"  - {check.name}: {check.detail}")

    lines.extend([
        "",
        "=" * 50,
        f"  Results: {total_pass} passed, {total_fail} failed",
        f"  Threshold: {PASS_THRESHOLD}/10",
        "=" * 50,
    ])

    return "\n".join(lines)
