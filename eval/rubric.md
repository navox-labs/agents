# Agent Quality Eval Rubric

Each agent is scored 0-10 against these checks. Minimum passing score: 8/10.

| # | Check | What to look for | Points |
|---|---|---|---|
| 1 | **Frontmatter completeness** | Has `name`, `description`, `model`, `tools` — all valid values | 1 |
| 2 | **Mode coverage** | Has PLAN mode + at least 2 operational modes | 1 |
| 3 | **Anti-hallucination** | Contains explicit "verify first" / "evidence required" instructions | 1 |
| 4 | **Handoff contracts** | Has `## Handoff Contract` with receive/deliver table + self-validation checklist | 1 |
| 5 | **Anti-sycophancy** | Does NOT contain agreement-first patterns; strategist/reviewer must have explicit anti-sycophancy rules | 1 |
| 6 | **Error handling** | Agent has instructions for when things go wrong (e.g., missing input, failed verification) | 1 |
| 7 | **Structured output** | Has `## Output Format` with a code block template showing exact output structure | 1 |
| 8 | **Scope boundaries** | Has `## What You Never Do` section with role-specific negations | 1 |
| 9 | **Preamble reference** | Identity section references ETHOS.md or includes its principles | 1 |
| 10 | **Memory integration** | Has `## Project memory` section with read/write commands and Current State + History format | 1 |

## Scoring Guide

- **10/10** — Exemplary agent. All checks pass. Ready for production.
- **8-9/10** — Strong agent. Minor gaps that don't affect function.
- **6-7/10** — Needs work. Missing structural elements.
- **Below 6** — Failing. Agent needs a rewrite to meet quality bar.

## Exceptions

- `installer.md` — utility agent, does not require modes, handoff contracts, or memory. Score N/A.
- `local-review.md` — single-mode agent, PLAN mode not required. Minimum 6/10.
