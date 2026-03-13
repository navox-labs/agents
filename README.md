# agents

**A specialist engineering team for Claude Code.**  
5 AI agents. No platform. No login. No data stored. Your code never leaves your machine.

```bash
# Install globally — works in every project
cp -r .claude/agents/* ~/.claude/agents/
cp -r .claude/commands/* ~/.claude/commands/
```

Not sure where to start? Run this first:

```
/hire-team
```

---

## The Team

| Agent | Agent Name | What it does |
|---|---|---|
| 🏗️ Architect | `architect` | System design, auth model, scalability, caching, handoff briefs |
| 🎨 UI/UX | `ux` | User flows, wireframes, visual design, component specs |
| ⚙️ Full Stack | `fullstack` | Builds features, writes unit tests, refactors, debugs |
| 🧪 QA Engineer | `qa` | Test plans, test runs, regression, auth flow coverage |
| 🔐 Security | `security` | Design review, code audit, launch sign-off, incident response |

---

## Why this exists

Every AI coding tool today is a plugin you install or a platform you log into.  
This is neither.

These are Claude Code subagents — markdown files that live in your project or globally in `~/.claude/agents/`. They run entirely inside your Claude Code session. No API calls to a third-party server. No account. No telemetry. Just specialists you can hire from the terminal.

```
architect design a multi-tenant SaaS with JWT auth and Redis caching
```
```
security plan — I'm about to build auth for a fintech app, where do I start?
```
```
qa test-run — here's the code, find everything that can break
```

---

## Install

**Global install** — available in every project:
```bash
git clone https://github.com/navox-labs/agents.git
cp -r agents/.claude/agents/* ~/.claude/agents/
```

**Project install** — scoped to one repo:
```bash
cp -r agents/.claude/agents/* your-project/.claude/agents/
```

---

## How each agent works

Every agent has a `PLAN` mode for when you're not sure what you need.  
Just describe your situation and the agent tells you what to do next.

### 🏗️ Architect

The first agent to talk to on any new project. Starts with `DIAGNOSE` if you don't know which agents you need.

```
Modes:
  PLAN          — not sure where to start architecturally
  DIAGNOSE      — don't know which agents you need, describe the situation
  DESIGN        — full system design: stack, data model, API contracts, auth model,
                  security model, caching strategy, scalability plan, testing strategy
  REVIEW-DESIGN — audit an existing architecture before it breaks in production
```

The Architect's output is the single source of truth every other agent inherits from.  
Auth model, security constraints, testing strategy — all defined here before a line of code is written.

---

### 🎨 UI/UX Agent

Covers the full design process. Delivers specs the Full Stack agent can build directly — no design-to-engineering translation required.

```
Modes:
  PLAN       — not sure what UX work you need
  FLOW       — user journey mapping before any screens
  WIREFRAME  — layout and hierarchy per screen, all states
  DESIGN     — full visual design + design system + component library
  SPEC       — developer-ready specs: props, states, interactions, accessibility
```

Auth UX is fully covered — login, signup, error states, session expiry, recovery flows, password reset. Every state, not just the happy path.

---

### ⚙️ Full Stack Engineer

Builds features from the Architect's brief and UI/UX specs. Unit tests are mandatory — not optional.

```
Modes:
  PLAN      — not sure what to build or where to start
  BUILD     — build a feature: complete code + unit tests + decisions made
  REFACTOR  — improve existing code + update tests
  DEBUG     — diagnose root cause + fix + test that would have caught it
  REVIEW    — code audit: Critical / Important / Minor with fixes for all Critical
```

Default stack when nothing is specified: Next.js + TypeScript + Tailwind + PostgreSQL (Prisma) + Supabase Auth + Redis + Vercel.  
State your stack and it follows it. Override any default explicitly.

---

### 🧪 QA Engineer

Tests what was specified and what wasn't. Auth flows get extra scrutiny — most failures start there.

