"""Solace netrun street, one procedural district, three cameras (district f2, street f3, HQ f4).
Run: blender -b -P nr_scene.py -- <frame f2|f3|f4> <out.png> <samples> <res_pct> [seed]
Everything is emissive flat colour (cel); windows are a world-space shader grid; detail geometry
is added per LOD: 0 city (rims, masts), 1 district (+ground strips, billboards, towers), 2 street (+shops, signs, escapes).
"""
import bpy, sys, math, random, os
import bmesh
from mathutils import Vector, Matrix

A = sys.argv[sys.argv.index('--') + 1:]
FRAME = A[0]; OUT = A[1]; SAMPLES = int(A[2]); RESPCT = int(A[3]); SEED = int(A[4]) if len(A) > 4 else 7
R = random.Random(SEED)

# ------------------------------------------------------------------ colour helpers
def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def hexc(h, k=1.0, a=1.0):
    h = h.lstrip('#')
    r, g, b = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return (lin(r) * k, lin(g) * k, lin(b) * k, a)

CORP = {
    'solace':   dict(rim='#96FF46', body='#2a5a62', body2='#2a2c58', win='#B8FF78', acc='#FF4696'),
    'halcyon':  dict(rim='#B06EFF', body='#4a3a8a', body2='#33285e', win='#D3B0FF', acc='#FFAA28'),
    'orbital':  dict(rim='#CDF0FF', body='#34506f', body2='#2a3a5c', win='#E6F8FF', acc='#9fd8ff'),
    'meridian': dict(rim='#FF8C1A', body='#74363a', body2='#522a40', win='#FFC878', acc='#FF2E28'),
    'rebel':    dict(rim='#FF2E3A', body='#6a2444', body2='#481a3c', win='#FF9AA0', acc='#FFB0C8'),
    'aurelian': dict(rim='#29DBA6', body='#6e5a5a', body2='#4a3d4c', win='#FFE7B8', acc='#E9D5AA'),
}
HQ = Vector((118.0, -7.0, 0))
_CC = [0]
PAT = ['solace', 'solace', 'halcyon', 'solace', 'orbital', 'solace', 'solace', 'meridian', 'solace', 'rebel', 'solace', 'aurelian', 'solace', 'halcyon']
def corp_for(x, y):
    d = (Vector((x, y, 0)) - HQ).length
    _CC[0] += 1
    c = PAT[(_CC[0] * 5) % len(PAT)]
    if d < 90 and c != 'solace' and (_CC[0] % 3):
        c = 'solace'
    return c

# ------------------------------------------------------------------ geometry accumulators
class Acc:
    def __init__(self, name):
        self.name = name; self.v = []; self.f = []; self.c = []; self.w = []
    def add_poly(self, pts, faces, col, win=(0, 0, 0, 0.5)):
        o = len(self.v)
        self.v += pts; self.f += [tuple(i + o for i in fc) for fc in faces]
        self.c += [col] * len(pts); self.w += [win] * len(pts)
ACC = {k: Acc(k) for k in ('body', 'far', 'solid', 'flat', 'ground', 'ink', 'glow')}
CAMLOC = {'f2': (-75.0, -8.0, 66.0), 'f3': (-6.0, -68.0, 22.0), 'f4': (-8.0, -9.5, 11.0)}[FRAME]
INK_PX = float(os.environ.get('NR_INKPX', '2.0'))
INK_JIT = random.Random(99)
def ink_t(cx, cy, cz, k=1.0):
    d = math.sqrt((cx - CAMLOC[0]) ** 2 + (cy - CAMLOC[1]) ** 2 + (cz - CAMLOC[2]) ** 2)
    return max(0.03, 0.00075 * d * INK_PX * k)

BOXF = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
def box(acc, x0, x1, y0, y1, z0, z1, col, win=(0, 0, 0, 0.5)):
    p = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    ACC[acc].add_poly(p, BOXF, col, win)
    if acc in ('body', 'far', 'solid') and INK_PX > 0:
        t = ink_t((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, 1.0 if acc != 'solid' else 0.7)
        j = lambda: INK_JIT.uniform(-0.35, 0.35) * t
        xs = (x0 - t, x1 + t); ys = (y0 - t, y1 + t); zs = (z0 - t if z0 > 0.5 else -0.3, z1 + t)
        hp = [(xs[0] + j(), ys[0] + j(), zs[0]), (xs[1] + j(), ys[0] + j(), zs[0]), (xs[1] + j(), ys[1] + j(), zs[0]), (xs[0] + j(), ys[1] + j(), zs[0]),
              (xs[0] + j(), ys[0] + j(), zs[1] + j()), (xs[1] + j(), ys[0] + j(), zs[1] + j()), (xs[1] + j(), ys[1] + j(), zs[1] + j()), (xs[0] + j(), ys[1] + j(), zs[1] + j())]
        ACC['ink'].add_poly(hp, BOXF, (0, 0, 0, 1))
def beam(acc, p0, p1, t, col, hint=(0, 0, 1)):
    p0 = Vector(p0); p1 = Vector(p1); d = (p1 - p0)
    if d.length < 1e-6: return
    d.normalize(); h = Vector(hint)
    if abs(d.dot(h)) > 0.95: h = Vector((1, 0, 0))
    a = d.cross(h).normalized() * t / 2; b = d.cross(a).normalized() * t / 2
    P = []
    for q in (p0, p1):
        for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            P.append(tuple(q + a * sa + b * sb))
    ACC[acc].add_poly(P, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], col)
def light_beam(base, d, L, w, col, a0=0.55):
    base = Vector(base); d = Vector(d).normalized(); side = d.cross(Vector((0, 0, 1))).normalized(); tip = base + d * L
    for sv in (side, Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))):
        pts = [tuple(base - sv * w * .5), tuple(base + sv * w * .5), tuple(tip + sv * w * 3.0), tuple(tip - sv * w * 3.0)]
        ACC['glow'].v += pts; o = len(ACC['glow'].v) - 4; ACC['glow'].f += [(o, o + 1, o + 2, o + 3), (o + 3, o + 2, o + 1, o)]
        ACC['glow'].c += [(col[0], col[1], col[2], a0), (col[0], col[1], col[2], a0), (col[0], col[1], col[2], 0.0), (col[0], col[1], col[2], 0.0)]
        ACC['glow'].w += [(a0, 0, 0, 1), (a0, 0, 0, 1), (0, 0, 0, 1), (0, 0, 0, 1)]
def quad_flat(acc, pts, col):
    ACC[acc].add_poly(pts, [(0, 1, 2, 3)], col)

# template meshes (flat faces) for blobs / cylinders
def template_ico(sub=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    V = [v.co.copy() for v in bm.verts]; F = [[V[v.index] for v in f.verts] for f in bm.faces]; bm.free(); return F
ICO = template_ico(1)
def add_blob(acc, c, sx, sy, sz, colfn):
    for tri in ICO:
        pts = [(c[0] + v.x * sx, c[1] + v.y * sy, c[2] + v.z * sz) for v in tri]
        n = (tri[0] + tri[1] + tri[2]).normalized()
        ACC[acc].add_poly(pts, [(0, 1, 2)], colfn(n))
def add_cyl(acc, c, r, h, col, n=10, col_top=None):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n; pts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a), c[2]))
    for i in range(n):
        a = 2 * math.pi * i / n; pts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a), c[2] + h))
    faces = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    faces.append(tuple(reversed(range(n)))); faces.append(tuple(range(n, 2 * n)))
    ACC[acc].add_poly(pts, faces, col)
def add_cone(acc, c, r, h, col, n=10):
    pts = [(c[0] + r * math.cos(2 * math.pi * i / n), c[1] + r * math.sin(2 * math.pi * i / n), c[2]) for i in range(n)]
    pts.append((c[0], c[1], c[2] + h))
    ACC[acc].add_poly(pts, [(i, (i + 1) % n, n) for i in range(n)] + [tuple(reversed(range(n)))], col)
def add_ring(acc, c, r0, r1, col, n=40, z=0.05, a0=0, a1=2 * math.pi):
    for i in range(n):
        t0 = a0 + (a1 - a0) * i / n; t1 = a0 + (a1 - a0) * (i + 1) / n
        quad_flat(acc, [(c[0] + r0 * math.cos(t0), c[1] + r0 * math.sin(t0), z), (c[0] + r1 * math.cos(t0), c[1] + r1 * math.sin(t0), z),
                        (c[0] + r1 * math.cos(t1), c[1] + r1 * math.sin(t1), z), (c[0] + r0 * math.cos(t1), c[1] + r0 * math.sin(t1), z)], col)
        ACC[acc].f[-1] = tuple(reversed(ACC[acc].f[-1]))  # face up

# ------------------------------------------------------------------ text
FONTS = {}
def font(name):
    if name not in FONTS:
        p = {'imp': 'C:/Windows/Fonts/impact.ttf', 'jp': 'C:/Windows/Fonts/YuGothB.ttc', 'bah': 'C:/Windows/Fonts/bahnschrift.ttf', 'ari': 'C:/Windows/Fonts/arialbd.ttf'}[name]
        FONTS[name] = bpy.data.fonts.load(p)
    return FONTS[name]
TEXT_MATS = {}
def text_mat(col):
    key = tuple(round(c, 3) for c in col)
    if key not in TEXT_MATS:
        m = bpy.data.materials.new('txt'); m.use_nodes = True
        nt = m.node_tree; nt.nodes.clear()
        e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value = col; e.inputs['Strength'].default_value = 1.0
        o = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(e.outputs[0], o.inputs[0])
        TEXT_MATS[key] = m
    return TEXT_MATS[key]
