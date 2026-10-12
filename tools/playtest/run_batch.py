"""Run a whole Claude playtest batch unattended: roll, play in waves, judge, synthesise (doc 05 §2-§9).

    python tools/playtest/run_batch.py --batch PB-010 --mix novice=3,intermediate=3,expert=1 --motion 1 --budget 40
    python tools/playtest/run_batch.py --batch PB-010 --resume          # after a stop: plays what is left, then judges

1. Rolls the testers (roll_testers.py --mix) plus `--motion` motion testers (explorer persona,
   animation_feel focus, intermediate tier).
2. Plays them with harness.py --defer, `--parallel` at a time, longest time box first, each with
   its tier's time box and dollar cap (TIERS below). Before each launch it checks the batch's
   spend (every session's cost.json) against `--budget` minus `--judge-reserve`; when the money
   for one more tester's cap is not there, the remaining testers are skipped and logged.
3. Runs judge_batch.py (motion, audits, lessons, reports, playbook, then _FINDINGS.md).
Logs to .playtest_sessions/<batch>/run.log; per tester, harness.out in its session folder.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS = ROOT / "tools" / "playtest"
SESSIONS = ROOT / ".playtest_sessions"
# Per tier: wall-clock minutes and the dollar cap of one tester (the harness stops at either).
TIERS = {
    "novice": (60, 1.5),
    "intermediate": (120, 4.0),
    "expert": (240, 14.0),
    "motion": (60, 3.0),
}


def log(batch: str, msg: str) -> None:
    line = "%s %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    with open(SESSIONS / batch / "run.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def spent(batch: str) -> float:
    total = 0.0
    for c in (SESSIONS / batch).glob("*/cost.json"):
        try:
            total += json.loads(c.read_text())["usd"]
        except (OSError, ValueError, KeyError):
            pass
    return total


def roll(a) -> None:
    base = [sys.executable, str(TOOLS / "roll_testers.py"), "--batch", a.batch]
    if a.mix:
        subprocess.run(base + ["--mix", a.mix, "--seed", str(a.seed)], check=True)
    if a.motion:
        subprocess.run(base + ["--count", str(a.motion), "--persona", "explorer", "--focus", "animation_feel",
                               "--seed", str(a.seed + 1)], check=True)


def plan(batch: str) -> list[dict]:
    m = json.loads((SESSIONS / batch / "batch.json").read_text(encoding="utf-8"))
    out = []
    for t in m["testers"]:
        session = SESSIONS / batch / t["handle"]
        kind = "motion" if t["focus"] == "animation_feel" else t["tier"]
        minutes, cap = TIERS[kind]
        out.append({"handle": t["handle"], "kind": kind, "minutes": minutes, "cap": cap, "session": session,
                    "done": (session / "session_end.json").exists()})
    return sorted(out, key=lambda x: -x["minutes"])


def launch(t: dict) -> subprocess.Popen:
    cmd = [sys.executable, "-u", str(TOOLS / "harness.py"), "--brief", str(t["session"] / "brief.md"),
           "--minutes", str(t["minutes"]), "--max-usd", str(t["cap"]), "--defer"]
    if t["kind"] == "motion":
        cmd.append("--motion")
    out = open(t["session"] / "harness.out", "a", encoding="utf-8")
    return subprocess.Popen(cmd, cwd=str(ROOT), stdout=out, stderr=subprocess.STDOUT)


def main() -> int:
    # Output goes to log files; the Windows console code page cannot encode every character a model writes.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--batch", required=True)
    ap.add_argument("--mix", default="", help="e.g. novice=3,intermediate=3,expert=1")
    ap.add_argument("--motion", type=int, default=0, help="motion testers to add")
    ap.add_argument("--seed", type=int, default=int(time.time()) % 100000)
    ap.add_argument("--budget", type=float, default=40.0, help="dollars for the whole batch, judging included")
    ap.add_argument("--judge-reserve", type=float, default=6.0, help="dollars kept back for judging and synthesis")
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--compare", default="", help="previous batch id for the findings' trend column")
    ap.add_argument("--resume", action="store_true", help="the batch is rolled already: play what is left, then judge")
    a = ap.parse_args()

    (SESSIONS / a.batch).mkdir(parents=True, exist_ok=True)
    if not a.resume:
        if (SESSIONS / a.batch / "batch.json").exists():
            sys.exit("run_batch: %s is already rolled; use --resume" % a.batch)
        roll(a)
    todo = [t for t in plan(a.batch) if not t["done"]]
    log(a.batch, "start: %d tester(s) to play, budget $%.2f (reserve $%.2f), %d at a time, seed %d"
        % (len(todo), a.budget, a.judge_reserve, a.parallel, a.seed))

    running: list[tuple[dict, subprocess.Popen]] = []
    committed = 0.0  # caps of the running testers, not yet spent
    while todo or running:
        for t, p in list(running):
            if p.poll() is not None:
                running.remove((t, p))
                committed -= t["cap"]
                log(a.batch, "done: %s (%s) exit %d, batch spend $%.2f" % (t["handle"], t["kind"], p.returncode, spent(a.batch)))
        while todo and len(running) < a.parallel:
            t = todo[0]
            room = a.budget - a.judge_reserve - spent(a.batch) - committed
            if room < t["cap"]:
                log(a.batch, "skip: %s (%s) cap $%.2f > room $%.2f" % (t["handle"], t["kind"], t["cap"], room))
                todo.pop(0)
                continue
            todo.pop(0)
            running.append((t, launch(t)))
            committed += t["cap"]
            log(a.batch, "play: %s (%s, %d min, cap $%.2f)" % (t["handle"], t["kind"], t["minutes"], t["cap"]))
            time.sleep(20)  # stagger the game launches
        time.sleep(15)

    played = sum(1 for t in plan(a.batch) if t["done"])
    log(a.batch, "play finished: %d session(s), spend $%.2f; judging" % (played, spent(a.batch)))
    if played == 0:
        return 1
    cmd = [sys.executable, "-u", str(TOOLS / "judge_batch.py"), "run", "--batch", a.batch, "--poll", "60"]
    if a.compare:
        cmd += ["--compare", a.compare]
    with open(SESSIONS / a.batch / "judge.out", "a", encoding="utf-8") as out:
        code = subprocess.run(cmd, cwd=str(ROOT), stdout=out, stderr=subprocess.STDOUT).returncode
    jc = SESSIONS / a.batch / "judge" / "cost.json"
    judge = json.loads(jc.read_text())["usd"] if jc.exists() else 0.0
    log(a.batch, "judge exit %d, judge $%.2f; batch total $%.2f; findings: docs/playtest/claude/%s/_FINDINGS.md"
        % (code, judge, spent(a.batch) + judge, a.batch))
    return code


if __name__ == "__main__":
    sys.exit(main())
