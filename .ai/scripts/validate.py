#!/usr/bin/env python3
"""Consistency checks for the .ai/ operating system.

Not a full guarantee of correctness — a script can't judge whether reasoning is
recorded well. It catches the mechanical drift that causes this kind of system to
rot: files referenced in FILE_INDEX.md that no longer exist, session files missing
from SESSION_LOG.md, and an empty sessions/ directory despite SESSION_LOG.md having
rows.

Usage: python3 .ai/scripts/validate.py
Exit code 0 = clean, 1 = issues found (advisory today; wire into CI later per
README.md's "Future improvements" once the project wants this as a hard gate).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

AI_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = AI_DIR.parent

issues: list[str] = []


def check_file_index_paths() -> None:
    """Every backtick-quoted path in FILE_INDEX.md that looks like a real file
    should exist, unless its row says deleted/deprecated."""
    file_index = AI_DIR / "FILE_INDEX.md"
    if not file_index.exists():
        issues.append("FILE_INDEX.md is missing entirely.")
        return

    text = file_index.read_text()
    # crude but effective: pull backtick-quoted tokens that look like paths
    path_re = re.compile(r"`([\w./-]+\.[\w]+)`")
    tracked_extensions = (".md", ".yml", ".yaml", ".toml", ".txt", ".py")
    for line in text.splitlines():
        if "deleted" in line.lower() or "deprecated: yes" in line.lower():
            continue
        for match in path_re.finditer(line):
            candidate = match.group(1)
            # skip things that are clearly examples/placeholders, not real paths
            if candidate.startswith(("path/to/", "<", "NNNN")):
                continue
            if not candidate.endswith(tracked_extensions):
                continue

            if "/" in candidate:
                # has a directory component — resolve relative to repo root
                if (REPO_ROOT / candidate).exists():
                    continue
                msg = f"FILE_INDEX.md references '{candidate}' but it does not exist on disk."
                issues.append(msg)
            else:
                # bare filename (e.g. "README.md" meaning ".ai/README.md") — the
                # index doesn't say which directory, so accept a match anywhere
                # in the repo (excluding heavy/irrelevant dirs) before flagging.
                found = any(
                    True
                    for _ in REPO_ROOT.rglob(candidate)
                    if ".git" not in _.parts and "node_modules" not in _.parts
                )
                if not found:
                    msg = (
                        f"FILE_INDEX.md references '{candidate}' "
                        "but it does not exist anywhere in the repo."
                    )
                    issues.append(msg)


def check_session_log_matches_sessions_dir() -> None:
    """Every file under sessions/ should be referenced in SESSION_LOG.md, and
    vice versa."""
    sessions_dir = AI_DIR / "sessions"
    session_log = AI_DIR / "SESSION_LOG.md"
    if not sessions_dir.exists() or not session_log.exists():
        return

    on_disk = {p.name for p in sessions_dir.glob("*.md")}
    logged_text = session_log.read_text()
    for name in on_disk:
        if name not in logged_text:
            issues.append(f"sessions/{name} exists but is not referenced in SESSION_LOG.md.")

    referenced = set(re.findall(r"sessions/([\w.-]+\.md)", logged_text))
    for name in referenced:
        if name not in on_disk:
            msg = f"SESSION_LOG.md references sessions/{name} but that file does not exist."
            issues.append(msg)


def check_state_tasks_agree_on_milestone() -> None:
    """Best-effort: warn if STATE.md's milestone table marks something DONE
    that TASKS.md's epic table doesn't also mark DONE, or vice versa."""
    state = AI_DIR / "STATE.md"
    tasks = AI_DIR / "TASKS.md"
    if not state.exists() or not tasks.exists():
        return

    state_text = state.read_text()
    tasks_text = tasks.read_text()

    milestone_re = re.compile(r"\|\s*(M\d+(?:\.\d+)?)[^|]*\|\s*\*\*([A-Za-z ]+?)\*\*")
    state_status = {m: s.strip() for m, s in milestone_re.findall(state_text)}

    epic_re = re.compile(
        r"\|\s*E\d+(?:\.\d+)?\s*—[^|]*\|\s*(M\d+(?:\.\d+)?)\s*\|\s*\*\*([A-Za-z ]+?)\*\*"
    )
    tasks_status = {m: s.strip() for m, s in epic_re.findall(tasks_text)}

    for milestone, s_status in state_status.items():
        t_status = tasks_status.get(milestone)
        if t_status is None:
            continue
        s_done = s_status.lower().startswith("done")
        t_done = t_status.lower().startswith("done")
        if s_done != t_done:
            msg = (
                f"STATE.md marks {milestone} as '{s_status}' but "
                f"TASKS.md marks it as '{t_status}' — they disagree."
            )
            issues.append(msg)


def main() -> int:
    check_file_index_paths()
    check_session_log_matches_sessions_dir()
    check_state_tasks_agree_on_milestone()

    if not issues:
        print("OK — no drift detected between .ai/ tracking files and the filesystem.")
        return 0

    print(f"Found {len(issues)} issue(s):\n")
    for issue in issues:
        print(f"  - {issue}")
    print("\nThese are advisory today (see .ai/README.md's Future improvements for CI wiring).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
