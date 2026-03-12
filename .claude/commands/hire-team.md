---
name: hire-team
description: Onboard the full 5-agent engineering team — Architect, UX, Full Stack, QA, and Security — and guide the user through the recommended workflow.
---

# Hire the Full Engineering Team

You now have access to a team of 5 specialist AI engineers. Each agent has deep expertise in their domain and they work together through structured handoffs.

## The Team

| Agent | Slash Command | What They Do |
|---|---|---|
| **Architect** | `/architect` | System design, auth model, tech stack, team coordination |
| **UX** | `/ux` | User flows, wireframes, visual design, component specs |
| **Full Stack** | `/fullstack` | Production code, unit tests, auth implementation |
| **QA** | `/qa` | Test plans, test execution, regression, auth flow testing |
| **Security** | `/security` | Threat modeling, auth audit, code review, launch sign-off |

## Not sure where to start?

Run `/architect DIAGNOSE` — the Architect will read your request, figure out what you actually need, and tell you exactly which agents to use and in what order.

## Recommended Handoff Order

```
1. /architect DIAGNOSE  → Understand the problem, recommend team + order
2. /architect DESIGN    → Full system design + auth model
3. /ux FLOW → WIREFRAME → DESIGN → SPEC  ┐
   /security DESIGN-REVIEW                 ┘  (parallel)
4. /fullstack BUILD     → Working code + unit tests
5. /qa TEST-RUN                ┐
   /security CODE-AUDIT        ┘  (parallel)
6. /security LAUNCH-AUDIT → Final sign-off
7. Ship
```

Every agent has a `PLAN` mode — use it when you're unsure what that agent needs from you.
