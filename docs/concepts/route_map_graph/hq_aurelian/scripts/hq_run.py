"""Aurelian HQ: run the Meridian v3 engine on the Aurelian corp modules (no engine copies).

python hq_run.py px                         the OVERVIEW room sizes (px tall at 1920 x 1080) against the 46 px target
python hq_run.py stills <quality> [names]   render (test: Cycles under the GPU lock, owner "aurelian"; eevee: preview,
                                            no lock), then plates + composites + values -> ../scratch/<quality>/
Names default to all stills (H_overview, H_decision, H_decision_cavea, H_hover).
"""
import json
import os
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aur_env  # noqa: E402

aur_env.setup()
import gpu_lock  # noqa: E402  (the shared GPU queue, Meridian v3's module)

gpu_lock.ME = "aurelian"
import hq_cam as CR  # noqa: E402
import hq_graph as G  # noqa: E402
import hq_jobs as J  # noqa: E402

J.HERE = aur_env.AUR                 # run() launches ./hq_scene.py: the Aurelian entry
J.SCR = aur_env.SCR
J.BIG = aur_env.BIG
J.have_lock = lambda: os.path.exists(J.LOCK) and open(J.LOCK, errors="replace").read().startswith("aurelian")
TARGET_PX = 46.0
import hq_preset as _HQP  # noqa: E402
HP_H = _HQP.PRESET["hq"]


def px():
    pose = CR.overview(G.WALK_OV)
    print("OVERVIEW yaw %.1f pitch %.1f dist %.1f lens %.1f sx %.3f sy %.3f" % (pose.yaw, pose.pitch, pose.dist,
                                                                               pose.lens, pose.sx, pose.sy))
    rows = []
    for i in G.NODES:
        if i == "start":
            continue
        f = G.room_front(i)
        q = [pose.proj(p, w=1920) for p in f]
        if any(v is None for v in q):
            continue
        hpx = 0.5 * (abs(q[3][1] - q[0][1]) + abs(q[2][1] - q[1][1]))
        vis = CR.visible_room(i, pose)
        rows.append((G.SLOT[i]["level"], i, hpx, vis, min(v[0] for v in q), min(v[1] for v in q)))
    for lvl in sorted(set(r[0] for r in rows), key=lambda L: [r[0] for r in rows].index(L)):
        rr = [r for r in rows if r[0] == lvl]
        print("%-6s rooms %2d  px tall min %.1f max %.1f  %s" % (lvl, len(rr), min(r[2] for r in rr),
              max(r[2] for r in rr), "PASS" if min(r[2] for r in rr) >= TARGET_PX else "FAIL"))
    xs = [r[4] for r in rows]
    ys = [r[5] for r in rows]
    print("room screen box x %.0f-%.0f y %.0f-%.0f (frame 1920 x 1080)" % (min(xs), max(xs), min(ys), max(ys)))
    return rows


def stills(q, names):
    S = J.stills()
    S = [s for s in S if names is None or s[0]["name"] in names]
    J.save_ov("ov_stills", {f["name"]: o for f, o in S}, merge=True)
    out = J.out_dir("stills", q)
    cycles = J.QUAL[q].get("engine", "CYCLES") == "CYCLES"
    if cycles:
        gpu_lock.acquire("aurelian test " + ",".join(f["name"] for f, _ in S), poll=60)
    try:
        t0 = time.time()
        rc = J.run("stills_" + q, [f for f, _ in S], q, out, extra=dict(force=True))
        print("render rc %s %.0f s" % (rc, time.time() - t0), flush=True)
    finally:
        if cycles:
            gpu_lock.release()
    if rc:
        return rc
    return post(q, [f["name"] for f, _ in S])


def post(q, names):
    """Plates + composites + values from the rendered passes (no render: the post / grade can be re-tuned)."""
    import hq_compose as C
    import hq_post as PO
    import hq_values as V
    dst = os.path.join(aur_env.SCR, q)
    os.makedirs(dst, exist_ok=True)
    ovs = json.load(open(os.path.join(aur_env.SCR, "ov_stills.json")))
    vp = os.path.join(dst, "values.json")
    res = json.load(open(vp)) if os.path.exists(vp) else {}      # merge: a partial run keeps the other frames' values
    out = J.out_dir("stills", q)
    for n in names:
        stem = os.path.join(out, n)
        e0 = PO.P["exposure"]
        PO.P["exposure"] = e0 * 2.0 ** HP_H.get("frame_stops", {}).get(n, 0.0)
        try:
            plate = PO.finish(stem, ovs[n]["zoom"], t=2.0)
        finally:
            PO.P["exposure"] = e0
        pp = os.path.join(dst, n + "_plate.png")
        plate.save(pp)
        C.compose(plate, ovs[n]).save(os.path.join(dst, n + ".png"))
        res[n] = V.check(pp, stem, os.path.join(dst, n + "_thumb.png"))
        print(n, json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res[n].items()}), flush=True)
    json.dump(res, open(os.path.join(dst, "values.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "px":
        px()
    elif what == "cams":
        for name, (p, s) in CR.stills().items():
            print(name, [round(v, 1) for v in p.loc()], "yaw %.1f pitch %.1f dist %.1f lens %.0f" % (
                p.yaw, p.pitch, p.dist, p.lens))
    elif what == "stills":
        q = sys.argv[2]
        names = sys.argv[3].split(",") if len(sys.argv) > 3 else None
        sys.exit(stills(q, names))
    elif what == "post":
        sys.exit(post(sys.argv[2], sys.argv[3].split(",")))
