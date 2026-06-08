"""Runner — Layer 2 evaluation that runs agents via API and grades outputs.

Follows the PromptEvaluator pattern from the Anthropic course:
- LLM-as-judge grading with structured JSON output
- Prefill + stop_sequences for reliable JSON extraction
- Hybrid scoring: deterministic validation + model grading
- ThreadPoolExecutor for parallel evaluation
"""

from __future__ import annotations

import json
import concurrent.futures
from dataclasses import dataclass, field
from pathlib import Path

from navox.server import AgentServer
from navox.validators.output_validator import validate_output


@dataclass
class EvalResult:
    """Result of evaluating a single agent run."""

    agent_id: str
    mode: str
    task: str
    raw_output: str
    # Deterministic scores
    schema_score: float = 0.0  # 0-10: does output follow XML schema?
    completeness_score: float = 0.0  # 0-10: are all required sections present?
    # Model-graded scores (requires API)
    quality_score: float | None = None  # 0-10: is the content good?
    grader_reasoning: str = ""
    # Combined
    combined_score: float = 0.0
    details: dict = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.combined_score >= 7.0


@dataclass
class EvalTask:
    """A task to evaluate an agent against."""

    agent_id: str
    mode: str
    task: str
    expected_status: str = "COMPLETE"
    required_sections: list[str] = field(default_factory=list)
    extra_criteria: str = ""


