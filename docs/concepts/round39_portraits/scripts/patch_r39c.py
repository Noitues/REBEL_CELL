"""Round 39 v2 patch: Phantom eyes become downward-pointing triangles (matching the Phantom icon);
Rigger goggles sit exactly inline with the headband (level band hugging the head, cups centred on it).

python patch_r39c.py
"""
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bust_rig.py")
s = open(P, encoding="utf8").read()
assert "def tri_prism" not in s, "already patched"

OLD_EYES = s[s.index("        er = 0.17 if seed % 3 != 1 else 0.2"):s.index("        for k_ in range(3 if seed % 2 else 2):")]
NEW_EYES = '''        er = 0.19 if seed % 3 != 1 else 0.23
        for sx in (-1, 1):
            rim_ = tri_prism(sx * 0.31, -0.93, 0.12, er + 0.07, 0.12)
            finish(rim_, toon("ring", (0.25, 0.22, 0.32), RIM, 0.4), ink=0.01, tri=False)
            lens = tri_prism(sx * 0.31, -1.0, 0.12, er, 0.06)
            finish(lens, emit(acc, 2.0), ink=0.0, tri=False)
'''
s = s.replace(OLD_EYES, NEW_EYES)

OLD_RIG = s[s.index('        gz = 0.62 if seed % 3 else 0.12'):s.index('        cup = cyl(8, 0.3, 0.3, 0.22, (-wid - 0.08')]
NEW_RIG = '''        gz = 0.62 if seed % 3 else 0.12
        # a level band hugging the head at the goggle height; the cups are centred ON the band
        rb = wid * math.sqrt(max(0.05, 1 - (gz / 1.1) ** 2)) + 0.07
        band = torus(rb, 0.075, (0, 0.0, gz), maj=18)
        band.scale = (1, 1.0, 1)
        finish(band, toon("band", (0.12, 0.12, 0.14), RIM, 0.5), ink=0.01)
        for sx in (-1, 1):
            gy = -math.sqrt(max(0.01, rb ** 2 - 0.3 ** 2)) - 0.05
            g = cyl(8, 0.22, 0.22, 0.22, (sx * 0.3, gy, gz), rot=(math.radians(90), 0, 0))
            finish(g, toon("goggle", (0.12, 0.12, 0.14), RIM, 0.5), ink=0.012)
            l = cyl(8, 0.16, 0.16, 0.05, (sx * 0.3, gy - 0.12, gz), rot=(math.radians(90), 0, 0))
            finish(l, emit(acc, 1.6), ink=0.006, tri=False)
        bridge = box((0, -rb - 0.06, gz), (0.24, 0.08, 0.075))
        finish(bridge, toon("band", (0.12, 0.12, 0.14), RIM, 0.5), ink=0.008)
'''
s = s.replace(OLD_RIG, NEW_RIG)

HELPER = '''def tri_prism(cx, cy, cz, r, depth):
    """A triangular prism facing the camera (-y), one vertex pointing DOWN."""
    pts = [(cx + r * math.cos(math.radians(a)), cz + r * math.sin(math.radians(a))) for a in (90 + 120 * 0 + 0, 210, 330)]
    pts = [(cx, cz - r), (cx + r * 0.95, cz + r * 0.55), (cx - r * 0.95, cz + r * 0.55)]
    verts = [(x, cy - depth / 2, z) for x, z in pts] + [(x, cy + depth / 2, z) for x, z in pts]
    faces = [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    me = bpy.data.meshes.new("tri")
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new("tri", me)
    bpy.context.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    return o


# ------------------------------------------------------------------ build
'''
s = s.replace("# ------------------------------------------------------------------ build\n", HELPER, 1)
open(P, "w", encoding="utf8").write(s)
print("patched")
