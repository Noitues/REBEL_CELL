"""Storyboard v3: render shots of the mainline city (m44/unified39.py, Eevee, headless) into ../scratch/m_bl.

python sb_mjobs.py hq            the mainline HQ camera (orthographic, the fit rule in sb_mainline)
python sb_mjobs.py dive [step]   the dive's mainline part (perspective), every `step`-th frame
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import sb_mainline as ML  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = "D:/rc_scratch/storyboard/m_bl"
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


def run(cams, name):
    os.makedirs(OUT, exist_ok=True)
    cf = os.path.join(ROOT, "scratch", "m_cams_%s.json" % name)
    json.dump(cams, open(cf, "w"), indent=1)
    log = os.path.join(ROOT, "scratch", "m_%s.log" % name)
    env = dict(os.environ, NET36="net_scope.json")
    with open(log, "w") as f:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "m44", "unified39.py"), "--",
                            "meridian_hq", OUT, cf], stdout=f, stderr=subprocess.STDOUT, env=env)
    print(name, "exit", r.returncode, flush=True)


def hq_spec(res=(1920, 1080)):
    t, o = ML.hq_cam()
    return dict(tag="m_hq", t=list(ML.L.lots(t[0], t[1])), ortho=o, res=list(res), samples=16)


if __name__ == "__main__":
    w = sys.argv[1]
    if w == "hq":
        run([hq_spec()], "hq")
    elif w == "dive":
        import sb_cams as SB
        step = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        cams = []
        for f in range(SB.NF):
            s, pose, ex = SB.cam_at(f)
            if s != "dive" or not SB.mainline_dive(f):
                continue
            if (f - SB.segments()[1][1]) % step:
                continue
            pm = SB.dive_pose_m(ex["u"])
            cams.append(dict(tag="m_f%04d" % f, persp=pm, res=[1280, 720], samples=12))
        # the dive board in the band, at 1920 (its AAA-2 twin is sb_jobs.py dive_board dboard_a)
        u = 0.46
        cams.append(dict(tag="m_dboard_a", persp=SB.dive_pose_m(u), res=[1920, 1080], samples=16))
        run(cams, "dive")
