"""Storyboard v3 proof (one continuous city): the camera path and the render jobs (headless Blender, one scene).

python sb_ocjobs.py derive                write ../scratch/oc_derive.json (the street, rooms, poses) and print it
python sb_ocjobs.py m_hq | m_dive         the mainline look (Eevee + the kit's passes) -> D:/rc_scratch/storyboard/oc_m
python sb_ocjobs.py c_dive [step]         the AAA-2 look (Cycles), the dive frames inside the look band and after
python sb_ocjobs.py c_test <u>            one Cycles test frame at dive fraction u
python sb_ocjobs.py c_boards              the 1920 street board (walls closed) + the rooms-revealed preview
python sb_ocjobs.py m_boards              the 1920 mainline mid-dive board
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
import cam_rig as R  # noqa: E402
import look_preset as LP  # noqa: E402
import sb_cams as SB  # noqa: E402
import sb_mainline as ML  # noqa: E402
import sb_onecity as OC  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
OUTM = "D:/rc_scratch/storyboard/oc_m"
OUTC = "D:/rc_scratch/storyboard/oc_c"
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
FPS = 24
T0 = 4.4                              # the proof starts on the hovered Site (beat 2), then select, jack in, dive
T_DIVE, DIVE_S = SB.T["dive"], 3.0
T_END = T_DIVE + DIVE_S + 0.5         # the REVEAL start, held 0.5 s
HQ_LENS = 300.0
LOOK = dict(unit_scale=3.0, neon=1.0, win=0.9, panel=4.0, cityglow=900.0, room=60.0, beams=6, beam_rise=1.35, lane_dim=0.5, lane_k=2.5,
            # v3-r3 (art director): beams = an emissive shaft (radial core + soft skirt, gone by 60 % of its length) and
            # one wide soft haze spot; fog 1.3x the v3a field plus coloured mid and ground banks; street-level glows
            beam=6.0e5, beam_cone=30.0, beam_emit=3.0, beam_half=6.0, beam_len=3.5, beam_fade=0.6, beam_efold=0.22,
            beam_core_s=0.13, beam_soft_s=0.42, beam_core_w=1.0, beam_soft_w=0.5, beam_hot=0.5,
            fog_peak=0.0507, wisp_k=1.2, fog_front=7.0, underlight_k=0.07, haze=0.0008, haze_efold=40.0,
            mid_bank=0.035, mid_glow=0.3, gb_top=2.2, ground_bank=0.04, ground_glow=0.05,
            ground_lamp=20.0, ground_glow_step=9.0, ground_glow_depth=60.0, ground_glow_p=0.55,
            step_rate=4.0, lamp=80.0, wash=1500.0)   # calibrated on the one-city tests (median luma 0.22)


def derive():
    p = os.path.join(SCR, "oc_derive.json")
    if os.path.exists(p):
        return json.load(open(p))
    d = OC.derive()
    out = dict(street=dict(a=d["a"], c=d["c"]), nrm=d["nrm"], start_left=d["start_left"], span=d["span"],
               columns=d["columns"], route_keys=d["route_keys"], rooms=d["rooms"], edges=d["edges"], col_info=d["col_info"], overview=d["overview"],
               decision=d["decision"], frontage=d["frontage"])
    os.makedirs(SCR, exist_ok=True)
    json.dump(out, open(p, "w"), indent=1)
    return out


def smoother(t):
    t = max(0.0, min(1.0, t))
    return t * t * t * (t * (6 * t - 15) + 10)


def hq_cam():
    t, o = ML.hq_cam()
    return dict(target=list(t), yaw=135.0, pitch=40.0, w=o)


def pose_at(u, D=None):
    """The ONE camera path (layout36 frame): the HQ pose (orthographic, emulated by a 300 mm lens so the start does not
    jump) down to the street OVERVIEW solved on the derived rooms. Target, yaw and shift on smootherstep, the frame width
    and the lens in log space, the pitch lagging (u^1.6) so the camera keeps looking down as it drops, then levels out."""
    D = D or derive()
    h, ov = hq_cam(), D["overview"]
    w1 = ov["dist"] * 36.0 / ov["persp"]["lens"]
    s = smoother(u)
    sp = smoother(min(1.0, u * 1.08) ** 1.6)
    y1 = ov["yaw"]
    while y1 - h["yaw"] > 180:
        y1 -= 360
    while y1 - h["yaw"] < -180:
        y1 += 360
    tg = [R.lerp(a, b, s) for a, b in zip(h["target"], ov["target"])]
    yaw = R.lerp(h["yaw"], y1, s)
    pit = R.lerp(h["pitch"], ov["pitch"], sp)
    w = math.exp(R.lerp(math.log(h["w"]), math.log(w1), s))
    lens = math.exp(R.lerp(math.log(HQ_LENS), math.log(ov["persp"]["lens"]), s))
    c = OC.cam(tg, yaw, pit, w * lens / 36.0, lens, R.lerp(0.0, ov["persp"]["sx"], s), R.lerp(0.0, ov["persp"]["sy"], s))
    c["persp"]["tgt"] = tg
    return c


def zoom_of(c, D=None):
    D = D or derive()
    ov = D["overview"]
    s = ov["target"]

    def dist(p):
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p, s)))
    d0, d1 = dist(pose_at(0.0, D)["persp"]["loc"]), dist(ov["persp"]["loc"])
    return max(0.0, min(1.0, math.log(d0 / max(dist(c["persp"]["loc"]), 1e-3)) / math.log(d0 / d1)))


def look_w(z):
    a, b = LP.PRESET["lod_bands"]["look_blend_by_zoom"]
    u = max(0.0, min(1.0, (z - a) / (b - a)))
    return u * u * (3 - 2 * u)


def zcut(z):
    zf, zn, a, b = LP.PRESET["lod_bands"]["section_by_zoom"]
    u = max(0.0, min(1.0, (z - a) / (b - a)))
    u = u * u * (3 - 2 * u)
    return math.exp(math.log(zf) + (math.log(zn) - math.log(zf)) * u) if u > 0 else 1.0e4


def frames():
    """[(f, t, segment, u)] of the proof video (f counts from T0)."""
    out = []
    n = int(round((T_END - T0) * FPS))
    for k in range(n):
        t = T0 + k / FPS
        if t < T_DIVE:
            out.append((k, t, "hq", 0.0))
        else:
            out.append((k, t, "dive", min(1.0, (t - T_DIVE) / DIVE_S)))
    return out


def run(out, cams, oc, tag):
    os.makedirs(out, exist_ok=True)
    cf = os.path.join(SCR, "oc_cams_%s.json" % tag)
    of = os.path.join(SCR, "oc_job_%s.json" % tag)
    json.dump(cams, open(cf, "w"))
    json.dump(oc, open(of, "w"))
    log = os.path.join(SCR, "oc_%s.log" % tag)
    t0 = time.time()
    env = dict(os.environ, NET36="net_scope.json")
    with open(log, "w") as f:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "m44", "onecity_scene.py"), "--",
                            "meridian_hq", out, cf, of], stdout=f, stderr=subprocess.STDOUT, env=env)
    print(tag, "exit", r.returncode, "wall %.0f s" % (time.time() - t0), "log", log, flush=True)


def oc_block(mode, D, **kw):
    b = dict(mode=mode, route_keys=D["route_keys"], rooms=D["rooms"], street=D["street"], look=LOOK, nrm=D["nrm"],
             layout_path=OC.LAYPATH, edges=D["edges"], col_info=D["col_info"], hero_sign_rule=OC.LAYOUT_RULES["hero_sign_rule"],
             plinth_off=OC.LAYOUT_RULES["border_street_width"] / 2 + 0.2)
    b.update(kw)
    return b


if __name__ == "__main__" and sys.argv[1] not in ("fc_dive", "fc_street", "fc_dyn", "fc_move", "fm_dive", "fc_test_end", "fc_t3"):
    w = sys.argv[1]
    D = derive()
    if w == "derive":
        print(json.dumps({k: v for k, v in D.items() if k != "rooms"}, indent=1)[:3000])
        for f, t, s, u in frames()[::12]:
            if s == "dive":
                c = pose_at(u, D)
                z = zoom_of(c, D)
                print("f %d t %.2f u %.2f zoom %.2f look %.2f yaw %.1f pitch %.1f lens %.0f" % (f, t, u, z, look_w(z), c["yaw"], c["pitch"], c["persp"]["lens"]))
    elif w == "m_hq":
        h = hq_cam()
        run(OUTM, [dict(tag="m_hq", t=list(ML.L.lots(h["target"][0], h["target"][1])), ortho=h["w"], res=[1920, 1080], samples=16)],
            oc_block("mainline", D), "m_hq")
    elif w == "m_dive":
        cams = []
        for f, t, s, u in frames():
            if s != "dive":
                continue
            c = pose_at(u, D)
            if look_w(zoom_of(c, D)) >= 0.999:
                continue
            cams.append(dict(tag="m_%04d" % f, persp=dict(loc=c["persp"]["loc"], tgt=c["persp"]["tgt"], lens=c["persp"]["lens"],
                                                          sx=c["persp"]["sx"], sy=c["persp"]["sy"]), res=[1280, 720], samples=12,
                             zcut=zcut(zoom_of(c, D))))
        print("mainline dive frames", len(cams))
        run(OUTM, cams, oc_block("mainline", D), "m_dive")
    elif w in ("c_dive", "c_test"):
        fr = []
        if w == "c_test":
            us = [float(x) for x in sys.argv[2:] if "=" not in x] or [0.5, 1.0]
            for x in sys.argv[2:]:
                if "=" in x:
                    k_, v_ = x.split("=")
                    LOOK[k_] = float(v_)
            res = [int(LOOK.pop("res_w", 960)), int(LOOK.pop("res_w2", 0)) or 540]
            res = [res[0], res[0] * 9 // 16]
            for u in us:
                c = pose_at(u, D)
                fr.append(dict(name="t_%03d" % int(u * 100), persp=dict(c["persp"]), res=res, zcut=zcut(zoom_of(c, D))))
            run(OUTC, [], oc_block("cycles", D, frames=fr, spp=int(LOOK.pop("spp", 24))), "c_test")
        else:
            step = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            last = None
            for f, t, s, u in frames():
                if s != "dive":
                    continue
                c = pose_at(u, D)
                if look_w(zoom_of(c, D)) <= 0.001:
                    continue
                key = round(u, 4)
                if key == last:
                    continue
                last = key
                if f % step and u < 1.0:
                    continue
                fr.append(dict(name="c_%04d" % f, persp=dict(c["persp"]), res=[1280, 720], zcut=zcut(zoom_of(c, D))))
            print("cycles dive frames", len(fr))
            run(OUTC, [], oc_block("cycles", D, frames=fr, spp=32), "c_dive")
    elif w == "c_boards":
        c = pose_at(1.0, D)
        allopen = {i: 1.0 for i in D["rooms"]}
        fr = [dict(name="b_street", persp=dict(c["persp"]), res=[1920, 1080], zcut=zcut(1.0)),
              dict(name="b_rooms", persp=dict(c["persp"]), res=[1920, 1080], dis=allopen, zcut=zcut(1.0))]
        run(OUTC, [], oc_block("cycles", D, frames=fr, spp=64), "c_boards")


# ================================================================ v3 FULL SEQUENCE on the one-city street (SB.T timeline)
def mix(a, b, k):
    """Pose mix (cam_rig convention): target, yaw, pitch, lens, shift linear; distance in log space."""
    tg = [R.lerp(x, y, k) for x, y in zip(a["target"], b["target"])]
    d = math.exp(R.lerp(math.log(a["dist"]), math.log(b["dist"]), k))
    c = OC.cam(tg, R.lerp(a["yaw"], b["yaw"], k), R.lerp(a["pitch"], b["pitch"], k), d,
               R.lerp(a["persp"]["lens"], b["persp"]["lens"], k), R.lerp(a["persp"]["sx"], b["persp"]["sx"], k),
               R.lerp(a["persp"]["sy"], b["persp"]["sy"], k))
    c["persp"]["tgt"] = tg
    return c


def hover_pose(D, room):
    """The v3_dynamic hover ease on the one-city rig: F 22 % to the room, yaw 3 deg toward it, distance x 0.96."""
    dec = D["decision"]
    r = D["rooms"][room]
    rc = [sum(p[i] for p in r["front"] + r["back"]) / 8.0 for i in range(3)]
    F = [R.lerp(a, b, 0.22) for a, b in zip(dec["target"], rc)]
    px = OC.proj(dec, rc)[0]
    s = 1.0 if px > OC.W_ / 2 else -1.0
    c = OC.cam(F, dec["yaw"] - 3.0 * s, dec["pitch"], dec["dist"] * 0.96, dec["persp"]["lens"], dec["persp"]["sx"], dec["persp"]["sy"])
    c["persp"]["tgt"] = F
    return c


def full_at(f, D=None):
    """(segment, pose, extra) for global video frame f (the SB.T timeline, 24 fps)."""
    D = D or derive()
    T = SB.T
    t = f / FPS
    ov, dec = D["overview"], D["decision"]
    for c in (ov, dec):
        c["persp"].setdefault("tgt", c["target"])
    if t < T["dive"]:
        return "hq", None, {}
    if t < T["b4"]:
        u = min(1.0, (t - T["dive"]) / DIVE_S)
        return "dive", pose_at(u, D), dict(u=u)
    if t < T["b5"]:
        return "ov", ov, {}
    if t < T["b5"] + SB.ZOOM_S:
        u = R.ease((t - T["b5"]) / SB.ZOOM_S)
        return "zoom", mix(ov, dec, u), dict(u=u)
    h1, h2 = hover_pose(D, SB.OPT1), hover_pose(D, SB.OPT2)
    if t < T["hover1"]:
        return "dec", dec, {}
    if t < T["hover1"] + SB.HOVER_IN:
        k = R.ease_out((t - T["hover1"]) / SB.HOVER_IN)
        return "hin", mix(dec, h1, k), dict(k=k)
    if t < T["hover2"]:
        return "h1", h1, {}
    if t < T["hover2"] + SB.HOVER_MOVE:
        k = R.ease((t - T["hover2"]) / SB.HOVER_MOVE)
        return "hmove", mix(h1, h2, k), dict(k=k)
    return "h2", h2, {}


HOLDS = ("ov", "dec", "h1", "h2")
OPEN_ALL = None


def _fr(name, c, t, res, **kw):
    d = dict(name=name, persp=dict(c["persp"]), t=t, res=res, zcut=zcut(1.0 if c is not None else 0.0))
    d.update(kw)
    return d


def full_jobs(kind, D):
    allopen = {i: 1.0 for i in D["rooms"]}
    for c in (D["overview"], D["decision"]):
        c["persp"].setdefault("tgt", c["target"])
    fr = []
    if kind == "fc_dive":
        last = None
        for f in range(SB.NF):
            s, c, ex = full_at(f, D)
            if s != "dive":
                continue
            z = zoom_of(c, D)
            if look_w(z) <= 0.001:
                continue
            fr.append(dict(name="g_%04d" % f, persp=dict(c["persp"]), t=f / FPS, res=[1280, 720], zcut=zcut(z)))
    elif kind == "fc_street":
        ov = D["overview"]
        t = SB.T["b4"]
        fr += [_fr("S_ov_closed", ov, t, [1280, 720], lanes=False), _fr("S_ov_open", ov, t, [1280, 720], lanes=False, dis=allopen),
               _fr("B_ov_closed", ov, t, [1920, 1080]), _fr("B_ov_open", ov, t, [1920, 1080], dis=allopen)]
        for seg in ("dec", "h1", "h2"):
            f0 = next(f for f in range(SB.NF) if full_at(f, D)[0] == seg)
            s, c, ex = full_at(f0, D)
            fr.append(_fr("S_%s" % seg, c, f0 / FPS, [1280, 720], lanes=False, dis=allopen))
    elif kind == "fc_dyn":
        # the moving lanes at 8 fps on every held shot (emission-only; blended between in the composite)
        for seg in HOLDS:
            fs = [f for f in range(SB.NF) if full_at(f, D)[0] == seg]
            for k, f in enumerate(fs):
                if k % 3 and f != fs[-1]:
                    continue
                s, c, ex = full_at(f, D)
                fr.append(_fr("Y_%04d" % f, c, f / FPS, [1280, 720], dyn=True, dis=allopen if seg != "ov" else {}))
    elif kind == "fc_move":
        # zoom and the two hover moves: every frame, walls open
        for f in range(SB.NF):
            s, c, ex = full_at(f, D)
            if s in ("zoom", "hin", "hmove"):
                fr.append(_fr("g_%04d" % f, c, f / FPS, [1280, 720], dis=allopen))
    return fr


if __name__ == "__main__" and sys.argv[1] in ("fc_dive", "fc_street", "fc_dyn", "fc_move", "fm_dive", "fc_test_end", "fc_t3"):
    D = derive()
    w = sys.argv[1]
    if w == "fm_dive":
        cams = []
        for f in range(SB.NF):
            s, c, ex = full_at(f, D)
            if s != "dive" or look_w(zoom_of(c, D)) >= 0.999:
                continue
            cams.append(dict(tag="m_g_%04d" % f, persp=dict(loc=c["persp"]["loc"], tgt=c["persp"]["tgt"], lens=c["persp"]["lens"],
                                                            sx=c["persp"]["sx"], sy=c["persp"]["sy"]), res=[1280, 720], samples=12,
                             zcut=zcut(zoom_of(c, D))))
        run(OUTM, cams, oc_block("mainline", D), "fm_dive")
    elif w == "fc_t3":
        # v3-r3 calibration: the street OVERVIEW (walls closed) and the dive frame of the review (f 300), 960 px
        for x in sys.argv[2:]:
            k_, v_ = x.split("=")
            LOOK[k_] = float(v_)
        ov = D["overview"]
        ov["persp"].setdefault("tgt", ov["target"])
        s3, c3, ex3 = full_at(300, D)
        fr = [_fr("T3_ov", ov, SB.T["b4"], [960, 540]), dict(name="T3_0300", persp=dict(c3["persp"]), t=300 / FPS, res=[960, 540],
                                                             zcut=zcut(zoom_of(c3, D)))]
        run(OUTC, [], oc_block("cycles", D, frames=fr, spp=24), "fc_t3")
    elif w == "fc_test_end":
        ov = D["overview"]
        ov["persp"].setdefault("tgt", ov["target"])
        fr = [_fr("E_closed", ov, SB.T["b4"], [1920, 1080]), _fr("E_open", ov, SB.T["b4"], [1920, 1080], dis={i: 1.0 for i in D["rooms"]})]
        run(OUTC, [], oc_block("cycles", D, frames=fr, spp=48), "fc_test_end")
    else:
        fr = full_jobs(w, D)
        tag = w
        if len(sys.argv) > 3:            # v3-r3: a frame range [f0, f1) so a long job fits one GPU lock block
            f0, f1 = int(sys.argv[2]), int(sys.argv[3])
            fr = [x for x in fr if not x["name"][2:6].isdigit() or f0 <= int(x["name"][2:6]) < f1]
            tag = "%s_%d" % (w, f0)
        print(w, "frames", len(fr), flush=True)
        mark = os.path.join(SCR, "r3_done_%s" % tag)      # v3-r3: a batch already rendered with the current LOOK is skipped
        if os.path.exists(mark):
            print("skip", tag, "(already rendered)", flush=True)
            sys.exit(0)
        run(OUTC, [], oc_block("cycles", D, frames=fr, spp=32 if w != "fc_dyn" else 24), tag)
        open(mark, "w").write(json.dumps(LOOK))
