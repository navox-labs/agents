# Team Handoff Chain

The full agent workflow from user request to ship. Each handoff is governed by a **handoff contract** — required sections the sending agent must include and the receiving agent validates before starting work.

```
USER ARRIVES (idea, problem, broken code, vague request — anything)
    ↓
ARCHITECT AGENT [MODE: DIAGNOSE]
  Reads request → identifies what's needed → recommends team + order
  Asks: "Deploy when done? (Y/N)"
  Flags bottlenecks before any agent starts work
    ↓
ARCHITECT AGENT [MODE: DESIGN]
  Produces: system design, auth model, security model, testing strategy
  Hands off to all agents with specific briefs
  ✓ Self-validates: all required sections present, no TBDs, build order numbered
    ↓
  ┌─────────────────────────────────────┐
  │                                     │
UI/UX AGENT [MODE: FLOW → WIREFRAME → DESIGN → SPEC]
  Expects from Architect: auth model,   │
  system overview, API contracts        │
  Produces: user flows, wireframes,     │
  component specs, design tokens,       │
  auth UX for all states                │
  ✓ Self-validates: all screens have    │
  5 states, auth flows complete         │
  Hands to: Full Stack Agent            │
                                        │
SECURITY AGENT [MODE: DESIGN-REVIEW]   │
  Expects from Architect: auth model,   │
  security model, API contracts         │
  Produces: numbered auth constraints,  │
  threat model for QA                   │
  ✓ Self-validates: constraints         │
  numbered, findings have severity      │
  │                                     │
  └─────────────────────────────────────┘
    ↓ (both complete before build starts)
FULL STACK AGENT [MODE: BUILD]
  Expects: Architect design + UX specs + Security constraints
  Produces: working code, unit tests, file manifest,
  auth implementation notes, run instructions
  ✓ Self-validates: all API endpoints built, auth constraints followed,
  file manifest complete, app starts locally
    ↓
LOCAL REVIEW AGENT [MODE: REVIEW]
  Expects from Fullstack: run instructions (command + port)
  Starts app locally → opens browser → takes screenshot
  Waits for human: LGTM | FEEDBACK | STOP
  Chain pauses here until human responds
    ↓
  ┌─────────────────────────────────────┐
  │                                     │
QA AGENT [MODE: TEST-RUN]              SECURITY AGENT [MODE: CODE-AUDIT]
  Expects: Fullstack code + run         Expects: Fullstack code + auth
  instructions + Architect API          implementation notes + file manifest
  contracts + UX user flows             Produces: vulnerability report
  Produces: bug report with             with file paths + severity + fix
  reproduction steps, auth test         ✓ Self-validates: all findings
  matrix, security-adjacent findings    have severity + location + fix
  ✓ Self-validates: auth flows          Hands to: Full Stack Agent
  tested, pass/fail counts exact        │
  Hands to: Full Stack Agent            │
  │                                     │
  └─────────────────────────────────────┘
    ↓ (Full Stack Agent fixes all findings)
SECURITY AGENT [MODE: LAUNCH-AUDIT]
  Expects: QA test results + own CODE-AUDIT findings
  Final auth + security sign-off
  Verdict: APPROVED | APPROVED WITH CONDITIONS | BLOCKED
  ✓ Self-validates: verdict is exactly one of the three values
    ↓
DEVOPS AGENT [MODE: DEPLOY]
  Expects: Fullstack code + run instructions + Security APPROVED verdict
  Will NOT deploy if verdict is BLOCKED
  Deploys frontend → Vercel
  Deploys backend → Cloudflare Workers
  Writes README with screenshot + live links
  ✓ Self-validates: endpoints return 200, no hardcoded secrets, README complete
    ↓
SHIP
  ✓ Live URL
  ✓ README with screenshot
  All from one prompt
```

---

## Handoff artifact summary

Each agent's handoff contract is defined in its prompt file (`.claude/agents/[agent].md`). The contracts specify:

| Agent | Delivers to | Key required sections |
|---|---|---|
| Architect | UX, Security, Fullstack | System overview, tech stack, data model, API contracts, auth model, build order |
| UX | Fullstack | User flows, screen inventory, auth UX specs, component specs, design tokens |
| Security | Fullstack, DevOps | Auth constraints (numbered), threat model, vulnerability report, launch verdict |
| Fullstack | Local Review, QA, Security | File manifest, auth notes, unit test results, run instructions, deviations |
| QA | Fullstack, Security | Test results summary, auth test matrix, bug report, security-adjacent findings |
| DevOps | Users | Live URLs, deployment verification, secrets list (names only), README |
| Local Review | Orchestrator | Verdict (LGTM/FEEDBACK/STOP), feedback notes |
