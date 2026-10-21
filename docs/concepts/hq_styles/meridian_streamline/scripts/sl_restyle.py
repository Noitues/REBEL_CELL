"""Meridian in Streamline Moderne / Machine-Age cyberpunk. Runs INSIDE Blender, hooked in front of the render section of the
base hq_scene.py (sl_blender_hq.py). Re-skins the Gatehouse Gantry (legs -> streamlined towers with speed bands and portholes,
span -> chrome-edged girder with speed lines, keep -> teardrop streamliner cab, train -> Loewy streamliner, walls -> triple
speed lines + hazard rim) and turns the city fill dark and cool. Reuses helpers of the art-deco pass (read only)."""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "art_deco", "scripts")))
import deco_restyle as D  # noqa: E402

CHROME = (0.78, 0.80, 0.84)
ENAMEL = (0.55, 0.58, 0.62)
STEEL = (0.05, 0.06, 0.075)
ORANGE = (1.0, 0.26, 0.01)
RED = (1.0, 0.03, 0.02)
CREAM = (1.0, 0.72, 0.40)
ICE = (0.60, 0.82, 1.0)


def sgnpow(v, e):
    return math.copysign(abs(v) ** e, v)


class SAcc(D.DAcc):
    def lathe(self, x0, x1, cy, cz, ry, rz, prof, n=28, pw=2.0):
        """Body of revolution (superellipse section) along x: prof = [(t, k)], t in 0..1 along x0..x1, k radius factor."""
        rings = []
        for t, k in prof:
            ring = []
            for j in range(n):
                a = 2 * math.pi * j / n
                ring.append((x0 + (x1 - x0) * t, cy + ry * k * sgnpow(math.cos(a), 2.0 / pw), cz + rz * k * sgnpow(math.sin(a), 2.0 / pw)))
            rings.append(ring)
        for r0, r1 in zip(rings, rings[1:]):
            for j in range(n):
                k2 = (j + 1) % n
                self.face([r0[j], r1[j], r1[k2], r0[k2]])
        self.face(rings[0][::-1])
        self.face(rings[-1])

    def cyl(self, p0, p1, r, n=10):
        p0, p1 = Vector(p0), Vector(p1)
        d = p1 - p0
        L = d.length
        if L < 1e-6:
            return
        d /= L
        ref = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
        a = d.cross(ref).normalized()
        b = d.cross(a).normalized()
        c = [p0 + (a * math.cos(2 * math.pi * i / n) + b * math.sin(2 * math.pi * i / n)) * r for i in range(n)]
        e = [q + d * L for q in c]
        self.face(c[::-1])
        self.face(e)
        for i in range(n):
            j = (i + 1) % n
            self.face([c[i], c[j], e[j], e[i]])

    def cyl_z(self, cx, cy, z0, z1, r, n=24):
        self.cyl((cx, cy, z0), (cx, cy, z1), r, n)

    def stadium(self, cx, cy, hx, hy, z0, z1, n=9):
        """Vertical stadium prism: half width hx (x), half length hy (y), round ends along y."""
        c = hy - hx
        pts = [(hx, -c), (hx, c)]
        for i in range(1, n):
            a = math.pi * i / n
            pts.append((hx * math.cos(a), c + hx * math.sin(a)))
        pts += [(-hx, c), (-hx, -c)]
        for i in range(1, n):
            a = math.pi + math.pi * i / n
            pts.append((hx * math.cos(a), -c + hx * math.sin(a)))
        self.prism(pts, (cx, cy, z0), (1, 0, 0), (0, 1, 0), (0, 0, 1), z1 - z0)

    def disc(self, o, nrm, r, t, n=12):
        nrm = Vector(nrm).normalized()
        u = Vector((-nrm.y, nrm.x, 0.0))
        if u.length < 1e-6:
            u = Vector((1, 0, 0))
        u.normalize()
        v = Vector((0, 0, 1)) if abs(nrm.z) < 0.9 else Vector((0, 1, 0))
        pts = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]
        self.prism(pts, Vector(o), u, v, nrm, t)


