"""Tethys Deep (atlantis): procedural Blender scenes (the drowned ward, the kit, ATLANTIS STATION, the Site street).

blender -b --factory-startup --python tethys_scene.py -- shot="district" engine="eevee" res=[1280,720] out="..."
Water replaces rain: one absorbing + scattering medium (red dies first), light shafts from the surface, caustics on
every upward surface, marine snow in the post, sub lanes instead of car streaks. Seeds fixed; numbers in the preset.
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
import tethys_preset as P  # noqa: E402

J = B.args()
SHOT = J.get("shot", "district")
PR = P.PRESET
C = {k: B.hexc(v) for k, v in PR["palette"].items()}
L = PR["light"]
UPL = []


def caustic_mat(name, base, rough=0.8, k=None, scale=0.22, surface_z=150.0):
    """Principled + an emissive caustic net (two voronoi edge layers, world xy, warped by z), fading with depth."""
    m = bpy.data.materials.new(name)
    nt = B._nodes(m)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(p.outputs[0], out.inputs[0])
    nt.links.new(B._jitter(nt, base, 0.2), p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    tc = nt.nodes.new("ShaderNodeTexCoord")

    def vor(sc, w):
        v = nt.nodes.new("ShaderNodeTexVoronoi")
        v.feature = "DISTANCE_TO_EDGE"
        v.voronoi_dimensions = "3D"
        v.inputs["Scale"].default_value = sc
        try:
            v.inputs["Randomness"].default_value = 0.9
        except KeyError:
            pass
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (1.0, 1.0, 0.15)
        mp.inputs["Location"].default_value = (w, w * 0.7, 0)
        nt.links.new(tc.outputs["Object"], mp.inputs[0])
        nt.links.new(mp.outputs[0], v.inputs["Vector"])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs[1].default_value = 0.0
        mr.inputs[2].default_value = 0.035
        mr.inputs[3].default_value = 1.0
        mr.inputs[4].default_value = 0.0
        nt.links.new(v.outputs["Distance"], mr.inputs[0])
        return mr.outputs[0]
    a = vor(scale, 0.0)
    b = vor(scale * 1.7, 3.3)
    mx = nt.nodes.new("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    nt.links.new(a, mx.inputs[0])
    nt.links.new(b, mx.inputs[1])
    # depth fade + only on up-facing surfaces
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    dz = nt.nodes.new("ShaderNodeMath")
    dz.operation = "SUBTRACT"
    dz.inputs[0].default_value = surface_z
    nt.links.new(sep.outputs["Z"], dz.inputs[1])
    ex = nt.nodes.new("ShaderNodeMath")
    ex.operation = "MULTIPLY"
    ex.inputs[1].default_value = -0.012
    nt.links.new(dz.outputs[0], ex.inputs[0])
    ex2 = nt.nodes.new("ShaderNodeMath")
    ex2.operation = "EXPONENT"
    nt.links.new(ex.outputs[0], ex2.inputs[0])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sn = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], sn.inputs[0])
    up = nt.nodes.new("ShaderNodeMath")
    up.operation = "MAXIMUM"
    up.inputs[1].default_value = 0.0
    nt.links.new(sn.outputs["Z"], up.inputs[0])
    m1 = nt.nodes.new("ShaderNodeMath")
    m1.operation = "MULTIPLY"
    nt.links.new(mx.outputs[0], m1.inputs[0])
    nt.links.new(ex2.outputs[0], m1.inputs[1])
    m2 = nt.nodes.new("ShaderNodeMath")
    m2.operation = "MULTIPLY"
    nt.links.new(m1.outputs[0], m2.inputs[0])
    nt.links.new(up.outputs[0], m2.inputs[1])
    m3 = nt.nodes.new("ShaderNodeMath")
    m3.operation = "MULTIPLY"
    m3.inputs[1].default_value = (k if k is not None else L["caustic"]) * 10
    nt.links.new(m2.outputs[0], m3.inputs[0])
    p.inputs["Emission Color"].default_value = (0.55, 0.9, 1.0, 1)
    nt.links.new(m3.outputs[0], p.inputs["Emission Strength"])
    B._M[name] = m
    return m


def facade_mat(name, base, wrgb, lit):
    """Sparse lit windows (squatters + the few paid-up floors) on a wet dark hull."""
    m = bpy.data.materials.new(name)
    nt = B._nodes(m)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(p.outputs[0], out.inputs[0])
    nt.links.new(B._jitter(nt, base, 0.25), p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.35
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])

    def M(op, a, b):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        nt.links.new(a, n.inputs[0])
        if isinstance(b, float):
            n.inputs[1].default_value = b
        else:
            nt.links.new(b, n.inputs[1])
        return n.outputs[0]
    u = M("ADD", sep.outputs["X"], sep.outputs["Y"])
    fu = M("FRACT", M("DIVIDE", u, 3.6), 0.0) if False else None
    du = nt.nodes.new("ShaderNodeMath")
    du.operation = "DIVIDE"
    nt.links.new(u, du.inputs[0])
    du.inputs[1].default_value = 3.6
    fr = nt.nodes.new("ShaderNodeMath")
    fr.operation = "FRACT"
    nt.links.new(du.outputs[0], fr.inputs[0])
    dz = nt.nodes.new("ShaderNodeMath")
    dz.operation = "DIVIDE"
    nt.links.new(sep.outputs["Z"], dz.inputs[0])
    dz.inputs[1].default_value = 4.0
    fz = nt.nodes.new("ShaderNodeMath")
    fz.operation = "FRACT"
    nt.links.new(dz.outputs[0], fz.inputs[0])
    wu = M("LESS_THAN", fr.outputs[0], 0.5)
    wz = M("MULTIPLY", M("GREATER_THAN", fz.outputs[0], 0.3), M("LESS_THAN", fz.outputs[0], 0.75))
    cell = M("MULTIPLY", wu, wz)
    fl1 = nt.nodes.new("ShaderNodeMath")
    fl1.operation = "FLOOR"
    nt.links.new(du.outputs[0], fl1.inputs[0])
    fl2 = nt.nodes.new("ShaderNodeMath")
    fl2.operation = "FLOOR"
    nt.links.new(dz.outputs[0], fl2.inputs[0])
    cmb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(fl1.outputs[0], cmb.inputs[0])
    nt.links.new(fl2.outputs[0], cmb.inputs[1])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "3D"
    nt.links.new(cmb.outputs[0], wn.inputs["Vector"])
    on = M("LESS_THAN", wn.outputs["Value"], lit)
    em = M("MULTIPLY", M("MULTIPLY", cell, on), L["window"])
    p.inputs["Emission Color"].default_value = wrgb
    nt.links.new(em, p.inputs["Emission Strength"])
    B._M[name] = m
    return m


def mats(surface_z):
    m = {
        "hull": B.mat_solid("hull", C["hull"], 0.28, metal=0.5, jitter=0.25),
        "titan": B.mat_solid("titan", C["titan"], 0.35, metal=0.8, jitter=0.15),
        "rock": caustic_mat("rock", C["rock"], 0.9, surface_z=surface_z),
        "sand": caustic_mat("sand", C["sand"], 0.95, scale=0.17, surface_z=surface_z),
        "roof": caustic_mat("roof", C["hull"], 0.4, surface_z=surface_z, k=L["caustic"] * 0.8),
        "tower": facade_mat("tower", (0.03, 0.045, 0.05, 1), B.hexc("#FFD9A0"), 0.12),
        "tower_b": facade_mat("tower_b", (0.025, 0.03, 0.045, 1), B.hexc("#7FB0FF"), 0.18),
        "algae": B.mat_solid("algae", (0.02, 0.05, 0.03, 1), 0.9, jitter=0.4),
        "kelp": B.mat_solid("kelp", (0.03, 0.06, 0.02, 1), 0.7, jitter=0.4),
        "glass": B.mat_glass("glass", (0.6, 0.85, 1.0, 1), rough=0.05, alpha=0.16, emit=(0.4, 0.7, 1.0, 1), emit_k=0.05),
        "water_in": B.mat_glass("water_in", (0.1, 0.4, 1.0, 1), rough=0.1, alpha=0.55, emit=C["abyss"], emit_k=0.8),
        "e_abyss": B.mat_emit("e_abyss", C["abyss"], L["neon"]),
        "e_abyss_hi": B.mat_emit("e_abyss_hi", C["abyss"], L["neon"] * 2.5),
        "e_photo": B.mat_emit("e_photo", C["photo"], L["photo"]),
        "e_dive": B.mat_emit("e_dive", C["dive"], L["dome"]),
        "e_red": B.mat_emit("e_red", C["red"], L["red"]),
        "e_room": B.mat_emit("e_room", B.hexc("#FFE6B8"), L["room"]),
        "e_room_c": B.mat_emit("e_room_c", B.hexc("#A8FFF2"), L["room"]),
        "e_head": B.mat_emit("e_head", (1, 0.95, 0.85, 1), L["sub_trail"] * 1.5),
        "e_trail": B.mat_emit("e_trail", C["photo"], L["sub_trail"], alpha=0.7),
        "e_trail_r": B.mat_emit("e_trail_r", C["red"], L["sub_trail"], alpha=0.7),
        "e_core": B.mat_emit("e_core", B.hexc("#E8F4FF"), L["neon"] * 4),
        "e_vent": B.mat_emit("e_vent", B.hexc("#FF5A2A"), L["vent"]),
        "e_holo": B.mat_emit("e_holo", C["abyss"], L["neon"] * 0.7, alpha=0.55),
        "e_holo_p": B.mat_emit("e_holo_p", C["photo"], L["neon"] * 0.6, alpha=0.5),
        "e_white": B.mat_emit("e_white", (1, 0.97, 0.92, 1), L["neon"] * 0.8),
        "e_surface": B.mat_emit("e_surface", (0.55, 0.85, 1.0, 1), L["surface"]),
        "bubble": B.mat_glass("bubble", (0.9, 0.97, 1.0, 1), rough=0.02, alpha=0.35, emit=(0.7, 0.9, 1, 1), emit_k=0.6),
    }
    return m


# ------------------------------------------------------------------ the kit
def drowned_tower(g, x, y, w, d, h, rng, key="tower"):
    g.box(key, (x, y, h / 2), (w, d, h))
    # broken crown: offset slabs, exposed floors
    z = h
    for k in range(rng.randint(1, 3)):
        ww, dd = w * rng.uniform(0.4, 0.8), d * rng.uniform(0.4, 0.8)
        hh = rng.uniform(3, 9)
        g.box(key, (x + rng.uniform(-w, w) * 0.2, y + rng.uniform(-d, d) * 0.2, z + hh / 2), (ww, dd, hh), rng.uniform(-0.1, 0.1))
        z += hh * 0.6
    g.box("roof", (x, y, h + 0.2), (w + 0.4, d + 0.4, 0.4))
    # algae skirts and photophore strips (the lit ones are Tethys-leased floors)
    g.box("algae", (x, y, 4), (w + 0.6, d + 0.6, 8))
    for k in range(rng.randint(1, 3)):
        side = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        px = x + side[0] * (w / 2 + 0.1) + (rng.uniform(-w, w) * 0.4 if side[0] == 0 else 0)
        py = y + side[1] * (d / 2 + 0.1) + (rng.uniform(-d, d) * 0.4 if side[1] == 0 else 0)
        hh = rng.uniform(h * 0.3, h * 0.8)
        g.box(rng.choice(["e_photo", "e_abyss", "e_photo"]), (px, py, 8 + hh / 2), (0.25 if side[0] else 0.5, 0.25 if side[1] else 0.5, hh))
    if rng.random() < 0.6:
        g.box("e_abyss", (x, y, h * rng.uniform(0.4, 0.8)), (w + 0.5, d + 0.5, 0.3))
    g.box("e_red", (x + w / 2 - 0.5, y - d / 2 + 0.5, z + 0.6), (0.6, 0.6, 0.6))
    return z


def dome(g, cx, cy, cz, r, rng, ring_key="e_abyss"):
    """A pressure dome: titanium base ring with portholes, glass shell with ribs, a lit township inside."""
    g.ring("titan", (cx, cy, cz), r - 1.0, r, 4.0, n=48)
    for k in range(int(r * 0.9)):
        a = 2 * math.pi * k / int(r * 0.9)
        g.box("e_dive", ((r + 0.05) * math.cos(a) + cx, (r + 0.05) * math.sin(a) + cy, cz + 2.0), (0.9, 0.9, 0.9), a)
    g.ring(ring_key, (cx, cy, cz + 4.0), r - 0.2, r + 0.35, 0.3, n=64)
    g.dome("glass", (cx, cy, cz + 4.0), r, n=24, rings=8)
    for k in range(8):                                                     # meridian ribs
        a = 2 * math.pi * k / 8
        pts = [(cx + r * math.cos(t) * math.cos(a), cy + r * math.cos(t) * math.sin(a), cz + 4.0 + r * math.sin(t))
               for t in [math.pi / 2 * j / 8 for j in range(9)]]
        g.tube("titan", pts, 0.35, n=5)
    for j in (0.35, 0.7):                                                  # parallels
        g.ring("titan", (cx, cy, cz + 4.0 + r * math.sin(j * math.pi / 2)), r * math.cos(j * math.pi / 2) - 0.2,
               r * math.cos(j * math.pi / 2) + 0.15, 0.4, n=48)
    # the township inside: small blocks with lit windows, a tower in the middle
    for k in range(int(r * 0.6)):
        a = rng.uniform(0, 2 * math.pi)
        rr = rng.uniform(0, r * 0.7)
        h = rng.uniform(3, r * 0.5)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        if (rr * rr + h * h) ** 0.5 > r * 0.9:
            h = max(2.0, (r * r * 0.8 - rr * rr) ** 0.5)
        g.box("tower_b" if k % 3 else "tower", (x, y, cz + 4 + h / 2), (rng.uniform(3, 7), rng.uniform(3, 7), h))
    g.cyl("e_dive", (cx, cy, cz + 4), 0.6, r * 0.75, n=6)
    B.light("POINT", (cx, cy, cz + 4 + r * 0.45), L["uplight"] * r / 12, C["dive"], size=r * 0.3, shadow=False)


def glass_tube(g, a, b, r, rng):
    g.tube("glass", [a, b], r, n=12)
    A, Bv = Vector(a), Vector(b)
    n = int((Bv - A).length / 6)
    for k in range(n + 1):
        p = A + (Bv - A) * (k / max(1, n))
        d = (Bv - A).normalized()
        q = d.to_track_quat("Z", "Y")
        # rib ring as a short thick tube segment
        g.tube("titan", [tuple(p - d * 0.3), tuple(p + d * 0.3)], r + 0.25, n=12)
    g.tube("e_dive", [tuple(A + Vector((0, 0, -r * 0.8))), tuple(Bv + Vector((0, 0, -r * 0.8)))], 0.12, n=4)


def pump_tower(g, x, y, h, rng):
    g.cyl("hull", (x, y, 0), 6, h, n=12, r2=4.5)
    for k in range(int(h / 12)):
        g.cyl("e_abyss", (x, y, 8 + k * 12), 6.2 - k * 0.3, 0.4, n=16, cap=False)
    g.cyl("titan", (x, y, h), 7.0, 2.0, n=12)
    for k in range(4):
        a = k * math.pi / 2
        g.box("e_red", (x + 7.1 * math.cos(a), y + 7.1 * math.sin(a), h + 1), (0.7, 0.7, 0.7))
    g.box("titan", (x, y, 3), (16, 3, 6))


def kelp(g, x, y, h, rng, tip=True):
    pts = []
    ph = rng.uniform(0, 6.28)
    lean = rng.uniform(-0.15, 0.15)
    for k in range(10):
        t = k / 9
        pts.append((x + math.sin(t * 3.0 + ph) * 1.6 + lean * h * t, y + math.cos(t * 2.3 + ph) * 1.0, h * t))
    g.tube("kelp", pts, 0.22, n=4)
    for k in range(2, 9):
        t = k / 9
        px, py, pz = pts[k]
        s = 1 if k % 2 else -1
        g.quad("kelp", [(px, py, pz), (px + s * 2.2, py + 0.3, pz + 0.8), (px + s * 2.6, py + 0.5, pz + 2.2), (px, py, pz + 1.2)])
    if tip:
        g.sphere("e_photo", pts[-1], 0.45, n=6, rings=4)


def bubbles(g, x, y, z0, z1, rng):
    z = z0
    while z < z1:
        r = rng.uniform(0.15, 0.6)
        g.sphere("bubble", (x + rng.uniform(-0.8, 0.8), y + rng.uniform(-0.8, 0.8), z), r, n=6, rings=4)
        z += rng.uniform(1.5, 6.0)


def sub(g, p, d, rng, trail=40.0, red=False):
    """A small sub: capsule hull, abyss stripe, headlight + a spot, a long glowing wake behind."""
    P_, D = Vector(p), Vector(d).normalized()
    a, b = P_ - D * 3.5, P_ + D * 3.5
    g.tube("hull", [tuple(a), tuple(b)], 1.4, n=8)
    g.sphere("hull", tuple(b), 1.4, n=8, rings=5)
    g.sphere("hull", tuple(a), 1.4, n=8, rings=5)
    g.tube("e_abyss" if not red else "e_red", [tuple(a + Vector((0, 0, 1.3))), tuple(b + Vector((0, 0, 1.3)))], 0.15, n=4)
    g.sphere("e_head", tuple(b + D * 1.2), 0.5, n=6, rings=4)
    g.tube("e_trail_r" if red else "e_trail", [tuple(a - D * 1.0), tuple(a - D * trail)], 0.18, n=4)
    UPL.append((tuple(b + D * 1.6), tuple(b + D * 40 + Vector((0, 0, -6))), "sub"))


def seabed(g, x0, x1, y0, y1, step, rng, key="sand", amp=2.5):
    nx, ny = int((x1 - x0) / step) + 1, int((y1 - y0) / step) + 1
    vs, fs = [], []
    for j in range(ny):
        for i in range(nx):
            x, y = x0 + i * step, y0 + j * step
            z = amp * (math.sin(x * 0.03 + 1.7) * math.cos(y * 0.025) + 0.5 * math.sin(x * 0.07 + y * 0.05)) + rng.uniform(-0.4, 0.4)
            vs.append((x, y, z - 1.0))
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            fs.append((a, a + 1, a + nx + 1, a + nx))
    g.poly_faces(key, vs, fs)


def surface(g, x0, x1, y0, y1, z, step, rng):
    nx, ny = int((x1 - x0) / step) + 1, int((y1 - y0) / step) + 1
    vs, fs = [], []
    for j in range(ny):
        for i in range(nx):
            x, y = x0 + i * step, y0 + j * step
            vs.append((x, y, z + 1.2 * math.sin(x * 0.11 + y * 0.07) + rng.uniform(-0.5, 0.5)))
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            fs.append((a, a + nx, a + nx + 1, a + 1))
    g.poly_faces("e_surface", vs, fs)


def water(lo, hi, density=None):
    W = PR["water"]
    m = B.mat_volume("water", W["scatter"], density or W["density"], aniso=W["aniso"], absorb=W["absorb"], noise=W["noise"])
    return B.volume_box("water", lo, hi, m)


def shafts(n, x0, x1, y0, y1, z, rng):
    for k in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        B.light("SPOT", (x, y, z + 40), L["shaft"] * rng.uniform(0.5, 1.2), (0.62, 0.9, 1.0), size=2.0,
                aim=(x + rng.uniform(-30, 30), y + rng.uniform(-20, 20), 0), spot=rng.uniform(2.5, 6.0), blend=0.6, shadow=True)


def make_uplights():
    for a, b, kind in UPL:
        if kind == "sub":
            B.light("SPOT", a, L["sub_head"], C["dive"], size=0.3, aim=b, spot=22, blend=0.5, shadow=False)
    UPL.clear()


def room_cut(g, cx, cy, cz, rw, rh, rd, key, nrm=(0, -1)):
    """Cutaway room standing proud of a hull toward -y (the camera): floor, ceiling, sides, lit back, props, frame."""
    t = 0.5
    g.box("hull", (cx, cy - rd / 2, cz + 0.25), (rw, rd, 0.5))
    g.box("hull", (cx, cy - rd / 2, cz + rh), (rw, rd, 0.5))
    for s in (-1, 1):
        g.box("hull", (cx + s * rw / 2, cy - rd / 2, cz + rh / 2), (t, rd, rh))
    g.quad(key, [(cx - rw / 2, cy - 0.05, cz + 0.5), (cx + rw / 2, cy - 0.05, cz + 0.5), (cx + rw / 2, cy - 0.05, cz + rh - 0.2),
                 (cx - rw / 2, cy - 0.05, cz + rh - 0.2)])
    g.box("hull", (cx - rw * 0.22, cy - rd * 0.45, cz + 1.4), (rw * 0.22, 1.4, 2.0))
    g.box("hull", (cx + rw * 0.25, cy - rd * 0.35, cz + 1.0), (rw * 0.3, 1.2, 1.2))
    g.box("titan", (cx, cy - rd - 0.2, cz + rh + 0.5), (rw + 1.4, 0.6, 0.9))
    g.box("titan", (cx, cy - rd - 0.2, cz - 0.1), (rw + 1.4, 0.6, 0.6))
    g.box("e_abyss", (cx, cy - rd - 0.55, cz + rh + 0.1), (rw + 0.8, 0.08, 0.12))
    return (cx, cy - rd * 0.5, cz + rh * 0.5)


def holo_sign(g, M, x, y, z, s, text, key="e_holo"):
    g.quad(key, [(x, y, z), (x + s * 2.2, y, z), (x + s * 2.2, y, z + s), (x, y, z + s)])
    B.text_obj(text, (x + s * 1.1, y - 0.3, z + s * 0.36), s * 0.24, M["e_white"])


def env(surface_z, x0, x1, y0, y1):
    B.world(B.hexc("#04101E"), B.hexc("#010307"), 1.0)
    B.light("SUN", (0, 0, surface_z), L["sun"], (0.55, 0.85, 1.0), size=6, aim=(10, 25, 0))


# ------------------------------------------------------------------ shots
def build_district():
    rng = random.Random(PR["seeds"]["district"])
    g = B.Geo()
    D = PR["district"]
    sz = D["surface_z"]
    M = mats(sz)
    seabed(g, -260, 260, -60, D["len"] + 320, 8.0, rng)
    # the drowned avenue: old towers both sides, a dome every few blocks, tubes across
    domes = []
    for side in (-1, 1):
        y = -30.0
        while y < D["len"]:
            w = rng.uniform(*D["block_w"])
            d = rng.uniform(18, 28)
            x = side * (16 + d / 2)
            if rng.random() < 0.25:
                r = rng.uniform(12, 18)
                dome(g, side * (16 + r), y + r, 0.0, r, rng)
                domes.append((side * (16 + r), y + r, r))
                y += 2 * r + 4
                continue
            h = rng.uniform(*D["tower_h"]) * (0.8 + 0.4 * max(0.0, y) / D["len"])
            top = drowned_tower(g, x, y + w / 2, d, w, h, rng)
            if rng.random() < 0.3:                                    # a pressure penthouse on the roof
                r = min(w, d) * 0.45
                dome(g, x, y + w / 2, h + 0.4, r, rng)
                domes.append((x, y + w / 2, r))
            y += w + rng.uniform(2, 6)
    for k in range(40):                                              # far ward
        x = rng.uniform(-260, 260)
        y = rng.uniform(D["len"] + 20, D["len"] + 300)
        if abs(x) < 20:
            continue
        drowned_tower(g, x, y, rng.uniform(16, 30), rng.uniform(16, 30), rng.uniform(40, 140), rng, key=rng.choice(["tower", "tower_b"]))
    for k in range(5):
        pump_tower(g, rng.choice([-1, 1]) * rng.uniform(70, 140), rng.uniform(40, D["len"]), rng.uniform(60, 110), rng)
    # tubes across the avenue between dome / tower pairs (rule: every ~70 m, alternating heights)
    yy = 40.0
    k = 0
    while yy < D["len"]:
        z = 18 + (k % 3) * 16
        glass_tube(g, (-24, yy, z), (24, yy + rng.uniform(-8, 8), z + rng.uniform(-4, 4)), 2.2, rng)
        yy += rng.uniform(55, 85)
        k += 1
    # kelp along the kerbs, bubble columns from vents and domes
    kr = random.Random(PR["seeds"]["kelp"])
    for k in range(70):
        side = kr.choice([-1, 1])
        kelp(g, side * kr.uniform(9, 15), kr.uniform(-20, D["len"]), kr.uniform(8, 26), kr, tip=kr.random() < 0.5)
    br = random.Random(PR["seeds"]["bubbles"])
    for (x, y, r) in domes[:6]:
        bubbles(g, x, y, r + 4, sz - 2, br)
    for k in range(10):
        bubbles(g, br.uniform(-40, 40), br.uniform(0, D["len"]), 1, br.uniform(40, sz - 4), br)
    # sub lanes (instead of car streaks): along the avenue, two depths, coming and going
    for i, (x, z) in enumerate(D["sub_lanes"]):
        y = -20 + rng.uniform(0, 30)
        while y < D["len"]:
            dirn = (0, -1, 0) if i % 2 == 0 else (0, 1, 0)
            sub(g, (x, y, z), dirn, rng, trail=rng.uniform(20, 50), red=(i == 3))
            y += rng.uniform(40, 90)
    holo_sign(g, M, -34, 120, 44, 10, PR["signs"]["ads"][0])
    holo_sign(g, M, 22, 210, 62, 12, PR["signs"]["ads"][1], "e_holo_p")
    holo_sign(g, M, -44, 300, 80, 14, PR["signs"]["ads"][2])
    surface(g, -300, 300, -80, D["len"] + 340, sz, 10.0, rng)
    g.finish(M, seed=PR["seeds"]["jitter"])
    make_uplights()
    env(sz, -300, 300, -80, D["len"] + 340)
    shafts(D["shafts"], -120, 120, 20, D["len"] + 100, sz, random.Random(PR["seeds"]["shafts"]))
    water((-300, -80, -2), (300, D["len"] + 340, sz))
    B.camera(D["cam"], D["target"], D["lens"])
    return {}


def build_kit():
    rng = random.Random(PR["seeds"]["kit"])
    g = B.Geo()
    M = mats(200.0)
    pitch = PR["kit_sheet"]["pitch"]
    items = ["dome", "tower", "pump", "penthouse", "tube", "cable", "coldvault", "kelp_sub"]
    anchors = {}
    for i, it in enumerate(items):
        col, row = i % 4, i // 4
        x0, y0 = col * pitch - 1.5 * pitch, row * pitch * 1.35
        g.box("titan", (x0, y0 + 10, -0.6), (pitch * 0.9, 44, 1.2))
        if it == "dome":
            dome(g, x0, y0 + 8, 0, 18, rng)
        elif it == "tower":
            drowned_tower(g, x0, y0 + 8, 22, 20, 70, rng)
        elif it == "pump":
            pump_tower(g, x0, y0 + 8, 70, rng)
        elif it == "penthouse":
            drowned_tower(g, x0, y0 + 8, 22, 22, 40, rng, key="tower_b")
            dome(g, x0, y0 + 8, 40.4, 10, rng)
        elif it == "tube":
            dome(g, x0 - 22, y0 + 8, 0, 9, rng)
            dome(g, x0 + 22, y0 + 8, 0, 9, rng)
            glass_tube(g, (x0 - 14, y0 + 8, 7), (x0 + 14, y0 + 8, 7), 2.2, rng)
        elif it == "cable":
            g.box("hull", (x0, y0 + 8, 6), (26, 18, 12))
            g.box("e_abyss", (x0, y0 - 1.2, 10), (24, 0.2, 0.4))
            for k in range(3):
                g.tube("hull", [(x0 - 8 + 8 * k, y0 + 18, 2), (x0 - 8 + 8 * k, y0 + 40, 0.5)], 1.2, n=8)
            g.box("e_red", (x0 + 12, y0 - 1, 12.5), (0.6, 0.6, 0.6))
        elif it == "coldvault":
            for k in range(3):
                g.tube("hull", [(x0 - 18, y0 + k * 9, 4), (x0 + 18, y0 + k * 9, 4)], 3.6, n=12)
                for j in range(4):
                    g.cyl("e_photo", (x0 - 12 + j * 8, y0 + k * 9 - 3.7, 4), 1.0, 0.2, n=10, rot0=0) if False else \
                        g.sphere("e_photo", (x0 - 12 + j * 8, y0 + k * 9 - 3.5, 4.5), 0.8, n=8, rings=4)
            bubbles(g, x0, y0 + 9, 8, 50, rng)
        elif it == "kelp_sub":
            for k in range(9):
                kelp(g, x0 + rng.uniform(-18, 18), y0 + rng.uniform(0, 20), rng.uniform(12, 30), rng)
            sub(g, (x0, y0 - 6, 14), (1, 0, 0), rng, trail=26)
        anchors["k%d" % i] = (x0, y0, -2)
    g.finish(M, seed=PR["seeds"]["jitter"])
    make_uplights()
    B.world(B.hexc("#06142A"), B.hexc("#020508"), 1.0)
    B.light("AREA", (-200, -250, 260), 5.0e6, B.hexc("#7FB0FF"), size=200, aim=(0, 60, 0))
    B.light("AREA", (260, 120, 120), 1.2e6, C["dive"], size=160, aim=(0, 60, 20))
    B.light("AREA", (0, -140, 8), 6.0e5, C["abyss"], size=200, aim=(0, 60, 30))
    B.camera(PR["kit_sheet"]["cam"], PR["kit_sheet"]["target"], PR["kit_sheet"]["lens"], shift=PR["kit_sheet"].get("shift", (0.0, 0.0)))
    return anchors


def build_hq():
    """ATLANTIS STATION: five pressure decks hung across a trench on a spine, drop tubes between them, the ballast
    column with the tide line, THE BLACK SMOKER at the vent on the floor. Side cutaway, rooms face the camera (-y)."""
    rng = random.Random(PR["seeds"]["hq"])
    g = B.Geo()
    Q = PR["hq"]
    sz = Q["surface_z"]
    M = mats(sz)
    anchors = {}
    tw = Q["trench_w"]
    # trench walls: strata of jittered slabs both sides, a floor
    for side in (-1, 1):
        z = -10.0
        while z < sz + 30:
            h = rng.uniform(8, 22)
            inset = rng.uniform(-14, 14) + (z / sz) * 26
            x_in = side * (tw / 2 + inset)
            g.box("rock", (x_in + side * 90, rng.uniform(-10, 30), z + h / 2), (180, 200 + rng.uniform(0, 60), h), rng.uniform(-0.05, 0.05))
            z += h * rng.uniform(0.7, 1.0)
        for k in range(30):
            kelp(g, side * (tw / 2 + rng.uniform(-6, 10)), rng.uniform(-20, 10), rng.uniform(6, 16), rng, tip=True)
    seabed(g, -tw, tw, -120, 200, 8.0, rng, key="sand", amp=4)
    # the spine and the surface dock
    g.cyl("titan", (0, 30, 20), 7, sz - 10, n=16)
    for k in range(int(sz / 20)):
        g.cyl("e_abyss", (0, 30, 30 + k * 20), 7.3, 0.5, n=20, cap=False)
    g.box("hull", (0, 30, sz + 2), (120, 40, 8))
    g.box("e_red", (55, 12, sz + 6.5), (0.8, 0.8, 0.8))
    g.box("e_red", (-55, 12, sz + 6.5), (0.8, 0.8, 0.8))
    # decks
    Ld, R = Q["deck_len"], Q["deck_r"]
    rw, rh, rd = Q["room"]
    for i, (z, n) in enumerate(Q["decks"]):
        g.tube("hull", [(-Ld / 2, 30, z), (Ld / 2, 30, z)], R, n=20)
        g.sphere("hull", (-Ld / 2, 30, z), R, n=16, rings=8)
        g.sphere("hull", (Ld / 2, 30, z), R, n=16, rings=8)
        g.tube("e_abyss", [(-Ld / 2, 30 - R - 0.1, z + R * 0.7), (Ld / 2, 30 - R - 0.1, z + R * 0.7)], 0.2, n=4)
        g.tube("e_abyss", [(-Ld / 2, 30 - R - 0.1, z - R * 0.7), (Ld / 2, 30 - R - 0.1, z - R * 0.7)], 0.2, n=4)
        g.box("titan", (0, 30 - R - 0.6, z - rh / 2 - 1.2), (Ld, 3.0, 1.2))            # the gallery deck in front
        for j in range(n):
            x = -Ld / 2 + 18 + j * (Ld - 36) / max(1, n - 1) if n > 1 else 0.0
            key = "e_room_c" if [i, j] == Q["current"] else "e_room"
            anchors["room_%d_%d" % (i, j)] = room_cut(g, x, 30 - R + 2, z - rh / 2, rw, rh, rd + 2, key)
        for k in range(int(Ld / 7)):
            x = -Ld / 2 + 4 + k * 7
            g.sphere("e_dive", (x, 30 - R * 0.7, z + R * 0.55), 0.7, n=6, rings=4)
        anchors["deck_%d" % i] = (0, 30 - R, z)
    # drop tubes between decks with their state: open (dry), flooded (water inside), airlock (hatch ring)
    for i, drops in enumerate(Q["drops"]):
        z_top = Q["decks"][i][0] - R
        z_bot = Q["decks"][i + 1][0] + R
        for (x, st) in drops:
            g.tube("glass", [(x, 30 - R - 4, z_bot), (x, 30 - R - 4, z_top)], 3.0, n=12)
            for zz in (z_bot, z_top):
                g.cyl("titan", (x, 30 - R - 4, zz - 0.6), 3.6, 1.2, n=12)
            if st == "flooded":
                g.cyl("water_in", (x, 30 - R - 4, z_bot), 2.7, (z_top - z_bot) * 0.98, n=12)
                g.cyl("e_abyss_hi", (x, 30 - R - 4, z_top - 1.4), 2.9, 0.3, n=16, cap=False)
            elif st == "airlock":
                zm = (z_top + z_bot) / 2
                g.cyl("titan", (x, 30 - R - 4, zm - 1.5), 4.0, 3.0, n=12)
                g.cyl("e_red", (x, 30 - R - 4, zm + 1.6), 4.1, 0.4, n=16, cap=False)
            else:
                g.tube("e_dive", [(x + 2.4, 30 - R - 6.5, z_bot), (x + 2.4, 30 - R - 6.5, z_top)], 0.12, n=4)
            anchors["drop_%d_%d" % (i, int(x))] = (x, 30 - R - 4, (z_top + z_bot) / 2)
    # the ballast column with the tide line
    bx = Ld / 2 + 34
    zb0, zb1 = Q["decks"][-1][0] - 20, Q["decks"][0][0] + 20
    g.tube("glass", [(bx, 30, zb0), (bx, 30, zb1)], 6.5, n=20)
    g.cyl("water_in", (bx, 30, zb0), 6.0, Q["tide_z"] - zb0, n=20)
    g.cyl("e_abyss_hi", (bx, 30, Q["tide_z"] - 0.3), 6.6, 0.6, n=24, cap=False)
    for k in range(int((zb1 - zb0) / 10) + 1):
        g.box("titan", (bx - 7.2, 30 - 3, zb0 + k * 10), (2.0, 0.6, 0.5))
    for i, (z, n) in enumerate(Q["decks"]):
        g.tube("titan", [(Ld / 2 + R * 0.6, 30, z), (bx - 6.0, 30, z)], 1.6, n=8)
    anchors["tide"] = (bx, 30 - 7, Q["tide_z"])
    anchors["tide_next"] = (bx, 30 - 7, Q["tide_next_z"])
    # the vent and THE BLACK SMOKER (the Central Server around the chimney)
    for k in range(5):
        cx, cy = rng.uniform(-16, 16), rng.uniform(20, 40)
        h = rng.uniform(14, 34)
        g.cyl("rock", (cx, cy, 0), rng.uniform(3, 5), h, n=7, r2=rng.uniform(1.2, 2.4))
        g.cyl("e_vent", (cx, cy, h - 0.2), 1.0, 0.6, n=6)
    g.ring("titan", (0, 30, 0), 26, 30, 6, n=48)
    for k in range(6):
        a = 2 * math.pi * k / 6
        g.box("hull", (28 * math.cos(a), 30 + 28 * math.sin(a), 12), (4, 4, 24), a)
        g.box("e_abyss", (28 * math.cos(a), 30 + 28 * math.sin(a) - 2.1, 12), (1.0, 0.2, 18), a)
    g.ring("e_core", (0, 30, 22), 24, 25, 1.0, n=48)
    g.ring("e_abyss_hi", (0, 30, 6), 30, 30.5, 0.6, n=48)
    anchors["server"] = (0, 30 - 26, 16)
    plume = B.mat_volume("plume", (0.05, 0.05, 0.06, 1), 0.08, aniso=0.2, absorb=(0.02, 0.02, 0.03, 1), noise=(0.06, 0.3, 0.8))
    B.volume_box("plume", (-20, 15, 24), (20, 45, 110), plume)
    # bubbles, subs passing in front, the surface
    br = random.Random(PR["seeds"]["bubbles"])
    for k in range(12):
        bubbles(g, br.uniform(-Ld / 2, Ld / 2), br.uniform(5, 20), 20, sz - 2, br)
    sub(g, (-150, -40, 290), (1, 0, 0), rng, trail=60)
    sub(g, (120, -50, 150), (-1, 0, 0), rng, trail=50, red=True)
    surface(g, -400, 400, -200, 300, sz, 12.0, rng)
    g.finish(M, seed=PR["seeds"]["jitter"])
    make_uplights()
    env(sz, -400, 400, -200, 300)
    shafts(10, -140, 140, -40, 80, sz, random.Random(PR["seeds"]["shafts"]))
    for i, (z, n) in enumerate(Q["decks"]):
        B.light("AREA", (0, 30 - R - 22, z + 6), L["uplight"] * 24, C["dive"], size=Ld * 0.9, size_y=10, aim=(0, 30, z), shadow=False)
    B.light("POINT", (0, 30, 20), L["uplight"] * 20, B.hexc("#FF6A3A"), size=6, shadow=False)
    B.light("POINT", (0, 30 - 30, 18), L["uplight"] * 12, C["abyss"], size=8, shadow=False)
    water((-420, -560, -12), (420, 320, sz), PR["water"]["hq_density"])
    B.camera(Q["cam"], Q["target"], Q["lens"])
    return anchors


def build_street():
    rng = random.Random(PR["seeds"]["street"])
    g = B.Geo()
    S_ = PR["street"]
    sz = S_["surface_z"]
    M = mats(sz)
    anchors = {}
    seabed(g, S_["x0"] - 300, S_["x1"] + 300, -120, 420, 8.0, rng)
    x = S_["x0"]
    cols = []
    while x < S_["x1"]:
        w = rng.uniform(*S_["block_w"])
        h = rng.uniform(88, 120)
        drowned_tower(g, x + w / 2, 12, w, 24, h, rng, key=rng.choice(["tower", "tower_b"]))
        if rng.random() < 0.35:
            dome(g, x + w / 2, 12, h + 0.4, min(w, 24) * 0.42, rng)
        cols.append((x, w, h))
        x += w + rng.uniform(1.0, 3.0)
    for i in range(len(cols) - 1):
        if i % 3 == 1:
            x0, w0, h0 = cols[i]
            x1, w1, h1 = cols[i + 1]
            z = min(h0, h1) * rng.uniform(0.4, 0.8)
            glass_tube(g, (x0 + w0 - 1, 4, z), (x1 + 1, 4, z), 2.0, rng)
    for name, (ci, floor) in S_["rooms"].items():
        x0, w, H = cols[ci]
        z = 6 + floor * 8.5
        key = "e_room_c" if name == S_["current"] else "e_room"
        anchors[name] = room_cut(g, x0 + w / 2, 0.0, z, 10.0, 6.4, 3.0, key)
        anchors[name + "_tl"] = (x0 + w / 2 - 5, -3, z + 6.4)
        anchors[name + "_br"] = (x0 + w / 2 + 5, -3, z)
    for k in range(50):
        xx = rng.uniform(S_["x0"] - 150, S_["x1"] + 150)
        yy = rng.uniform(70, 380)
        drowned_tower(g, xx, yy, rng.uniform(18, 34), rng.uniform(18, 34), rng.uniform(40, 150), rng, key=rng.choice(["tower", "tower_b"]))
    for k in range(4):
        dome(g, rng.uniform(S_["x0"], S_["x1"]), rng.uniform(60, 120), 0, rng.uniform(16, 26), rng)
    kr = random.Random(PR["seeds"]["kelp"])
    for k in range(60):
        kelp(g, kr.uniform(S_["x0"] - 60, S_["x1"] + 60), kr.uniform(-12, -2), kr.uniform(6, 22), kr, tip=kr.random() < 0.5)
    for i, (y, z, dirn) in enumerate(((-16, 6, 1), (-22, 12, -1), (-30, 30, 1), (-26, 52, -1))):
        xx = S_["x0"] - 120 + rng.uniform(0, 40)
        while xx < S_["x1"] + 120:
            sub(g, (xx, y, z), (dirn, 0, 0), rng, trail=rng.uniform(25, 55), red=(i == 2 and rng.random() < 0.4))
            xx += rng.uniform(50, 110)
    br = random.Random(PR["seeds"]["bubbles"])
    for k in range(14):
        bubbles(g, br.uniform(S_["x0"], S_["x1"]), br.uniform(-4, 30), 1, sz - 3, br)
    holo_sign(g, M, 40, -1.2, 60, 11, PR["signs"]["ads"][3], "e_holo_p")
    holo_sign(g, M, 300, -1.2, 72, 12, PR["signs"]["ads"][0])
    surface(g, S_["x0"] - 320, S_["x1"] + 320, -300, 440, sz, 12.0, rng)
    g.finish(M, seed=PR["seeds"]["jitter"])
    make_uplights()
    env(sz, S_["x0"] - 320, S_["x1"] + 320, -300, 440)
    shafts(12, S_["x0"] - 40, S_["x1"] + 40, -10, 200, sz, random.Random(PR["seeds"]["shafts"]))
    water((S_["x0"] - 340, -320, -3), (S_["x1"] + 340, 440, sz))
    B.camera(S_["cam"], S_["target"], S_["lens"])
    return anchors


B.reset()
B.setup_render(J)
anchors = {"district": build_district, "kit": build_kit, "hq": build_hq, "street": build_street}[SHOT]()
B.log("built", SHOT, len(bpy.data.objects), "objects")
B.render(J, anchors)
