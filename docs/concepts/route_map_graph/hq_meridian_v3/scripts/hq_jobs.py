"""HQ kit: shot lists (stills, the reveal, the mechanic sheet shots) and the headless Blender launcher.

python hq_jobs.py stills  [quality] [names,..]   -> <big>/bl_stills[_q]/<name>_*.npy
python hq_jobs.py sheet   [quality]              -> the mechanic-state shots (hq_graph.SHEET_SHOTS)
python hq_jobs.py reveal  [quality] [a b]        -> <big>/bl_reveal[_q]/r###_*.npy (hq_graph.REVEAL)
quality: final | video | test | mini | eevee (layout preview: Eevee, no GPU lock needed) | dry
Every frame's overlay state goes to ../scratch/ov_<kind>.json (compose reads it). Blender logs go to ../scratch/.
GPU rule: Cycles qualities refuse to run unless this process holds D:/rc_scratch/GPU_LOCK (gpu_lock.py).
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_cam as CR  # noqa: E402
import hq_graph as G  # noqa: E402
import hq_preset as HP  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
BIG = HP.PRESET["hq"]["out_big"]
os.makedirs(BIG, exist_ok=True)
os.makedirs(SCR, exist_ok=True)
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
LOCK = r"D:\rc_scratch\GPU_LOCK"
QUAL = {
    "final": dict(res=[2560, 1440], samples=64, threshold=0.015, step_rate=1.2),
    "sheet": dict(res=[1280, 720], samples=48, threshold=0.02, step_rate=1.5),
    "video": dict(res=[960, 540], samples=12, threshold=0.06, step_rate=3.0),   # upscaled to 1280 x 720 by the encoder
    "test": dict(res=[1280, 720], samples=32, threshold=0.04, step_rate=2.0),
    "mini": dict(res=[640, 360], samples=16, threshold=0.06, step_rate=3.0),
    "eevee": dict(res=[960, 540], samples=24, engine="EEVEE"),
    "board": dict(res=[960, 540], samples=32, threshold=0.04, step_rate=2.0),
}
POWER_K, POWER_BOOST = 0.22, 1.45
FPS = 24


def frame(name, pose, walked, zoom, hover=None, hover_k=0.0, mt=None, extra=None):
    mt = (len(walked) - 1) if mt is None else mt
    if hasattr(G, "set_shot"):
        G.set_shot(extra or {})
    st, opts = G.states(walked, int(mt))
    me = G.mech(walked, int(mt))
    fr = dict(name=name, pose=pose.to_json(), zoom=zoom, mt=mt, room_state=st, affected=me.get("affected", []),
              movers=dict(G.MOVER_POS(mt, walked), **(extra or {}).get("movers", {})), mech=dict(me, **(extra or {})),
              power=None)
    if hover and hover_k > 0.5:
        br = G.branch(hover, walked, int(mt))[0]
        fr["power"] = dict(keep=sorted(br | {walked[-1]}), k=POWER_K, boost=POWER_BOOST)
    # HQ_REV_V2: the section cut (downtown.section_params): overview = the keep, decision / hover = the framed rooms
    dtc = HP.PRESET["hq"].get("downtown")
    if dtc and not (extra or {}).get("no_section"):
        from hq_kit import downtown as KDT
        # v3: the OCCLUSION rule (flatten, then ghost): the cone from the camera to the target volume = the active
        # room + the visible route nodes (overview: every route node)
        if zoom < 0.5 or (extra or {}).get("section_keep"):
            ids = [i for i in G.NODES if i != "start" and i not in getattr(G, "OCC_HIDDEN", ())]
        else:
            ids = [i for i in [walked[-1]] + list(opts) if i != "start"]
        pts = [c for i in ids for c in G.room_front(i, mt)]
        if pts:
            fr["section"] = KDT.occlusion_params(pose.loc(), pts, dtc)
    ov = dict(walked=walked, hover=hover, hover_k=hover_k, zoom=zoom, mt=mt, pose=pose.to_json(), extra=extra or {})
    return fr, ov


def stills():
    out = []
    for name, (p, s) in CR.stills().items():
        w = s["walked"]
        out.append(frame(name, p, w, CR.zoom_of(p, w) if name != "H_overview" else 0.0, s.get("hover"),
                         s.get("hover_k", 0.0), s.get("mt"), s.get("extra")))
    return out


def sheet():
    return [frame(name, p, s["walked"], CR.zoom_of(p, s["walked"]), s.get("hover"), s.get("hover_k", 0.0), s.get("mt"),
                  s.get("extra")) for name, (p, s) in G.SHEET_SHOTS(CR).items()]


def reveal():
    out = []
    for k, (t, pose, walked, mt, extra) in enumerate(G.REVEAL(CR)):
        fr, ov = frame("r%03d" % k, pose, walked, CR.zoom_of(pose, walked), mt=mt, extra=extra)
        ov.update(t=t, ui=extra.get("ui", 1.0), route=extra.get("route", 1.0))
        out.append((fr, ov))
    return out


def have_lock():
    if not os.path.exists(LOCK):
        return False
    return open(LOCK, errors="replace").read().startswith("meridian_v3")


def run(kind, frames, quality, out_dir, chunk=None, extra=None):
    q = QUAL[quality]
    if q.get("engine", "CYCLES") == "CYCLES" and not have_lock():
        print("REFUSED: Cycles render without D:/rc_scratch/GPU_LOCK held by hq_rev", flush=True)
        return 9
    os.makedirs(out_dir, exist_ok=True)
    chunks = [frames] if not chunk else [frames[i:i + chunk] for i in range(0, len(frames), chunk)]
    for ci, ch in enumerate(chunks):
        job = dict(q, out=out_dir, frames=ch)
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
        print(kind, "chunk", ci, "exit", r.returncode, "TRACEBACK" if bad else "ok", "log", log,
              "wall %.0f s" % (time.time() - t0), flush=True)
        if bad:
            return 3
        if r.returncode:
            return r.returncode
    return 0


def save_ov(name, ovs, merge=False):
    path = os.path.join(SCR, name + ".json")
    if merge and os.path.exists(path):
        old = json.load(open(path))
        old.update(ovs)
        ovs = old
    with open(path, "w") as f:
        json.dump(ovs, f, indent=1)


def out_dir(kind, q):
    return os.path.join(BIG, "bl_" + kind + ("" if q in ("final", "video", "sheet") else "_" + q))


if __name__ == "__main__":
    what = sys.argv[1]
    q = sys.argv[2] if len(sys.argv) > 2 else "final"
    extra = {}
    for kv in sys.argv[4:]:
        if "=" in kv:
            k_, _, v_ = kv.partition("=")
            extra[k_] = json.loads(v_)
    if what in ("stills", "sheet"):
        S = stills() if what == "stills" else sheet()
        names = sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[3] != "all" else None
        S = [s for s in S if names is None or s[0]["name"] in names]
        save_ov("ov_" + what, {f["name"]: o for f, o in S}, merge=True)
        if q == "dry":
            for f, o in S:
                print(f["name"], f["pose"]["loc"], f["zoom"], f["movers"])
            sys.exit(0)
        sys.exit(run(what + "_" + q, [f for f, _ in S], q, out_dir(what, q), extra=dict(extra, force=True)))
    if what == "shots":
        # any shot list the graph offers (G.<fn>(CR) -> {name: (pose, state)}): python hq_jobs.py shots <fn> <quality>
        fn = sys.argv[2]
        q = sys.argv[3] if len(sys.argv) > 3 else "board"
        S = [frame(n, p, s_["walked"], CR.zoom_of(p, s_["walked"]), s_.get("hover"), s_.get("hover_k", 0.0), s_.get("mt"),
                   s_.get("extra")) for n, (p, s_) in getattr(G, fn)(CR).items()]
        save_ov("ov_" + fn, {f["name"]: o for f, o in S}, merge=False)
        qq = "eevee" if q.endswith("eevee") else q
        sys.exit(run("shots_%s_%s" % (fn, q), [f for f, _ in S], qq, os.path.join(BIG, "bl_%s_%s" % (fn, q)),
                     extra=dict(force=True)))
    if what == "reveal":
        fr = reveal()
        save_ov("ov_reveal", {f["name"]: o for f, o in fr})
        a = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        b = int(sys.argv[4]) if len(sys.argv) > 4 else len(fr)
        step = int(sys.argv[5]) if len(sys.argv) > 5 else 1
        if q == "dry":
            print("reveal", len(fr), "frames")
            sys.exit(0)
        sys.exit(run("reveal_%d_%d" % (a, b), [f for f, _ in fr[a:b:step]], q, out_dir("reveal", q), chunk=48))
# OCC_V3
