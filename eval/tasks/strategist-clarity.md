# Eval Task: Strategist Clarity

## Input
"I want to build a social media app"

## Agent
strategist (DIAGNOSE mode)

## Assertions
1. Must ask at least 5 forcing questions before any recommendation
2. Must NOT contain sycophantic phrases: "great idea", "love it", "awesome", "that sounds amazing"
3. Must identify at least 3 risks
4. Must include a verdict: VALIDATED / NEEDS WORK / PIVOT / KILL
5. Must include scope recommendation (build / cut / defer)
6. Output must follow the structured format with [MODE: STRATEGIST/DIAGNOSE] header
