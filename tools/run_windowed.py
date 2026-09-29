"""Quiet windowed Godot runs for REBEL_CELL (docs/TEST_SUITE.md, "Windowed checks").

Anything that needs the real renderer (Movie Maker captures, the storyboard, the motion
lab, frame profiling, GPU bake checks) cannot run headless. This runs it so it never
takes keyboard or mouse focus from whatever the person at the machine is using, plays
no sound, and keeps its window off the screen:

- override.cfg in the project folder sets display/window/size/no_focus (the window is
  created without focus, so Windows never makes it the foreground window) and the Dummy
  audio driver; the file is removed again when the last quiet run in that folder ends;
- --audio-driver Dummy on the command line as well;
- REBEL_CELL_QUIET_WINDOW=1, which Settings reads: the window moves off the screen on
  its first frame and stays windowed (never fullscreen), and AudioDirector mutes Master.

Godot keeps a window's first position on a screen and a minimized window stops drawing,
so the window can show for its first frame (without focus) before it moves off.

Because override.cfg would also apply to anyone launching the game from that folder
meanwhile, it refuses the main checkout (use a git worktree or a copy) unless
--allow-main-checkout is given.

    python tools/run_windowed.py --log out.log -- res://tools/design_lab/motion_lab.tscn \
        --write-movie C:/tmp/frames/f.png --fixed-fps 30 --quit-after 60 -- --demo-anim=card_hover

Everything after "--" goes to Godot (after --path <project>). Godot's output goes to
--log (never a pipe). Exits with Godot's exit code (124 on --timeout).

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = "; run_windowed.py quiet override (removed when the last quiet run ends)"
OVERRIDE = MARKER + """

[display]

window/size/no_focus=true

[audio]

driver/driver="Dummy"
"""
LOCK_DIR = ".quiet_runs"
ENV_FLAG = "REBEL_CELL_QUIET_WINDOW"


def is_main_checkout(project: Path) -> bool:
    """True when `project` is a git repository's primary working tree (not a worktree)."""
    return (project / ".git").is_dir()


def _alive(pid: int) -> bool:
    if os.name == "nt":
        import ctypes
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)  # QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        code = ctypes.c_ulong()
        ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(handle)
        return code.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _holders(locks: Path) -> list[Path]:
    """Lock files of quiet runs still alive (stale ones are removed)."""
    out = []
    for f in locks.glob("*.pid"):
        try:
            pid = int(f.stem)
        except ValueError:
            continue
        if _alive(pid):
            out.append(f)
        else:
            f.unlink(missing_ok=True)
    return out


def acquire(project: Path) -> Path:
    """Registers this run and writes override.cfg; refuses one that isn't ours."""
    cfg = project / "override.cfg"
    if cfg.exists() and not cfg.read_text(encoding="utf-8", errors="replace").startswith(MARKER):
        sys.exit("run_windowed: %s exists and is not ours; not touching it" % cfg)
    locks = project / LOCK_DIR
    locks.mkdir(exist_ok=True)
    me = locks / ("%d.pid" % os.getpid())
    me.write_text(str(time.time()), encoding="utf-8")
    cfg.write_text(OVERRIDE, encoding="utf-8")
    return me


def release(project: Path, me: Path) -> None:
    """Unregisters this run; the last one out removes override.cfg."""
    me.unlink(missing_ok=True)
    locks = project / LOCK_DIR
    if _holders(locks):
        return
    cfg = project / "override.cfg"
    if cfg.exists() and cfg.read_text(encoding="utf-8", errors="replace").startswith(MARKER):
        cfg.unlink()
    try:
        locks.rmdir()
    except OSError:
        pass


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default=str(ROOT), help="project folder (default: this checkout)")
    ap.add_argument("--godot", default=os.environ.get("GODOT", "godot"))
    ap.add_argument("--log", required=True, help="file for Godot's output")
    ap.add_argument("--timeout", type=float, default=600.0, help="seconds before the run is stopped")
    ap.add_argument("--allow-main-checkout", action="store_true",
                    help="run in the main checkout anyway (override.cfg applies to any launch there meanwhile)")
    ap.add_argument("godot_args", nargs=argparse.REMAINDER, help="-- then the Godot arguments")
    args = ap.parse_args()
    rest = args.godot_args[1:] if args.godot_args[:1] == ["--"] else args.godot_args
    project = Path(args.project).resolve()
    if not (project / "project.godot").exists():
        sys.exit("run_windowed: no project.godot in %s" % project)
    if is_main_checkout(project) and not args.allow_main_checkout:
        sys.exit("run_windowed: %s is the main checkout; run in a git worktree or a copy "
                 "(or pass --allow-main-checkout)" % project)
    if "--headless" in rest:
        sys.exit("run_windowed: --headless needs no quiet window; run Godot directly")
    me = acquire(project)
    env = dict(os.environ)
    env[ENV_FLAG] = "1"
    cmd = [args.godot, "--path", str(project), "--audio-driver", "Dummy"] + rest
    try:
        with open(args.log, "w", encoding="utf-8", errors="replace") as log:
            p = subprocess.Popen(cmd, cwd=str(project), stdout=log, stderr=subprocess.STDOUT, env=env)
            try:
                return p.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                p.kill()  # only this run's own child
                p.wait()
                return 124
    finally:
        release(project, me)


if __name__ == "__main__":
    sys.exit(main())
