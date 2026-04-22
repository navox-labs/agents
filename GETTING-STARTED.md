# Your first engineering team

You just got access to a team of 8 specialist AI agents who work for you, inside Claude Code, for free.

This guide explains who they are, how a real engineering team works, and how to use them — even if you've never worked with other engineers before.

---

## First: how a real engineering team works

When a company builds software, no single person does everything. Different people own different parts of the work. Here's the typical order:

**1. Someone designs the system first**
Before anyone writes code, an architect figures out how everything fits together. What's the database? How does auth work? What's the API structure? Without this, everyone builds different things that don't connect.

**2. A designer specifies what users see**
A UX designer maps out every screen — not just what it looks like, but every state (loading, error, empty, success). Developers can't build what hasn't been drawn.

**3. Security reviews the plan before code is written**
Fixing a security hole after shipping is 10x harder than catching it in the design. Security engineers review the plan while it's still easy to change.

**4. Engineers build from the spec**
Developers write code based on what the architect designed and what the UX designer specified. They don't invent the structure — they implement it.

**5. QA breaks it before users do**
A QA engineer tries every edge case, every wrong input, every unhappy path. They find what developers missed.

**6. Security audits the code before launch**
A final check — does the actual code match the security model? Are there vulnerabilities in the implementation?

**7. The team signs off and you ship**

This is the process. Without it, you get: code that doesn't scale, UX decisions made by developers, security holes, bugs that reach users, and a codebase nobody understands three months later.

---

## What these agents are

Each agent is a specialist who owns one part of that process:

