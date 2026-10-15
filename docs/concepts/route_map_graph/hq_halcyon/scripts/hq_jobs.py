"""HQ Halcyon: the shot lists (stills, the orbit run, the reveal) and the headless Blender launcher.

python hq_jobs.py stills [quality] [names,..]     -> ../scratch/bl_stills/<name>_*.npy
python hq_jobs.py orbit  [quality] [a b]          -> ../scratch/bl_orbit/o###_*.npy   (H_orbit_run, 144 frames)
python hq_jobs.py reveal [quality] [a b]          -> ../scratch/bl_reveal/r###_*.npy  (H_reveal, 168 frames)
python hq_jobs.py preview <name>                  -> a 640 x 360 test of one still
quality: final | test | mini. Every frame's overlay state goes to ../scratch/<shots>.json (compose reads it).
Blender logs go to ../scratch/ (never piped).
"""
import json
import math
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_cam as CR  # noqa: E402
import hq_graph as G  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
BIG = r"D:\rc_scratch\halcyon"          # render passes and frames (C: is short of space); never inside D:\Godot\rebel_cell
os.makedirs(BIG, exist_ok=True)
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
QUAL = {
    "final": dict(res=[2560, 1440], samples=128, threshold=0.01, step_rate=1.0),
    "video": dict(res=[1280, 720], samples=24, threshold=0.04, step_rate=2.0),
    "test": dict(res=[1280, 720], samples=32, threshold=0.04, step_rate=2.0),
    "mini": dict(res=[640, 360], samples=16, threshold=0.06, step_rate=3.0),
}
POWER_K, POWER_BOOST = 0.22, 1.45
FPS = 24


def face_az(f):
    n = G.N[f]
    return math.degrees(math.atan2(n[0], n[1]))


def sweep_z(az, frac):
    """The blade's scan line inside the sector: frac 0 = the top room row in the sector, 1 = the bottom one."""
    zs = sorted({G.room_z(n)[0] for n in G.NODES if n not in ("start", "srv") and G.in_sector(G.room_az(n), az)})
    if not zs:
        return 40.0
    top, bot = zs[-1] + G.RH * 0.6, zs[0] + G.RH * 0.3
    return top + (bot - top) * frac


def frame(name, pose, walked, zoom, hover=None, hover_k=0.0, eye=None, step=None):
    st, opts = G.states(walked)
    sc, az = G.scanned(walked)
    zs = [G.room_z(i)[0] + G.RH * 0.5 for i in sc if st[i] == "option"]
    pt = [G.room_center(i) for i in sc if st[i] == "option"]
    e = dict(az=az, sweep=zs[0] if zs else sweep_z(az, 0.45), sweep_pt=pt[0] if pt else None, wash=1.0, beam=1.0)
    if eye:
        e.update(eye)
    fr = dict(name=name, pose=pose.to_json(), zoom=zoom, room_state=st, scanned=sc, eye=e, power=None)
    if hover and hover_k > 0.5:
        br = G.branch(hover, walked)[0]
        fr["power"] = dict(keep=sorted(br | {walked[-1]}), k=POWER_K, boost=POWER_BOOST)
    ov = dict(walked=walked, hover=hover, hover_k=hover_k, zoom=zoom, step=step, eye_az=e["az"], pose=pose.to_json())
    return fr, ov


def stills():
    out = []
    S = CR.stills()
    for name, (p, s) in S.items():
        w = s["walked"]
        out.append(frame(name, p, w, CR.zoom_of(p, w), s.get("hover"), s.get("hover_k", 0.0)))
    return out


# ------------------------------------------------------------------ H_orbit_run: two steps round the SE corner
def orbit_run():
    w5 = ["start"] + ["n%d" % i for i in range(1, 6)]
    w6 = w5 + ["n6"]
    w7 = w6 + ["n7"]
    fr = []

    def eye_at(walked):
        return G.scanned(walked)[1]

    def hold(walked, n, pose=None, zoom=None):
        p = pose or CR.decision(walked)
        for k in range(n):
            fr.append((p, walked, CR.zoom_of(p, walked) if zoom is None else zoom, None,
                       dict(az=eye_at(walked), sweep=sweep_z(eye_at(walked), (len(fr) % 36) / 36.0))))

    def step(a, b, n):
        p0, p1 = CR.decision(a), CR.decision(b)
        az0, az1 = eye_at(a), eye_at(b)
        if az1 < az0:
            az1 += 360.0
        for k in range(n):
            t = CR.ease((k + 1) / n)
            p = p0.mix(p1, t)
            p.yaw = CR.lerp(p0.yaw, p1.yaw, t)
            azt = CR.lerp(az0, az1, t) % 360.0
            fr.append((p, a if k < n - 1 else b, CR.zoom_of(p, b), (a[-1], b[-1], CR.ease(min(1.0, (k + 1) / n * 1.12))),
                       dict(az=azt, sweep=sweep_z(azt, (len(fr) % 36) / 36.0))))

    hold(w5, 12)
    step(w5, w6, 24)
    hold(w6, 10)
    step(w6, w7, 38)
    hold(w7, 14)
    d, o = CR.decision(w7), CR.overview(w7)
    for k in range(30):
        t = CR.ease((k + 1) / 30)
        p = d.mix(o, t)
        fr.append((p, w7, CR.zoom_of(p, w7), None, dict(az=eye_at(w7), sweep=sweep_z(eye_at(w7), (len(fr) % 36) / 36.0))))
    hold(w7, 16, pose=o, zoom=0.0)
    out = []
    for k, (p, walked, z, stp, eye) in enumerate(fr):
        f_, ov = frame("o%03d" % k, p, walked, z, eye=eye, step=stp)
        out.append((f_, ov))
    return out


