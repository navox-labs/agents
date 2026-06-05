# Eval Task: Reviewer Thoroughness

## Input
A diff that adds a new API endpoint with database queries and user authentication.

## Agent
reviewer (REVIEW mode)

## Assertions
1. Must cover all 7 specialist areas: security, performance, maintainability, API contracts, data integrity, test coverage, error handling
2. Each specialist must output PASS / WARN / BLOCK with evidence
3. Every finding must cite file:line
4. Findings must be severity-ranked: BLOCK > WARN > MINOR
5. Must include a verdict: APPROVE / REQUEST CHANGES / BLOCK
6. BLOCK findings must include specific fix instructions
7. Output must follow structured format with [MODE: REVIEWER/REVIEW] header
