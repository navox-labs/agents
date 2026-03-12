# Team Handoff Chain

The full agent workflow from user request to ship.

```
USER ARRIVES (idea, problem, broken code, vague request — anything)
    ↓
ARCHITECT AGENT [MODE: DIAGNOSE]
  Reads request → identifies what's needed → recommends team + order
  Flags bottlenecks before any agent starts work
    ↓
ARCHITECT AGENT [MODE: DESIGN]
  Produces: system design, auth model, security model, testing strategy
  Hands off to all agents with specific briefs
    ↓
  ┌─────────────────────────────────────┐
  │                                     │
UI/UX AGENT [MODE: FLOW → WIREFRAME → DESIGN → SPEC]
  Produces: user flows, wireframes,     │
  visual design, component specs,       │
  auth UX for all states                │
  Hands to: Full Stack Agent            │
                                        │
SECURITY AGENT [MODE: DESIGN-REVIEW]   │
  Reviews auth model + security design  │
  Produces: auth constraints for        │
  Full Stack Agent                      │
  │                                     │
  └─────────────────────────────────────┘
    ↓ (both complete before build starts)
FULL STACK AGENT [MODE: BUILD]
  Receives: Arch doc + UI/UX specs + Security auth constraints
  Produces: working code + unit tests + auth implementation
    ↓
  ┌─────────────────────────────────────┐
  │                                     │
QA AGENT [MODE: TEST-RUN]              SECURITY AGENT [MODE: CODE-AUDIT]
  Tests all flows including auth        Audits auth implementation + code
  Produces: bug report                  Produces: vulnerability report
  Hands to: Full Stack Agent            Hands to: Full Stack Agent
  │                                     │
  └─────────────────────────────────────┘
    ↓ (Full Stack Agent fixes all findings)
SECURITY AGENT [MODE: LAUNCH-AUDIT]
  Final auth + security sign-off
  Verdict: APPROVED | APPROVED WITH CONDITIONS | BLOCKED
    ↓
SHIP
```
