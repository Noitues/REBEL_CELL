"""Halcyon deco: a Mesoamerican-deco ziggurat (the seven tiers stay), the Eye as a sunburst crown, violet parallel neon
on each setback edge, amber floodlights. Runs inside Blender (called from deco_restyle.apply_hq)."""
import math
import random

import deco_restyle as D

VIOLET = (0.43, 0.16, 1.0)
AMBER = (1.0, 0.40, 0.03)


def restyle(g, cfg, ctx):
    cfg.setdefault("hue", VIOLET)
    cfg.setdefault("hue2", AMBER)
    ctx["hue"] = tuple(cfg["hue"])
    cfg.setdefault("lm_box", (0.0, 0.0, 75.0, 75.0, 150.0))
    cfg.setdefault("veil_z", (150.0, 300.0))
    D.hq_common(g, cfg, ctx)
    G, L, N, N2, GN = ctx["gold"], ctx["lac"], ctx["neon"], ctx["neon2"], ctx["gneon"]
    from mathutils import Vector
    _fp = g["fp"]

    def fp(*a):
        return Vector(_fp(*a))
    rng = random.Random(77)
    TEAL, CWHITE = g["TEAL"], g["CWHITE"]
    # the compound's own light lines: teal -> violet, cold white -> gold
    def rc(c):
        if D.hue_close(c, TEAL, 0.35):
            return tuple(x * 1.0 for x in cfg["hue"])
        if D.hue_close(c, CWHITE, 0.35):
            return (1.0, 0.66, 0.24)
        return c
    for k in ("trim", "small"):
        D.recolor_attr(g["OBJ"].get(k), rc)
    for t in g["TIERS"]:
        hs, z0, z1 = t["hs"], t["z0"], t["z1"]
        r = t["r"]
        # gold cornice band proud of the base cornice
        w = 0.55
        for (a, b, c_, d_) in ((-hs - 1.7, -hs - 1.7, hs + 1.7, -hs - 1.7 + w), (-hs - 1.7, hs + 1.7 - w, hs + 1.7, hs + 1.7),
                               (-hs - 1.7, -hs - 1.7, -hs - 1.7 + w, hs + 1.7), (hs + 1.7 - w, -hs - 1.7, hs + 1.7, hs + 1.7)):
            G.box(a, b, z1 - 1.0, c_, d_, z1 + 0.5)
        # three parallel violet lines on the setback edge, two amber just above
        D.neon_lines(N, 0, 0, hs, hs, z1 - 3.4, n=3, gap=0.55, th=0.28, out=1.75)
        D.neon_lines(N2, 0, 0, hs, hs, z1 + 0.9, n=2, gap=0.5, th=0.22, out=1.2)
        # corner piers running past the roofline, with parallel lines either side
        for sx in (-1, 1):
            for sy in (-1, 1):
                px, py = sx * (hs + 0.9), sy * (hs + 0.9)
                G.box(px - 0.9, py - 0.9, z0, px + 0.9, py + 0.9, z1 + 4.5 if r < 6 else z1 + 7.0)
                D.vlines(N, px + sx * 1.15, py + sy * 1.15, z0 + 1.0, z1 + 4.0, "x", n=2, gap=0.5, th=0.2)
        # chevron band under the cornice on every face
        for f in range(4):
            o = fp(f, hs + 1.0, -hs, 0.0)
            u = (fp(f, hs + 1.0, 1.0, 0.0) - o)
            n = (fp(f, hs + 2.0, 0.0, 0.0) - fp(f, hs + 1.0, 0.0, 0.0))
            D.chevron_band(G, o, u, (0, 0, 1), n, hs, z1 - 5.6, 2.0, 0.34, 0.5)
        # stepped parapet merlons
        for f in range(4):
            for q in range(int(hs / 3.0)):
                uu = -hs + 1.5 + q * 6.0
                if uu > hs - 3.0:
                    break
                p0 = fp(f, hs + 1.0, uu, z1 + 0.5)
                p1 = fp(f, hs + 1.5, uu + 2.4, z1 + 2.0)
                G.box(min(p0.x, p1.x), min(p0.y, p1.y), p0.z, max(p0.x, p1.x), max(p0.y, p1.y), p1.z)
    # the Eye as a sunburst crown: two open fans (gold ribs + parallel neon arcs) behind and around the eye
    EX, EY, EZ = g["EX"], g["EY"], g["EZ"]
    R = cfg.get("eye_fan_r", 34.0)
    for ax in ("x", "y"):
        D.fan_crown(G, L, N2, EX, EY, EZ - 6.0, ax, R, rng, nray=13, t=0.7, backing=False)
    # eye plinth: stepped gold rings
    for i, (rr, hh) in enumerate(((12.0, 1.4), (9.5, 1.4), (7.0, 1.4))):
        G.box(EX - rr, EY - rr, EZ - 24.0 + i * 1.4, EX + rr, EY + rr, EZ - 22.6 + i * 1.4)
    if cfg.get("v2"):
        # v2: graded Chrysler arcs on the four corners of the top four tiers (small low, large high), stainless metal,
        # triangular windows between the arcs lit violet from inside; the Eye's gold stays the only gold focal point
        import bpy
        steel = D.principled("deco_steel_h", (0.80, 0.84, 0.92), 1.0, 0.14, coat=0.4, coat_rough=0.05, emit=(0.8, 0.85, 1.0), emit_k=0.25)
        vio = D.principled("deco_vio_win", (0, 0, 0), 0.0, 0.5, emit=(0.43, 0.16, 1.0), emit_k=cfg.get("v2_win_k", 4.0))
        ST, VI = D.DAcc("deco_h_steel", steel, ctx["coll"]), D.DAcc("deco_h_vio", vio, ctx["coll"])
        tiers = g["TIERS"]
        sizes = cfg.get("v2_r", (3.5, 5.0, 7.0, 9.5))
        for k, t in enumerate(tiers[3:]):
            hs, z1 = t["hs"], t["z1"]
            R = sizes[k]
            for sx in (-1, 1):
                for sy in (-1, 1):
                    cx, cy = sx * (hs + 0.9), sy * (hs + 0.9)
                    D.fan_crown(ST, VI, N, cx, cy - sy * 0.0, z1 + 0.5, "x", R, rng, nray=9, t=0.5, backing=True)
                    D.fan_crown(ST, VI, N, cx, cy, z1 + 0.5, "y", R, rng, nray=9, t=0.5, backing=True)
        ST.build()
        VI.build()
