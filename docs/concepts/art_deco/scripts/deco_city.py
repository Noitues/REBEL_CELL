"""Art-deco restyle of the whole-city panel (A2 city, hero camera). Imported by deco_blender_city.py inside Blender.

wrap_prism    records every tall prism (the building bodies) while city_build.py builds the city
patch_src     inserts apply_city() in front of the render in city_render.py and softens a few base numbers first
apply_city    lacquer + gold facades, setback crowns on the tallest towers in frame, deco ornament on each landmark
              (stepped gold plinth, ground sunburst, fan crown, spire, fan searchlights), charcoal fog
"""
import json
import math
import os
import random

import bpy
from mathutils import Vector

import deco_restyle as D

CFG = json.loads(os.environ.get("DECO_CFG", "{}"))
REC = []


def wrap_prism(orig):
    def prism(acc, pts, z0, z1, col, *a, **kw):
        try:
            if z1 - z0 > 14.0 and len(pts) >= 3:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                REC.append(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2,
                            float(z0), float(z1)))
        except Exception:  # noqa: BLE001
            pass
        return orig(acc, pts, z0, z1, col, *a, **kw)
    return prism


def patch_src(fname, src):
    if fname == "city_render.py":
        key = 'stem = os.path.join(OUTDIR, "%s_%s" % (CAMK, MODE))'
        assert key in src
        src = src.replace(key, "import deco_city as _DCC\n_DCC.apply_city(globals())\n" + key, 1)
        # fog colour: neutral warm charcoal (the volume scatter colour in mat_fog)
        k2 = 'vs.inputs["Color"].default_value = (0.85, 0.80, 1.0, 1)'
        assert k2 in src
        c = CFG.get("fog_col", (0.62, 0.56, 0.50))
        src = src.replace(k2, 'vs.inputs["Color"].default_value = (%f, %f, %f, 1)' % tuple(c), 1)
    return src


def _prep_preset():
    import city_preset as CP
    A = CP.AAA
    for k, v in CFG.get("aaa", {}).items():
        A[k] = v
    return CP


def _towers(g, n, min_top, avoid, min_half=2.0):
    from bpy_extras.object_utils import world_to_camera_view
    sc, cam = g["scene"], g["cam"]
    bpy.context.view_layer.update()
    best = {}
    for (cx, cy, hx, hy, z0, z1) in REC:
        k = (round(cx / 3.0), round(cy / 3.0))
        if k not in best or z1 > best[k][5]:
            best[k] = (cx, cy, hx, hy, z0, z1)
    out = []
    for k, (cx, cy, hx, hy, z0, z1) in sorted(best.items()):
        if z1 < min_top or hx < min_half or hy < min_half or hx > 30 or hy > 30:
            continue
        if any(math.hypot(cx - ax, cy - ay) < ar for ax, ay, ar in avoid):
            continue
        p = world_to_camera_view(sc, cam, Vector((cx, cy, z1)))
        if not (0.01 < p.x < 0.99 and 0.01 < p.y < 0.99 and p.z > 0):
            continue
        out.append((-(z1), cx, cy, hx, hy, z1))
    out.sort()
    return [(cx, cy, hx, hy, z1) for (_, cx, cy, hx, hy, z1) in out[:n]]


