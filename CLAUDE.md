# CLAUDE.md — navox-labs/agents

This is the build instruction file for the `navox-labs/agents` repository.
Read this entire file before touching any file in this repo.

---

## What this repo is

A collection of Claude Code subagents — 5 specialist AI engineers that run entirely inside Claude Code sessions. No platform, no login, no data stored. Engineers install them globally or per project and hire them via slash commands.

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

## Exact folder structure

This is the required structure. Do not deviate.

```
navox-labs/agents/
│
├── CLAUDE.md                          ← this file
├── README.md                          ← public-facing documentation
├── LICENSE                            ← MIT license
│
├── .claude/
│   ├── agents/                        ← subagent definitions (one file per agent)
│   │   ├── architect.md               ← /architect
│   │   ├── fullstack.md               ← /fullstack
│   │   ├── ux.md                      ← /ux
│   │   ├── qa.md                      ← /qa
│   │   └── security.md                ← /security
│   │
│   └── commands/                      ← slash commands (orchestration)
│       └── hire-team.md               ← /hire-team (runs all 5 agents)
│
└── docs/
    ├── modes.md                       ← all modes for all agents explained
    ├── auth-ownership.md              ← auth responsibility table
    ├── handoff-chain.md               ← agent handoff flow diagram
    └── install.md                     ← detailed install instructions
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
| `name` | Lowercase kebab-case. Becomes the slash command. No spaces. |
| `description` | One sentence. Used by Claude to auto-load the agent. Must include trigger keywords. |
| No other fields | Do not add model, temperature, or any other frontmatter fields. |

### Agent name → slash command mapping

| File | name field | Slash command |
|---|---|---|
| architect.md | `architect` | `/architect` |
| fullstack.md | `fullstack` | `/fullstack` |
| ux.md | `ux` | `/ux` |
| qa.md | `qa` | `/qa` |
| security.md | `security` | `/security` |
| hire-team.md | `hire-team` | `/hire-team` |

---

## Command file format

Every file in `.claude/commands/` uses the same frontmatter format as agents.
The `hire-team` command should:
1. Briefly explain what the full team does
2. Instruct the user to start with `/architect DIAGNOSE` if unsure
3. List all 5 agents with their primary slash command
4. Show the recommended handoff order

---

## Docs folder rules

| File | What it must contain |
|---|---|
| `modes.md` | Every agent listed, every mode listed, one-line description per mode |
| `auth-ownership.md` | The full auth ownership table — all 10 rows, all agents |
| `handoff-chain.md` | The full chain: DIAGNOSE → DESIGN → parallel tracks → BUILD → parallel QA+Security → LAUNCH-AUDIT → SHIP |
| `install.md` | Global install, project install, verification steps, uninstall |

---

## README.md rules

The README is the public landing page. Keep it sharp.

- First 3 lines must communicate: what it is, who it's for, how to install
- The team table must stay at the top — 5 rows, one per agent
- Install block must always show a working copy command
- Never remove the "What this is not" section — it's a key differentiator
- The auth ownership table must stay complete
- Roadmap must reflect only unbuilt features

---

## How to add a new agent

1. Create `.claude/agents/[agent-name].md`
2. Add correct frontmatter (`name`, `description`)
3. Write full system prompt with all required modes including `PLAN`
4. Add the agent to README.md team table
5. Add the agent to `docs/modes.md`
6. Update `docs/handoff-chain.md` if it changes the chain
7. Update `.claude/commands/hire-team.md` if it joins the default team

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

- [ ] All 5 agent files exist in `.claude/agents/`
- [ ] All agent files have valid frontmatter (`name` + `description`)
- [ ] `hire-team.md` exists in `.claude/commands/`
- [ ] All 4 docs files exist and are non-empty
- [ ] README.md team table matches the actual agent files
- [ ] No file outside this structure was created
- [ ] No binary, config, or dependency file was added

Run this to verify agent files are present:
```bash
ls .claude/agents/
# Expected: architect.md  fullstack.md  qa.md  security.md  ux.md

ls .claude/commands/
# Expected: hire-team.md

ls docs/
# Expected: auth-ownership.md  handoff-chain.md  install.md  modes.md
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
