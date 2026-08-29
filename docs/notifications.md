# Notifications

`sdk/navox/notify.py` — how an unattended run reaches you.

## Why Telegram is the default recommendation

| Channel | Setup | Latency | Reply from phone | Best use |
|---|---|---|---|---|
| **Telegram** | Bot token + chat id. No OAuth, no app review, no workspace admin | Instant | Yes | **Real-time events and escalations** |
| Slack | Incoming webhook | Instant | Yes | Searchable archive if you want one |
| Email | SMTP url | Minutes | Poorly | Daily digest |

Pick one real-time channel. Running Telegram and Slack together duplicates every alert.

## Events

| Method | Level | Sent when |
|---|---|---|
| `step_complete(step)` | ALL | An agent finishes. Status, duration, model, token counts |
| `gate_reached(gate, q)` | URGENT | A hard gate needs approval. Carries the valid replies |
| `escalation(agent, reason, options)` | URGENT | An agent stopped. Carries the exact question and options |
| `budget_warning(spent, cap, pct)` | URGENT | 50%, 75%, 90% of the cap |
| `chain_complete(result)` | MILESTONES | Sprint ends. Steps, cached, failed, duration, tokens |

## Guarantees

1. **Never raises into the chain.** Every send is wrapped; a dead webhook is logged and the sprint continues.
2. **Escalations are answerable.** Every urgent event includes the question and the valid replies, so a run can be unblocked from a phone.
3. **No secrets in the repo.** Configuration is environment-variable only.

## Setting up a Telegram bot

1. Message `@BotFather`, send `/newbot`, follow the prompts, copy the token.
2. Message `@userinfobot` to get your numeric chat id.
3. Send your bot any message once — a bot cannot open a conversation with you.
4. Export `NAVOX_TELEGRAM_BOT_TOKEN` and `NAVOX_TELEGRAM_CHAT_ID`.

```bash
python -c "from navox.notify import Notifier; n=Notifier(); print([c.name for c in n.active])"
```