def mats():
    M = {}
    M["chrome"] = D.principled("sl_chrome", CHROME, 1.0, 0.20, emit=CHROME, emit_k=0.04)
    M["enamel"] = D.principled("sl_enamel", ENAMEL, 0.0, 0.25, coat=1.0, coat_rough=0.03, emit=ENAMEL, emit_k=0.02)
    M["steel"] = D.principled("sl_steel", STEEL, 0.6, 0.30, coat=0.5)
    M["orange"] = D.emission("sl_orange", ORANGE, 7.0)
    M["red"] = D.emission("sl_red", RED, 6.0)
    M["white"] = D.emission("sl_white", (1.0, 0.88, 0.70), 6.0)
    M["port"] = D.emission("sl_port", CREAM, 9.0)
    M["ice"] = D.emission("sl_ice", ICE, 4.0)
    M["hazard"] = D.emission("sl_hazard", ORANGE, 1.6)
    M["hull"] = D.principled("sl_hull", (0.62, 0.68, 0.78), 0.5, 0.18, coat=1.0, coat_rough=0.03, emit=(0.5, 0.6, 0.8), emit_k=0.35)
    M["glass"] = D.emission("sl_glassblock", (0.80, 0.90, 1.0), 2.4)
    M["train"] = D.principled("sl_train", (0.10, 0.12, 0.17), 0.3, 0.22, coat=1.0, coat_rough=0.03, emit=(0.10, 0.14, 0.2), emit_k=0.15)
    return M


def porthole_spots(cx, cy, hx, hy, z, pad=0.9, step=5.0, cap_n=5):
    """Candidate porthole positions + outward normals on a stadium tower at height z (camera-facing sides only)."""
    c = hy - hx
    out = []
    for sx in (-1, 1):
        y = -c + 3.0
        while y <= c - 3.0:
            out.append(((cx + sx * (hx + pad), cy + y, z), (sx, 0.0)))
            y += step
    for sy in (-1, 1):
        for i in range(cap_n):
            a = math.pi * (i + 0.5) / cap_n
            nx, ny = math.cos(a), sy * math.sin(a)
            out.append(((cx + nx * (hx + pad), cy + sy * c + ny * (hx + pad), z), (nx, ny)))
    cam = (-0.57, -0.82)
    return [(p, n) for p, n in out if n[0] * cam[0] + n[1] * cam[1] > 0.05]


def teardrop_prof(n=26):
    pts = []
    for i in range(n + 1):
        t = i / n
        if t < 0.35:                               # blunt bullet nose
            k = math.sqrt(max(0.0, 1.0 - ((0.35 - t) / 0.35) ** 2.2)) * 0.97 + 0.03
        else:                                      # long tail taper
            k = max(0.06, (1.0 - (t - 0.35) / 0.65) ** 1.35)
        pts.append((t, k))
    return pts


def train_prof(n=34):
    """Loewy nose (bullet, raked) over the whole set, mirrored at the rear."""
    pts = []
    for i in range(n + 1):
        t = i / n
        e = min(t, 1 - t)
        k = 1.0 if e > 0.07 else math.sqrt(max(0.0, 1 - ((0.07 - e) / 0.07) ** 1.8)) * 0.95 + 0.05
        pts.append((t, k))
    return pts


