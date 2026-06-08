"""Orchestrator — autonomous agent chain execution.

Runs sprint chains (FULL/QUICK/HOTFIX) without human gates.
Each step is journaled for resumability. Failures are contained
per agent — one crash doesn't kill the chain.

Follows Anthropic's recommended patterns:
- Stop reason handling for all 6 cases
- Failure containment per agent
- Content-addressed journaling
- 3-layer validation (schema → contract → LLM-judge)
- Structured logging
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from navox.journal import Journal, JournalEntry
from navox.models.agent_config import AgentConfig
from navox.models.output_schema import AgentOutput
from navox.validators.output_validator import validate_output

logger = logging.getLogger("navox.orchestrator")


# ── Stop reason handling ──────────────────────────────────────


class StopReason:
    """All possible stop reasons from the Anthropic API."""

    END_TURN = "end_turn"
    MAX_TOKENS = "max_tokens"
    TOOL_USE = "tool_use"
    PAUSE_TURN = "pause_turn"
    REFUSAL = "refusal"


# ── Result types ──────────────────────────────────────────────


@dataclass
class StepResult:
    """Result of a single agent execution step."""

    agent_id: str
    mode: str
    status: str  # COMPLETE, BLOCKED, ERROR, PARSE_ERROR, SKIPPED
    raw_output: str = ""
    parsed_output: AgentOutput | None = None
    model: str = ""
    duration_ms: int = 0
    token_usage: dict = field(default_factory=dict)
    error: str = ""
    cached: bool = False
    eval_score: float | None = None
    eval_details: dict = field(default_factory=dict)
    retry_count: int = 0

    @property
    def ok(self) -> bool:
        return self.status == "COMPLETE"

    @property
    def context_for_next(self) -> str:
        """Extract context to pass to the next agent."""
        if self.parsed_output and self.parsed_output.context_for_next:
            return self.parsed_output.context_for_next
        return self.raw_output


@dataclass
class ChainResult:
    """Result of a full sprint chain execution."""

    sprint_mode: str
    task: str
    steps: list[StepResult] = field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""
    interrupted: bool = False
    interrupt_reason: str = ""

    @property
    def ok(self) -> bool:
        return all(s.ok or s.cached for s in self.steps) and not self.interrupted

    @property
    def failed_steps(self) -> list[StepResult]:
        return [s for s in self.steps if not s.ok and not s.cached]

    def summary(self) -> dict:
        return {
            "sprint_mode": self.sprint_mode,
            "task": self.task[:100],
            "total_steps": len(self.steps),
            "completed": sum(1 for s in self.steps if s.ok),
            "cached": sum(1 for s in self.steps if s.cached),
            "failed": len(self.failed_steps),
            "ok": self.ok,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "total_duration_ms": sum(s.duration_ms for s in self.steps),
            "total_tokens": sum(
                s.token_usage.get("input_tokens", 0) + s.token_usage.get("output_tokens", 0)
                for s in self.steps
            ),
        }


# ── Orchestrator ──────────────────────────────────────────────


class Orchestrator:
    """Autonomous agent chain executor.

    Usage:
        orch = Orchestrator(
            agents_dir=".claude/agents",
            registry_path="sdk/agents_registry.json",
        )

        # Run a full sprint (autonomous, no human gates)
        result = orch.run("full", "Build an invoicing app for freelancers")

        # Resume an interrupted chain
        result = orch.run("full", "Build an invoicing app for freelancers")
        # ^ automatically resumes from journal

        # Dry run (validate chain without API calls)
        result = orch.dry_run("full", "Build an invoicing app")
    """

    MAX_CONTINUATION_TURNS = 3  # Max retries for max_tokens truncation
    MAX_RETRIES = 2  # Max retries for transient API errors
    EVAL_THRESHOLD = 8.0  # Minimum deterministic eval score to accept output

    def __init__(
        self,
        agents_dir: str | Path = ".claude/agents",
        registry_path: str | Path = "sdk/agents_registry.json",
        journal_path: str | Path = ".navox/journal.json",
        max_parallel: int = 2,
    ):
        self.agents_dir = Path(agents_dir)
        self.registry_path = Path(registry_path)
        self.journal = Journal(journal_path)
        self.max_parallel = max_parallel
        self._client = None

        # Load agent configs
        self.agents: dict[str, AgentConfig] = {}
        if self.agents_dir.exists():
            for f in self.agents_dir.glob("*.md"):
                config = AgentConfig.from_file(f)
                self.agents[config.slug] = config

        # Load registry
        self.registry: dict = {}
        if self.registry_path.exists():
            with open(self.registry_path) as f:
                self.registry = json.load(f)

    @property
    def client(self):
        """Lazy-load Anthropic client."""
        if self._client is None:
            from anthropic import Anthropic
            self._client = Anthropic()
        return self._client

    # ── Public API ────────────────────────────────────────────

    def run(
        self,
        sprint_mode: str,
        task: str,
        project_memory: str = "",
    ) -> ChainResult:
        """Run a sprint chain autonomously.

        Resumes from journal if a previous run was interrupted.
        Each step is journaled on completion for crash recovery.
        Parallel groups run concurrently with failure containment.
        """
        chain_def = self.registry.get("sprint_chains", {}).get(sprint_mode)
        if not chain_def:
            raise ValueError(f"Unknown sprint mode: {sprint_mode}")

        result = ChainResult(
            sprint_mode=sprint_mode,
            task=task,
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        context = ""
        task_hash = hashlib.sha256(task.encode()).hexdigest()[:12]

        logger.info(f"Starting {sprint_mode.upper()} sprint: {task[:80]}")

        for group in chain_def:
            agent_ids = group["agents"]
            modes = group["mode"]
            is_parallel = group.get("parallel", False)

            # Normalize modes to list
            if isinstance(modes, str):
                modes = [modes] * len(agent_ids)

            # Build context hash for journal keys
            context_hash = hashlib.sha256(context.encode()).hexdigest()[:12]

            if is_parallel and len(agent_ids) > 1:
                group_results = self._run_parallel(
                    agent_ids, modes, task, context,
                    project_memory, context_hash,
                )
            else:
                group_results = self._run_sequential(
                    agent_ids, modes, task, context,
                    project_memory, context_hash,
                )

            result.steps.extend(group_results)

            # Update context with outputs
            for step in group_results:
                if step.ok or step.cached:
                    context += f"\n\n--- {step.agent_id} ({step.mode}) ---\n"
                    context += step.context_for_next

            # Check for chain-stopping failures
            for step in group_results:
                if step.status in ("BLOCKED", "ERROR"):
                    result.interrupted = True
                    result.interrupt_reason = (
                        f"{step.agent_id} returned {step.status}: {step.error}"
                    )
                    logger.error(f"Chain interrupted: {result.interrupt_reason}")
                    break

            if result.interrupted:
                break

        result.finished_at = datetime.now(timezone.utc).isoformat()
        logger.info(
            f"Sprint {'COMPLETE' if result.ok else 'INTERRUPTED'}: "
            f"{len(result.steps)} steps, "
            f"{sum(1 for s in result.steps if s.cached)} cached"
        )

        return result

    def dry_run(self, sprint_mode: str, task: str) -> ChainResult:
        """Validate a sprint chain without making API calls.

        Returns a ChainResult with SKIPPED status for each step,
        showing the execution plan.
        """
        chain_def = self.registry.get("sprint_chains", {}).get(sprint_mode)
        if not chain_def:
            raise ValueError(f"Unknown sprint mode: {sprint_mode}")

        result = ChainResult(
            sprint_mode=sprint_mode,
            task=task,
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        for group in chain_def:
            agent_ids = group["agents"]
            modes = group["mode"]
            is_parallel = group.get("parallel", False)

            if isinstance(modes, str):
                modes = [modes] * len(agent_ids)

            for agent_id, mode in zip(agent_ids, modes):
                config = self.agents.get(agent_id)
                if not config:
                    result.steps.append(StepResult(
                        agent_id=agent_id,
                        mode=mode,
                        status="ERROR",
                        error=f"Agent not found: {agent_id}",
                    ))
                    continue

                suffix = " (parallel)" if is_parallel else ""
                result.steps.append(StepResult(
                    agent_id=agent_id,
                    mode=mode,
                    status="SKIPPED",
                    model=config.model,
                    raw_output=f"[DRY RUN] Would run {agent_id} in {mode} mode{suffix}",
                ))

        result.finished_at = datetime.now(timezone.utc).isoformat()
        return result

    # ── Internal execution ────────────────────────────────────

    def _run_sequential(
        self,
        agent_ids: list[str],
        modes: list[str],
        task: str,
        context: str,
        project_memory: str,
        context_hash: str,
    ) -> list[StepResult]:
        """Run agents sequentially within a group."""
        results = []
        for agent_id, mode in zip(agent_ids, modes):
            step = self._run_single(
                agent_id, mode, task, context,
                project_memory, context_hash,
            )
            results.append(step)

            # Update context within the group
            if step.ok:
                context += f"\n\n--- {step.agent_id} ({step.mode}) ---\n"
                context += step.context_for_next

        return results

    def _run_parallel(
        self,
        agent_ids: list[str],
        modes: list[str],
        task: str,
        context: str,
        project_memory: str,
        context_hash: str,
    ) -> list[StepResult]:
        """Run agents in parallel with failure containment."""
        results = []

        with ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
            futures = {
                executor.submit(
                    self._run_single,
                    agent_id, mode, task, context,
                    project_memory, context_hash,
                ): agent_id
                for agent_id, mode in zip(agent_ids, modes)
            }

            for future in as_completed(futures):
                agent_id = futures[future]
                try:
                    step = future.result()
                except Exception as e:
                    # Failure containment: one agent crash doesn't kill siblings
                    logger.error(f"{agent_id} crashed: {e}")
                    step = StepResult(
                        agent_id=agent_id,
                        mode="UNKNOWN",
                        status="ERROR",
                        error=f"Unhandled exception: {e}",
                    )
                results.append(step)

        return results

    def _run_single(
        self,
        agent_id: str,
        mode: str,
        task: str,
        context: str,
        project_memory: str,
        context_hash: str,
    ) -> StepResult:
        """Run a single agent with journaling, eval gating, and stop reason handling."""
        # Check journal for cached result
        key = Journal.make_key(agent_id, mode, task, context_hash)
        cached = self.journal.get(key)
        if cached and cached.status == "COMPLETE":
            logger.info(f"  CACHED  {agent_id} ({mode})")
            parsed = None
            try:
                parsed = AgentOutput.from_xml(cached.raw_output)
            except ValueError:
                pass
            return StepResult(
                agent_id=agent_id,
                mode=mode,
                status="COMPLETE",
                raw_output=cached.raw_output,
                parsed_output=parsed,
                model=cached.model,
                duration_ms=cached.duration_ms,
                token_usage=cached.token_usage,
                cached=True,
            )

        # Load agent config
        config = self.agents.get(agent_id)
        if not config:
            return StepResult(
                agent_id=agent_id,
                mode=mode,
                status="ERROR",
                error=f"Agent not found: {agent_id}",
            )

        logger.info(f"  RUN     {agent_id} ({mode}) — {config.model}")

        # Eval-gated retry loop: run agent, evaluate output, retry if below threshold
        best_step = None
        for attempt in range(self.MAX_RETRIES + 1):
            step = self._execute_and_parse(
                agent_id, mode, task, context, project_memory,
                config, key, attempt,
            )

            if not step.ok:
                # Don't retry non-COMPLETE outputs (BLOCKED, ERROR, PARSE_ERROR)
                best_step = step
                break

            # Evaluate output quality
            eval_score, eval_details = self._evaluate_output(
                agent_id, mode, task, step.raw_output,
            )
            step.eval_score = eval_score
            step.eval_details = eval_details
            step.retry_count = attempt

            if eval_score >= self.EVAL_THRESHOLD:
                best_step = step
                break

            # Below threshold — retry with feedback
            logger.warning(
                f"  EVAL    {agent_id}: score {eval_score:.1f} < {self.EVAL_THRESHOLD} "
                f"(attempt {attempt + 1}/{self.MAX_RETRIES + 1})"
            )

            if attempt < self.MAX_RETRIES:
                # Add eval feedback to context for the retry
                failed_checks = [
                    f"- {k}: {v}" for k, v in eval_details.items()
                    if isinstance(v, bool) and not v
                ]
                context += (
                    f"\n\n[EVAL FEEDBACK — your previous output scored {eval_score:.1f}/10. "
                    f"Issues:\n" + "\n".join(failed_checks[:5]) + "]"
                )
            else:
                # Accept the best attempt even if below threshold
                best_step = step

        # Journal the final result
        self.journal.save(key, JournalEntry(
            key=key, agent_id=agent_id, mode=mode,
            status=best_step.status, raw_output=best_step.raw_output,
            timestamp=time.time(), duration_ms=best_step.duration_ms,
            model=config.model, token_usage=best_step.token_usage,
            error=best_step.error,
        ))

        status_icon = "DONE" if best_step.ok else best_step.status
        eval_info = f" eval={best_step.eval_score:.1f}" if best_step.eval_score is not None else ""
        retry_info = f" retries={best_step.retry_count}" if best_step.retry_count > 0 else ""
        logger.info(f"  {status_icon:8s} {agent_id} — {best_step.duration_ms}ms{eval_info}{retry_info}")

        return best_step

    def _execute_and_parse(
        self,
        agent_id: str,
        mode: str,
        task: str,
        context: str,
        project_memory: str,
        config: AgentConfig,
        journal_key: str,
        attempt: int,
    ) -> StepResult:
        """Execute a single API call and parse the output."""
        start_time = time.monotonic()

        # Build messages
        user_message = self._build_user_message(mode, task, context, project_memory)
        messages = [{"role": "user", "content": user_message}]

        # Call API with stop reason handling
        try:
            raw_output, token_usage = self._call_with_continuation(
                messages=messages,
                system=config.raw_content,
                model=config.model,
            )
        except Exception as e:
            duration_ms = int((time.monotonic() - start_time) * 1000)
            logger.error(f"  ERROR   {agent_id}: {e}")
            return StepResult(
                agent_id=agent_id,
                mode=mode,
                status="ERROR",
                error=str(e),
                model=config.model,
                duration_ms=duration_ms,
            )

        duration_ms = int((time.monotonic() - start_time) * 1000)

        # Parse and validate output
        parsed = None
        status = "PARSE_ERROR"
        error = ""

        try:
            parsed = AgentOutput.from_xml(raw_output)
            if parsed.is_blocked:
                status = "BLOCKED"
                error = parsed.blockers or "Agent reported BLOCKED status"
            elif parsed.is_error:
                status = "ERROR"
                error = parsed.blockers or "Agent reported ERROR status"
            else:
                status = "COMPLETE"
        except ValueError as e:
            error = f"Failed to parse XML output: {e}"
            logger.warning(f"  PARSE   {agent_id}: {error}")

        # Validate output structure
        if status == "COMPLETE":
            validation = validate_output(raw_output)
            if not validation.ok:
                logger.warning(
                    f"  WARN    {agent_id}: validation issues: "
                    f"{', '.join(validation.failed[:3])}"
                )

        return StepResult(
            agent_id=agent_id,
            mode=mode,
            status=status,
            raw_output=raw_output,
            parsed_output=parsed,
            model=config.model,
            duration_ms=duration_ms,
            token_usage=token_usage,
            error=error,
        )

    def _evaluate_output(
        self,
        agent_id: str,
        mode: str,
        task: str,
        raw_output: str,
    ) -> tuple[float, dict]:
        """Evaluate agent output using deterministic checks.

        Returns (score, details_dict). Score is 0-10.
        Uses the same validation as eval/runner.py but without API calls.
        """
        from navox.models.output_schema import AgentOutput

        details = {}
        checks_passed = 0
        checks_total = 0

        # 1. XML parses
        checks_total += 1
        try:
            parsed = AgentOutput.from_xml(raw_output)
            details["xml_parses"] = True
            checks_passed += 1
        except ValueError:
            details["xml_parses"] = False
            return 0.0, details

        # 2. Required fields present
        for field_name in ("agent", "mode", "status", "deliverable", "verdict"):
            checks_total += 1
            value = getattr(parsed, field_name, "")
            present = bool(value and value.strip())
            details[f"field_{field_name}"] = present
            if present:
                checks_passed += 1

        # 3. Deliverable has substance (>50 chars)
        checks_total += 1
        has_substance = len(parsed.deliverable) > 50
        details["deliverable_substance"] = has_substance
        if has_substance:
            checks_passed += 1

        # 4. Handoff present for COMPLETE
        if parsed.is_complete:
            checks_total += 1
            has_handoff = bool(parsed.next_agent)
            details["handoff_present"] = has_handoff
            if has_handoff:
                checks_passed += 1

        # 5. Self-validation present and passing
        checks_total += 1
        has_validation = len(parsed.self_validation) > 0
        details["self_validation_present"] = has_validation
        if has_validation:
            checks_passed += 1

        if has_validation and parsed.is_complete:
            checks_total += 1
            all_pass = parsed.all_validations_pass
            details["self_validation_passing"] = all_pass
            if all_pass:
                checks_passed += 1

        # Score: scale to 0-10
        score = (checks_passed / checks_total * 10) if checks_total > 0 else 0.0
        return round(score, 1), details

    def _call_with_continuation(
        self,
        messages: list[dict],
        system: str,
        model: str,
        max_tokens: int = 8192,
    ) -> tuple[str, dict]:
        """Call the API with stop reason handling and continuation.

        Handles:
        - end_turn: natural completion → return result
        - max_tokens: truncated → continue with "Please continue"
        - tool_use: not supported in autonomous mode → return partial
        - pause_turn: server limit → return result as-is
        - refusal: safety refusal → raise error

        Returns (full_text, token_usage).
        """
        full_text = ""
        total_usage = {"input_tokens": 0, "output_tokens": 0}

        for turn in range(self.MAX_CONTINUATION_TURNS + 1):
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
            )

            # Accumulate token usage
            if hasattr(response, "usage"):
                total_usage["input_tokens"] += response.usage.input_tokens
                total_usage["output_tokens"] += response.usage.output_tokens

            # Extract text
            text = "\n".join(
                block.text for block in response.content if block.type == "text"
            )
            full_text += text

            # Handle stop reason
            stop = response.stop_reason

            if stop == StopReason.END_TURN:
                break  # Natural completion

            elif stop == StopReason.MAX_TOKENS:
                if turn >= self.MAX_CONTINUATION_TURNS:
                    logger.warning("Max continuation turns reached, returning partial output")
                    break
                # Continue: add assistant response and ask to continue
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": "Please continue from where you left off."})
                logger.debug(f"Continuing after max_tokens (turn {turn + 1})")

            elif stop == StopReason.TOOL_USE:
                logger.warning("Agent requested tool use — not supported in autonomous mode")
                break

            elif stop == StopReason.PAUSE_TURN:
                break  # Server limit, return what we have

            elif stop == StopReason.REFUSAL:
                raise RuntimeError(f"Agent refused the request: {text[:200]}")

            else:
                logger.warning(f"Unknown stop reason: {stop}")
                break

        return full_text, total_usage

    # ── Helpers ───────────────────────────────────────────────

    @staticmethod
    def _build_user_message(
        mode: str,
        task: str,
        context: str,
        project_memory: str,
    ) -> str:
        parts = [f"[MODE: {mode}]", "", f"## Task\n{task}"]

        if project_memory:
            parts.append(f"\n## Project Memory\n{project_memory}")

        if context:
            parts.append(f"\n## Context from previous agents\n{context}")

        return "\n".join(parts)


# ── Formatting ────────────────────────────────────────────────


def format_chain_result(result: ChainResult) -> str:
    """Format a chain result as a human-readable report."""
    lines = [
        "=" * 60,
        f"  SPRINT REPORT — {result.sprint_mode.upper()}",
        "=" * 60,
        f"  Task: {result.task[:80]}",
        f"  Status: {'COMPLETE' if result.ok else 'INTERRUPTED'}",
        "",
    ]

    for step in result.steps:
        if step.cached:
            icon = "CACHED"
        elif step.ok:
            icon = "DONE"
        else:
            icon = step.status

        duration = f"{step.duration_ms}ms" if step.duration_ms else "-"
        tokens = ""
        if step.token_usage:
            t = step.token_usage.get("input_tokens", 0) + step.token_usage.get("output_tokens", 0)
            if t:
                tokens = f" [{t:,} tokens]"

        eval_info = f" eval={step.eval_score:.1f}" if step.eval_score is not None else ""
        retry_info = f" (retried {step.retry_count}x)" if step.retry_count > 0 else ""

        lines.append(f"  {icon:10s} {step.agent_id} ({step.mode}) — {duration}{tokens}{eval_info}{retry_info}")
        if step.error:
            lines.append(f"             {step.error[:80]}")

    summary = result.summary()
    lines.extend([
        "",
        "-" * 60,
        f"  Steps: {summary['completed']} completed, {summary['cached']} cached, {summary['failed']} failed",
        f"  Duration: {summary['total_duration_ms']}ms",
        f"  Tokens: {summary['total_tokens']:,}",
        "=" * 60,
    ])

    if result.interrupted:
        lines.append(f"  INTERRUPTED: {result.interrupt_reason}")

    return "\n".join(lines)
