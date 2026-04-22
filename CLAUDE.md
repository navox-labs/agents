# CLAUDE.md — navox-labs/agents

This is the build instruction file for the `navox-labs/agents` repository.
Read this entire file before touching any file in this repo.

---

## What this repo is

A collection of Claude Code subagents — 8 specialist AI agents (7 engineers + 1 installer utility) that run entirely inside Claude Code sessions. No platform, no login, no data stored. Engineers install them globally or per project and hire them via slash commands.

This repo is open source under MIT. It lives at `github.com/navox-labs/agents`.

---

## Non-negotiable rules

- **Never modify agent prompt content without an explicit instruction to do so** — the prompts are the product
- **Never flatten the folder structure** — every file has a specific location for a reason
- **Never add dependencies** — this repo has zero dependencies by design
- **Never create binary files** — everything is markdown
- **Never rename agent files** — the filename becomes the slash command name
- **Always validate frontmatter** — malformed frontmatter breaks Claude Code agent loading
- **Always keep README.md in sync** — if you add/rename an agent, update the README table

---

## Commands

| Command | What it does |
|---|---|
| `/hire-team` | Onboard the full team, show handoff order |
| `/agency-run <task>` | Orchestrate the full team to complete a task end-to-end |
| `bash scripts/validate.sh` | Run repo integrity checks (111 checks across agents, docs, plugins, git) |

## Project memory

The team's institutional memory lives in two places:
- `.claude/project-memory.md` — shared across all agents, updated after every run
- `.claude/memory/[agent].md` — per-agent memory, updated after each agent run

Never delete these files. They are the team's knowledge base.

---

## Exact folder structure

This is the required structure. Do not deviate.

```
navox-labs/agents/
│
├── .gitignore
├── CLAUDE.md
├── README.md
├── GETTING-STARTED.md
├── LICENSE
│
├── .claude/
│   ├── agents/                        ← subagent definitions (one file per agent)
│   │   ├── architect.md               ← _architect (agent)
│   │   ├── devops.md                  ← _devops (agent)
│   │   ├── fullstack.md               ← _fullstack (agent)
│   │   ├── installer.md               ← _installer (agent, auto-dispatched — no command wrapper)
│   │   ├── local-review.md            ← local-review (agent, invoked by agency-run)
│   │   ├── qa.md                      ← _qa (agent)
│   │   ├── security.md                ← _security (agent)
│   │   └── ux.md                      ← _ux (agent)
│   │
│   ├── commands/                      ← slash commands
│   │   ├── agency-run.md              ← /agency-run (orchestrator)
│   │   ├── architect.md               ← /architect (command wrapper → _architect)
│   │   ├── devops.md                  ← /devops (command wrapper → _devops)
│   │   ├── fullstack.md               ← /fullstack (command wrapper → _fullstack)
│   │   ├── hire-team.md               ← /hire-team (onboarding)
│   │   ├── qa.md                      ← /qa (command wrapper → _qa)
│   │   ├── security.md               ← /security (command wrapper → _security)
│   │   └── ux.md                      ← /ux (command wrapper → _ux)
│   │
│   ├── memory/                        ← per-agent memory files (created at runtime)
│   │   └── [agent].md
│   │
│   ├── project-memory.md             ← shared project memory (created at runtime)
│   └── settings.local.json           ← local permission overrides (gitignored)
│
├── .claude-plugin/
│   ├── plugin.json                    ← plugin manifest for marketplace distribution
│   └── marketplace.json               ← marketplace registry
│
├── scripts/
│   └── validate.sh                    ← repo integrity checker (bash scripts/validate.sh)
│
├── templates/                         ← starter CLAUDE.md files per stack
│   ├── nextjs.CLAUDE.md
│   ├── node-api.CLAUDE.md
│   ├── rails.CLAUDE.md
│   ├── python-fastapi.CLAUDE.md
│   └── cloudflare-workers.CLAUDE.md
│
└── docs/
    ├── modes.md                       ← all modes for all agents
    ├── auth-ownership.md              ← auth responsibility table
    ├── handoff-chain.md               ← agent handoff flow diagram
    ├── hitl.md                        ← human-in-the-loop guide
    ├── parallel-execution.md          ← parallel agent execution guide
    └── install.md                     ← installation instructions
```

If a file or folder does not exist in this structure, create it.
If a file or folder exists that is not in this structure, ask before touching it.

---

## Agent file format (strict)

Every file in `.claude/agents/` must follow this exact format.
No exceptions. Malformed frontmatter silently breaks agent loading.

```markdown
---
name: agent-name-in-kebab-case
description: One sentence. What this agent does and when Claude should load it automatically. Include key trigger words.
---

[Full system prompt content here]
```

### Frontmatter rules

| Field | Rule |
|---|---|
| `name` | Lowercase. Agents use underscore prefix (`_architect`). Commands use plain name (`architect`). |
| `description` | One sentence. Used by Claude to auto-load the agent. Must include trigger keywords. |
| `model` | Required for agents. `claude-opus-4-6` for Architect + Security. `claude-sonnet-4-6` for all others. |
| `tools` | Required for agents. Comma-separated list of allowed tools (Read, Write, Edit, Bash, Glob, Grep, WebSearch). |

### Agent name → slash command mapping

Agents use the underscore-prefix pattern to avoid name collision with command wrappers (see project-memory.md for history).

