# Navox Agents — Maximum Visibility Plan

**Context:** Solo founder, 13 GitHub stars, 1 karma everywhere, 15 agents scoring 10/10, 210/210 validation checks, zero dependencies. Competing in a space where the top player has 211K stars.

**Core positioning:** The only Claude Code agent plugin with a measurable reliability score. Not the most agents. Not the most features. The most reliable.

---

## The Competitive Landscape

### Tier 1: Mega repos (50K+ stars)

| Competitor | Stars | What they offer |
|---|---|---|
| affaan-m/ECC | 211K | 64 agents, 261 skills, 7 harnesses, paid Pro tier ($19/seat/mo), GitHub App, weekly releases |
| anthropics/skills | 148K | Official Anthropic skills registry and reference implementation |
| anthropics/claude-code | 131K | Official Claude Code repo |
| garrytan/gstack | 108K | 23 skills, browser automation, iOS testing, 10+ harnesses. Celebrity founder (YC president). 10K stars in 48 hours. |
| farion1231/cc-switch | 95.2K | Cross-platform desktop assistant for Claude Code, Codex |
| thedotmack/claude-mem | 81.3K | Persistent context across agent sessions. Active X account, Discord community. |
| shareAI-lab/learn-claude-code | 65.5K | Nano Claude Code-like agent harness |
| ruvnet/ruflo | 58.6K | 98 agents, vector memory (AgentDB), federation layer, web UI, 22.2M ecosystem downloads |
| shanraisshan/claude-code-best-practice | 56.9K | From vibe coding to agentic engineering |

### Tier 2: Major plugins (10K-50K stars)

| Competitor | Stars | What they offer |
|---|---|---|
| hesreallyhim/awesome-claude-code | 46K | Canonical curated list. Submission via issues only. |
| sickn33/antigravity-awesome-skills | 40.1K | 1,500+ skills. Breadth play — covers every platform. |
| wshobson/agents | 36.5K | 112 agents, 72 plugins, 16 orchestrators. Multi-platform. |
| anthropics/claude-plugins-official | 29.7K | Official Anthropic directory. Curated at their discretion. |
| jarrodwatts/claude-hud | 24.7K | Context usage, active tools, running agents dashboard. |
| VoltAgent/awesome-agent-skills | 24.7K | 1,000+ agent skills from official dev teams + community |
| VoltAgent/awesome-claude-code-subagents | 21.4K | 100+ specialized subagents |
| EveryInc/compound-engineering | 20.6K | Compound Engineering plugin. Multi-platform. |
| openai/codex-plugin-cc | 20.5K | Use Codex from within Claude Code |
| alirezarezvani/claude-skills | 17.5K | 337 skills, 30+ agents, 70+ custom commands |
| travisvn/awesome-claude-skills | 13.3K | Curated list of Claude Skills |
| YishenTu/claudian | 12.5K | Obsidian plugin embedding Claude Code |

### Tier 3: Direct competitors (multi-agent teams)

| Competitor | Stars | What they offer |
|---|---|---|
| vijaythecoder/awesome-claude-agents | 4.3K | Orchestrated sub-agent dev team — closest competitor to navox |
| rohitg00/awesome-claude-code-toolkit | 2K | 135 agents, 35 skills, 42 commands, 176+ plugins |
| **navox-labs/agents** | **13** | **15 agents, 10/10 eval, 210/210 validation, handoff contracts, eval-gated retries** |

**Your edge:** None of these publish a reliability score. None have eval-gated retries. None have handoff contracts between agents. None have 210 automated validation checks. They compete on quantity — you compete on quality.

**Your gap:** 13 stars vs 4.3K for your closest competitor. Distribution is the #1 problem — not product.

---

## The Hard Truth

You're starting from zero in a market where the top player got 10K stars in 48 hours because he's the president of Y Combinator. You cannot out-distribute Garry Tan. You cannot out-breadth wshobson's 112 agents.

What you can do:
1. **Be the reliability standard** — the plugin you install when you actually need agents that don't break
2. **Be everywhere the audience already looks** — directories, lists, communities
3. **Compound credibility through consistency** — build in public, ship weekly, let the work speak

---

## Phase 1: Get Listed (Week 1-2)

These are free, one-time actions that put you where 250K+ developers/month already browse.