TEXT_COLL = None
def add_text(txt, pos, size, col, facing, fnt='imp', extrude=0.03, align='CENTER'):
    """facing: 'N' toward -y, 'S' toward +y, 'E' toward +x, 'W' toward -x"""
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = txt; cu.size = size; cu.font = font(fnt)
    cu.extrude = extrude; cu.align_x = align; cu.align_y = 'CENTER'; cu.space_line = 0.85
    ob = bpy.data.objects.new('t', cu); ob.data.materials.append(text_mat(col))
    rz = {'N': 0, 'S': math.pi, 'E': math.pi / 2, 'W': -math.pi / 2}[facing]
    ob.rotation_euler = (math.pi / 2, 0, rz); ob.location = pos
    TEXT_COLL.objects.link(ob)

# ------------------------------------------------------------------ names
SOLACE_NAMES = ['SOLACE', 'LEAFLET', 'HELIX', 'CHLORO', 'BIO-TEA', 'PETAL', 'SPORE BAR', 'VIRIDIAN', 'GENEBAR', 'CLINIC 24', 'SOLACE RX', 'FERN', 'CELLS', 'SAP', 'ALGAE', 'MOSS']
OTHER_NAMES = ['NOODLE', 'KARAOKE', 'ARCADE', 'PAWN', 'VOLTA', 'ORBIT', 'DATA', 'TEA', 'SUSHI', 'HOTEL', 'OPEN 24', 'PHARMA', 'BAR', 'RAMEN']
JP = ['ソラス', '葉', '薬', '茶', '24', '営業中', 'ラーメン', '酒', '遺伝子', 'カラオケ']
WARM = '#FFE0A0'; CYAN = '#5EF0FF'; PINK = '#FF4696'; AMBER = '#FFAA28'; LIME = '#96FF46'
SHOPCOLS = [WARM, WARM, CYAN, PINK, LIME, AMBER, '#FFFFFF']

# ------------------------------------------------------------------ building
FOCUS = None
def lod_at(x, y):
    cx, cy, r2, r1 = FOCUS
    d = math.hypot(x - cx, y - cy)
    return 2 if d < r2 else (1 if d < r1 else 0)

def building(x0, x1, yf, depth, h, f, corp_name=None, lod=None, tall_far=False, dim=1.0):
    """f=-1: front faces -y (north row, front plane y=yf, body extends +y). f=+1: front faces +y (south row, body extends -y)."""
    cx = (x0 + x1) / 2
    y_a, y_b = (yf, yf + depth) if f == -1 else (yf - depth, yf)
    cn = corp_name or corp_for(cx, yf)
    P = CORP[cn]
    if lod is None: lod = lod_at(cx, yf)
    body = hexc(P['body'] if R.random() < 0.7 else P['body2'])
    body = (body[0] * dim, body[1] * dim, body[2] * dim, 1)
    winc = hexc(P['win'])
    accname = 'body' if lod >= 1 else 'far'
    lit = R.uniform(0.1, 0.3) * (0.7 if dim < 1 else 1.0)
    htop = h
    ACC_ON = R.random() < (0.42 if cn == 'solace' else 0.28) and dim >= 0.6
    ACC_KIND = R.choice(['parapet', 'corner', 'crown'])
    if h > 26 and R.random() < 0.65:
        h = h * R.uniform(0.42, 0.62)
        ins = R.uniform(1.2, 2.6); setb = R.uniform(1.5, 4.0)
        ua, ub = (y_a + setb, y_b) if f == -1 else (y_a, y_b - setb)
        ufy = (ua if f == -1 else ub) + f * 0.10
        box(accname, x0 + ins, x1 - ins, ua, ub, h, htop, body, (winc[0], winc[1], winc[2], lit))
        urim = hexc(P['rim'], 3.2)
        if ACC_ON and ACC_KIND in ('crown', 'parapet'):
            beam('flat', (x0 + ins, ufy, htop), (x1 - ins, ufy, htop), 0.16, urim)
            if ACC_KIND == 'crown':
                beam('flat', (x0 + ins, ufy, htop - 1.6), (x1 - ins, ufy, htop - 1.6), 0.1, urim)
        if ACC_ON and ACC_KIND == 'corner':
            beam('flat', (x0 + ins, ufy, h), (x0 + ins, ufy, htop), 0.14, urim)
        mh = R.uniform(3, 12); mx = (x0 + x1) / 2; my = (ua + ub) / 2
        beam('flat', (mx, my, htop), (mx, my, htop + mh), 0.18, hexc('#10081c'))
        box('flat', mx - .3, mx + .3, my - .3, my + .3, htop + mh, htop + mh + .6, hexc(R.choice(['#FF3030', P['acc']]), 5))
    box(accname, x0, x1, y_a, y_b, 0, h, body, (winc[0], winc[1], winc[2], lit))
    rim = hexc(P['rim'], 3.2)
    rimdim = hexc(P['rim'], 2.0)
    ff = yf  # front plane
    o = -f * 0.0  # outward sign n: toward street
    n = -1 if f == -1 else 1   # outward direction along y for front... front plane faces n
    nn = f  # f=-1 -> outward -y ; f=+1 -> outward +y  (nn is the outward y sign)
    fy = ff + nn * 0.10
    th = 0.16
    # parapet rim and corner rims (city LOD and up)
    if ACC_ON:
        if ACC_KIND == 'parapet':
            beam('flat', (x0, fy, h), (x1, fy, h), th, rim)
        elif ACC_KIND == 'corner':
            cxe = x0 + 0.1 if R.random() < .5 else x1 - 0.1
            beam('flat', (cxe, fy, 1.0), (cxe, fy, h), th, rim)
        else:
            beam('flat', (x0, fy, h), (x1, fy, h), th, rim); beam('flat', (x0, fy, h - 1.4), (x1, fy, h - 1.4), 0.1, rimdim)
    # mast / roof
    if lod == 0 or (h > 40 and R.random() < 0.7):
        mh = R.uniform(4, 14)
        beam('flat', ((x0 + x1) / 2, (y_a + y_b) / 2, h), ((x0 + x1) / 2, (y_a + y_b) / 2, h + mh), 0.18, hexc('#10081c'))
        box('flat', (x0 + x1) / 2 - .28, (x0 + x1) / 2 + .28, (y_a + y_b) / 2 - .28, (y_a + y_b) / 2 + .28, h + mh, h + mh + .6, hexc(P['acc'] if R.random() < .5 else '#FF3030', 5))
    if lod == 0:
        return
    # ---- LOD1: ground strip glow, roof billboard, water tower
    ww = x1 - x0
    shopc = hexc(R.choice(SHOPCOLS), 2.2)
    box('flat', x0 + 0.4, x1 - 0.4, fy - 0.0 if f == 1 else fy - 0.12, fy + 0.0 if f == -1 else fy + 0.12, 0.3, 3.3, shopc) if False else None
    # (street LOD adds real shop bays; LOD1 gets a lit strip)
    if lod == 1:
        zc = (0.5, 3.4)
        box('flat', x0 + 0.5, x1 - 0.5, min(fy, fy + nn * 0.05), max(fy, fy + nn * 0.05), zc[0], zc[1], shopc)
        if h > 14 and R.random() < 0.45:
            bw = min(ww - 2, R.uniform(3.5, 6)); bz = h + 0.5
            ac = hexc(R.choice([P['acc'], P['rim'], '#FFAA28']), 2.6)
            box('solid', cx - bw / 2, cx + bw / 2, (y_a + y_b) / 2 - 0.2, (y_a + y_b) / 2 + 0.2, bz, bz + 2.6, hexc('#140a22'))
            box('flat', cx - bw / 2 + 0.2, cx + bw / 2 - 0.2, (y_a + y_b) / 2 - 0.22, (y_a + y_b) / 2 - 0.2, bz + 0.2, bz + 2.4, ac)
        return
    # ---------------- LOD2 street detail (front face) ----------------
    street_detail(x0, x1, y_a, y_b, fy, nn, h, P, cn)

ICONS = ['cross', 'ring', 'leaf', 'drop', 'bars', 'helix', 'pill', 'bowl']
def vring(cx, y, z, r0, r1, col, n=20, a0=0.0, a1=2 * math.pi):
    for i in range(n):
        t0 = a0 + (a1 - a0) * i / n; t1 = a0 + (a1 - a0) * (i + 1) / n
        quad_flat('flat', [(cx + r0 * math.cos(t0), y, z + r0 * math.sin(t0)), (cx + r1 * math.cos(t0), y, z + r1 * math.sin(t0)),
                           (cx + r1 * math.cos(t1), y, z + r1 * math.sin(t1)), (cx + r0 * math.cos(t1), y, z + r0 * math.sin(t1))], col)
