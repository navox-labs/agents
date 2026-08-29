"""Hard spend caps for unattended runs.

An advisory token budget is not a budget. When nobody is at the desk, the
only thing standing between a looping agent and a five-figure bill is a
counter that can stop the chain. This module is that counter.

Competitor parity note: Cursor prompts for a spend limit before the first
cloud agent runs; Devin meters each child session and can terminate it.
Navox enforces the same idea at the chain level.

Environment:
    NAVOX_BUDGET_USD        Hard cap for one chain run (default: 25.00)
    NAVOX_BUDGET_TOKENS     Optional hard cap on total tokens
    NAVOX_BUDGET_ACTION     halt | warn   (default: halt)
"""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass

logger = logging.getLogger("navox.budget")


class BudgetExceeded(RuntimeError):
    """Raised to stop a chain when the cap is reached."""


@dataclass(frozen=True)
class Price:
    """USD per million tokens."""

    input_per_mtok: float
    output_per_mtok: float


# Prices are declared per model tier, not per dated model id, so that a model
# refresh touches one table. Verify against current published pricing before a
# long unattended run — these are the defaults, not a source of truth.
TIER_PRICES: dict[str, Price] = {
    "opus": Price(input_per_mtok=15.0, output_per_mtok=75.0),
    "sonnet": Price(input_per_mtok=3.0, output_per_mtok=15.0),
    "haiku": Price(input_per_mtok=0.80, output_per_mtok=4.0),
}

_DEFAULT_TIER = "sonnet"


def tier_for_model(model: str) -> str:
    m = (model or "").lower()
    for tier in ("opus", "sonnet", "haiku"):
        if tier in m:
            return tier
    return _DEFAULT_TIER


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    price = TIER_PRICES[tier_for_model(model)]
    return (
        input_tokens / 1_000_000 * price.input_per_mtok
        + output_tokens / 1_000_000 * price.output_per_mtok
    )


class Budget:
    """Thread-safe running total with warning thresholds and a hard stop.

    Thread safety matters: parallel groups charge concurrently.
    """

    WARN_AT = (50, 75, 90)

    def __init__(
        self,
        cap_usd: float | None = None,
        cap_tokens: int | None = None,
        action: str | None = None,
        notifier=None,
    ):
        self.cap_usd = cap_usd if cap_usd is not None else float(
            os.environ.get("NAVOX_BUDGET_USD", "25.0")
        )
        env_tokens = os.environ.get("NAVOX_BUDGET_TOKENS")
        self.cap_tokens = cap_tokens if cap_tokens is not None else (
            int(env_tokens) if env_tokens else None
        )
        self.action = (action or os.environ.get("NAVOX_BUDGET_ACTION", "halt")).lower()
        self.notifier = notifier

        self.spent_usd = 0.0
        self.tokens = 0
        self._warned: set[int] = set()
        self._lock = threading.Lock()

    @property
    def pct(self) -> int:
        if self.cap_usd <= 0:
            return 0
        return int(self.spent_usd / self.cap_usd * 100)

    @property
    def remaining_usd(self) -> float:
        return max(0.0, self.cap_usd - self.spent_usd)

    def charge(self, model: str, input_tokens: int, output_tokens: int) -> None:
        """Record spend. Raises BudgetExceeded when the cap is hit and action=halt."""
        with self._lock:
            self.spent_usd += cost_usd(model, input_tokens, output_tokens)
            self.tokens += input_tokens + output_tokens
            pct = self.pct
            crossed = [t for t in self.WARN_AT if pct >= t and t not in self._warned]
            for t in crossed:
                self._warned.add(t)
            over = (
                self.spent_usd >= self.cap_usd
                or (self.cap_tokens is not None and self.tokens >= self.cap_tokens)
            )

        for t in crossed:
            logger.warning("budget: %d%% consumed ($%.2f/$%.2f)", t, self.spent_usd, self.cap_usd)
            if self.notifier:
                self.notifier.budget_warning(self.spent_usd, self.cap_usd, t)

        if over:
            msg = (
                f"Budget cap reached: ${self.spent_usd:.2f} of ${self.cap_usd:.2f} "
                f"({self.tokens:,} tokens)"
            )
            logger.error("budget: %s", msg)
            if self.action == "halt":
                raise BudgetExceeded(msg)

    def summary(self) -> dict:
        return {
            "spent_usd": round(self.spent_usd, 4),
            "cap_usd": self.cap_usd,
            "pct": self.pct,
            "tokens": self.tokens,
            "action": self.action,
        }
