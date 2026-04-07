# Navox Agents

> A specialist AI engineering team for Claude Code.
> 6 agents. No platform. No login. Your code never leaves your machine.

[![GitHub stars](https://img.shields.io/github/stars/navox-labs/agents?style=social)](https://github.com/navox-labs/agents)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Built for Claude Code](https://img.shields.io/badge/Built_for-Claude_Code-blueviolet)](https://claude.ai)

---

## See it work first

> We gave the agents one prompt.
> 7 minutes later: a playable crab cookie clicker game.
> 1,330 lines. Zero dependencies. 6 bugs caught by QA.
> [🦀 Play nom.sh →](https://github.com/navox-labs/nom)

![Agents building nom.sh](assets/demo.gif)

---

## Install

**Global** — available in every project:
```bash
git clone https://github.com/navox-labs/agents.git
cp -r agents/.claude/agents/* ~/.claude/agents/
cp -r agents/.claude/commands/* ~/.claude/commands/
```

**Project only:**
```bash
cp -r agents/.claude/agents/* .claude/agents/
cp -r agents/.claude/commands/* .claude/commands/
```

---

## Run your first build

Open Claude Code in any project folder and run:

```
/agency-run Build a SaaS app with user auth, team billing, and an admin dashboard
```

That's it. The full team runs automatically.

---

## The team

| | Agent | What they do |
|---|---|---|
| 🏗️ | **Architect** | Designs the system. Picks the stack. Defines auth. |
| 🎨 | **UI/UX** | Maps user flows. Specs every screen and state. |
| ⚙️ | **Full Stack** | Builds it. Tests it. Ships clean code. |
| 🚀 | **DevOps** | CI/CD. Docker. Deploys. Secrets never touch code. |
| 🧪 | **QA** | Finds every bug. Auth flows get extra scrutiny. |
| 🔐 | **Security** | Audits everything. Nothing launches without a verdict. |

Use one agent directly: `architect DIAGNOSE`, `security LAUNCH-AUDIT`, `qa PLAN`

---

## How it works

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

---

## You stay in control

1. Agents pause at every gate and wait for your approval
2. Nothing destructive runs without your explicit sign-off
3. You can redirect, reject, or stop at any point

Full guide: [docs/hitl.md](docs/hitl.md)

---

## Stack templates

Drop a pre-built `CLAUDE.md` into your project so agents know your stack immediately:

```bash
cp templates/nextjs.CLAUDE.md your-project/CLAUDE.md     # Next.js 15 + Prisma + Supabase Auth
cp templates/node-api.CLAUDE.md your-project/CLAUDE.md    # Express + JWT + Redis + Railway
cp templates/rails.CLAUDE.md your-project/CLAUDE.md       # Rails 8 + Devise + Sidekiq + Render
```

---

## What this is not

- Not a platform. No dashboard, no login.
- Not a SaaS. No subscription, no usage limit.
- Not a plugin. Nothing to configure in your editor.
- Not storing your data. Everything runs locally through Claude Code.
- Not autonomous. You stay in the loop.

---

[📖 Docs](docs/) · [⚡ Install](docs/install.md) · [🦀 See it work](https://github.com/navox-labs/nom) · [🐛 Report Bug](https://github.com/navox-labs/agents/issues)

Built by [Navox Labs](https://navox.tech) · MIT License