def icon(kind, cx, fy, nn, z, sz, col, depth=0.34):
    y = fy + nn * depth; t = max(0.07, sz * 0.12)
    if kind == 'cross':
        beam('flat', (cx - sz * .5, y, z), (cx + sz * .5, y, z), t * 1.6, col); beam('flat', (cx, y, z - sz * .5), (cx, y, z + sz * .5), t * 1.6, col)
    elif kind == 'ring':
        vring(cx, y, z, sz * .38, sz * .5, col); vring(cx, y, z, 0.0, sz * .16, col, 10)
    elif kind == 'leaf':
        pts = [(cx, z + sz * .55), (cx + sz * .34, z), (cx, z - sz * .55), (cx - sz * .34, z)]
        for a, b in zip(pts, pts[1:] + pts[:1]): beam('flat', (a[0], y, a[1]), (b[0], y, b[1]), t, col)
        beam('flat', (cx, y, z - sz * .55), (cx, y, z + sz * .3), t * .8, col)
    elif kind == 'drop':
        beam('flat', (cx, y, z + sz * .55), (cx - sz * .32, y, z - sz * .1), t, col); beam('flat', (cx, y, z + sz * .55), (cx + sz * .32, y, z - sz * .1), t, col)
        vring(cx, y, z - sz * .12, sz * .22, sz * .34, col, 14, math.pi, 2 * math.pi)
    elif kind == 'bars':
        for i, hh in enumerate((.5, .95, .7)):
            xx = cx + (i - 1) * sz * .3; beam('flat', (xx, y, z - sz * .5), (xx, y, z - sz * .5 + sz * hh), sz * .17, col)
    elif kind == 'helix':
        prev = [None, None]
        for i in range(9):
            tt = i / 8; zz = z - sz * .5 + sz * tt; dx = math.sin(tt * 2 * math.pi * 1.2) * sz * .26
            for k, sg in enumerate((1, -1)):
                p1 = (cx + sg * dx, y, zz)
                if prev[k]: beam('flat', prev[k], p1, t, col)
                prev[k] = p1
            if i % 2 == 0: beam('flat', (cx - dx, y, zz), (cx + dx, y, zz), t * .6, col)
    elif kind == 'pill':
        beam('flat', (cx - sz * .3, y, z - sz * .12), (cx + sz * .3, y, z + sz * .12), sz * .3, col)
    else:  # bowl
        vring(cx, y, z, sz * .3, sz * .42, col, 14, math.pi, 2 * math.pi)
        for k in (-1, 0, 1): beam('flat', (cx + k * sz * .18, y, z + sz * .08), (cx + k * sz * .18, y, z + sz * .45), t * .7, col)

def big_sign(cx, y, z, w, hgt, nn, text, kind, col, panel_hex, size):
    face = facing_of(nn)
    box('solid', cx - w / 2, cx + w / 2, y - .2, y + .2, z - hgt / 2, z + hgt / 2, hexc('#120a20'))
    yy = y + nn * 0.23
    ph = hexc(panel_hex, 1.5)
    quad_flat('flat', [(cx - w / 2 + .25, yy, z - hgt / 2 + .25), (cx + w / 2 - .25, yy, z - hgt / 2 + .25), (cx + w / 2 - .25, yy, z + hgt / 2 - .25), (cx - w / 2 + .25, yy, z + hgt / 2 - .25)], ph)
    yy2 = yy + nn * 0.03
    for (a, b) in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
        beam('flat', (cx + a[0] * w / 2, yy2, z + a[1] * hgt / 2), (cx + b[0] * w / 2, yy2, z + b[1] * hgt / 2), 0.14, col)
    icon(kind, cx - w * 0.5 + hgt * .55, y, nn, z, hgt * .6, hexc('#FFFFFF', 3.2), depth=0.27)
    add_text(text, (cx + hgt * 0.3, y + nn * 0.28, z), size, hexc('#FFFFFF', 3.4), face, 'imp')

def facing_of(nn):
    return 'N' if nn == -1 else 'S'

def sign_board(cx, fy, nn, z, w, hgt, text, tcol, rimcol, bcol='#140a22', fnt='imp', size=None, vertical=False, depth=0.28, icon_kind=None):
    yb0 = fy; yb1 = fy + nn * depth
    box('solid', cx - w / 2, cx + w / 2, min(yb0, yb1), max(yb0, yb1), z - hgt / 2, z + hgt / 2, hexc(bcol))
    yy = fy + nn * (depth + 0.02)
    t = 0.09
    beam('flat', (cx - w / 2, yy, z - hgt / 2), (cx + w / 2, yy, z - hgt / 2), t, rimcol)
    beam('flat', (cx - w / 2, yy, z + hgt / 2), (cx + w / 2, yy, z + hgt / 2), t, rimcol)
    beam('flat', (cx - w / 2, yy, z - hgt / 2), (cx - w / 2, yy, z + hgt / 2), t, rimcol)
    beam('flat', (cx + w / 2, yy, z - hgt / 2), (cx + w / 2, yy, z + hgt / 2), t, rimcol)
    if size is None: size = hgt * 0.62 if not vertical else min(w * 0.7, hgt / max(len(text), 1) * 0.9)
    if icon_kind and not vertical:
        icon(icon_kind, cx + w / 2 - hgt * 0.55, fy, nn, z, hgt * 0.62, tcol, depth=depth + 0.03)
        add_text(text, (cx - hgt * 0.3, fy + nn * (depth + 0.05), z), size * 0.9, tcol, facing_of(nn), fnt)
    else:
        add_text(text, (cx, fy + nn * (depth + 0.05), z), size, tcol, facing_of(nn), fnt)

