"""V3 dynamic: write a Blender job and run it headless (log to scratch, never piped).

python jobs.py stills [names...]   -> 2880 x 1620 passes of the five stills
python jobs.py video [from to]     -> 1440 x 810 passes of the video frames (from cam_rig.timeline())
python jobs.py sheet               -> the architecture sheet strips
python jobs.py preview <name>      -> one still at 1440 x 810, beauty only (fast look)
"""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import cam_rig as R  # noqa: E402
import sgraph3 as G  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


def protect(state):
    st, opts = G.states(state["walked"])
    if state.get("zoom", 0) > 0.5:
        return []
    return [state["walked"][-1]] + opts


def run(job, tag):
    os.makedirs(os.path.join(SCR, "bl"), exist_ok=True)
    lay = os.path.join(SCR, "layout.json")
    G.dump(lay)
    job["layout"] = lay
    job.setdefault("out", os.path.join(SCR, "bl"))
    jp = os.path.join(SCR, "job_%s.json" % tag)
    with open(jp, "w") as f:
        json.dump(job, f, indent=1)
    log = os.path.join(SCR, "bl_%s.log" % tag)
    with open(log, "w") as f:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "scene3.py"), "--", jp],
                           stdout=f, stderr=subprocess.STDOUT)
    print("exit", r.returncode, "log", log, flush=True)
    return r.returncode


def sheet_pose(x0, x1, z0, z1, res, yaw=7.0, pitch=12.0):
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    y, p = math.radians(yaw), math.radians(pitch)
    d = (math.sin(y) * math.cos(p), math.cos(y) * math.cos(p), -math.sin(p))
    tgt = (cx, 4.0, cz)
    loc = tuple(t - 400 * k for t, k in zip(tgt, d))
    scale = max((x1 - x0) * 1.04, (z1 - z0) * 1.1 * res[0] / res[1])
    return dict(loc=loc, tgt=tgt, ortho=scale, lens=50)


if __name__ == "__main__":
    what = sys.argv[1]
    if what in ("stills", "preview"):
        st = R.stills()
        names = sys.argv[2:] or list(st)
        shots = [dict(name=n, pose=st[n][0].to_json(), t=2.0, protect=protect(st[n][1])) for n in names]
        if what == "preview":
            run(dict(res=[1440, 810], samples=6, shots=shots), "preview")
        else:
            run(dict(res=[2880, 1620], samples=24, shots=shots), "stills")
    elif what == "video":
        fr, _ = R.timeline()
        a = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        b = int(sys.argv[3]) if len(sys.argv) > 3 else len(fr)
        shots = [dict(name="v%03d" % k, pose=fr[k][0].to_json(), t=k / R.FPS, protect=protect(fr[k][1]))
                 for k in range(a, b)]
        run(dict(res=[1440, 810], samples=8, shots=shots, out=os.path.join(SCR, "blv")), "video_%d_%d" % (a, b))
    elif what == "sheet":
        CW = 58.0
        shots = [dict(name="sheet_c1", res=[2560, 600], pose=sheet_pose(-8, 5 * CW - 12, -9, 50, (2560, 600))),
                 dict(name="sheet_c2", res=[2560, 600], pose=sheet_pose(5 * CW - 8, 10 * CW - 12, -9, 50, (2560, 600))),
                 dict(name="sheet_b", res=[2560, 640], pose=sheet_pose(10 * CW + 22, 10 * CW + 30 + 7 * 46 - 8, -9, 88, (2560, 640)))]
        run(dict(res=[2560, 600], samples=24, mode="sheet", shots=shots), "sheet")
