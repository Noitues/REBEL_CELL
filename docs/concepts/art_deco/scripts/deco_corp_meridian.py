"""Meridian deco: Machine-Age. The Gatehouse Gantry stays (two legs, the span, the keep) and is re-ornamented as a riveted
brass gatehouse: gold fluted piers, chevron hazard bands, stepped crowns on the legs, orange triple-line neon up the
legs and along the span, a fan crown behind the keep. Runs inside Blender."""
import random

import bpy

import deco_restyle as D

ORANGE = (1.0, 0.26, 0.01)
RED = (1.0, 0.03, 0.02)


def restyle(g, cfg, ctx):
    cfg.setdefault("hue", ORANGE)
    cfg.setdefault("hue2", RED)
    ctx["hue"] = tuple(cfg["hue"])
    cfg.setdefault("lm_box", (0.0, 20.0, 125.0, 110.0, 150.0))
    cfg.setdefault("veil_z", (110.0, 300.0))
    D.hq_common(g, cfg, ctx)
    G, L, N, N2 = ctx["gold"], ctx["lac"], ctx["neon"], ctx["neon2"]
    CP = g["CP"]
    GC = CP["gantry"]
    lot, wt, nc, crs = CP["lot"], CP["wall"]["t"], CP["wall"]["courses"], CP["course"]
    wtop = nc * crs
    gy = GC["y"]
    lhx, lhy = GC["leg"]
    ltop = GC["leg_top"]
    legx = lot - wt / 2
    sz0, sz1 = GC["span_z"]
    sh = GC["span_half"]
    kx, (khx, khy), ktop = GC["keep_x"], GC["keep"], GC["keep_top"]
    rng = random.Random(33)
    # containers: dark lacquer, brass ribs read through
    m = bpy.data.materials.get("container")
    if m is not None:
        D.lacquer_panels(m, dark=0.35, seam_gold=0.0)
    for sx in (-1, 1):
        cx = sx * legx
        x0, x1, y0, y1 = cx - lhx, cx + lhx, gy - lhy, gy + lhy
        # fluted gold piers on all four corners and mid-faces, running past the parapet
        for fx in (x0, x1):
            for fy in (y0, y1):
                G.box(fx - 1.0, fy - 1.0, wtop + 4.0, fx + 1.0, fy + 1.0, ltop + 16.0)
        for q in range(1, 4):
            yy = y0 + (y1 - y0) * q / 4.0
            G.box(x0 - 0.7, yy - 0.4, wtop + 8.0, x0 + 0.2, yy + 0.4, ltop)
            G.box(x1 - 0.2, yy - 0.4, wtop + 8.0, x1 + 0.7, yy + 0.4, ltop)
        # chevron hazard bands (gold V on lacquer) on the south and north faces, three heights
        for zb in (wtop + 22.0, wtop + 60.0, ltop - 22.0):
            L.box(x0 - 0.15, y0 - 0.25, zb - 0.3, x1 + 0.15, y0 + 0.0, zb + 7.3)
            D.chevron_band(G, (x0, y0 - 0.3, 0.0), (1, 0, 0), (0, 0, 1), (0, -1, 0), (x1 - x0) / 2.0, zb, 7.0, 1.2, 0.35)
            L.box(x0 - 0.15, y1, zb - 0.3, x1 + 0.15, y1 + 0.25, zb + 7.3)
            D.chevron_band(G, (x0, y1 + 0.25, 0.0), (1, 0, 0), (0, 0, 1), (0, 1, 0), (x1 - x0) / 2.0, zb, 7.0, 1.2, 0.35)
        # triple-line orange neon, vertical, up the outer/inner x faces and the south face
        for fx, sgn in ((x0, -1), (x1, 1)):
            D.vlines(N, fx + sgn * 0.5, gy, wtop + 6.0, ltop + 2.0, "y", n=3, gap=1.6, th=0.4)
        D.vlines(N, cx, y0 - 0.6, wtop + 6.0, ltop + 2.0, "x", n=3, gap=1.8, th=0.4)
        D.neon_lines(N, cx, gy, lhx, lhy, ltop - 4.0, n=3, gap=1.0, th=0.4, out=0.6)
        # stepped crown (3 tiers x 80 %) with spire
        sx_, sy_, z = lhx, lhy, ltop + 1.0
        for i in range(3):
            h = 8.0
            L.box(cx - sx_, gy - sy_, z, cx + sx_, gy + sy_, z + h)
            G.box(cx - sx_ - 0.5, gy - sy_ - 0.5, z + h - 0.7, cx + sx_ + 0.5, gy + sy_ + 0.5, z + h + 0.2)
            D.neon_lines(N, cx, gy, sx_, sy_, z + h * 0.45, n=3, gap=0.8, th=0.3, out=0.15)
            z += h
            sx_ *= 0.8
            sy_ *= 0.8
        D.spire(G, N2, cx, gy, z, 22.0, 2.4)
    # the span: gold edge beams, triple neon along both faces, chevron band
    xa, xb = -legx + lhx, legx - lhx
    for zz in (sz0, sz1):
        G.box(xa, gy - sh - 0.6, zz - 0.5, xb, gy + sh + 0.6, zz + 0.5)
    for yy in (gy - sh - 0.5, gy + sh + 0.5):
        for i in range(3):
            N.box(xa, yy - 0.2, sz0 + 3.5 + i * 2.6 - 0.2, xb, yy + 0.2, sz0 + 3.5 + i * 2.6 + 0.2)
    D.chevron_band(G, (xa, gy - sh - 0.9, 0.0), (1, 0, 0), (0, 0, 1), (0, -1, 0), (xb - xa) / 2.0, sz0 + 3.0, 12.0, 1.4, 0.4)
    # the keep: stepped fan crown behind its lantern (open, so the keep silhouette stays), parallel neon on its body
    D.fan_crown(G, L, N2, kx, gy, ktop + 2.0, "x", 26.0, rng, nray=13, t=0.9, backing=False)
    D.neon_lines(N, kx, gy, khx, khy, ktop - 14.0, n=3, gap=1.2, th=0.35, out=0.3)
    for sx in (-1, 1):
        for sy in (-1, 1):
            G.box(kx + sx * khx - 0.9, gy + sy * khy - 0.9, wtop + 30.0, kx + sx * khx + 0.9, gy + sy * khy + 0.9, ktop + 6.0)
    # S corner towers: stepped, gold cornices, triple neon
    ch, ct = CP["corner"]["half"], CP["corner"]["h"]
    for sx in (-1, 1):
        cx, cy = sx * (lot - ch), -(lot - ch)
        z = ct
        s_ = ch
        for i in range(3):
            L.box(cx - s_, cy - s_, z, cx + s_, cy + s_, z + 9.0)
            G.box(cx - s_ - 0.5, cy - s_ - 0.5, z + 8.4, cx + s_ + 0.5, cy + s_ + 0.5, z + 9.2)
            D.neon_lines(N, cx, cy, s_, s_, z + 4.0, n=3, gap=0.8, th=0.3, out=0.2)
            z += 9.0
            s_ *= 0.8
        D.neon_lines(N, cx, cy, ch, ch, ct - 6.0, n=3, gap=1.0, th=0.35, out=0.6)
        for fx in (-1, 1):
            for fy in (-1, 1):
                G.box(cx + fx * ch - 0.9, cy + fy * ch - 0.9, wtop + 2.0, cx + fx * ch + 0.9, cy + fy * ch + 0.9, ct + 4.0)
