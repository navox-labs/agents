# Eval Task: Context Accuracy

## Input
"Save the current context — we're halfway through building the payment integration"

## Agent
context-manager (SAVE mode)

## Assertions
1. Snapshot must contain all 7 sections: Task, Decisions Made, Files Changed, Auth State, Next Steps, Open Questions, Blockers
2. Every decision must include rationale (not just the decision)
3. Next steps must be ordered by priority
4. File path must follow naming convention: YYYY-MM-DD-HH-MM-{task-slug}.md
5. Snapshot must be self-contained (readable without any other context)
6. Auth state section must be present (even if "N/A — no auth in scope")
7. Output must follow structured format with [MODE: CONTEXT-MANAGER/SAVE] header
