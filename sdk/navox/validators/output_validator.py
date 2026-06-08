"""Output validator — validates agent XML output against the schema."""

from __future__ import annotations

from navox.models.output_schema import AgentOutput
from navox.validators.frontmatter import ValidationResult


# Required XML fields for a valid output
REQUIRED_FIELDS = [
    "agent", "mode", "status", "timestamp",
    "input_received", "deliverable", "verdict",
]

VALID_STATUSES = {"COMPLETE", "BLOCKED", "ERROR"}


def validate_output(xml_text: str) -> ValidationResult:
    """Validate an XML output string against the agent output schema."""
    result = ValidationResult(agent_name="output")

    # 1. Parse XML
    try:
        output = AgentOutput.from_xml(xml_text)
        result.passed.append("xml: parses successfully")
    except ValueError as e:
        result.failed.append(f"xml: parse error — {e}")
        return result

    result.agent_name = output.agent or "unknown"

    # 2. Required fields present
    for field_name in REQUIRED_FIELDS:
        value = getattr(output, field_name, "")
        if value and value.strip():
            result.passed.append(f"field: {field_name} present")
        else:
            result.failed.append(f"field: {field_name} missing or empty")

    # 3. Status is valid
    status_upper = output.status.upper().strip()
    if status_upper in VALID_STATUSES:
        result.passed.append(f"status: valid ({status_upper})")
    else:
        result.failed.append(f"status: '{output.status}' not in {VALID_STATUSES}")

    # 4. Handoff present (required for COMPLETE status)
    if output.is_complete:
        if output.next_agent:
            result.passed.append("handoff: next-agent specified")
        else:
            result.failed.append("handoff: COMPLETE but no next-agent specified")

        if output.context_for_next:
            result.passed.append("handoff: context-for-next present")
        else:
            result.failed.append("handoff: COMPLETE but no context-for-next")

    # 5. Self-validation present
    if output.self_validation:
        result.passed.append(f"self-validation: {len(output.self_validation)} items")

        if output.is_complete and not output.all_validations_pass:
            failed = output.failed_validations
            result.failed.append(
                f"self-validation: COMPLETE but {len(failed)} item(s) unchecked"
            )
        elif output.is_complete:
            result.passed.append("self-validation: all items checked")
    else:
        result.failed.append("self-validation: no validation items found")

    # 6. Blockers field
    if output.blockers:
        result.passed.append("blockers: field present")

        if output.is_blocked and output.blockers.strip().lower() == "none":
            result.failed.append("blockers: status BLOCKED but blockers says 'None'")
    else:
        result.failed.append("blockers: field missing")

    return result


def validate_few_shot_examples(raw_content: str) -> ValidationResult:
    """Validate few-shot examples embedded in an agent's prompt."""
    result = ValidationResult(agent_name="few-shot")

    import re
    examples = re.findall(
        r"<example[^>]*>(.*?)</example>", raw_content, re.DOTALL
    )

    if not examples:
        result.failed.append("no <example> blocks found")
        return result

    result.passed.append(f"found {len(examples)} example(s)")

    for i, example_text in enumerate(examples, 1):
        # Each example should contain a valid <output> block
        try:
            output = AgentOutput.from_xml(example_text)
            result.passed.append(f"example {i}: valid XML output")

            # Check it has the essential fields
            if output.agent:
                result.passed.append(f"example {i}: agent name present")
            else:
                result.failed.append(f"example {i}: missing agent name")

            if output.status:
                result.passed.append(f"example {i}: status present ({output.status})")
            else:
                result.failed.append(f"example {i}: missing status")

        except ValueError as e:
            result.failed.append(f"example {i}: invalid — {e}")

    return result
