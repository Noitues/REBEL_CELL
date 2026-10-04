"""Round 39: one-off patch applied to bust_rig.py (copied from round 38): Ghost ninja wrap, Phantom full
mask with round robotic eyes, Rigger strap through the goggle cups, Hivemind square lens wired to the
circlet, no beard on Breaker / Ghost / Phantom. Idempotent guard: refuses to run twice.

python patch_r39.py
"""
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bust_rig.py")
s = open(P, encoding="utf8").read()
assert "ninja wrap" not in s, "already patched"

GHOST_RIGGER = '''    elif cls == "ghost":
        # ninja wrap: the whole head and face wrapped in cloth, one open band for the (real) eyes
        cloth = [(0.07, 0.08, 0.11), (0.16, 0.17, 0.20), (0.05, 0.05, 0.06)][seed % 3]
        wrap = sphere(10, 8, 1.0, (0, 0.02, 0.0), (wid + 0.07, 1.0, 1.12))
        for v in wrap.data.vertices:
            if v.co.z < -0.2:
                k = (-0.2 - v.co.z) / 0.9
                v.co.x *= 1 - (jaw - 0.06) * k
                v.co.y = v.co.y * (1 - 0.18 * k) - 0.05 * k
        boolean(wrap, box((0, -0.95, 0.14), (1.4, 0.6, 0.28)))
        jitter_verts(wrap, 0.02)
        finish(wrap, toon("wrap", cloth, RIM, 0.7))
        for z_, t_ in ((-0.35, 12), (0.5, -10)):
            fold = torus(wid + 0.05, 0.045, (0, 0.02, z_), rot=(math.radians(t_), 0, 0), maj=14)
            fold.scale = (1, 1.12, 1)
            finish(fold, toon("wrapf", tuple(c * 1.6 for c in cloth), RIM, 0.6), ink=0.006)
        if seed % 3 != 2:
            hb = torus(wid + 0.1, 0.06, (0, 0.02, 0.36), rot=(math.radians(-6), 0, 0), maj=14)
            hb.scale = (1, 1.12, 1)
            finish(hb, toon("hb", acc, RIM, 0.3), ink=0.008)
        for k_, sx in enumerate((-1, 1)):
            tl = box((sx * 0.18, 1.25, 0.15 - 0.25 * k_), (0.16, 0.9 if seed % 2 else 0.6, 0.06),
                     rot=(math.radians(20 + 10 * k_), 0, math.radians(sx * 12)))
            finish(tl, toon("tail", acc if seed % 3 != 2 else tuple(c * 1.6 for c in cloth), RIM, 0.3), ink=0.008)
        nw = cyl(8, 0.46, 0.5, 0.7, (0, 0.1, -1.05))
        finish(nw, toon("wrap", cloth, RIM, 0.6))
    elif cls == "phantom":
        hair()
        # full mask: a smooth shell over the face, two round robotic eyes
        mk = sphere(10, 8, 1.0, (0, -0.04, -0.02), (wid + 0.05, 0.98, 1.1))
        for v in mk.data.vertices:
            if v.co.z < -0.2:
                k = (-0.2 - v.co.z) / 0.9
                v.co.x *= 1 - jaw * k
                v.co.y = v.co.y * (1 - 0.2 * k) - 0.06 * k
        boolean(mk, box((0, 0.62, 0), (3, 1.2, 3)))
        boolean(mk, box((0, 0, 1.0), (3, 3, 0.7)))
        finish(mk, toon("phmask", (0.93, 0.90, 0.98) if seed % 3 != 2 else (0.80, 0.74, 0.90), RIM, 0.5), ink=0.025)
        er = 0.17 if seed % 3 != 1 else 0.2
        for sx in (-1, 1):
            ring = cyl(12, er + 0.06, er + 0.06, 0.12, (sx * 0.31, -0.95, 0.12), rot=(math.radians(90), 0, 0))
            finish(ring, toon("ring", (0.25, 0.22, 0.32), RIM, 0.4), ink=0.01, tri=False)
            lens = cyl(12, er, er, 0.06, (sx * 0.31, -1.02, 0.12), rot=(math.radians(90), 0, 0))
            finish(lens, emit(acc, 2.0), ink=0.0, tri=False)
            pup = cyl(8, er * 0.35, er * 0.35, 0.04, (sx * 0.31, -1.06, 0.12), rot=(math.radians(90), 0, 0))
            finish(pup, toon("pupil", (0.12, 0.08, 0.2), RIM, 0.0), ink=0.0, tri=False)
        for k_ in range(3 if seed % 2 else 2):
            vent = box((0, -0.9, -0.5 - k_ * 0.12), (0.28, 0.05, 0.035))
            finish(vent, toon("vent", (0.35, 0.3, 0.42), RIM, 0.0), ink=0.0)
    elif cls == "rigger":
        hair()
        gz = 0.62 if seed % 3 else 0.12
        tilt = 12 if gz > 0.5 else 0
        # one strap running through both goggle cups; lenses sit in the cups
        band = torus(wid + 0.07, 0.07, (0, 0.04, gz - 0.02), rot=(math.radians(tilt), 0, 0), maj=16)
        band.scale = (1, 1.04, 1)
        finish(band, toon("band", (0.12, 0.12, 0.14), RIM, 0.5), ink=0.01)
        R_ = (wid + 0.07) * 1.04
        for sx in (-1, 1):
            gy = 0.04 - math.sqrt(max(0.01, R_ ** 2 - 0.3 ** 2)) - 0.06
            g = cyl(8, 0.22, 0.22, 0.24, (sx * 0.3, gy, gz), rot=(math.radians(90 - tilt), 0, 0))
            finish(g, toon("goggle", (0.12, 0.12, 0.14), RIM, 0.5), ink=0.012)
            l = cyl(8, 0.16, 0.16, 0.05, (sx * 0.3, gy - 0.13, gz - 0.02 * (tilt > 0)), rot=(math.radians(90 - tilt), 0, 0))
            finish(l, emit(acc, 1.6), ink=0.006, tri=False)
        bridge = box((0, 0.04 - R_ - 0.04, gz), (0.24, 0.08, 0.08), rot=(math.radians(tilt), 0, 0))
        finish(bridge, toon("band", (0.12, 0.12, 0.14), RIM, 0.5), ink=0.008)
        cup = cyl(8, 0.3, 0.3, 0.22, (-wid - 0.08, 0.05, 0.0), rot=(0, math.radians(90), 0))
        finish(cup, toon("cup", (0.15, 0.15, 0.18), RIM, 0.5))
        mic = box((-0.62, -0.6, -0.42), (0.06, 0.8, 0.06), rot=(0, 0, math.radians(30)))
        finish(mic, toon("mic", (0.12, 0.12, 0.14), RIM, 0.3), ink=0.008)
        tip = sphere(5, 4, 0.08, (-0.38, -0.95, -0.46), (1, 1, 1))
        finish(tip, emit(acc, 2.0), ink=0.005, tri=False)
'''

