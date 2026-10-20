"""Orbital deco: Streamline Moderne. The pad becomes a sunburst (gold inlay + ice-white parallel rays), the silo and the
podium step in concentric brass rings with three-line ice neon, the rocket reads as a Ferriss spire (stepped gold bands),
the antenna truss is stepped with a fan crown, the dish bunkers sit on concentric rings. Runs inside Blender."""
import math
import random

import deco_restyle as D

ICE = (0.61, 0.87, 1.0)
SODIUM = (1.0, 0.45, 0.06)


def ring_boxes(acc, r0, r1, z0, z1, n=96, cx=0.0, cy=0.0, a0=0.0, a1=360.0):
    for i in range(n):
        b0, b1 = math.radians(a0 + (a1 - a0) * i / n), math.radians(a0 + (a1 - a0) * (i + 1) / n)
        quad = [(r0 * math.sin(b0), r0 * math.cos(b0)), (r1 * math.sin(b0), r1 * math.cos(b0)),
                (r1 * math.sin(b1), r1 * math.cos(b1)), (r0 * math.sin(b1), r0 * math.cos(b1))]
        acc.prism([(cx + a, cy + b) for a, b in quad], (0, 0, z0), (1, 0, 0), (0, 1, 0), (0, 0, 1), z1 - z0)


def restyle(g, cfg, ctx):
    cfg.setdefault("hue", ICE)
    cfg.setdefault("hue2", SODIUM)
    ctx["hue"] = tuple(cfg["hue"])
    cfg.setdefault("lm_box", (0.0, 0.0, 110.0, 110.0, 110.0))
    cfg.setdefault("veil_k", 0.003)
    cfg.setdefault("veil_z", (110.0, 300.0))
    D.hq_common(g, cfg, ctx)
    G, L, N, N2 = ctx["gold"], ctx["lac"], ctx["neon"], ctx["neon2"]
    CP = g["CP"]
    PR, PH, SR = CP["podium_r"], CP["podium_h"], CP["silo_r"]
    RR = CP["ring_r"]
    AN, RK = CP["antenna"], CP["rocket"]
    rng = random.Random(41)
    # the sunburst pad: 48 rays of ice neon (pairs of thin parallel lines) + gold inlay arcs, over the deck
    z = PH + 0.12
    for k in range(48):
        a = math.radians(k * 7.5)
        c, s = math.cos(a), math.sin(a)
        r0 = SR + 3.5
        r1 = PR - 3.0 if k % 2 == 0 else PR - 14.0
        for off in (-0.35, 0.35):
            p0 = (s * r0 - c * off, c * r0 + s * off, z)
            p1 = (s * r1 - c * off, c * r1 + s * off, z)
            N.bar(p0, p1, 0.18, 0.12)
    for r0, r1 in ((SR + 3.0, SR + 3.6), (PR - 15.0, PR - 14.4), (PR - 3.4, PR - 2.8)):
        ring_boxes(G, r0, r1, PH + 0.02, PH + 0.3)
    # stepped concentric rings: the silo collar and the podium rim (3 steps, gold, ice neon between)
    for (r0, r1, h) in ((SR, SR + 5.0, 1.6), (SR, SR + 3.0, 3.2), (SR, SR + 1.4, 4.8)):
        ring_boxes(G, r0, r1, PH + 0.1, PH + 0.1 + h, n=72)
    for dz in (3.5, 4.1, 4.7):
        ring_boxes(N, PR + 0.15, PR + 0.4, PH - dz, PH - dz + 0.22, n=120)
    ring_boxes(G, PR + 0.0, PR + 0.9, PH - 1.2, PH + 0.4, n=120)
    ring_boxes(G, RR + 18.0, RR + 18.8, 0.1, 0.5, n=140)
    for dz in (0.7, 1.1):
        ring_boxes(N, RR + 18.9, RR + 19.15, dz, dz + 0.16, n=140)
    # the rocket as a Ferriss spire: stepped gold collars up the body, ice neon rings
    rr_ = RK["r"]
    rz0 = PH + 4.0
    # the rocket keeps its silhouette (a slim body + nose): gold bands hugging the body, ice neon lines between, three
    # streamline fins at the base; nothing wider than the body but the fins
    for i, zz in enumerate((6, 16, 26, 36, 46)):
        rad = rr_ * 1.05
        ring_boxes(G, rad - 0.3, rad + 0.18, rz0 + zz, rz0 + zz + 0.9, n=24)
        ring_boxes(N, rad - 0.1, rad + 0.22, rz0 + zz + 1.4, rz0 + zz + 1.55, n=24)
        ring_boxes(N, rad - 0.1, rad + 0.22, rz0 + zz + 1.95, rz0 + zz + 2.1, n=24)
    for k in range(3):
        a_ = math.radians(90 + 120 * k)
        c_, s_ = math.cos(a_), math.sin(a_)
        poly = [(rr_ * 0.9, 0.0), (rr_ + 5.0, -3.0), (rr_ + 5.0, 6.0), (rr_ * 0.9, 20.0)]
        G.prism([(p[0], p[1]) for p in poly], (0, 0, rz0 + 4.0), (c_, s_, 0), (0, 0, 1), (-s_, c_, 0), 0.5)
    # the antenna truss (az 0, r 104, half 9, h 104): stepped sheath + fan crown + lines
    ax, ay = 0.0, AN["r"]
    h = AN["half"]
    z0 = AN["h"]
    for i in range(4):
        hh = 7.0
        s = h * (0.8 ** i)
        L.box(ax - s, ay - s, z0 + i * hh, ax + s, ay + s, z0 + (i + 1) * hh)
        G.box(ax - s - 0.4, ay - s - 0.4, z0 + (i + 1) * hh - 0.6, ax + s + 0.4, ay + s + 0.4, z0 + (i + 1) * hh + 0.1)
        D.neon_lines(N, ax, ay, s, s, z0 + i * hh + 3.0, n=3, gap=0.6, th=0.22, out=0.12)
    D.fan_crown(G, L, N, ax, ay, z0 + 28.0, "x", 20.0, rng, nray=11, t=0.9, backing=True)
    D.spire(G, N, ax, ay, z0 + 28.0 + 18.0, 30.0, 1.0)
    for dz in (24.0, 50.0, 76.0):
        D.neon_lines(N, ax, ay, h, h, dz, n=3, gap=0.9, th=0.28, out=0.3)
    # the five stations: concentric brass rings under each bunker
    for nid, a in g["G"].STATION.items():
        v = g["G"].az_vec(a)
        cx, cy = v[0] * RR, v[1] * RR
        for r0, r1, hh in ((13.0, 14.0, 0.7), (16.0, 16.7, 0.7), (19.0, 19.5, 0.7)):
            ring_boxes(G, r0, r1, 0.1, 0.1 + hh, n=40, cx=cx, cy=cy)
        ring_boxes(N, 14.2, 14.45, 0.5, 0.7, n=40, cx=cx, cy=cy)
