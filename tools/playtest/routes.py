"""Checked routes: recorded inputs that carry a tester past screens it is not here to test (doc 05 §10).

A route is a list of steps; each step is some inputs (1280x720 coordinates, as blackbox.py takes
them) and the screen it must lead to, kept as a small reference frame. Playing a route checks every
checkpoint with a pixel comparison (no model call); the first checkpoint that does not match stops the
route and hands the tester the screen as it is, with "the route broke here" (itself a sign the UI
changed). Routes belong to the build they were recorded on (`routes/<build8>/<name>.json`).

Recording (drive the game yourself, one step at a time; each step prints the new screenshot):

    python tools/playtest/routes.py rec-start --name to_hq
    python tools/playtest/routes.py rec --name to_hq click 500 405 [--note "New campaign setup"]
    python tools/playtest/routes.py rec --name to_hq key enter
    python tools/playtest/routes.py rec --name to_hq wait 3
    python tools/playtest/routes.py rec-undo --name to_hq          # drop the last step (it is not replayed)
    python tools/playtest/routes.py rec-end --name to_hq
    python tools/playtest/routes.py test --name to_hq             # replay on a fresh copy and report

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blackbox as bb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
ROUTES = ROOT / "tools" / "playtest" / "routes"
BUILD = ROOT / ".claude" / "worktrees" / "playtest-build"
REC_SESSIONS = ROOT / ".playtest_sessions" / "_routes"
MIN_TOL = 0.06


def build_sha() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=BUILD, capture_output=True, text=True).stdout.strip()


def sig(img, region=None) -> bytes:
    """Greyscale fingerprint; `region` (x0, y0, x1, y1) compares only a static part of the screen."""
    if region:
        return img.convert("L").crop(tuple(region)).resize((160, 40)).tobytes()
    small = img.convert("L").resize((160, 90))
    return small.crop((0, 0, 160, 85)).tobytes()  # the bottom ticker scrolls forever


def diff(a: bytes, b: bytes) -> float:
    return sum(1 for p, q in zip(a, b) if abs(p - q) > 14) / max(1, len(a))


def stable(hwnd: int, timeout: float = 8.0):
    prev = bb.grab(hwnd)
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(0.35)
        cur = bb.grab(hwnd)
        if diff(sig(prev), sig(cur)) < 0.012:
            return cur
        prev = cur
    return prev


def route_file(name: str, build: str | None = None) -> Path:
    return ROUTES / (build or build_sha())[:8] / ("%s.json" % name)


def do_action(hwnd: int, act: dict) -> None:
    t = act["type"]
    if t in ("click", "right_click"):
        bb.click(hwnd, act["x"], act["y"], right=(t == "right_click"), double=False)
    elif t == "move":
        bb.mouse_move(hwnd, act["x"], act["y"])
    elif t == "key":
        for k in act["keys"].split():
            bb.key(hwnd, k)
    elif t == "scroll":
        bb.scroll(hwnd, act["x"], act["y"], act["amount"])
    elif t == "wait":
        time.sleep(act["seconds"])


def load(name: str, build: str | None = None) -> dict | None:
    f = route_file(name, build)
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def play(hwnd_fn, name: str, build: str, log=print, fail_dir: str = "") -> tuple[bool, str]:
    """Plays route `name` for `build`. hwnd_fn() returns the game window. Returns (ok, where it stopped)."""
    from PIL import Image

    r = load(name, build)
    if not r:
        return False, "no route %r for build %s" % (name, build[:8])
    folder = route_file(name, build).parent / name
    for i, step in enumerate(r["steps"]):
        hwnd = hwnd_fn()
        for act in step["do"]:
            do_action(hwnd, act)
            time.sleep(0.25)
        if not step.get("expect"):  # no checkpoint (the screen depends on the save): just let it settle
            stable(hwnd_fn(), step.get("timeout", 10))
            log("route %s: step %d/%d done (%s)" % (name, i + 1, len(r["steps"]), step.get("note", "")))
            continue
        region = step.get("region")
        want = sig(Image.open(folder / step["expect"]).convert("RGB"), region)
        deadline, best, last = time.time() + step.get("timeout", 10), 1.0, None
        while time.time() < deadline:
            last = stable(hwnd_fn(), 4.0)
            best = min(best, diff(sig(last, region), want))
            if best <= step["tol"]:
                break
        if best > step["tol"]:
            if last is not None and fail_dir:
                last.save(Path(fail_dir) / ("route_%s_fail_step%02d.png" % (name, i + 1)))
            return False, "step %d (%s): screen differs by %.0f%% (allowed %.0f%%)" % (
                i + 1, step.get("note", ""), best * 100, step["tol"] * 100)
        log("route %s: step %d/%d ok (%s)" % (name, i + 1, len(r["steps"]), step.get("note", "")))
    return True, r.get("end", "")


# ---------------------------------------------------------------- recorder

def rec_session(name: str) -> bb.Session:
    return bb.Session((REC_SESSIONS / name).resolve())


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["rec-start", "rec", "rec-undo", "rec-fix", "rec-end", "test", "list"])
    ap.add_argument("--name")
    ap.add_argument("--note", default="")
    ap.add_argument("--end", default="", help="rec-end: what the route leaves the tester at")
    ap.add_argument("--start-save", default="", help="rec-start/test: begin from this library save (streamline.py)")
    ap.add_argument("--region", type=int, nargs=4, help="rec: compare only this part of the screen (x0 y0 x1 y1)")
    ap.add_argument("--game", default="", help="rec/rec-fix/rec-end: use the recording game of another route (to extend it)")
    ap.add_argument("--from", dest="from_route", default="", help="rec-start: copy this route's steps first (the game must already be past them)")
    ap.add_argument("--settle", type=float, default=2.0, help="rec: seconds between the two checkpoint frames")
    ap.add_argument("args", nargs="*", help="rec: click X Y | right_click X Y | key NAME.. | scroll X Y N | wait S | move X Y")
    a = ap.parse_args()

    if a.cmd == "list":
        for f in sorted(ROUTES.glob("*/*.json")):
            r = json.loads(f.read_text(encoding="utf-8"))
            print("%s %-24s %2d steps -> %s" % (f.parent.name, f.stem, len(r["steps"]), r.get("end", "")))
        return 0

    sha = build_sha()
    rf = route_file(a.name, sha)
    folder = rf.parent / a.name
    if a.cmd in ("rec-start", "test"):
        s = rec_session(a.name if a.cmd == "rec-start" else a.name + "_test")
        if s.state.get("launcher_pid"):
            subprocess.run([sys.executable, str(Path(bb.__file__)), "--session", str(s.path), "stop"], capture_output=True)
        shutil.rmtree(s.path, ignore_errors=True)
        s.path.mkdir(parents=True)
        if a.start_save:
            import streamline

            save = streamline.pick_save(sha, a.start_save)
            if not save:
                sys.exit("routes: no save %r" % a.start_save)
            bb.private_copy(BUILD, s.path / "game")
            streamline.install_save(save, s.path / "game")
        subprocess.run([sys.executable, str(Path(bb.__file__)), "--session", str(s.path), "--settle", "6",
                        "start", "--private-copy", "--project", str(BUILD)], check=True)
        if a.cmd == "rec-start":
            if rf.exists():
                sys.exit("routes: %s exists; delete it to re-record" % rf)
            folder.mkdir(parents=True, exist_ok=True)
            rf.write_text(json.dumps({"name": a.name, "build": sha, "start": "title" if not a.start_save else "title, save " + a.start_save,
                                      "steps": []}, indent=1), encoding="utf-8")
            print("recording %s; screen: %s" % (a.name, sorted((s.path / "shots").glob("*.png"))[-1]))
            return 0
        s = bb.Session(s.path)
        ok, where = play(s.hwnd, a.name, sha, fail_dir=str(s.path))
        print("route %s: %s (%s)" % (a.name, "OK" if ok else "BROKE", where))
        subprocess.run([sys.executable, str(Path(bb.__file__)), "--session", str(s.path), "stop"], capture_output=True)
        return 0 if ok else 1

    r = json.loads(rf.read_text(encoding="utf-8"))
    s = rec_session(a.game or a.name)
    if a.cmd == "rec-undo":
        r["steps"].pop()
        rf.write_text(json.dumps(r, indent=1), encoding="utf-8")
        print("dropped the last step; %d left (the game is NOT rewound: put it back by hand)" % len(r["steps"]))
        return 0
    if a.cmd == "rec-fix":
        hwnd = s.hwnd()
        first = stable(hwnd)
        time.sleep(a.settle)
        second = stable(hwnd)
        drift = diff(sig(first, a.region), sig(second, a.region))
        step = r["steps"][-1]
        second.save(folder / step["expect"])
        step["tol"] = round(max(MIN_TOL, drift * 2.5 + 0.02), 3)
        if a.region:
            step["region"] = a.region
        rf.write_text(json.dumps(r, indent=1), encoding="utf-8")
        print("step %d re-taken (region %s, self-drift %.1f%%, tolerance %.1f%%)" % (len(r["steps"]), a.region, drift * 100, step["tol"] * 100))
        return 0
    if a.cmd == "rec-end":
        r["end"] = a.end or a.note
        rf.write_text(json.dumps(r, indent=1), encoding="utf-8")
        subprocess.run([sys.executable, str(Path(bb.__file__)), "--session", str(s.path), "stop"], capture_output=True)
        print("saved %s (%d steps)" % (rf, len(r["steps"])))
        return 0

    # rec: do one step, record its checkpoint and how much the settled screen still moves by itself
    w = a.args
    kinds = {"click": 2, "right_click": 2, "move": 2, "scroll": 3, "wait": 1}
    if w[0] == "key":
        act = {"type": "key", "keys": " ".join(w[1:])}
    elif w[0] in kinds:
        nums = [float(x) for x in w[1:1 + kinds[w[0]]]]
        act = {"type": w[0]}
        if w[0] == "wait":
            act["seconds"] = nums[0]
        else:
            act.update({"x": int(nums[0]), "y": int(nums[1])})
            if w[0] == "scroll":
                act["amount"] = int(nums[2])
    else:
        sys.exit("routes: unknown action %s" % w[0])
    hwnd = s.hwnd()
    do_action(hwnd, act)
    first = stable(hwnd)
    time.sleep(a.settle)
    second = stable(hwnd)
    drift = diff(sig(first, a.region), sig(second, a.region))
    n = len(r["steps"]) + 1
    img_name = "%02d.png" % n
    second.save(folder / img_name)
    shot = s.next_shot("rec%02d" % n)
    second.save(shot)
    step = {"do": [act], "expect": img_name, "tol": round(max(MIN_TOL, drift * 2.5 + 0.02), 3), "timeout": 12, "note": a.note}
    if a.region:
        step["region"] = a.region
    r["steps"].append(step)
    rf.write_text(json.dumps(r, indent=1), encoding="utf-8")
    print("step %d recorded (self-drift %.1f%%, tolerance %.1f%%): %s" % (n, drift * 100, r["steps"][-1]["tol"] * 100, shot))
    return 0


if __name__ == "__main__":
    sys.exit(main())