HIVE = '''    elif cls == "hivemind":
        hair()
        circ = torus(wid + 0.1, 0.06, (0, 0.05, 0.38), rot=(math.radians(15), 0, 0), maj=6)
        finish(circ, emit(acc, 1.2), ink=0.012, tri=False)
        for k in range(6):
            a = math.radians(60 * k + 30)
            x, y = (wid + 0.1) * math.cos(a), (wid + 0.1) * math.sin(a) * 0.97
            z = 0.38 + y * math.tan(math.radians(15)) * -1
            nd = sphere(6, 4, 0.11, (x, 0.05 + y, z), (1, 1, 1))
            finish(nd, toon("node", (0.25, 0.15, 0.3), RIM, 0.6), ink=0.008, tri=False)
        # one eye replaced by a square lens (the Overclocker lens shape), wired up to the circlet
        hous = box((0.3, -0.86, 0.13), (0.42, 0.18, 0.34))
        finish(hous, toon("hous", (0.14, 0.10, 0.18), RIM, 0.5), ink=0.014)
        sq = box((0.3, -0.96, 0.13), (0.3 if seed % 3 != 1 else 0.34, 0.05, 0.24))
        finish(sq, emit(acc, 2.0), ink=0.006)

        def bar(p0, p1, t=0.05):
            p0, p1 = Vector(p0), Vector(p1)
            dv = p1 - p0
            bpy.ops.mesh.primitive_cube_add(size=1, location=(p0 + p1) / 2)
            o = bpy.context.object
            o.scale = (t, t, dv.length)
            o.rotation_euler = dv.to_track_quat("Z", "Y").to_euler()
            bpy.ops.object.transform_apply(scale=True, rotation=True)
            return o
        a = math.radians(-60)
        cx_, cy_ = (wid + 0.1) * math.cos(a), 0.05 + (wid + 0.1) * math.sin(a) * 0.97
        cz_ = 0.38 - (cy_ - 0.05) * math.tan(math.radians(15))
        arm = bar((0.5, -0.86, 0.22), (cx_, cy_, cz_), 0.07)
        finish(arm, toon("arm", (0.20, 0.16, 0.24), RIM, 0.5), ink=0.008)
        cab = bar((0.42, -0.84, 0.3), (cx_ - 0.05, cy_ + 0.05, cz_ + 0.02), 0.035)
        finish(cab, emit(acc, 1.4), ink=0.0)
'''

i0 = s.index('    elif cls == "ghost":')
i1 = s.index('    elif cls == "overclocker":')
s = s[:i0] + GHOST_RIGGER + s[i1:]
i0 = s.index('    elif cls == "hivemind":')
i1 = s.index('    elif cls == "fixer":')
s = s[:i0] + HIVE + s[i1:]
a = '    beard = r.random() < 0.3'
assert a in s
s = s.replace(a, '    beard = r.random() < 0.3 and cls not in ("breaker", "ghost", "phantom")')
a = 'covered_eyes = cls in ("breaker", "overclocker", "fixer", "ghost")'
assert a in s
s = s.replace(a, 'covered_eyes = cls in ("breaker", "overclocker", "fixer", "phantom")')
open(P, "w", encoding="utf8").write(s)
print("patched")
