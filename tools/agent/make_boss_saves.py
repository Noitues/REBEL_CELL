"""Boss saves for the save library (change plan 1 V4; docs/process/05_CLAUDE_PLAYTESTER.md "Boss save (V4)").

    python tools/agent/make_boss_saves.py --seeds 1002,1017,1018          # generate + meta.json
    python tools/agent/make_boss_saves.py --seeds 1002 --meta-only         # (re)write meta.json from the saves

Runs tools/agent/make_boss_save.gd per seed into .playtest_saves/boss/<seed>/ and writes the
meta.json that `python tools/playtest/streamline.py saves list` reads (label boss). One Godot at a time.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LIB = ROOT / ".playtest_saves" / "boss"


def state_text(save: Path) -> str:
    """The text streamline.py's healthy() / heat_of() read: Home integrity, Heat, crew."""
    data = json.loads((save / "campaign_1.json").read_text(encoding="utf-8"))
    c = data["campaign"]
    grid = c.get("grid", {})
    crew = [o for o in c.get("roster", []) if o.get("alive", True)]
    return "Heat %d. Home %d/%d. Crew %d ready. Exploits %d. Schematics %d. Genome Core breach ready." % (
        c["heat"], grid.get("home_integrity", 0), grid.get("home_max_integrity", 0), len(crew), len(c.get("exploits", [])), c["schematics"])


def write_meta(save: Path, seed: int, summary: str) -> None:
    data = json.loads((save / "campaign_1.json").read_text(encoding="utf-8"))
    info = {"label": "boss", "heat": data["campaign"]["heat"], "tester": "make_boss_save seed %d" % seed, "batch": "V4",
            "saved": time.strftime("%Y-%m-%d %H:%M:%S"), "state": state_text(save), "summary": summary}
    (save / "meta.json").write_text(json.dumps(info, indent=1), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", required=True, help="comma-separated seeds")
    ap.add_argument("--meta-only", action="store_true")
    a = ap.parse_args()
    rc = 0
    for seed in [int(s) for s in a.seeds.split(",")]:
        out = LIB / str(seed)
        out.mkdir(parents=True, exist_ok=True)
        summary = ""
        if not a.meta_only:
            r = subprocess.run(["godot", "--headless", "--path", str(ROOT), "-s", "tools/agent/make_boss_save.gd", "--",
                                "seed=%d" % seed, "out=%s" % out.as_posix()], capture_output=True, text=True, timeout=1800)
            lines = [ln for ln in r.stdout.splitlines() if ln.startswith("MAKE_BOSS_SAVE:")]
            summary = lines[-1] if lines else ""
            print(summary or "seed %d: no summary (rc %d)" % (seed, r.returncode))
            if r.returncode != 0:
                rc = 1
                continue
        write_meta(out, seed, summary)
        print(out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
