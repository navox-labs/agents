"""AgentOutput — parsed representation of an agent's XML output."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from xml.etree import ElementTree


@dataclass
class AgentOutput:
    """Parsed XML output from any agent."""

    agent: str = ""
    mode: str = ""
    status: str = ""  # COMPLETE | BLOCKED | ERROR
    timestamp: str = ""
    input_received: str = ""
    deliverable: str = ""
    verdict: str = ""
    next_agent: str = ""
    next_mode: str = ""
    context_for_next: str = ""
    self_validation: list[ValidationItem] = field(default_factory=list)
    blockers: str = ""
    raw_xml: str = ""

    @classmethod
    def from_xml(cls, xml_text: str) -> AgentOutput:
        """Parse an agent's XML output into an AgentOutput."""
        # Extract the <output>...</output> block
        match = re.search(r"<output>(.*?)</output>", xml_text, re.DOTALL)
        if not match:
            raise ValueError("No <output> block found in text")

        raw = match.group(0)

        # Parse XML — wrap in try/except for malformed output
        try:
            root = ElementTree.fromstring(raw)
        except ElementTree.ParseError as e:
            raise ValueError(f"Malformed XML: {e}") from e

        # Extract handoff sub-elements
        handoff = root.find("handoff")
        next_agent = _text(handoff, "next-agent") if handoff is not None else ""
        next_mode = _text(handoff, "next-mode") if handoff is not None else ""
        context = _text(handoff, "context-for-next") if handoff is not None else ""

        # Parse self-validation checkboxes
        validation_text = _text(root, "self-validation")
        validations = _parse_validation(validation_text)

        return cls(
            agent=_text(root, "agent"),
            mode=_text(root, "mode"),
            status=_text(root, "status"),
            timestamp=_text(root, "timestamp"),
            input_received=_text(root, "input-received"),
            deliverable=_text(root, "deliverable"),
            verdict=_text(root, "verdict"),
            next_agent=next_agent,
            next_mode=next_mode,
            context_for_next=context,
            self_validation=validations,
            blockers=_text(root, "blockers"),
            raw_xml=raw,
        )

    @property
    def is_complete(self) -> bool:
        return self.status.upper() == "COMPLETE"

    @property
    def is_blocked(self) -> bool:
        return self.status.upper() == "BLOCKED"

    @property
    def is_error(self) -> bool:
        return self.status.upper() == "ERROR"

    @property
    def all_validations_pass(self) -> bool:
        return all(v.checked for v in self.self_validation)

    @property
    def failed_validations(self) -> list[ValidationItem]:
        return [v for v in self.self_validation if not v.checked]


@dataclass
class ValidationItem:
    """A single self-validation checkbox item."""

    text: str
    checked: bool


def _text(element: ElementTree.Element, tag: str) -> str:
    """Safely extract text from a child element."""
    child = element.find(tag)
    if child is None:
        return ""
    # Get all text content including tail text of sub-elements
    return "".join(child.itertext()).strip()


def _parse_validation(text: str) -> list[ValidationItem]:
    """Parse markdown checkbox items from self-validation text."""
    items = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- [x]"):
            items.append(ValidationItem(text=line[5:].strip(), checked=True))
        elif line.startswith("- [ ]"):
            items.append(ValidationItem(text=line[5:].strip(), checked=False))
    return items
