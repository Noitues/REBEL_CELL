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
LOOK = dict(unit_scale=3.0, neon=1.0, win=0.9, panel=4.0, cityglow=300.0, room=60.0, beam=6.0e5, beams=4, fog_peak=0.008,
            haze=0.0008, step_rate=4.0, lamp=80.0, wash=1500.0)   # calibrated on the one-city tests (median luma 0.22)


def derive():
    p = os.path.join(SCR, "oc_derive.json")
    if os.path.exists(p):
        return json.load(open(p))
    d = OC.derive()
    out = dict(street=dict(a=d["a"], c=d["c"]), nrm=d["nrm"], start_left=d["start_left"], span=d["span"],
               columns=d["columns"], route_keys=d["route_keys"], rooms=d["rooms"], overview=d["overview"],
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
    b = dict(mode=mode, route_keys=D["route_keys"], rooms=D["rooms"], street=D["street"], look=LOOK, nrm=D["nrm"])
    b.update(kw)
    return b


if __name__ == "__main__":
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
