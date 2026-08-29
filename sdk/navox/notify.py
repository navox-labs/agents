"""Notification fan-out for unattended sprint runs.

The orchestrator can run for hours without a human present. This module is
how the human finds out what happened, and — critically — how they unblock a
run from a phone when an agent escalates.

Design rules:
  1. Never raise into the chain. A dead webhook must not kill a sprint.
  2. Escalations and gates carry the exact question and options, so the
     human can answer in one reply without opening a laptop.
  3. Channels are configured by environment variable only. No secrets in
     the repo, ever.

Environment:
    NAVOX_TELEGRAM_BOT_TOKEN    Telegram bot token from @BotFather
    NAVOX_TELEGRAM_CHAT_ID      Target chat id
    NAVOX_SLACK_WEBHOOK_URL     Slack incoming webhook
    NAVOX_SMTP_URL              smtp://user:pass@host:port
    NAVOX_DIGEST_EMAIL          Recipient for the daily digest
    NAVOX_NOTIFY_LEVEL          all | milestones | urgent   (default: milestones)
"""

from __future__ import annotations

import json
import logging
import os
import smtplib
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.message import EmailMessage
from enum import IntEnum

logger = logging.getLogger("navox.notify")

_TIMEOUT = 10


class Level(IntEnum):
    """Ordered so a configured level admits everything at or above it."""

    ALL = 0
    MILESTONES = 1
    URGENT = 2


_LEVELS = {"all": Level.ALL, "milestones": Level.MILESTONES, "urgent": Level.URGENT}


@dataclass
class Event:
    kind: str
    title: str
    body: str
    level: Level
    urgent: bool = False
    actions: list[str] = field(default_factory=list)
    at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def as_text(self) -> str:
        lines = [f"{'🚨 ' if self.urgent else ''}{self.title}", "", self.body]
        if self.actions:
            lines += ["", "Reply with one of:"] + [f"  • {a}" for a in self.actions]
        return "\n".join(lines).strip()


# ── Channels ──────────────────────────────────────────────────


class Channel:
    name = "channel"

    def enabled(self) -> bool:
        raise NotImplementedError

    def send(self, event: Event) -> None:
        raise NotImplementedError