def street_detail(x0, x1, y_a, y_b, fy, nn, h, P, cn):
    ww = x1 - x0
    # ---- storefront bays
    nb = max(1, int(ww // R.uniform(3.6, 5.2))); bw = ww / nb
    names = SOLACE_NAMES if cn == 'solace' else OTHER_NAMES
    if cn == 'solace' and R.random() < 0.3: names = OTHER_NAMES + SOLACE_NAMES
    for i in range(nb):
        bx0 = x0 + i * bw; bx1 = bx0 + bw; bc = (bx0 + bx1) / 2
        kind = R.random()
        wc = R.choice(SHOPCOLS)
        shopc = hexc(wc, 2.6)
        zb0 = 0.4; zb1 = 3.5
        fo = 0.12 * nn
        if kind < 0.18:
            # shutter / door bay: dark ribbed, small lit door
            box('solid', bx0 + .2, bx1 - .2, min(fy, fy + fo), max(fy, fy + fo), 0.0, 3.6, hexc('#241833'))
            for k in range(7):
                zz = 0.4 + k * 0.45
                beam('flat', (bx0 + .3, fy + nn * 0.14, zz), (bx1 - .3, fy + nn * 0.14, zz), 0.04, hexc('#5a3a80', 1.0))
            box('flat', bc - .5, bc + .5, min(fy, fy + nn * 0.15), max(fy, fy + nn * 0.15), 0.1, 2.5, shopc)
        else:
            # lit shop window with goods shelves
            box('flat', bx0 + .25, bx1 - .25, min(fy, fy + nn * .13), max(fy, fy + nn * .13), zb0, zb1, shopc)
            quad_flat('flat', [(bx0 + .2, fy + nn * .3, 0.19), (bx1 - .2, fy + nn * .3, 0.19), (bx1 - .2, fy + nn * 4.2, 0.19), (bx0 + .2, fy + nn * 4.2, 0.19)], hexc(wc, 0.55))
            for s in range(2):
                zs = zb0 + 0.9 + s * 1.05
                beam('flat', (bx0 + .3, fy + nn * .15, zs), (bx1 - .3, fy + nn * .15, zs), 0.07, hexc('#3a1f55'))
                for g in range(int((bw - .6) / 0.55)):
                    gx = bx0 + .45 + g * 0.55 + R.uniform(0, .1)
                    gc = hexc(R.choice([PINK, LIME, CYAN, AMBER, '#FFFFFF', '#7a2cff']), 2.0)
                    box('flat', gx, gx + 0.32, min(fy + nn * .17, fy + nn * .22), max(fy + nn * .17, fy + nn * .22), zs + .04, zs + .04 + R.uniform(.25, .6), gc)
            # window frame
            fr = hexc('#120a1e')
            beam('solid', (bx0 + .22, fy + nn * .14, zb0), (bx1 - .22, fy + nn * .14, zb0), .12, fr)
            beam('solid', (bx0 + .22, fy + nn * .14, zb1), (bx1 - .22, fy + nn * .14, zb1), .12, fr)
            beam('solid', (bc, fy + nn * .14, zb0), (bc, fy + nn * .14, zb1), .08, fr)
            # awning (slanted slab)
            ac = hexc(R.choice([P['rim'], PINK, P['acc'], '#7a2cff', '#ff8c1a']), 1.0)
            pts = [(bx0 + .1, fy, 3.9), (bx1 - .1, fy, 3.9), (bx1 - .1, fy + nn * 1.3, 3.55), (bx0 + .1, fy + nn * 1.3, 3.55)]
            quad_flat('solid', pts, ac)
            quad_flat('solid', [(p[0], p[1], p[2] - 0.12) for p in reversed(pts)], hexc('#150b22'))
            beam('flat', (bx0 + .1, fy + nn * 1.3, 3.5), (bx1 - .1, fy + nn * 1.3, 3.5), .06, hexc(P['rim'], 3))
        # sign board over the bay
        if R.random() < 0.9:
            nm = R.choice(names)
            tcol = hexc(R.choice([WARM, CYAN, PINK, LIME, '#FFFFFF', AMBER]), 3.2)
            rcol = hexc(R.choice([P['rim'], PINK, CYAN, AMBER]), 3.0)
            wsz = min(bw - .3, max(2.4, 0.8 * len(nm) + 1.0))
            ik = R.choice(ICONS) if (wsz >= 3.6 and R.random() < 0.6) else None
            sign_board(bc, fy, nn, 4.9, wsz + (1.0 if ik else 0), 1.6, nm, tcol, rcol, size=1.15 if len(nm) < 8 else 0.9, icon_kind=ik)
        # floor-2 small things
        if R.random() < 0.5:
            jp = R.choice(JP)
            tcol = hexc(R.choice([PINK, CYAN, AMBER, LIME]), 3)
            box('solid', bc - .5, bc + .5, min(fy, fy + nn * .3), max(fy, fy + nn * .3), 6.4, 8.4 if len(jp) > 1 else 7.6, hexc('#140a22')) if False else None
    # ---- blade signs (vertical), at bay joints
    for k in range(R.randint(2, 4)):
        bxx = R.uniform(x0 + 1.0, x1 - 1.0); z0 = R.uniform(6.5, 11); hh = R.uniform(4.5, 9.0)
        nm = R.choice(SOLACE_NAMES + JP if cn == 'solace' else OTHER_NAMES + JP)
        nm = nm.replace(' ', '\n') if len(nm) > 5 else nm
        word = '\n'.join(list(nm.replace('\n', ''))) if R.random() < 0.7 else nm
        lc = R.choice([P['rim'], PINK, CYAN, AMBER, '#FFFFFF'])
        wv = 1.7
        if R.random() < 0.38:
            sign_board(bxx, fy, nn, z0 + hh / 2, wv, hh, '', hexc(lc, 3.2), hexc(lc, 3.0), vertical=True, depth=0.5, size=0.1)
            icon(R.choice(ICONS), bxx, fy, nn, z0 + hh / 2, wv * 0.85, hexc(lc, 3.4), depth=0.53)
        else:
            sign_board(bxx, fy, nn, z0 + hh / 2, wv, hh, word, hexc(lc, 3.2), hexc(lc, 3.0), size=min(1.2, hh / max(1, len(word.split(chr(10)))) * 0.86), vertical=True, depth=0.5)
        # bracket
        beam('solid', (bxx - 0.3, fy, z0 + hh * 0.5), (bxx - 0.3, fy + nn * .5, z0 + hh * 0.5), 0.08, hexc('#120a1e'))
    # ---- AC units, pipes, balconies
    for k in range(R.randint(2, 6)):
        ax = R.uniform(x0 + .8, x1 - .8); az = R.uniform(6, min(h - 2, 24))
        box('solid', ax - .5, ax + .5, min(fy, fy + nn * .55), max(fy, fy + nn * .55), az, az + .65, hexc('#6b5b86'))
        add_cyl('solid', (ax - 0.0, fy + nn * .57, az + .32), .22, .02 * nn if False else 0.03, hexc('#241833')) if False else None
        box('flat', ax - .3, ax + .3, min(fy + nn * .55, fy + nn * .57), max(fy + nn * .55, fy + nn * .57), az + .12, az + .5, hexc('#1b1030'))
    if R.random() < 0.7:
        px = R.choice([x0 + .5, x1 - .5]); beam('solid', (px, fy + nn * .2, 0), (px, fy + nn * .2, h), 0.2, hexc('#3b2f57'))
    # ---- fire escape
    if h > 14 and R.random() < 0.55:
        ex0 = R.uniform(x0 + .8, max(x0 + 1.0, x1 - 4.6)); ex1 = min(x1 - .5, ex0 + 4.0)
        zt = min(h - 2, R.choice([20, 26, 32])); z = 6.4; fe = hexc('#2a1c3e'); fl = hexc('#8a6bb0', 1.3)
        side = 0
        while z < zt:
            box('solid', ex0, ex1, min(fy, fy + nn * 1.5), max(fy, fy + nn * 1.5), z, z + 0.08, fe)
            beam('flat', (ex0, fy + nn * 1.5, z + 1.0), (ex1, fy + nn * 1.5, z + 1.0), .06, fl)
            for q in range(5):
                bxq = ex0 + (ex1 - ex0) * q / 4
                beam('solid', (bxq, fy + nn * 1.5, z), (bxq, fy + nn * 1.5, z + 1.0), .05, fe)
            a = (ex0, ex1) if side == 0 else (ex1, ex0)
            beam('solid', (a[0], fy + nn * 0.9, z + 0.08), (a[1], fy + nn * 0.9, z + 3.2), .14, fe)
            side = 1 - side; z += 3.2
        beam('solid', (ex0, fy + nn * .1, 6.4), (ex0, fy + nn * 1.5, 6.4), .06, fe)
    # ---- hanging lanterns / string lights at 1st floor
    if R.random() < 0.5:
        for q in range(R.randint(2, 5)):
            lx = R.uniform(x0 + .5, x1 - .5)
            beam('flat', (lx, fy + nn * .9, 3.7), (lx, fy + nn * .9, 3.3), .03, hexc('#120a1e'))
            box('flat', lx - .2, lx + .2, fy + nn * .9 - .2, fy + nn * .9 + .2, 2.7, 3.3, hexc(R.choice([PINK, AMBER, '#FF3030']), 3))
    # ---- rooftop: water tower / HVAC / roof sign
    ry = (y_a + y_b) / 2
    if h < 34 and R.random() < 0.6:
        tx = R.uniform(x0 + 2, x1 - 2); wood = hexc('#7a4a36', 1.0)
        for lx, ly in ((-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)):
            beam('solid', (tx + lx, ry + ly, h), (tx + lx, ry + ly, h + 2.4), .14, hexc('#241833'))
        add_cyl('solid', (tx, ry, h + 2.4), 1.5, 2.8, wood, 12)
        add_cone('solid', (tx, ry, h + 5.2), 1.7, 1.2, hexc('#3a2418'), 12)
        for q in range(3): add_ring('flat', (tx, ry), 1.5, 1.56, hexc('#1b1030'), 12, z=h + 3.2 + q * 0.8) if False else None
    if R.random() < 0.55:
        for q in range(R.randint(1, 3)):
            hx = R.uniform(x0 + 1, x1 - 1); box('solid', hx - 1, hx + 1, ry - 1, ry + 1, h, h + 1.4, hexc('#4b3a68'))
            box('flat', hx - .6, hx + .6, ry - 1.02, ry - 1.0, h + .3, h + .9, hexc('#1b1030'))
    if h > 16 and R.random() < 0.7:
        nm = R.choice(SOLACE_NAMES if cn == 'solace' else OTHER_NAMES); wsz = max(5, 0.9 * len(nm) + 2)
        wsz = min(wsz, ww - 1.5); zc = h + 2.3
        lc = hexc(R.choice([P['rim'], PINK, CYAN, AMBER]), 3.0)
        big_sign((x0 + x1) / 2, ry, zc, wsz + 3, 4.2, nn, nm, R.choice(ICONS), lc, R.choice(['#7a1a58', '#1a5a3a', '#2a2a8a', '#8a3a10', '#0e4a6a', '#5a1a7a']), 2.1)
        for lx in (-wsz / 2 + .4, wsz / 2 - .4):
            beam('solid', ((x0 + x1) / 2 + lx, ry, h), ((x0 + x1) / 2 + lx, ry, zc - 1.6), .12, hexc('#241833'))

# ------------------------------------------------------------------ street furniture / ground
Y_N = 8.0     # north row front plane
Y_S = -22.0   # south row front plane
YC = -7.0     # avenue centreline
def route_y(x): return -8.5 + 2.6 * math.sin(x / 21.0)
NODE_TYPES = ['shop', 'fight', 'event', 'fight', 'shop', 'elite', 'event', 'fight', 'rest', 'fight', 'shop', 'elite', 'fight', 'hq']
NODE_X = [-44 + 15.5 * i for i in range(14)]
NODE_X[-1] = 100
NCOL = {'shop': LIME, 'fight': '#FF3A6E', 'event': '#FFD23A', 'elite': PINK, 'rest': CYAN, 'hq': '#FFFFFF'}

def ground():
    G = 'ground'
    asph = hexc('#1c1830'); pav = hexc('#2a2740'); pav2 = hexc('#37304f')
    x0, x1 = -150, 260
    ACC[G].add_poly([(x0, Y_S, 0), (x1, Y_S, 0), (x1, Y_N, 0), (x0, Y_N, 0)], [(3, 2, 1, 0)], asph)
    # pavements N and S (slightly raised kerb)
    box(G, x0, x1, Y_N - 5.5, Y_N, 0, 0.18, pav)
    box(G, x0, x1, Y_S, Y_S + 5.5, 0, 0.18, pav)
    # behind rows and surrounding ground
    ACC[G].add_poly([(x0, -400, -0.02), (x1, -400, -0.02), (x1, 400, -0.02), (x0, 400, -0.02)], [(3, 2, 1, 0)], hexc('#14102a'))
    # kerb neon line
    beam('flat', (x0, Y_N - 5.5, 0.2), (x1, Y_N - 5.5, 0.2), .06, hexc('#5a3a9a', 0.8))
    # lane dashes
    for lane in (YC + 3.5, YC - 4.5):
        x = -110.0
        while x < 230:
            quad_flat('flat', [(x, lane - .13, 0.02), (x + 3, lane - .13, 0.02), (x + 3, lane + .13, 0.02), (x, lane + .13, 0.02)], hexc('#E8C84A', 0.9))
            ACC['flat'].f[-1] = tuple(reversed(ACC['flat'].f[-1])); x += 7.0
    # crosswalk
    for cxw in (-14.0, 66.0):
        for k in range(16):
            yy = Y_S + 6 + k * 0.95
            quad_flat('flat', [(cxw, yy, 0.025), (cxw + 3.2, yy, 0.025), (cxw + 3.2, yy + .5, 0.025), (cxw, yy + .5, 0.025)], hexc('#a79bd0', 0.7))
            ACC['flat'].f[-1] = tuple(reversed(ACC['flat'].f[-1]))
    # tram/car light streaks along far lanes
    for k in range(110):
        x = R.uniform(-110, 220)
        lane = (YC + R.choice([2.0, 3.0, 4.0, 5.0, 5.6, 2.6])) if k % 3 else (Y_S + R.choice([6.5, 7.6, 8.8, 10.0]))
        L = R.uniform(18, 80); c = R.choice([hexc('#FF2A22', 3.4), hexc('#FF2A22', 3.4), hexc('#FF4A30', 3.0), hexc('#FFFFFF', 3.0), hexc('#FFFFFF', 3.0), hexc('#FFD060', 2.6), hexc(PINK, 2.6)])
        quad_flat('flat', [(x, lane - .07, 0.05), (x + L, lane - .07, 0.05), (x + L, lane + .07, 0.05), (x, lane + .07, 0.05)], c)
        ACC['flat'].f[-1] = tuple(reversed(ACC['flat'].f[-1]))
    # manholes
    for k in range(14):
        x = R.uniform(-60, 90); y = R.uniform(Y_S + 8, Y_N - 8)
        add_cyl(G, (x, y, 0.0), 0.55, 0.03, hexc('#0f0b1e'), 10)

def route():
    RW = {'f2': 0.8, 'f3': 0.34, 'f4': 0.34}[FRAME]; RS = {'f2': 2.4, 'f3': 1.0, 'f4': 1.0}[FRAME]
    SEL = {'f2': 13, 'f3': 3, 'f4': 13}[FRAME]
    pts = [(x, route_y(x)) for x in range(-62, 112, 2)]
    lc = hexc(LIME, 5.0)
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        d = Vector((xb - xa, yb - ya, 0)); nrm = Vector((-d.y, d.x, 0)).normalized() * RW
        quad_flat('flat', [(xa - nrm.x, ya - nrm.y, 0.06), (xb - nrm.x, yb - nrm.y, 0.06), (xb + nrm.x, yb + nrm.y, 0.06), (xa + nrm.x, ya + nrm.y, 0.06)], lc)
        ACC['flat'].f[-1] = tuple(reversed(ACC['flat'].f[-1]))
    # chevrons
    for x in range(-60, 108, 4):
        y = route_y(x); dy = route_y(x + .1) - y; ang = math.atan2(dy, .1)
        for s in (-1, 1):
            p0 = Vector((x - 0.7, y + s * 0.8, 0.07)); p1 = Vector((x + 0.6, y, 0.07))
            beam('flat', p0, p1, 0.16 * RS, hexc(LIME, 4.5), hint=(0, 0, 1))
    # nodes: small ground discs; only the selected node gets a pole and marker
    for ni, (x, t) in enumerate(zip(NODE_X, NODE_TYPES)):
        y = route_y(x); c = NCOL[t]
        add_ring('flat', (x, y), 1.0 * RS, 1.4 * RS, hexc(c, 4.5), 32, z=0.08)
        add_ring('flat', (x, y), 0.0 + 0.1, 0.9 * RS, hexc(c, 1.2), 20, z=0.075)
        if ni == SEL:
            add_ring('flat', (x, y), 1.9 * RS, 2.1 * RS, hexc('#FFFFFF', 3.0), 32, z=0.085)
            beam('flat', (x, y, 0.1), (x, y, 5.5 * RS), 0.1 * RS, hexc('#EFFFE0', 4.0))
            ph = 5.5 * RS
            ACC['flat'].add_poly([(x, y, ph + 0.1 * RS), (x + 0.7 * RS, y, ph + 1.1 * RS), (x, y, ph + 2.1 * RS), (x - 0.7 * RS, y, ph + 1.1 * RS)], [(0, 1, 2, 3), (3, 2, 1, 0)], hexc('#EFFFE0', 4.0))

def street_furniture():
    # lamp posts both pavements, power poles with wires across
    for x in range(-100, 200, 14):
        for side in (0, 1):
            y = Y_N - 4.4 if side == 0 else Y_S + 4.4
            lod = lod_at(x, y)
            if lod == 0: continue
            col = hexc('#241833')
            beam('solid', (x, y, 0), (x, y, 7.2), 0.16, col)
            nn = -1 if side == 0 else 1
            beam('solid', (x, y, 7.2), (x, y + (-nn) * 1.4 * -1, 7.5), 0.1, col) if False else None
            box('flat', x - .3, x + .3, y - .3, y + .3, 7.2, 7.6, hexc('#FFE3B0', 4.5))
            if lod == 2:
                # glow puddle on pavement
                pass
    for x in range(-90, 200, 28):
        lod = lod_at(x, YC)
        if lod < 2: continue
        for side, y in ((0, Y_N - 4.4), (1, Y_S + 4.4)):
            beam('solid', (x, y, 0), (x, y, 11.5), .22, hexc('#1c1230'))
            beam('solid', (x - 1.4, y, 10.6), (x + 1.4, y, 10.6), .16, hexc('#1c1230'))
        # wires across
        for k in range(4):
            xx = x + (k - 1.5) * 0.4
            prev = None
            for s in range(0, 9):
                t = s / 8; y = (Y_S + 4.4) + t * ((Y_N - 4.4) - (Y_S + 4.4)); z = 10.6 - 2.0 * 4 * t * (1 - t) * 1.0 + k * .1
                p = (xx, y, z)
                if prev: beam('flat', prev, p, 0.035, hexc('#0b0716', 1.0))
                prev = p
    # vending machines, bins, scooters near north pavement
    for k in range(18):
        x = R.uniform(-45, 55)
        if lod_at(x, Y_N) < 2: continue
        yv = Y_N - 1.0
        c = hexc(R.choice([PINK, CYAN, LIME, AMBER, '#FFFFFF']), 3.0)
        box('solid', x - .45, x + .45, yv - .35, yv + .35, 0.18, 1.9, hexc('#241833'))
        box('flat', x - .35, x + .35, yv - .37, yv - .35, .6, 1.7, c)
    # kerb-side scooters / bollards silhouette on the south pavement near camera
    for k in range(0):
        x = R.uniform(-30, 25); y = Y_S + R.uniform(1, 4)
        box('solid', x - .45, x + .45, y - .15, y + .15, .2, .8, hexc('#241833'))
        add_cyl('solid', (x - .5, y, .0), .28, .24, hexc('#0d0817'), 8)
        add_cyl('solid', (x + .5, y, .0), .28, .24, hexc('#0d0817'), 8)

def steam():
    for x in (-8, 24, 61):
        pass

# ------------------------------------------------------------------ city layout
def row(yf, depth, f, xa, xb, hlo, hhi, gap_p=0.18, wlo=8, whi=17, lod_force=None):
    x = xa
    while x < xb:
        w = R.uniform(wlo, whi)
        if R.random() < gap_p:
            x += R.uniform(3.5, 6.5); continue
        h = R.uniform(hlo, hhi)
        # stepped heights: occasionally a low shop block
        if R.random() < 0.28: h = R.uniform(10, 16)
        lod = lod_force if lod_force is not None else None
        building(x, min(x + w, xb), yf, depth, h, f, lod=lod)
        x += w + R.uniform(0.0, 0.3)

def far_blocks():
    # second and third rows: tall towers, cheap
    for (ya, yb, f, hl, hh) in ((Y_N + 22, 0, -1, 28, 52 if FRAME == 'f3' else 74), (Y_N + 52, 0, -1, 36, 66 if FRAME == 'f3' else 100), (Y_S - 16, 0, 1, 34, 80), (Y_S - 44, 0, 1, 46, 110)):
        x = -140.0
        while x < 250:
            w = R.uniform(10, 22); h = R.uniform(hl, hh)
            if FRAME == 'f2' and f == 1: h = R.uniform(18, 34)
            if FRAME == 'f3' and f == 1 and -120 < x < 120:
                x += w + 2; continue
            if x > 70 and x < 170 and abs(ya - YC) < 120 and f == 1:
                x += w + 2; continue  # park corridor shoulder kept open
            building(x, x + w, ya, R.uniform(14, 22), h, f, lod=0 if lod_at(x + w / 2, ya) < 1 else 1, dim=0.62)
            x += w + R.uniform(1.0, 4.0)
    BEAMS = {'f3': [(-58, Y_N + 52, 56, PINK), (-20, Y_N + 22, 40, CYAN), (24, Y_N + 52, 60, LIME), (58, Y_N + 22, 46, '#FFFFFF')],
             'f4': [(60, Y_N + 22, 40, PINK), (105, Y_S - 16, 50, CYAN), (150, Y_N + 40, 60, LIME), (20, Y_S - 16, 40, PINK)],
             'f2': [(20, Y_N + 22, 60, PINK), (140, Y_N + 22, 60, CYAN), (-30, Y_N + 52, 70, LIME)]}[FRAME]
    for (bx, by, bz, bc) in BEAMS:
        light_beam((bx, by, bz), (R.uniform(-.25, .25), -0.12, 1.0), 120, 1.1, hexc(bc, 3.2), a0=0.42)
    # far skyline ring
    for k in range(34):
        x = R.uniform(-160, 300); side = R.choice([-1, 1]); y = YC + side * R.uniform(120, 260)
        if FRAME == 'f2' and side == -1: continue
        building(x, x + R.uniform(12, 24), y, R.uniform(14, 26), R.uniform(50, 120), -side, lod=0, dim=0.4)

def park():
    cx, cy = HQ.x, HQ.y
    # lawn disc (dark green), paths, plaza
    n = 48
    lawn = hexc('#123a2e')
    pts = [(cx + 70 * math.cos(2 * math.pi * i / n), cy + 78 * math.sin(2 * math.pi * i / n), 0.01) for i in range(n)]
    ACC['ground'].add_poly(pts, [tuple(reversed(range(n)))], lawn)
    add_cyl('ground', (cx, cy, 0.0), 26, 0.25, hexc('#2c2c4a'), 40)
    for r, c, k in ((25.6, LIME, 2.6), (21.0, '#B8FF78', 1.4), (14.5, PINK, 2.2), (9.0, LIME, 2.6)):
        add_ring('flat', (cx, cy), r - .35, r + .35, hexc(c, k), 60, z=0.3)
    # radial spokes
    for a in range(0, 360, 30):
        ar = math.radians(a); beam('flat', (cx + 9 * math.cos(ar), cy + 9 * math.sin(ar), 0.31), (cx + 25 * math.cos(ar), cy + 25 * math.sin(ar), 0.31), 0.12, hexc(LIME, 1.4))
    # trees
    for k in range(560):
        a = R.uniform(0, 2 * math.pi); r = 28 + 44 * math.sqrt(R.random())
        x = cx + r * math.cos(a) * 0.95; y = cy + r * math.sin(a) * 1.05
        if x < 78: continue
        if abs(y - YC) < 6.5 and x < 96: continue
        s = R.uniform(2.6, 5.0)
        shade = R.uniform(0.7, 1.2); tone = hexc(R.choice(['#1a5a3c', '#16503a', '#1d6a40']))
        top = hexc(R.choice(['#3ea857', '#4fbe5c', '#6fd860']))
        def cf(n, tone=tone, top=top, shade=shade):
            if n.z > 0.45: return (top[0] * shade, top[1] * shade, top[2] * shade, 1)
            if n.x > 0.3: return (tone[0] * 1.5, tone[1] * 1.5, tone[2] * 1.5, 1)
            return tone
        if r > 62 and R.random() < .6: pass
        add_blob('flat', (x, y, s * 0.9), s, s, s * 0.9, cf)
        if R.random() < 0.45:
            add_blob('flat', (x + R.uniform(-1.4, 1.4), y + R.uniform(-1.4, 1.4), s * 1.5), s * .7, s * .7, s * .6, cf)
        beam('solid', (x, y, 0), (x, y, s * .6), .35, hexc('#2a1f2a'))
    # low Solace pods / labs around plaza
    for a in range(0, 360, 36):
        ar = math.radians(a + 11); r = 36 + R.choice([0, 6])
        x = cx + r * math.cos(ar); y = cy + r * math.sin(ar) * 1.0
        if x < 82 or abs(y - YC) < 8: continue
        h = R.uniform(9, 26)
        building(x - 4, x + 4, y - 4, 8, h, -1, corp_name='solace', lod=2 if FRAME == 'f4' else 1)
    # glowing pink/lime pods in the lawn
    for k in range(60):
        a = R.uniform(0, 2 * math.pi); r = R.uniform(30, 66); x = cx + r * math.cos(a); y = cy + r * math.sin(a)
        if x < 80: continue
        add_blob('flat', (x, y, 0.5), .9, .9, .5, lambda n: hexc(R.choice([LIME, PINK, '#B8FF78']), 2.6))

def helix():
    cx, cy = HQ.x, HQ.y
    H = 82.0; turns = 2.6; rad = 6.2; N = 160
    mats = {}
    def mk(name, col):
        m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
        e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value = col
        o = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(e.outputs[0], o.inputs[0]); return m
    strand_m = mk('hx_strand', hexc('#8CFF3C', 1.3)); rim_m = mk('hx_rim', hexc('#EFFFC0', 3.5)); pink_m = mk('hx_pink', hexc(PINK, 3.2))
    coll = bpy.data.collections['ink']
    for s in (0, 1):
        cu = bpy.data.curves.new('hx%d' % s, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 1.45; cu.bevel_resolution = 3; cu.resolution_u = 4
        sp = cu.splines.new('POLY'); sp.points.add(N)
        for i in range(N + 1):
            t = i / N; a = 2 * math.pi * turns * t + s * math.pi
            rr = rad * (1.0 + 0.35 * math.sin(math.pi * t) ** 2) * (0.75 + 0.25 * min(1.0, t * 6))
            sp.points[i].co = (cx + rr * math.cos(a), cy + rr * math.sin(a), 2 + H * t, 1)
        cu.materials.append(strand_m)
        ob = bpy.data.objects.new('hx%d' % s, cu); coll.objects.link(ob)
        # neon rim along strand (thin, bright)
        cu2 = bpy.data.curves.new('hxr%d' % s, 'CURVE'); cu2.dimensions = '3D'; cu2.bevel_depth = 0.28; cu2.bevel_resolution = 1; cu2.resolution_u = 4
        sp2 = cu2.splines.new('POLY'); sp2.points.add(N)
        for i in range(N + 1):
            t = i / N; a = 2 * math.pi * turns * t + s * math.pi
            rr = rad * (1.0 + 0.35 * math.sin(math.pi * t) ** 2) * (0.75 + 0.25 * min(1.0, t * 6))
            sp2.points[i].co = (cx + (rr + 0.55) * math.cos(a), cy + (rr + 0.55) * math.sin(a), 2 + H * t + 0.5, 1)
        cu2.materials.append(rim_m); ob2 = bpy.data.objects.new('hxr%d' % s, cu2); TEXT_COLL.objects.link(ob2)
    # rungs + cell pods
    for i in range(3, N - 3, 7):
        t = i / N; z = 2 + H * t; rr = rad * (1.0 + 0.35 * math.sin(math.pi * t) ** 2) * (0.75 + 0.25 * min(1.0, t * 6))
        a = 2 * math.pi * turns * t
        p0 = (cx + rr * math.cos(a), cy + rr * math.sin(a), z); p1 = (cx - rr * math.cos(a), cy - rr * math.sin(a), z)
        beam('flat', p0, p1, 0.5, hexc(PINK if (i // 7) % 2 == 0 else LIME, 3.4))
        add_blob('flat', ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, z), 1.1, 1.1, 0.7, lambda n: hexc('#D8FFB0', 1.6))
    # halo ring
    add_ring('flat', (cx, cy), 8.2, 9.0, hexc(PINK, 5.0), 64, z=2 + H + 4)
    add_ring('flat', (cx, cy), 6.6, 7.0, hexc(LIME, 5.0), 64, z=2 + H + 4.4)
    # light column up the helix core (so it reads in squint)
    beam('flat', (cx, cy, 2), (cx, cy, 2 + H + 4), 0.5, hexc('#CFFF90', 1.6))

# ------------------------------------------------------------------ scene assembly
def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def make_objects():
    G = bpy.data.collections.new('ink'); bpy.context.scene.collection.children.link(G)
    N = bpy.data.collections.new('neon'); bpy.context.scene.collection.children.link(N)
    return G, N

def fog_mix(nt, col_sock, k=0.005, fmax=0.5):
    N = nt.nodes; L = nt.links
    cd = N.new('ShaderNodeCameraData'); mu = N.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = -k; L.new(cd.outputs['View Distance'], mu.inputs[0])
    ex = N.new('ShaderNodeMath'); ex.operation = 'EXPONENT'; L.new(mu.outputs[0], ex.inputs[0])
    iv = N.new('ShaderNodeMath'); iv.operation = 'SUBTRACT'; iv.inputs[0].default_value = 1.0; L.new(ex.outputs[0], iv.inputs[1])
    sc = N.new('ShaderNodeMath'); sc.operation = 'MULTIPLY'; sc.inputs[1].default_value = fmax; L.new(iv.outputs[0], sc.inputs[0])
    fc = N.new('ShaderNodeRGB'); fc.outputs[0].default_value = hexc('#3a1a5a', 0.8)
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; L.new(sc.outputs[0], mx.inputs['Factor']); L.new(col_sock, mx.inputs['A']); L.new(fc.outputs[0], mx.inputs['B'])
    return mx.outputs[2]

def mat_vc_emission(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'Col'
    e = nt.nodes.new('ShaderNodeEmission'); o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(fog_mix(nt, at.outputs['Color']), e.inputs['Color']); nt.links.new(e.outputs[0], o.inputs[0]); return m

def mat_windows(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    N = nt.nodes; L = nt.links
    def mn(op, a=None, b=None, clamp=False):
        n = N.new('ShaderNodeMath'); n.operation = op; n.use_clamp = clamp
        if a is not None:
            if isinstance(a, (int, float)): n.inputs[0].default_value = a
            else: L.new(a, n.inputs[0])
        if b is not None:
            if isinstance(b, (int, float)): n.inputs[1].default_value = b
            else: L.new(b, n.inputs[1])
        return n.outputs[0]
    geo = N.new('ShaderNodeNewGeometry'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sep.inputs[0])
    nsep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Normal'], nsep.inputs[0])
    col = N.new('ShaderNodeAttribute'); col.attribute_name = 'Col'
    win = N.new('ShaderNodeAttribute'); win.attribute_name = 'Win'
    u = mn('ADD', sep.outputs['X'], sep.outputs['Y']); u = mn('DIVIDE', u, 0.95); v = mn('DIVIDE', sep.outputs['Z'], 1.25)
    cu = mn('FLOOR', u); cv = mn('FLOOR', v); fu = mn('FRACT', u); fv = mn('FRACT', v)
    cmb3 = N.new('ShaderNodeCombineXYZ'); L.new(cu, cmb3.inputs['X']); L.new(cv, cmb3.inputs['Y']); cmb3.inputs['Z'].default_value = 13.0
    wn3 = N.new('ShaderNodeTexWhiteNoise'); wn3.noise_dimensions = '3D'; L.new(cmb3.outputs[0], wn3.inputs['Vector'])
    lo = mn('ADD', 0.14, mn('MULTIPLY', wn3.outputs['Value'], 0.22)); hi = mn('SUBTRACT', 0.88, mn('MULTIPLY', wn3.outputs['Value'], 0.22))
    lov = mn('ADD', 0.16, mn('MULTIPLY', wn3.outputs['Value'], 0.2)); hiv = mn('SUBTRACT', 0.84, mn('MULTIPLY', wn3.outputs['Value'], 0.28))
    inx = mn('MULTIPLY', mn('GREATER_THAN', fu, lo), mn('LESS_THAN', fu, hi))
    iny = mn('MULTIPLY', mn('GREATER_THAN', fv, lov), mn('LESS_THAN', fv, hiv))
    wall = mn('LESS_THAN', mn('ABSOLUTE', nsep.outputs['Z']), 0.5)
    mask = mn('MULTIPLY', mn('MULTIPLY', inx, iny), wall)
    cmb = N.new('ShaderNodeCombineXYZ'); L.new(cu, cmb.inputs['X']); L.new(cv, cmb.inputs['Y']); cmb.inputs['Z'].default_value = 1.0
    wn = N.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions = '3D'; L.new(cmb.outputs[0], wn.inputs['Vector'])
    cmb2 = N.new('ShaderNodeCombineXYZ'); L.new(cu, cmb2.inputs['X']); L.new(cv, cmb2.inputs['Y']); cmb2.inputs['Z'].default_value = 7.0
    wn2 = N.new('ShaderNodeTexWhiteNoise'); wn2.noise_dimensions = '3D'; L.new(cmb2.outputs[0], wn2.inputs['Vector'])
    on = mn('LESS_THAN', wn.outputs['Value'], win.outputs['Alpha'])
    # window colour: warm / corp tint / cyan
    warm = N.new('ShaderNodeRGB'); warm.outputs[0].default_value = hexc('#FFA84A')
    cyan = N.new('ShaderNodeRGB'); cyan.outputs[0].default_value = hexc('#C8F2FF')
    mx1 = N.new('ShaderNodeMix'); mx1.data_type = 'RGBA'; L.new(mn('GREATER_THAN', wn2.outputs['Value'], 0.76), mx1.inputs['Factor'])
    L.new(warm.outputs[0], mx1.inputs['A']); L.new(win.outputs['Color'], mx1.inputs['B'])
    mx2 = N.new('ShaderNodeMix'); mx2.data_type = 'RGBA'; L.new(mn('GREATER_THAN', wn2.outputs['Value'], 0.9), mx2.inputs['Factor'])
    L.new(mx1.outputs[2], mx2.inputs['A']); L.new(cyan.outputs[0], mx2.inputs['B'])
    wcol = N.new('ShaderNodeVectorMath'); wcol.operation = 'SCALE'; L.new(mx2.outputs[2], wcol.inputs[0]); wcol.inputs['Scale'].default_value = 1.9
    # tone ramp by height (cel bands)
    zn = mn('DIVIDE', sep.outputs['Z'], 110.0)
    ramp = N.new('ShaderNodeValToRGB'); ramp.color_ramp.interpolation = 'CONSTANT'; L.new(zn, ramp.inputs['Fac'])
    el = ramp.color_ramp.elements; el[0].position = 0.0; el[0].color = (1.0, 1.0, 1.0, 1)
    for pos, val in ((0.04, 0.8), (0.09, 0.66), (0.17, 0.54), (0.3, 0.46), (0.6, 0.4)):
        e = el.new(pos); e.color = (val, val, val, 1)
    side = mn('ADD', 1.0, mn('MULTIPLY', nsep.outputs['X'], 0.28))
    roof = mn('ADD', 1.0, mn('MULTIPLY', mn('GREATER_THAN', nsep.outputs['Z'], 0.5), 0.35))
    band = mn('SUBTRACT', 1.0, mn('MULTIPLY', mn('LESS_THAN', fv, 0.07), 0.25))
    col_line = mn('SUBTRACT', 1.0, mn('MULTIPLY', mn('LESS_THAN', fu, 0.04), 0.12))
    mpg = N.new('ShaderNodeMapping'); mpg.inputs['Scale'].default_value = (0.7, 0.7, 0.10); L.new(geo.outputs['Position'], mpg.inputs['Vector'])
    ng = N.new('ShaderNodeTexNoise'); ng.inputs['Scale'].default_value = 2.2; ng.inputs['Detail'].default_value = 6; L.new(mpg.outputs[0], ng.inputs['Vector'])
    mps = N.new('ShaderNodeMapping'); mps.inputs['Scale'].default_value = (2.6, 2.6, 0.035); L.new(geo.outputs['Position'], mps.inputs['Vector'])
    nsg = N.new('ShaderNodeTexNoise'); nsg.inputs['Scale'].default_value = 3.0; nsg.inputs['Detail'].default_value = 3; L.new(mps.outputs[0], nsg.inputs['Vector'])
    grime = mn('ADD', 0.55, mn('ADD', mn('MULTIPLY', ng.outputs['Fac'], 0.6), mn('MULTIPLY', nsg.outputs['Fac'], 0.4)))
    shade = mn('MULTIPLY', mn('MULTIPLY', mn('MULTIPLY', mn('MULTIPLY', side, roof), mn('MULTIPLY', band, col_line)), ramp.outputs['Color']), grime)
    bodyc = N.new('ShaderNodeVectorMath'); bodyc.operation = 'SCALE'; L.new(col.outputs['Color'], bodyc.inputs[0]); L.new(shade, bodyc.inputs['Scale'])
    # wmask: window (on) replaces body
    wm = mn('MULTIPLY', mask, on)
    fin = N.new('ShaderNodeMix'); fin.data_type = 'RGBA'; L.new(wm, fin.inputs['Factor']); L.new(bodyc.outputs[0], fin.inputs['A']); L.new(wcol.outputs[0], fin.inputs['B'])
    # dark window (off) slightly darker than body
    dark = N.new('ShaderNodeVectorMath'); dark.operation = 'SCALE'; L.new(bodyc.outputs[0], dark.inputs[0]); dark.inputs['Scale'].default_value = 0.5
    fin2 = N.new('ShaderNodeMix'); fin2.data_type = 'RGBA'; L.new(mn('MULTIPLY', mask, mn('SUBTRACT', 1.0, on)), fin2.inputs['Factor']); L.new(fin.outputs[2], fin2.inputs['A']); L.new(dark.outputs[0], fin2.inputs['B'])
    e = N.new('ShaderNodeEmission'); L.new(fog_mix(nt, fin2.outputs[2]), e.inputs['Color']); e.inputs['Strength'].default_value = 0.5
    o = N.new('ShaderNodeOutputMaterial'); L.new(e.outputs[0], o.inputs[0]); return m

def mat_ink():
    m = bpy.data.materials.new('ink'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); N = nt.nodes; L = nt.links
    g = N.new('ShaderNodeNewGeometry'); tr = N.new('ShaderNodeBsdfTransparent'); em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = hexc('#0b0516'); em.inputs['Strength'].default_value = 1.0
    mx = N.new('ShaderNodeMixShader'); L.new(g.outputs['Backfacing'], mx.inputs['Fac']); L.new(tr.outputs[0], mx.inputs[1]); L.new(em.outputs[0], mx.inputs[2])
    o = N.new('ShaderNodeOutputMaterial'); L.new(mx.outputs[0], o.inputs[0]); return m

def mat_glow():
    m = bpy.data.materials.new('glow'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); N = nt.nodes; L = nt.links
    at = N.new('ShaderNodeAttribute'); at.attribute_name = 'Col'; aw = N.new('ShaderNodeAttribute'); aw.attribute_name = 'Win'; sc_ = N.new('ShaderNodeSeparateColor'); L.new(aw.outputs['Color'], sc_.inputs[0])
    tr = N.new('ShaderNodeBsdfTransparent'); em = N.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.0
    L.new(at.outputs['Color'], em.inputs['Color']); mx = N.new('ShaderNodeMixShader'); L.new(sc_.outputs['Red'], mx.inputs['Fac']); L.new(tr.outputs[0], mx.inputs[1]); L.new(em.outputs[0], mx.inputs[2])
    o = N.new('ShaderNodeOutputMaterial'); L.new(mx.outputs[0], o.inputs[0]); return m

def mat_ground():
    m = bpy.data.materials.new('ground'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); N = nt.nodes; L = nt.links
    at = N.new('ShaderNodeAttribute'); at.attribute_name = 'Col'
    geo = N.new('ShaderNodeNewGeometry')
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.09, 0.5, 1.0); L.new(geo.outputs['Position'], mp.inputs['Vector'])
    ns = N.new('ShaderNodeTexNoise'); ns.inputs['Scale'].default_value = 1.4; ns.inputs['Detail'].default_value = 3; L.new(mp.outputs[0], ns.inputs['Vector'])
    mp2 = N.new('ShaderNodeMapping'); mp2.inputs['Scale'].default_value = (0.35, 0.35, 1.0); L.new(geo.outputs['Position'], mp2.inputs['Vector'])
    ns2 = N.new('ShaderNodeTexNoise'); ns2.inputs['Scale'].default_value = 1.0; ns2.inputs['Detail'].default_value = 4; L.new(mp2.outputs[0], ns2.inputs['Vector'])
    rr = N.new('ShaderNodeMapRange'); L.new(ns.outputs['Fac'], rr.inputs['Value']); rr.inputs['From Min'].default_value = 0.42; rr.inputs['From Max'].default_value = 0.58
    rr.inputs['To Min'].default_value = 0.03; rr.inputs['To Max'].default_value = 0.34
    rr2 = N.new('ShaderNodeMapRange'); L.new(ns2.outputs['Fac'], rr2.inputs['Value']); rr2.inputs['From Min'].default_value = 0.4; rr2.inputs['From Max'].default_value = 0.55
    rr2.inputs['To Min'].default_value = 0.0; rr2.inputs['To Max'].default_value = 0.3
    ad = N.new('ShaderNodeMath'); ad.operation = 'MULTIPLY'; L.new(rr.outputs[0], ad.inputs[0]); L.new(rr2.outputs[0], ad.inputs[1]); ad.inputs[1].default_value = 1.0
    mn_ = N.new('ShaderNodeMath'); mn_.operation = 'MINIMUM'; L.new(rr.outputs[0], mn_.inputs[0]); L.new(rr2.outputs[0], mn_.inputs[1])
    # rough = puddle zones very smooth; others moderately wet
    rg = N.new('ShaderNodeMath'); rg.operation = 'ADD'; L.new(mn_.outputs[0], rg.inputs[0]); rg.inputs[1].default_value = 0.05
    b = N.new('ShaderNodeBsdfPrincipled'); L.new(at.outputs['Color'], b.inputs['Base Color']); L.new(rg.outputs[0], b.inputs['Roughness'])
    b.inputs['Metallic'].default_value = 0.0
    for k in ('Specular IOR Level',):
        if k in b.inputs: b.inputs[k].default_value = 0.9
    if 'IOR' in b.inputs: b.inputs['IOR'].default_value = 1.6
    o = N.new('ShaderNodeOutputMaterial'); L.new(b.outputs[0], o.inputs[0]); return m

def flush(coll_ink, coll_neon):
    mats = {'body': mat_windows('win_body'), 'far': mat_windows('win_far'), 'solid': mat_vc_emission('solid'), 'flat': mat_vc_emission('flat'), 'ground': mat_ground(), 'ink': mat_ink(), 'glow': mat_glow()}
    # solid pieces are dim emission (cel, not lit): scale handled by colour; no extra
    for k, acc in ACC.items():
        if not acc.v: continue
        me = bpy.data.meshes.new(k); me.from_pydata(acc.v, [], acc.f); me.update()
        ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT'); flat = [c for col in acc.c for c in col]; ca.data.foreach_set('color', flat)
        cw = me.color_attributes.new('Win', 'FLOAT_COLOR', 'POINT'); flat = [c for col in acc.w for c in col]; cw.data.foreach_set('color', flat)
        me.materials.append(mats[k]); ob = bpy.data.objects.new(k, me)
        coll_neon.objects.link(ob)
        # ground must reflect; no flat shading issue

def world():
    w = bpy.data.worlds.new('w'); bpy.context.scene.world = w; w.use_nodes = True; nt = w.node_tree; nt.nodes.clear(); N = nt.nodes; L = nt.links
    tc = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Generated'] if False else tc.outputs['Window'], sp.inputs[0]) if False else None
    ge = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(ge.outputs['Generated'], sp.inputs[0])
    mr = N.new('ShaderNodeMapRange'); L.new(sp.outputs['Z'], mr.inputs['Value']); mr.inputs['From Min'].default_value = 0.0; mr.inputs['From Max'].default_value = 0.8
    mr.inputs['To Min'].default_value = 0.0; mr.inputs['To Max'].default_value = 1.0
    ramp = N.new('ShaderNodeValToRGB'); L.new(mr.outputs[0], ramp.inputs['Fac'])
    el = ramp.color_ramp.elements; el[0].position = 0.0; el[0].color = hexc('#d0568a'); el[1].position = 1.0; el[1].color = hexc('#150a34')
    e2 = el.new(0.10); e2.color = hexc('#8a3a90'); e3 = el.new(0.45); e3.color = hexc('#3a1a6e')
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 2.4; nz.inputs['Detail'].default_value = 5
    mpn = N.new('ShaderNodeMapping'); mpn.inputs['Scale'].default_value = (1.0, 1.0, 3.2); L.new(ge.outputs['Generated'], mpn.inputs['Vector']); L.new(mpn.outputs[0], nz.inputs['Vector'])
    adn = N.new('ShaderNodeMath'); adn.operation = 'ADD'; L.new(mr.outputs[0], adn.inputs[0]); sbn = N.new('ShaderNodeMath'); sbn.operation = 'MULTIPLY'; sbn.inputs[1].default_value = 0.22; L.new(nz.outputs['Fac'], sbn.inputs[0])
    L.new(sbn.outputs[0], adn.inputs[1])
    L.new(adn.outputs[0], ramp.inputs['Fac'])
    bg = N.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 1.0; L.new(ramp.outputs[0], bg.inputs['Color'])
    o = N.new('ShaderNodeOutputWorld'); L.new(bg.outputs[0], o.inputs[0])
    vs = N.new('ShaderNodeVolumeScatter'); vs.inputs['Density'].default_value = float(os.environ.get('NR_FOG', '0.0018')); vs.inputs['Color'].default_value = hexc('#9a60c8'); vs.inputs['Anisotropy'].default_value = 0.35
    L.new(vs.outputs[0], o.inputs['Volume'])

def mist():
    me = bpy.data.meshes.new('mist'); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('mist', me); ob.scale = (460, 150, 9.0); ob.location = (50, -20, 4.5); bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new('mist'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    v = nt.nodes.new('ShaderNodeVolumeScatter'); v.inputs['Density'].default_value = float(os.environ.get('NR_MIST', '0.028')); v.inputs['Color'].default_value = hexc('#c88adf'); v.inputs['Anisotropy'].default_value = 0.4
    o = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(v.outputs[0], o.inputs['Volume']); me.materials.append(m)

def camera():
    cam = bpy.data.cameras.new('cam'); ob = bpy.data.objects.new('cam', cam); bpy.context.scene.collection.objects.link(ob); bpy.context.scene.camera = ob
    cfg = {
        'f2': ((-75.0, -8.0, 66.0), (112.0, -7.0, 40.0), 27),
        'f3': ((-6.0, -68.0, 22.0), (0.0, 6.0, 17.0), 25),
        'f4': ((-8.0, -9.5, 11.0), (118.0, -7.0, 40.0), 19),
    }[FRAME]
    ob.location = cfg[0]; d = Vector(cfg[1]) - Vector(cfg[0]); ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); cam.lens = cfg[2]; cam.sensor_width = 36
    cam.clip_end = 1500

def render_setup():
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = 4; sc.cycles.glossy_bounces = 4; sc.cycles.diffuse_bounces = 1; sc.cycles.transmission_bounces = 0; sc.cycles.transparent_max_bounces = 16
    sc.cycles.volume_bounces = 1; sc.cycles.sample_clamp_indirect = 8.0
    sc.cycles.volume_step_rate = 4.0 if hasattr(sc.cycles, 'volume_step_rate') else 1
    sc.render.resolution_x = 1920; sc.render.resolution_y = 1080; sc.render.resolution_percentage = RESPCT
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
    sc.render.filepath = OUT; sc.render.image_settings.file_format = 'PNG'
    sc.render.film_transparent = False
    if os.environ.get('NR_FS', '0') == '1':
        try:
            sc.render.use_freestyle = True; sc.render.line_thickness_mode = 'ABSOLUTE'; sc.render.line_thickness = 1.6 * max(0.5, RESPCT / 100)
            vl = bpy.context.view_layer; vl.use_freestyle = True
            ls = vl.freestyle_settings.linesets.new('ink'); ls.select_by_collection = True; ls.collection = bpy.data.collections['ink']
            ls.select_silhouette = True; ls.select_border = True; ls.select_crease = True; ls.select_by_visibility = True
            vl.freestyle_settings.crease_angle = math.radians(80)
            st = ls.linestyle; st.color = hexc('#0a0414')[:3]; st.thickness = 1.7
            try:
                if os.environ.get('NR_WOB', '1') == '1':
                    m = st.geometry_modifiers.new('wob', 'SINUS_DISPLACEMENT'); m.wavelength = 14.0; m.amplitude = 1.2; m.phase = 0.0
            except Exception as e: print('wobble fail', e)
        except Exception as e:
            print('freestyle fail', e)

def main():
    global FOCUS, TEXT_COLL
    clear()
    ink, neon = make_objects(); TEXT_COLL = neon
    FOCUS = {'f2': (40, YC, -1, 150), 'f3': (-4, YC, 90, 190), 'f4': (62, YC, 62, 170)}[FRAME]
    ground()
    # near rows: north (front plane y=Y_N, body deeper), south (front plane Y_S, extends -y)
    row(Y_N, 18, -1, -75, 84, 16, 34 if FRAME == 'f3' else 40)
    row(Y_S, 18, 1, 60 if FRAME == 'f3' else -75, 84, 12 if FRAME == 'f2' else 20, 24 if FRAME == 'f2' else 56)
    # cross-avenue stubs behind: far blocks
    far_blocks()
    route(); street_furniture(); park(); helix()
    flush(ink, neon)
    world(); mist(); camera(); render_setup()
    bpy.ops.render.render(write_still=True)

main()
