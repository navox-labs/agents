# Eval Task: Investigator Discipline

## Input
"Users are getting 403 errors when trying to access their dashboard after login"

## Agent
investigator (INVESTIGATE mode)

## Assertions
1. Must attempt reproduction before diagnosis
2. Must follow 4-step sequence: reproduce, isolate, trace, identify
3. Investigation report must appear BEFORE any fix proposal
4. Root cause must include file:line evidence (or explanation of why it cannot)
5. Must include regression risk assessment
6. Must include prevention recommendation
7. Must NOT contain "try this and see" or equivalent guessing language
8. Output must follow structured format with [MODE: INVESTIGATOR/INVESTIGATE] header
