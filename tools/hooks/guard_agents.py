"""PreToolUse hook on the Agent tool: enforce the agent routing of docs/process/02 mechanically.

Denies, with a reason that says what to do instead:
  - an Agent call without a pinned `subagent_type` (general-purpose / claude / omitted): the
    pinned definitions in .claude/agents/ carry the model and effort the process ruled
  - a `model` override to opus or fable on a Sonnet/Haiku-pinned type, unless the prompt carries a
    line `OPUS-BECAUSE: <reason>` (the reason lands in the gate report's retrospective)
  - a `model` override to fable anywhere (the orchestrator is the only Fable-class context)
  - an `effort` override above the type's pinned level
  - a prompt over MAX_PROMPT_CHARS: briefs reference docs/process/agent_rules/<area>.md and let
    the agent slice; they never inline source or rule blocks
  - more than MAX_WORKTREE_AGENTS agent worktrees alive at once (git worktree list)
Read-only agents (Explore, Plan, claude-code-guide) pass. Never raises: on any problem it allows.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MAX_PROMPT_CHARS = 4000
MAX_WORKTREE_AGENTS = 5
# Pinned types -> (model family allowed without justification, max effort)
PINNED = {
    "fix-visual": ("sonnet", "medium"),
    "fix-mechanical": ("sonnet", "medium"),
    "code-cleanup": ("haiku", "low"),
    "fix-rules": ("opus", "medium"),
    "auditor": ("opus", "medium"),
}
PASS_THROUGH = {"Explore", "Plan", "claude-code-guide", "statusline-setup"}
EFFORT_RANK = {"low": 0, "medium": 1, "high": 2, "xhigh": 3, "max": 4}
FAMILY_RANK = {"haiku": 0, "sonnet": 1, "opus": 2, "fable": 3}


def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))


def live_agent_worktrees() -> int:
    try:
        out = subprocess.run(["git", "worktree", "list"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10, check=False).stdout
    except Exception:
        return 0
    return sum(1 for l in out.splitlines() if "worktree-agent-" in l or "/agent-" in l.replace("\\", "/"))


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") != "Agent":
        return 0
    inp = data.get("tool_input", {}) or {}
    stype = str(inp.get("subagent_type", "") or "")
    model = str(inp.get("model", "") or "").lower()
    effort = str(inp.get("effort", "") or "").lower()
    prompt = str(inp.get("prompt", "") or "")
    if stype in PASS_THROUGH:
        return 0
    if stype not in PINNED:
        deny("Agent routing (docs/process/02 §3): spawn only a pinned type: fix-visual (Sonnet), fix-mechanical (Sonnet), "
             "code-cleanup (Haiku), fix-rules (Opus), auditor (Opus), or a read-only Explore/Plan. "
             f"Got subagent_type={stype or 'none'}. The type carries the model and effort; do not pick them per call.")
        return 0
    fam, max_eff = PINNED[stype]
    if model:
        m = next((f for f in FAMILY_RANK if f in model), "")
        if m == "fable":
            deny("Agent routing: no Fable-class sub-agents; the orchestrator is the only Fable context (and should itself run on Opus for orchestration).")
            return 0
        if m and FAMILY_RANK[m] > FAMILY_RANK[fam] and not re.search(r"^OPUS-BECAUSE:\s*\S", prompt, re.M):
            deny(f"Agent routing: {stype} is pinned to {fam}. To use {m} add a line 'OPUS-BECAUSE: <reason>' to the brief; "
                 "the reason is reported in the gate retrospective. Otherwise drop the model override.")
            return 0
    if effort and EFFORT_RANK.get(effort, 0) > EFFORT_RANK[max_eff]:
        deny(f"Agent routing: {stype} runs at effort {max_eff} at most (designer ruling 2026-10-12). Drop the effort override.")
        return 0
    if len(prompt) > MAX_PROMPT_CHARS:
        deny(f"Agent brief too long ({len(prompt)} chars, limit {MAX_PROMPT_CHARS}): a brief is the rules file path + a footer "
             "(items, base sha, files owned, temp tag). Put long item lists in a docs/handoff/<round>/ file and name it; "
             "never inline source or rule blocks (docs/process/01 §5).")
        return 0
    if stype != "code-cleanup" and str(inp.get("isolation", "")) == "worktree":
        n = live_agent_worktrees()
        if n >= MAX_WORKTREE_AGENTS:
            deny(f"Agent cap: {n} agent worktrees are alive (limit {MAX_WORKTREE_AGENTS}). Merge and `git worktree remove` finished ones first "
                 "(docs/process/01 W8); more agents on one PC only slow each other down.")
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