### 1.1 Anthropic Community Marketplace
- Run `claude plugin validate` locally
- Submit at `platform.claude.com/plugins/submit` or `claude.ai/settings/plugins/submit`
- Also available via: `clau.de/plugin-directory-submission`
- Automated screening + safety review, approved plugins pinned to commit SHA, catalog syncs nightly
- This is the highest-leverage single action — developers discover plugins here first
- **Goal:** Listed in @claude-community marketplace, installable via `claude plugin install navox-agents@claude-community`

### 1.2 Anthropic Official Directory
- No application process — Anthropic curates at their discretion
- But being in the community marketplace makes you visible to them
- Your 210/210 validation + 10/10 eval scores are exactly the "quality signals" they look for
- **Goal:** Eventually earn "Anthropic Verified" badge

### 1.3 awesome-claude-code (36.8K stars)
- DO NOT open a PR — only Claude (their bot) submits PRs
- Open an issue using their resource submission template
- Position: "15-agent sprint team with eval-gated reliability (210/210 validation, 14/14 agents at 10/10)"
- Link: https://github.com/hesreallyhim/awesome-claude-code/issues
- **Goal:** Listed in the canonical awesome list

### 1.4 Other Directories
Submit to all of these:

| Directory | How to submit |
|---|---|
| ComposioHQ/awesome-claude-plugins | PR with plugin details |
| Chat2AnyLLM/awesome-claude-plugins | PR with plugin details |
| rdmgator12/awesome-claude-plugins | PR — 132 bundles indexed |
| rohitg00/awesome-claude-code-toolkit | PR — 135 agents, 176+ plugins indexed |
| GetBindu/awesome-claude-code-and-skills | PR with plugin details |
| VoltAgent/awesome-claude-code-subagents | PR — 100+ subagents, 21.4K stars |
| VoltAgent/awesome-agent-skills | PR — 1,000+ skills, 24.7K stars |
| travisvn/awesome-claude-skills | PR — 13.3K stars |
| ccplugins/awesome-claude-code-plugins | PR — 824 stars, 150+ plugins across 13 categories |
| claudemarketplaces.com | Submit via their form — 250K+ devs/month |
| claudepluginhub.com | Submit via their form — tracks 30,476+ plugins |
| claudefa.st | Submit via their form |
| aitmpl.com/plugins | Submit via their form |
| skills.sh | Skills discovery platform |

### 1.5 GitHub Topics (do this NOW — 5 minutes)
The `claude-code` topic has 3,000+ repos. navox-labs/agents has NO topics set. Add these immediately via repo Settings > Topics:

```
claude-code, claude-code-plugin, ai-agents, multi-agent, agent-orchestration,
developer-tools, claude-code-agents, open-source, sprint, devtools
```

### 1.6 Your Own awesome-claude-code Fork
You already own `nahrinoda/awesome-claude-code`. Make sure navox-agents is prominently listed there. This fork has 1,157 commits — use it as a distribution channel.

---

## Phase 2: Build Karma (Week 1-4, ongoing)

You have 1 karma everywhere. You cannot post your product on day 1 without getting flagged as spam. Build credibility first.

### 2.1 Reddit (r/ClaudeAI, r/claudedev, r/LocalLLaMA)

**Week 1-2: Give before you take**
- Answer questions about Claude Code setup, plugins, agent configuration
- Share genuinely helpful tips (not your product)
- Comment on posts about agent reliability issues — offer insights without linking
- Target: 50+ karma before any self-promotion

**Week 3+: Share your work**
- Post format: "I built a 15-agent team for Claude Code with a reliability scoring system — here's what I learned"
- Lead with the PROBLEM (agents that hallucinate, break handoffs, produce unreliable output)
- Show the PROOF (10/10 scores, 210/210 validation, eval-gated retries)
- Link to repo at the end, not the beginning
- Never post the same thing to multiple subreddits on the same day

### 2.2 Hacker News

**Show HN format that works:**
```
Show HN: 15 AI agents for Claude Code with eval-gated reliability (all score 10/10)
```

**Timing:** Tuesday-Thursday, 8-10am ET (peak HN traffic)

**What gets traction on HN:**
- Technical depth — explain the handoff contract system, the eval rubric, the validation architecture
- Contrarian angle — "everyone is building more agents, we built fewer agents that actually work"
- Show real output — paste an actual agent run with the XML output format
- Engage in comments for 2-3 hours after posting