class AgentEvaluator:
    """Evaluates agent outputs using deterministic checks + LLM-as-judge.

    Layer 1: Deterministic validation (no API calls)
    Layer 2: LLM-as-judge grading (requires API key)

    Usage:
        evaluator = AgentEvaluator(agents_dir=".claude/agents")

        # Layer 1 only (free, fast)
        result = evaluator.eval_deterministic(agent_id, mode, task, output)

        # Layer 1 + 2 (requires API)
        result = evaluator.eval_full(agent_id, mode, task, output)
    """

    GRADING_PROMPT = """You are an expert evaluator for AI agent outputs. Grade the following output on a scale of 1-10.

## Agent
{agent_id} in {mode} mode

## Task Given
{task}

## Output to Grade
{output}

## Extra Criteria
{extra_criteria}

## Scoring Guide
Score 1-3: Fails to address the task OR output is malformed/incomplete
Score 4-6: Addresses the task but has significant gaps or quality issues
Score 7-8: Good output that meets most requirements with minor gaps
Score 9-10: Excellent output that fully addresses the task with no gaps

## Important
- Grade ONLY on the listed criteria. Do not add your own extra requirements.
- ANY missing required section MUST result in score 5 or lower.
- Focus on substance, not style.

Return your evaluation as JSON with these fields:
- score: integer 1-10
- strengths: list of strings
- weaknesses: list of strings
- reasoning: one paragraph explaining your score"""

    def __init__(
        self,
        agents_dir: str | Path = ".claude/agents",
        registry_path: str | Path = "agents_registry.json",
        max_concurrent: int = 3,
    ):
        self.server = AgentServer(agents_dir, registry_path)
        self.max_concurrent = max_concurrent

    def eval_deterministic(
        self,
        agent_id: str,
        mode: str,
        task: str,
        output: str,
    ) -> EvalResult:
        """Layer 1: Score output using deterministic checks only (no API)."""
        result = EvalResult(
            agent_id=agent_id,
            mode=mode,
            task=task,
            raw_output=output,
        )

        # Schema validation
        validation = validate_output(output)
        schema_total = validation.total
        schema_passed = validation.score
        result.schema_score = (schema_passed / schema_total * 10) if schema_total > 0 else 0
        result.details["schema_passed"] = validation.passed
        result.details["schema_failed"] = validation.failed

        # Completeness: check required fields are non-empty
        from navox.models.output_schema import AgentOutput
        try:
            parsed = AgentOutput.from_xml(output)
            completeness_checks = {
                "agent": bool(parsed.agent),
                "mode": bool(parsed.mode),
                "status": bool(parsed.status),
                "deliverable": bool(parsed.deliverable) and len(parsed.deliverable) > 50,
                "verdict": bool(parsed.verdict),
                "handoff": bool(parsed.next_agent),
                "self_validation": len(parsed.self_validation) > 0,
            }
            passed = sum(completeness_checks.values())
            result.completeness_score = passed / len(completeness_checks) * 10
            result.details["completeness"] = completeness_checks
        except ValueError:
            result.completeness_score = 0

        # Combined (deterministic only)
        result.combined_score = (result.schema_score + result.completeness_score) / 2

        return result

    def eval_with_grader(
        self,
        agent_id: str,
        mode: str,
        task: str,
        output: str,
        extra_criteria: str = "",
    ) -> EvalResult:
        """Layer 2: Score with deterministic checks + LLM-as-judge grading."""
        # Start with deterministic
        result = self.eval_deterministic(agent_id, mode, task, output)

        # Add model grading
        grade = self._grade_by_model(agent_id, mode, task, output, extra_criteria)
        result.quality_score = grade.get("score", 0)
        result.grader_reasoning = grade.get("reasoning", "")
        result.details["grader"] = grade

        # Combined: average of all three scores
        result.combined_score = (
            result.schema_score
            + result.completeness_score
            + (result.quality_score or 0)
        ) / 3

        return result

    def eval_batch(
        self,
        tasks: list[EvalTask],
        use_grader: bool = False,
    ) -> list[EvalResult]:
        """Run evaluation on multiple tasks, optionally in parallel."""
        results = []

        if use_grader:
            # Parallel with ThreadPoolExecutor (Anthropic course pattern)
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_concurrent
            ) as executor:
                futures = {
                    executor.submit(
                        self._run_and_eval, task, use_grader
                    ): task
                    for task in tasks
                }
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())
        else:
            # Sequential for deterministic-only
            for task in tasks:
                results.append(self._run_and_eval(task, use_grader))

        return results

    def _run_and_eval(self, task: EvalTask, use_grader: bool) -> EvalResult:
        """Run an agent and evaluate its output."""
        try:
            run_result = self.server.run_agent(
                agent_id=task.agent_id,
                mode=task.mode,
                task=task.task,
            )
            output = run_result.raw_output
        except Exception as e:
            return EvalResult(
                agent_id=task.agent_id,
                mode=task.mode,
                task=task.task,
                raw_output=f"ERROR: {e}",
                combined_score=0,
            )

        if use_grader:
            return self.eval_with_grader(
                task.agent_id, task.mode, task.task,
                output, task.extra_criteria,
            )
        return self.eval_deterministic(
            task.agent_id, task.mode, task.task, output,
        )

    def _grade_by_model(
        self,
        agent_id: str,
        mode: str,
        task: str,
        output: str,
        extra_criteria: str = "",
    ) -> dict:
        """Use LLM-as-judge to grade output (Anthropic course pattern).

        Uses prefill + stop_sequences for reliable JSON extraction.
        """
        prompt = self.GRADING_PROMPT.format(
            agent_id=agent_id,
            mode=mode,
            task=task,
            output=output[:4000],  # Truncate to avoid token limits
            extra_criteria=extra_criteria or "No extra criteria.",
        )

        messages = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "```json"},  # Prefill
        ]

        try:
            response = self.server.chat(
                messages=messages,
                model="claude-haiku-4-5",  # Use cheapest model for grading
                max_tokens=1000,
                stop_sequences=["```"],
            )
            text = self.server.text_from_message(response)
            return json.loads(text.strip())
        except Exception as e:
            return {"score": 0, "reasoning": f"Grading failed: {e}"}


def format_eval_results(results: list[EvalResult]) -> str:
    """Format evaluation results as a human-readable report."""
    lines = [
        "=" * 50,
        "  AGENT EVALUATION REPORT",
        "=" * 50,
        "",
    ]

    for r in sorted(results, key=lambda x: x.combined_score, reverse=True):
        status = "PASS" if r.passed else "FAIL"
        scores = f"schema={r.schema_score:.1f} complete={r.completeness_score:.1f}"
        if r.quality_score is not None:
            scores += f" quality={r.quality_score:.1f}"
        lines.append(f"{status}  {r.agent_id} ({r.mode}) — {r.combined_score:.1f}/10 [{scores}]")

    passed = sum(1 for r in results if r.passed)
    lines.extend([
        "",
        f"  {passed}/{len(results)} passed (threshold: 7.0/10)",
        "=" * 50,
    ])

    return "\n".join(lines)