```
Modes:
  PLAN        — not sure what testing you need or where to start
  TEST-PLAN   — create a testing plan from the Architect's design and UX flows
  TEST-RUN    — execute tests, report findings by severity, hand off issues
  REGRESSION  — verify a fix didn't break something else, especially auth
```

Every finding includes: what failed, how to reproduce, expected vs actual, severity.  
No vague reports. No passing tests without a clear success condition.

---

### 🔐 Security Engineer

Active throughout the build — not just at launch. Auth is always the highest-priority surface.

```
Modes:
  PLAN           — not sure what your security risks are
  DESIGN-REVIEW  — review auth and security model before build starts
  CODE-AUDIT     — audit Full Stack Agent's code, auth implementation first
  LAUNCH-AUDIT   — final sign-off: APPROVED / APPROVED WITH CONDITIONS / BLOCKED
  INCIDENT       — containment, scope, root cause, remediation
```

Launch audit covers the full OWASP Top 10, auth security, dependency CVEs, secrets management, rate limiting, and information leakage. Nothing ships without a verdict.

---

## The handoff chain

```
You arrive with anything — idea, broken code, vague request
        ↓
architect DIAGNOSE      — figures out what you need and who to hire
        ↓
architect DESIGN        — system design, auth model, security model, testing strategy
        ↓
        ├── ux FLOW → WIREFRAME → DESIGN → SPEC    (runs in parallel)
        └── security DESIGN-REVIEW                  (runs in parallel)
        ↓
fullstack BUILD         — code + unit tests, follows arch doc and UX specs
        ↓
        ├── qa TEST-RUN           (runs in parallel)
        └── security CODE-AUDIT   (runs in parallel)
        ↓
fullstack               — fixes all findings
        ↓
security LAUNCH-AUDIT   — final verdict
        ↓
ship
```

---

## Auth ownership

Every agent has a defined slice. Nothing falls through the gap.

| Auth concern | Owner |
|---|---|
| Auth strategy and model | Architect |
| Auth data model (users, sessions, roles) | Architect |
| Login / signup / recovery UX | UI/UX Agent |
| Auth component design + all states | UI/UX Agent |
| Auth implementation (code) | Full Stack Agent |
| Auth unit tests + edge cases | Full Stack Agent |
| Auth flow testing (happy + unhappy paths) | QA Agent |
| Auth security constraints | Security Agent |
| Auth code audit | Security Agent |
| Auth launch sign-off | Security Agent |

---

## Hire one or hire all

These agents are independent. You don't need the full team.

- Building a new product? Start with `architect DIAGNOSE`
- Already have code, want it tested? `qa PLAN`
- Shipping next week and worried about security? `security LAUNCH-AUDIT`
- Something's broken and you don't know why? `fullstack DEBUG`
- Not sure which agent you need? `architect DIAGNOSE` — describe your situation

---

## What this is not

- Not a web platform. There's no dashboard to log into.
- Not a SaaS. There's no subscription or usage limit.
- Not a plugin. There's nothing to configure in your editor.
- Not storing your data. Your code runs through Claude Code locally.

This is a set of markdown files with carefully engineered system prompts.  
The intelligence is in the prompts. The execution is in Claude Code.  
Your data stays in your machine.

---

## Roadmap

- [ ] Stack-specific CLAUDE.md templates (Next.js, Rails, Django, Go)
- [ ] `/hire-team` orchestrator command
- [ ] DevOps Agent — CI/CD, Docker, deployment strategy
- [ ] Data Agent — analytics instrumentation, KPI tracking
- [ ] Performance Agent — profiling, optimization, load testing

---

## Contributing

Found a mode that's missing? A prompt that produces weak output? Open an issue or PR.

The goal is one thing: agents that produce output a senior engineer would actually respect.  
If a mode produces something you'd throw away, it's broken and worth fixing.

---

## License

MIT — use these in your projects, your company, your team.  
If you build something on top of this, a star or a mention goes a long way.

---

Built by [Navox Labs](https://navox.tech) — tools for engineering teams that move fast.
