"""Git worktree isolation for parallel agents.

Parallel agents editing one checkout is the most common way an autonomous
run corrupts itself: two agents write the same file, the second overwrites
the first, and nothing reports a conflict because there was no merge.

Codex ships worktrees for exactly this reason. Navox now does too. Each
parallel agent gets its own checkout of the same repository, works in
isolation, and its branch is merged deliberately — with conflicts surfaced
as an escalation rather than silently resolved.

Nothing here resolves a conflict automatically. A conflict is a human
decision, and pretending otherwise is how autonomous systems lose work.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("navox.worktree")


class WorktreeError(RuntimeError):
    pass


class MergeConflict(WorktreeError):
    """Raised when a worktree branch cannot be merged cleanly.

    This is always an escalation. Never auto-resolve.
    """

    def __init__(self, branch: str, files: list[str]):
        self.branch = branch
        self.files = files
        super().__init__(
            f"Merge conflict on {branch} in {len(files)} file(s): {', '.join(files[:5])}"
        )


def _git(args: list[str], cwd: Path) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise WorktreeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


@dataclass
class Worktree:
    path: Path
    branch: str
    repo: Path

    def diff_stat(self) -> str:
        return _git(["diff", "--stat", "HEAD"], self.path)

    def has_changes(self) -> bool:
        return bool(_git(["status", "--porcelain"], self.path))

    def commit_all(self, message: str) -> str | None:
        if not self.has_changes():
            return None
        _git(["add", "-A"], self.path)
        _git(["commit", "-m", message], self.path)
        return _git(["rev-parse", "HEAD"], self.path)


class WorktreeManager:
    """Creates and reaps isolated checkouts under .navox/worktrees/."""

    def __init__(self, repo: str | Path = ".", root: str | Path = ".navox/worktrees"):
        self.repo = Path(repo).resolve()
        self.root = (self.repo / root) if not Path(root).is_absolute() else Path(root)
        if not (self.repo / ".git").exists():
            raise WorktreeError(f"Not a git repository: {self.repo}")

    def create(self, agent_id: str, base: str = "HEAD") -> Worktree:
        self.root.mkdir(parents=True, exist_ok=True)
        branch = f"navox/{agent_id}"
        path = self.root / agent_id
        if path.exists():
            self.remove(agent_id)
        _git(["worktree", "add", "-B", branch, str(path), base], self.repo)
        logger.info("worktree: created %s at %s", branch, path)
        return Worktree(path=path, branch=branch, repo=self.repo)

    def merge(self, wt: Worktree, into: str = "HEAD") -> str:
        """Merge a worktree branch back. Raises MergeConflict — never resolves one."""
        proc = subprocess.run(
            ["git", "merge", "--no-ff", "--no-edit", wt.branch],
            cwd=self.repo, capture_output=True, text=True,
        )
        if proc.returncode != 0:
            conflicted = _git(["diff", "--name-only", "--diff-filter=U"], self.repo)
            files = [f for f in conflicted.splitlines() if f]
            subprocess.run(["git", "merge", "--abort"], cwd=self.repo,
                           capture_output=True, text=True)
            raise MergeConflict(wt.branch, files)
        return _git(["rev-parse", "HEAD"], self.repo)

    def remove(self, agent_id: str) -> None:
        path = self.root / agent_id
        subprocess.run(["git", "worktree", "remove", "--force", str(path)],
                       cwd=self.repo, capture_output=True, text=True)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)

    def reap(self) -> None:
        """Remove every navox worktree. Safe to call on startup."""
        subprocess.run(["git", "worktree", "prune"], cwd=self.repo,
                       capture_output=True, text=True)
        if self.root.exists():
            for child in self.root.iterdir():
                if child.is_dir():
                    self.remove(child.name)

    @contextmanager
    def isolated(self, agent_id: str, base: str = "HEAD"):
        wt = self.create(agent_id, base)
        try:
            yield wt
        finally:
            pass  # branches persist for inspection; call reap() to clean up
