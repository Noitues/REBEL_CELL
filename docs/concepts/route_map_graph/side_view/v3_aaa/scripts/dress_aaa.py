"""V3 AAA dressing (exec'd into scene_aaa.py AFTER the V3 dynamic build, so the shared stream 4207 is untouched).

Own seeded stream DR = Random(5150). Adds the density an AAA street needs, all kept off the route's room openings:
  facades   AC units with fan grilles, balconies with rails / plants / laundry, drain pipes, sagging cable bundles,
            wall vents, small lit doors; only on floors that are not route floors (rooms stay clear).
  roofs     condensers, water tanks, antenna masts with red blinkers, dishes, railings.
  street    ~240 tiny pedestrians (some with lit umbrella rims), vendor stalls with awnings and menu glow, bollards;
            nobody stands in front of the two street-floor rooms (L0_0, L4_0) or in the tunnel trench.
  signage   invented shop names and our corps only (Meridian, Solace, Halcyon, Orbital): text meshes on dark plates.
  holograms three translucent ad volumes in the mid row (Orbital globe, Solace lotus, Halcyon ribbon), additive.
  skyline   a fourth, taller far layer and a few distant arcology masses (the window grid shader lights them).
Text uses Blender's built-in font. Every name below is invented or one of our four corps.
"""
import random as _random
from mathutils import Matrix

DR = _random.Random(5150)
DRESS_SEM = 0.15
SIGN_K, HOLO_K = 1.0, 0.6      # signs: k is set per sign (hero 7, trim 1.6); holograms at 60 %
HERO_K, TRIM_K = 7.0, 1.6
TEXT_OBJS, HOLO_OBJS, VOLUME_OBJS, STEAM_OBJS = [], [], [], []
SAFE_COLS = [(1.0, 0.16, 0.54), (0.16, 0.83, 1.0), (0.54, 0.24, 1.0), (1.0, 0.3, 0.65), (1.0, 0.16, 0.16), (0.3, 0.7, 1.0), (1.0, 0.16, 0.54)]   # district pair + violet/pink/red only


def mat_text(name, rgb, k):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = tuple(rgb) + (1,)
    pw = attr(nt, "pwo", "OBJECT")
    pwk = math_n(nt, "ADD", pw.outputs["Fac"], math_n(nt, "LESS_THAN", pw.outputs["Fac"], 0.001))
    nt.links.new(math_n(nt, "MULTIPLY", pwk, k * SIGN_K), em.inputs["Strength"])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def mat_holo(name, rgb, k, scan=2.2):
    m = bpy.data.materials.new(name)
    for prop, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
        try:
            setattr(m, prop, val)
        except (AttributeError, TypeError):
            pass
    nt = m.node_tree
    nt.nodes.clear()
    L = nt.links.new
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    add = nt.nodes.new("ShaderNodeAddShader")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "Z"
    wave.inputs["Scale"].default_value = scan
    L(tc.outputs["Object"], wave.inputs["Vector"])
    mr = nn(nt, "ShaderNodeMapRange", From_Min=0.0, From_Max=1.0, To_Min=0.35, To_Max=1.0)
    L(wave.outputs["Fac"], mr.inputs["Value"])
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    edge = math_n(nt, "ADD", 0.35, lw.outputs["Facing"])
    pw = attr(nt, "pwo", "OBJECT")
    pwk = math_n(nt, "ADD", pw.outputs["Fac"], math_n(nt, "LESS_THAN", pw.outputs["Fac"], 0.001))
    s = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", mr.outputs[0], edge), math_n(nt, "MULTIPLY", pwk, k * HOLO_K))
    em.inputs["Color"].default_value = tuple(rgb) + (1,)
    L(s, em.inputs["Strength"])
    L(tr.outputs[0], add.inputs[0])
    L(em.outputs[0], add.inputs[1])
    L(add.outputs[0], out.inputs[0])
    return m


TEXT_MATS = {}


