"""Gritty E-style double-helix HQ (restyled from r2_helix_blender/scripts/helix_scene.py).

Two chunky, slightly wonky inhabitable strands (4 floors) wind 180 deg apart round a hollow core.
Hand-painted rust/grime paint (tt_lib.paint with grit), thick ink (Freestyle), patched panels,
riser pipes, cable bundles, window grids, balconies, rooftop shacks, a cyan and a magenta neon strip,
and 11 enclosed skybridges crossing the core at many heights (some tilted, patched or cable-hung,
some with lit windows).  Built directly in Blender world units (z up).  Seeded randomness only.
"""
import math
import random
import bmesh
import bpy
from mathutils import Vector, Matrix
import tt_lib as T

RI, RO = 1.9, 3.6
FL = 0.6
NFL = 4
TH = FL * NFL
PITCH = 12.0
TURNS = 2.0
Z0 = 0.6
SEG = 36


def M(h, **kw):
    return T.paint(h, **kw)


def _mesh(bm, name, mats, coll=None):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(o)
    for m in mats:
        me.materials.append(m)
    return o


class Helix:
    def __init__(self, cx, cy, entry, coll=None, seed=77):
        self.cx, self.cy, self.entry = cx, cy, entry
        self.coll = coll
        self.rng = random.Random(seed)
        self.objs = []

    # -------------------------------------------------------------- helpers
    def zb(self, t):
        return Z0 + PITCH * t / (2 * math.pi)

    def P(self, r, a, z):
        return Vector((self.cx + r * math.cos(a), self.cy + r * math.sin(a), z))

    def tan(self, a):
        return Vector((-math.sin(a), math.cos(a), 0.0))

    def link(self, o):
        if self.coll is not None:
            for c in list(o.users_collection):
                c.objects.unlink(o)
            self.coll.objects.link(o)
        self.objs.append(o)
        return o

    def band(self, r0, r1, z_off, thick, t0, t1, phase, name, mats, wob=0.0, mat_fn=None):
        rng = random.Random(name)
        bm = bmesh.new()
        n = max(2, int(abs(t1 - t0) / (2 * math.pi) * SEG))
        rings = []
        for i in range(n + 1):
            t = t0 + (t1 - t0) * i / n
            a = t + phase
            z = self.zb(t) + z_off
            d = rng.uniform(-wob, wob) + wob * 0.6 * math.sin(i * 1.7)
            dz = rng.uniform(-wob, wob) * 0.5
            rings.append([bm.verts.new(self.P(r0 + d * 0.5, a, z + dz)), bm.verts.new(self.P(r1 + d, a, z + dz)),
                          bm.verts.new(self.P(r1 + d, a, z + thick + dz)), bm.verts.new(self.P(r0 + d * 0.5, a, z + thick + dz))])
        for i in range(n):
            A, B = rings[i], rings[i + 1]
            for k in range(4):
                f = bm.faces.new((A[k], A[(k + 1) % 4], B[(k + 1) % 4], B[k]))
                if mat_fn:
                    f.material_index = mat_fn(i, k)
        bm.faces.new(rings[0][::-1])
        bm.faces.new(rings[-1])
        return self.link(_mesh(bm, name, mats))

    def boxes(self, parts, name, mats, bev=0.0):
        """parts: (center, x_axis, (sx, sy, sz), mat_idx[, tilt_deg]) boxes with z up (optional tilt about x)."""
        bm = bmesh.new()
        for p in parts:
            c, xa, s, mi = p[:4]
            tilt = math.radians(p[4]) if len(p) > 4 else 0.0
            xa = xa.normalized()
            za = Vector((0, 0, 1))
            ya = za.cross(xa).normalized()
            if tilt:
                q = Matrix.Rotation(tilt, 3, xa)
                ya, za = q @ ya, q @ za
            mt = Matrix((xa * s[0], ya * s[1], za * s[2])).transposed()
            r = bmesh.ops.create_cube(bm, size=1.0)
            for v in r["verts"]:
                v.co = c + mt @ v.co
            for f in {f for v in r["verts"] for f in v.link_faces}:
                f.material_index = mi
        o = self.link(_mesh(bm, name, mats))
        if bev:
            T.bevel(o, bev, 1)
        return o

    def cable(self, p0, p1, sag, col="#15161a", r=0.03):
        cu = bpy.data.curves.new("hcable", "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = r
        sp = cu.splines.new("POLY")
        n = 12
        sp.points.add(n - 1)
        for i in range(n):
            t = i / (n - 1)
            p = p0.lerp(p1, t)
            p.z -= sag * 4 * t * (1 - t)
            sp.points[i].co = (p.x, p.y, p.z, 1)
        o = bpy.data.objects.new("hcable", cu)
        bpy.context.scene.collection.objects.link(o)
        cu.materials.append(M(col))
        return self.link(o)

    # -------------------------------------------------------------- build
    def build(self, night=False):
        rng = self.rng
        T_END = TURNS * 2 * math.pi
        strands = (("#5a7488", "#3a4a58", "#3fd8f0", "A"), ("#74402e", "#4a2a22", "#ec4aa0", "B"))
        glass = M("#1e2a2e", gloss=0.5, stroke=0.1)
        lit = T.glow("#ffb45a", 1.8)
        lit2 = T.glow("#78eaff", 1.5)
        for s, (fam, roof, neon, nm) in enumerate(strands):
            ph = s * math.pi
            self.band(RI, RO, 0.0, TH, 0.0, T_END, ph, "hx" + nm,
                      [M(fam, streak_axis=2, streak=8, stroke=0.3, seed=s + 3), M(roof, stroke=0.25)],
                      wob=0.07, mat_fn=lambda i, k: 1 if k == 2 else 0)
            for f in range(1, NFL):
                self.band(RO - 0.04, RO + 0.2, f * FL - 0.04, 0.08, 0.0, T_END, ph, "hx%s_lip%d" % (nm, f),
                          [M("#8a8272", stroke=0.25)], wob=0.03)
            self.band(RO - 0.08, RO + 0.05, TH, 0.2, 0.0, T_END, ph, "hx%s_rail" % nm, [M("#3a3a3e", gloss=0.3)], wob=0.03)
            self.band(RO + 0.02, RO + 0.14, TH - 0.3, 0.13, 0.0, T_END, ph, "hx%s_neon" % nm,
                      [T.glow(neon, 3.4 if night else 2.4)])
            # windows
            parts = []
            n_out = int(T_END * RO / 0.5)
            for f in range(NFL):
                for i in range(n_out):
                    if rng.random() < 0.08:
                        continue
                    t = (i + 0.5) / n_out * T_END
                    a = t + ph
                    z = self.zb(t) + f * FL + FL * 0.52
                    r_ = rng.random()
                    mi = 1 if r_ < (0.3 if night else 0.14) else (2 if r_ < (0.4 if night else 0.2) else 0)
                    parts.append((self.P(RO + 0.02, a, z), self.tan(a), (0.28, 0.08, FL * 0.48), mi))
                n_in = int(T_END * RI / 0.55)
                for i in range(n_in):
                    t = (i + 0.5) / n_in * T_END
                    a = t + ph
                    z = self.zb(t) + f * FL + FL * 0.52
                    r_ = rng.random()
                    mi = 1 if r_ < 0.2 else (2 if r_ < 0.28 else 0)
                    parts.append((self.P(RI - 0.02, a, z), self.tan(a), (0.26, 0.08, FL * 0.48), mi))
            self.boxes(parts, "hx%s_win" % nm, [glass, lit, lit2])
            # balconies, patched panels, AC boxes on the outer face
            bal, patch = [], []
            for k in range(int(TURNS * 9)):
                t = (k + rng.uniform(0.1, 0.9)) / (TURNS * 9) * T_END
                a = t + ph
                f = rng.randint(1, NFL - 1)
                z = self.zb(t) + f * FL
                bal.append((self.P(RO + 0.38, a, z + 0.03), self.tan(a), (0.9, 0.5, 0.07), 0))
                bal.append((self.P(RO + 0.6, a, z + 0.22), self.tan(a), (0.9, 0.04, 0.32), 1))
            for k in range(int(TURNS * 14)):
                t = rng.uniform(0.1, T_END - 0.1)
                a = t + ph
                z = self.zb(t) + rng.uniform(0.2, TH - 0.6)
                w = rng.uniform(0.4, 0.9)
                patch.append((self.P(RO + 0.05, a, z), self.tan(a), (w, 0.07, rng.uniform(0.3, 0.6)), rng.randrange(3)))
                if rng.random() < 0.4:
                    patch.append((self.P(RO + 0.18, a + 0.1, z - 0.1), self.tan(a), (0.36, 0.3, 0.26), 3))
            self.boxes(bal, "hx%s_bal" % nm, [M("#8a8272"), M("#2e2e32", gloss=0.3)])
            self.boxes(patch, "hx%s_patch" % nm, [M("#6e5a44", stroke=0.35), M("#4e5a58", stroke=0.35),
                                                  M("#8a4a2a", stroke=0.35), M("#8e928c", gloss=0.2)])
            # riser pipes between turns on the outer face
            for k in range(3):
                a = rng.uniform(0, 2 * math.pi)
                t = (a - ph) % (2 * math.pi)
                for turn in range(int(TURNS)):
                    tt = t + turn * 2 * math.pi
                    if tt + math.pi > T_END:
                        break
                    z0 = self.zb(tt) + TH
                    z1 = self.zb(tt + 2 * math.pi)
                    if z1 - z0 < 0.4:
                        continue
                    o = T.cyl(0.07, z1 - z0, tuple(self.P(RO - 0.25, tt + ph, z0)), M("#7a4a32", gloss=0.2), verts=8,
                              bev=0)
                    self.link(o)
            # rooftop clutter: shack, AC units, antenna, dish
            t_top = T_END - 0.35
            a = t_top + ph
            zt = self.zb(t_top) + TH + 0.2
            mid = (RI + RO) / 2
            self.boxes([(self.P(mid, a, zt), self.tan(a), (1.2, 1.1, 0.8), 0),
                        (self.P(mid + 0.5, a - 0.45, zt), self.tan(a), (0.45, 0.4, 0.35), 1),
                        (self.P(mid - 0.4, a - 0.6, zt), self.tan(a), (0.45, 0.4, 0.35), 1),
                        (self.P(mid, a, zt + 0.8), self.tan(a), (1.45, 1.3, 0.08), 2, 6)],
                       "hx%s_roof" % nm, [M(fam, pattern="plank", stroke=0.3), M("#9a9a92", gloss=0.2),
                                          M("#5a5a52", gloss=0.3)], bev=0.04)
            ant = self.P(mid - 0.2, a + 0.12, zt)
            self.link(T.cyl(0.05, 2.4, tuple(ant), M("#3a3a3e"), verts=6, bev=0))
            self.link(T.cyl(0.12, 0.16, tuple(ant + Vector((0, 0, 2.4))), T.glow("#ff3a3a", 5), verts=8, bev=0))
            dish = T.cyl(0.42, 0.16, tuple(self.P(mid + 0.3, a + 0.3, zt + 0.35)), M("#b8b4a8", gloss=0.3), r2=0.1,
                         verts=14, bev=0.02, rot=(-40, 0, math.degrees(a)), origin_bottom=False)
            self.link(dish)
        # ---------------- skybridges: 11 across the hollow core, many heights
        conc = M("#8a8578", stroke=0.3, streak_axis=0)
        br_parts, br_win = [], []
        # Bridges sit where the view can see them: across the screen (bearing ~0/pi), two per gap
        # between the front turns (a point at the core centre shows ~RO*tan(el) higher than the front
        # face, so the visible window is the front gap shifted down by that).  The lower one of each
        # pair butts into the side bands; the upper one is cable-hung from the band above.  A few more
        # cross at other bearings deeper in the core.
        spots = []
        for k in range(int(TURNS * 2)):
            g0 = Z0 + 0.25 * PITCH + k * PITCH / 2 + TH - RO * 0.95
            spots.append((g0 + 0.15, rng.uniform(-0.12, 0.12), False))
            spots.append((g0 + 2.15, rng.uniform(-0.18, 0.18), True))
        for k in range(3):
            spots.append((Z0 + 3.0 + k * 6.5, rng.choice((0.7, -0.7, 2.4)), False))
        for i, (z, b, hung) in enumerate(spots):
            if z < 1.0 or z > Z0 + TURNS * PITCH + TH - 1.2:
                continue
            axis = Vector((math.cos(b), math.sin(b), 0))
            c = Vector((self.cx, self.cy, z))
            L = 2 * RI + 0.9
            tilt = rng.choice((0, 0, 0, 4, -5))
            hh = rng.uniform(0.9, 1.15)
            br_parts.append((c, axis, (L, 1.3, hh), rng.choice((0, 0, 1)), tilt))
            br_parts.append((c + Vector((0, 0, hh)), axis, (L + 0.1, 1.45, 0.1), 2, tilt))
            if rng.random() < 0.5:   # patch plate
                br_parts.append((c + axis * rng.uniform(-0.8, 0.8) + Vector((0, 0, 0.3)), axis, (0.5, 1.24, 0.4), 3, tilt))
            perp = Vector((0, 0, 1)).cross(axis).normalized()
            litb = rng.random() < 0.7
            for side in (-1, 1):
                for w in range(5):
                    off = -L / 2 + 0.6 + w * (L - 1.2) / 4
                    br_win.append((c + axis * off + perp * (0.66 * side) + Vector((0, 0, hh * 0.3)), axis,
                                   (0.34, 0.05, hh * 0.42), (1 if (w + i) % 2 else 2) if litb else 0, tilt))
            if hung or rng.random() < 0.2:  # cable-hung: stays up to the strand above
                for side in (-1, 1):
                    p0 = c + axis * (side * L / 2 * 0.7) + Vector((0, 0, hh))
                    self.cable(p0, p0 + Vector((0, 0, 2.2)) + axis * (side * 0.6), 0.05, r=0.025)
        self.boxes(br_parts, "hx_bridges", [conc, M("#4e5a58", stroke=0.3), M("#34343a"), M("#8a4a2a", stroke=0.35)],
                   bev=0.03)
        self.boxes(br_win, "hx_bridge_win", [M("#1e2a2e", gloss=0.4), T.glow("#9ff0ff", 1.4), T.glow("#ffc27a", 1.6)])
        # cable bundles slung between the strands' outer faces
        for k in range(5):
            a = rng.uniform(0, 2 * math.pi)
            z = rng.uniform(3, TURNS * PITCH - 2)
            p0 = self.P(RO + 0.1, a, z)
            p1 = self.P(RO + 0.1, a + rng.uniform(1.0, 2.0), z + rng.uniform(-1.5, 1.5))
            for j in range(3):
                o = Vector((0, 0, j * 0.08))
                self.cable(p0 + o, p1 + o, rng.uniform(0.5, 1.0), rng.choice(("#15161a", "#2a2020")), r=0.025)
        # ---------------- podium + entrance
        PR = RO + 0.9
        bm = bmesh.new()
        N = 22
        lo = [bm.verts.new(self.P(PR + self.rng.uniform(-0.06, 0.06), 2 * math.pi * i / N, 0.0)) for i in range(N)]
        hi = [bm.verts.new(self.P(PR, 2 * math.pi * i / N, Z0)) for i in range(N)]
        for i in range(N):
            j = (i + 1) % N
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
        bm.faces.new(hi)
        bm.faces.new(lo[::-1])
        pod = self.link(_mesh(bm, "hx_podium", [M("#6e695e", stroke=0.3, pattern="tiles")]))
        T.bevel(pod, 0.06, 1)
        ea = self.entry
        self.boxes([(self.P(RO + 0.25, ea, Z0), self.tan(ea), (1.8, 1.0, 1.35), 0),
                    (self.P(RO + 0.3, ea, Z0 + 1.35), self.tan(ea), (2.1, 1.25, 0.16), 1)], "hx_portal",
                   [M("#4a5866", stroke=0.25), M("#2a2c30")], bev=0.03)
        self.boxes([(self.P(RO + 0.77, ea, Z0), self.tan(ea), (1.0, 0.05, 1.05), 0)], "hx_door",
                   [T.glow("#3fd8f0", 2.8)])
        self.boxes([(self.P(PR + 0.2 + k * 0.25, ea, 0.0), self.tan(ea), (1.5, 0.26, Z0 - k * 0.2), 0) for k in range(3)],
                   "hx_steps", [M("#6e695e", stroke=0.25)])
        T.point(tuple(self.P(RO + 1.6, ea, Z0 + 0.8)), "#3fd8f0", 120, 0.6)
        return self.objs

    def top_z(self):
        return Z0 + TURNS * PITCH + TH + 2.6
