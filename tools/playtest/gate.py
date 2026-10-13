"""Playtest routine for a User-Ready Gate (docs/process/04 + 05 §12): one command, three parts.

    python tools/playtest/gate.py --gate PT-014 --compare PB-010 --budget 50
    python tools/playtest/gate.py --gate PT-014 --compare PB-010 --skip-screen        # state sweep only

1. Build and routes: points the build copy at main (roll_testers --build), replays every recorded
   route on a fresh copy (routes.py test). A route that breaks means the UI changed: it is listed
   in the gate summary to re-record (routes.py rec-start ...), and testers fall back to starting
   from the title (the coverage plan only uses routes that exist for this build).
2. Screen batch (run_batch.py): the standard mix, judged in batch, findings compared with --compare,
   combat skill from the replays (ground truth).
3. State sweep (state_agent.py): the built-in baseline (free) and an intermediate LLM run on the
   same seeds, for win rate, deaths, Heat and the reasons behind picks.
Writes docs/playtest/claude/gates/<gate>.md: route status, the batch's headline and skill table,
the state sweep table, and links. Total spend is capped by --budget (screen batch gets the rest
after the state sweep's share).

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS = ROOT / "tools" / "playtest"
DOCS = ROOT / "docs" / "playtest" / "claude"
MIX = "novice=3,intermediate=3,expert=1"


def run(cmd: list[str], log: Path, timeout: float | None = None) -> int:
    with open(log, "w", encoding="utf-8") as f:
        return subprocess.run(cmd, cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT, timeout=timeout).returncode


def section(md: Path, start: str, stop: str) -> str:
    if not md.exists():
        return "(missing: %s)" % md.name
    text = md.read_text(encoding="utf-8")
    m = re.search(re.escape(start) + r"(.*?)(?=" + re.escape(stop) + r"|\Z)", text, re.S)
    return ((start if start.startswith("|") else "") + m.group(1)).strip() if m else "(no %s)" % start


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gate", required=True)
    ap.add_argument("--compare", default="", help="previous screen batch, for trends")
    ap.add_argument("--budget", type=float, default=50.0)
    ap.add_argument("--state-budget", type=float, default=12.0)
    ap.add_argument("--seeds", default="1000-1004")
    ap.add_argument("--build", default="main")
    ap.add_argument("--skip-screen", action="store_true")
    ap.add_argument("--skip-state", action="store_true")
    a = ap.parse_args()
    work = ROOT / ".playtest_sessions" / ("gate_" + a.gate)
    work.mkdir(parents=True, exist_ok=True)
    batch, sa = "PB-" + a.gate, "SA-" + a.gate
    out = ["# Playtest gate %s — %s" % (a.gate, time.strftime("%Y-%m-%d")), ""]

    # 1. build + routes
    run([sys.executable, str(TOOLS / "roll_testers.py"), "--batch", "_gate_build", "--count", "0", "--build", a.build], work / "build.log")
    routes = sorted({p.stem for p in (TOOLS / "routes").glob("*/*.json")})
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT / ".claude" / "worktrees" / "playtest-build",
                         capture_output=True, text=True).stdout.strip()
    out += ["## 1. Build %s and routes" % sha[:8], ""]
    for r in routes:
        if not (TOOLS / "routes" / sha[:8] / ("%s.json" % r)).exists():
            out.append("- %s: **not recorded for this build** (re-record: `routes.py rec-start --name %s`)" % (r, r))
            continue
        code = run([sys.executable, str(TOOLS / "routes.py"), "test", "--name", r], work / ("route_%s.log" % r), timeout=600)
        out.append("- %s: %s" % (r, "ok" if code == 0 else "**broke** (UI changed; see %s)" % (work / ("route_%s.log" % r)).name))

    # 3 first (cheap, bounded), so the screen batch gets the rest of the budget
    if not a.skip_state:
        run([sys.executable, str(TOOLS / "state_agent.py"), "--name", sa + "-base", "--seeds", a.seeds, "--builtin", "all"], work / "state_base.log")
        run([sys.executable, str(TOOLS / "state_agent.py"), "--name", sa, "--seeds", a.seeds, "--tier", "intermediate",
             "--budget", str(a.state_budget)], work / "state.log")
    # 2. screen batch
    if not a.skip_screen:
        left = a.budget - (0 if a.skip_state else a.state_budget)
        cmd = [sys.executable, str(TOOLS / "run_batch.py"), "--batch", batch, "--mix", MIX, "--motion", "1",
               "--budget", str(left), "--judge-reserve", "6"]
        if a.compare:
            cmd += ["--compare", a.compare]
        run(cmd, work / "screen.log")
        out += ["", "## 2. Screen batch %s" % batch, "", section(DOCS / batch / "_FINDINGS.md", "## 1. Headline", "## 2."), "",
                "Skill (ground truth):", "", section(DOCS / batch / "_BATCH.md", "## Combat skill, ground truth (fights rebuilt from replays)", "## Top"),
                "", "Full findings: `docs/playtest/claude/%s/_FINDINGS.md`" % batch]
    if not a.skip_state:
        out += ["", "## 3. State sweep (seeds %s)" % a.seeds, "", "Baseline (built-in policy):", "",
                section(DOCS / "state" / (sa + "-base.md"), "| Seed", "## Reasons"), "", "LLM, intermediate:", "",
                section(DOCS / "state" / (sa + ".md"), "| Seed", "## Reasons")]
    gates = DOCS / "gates"
    gates.mkdir(parents=True, exist_ok=True)
    (gates / ("%s.md" % a.gate)).write_text("\n".join(out) + "\n", encoding="utf-8")
    print(gates / ("%s.md" % a.gate))
    return 0


if __name__ == "__main__":
    sys.exit(main())
