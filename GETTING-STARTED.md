# Your first engineering team

You just got access to a team of 15 specialist AI agents who work for you, inside Claude Code, for free.

This guide explains who they are, how a real engineering team works, and how to use them — even if you've never worked with other engineers before.

---

## First: how a real engineering team works

When a company builds software, no single person does everything. Different people own different parts of the work. Here's the typical order:

**1. Someone validates the idea first**
Before anyone designs or builds, a strategist asks hard questions: What problem are we solving? Who has this problem? How do we know? What happens if we don't build this? This prevents building the wrong thing.

**2. Someone writes a precise specification**
Vague ideas produce vague software. A spec writer turns "build a login system" into a precise document with every requirement, edge case, and acceptance criterion spelled out.

**3. Someone designs the system**
Before anyone writes code, an architect figures out how everything fits together. What's the database? How does auth work? What's the API structure?

**4. A designer specifies what users see**
A UX designer maps out every screen — not just what it looks like, but every state (loading, error, empty, success).

**5. Security reviews the plan before code is written**
Fixing a security hole after shipping is 10x harder than catching it in the design.

**6. Engineers build from the spec**
Developers write code based on what the architect designed and what the UX designer specified.

**7. A reviewer checks the code**
Before testing, a code reviewer examines every change from 7 different angles: security, performance, maintainability, API contracts, data integrity, test coverage, and error handling.

**8. QA breaks it before users do**
A QA engineer tries every edge case, every wrong input, every unhappy path.

**9. Security audits the code before launch**
A final check — does the actual code match the security model?

**10. Someone ships it properly**
A release engineer runs the tests, generates the changelog, bumps the version, and creates the PR. No "just push it."

**11. The team learns from the sprint**
A retrospective captures what worked, what didn't, and what to change next time. Without this, teams make the same mistakes forever.

---

## What these agents are

Each agent is a specialist who owns one part of that process:

| | Agent | Real-world equivalent | Their job |
|---|---|---|---|
| 🧠 | Strategist | Product Manager | Validates ideas with forcing questions before anything gets built |
| 📋 | Spec Writer | Technical Writer | Turns vague requests into precise, testable specifications |
| 🏗️ | Architect | Principal Engineer | Designs the system before code is written |
| 🎨 | UX | Product Designer | Specifies every screen, state, and interaction |
| ⚙️ | Full Stack | Senior Developer | Writes production code with tests |
| 🔍 | Investigator | Debugging Specialist | Finds root causes before anyone writes a fix |
| 📝 | Reviewer | Code Reviewer | Reviews code with 7 specialist perspectives in parallel |
| 🚀 | DevOps | DevOps Engineer | CI/CD, Docker, deploys to production |
| 👁️ | Local Review | Manual QA | Starts the app, shows it to you, waits for your approval |
| 🧪 | QA | QA Engineer | Finds everything that can break |
| 🔐 | Security | Security Engineer | Reviews design + audits code before launch |
| 📦 | Shipper | Release Engineer | Tests, changelog, version bump, PR — the last mile |
| 🔄 | Retro | Engineering Lead | Runs retrospectives, captures learnings for next sprint |
| 💾 | Context Manager | Project Manager | Saves and restores session context so you can pause and resume |
| 🛠️ | Installer | Setup Wizard | Helps you discover and install individual agents |

The orchestrator (`/agency-run`) is like a project manager — it runs the team in the right order so you don't have to.

---

## Install

**Step 1 — install as a Claude Code plugin:**

If you hit an SSH error, run this first (one time):
```bash
git config --global url."https://github.com/".insteadOf "git@github.com:"
```

Then in Claude Code:
```
/plugin marketplace add https://github.com/navox-labs/agents
/plugin install navox-agents
/reload-plugins
```

That's it. No npm install. No API key. No account.

**Alternative: manual install (for customization)**

```bash
git clone https://github.com/navox-labs/agents.git
cd agents
bash scripts/setup.sh
```

Run `bash scripts/setup.sh --help` for options (e.g. `--global` to install for all projects).

**Verify it worked:**

```bash
ls ~/.claude/agents/
```

You should see 15 agent files:
```
architect.md  context-manager.md  devops.md  fullstack.md  installer.md
investigator.md  local-review.md  qa.md  retro.md  reviewer.md
security.md  shipper.md  spec-writer.md  strategist.md  ux.md
```

---

## Start a project: step by step

### Step 1 — Open Claude Code in your project folder

```bash
cd your-project
claude .
```

If you don't have a project yet, create an empty folder:

```bash
mkdir my-first-app
cd my-first-app
claude .
```

---

### Step 2 — Choose your sprint mode

There are three ways to run the team:

**Full Sprint** — for new features, big changes, or anything you're not sure about:
```
/agency-run FULL Build a simple to-do app — users can add, complete, and delete tasks.
Needs user login. Use Next.js and a database.
```

**Quick Sprint** — for small features when you already know what to build:
```
/agency-run QUICK Add a dark mode toggle to the settings page
```

**Hotfix** — when something is broken and needs fixing fast:
```
/agency-run HOTFIX Users get a blank screen after logging in on Safari
```

You don't need to know the tech stack in detail. Just describe what you want to build in plain English.

---

### Step 3 — Watch the team work (Full Sprint)

The agents run in this order automatically:

**Strategist goes first.**
It asks hard questions about your idea — who is this for? What problem does it solve? How will you know it worked? It might push back on your idea. That's its job.

**Spec Writer takes the validated idea.**
It produces a precise specification with every requirement, edge case, and acceptance criterion documented. No vague language allowed.

**Architect designs the system.**
It reads the spec and decides the tech stack, database, API structure, and auth model. All other agents work from this design.

**UX and Security run at the same time.**
UX designs every screen. Security reviews the architecture for vulnerabilities. Both finish before any code is written.

**Fullstack builds.**
Using the spec, architecture, and UX designs, the developer writes the actual code with unit tests.

**Local review — your checkpoint.**
After Fullstack builds the code, the app starts automatically in your browser. This is where the team stops and waits for you. Look at the running app, click around, then type:
- `LGTM` — you're happy, continue to review
- `FEEDBACK: [what you want changed]` — send it back for fixes
- `STOP` — pause everything

**Reviewer checks the code.**
The reviewer spawns 7 specialist checks in parallel — security, performance, maintainability, API contracts, data integrity, test coverage, and error handling. Every finding cites the exact file and line number.

**QA and Security run at the same time.**
QA tests everything that can break. Security audits the code.

**Shipper ships it.**
Tests pass, changelog generated, version bumped, PR created. Done properly.

**Retro captures learnings.**
What worked, what didn't, what to change next time. These learnings are saved to project memory so the team gets better with every sprint.

---

### Step 4 — Find your output files

After the run, look in `.agency-workspace/`:

```bash
ls .agency-workspace/
```

You'll see one file per agent — the strategist's brief, the spec, the architecture, the code, the review, the test results, the ship report, and the retro.

---

### Step 5 — Read the project memory

```bash
cat .claude/project-memory.md
```

This file has three sections:

- **Current State** — what's true right now: the stack, status, live URL. Overwritten each run.
- **Active Decisions** — open questions that still need answers.
- **History** — what happened in each run, newest first. Never deleted.

Each agent also keeps its own memory in `.claude/memory/[agent].md`.

**This is important.** Next time you run `/agency-run`, the team reads these files first. It won't repeat work or ask you to re-explain the stack.

---

## Common situations

**"I don't know what to build."**
Start with the strategist — it asks the right questions:
```
/strategist DIAGNOSE I want to build something for {your domain}
```

**"I have an idea but I'm not sure it's good."**
Let the strategist challenge it:
```
/strategist CHALLENGE My idea is to build {your idea}
```

**"I have existing code. Can the team work with it?"**
Yes. Run:
```
/agency-run FULL Review the existing codebase and add user authentication
```

**"Something is broken and I don't know why."**
Use the investigator — it finds root causes, not symptoms:
```
/investigator INVESTIGATE — here's the error: [paste error]
```

**"I just need to know if my app is secure."**
```
/security LAUNCH-AUDIT
```

**"I need to pause and come back tomorrow."**
```
/context-manager SAVE
```
Tomorrow:
```
/context-manager RESTORE
```

**"I don't know which agent I need."**
```
/architect DIAGNOSE — [describe your situation]
```

---

## What the agents won't do

- They won't buy a domain or set up hosting accounts — but DevOps can deploy to Vercel and Cloudflare Workers.
- They won't make product decisions — the strategist challenges your decisions, but you're always in control.
- They won't remember things outside of the memory files.

---

## Three rules to remember

1. **Start with strategy or architecture** before writing code — the most common mistake is coding before understanding the system.
2. **Read ETHOS.md** — it explains the three principles every agent follows: Do the Complete Thing, Investigate Before Acting, Builder Sovereignty.
3. **Use context-manager SAVE** before ending a long session — so you can resume tomorrow without losing context.

---

## Glossary of terms you'll hear the agents use

| Term | What it means |
|---|---|
| Auth | How users log in and prove who they are |
| API | The interface between your frontend and your database |
| Unit test | Code that automatically checks if a function works correctly |
| Edge case | An unusual input that breaks things (empty form, wrong type, etc.) |
| Acceptance criteria | Specific conditions that must be true for a feature to be "done" |
| Threat model | A map of who might attack your app and how |
| OWASP Top 10 | The 10 most common security vulnerabilities in web apps |
| STRIDE | A framework for categorizing security threats (Spoofing, Tampering, etc.) |
| Tech stack | The combination of tools used to build the app (Next.js, PostgreSQL, etc.) |
| Schema | The structure of your database — what tables and columns exist |
| JWT | A type of login token that proves a user is authenticated |
| Refactor | Rewriting code to be cleaner without changing what it does |
| Sprint | A focused period of work with a clear goal and defined end |
| Retro | A meeting after a sprint to discuss what worked and what didn't |
| Handoff contract | The agreement between agents about what output is required |
| Root cause | The underlying reason something broke (not just the symptom) |
| Review army | The 7 specialist reviewers that check code from different angles |

---

## Next steps after your first run

1. Read the strategist's brief — understand why this is worth building
2. Read the spec — understand what exactly is being built
3. Read the architecture — understand how the system is designed
4. Read the review — understand what the reviewers found
5. Read the retro — understand what to do better next time
6. Run `/agency-run` again with the next feature when you're ready

The team is already hired. They just need a task.

---

Built by [Navox Labs](https://navox.tech)