def build_gantry(g, cfg, A):
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
    CH, EN, OR, RD, WH, PT, ST, IC = (A[k] for k in ("chrome", "enamel", "orange", "red", "white", "port", "steel", "ice"))
    rng = random.Random(77)
    # -------------------------------------------------------- legs: streamlined towers
    top_shaft = ltop - 14.0
    for sx in (-1, 1):
        cx = sx * legx
        hx, hy = lhx + 0.9, lhy + 0.9
        ST.stadium(cx, gy, hx, hy, wtop, top_shaft)
        # chrome plinth + vertical chrome fins on the flat faces
        CH.stadium(cx, gy, hx + 0.9, hy + 0.9, wtop, wtop + 6.0)
        for fx in (-1, 1):
            for yy in (-9.0, 0.0, 9.0):
                CH.box(cx + fx * (hx + 0.2) - 0.35, gy + yy - 0.35, wtop + 6.0, cx + fx * (hx + 0.2) + 0.35, gy + yy + 0.35, top_shaft)
        # speed bands: three parallel horizontal rings, repeated up the shaft (white enamel / orange / red)
        for zb in (wtop + 16.0, wtop + 38.0, wtop + 60.0, wtop + 82.0, top_shaft - 6.0):
            EN.stadium(cx, gy, hx + 0.55, hy + 0.55, zb, zb + 1.6)
            OR.stadium(cx, gy, hx + 0.75, hy + 0.75, zb + 2.3, zb + 3.5)
            RD.stadium(cx, gy, hx + 0.65, hy + 0.65, zb + 4.2, zb + 4.9)
            WH.stadium(cx, gy, hx + 0.55, hy + 0.55, zb + 5.5, zb + 5.9)
        # lit glass-block pylons (light built into the structure) and ribbon window bands
        for fx in (-1, 1):
            for yy in (-13.5, -4.5, 4.5, 13.5):
                A['glass'].box(cx + fx * (hx + 0.35) - 0.3, gy + yy - 0.9, wtop + 8.0, cx + fx * (hx + 0.35) + 0.3, gy + yy + 0.9, top_shaft - 8.0)
        for zr in (wtop + 30.0, wtop + 52.0, wtop + 74.0):
            PT.stadium(cx, gy, hx + 0.3, hy + 0.3, zr, zr + 1.3)
        # clock face (Hoover intake towers) on the nose of the tower
        CH.disc((cx, gy - hy - 0.9, top_shaft - 8.0), (0, -1, 0), 3.6, 0.5, n=24)
        PT.disc((cx, gy - hy - 1.2, top_shaft - 8.0), (0, -1, 0), 3.0, 0.5, n=24)
        CH.bar((cx, gy - hy - 1.8, top_shaft - 8.0), (cx, gy - hy - 1.8, top_shaft - 5.6), 0.35)
        CH.bar((cx, gy - hy - 1.8, top_shaft - 8.0), (cx + 1.6, gy - hy - 1.8, top_shaft - 8.0), 0.35)
        # portholes in rows between the bands
        for zp in [wtop + 24.0 + 4.0 * i for i in range(0, 4)] + [wtop + 46.0 + 4.0 * i for i in range(0, 4)] + \
                  [wtop + 68.0 + 4.0 * i for i in range(0, 4)]:
            for (p, n) in porthole_spots(cx, gy, hx, hy, zp):
                CH.disc((p[0] - n[0] * 0.2, p[1] - n[1] * 0.2, p[2]), (n[0], n[1], 0), 1.25, 0.35)
                PT.disc((p[0], p[1], p[2]), (n[0], n[1], 0), 0.95, 0.5)
        # crown: three rounded setbacks (stadium, 82 %) with chrome copings, then a streamlined fin and a red beacon
        z = top_shaft
        s = 1.0
        for i in range(3):
            h = 4.6
            EN.stadium(cx, gy, (hx - 0.2) * s, (hy - 0.2) * s, z, z + h)
            CH.stadium(cx, gy, (hx + 0.6) * s, (hy + 0.6) * s, z + h - 0.9, z + h + 0.3)
            OR.stadium(cx, gy, (hx + 0.35) * s, (hy + 0.35) * s, z + 1.3, z + 1.9)
            RD.stadium(cx, gy, (hx + 0.35) * s, (hy + 0.35) * s, z + 2.4, z + 2.8)
            z += h
            s *= 0.82
        # aircraft-tail fins (Pan-Pacific Auditorium): three swept fins on the crown
        for fo, fh in ((0.0, 38.0), (-3.2, 26.0), (3.2, 26.0)):
            CH.prism([(-9.0, 0.0), (9.0, 0.0), (2.0, fh), (-0.6, fh)], (cx + fo - 0.3, gy, z), (0, 1, 0), (0, 0, 1), (1, 0, 0), 0.6)
            OR.prism([(-6.0, 4.0), (6.0, 4.0), (5.2, 5.2), (-5.2, 5.2)], (cx + fo - 0.5, gy, z), (0, 1, 0), (0, 0, 1), (1, 0, 0), 1.0)
        CH.stadium(cx, gy, 1.6, 6.0, z, z + 6.0)
        CH.cyl((cx, gy, z + 6.0), (cx, gy, z + 48.0), 0.45, 8)
        RD.cyl_z(cx, gy, z + 48.0, z + 49.8, 0.9, 10)
    # -------------------------------------------------------- the span: chrome-edged girder, speed lines, portholes
    xa, xb = -legx + lhx, legx - lhx
    for zz in (sz0 - 0.2, sz1 + 0.2):
        for yy in (gy - sh - 0.4, gy + sh + 0.4):
            CH.cyl((xa, yy, zz), (xb, yy, zz), 1.5, 12)
    for yy, sg in ((gy - sh - 0.55, -1), (gy + sh + 0.55, 1)):
        EN.box(xa, yy - 0.15 * sg, sz0 + 1.2, xb, yy + 0.35 * sg, sz0 + 3.0)
        for (zo, mat, th) in ((sz0 + 4.5, OR, 0.9), (sz0 + 6.4, RD, 0.5), (sz0 + 7.6, WH, 0.35)):
            mat.box(xa, min(yy, yy + 0.7 * sg), zo, xb, max(yy, yy + 0.7 * sg), zo + th)
        x = xa + 6.0
        while x < xb - 3.0:
            CH.disc((x, yy, sz0 + 13.2), (0, sg, 0), 1.6, 0.4)
            PT.disc((x, yy, sz0 + 13.2), (0, sg, 0), 1.2, 0.6)
            x += 7.0
        for xr in range(int(xa) + 12, int(xb), 24):
            CH.box(xr - 0.4, yy - 0.2 * sg, sz0, xr + 0.4, yy + 0.8 * sg, sz1)
    # promenade-deck catwalk rail and a row of masts with pennants along the span (ocean liner / flagpoles)
    for yy in (gy - sh + 1.0, gy + sh - 1.0):
        CH.cyl((xa, yy, sz1 + 3.6), (xb, yy, sz1 + 3.6), 0.35, 8)
        for xr in range(int(xa) + 3, int(xb), 8):
            CH.bar((xr, yy, sz1), (xr, yy, sz1 + 3.6), 0.3)
    for xr in range(int(xa) + 10, int(xb) - 4, 18):
        CH.cyl((xr, gy, sz1), (xr, gy, sz1 + 17.0), 0.3, 6)
        OR.box(xr, gy - 0.15, sz1 + 13.0, xr + 4.5, gy + 0.15, sz1 + 16.6)
    # -------------------------------------------------------- the keep: teardrop streamliner cab
    zc = (ktop + 122.0) / 2.0 + 1.0
    rz = (ktop - 122.0) / 2.0 + 1.2
    ry = khy + 3.0
    L0, L1 = kx - 26.0, kx + 34.0
    prof = teardrop_prof()
    A['hull'].lathe(L0, L1, gy, zc, ry, rz, prof, n=32, pw=2.4)
    # chrome nose cap + bands (speed lines) lengthwise on both sides, following the hull
    CH.lathe(L0 - 0.4, L0 + 6.0, gy, zc, ry * 0.98, rz * 0.98, [(0.0, 0.40), (0.15, 0.80), (0.5, 0.96), (1.0, 0.99)], n=32, pw=2.4)
    for sy in (-1, 1):
        for (al, mat, w) in ((18, OR, 0.75), (30, WH, 0.35), (42, RD, 0.55), (-8, OR, 0.5)):
            pts = []
            for i in range(0, 21):
                t = 0.06 + 0.88 * i / 20.0
                k = [kk for tt, kk in prof if tt >= t][0]
                a = math.radians(al)
                pts.append((L0 + (L1 - L0) * t, gy + sy * (ry * k * 1.012) * math.cos(a) ** 0.83, zc - rz * k * 1.012 * sgnpow(math.sin(a), 0.83)))
            for p0, p1 in zip(pts, pts[1:]):
                mat.bar(p0, p1, w)
        # cab portholes / windscreen band
        for i in range(7):
            t = 0.12 + i * 0.075
            k = [kk for tt, kk in prof if tt >= t][0]
            x = L0 + (L1 - L0) * t
            y = gy + sy * ry * k * 1.0
            CH.disc((x, y, zc + rz * k * 0.30), (0, sy, 0), 1.7, 0.3)
            PT.disc((x, y, zc + rz * k * 0.30), (0, sy, 0), 1.3, 0.55)
    # flying bridge on the nose (Coca-Cola plant): a rounded wheelhouse with a ribbon window and a rail
    EN.stadium(kx - 14.0, gy, 7.0, 9.0, ktop - 1.0, ktop + 4.5)
    PT.stadium(kx - 14.0, gy, 7.2, 9.2, ktop + 1.4, ktop + 2.8)
    CH.stadium(kx - 14.0, gy, 7.6, 9.6, ktop + 4.5, ktop + 5.2)
    # tail fin
    CH.box(L1 - 10.0, gy - 0.35, zc, L1 + 6.0, gy + 0.35, zc + rz + 8.0)
    RD.box(L1 + 1.5, gy - 0.4, zc + rz + 4.0, L1 + 6.2, gy + 0.4, zc + rz + 5.2)
    # dorsal ridge ring under the lantern + hanger struts down to the span
    CH.stadium(kx, gy, khx * 0.75, khy * 0.75, ktop + 0.4, ktop + 1.6)


