---
name: hire-team
description: Onboard the full 15-agent engineering team and guide the user through the sprint cycle workflow.
---

# Hire the Full Engineering Team

You now have access to a team of 15 specialist AI agents covering the complete software sprint cycle — from idea validation to shipped code to retrospective. Each agent has deep expertise in their domain and they work together through structured handoff contracts.

## The Team

| Agent | Slash Command | What They Do |
|---|---|---|
| **Strategist** | `/strategist` | Product strategy, forcing questions, anti-sycophancy — validates ideas before any code |
| **Spec Writer** | `/spec-writer` | Turns vague intent into precise, buildable specs with acceptance criteria |
| **Architect** | `/architect` | System design, auth model, tech stack, team coordination |
| **UX** | `/ux` | User flows, wireframes, visual design, component specs |
| **Full Stack** | `/fullstack` | Production code, unit tests, auth implementation |
| **Investigator** | `/investigator` | Root-cause debugging — no fixes without diagnosis |
| **Reviewer** | `/reviewer` | Code review with 7-specialist parallel review army |
| **DevOps** | `/devops` | CI/CD pipelines, Docker, deployment, infrastructure |
| **Local Review** | *(auto, via /agency-run)* | Starts app locally, human checkpoint before QA |
| **QA** | `/qa` | Test plans, test execution, regression, auth flow testing |
| **Security** | `/security` | Threat modeling, auth audit, OWASP/STRIDE, launch sign-off |
| **Shipper** | `/shipper` | Release engineering — tests, changelog, version bump, PR |
| **Retro** | `/retro` | Sprint retrospectives, learnings, process improvement |
| **Context Manager** | `/context-manager` | Session persistence — pause and resume any sprint |
| **Installer** | *(auto-dispatched)* | Discover and install individual agents or templates |

## Not sure where to start?

- **New idea?** Run `/strategist DIAGNOSE` — the Strategist will challenge your assumptions before you build the wrong thing.
- **Know what to build?** Run `/architect DIAGNOSE` — the Architect will recommend which agents you need.
- **Bug to fix?** Run `/investigator INVESTIGATE` — root cause first, fix second.
- **Want the full team?** Run `/agency-run FULL <task>` — orchestrates the entire sprint.

## Sprint Modes

```
/agency-run FULL <task>    — Full sprint: Think → Plan → Build → Review → Test → Ship → Reflect
/agency-run QUICK <task>   — Quick sprint: Plan → Build → Test → Ship
/agency-run HOTFIX <task>  — Hotfix sprint: Investigate → Build → Ship
```

## Recommended Handoff Order (Full Sprint)

```
 1. /strategist DIAGNOSE   → Validate the idea with forcing questions
 2. /spec-writer WRITE     → Create precise spec with acceptance criteria
 3. /architect DESIGN      → Full system design + auth model
 4. /ux FLOW → DESIGN → SPEC          |
    /security DESIGN-REVIEW            |  (parallel)
 5. /fullstack BUILD       → Working code + unit tests
 6. Local Review           → Human checkpoint (LGTM / FEEDBACK / STOP)
 7. /reviewer REVIEW       → 7-specialist review army
 8. /qa TEST-RUN                       |
    /security CODE-AUDIT               |  (parallel)
 9. /shipper SHIP          → Tests → changelog → PR
10. /retro RETRO           → Capture learnings
```

Every agent has a `PLAN` mode — use it when you're unsure what that agent needs from you.

All agents are guided by the principles in ETHOS.md — read it to understand the team's shared values.

---

If this team saves you time, [star the repo](https://github.com/navox-labs/agents) — it helps other builders find it.