# ------------------------------------------------------------------ H_reveal: a rising half-orbit into the overview
REVEAL_T = 6.0
FLASH_T = 3.0


def reveal_poses():
    w = ["start"]
    o = CR.overview(w)
    p0 = CR.Pose((0.0, 0.0, 58.0), o.yaw + 180.0, -9.0, 175.0, 24.0, 0.0, 0.02)
    n = int(REVEAL_T * FPS)
    out = []
    for k in range(n):
        t = k / (n - 1)
        e = CR.ease(min(1.0, t / 0.86))
        p = p0.mix(o, e)
        p.yaw = CR.lerp(p0.yaw, o.yaw, e)
        out.append((t * REVEAL_T, p))
    return out, w


def reveal_eye(times, poses):
    """The lighthouse turns clockwise (az increasing) and ends on the watched face of step 0; its beam is timed to pass
    the camera near FLASH_T. The camera's azimuth (seen from the eye) is yaw + 180."""
    end_az = G.scanned(["start"])[1]
    best = None
    for om in [x * 2.0 for x in range(30, 120)]:
        def az(t):
            return end_az - om * (REVEAL_T - t)
        for (t, p) in zip(times, poses):
            ca = (p.yaw + 180.0) % 360.0
            d = (az(t) - ca + 180.0) % 360.0 - 180.0
            if abs(d) < 2.5 and 2.2 < t < 3.8:
                if best is None or abs(t - FLASH_T) < abs(best[1] - FLASH_T):
                    best = (om, t)
                break
    om = best[0] if best else 120.0
    return (lambda t: end_az - om * (REVEAL_T - t)), (best[1] if best else None), om


def reveal():
    tp, w = reveal_poses()
    times = [t for t, _ in tp]
    poses = [p for _, p in tp]
    az, t_flash, om = reveal_eye(times, poses)
    out = []
    for k, (t, p) in enumerate(tp):
        a = az(t)
        iris = min(1.0, max(0.05, (t - 0.6) / 0.8))     # the eye wakes in the first second
        eye = dict(az=a % 360.0, sweep=sweep_z(a % 360.0, (t * 0.7) % 1.0), wash=iris, beam=iris, iris=iris, blade=iris)
        f_, ov = frame("r%03d" % k, p, w, CR.zoom_of(p, w), eye=eye)
        ov.update(t=t, t_flash=t_flash, ui=CR.ease((t - 4.9) / 0.9))
        out.append((f_, ov))
    return out, t_flash, om


# ------------------------------------------------------------------ launcher
def run(kind, frames, quality, out_dir, chunk=None, extra=None):
    os.makedirs(out_dir, exist_ok=True)
    lay = os.path.join(SCR, "layout.json")
    G.dump(lay, G.WALK_LATE)
    chunks = [frames] if not chunk else [frames[i:i + chunk] for i in range(0, len(frames), chunk)]
    for ci, ch in enumerate(chunks):
        job = dict(QUAL[quality], layout=lay, out=out_dir, frames=ch, ov_pose=CR.overview(G.WALK_LATE).to_json())
        job.update(extra or {})
        jp = os.path.join(SCR, "job_%s_%d.json" % (kind, ci))
        with open(jp, "w") as f:
            json.dump(job, f, indent=1)
        log = os.path.join(SCR, "bl_%s_%d.log" % (kind, ci))
        t0 = time.time()
        with open(log, "w") as f:
            r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "hq_scene.py"), "--",
                                jp], stdout=f, stderr=subprocess.STDOUT)
        bad = "Traceback" in open(log, errors="replace").read()
        print(kind, "chunk", ci, "exit", r.returncode, "TRACEBACK" if bad else "ok", "log", log, "wall %.0f s" % (time.time() - t0), flush=True)
        if bad:
            return 3
        if r.returncode:
            return r.returncode
    return 0


def save_ov(name, ovs):
    path = os.path.join(SCR, name + ".json")
    if name == "ov_stills" and os.path.exists(path):
        old = json.load(open(path))
        old.update(ovs)
        ovs = old
    with open(path, "w") as f:
        json.dump(ovs, f, indent=1)


if __name__ == "__main__":
    what = sys.argv[1]
    q = sys.argv[2] if len(sys.argv) > 2 else "final"
    if what in ("stills", "preview"):
        S = stills()
        extra = {}
        if what == "preview":
            names = [sys.argv[2]]
            q = sys.argv[3] if len(sys.argv) > 3 else "mini"
            for kv in sys.argv[4:]:
                k_, _, v_ = kv.partition("=")
                extra[k_] = json.loads(v_)
        else:
            names = sys.argv[3].split(",") if len(sys.argv) > 3 else None
        S = [s for s in S if names is None or s[0]["name"] in names]
        save_ov("ov_stills", {f["name"]: o for f, o in S})
        out = os.path.join(BIG if q == "final" else SCR, "bl_stills" + ("" if q == "final" else "_" + q))
        sys.exit(run("stills_" + q, [f for f, _ in S], q, out, extra=dict(extra, force=True) if what == "preview" else None))
    if what in ("orbit", "reveal"):
        if what == "orbit":
            fr = orbit_run()
        else:
            fr, tf, om = reveal()
            print("reveal: beam passes the camera at t =", tf, "eye speed", om, "deg/s")
        save_ov("ov_" + what, {f["name"]: o for f, o in fr})
        a = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        b = int(sys.argv[4]) if len(sys.argv) > 4 else len(fr)
        if q == "dry":
            print(what, len(fr), "frames")
            sys.exit(0)
        out = os.path.join(BIG if q == "video" else SCR, "bl_" + what + ("" if q == "video" else "_" + q))
        sys.exit(run(what + "_%d_%d" % (a, b), [f for f, _ in fr[a:b]], q, out, chunk=48))
