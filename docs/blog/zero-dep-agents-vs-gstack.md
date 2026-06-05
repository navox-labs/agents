# I Rebuilt gstack's Workflow in Zero-Dependency Markdown

gstack is the most popular AI agent framework right now — 107k stars, built by Y Combinator's CEO, and for good reason. It turns Claude Code into a full engineering team with 40+ skills covering everything from strategy to shipping.

But it requires Bun, Playwright, TypeScript, and a compile step. I wanted the same depth with none of the overhead.

So I built Navox Agents: 15 specialist AI agents that cover the complete sprint cycle — Think, Plan, Build, Review, Test, Ship, Reflect — in pure markdown with zero dependencies.

Here's what I learned, and why the zero-dependency constraint actually makes the agents better.

---

## The setup comparison

**gstack:**
```bash
git clone --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup
# Requires: Bun runtime, compiles Playwright binary, 1000+ files
```

**Navox Agents:**
```
/plugin install navox-agents
```

That's it. No runtime. No compile step. No binary. 30 seconds and you have 15 agents.

Or if you want to customize:
```bash
git clone https://github.com/navox-labs/agents.git
cd agents && bash scripts/setup.sh
```

---

## What each project covers

| Phase | gstack | Navox Agents |
|---|---|---|
| Strategy | /office-hours (YC-style) | /strategist (agnostic, anti-sycophancy) |
| Specification | /spec | /spec-writer (7-section format) |
| Architecture | /plan-eng-review | /architect (DIAGNOSE + DESIGN + ENG-REVIEW) |
| Design | /design-consultation | /ux (FLOW + WIREFRAME + DESIGN + SPEC + AUDIT) |
| Build | (manual) | /fullstack (BUILD + REFACTOR + DEBUG) |
| Investigation | /investigate | /investigator (INVESTIGATE + AUTOPSY + TRACE) |
| Code Review | /review (review army) | /reviewer (7-specialist parallel army) |
| Testing | /qa (browser-based) | /qa (TEST-PLAN + TEST-RUN + BROWSER + REPORT) |
| Security | /cso | /security (OWASP Top 10 + STRIDE audit) |
| Deployment | /land-and-deploy | /devops (DEPLOY + CANARY) |
| Shipping | /ship | /shipper (tests + changelog + version + PR) |
| Retrospective | /retro | /retro (learnings persist to project memory) |
| Context | /context-save | /context-manager (SAVE + RESTORE + LIST) |

Both cover the full cycle. The difference is how.

---

## Why zero dependencies matters

### 1. Nothing breaks when upstream changes

gstack depends on Bun, Playwright, ngrok, and huggingface transformers. When any of these release a breaking change, gstack breaks. When Bun changes its compile API, the setup script breaks. When Playwright updates its browser binary format, QA breaks.

Navox Agents depends on nothing. The agents are markdown files. They work today, they'll work in 5 years.

### 2. You can read and modify everything

gstack's SKILL.md files are generated from .tmpl templates through a TypeScript build pipeline with 15+ template resolvers. Want to change how the review army works? You need to find the right resolver, understand the template syntax, modify it, and recompile.

Navox Agents are raw markdown. Want to change the review army? Open `.claude/agents/reviewer.md`. Edit it. Done.

### 3. Install friction kills adoption

Every dependency is a reason someone doesn't install your tool. "I need to install Bun first? Never mind." Developer tools live and die by their install experience. `git clone && bash setup.sh` beats `git clone && install runtime && compile binary && register skills`.

### 4. Multi-platform is trivial

Because the agents are just markdown files, supporting new platforms is a copy operation. Our setup script supports Claude Code, Cursor, Copilot CLI, and Codex — with one bash script, no platform-specific code.

gstack supports 10 platforms too, but needs a TypeScript host configuration per platform with typed feature flags and suppressed resolver lists.

---

## What gstack does better (honest assessment)

**Browser-based QA.** gstack bundles a persistent headless Chromium daemon. When `/qa` runs, it opens a real browser, clicks through flows, and catches visual bugs. Our QA agent does code-level testing and delegates browser testing to whatever MCP browser the user has installed. If you need integrated browser QA, gstack wins here.

**Template reuse at scale.** With 40+ skills, gstack needs a build pipeline to avoid copy-pasting shared blocks. At 15 agents, we can maintain shared content manually. If we hit 40+, we'd need something similar — though probably a bash script, not TypeScript.

**Community.** 107k stars and 80 contributors vs. our small but growing user base. Community compounds — more contributors means more edge cases caught, more prompt refinements, more platform support.

---

## What Navox Agents does better

**Handoff contracts.** Every agent declares what it receives and what it delivers in a structured table. The downstream agent validates the upstream output before starting. gstack skills chain by convention; our agents chain by contract.

**Eval system.** Every agent is scored 0-10 against a quality rubric checking: frontmatter completeness, mode coverage, anti-hallucination rules, handoff contracts, output format, scope boundaries, memory integration, and more. 14/14 agents pass. gstack has no equivalent quality gate.

**Sprint modes.** One command, three modes:
- `FULL` — 10-step sprint from strategy to retrospective
- `QUICK` — 6-step fast track for small changes
- `HOTFIX` — 3-step investigate-fix-ship for bugs

gstack chains skills manually. Our orchestrator selects the right chain automatically.

**Anti-sycophancy.** Our strategist agent is explicitly designed to push back on bad ideas. It never says "great idea." It asks forcing questions and won't move forward until they're answered. gstack's office-hours skill has anti-sycophancy too, but it's framed around YC-style startup advice. Ours is agnostic — works for side projects, enterprise tools, or anything in between.

**Session persistence.** The context-manager agent creates full snapshots of sprint state — decisions with rationale, files changed, next steps, open questions. Pause on Tuesday, resume on Thursday, and the agent knows exactly where you left off. gstack has context-save too, but ours includes auth state tracking and decision rationale as required fields.

---

## The philosophy difference

gstack's philosophy is "Boil the Lake" — do the complete thing, search before building, user sovereignty. Good principles.

Our philosophy (ETHOS.md) has three similar but differently framed principles:
1. **Do the Complete Thing** — no half-done work
2. **Investigate Before Acting** — understand what exists before changing it
3. **Builder Sovereignty** — AI recommends, humans decide

The difference isn't in the principles — it's in enforcement. Our principles are checked by the eval system. Every agent is scored on whether it references ETHOS.md, has anti-hallucination rules, and includes scope boundaries. Philosophy without enforcement is just a README section.

---

## Try it

```
/plugin marketplace add https://github.com/navox-labs/agents
/plugin install navox-agents
/hire-team
```

Or clone and customize:
```bash
git clone https://github.com/navox-labs/agents.git
cd agents && bash scripts/setup.sh
```

MIT licensed. Zero dependencies. 15 agents. Full sprint cycle.

GitHub: https://github.com/navox-labs/agents