| | Agent | Real-world equivalent | Their job |
|---|---|---|---|
| 🏗️ | Architect | Principal Engineer | Designs the system before code is written |
| 🎨 | UX | Product Designer | Specifies every screen, state, and interaction |
| ⚙️ | Full Stack | Senior Developer | Writes production code with tests |
| 🚀 | DevOps | DevOps Engineer | CI/CD, Docker, deploys to production |
| 👁️ | Local Review | Code Reviewer | Starts the app, shows it to you, waits for your approval |
| 🧪 | QA | QA Engineer | Finds everything that can break |
| 🔐 | Security | Security Engineer | Reviews design + audits code before launch |
| 📦 | Installer | Setup Wizard | Helps you discover and install individual agents |

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
mkdir -p ~/.claude/agents ~/.claude/commands ~/.claude/templates
cp -r agents/.claude/agents/* ~/.claude/agents/
cp -r agents/.claude/commands/* ~/.claude/commands/
cp -r agents/templates/* ~/.claude/templates/
```

**Verify it worked:**

```bash
ls ~/.claude/agents/
```

You should see:
```
architect.md  devops.md  fullstack.md  installer.md  local-review.md  qa.md  security.md  ux.md
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

### Step 2 — Tell the team what you're building

Type this in Claude Code (replace the task with your own):

```
/agency-run Build a simple to-do app — users can add, complete, and delete tasks. 
Needs user login. Use Next.js and a database.
```

You don't need to know the tech stack in detail. Just describe what you want to build in plain English.

---

### Step 3 — Watch the team work

The agents will run in this order automatically:

**Architect goes first.**
It reads your request and designs the whole system — which database, how auth works, what the API looks like. You don't need to understand everything it produces. What matters is it makes decisions so the other agents can start.

**UX and Security run at the same time.**
UX designs every screen — login page, main app, error states. Security reviews the architect's plan and flags anything dangerous before code is written.

**Fullstack builds.**
Using everything the Architect and UX produced, the developer writes the actual code with unit tests.

**Local review — your checkpoint.**
After Fullstack builds the code, the app starts automatically in your browser. This is the one step where the team stops and waits for you. You are the only person who can approve it before testing begins. Look at the running app, click around, and then type one of three things:
- `LGTM` — you're happy with what you see, continue to testing
- `FEEDBACK: [what you want changed]` — send it back to Fullstack with your notes, and they'll fix it and show you again
- `STOP` — pause everything so you can fix something yourself

This is your checkpoint. The team waits here until you respond. Nothing moves forward without your say-so.

**QA and Security run at the same time.**
QA tests everything that can break. Security audits the code.

**Security gives the final verdict.**
`APPROVED` — you're good to ship.  
`APPROVED WITH CONDITIONS` — ship after fixing a specific list of things.  
`BLOCKED` — do not ship, here's exactly what needs to change.

---

### Step 4 — Find your output files

After the run, look in `.agency-workspace/`:

```bash
ls .agency-workspace/
```

You'll see one file per agent:

```
architect-design.md        ← the system design
ux-spec.md                 ← every screen and state
security-design-review.md  ← threat model and constraints
fullstack-build.md         ← the code that was written
qa-test-run.md             ← what was tested and what failed
security-launch-audit.md   ← final verdict
```

Open any of these files to read what the agent produced.

---

### Step 5 — Read the project memory

After the run, the team wrote down everything it learned:

```bash
cat .claude/project-memory.md
```

This file has three sections:

- **Current State** — what's true right now: the stack, status, live URL. This gets overwritten each run so it's always accurate.
- **Active Decisions** — open questions that still need answers. Resolved decisions get removed automatically.
- **History** — what happened in each run, newest first. Never deleted — this is the audit trail.

Each agent also keeps its own memory in `.claude/memory/[agent].md` with the same structure.

**This is important.** Next time you run `/agency-run`, the team reads these files first. It won't repeat work. It won't ask you to re-explain the stack. And because current state is separate from history, the team always knows what's true right now vs what happened in the past.

---

## Common situations

**"I don't know what tech stack to use."**  
Just describe what you want to build. The Architect decides the stack and explains why.

**"I have existing code. Can the team work with it?"**  
Yes. Run:
```
/agency-run Review the existing codebase and add user authentication
```
The team reads what's there before making decisions.

**"Something is broken and I don't know why."**  
Skip the full team. Use one agent:
```
fullstack DEBUG — here's the error: [paste error]
```

**"I just need to know if my app is secure before I show it to anyone."**  
```
security LAUNCH-AUDIT
```
It audits what's there and gives you a verdict.

**"I don't know which agent I need."**  
```
architect DIAGNOSE — [describe your situation]
```
The Architect reads your situation and tells you exactly which agents to use and in what order.

---

## What the agents won't do

- They won't buy a domain or set up hosting accounts — but the DevOps agent can deploy your app to platforms like Vercel and Cloudflare Workers if you ask.
- They won't make product decisions — they build what you tell them to build.
- They won't remember things you told them outside of Claude Code or outside of the memory files.

---

## One rule to remember

**Always start with the Architect before you write any code yourself.**

The most common mistake junior engineers make is opening a code file and starting to type before understanding the full system. You end up with code that works in isolation but doesn't connect to anything else, auth bolted on at the end, and a structure that breaks when the app grows.

The Architect exists to prevent that. Let it design first. Then build.

---

## Glossary of terms you'll hear the agents use

| Term | What it means |
|---|---|
| Auth | How users log in and prove who they are |
| API | The interface between your frontend and your database |
| Unit test | Code that automatically checks if a function works correctly |
| Edge case | An unusual input that breaks things (empty form, wrong type, etc.) |
| Threat model | A map of who might attack your app and how |
| OWASP Top 10 | The 10 most common security vulnerabilities in web apps |
| Tech stack | The combination of tools used to build the app (Next.js, PostgreSQL, etc.) |
| Schema | The structure of your database — what tables and columns exist |
| JWT | A type of login token that proves a user is authenticated |
| Refactor | Rewriting code to be cleaner without changing what it does |

---

## Next steps after your first run

1. Read `architect-design.md` — understand how the system was designed
2. Read `ux-spec.md` — understand what every screen should look like
3. Read `security-launch-audit.md` — fix anything marked BLOCKED before shipping
4. Run `/agency-run` again with the next feature when you're ready

The team is already hired. They just need a task.

---

Built by [Navox Labs](https://navox.tech)
