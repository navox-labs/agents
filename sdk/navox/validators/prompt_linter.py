"""Prompt linter — validates agent prompt structure and required sections."""

from __future__ import annotations

from navox.models.agent_config import AgentConfig
from navox.validators.frontmatter import ValidationResult


def lint_prompt(config: AgentConfig) -> ValidationResult:
    """Lint an agent's prompt for required structural elements."""
    result = ValidationResult(agent_name=config.name)

    # Skip utility agents — they don't follow the standard structure
    if config.is_utility:
        result.passed.append("utility agent — exempt from standard structure")
        return result

    # 1. Mode coverage: PLAN + at least 2 operational modes
    if config.name == "local-review":
        # local-review is exempt from PLAN requirement
        if len(config.modes) >= 1:
            result.passed.append(f"modes: {len(config.modes)} mode(s) defined")
        else:
            result.failed.append("modes: no modes defined")
    else:
        if "PLAN" in config.modes:
            result.passed.append("modes: has PLAN mode")
        else:
            result.failed.append("modes: missing PLAN mode")

        if len(config.modes) >= 3:
            result.passed.append(f"modes: {len(config.modes)} modes (3+ required)")
        else:
            result.failed.append(f"modes: only {len(config.modes)} modes (need 3+)")

    # 2. Required sections
    _check_section(result, config.has_handoff_contract, "Handoff Contract")
    _check_section(result, config.has_self_validation, "Self-validation checklist")
    _check_section(result, config.has_output_format, "Output Format")
    _check_section(result, config.has_error_protocol, "Error Protocol")
    _check_section(result, config.has_memory, "Project memory")
    _check_section(result, config.has_ethos_ref, "ETHOS.md reference")

    # 3. Anti-hallucination rules
    content = config.raw_content.lower()
    anti_hallucination_terms = [
        "evidence", "verify", "reproduce", "never guess",
        "investigate before", "proven", "confirm", "do not assume",
    ]
    if any(term in content for term in anti_hallucination_terms):
        result.passed.append("anti-hallucination: rules present")
    else:
        result.failed.append("anti-hallucination: no verification rules found")

    # 4. Anti-sycophancy (required for strategist/reviewer)
    if config.slug in ("strategist", "reviewer"):
        import re
        sycophancy_terms = [
            "never say.*great idea", "anti-sycophancy",
            "not a cheerleader", "do not agree",
            "looks good.*but", "what you never sound like",
            "never sound like",
        ]
        if any(re.search(term, content) for term in sycophancy_terms):
            result.passed.append("anti-sycophancy: rules present")
        else:
            result.failed.append("anti-sycophancy: missing for strategist/reviewer")

    # 5. Scope boundaries
    if "## What You Never Do" in config.raw_content:
        result.passed.append("scope boundaries: What You Never Do present")
    else:
        result.failed.append("scope boundaries: missing What You Never Do")

    # 6. XML output schema
    if "<output>" in config.raw_content and "</output>" in config.raw_content:
        result.passed.append("XML output: schema present in Output Format")
    else:
        result.failed.append("XML output: no <output> schema found")

    # 7. Few-shot examples
    if config.has_few_shot:
        result.passed.append("few-shot examples: present")
    else:
        result.failed.append("few-shot examples: missing")

    # 8. Identity/persona section
    if "## Identity" in config.raw_content:
        result.passed.append("identity: persona section present")
    else:
        result.failed.append("identity: missing ## Identity section")

    # 9. Team member names (not generic role titles)
    team_names = ["Raya", "Marcus", "Dmitri", "Lena", "Jordan", "Sam", "Ava",
                  "Priya", "Kai", "Omar", "Elena", "James", "Nina"]
    names_found = sum(1 for name in team_names if name in config.raw_content)
    if names_found >= 3:
        result.passed.append(f"team names: {names_found} team member names referenced")
    else:
        result.failed.append(f"team names: only {names_found} names found (need 3+)")

    return result


def _check_section(result: ValidationResult, present: bool, name: str) -> None:
    if present:
        result.passed.append(f"section: {name} present")
    else:
        result.failed.append(f"section: {name} missing")
