# r2b_painterly_matte - city establishing shot (Blender 5.2, headless).
# Usage: blender -b --factory-startup --python city_scene.py -- <mode> <out.png> <out.json> [samples]
#   mode: day | night | alarm | depth
# All geometry comes from one seeded generator, so every mode renders the same city.
import bpy, sys, math, json, random
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index("--") + 1:]
MODE = argv[0]
OUT = argv[1]
JSON_OUT = argv[2] if len(argv) > 2 else ""
SAMPLES = int(argv[3]) if len(argv) > 3 else 64
W, H = 1920, 1080
DMAX = 1800.0
NIGHT = MODE in ("night", "alarm")
ALARM = MODE == "alarm"
DEPTH = MODE == "depth"

scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

rng = random.Random(20260930)

# ---------------------------------------------------------------- node helpers
def sock_in(node, name, stype=None):
    for s in node.inputs:
        if s.name == name and (stype is None or s.type == stype):
            return s
    raise KeyError(name)

def sock_out(node, name, stype=None):
    for s in node.outputs:
        if s.name == name and (stype is None or s.type == stype):
            return s
    raise KeyError(name)

class NB:
    def __init__(self, mat):
        self.nt = mat.node_tree
        self.N = self.nt.nodes
        self.L = self.nt.links
        self.bsdf = next(n for n in self.N if n.type == "BSDF_PRINCIPLED")

    def feed(self, sock, v):
        if isinstance(v, (int, float)):
            sock.default_value = v
        elif isinstance(v, tuple):
            sock.default_value = v if len(v) == len(sock.default_value) else (*v, 1.0)
        else:
            self.L.new(v, sock)

    def m(self, op, a, b=0.0):
        n = self.N.new("ShaderNodeMath"); n.operation = op
        self.feed(n.inputs[0], a); self.feed(n.inputs[1], b)
        return n.outputs[0]

    def vm(self, op, a, b=(0, 0, 0)):
        n = self.N.new("ShaderNodeVectorMath"); n.operation = op
        self.feed(n.inputs[0], a); self.feed(n.inputs[1], b)
        return n.outputs[0] if op not in ("DOT_PRODUCT", "LENGTH", "DISTANCE") else n.outputs[1]

    def mix(self, fac, a, b):
        n = self.N.new("ShaderNodeMix"); n.data_type = "RGBA"
        self.feed(sock_in(n, "Factor", "VALUE"), fac)
        self.feed(sock_in(n, "A", "RGBA"), a)
        self.feed(sock_in(n, "B", "RGBA"), b)
        return sock_out(n, "Result", "RGBA")

    def ramp(self, fac, stops, interp="LINEAR"):
        n = self.N.new("ShaderNodeValToRGB")
        cr = n.color_ramp; cr.interpolation = interp
        els = cr.elements
        while len(els) < len(stops):
            els.new(0.5)
        for e, (p, c) in zip(els, stops):
            e.position = p; e.color = (*c, 1.0)
        self.feed(n.inputs["Fac"], fac)
        return n.outputs["Color"]

    def geo(self):
        g = self.N.new("ShaderNodeNewGeometry")
        return g

    def sep(self, v):
        n = self.N.new("ShaderNodeSeparateXYZ"); self.feed(n.inputs[0], v)
        return n.outputs

    def comb(self, x, y, z):
        n = self.N.new("ShaderNodeCombineXYZ")
        self.feed(n.inputs[0], x); self.feed(n.inputs[1], y); self.feed(n.inputs[2], z)
        return n.outputs[0]

    def noise(self, vec, scale, detail=4.0, rough=0.55):
        n = self.N.new("ShaderNodeTexNoise")
        if vec is not None:
            self.feed(n.inputs["Vector"], vec)
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough
        return n.outputs["Fac"]

    def white(self, vec):
        n = self.N.new("ShaderNodeTexWhiteNoise"); n.noise_dimensions = "3D"
        self.feed(n.inputs["Vector"], vec)
        return n.outputs["Value"], n.outputs["Color"]

    def set(self, name, v):
        self.feed(self.bsdf.inputs[name], v)

    def bump(self, h, strength):
        n = self.N.new("ShaderNodeBump"); n.inputs["Strength"].default_value = strength
        self.feed(n.inputs["Height"], h)
        self.L.new(n.outputs["Normal"], self.bsdf.inputs["Normal"])


def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, NB(m)

# ---------------------------------------------------------------- materials
SAND = [(0.56, 0.44, 0.30), (0.62, 0.52, 0.38), (0.44, 0.25, 0.16), (0.50, 0.47, 0.42),
        (0.36, 0.34, 0.31), (0.55, 0.38, 0.24), (0.26, 0.36, 0.34)]