def text_sign(body, x, y, z, size, rgb, k=7.0, plate=True, rot=(math.pi / 2, 0, 0), extrude=0.05, name=None, frame=True):
    """A lit text sign facing the street (-y). Text is Blender's built-in font, the words are ours."""
    key = (tuple(round(v, 3) for v in rgb), k)
    if key not in TEXT_MATS:
        TEXT_MATS[key] = mat_text("txt_%d" % len(TEXT_MATS), rgb, k)
    cu = bpy.data.curves.new(name or "txt_%s" % body, "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.materials.append(TEXT_MATS[key])
    ob = bpy.data.objects.new(name or "txt_%s" % body, cu)
    ob.location = (x, y, z)
    ob.rotation_euler = rot
    scene.collection.objects.link(ob)
    TEXT_OBJS.append(ob)
    if plate:
        bpy.context.view_layer.update()
        w = max(0.6, len(body.split("\n")[0]) * size * 0.62)
        lines = body.count("\n") + 1
        h = size * 1.15 * lines
        if rot[2] == 0:
            box(x - w / 2 - 0.35, y + 0.08, z - h / 2 - 0.3, x + w / 2 + 0.35, y + 0.5, z + h / 2 + 0.3, (0.06, 0.05, 0.08), facet=False)
            if frame:
                beam((x - w / 2 - 0.35, y + 0.02, z - h / 2 - 0.3), (x + w / 2 + 0.35, y + 0.02, z - h / 2 - 0.3), 0.1,
                     tuple(v * 0.6 for v in rgb), acc=NEON)
                beam((x - w / 2 - 0.35, y + 0.02, z + h / 2 + 0.3), (x + w / 2 + 0.35, y + 0.02, z + h / 2 + 0.3), 0.1,
                     tuple(v * 0.6 for v in rgb), acc=NEON)
    return ob


def vtext(word):
    return "\n".join(word)


# ------------------------------------------------------------------ facades of the route row
def ac_unit(x, y, z, face="y"):
    c = DR.choice([(0.52, 0.52, 0.55), (0.45, 0.47, 0.5), (0.58, 0.55, 0.5)])
    if face == "y":
        box(x - 0.65, y - 0.85, z, x + 0.65, y, z + 0.85, c, facet=False)
        quad_y(SOLID, x - 0.45, z + 0.12, x + 0.45, z + 0.72, y - 0.87, (0.07, 0.07, 0.08))
        beam((x + 0.5, y - 0.3, z), (x + 0.5, y - 0.3, z - DR.uniform(0.6, 1.6)), 0.05, (0.15, 0.15, 0.16))
        if DR.random() < 0.08:
            panel(x - 0.55, z + 0.74, x - 0.35, z + 0.8, y - 0.88, RED)


def balcony(x0, x1, y, z):
    box(x0, y - 1.5, z, x1, y, z + 0.25, (0.30, 0.29, 0.33), facet=False)
    beam((x0, y - 1.45, z + 1.05), (x1, y - 1.45, z + 1.05), 0.07, (0.2, 0.2, 0.22))
    n = max(2, int((x1 - x0) / 0.6))
    for k in range(n + 1):
        xx = x0 + (x1 - x0) * k / n
        beam((xx, y - 1.45, z + 0.25), (xx, y - 1.45, z + 1.05), 0.035, (0.2, 0.2, 0.22))
    r = DR.random()
    if r < 0.35:
        for k in range(DR.randint(1, 3)):
            px = DR.uniform(x0 + 0.4, x1 - 0.4)
            box(px - 0.25, y - 1.3, z + 0.25, px + 0.25, y - 0.8, z + 0.65, (0.35, 0.22, 0.16), facet=False)
            box(px - 0.4, y - 1.4, z + 0.65, px + 0.4, y - 0.7, z + 1.25, (0.12, 0.32, 0.16), facet=False)
    elif r < 0.6:
        beam((x0 + 0.2, y - 1.0, z + 2.1), (x1 - 0.2, y - 1.0, z + 2.1), 0.03, (0.3, 0.3, 0.3))
        for k in range(int((x1 - x0) / 0.8)):
            px = x0 + 0.5 + k * 0.8
            if DR.random() < 0.7:
                quad_y(SOLID, px - 0.25, z + 1.4, px + 0.25, z + 2.08, y - 1.0, DR.choice(
                    [(0.6, 0.2, 0.25), (0.2, 0.35, 0.6), (0.7, 0.7, 0.65), (0.6, 0.5, 0.2), (0.3, 0.3, 0.35)]))
    if DR.random() < 0.45:
        dx = DR.uniform(x0 + 0.6, x1 - 1.6)
        quad_y(NEON, dx, z + 0.3, dx + 1.0, z + 2.3, y - 0.02, DR.choice([(0.55, 0.35, 0.15), (0.3, 0.4, 0.55), (0.5, 0.2, 0.35)]))


def dress_route_building(l):
    x0, x1 = LY["cols"][str(l)]
    y = LY["dy"][l]
    st = LY["storeys"][str(l)]
    rf = ROUTE_FLOORS.get(l, {})
    top = st * FH
    set_sem(DRESS_SEM, 0, l)
    for f in range(st):
        if f in rf:
            continue
        za = f * FH
        if l != 7 and f > 0 and DR.random() < 0.42 and (f - 1) not in rf:
            w = DR.uniform(4.0, 7.0)
            bx = DR.uniform(x0 + 1.0, x1 - 1.0 - w)
            balcony(bx, bx + w, y, za)
        nslot = int((x1 - x0 - 1.0) / 2.15)
        for s in range(nslot):
            if DR.random() < (0.2 if l != 7 else 0.08):
                ax = x0 + 0.5 + (s + 0.5) * (x1 - x0 - 1.0) / nslot
                ac_unit(ax, y, za + DR.choice([0.9, 4.6]))
        if DR.random() < 0.5:
            vx = DR.uniform(x0 + 1.5, x1 - 2.5)
            vz = za + DR.uniform(5.2, 6.6)
            box(vx, y - 0.25, vz, vx + 1.1, y, vz + 0.7, (0.25, 0.25, 0.28), facet=False)
            for k in range(4):
                quad_y(SOLID, vx + 0.1, vz + 0.1 + k * 0.15, vx + 1.0, vz + 0.16 + k * 0.15, y - 0.27, (0.08, 0.08, 0.09))
        if f > 0 and (f - 1) not in rf and DR.random() < 0.55:
            # a sagging cable bundle along the floor line
            zc = za + 0.25
            pts = [(x0 + 0.4 + (x1 - x0 - 0.8) * k / 8, y - 0.35, zc - 0.55 * math.sin(math.pi * k / 8)) for k in range(9)]
            for a, b in zip(pts, pts[1:]):
                beam(a, b, 0.09, (0.07, 0.07, 0.08))
    # drain pipes on the cut-wall edges (never over an opening)
    for px in ((x0 + 0.35,) if l % 2 else (x1 - 0.35,)):
        beam((px, y - 0.3, 0.0), (px, y - 0.3, top), 0.28, (0.28, 0.27, 0.3))
        for z in range(2, int(top), 4):
            beam((px - 0.2, y - 0.05, z), (px + 0.2, y - 0.5, z), 0.06, (0.2, 0.2, 0.22))
    # roof clutter (back half of the roof, behind the arch pieces)
    zt = top + 0.8
    for k in range(DR.randint(2, 4)):
        cx = DR.uniform(x0 + 1.5, x1 - 2.5)
        cy = y + DR.uniform(6.5, 10.0)
        box(cx, cy, zt, cx + 1.8, cy + 1.2, zt + 1.2, (0.42, 0.42, 0.45), facet=False)
        quad_y(SOLID, cx + 0.3, zt + 0.25, cx + 1.5, zt + 1.0, cy - 0.02, (0.08, 0.08, 0.09))
    if l in (1, 3, 6):
        tx, ty = x1 - 3.0, y + 9.0
        tube((tx, ty, zt + 2.0), (tx, ty, zt + 5.5), 1.4, (0.36, 0.3, 0.26), n=8)
        tube((tx, ty, zt + 5.5), (tx, ty, zt + 6.2), 0.7, (0.3, 0.26, 0.24), n=8)
        for s in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            beam((tx + s[0], ty + s[1], zt), (tx + s[0] * 0.9, ty + s[1] * 0.9, zt + 2.0), 0.15, (0.2, 0.2, 0.22))
    for k in range(DR.randint(1, 3)):
        ax = DR.uniform(x0 + 1.0, x1 - 1.0)
        ay = y + DR.uniform(8.0, 11.0)
        h = DR.uniform(4.0, 11.0)
        beam((ax, ay, zt), (ax, ay, zt + h), 0.12, (0.25, 0.25, 0.28))
        for q in range(DR.randint(1, 3)):
            hz = zt + h * DR.uniform(0.4, 0.9)
            beam((ax - 0.8, ay, hz), (ax + 0.8, ay, hz), 0.06, (0.25, 0.25, 0.28))
        panel(ax - 0.12, zt + h - 0.1, ax + 0.12, zt + h + 0.15, ay - 0.08, RED)
    if DR.random() < 0.6:
        dx, dyy = DR.uniform(x0 + 2, x1 - 2), y + DR.uniform(7, 10)
        tube((dx, dyy, zt + 1.6), (dx + 0.25, dyy - 0.6, zt + 2.2), 1.0, (0.55, 0.55, 0.58), n=10)
        beam((dx, dyy, zt), (dx, dyy, zt + 1.6), 0.15, (0.25, 0.25, 0.28))


for _l in range(8):
    dress_route_building(_l)

# ground-floor shop signs (only where the street floor is not a route room)
SHOP_WORDS = ["NOODLE 9", "OPEN 24", "PAWN", "NETCAFE", "CAPSULES", "CLINIC", "REPAIR", "RAMEN"]
_wi = 0
for _l in range(8):
    if 0 in ROUTE_FLOORS.get(_l, {}) or _l == 7:
        continue
    x0, x1 = LY["cols"][str(_l)]
    y = LY["dy"][_l]
    set_sem(DRESS_SEM, 0, _l)
    word = SHOP_WORDS[_wi % len(SHOP_WORDS)]
    _wi += 1
    text_sign(word, (x0 + x1) / 2 + DR.uniform(-1.5, 1.5), y - 1.75, 5.1, 0.85, DR.choice(SAFE_COLS), k=TRIM_K)

# ------------------------------------------------------------------ the street: people, stalls, bollards
_tun = next((e for e in LY["edges"] if e["type"] == "tunnel"), None)
_txs = [q[0] for q in _tun["path"][2:7]] if _tun else [0, 0]
TRENCH = (min(_txs) - 3.5, max(_txs) + 3.5)
NO_STAND = [TRENCH]
for _i, _n in LY["nodes"].items():
    if _n["floor"] == 0:
        NO_STAND.append((_n["room"][0] - 1.5, _n["room"][2] + 1.5))


def free_x(x):
    return all(not (a <= x <= b) for a, b in NO_STAND)


def person(x, y, umbrella=None):
    skin = DR.choice([(0.05, 0.045, 0.06), (0.08, 0.07, 0.09), (0.11, 0.09, 0.1), (0.06, 0.07, 0.1)])
    h = DR.uniform(1.55, 1.85)
    box(x - 0.22, y - 0.13, 0.0, x + 0.22, y + 0.13, h * 0.82, skin, facet=False)
    box(x - 0.13, y - 0.12, h * 0.84, x + 0.13, y + 0.12, h, skin, facet=False)
    if DR.random() < 0.18:
        quad_y(NEON, x - 0.2, h * 0.5, x + 0.2, h * 0.56, y - 0.14, DR.choice(SAFE_COLS))
    if umbrella:
        r = 0.62
        zt = h + 0.25
        for k in range(8):
            a0, a1 = 2 * math.pi * k / 8, 2 * math.pi * (k + 1) / 8
            SOLID.face([(x, y, zt + 0.18), (x + r * math.cos(a0), y + r * math.sin(a0), zt),
                        (x + r * math.cos(a1), y + r * math.sin(a1), zt)], (0.05, 0.05, 0.07), (0.3, 0.3, 0.3))
            NEON.face([(x + r * math.cos(a0), y + r * math.sin(a0), zt - 0.01), (x + r * math.cos(a1), y + r * math.sin(a1), zt - 0.01),
                       (x + (r + 0.07) * math.cos(a1), y + (r + 0.07) * math.sin(a1), zt - 0.04),
                       (x + (r + 0.07) * math.cos(a0), y + (r + 0.07) * math.sin(a0), zt - 0.04)], umbrella, (0, 0, 0))
        beam((x, y, h * 0.8), (x, y, zt + 0.15), 0.03, (0.1, 0.1, 0.1))


set_sem(DRESS_SEM, 0, 0)
_n_people = 0
for _k in range(420):
    if _n_people >= 240:
        break
    x = DR.uniform(-30, 215)
    if not free_x(x):
        continue
    near = DR.random() < 0.7
    y = DR.uniform(-8.1, -4.5) if near else DR.uniform(-4.5, -1.2)
    # keep people out of the building footprints (route columns start at their DY)
    col = next((l for l in range(8) if LY["cols"][str(l)][0] - 0.5 <= x <= LY["cols"][str(l)][1] + 0.5), None)
    if col is not None and y > LY["dy"][col] - 0.8:
        continue
    umb = DR.choice([CYAN, PINK, VIOLET, VIOLET, (0.4, 0.75, 1.0)]) if DR.random() < 0.22 else None
    person(x, y, umb)
    _n_people += 1
# a few crossing the road at the far crossing
for _k in range(14):
    person(DR.uniform(132, 142), DR.uniform(-36, -12), DR.choice([CYAN, None, None, PINK]))


def stall(x, y, col, word):
    box(x - 2.0, y - 1.2, 0, x + 2.0, y + 1.2, 1.1, (0.2, 0.18, 0.22), facet=False)
    for s in (-1.9, 1.9):
        beam((x + s, y - 1.1, 1.1), (x + s, y - 1.1, 2.9), 0.1, (0.2, 0.2, 0.22))
    for k in range(6):
        c = col if k % 2 == 0 else (0.85, 0.85, 0.82)
        a, b = x - 2.3 + k * 4.6 / 6, x - 2.3 + (k + 1) * 4.6 / 6
        SOLID.face([(a, y - 1.9, 2.6), (b, y - 1.9, 2.6), (b, y + 1.2, 3.2), (a, y + 1.2, 3.2)], c, (0.4, 0.2, 0.1))
    quad_y(NEON, x - 1.7, 0.3, x + 1.7, 0.95, y - 1.22, tuple(v * 0.8 for v in col))
    panel(x - 1.6, 2.0, x + 1.6, 2.45, y - 1.15, (1.0, 0.85, 0.6))
    text_sign(word, x, y - 1.95, 3.55, 0.42, col, k=TRIM_K, plate=False)
    VENTS_EXTRA.append((x + 0.8, y, 1.1, 0.5, 6.0))


VENTS_EXTRA = []
set_sem(DRESS_SEM, 0, 0)
for (sx, sc, w) in ((18.0, PINK, "YAKI"), (67.5, CYAN, "SOBA"), (141.0, RED, "CHAI"), (163.0, PINK, "DUMPLING")):
    if free_x(sx):
        stall(sx, -5.0, sc, w)
for _k in range(26):
    bx = -20 + _k * 9.0 + DR.uniform(-1, 1)
    if free_x(bx):
        beam((bx, -8.9, 0), (bx, -8.9, 0.9), 0.22, (0.3, 0.3, 0.33))
        panel(bx - 0.08, 0.72, bx + 0.08, 0.84, -9.02, (1.0, 0.75, 0.4))

# ------------------------------------------------------------------ mid-row signage (our corps only)
set_sem(0.6, 0, 0)
text_sign("ORBITAL", 72.0, 16.6, 61.5, 2.6, (0.16, 0.83, 1.0), k=TRIM_K, plate=False)
text_sign(vtext("HALCYON"), 19.0, 21.0, 44.0, 2.2, (1.0, 0.16, 0.54), k=HERO_K)          # hero 1
text_sign("SOLACE", 163.0, 39.0, 56.5, 2.4, (0.54, 0.24, 1.0), k=HERO_K)               # hero 2
text_sign("MERIDIAN", 230.0, 5.0, 50.0, 2.6, (0.16, 0.83, 1.0), k=HERO_K)              # hero 3
# moved off the decision set (it stood behind option column L4)
text_sign(vtext("ORBITAL"), -20.0, 23.0, 58.0, 1.9, (0.16, 0.83, 1.0), k=TRIM_K)
text_sign("HOTEL", -50.0, 9.0, 60.0, 2.0, (1.0, 0.16, 0.16), k=HERO_K)                  # hero 4
text_sign(vtext("NOODLE"), 127.5, 19.0, 46.0, 1.7, (1.0, 0.16, 0.16), k=HERO_K)        # hero 5
# a route-roof sign: the slab column's pink frame gets a name (col 2)
_x0, _x1 = LY["cols"]["2"]
text_sign("SOLACE", (_x0 + _x1) / 2, LY["dy"][2] + 0.55, LY["storeys"]["2"] * FH + 0.8 + 4.5, 1.7, (1.0, 0.16, 0.54), k=TRIM_K,
          plate=False)

# ------------------------------------------------------------------ holograms (translucent ad volumes, mid row)
HOLO_M = {}


def holo_mat(rgb, k):
    key = (rgb, k)
    if key not in HOLO_M:
        HOLO_M[key] = mat_holo("holo_%d" % len(HOLO_M), rgb, k)
    return HOLO_M[key]


def holo_obj(name, bmfill, mat, loc):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmfill(bm)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    me.materials.append(mat)
    scene.collection.objects.link(ob)
    HOLO_OBJS.append(ob)
    return ob


def fill_globe(bm, r=9.0, w=0.16):
    """Orbital: a wireframe globe (latitude and longitude struts as thin quads) plus an orbit ring."""
    def strut(a, b, n_off):
        a, b = Vector(a), Vector(b)
        d = (b - a)
        if d.length < 1e-6:
            return
        s = d.cross(Vector(n_off)).normalized() * w
        vs = [bm.verts.new(p) for p in (a - s, b - s, b + s, a + s)]
        bm.faces.new(vs)
    for la in range(-3, 4):
        phi = la * math.pi / 8
        for k in range(24):
            t0, t1 = 2 * math.pi * k / 24, 2 * math.pi * (k + 1) / 24
            strut((r * math.cos(phi) * math.cos(t0), r * math.cos(phi) * math.sin(t0), r * math.sin(phi)),
                  (r * math.cos(phi) * math.cos(t1), r * math.cos(phi) * math.sin(t1), r * math.sin(phi)), (0, 0, 1))
    for lo in range(8):
        t = math.pi * lo / 8
        for k in range(24):
            p0, p1 = math.pi * k / 12, math.pi * (k + 1) / 12
            strut((r * math.cos(p0) * math.cos(t), r * math.cos(p0) * math.sin(t), r * math.sin(p0)),
                  (r * math.cos(p1) * math.cos(t), r * math.cos(p1) * math.sin(t), r * math.sin(p1)), (math.cos(t + 1.57), math.sin(t + 1.57), 0))
    R2 = r * 1.5
    for k in range(48):
        t0, t1 = 2 * math.pi * k / 48, 2 * math.pi * (k + 1) / 48
        a = Vector((R2 * math.cos(t0), R2 * math.sin(t0), 0.0))
        b = Vector((R2 * math.cos(t1), R2 * math.sin(t1), 0.0))
        rot = Matrix.Rotation(math.radians(22), 3, "X")
        strut(tuple(rot @ a), tuple(rot @ b), (0, 0, 1))


def fill_lotus(bm, r=8.0):
    """Solace: a lotus of flat petals (two rings), a soft wellness mark, not a figure."""
    for ring, (n, rr, tilt, z0) in enumerate(((8, r, 0.55, 0.0), (8, r * 0.7, 0.95, 0.6))):
        for k in range(n):
            a = 2 * math.pi * (k + 0.5 * ring) / n
            ca, sa = math.cos(a), math.sin(a)
            tip = Vector((ca * rr * math.cos(tilt), sa * rr * math.cos(tilt), z0 + rr * math.sin(tilt)))
            side = Vector((-sa, ca, 0)) * rr * 0.28
            mid = tip * 0.5 + Vector((0, 0, z0 * 0.5))
            vs = [bm.verts.new(p) for p in ((0, 0, z0), tuple(mid - side), tuple(tip), tuple(mid + side))]
            bm.faces.new(vs)


def fill_ribbon(bm, h=34.0, w=4.5, turns=1.25):
    n = 60
    prev = None
    for k in range(n + 1):
        t = k / n
        a = 2 * math.pi * turns * t
        c = Vector((math.cos(a) * 2.0, math.sin(a) * 2.0, h * t))
        s = Vector((-math.sin(a), math.cos(a), 0)) * (w / 2)
        cur = (bm.verts.new(tuple(c - s)), bm.verts.new(tuple(c + s)))
        if prev:
            bm.faces.new((prev[0], cur[0], cur[1], prev[1]))
        prev = cur


holo_obj("holo_orbital", fill_globe, holo_mat((0.35, 0.8, 1.0), 2.4), (128.0, 44.0, 89.0)).rotation_euler = (0.25, 0.0, 0.5)
holo_obj("holo_solace", fill_lotus, holo_mat((0.95, 0.5, 1.0), 2.0), (40.0, 40.0, 70.0))
# (designer: the helix read as nothing; it is replaced by a readable Halcyon holo billboard in dress2_aaa.py)
text_sign("ORBITAL", 128.0, 36.0, 68.5, 1.5, (0.16, 0.83, 1.0), k=TRIM_K, plate=False)

# ------------------------------------------------------------------ the deeper skyline (a 4th far layer + arcologies)
set_sem(0.85, 0, 0)
x = -300.0
while x < 520:
    w = DR.uniform(22, 46)
    h = DR.uniform(180, 340)
    c = tuple(v * 0.2 for v in DR.choice(FAMS))
    yy = 380 + DR.uniform(-20, 20)
    box(x, yy, 0, x + w, yy + w, h, c, facet=False)
    if DR.random() < 0.55:
        tw = w * DR.uniform(0.35, 0.6)
        th = h * DR.uniform(0.1, 0.25)
        box(x + (w - tw) / 2, yy + (w - tw) / 2, h, x + (w + tw) / 2, yy + (w + tw) / 2, h + th, c, facet=False)
        h += th
    if DR.random() < 0.5:
        roof_trim(x + 0.3, yy + 0.3, x + w - 0.3, yy + w - 0.3, h + 0.1, DR.choice(TRIMS), w=1.0)
    if DR.random() < 0.5:
        beam((x + w / 2, yy + w / 2, h), (x + w / 2, yy + w / 2, h + DR.uniform(15, 40)), 1.0, (0.12, 0.12, 0.15))
        panel(x + w / 2 - 1.5, h + 36, x + w / 2 + 1.5, h + 39, yy + w / 2 - 1.5, RED)
    if DR.random() < 0.3:
        quad_y(NEON, x + w * 0.3, h * 0.2, x + w * 0.3 + 2.5, h * 0.85, yy - 0.2,
               tuple(v * 0.35 for v in DR.choice([PINK, CYAN, VIOLET])))
    x += w + DR.uniform(2, 14)
for (ax, aw, ah) in ((-120.0, 120.0, 420.0), (240.0, 150.0, 380.0)):
    box(ax, 560, 0, ax + aw, 640, ah, (0.05, 0.045, 0.07), facet=False)
    box(ax + aw * 0.2, 580, ah, ax + aw * 0.8, 620, ah + 80, (0.05, 0.045, 0.07), facet=False)
    for k in range(6):
        quad_y(NEON, ax + 4, ah * (0.15 + k * 0.14), ax + aw - 4, ah * (0.15 + k * 0.14) + 1.2, 559.5, (0.28, 0.12, 0.3))

# ------------------------------------------------------------------ steam (volumetric plumes, rendered in the volume pass)
STEAM_SPOTS = [(30, -6, 0, 1.6, 14), (128, -6, 0, 1.6, 12), (178, -7, 0, 1.4, 11)] + VENTS_EXTRA
for _l in (1, 3, 5):
    _x0, _x1 = LY["cols"][str(_l)]
    STEAM_SPOTS.append((_x0 + 3, LY["dy"][_l] + 5, LY["storeys"][str(_l)] * FH + 0.8, 1.2, 10))
set_sem(DRESS_SEM, 0, 0)
for (sx, sy, sz, sr, sh) in STEAM_SPOTS:
    if sz == 0 and free_x(sx):
        box(sx - 1.0, sy - 0.6, 0.0, sx + 1.0, sy + 0.6, 0.05, (0.1, 0.1, 0.11), facet=False)
        for k in range(5):
            quad_y(SOLID, sx - 0.9, 0.06, sx + 0.9, 0.065, sy - 0.5 + k * 0.25, (0.03, 0.03, 0.03))
print("dressed: people", _n_people, "texts", len(TEXT_OBJS), "holos", len(HOLO_OBJS), flush=True)

# stall steam: additive noise plumes (the V3 dynamic steam quads), cheap and seen in every look
_st2 = AtmosAcc("steam2")
for (sx, sy, sz, sw, sh) in VENTS_EXTRA:
    c = (0.24, 0.22, 0.3)
    for ang in (0.0, 1.5708):
        dx, dy = math.cos(ang) * sw, math.sin(ang) * sw
        _st2.quad([(sx - dx, sy - dy, sz), (sx + dx, sy + dy, sz), (sx + dx * 3.0, sy + dy * 3.0, sz + sh),
                   (sx - dx * 3.0, sy - dy * 3.0, sz + sh)], [c, c, (0, 0, 0), (0, 0, 0)])
ATMOS_OBJS.append(_st2.obj(STEAMM, "air_steam2"))