def apply_city(g):
    CP = g["CP"]
    sc = g["scene"]
    MS, OBJ, LM = g["MS"], g["OBJ"], g["LM"]
    rng = random.Random(CFG.get("seed", 20261020))
    M = D.Mats()
    coll = bpy.data.collections.new("deco")
    sc.collection.children.link(coll)
    nk = CFG.get("neon_k", 12.0)
    ctx = dict(mats=M, coll=coll)
    ctx["lac"] = D.DAcc("deco_lacquer", M.lacquer, coll)
    ctx["gold"] = D.DAcc("deco_gold", M.gold, coll)
    ctx["neon"] = D.DAcc("deco_neon", M.neon((0.55, 0.45, 0.95), nk), coll)       # replaced per landmark below
    ctx["neon2"] = D.DAcc("deco_neon2", M.neon((1.0, 0.55, 0.12), nk), coll)
    # 1. facades: black lacquer, gold bands every 8 floors (the grid fades with distance), windows pulled toward gold
    for k in ("surf", "smooth"):
        m = MS.get(k)
        if m is not None and not m.get("deco_done"):
            D.lacquer_facade(m, dark=CFG.get("dark", 0.22), window_tint=tuple(CFG.get("win_tint", (1.0, 0.82, 0.55))),
                             fade0=CFG.get("fade0", 400.0), fade1=CFG.get("fade1", 900.0), band_w=CFG.get("band_w", 0.05))
            m["deco_done"] = 1
    if OBJ.get("bill") is not None:
        OBJ["bill"].hide_render = True            # signs-as-light off: the deco light is lines
    # 2. landmarks
    avoid = []
    hues = {"halcyon": ((0.43, 0.16, 1.0), (1.0, 0.40, 0.03)), "meridian": ((1.0, 0.26, 0.01), (1.0, 0.03, 0.02)),
            "orbital": ((0.61, 0.87, 1.0), (1.0, 0.45, 0.06)), "solace": ((0.30, 1.0, 0.06), (1.0, 0.05, 0.30)),
            "aurelian": ((1.0, 0.70, 0.20), (1.0, 0.30, 0.10)), "tethys": ((0.10, 0.80, 1.0), (0.1, 1.0, 0.8)),
            "rebel_cell": ((0.8, 1.0, 0.0), (1.0, 0.1, 0.1))}
    terr_h = g.get("terr_h", lambda x, y: 0.0)
    fp = CP.LANDMARK_FP
    gold = ctx["gold"]
    lac = ctx["lac"]
    extra = []
    for corp, v in sorted(LM.items()):
        lab, crown, hue = v
        if corp == "rebel_cell":
            continue
        h1, h2 = hues.get(corp, ((1, 0.6, 0.2), (1, 0.3, 0.1)))
        bx, by = lab[0], lab[1]
        z0 = terr_h(bx, by)
        avoid.append((bx, by, 60.0))
        neon = D.DAcc("deco_neon_" + corp, M.neon(h1, nk), coll)
        neon2 = D.DAcc("deco_neon2_" + corp, M.neon(h2, nk * 0.8), coll)
        fpi = fp.get(corp, ("circ", 30.0))
        r = fpi[1] * CFG.get("plinth_k", 1.35)
        # stepped gold plinth: three concentric rings with two parallel neon lines between
        n = 64
        for i, (dr, hh) in enumerate(((0.0, 2.0), (2.6, 1.4), (5.2, 0.8))):
            for j in range(n):
                a0, a1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
                r0, r1 = r + dr, r + dr + 1.6
                quad = [(bx + r0 * math.cos(a0), by + r0 * math.sin(a0)), (bx + r1 * math.cos(a0), by + r1 * math.sin(a0)),
                        (bx + r1 * math.cos(a1), by + r1 * math.sin(a1)), (bx + r0 * math.cos(a1), by + r0 * math.sin(a1))]
                gold.prism(quad, (0, 0, z0 + 0.1), (1, 0, 0), (0, 1, 0), (0, 0, 1), hh + 0.2)
        for dr in (1.4, 2.0, 3.6, 4.2):
            for j in range(n):
                a0, a1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
                neon.bar((bx + (r + dr) * math.cos(a0), by + (r + dr) * math.sin(a0), z0 + 1.4),
                         (bx + (r + dr) * math.cos(a1), by + (r + dr) * math.sin(a1), z0 + 1.4), 0.7, 0.5)
        # ground sunburst: 48 ray pairs from the plinth outward
        for k in range(CFG.get("rays", 48)):
            a = 2 * math.pi * k / CFG.get("rays", 48)
            c, s = math.cos(a), math.sin(a)
            r0 = r + 7.0
            r1 = r0 + (38.0 if k % 2 == 0 else 22.0) * CFG.get("ray_k", 1.0)
            for off in (-1.1, 1.1):
                neon.bar((bx + c * r0 - s * off, by + s * r0 + c * off, z0 + 0.35), (bx + c * r1 - s * off, by + s * r1 + c * off, z0 + 0.35), 0.7, 0.5)
        # crown: crossed open fans + spire on top of the landmark
        if crown is not None:
            cz = crown[2]
            R = CFG.get("fan_r", 48.0)
            for ax in ("x", "y"):
                D.fan_crown(gold, lac, neon2, crown[0], crown[1], cz - R * 0.35, ax, R, rng, nray=13, t=0.8, backing=False)
            D.spire(gold, neon, crown[0], crown[1], cz + R * 0.65, 95.0, 3.2)
        extra.append((corp, neon, neon2))
        # base uplight on the landmark: warm gold, from the plinth ring toward the crown (a flood from below)
        if crown is not None:
            for k in range(4):
                a = math.pi / 4 + k * math.pi / 2
                loc = (bx + (r + 9.0) * math.cos(a), by + (r + 9.0) * math.sin(a), z0 + 1.5)
                g["light"]("deco_up_%s_%d" % (corp, k), "SPOT", loc, CFG.get("up_w", 2.0e6), (1.0, 0.66, 0.30),
                           rot=g["aim"](loc, (bx, by, crown[2] * 0.7)), spot=CFG.get("up_cone", 38.0), blend=0.6, shadow=False)
    # 3. towers: stepped crowns, piers, parallel neon in the district's corp hue, fans on the tallest few
    zs = sorted(r[5] - r[4] for r in REC)
    zt = sorted(r[5] for r in REC)
    print("[deco] REC height p50/p90/p99/max", zs[len(zs)//2], zs[int(len(zs)*0.9)], zs[int(len(zs)*0.99)], zs[-1], "top p50/p90/max", zt[len(zt)//2], zt[int(len(zt)*0.9)], zt[-1], flush=True)
    towers = _towers(g, CFG.get("n_towers", 160), CFG.get("min_top", 38.0), avoid, CFG.get("min_half", 2.0))
    nfan = CFG.get("n_fans", 14)
    lacq, goldq = ctx["lac"], ctx["gold"]
    nq = {}
    for k, (cx, cy, hx, hy, z1) in enumerate(towers):
        rr = random.Random(7000 + k)
        # the corp hue by the nearest landmark
        best, bd = None, 1e18
        for corp, v in LM.items():
            d = math.hypot(cx - v[0][0], cy - v[0][1])
            if d < bd and corp != "rebel_cell":
                best, bd = corp, d
        h1 = hues.get(best, ((1, 0.6, 0.2), None))[0] if best else (1, 0.6, 0.2)
        key = tuple(round(x, 2) for x in h1)
        if key not in nq:
            nq[key] = D.DAcc("deco_tw_neon_%d" % len(nq), M.neon(h1, nk), coll)
        t_ctx = dict(lac=lacq, gold=goldq, neon=nq[key], neon2=ctx["neon2"])
        D.tower_deco(t_ctx, cx, cy, z1, min(hx, 9.0), min(hy, 9.0), rr, 3 + (1 if z1 > 70 else 0) + (1 if k < 12 else 0), k < nfan, k, th_k=CFG.get("th_k", 2.2), ln_k=CFG.get("ln_k", 2.0))
    # 4. fan searchlights: gold shafts spreading from each crown (camera-only cones like the pipeline's own beams)
    if g.get("beam_shaft") and g.get("beam_mat") and not CFG.get("no_fans", False):
        BM = CP.AAA["beam"]
        for corp, v in sorted(LM.items()):
            lab, crown, hue = v
            if crown is None or corp == "rebel_cell":
                continue
            org = Vector(crown) + Vector((0, 0, 0.5))
            for k in range(CFG.get("n_fan_beams", 5)):
                a = (k - (CFG.get("n_fan_beams", 5) - 1) / 2.0) * math.radians(CFG.get("fan_deg", 17.0))
                lean = Vector((math.sin(a) * 0.9, math.sin(a) * 0.4, math.cos(a))).normalized()
                L_ = CFG.get("fan_len", 520.0)
                col = (1.0, 0.72, 0.32) if k % 2 == 0 else hues.get(corp, ((1, 0.6, 0.2),))[0]
                g["beam_shaft"]("deco_fan_%s_%d" % (corp, k), tuple(org), tuple(lean), L_, CFG.get("fan_half", 1.1),
                                g["beam_mat"]("deco_fanmat_%s_%d" % (corp, k), col, BM["emit"] * CFG.get("fan_k", 0.7)))
    # 5. build the shared accumulators
    for k in ("lac", "gold", "neon", "neon2"):
        ctx[k].build()
    for corp, a, b in extra:
        a.build()
        b.build()
    for a in nq.values():
        a.build()
    print("[deco] city: towers", len(towers), "recorded", len(REC), "landmarks", [e[0] for e in extra], flush=True)