def facade_mat(name, palette, glass_room=2.8, emit_scale=1.0, lit_cut=0.62):
    m, b = new_mat(name)
    oi = b.N.new("ShaderNodeObjectInfo")
    stops = [(i / len(palette), c) for i, c in enumerate(palette)]
    base = b.ramp(oi.outputs["Random"], stops, "CONSTANT")
    g = b.geo()
    p = b.sep(g.outputs["Position"]); nrm = b.sep(g.outputs["Normal"])
    grime = b.noise(g.outputs["Position"], 0.09, 6.0, 0.6)
    streak = b.noise(b.comb(b.m("MULTIPLY", p[0], 0.4), b.m("MULTIPLY", p[1], 0.4), b.m("MULTIPLY", p[2], 0.03)), 1.0, 3.0)
    dirt = b.m("MULTIPLY", b.m("ADD", grime, streak), 0.5)
    base = b.mix(b.m("MULTIPLY", dirt, 0.55), base, (0.25, 0.2, 0.17))
    hor = b.m("ADD", p[0], p[1])
    u = b.m("FRACT", b.m("DIVIDE", hor, glass_room))
    a = b.m("LESS_THAN", b.m("ABSOLUTE", b.m("SUBTRACT", u, 0.5)), 0.27)
    v = b.m("FRACT", b.m("DIVIDE", p[2], 3.6))
    bb = b.m("LESS_THAN", b.m("ABSOLUTE", b.m("SUBTRACT", v, 0.55)), 0.24)
    fac = b.m("LESS_THAN", b.m("ABSOLUTE", nrm[2]), 0.5)
    above = b.m("GREATER_THAN", p[2], 3.2)
    mask = b.m("MULTIPLY", b.m("MULTIPLY", a, bb), b.m("MULTIPLY", fac, above))
    b.set("Base Color", b.mix(mask, base, (0.10, 0.12, 0.16)))
    b.set("Roughness", b.m("ADD", b.m("MULTIPLY", mask, -0.65), 0.88))
    cell = b.comb(b.m("FLOOR", b.m("DIVIDE", hor, glass_room)), b.m("FLOOR", b.m("DIVIDE", p[2], 3.6)),
                  b.m("MULTIPLY", oi.outputs["Random"], 91.0))
    val, col = b.white(cell)
    lit = b.m("GREATER_THAN", val, lit_cut if not ALARM else lit_cut - 0.07)
    cs = b.sep(col)
    wcol = b.ramp(cs[0], [(0.0, (1.0, 0.62, 0.30)), (0.55, (1.0, 0.80, 0.52)), (0.75, (0.45, 0.80, 1.0)),
                          (0.93, (1.0, 0.30, 0.75))], "CONSTANT")
    em = b.vm("MULTIPLY", wcol, b.comb(b.m("MULTIPLY", mask, lit), b.m("MULTIPLY", mask, lit), b.m("MULTIPLY", mask, lit)))
    b.set("Emission Color", em)
    b.set("Emission Strength", 3.2 * emit_scale if NIGHT else 0.0)
    b.bump(grime, 0.15)
    return m

def simple_mat(name, color, rough=0.7, metal=0.0, emit=None, emit_str=0.0, noise_bump=0.0):
    m, b = new_mat(name)
    b.set("Base Color", (*color, 1.0)); b.set("Roughness", rough); b.set("Metallic", metal)
    if emit is not None:
        b.set("Emission Color", (*emit, 1.0)); b.set("Emission Strength", emit_str)
    if noise_bump > 0:
        g = b.geo(); b.bump(b.noise(g.outputs["Position"], 0.6, 6.0), noise_bump)
    return m

def patina_mat(name):
    m, b = new_mat(name)
    g = b.geo()
    n1 = b.noise(g.outputs["Position"], 0.12, 8.0, 0.62)
    n2 = b.noise(g.outputs["Position"], 0.9, 4.0, 0.5)
    c = b.ramp(b.m("ADD", b.m("MULTIPLY", n1, 0.8), b.m("MULTIPLY", n2, 0.3)),
               [(0.30, (0.45, 0.28, 0.16)), (0.50, (0.30, 0.44, 0.38)), (0.66, (0.20, 0.52, 0.46)),
                (0.80, (0.52, 0.66, 0.58))])
    b.set("Base Color", c); b.set("Metallic", 0.25); b.set("Roughness", 0.62)
    b.bump(n2, 0.25)
    return m

def neon_mat(name, color, day_str, night_str):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*color, 1.0)
    e.inputs["Strength"].default_value = night_str if NIGHT else day_str
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    return m

def ground_mat():
    m, b = new_mat("ground")
    g = b.geo(); p = b.sep(g.outputs["Position"])
    sx = b.m("LESS_THAN", b.m("ABSOLUTE", b.m("SUBTRACT", b.m("FRACT", b.m("ADD", b.m("DIVIDE", p[0], 36.0), 0.5)), 0.5)), 5.0 / 36.0)
    sy = b.m("LESS_THAN", b.m("ABSOLUTE", b.m("SUBTRACT", b.m("FRACT", b.m("ADD", b.m("DIVIDE", b.m("ADD", p[1], 10.0), 36.0), 0.5)), 0.5)), 5.0 / 36.0)
    street = b.m("MAXIMUM", sx, sy)
    n = b.noise(g.outputs["Position"], 0.05, 6.0, 0.6)
    n2 = b.noise(g.outputs["Position"], 0.7, 3.0, 0.5)
    pave = b.ramp(n, [(0.3, (0.52, 0.45, 0.36)), (0.7, (0.70, 0.60, 0.46))])
    road = b.ramp(n2, [(0.3, (0.13, 0.12, 0.12)), (0.7, (0.22, 0.20, 0.19))])
    b.set("Base Color", b.mix(street, pave, road))
    b.set("Roughness", b.m("ADD", b.m("MULTIPLY", street, -0.35 if NIGHT else -0.1), 0.85))
    b.bump(n2, 0.1)
    return m

