"""Solace deco: the double helix in brass ribs. A gold rib rings each strand at every floor, lime / pink double lines
run both strands, the plaza podium steps in tiers, the crown gets a sunburst fan. Runs inside Blender."""
import math
import random

import deco_restyle as D

LIME = (0.30, 1.0, 0.06)
PINK = (1.0, 0.05, 0.30)


def restyle(g, cfg, ctx):
    cfg.setdefault("hue", LIME)
    cfg.setdefault("hue2", PINK)
    ctx["hue"] = tuple(cfg["hue"])
    cfg.setdefault("lm_box", (0.0, 0.0, 60.0, 60.0, 360.0))
    cfg.setdefault("pick", "near")
    cfg.setdefault("min_top", 30.0)
    cfg.setdefault("n_towers", 160)
    cfg.setdefault("max_top", 140.0)
    cfg.setdefault("veil_k", 0.003)
    cfg.setdefault("veil_z", (200.0, 300.0))
    D.hq_common(g, cfg, ctx)
    G, L, N, N2 = ctx["gold"], ctx["lac"], ctx["neon"], ctx["neon2"]
    GR = g["G"]
    CP = g["CP"]
    RT, FH, PH = GR.RT, GR.FH, GR.PODIUM_H
    floors = CP["floors"]
    ztop = PH + floors * FH
    rng = random.Random(61)
    nseg = 18
    # brass ribs: a gold annulus round each strand every floor, double rib on the route floors
    for t in ("A", "B"):
        for f in range(1, floors + 1):
            z = PH + f * FH - 0.4
            thick = 1.5 if f in CP["route_floors"] else 0.7
            pts = [GR.tube_pt(t, z, 2 * math.pi * j / nseg, RT + 0.45) for j in range(nseg + 1)]
            for j in range(nseg):
                G.bar(pts[j], pts[j + 1], 0.55 if thick < 1 else 0.9, thick)
        # lime / pink double lines running the strand (two parallel lines each side of the front band)
        for (phi0, acc) in ((0.55, N), (0.80, N2), (-0.55, N), (-0.80, N2)):
            prev = None
            nz = int((ztop - PH) / 3.0)
            for i in range(nz + 1):
                z = PH + 1.0 + i * 3.0
                p = GR.tube_pt(t, z, phi0, RT + 0.2)
                if prev is not None:
                    acc.bar(prev, p, 0.22, 0.22)
                prev = p
    # the podium steps (plaza): 3 tiers, gold edges, lime lines
    px, py, ph = CP["podium"]
    for i in range(3):
        s = 0.86 ** i
        z0 = ph + i * 1.4
        L.box(-px * s, -py * s, z0, px * s, py * s, z0 + 1.4)
        G.box(-px * s - 0.4, -py * s - 0.4, z0 + 1.2, px * s + 0.4, py * s + 0.4, z0 + 1.55)
        D.neon_lines(N, 0, 0, px * s, py * s, z0 + 0.6, n=3, gap=0.4, th=0.14, out=0.45)
    # the crown: two crossing open fans (sunburst) behind the genome core
    for ax in ("x", "y"):
        D.fan_crown(G, L, N2, 0.0, 0.0, ztop - 2.0, ax, 34.0, rng, nray=15, t=0.9, backing=False)