def build_train(g, A):
    CP = g["CP"]
    RC = CP["rail"]
    ty = RC["y"][0]
    txa, txb = RC["train_x"]
    x0, x1 = txa - 20.5, txb + 20.5
    CH, EN, OR, RD, WH, PT = (A[k] for k in ("chrome", "enamel", "orange", "red", "white", "port"))
    zc, ry, rz = 4.9, 3.95, 4.15
    A["train"].lathe(x0, x1, ty, zc, ry, rz, train_prof(), n=24, pw=3.2)
    # chrome roof spine + skirt
    CH.cyl((x0 + 14, ty, zc + rz + 0.1), (x1 - 14, ty, zc + rz + 0.1), 0.45, 8)
    for sy in (-1, 1):
        yy = ty + sy * (ry + 0.08)
        for (zo, mat, th) in ((2.6, OR, 0.55), (3.5, WH, 0.22), (4.1, RD, 0.40)):
            mat.box(x0 + 12.0, min(yy, yy + 0.25 * sy), zo, x1 - 12.0, max(yy, yy + 0.25 * sy), zo + th)
        # nose speed lines sweeping onto the bullet
        for xe, s in ((x0, 1), (x1, -1)):
            for (zo, mat, th) in ((2.6, OR, 0.55), (4.1, RD, 0.4)):
                mat.box(min(xe + s * 1.5, xe + s * 12.0), min(yy, yy + 0.2 * sy), zo, max(xe + s * 1.5, xe + s * 12.0), max(yy, yy + 0.2 * sy), zo + th)
        x = x0 + 14.0
        while x < x1 - 12.0:
            PT.disc((x, yy, 6.3), (0, sy, 0), 0.8, 0.4, n=10)
            x += 2.6
        # car joints: chrome rings
    x = x0 + 12.0
    while x < x1 - 12.0:
        CH.box(x, ty - ry * 0.95, 1.1, x + 0.4, ty + ry * 0.95, zc + rz - 0.2)
        x += 22.8
    PT.disc((x0 + 1.4, ty, 4.2), (-1, 0, 0), 1.0, 0.5)
    PT.disc((x1 - 1.4, ty, 4.2), (1, 0, 0), 1.0, 0.5)


