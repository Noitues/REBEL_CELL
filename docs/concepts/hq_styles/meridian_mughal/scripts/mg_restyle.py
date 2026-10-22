"""Meridian v2: a Mughal freight palace. Runs INSIDE Blender, hooked in front of the render section of hq_scene.py.
The castle compound (walls, towers, gantry, containers, rooms, rail gates) is cut out of the scene and rebuilt as a charbagh:
a white-marble mausoleum with an onion dome on a raised plinth, four minarets that are container cranes, a reflecting pool
that is also the barge canal, four container parterres divided by water, an iwan gateway for the trucks, backlit jali.
Reuses the streamline accumulator (SAcc) and the art-deco helpers (read only)."""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "meridian_streamline", "scripts")))
import sl_restyle as S  # noqa: E402
import deco_restyle as D  # noqa: E402

ORANGE = (1.0, 0.26, 0.01)
RED = (1.0, 0.03, 0.02)
BOX = 124.0


def cut_castle(g):
    OBJ = g["OBJ"]
    for k in ("gantry", "masonry", "cut", "int", "glass"):
        if OBJ.get(k) is not None:
            OBJ[k].hide_render = True
    for k, o in OBJ.items():
        if o is not None and k.startswith("room_"):
            o.hide_render = True
    for k in ("containers", "rough", "metal", "trim", "small", "seams", "train", "streaks"):
        o = OBJ.get(k)
        if o is None:
            continue
        bm = bmesh.new()
        bm.from_mesh(o.data)
        dead = [f for f in bm.faces if abs(f.calc_center_median().x) < BOX and abs(f.calc_center_median().y) < BOX]
        bmesh.ops.delete(bm, geom=dead, context="FACES")
        bm.to_mesh(o.data)
        bm.free()
        o.data.update()
    # compound lights off (keep the gate floods)
    L = g["LIGHTS"]
    for i, (ob, e0, grp) in enumerate(L):
        if grp == "corp" and abs(ob.location.x) < BOX + 12 and abs(ob.location.y) < BOX + 12 and not ob.name.startswith("gate_"):
            L[i] = (ob, 0.0, grp)
            ob.data.energy = 0.0
    for ob, e0, grp in L:
        if ob.name.startswith("beam_0"):
            ob.location = (0.0, 72.0, 181.0)


# ----------------------------------------------------------------------------------------------- shape helpers
def arch_pts(hw, spring, apex, n=10):
    """Left half of a pointed arch from (-hw, spring) up to (0, apex): list of (a, b)."""
    h = apex - spring
    c = (h * h - hw * hw) / (2.0 * hw)
    R = hw + c
    pts = []
    a0 = math.atan2(0.0, -hw - c)
    a1 = math.atan2(h, -c)
    for i in range(n + 1):
        t = a0 + (a1 - a0) * i / n
        pts.append((c + R * math.cos(t), spring + R * math.sin(t)))
    pts[-1] = (0.0, apex)
    return pts, c, R


def arch_poly(hw, spring, apex, base=0.0, n=10):
    left, _, _ = arch_pts(hw, spring, apex, n)
    right = [(-a, b) for a, b in reversed(left[:-1])]
    return [(-hw, base)] + left + right + [(hw, base)]


def arch_h(a, hw, spring, apex):
    left, c, R = arch_pts(hw, spring, apex, 4)
    return spring + math.sqrt(max(0.0, R * R - (abs(a) + c) ** 2))


def frame(n):
    n = Vector(n)
    if n.y < -0.5:
        return Vector((1, 0, 0)), n
    if n.y > 0.5:
        return Vector((-1, 0, 0)), n
    if n.x < -0.5:
        return Vector((0, -1, 0)), n
    return Vector((0, 1, 0)), n


def lathe_z(acc, cx, cy, z0, prof, n=36, scale=1.0):
    """Body of revolution about z. prof = [(r, dz)]."""
    rings = []
    for r, dz in prof:
        rings.append([(cx + r * scale * math.cos(2 * math.pi * j / n), cy + r * scale * math.sin(2 * math.pi * j / n), z0 + dz) for j in range(n)])
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(n):
            k = (j + 1) % n
            acc.face([r0[j], r0[k], r1[k], r1[j]])
    acc.face(rings[0][::-1])
    acc.face(rings[-1])


ONION = [(0, 1.0), (.08, 1.12), (.18, 1.22), (.30, 1.24), (.42, 1.15), (.55, .95), (.68, .70), (.80, .45), (.90, .24), (.96, .10), (1.0, .03)]


def onion(acc, cx, cy, z0, R, H, n=40):
    prof = [(R * k, H * t) for t, k in ONION]
    lathe_z(acc, cx, cy, z0, prof, n)


def chattri(A, cx, cy, z0, s, hcol=7.0, hdome=None):
    MB, GD = A["marble"], A["gold"]
    for sx in (-1, 1):
        for sy in (-1, 1):
            MB.box(cx + sx * s - 0.45, cy + sy * s - 0.45, z0, cx + sx * s + 0.45, cy + sy * s + 0.45, z0 + hcol)
    MB.box(cx - s - 1.0, cy - s - 1.0, z0 + hcol, cx + s + 1.0, cy + s + 1.0, z0 + hcol + 0.9)
    onion(A["glow"], cx, cy, z0 + hcol + 0.9, s * 1.25, hdome or s * 2.6, 20)
    GD.cyl_z(cx, cy, z0 + hcol + 0.9 + (hdome or s * 2.6) * 0.95, z0 + hcol + 0.9 + (hdome or s * 2.6) * 1.35, 0.25, 6)


