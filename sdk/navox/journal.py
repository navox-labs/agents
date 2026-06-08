"""Journal — content-addressed caching for resumable agent chains.

Stores results keyed by a hash of (agent_id, mode, task, context_hash).
On resume, completed steps are skipped. Delete the journal to start fresh.

Pattern from Anthropic's recommended "journaled execution" approach.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class JournalEntry:
    """A single completed step in a sprint chain."""

    key: str
    agent_id: str
    mode: str
    status: str  # COMPLETE, BLOCKED, ERROR, PARSE_ERROR
    raw_output: str
    timestamp: float
    duration_ms: int = 0
    model: str = ""
    token_usage: dict = field(default_factory=dict)
    error: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> JournalEntry:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class Journal:
    """Content-addressed journal for resumable chain execution.

    Usage:
        journal = Journal(path=".navox/journal.json")

        key = journal.make_key("strategist", "DIAGNOSE", "build X", "")
        if journal.has(key):
            entry = journal.get(key)  # Resume from cache
        else:
            result = run_agent(...)
            journal.save(key, entry)
    """

    def __init__(self, path: str | Path = ".navox/journal.json"):
        self.path = Path(path)
        self._entries: dict[str, JournalEntry] = {}
        self._load()

    def _load(self) -> None:
        """Load journal from disk."""
        if not self.path.exists():
            return
        content = self.path.read_text().strip()
        if not content:
            return
        data = json.loads(content)
        for key, entry_data in data.get("entries", {}).items():
            self._entries[key] = JournalEntry.from_dict(entry_data)

    def _save(self) -> None:
        """Persist journal to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": 1,
            "entries": {k: v.to_dict() for k, v in self._entries.items()},
        }
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def make_key(
        agent_id: str,
        mode: str,
        task: str,
        context_hash: str = "",
    ) -> str:
        """Create a content-addressed key for a step.

        Same inputs always produce the same key. This means re-running
        the same chain with the same task resumes from where it left off.
        """
        content = f"{agent_id}:{mode}:{task}:{context_hash}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def has(self, key: str) -> bool:
        """Check if a step has been completed."""
        entry = self._entries.get(key)
        if not entry:
            return False
        # Only consider successful completions as cached
        return entry.status in ("COMPLETE",)

    def get(self, key: str) -> JournalEntry | None:
        """Retrieve a completed step."""
        return self._entries.get(key)

    def save(self, key: str, entry: JournalEntry) -> None:
        """Save a completed step and persist to disk."""
        self._entries[key] = entry
        self._save()

    def clear(self) -> None:
        """Clear all entries and delete journal file."""
        self._entries.clear()
        if self.path.exists():
            self.path.unlink()

    @property
    def entries(self) -> list[JournalEntry]:
        """All entries in chronological order."""
        return sorted(self._entries.values(), key=lambda e: e.timestamp)

    def summary(self) -> dict:
        """Summary stats for the journal."""
        entries = self.entries
        if not entries:
            return {"total": 0, "completed": 0, "failed": 0}

        return {
            "total": len(entries),
            "completed": sum(1 for e in entries if e.status == "COMPLETE"),
            "failed": sum(1 for e in entries if e.status in ("ERROR", "BLOCKED", "PARSE_ERROR")),
            "total_duration_ms": sum(e.duration_ms for e in entries),
            "total_tokens": sum(
                e.token_usage.get("input_tokens", 0) + e.token_usage.get("output_tokens", 0)
                for e in entries
            ),
        }
