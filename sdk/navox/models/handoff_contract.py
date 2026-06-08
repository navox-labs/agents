"""HandoffContract — parsed representation of agent handoff expectations."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class HandoffContract:
    """What an agent expects to receive and must deliver."""

    agent_name: str
    receives_from: list[ContractEntry] = field(default_factory=list)
    delivers_to: list[ContractEntry] = field(default_factory=list)
    validation_items: list[str] = field(default_factory=list)

    @classmethod
    def from_content(cls, agent_name: str, content: str) -> HandoffContract:
        """Parse handoff contract from agent markdown content."""
        # "What I must deliver" always uses tables
        delivers = _parse_contract_table(content, "What I must deliver")

        # "What I expect to receive" uses prose OR tables — try both
        receives = _parse_contract_table(content, "What I expect to receive")
        if not receives:
            receives = _parse_receives_prose(content)

        validations = _parse_checklist(content)

        return cls(
            agent_name=agent_name,
            receives_from=receives,
            delivers_to=delivers,
            validation_items=validations,
        )

    def validate_against(self, other: HandoffContract) -> list[str]:
        """Check if this agent's deliverables match what another agent expects.

        Returns a list of mismatches. Empty list = contracts are compatible.
        """
        errors = []

        # Check: does 'other' expect something from me?
        for entry in other.receives_from:
            if self.agent_name.lower() in entry.agent.lower():
                # They expect something from me — do I deliver it?
                matching = [
                    d
                    for d in self.delivers_to
                    if _sections_overlap(d.section, entry.section)
                ]
                if not matching:
                    errors.append(
                        f"{self.agent_name} does not deliver '{entry.section}' "
                        f"that {other.agent_name} expects"
                    )

        return errors


@dataclass
class ContractEntry:
    """A single row in a handoff contract table."""

    section: str
    agent: str  # consumed by / received from
    requirements: str


def _parse_contract_table(content: str, header: str) -> list[ContractEntry]:
    """Parse a markdown table under a specific header."""
    entries = []

    # Find the section
    pattern = rf"###?\s*{re.escape(header)}(.*?)(?=###|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return entries

    section_text = match.group(1)

    # Parse table rows — handle both 3-column and 4+ column tables
    # 4-column: | Mode | Section | Consumed by | Details |
    # 3-column: | Section | Consumed by | Details |
    rows = re.findall(r"\|(.+?)\|(.+?)\|(.+?)\|(?:(.+?)\|)?", section_text)
    for row in rows:
        cells = [c.strip().strip("*") for c in row if c]
        # Skip header/separator rows
        if any(c.startswith("---") for c in cells):
            continue
        if cells[0].lower() in ("required section", "source", "mode"):
            continue

        if len(cells) >= 4:
            # 4-column table: section=col[1], agent=col[2], requirements=col[3]
            entries.append(
                ContractEntry(section=cells[1], agent=cells[2], requirements=cells[3])
            )
        else:
            # 3-column table: section=col[0], agent=col[1], requirements=col[2]
            entries.append(
                ContractEntry(section=cells[0], agent=cells[1], requirements=cells[2])
            )

    return entries


def _parse_receives_prose(content: str) -> list[ContractEntry]:
    """Parse 'What I expect to receive' from prose format.

    Agents use several patterns:
    - From **Dmitri** (architect — DESIGN):         (bold name, parenthesized role)
    - From **Jordan Rivera — Full Stack Engineer**:  (bold full name with role)
    - From Marcus (spec-writer):                     (plain name, parenthesized role)
    - from Dmitri Volkov (architect, DESIGN):         (inline in bold-prefixed line)
    - From the builder directly:
    - From the sprint chain:
    """
    entries = []

    # Find the "What I expect to receive" section
    pattern = r"###?\s*What I expect to receive(.*?)(?=###|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return entries

    section = match.group(1)

    # Map human first names to agent slugs
    name_to_slug = {
        "raya": "strategist", "marcus": "spec-writer", "dmitri": "architect",
        "lena": "ux", "jordan": "fullstack", "sam": "investigator",
        "ava": "reviewer", "priya": "qa", "kai": "security",
        "omar": "devops", "elena": "shipper", "james": "retro",
        "nina": "context-manager",
    }

    found_slugs = set()

    # Pattern 1: From **Name** (role) or From **Name — Role** (mode)
    bold_patterns = re.findall(
        r"[Ff]rom\s+\*\*([^*]+)\*\*\s*\(([^)]+)\)", section
    )
    for name_part, role_part in bold_patterns:
        slug = _resolve_agent_slug(name_part, role_part, name_to_slug)
        if slug and slug not in found_slugs:
            found_slugs.add(slug)
            entries.append(ContractEntry(
                section=f"input from {slug}",
                agent=slug,
                requirements=role_part.strip(),
            ))

    # Pattern 2: From Name (role) — plain text, no bold
    plain_patterns = re.findall(
        r"[Ff]rom\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(([^)]+)\)", section
    )
    for name_part, role_part in plain_patterns:
        slug = _resolve_agent_slug(name_part, role_part, name_to_slug)
        if slug and slug not in found_slugs:
            found_slugs.add(slug)
            entries.append(ContractEntry(
                section=f"input from {slug}",
                agent=slug,
                requirements=role_part.strip(),
            ))

    # Pattern 3: Inline "from Name (role)" inside bold-prefixed lines
    # e.g., "**In CODE-AUDIT mode** — from Jordan Rivera (fullstack, BUILD):"
    inline_patterns = re.findall(
        r"from\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(([^)]+)\)", section
    )
    for name_part, role_part in inline_patterns:
        slug = _resolve_agent_slug(name_part, role_part, name_to_slug)
        if slug and slug not in found_slugs:
            found_slugs.add(slug)
            entries.append(ContractEntry(
                section=f"input from {slug}",
                agent=slug,
                requirements=role_part.strip(),
            ))

    # Pattern 4: Agent names mentioned in sub-bullets
    # e.g., "- Ava (reviewer)" or "- Priya (QA)"
    bullet_patterns = re.findall(
        r"[-•]\s+(?:.*?)([A-Z][a-z]+)\s*\(([^)]+)\)", section
    )
    for name_part, role_part in bullet_patterns:
        slug = _resolve_agent_slug(name_part, role_part, name_to_slug)
        if slug and slug not in found_slugs:
            found_slugs.add(slug)
            entries.append(ContractEntry(
                section=f"input from {slug}",
                agent=slug,
                requirements=role_part.strip(),
            ))

    # Also check for "From the builder" / "From the sprint chain"
    if re.search(r"[Ff]rom the builder|[Ff]rom builder", section):
        entries.append(ContractEntry(
            section="input from builder",
            agent="builder",
            requirements="direct input",
        ))

    if re.search(r"[Ff]rom the sprint chain|[Ff]rom.*sprint", section):
        entries.append(ContractEntry(
            section="input from sprint chain",
            agent="sprint-chain",
            requirements="chain context",
        ))

    if re.search(r"[Ff]rom any", section):
        entries.append(ContractEntry(
            section="input from any",
            agent="any",
            requirements="any agent",
        ))

    return entries


def _resolve_agent_slug(
    name_part: str,
    role_part: str,
    name_to_slug: dict[str, str],
) -> str:
    """Resolve a human name + role to an agent slug."""
    first_name = name_part.split()[0].lower().rstrip(",")
    agent_slug = name_to_slug.get(first_name, "")

    if not agent_slug:
        role_lower = role_part.lower()
        for slug_name in [
            "architect", "strategist", "spec-writer", "fullstack",
            "ux", "investigator", "reviewer", "qa",
            "security", "devops", "shipper", "retro", "context-manager",
        ]:
            if slug_name in role_lower:
                agent_slug = slug_name
                break

    if agent_slug == "builder":
        return ""
    return agent_slug


def _parse_checklist(content: str) -> list[str]:
    """Extract self-validation checklist items."""
    items = []
    in_checklist = False
    for line in content.splitlines():
        if "Self-validation checklist" in line:
            in_checklist = True
            continue
        if in_checklist:
            stripped = line.strip()
            if stripped.startswith("- [ ]"):
                items.append(stripped[5:].strip())
            elif stripped.startswith("- [x]"):
                items.append(stripped[5:].strip())
            elif stripped.startswith("#") or (stripped == "" and items):
                break
    return items


def _sections_overlap(delivered: str, expected: str) -> bool:
    """Check if two section names refer to the same thing."""
    d = delivered.lower().strip()
    e = expected.lower().strip()
    return d == e or d in e or e in d
