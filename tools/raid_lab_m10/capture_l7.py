"""Capture runner of the L7 raid lab: the four still sets, the two Movie Maker clips with their key frames, the comparison sheet.

    python tools/raid_lab_m10/capture_l7.py [--out D:/rc_tmp/raid_design_lab/lab_l7] [--only shots,breach,scrambled,jam,clips,sheet]

Every windowed run goes through tools/run_windowed.py (quiet window, no focus, no sound), one after the other, and writes its
Godot output to a log under --out (never a pipe). Run it from a worktree, not the main checkout.

  shots/            leg 0, planned line (every screen and every playout beat)
  shots_breach/     leg 0, naive line (the settled breach, the fast playout, the BREACHED card)
  shots_scrambled/  leg 5, planned line, --scramble (the no-words test)
  shots_jam/        leg 3, planned line (raid 1 jams the hunter)
  clips/            planned_raid.avi and breach_raid.avi (Movie Maker, 30 fps), clips/frames/<clip>/ the key frames
  comparison_sheet.png   each target frame next to its lab still
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCENE = "res://tools/raid_lab_m10/raid_lab_m10.tscn"
SETS = {
    "shots": ["--leg=0", "--line=planned"],
    "shots_breach": ["--leg=0", "--line=naive"],
    "shots_scrambled": ["--leg=5", "--line=planned", "--scramble"],
    "shots_jam": ["--leg=3", "--line=planned"],
}
KEYS = {"shots": "shots", "breach": "shots_breach", "scrambled": "shots_scrambled", "jam": "shots_jam"}


def windowed(log: Path, godot_args: list[str]) -> int:
    cmd = [sys.executable, str(ROOT / "tools" / "run_windowed.py"), "--log", str(log), "--timeout", "1800", "--"] + godot_args
    print(" ".join(cmd))
    return subprocess.run(cmd, cwd=str(ROOT)).returncode


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="D:/rc_tmp/raid_design_lab/lab_l7")
    ap.add_argument("--only", default="shots,breach,scrambled,jam,clips,sheet")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    todo = set(args.only.split(","))
    for key, folder in KEYS.items():
        if key not in todo:
            continue
        d = out / folder
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.png"):
            old.unlink()
        code = windowed(out / (folder + ".log"), ["--resolution", "1280x720", SCENE, "--", "--shots=" + str(d)] + SETS[folder])
        print(folder, "exit", code)
    if "clips" in todo:
        clips = out / "clips"
        for name in ("planned", "breach"):
            frames = clips / "frames" / (name + "_raid")
            frames.mkdir(parents=True, exist_ok=True)
            for old in frames.glob("*.png"):
                old.unlink()
            avi = clips / (name + "_raid.avi")
            code = windowed(out / ("clip_" + name + ".log"),
                            ["--resolution", "1280x720", SCENE, "--write-movie", str(avi), "--fixed-fps", "30", "--",
                             "--clip=" + name, "--clipdir=" + str(frames)])
            print("clip", name, "exit", code)
    if "sheet" in todo:
        subprocess.run([sys.executable, str(ROOT / "tools" / "raid_lab_m10" / "compare_sheet.py"), "--out", str(out)], cwd=str(ROOT))


if __name__ == "__main__":
    main()
