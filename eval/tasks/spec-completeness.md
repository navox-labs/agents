# Eval Task: Spec Completeness

## Input
"Build a user authentication system with email/password and Google OAuth"

## Agent
spec-writer (WRITE mode)

## Assertions
1. Output must contain all 7 sections: Problem statement, Success criteria, Technical constraints, Out of scope, Acceptance criteria, Edge cases, Dependencies
2. Success criteria must have at least 3 measurable outcomes
3. Out of scope must have at least 3 explicit exclusions
4. Edge cases must cover: empty state, error state, boundary, concurrent access, permissions
5. No vague language ("fast", "intuitive", "robust") without metrics
6. Acceptance criteria must be in Given/When/Then format
7. Output must follow the structured format with [MODE: SPEC-WRITER/WRITE] header