def water_mat():
    m, b = new_mat("water")
    g = b.geo()
    n = b.noise(b.comb(b.m("MULTIPLY", b.sep(g.outputs["Position"])[0], 0.15), b.sep(g.outputs["Position"])[1], 0.0), 0.6, 3.0)
    b.set("Base Color", (0.02, 0.30, 0.28, 1.0) if not NIGHT else (0.01, 0.05, 0.07, 1.0))
    b.set("Roughness", 0.06); b.set("Metallic", 0.1)
    b.bump(n, 0.12)
    return m

def people_mat():
    m, b = new_mat("people")
    oi = b.N.new("ShaderNodeObjectInfo")
    b.set("Base Color", b.ramp(oi.outputs["Random"], [(0.0, (0.55, 0.07, 0.05)), (0.3, (0.04, 0.38, 0.33)),
                                                       (0.55, (0.70, 0.50, 0.22)), (0.8, (0.12, 0.11, 0.14))], "CONSTANT"))
    b.set("Roughness", 0.8)
    return m

def depth_mat():
    m = bpy.data.materials.new("depth"); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    cd = nt.nodes.new("ShaderNodeCameraData")
    d = nt.nodes.new("ShaderNodeMath"); d.operation = "DIVIDE"; d.use_clamp = True
    nt.links.new(cd.outputs["View Z Depth"], d.inputs[0]); d.inputs[1].default_value = DMAX
    s = nt.nodes.new("ShaderNodeMath"); s.operation = "SQRT"
    nt.links.new(d.outputs[0], s.inputs[0])
    e = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(s.outputs[0], e.inputs["Color"]); e.inputs["Strength"].default_value = 1.0
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    return m

M_FAC = facade_mat("facade", SAND)
M_FAC_FAR = facade_mat("facade_far", [(0.62, 0.62, 0.64), (0.70, 0.66, 0.60), (0.50, 0.52, 0.56), (0.76, 0.70, 0.62)], 2.2, 0.35, 0.74)
M_STUCCO = simple_mat("stucco", (0.60, 0.45, 0.30), 0.9, noise_bump=0.25)
M_STONE = simple_mat("stone", (0.32, 0.20, 0.13), 0.95, noise_bump=0.6)
M_PATINA = patina_mat("patina")
M_BRASS = simple_mat("brass", (0.88, 0.64, 0.30), 0.32, 1.0)
M_BLUE = simple_mat("bluepaint", (0.06, 0.10, 0.34), 0.55)
M_DARK = simple_mat("recess", (0.05, 0.035, 0.03), 0.9, emit=(1.0, 0.55, 0.25), emit_str=(1.2 if NIGHT else 0.5))
M_GROUND = ground_mat()
M_WATER = water_mat()
M_PEOPLE = people_mat()
M_METAL = simple_mat("metal", (0.20, 0.19, 0.19), 0.5, 0.8)
M_RUST = simple_mat("rust", (0.38, 0.20, 0.12), 0.8, 0.3, noise_bump=0.3)
M_BANNER = simple_mat("banner", (0.62, 0.06, 0.05), 0.8, emit=(1.0, 0.15, 0.08), emit_str=(2.0 if NIGHT else 0.0))
NEON_C = [(0.1, 0.95, 0.9), (1.0, 0.25, 0.7), (1.0, 0.65, 0.15), (0.45, 0.4, 1.0)]
M_NEON = [neon_mat("neon%d" % i, c, 0.35, 9.0) for i, c in enumerate(NEON_C)]
M_RING = neon_mat("ring", (1.0, 0.1, 0.05) if ALARM else (0.2, 0.95, 0.9), 0.6, 12.0)
M_HEAD = neon_mat("headlight", (1.0, 0.92, 0.75), 0.0, 14.0)
M_TAIL = neon_mat("taillight", (1.0, 0.08, 0.04), 0.0, 10.0)
M_LAMP = neon_mat("lamp", (1.0, 0.72, 0.4), 0.0, 10.0)
M_BILL = [neon_mat("bill%d" % i, c, 0.9, 5.0) for i, c in enumerate(NEON_C)]
M_ALARM = neon_mat("alarm", (1.0, 0.05, 0.02), 0.0, 25.0)

# ---------------------------------------------------------------- mesh helpers
def link(ob):
    scene.collection.objects.link(ob); return ob

def mesh_obj(name, verts, faces, mat, loc=(0, 0, 0)):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); ob.location = loc
    if mat:
        me.materials.append(mat)
    return link(ob)

def box(cx, cy, z0, sx, sy, sz, mat, name="box", rotz=0.0):
    x0, x1, y0, y1 = -sx / 2, sx / 2, -sy / 2, sy / 2
    v = [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0), (x0, y0, sz), (x1, y0, sz), (x1, y1, sz), (x0, y1, sz)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    ob = mesh_obj(name, v, f, mat, (cx, cy, z0)); ob.rotation_euler.z = rotz
    return ob

def prim(kind, mat, smooth=True, **kw):
    getattr(bpy.ops.mesh, "primitive_" + kind + "_add")(**kw)
    ob = bpy.context.active_object
    if mat:
        ob.data.materials.append(mat)
    if smooth:
        for poly in ob.data.polygons:
            poly.use_smooth = True
    return ob

def cyl(x, y, z, r, d, mat, verts=32, smooth=True):
    return prim("cylinder", mat, smooth, vertices=verts, radius=r, depth=d, location=(x, y, z + d / 2))