def build_walls(g, A):
    CP = g["CP"]
    lot, wt, nc, crs = CP["lot"], CP["wall"]["t"], CP["wall"]["courses"], CP["course"]
    wtop = nc * crs
    ew0, ew1 = CP["ew_y"]
    CH, OR, RD, WH, HZ = A["chrome"], A["orange"], A["red"], A["white"], A["hazard"]
    EN = A["enamel"]
    o = 0.35
    zb = (wtop - 17.0, wtop - 14.6, wtop - 12.8)
    for (a, b, fixed, axis) in ((-lot, lot, -lot - o, "y"), (ew0 + 1.0, ew1, -lot - o, "x")):
        for (z, mat, th) in ((zb[0], OR, 1.1), (zb[1], WH, 0.4), (zb[2], RD, 0.7)):
            if axis == "y":
                mat.box(a, fixed - 0.25, z, b, fixed + 0.25, z + th)
            else:
                mat.box(fixed - 0.25, a, z, fixed + 0.25, b, z + th)
    # hazard rim (slanted orange slabs) along the top of the W and S outer faces + chrome coping
    for (a, b, fixed, axis) in ((-lot, lot, -lot - o - 0.1, "y"), (ew0 + 1.0, ew1, -lot - o - 0.1, "x")):
        x = a
        while x < b - 4.0:
            poly = [(0, 0), (2.0, 0), (3.6, 2.8), (1.6, 2.8)]
            if axis == "y":
                A["hazard"].prism(poly, (x, fixed, wtop - 4.0), (1, 0, 0), (0, 0, 1), (0, -1, 0), 0.4)
            else:
                A["hazard"].prism(poly, (fixed, x, wtop - 4.0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), 0.4)
            x += 6.0
        if axis == "y":
            CH.cyl((a, fixed, wtop - 0.6), (b, fixed, wtop - 0.6), 0.8, 8)
        else:
            CH.cyl((fixed, a, wtop - 0.6), (fixed, b, wtop - 0.6), 0.8, 8)
    # S corner towers: rounded drum setbacks with a chrome dome, speed rings
    ch, ct = CP["corner"]["half"], CP["corner"]["h"]
    for sx in (-1, 1):
        cx, cy = sx * (lot - ch), -(lot - ch)
        for i, z in enumerate((ct - 16.0, ct - 13.2, ct - 11.4)):
            mat = (OR, WH, RD)[i]
            mat.box(cx - ch - 0.25, cy - ch - 0.25, z, cx + ch + 0.25, cy + ch + 0.25, z + (1.1, 0.4, 0.7)[i])
        zt = ct
        for r, h in ((13.4, 3.0), (11.2, 4.0), (8.6, 4.0), (6.0, 3.4)):
            EN.cyl_z(cx, cy, zt, zt + h, r, 28)
            CH.cyl_z(cx, cy, zt + h - 0.6, zt + h + 0.1, r + 0.6, 28)
            OR.cyl_z(cx, cy, zt + 1.0, zt + 1.6, r + 0.25, 28)
            RD.cyl_z(cx, cy, zt + 2.0, zt + 2.35, r + 0.25, 28)
            zt += h
        CH.lathe(cx - 4.2, cx + 4.2, cy, zt, 4.2, 3.4, [(0.0, 0.05), (0.2, 0.7), (0.5, 0.98), (0.8, 0.7), (1.0, 0.05)], n=20)
        CH.cyl((cx, cy, zt + 3.0), (cx, cy, zt + 14.0), 0.35, 8)
        RD.cyl_z(cx, cy, zt + 14.0, zt + 15.4, 0.8, 10)
        for (a, p) in enumerate(porthole_spots(cx, cy, ch, ch, ct - 6.0, pad=0.4, step=6.0)):
            pass
        for sgn in (-1, 1):
            for yy in (-6.0, 0.0, 6.0):
                for zq in (ct - 26.0, ct - 22.0):
                    n = (0.0, -1.0)
                    A["port"].disc((cx + yy, cy - ch - 0.25, zq), (0, -1, 0), 1.0, 0.3)
                    break
            break


