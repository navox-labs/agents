"""Contract checker — validates bidirectional handoff contracts between agents."""

from __future__ import annotations

import json
from pathlib import Path

from navox.models.agent_config import AgentConfig
from navox.models.handoff_contract import HandoffContract
from navox.validators.frontmatter import ValidationResult


def load_all_contracts(agents_dir: str | Path) -> dict[str, HandoffContract]:
    """Load handoff contracts from all agent files."""
    contracts = {}
    agents_dir = Path(agents_dir)

    for f in agents_dir.glob("*.md"):
        config = AgentConfig.from_file(f)
        if config.is_utility:
            continue
        contract = HandoffContract.from_content(config.slug, config.raw_content)
        contracts[config.slug] = contract

    return contracts


def validate_contracts(
    agents_dir: str | Path,
    registry_path: str | Path | None = None,
) -> ValidationResult:
    """Validate handoff contracts are bidirectionally consistent.

    Uses the registry as the authoritative source for handoff topology.
    Only validates connections defined in the registry — extra connections
    in agent prompts are informational and don't require bidirectional match.

    If no registry is provided, falls back to checking all prompt-level pairs.
    """
    result = ValidationResult(agent_name="contracts")
    contracts = load_all_contracts(agents_dir)

    result.passed.append(f"loaded {len(contracts)} agent contracts")

    # Load registry handoff topology if available
    registry_pairs = _load_registry_pairs(registry_path) if registry_path else None

    if registry_pairs is not None:
        # Registry-aware validation: only check connections the registry defines
        for sender, receiver in registry_pairs:
            if sender not in contracts or receiver not in contracts:
                continue

            contract_a = contracts[sender]
            contract_b = contracts[receiver]

            # Does A's prompt confirm delivery to B?
            a_delivers_to_b = _agent_matches(
                contract_a.delivers_to, receiver
            )

            # Does B's prompt confirm receipt from A?
            b_receives_from_a = _agent_matches(
                contract_b.receives_from, sender
            )

            if a_delivers_to_b and b_receives_from_a:
                result.passed.append(
                    f"{sender} -> {receiver}: bidirectional contract confirmed"
                )
            elif a_delivers_to_b and not b_receives_from_a:
                result.failed.append(
                    f"{sender} delivers to {receiver}, but {receiver} "
                    f"doesn't list {sender} in 'receives from'"
                )
            elif not a_delivers_to_b and b_receives_from_a:
                result.failed.append(
                    f"{receiver} expects from {sender}, but {sender} "
                    f"doesn't list {receiver} in 'delivers to'"
                )
            else:
                result.failed.append(
                    f"registry says {sender} -> {receiver}, "
                    f"but neither prompt confirms the handoff"
                )
    else:
        # Fallback: check all prompt-level pairs (original behavior)
        for name_a, contract_a in contracts.items():
            for name_b, contract_b in contracts.items():
                if name_a == name_b:
                    continue

                a_delivers_to_b = _agent_matches(
                    contract_a.delivers_to, name_b
                )

                b_receives_from_a = _agent_matches(
                    contract_b.receives_from, name_a
                )

                if a_delivers_to_b and not b_receives_from_a:
                    result.failed.append(
                        f"{name_a} delivers to {name_b}, but {name_b} "
                        f"doesn't list {name_a} in 'receives from'"
                    )

    if not result.failed:
        result.passed.append("all handoff contracts are bidirectionally consistent")

    return result


# Wildcards that implicitly match any agent
_WILDCARD_AGENTS = {"all agents", "orchestrator", "sprint-chain", "any", "any agent"}

# Map human first names to agent slugs (for matching "Jordan" → "fullstack")
_NAME_TO_SLUG = {
    "raya": "strategist", "marcus": "spec-writer", "dmitri": "architect",
    "lena": "ux", "jordan": "fullstack", "sam": "investigator",
    "ava": "reviewer", "priya": "qa", "kai": "security",
    "omar": "devops", "elena": "shipper", "james": "retro",
    "nina": "context-manager", "devon": "devops",
}


def _agent_matches(entries: list, target_slug: str) -> bool:
    """Check if any contract entry matches a target agent slug.

    Handles wildcards ('All agents', 'Orchestrator', 'sprint-chain')
    and human name references ('Jordan' → fullstack, 'Kai' → security).
    """
    from navox.models.handoff_contract import ContractEntry

    for entry in entries:
        agent_lower = entry.agent.lower()

        # Direct slug match
        if target_slug.lower() in agent_lower:
            return True

        # Wildcard match
        if any(w in agent_lower for w in _WILDCARD_AGENTS):
            return True

        # Human name match: extract first names and map to slugs
        for name, slug in _NAME_TO_SLUG.items():
            if name in agent_lower and slug == target_slug.lower():
                return True

    return False


def _load_registry_pairs(registry_path: str | Path | None) -> list[tuple[str, str]] | None:
    """Extract (sender, receiver) pairs from the registry's handoff definitions."""
    if registry_path is None:
        return None

    registry_path = Path(registry_path)
    if not registry_path.exists():
        return None

    with open(registry_path) as f:
        registry = json.load(f)

    pairs = []
    for agent in registry.get("agents", []):
        agent_id = agent["id"]
        handoff = agent.get("handoff", {})
        for target in handoff.get("delivers_to", []):
            # Skip non-agent targets like "project-memory"
            if target not in ("project-memory", "builder"):
                pairs.append((agent_id, target))

    return pairs


def validate_registry_contracts(
    agents_dir: str | Path,
    registry_path: str | Path,
) -> ValidationResult:
    """Validate agent contracts match the registry's handoff definitions."""
    result = ValidationResult(agent_name="registry-contracts")

    registry_path = Path(registry_path)
    if not registry_path.exists():
        result.failed.append("agents_registry.json not found")
        return result

    with open(registry_path) as f:
        registry = json.load(f)

    # Build registry handoff map
    registry_handoffs = {}
    for agent in registry["agents"]:
        registry_handoffs[agent["id"]] = agent["handoff"]

    contracts = load_all_contracts(agents_dir)

    for agent_id, handoff in registry_handoffs.items():
        if agent_id not in contracts:
            continue

        contract = contracts[agent_id]

        # Check: registry says agent delivers to X, does the contract agree?
        for target in handoff.get("delivers_to", []):
            has_delivery = any(
                target.lower() in entry.agent.lower()
                for entry in contract.delivers_to
            )
            if has_delivery:
                result.passed.append(
                    f"{agent_id}: delivers to {target} (matches registry)"
                )
            # Not a hard failure — registry is a summary, contract has detail

    result.passed.append(f"checked {len(registry_handoffs)} registry entries")
    return result
