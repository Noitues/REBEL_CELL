"""PreToolUse hook: enforce the context reading rules (docs/process/01, section 3).

Denies, with a reason that says what to do instead:
  - Read of docs/DECISIONS.md without a line range (offset/limit) or with a range over MAX_LINES
  - Read of any *.log / results.xml / gut.log file without a range, or with a range over MAX_LINES
  - Bash/PowerShell `cat`, `type`, `Get-Content` of those files when the output is not narrowed
    by grep / head / tail / sed -n / Select-String / -TotalCount / -Tail
Everything else is allowed (exit 0, no output). Never raises: on any parsing problem it allows.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import json
import re
import sys

MAX_LINES = 400
BIG_FILES = re.compile(r"(docs[\\/]DECISIONS\.md|docs[\\/]decisions[\\/][^\\/]+\.md|\.log|results\.xml)$", re.I)
NARROWED = re.compile(r"\|\s*(grep|head|tail|sed|awk|wc|rg|Select-String|Select-Object|findstr)\b|\bsed\s+-n\b|-TotalCount\b|-Tail\b|\bgrep\b|\brg\b|\bfindstr\b", re.I)
DUMPER = re.compile(r"\b(cat|type|Get-Content|gc|more|less)\b\s+[^|;&]*" + r"(DECISIONS\.md|decisions[\\/]20[0-9-]+\.md|\.log\b|results\.xml)", re.I)


def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {}) or {}
    if tool == "Read":
        path = str(inp.get("file_path", ""))
        if BIG_FILES.search(path):
            limit = inp.get("limit")
            if limit is None or int(limit) > MAX_LINES:
                deny(f"Reading rule (docs/process/01 §3): never read {path.replace(chr(92), '/').split('/')[-1]} whole. "
                     f"grep -n for the topic/verdict first, then Read with offset+limit (≤ {MAX_LINES} lines). "
                     "Logs: grep -E '^(import|fast|smoke|validate|tests|parse)=|FAIL|ERROR|ORDER-DEPENDENT|ALONE'.")
    elif tool in ("Bash", "PowerShell"):
        cmd = str(inp.get("command", ""))
        if DUMPER.search(cmd) and not NARROWED.search(cmd):
            deny("Reading rule (docs/process/01 §3): don't dump DECISIONS.md or a log into the context. "
                 "Narrow it: grep -n / grep -E '=|FAIL|ERROR' / tail -n 3 / sed -n a,bp.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