def city(g, cfg, A, ctx):
    D.lacquer_facade(g["M_CITY"], gold=cfg.get("mull", (0.35, 0.50, 0.70)), dark=cfg.get("dark", 0.22), window_tint=cfg.get("win_tint", (0.70, 0.86, 1.0)),
                     band_emit=cfg.get("band_emit", 0.25), win_boost=cfg.get("win_boost", 3.0), mull_w=0.045, span_w=0.05, band_w=0.02)
    D.lacquer_panels(g["M_CIVIC"], gold=(0.2, 0.3, 0.42), dark=0.32, seam_gold=0.0)
    for k in ("M_METAL", "M_CMETAL"):
        if k in g:
            D.brass_metal(g[k], tint=(0.55, 0.60, 0.68), metal=1.0, rough=0.35)
    OBJ = g["OBJ"]
    for k in ("city_sign", "city_neon"):
        if OBJ.get(k) is not None:
            OBJ[k].hide_render = True
    D.tune_fog(g, cfg)
    D.fog_veil(g, cfg)
    fr = g["JOB"]["frames"][0]
    towers = D.select_towers(g, fr["pose"], cfg.get("n_towers", 70), cfg.get("min_top", 45.0), lm_box=cfg.get("lm_box", (0.0, 20.0, 125.0, 110.0, 150.0)),
                             min_cam_k=0.8)
    CH, EN, IC, ST = A["chrome"], A["enamel"], A["ice"], A["steel"]
    for k, (x, y, top, hx, hy, bi) in enumerate(towers):
        rr = random.Random(500 + bi)
        # modest rounded caps and one cool speed line: the fill stays dark
        r = min(hx, hy) * 0.86
        z = top
        for i in range(2):
            h = 3.0 + 3.0 * rr.random()
            ST.cyl_z(x, y, z, z + h, r, 20)
            CH.cyl_z(x, y, z + h - 0.35, z + h + 0.1, r + 0.3, 20)
            z += h
            r *= 0.7
    add = g["add_light"]
    for k, (x, y, top, hx, hy, bi) in enumerate(towers[:cfg.get("n_flood", 14)]):
        rr = random.Random(2000 + bi)
        a = rr.random() * math.tau
        d = max(hx, hy) + 9.0
        add("sl_flood_%d" % k, "SPOT", (x + math.cos(a) * d, y + math.sin(a) * d, 1.5), cfg.get("flood_w", 3500.0), (0.55, 0.75, 1.0),
            aim=(x, y, top * 0.75), size=1.5, spot=34.0, blend=0.55, group="deco", shadow=False)
    for ob, e0, grp in g["LIGHTS"]:
        if ob.name.startswith(("cityglow_", "bankglow_")):
            ob.data.color = cfg.get("glow_col", (0.50, 0.66, 0.95))


