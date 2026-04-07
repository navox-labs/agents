<div align="center">

# Navox Agents

### You just hired 6 AI engineers. They start now.

No platform. No login. No subscription.<br>
Your code never leaves your machine.

[![GitHub stars](https://img.shields.io/github/stars/navox-labs/agents?style=social)](https://github.com/navox-labs/agents)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Built for Claude Code](https://img.shields.io/badge/Built_for-Claude_Code-blueviolet)](https://claude.ai)

</div>

<br>

## Watch them build a game in 7 minutes

> We gave the agents one prompt.<br>
> 7 minutes later: a playable crab cookie clicker game.<br>
> 1,330 lines. Zero dependencies. 6 bugs caught by QA.
>
> [See the git history](https://github.com/navox-labs/nom/commits/main)

![Agents building nom.sh](assets/demo.gif)

<br>

## Hire the team

```bash
# Global install — works in every project
git clone https://github.com/navox-labs/agents.git && cp -r agents/.claude/agents/* ~/.claude/agents/ && cp -r agents/.claude/commands/* ~/.claude/commands/
```

```bash
# Or install into one project
git clone https://github.com/navox-labs/agents.git /tmp/navox-agents && mkdir -p .claude/agents .claude/commands && cp -r /tmp/navox-agents/.claude/agents/* .claude/agents/ && cp -r /tmp/navox-agents/.claude/commands/* .claude/commands/ && rm -rf /tmp/navox-agents
```

<br>

## The team

| | Agent | Personality |
|---|---|---|
| 🏗️ | **Architect** | Thinks 10 steps ahead. Refuses to let you make the wrong call. |
| 🎨 | **UI/UX** | Makes it beautiful. Won't ship a screen without every state covered. |
| ⚙️ | **Full Stack** | Moves fast. Tests everything. Writes code your future self won't hate. |
| 🧪 | **QA** | Finds the bugs you didn't know existed. Nothing ships without their sign-off. |
| 🔐 | **Security** | Thinks like a hacker. Sleeps better than you do. |
| 🚀 | **DevOps** | Automates everything that runs twice. Secrets never touch the code. |
| 🎮 | **Orchestrator** (`/agency-run`) | One prompt. Full team. Done. |

<br>

## The agent brain

```mermaid
flowchart TD
    CLI["`**$ /agency-run** your prompt here`"]

    CLI -->|your prompt| AD

    subgraph ARCH ["🏗️ Architect · Opus 4.6"]
        AD["DIAGNOSE\nreads request · maps team · flags blockers"]
        ADE["DESIGN\nstack · auth · API contracts · security · testing"]
        AD -->|team plan| ADE
    end

    ADE -->|system design doc| G1

    G1{{"⚠️ Gate 1\nyou review + approve"}}

    G1 -->|auth + UX brief| UX
    G1 -->|auth model + threats| SEC1

    subgraph PARALLEL1 ["runs in parallel"]
        UX["🎨 UI/UX · Sonnet 4.6\nFLOW → WIREFRAME → SPEC\nwireframes · component specs · all states"]
        SEC1["🔐 Security · Opus 4.6\nDESIGN-REVIEW\nauth model · threat surface · constraints"]
    end

    UX -->|wireframes + specs| G2
    SEC1 -->|auth constraints| G2

    G2{{"⚠️ Gate 2\nyou approve — cleared to build"}}

    G2 -->|cleared to build| FS1

    FS1["⚙️ Full Stack · Sonnet 4.6\nBUILD\ncode + auth implementation + unit tests"]

    FS1 -->|working code + tests| CP

    CP{{"⚠️ Checkpoint\napp running locally · LGTM / FEEDBACK / STOP"}}

    CP -->|code to test| QA
    CP -->|code to audit| SEC2

    subgraph PARALLEL2 ["runs in parallel"]
        QA["🧪 QA · Sonnet 4.6\nTEST-RUN\n38 tests · auth matrix · edge cases"]
        SEC2["🔐 Security · Opus 4.6\nCODE-AUDIT\nOWASP · auth bypass · vulns"]
    end

    QA -->|bug report| FS2
    SEC2 -->|vulnerability report| FS2

    FS2["⚙️ Full Stack · Sonnet 4.6\nFIXES\nall Critical findings resolved · clean push"]

    FS2 -->|all findings resolved| G3

    G3{{"⚠️ Gate 3\nSecurity LAUNCH-AUDIT · verdict"}}

    G3 -->|APPROVED ✓| SHIP

    SHIP["🚀 SHIP"]
```

<br>

## One prompt. Full team.

You describe what you want. The Architect designs the system. UX and Security review the plan in parallel. Full Stack builds it — with tests. The app opens in your browser so you can see it running. QA hunts for bugs while Security audits the code. When everything passes, you ship.

**The human stays in control. Every critical decision waits for your approval.**

<br>

## You're always in control

- Agents stop at critical decisions and wait for you
- Nothing destructive runs without your explicit approval
- You can redirect, reject, or stop at any point

Full guide: [docs/hitl.md](docs/hitl.md)

<br>

## Start with your stack

Pre-built `CLAUDE.md` templates so agents understand your stack from the first session.

```
templates/nextjs.CLAUDE.md      — Next.js 15, TypeScript, Tailwind, Prisma, Supabase Auth
templates/node-api.CLAUDE.md    — Express, TypeScript, Prisma, JWT, Redis, Railway
templates/rails.CLAUDE.md       — Rails 8, PostgreSQL, Devise, Sidekiq, Render
```

<br>

## What this is not

- Not a web platform. There's no dashboard to log into.
- Not a SaaS. There's no subscription or usage limit.
- Not a plugin. There's nothing to configure in your editor.
- Not storing your data. Your code runs through Claude Code locally.
- Not autonomous. You stay in the loop.

<br>

---

[📖 Docs](docs/) · [⚡ Install](docs/install.md) · [🦀 See it work](https://github.com/navox-labs/nom) · [🐛 Report Bug](https://github.com/navox-labs/agents/issues)

Built by [Navox Labs](https://navox.tech) · MIT License
