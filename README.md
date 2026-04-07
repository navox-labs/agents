# agents — A Specialist Engineering Team for Claude Code

> 6 AI agents. Zero dependencies. No platform, no login, no data stored. Your code never leaves your machine.

[![GitHub stars](https://img.shields.io/github/stars/navox-labs/agents?style=social)](https://github.com/navox-labs/agents)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)

```bash
# Install globally — works in every project
git clone https://github.com/navox-labs/agents.git
cp -r agents/.claude/agents/* ~/.claude/agents/
cp -r agents/.claude/commands/* ~/.claude/commands/
```

```
/agency-run Build a SaaS app with user auth, team billing, and an admin dashboard
```

New to engineering teams? Read the [Getting Started guide](GETTING-STARTED.md) first.

---

## What is this?

Every AI coding tool today is a plugin you install or a platform you log into. This is neither.

These are Claude Code subagents — markdown files that live in your project or globally in `~/.claude/agents/`. They run entirely inside your Claude Code session. No API calls to a third-party server. No account. No telemetry. Just specialists you can hire from the terminal.

The intelligence is in the prompts. The execution is in Claude Code. Your data stays on your machine.

---

## Quick start

**Global install** — available in every project:
```bash
git clone https://github.com/navox-labs/agents.git
cp -r agents/.claude/agents/* ~/.claude/agents/
cp -r agents/.claude/commands/* ~/.claude/commands/
```

**Project install** — scoped to one repo:
```bash
mkdir my-project
cd my-project
git clone https://github.com/navox-labs/agents.git /tmp/navox-agents
mkdir -p .claude/agents .claude/commands
cp -r /tmp/navox-agents/.claude/agents/* .claude/agents/
cp -r /tmp/navox-agents/.claude/commands/* .claude/commands/
rm -rf /tmp/navox-agents
```

Then open Claude Code:
```bash
claude
```

And run:
```
/agency-run Build a to-do app with user login. Use Next.js and a database.
```

Or hire a single agent:
```
architect DIAGNOSE — I have a broken auth flow and I'm not sure where to start
```

---

## The team

| Agent | Specialty | When to use |
|---|---|---|
| 🎯 **Orchestrator** (`/agency-run`) | Full team coordination, handoff sequencing | Any task that needs more than one agent, or when you're not sure who to hire |
| 🏗️ **Architect** (`architect`) | System design, auth model, scalability, caching | New project, major feature, architecture review, don't know where to start |
| 🎨 **UI/UX** (`ux`) | User flows, wireframes, visual design, component specs | Designing screens, auth UX, building a design system |
| ⚙️ **Full Stack** (`fullstack`) | Production code, unit tests, auth implementation | Building features, fixing bugs, refactoring, code review |
| 👁️ **Local Review** (`local-review`) | Dev server, browser preview, owner checkpoint | After every build — mandatory human approval before QA runs |
| 🧪 **QA** (`qa`) | Test plans, test execution, regression, auth flow testing | Testing delivered code, validating fixes, pre-launch coverage |
| 🚀 **DevOps** (`devops`) | CI/CD pipelines, Docker, deployment, infrastructure | Setting up pipelines, containerizing, deploying, infra incidents |
| 🔐 **Security** (`security`) | Threat modeling, auth audit, code review, launch sign-off | Design review, code audit, launch readiness, incident response |

---

## Scenarios

### Scenario 1: Starting a new project from scratch

```
/agency-run Build a multi-tenant SaaS with JWT auth and Redis caching
```

1. **Architect** DIAGNOSE → DESIGN — designs the full system, picks the stack, defines the auth model
2. **UX** FLOW → SPEC — maps every screen and state, delivers component specs
3. **Security** DESIGN-REVIEW — reviews the auth model and flags risks before code is written
4. **Full Stack** BUILD — writes production code with unit tests from the arch doc and UX specs
5. **Local Review** — starts the app in your browser, waits for your approval
6. **QA** TEST-RUN — tests every flow including auth edge cases
7. **Security** CODE-AUDIT → LAUNCH-AUDIT — audits the code, gives final verdict

**Result:** Production-ready codebase with system design, tested code, security sign-off, and full project memory for the next run.

### Scenario 2: Adding auth to an existing app

```
/agency-run Add user authentication to this Express app — email/password with JWT
```

1. **Architect** DESIGN — defines auth strategy, token lifecycle, data model for the existing codebase
2. **Security** DESIGN-REVIEW — validates the auth model before implementation
3. **Full Stack** BUILD — implements auth with unit tests, following the Architect's spec exactly
4. **Local Review** — you verify login, signup, and error states in the browser
5. **QA** TEST-RUN + **Security** CODE-AUDIT — parallel testing and audit of the auth implementation

**Result:** Auth added with zero gaps — every flow tested, every vulnerability checked, every decision documented.

### Scenario 3: Shipping a feature safely before a deadline

```
/agency-run Add Stripe billing with team plans — shipping Friday
```

1. **Architect** DESIGN — scopes the billing integration, defines API contracts
2. **Full Stack** BUILD — implements billing with Stripe webhooks and unit tests
3. **Local Review** — you verify the checkout flow works end-to-end
4. **QA** TEST-RUN — tests payment edge cases: failed charges, plan upgrades, cancellations
5. **Security** LAUNCH-AUDIT — final sign-off on payment handling and data security

**Result:** Feature ships on time with QA coverage and security approval. No shortcuts.

---

## The handoff chain

```
You arrive with anything — idea, broken code, vague request
        ↓
architect DIAGNOSE         → figures out what you need and who to hire
        ↓
architect DESIGN           → system design, auth model, security model, testing strategy
        ↓
        ├── ux FLOW → WIREFRAME → DESIGN → SPEC      (parallel)
        └── security DESIGN-REVIEW                     (parallel)
        ↓
fullstack BUILD            → code + unit tests, follows arch doc and UX specs
        ↓
local-review CHECKPOINT    → starts dev server, opens browser, waits for you
        ↓                    LGTM → continue | FEEDBACK → back to fullstack | STOP → pause
        ├── qa TEST-RUN                                (parallel, after LGTM)
        └── security CODE-AUDIT                        (parallel, after LGTM)
        ↓
fullstack                  → fixes all findings
        ↓
security LAUNCH-AUDIT      → final verdict: APPROVED | APPROVED WITH CONDITIONS | BLOCKED
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
| Deployment secrets management (env vars, rotation) | DevOps Agent |
| Auth security constraints | Security Agent |
| Auth code audit | Security Agent |
| Auth launch sign-off | Security Agent |

---

## Local review

After every Fullstack BUILD, the chain pauses for you. The local-review agent:

1. Detects the framework from `package.json` or equivalent
2. Starts the dev server and waits for it to respond
3. Opens the browser automatically
4. Takes a screenshot to `.agency-workspace/local-review-screenshot.png`
5. Prints a checkpoint and waits for your response

Three responses:
- `LGTM` — approve and continue to QA + Security
- `FEEDBACK: [notes]` — send back to Fullstack with your notes
- `STOP` — kill the server and pause the chain

The chain never auto-continues past this point. You are the only one who can approve.

---

## Project memory

Every run updates two memory files automatically:

- `.claude/project-memory.md` — what was built, decided, and why
- `.claude/memory/[agent].md` — each agent's per-codebase knowledge

Agents read their memory before starting and update it after finishing. This is how the team knows what was already done. Next time you run `/agency-run`, it won't repeat work or re-ask questions.

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

### 👁️ Local Review

The mandatory human checkpoint between build and test. After Fullstack delivers code, this agent starts the dev server, opens your browser, and waits for you to respond.

```
Responses:
  LGTM              — approve and continue to QA + Security
  FEEDBACK: [notes]  — send back to Fullstack with your notes
  STOP              — kill the server and pause the chain
```

The chain never auto-continues past this point. You are the only one who can approve.

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

## What makes this different

**What this is NOT:**
- Not a web platform. There's no dashboard to log into.
- Not a SaaS. There's no subscription or usage limit.
- Not a plugin. There's nothing to configure in your editor.
- Not storing your data. Your code runs through Claude Code locally.

**What this IS:**
- Carefully engineered system prompts — not generic "be helpful" instructions, but deep domain expertise with structured modes, handoff protocols, and auth ownership across every agent.
- A real team workflow — agents don't work in isolation. The Architect's output feeds UX and Security. Fullstack builds from their specs. QA and Security audit the result. Every handoff is explicit.
- A human-in-the-loop system — local-review ensures you see the running app before testing begins. The team works for you, not around you.

---

## By the numbers

- **7** specialist agents across architecture, UX, engineering, DevOps, QA, and security — plus 1 orchestrator command that runs them all
- **1** structured handoff chain with zero gaps in auth ownership
- **1** mandatory human checkpoint built into every run
- **Persistent** project memory that carries context across sessions

---

## Hire one or hire all

These agents are independent. You don't need the full team.

- Building a new product? Start with `architect DIAGNOSE`
- Already have code, want it tested? `qa PLAN`
- Shipping next week and worried about security? `security LAUNCH-AUDIT`
- Need CI/CD or Docker setup? `devops PLAN`
- Something's broken and you don't know why? `fullstack DEBUG`
- Not sure which agent you need? `architect DIAGNOSE` — describe your situation

---

## Stack Templates

Drop a pre-built `CLAUDE.md` into your project so agents understand your stack from the first session.

| Template | Stack | File |
|---|---|---|
| **Next.js** | Next.js 15, TypeScript, Tailwind, PostgreSQL, Prisma, Supabase Auth, Redis, Vercel | [`templates/nextjs.CLAUDE.md`](templates/nextjs.CLAUDE.md) |
| **Node API** | Node.js, Express, TypeScript, PostgreSQL, Prisma, JWT, Redis, Railway | [`templates/node-api.CLAUDE.md`](templates/node-api.CLAUDE.md) |
| **Rails** | Ruby on Rails 8, PostgreSQL, Devise, Sidekiq, Redis, Render | [`templates/rails.CLAUDE.md`](templates/rails.CLAUDE.md) |

```bash
# Copy a template into your project
cp templates/nextjs.CLAUDE.md your-project/CLAUDE.md
```

Edit the file to match your project's specifics — these are starting points, not rigid configs.

---

## Roadmap

- [x] Stack-specific CLAUDE.md templates (Next.js, Rails, Node API)
- [x] DevOps Agent — CI/CD, Docker, deployment strategy
- [ ] More templates (Django, Go, Laravel)
- [ ] Data Agent — analytics instrumentation, KPI tracking
- [ ] Performance Agent — profiling, optimization, load testing

---

## Contributing

Found a mode that's missing? A prompt that produces weak output? Open an issue or PR.

The goal is one thing: agents that produce output a senior engineer would actually respect.
If a mode produces something you'd throw away, it's broken and worth fixing.

---

## Get started now

```bash
# 1. Install the team
git clone https://github.com/navox-labs/agents.git
cp -r agents/.claude/agents/* ~/.claude/agents/
cp -r agents/.claude/commands/* ~/.claude/commands/

# 2. Open your project in Claude Code
cd your-project

# 3. Run the team
# /agency-run [your task]

# 4. Review the app when local-review pauses for you

# 5. Ship when Security says APPROVED
```

---

## License

MIT — use these in your projects, your company, your team.
If you build something on top of this, a star or a mention goes a long way.

---

Built by [Navox Labs](https://navox.tech) — tools for engineering teams that move fast.
