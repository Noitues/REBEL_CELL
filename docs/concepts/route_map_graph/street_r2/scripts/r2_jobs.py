"""Street round 2: the render jobs (headless Blender 5.2, Cycles HIP, one job per GPU lock).

python r2_jobs.py prep <seed>                       layout + plan + sign textures for an art seed
python r2_jobs.py dry <seed>                        build the scene only (no render, no GPU): errors and counts
python r2_jobs.py test <seed> [k=v ...]             960 px OVERVIEW + DECISION, walls closed, 16 spp (GPU lock)
python r2_jobs.py finals <seed> [names]             the 1920 plates: ov_closed, ov_open, dec_closed (GPU lock)

Renders go to D:/rc_scratch/street_r2/render_s<seed>/. The street, rooms and cameras are the v3 derivation
(r2_rules.derive_v3); the city is the r2 layout of the seed; the dressing is the seed's plan.
GPU protocol (D:/rc_scratch/GPU_QUEUE.md): the lock is created atomically and held only for the Blender job;
while it is taken, GPU_WAITING_street_r2 marks the wait; before re-taking it, other waiting agents go first.
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import r2_config as CFG  # noqa: E402
import r2_rules as RR  # noqa: E402

SBS = os.path.normpath(os.path.join(HERE, "..", "..", "storyboard", "scripts"))
sys.path.insert(1, SBS)
import sb_ocjobs as OJ  # noqa: E402  (read-only: its LOOK block is the approved v3-r3 look)

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
SCR = RR.SCR
LOCK = "D:/rc_scratch/GPU_LOCK"
WAIT = "D:/rc_scratch/GPU_WAITING_street_r2"
ME = "street_r2"
R = CFG.RULES_R2
A_ = R["atmosphere.layers"]
FG = R["foreground.street"]
LOOK = dict(OJ.LOOK)
LOOK.update(haze=A_["sky_haze"], back_haze=A_["back_haze"], back_haze_band=list(A_["back_haze_band"]),
            back_haze_top=A_["back_haze_top"], plume_k=A_["plume_k"], scatter=list(R["palette.districts"]["scatter"]),
            sign_k=1.0, lamp=60.0, facade_wash=R["streets.light"]["facade_wash"],
            section_spill=R["streets.light"]["section_spill"])


def out_dir(seed):
    return os.path.join(SCR, "render_s%s" % seed)


def job_block(seed, frames, spp):
    D = RR.derive_v3()
    return dict(mode="cycles", seed=int(seed), route_keys=D["route_keys"], route_uids=D["route_uids"], rooms=D["rooms"],
                street=dict(a=D["a"], c=D["c"]), look=LOOK, nrm=D["nrm"], layout_path=os.path.join(SCR, "unified_r2_s%s.json" % seed),
                edges=D["edges"], col_info=D["col_info"], plan_path=os.path.join(SCR, "plan_s%s.json" % seed),
                signs_dir=os.path.join(SCR, "signs_s%s" % seed), plinth_off=8.0 / 2 + 0.2,
                plinth=dict(albedo=FG["fill_albedo"], edge=0.05, edge_k=0.0, on=(1.5, 5.0), wet=True),
                lamp_post_h=R["streets.light"]["lamp_post_h"], frames=frames, spp=spp)


def cams(seed):
    D = RR.derive_v3()
    ov, dec = D["overview"], D["decision"]
    for c in (ov, dec):
        c["persp"].setdefault("tgt", c["target"])
    return D, ov, dec


def frame(name, c, res, **kw):
    d = dict(name=name, persp=dict(c["persp"]), t=OJ.SB.T["b4"], res=res, zcut=FG["zcut_street"])
    d.update(kw)
    return d


# ---------------------------------------------------------------- GPU lock
def _others_waiting():
    return [f for f in os.listdir("D:/rc_scratch") if f.startswith("GPU_WAITING_") and f != os.path.basename(WAIT)]


def _older_waiters():
    """Other agents that started waiting before this one (first come, first served)."""
    if not os.path.exists(WAIT):
        return _others_waiting()
    mine = os.path.getmtime(WAIT)
    return [f for f in _others_waiting() if os.path.getmtime(os.path.join("D:/rc_scratch", f)) < mine]


def acquire(first=True):
    """Take the lock when it is free and no agent that started waiting earlier is still waiting (first come, first
    served). Others poll every 2-5 min (GPU_QUEUE.md), so a waiting file that has not taken a free lock for 7 polls
    (about 6 min) in a row is treated as stale."""
    t0 = time.time()
    free_polls = 0
    while True:
        free = not os.path.exists(LOCK)
        free_polls = free_polls + 1 if free else 0
        if free and (not _older_waiters() or free_polls >= 7):
            try:
                fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, ("%s %s\n" % (ME, time.strftime("%Y-%m-%d %H:%M:%S"))).encode())
                os.close(fd)
                if os.path.exists(WAIT):
                    os.remove(WAIT)
                print("GPU lock taken after %.0f s" % (time.time() - t0), flush=True)
                return
            except FileExistsError:
                pass
        if not os.path.exists(WAIT):
            open(WAIT, "w").write("%s waiting since %s\n" % (ME, time.strftime("%H:%M:%S")))
        time.sleep(60)


def release():
    if os.path.exists(LOCK) and open(LOCK).read().startswith(ME):
        os.remove(LOCK)
        print("GPU lock released", flush=True)


def run(seed, frames, spp, tag, gpu=True):
    od = out_dir(seed)
    os.makedirs(od, exist_ok=True)
    cf = os.path.join(SCR, "cams_%s.json" % tag)
    of = os.path.join(SCR, "job_%s.json" % tag)
    json.dump([], open(cf, "w"))
    json.dump(job_block(seed, frames, spp), open(of, "w"))
    log = os.path.join(SCR, "blender_%s.log" % tag)
    if gpu:
        acquire()
    t0 = time.time()
    try:
        env = dict(os.environ, NET36="net_scope.json")
        with open(log, "w") as f:
            r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "r2_scene.py"), "--",
                                "meridian_hq", od, cf, of], stdout=f, stderr=subprocess.STDOUT, env=env)
    finally:
        if gpu:
            release()
    print(tag, "exit", r.returncode, "wall %.0f s" % (time.time() - t0), "log", log, flush=True)
    return r.returncode


def prep(seed):
    RR.layout_pass(int(seed))
    RR.plan_pass(int(seed))
    import r2_signs
    r2_signs.make(seed)


if __name__ == "__main__":
    w, seed = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "1"
    kv = dict(a.split("=") for a in sys.argv[3:] if "=" in a)
    for k, v in kv.items():
        LOOK[k] = float(v) if k in LOOK or "." in v or v.isdigit() else v
    names = [a for a in sys.argv[3:] if "=" not in a]
    D, ov, dec = cams(seed)
    allopen = {i: 1.0 for i in D["rooms"]}
    if w == "prep":
        prep(seed)
    elif w == "dry":
        run(seed, [], 1, "dry_s%s" % seed, gpu=False)
    elif w == "test":
        res = [int(kv.get("res", 960)), int(kv.get("res", 960)) * 9 // 16]
        fr = [frame("T_ov_closed", ov, res), frame("T_dec_closed", dec, res)]
        if names:
            fr = [f for f in fr if f["name"] in names]
        run(seed, fr, int(kv.get("spp", 16)), "test_s%s" % seed)
    elif w == "finals":
        all_ = dict(ov_closed=frame("F_ov_closed", ov, [1920, 1080]), ov_open=frame("F_ov_open", ov, [1920, 1080], dis=allopen),
                    dec_closed=frame("F_dec_closed", dec, [1920, 1080]))
        sel = names or list(all_)
        run(seed, [all_[n] for n in sel], int(kv.get("spp", 48)), "finals_s%s_%s" % (seed, "_".join(sel)))