def pishtaq(A, cx, cy, zb, n, w, h, rng, depth=2.4, bar=True):
    """Rectangular frame slab with a pointed-arch iwan whose interior is a backlit orange jali; barcode band above."""
    MB, OR, RD, DK, GD = A["marble"], A["orange"], A["red"], A["inlay"], A["gold"]
    u, nv = frame(n)
    o = Vector((cx, cy, zb))
    v = Vector((0, 0, 1))
    MB.prism([(-w / 2, 0), (w / 2, 0), (w / 2, h), (-w / 2, h)], o, u, v, nv, depth)
    hw, spring, apex = w * 0.30, h * 0.52, h * 0.80
    # recessed arch: backlit orange panel
    OR.prism(arch_poly(hw, spring, apex, h * 0.06), o + nv * (depth - 0.1), u, v, nv, 0.35)
    # jali lattice over the panel: dark bars clipped to the arch
    oo = o + nv * (depth + 0.2)
    k = -hw + 0.8
    while k < hw - 0.5:
        top = arch_h(k, hw, spring, apex) - 0.4
        DK.prism([(k - 0.17, h * 0.06), (k + 0.17, h * 0.06), (k + 0.17, top), (k - 0.17, top)], oo, u, v, nv, 0.35)
        k += 1.6
    b = h * 0.06 + 2.0
    while b < apex - 1.5:
        ww = min(hw, math.sqrt(max(0.0, 1.0 - 0)) * 0) + 0
        hh = arch_h(0.0, hw, spring, apex)
        # half-width of the arch at height b
        left, c, R = arch_pts(hw, spring, apex, 6)
        if b <= spring:
            wb = hw
        else:
            wb = max(0.0, math.sqrt(max(0.0, R * R - (b - spring) ** 2)) - c)
        if wb > 0.6:
            DK.prism([(-wb, b - 0.15), (wb, b - 0.15), (wb, b + 0.15), (-wb, b + 0.15)], oo, u, v, nv, 0.35)
        b += 2.4
    # arch outline: hot red neon
    pl = arch_poly(hw + 0.5, spring, apex + 0.5, h * 0.06)
    for p0, p1 in zip(pl, pl[1:]):
        P0 = o + u * p0[0] + v * p0[1] + nv * (depth + 0.1)
        P1 = o + u * p1[0] + v * p1[1] + nv * (depth + 0.1)
        RD.bar(P0, P1, 0.35)
    # barcode band (pietra dura as shipping marks) in the spandrel zone above the arch
    if bar:
        x = -w / 2 + 1.2
        while x < w / 2 - 1.4:
            bw = rng.choice((0.25, 0.25, 0.5, 0.8))
            DK.prism([(x, h * 0.86), (x + bw, h * 0.86), (x + bw, h * 0.95), (x, h * 0.95)], o + nv * depth, u, v, nv, 0.2)
            x += bw + rng.choice((0.3, 0.45, 0.7))
    # frame edge neon
    for sgn in (-1, 1):
        OR.prism([(sgn * w / 2 - 0.2, 0), (sgn * w / 2 + 0.2, 0), (sgn * w / 2 + 0.2, h), (sgn * w / 2 - 0.2, h)], o + nv * depth, u, v, nv, 0.25)