| File | name field | Type | Slash command |
|---|---|---|---|
| architect.md | `_architect` | agent | via `/architect` command wrapper |
| devops.md | `_devops` | agent | via `/devops` command wrapper |
| fullstack.md | `_fullstack` | agent | via `/fullstack` command wrapper |
| qa.md | `_qa` | agent | via `/qa` command wrapper |
| security.md | `_security` | agent | via `/security` command wrapper |
| ux.md | `_ux` | agent | via `/ux` command wrapper |
| installer.md | `_installer` | agent | auto-dispatched by Claude (no wrapper) |
| local-review.md | `local-review` | agent | invoked by agency-run (no wrapper) |
| agency-run.md | `agency-run` | command | `/agency-run` |
| hire-team.md | `hire-team` | command | `/hire-team` |
| architect.md (commands/) | `architect` | command wrapper | `/architect` → reads `_architect` |
| devops.md (commands/) | `devops` | command wrapper | `/devops` → reads `_devops` |
| fullstack.md (commands/) | `fullstack` | command wrapper | `/fullstack` → reads `_fullstack` |
| qa.md (commands/) | `qa` | command wrapper | `/qa` → reads `_qa` |
| security.md (commands/) | `security` | command wrapper | `/security` → reads `_security` |
| ux.md (commands/) | `ux` | command wrapper | `/ux` → reads `_ux` |

---

## Command file format

Every file in `.claude/commands/` uses the same frontmatter format as agents.
The `hire-team` command should:
1. Briefly explain what the full team does
2. Instruct the user to start with `/architect DIAGNOSE` if unsure
3. List all 8 agents with their primary slash command
4. Show the recommended handoff order

---

## Docs folder rules

| File | What it must contain |
|---|---|
| `modes.md` | Every agent listed, every mode listed, one-line description per mode |
| `auth-ownership.md` | The full auth ownership table — all 10 rows, all agents |
| `handoff-chain.md` | The full chain: DIAGNOSE → DESIGN → parallel tracks → BUILD → parallel QA+Security → LAUNCH-AUDIT → SHIP |
| `install.md` | Plugin install, manual install, verification steps, uninstall |

---

## README.md rules

The README is the public landing page. Keep it sharp.

- First 3 lines must communicate: what it is, who it's for, how to install
- The team table must stay at the top — 8 rows, one per agent
- Install block must always show a working copy command
- Never remove the "What this is not" section — it's a key differentiator
- The auth ownership table must stay complete
- Roadmap must reflect only unbuilt features

---

## GETTING-STARTED.md rules

This file is written for junior engineers who have never worked in a team before.

- Language must be plain English — no assumed knowledge
- Every agent must be listed with a real-world job equivalent
- The handoff chain must match `docs/handoff-chain.md` exactly
- local-review must be included with its three responses: LGTM, FEEDBACK, STOP
- The glossary must stay current — add any new terms agents introduce

---

## How to add a new agent

1. Create `.claude/agents/[agent-name].md`
2. Add correct frontmatter (`name`, `description`)
3. Write full system prompt with all required modes including `PLAN`
4. Add the agent to README.md team table
5. Add the agent to `docs/modes.md`
6. Update `docs/handoff-chain.md` if it changes the chain
7. Update `.claude/commands/hire-team.md` if it joins the default team
8. Update `GETTING-STARTED.md` if the new agent affects the onboarding flow

---

## How to update an agent prompt

1. Open the agent file
2. Make the change
3. Verify frontmatter is still valid after editing
4. Update `docs/modes.md` if a mode was added or renamed
5. Do NOT change the `name` field — it breaks anyone who installed globally

---

## Verification checklist

Before committing any changes, verify:

- [ ] All 8 agent files exist in `.claude/agents/`
- [ ] All agent files have valid frontmatter (`name` + `description` + `model` + `tools` where applicable)
- [ ] All 6 command wrappers exist in `.claude/commands/` and reference the correct agent file
- [ ] `hire-team.md` exists in `.claude/commands/`
- [ ] `agency-run.md` exists in `.claude/commands/`
- [ ] `local-review.md` exists in `.claude/agents/`
- [ ] `GETTING-STARTED.md` exists in repo root
- [ ] All 4 docs files exist and are non-empty
- [ ] `docs/handoff-chain.md` includes local-review in the chain
- [ ] README.md team table matches the actual agent files
- [ ] No file outside this structure was created
- [ ] No binary, config, or dependency file was added

Run this to verify agent files are present:
```bash
ls .claude/agents/
# Expected: architect.md  devops.md  fullstack.md  installer.md  local-review.md  qa.md  security.md  ux.md

ls .claude/commands/
# Expected: agency-run.md  architect.md  devops.md  fullstack.md  hire-team.md  qa.md  security.md  ux.md

ls docs/
# Expected: auth-ownership.md  handoff-chain.md  hitl.md  install.md  modes.md  parallel-execution.md
```

---

## Git commit conventions

```
feat: add [agent-name] agent
fix: [agent-name] — fix [mode] mode [issue]
docs: update README [what changed]
prompt: [agent-name] — improve [mode] output quality
refactor: rename [old] to [new] — update README accordingly
```

Do not use generic messages like `update agents` or `fix stuff`.

---

## What Claude Code should never do in this repo

- Never run `npm install`, `pip install`, or any package manager
- Never create a `package.json`, `requirements.txt`, or any dependency file
- Never create `.env` files — this repo has no environment variables
- Never create subdirectories inside `.claude/agents/` — agents are flat files
- Never auto-generate documentation that contradicts the agent prompts
- Never modify two agent files in the same commit without an explicit instruction to do so
- Never guess at frontmatter values — follow the format exactly as specified above

---

## Context for Claude Code

When working in this repo, you are:
- Maintaining a set of carefully engineered AI agent prompts
- The prompts ARE the product — treat them with the same care as production code
- Your audience is senior engineers who will scrutinize every word
- Quality bar: output a senior engineer would actually use and trust

If in doubt about any change, ask before making it.