**Build HN karma first:**
- Comment thoughtfully on AI/developer tool posts for 2 weeks
- Upvote good content
- Target: 20+ karma before Show HN

### 2.3 IndieHackers

**Post format:** Build log / case study
- "From architect to AI agent builder: how I built a 15-agent engineering team that scores 10/10"
- Personal story resonates on IH — your architecture-to-software journey is compelling
- Show real numbers: 210 validation checks, 14 agents, 3 sprint modes
- The "no VC, no platform, building in public" angle is catnip for this audience

### 2.4 X/Twitter

**Content cadence:** 3-5 posts/week

**What works for dev tools on X:**

| Format | Example |
|---|---|
| Build log thread | "I just shipped v3.0.0 of my AI agent team. 15 agents. All scoring 10/10. Here's how I got there (thread)" |
| Problem/solution | "Most AI agents fail silently. Mine fail loudly. Here's why that matters." |
| Show the proof | Screenshot of eval.sh output — 14/14 passed, all 10/10 |
| Contrarian take | "gstack has 108K stars. But do you know if any of those agents actually work reliably? We score ours." |
| Demo video | 60-second terminal recording of `/agency-run FULL` completing a sprint |

**Hashtags:** #ClaudeCode #BuildInPublic #AIAgents #DevTools #OpenSource

**Engage with:** @AnthropicAI, @alexalbert__, Claude Code community accounts. Don't tag-spam — reply meaningfully to their posts.

---

## Phase 3: Content That Compounds (Week 2-8)

### 3.1 Blog Posts (Dev.to + Hashnode)

Write 4-6 posts. Each one is a distribution event.

| # | Title | Angle |
|---|---|---|
| 1 | "Why I Score My AI Agents (And You Should Too)" | Introduce the eval rubric concept. Novel idea. Shareable. |
| 2 | "Handoff Contracts: The Missing Piece in Multi-Agent Systems" | Technical deep-dive. Positions you as a thinker, not just a builder. |
| 3 | "I Built 15 AI Agents. Here's What I Learned About Reliability." | Lessons learned format. High engagement on Dev.to. |
| 4 | "Claude Code Agents: gstack vs navox vs rolling your own" | Comparison post. Will get search traffic. Be fair — acknowledge gstack's strengths. |
| 5 | "The Solo Founder Sprint: How One Person Ships With 15 AI Agents" | Personal story. IndieHackers cross-post. |
| 6 | "210 Validation Checks: How I Made Sure My AI Agents Don't Break" | Engineering rigor angle. Appeals to senior devs. |

Cross-post every article to: Dev.to, Hashnode, Medium (in that order).

### 3.2 Video Content

| Format | Platform | What |
|---|---|---|
| 60s demo | X, LinkedIn | Terminal recording of a full sprint completing |
| 5-min tutorial | YouTube | "Install navox-agents and run your first sprint" |
| 10-min deep dive | YouTube | "How the eval system works — scoring AI agents for reliability" |
| Comparison | YouTube | "gstack vs navox-agents: which Claude Code plugin should you use?" |

Use `asciinema` or `vhs` for terminal recordings. These perform well on X.

### 3.3 GitHub README Optimization

Your README is the landing page. Optimize for the developer scanning for 10 seconds:

- [ ] Add shields/badges at the top: `agents: 15` | `eval: 10/10` | `validation: 210/210` | `dependencies: 0`
- [ ] Add a 30-second GIF of a sprint running
- [ ] Add "vs gstack" comparison section (you already have this)
- [ ] Add GitHub topics: `claude-code`, `ai-agents`, `claude-code-plugin`, `developer-tools`, `multi-agent`, `agent-orchestration`, `claude-code-agents`
- [ ] Pin the repo on your GitHub profile

---

## Phase 4: Strategic Amplifiers (Week 4-12)

### 4.1 Newsletter Features
Pitch these newsletters that cover AI dev tools:

| Newsletter | Why | How to pitch |
|---|---|---|
| TLDR AI | Large dev audience | Email with 2-line pitch + repo link |
| Ben's Bites | AI tools focus | Show the reliability angle |
| The Pragmatic Engineer | Engineering quality | "Eval-gated AI agents" angle |
| Changelog | Open source focus | Submit to Changelog News |
| Console.dev | Dev tool discoveries | Submit via their form |
| Build to Launch (Substack) | Already reviews Claude plugins | They reviewed "11 plugins, kept 4" — pitch yours |