class TelegramChannel(Channel):
    """Preferred real-time channel: one POST, no OAuth, instant on mobile."""

    name = "telegram"

    def __init__(self) -> None:
        self.token = os.environ.get("NAVOX_TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.environ.get("NAVOX_TELEGRAM_CHAT_ID", "")

    def enabled(self) -> bool:
        return bool(self.token and self.chat_id)

    def send(self, event: Event) -> None:
        payload = json.dumps({
            "chat_id": self.chat_id,
            "text": event.as_text(),
            "disable_notification": not event.urgent,
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{self.token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=_TIMEOUT).read()


class SlackChannel(Channel):
    name = "slack"

    def __init__(self) -> None:
        self.url = os.environ.get("NAVOX_SLACK_WEBHOOK_URL", "")

    def enabled(self) -> bool:
        return bool(self.url)

    def send(self, event: Event) -> None:
        payload = json.dumps({"text": event.as_text()}).encode()
        req = urllib.request.Request(
            self.url, data=payload, headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=_TIMEOUT).read()


class EmailChannel(Channel):
    """Digest channel. Too slow for escalations, right for the daily summary."""

    name = "email"

    def __init__(self) -> None:
        self.smtp_url = os.environ.get("NAVOX_SMTP_URL", "")
        self.to = os.environ.get("NAVOX_DIGEST_EMAIL", "")

    def enabled(self) -> bool:
        return bool(self.smtp_url and self.to)

    def send(self, event: Event) -> None:
        from urllib.parse import urlparse

        u = urlparse(self.smtp_url)
        msg = EmailMessage()
        msg["Subject"] = f"[navox] {event.title}"
        msg["From"] = u.username or "navox@localhost"
        msg["To"] = self.to
        msg.set_content(event.as_text())
        with smtplib.SMTP(u.hostname, u.port or 587, timeout=_TIMEOUT) as s:
            s.starttls()
            if u.username:
                s.login(u.username, u.password or "")
            s.send_message(msg)


# ── Notifier ──────────────────────────────────────────────────


class Notifier:
    """Fan-out to every configured channel. Never raises into the chain."""

    def __init__(self, channels: list[Channel] | None = None, level: str | None = None):
        self.channels = channels if channels is not None else [
            TelegramChannel(), SlackChannel(), EmailChannel()
        ]
        configured = (level or os.environ.get("NAVOX_NOTIFY_LEVEL", "milestones")).lower()
        self.level = _LEVELS.get(configured, Level.MILESTONES)
        self._sent = 0

    @property
    def active(self) -> list[Channel]:
        return [c for c in self.channels if c.enabled()]

    def _emit(self, event: Event) -> None:
        if event.level < self.level:
            return
        for channel in self.active:
            # Digest-only channels stay quiet for routine step traffic.
            if channel.name == "email" and not event.urgent and event.kind == "step":
                continue
            try:
                channel.send(event)
                self._sent += 1
            except (urllib.error.URLError, OSError, smtplib.SMTPException) as e:
                # Rule 1: a dead webhook must never kill a running sprint.
                logger.warning("notify: %s failed: %s", channel.name, e)
            except Exception as e:  # noqa: BLE001 - defensive by design
                logger.warning("notify: %s unexpected failure: %s", channel.name, e)

    # ── Events the orchestrator emits ─────────────────────────

    def step_complete(self, step) -> None:
        icon = "✅" if step.status == "COMPLETE" else "⚠️"
        self._emit(Event(
            kind="step",
            title=f"{icon} {step.agent_id} ({step.mode}) — {step.status}",
            body=(
                f"{step.duration_ms / 1000:.1f}s · {step.model}\n"
                f"tokens in/out: {step.token_usage.get('input_tokens', 0)}/"
                f"{step.token_usage.get('output_tokens', 0)}"
                + (f"\nerror: {step.error}" if step.error else "")
            ),
            level=Level.ALL,
        ))

    def gate_reached(self, gate: str, question: str) -> None:
        self._emit(Event(
            kind="gate",
            title=f"Gate: {gate}",
            body=question,
            level=Level.URGENT,
            urgent=True,
            actions=["APPROVED", "REVISION NEEDED: <notes>"],
        ))

    def escalation(self, agent: str, reason: str, options: list[str] | None = None) -> None:
        self._emit(Event(
            kind="escalation",
            title=f"{agent} stopped and needs a decision",
            body=reason,
            level=Level.URGENT,
            urgent=True,
            actions=options or [],
        ))

    def budget_warning(self, spent_usd: float, cap_usd: float, pct: int) -> None:
        self._emit(Event(
            kind="budget",
            title=f"Budget {pct}% consumed",
            body=f"${spent_usd:.2f} of ${cap_usd:.2f}. The run halts at the cap.",
            level=Level.URGENT,
            urgent=pct >= 90,
        ))

    def chain_complete(self, result) -> None:
        s = result.summary()
        self._emit(Event(
            kind="chain",
            title=("✅ Sprint complete" if result.ok else "❌ Sprint interrupted")
                  + f" — {s['sprint_mode'].upper()}",
            body=(
                f"{s['task']}\n\n"
                f"steps: {s['completed']}/{s['total_steps']} complete, "
                f"{s['cached']} cached, {s['failed']} failed\n"
                f"duration: {s['total_duration_ms'] / 60000:.1f} min\n"
                f"tokens: {s['total_tokens']:,}"
                + (f"\n\ninterrupted: {result.interrupt_reason}" if result.interrupted else "")
            ),
            level=Level.MILESTONES,
            urgent=not result.ok,
        ))
