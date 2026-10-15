"""Aurelian Concord (roman): procedural Blender scenes. Run headless:

blender -b --factory-startup --python roman_scene.py -- shot="district" engine="eevee" res=[1280,720] out="D:/rc_scratch/new_corps/roman/district_prev"

shots: district (C), kit (C sheet), hq (D), street (F). Everything is placed by rules from the preset (roman_preset.py);
seeds are fixed. The anchors JSON carries projected room centres for the 2D overlay.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import nc_blend as B  # noqa: E402
import roman_preset as P  # noqa: E402

J = B.args()
SHOT = J.get("shot", "district")
PR = P.PRESET
C = {k: B.hexc(v) for k, v in PR["palette"].items()}


# ------------------------------------------------------------------ frames
class Frame:
    """Local facade frame: u along the facade, w into the building, z up."""

    def __init__(self, origin, rz):
        self.o = Vector(origin)
        self.rz = rz
        self.U = Vector((math.cos(rz), math.sin(rz), 0))
        self.W = Vector((-math.sin(rz), math.cos(rz), 0))

    def p(self, u, w, z):
        q = self.o + self.U * u + self.W * w
        return (q.x, q.y, self.o.z + z)


def mats():
    L = PR["light"]
    m = {
        "trav": B.mat_solid("trav", C["travertine"], 0.75, jitter=0.16),
        "trav_d": B.mat_solid("trav_d", tuple(c * 0.45 for c in C["travertine"][:3]) + (1,), 0.8, jitter=0.18),
        "marble": B.mat_solid("marble", C["marble"], 0.35, jitter=0.08),
        "porph": B.mat_solid("porph", C["porphyry"], 0.5, jitter=0.12),
        "bronze": B.mat_solid("bronze", C["bronze"], 0.38, metal=0.75, jitter=0.2),
        "gilt": B.mat_solid("gilt", C["gilt"], 0.3, metal=0.9, jitter=0.1),
        "dark": B.mat_solid("dark", (0.012, 0.011, 0.016, 1), 0.7, jitter=0.25),
        "road": B.mat_solid("road", (0.008, 0.008, 0.011, 1), 0.32, jitter=0.05, spec=0.6, wet=(0.05, 0.03)),
        "walk": B.mat_solid("walk", (0.05, 0.045, 0.04, 1), 0.45, jitter=0.2, wet=(0.09, 0.06)),
        "facade": facade_mat("facade", C["travertine"], L["win_warm"], 0.18),
        "facade_far": facade_mat("facade_far", (0.05, 0.05, 0.06, 1), L["win_cool"], 0.22),
        "e_verd": B.mat_emit("e_verd", C["verdigris"], L["neon"]),
        "e_verd_hi": B.mat_emit("e_verd_hi", C["verdigris"], L["neon"] * 2.5),
        "e_warm": B.mat_emit("e_warm", B.hexc("#FFB46A"), L["shop"]),
        "e_pink": B.mat_emit("e_pink", B.hexc("#FF4FB0"), L["neon"]),
        "e_cyan": B.mat_emit("e_cyan", B.hexc("#62D8FF"), L["neon"]),
        "e_amber": B.mat_emit("e_amber", B.hexc("#FFB23A"), L["neon"]),
        "e_white": B.mat_emit("e_white", (1, 0.95, 0.88, 1), L["shop"] * 1.4),
        "e_red": B.mat_emit("e_red", B.hexc("#FF2030"), L["neon"] * 1.4),
        "e_tail": B.mat_emit("e_tail", B.hexc("#FF2A2A"), L["streak"]),
        "e_head": B.mat_emit("e_head", (1, 0.92, 0.8, 1), L["streak"] * 1.3),
        "e_win": B.mat_emit("e_win", B.hexc("#FFC98A"), L["window"]),
        "e_wind": B.mat_emit("e_wind", B.hexc("#4A6C88"), L["window"] * 0.08),
        "e_room": B.mat_emit("e_room", B.hexc("#FFE2B0"), L["room"]),
        "e_room_c": B.mat_emit("e_room_c", B.hexc("#9CF5D8"), L["room"]),
        "e_holo": B.mat_emit("e_holo", C["verdigris"], L["neon"] * 0.7, alpha=0.55),
        "e_holo_p": B.mat_emit("e_holo_p", B.hexc("#FF4FB0"), L["neon"] * 0.7, alpha=0.55),
        "e_gate": B.mat_emit("e_gate", C["verdigris"], L["neon"] * 3.0),
        "e_lock": B.mat_emit("e_lock", B.hexc("#FF2030"), L["neon"] * 2.2),
        "e_core": B.mat_emit("e_core", B.hexc("#E8FFF6"), L["neon"] * 4.0),
    }
    return m


def facade_mat(name, base, wrgb, lit):
    """Procedural window grid on any axis-aligned facade (u = x + y), lit by a seeded noise."""
    m = bpy.data.materials.new(name)
    nt = B._nodes(m)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(p.outputs[0], out.inputs[0])
    nt.links.new(B._jitter(nt, base, 0.18), p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.8
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])

    def M(op, a, b=None, v=None):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        nt.links.new(a, n.inputs[0]) if not isinstance(a, float) else n.inputs[0].__setattr__("default_value", a)
        if b is not None:
            if isinstance(b, float):
                n.inputs[1].default_value = b
            else:
                nt.links.new(b, n.inputs[1])
        return n.outputs[0]
    u = M("ADD", sep.outputs["X"], sep.outputs["Y"])
    fu = M("FRACT", M("DIVIDE", u, 3.2))
    fz = M("FRACT", M("DIVIDE", sep.outputs["Z"], 4.2))
    wu = M("LESS_THAN", fu, 0.55)
    wz = M("MULTIPLY", M("GREATER_THAN", fz, 0.25), M("LESS_THAN", fz, 0.78))
    cell = M("MULTIPLY", wu, wz)
    # per-window random (cell id hashed through a white noise)
    idu = M("FLOOR", M("DIVIDE", u, 3.2))
    idz = M("FLOOR", M("DIVIDE", sep.outputs["Z"], 4.2))
    cmb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(idu, cmb.inputs[0])
    nt.links.new(idz, cmb.inputs[1])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "3D"
    nt.links.new(cmb.outputs[0], wn.inputs["Vector"])
    on = M("LESS_THAN", wn.outputs["Value"], lit)
    em = M("MULTIPLY", cell, on)
    p.inputs["Emission Color"].default_value = wrgb
    nt.links.new(M("MULTIPLY", em, PR["light"]["window"] * 0.8), p.inputs["Emission Strength"])
    B._M[name] = m
    return m


# ------------------------------------------------------------------ the kit
def column(g, f, u, w, z, h, r=0.5, key="marble"):
    x, y, zz = f.p(u, w, z)
    g.box(key, f.p(u, w, z + 0.3), (r * 2.6, r * 2.6, 0.6), f.rz)
    g.cyl(key, (x, y, zz + 0.6), r, h - 1.4, n=8, r2=r * 0.86)
    g.box(key, f.p(u, w, z + h - 0.4), (r * 2.8, r * 2.8, 0.8), f.rz)


def arch_outline(w, h, spring):
    """Outline of a round-headed opening, width w, top at h, springline at spring (u centred)."""
    pts = [(-w / 2, 0.0)]
    n = 10
    r = w / 2
    for k in range(n + 1):
        a = math.pi - math.pi * k / n
        pts.append((r * math.cos(a), spring + r * math.sin(a)))
    pts.append((w / 2, 0.0))
    return pts


def spandrel(g, f, u0, u1, z0, z1, ow, spring, depth, key):
    """The wall of one arch bay with its opening cut: a prism of the bay minus the arch (as two side prisms + a crown)."""
    uc = (u0 + u1) / 2
    r = ow / 2
    # left and right piers
    g.prism(key, [(u0, z0), (uc - r, z0), (uc - r, z1), (u0, z1)], depth, f.p(0, 0, 0), f.rz)
    g.prism(key, [(uc + r, z0), (u1, z0), (u1, z1), (uc + r, z1)], depth, f.p(0, 0, 0), f.rz)
    # crown: from the arch curve up to z1
    pts = [(uc - r, z1)]
    n = 8
    for k in range(n + 1):
        a = math.pi - math.pi * k / n
        pts.append((uc + r * math.cos(a), z0 + spring + r * math.sin(a)))
    pts.append((uc + r, z1))
    g.prism(key, list(reversed(pts)), depth, f.p(0, 0, 0), f.rz)


def window_arch(g, f, u, z, w, h, key, inset=-0.05):
    pts = arch_outline(w, h, h - w / 2)
    pts = [(u + a, z + b) for a, b in pts]
    g.prism(key, pts, 0.08, f.p(0, inset, 0), f.rz)


UPL = []   # rule-placed uplights: (from, to, kind) collected while building, created after the geometry


def statue(g, f, u, w, z, s, rng, pose=0):
    """A rooftop statue (bronze gone verdigris): plinth, legs, toga cone, torso, head, one raised arm."""
    g.box("marble", f.p(u, w, z + 1.2 * s), (3.2 * s, 3.2 * s, 2.4 * s), f.rz)
    x, y, zz = f.p(u, w, z + 2.4 * s)
    UPL.append((f.p(u, w - 3.5 * s, z + 2.6 * s), (x, y, zz + 5.0 * s), "statue", s))
    g.cyl("bronze", (x, y, zz), 1.15 * s, 4.6 * s, n=7, r2=0.7 * s)               # toga
    g.cyl("bronze", (x, y, zz + 4.6 * s), 0.75 * s, 1.8 * s, n=6, r2=0.9 * s)     # chest
    g.sphere("bronze", (x, y, zz + 7.0 * s), 0.6 * s, n=7, rings=5)               # head
    side = 1 if pose % 2 == 0 else -1
    sh = Vector(f.p(u + side * 0.8 * s, w, z + 2.4 * s + 6.0 * s))
    up = Vector(f.p(u + side * 1.6 * s, w - 0.6 * s, z + 2.4 * s + 9.0 * s))
    g.tube("bronze", [tuple(sh), tuple(up)], 0.28 * s, n=5)
    if pose % 3 == 0:                                                             # a laurel ring held up: neon
        g.cyl("e_verd_hi", tuple(up + Vector((0, 0, 0.3 * s))), 0.9 * s, 0.25 * s, n=10, cap=False)
    else:                                                                         # a torch
        g.cyl("e_amber", tuple(up), 0.25 * s, 0.9 * s, n=5)
    return Vector((x, y, zz))


def insula(g, f, width, depth, floors, rng, near=True, top="auto", trims=True, neon="e_verd"):
    """The ordinary block: colonnaded ground floor, arched windows, cornices with neon trim, a roof dressing."""
    st = PR["kit"]["storey"]
    gh = PR["kit"]["ground_h"]
    H = gh + floors * st
    # mass behind the portico
    g.box("facade" if near else "facade_far", f.p(width / 2, depth / 2, gh + floors * st / 2), (width, depth, floors * st), f.rz)
    g.box("dark", f.p(width / 2, depth / 2 + 3, gh / 2), (width, depth - 6, gh), f.rz)
    if near:
        # portico: columns + entablature + lit shop fronts behind
        n = max(2, int(width / PR["kit"]["col_pitch"]))
        for k in range(n + 1):
            column(g, f, k * width / n, 0.6, 0, gh - 0.8)
        g.box("trav", f.p(width / 2, 1.4, gh - 0.4), (width + 0.6, 3.4, 0.8), f.rz)
        g.box("trav", f.p(width / 2, 0.0, gh + 0.25), (width + 1.0, 1.0, 0.5), f.rz)
        for k in range(n):
            if rng.random() < 0.8:
                key = rng.choice(["e_warm", "e_warm", "e_white", "e_cyan", "e_pink"])
                uc = (k + 0.5) * width / n
                g.quad(key, [f.p(uc - 1.4, 3.0, 0.3), f.p(uc + 1.4, 3.0, 0.3), f.p(uc + 1.4, 3.0, 3.4), f.p(uc - 1.4, 3.0, 3.4)])
        # arched windows in front of the procedural grid on the lower floors
        bays = max(2, int(width / 3.6))
        for fl in range(min(floors, 4)):
            for b in range(bays):
                uc = (b + 0.5) * width / bays
                lit = rng.random() < PR["kit"]["lit_p"]
                window_arch(g, f, uc, gh + fl * st + 0.7, 1.7, 2.9, "e_win" if lit else "e_wind", inset=-0.06)
    # cornices with trims
    zc = gh
    every = rng.choice([3, 4])
    for fl in range(0, floors + 1, every):
        z = gh + fl * st
        g.box("trav", f.p(width / 2, -0.4, z), (width + 1.2, 1.2, 0.6), f.rz)
        if trims and rng.random() < 0.7:
            g.box(neon, f.p(width / 2, -1.02, z + 0.05), (width + 1.0, 0.08, 0.14), f.rz)
    g.box("trav", f.p(width / 2, depth / 2 - 0.6, H + 0.4), (width + 1.4, depth + 1.4, 0.8), f.rz)
    if trims:
        g.box(neon, f.p(width / 2, -1.12, H + 0.5), (width + 1.2, 0.1, 0.16), f.rz)
    if top == "auto":
        top = rng.choice(["pediment", "statue", "statue", "plain", "crown"])
    if top == "pediment":
        g.prism("trav", [(0, H + 0.8), (width, H + 0.8), (width / 2, H + 0.8 + width * 0.22)], -2.0, f.p(0, 2.5, 0), f.rz)
        apex = Vector(f.p(width / 2, 0.38, H + 0.8 + width * 0.22 + 0.2))
        for end in (f.p(-0.2, 0.38, H + 1.0), f.p(width + 0.2, 0.38, H + 1.0)):
            g.tube(neon, [end, tuple(apex)], 0.09, n=4)
        g.box("gilt", tuple(apex + Vector((0, 0, 0.8))), (0.9, 0.9, 1.6), f.rz)
    elif top == "statue":
        s = rng.uniform(1.6, 2.4)
        statue(g, f, width * rng.uniform(0.3, 0.7), depth * 0.3, H + 0.8, s, rng, pose=rng.randint(0, 5))
    elif top == "crown":
        g.box("trav", f.p(width / 2, depth / 2, H + 3), (width * 0.6, depth * 0.6, 4.4), f.rz)
        g.box(neon, f.p(width / 2, depth * 0.2 - 0.08, H + 5.1), (width * 0.6, 0.1, 0.18), f.rz)
    return H


def arcade_tower(g, f, width, depth, H, rng, neon="e_verd", key="facade_far"):
    """A tall tower in stacked arcade tiers with setbacks, a crown ring and a beacon."""
    tiers = rng.randint(3, 5)
    z = 0.0
    w, d = width, depth
    for t in range(tiers):
        h = H / tiers
        g.box(key, f.p(width / 2, depth / 2, z + h / 2), (w, d, h), f.rz)
        # a band of tall arched openings on the facade (big lit arches)
        bays = max(2, int(w / 7))
        for b in range(bays):
            uc = width / 2 - w / 2 + (b + 0.5) * w / bays
            window_arch(g, f, uc, z + h * 0.62, min(4.0, w / bays * 0.6), h * 0.3,
                        rng.choice(["e_win", "e_wind", "e_wind", neon]), inset=depth / 2 - d / 2 - 0.08)
        g.box("trav", f.p(width / 2, depth / 2, z + h), (w + 1.0, d + 1.0, 0.8), f.rz)
        g.box(neon, f.p(width / 2, depth / 2 - d / 2 - 0.55, z + h + 0.1), (w + 0.8, 0.1, 0.16), f.rz)
        z += h
        w *= 0.82
        d *= 0.82
    x, y, _ = f.p(width / 2, depth / 2, 0)
    g.cyl("trav", (x, y, z), min(w, d) * 0.45, 6, n=12)
    g.cyl(neon, (x, y, z + 6), min(w, d) * 0.47, 0.4, n=16, cap=False)
    g.box("e_red", (x, y, z + 9), (0.6, 0.6, 0.6))
    return z + 9


def basilica(g, f, width, rng):
    """Domed drum on a podium (a bank, a bath, a senate hall)."""
    x, y, _ = f.p(width / 2, width / 2, 0)
    g.box("trav", (x, y, 6), (width, width, 12), f.rz)
    for k in range(8):
        column(g, f, width * (k + 0.5) / 8, -0.6, 0, 11.4, r=0.55)
    g.cyl("trav", (x, y, 12), width * 0.38, 8, n=16)
    g.dome("marble", (x, y, 20), width * 0.38, n=16, rings=6)
    g.cyl("e_verd", (x, y, 20), width * 0.39, 0.35, n=24, cap=False)
    g.cyl("gilt", (x, y, 20 + width * 0.38), 1.2, 3.2, n=6)


def aqueduct(g, y, x0, x1, z_top, rng, pitch=12.0):
    """Two tiers of arches across the street; the channel on top carries the lit data stream."""
    f = Frame((x0, y, 0), 0.0)
    L = x1 - x0
    n = int(L / pitch)
    t1 = z_top * 0.55
    for k in range(n):
        u0, u1 = k * pitch, (k + 1) * pitch
        spandrel(g, f, u0, u1, 0, t1, pitch * 0.62, t1 * 0.6, 4.0, "trav")
        spandrel(g, f, u0, u1, t1, z_top - 2.4, pitch * 0.5, (z_top - 2.4 - t1) * 0.45, 3.4, "trav")
    g.box("trav", f.p(L / 2, 1.7, z_top - 1.2), (L, 4.4, 2.4), 0.0)
    g.box("trav_d", f.p(L / 2, 1.7, z_top + 0.4), (L, 4.4, 0.8), 0.0)
    g.box("e_verd", f.p(L / 2, 1.7, z_top + 0.9), (L, 1.8, 0.25), 0.0)            # the data stream
    rr = random.Random(PR["seeds"]["packets"])
    u = 0.0
    while u < L:
        u += rr.uniform(4, 14)
        g.box("e_core", f.p(u, 1.7, z_top + 1.05), (rr.uniform(1.0, 2.6), 1.9, 0.3), 0.0)
    for side in (-0.4, 3.8):
        g.box("e_verd", f.p(L / 2, side, z_top - 2.5), (L, 0.08, 0.14), 0.0)
    for k in range(0, n, 2):                                   # warm uplights wash every other pier
        UPL.append((f.p(k * pitch, -6.0, 0.6), f.p(k * pitch, 1.0, z_top * 0.7), "pier", 1.0))
    return f


def campanile(g, cx, cy, r, levels, rng, neon="e_verd"):
    """A round campanile (upright, never leaning): a solid base drum, stacked arcaded galleries (a ring of columns round
    each level's lit core, a cornice slab with a neon line), a belfry of open arches and a conical roof."""
    z = 0.0
    g.cyl("trav", (cx, cy, 0), r * 1.06, 10.0, n=24)                       # base drum
    g.cyl("trav_d", (cx, cy, 10.0), r * 1.12, 0.9, n=24)
    z = 10.9
    lh = PR["kit"]["campanile_level"]
    ncol = int(PR["kit"]["campanile_cols"])
    for lv in range(levels):
        g.cyl("facade", (cx, cy, z), r * 0.72, lh, n=20)                   # the lit core
        for k in range(ncol):                                               # the gallery's ring of columns
            a = 2 * math.pi * (k + 0.5 * (lv % 2)) / ncol
            x, y = cx + r * 0.94 * math.cos(a), cy + r * 0.94 * math.sin(a)
            g.cyl("marble", (x, y, z), 0.42, lh - 0.9, n=6)
            if rng.random() < 0.35:                                         # a warm lamp behind some arches
                g.box("e_win", (cx + r * 0.73 * math.cos(a), cy + r * 0.73 * math.sin(a), z + lh * 0.45), (0.9, 0.9, lh * 0.5), a)
        g.cyl("trav", (cx, cy, z + lh - 0.9), r * 1.04, 0.9, n=24)          # cornice
        g.cyl(neon, (cx, cy, z + lh - 0.95), r * 1.06, 0.18, n=32, cap=False)
        z += lh
    # belfry: tall open arches round a dark bell chamber, a gilt bell
    g.cyl("dark", (cx, cy, z), r * 0.6, lh * 1.5, n=16)
    for k in range(8):
        a = 2 * math.pi * k / 8
        g.box("trav", (cx + r * 0.92 * math.cos(a), cy + r * 0.92 * math.sin(a), z + lh * 0.75), (1.4, 1.4, lh * 1.5), a)
    g.cyl("gilt", (cx, cy, z + lh * 0.3), r * 0.25, lh * 0.7, n=10, r2=r * 0.12)
    g.cyl("e_amber", (cx, cy, z + lh * 0.2), r * 0.3, 0.3, n=12)
    z += lh * 1.5
    # the crown: flat, like Pisa's top: a cornice slab, a flat roof, a low parapet ring, the neon trim ring
    g.cyl("trav", (cx, cy, z), r * 1.08, 1.0, n=24)                         # cornice
    g.cyl("trav_d", (cx, cy, z + 1.0), r * 1.0, 0.4, n=24)                  # flat roof
    g.ring("trav", (cx, cy, z + 1.0), r * 0.92, r * 1.06, 1.3, n=32)        # low parapet
    g.ring("e_verd_hi", (cx, cy, z + 2.2), r * 1.05, r * 1.1, 0.2, n=40)    # neon trim ring
    g.box("e_red", (cx + r * 0.8, cy, z + 2.7), (0.6, 0.6, 0.6))            # one aviation light on the parapet
    UPL.append(((cx, cy - r * 2.6, 0.6), (cx, cy, z * 0.6), "arch", 1.4))
    return z + 2.4


def piazza(g, cx, cy, size, rng):
    """An open paved square: a travertine / marble paving grid, a fountain (basin, a three-figure statue group back to
    back, lit water jets), a neon line round the basin, benches and lamp posts, low colonnaded blocks on two sides."""
    n = 8
    t = size / n
    for i in range(n):
        for j in range(n):
            key = "marble" if (i + j) % 2 else "walk"
            g.box(key, (cx - size / 2 + (i + 0.5) * t, cy - size / 2 + (j + 0.5) * t, -0.05), (t - 0.25, t - 0.25, 0.3))
    g.ring("trav", (cx, cy, 0), 7.0, 8.4, 1.4, n=40)                       # the basin
    g.cyl("e_holo", (cx, cy, 0.1), 7.0, 0.9, n=40)                         # lit water surface
    g.ring("e_verd_hi", (cx, cy, 1.4), 8.3, 8.5, 0.18, n=48)
    g.cyl("trav", (cx, cy, 0), 2.2, 3.4, n=12)                             # the plinth
    for k in range(3):                                                      # the statue group, back to back
        a = 2 * math.pi * k / 3
        statue(g, Frame((cx + 1.4 * math.cos(a), cy + 1.4 * math.sin(a), 0), a + math.pi / 2), 0, 0, 3.4, 1.15, rng, pose=k)
    for k in range(6):                                                      # water jets (emissive arcs)
        a = 2 * math.pi * (k + 0.5) / 6
        p0 = (cx + 2.6 * math.cos(a), cy + 2.6 * math.sin(a), 1.0)
        pm = (cx + 4.6 * math.cos(a), cy + 4.6 * math.sin(a), 4.2)
        p1 = (cx + 6.4 * math.cos(a), cy + 6.4 * math.sin(a), 1.0)
        g.tube("e_white", [p0, pm, p1], 0.12, n=4)
    for k in range(8):                                                      # lamps and benches round the edge
        a = 2 * math.pi * k / 8
        x, y = cx + size * 0.4 * math.cos(a), cy + size * 0.4 * math.sin(a)
        g.cyl("bronze", (x, y, 0), 0.18, 5.0, n=6)
        g.sphere("e_amber", (x, y, 5.2), 0.45, n=6, rings=4)
        g.box("trav", (cx + size * 0.3 * math.cos(a), cy + size * 0.3 * math.sin(a), 0.4), (2.6, 0.8, 0.8), a + math.pi / 2)
    # low colonnaded blocks framing two sides of the square
    insula(g, Frame((cx - size / 2, cy + size / 2 + 1, 0), 0.0), size, 12, 2, rng, near=True, top="plain")
    insula(g, Frame((cx - size / 2 - 1, cy - size / 2, 0), math.pi / 2), size, 12, 2, rng, near=True, top="plain")
    UPL.append(((cx, cy - size * 0.45, 0.4), (cx, cy, 6.0), "arch", 1.0))


def triumph_arch(g, y, width, height, rng, text_mat, x=0.0):
    f = Frame((x - width / 2, y, 0), 0.0)
    depth = 9.0
    ow = width * 0.42
    spandrel(g, f, 0, width, 0, height * 0.72, ow, height * 0.36, depth, "trav")
    for u0 in (0.0, width - width * 0.18):                                         # side arches (pedestrian)
        pass
    g.box("trav", f.p(width / 2, depth / 2, height * 0.72 + height * 0.14), (width + 2, depth + 1, height * 0.28), 0.0)   # attic
    g.box("porph", f.p(width / 2, -0.15, height * 0.86), (width * 0.7, 0.3, height * 0.16), 0.0)
    for u in (width * 0.08, width * 0.2, width * 0.8, width * 0.92):
        column(g, f, u, -1.0, 0, height * 0.7, r=0.75)
    g.box("e_verd_hi", f.p(width / 2, -1.6, height * 0.72 + 0.2), (ow + 1.0, 0.12, 0.25), 0.0)
    # quadriga stand-in: the big statue on top + a laurel ring holo
    s = 3.4
    c = statue(g, f, width / 2, depth / 2, height, s, rng, pose=0)
    g.cyl("e_holo", (c.x, c.y - 1, c.z + 12 * 0.5), 9.0, 0.6, n=28, cap=False)
    x, yy, _ = f.p(width / 2, -0.4, 0)
    B.text_obj(PR["signs"]["arch"], (x, yy - 0.2, height * 0.83), height * 0.085, text_mat)
    for u in (width * 0.12, width * 0.88):
        UPL.append((f.p(u, -10.0, 0.6), f.p(u, 0.0, height * 0.7), "arch", 2.0))
    return f


def room_cut(g, f, u, z, rw, rh, rd, key, frame="trav"):
    """A route room drawn as a cutaway: an open box standing proud of the wall (floor, side walls, ceiling), its lit
    back wall, two prop silhouettes and a stone frame. Front faces the camera side of the facade (w < 0)."""
    t = 0.5
    g.box("dark", f.p(u, -rd / 2, z + 0.25), (rw, rd, 0.5), f.rz)                  # floor
    g.box("dark", f.p(u, -rd / 2, z + rh), (rw, rd, 0.5), f.rz)                    # ceiling
    for s in (-1, 1):
        g.box("dark", f.p(u + s * rw / 2, -rd / 2, z + rh / 2), (t, rd, rh), f.rz)    # side walls
    g.quad(key, [f.p(u - rw / 2, -0.05, z + 0.5), f.p(u + rw / 2, -0.05, z + 0.5), f.p(u + rw / 2, -0.05, z + rh - 0.2),
                 f.p(u - rw / 2, -0.05, z + rh - 0.2)])
    g.box("dark", f.p(u - rw * 0.22, -rd * 0.45, z + 1.4), (rw * 0.22, 1.4, 2.0), f.rz)
    g.box("dark", f.p(u + rw * 0.25, -rd * 0.35, z + 1.0), (rw * 0.3, 1.2, 1.2), f.rz)
    g.box(frame, f.p(u, -rd - 0.2, z + rh + 0.5), (rw + 1.4, 0.6, 0.9), f.rz)       # lintel
    g.box(frame, f.p(u, -rd - 0.2, z - 0.1), (rw + 1.4, 0.6, 0.6), f.rz)            # sill
    g.box("e_verd", f.p(u, -rd - 0.55, z + rh + 0.1), (rw + 0.8, 0.08, 0.12), f.rz)
    return f.p(u, -rd * 0.5, z + rh * 0.5)


def make_uplights():
    k = PR["light"]["uplight"]
    for a, b, kind, s in UPL:
        e = {"statue": k * 0.35 * s * s, "pier": k * 0.6, "arch": k * 1.6}[kind]
        col = B.hexc("#FFD2A0") if kind != "statue" else B.hexc("#BFFFE6")
        B.light("SPOT", a, e, col, size=0.5, aim=b, spot=34 if kind != "statue" else 26, blend=0.6, shadow=False)
    UPL.clear()


# ------------------------------------------------------------------ city, street, media
def street(g, y0, y1, half=11.0, walk=6.0):
    g.box("road", (0, (y0 + y1) / 2, -0.25), (2 * half, y1 - y0, 0.5))
    for s in (-1, 1):
        g.box("walk", (s * (half + walk / 2), (y0 + y1) / 2, 0.0), (walk, y1 - y0, 0.5))
        g.box("trav_d", (s * (half + 0.2), (y0 + y1) / 2, 0.05), (0.4, y1 - y0, 0.6))
    y = y0
    while y < y1:
        g.box("e_wind", (0, y, 0.02), (0.25, 3.0, 0.02))
        y += 9.0


def streaks(g, y0, y1, xs, rng, key_near="e_head", key_far="e_tail"):
    for x, key in xs:
        y = y0 + rng.uniform(0, 10)
        while y < y1:
            L = rng.uniform(10, 34)
            g.box(key, (x, y + L / 2, 0.75), (0.22, L, 0.18))
            y += L + rng.uniform(8, 30)


def sky_lanes(g, rng, n, x0, x1, ys, zs):
    for k in range(n):
        y = rng.choice(ys)
        z = rng.uniform(*zs)
        x = rng.uniform(x0, x1)
        L = rng.uniform(14, 40)
        g.box(rng.choice(["e_head", "e_tail", "e_verd"]), (x, y, z), (L, 0.25, 0.25), rng.uniform(-0.08, 0.08))


def fog(lo, hi, density, rgb=(0.85, 0.82, 1.0, 1)):
    m = B.mat_volume("fog", rgb, density, aniso=0.45, noise=(0.015, 0.35, 0.75), height=2.4)
    return B.volume_box("fog", lo, hi, m)


def beam(loc, aim, rgb, energy, spot=3.0):
    return B.light("SPOT", loc, energy, rgb, size=0.3, aim=aim, spot=spot, blend=0.25, shadow=False)


# ------------------------------------------------------------------ shots
def build_district():
    rng = random.Random(PR["seeds"]["district"])
    g = B.Geo()
    M = mats()
    D = PR["district"]
    street(g, -60, D["street_len"])
    # blocks on both sides, by rule: widths from the preset ranges, heights rise with distance
    for side in (-1, 1):
        y = -40.0
        bi = 0
        while y < D["street_len"] - 20:
            width = rng.uniform(*D["block_w"])
            if abs(y + width / 2 - D["aqueduct_y"]) < 10 or abs(y + width / 2 - D["arch_y"]) < 16:
                y += 8
                continue
            depth = rng.uniform(18, 26)
            if side < 0:
                f = Frame((-17, y, 0), math.pi / 2)
                f = Frame((-17, y, 0), math.pi / 2)
            else:
                f = Frame((17, y + width, 0), -math.pi / 2)
            far = y > D["near_until"]
            if bi % 5 == 3 and not far:
                basilica(g, f, width, rng)
            else:
                floors = rng.randint(*D["floors"]) + (int((y / D["street_len"]) * 6) if far else 0)
                insula(g, f, width, depth, floors, rng, near=not far or y < D["near_until"] + 60,
                       neon=rng.choice(["e_verd", "e_verd", "e_verd", "e_amber", "e_pink"]))
            y += width + rng.uniform(1.5, 4.0)
            bi += 1
    # the second row (taller, behind) and the far towers
    for side in (-1, 1):
        y = -20.0
        while y < D["street_len"] + 120:
            w = rng.uniform(16, 30)
            H = rng.uniform(*D["tower_h"]) * (0.7 + 0.6 * max(0.0, y) / D["street_len"])
            x = side * rng.uniform(52, 90)
            f = Frame((x - w / 2, y, 0), 0.0)
            if rng.random() < PR["district"]["campanile_p"]:
                campanile(g, x, y + w / 2, w * 0.32, int(H / PR["kit"]["campanile_level"]), rng)
            else:
                arcade_tower(g, f, w, w, H, rng, neon=rng.choice(["e_verd", "e_verd", "e_cyan", "e_pink", "e_amber"]))
            y += w + rng.uniform(6, 20)
    for k in range(26):
        x = rng.uniform(-240, 240)
        y = rng.uniform(D["street_len"] + 40, D["street_len"] + 420)
        w = rng.uniform(20, 40)
        arcade_tower(g, Frame((x, y, 0), 0.0), w, w, rng.uniform(80, 220), rng, neon=rng.choice(["e_verd", "e_cyan", "e_pink"]))
    aqueduct(g, D["aqueduct_y"], -260, 260, D["aqueduct_z"], rng)
    triumph_arch(g, D["arch_y"], 46, 40, rng, M["e_verd_hi"])
    # billboards: holo panels beside rooftop statues (ad copy invented)
    for i, (x, y, z, s, key) in enumerate(D["billboards"]):
        g.quad(key, [(x, y, z), (x + s * 1.8, y, z), (x + s * 1.8, y, z + s), (x, y, z + s)])
        B.text_obj(PR["signs"]["ads"][i % len(PR["signs"]["ads"])], (x + s * 0.9, y - 0.3, z + s * 0.38), s * 0.22, M["e_white"])
    streaks(g, -60, D["street_len"], [(-7.5, "e_tail"), (-4.0, "e_tail"), (4.0, "e_head"), (7.5, "e_head")], rng)
    sky_lanes(g, rng, 40, -200, 200, [140, 220, 300, 380], (60, 120))
    g.finish(M, seed=PR["seeds"]["jitter"])
    make_uplights()
    # light: dim moon, street lamps, shop spill, beams in the fog
    B.world(B.hexc("#0B0A18"), B.hexc("#1A1020"), 1.0)
    B.light("SUN", (0, 0, 100), 0.06, B.hexc("#8FA0FF"), size=2, aim=(30, 60, 0))
    for side in (-1, 1):
        for y in range(-40, int(D["street_len"]), 24):
            B.light("POINT", (side * 12.5, y, 7.5), PR["light"]["lamp"], B.hexc("#FFB070"), size=1.0, shadow=False)
    br = random.Random(PR["seeds"]["beams"])
    for k, (x, y, z, col) in enumerate(D["beams"]):
        beam((x, y, z), (x + br.uniform(-40, 40), y + br.uniform(10, 80), z + 300), B.hexc(col), PR["light"]["beam"], spot=br.uniform(2.0, 4.0))
    fog((-320, -60, 0), (320, D["street_len"] + 480, 260), PR["fog"]["density"])
    B.camera(D["cam"], D["cam_target"], D["lens"])
    return {}


def build_kit():
    """The building kit sheet: every generator on a plinth, spaced on a grid, neutral night light."""
    rng = random.Random(PR["seeds"]["kit"])
    g = B.Geo()
    M = mats()
    items = PR["kit_sheet"]["items"]
    pitch = PR["kit_sheet"]["pitch"]
    anchors = {}
    for i, it in enumerate(items):
        col, row = i % 4, i // 4
        x0, y0 = col * pitch - 1.5 * pitch, row * pitch * 1.35
        g.box("porph", (x0, y0 + 10, -0.6), (pitch * 0.9, 44, 1.2))
        f = Frame((x0 - 12, y0, 0), 0.0)
        kind = it[0]
        if kind == "insula":
            H = insula(g, f, 24, 20, it[1], random.Random(i + 3), near=True, top=it[2])
        elif kind == "tower":
            H = arcade_tower(g, f, 24, 22, it[1], random.Random(i + 3), key="facade")
        elif kind == "basilica":
            basilica(g, Frame((x0 - 12, y0, 0), 0.0), 24, rng)
            H = 30
        elif kind == "aqueduct":
            aqueduct(g, y0, x0 - 24, x0 + 24, 26, rng)
            H = 28
        elif kind == "arch":
            triumph_arch(g, y0 + 6, 34, 26, rng, M["e_verd_hi"], x=x0)
            H = 40
        elif kind == "campanile":
            H = campanile(g, x0, y0 + 8, 7.0, it[1], random.Random(i + 7))
        elif kind == "piazza":
            piazza(g, x0, y0 + 8, 40.0, random.Random(i + 5))
            H = 20
        elif kind == "statue":
            for k in range(3):
                statue(g, Frame((x0 - 10 + k * 10, y0, 0), 0.0), 0, 0, 0, 1.6 + 0.4 * k, rng, pose=k)
            H = 22
        anchors["k%d" % i] = (x0, y0, -2)
    g.finish(M, seed=PR["seeds"]["jitter"])
    make_uplights()
    B.world(B.hexc("#0E0C1A"), B.hexc("#06050A"), 1.0)
    B.light("AREA", (-200, -250, 260), 6.0e6, B.hexc("#9AA8FF"), size=200, aim=(0, 60, 0))
    B.light("AREA", (260, 120, 120), 2.0e6, B.hexc("#FFB070"), size=160, aim=(0, 60, 20))
    B.light("AREA", (0, -140, 8), 8.0e5, B.hexc("#29DBA6"), size=200, aim=(0, 60, 30))
    B.camera(PR["kit_sheet"]["cam"], PR["kit_sheet"]["target"], PR["kit_sheet"]["lens"], shift=PR["kit_sheet"].get("shift", (0.0, 0.0)))
    return anchors


def build_hq():
    """THE CIRCUS AURELIUS: a colosseum bowl of four terrace rings; boxes (rooms) in each riser; a turning
    bronze gate ring at each terrace edge; THE ROSTRUM on the arena floor. Rooms face the centre."""
    rng = random.Random(PR["seeds"]["hq"])
    g = B.Geo()
    M = mats()
    Q = PR["hq"]
    rings = Q["rings"]          # [(r_out, r_in, floor_z), ...] outer to inner
    anchors = {}
    # the outer wall: 4 storeys of arcades (outward), travertine, neon trim lines
    R0, Hw = Q["outer_r"], Q["outer_h"]
    g.ring("trav", (0, 0, 0), R0 - 8, R0, Hw, n=96)
    nb = Q["outer_bays"]
    for s in range(4):
        z0 = s * Hw / 4
        for k in range(nb):
            a = 2 * math.pi * (k + 0.5) / nb
            x, y = (R0 + 0.06) * math.cos(a), (R0 + 0.06) * math.sin(a)
            f = Frame((x, y, 0), a + math.pi / 2)
            lit = rng.random() < 0.55
            window_arch(g, f, 0, z0 + 2.0, 4.2, Hw / 4 - 4.0, "e_win" if lit else ("e_verd" if rng.random() < 0.3 else "e_wind"), inset=0.0)
        g.ring("e_verd", (0, 0, z0 + Hw / 4 - 0.6), R0 + 0.1, R0 + 0.3, 0.25, n=120)
    # terraces + risers
    prev_floor = Hw
    for i, (ro, ri, fz) in enumerate(rings):
        g.ring("trav", (0, 0, 0), ri, ro, fz, n=96)                         # the terrace mass
        g.ring("trav_d", (0, 0, fz), ri, ro, 0.4, n=96)                     # its deck
        # seating steps on the deck (tiers)
        for s in range(3):
            g.ring("marble", (0, 0, fz + 0.4 + s * 0.6), ri + 6 + s * 3, ro - 2, 0.6, n=96)
        # the gate ring (bronze barrier) at the inner edge, with its openings at this step
        gates = [math.radians(a) for a in Q["gates_now"][i]] if i < len(Q["gates_now"]) else []
        gw = math.radians(Q["gate_w"])
        a_prev = 0.0
        cuts = sorted(gates)
        segs = []
        if cuts:
            for j, a in enumerate(cuts):
                nxt = cuts[(j + 1) % len(cuts)] + (2 * math.pi if j == len(cuts) - 1 else 0)
                segs.append((a + gw / 2, nxt - gw / 2))
        else:
            segs = [(0, 2 * math.pi)]
        for a0, a1 in segs:
            g.ring("bronze", (0, 0, fz + 0.4), ri - 0.4, ri + 1.2, 3.0, n=128, a0=a0, a1=a1)
            g.ring("e_verd", (0, 0, fz + 3.4), ri - 0.45, ri + 1.25, 0.18, n=128, a0=a0, a1=a1)
        for a in gates:                                                      # lit gate jambs + stair down
            for s_ in (-1, 1):
                aa = a + s_ * gw / 2
                g.box("e_gate", ((ri + 0.4) * math.cos(aa), (ri + 0.4) * math.sin(aa), fz + 2.4), (0.6, 0.6, 4.4), aa)
            nxt_floor = rings[i + 1][2] if i + 1 < len(rings) else 0.0
            steps = 8
            for s_ in range(steps):
                rr = ri - 1.0 - s_ * 1.4
                zz = fz - (fz - nxt_floor) * (s_ + 1) / steps
                g.box("marble", (rr * math.cos(a), rr * math.sin(a), zz), (1.4, 5.0, 0.5), a)
            anchors["gate_%d_%d" % (i, int(round(math.degrees(a))))] = (ri * math.cos(a), ri * math.sin(a), fz + 3.0)
        prev_floor = fz
    # rooms (the boxes) in each riser: ring i rooms sit on terrace i against the riser of ring i-1 (or the outer wall)
    for i, angs in enumerate(Q["rooms"]):
        ro = rings[i][0]
        fz = rings[i][2]
        for j, ad in enumerate(angs):
            a = math.radians(ad)
            # the room is a recess in the wall behind the terrace (r = ro), facing the centre
            rx, ry = ro * math.cos(a), ro * math.sin(a)
            f = Frame((rx, ry, fz + 0.4), a - math.pi / 2)      # u along the wall (clockwise), w outward (into the wall)
            rw, rh, rd = Q["room"]
            # the wall behind is r = ro; w < 0 is the terrace side (toward the centre)
            c = room_cut(g, f, 0, 0, rw, rh, rd, "e_room" if (i, j) != tuple(Q["current"]) else "e_room_c")
            anchors["room_%d_%d" % (i, j)] = c
    # the arena floor + THE ROSTRUM (the Central Server)
    g.cyl("trav_d", (0, 0, -0.5), rings[-1][1], 0.5, n=64)
    g.ring("e_verd", (0, 0, 0.0), rings[-1][1] - 1.5, rings[-1][1] - 1.0, 0.12, n=96)
    g.cyl("porph", (0, 0, 0), 14, 5, n=12)
    g.cyl("marble", (0, 0, 5), 10, 2, n=12)
    for k in range(8):
        a = 2 * math.pi * k / 8
        g.cyl("marble", (11 * math.cos(a), 11 * math.sin(a), 0), 0.8, 12, n=8)
    g.cyl("dark", (0, 0, 7), 4.5, 26, n=10, r2=3.4)
    for k in range(6):
        g.cyl("e_core", (0, 0, 9 + k * 4), 4.7 - k * 0.2, 0.6, n=12, cap=False)
    g.cyl("e_holo", (0, 0, 36), 9, 1.0, n=36, cap=False)
    g.cyl("e_verd_hi", (0, 0, 35.5), 9.4, 0.25, n=36, cap=False)
    anchors["server"] = (0, 0, 22)
    # the surrounding city ring (simple towers), the perimeter plaza, the road
    g.cyl("walk", (0, 0, -0.6), 260, 0.5, n=96)
    g.ring("road", (0, 0, -0.3), 200, 222, 0.3, n=128)
    for k in range(70):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(270, 520)
        if -math.pi * 0.75 < a < -math.pi * 0.25 and r < 420:        # keep the camera side open (the perimeter rule)
            continue
        w = rng.uniform(18, 36)
        f = Frame((r * math.cos(a), r * math.sin(a), 0), a + math.pi / 2)
        arcade_tower(g, f, w, w, rng.uniform(50, 180), rng, neon=rng.choice(["e_verd", "e_verd", "e_cyan", "e_pink", "e_amber"]))
    for k in range(18):                                             # rim statues on the outer wall
        a = 2 * math.pi * k / 18
        statue(g, Frame(((R0 - 4) * math.cos(a), (R0 - 4) * math.sin(a), 0), a + math.pi / 2), 0, 0, Hw, 1.6, rng, pose=k)
    g.finish(M, seed=PR["seeds"]["jitter"])
    make_uplights()
    B.world(B.hexc("#0B0A18"), B.hexc("#1A1020"), 1.0)
    B.light("SUN", (0, 0, 100), 0.08, B.hexc("#8FA0FF"), size=2, aim=(30, 60, 0))
    # bowl wash + rim uplights + the rostrum's own light
    B.light("POINT", (0, 0, 60), PR["light"]["hq_wash"], B.hexc("#BFFFF0"), size=20, shadow=True)
    for k in range(12):
        a = 2 * math.pi * k / 12
        B.light("SPOT", (R0 + 10) * Vector((math.cos(a), math.sin(a), 0)) + Vector((0, 0, 1)), PR["light"]["uplight"],
                B.hexc("#FFD9A0"), aim=(R0 * math.cos(a), R0 * math.sin(a), Hw), spot=40, shadow=False)
    br = random.Random(PR["seeds"]["beams"])
    for k in range(8):
        a = 2 * math.pi * (k + 0.5) / 8
        p = Vector(((R0 - 2) * math.cos(a), (R0 - 2) * math.sin(a), Hw + 2))
        beam(tuple(p), tuple(p + Vector((math.cos(a) * 60, math.sin(a) * 60, 300))), C["verdigris"] if k % 2 else B.hexc("#FFFFFF"),
             PR["light"]["beam"], spot=2.5)
    B.light("POINT", (0, 0, 24), PR["light"]["server"], B.hexc("#C8FFF0"), size=4, shadow=False)
    fog((-700, -700, 0), (700, 700, 260), PR["fog"]["density"] * 0.7)
    B.camera(Q["cam"], Q["target"], Q["lens"])
    return anchors


def build_street():
    """The V3 side-view street (a Site run): a row of facades facing the camera, route rooms cut into them."""
    rng = random.Random(PR["seeds"]["street"])
    g = B.Geo()
    M = mats()
    S_ = PR["street"]
    anchors = {}
    # road along x in front (y from -24 to 0), facades at y = 0 facing -y
    g.box("road", (S_["x1"] / 2 + S_["x0"] / 2, -14, -0.25), (S_["x1"] - S_["x0"] + 400, 26, 0.5))
    g.box("walk", (S_["x1"] / 2 + S_["x0"] / 2, -2.5, 0.0), (S_["x1"] - S_["x0"] + 400, 5, 0.5))
    x = S_["x0"]
    cols = []
    while x < S_["x1"]:
        w = rng.uniform(*S_["block_w"])
        floors = rng.randint(*S_["floors"])
        f = Frame((x, 0, 0), 0.0)
        if rng.random() < 0.25:
            H = arcade_tower(g, f, w, 22, rng.uniform(70, 120), rng, key="facade")
        else:
            H = insula(g, f, w, 22, floors, rng, near=True, neon=rng.choice(["e_verd", "e_verd", "e_amber"]))
        cols.append((x, w, H, f))
        x += w + rng.uniform(1.0, 3.0)
    # the route rooms: one column per layer, rooms on given floors (preset), cut into the facade
    for name, (ci, floor) in S_["rooms"].items():
        x0, w, H, f = cols[ci]
        z = PR["kit"]["ground_h"] + floor * PR["kit"]["storey"]
        rw, rh, rd = 10.0, 6.4, 3.0
        uc = w / 2
        key = "e_room_c" if name == S_["current"] else "e_room"
        anchors[name] = room_cut(g, f, uc, z, rw, rh, rd, key)
        anchors[name + "_tl"] = f.p(uc - rw / 2, -rd, z + rh)
        anchors[name + "_br"] = f.p(uc + rw / 2, -rd, z)
    # the aqueduct behind the row and towers further back
    aqueduct(g, 60, S_["x0"] - 100, S_["x1"] + 100, 46, rng)
    for k in range(40):
        xx = rng.uniform(S_["x0"] - 120, S_["x1"] + 120)
        yy = rng.uniform(90, 360)
        w = rng.uniform(20, 36)
        arcade_tower(g, Frame((xx, yy, 0), 0.0), w, w, rng.uniform(70, 200), rng, neon=rng.choice(["e_verd", "e_cyan", "e_pink", "e_amber"]))
    for i, (xx, z, s, key) in enumerate(S_["billboards"]):
        g.quad(key, [(xx, -0.5, z), (xx + s * 1.8, -0.5, z), (xx + s * 1.8, -0.5, z + s), (xx, -0.5, z + s)])
        B.text_obj(PR["signs"]["ads"][(i + 1) % len(PR["signs"]["ads"])], (xx + s * 0.9, -0.8, z + s * 0.38), s * 0.22, M["e_white"])
    # streak lanes along x
    for y, key in ((-20, "e_tail"), (-16.5, "e_tail"), (-11.5, "e_head"), (-8, "e_head")):
        xx = S_["x0"] - 150
        while xx < S_["x1"] + 150:
            L = rng.uniform(12, 34)
            g.box(key, (xx + L / 2, y, 0.75), (L, 0.22, 0.18))
            xx += L + rng.uniform(10, 34)
    g.finish(M, seed=PR["seeds"]["jitter"])
    make_uplights()
    B.world(B.hexc("#0B0A18"), B.hexc("#1A1020"), 1.0)
    B.light("SUN", (0, 0, 100), 0.06, B.hexc("#8FA0FF"), size=2, aim=(30, 60, 0))
    for xx in range(int(S_["x0"]) - 40, int(S_["x1"]) + 40, 22):
        B.light("POINT", (xx, -4, 7.5), PR["light"]["lamp"], B.hexc("#FFB070"), size=1.0, shadow=False)
    br = random.Random(PR["seeds"]["beams"])
    for (xx, yy, zz, col) in S_["beams"]:
        beam((xx, yy, zz), (xx + br.uniform(-60, 60), yy + br.uniform(20, 90), zz + 300), B.hexc(col), PR["light"]["beam"], spot=br.uniform(2, 4))
    fog((S_["x0"] - 400, 10, 0), (S_["x1"] + 400, 520, 240), PR["fog"]["density"])
    B.camera(S_["cam"], S_["target"], S_["lens"])
    return anchors


B.reset()
B.setup_render(J)
anchors = {"district": build_district, "kit": build_kit, "hq": build_hq, "street": build_street}[SHOT]()
B.log("built", SHOT, len(bpy.data.objects), "objects")
B.render(J, anchors)