def half_dome(x, y, z, r, sz, mat, seg=48):
    ob = prim("uv_sphere", mat, True, segments=seg, ring_count=24, radius=r, location=(0, 0, 0))
    me = ob.data
    import bmesh
    bm = bmesh.new(); bm.from_mesh(me)
    kill = [v for v in bm.verts if v.co.z < -0.01]
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    bm.to_mesh(me); bm.free()
    ob.location = (x, y, z); ob.scale = (1, 1, sz)
    return ob

def upper_half(ob, loc, cyl_axis=False):
    """Keep the half of a ring/disc lying in +Y, then stand it up facing the camera (-Y)."""
    import bmesh
    me = ob.data
    if cyl_axis:  # cylinder axis Z -> make it a disc facing Y first
        for v in me.vertices:
            v.co = Vector((v.co.x, v.co.z, v.co.y))
    bm = bmesh.new(); bm.from_mesh(me)
    kill = [v for v in bm.verts if v.co.y < -0.01]
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    bm.to_mesh(me); bm.free()
    ob.rotation_euler = (math.pi / 2, 0, 0)
    ob.location = loc
    return ob

# ---------------------------------------------------------------- layout
HERO = (72.0, 40.0)
DOME2 = (-128.0, 214.0)
NODES = [  # x, y, kind, label
    (-36.0, -10.0, "safehouse", "HIDEOUT"),
    (-36.0, 62.0, "site", "RELAY"),
    (36.0, -10.0, "site", "MARKET"),
    (72.0, 2.0, "target", "SPIRE"),
    (-108.0, 98.0, "target", "DATAVAULT"),
    (0.0, 134.0, "site", "CLINIC"),
    (-72.0, 206.0, "site", "PIRATE TX"),
    (108.0, 134.0, "target", "ARCHIVE"),
]
EDGES = [  # node a, node b, corner points between
    (0, 1, []), (0, 2, []), (2, 3, [(72.0, -10.0)]), (1, 4, [(-108.0, 62.0)]),
    (1, 5, [(0.0, 62.0)]), (5, 6, [(-72.0, 134.0)]), (5, 7, []), (1, 2, [(36.0, 62.0)]),
]
HERE = 0

def blocked(x, y, pad=0.0):
    if math.hypot(x - HERO[0], y - HERO[1]) < 44 + pad:
        return True
    if math.hypot(x - DOME2[0], y - DOME2[1]) < 30 + pad:
        return True
    return False

# ground + canal
mesh_obj("ground", [(-1600, -22, 0), (1600, -22, 0), (1600, 2400, 0), (-1600, 2400, 0)], [(0, 1, 2, 3)], M_GROUND)
mesh_obj("water", [(-1600, -400, -4), (1600, -400, -4), (1600, -22, -4), (-1600, -22, -4)], [(0, 1, 2, 3)], M_WATER)
box(0, -23, -4.5, 3200, 2.2, 4.6, M_STONE, "quaywall")
# broken ledges / slabs along the bank and in the water (the reference's rock shelves)
def rock(x, y, z, sx, sy, sz, rz):
    ob = prim("ico_sphere", M_STONE, False, subdivisions=1, radius=1.0, location=(x, y, z))
    ob.scale = (sx, sy, sz); ob.rotation_euler = (rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), rz)
    return ob

# broken rock shelves along the bank (the reference's red rock ledges), stacked in layers
for i in range(90):
    x = rng.uniform(-300, 300); y = rng.uniform(-30, -23); w = rng.uniform(5, 12)
    rock(x, y, rng.uniform(-3.8, -1.5), w, rng.uniform(2.5, 5), rng.uniform(1.0, 2.4), rng.uniform(-0.3, 0.3))
for i in range(9):
    x = rng.uniform(-110, -20); y = rng.uniform(-60, -36)
    rock(x, y, -4.2, rng.uniform(2, 5), rng.uniform(1.5, 3.5), rng.uniform(0.6, 1.2), rng.uniform(0, 3.1))