def minaret(A, cx, cy, z0, rng, jib_dir, base_r=3.8, top_r=2.5, H=92.0):
    MB, GD, OR, RD, CH = A["marble"], A["gold"], A["orange"], A["red"], A["chrome"]
    n = 12
    sec = [z0, z0 + H * 0.36, z0 + H * 0.68, z0 + H]
    for i in range(3):
        r0 = base_r + (top_r - base_r) * (sec[i] - z0) / H
        r1 = base_r + (top_r - base_r) * (sec[i + 1] - z0) / H
        lathe_z(MB, cx, cy, sec[i], [(r0, 0.0), (r0 * 0.96, 0.7), (r1, sec[i + 1] - sec[i] - 1.8), (r1 * 1.0, sec[i + 1] - sec[i])], n)
        # orange inlay lines (pietra dura rings) and vertical barcode flutes
        for dz in (6.0, 7.2):
            rr = r0 + (r1 - r0) * dz / (sec[i + 1] - sec[i])
            OR.cyl_z(cx, cy, sec[i] + dz, sec[i] + dz + 0.35, rr + 0.12, 16)
        for j in range(8):
            a = 2 * math.pi * j / 8
            for q in range(4):
                zz = sec[i] + 10.0 + q * 6.0
                if zz + 3.0 > sec[i + 1] - 4.0:
                    break
                rr = r0 + (r1 - r0) * (zz - sec[i]) / (sec[i + 1] - sec[i])
                A["inlay"].box(cx + (rr + 0.05) * math.cos(a) - 0.12, cy + (rr + 0.05) * math.sin(a) - 0.12, zz, cx + (rr + 0.05) * math.cos(a) + 0.12, cy + (rr + 0.05) * math.sin(a) + 0.12, zz + rng.choice((1.5, 2.4, 3.0)))
        # balcony
        zb = sec[i + 1]
        rb = r1 + 2.4
        MB.cyl_z(cx, cy, zb - 0.6, zb + 0.5, rb, 16)
        OR.cyl_z(cx, cy, zb + 0.5, zb + 0.9, rb + 0.1, 16)
        for j in range(16):
            a = 2 * math.pi * j / 16
            MB.cyl((cx + rb * 0.92 * math.cos(a), cy + rb * 0.92 * math.sin(a), zb + 0.5), (cx + rb * 0.92 * math.cos(a), cy + rb * 0.92 * math.sin(a), zb + 2.1), 0.14, 5)
    ztop = z0 + H
    # top chattri
    chattri(A, cx, cy, ztop + 0.6, 1.9, 5.2, 5.0)
    # container-crane jib swinging out from the top: pivot mast, lattice jib, counterweight, trolley, hanging container
    zj = ztop + 12.0
    CH.cyl((cx, cy, ztop + 5.0), (cx, cy, zj + 3.0), 0.5, 8)
    d = Vector((math.cos(jib_dir), math.sin(jib_dir), 0.0))
    P = Vector((cx, cy, zj))
    tipA = P + d * 44.0
    tipB = P - d * 14.0
    CH.bar(tipB, tipA, 3.2, 4.0)
    OR.bar(tipB + Vector((0, 0, 1.2)), tipA + Vector((0, 0, 1.2)), 0.35)
    RD.bar(tipB + Vector((0, 0, -1.3)), tipA + Vector((0, 0, -1.3)), 0.3)
    for i in range(0, 12):
        a = P + d * (-14.0 + i * 4.8)
        b = P + d * (-14.0 + (i + 1) * 4.8)
        CH.bar(a + Vector((0, 0, -1.0)), b + Vector((0, 0, 1.0)) if i % 2 == 0 else b + Vector((0, 0, -1.0)), 0.18)
    CH.bar(P + Vector((0, 0, 0.5)), P + d * 30.0 + Vector((0, 0, -0.5)), 0.001) if False else None
    for sgn in (-1, 1):   # backstays from the mast head
        CH.bar(P + Vector((0, 0, 8.0)), P + d * 40.0 + Vector((0, 0, 1.2)), 0.12)
        break
    CH.bar(P + Vector((0, 0, 8.0)), tipB, 0.12)
    CH.box(cx + d.x * (-14) - 2.0, cy + d.y * (-14) - 2.0, zj - 2.5, cx + d.x * (-14) + 2.0, cy + d.y * (-14) + 2.0, zj + 2.5)
    tp = P + d * rng.uniform(24.0, 36.0)
    CH.box(tp.x - 1.6, tp.y - 1.6, zj - 2.6, tp.x + 1.6, tp.y + 1.6, zj - 1.0)
    hang = rng.uniform(8.0, 14.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            CH.bar((tp.x + sx * 1.2, tp.y + sy * 1.0, zj - 2.6), (tp.x + sx * 2.6, tp.y + sy * 1.0, zj - 2.6 - hang), 0.08)
    ctn = "crane_ctn"
    # container: long axis perpendicular-ish to the jib
    A[ctn].box(tp.x - 7.0, tp.y - 3.0, zj - 2.6 - hang - 6.0, tp.x + 7.0, tp.y + 3.0, zj - 2.6 - hang)
    # lit tip lamp
    RD.cyl_z(tipA.x, tipA.y, zj + 1.0, zj + 2.4, 0.7, 8)


# ----------------------------------------------------------------------------------------------- the palace
def materials():
    M = S.mats()
    M["marble"] = D.principled("mg_marble", (0.78, 0.79, 0.84), 0.0, 0.30, coat=0.6, coat_rough=0.05, emit=(0.85, 0.9, 1.0), emit_k=0.05)
    M["glow"] = D.principled("mg_dome", (0.85, 0.86, 0.9), 0.0, 0.28, coat=0.6, coat_rough=0.05, emit=(0.95, 0.95, 1.0), emit_k=0.60)
    M["gold"] = D.principled("mg_gold", (1.0, 0.62, 0.16), 1.0, 0.22, emit=(1.0, 0.55, 0.12), emit_k=0.6)
    M["inlay"] = D.principled("mg_inlay", (0.012, 0.012, 0.016), 0.0, 0.25, coat=0.5)
    M["sand"] = D.principled("mg_sandstone", (0.16, 0.035, 0.024), 0.0, 0.5, emit=(0.5, 0.1, 0.05), emit_k=0.03)
    M["paving"] = D.principled("mg_paving", (0.06, 0.065, 0.08), 0.1, 0.35, coat=0.3)
    M["water"] = D.principled("mg_water", (0.30, 0.38, 0.50), 1.0, 0.03, emit=(0.25, 0.5, 0.9), emit_k=0.35)
    M["ctn_steel"] = D.principled("mg_ctn_steel", (0.17, 0.22, 0.32), 0.4, 0.35, coat=0.6, emit=(0.30, 0.40, 0.60), emit_k=0.06)
    M["ctn_red"] = D.principled("mg_ctn_red", (0.45, 0.04, 0.03), 0.3, 0.3, coat=0.6, emit=(0.6, 0.05, 0.03), emit_k=0.05)
    M["ctn_orange"] = D.principled("mg_ctn_orange", (0.9, 0.25, 0.02), 0.3, 0.3, coat=0.6, emit=(1.0, 0.26, 0.01), emit_k=0.15)
    M["crane_ctn"] = D.emission("mg_crane_ctn", (1.0, 0.30, 0.03), 5.0)
    M["ctn_white"] = D.principled("mg_ctn_white", (0.5, 0.52, 0.56), 0.2, 0.3, coat=0.6, emit=(0.6, 0.62, 0.7), emit_k=0.15)
    return M


def box2(acc, cx, cy, hx, hy, z0, z1):
    acc.box(cx - hx, cy - hy, z0, cx + hx, cy + hy, z1)


def build(g, cfg, A):
    rng = random.Random(2610)
    MB, GL, GD, OR, RD, DK, SD, PV, WT = (A[k] for k in ("marble", "glow", "gold", "orange", "red", "inlay", "sand", "paving", "water"))
    CH = A["chrome"]
    LOT = 120.0
    # ---------------------------------------------------------------- ground: plots, channels, pool
    ZP = 1.9
    ZW = 1.3
    ch_x = 10.0                        # half width of the main axis pool
    cy0, ch_w = -48.0, 6.0            # cross channel centre / half width
    y_s, y_n = -113.0, 20.0           # garden extent S .. plinth
    # water: main axis + cross channel + central basin
    WT.box(-ch_x, y_s, 0.0, ch_x, y_n + 4.0, ZW)
    WT.box(-LOT + 8.0, cy0 - ch_w, 0.0, LOT - 8.0, cy0 + ch_w, ZW)
    WT.box(-13.0, cy0 - 13.0, 0.0, 13.0, cy0 + 13.0, ZW)
    # paving under everything (dark)
    PV.box(-LOT, -LOT, 0.0, LOT, LOT, 0.5)
    # white coping along the water edges
    def coping(x0, y0, x1, y1):
        MB.box(x0, y0, ZW - 0.1, x1, y1, ZP + 0.25)
    plots = []
    xs = ((-LOT + 8.0, -ch_x - 2.0), (ch_x + 2.0, LOT - 8.0))
    ys = ((y_s, cy0 - ch_w - 2.0), (cy0 + ch_w + 2.0, y_n))
    for (xa, xb) in xs:
        for (ya, yb) in ys:
            plots.append((xa, ya, xb, yb))
    for sgn in (-1, 1):   # flank gardens beside the plinth
        plots.append((min(sgn * 63.0, sgn * (LOT - 8.0)), 27.0, max(sgn * 63.0, sgn * (LOT - 8.0)), LOT - 8.0))
    for (xa, ya, xb, yb) in plots:
        PV.box(xa, ya, 0.0, xb, yb, ZP)
        # pietra-dura border: orange line, white line, barcode band, round the plot
        for (a0, b0, a1, b1) in ((xa, ya, xb, ya + 0.5), (xa, yb - 0.5, xb, yb), (xa, ya, xa + 0.5, yb), (xb - 0.5, ya, xb, yb)):
            MB.box(a0, b0, ZP, a1, b1, ZP + 0.12)
        for (a0, b0, a1, b1) in ((xa + 0.9, ya + 0.9, xb - 0.9, ya + 1.3), (xa + 0.9, yb - 1.3, xb - 0.9, yb - 0.9), (xa + 0.9, ya + 0.9, xa + 1.3, yb - 0.9), (xb - 1.3, ya + 0.9, xb - 0.9, yb - 0.9)):
            DK.box(a0, b0, ZP, a1, b1, ZP + 0.15)
        # container parterre: concentric rectangular rings of containers (geometric), heights 3 / 2 / 1, three colours
        cxm, cym = (xa + xb) / 2.0, (ya + yb) / 2.0
        hx, hy = (xb - xa) / 2.0, (yb - ya) / 2.0
        cl, cw, chh = 9.6, 4.6, 5.0
        for ring, (inset, nstack, mat) in enumerate(((5.0, 3, "ctn_steel"), (13.0, 2, "ctn_steel"), (21.0, 1, "ctn_orange"))):
            rx, ry = hx - inset, hy - inset
            if rx < 6 or ry < 6:
                continue
            # long sides along x, short sides along y
            x = -rx
            while x + cl <= rx + 0.01:
                for sgn in (-1, 1):
                    for s_ in range(nstack):
                        m = mat if rng.random() > 0.1 else "ctn_red"
                        A[m].box(cxm + x + 0.15, cym + sgn * ry - cw / 2, ZP + s_ * chh, cxm + x + cl - 0.15, cym + sgn * ry + cw / 2, ZP + (s_ + 1) * chh - 0.1)
                x += cl
            y = -ry + cw
            while y + cl <= ry - cw + 0.01:
                for sgn in (-1, 1):
                    for s_ in range(nstack):
                        m = mat if rng.random() > 0.1 else "ctn_red"
                        A[m].box(cxm + sgn * rx - cw / 2, cym + y + 0.15, ZP + s_ * chh, cxm + sgn * rx + cw / 2, cym + y + cl - 0.15, ZP + (s_ + 1) * chh - 0.1)
                y += cl
        # centre: an eight-pointed star of orange inlay and a lit white fountain disc
        A["white"].cyl_z(cxm, cym, ZP, ZP + 0.4, 3.2, 20)
        for k_ in range(8):
            a = math.pi * k_ / 8
            pass
    # coping for the channels
    for sgn in (-1, 1):
        coping(min(sgn * ch_x, sgn * (ch_x + 2.0)), y_s, max(sgn * ch_x, sgn * (ch_x + 2.0)), y_n + 4.0)
        yc = cy0 + sgn * ch_w
        coping(-LOT + 8.0, min(yc, yc + sgn * 2.0), LOT - 8.0, max(yc, yc + sgn * 2.0))
    # barcode band along both sides of the main pool (shipping-mark inlay)
    for sgn in (-1, 1):
        y = y_s + 2.0
        while y < y_n:
            bw = rng.choice((0.3, 0.3, 0.6, 1.0))
            DK.box(sgn * (ch_x + 1.3) - 0.9, y, ZP, sgn * (ch_x + 1.3) + 0.9, y + bw, ZP + 0.2)
            y += bw + rng.choice((0.4, 0.6, 0.9))
    # barges on the canal, loaded with lit containers
    def barge(cx, cy, along_y, ncs, mat):
        L, Wd = 30.0, 6.4
        hx, hy = (Wd / 2, L / 2) if along_y else (L / 2, Wd / 2)
        A["steel"].box(cx - hx, cy - hy, ZW - 0.3, cx + hx, cy + hy, ZW + 1.6)
        RD.box(cx - hx - 0.05, cy - hy - 0.05, ZW + 1.0, cx + hx + 0.05, cy + hy + 0.05, ZW + 1.3) if False else None
        n = 3
        for i in range(n):
            for j in range(ncs):
                m = mat if rng.random() > 0.2 else "ctn_white"
                off = (i - (n - 1) / 2.0) * 9.8
                if along_y:
                    A[m].box(cx - 2.1, cy + off - 4.6, ZW + 1.6 + j * chh, cx + 2.1, cy + off + 4.6, ZW + 1.6 + (j + 1) * chh - 0.1)
                else:
                    A[m].box(cx + off - 4.6, cy - 2.1, ZW + 1.6 + j * chh, cx + off + 4.6, cy + 2.1, ZW + 1.6 + (j + 1) * chh - 0.1)
        # bow lamp + stripe
        OR.box(cx - hx - 0.1, cy - hy, ZW + 1.0, cx + hx + 0.1, cy + hy, ZW + 1.25) if along_y else OR.box(cx - hx, cy - hy - 0.1, ZW + 1.0, cx + hx, cy + hy + 0.1, ZW + 1.25)
    barge(0.0, -88.0, True, 2, "ctn_orange")
    barge(0.0, -22.0, True, 1, "ctn_red")
    barge(-62.0, cy0, False, 2, "ctn_steel")
    barge(64.0, cy0, False, 1, "ctn_orange")
    # ---------------------------------------------------------------- the enclosing wall with backlit jali slits
    WH = 11.0
    ent = 28.0
    for (x0, y0, x1, y1) in ((-LOT, -LOT, -ent, -LOT + 6.0), (ent, -LOT, LOT, -LOT + 6.0), (-LOT, -LOT, -LOT + 6.0, LOT), (LOT - 6.0, -LOT, LOT, LOT), (-LOT, LOT - 6.0, LOT, LOT)):
        SD.box(x0, y0, 0.0, x1, y1, WH)
        MB.box(x0 - 0.5, y0 - 0.5, WH, x1 + 0.5, y1 + 0.5, WH + 1.0)
    # jali slits (emissive orange, dark mullions) on the S and W outer faces and the inner faces
    xs_ = [x for x in range(-int(LOT) + 8, int(-ent) - 2, 3)] + [x for x in range(int(ent) + 2, int(LOT) - 8, 3)]
    for x in xs_:
        OR.box(x, -LOT - 0.25, 3.0, x + 1.3, -LOT, 9.0)
    y = -int(LOT) + 8
    while y < LOT - 8:
        OR.box(-LOT - 0.25, y, 3.0, -LOT, y + 1.3, 9.0)
        y += 3
    # corner pavilions (chattri) on the wall corners
    for sx in (-1, 1):
        for sy in (-1, 1):
            chattri(A, sx * (LOT - 3.0), sy * (LOT - 3.0), WH + 1.0, 3.6, 8.0, 9.0)
    # ---------------------------------------------------------------- iwan gateway (trucks enter): S wall
    gz, gw, gh = 0.0, 60.0, 62.0
    ay, apex_w = -LOT + 3.0, 11.0
    # two piers, lintel, spandrels
    for sgn in (-1, 1):
        MB.box(min(sgn * ent, sgn * (ent - 14)) , -LOT - 3.0, 0.0, max(sgn * ent, sgn * (ent - 14)), -LOT + 11.0, gh)
    MB.box(-ent, -LOT - 3.0, 38.0, ent, -LOT + 11.0, gh)
    hw_, spr_, apx_ = 13.0, 24.0, 38.0
    for sgn in (-1, 1):
        left, c, R = arch_pts(hw_, spr_, apx_, 10)
        poly = [(sgn * hw_, spr_), (sgn * hw_, apx_), (0.0, apx_)] + [(sgn * -a, b) for a, b in reversed(left)][::-1][::-1]
        pass
    # spandrels: region between the arch curve and the rectangle above the springline
    left, c, R = arch_pts(hw_, spr_, apx_, 10)
    for sgn in (-1, 1):
        poly = [(sgn * hw_, spr_)] + [(sgn * (-a), b) for a, b in left[1:]] + [(sgn * hw_, apx_)]
        MB.prism(poly, (0.0, -LOT - 3.0, 0.0), (1, 0, 0), (0, 0, 1), (0, 1, 0), 14.0)
    # arch passage: a dark tunnel; at the back the backlit orange jali wall (truck lanes glow)
    OR.box(-hw_ + 0.5, -LOT + 7.0, 0.0, hw_ - 0.5, -LOT + 7.3, apx_ - 6.0)
    for k_ in range(-12, 13, 2):
        DK.box(k_ * 1.0 - 0.15, -LOT + 6.8, 0.0, k_ * 1.0 + 0.15, -LOT + 7.0, arch_h(k_, hw_, spr_, apx_) - 1.0)
    for zz in range(3, int(apx_) - 4, 4):
        DK.box(-hw_ + 0.5, -LOT + 6.8, zz, hw_ - 0.5, -LOT + 7.0, zz + 0.25)
    # arch outline neon red and orange
    pl = arch_poly(hw_ + 0.6, spr_, apx_ + 0.6, 0.0)
    for p0, p1 in zip(pl, pl[1:]):
        RD.bar((p0[0], -LOT - 3.2, p0[1]), (p1[0], -LOT - 3.2, p1[1]), 0.5)
    # upper stages: two tiers of small arch niches + barcode frieze + flanking chattris and a crown row
    for tier, zb_ in enumerate((40.0, 49.0)):
        for k_ in range(-3, 4):
            if tier == 1 and abs(k_) > 2:
                continue
            xx = k_ * 7.0
            OR.prism(arch_poly(1.9, 4.0, 7.2, 0.0, 6), (xx, -LOT - 3.0, zb_), (1, 0, 0), (0, 0, 1), (0, -1, 0), 0.3)
    x = -ent + 1.0
    while x < ent - 2.0:
        bw = rng.choice((0.3, 0.3, 0.6, 1.0))
        DK.box(x, -LOT - 3.2, 56.5, x + bw, -LOT - 3.0, 61.0)
        x += bw + rng.choice((0.5, 0.8))
    for k_ in (-24, -12, 0, 12, 24):
        chattri(A, k_, -LOT + 4.0, gh, 3.0, 7.0, 8.0)
    for sgn in (-1, 1):
        MB.box(sgn * ent - 1.0 * sgn - 1.5, -LOT - 3.0, 0.0, sgn * ent + 1.5 - 1.0 * sgn, -LOT - 2.0, 1.0)
        A["gold"].cyl_z(sgn * (ent - 4.0), -LOT + 4.0, gh + 8.0, gh + 18.0, 0.3, 6)
    # lit gate road: white strip down the axis into the garden
    # ---------------------------------------------------------------- the plinth
    px0, px1, py0, py1 = -58.0, 58.0, 25.0, 118.0
    ZT = 9.0
    SD.box(px0, py0, 0.0, px1, py1, 5.0)                       # red sandstone base (Humayun's Tomb)
    MB.box(px0 - 0.6, py0 - 0.6, 5.0, px1 + 0.6, py1 + 0.6, 5.8)
    MB.box(px0, py0, 5.8, px1, py1, ZT)
    MB.box(px0 - 1.0, py0 - 1.0, ZT, px1 + 1.0, py1 + 1.0, ZT + 0.9)  # coping
    # arcaded cells (pointed-arch niches, backlit) round the S and W (and E) faces
    nx_ = 14
    for i in range(nx_):
        xx = px0 + (px1 - px0) * (i + 0.5) / nx_
        if abs(xx) < 9.0:
            continue
        OR.prism(arch_poly(2.0, 2.2, 3.9, 0.3, 6), (xx, py0 - 0.05, 0.4), (1, 0, 0), (0, 0, 1), (0, -1, 0), 0.3)
    ny_ = 11
    for i in range(ny_):
        yy = py0 + (py1 - py0) * (i + 0.5) / ny_
        OR.prism(arch_poly(2.0, 2.2, 3.9, 0.3, 6), (px0 - 0.05, yy, 0.4), (0, -1, 0), (0, 0, 1), (-1, 0, 0), 0.3)
    # grand stair on the S face (to the terrace), orange-lit risers
    for k_ in range(8):
        MB.box(-9.0, py0 - 8.0 + k_ * 1.0, 0.0, 9.0, py0 - 7.0 + k_ * 1.0 + 0.0, 1.0 + k_ * 1.0)
        OR.box(-9.0, py0 - 8.0 + k_ * 1.0 - 0.1, 0.2 + k_ * 1.0, 9.0, py0 - 8.0 + k_ * 1.0, 0.5 + k_ * 1.0) if False else None
    # terrace barcode inlay: bands of shipping marks round the mausoleum and a hot-red and orange border
    cx, cy = 0.0, 72.0
    for ring_r, mat in ((44.0, "orange"), (45.2, "red")):
        A[mat].box(cx - ring_r, cy - ring_r, ZT + 0.9, cx + ring_r, cy - ring_r + 0.35, ZT + 1.05)
        A[mat].box(cx - ring_r, cy + ring_r - 0.35, ZT + 0.9, cx + ring_r, cy + ring_r, ZT + 1.05)
        A[mat].box(cx - ring_r, cy - ring_r, ZT + 0.9, cx - ring_r + 0.35, cy + ring_r, ZT + 1.05)
        A[mat].box(cx + ring_r - 0.35, cy - ring_r, ZT + 0.9, cx + ring_r, cy + ring_r, ZT + 1.05)
    for side in range(4):
        for k_ in range(60):
            bw = rng.choice((0.35, 0.35, 0.7, 1.1))
            off = -43.0 + k_ * 1.45
            if side == 0:
                DK.box(cx + off, cy - 41.5, ZT + 0.9, cx + off + bw, cy - 39.5, ZT + 1.1)
            elif side == 1:
                DK.box(cx - 41.5, cy + off, ZT + 0.9, cx - 39.5, cy + off + bw, ZT + 1.1)
            elif side == 2:
                DK.box(cx + off, cy + 39.5, ZT + 0.9, cx + off + bw, cy + 41.5, ZT + 1.1)
            else:
                DK.box(cx + 39.5, cy + off, ZT + 0.9, cx + 41.5, cy + off + bw, ZT + 1.1)
    # ---------------------------------------------------------------- the mausoleum (the target / the keep, inside the dome)
    z0 = ZT + 0.9
    hh, ch_ = 28.0, 8.0
    ph = 38.0
    poly = [(-hh + ch_, -hh), (hh - ch_, -hh), (hh, -hh + ch_), (hh, hh - ch_), (hh - ch_, hh), (-hh + ch_, hh), (-hh, hh - ch_), (-hh, -hh + ch_)]
    MB.prism(poly, (cx, cy, z0), (1, 0, 0), (0, 1, 0), (0, 0, 1), ph)
    MB.box(cx - hh - 0.8, cy - hh - 0.8, z0 + ph, cx + hh + 0.8, cy + hh + 0.8, z0 + ph + 1.4)
    # horizontal speed lines: three parallel bands round the building, orange / white / red
    ZB = z0 + ph - 5.0
    for ring_o, mat, th in ((0.3, "orange", 0.9), (0.2, "white", 0.35), (0.3, "red", 0.5)):
        pass
    for (zb_, mat, th) in ((z0 + 2.0, "orange", 0.5), (z0 + 3.2, "red", 0.35), (z0 + ph - 1.0, "orange", 0.6)):
        A[mat].prism([(p[0] * 1.012, p[1] * 1.012) for p in poly], (cx, cy, zb_), (1, 0, 0), (0, 1, 0), (0, 0, 1), th)
    # pishtaq on each face
    for n_, (fx, fy) in (((0, -1, 0), (0, -hh)), ((0, 1, 0), (0, hh)), ((-1, 0, 0), (-hh, 0)), ((1, 0, 0), (hh, 0))):
        pishtaq(A, cx + fx, cy + fy, z0 + 1.0, n_, 24.0, 34.0, rng)
        # two stacked flank niches either side
        u, nv = frame(n_)
        for sgn in (-1, 1):
            for zz in (z0 + 4.0, z0 + 19.0):
                o = Vector((cx + fx, cy + fy, zz)) + u * (sgn * 18.2)
                OR.prism(arch_poly(1.8, 5.5, 9.0, 0.0, 6), o, u, Vector((0, 0, 1)), nv, 0.3)
    # chamfered corner arches
    for sx in (-1, 1):
        for sy in (-1, 1):
            nn = Vector((sx, sy, 0)).normalized()
            u = Vector((-nn.y, nn.x, 0))
            o = Vector((cx + sx * (hh - ch_ / 2.0), cy + sy * (hh - ch_ / 2.0), z0 + 6.0)) + nn * 0.0
            for dz in (0.0, 15.0):
                OR.prism(arch_poly(2.4, 7.0, 12.0, 0.0, 6), o + Vector((0, 0, dz)), u, Vector((0, 0, 1)), nn, 0.3)
    # roof: four chattris, guldasta spires, drum, great onion dome, gilded finial
    zr = z0 + ph + 1.4
    for sx in (-1, 1):
        for sy in (-1, 1):
            chattri(A, cx + sx * 21.0, cy + sy * 21.0, zr, 3.0, 7.0, 8.0)
    MB.cyl_z(cx, cy, zr, zr + 14.0, 15.5, 40)
    MB.cyl_z(cx, cy, zr + 14.0, zr + 15.0, 17.0, 40)
    for j in range(24):
        a = 2 * math.pi * j / 24
        A["orange"].box(cx + 15.7 * math.cos(a) - 0.4, cy + 15.7 * math.sin(a) - 0.4, zr + 3.0, cx + 15.7 * math.cos(a) + 0.4, cy + 15.7 * math.sin(a) + 0.4, zr + 11.0)
    zd = zr + 15.0
    onion(GL, cx, cy, zd, 16.5, 40.0, 48)
    # lotus/rib lines on the dome (thin orange meridians fade into white marble)
    zf = zd + 40.0 * 0.96
    GD.cyl_z(cx, cy, zf - 2.0, zf + 5.0, 0.9, 10)
    GD.cyl_z(cx, cy, zf + 5.0, zf + 11.0, 0.35, 8)
    onion(GD, cx, cy, zf + 1.0, 2.2, 6.0, 12)
    OR.cyl_z(cx, cy, zf + 6.0, zf + 8.0, 1.6, 12)
    # crescent finial (a lit orange ring)
    for j in range(16):
        a0, a1 = 2 * math.pi * j / 16 * 0.78 + 0.5, 2 * math.pi * (j + 1) / 16 * 0.78 + 0.5
        OR.bar((cx, cy + 2.6 * math.cos(a0), zf + 11.5 + 2.6 * math.sin(a0)), (cx, cy + 2.6 * math.cos(a1), zf + 11.5 + 2.6 * math.sin(a1)), 0.4)
    # ---------------------------------------------------------------- four minarets (container cranes) at the plinth corners
    spots = ((-52.0, 31.0, math.radians(-100)), (52.0, 31.0, math.radians(-70)), (-52.0, 112.0, math.radians(-135)), (52.0, 112.0, math.radians(-30)))
    for (mx, my, jd) in spots:
        minaret(A, mx, my, ZT + 0.9, rng, jd)


def city(g, cfg, A):
    D.lacquer_facade(g["M_CITY"], gold=cfg.get("mull", (0.35, 0.50, 0.70)), dark=cfg.get("dark", 0.20), window_tint=cfg.get("win_tint", (0.70, 0.86, 1.0)),
                     band_emit=cfg.get("band_emit", 0.20), win_boost=cfg.get("win_boost", 2.6), mull_w=0.045, span_w=0.05, band_w=0.02)
    D.lacquer_panels(g["M_CIVIC"], gold=(0.2, 0.3, 0.42), dark=0.32, seam_gold=0.0)
    for k in ("M_METAL", "M_CMETAL"):
        if k in g:
            D.brass_metal(g[k], tint=(0.55, 0.60, 0.68), metal=1.0, rough=0.35)
    OBJ = g["OBJ"]
    for k in ("city_sign", "city_neon"):
        if OBJ.get(k) is not None:
            OBJ[k].hide_render = True
    cfg.setdefault("fog_col", (0.52, 0.64, 0.88))
    D.tune_fog(g, cfg)
    D.fog_veil(g, cfg)
    for ob, e0, grp in g["LIGHTS"]:
        if ob.name.startswith(("cityglow_", "bankglow_")):
            ob.data.color = cfg.get("glow_col", (0.50, 0.66, 0.95))


def apply_hq(g, cfg):
    if cfg.get("off"):
        return
    sc = bpy.context.scene
    coll = bpy.data.collections.new("mg")
    sc.collection.children.link(coll)
    M = materials()
    M["white"] = D.emission("mg_white", (1.0, 0.9, 0.75), 3.0)
    M["steel"] = D.principled("mg_hull", (0.04, 0.05, 0.07), 0.6, 0.3, coat=0.5)
    A = {k: S.SAcc("mg_" + k, m, coll) for k, m in M.items()}
    cut_castle(g)
    city(g, cfg, A)
    build(g, cfg, A)
    for a in A.values():
        a.build()
    # lights: white uplights wash the dome and minarets, orange wells in the iwans and the gate passage
    add = g["add_light"]
    for k, (x, y) in enumerate(((-40, 32), (40, 32), (-40, 110), (40, 110), (0, 28))):
        add("mg_up_%d" % k, "SPOT", (x, y, 10.5), cfg.get("up_w", 140000.0), (1.0, 0.92, 0.82), aim=(0.0, 72.0, 62.0), size=2.0, spot=38.0, blend=0.7,
            group="deco", shadow=False)
    for k, (x, y) in enumerate(((-52, 31), (52, 31), (-52, 112), (52, 112))):
        add("mg_min_%d" % k, "SPOT", (x * 1.0, y * 1.0 - 8.0, 10.5), cfg.get("min_w", 60000.0), (1.0, 0.9, 0.8), aim=(x, y, 70.0), size=1.0, spot=18.0, blend=0.7,
            group="deco", shadow=False)
    add("mg_gate", "AREA", (0.0, -105.0, 14.0), cfg.get("gate_w", 150000.0), (1.0, 0.45, 0.12), aim=(0.0, -60.0, 0.0), size=14.0, size_y=14.0, group="deco", shadow=False)
    add("mg_garden", "AREA", (0.0, -40.0, 60.0), cfg.get("garden_w", 250000.0), (0.85, 0.9, 1.0), aim=(0.0, -40.0, 0.0), size=90.0, size_y=90.0, group="deco", shadow=False)
    print("[mg] built", {k: len(a.f) for k, a in A.items()}, flush=True)