def apply_hq(g, cfg):
    if cfg.get("off"):
        return
    sc = bpy.context.scene
    coll = bpy.data.collections.new("sl")
    sc.collection.children.link(coll)
    M = mats()
    A = {k: SAcc("sl_" + k, m, coll) for k, m in M.items()}
    # the gantry's own base paint: dark enamel steel, rust-orange toned down toward machine paint
    m = bpy.data.materials.get("container")
    if m is not None:
        D.lacquer_panels(m, gold=(0.25, 0.3, 0.4), dark=0.35, seam_gold=0.0)
    city(g, cfg, A, {})
    build_gantry(g, cfg, A)
    build_train(g, A)
    build_walls(g, A)
    # lights: orange floods up the leg faces, white-ice wash on the keep, so chrome and enamel read
    add = g["add_light"]
    CP = g["CP"]
    lot = CP["lot"]
    gy = CP["gantry"]["y"]
    kx = CP["gantry"]["keep_x"]
    for sx in (-1, 1):
        add("sl_leg_%d" % sx, "SPOT", (sx * (lot - 7.0) - 40.0, gy - 70.0, 30.0), cfg.get("leg_w", 90000.0), (1.0, 0.55, 0.20),
            aim=(sx * (lot - 7.0), gy - 18.0, 90.0), size=3.0, spot=28.0, blend=0.6, group="deco", shadow=False)
    add("sl_keep", "SPOT", (kx - 90.0, gy - 80.0, 100.0), cfg.get("keep_w", 600000.0), (0.75, 0.88, 1.0), aim=(kx, gy, 135.0), size=3.0,
        spot=22.0, blend=0.6, group="deco", shadow=False)
    add("sl_train", "SPOT", (30.0, 40.0, 40.0), cfg.get("train_w", 70000.0), (1.0, 0.65, 0.35), aim=(30.0, 96.0, 4.0), size=3.0,
        spot=30.0, blend=0.6, group="deco", shadow=False)
    for k, a in A.items():
        a.build()
    print("[sl] built", {k: len(a.f) for k, a in A.items()}, flush=True)
