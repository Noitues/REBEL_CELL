"""V3 AAA: write a Blender job for the overview and run it headless (log to scratch, never piped).

python jobs_aaa.py <look> [quality] [hover] [renders]
  look     cel | real | hybrid
  quality  final (2560 x 1440) | test (1280 x 720, few samples) | mini (960 x 540)
  hover    "hover" = option 2 (the Rack) hovered: the power cut is done in 3D (lights and emitters outside the branch)
  renders  comma list of main,vol,data (default all)
Passes land in ../scratch/bl_<look>[_hover]/.
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import cam_rig as R  # noqa: E402
import sgraph3 as G  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

# CRITIQUE §5 brightness ladder: options 1.8, TARGET 1.7, current 1.1, walked 0.6, ahead 0.35 (cool), past 0.12
# the ladder is the critique's, scaled x0.5 for our exposure (2.6 vs 0.75): options read 0.70-0.82, not washed out
STATE_K = {"option": 0.9, "current": 0.55, "walked": 0.3, "reach": 0.3, "grey": 0.06, "target": 0.85}
POWER_K = 0.22          # hover power cut in 3D: emitters and lights outside the branch drop to 22 %
POWER_BOOST = 1.45      # branch rooms light x(1 + 0.45), as in V3 dynamic

QUAL = {
    # r2: GPU (HIP + HIP-RT, RX 6700 XT): 128 spp main + OIDN; the volume pass at 800 x 450 and 64 spp (4x the CPU spp)
    "final": dict(res=[2560, 1440], data_res=[3840, 2160], vol_res=[800, 450], samples=128, vol_samples=64,
                  threshold=0.01, vol_threshold=0.02),
    "test": dict(res=[1280, 720], data_res=[1920, 1080], vol_res=[640, 360], samples=64, vol_samples=32,
                 threshold=0.03, vol_threshold=0.04),
    "mini": dict(res=[960, 540], data_res=[1440, 810], vol_res=[480, 270], samples=24, vol_samples=16,
                 threshold=0.06, vol_threshold=0.06),
}


def room_k(walked):
    st, opts = G.states(walked)
    return {i: STATE_K.get(st[i], 1.0) for i in G.NODES}


def make(look, quality="final", hover=False, renders=None):
    st = R.stills()
    pose, state = st["O_overview"]
    walked = state["walked"]
    tag = look + ("_hover" if hover else "")
    out = os.path.join(SCR, "bl_" + tag + ("" if quality == "final" else "_" + quality))
    job = dict(QUAL[quality], look=look, out=out, room_k=room_k(walked),
               shots=[dict(name="O_overview", pose=pose.to_json(), t=2.0, protect=[])])
    st_, _ = G.states(walked)
    job["edge_states"] = {"%s|%s" % k: v for k, v in G.edge_states(walked, st_).items()}
    if renders:
        job["renders"] = renders
    job["room_state"] = {i: st_[i] for i in G.NODES}
    job["power"] = dict(room_k=job["room_k"])
    if hover:
        br = G.branch(G.HOVER_MID)[0]
        job["power"].update(keep=sorted(set(br) | {walked[-1]}), k=POWER_K, boost=POWER_BOOST)
    return job, tag + "_" + quality


def run(job, tag):
    os.makedirs(job["out"], exist_ok=True)
    lay = os.path.join(SCR, "layout.json")
    G.dump(lay)
    job["layout"] = lay
    jp = os.path.join(SCR, "job_%s.json" % tag)
    with open(jp, "w") as f:
        json.dump(job, f, indent=1)
    log = os.path.join(SCR, "bl_%s.log" % tag)
    t0 = time.time()
    with open(log, "w") as f:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "scene_aaa.py"), "--", jp],
                           stdout=f, stderr=subprocess.STDOUT)
    print("exit", r.returncode, "log", log, "wall %.0f s" % (time.time() - t0), flush=True)
    return r.returncode


if __name__ == "__main__":
    look = sys.argv[1]
    q = sys.argv[2] if len(sys.argv) > 2 else "final"
    hv = len(sys.argv) > 3 and sys.argv[3] == "hover"
    rd = sys.argv[4].split(",") if len(sys.argv) > 4 else None
    job, tag = make(look, q, hv, rd)
    for extra in sys.argv[5:]:
        _k, _, _v = extra.partition("=")
        try:
            job[_k] = json.loads(_v) if _v else True
        except ValueError:
            job[_k] = _v
        if _k == "out":         # r3: write the passes into an existing pass folder (e.g. re-render only vol/trans)
            job["out"] = os.path.join(SCR, _v)
        tag += "_" + _k
    sys.exit(run(job, tag))