# city blocks
buildings = []
for i in range(-11, 11):
    for j in range(0, 14):
        bx0, bx1 = 36 * i + 5, 36 * i + 31
        by0, by1 = 36 * j - 5, 36 * j + 21
        split = rng.choice([1, 2, 2, 3, 4])
        lots = []
        if split == 1:
            lots = [(bx0, bx1, by0, by1)]
        elif split == 2:
            if rng.random() < 0.5:
                mx = rng.uniform(bx0 + 9, bx1 - 9); lots = [(bx0, mx, by0, by1), (mx, bx1, by0, by1)]
            else:
                my = rng.uniform(by0 + 9, by1 - 9); lots = [(bx0, bx1, by0, my), (bx0, bx1, my, by1)]
        elif split == 3:
            mx = rng.uniform(bx0 + 10, bx1 - 10); my = rng.uniform(by0 + 9, by1 - 9)
            lots = [(bx0, mx, by0, by1), (mx, bx1, by0, my), (mx, bx1, my, by1)]
        else:
            mx = (bx0 + bx1) / 2; my = (by0 + by1) / 2
            lots = [(bx0, mx, by0, my), (mx, bx1, by0, my), (bx0, mx, my, by1), (mx, bx1, my, by1)]
        for (x0, x1, y0, y1) in lots:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            r_tower = rng.random(); r_h = rng.random(); r_top = rng.random(); r_clut = rng.random()
            inset = rng.uniform(0.6, 1.8)
            if blocked(cx, cy):
                continue
            far = max(0.0, cy - 60.0)
            h = 7 + r_h * 10 + far * 0.035 * (0.4 + r_h)
            if cy > 230 and r_tower < 0.045:
                h += 30 + r_h * 60
            if cy < 40:
                h = min(h, 13)
            sx, sy = (x1 - x0) - 2 * inset, (y1 - y0) - 2 * inset
            if sx < 3 or sy < 3:
                continue
            mat = M_FAC if cy < 260 else M_FAC_FAR
            box(cx, cy, 0, sx, sy, h, mat, "bld")
            buildings.append((cx, cy, sx, sy, h))
            top = h
            if h > 30 and r_top < 0.6:
                s2 = rng.uniform(0.55, 0.8); h2 = rng.uniform(0.2, 0.5) * h
                box(cx, cy, h, sx * s2, sy * s2, h2, mat, "bld")
                top = h + h2
            # cornice
            box(cx, cy, h - 0.2, sx + 0.6, sy + 0.6, 0.6, M_STONE if cy < 150 else M_FAC_FAR, "corn")
            # rooftop clutter
            if r_clut < 0.35:
                cyl(cx + rng.uniform(-sx / 4, sx / 4), cy + rng.uniform(-sy / 4, sy / 4), top, 1.3, 2.4, M_RUST, 12)
            elif r_clut < 0.6:
                box(cx + rng.uniform(-sx / 4, sx / 4), cy + rng.uniform(-sy / 4, sy / 4), top, 2.5, 2.0, 1.5, M_METAL, "ac")
                cyl(cx - sx / 3, cy - sy / 3, top, 0.12, rng.uniform(4, 10), M_METAL, 6, False)
            elif r_clut < 0.72 and h > 14:
                # billboard on the camera-facing side
                bw = min(sx * 0.8, 10); bh = bw * 0.5
                box(cx, cy - sy / 2 - 0.35, h * rng.uniform(0.45, 0.8), bw, 0.3, bh, M_BILL[int(r_h * 97) % 4], "bill")

# far mega-towers: the "mountain range" of the matte painting
for k in range(24):
    x = rng.uniform(-900, 900); y = rng.uniform(560, 1300)
    w = rng.uniform(30, 90); d = rng.uniform(30, 90); h = rng.uniform(55, 170) * (1.6 if rng.random() < 0.12 else 1.0)
    box(x, y, 0, w, d, h, M_FAC_FAR, "mega")
    if rng.random() < 0.5:
        box(x, y, h, w * 0.6, d * 0.6, h * rng.uniform(0.15, 0.45), M_FAC_FAR, "mega")
    if rng.random() < 0.4:
        cyl(x, y, h, 1.2, rng.uniform(20, 60), M_METAL, 6, False)
# arcology pyramid (the distant peak)
mesh_obj("arcology", [(-200, 1000, 0), (-20, 1000, 0), (-20, 1180, 0), (-200, 1180, 0), (-120, 1090, 330)],
         [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (3, 2, 1, 0)], M_FAC_FAR)

