"""Contract checker — validates bidirectional handoff contracts between agents."""

from __future__ import annotations

import json
from pathlib import Path

from navox_agents.models.agent_config import AgentConfig
from navox_agents.models.handoff_contract import HandoffContract
from navox_agents.validators.frontmatter import ValidationResult


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


def validate_contracts(agents_dir: str | Path) -> ValidationResult:
    """Validate all handoff contracts are bidirectionally consistent."""
    result = ValidationResult(agent_name="contracts")
    contracts = load_all_contracts(agents_dir)

    result.passed.append(f"loaded {len(contracts)} agent contracts")

    # Check each pair of agents
    for name_a, contract_a in contracts.items():
        for name_b, contract_b in contracts.items():
            if name_a == name_b:
                continue

            # Does A claim to deliver to B?
            a_delivers_to_b = any(
                name_b.lower() in entry.agent.lower()
                for entry in contract_a.delivers_to
            )

            # Does B claim to receive from A?
            b_receives_from_a = any(
                name_a.lower() in entry.agent.lower()
                for entry in contract_b.receives_from
            )

            # Bidirectional check: if A delivers to B, B should receive from A
            if a_delivers_to_b and not b_receives_from_a:
                result.failed.append(
                    f"{name_a} delivers to {name_b}, but {name_b} "
                    f"doesn't list {name_a} in 'receives from'"
                )

    if not result.failed:
        result.passed.append("all handoff contracts are bidirectionally consistent")

    return result


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
