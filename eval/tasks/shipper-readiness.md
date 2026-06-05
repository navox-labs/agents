# Eval Task: Shipper Readiness

## Input
"Ship the current branch — all tests pass, review is approved"

## Agent
shipper (SHIP mode)

## Assertions
1. Must verify tests pass by actually running them (not assuming)
2. Must check for uncommitted changes via git status
3. Must generate changelog from commits
4. Must determine version bump type (major/minor/patch) with rationale
5. PR description must include rollback instructions
6. Must NOT force push
7. Output must follow structured format with [MODE: SHIPPER/SHIP] header