# ---------------------------------------------------------------- hero spire (the focal building)
def domed_hall(cx, cy, s, with_door=True, crown=True):
    R = 26 * s
    cyl(cx, cy, 0, R + 1.5 * s, 2.0 * s, M_STONE, 64)                     # plinth
    cyl(cx, cy, 2 * s, R, 26 * s, M_STUCCO, 64)                           # drum
    # blue pilasters with brass caps
    for k in range(16):
        a = k / 16 * math.tau
        if with_door and abs(a - 1.5 * math.pi) < 0.35:
            continue
        px, py = cx + math.cos(a) * (R + 0.2), cy + math.sin(a) * (R + 0.2)
        box(px, py, 2 * s, 1.6 * s, 1.6 * s, 22 * s, M_BLUE, "pil", a)
        prim("uv_sphere", M_BRASS, True, radius=1.1 * s, segments=12, ring_count=8, location=(px, py, 24.4 * s))
        # arched window niches between pilasters
        a2 = a + math.pi / 16
        wx, wy = cx + math.cos(a2) * (R - 0.3), cy + math.sin(a2) * (R - 0.3)
        box(wx, wy, 14 * s, 2.4 * s, 1.2 * s, 5 * s, M_DARK, "win", a2 + math.pi / 2)
        box(wx, wy, 6 * s, 2.0 * s, 1.2 * s, 3 * s, M_DARK, "win", a2 + math.pi / 2)
    # brass belt, cornice, rivet ring
    prim("torus", M_BRASS, True, major_radius=R + 0.3, minor_radius=0.5 * s, location=(cx, cy, 20 * s))
    cyl(cx, cy, 26 * s, R + 2.2 * s, 3 * s, M_PATINA, 64)
    prim("torus", M_BRASS, True, major_radius=R + 2.3 * s, minor_radius=0.45 * s, location=(cx, cy, 29 * s))
    for k in range(36):
        a = k / 36 * math.tau
        prim("uv_sphere", M_BRASS, True, radius=0.55 * s, segments=10, ring_count=6,
             location=(cx + math.cos(a) * (R + 2.3 * s), cy + math.sin(a) * (R + 2.3 * s), 27.4 * s))
    # neon band (cyan normally, red under alarm)
    prim("torus", M_RING, True, major_radius=R + 0.35, minor_radius=0.28 * s, location=(cx, cy, 17 * s))
    # dome + ribs
    half_dome(cx, cy, 29 * s, R + 0.5 * s, 0.82, M_PATINA)
    for k in range(4):
        t = prim("torus", M_BRASS, True, major_radius=R + 0.9 * s, minor_radius=0.35 * s, location=(cx, cy, 29 * s),
                 rotation=(math.pi / 2, 0, k * math.pi / 4))
        t.scale = (1, 1, 1); t.scale.y = 1.0
        t.scale = (1.0, 0.82, 1.0)
    # dormers
    for k in range(4):
        a = math.pi * 1.25 + k * math.pi / 2
        dx, dy = cx + math.cos(a) * R * 0.78, cy + math.sin(a) * R * 0.78
        box(dx, dy, 29 * s, 5 * s, 5 * s, 9 * s, M_STUCCO, "dormer", a)
        box(dx + math.cos(a) * 2.6 * s, dy + math.sin(a) * 2.6 * s, 31 * s, 2.4 * s, 0.4 * s, 4.5 * s, M_DARK, "dwin", a + math.pi / 2)
        prim("cone", M_PATINA, True, vertices=4, radius1=4.2 * s, depth=5 * s, location=(dx, dy, 40.5 * s), rotation=(0, 0, a + math.pi / 4))
        prim("uv_sphere", M_BRASS, True, radius=0.6 * s, segments=10, ring_count=6, location=(dx, dy, 43.3 * s))
    if crown:
        top = 29 * s + (R + 0.5 * s) * 0.82
        cyl(cx, cy, top - 2 * s, 5 * s, 6 * s, M_STUCCO, 24)
        half_dome(cx, cy, top + 4 * s, 5.4 * s, 0.9, M_PATINA, 24)
        prim("torus", M_BRASS, True, major_radius=5.3 * s, minor_radius=0.35 * s, location=(cx, cy, top + 4 * s))
        prim("cone", M_PATINA, True, vertices=24, radius1=2.8 * s, depth=16 * s, location=(cx, cy, top + 16 * s))
        prim("uv_sphere", M_BRASS, True, radius=1.6 * s, location=(cx, cy, top + 9 * s))
        cyl(cx, cy, top + 22 * s, 0.25 * s, 22 * s, M_METAL, 8, False)          # antenna mast
        for k in range(3):
            prim("torus", M_RING, True, major_radius=(2.6 - k * 0.6) * s, minor_radius=0.12 * s,
                 location=(cx, cy, top + (27 + k * 5) * s))
        prim("uv_sphere", M_ALARM if ALARM else M_LAMP, True, radius=0.6 * s, location=(cx, cy, top + 44 * s))
    if with_door:
        fy = cy - R
        box(cx, fy - 2.5 * s, 2 * s, 16 * s, 8 * s, 16 * s, M_STUCCO, "porch")
        box(cx, fy - 6.4 * s, 2 * s, 10 * s, 0.6 * s, 11 * s, M_DARK, "door")
        upper_half(prim("torus", M_STUCCO, True, major_radius=6.6 * s, minor_radius=1.5 * s, location=(0, 0, 0)),
                   (cx, fy - 6.9 * s, 13 * s))
        upper_half(prim("cylinder", M_DARK, False, vertices=32, radius=5.2 * s, depth=0.8 * s, location=(0, 0, 0)),
                   (cx, fy - 6.5 * s, 13 * s))
        # scalloped trim on the arch (small brass beads)
        for k in range(11):
            a = math.pi * k / 10
            prim("uv_sphere", M_BRASS, True, radius=0.45 * s, segments=8, ring_count=6,
                 location=(cx + math.cos(a) * 8.2 * s, fy - 7.6 * s, 13 * s + math.sin(a) * 8.2 * s))
        for sx_ in (-1, 1):
            box(cx + sx_ * 7.4 * s, fy - 7 * s, 2 * s, 1.8 * s, 1.8 * s, 11 * s, M_BLUE, "pil")
            prim("uv_sphere", M_BRASS, True, radius=1.2 * s, location=(cx + sx_ * 7.4 * s, fy - 7 * s, 13.6 * s))
    return 29 * s + (R + 0.5 * s) * 0.82 + 44 * s

hero_top = domed_hall(HERO[0], HERO[1], 1.0)
domed_hall(DOME2[0], DOME2[1], 0.62, with_door=False, crown=True)
cyl(HERO[0], HERO[1], 0, 44, 0.15, M_STONE, 64)  # plaza paving

# banner poles + lanterns at the hero porch (the reference's red standards)
for sx_ in (-1, 1):
    px, py = HERO[0] + sx_ * 13, HERO[1] - 26 - 12
    cyl(px, py, 0, 0.25, 14, M_BRASS, 8, False)
    box(px, py, 8.5, 0.2, 2.2, 4.5, M_BANNER, "banner", 0.0)
    prim("uv_sphere", M_BRASS, True, radius=0.7, location=(px, py, 14.2))

# people for scale
for k in range(34):
    if k < 14:
        x = HERO[0] + rng.uniform(-14, 14); y = HERO[1] - 26 - rng.uniform(10, 26)
    else:
        x = rng.uniform(-110, 60); y = rng.uniform(-19, -6)
    s = rng.uniform(0.9, 1.1)
    body = prim("cone", M_PEOPLE, True, vertices=10, radius1=0.45 * s, radius2=0.2 * s, depth=1.5 * s, location=(x, y, 0.75 * s))
    prim("uv_sphere", M_PEOPLE, True, radius=0.2 * s, segments=10, ring_count=6, location=(x, y, 1.75 * s))

