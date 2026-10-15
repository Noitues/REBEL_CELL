"""Storyboard: write and run the headless Blender jobs (scene_aaa.py + sb_r.py). Logs go to ../scratch, never piped.

python sb_jobs.py <job> [key=value ...]
  test        a quick aerial look test (960 x 540, few samples)
  hq          the HQ aerial still, 1920 x 1080 (dive frame 0)
  dive        the dive frames (1280 x 720), moving
  dive_board  one dive frame at 1920 x 1080 for the board
  ov / dec / h1 / h2   a static hold: the 1920 statics + per-frame dyn and beams at 1280
  zoom        the zoom frames (overview-calm volumes); zoom_dcalm: their volumes again with the decision calm
  hin / hmove the hover ease frames, moving (power cut in 3D)
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
import sb_cams as SB  # noqa: E402
import jobs_aaa as J  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
BLENDER = J.BLENDER
POWER_K = 0.22


def base_job(out, fog_pose):
    walked = SB.WALK
    st, _ = G.states(walked)
    job = dict(J.QUAL["test"], look="real", out=os.path.join(SCR, out), room_k=J.room_k(walked))
    job["edge_states"] = {"%s|%s" % k: v for k, v in G.edge_states(walked, st).items()}
    job["room_state"] = {i: st[i] for i in G.NODES}
    job["power"] = dict(room_k=job["room_k"])
    job.update(hiprt=False, fill=True, calm_rule=True, rules_pose=SB.OVERVIEW.to_json(), fog_pose=fog_pose.to_json(),
               res=[1280, 720], renders=[])
    job["_protect"] = dict(protect_poses=[p.to_json() for p in (SB.OVERVIEW, SB.DECISION, SB.HOVER1, SB.HOVER2)],
                           protect=[walked[-1]] + G.states(walked)[1])
    return job


def power_for(seg, extra):
    if seg in ("hin",):
        k = 1.0 - (1.0 - POWER_K) * extra["k"]
        return dict(keep=sorted(set(G.branch(SB.OPT1)[0]) | {SB.WALK[-1]}), k=k)
    if seg == "h1":
        return dict(keep=sorted(set(G.branch(SB.OPT1)[0]) | {SB.WALK[-1]}), k=POWER_K)
    if seg in ("hmove", "h2"):
        o = SB.OPT2 if (seg == "h2" or extra.get("k", 0) >= 0.5) else SB.OPT1
        return dict(keep=sorted(set(G.branch(o)[0]) | {SB.WALK[-1]}), k=POWER_K)
    return None


MOVE_STEP = 2      # moving shots render every 2nd frame (12 fps); sb_frames reprojects the frames between by depth


def frames_of(seg, f0=None, f1=None):
    out = []
    segs = {s_: (a, b) for s_, a, b in SB.segments()}
    for f in range(SB.NF):
        s, pose, ex = SB.cam_at(f)
        if s != seg or (f0 is not None and f < f0) or (f1 is not None and f > f1):
            continue
        a_, b_ = segs[s]
        if s == "dive" and not SB.aaa_dive(f):
            continue            # v3: the dive's first part is the mainline world (sb_mjobs.py)
        if s == "dive":
            a_ = min(g for g in range(a_, b_ + 1) if SB.aaa_dive(g))
        if s in SB.MOVING and (f - a_) % MOVE_STEP and f != b_:
            continue
        out.append(dict(name="f%04d" % f, pose=pose.to_json(), t=f / SB.FPS, power=power_for(s, ex), fk=SB.fill_fk(s, ex),
                        haze=SB.haze_at(s, ex)[0], fkh=SB.haze_at(s, ex)[1],
                        zoom=SB.zoom_at(s, pose), **({"dis": SB.wall_dis(f)} if s == "dive" else {})))
    return out


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
    print("job", tag, "exit", r.returncode, "log", log, "wall %.0f s" % (time.time() - t0), flush=True)
    return r.returncode


STATIC_POSE = {"ov": SB.OVERVIEW, "dec": SB.DECISION, "h1": SB.HOVER1, "h2": SB.HOVER2}


def make(name, kv):
    if name == "test":
        job = base_job("bl_test", SB.OVERVIEW)
        fr = [dict(name="aerial", pose=SB.AERIAL.to_json(), t=0.0, fk=SB.FILL_FK0, zoom=0.0)]
        for u in (0.5, 0.8):
            f = SB.fr(SB.T["dive"] + u * SB.DIVE_S)
            p = SB.dive_pose(u)
            fr.append(dict(name="dive%02d" % int(u * 100), pose=p.to_json(), t=1.0,
                           fk=SB.fill_fk("dive", dict(u=u)), zoom=SB.zoom_at("dive", p), dis=SB.wall_dis(f)))
        fr += [dict(name="ov", pose=SB.OVERVIEW.to_json(), t=2.0, fk=0.0, dis_all=1),
               dict(name="dec", pose=SB.DECISION.to_json(), t=2.0, fk=0.0, dis_all=1)]
        job["sb"] = dict(mode="full", frames=fr, res=[960, 540], vres=[480, 270], spp=24, vspp=12, tspp=8)
    elif name == "hq":
        job = base_job("bl_hq2", SB.OVERVIEW)
        job["sb"] = dict(mode="full", frames=[dict(name="hq", pose=SB.AERIAL.to_json(), t=SB.T["dive"], fk=SB.FILL_FK0,
                                                   haze=SB.CITY_HAZE, fkh=SB.CITY_HAZE,
                                                   zoom=0.0)],
                         res=[1920, 1080], vres=[960, 540], spp=128, vspp=24, tspp=16)
    elif name == "dive":
        job = base_job("bl_dive2", SB.OVERVIEW)
        job["sb"] = dict(mode="full", frames=frames_of("dive", kv.get("f0"), kv.get("f1")), res=[1280, 720],
                         vres=[640, 360], spp=48, vspp=16, tspp=12)
    elif name == "dive_vol":
        # the volume pass only, at every 4th frame of the dive (the main passes exist at every 2nd frame): the frames'
        # volumes between are reprojected by depth (budget cut under a shared GPU)
        job = base_job("bl_dive2", SB.OVERVIEW)
        fr = [x for x in frames_of("dive") if (int(x["name"][1:]) - SB.segments()[1][1]) % 4 == 0 or x["name"] == "f%04d" % SB.segments()[1][2]]
        job["sb"] = dict(mode="full", frames=fr, res=[960, 540], vres=[400, 225], spp=16, vspp=10, tspp=6, passes=["vol"])
    elif name == "zoomkey":
        # two key frames of the zoom (1/3, 2/3), full passes; the rest of the zoom is reprojected between OVERVIEW,
        # the keys and DECISION
        job = base_job("bl_zoom", SB.OVERVIEW)
        a, b = [(x[1], x[2]) for x in SB.segments() if x[0] == "zoom"][0]
        keys = [a + round((b - a) / 3.0), a + round(2 * (b - a) / 3.0)]
        fr = []
        for f in keys:
            s_, pose, ex = SB.cam_at(f)
            fr.append(dict(name="f%04d" % f, pose=pose.to_json(), t=f / SB.FPS, power=None, fk=0.0, zoom=1.0,
                           dis=SB.wall_dis(f)))
        job["sb"] = dict(mode="full", frames=fr, res=[960, 540], vres=[400, 225], spp=24, vspp=12, tspp=8,
                         dis_all=1.0)
    elif name == "hq_static":
        # v2: the HQ aerial is LIVE: a held render + the moving layers (street traffic lanes, globe) and the beam sweep
        # per frame at 8 fps (blended between); fog-bank drift in 2D
        job = base_job("bl_hq3", SB.OVERVIEW)
        fr = frames_of("hq")
        fr = [x for k, x in enumerate(fr) if k % 3 == 0 or k == len(fr) - 1]
        ex = dict(fk=SB.FILL_FK0, haze=SB.CITY_HAZE, fkh=SB.CITY_HAZE, zoom=0.0, dis_all=0.0)
        job["sb"] = dict(mode="static", static=dict(name="S_hq", pose=SB.AERIAL.to_json(), t=0.0, power=None, extra=ex,
                                                    res=[1920, 1080], spp=128, vres=[960, 540], vspp=32,
                                                    bres=[640, 360], bspp=32, tspp=16),
                         frames=fr, res=[1280, 720], dspp=32, bres=[640, 360], bspp=32, dis_all=0.0,
                         passes=["main", "vol", "dyn", "beams"])
    elif name.startswith("loop_"):
        # v2: street level = the approved r3 idle loop, run at the run-start state (statics | beams | dyn), into
        # ../scratch/loop exactly like r3 (post_loop.py's layer composite is reused)
        job = base_job("loop", SB.OVERVIEW)
        job.pop("sb", None)
        job["loop"] = dict(mode=name[5:], groups=True)
        job["shots"] = [dict(name="O_overview", pose=SB.OVERVIEW.to_json(), t=2.0, protect=[])]
        job["renders"] = ["data"]
        job["fill"] = False
        job["fg_hide"] = ["fence"]     # the storyboard's sequence-wide occlusion set (sb_r), so no pop at the zoom
        return job
    elif name == "street_media":
        # v2: the loop's static media at the run start, every medium together (as r3 loop_media.py): no beams /
        # beams only, 1280 x 720 at 48 spp, plus the transmittance; into the loop folder
        job = base_job("loop", SB.OVERVIEW)
        job["sb"] = dict(mode="static", static=dict(name="S_street", pose=SB.OVERVIEW.to_json(), t=0.0, power=None,
                                                    extra=dict(fk=0.0, zoom=1.0, dis_all=1.0), res=[1280, 720],
                                                    vres=[1280, 720], vspp=48, bres=[1280, 720], bspp=48, tspp=32),
                         frames=[dict(name="S_street", pose=SB.OVERVIEW.to_json(), t=0.0)], passes=["vol"])
    elif name == "ov_closed2":
        # v2: the street with every route wall closed, as the loop's base (moving layers hidden), into the loop folder
        job = base_job("loop", SB.OVERVIEW)
        job["sb"] = dict(mode="static", static=dict(name="S_ovc", pose=SB.OVERVIEW.to_json(), t=0.0, power=None,
                                                    extra=dict(fk=0.0, zoom=1.0, dis_all=0.0), res=[1280, 720], spp=128),
                         frames=[dict(name="S_ovc", pose=SB.OVERVIEW.to_json(), t=0.0)], passes=["main"], dis_all=0.0)
    elif name == "t_dive":
        # v2 test frame a): mid-dive, walls closed (no route), the live city at mid LOD
        u = 0.5
        f = SB.fr(SB.T["dive"] + u * SB.DIVE_S)
        p = SB.dive_pose(u)
        ex = dict(u=u)
        job = base_job("bl_t", SB.OVERVIEW)
        job["sb"] = dict(mode="full", frames=[dict(name="t_dive", pose=p.to_json(), t=f / SB.FPS, fk=SB.fill_fk("dive", ex),
                                                   haze=SB.haze_at("dive", ex)[0], fkh=SB.haze_at("dive", ex)[1],
                                                   zoom=SB.zoom_at("dive", p), dis_all=0.0)],
                         res=[1280, 720], vres=[640, 360], spp=96, vspp=24, tspp=16)
    elif name == "ov_closed":
        # v2: the street OVERVIEW with every route wall closed (the reveal composites closed -> open per room)
        job = base_job("bl_ov", SB.OVERVIEW)
        job["sb"] = dict(mode="full", frames=[dict(name="S_ovc", pose=SB.OVERVIEW.to_json(), t=SB.T["b4"], fk=0.0, zoom=1.0,
                                                   dis_all=0.0)],
                         res=[1920, 1080], vres=[960, 540], spp=128, vspp=24, tspp=16, passes=["main", "sem"])
    elif name == "dive_board":
        fr = []
        for nm, u in (("dboard_a", 0.46), ("dboard_b", 0.82)):
            f = SB.fr(SB.T["dive"] + SB.DIVE_S * u)
            s, pose, ex = SB.cam_at(f)
            fr.append(dict(name=nm, frame=f, pose=pose.to_json(), t=f / SB.FPS, fk=SB.fill_fk(s, ex),
                           haze=SB.haze_at(s, ex)[0], fkh=SB.haze_at(s, ex)[1],
                           zoom=SB.zoom_at(s, pose), **({"dis": SB.wall_dis(f)} if s == "dive" else {})))
        job = base_job("bl_diveboard2", SB.OVERVIEW)
        job["sb"] = dict(mode="full", frames=fr, res=[1920, 1080], vres=[960, 540], spp=64, vspp=16, tspp=12)
    elif name in STATIC_POSE:
        fog = SB.OVERVIEW if name == "ov" else SB.DECISION
        job = base_job(("D:/rc_scratch/storyboard/bl_" + name) if name == "h2" else ("bl_" + name), fog)   # new passes on D: (C: low)
        fr = frames_of(name)
        # dyn (the moving streak lanes) at 8 fps; the frames between are interpolated in the post (long-exposure light
        # streaks blend cleanly); the beams hold still (beams_full), so no per-frame beam pass
        DYN_STEP = 2
        fr = [x for k, x in enumerate(fr) if k % DYN_STEP == 0 or k == len(fr) - 1]
        pw = power_for(name, {})
        job["sb"] = dict(mode="static", static=dict(name="S_" + name, pose=STATIC_POSE[name].to_json(), t=fr[0]["t"],
                                                    power=pw, res=[1920, 1080], spp=128, vres=[960, 540], vspp=24,
                                                    bres=[640, 360], bspp=24, tspp=16),
                         frames=fr, res=[1280, 720], dspp=24, bres=[640, 360], bspp=24,
                         passes=kv.get("passes", ["main", "vol", "layers", "dyn", "beams"]))
    elif name in ("zoom", "zoom_dcalm"):
        fog = SB.OVERVIEW if name == "zoom" else SB.DECISION
        job = base_job("D:/rc_scratch/storyboard/bl_zoom", fog)   # v3 re-render (walls open), on D:
        job["sb"] = dict(mode="full", frames=frames_of("zoom"), res=[1280, 720], vres=[640, 360], spp=48, vspp=16, tspp=12,
                         passes=["main", "sem", "vol", "trans"] if name == "zoom" else ["vol"],
                         vol_suffix="_vol" if name == "zoom" else "_vold")
    elif name in ("hin", "hmove"):
        job = base_job("bl_" + name, SB.DECISION)
        job["sb"] = dict(mode="full", frames=frames_of(name), res=[960, 540], vres=[400, 225], spp=16, vspp=10, tspp=6)
    else:
        raise SystemExit("unknown job " + name)
    job["sb"].update(job.pop("_protect"))
    if name not in ("test", "hq", "dive", "dive_board", "dive_vol", "t_dive", "hq_static"):
        job["fill"] = False      # the route views never see the fill (cityfill rules 5a/5c): a lighter scene
    if name not in ("test", "hq", "dive", "dive_board", "dive_vol", "t_dive", "ov_closed", "hq_static", "ov_closed2"):
        job["sb"]["dis_all"] = 1.0        # the route views: every wall has dissolved
    for k, v in kv.items():
        if k in ("f0", "f1", "passes"):
            continue
        if k.startswith("sb."):
            job["sb"][k[3:]] = v
        else:
            job[k] = v
    return job


if __name__ == "__main__":
    name = sys.argv[1]
    kv = {}
    for a in sys.argv[2:]:
        k, _, v = a.partition("=")
        try:
            kv[k] = json.loads(v)
        except ValueError:
            kv[k] = v
    job = make(name, kv)
    sys.exit(run(job, name + ("_m" if name in ("hq", "dive", "dive_board", "dive_vol") else "")))
