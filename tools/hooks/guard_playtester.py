"""PreToolUse hook: keep the Claude playtester a black box player (docs/process/05_CLAUDE_PLAYTESTER.md).

A playtester sees the game only through tools/playtest/blackbox.py. For the `playtester`
agent (hook input agent_type == "playtester", or this script run with --always from the
agent's own frontmatter) it denies:
  - Read of anything outside .playtest_sessions/, docs/playtest/claude/, the feedback template
    and the agent's own definition (no code, scenes, content, GDD, design docs, git history)
  - Write / Edit outside .playtest_sessions/ and docs/playtest/claude/
  - Bash / PowerShell other than `python <...>/tools/playtest/blackbox.py ...` calls (several
    may be chained with && or ;), and any pipe, redirect or command substitution
  - every other tool (Grep, Glob, Agent, web, ...)
Other agents and the main session pass untouched. Never raises: on a parsing problem it allows
for other agents and denies for the playtester.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
READ_OK = [ROOT / ".playtest_sessions", ROOT / "docs" / "playtest" / "claude",
           ROOT / "docs" / "process" / "templates" / "CLAUDE_PLAYTEST_FEEDBACK.md",
           ROOT / ".claude" / "agents" / "playtester.md"]
WRITE_OK = [ROOT / ".playtest_sessions", ROOT / "docs" / "playtest" / "claude"]
BLACKBOX_CALL = re.compile(r"^\s*python3?(\.exe)?\s+\"?[^\s\"]*tools[\\/]playtest[\\/]blackbox\.py\"?\s+[^|<>`]*$")
SHELL_TRICKS = re.compile(r"[|<>`]|\$\(")


def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": reason}}))


def inside(path: str, roots: list[Path]) -> bool:
    try:
        p = Path(path).resolve()
    except Exception:
        return False
    for r in roots:
        r = r.resolve()
        if p == r or r in p.parents:
            return True
    return False


def check(tool: str, inp: dict) -> str | None:
    """The deny reason for a playtester tool call, or None to allow."""
    if tool == "Read":
        path = str(inp.get("file_path", ""))
        if not inside(path, READ_OK):
            return ("Playtester rule: you are a human player and cannot see the game's files. "
                    "Read only your screenshots, your journal, your brief and the feedback template. "
                    "Learn the game from the screen (blackbox.py shot / move / right-click).")
        return None
    if tool in ("Write", "Edit"):
        path = str(inp.get("file_path", ""))
        if not inside(path, WRITE_OK):
            return "Playtester rule: write only your journal (session folder) and your report (docs/playtest/claude/)."
        return None
    if tool in ("Bash", "PowerShell"):
        cmd = str(inp.get("command", "")).strip()
        parts = [p for p in re.split(r"&&|;|\n", cmd) if p.strip()]
        if not parts or SHELL_TRICKS.search(cmd) or not all(BLACKBOX_CALL.match(p) for p in parts):
            return ("Playtester rule: the only command you run is `python .../tools/playtest/blackbox.py --session <yours> <action>` "
                    "(chain several with &&). No other commands, pipes or redirects: a human tester has only the screen, "
                    "the mouse and the keyboard.")
        return None
    return "Playtester rule: use only blackbox.py (Bash), Read on your screenshots, and Write/Edit on your journal and report."


def main() -> int:
    always = "--always" in sys.argv[1:]
    try:
        data = json.load(sys.stdin)
    except Exception:
        if always:
            deny("Playtester guard could not read the tool call; retry it.")
        return 0
    if not always and str(data.get("agent_type", "")) != "playtester":
        return 0
    reason = check(str(data.get("tool_name", "")), data.get("tool_input", {}) or {})
    if reason:
        deny(reason)
    return 0


if __name__ == "__main__":
    sys.exit(main())