# street lamps along the quay
lamp_pos = []
for k in range(24):
    x = -200 + k * 18 + rng.uniform(-2, 2)
    cyl(x, -18.5, 0, 0.15, 6, M_METAL, 6, False)
    prim("uv_sphere", M_LAMP, True, radius=0.45, segments=10, ring_count=6, location=(x, -18.5, 6.2))
    lamp_pos.append((x, -18.5, 6.0))

# ground traffic (dark cars by day, light streaks by night)
for k in range(260):
    if rng.random() < 0.5:
        x = 36 * rng.randint(-8, 8) + rng.choice([-2.2, 2.2]); y = rng.uniform(-12, 420); along = "y"
    else:
        y = 36 * rng.randint(0, 11) - 10 + rng.choice([-2.2, 2.2]); x = rng.uniform(-300, 300); along = "x"
    if blocked(x, y, -6):
        continue
    L = rng.uniform(2.5, 4.5)
    sx, sy = (L, 1.6) if along == "x" else (1.6, L)
    box(x, y, 0.2, sx, sy, 1.2, M_METAL, "car")
    if NIGHT:
        st = rng.uniform(4, 10)
        box(x, y, 0.4, sx if along == "x" else 1.0, sy if along == "y" else 1.0, 0.25,
            M_HEAD if rng.random() < 0.5 else M_TAIL, "trail")
    else:
        rng.uniform(4, 10); rng.random()

# flying traffic lanes
for k in range(40):
    x = rng.uniform(-220, 260); y = rng.uniform(40, 520); z = rng.uniform(26, 80)
    box(x, y, z, 3.2, 1.6, 1.0, M_METAL, "flyer", rng.uniform(0, math.tau))
    box(x, y, z - 0.25, 1.0, 1.0, 0.2, M_HEAD if NIGHT else M_METAL, "flylight")

# foreground framing: rusted relay mast with dish and cables at the left (the reference's agave)
mx, my = -46.0, -92.0
cyl(mx, my, -4, 0.8, 60, M_RUST, 10, False)
for k in range(6):
    box(mx, my, 8 + k * 9, 6, 0.4, 0.4, M_RUST, "strut", k * 0.7)
d = half_dome(mx + 3, my + 1, 44, 5.0, 0.35, M_METAL, 24)
d.rotation_euler = (math.radians(110), 0, math.radians(-30))
box(mx + 1.5, my, 30, 0.3, 3, 9, M_BANNER, "fgbanner")

# ---------------------------------------------------------------- suspicion: helicopters, drones, searchlights
alarm_info = {"helis": [], "drones": []}
if ALARM:
    arng = random.Random(4242)
    heli_spots = [((-60, 150, 95), (-40, 70, 0)), ((150, 220, 120), (90, 120, 0)), ((20, 40, 70), (30, 0, 0)),
                  ((-190, 330, 140), (-150, 240, 0))]
    for (hp, tp) in heli_spots:
        hx, hy, hz = hp
        box(hx, hy, hz, 7, 3, 2.6, M_METAL, "heli")
        box(hx - 6, hy, hz + 1, 7, 0.6, 0.6, M_METAL, "tail")
        cyl(hx, hy, hz + 2.6, 7, 0.08, M_METAL, 24, False)
        prim("uv_sphere", M_ALARM, True, radius=0.5, location=(hx + 3.5, hy, hz))
        sp = bpy.data.lights.new("search", "SPOT"); sp.energy = 3.5e6; sp.spot_size = math.radians(9)
        sp.spot_blend = 0.4; sp.color = (0.85, 0.92, 1.0)
        so = bpy.data.objects.new("search", sp); link(so)
        so.location = (hx, hy, hz - 1.5)
        dvec = Vector(tp) - Vector(so.location)
        so.rotation_euler = dvec.to_track_quat("-Z", "Y").to_euler()
        alarm_info["helis"].append({"src": list(so.location), "dst": list(tp)})
    for k in range(14):
        x = arng.uniform(-150, 180); y = arng.uniform(0, 300); z = arng.uniform(25, 75)
        box(x, y, z, 1.6, 1.6, 0.5, M_METAL, "drone")
        prim("uv_sphere", M_ALARM if k % 2 == 0 else M_NEON[3], True, radius=0.35, location=(x, y, z - 0.3))
        alarm_info["drones"].append([x, y, z])
    for k in range(10):
        x = arng.uniform(-150, 160); y = arng.uniform(0, 250)
        pl = bpy.data.lights.new("alarm", "POINT"); pl.energy = 14000; pl.color = (1.0, 0.1, 0.05)
        pl.use_shadow = False
        po = bpy.data.objects.new("alarm", pl); link(po); po.location = (x, y, 18)

# ---------------------------------------------------------------- lights & world
sun = bpy.data.lights.new("sun", "SUN")
so = bpy.data.objects.new("sun", sun); link(so)
so.rotation_euler = (math.radians(58), 0, math.radians(-38))
world = bpy.data.worlds.new("w"); scene.world = world; world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
if MODE == "day":
    sun.energy = 3.2; sun.color = (1.0, 0.80, 0.55); sun.angle = math.radians(2)
    bg.inputs["Color"].default_value = (0.30, 0.45, 0.85, 1); bg.inputs["Strength"].default_value = 0.55
