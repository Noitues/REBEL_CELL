"""Look-bias sign check (tools spec 6.2; DERIVE_V2_REVIEW.md Q2.1.4 / AD resolution 8).

python look_bias_check.py poses     writes the two DECISION poses (bias = +sgn*0.10 and -sgn*0.10) and the Eevee job
python look_bias_check.py measure   projects the current room with each pose, prints the offset from the usable-area
                                    centre and writes the side-by-side JPEG (needs the two Eevee stills)
The street_r2 scene is rendered by r2_scene.py in its mainline Eevee mode (no GPU lock): Blender is run from the shell.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RMG = os.path.normpath(os.path.join(HERE, "..", "..", "route_map_graph"))
S2 = os.path.join(RMG, "street_r2", "scripts")
sys.path.insert(0, S2)
sys.dont_write_bytecode = True
import r2_rules as RR  # noqa: E402
import r2_jobs as JOBS  # noqa: E402

OUT = "D:/rc_scratch/idpass/lookbias"
LB = 0.10


def poses():
    OC = RR._oc("v3")
    D = RR.derive_v3()
    sgn = 1.0 if D["start_left"] else -1.0
    y0 = OC.street_yaw(D["nrm"])
    cur = [OC.G.WALK_START[-1]]
    opts = OC.G.states(OC.G.WALK_START)[1]
    rooms = D["rooms"]
    dpts = [tuple(p) for i in cur + opts for p in rooms[i]["front"] + rooms[i]["back"]]
    res = {}
    for name, b in (("plus", sgn * LB), ("minus", -sgn * LB)):
        res[name] = OC.frame(dpts, y0 - sgn * 24.0, 9.0, 30.0, 0.66, 0.70, bias=b)
    return OC, D, sgn, cur[0], rooms, res


def current_px(OC, cam, room):
    q = [OC.proj(cam, tuple(p)) for p in room["front"] + room["back"]]
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    return min(xs), max(xs), min(ys), max(ys)


def main_poses():
    OC, D, sgn, cur, rooms, res = poses()
    cached = D["decision"]["persp"]["loc"]
    print("sgn", sgn, "start_left", D["start_left"], "current", cur)
    print("cached decision loc", [round(v, 3) for v in cached])
    for k, c in res.items():
        print(k, "loc", [round(v, 3) for v in c["persp"]["loc"]], "shift", round(c["persp"]["sx"], 4), round(c["persp"]["sy"], 4))
    own = res["plus"]["persp"]["loc"]
    assert all(abs(a - b) < 1e-3 for a, b in zip(own, cached)), "the +sgn pose does not reproduce the cached derive_v3 decision"
    frames = []
    for k, c in res.items():
        p = dict(c["persp"])
        p["tgt"] = c["target"]
        frames.append(dict(name="LB_" + k, persp=p, res=[960, 540], samples=16, zcut=JOBS.FG["zcut_street"], dis={}))
    os.makedirs(OUT, exist_ok=True)
    cams = [dict(tag=f["name"], persp=f["persp"], res=f["res"], samples=f["samples"], zcut=f["zcut"], dis={}) for f in frames]
    job = JOBS.job_block(1, frames, 16)
    job["mode"] = "eevee"
    json.dump(cams, open(os.path.join(OUT, "cams.json"), "w"))
    json.dump(job, open(os.path.join(OUT, "job.json"), "w"))
    json.dump(dict(sgn=sgn, current=cur), open(os.path.join(OUT, "meta.json"), "w"))
    print("wrote", OUT)


def main_measure():
    from PIL import Image, ImageDraw
    OC, D, sgn, cur, rooms, res = poses()
    ucx = (OC.USE[0] + OC.USE[2]) / 2
    rows = {}
    ims = []
    for k in ("plus", "minus"):
        x0, x1, y0, y1 = current_px(OC, res[k], rooms[cur])
        cx = (x0 + x1) / 2
        rows[k] = dict(bias=(sgn if k == "plus" else -sgn) * LB, room_x0=round(x0, 1), room_x1=round(x1, 1), room_cx=round(cx, 1),
                       usable_cx=ucx, offset_px=round(cx - ucx, 1), offset_frac_of_usable=round((cx - ucx) / (OC.USE[2] - OC.USE[0]), 4))
        im = Image.open(os.path.join(OUT, "LB_%s_beauty_night.png" % k)).convert("RGB")
        s = im.size[0] / 1920.0
        d = ImageDraw.Draw(im)
        d.rectangle([OC.USE[0] * s, OC.USE[1] * s, OC.USE[2] * s, OC.USE[3] * s], outline=(255, 255, 0), width=1)
        d.line([ucx * s, 0, ucx * s, im.size[1]], fill=(255, 255, 0), width=1)
        d.rectangle([x0 * s, y0 * s, x1 * s, y1 * s], outline=(255, 40, 40), width=2)
        d.line([cx * s, y0 * s, cx * s, y1 * s], fill=(255, 40, 40), width=1)
        ims.append((k, im))
    W, H = ims[0][1].size
    sheet = Image.new("RGB", (W * 2 + 6, H + 22), (20, 20, 20))
    dd = ImageDraw.Draw(sheet)
    for i, (k, im) in enumerate(ims):
        sheet.paste(im, (i * (W + 6), 22))
        r = rows[k]
        dd.text((i * (W + 6) + 4, 4), "%s (bias %+.2f, sgn %+.0f): current room centre x %.0f of 1920, usable centre %.0f, off by %+.0f px" % (
            "DERIVE sign +sgn*0.10" if k == "plus" else "RIG sign -sgn*0.10", r["bias"], sgn, r["room_cx"], ucx, r["offset_px"]), fill=(255, 255, 255))
    out = os.path.normpath(os.path.join(HERE, "..", "look_bias_check.jpg"))
    sheet.save(out, quality=88)
    best = min(rows, key=lambda k: abs(rows[k]["offset_px"]))
    print(json.dumps(rows, indent=1))
    print("nearer the usable centre:", best, "(+sgn = derive sign)" if best == "plus" else "(-sgn = rig sign)")
    json.dump(dict(sgn=sgn, rows=rows, nearer=best), open(os.path.join(OUT, "result.json"), "w"), indent=1)


if __name__ == "__main__":
    {"poses": main_poses, "measure": main_measure}[sys.argv[1]]()
