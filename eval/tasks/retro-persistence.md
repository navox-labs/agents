# Eval Task: Retro Persistence

## Input
"Run a retrospective on the last sprint — we built a user auth system"

## Agent
retro (RETRO mode)

## Assertions
1. Must include all 3 sections: What worked, What didn't work, Action items
2. "What worked" must have at least 3 specific items with evidence
3. "What didn't work" must have at least 3 specific items with root cause
4. Every "didn't work" item must have a corresponding action item
5. Action items must be specific, assigned to an agent, and prioritized
6. Must write to .claude/memory/retro.md
7. Must NOT use blame language (focus on process, not agents)
8. Output must follow structured format with [MODE: RETRO/RETRO] header
