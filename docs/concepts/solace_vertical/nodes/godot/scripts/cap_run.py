"""Runs the nodes capture on the then and now worktrees under the shared GPU lock (gpu_lock.py, ME solace_nodes)."""
import os
import subprocess
import sys

sys.path.insert(0, "D:/rc_art/art-pass/docs/concepts/solace_vertical/district/scripts")
import gpu_lock

gpu_lock.ME = "solace_nodes"
BASE = "D:/rc_scratch/solace_v1/nodes/"
shots = sys.argv[1] if len(sys.argv) > 1 else "map,rest,workshop,cache"
which = sys.argv[2].split(",") if len(sys.argv) > 2 else ["now", "then"]
gpu_lock.acquire("godot nodes captures")
try:
    for w in which:
        tree = BASE + "wt_" + w
        out = BASE + "cap_" + w
        os.makedirs(out, exist_ok=True)
        env = dict(os.environ)
        env["APPDATA"] = BASE + "appdata_" + w
        os.makedirs(env["APPDATA"], exist_ok=True)
        cmd = [sys.executable, "tools/run_windowed.py", "--log", BASE + "work/cap_%s.log" % w, "--timeout", "900", "--", "res://tools/design_lab/nodes_capture.tscn", "--", "--out=" + out, "--shots=" + shots]
        r = subprocess.run(cmd, cwd=tree, env=env)
        print(w, "exit", r.returncode)
finally:
    gpu_lock.release()
