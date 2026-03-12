# Agent Modes Reference

Every agent supports a `PLAN` mode as its entry point for when you're unsure what you need. Below is the full list of modes per agent.

---

## Architect (`/architect`)

| Mode | Description |
|---|---|
| **PLAN** | Turn a vague idea into a clear architectural starting point before committing to a full design |
| **DIAGNOSE** | Default entry point — read any request and recommend which agents are needed, in what order |
| **DESIGN** | Full system design: tech stack, data model, API contracts, auth model, security model, caching, scaling |
| **REVIEW-DESIGN** | Audit an existing architecture for structural risks, scalability concerns, and auth gaps |

---

## UX (`/ux`)

| Mode | Description |
|---|---|
| **PLAN** | Assess what UX/UI work is needed and map out the design sequence |
| **FLOW** | Map user journeys, personas, navigation architecture, and auth flows before any screens |
| **WIREFRAME** | Low-fidelity layout and hierarchy for every screen including all states |
| **DESIGN** | Full visual design: design tokens, component library, screen designs, accessibility |
| **SPEC** | Developer-ready component specifications for the Full Stack Agent |

---

## Full Stack (`/fullstack`)

| Mode | Description |
|---|---|
| **PLAN** | Turn an idea into an actionable engineering brief with stack, structure, and build order |
| **BUILD** | Build a feature with complete working code, unit tests, and auth implementation |
| **REFACTOR** | Improve existing code with auth anti-pattern review and updated tests |
| **DEBUG** | Fix a reported issue with root cause, fix, and regression test |
| **REVIEW** | Code audit focused on quality, correctness, and auth security |

---

## QA (`/qa`)

| Mode | Description |
|---|---|
| **PLAN** | Assess testing situation and produce a clear testing strategy |
| **TEST-PLAN** | Create a testing plan with unit test checklist, integration cases, and auth test matrix |
| **TEST-RUN** | Execute tests and report findings with severity and reproduction steps |
| **REGRESSION** | Verify fixes didn't break anything, with auth flow re-validation |

---

## Security (`/security`)

| Mode | Description |
|---|---|
| **PLAN** | Assess security risks and produce a strategy before any audit begins |
| **DESIGN-REVIEW** | Review the Architect's auth and security model before build starts |
| **CODE-AUDIT** | Audit delivered code with auth as the primary surface |
| **LAUNCH-AUDIT** | Final security sign-off with pass/fail checklist and launch verdict |
| **INCIDENT** | Security incident response: containment, scope, root cause, remediation |