### 4.2 Conference/Meetup Talks
- Local AI/dev meetups — present "Building Reliable AI Agent Teams"
- AI Engineer Summit, AI Tinkerers — submit CFP
- Virtual: Dev.to AMAs, Reddit AMAs in r/ClaudeAI

### 4.3 Anthropic Relationship
- Engage with Anthropic's Claude Code team on GitHub (issues, discussions)
- If they see consistent quality + community adoption, official directory listing follows
- Their blog/changelog sometimes features community plugins

---

## Phase 5: The Compounding Flywheel

Once you have initial traction (100+ stars, listed in 3+ directories):

```
Content -> Discovery -> Stars -> Social proof -> More content -> More discovery
   ^                                                                    |
   |____________________________________________________________________|
```

**Weekly rhythm:**
- Monday: Ship something (feature, fix, blog post)
- Wednesday: Share on X + Reddit
- Friday: Engage in communities (answer questions, comment on related posts)

**Monthly rhythm:**
- 1 blog post (cross-posted to 3 platforms)
- 1 video (YouTube + X clip)
- 1 directory submission or newsletter pitch
- Run `bash scripts/validate.sh && bash scripts/eval.sh` and screenshot the results

---

## Current Distribution Gaps

Everything below is something every competitor with 1K+ stars has done that navox has not:

- [ ] Not listed on ANY awesome list (0 out of 10+)
- [ ] Not submitted to Anthropic's official or community marketplace
- [ ] No GitHub topics set on the repo
- [ ] No Discord or X/Twitter presence
- [ ] No multi-harness support (competitors support 5-7 platforms)
- [ ] No npx/one-liner install beyond `claude plugin add`
- [ ] No blog posts or content about the project
- [ ] No demo video or GIF in README
- [ ] No shields/badges in README
- [ ] Not tagged in GitHub's `claude-code` topic (3,000+ repos)

Each of these is a concrete, fixable action. The plan below prioritizes them.

---

## Priority Stack (What to Do First)

Ranked by effort-to-impact ratio:

| Priority | Action | Effort | Impact |
|---|---|---|---|
| 1 | Add GitHub topics to repo | 2 min | High — instant search discoverability across 3K+ repos |
| 2 | Submit to Anthropic community marketplace | 30 min | Highest — 250K devs/month browse this |
| 3 | Submit issue to awesome-claude-code (46K stars) | 15 min | High — canonical discovery list |
| 4 | Submit to 10+ other awesome lists (PRs) | 3 hours | High — multiple discovery surfaces |
| 5 | Write first blog post (Dev.to) | 3 hours | Medium — compounds over time |
| 6 | Start Reddit karma building | 30 min/day | Medium — unlocks self-promotion later |
| 7 | Post first X thread with eval screenshot | 1 hour | Medium — visual proof is compelling |
| 8 | Record 60s terminal demo | 1 hour | Medium — reusable across platforms |
| 9 | Show HN post | 1 hour | High but risky — needs karma first |
| 10 | Pitch 3 newsletters | 1 hour | Low effort, potentially high reach |

---

## What NOT to Do

- Don't spam your link in communities before building karma — you'll get banned
- Don't compare yourself to gstack by attacking it — be respectful, acknowledge its strengths, differentiate on reliability
- Don't try to compete on agent count — wshobson has 112, you have 15. Compete on quality.
- Don't pay for promotion, ads, or star-buying services — it's detectable and destroys credibility
- Don't wait until everything is perfect — ship the visibility work alongside the product work
- Don't post the same content on the same day across multiple platforms — stagger by 2-3 days

---

## Success Metrics

| Timeframe | Target |
|---|---|
| Week 2 | Listed in 3+ directories/awesome lists |
| Week 4 | 50+ GitHub stars, 20+ Reddit karma |
| Week 8 | 200+ stars, 1 blog post with 1K+ views, listed in Anthropic community marketplace |
| Week 12 | 500+ stars, Show HN posted, 3+ blog posts published |
| Week 24 | 1K+ stars, newsletter feature, community recognition |

---

## The One-Line Pitch

For every platform, every submission, every bio:

> **15 AI agents for Claude Code. All scoring 10/10. 210 validation checks. Zero dependencies. Your code never leaves your machine.**

That's your hook. Reliability is your brand. Own it.
