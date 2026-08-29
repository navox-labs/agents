# Unattended Operation

How to run a sprint while you are away from your desk — and what happens when something goes wrong at 3am with nobody watching.

---

## The laptop question

**Navox runs where you run it.** The Python SDK and Claude Code both execute as local processes. If the laptop is asleep, shut, or off, nothing runs. There is no hosted Navox service.

That leaves four honest options.

| Option | Runs with the laptop off? | Cost | Setup | Best for |
|---|---|---|---|---|
| **Keep the laptop awake** | No — awake and plugged in | £0 | `caffeinate -dimsu` | An overnight run you will check in the morning |
| **Cloud VM** | **Yes** | ~$5–20/mo | 30 min | Multi-day autonomous builds. **Recommended** |
| **GitHub Actions** | **Yes** | Free tier, then per-minute | 20 min | Scheduled or PR-triggered sprints |
| **Both** | Yes | — | — | VM for long chains, Actions for CI self-healing |

### Keeping a Mac awake

```bash
caffeinate -dimsu navox run --mode mobile --task "M1: identity firewall"
```

`-d` display, `-i` idle, `-m` disk, `-s` on AC power, `-u` user-active. The lid must stay open unless an external display is attached. This is the fragile option — a system update reboot kills the run. The journal means you resume rather than restart, but nothing runs while nobody notices.

### Cloud VM — the recommended path

Any small always-on Linux box. Fly.io, Hetzner, and a t4g.small all work; 2 vCPU and 4GB is comfortable.

```bash
# on the VM
git clone https://github.com/nahrinoda/waytress-dev.git && cd waytress-dev
pip install navox
cp .env.example .env    # fill in the keys from the access checklist

# survive SSH disconnect
tmux new -s build
navox run --mode mobile --task "M1: identity firewall per docs/waytress-build-spec.md"
# Ctrl-B then D to detach; tmux attach -t build to come back
```

For a chain of milestones, run it under systemd so it restarts on reboot rather than dying silently.

The journal (`.navox/journal.json`) is content-addressed, so a killed run resumes from the last completed step instead of re-spending on work already done. Reboots are survivable. Losing the machine is not — commit and push between milestones.

---

## Notifications — how you find out

Configured entirely by environment variable. No secrets in the repo.

```bash
# Real-time. One POST, no OAuth, instant on your phone.
export NAVOX_TELEGRAM_BOT_TOKEN=...      # from @BotFather
export NAVOX_TELEGRAM_CHAT_ID=...        # from @userinfobot

# Optional: searchable archive
export NAVOX_SLACK_WEBHOOK_URL=...

# Optional: daily digest
export NAVOX_SMTP_URL=smtp://user:pass@smtp.example.com:587
export NAVOX_DIGEST_EMAIL=you@example.com

export NAVOX_NOTIFY_LEVEL=milestones     # all | milestones | urgent
```

| Level | You receive |
|---|---|
| `all` | Every agent step as it completes. Noisy; useful on the first run |
| `milestones` | Chain start and finish, gates, escalations, budget warnings. **Default** |
| `urgent` | Gates, escalations, and budget only |

Escalations and gates always carry the exact question and the valid replies, so you can unblock a run from a phone without opening a laptop.

A dead webhook never kills a sprint. Delivery failures are logged and the chain continues.

---

## Budget caps

An advisory token budget is not a budget. When nobody is at the desk, the counter is the only thing between a looping agent and a large bill.

```bash
export NAVOX_BUDGET_USD=25          # hard cap for one chain run
export NAVOX_BUDGET_TOKENS=5000000  # optional secondary cap
export NAVOX_BUDGET_ACTION=halt     # halt | warn
```

You are notified at 50%, 75%, and 90%. At 100% with `halt`, the chain stops and sends an escalation offering `RAISE BUDGET: <usd>` or `STOP`. Spend is metered per step and charged by model tier; prices live in one table in `sdk/navox/budget.py`.

---

## Parallel isolation

Parallel agents sharing one checkout is the most common way an autonomous run corrupts itself: two agents write the same file, the second silently wins, and nothing reports a conflict because there was no merge.

`sdk/navox/worktree.py` gives each parallel agent its own git worktree. Branches merge deliberately, and **a merge conflict raises rather than resolves**. Auto-resolving conflicts unattended is how you lose work you cannot recover.

```python
from navox.worktree import WorktreeManager, MergeConflict

mgr = WorktreeManager(repo=".")
mgr.reap()                                  # clean up any previous run
with mgr.isolated("mobile") as wt:
    ...                                     # agent works in wt.path
    wt.commit_all("mobile: M3 rooms")
try:
    mgr.merge(wt)
except MergeConflict as e:
    notifier.escalation("worktree", str(e), ["RESOLVE MANUALLY", "DISCARD"])
```

---

## What still stops for you

Autonomy is not the absence of judgment. These always escalate and wait:

1. A hard gate in the sprint chain (`strategy`, `architecture`, `plan`, `device`, `security`, `privacy`)
2. Any agent self-escalation
3. Budget cap reached
4. A merge conflict between parallel agents
5. Any destructive command matched by the interception patterns in `hitl.md`

Everything else proceeds, journals, and notifies.

---

## A realistic first run

```bash
export NAVOX_NOTIFY_LEVEL=all      # watch the first one closely
export NAVOX_BUDGET_USD=10         # start small
navox run --mode mobile --task "M0: foundation per docs/waytress-build-spec.md"
```

Watch it end to end once. Then raise the budget, drop the level to `milestones`, and let the next milestone run while you are away.
