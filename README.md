# Navox Agents

> A specialist AI engineering team for Claude Code.
> 8 agents. No platform. No login. Your code never leaves your machine.

[![GitHub stars](https://img.shields.io/github/stars/navox-labs/agents?style=social)](https://github.com/navox-labs/agents)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Built for Claude Code](https://img.shields.io/badge/Built_for-Claude_Code-blueviolet)](https://claude.ai)
<img width="2752" height="1536" alt="Game Poster Merge" src="https://github.com/user-attachments/assets/d0bcd837-7438-4267-86f6-75a1810b56f9" />


---

## See it work

**nom.sh — one prompt, 7 minutes:**
> 🦀 A crab cookie clicker. 1,330 lines. 6 bugs caught by QA.
> [See the code →](https://github.com/navox-labs/nom)

**PipeWar — built, debugged, and deployed by agents:**
> 🛡️ A Factorio-inspired tower defense game. Built from scratch, 8 production bugs diagnosed and fixed, 65 tests passing. All by the agent team.
> [Play PipeWar →](https://frontend-beta-five-83.vercel.app) · [See the code →](https://github.com/navox-labs/pipewar)

---

## Install as a Claude Code plugin

Navox Agents is available on Claude Code's plugin marketplace. This is the fastest way to get started — no cloning, no copying files.

If you hit an SSH error, run this first (one time):
```bash
git config --global url."https://github.com/".insteadOf "git@github.com:"
```

Then install:
```
/plugin marketplace add https://github.com/navox-labs/agents
/plugin install navox-agents
/reload-plugins
```

> If this saves you time, [⭐ star the repo](https://github.com/navox-labs/agents) — it helps others find it.

> **Note:** Plugin commands are namespaced. Use `/navox-agents:agency-run` and `/navox-agents:hire-team` instead of `/agency-run` and `/hire-team`. If you installed via the manual copy method below, no namespace is needed.

---

## Alternative: manual install (for customization)

```bash
git clone https://github.com/navox-labs/agents.git
mkdir -p ~/.claude/agents ~/.claude/commands ~/.claude/templates
cp -r agents/.claude/agents/* ~/.claude/agents/
cp -r agents/.claude/commands/* ~/.claude/commands/
cp -r agents/templates/* ~/.claude/templates/
```

---

## Run your first build

Open Claude Code in any project folder and run:

**If you installed as a plugin:**
```
/navox-agents:agency-run Build a {browser-based} {Cookie Clicker game}
with {Atari pixel art} vibes where {crabs eat cookies}.
No authentication. No backend. Single HTML file,
runs in any browser. Make it {addictive} and {funny}.
```

**If you installed manually (copy method):**
```
/agency-run Build a {browser-based} {Cookie Clicker game}
with {Atari pixel art} vibes where {crabs eat cookies}.
No authentication. No backend. Single HTML file,
runs in any browser. Make it {addictive} and {funny}.
```

Replace the `{variables}` with your own idea.
This is exactly how we built [nom.sh](https://github.com/navox-labs/nom) in 7 minutes.

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

    G3 -->|APPROVED ✓| DEVOPS
    DEVOPS["🚀 DevOps · Sonnet 4.6\nDEPLOY\nVercel + Cloudflare · README written"]
    DEVOPS -->|live URL + video| SHIP

    SHIP["🚀 SHIP"]
```

---

## The team

| | Agent | What they do |
|---|---|---|
| 🏗️ | **Architect** | Designs the system. Picks the stack. Defines auth. |
| 🎨 | **UI/UX** | Maps user flows. Specs every screen and state. |
| ⚙️ | **Full Stack** | Builds it. Tests it. Ships clean code. |
| 🚀 | **DevOps** | CI/CD. Docker. Deploys. Secrets never touch code. |
| 👁️ | **Local Review** | Starts the app. Shows it to you. Waits for your go. |
| 🧪 | **QA** | Finds every bug. Auth flows get extra scrutiny. |
| 🔐 | **Security** | Audits everything. Nothing launches without a verdict. |
| 📦 | **Installer** | Helps you discover and install individual agents. |

Use one agent directly: `/architect DIAGNOSE`, `/security LAUNCH-AUDIT`, `/qa PLAN`
(Plugin users: prefix with `navox-agents:` e.g. `/navox-agents:architect DIAGNOSE`)

---

## Handoff contracts

Every agent has a **handoff contract** — a defined set of required sections it must include in its output before passing work to the next agent. Agents self-validate against their contract before completing.

This means:
- The **Architect** must include API contracts, auth model, and build order — not just a prose summary
- **Fullstack** must include a file manifest and run instructions — not just "I built it"
- **Security** must reference specific file paths and severity levels — not general advice
- **QA** must include exact pass/fail counts and reproduction steps — not approximations

If an upstream agent omits a required section, the downstream agent flags it before starting work. No agent guesses at what it should have received.

Full contract details: [docs/handoff-chain.md](docs/handoff-chain.md)

---

## Quick commands

Each agent supports multiple **modes** — specific workflows you trigger by name.

| What you need | Command |
|---|---|
| Don't know where to start | `/architect DIAGNOSE` |
| Full system design | `/architect DESIGN` |
| Build a feature | `/fullstack BUILD` |
| Check if it's secure | `/security LAUNCH-AUDIT` |
| Run the whole team | `/agency-run your task here` |
| See all modes | [docs/modes.md](docs/modes.md) |

Plugin users: prefix commands with `navox-agents:` (e.g. `/navox-agents:architect DIAGNOSE`)

---

## You stay in control

1. Agents pause at every gate and wait for your approval
2. Nothing destructive runs without your explicit sign-off
3. You can redirect, reject, or stop at any point

> Agents stop. They wait. You decide. Then they continue.

Full guide: [docs/hitl.md](docs/hitl.md)

---

## Project memory

After each `/agency-run`, the team writes down what it learned in `.claude/project-memory.md`. Next run, it reads this file first — so it won't repeat work or ask you to re-explain the stack.

Memory is structured into three sections:

| Section | Update rule | Purpose |
|---|---|---|
| **Current State** | Overwritten each run | What's true right now — stack, status, live URL |
| **Active Decisions** | Add new, remove resolved | Open questions that still need answers |
| **History** | Prepend, never delete | What happened in each run (audit trail) |

Each agent also keeps its own memory in `.claude/memory/[agent].md` with the same structure. Old history entries are automatically summarized to prevent unbounded growth.

---

## Start faster

First time using Navox Agents on a new project?
Tell the agents your stack once — they'll know it every session.

After installing the agents globally, run this from inside your project folder:

```bash
cp ~/.claude/templates/nextjs.CLAUDE.md ./CLAUDE.md          # Next.js + Vercel
cp ~/.claude/templates/node-api.CLAUDE.md ./CLAUDE.md        # Node.js + Express
cp ~/.claude/templates/rails.CLAUDE.md ./CLAUDE.md           # Rails 8
cp ~/.claude/templates/python-fastapi.CLAUDE.md ./CLAUDE.md  # Python + FastAPI
cp ~/.claude/templates/cloudflare-workers.CLAUDE.md ./CLAUDE.md  # Cloudflare Workers
```

Pick one. The agents read it automatically when Claude Code opens.

---

## Repo validation

If you fork or customize agent prompts, run the integrity checker to catch drift:

```bash
bash scripts/validate.sh
```

Checks 111 things: agent files, frontmatter, model routing, handoff contracts, memory templates, plugin manifests, doc completeness, agent count consistency, and git hygiene. Exits 0 on pass, 1 on failure.

---

## What this is not

- Not a platform. No dashboard, no login.
- Not a SaaS. No subscription, no usage limit.
- Not a walled garden. It's a plugin, but the source is open — fork it, customize the prompts, make it yours.
- Not storing your data. Everything runs locally through Claude Code.
- Not autonomous. You stay in the loop.

---

[📖 Docs](docs/) · [⚡ Install](docs/install.md) · [🦀 See it work](https://github.com/navox-labs/nom) · [🐛 Report Bug](https://github.com/navox-labs/agents/issues)

Built by [Navox Labs](https://navox.tech) · MIT License