elif MODE == "night":
    sun.energy = 0.35; sun.color = (0.45, 0.6, 1.0)
    bg.inputs["Color"].default_value = (0.03, 0.05, 0.12, 1); bg.inputs["Strength"].default_value = 1.0
elif MODE == "alarm":
    sun.energy = 0.25; sun.color = (0.5, 0.55, 1.0)
    bg.inputs["Color"].default_value = (0.07, 0.02, 0.05, 1); bg.inputs["Strength"].default_value = 1.0
else:
    sun.energy = 0.0; bg.inputs["Strength"].default_value = 0.0

if NIGHT:
    for (x, y, z) in lamp_pos:
        pl = bpy.data.lights.new("lamp", "POINT"); pl.energy = 1500; pl.color = (1.0, 0.7, 0.4); pl.use_shadow = False
        po = bpy.data.objects.new("lamp", pl); link(po); po.location = (x, y, z - 0.6)
    # warm interior spill from the hero doorway, cool uplight on the dome
    for (loc, en, col) in [((HERO[0], HERO[1] - 36, 8), 5000, (1.0, 0.55, 0.25)),
                           ((HERO[0] - 30, HERO[1] - 40, 4), 7000, (0.2, 0.9, 1.0) if not ALARM else (1.0, 0.1, 0.05)),
                           ((HERO[0] + 34, HERO[1] - 30, 4), 7000, (1.0, 0.3, 0.7) if not ALARM else (1.0, 0.15, 0.05))]:
        pl = bpy.data.lights.new("fx", "POINT"); pl.energy = en; pl.color = col; pl.use_shadow = False
        po = bpy.data.objects.new("fx", pl); link(po); po.location = loc
    for k in range(18):
        b_ = buildings[(k * 37) % len(buildings)]
        pl = bpy.data.lights.new("street", "POINT"); pl.energy = 6000; pl.color = NEON_C[k % 4]; pl.use_shadow = False
        po = bpy.data.objects.new("street", pl); link(po); po.location = (b_[0], b_[1] - b_[3] / 2 - 4, 5)

# ---------------------------------------------------------------- camera
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 26; cam_d.clip_end = 4000
cam = bpy.data.objects.new("cam", cam_d); link(cam)
cam.location = (8.0, -172.0, 58.0)
cam.rotation_euler = (math.radians(90 - 8.0), 0, math.radians(-4))
scene.camera = cam

# ---------------------------------------------------------------- render settings
try:
    scene.render.engine = "BLENDER_EEVEE"
except TypeError as e:
    print("ENGINE", e)
ee = scene.eevee
ee.taa_render_samples = SAMPLES if not DEPTH else 1
for attr, val in (("use_raytracing", True), ("use_shadows", True), ("shadow_ray_count", 2), ("shadow_step_count", 8)):
    if hasattr(ee, attr) and not DEPTH:
        try:
            setattr(ee, attr, val)
        except Exception:
            pass
scene.render.resolution_x = W; scene.render.resolution_y = H; scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
try:
    scene.view_settings.view_transform = "Standard"
except Exception as e:
    print("VT", e)
scene.view_settings.look = "None"
if DEPTH:
    scene.view_layers[0].material_override = depth_mat()
    try:
        scene.view_settings.view_transform = "Raw"
    except Exception as e:
        print("RAW", e)
if hasattr(scene.render, "filter_size") and DEPTH:
    scene.render.filter_size = 0.01
scene.render.filepath = OUT
bpy.context.view_layer.update()

# ---------------------------------------------------------------- overlay projection data
def proj(p):
    co = world_to_camera_view(scene, cam, Vector(p))
    return [co.x * W, (1 - co.y) * H, co.z]

if JSON_OUT:
    data = {"W": W, "H": H, "DMAX": DMAX, "nodes": [], "paths": [], "here": HERE}
    for (x, y, kind, label) in NODES:
        ring = [proj((x + math.cos(t / 48 * math.tau) * 6.5, y + math.sin(t / 48 * math.tau) * 6.5, 0.4)) for t in range(48)]
        data["nodes"].append({"c": proj((x, y, 0.4)), "ring": ring, "kind": kind, "label": label,
                              "top": proj((x, y, 9.0))})
    NXY = {i: (n[0], n[1]) for i, n in enumerate(NODES)}
    for (a, b_, corners) in EDGES:
        pts = [NXY[a]] + corners + [NXY[b_]]
        samples = []
        for (p0, p1) in zip(pts[:-1], pts[1:]):
            L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); n = max(2, int(L / 0.8))
            for t in range(n):
                f = t / n
                samples.append(proj((p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f, 0.4)))
        samples.append(proj((pts[-1][0], pts[-1][1], 0.4)))
        data["paths"].append({"a": a, "b": b_, "pts": samples})
    data["helis"] = [{"src": proj(h["src"]), "dst": proj(h["dst"]),
                      "dst_ring": [proj((h["dst"][0] + math.cos(t / 32 * math.tau) * 10, h["dst"][1] + math.sin(t / 32 * math.tau) * 10, 0.3)) for t in range(32)]}
                     for h in alarm_info["helis"]]
    data["drones"] = [proj(d_) for d_ in alarm_info["drones"]]
    data["hero_top"] = proj((HERO[0], HERO[1], hero_top))
    data["cam_loc"] = list(cam.location)
    with open(JSON_OUT, "w") as f:
        json.dump(data, f)

bpy.ops.render.render(write_still=True)
print("DONE", MODE, OUT)
