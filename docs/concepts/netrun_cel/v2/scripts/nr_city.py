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
        if XF[0]:
            c_, s_, tx_, ty_, tz_ = XF[0]
            pts = [(p_[0] * c_ - p_[1] * s_ + tx_, p_[0] * s_ + p_[1] * c_ + ty_, p_[2] + tz_) for p_ in pts]
        o = len(self.v)
        self.v += pts; self.f += [tuple(i + o for i in fc) for fc in faces]
        self.c += [col] * len(pts); self.w += [win] * len(pts)
ACC = {k: Acc(k) for k in ('body', 'far', 'solid', 'flat', 'ground', 'ink', 'glow')}
CAMLOC = [0.0, 0.0, 0.0]
INK_FIXED = [None]
XF = [None]  # local->world frame of a facade: (cos, sin, tx, ty, tz)
INK_PX = float(os.environ.get('NR_INKPX', '2.0'))
INK_JIT = random.Random(99)
WS = 1.0
def ink_t(cx, cy, cz, k=1.0):
    if XF[0]:
        c_, s_, tx_, ty_, tz_ = XF[0]
        cx, cy, cz = cx * c_ - cy * s_ + tx_, cx * s_ + cy * c_ + ty_, cz + tz_
    if INK_FIXED[0] is not None:
        return max(0.03, INK_FIXED[0] * INK_PX * k)
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
    if XF[0]:
        c_, s_, tx_, ty_, tz_ = XF[0]
        pos = (pos[0] * c_ - pos[1] * s_ + tx_, pos[0] * s_ + pos[1] * c_ + ty_, pos[2] + tz_); rz += math.atan2(s_, c_)
    ob.rotation_euler = (math.pi / 2, 0, rz); ob.location = pos
    TEXT_COLL.objects.link(ob)

# ------------------------------------------------------------------ names
SOLACE_NAMES = ['SOLACE', 'LEAFLET', 'HELIX', 'CHLORO', 'BIO-TEA', 'PETAL', 'SPORE BAR', 'VIRIDIAN', 'GENEBAR', 'CLINIC 24', 'SOLACE RX', 'FERN', 'CELLS', 'SAP', 'ALGAE', 'MOSS']
OTHER_NAMES = ['NOODLE', 'KARAOKE', 'ARCADE', 'PAWN', 'VOLTA', 'ORBIT', 'DATA', 'TEA', 'SUSHI', 'HOTEL', 'OPEN 24', 'PHARMA', 'BAR', 'RAMEN']
JP = ['ソラス', '葉', '薬', '茶', '24', '営業中', 'ラーメン', '酒', '遺伝子', 'カラオケ']
WARM = '#FFE0A0'; CYAN = '#5EF0FF'; PINK = '#FF4696'; AMBER = '#FFAA28'; LIME = '#96FF46'
SHOPCOLS = [WARM, WARM, CYAN, PINK, LIME, AMBER, '#FFFFFF']

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
    u = mn('ADD', sep.outputs['X'], sep.outputs['Y']); u = mn('DIVIDE', u, 0.95 * WS); v = mn('DIVIDE', sep.outputs['Z'], 1.25 * WS)
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
    e = N.new('ShaderNodeEmission'); L.new(fog_mix(nt, fin2.outputs[2]), e.inputs['Color']); e.inputs['Strength'].default_value = float(os.environ.get('NR_BODYK', '0.5'))
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
    L.new(at.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = float(os.environ.get('NR_GEMIT', '0.0'))
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
    vs = N.new('ShaderNodeVolumeScatter'); vs.inputs['Density'].default_value = float(os.environ.get('NR_FOG', '0.0')); vs.inputs['Color'].default_value = hexc('#9a60c8'); vs.inputs['Anisotropy'].default_value = 0.35
    L.new(vs.outputs[0], o.inputs['Volume'])

MIST_BOX = [(400, 300, 9.0), (0, 0, 4.5)]
def mist():
    me = bpy.data.meshes.new('mist'); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('mist', me); ob.scale = MIST_BOX[0]; ob.location = MIST_BOX[1]; bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new('mist'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    v = nt.nodes.new('ShaderNodeVolumeScatter'); v.inputs['Density'].default_value = float(os.environ.get('NR_MIST', '0.028')); v.inputs['Color'].default_value = hexc('#c88adf'); v.inputs['Anisotropy'].default_value = 0.4
    o = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(v.outputs[0], o.inputs['Volume']); me.materials.append(m)

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


# ====================================================================== REAL CITY LAYOUT (r43 data)
import json
CITY = json.load(open('D:/rc_scratch/netrun_cel/city/lots_city.json'))
BU = 2.0                                   # metres per world BU (a lot is 6 BU = 12 m)
CAMD = CITY['camera']; RECT = CAMD['city_rect']; DC = CAMD['district_centre']; LB = CAMD['lot_bu']
GR = CITY['ground']; RWID = RECT[2]
LM = LB * BU
KIND = ['halcyon', 'solace', 'halcyon', 'meridian', 'orbital', 'aurelian']   # CityCorpColor kind = 1 + index in [solace, halcyon, meridian, orbital, aurelian]
STREET = {(a[0], a[1]) for a in CITY['streets']}
PLAZA = {(a[0], a[1]) for a in CITY['plazas']}
PARK = {(a[0], a[1]) for a in CITY['parks']}
PRISMS = CITY['prisms']
SOL = CITY['hqs']['solace']                 # lots x, y, w, h
BUILT = set()
for _p in PRISMS:
    _c = _p['cell']
    for _i in range(_c[0], _c[0] + _c[2]):
        for _j in range(_c[1], _c[1] + _c[3]): BUILT.add((_i, _j))

def cell_ground(i, j):
    i = min(max(i, RECT[0]), RECT[0] + RWID - 1); j = min(max(j, RECT[1]), RECT[1] + RECT[3] - 1)
    return GR[(j - RECT[1]) * RWID + (i - RECT[0])] * BU
def vh(i, j):
    return (cell_ground(i - 1, j - 1) + cell_ground(i, j - 1) + cell_ground(i - 1, j) + cell_ground(i, j)) / 4.0
def lot_xy(i, j): return ((i - DC[0]) * LM, -(j - DC[1]) * LM)
def gz(x, y):
    u = x / LM + DC[0]; v = -y / LM + DC[1]
    i0 = math.floor(u); j0 = math.floor(v); fu = u - i0; fv = v - j0
    return (vh(i0, j0) * (1 - fu) * (1 - fv) + vh(i0 + 1, j0) * fu * (1 - fv) + vh(i0, j0 + 1) * (1 - fu) * fv + vh(i0 + 1, j0 + 1) * fu * fv)
def LOT(i, j, dz=0.0):
    x, y = lot_xy(i, j); return (x, y, gz(x, y) + dz)

# ---------------- the iso camera of frame 1 (CityIsoCamera maths)
def iso_basis(yaw, pitch):
    y = math.radians(yaw); p = math.radians(pitch)
    f = Vector((math.cos(y) * math.cos(p), -math.sin(p), -math.sin(y) * math.cos(p)))
    r = Vector((math.sin(y), 0, math.cos(y))); u = r.cross(f)
    return f, r, u
def iso_unproject(px, py, target, ortho, h=0.0):
    f, r, u = iso_basis(CAMD['yaw'], CAMD['pitch']); vp = CAMD['viewport']
    oh = ortho * vp[1] / vp[0]; xc = (px / vp[0] - 0.5) * ortho; yc = (0.5 - py / vp[1]) * oh
    o = Vector(target) + r * xc + u * yc
    return o + f * ((h - o.y) / f.y)

FOCUS_L = None
def lod_cell(ci, cj):
    fx, fy, r2, r1 = FOCUS_L
    d = math.hypot(ci - fx, cj - fy)
    return 2 if d < r2 else (1 if d < r1 else 0)

def side_streets(ci, cj, cw, ch):
    def frac(cells):
        n = sum(1 for c in cells if (c in STREET or c in PLAZA) and c not in BUILT)
        return n / max(1, len(cells))
    return {
        'S': frac([(ci + k, cj + ch) for k in range(cw)]) >= 0.5,
        'N': frac([(ci + k, cj - 1) for k in range(cw)]) >= 0.5,
        'E': frac([(ci + cw, cj + k) for k in range(ch)]) >= 0.5,
        'W': frac([(ci - 1, cj + k) for k in range(ch)]) >= 0.5}

def facade_local(side, x0, x1, y0, y1, z0, h, P, cn):
    if side == 'S':   th, ox, oy, w, dep = 0.0, (x0 + x1) / 2, y0, x1 - x0, y1 - y0
    elif side == 'N': th, ox, oy, w, dep = math.pi, (x0 + x1) / 2, y1, x1 - x0, y1 - y0
    elif side == 'E': th, ox, oy, w, dep = math.pi / 2, x1, (y0 + y1) / 2, y1 - y0, x1 - x0
    else:             th, ox, oy, w, dep = -math.pi / 2, x0, (y0 + y1) / 2, y1 - y0, x1 - x0
    XF[0] = (math.cos(th), math.sin(th), ox, oy, z0)
    try:
        # pavement strip and kerb in front of the facade
        box('ground', -w / 2, w / 2, -3.2, 0.0, -1.2, 0.14, hexc('#2e2a46'))
        beam('flat', (-w / 2, -3.2, 0.16), (w / 2, -3.2, 0.16), .06, hexc('#5a3a9a', 0.9))
        if w > 9:
            for lx in (-w / 2 + 1.2, w / 2 - 1.2):
                beam('solid', (lx, -2.6, 0), (lx, -2.6, 7.0), 0.16, hexc('#241833'))
                box('flat', lx - .3, lx + .3, -2.9, -2.3, 7.0, 7.4, hexc('#FFE3B0', 4.5))
        street_detail(-w / 2, w / 2, 0.0, dep, -0.10, -1, h, P, cn)
    finally:
        XF[0] = None

TALL = []
def building_data(p, skip_hq_solace=True):
    ci, cj, cw, ch = p['cell']
    if skip_hq_solace and p['hq'] and SOL[0] <= ci < SOL[0] + SOL[2] and SOL[1] <= cj < SOL[1] + SOL[3]:
        return
    poly = p['poly']
    xs = [q[0] * BU for q in poly]; ys = [-q[1] * BU for q in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    z0 = p['y0'] * BU; h = p['h'] * BU
    if h < 0.8: return
    lod = lod_cell(ci + cw / 2, cj + ch / 2)
    R.seed(p['key'] & 0x7fffffff)
    ak = p['ak']; cn = KIND[ak] if 1 <= ak <= 5 else 'solace'
    P = CORP[cn]
    dim = 0.62 if lod == 0 else 1.0
    body = hexc(P['body'] if R.random() < 0.7 else P['body2']); body = (body[0] * dim, body[1] * dim, body[2] * dim, 1)
    winc = hexc(P['win']); lit = R.uniform(0.1, 0.3) * (0.7 if lod == 0 else 1.0)
    acc = 'body' if lod >= 1 else 'far'
    zt = z0 + h
    win = (winc[0], winc[1], winc[2], lit)
    tp = p['taper']; hi = zt
    if tp < 0.97 and h > 8:
        hl = z0 + h * 0.62; ins = (1.0 - tp) * 0.5 * min(x1 - x0, y1 - y0) * 1.2
        box(acc, x0, x1, y0, y1, z0 - 2.5, hl, body, win)
        box(acc, x0 + ins, x1 - ins, y0 + ins, y1 - ins, hl, zt, body, win)
        bx0, bx1, by0, by1 = x0 + ins, x1 - ins, y0 + ins, y1 - ins
    else:
        box(acc, x0, x1, y0, y1, z0 - 2.5, zt, body, win)
        bx0, bx1, by0, by1 = x0, x1, y0, y1
    ACC_ON = R.random() < (0.45 if cn == 'solace' else 0.28)
    kind = R.choice(['parapet', 'corner', 'crown'])
    sides = side_streets(ci, cj, cw, ch)
    rim = hexc(P['rim'], 3.2); rimd = hexc(P['rim'], 2.0)
    if ACC_ON and lod >= 0:
        face = [k for k, v in sides.items() if v] or ['S']
        fs = R.choice(face)
        if fs in ('S', 'N'):
            yy = (by0 - 0.1) if fs == 'S' else (by1 + 0.1); ea, eb = (bx0, yy), (bx1, yy)
        else:
            xx = (bx1 + 0.1) if fs == 'E' else (bx0 - 0.1); ea, eb = (xx, by0), (xx, by1)
        if kind in ('parapet', 'crown'):
            beam('flat', (ea[0], ea[1], zt), (eb[0], eb[1], zt), 0.16, rim)
            if kind == 'crown': beam('flat', (ea[0], ea[1], zt - 1.6), (eb[0], eb[1], zt - 1.6), 0.1, rimd)
        else:
            beam('flat', (ea[0], ea[1], z0 + 1.0), (ea[0], ea[1], zt), 0.14, rim)
    if zt - z0 > 40 or lod == 0:
        mh = R.uniform(4, 14); mx = (bx0 + bx1) / 2; my = (by0 + by1) / 2
        beam('flat', (mx, my, zt), (mx, my, zt + mh), 0.18, hexc('#10081c'))
        box('flat', mx - .3, mx + .3, my - .3, my + .3, zt + mh, zt + mh + .6, hexc(R.choice(['#FF3030', P['acc']]), 5))
    if lod >= 1 and h > 40: TALL.append((zt, (bx0 + bx1) / 2, (by0 + by1) / 2, cn))
    if lod == 1 and sides.get('S', False) or lod == 1 and any(sides.values()):
        # district level: lit ground-floor strip on the first street side
        shopc = hexc(R.choice(SHOPCOLS), 2.2)
        s0 = [k for k, v in sides.items() if v][0]
        if s0 == 'S': box('flat', x0 + .5, x1 - .5, y0 - 0.1, y0 - 0.05, z0 + .4, z0 + 3.6, shopc)
        elif s0 == 'N': box('flat', x0 + .5, x1 - .5, y1 + 0.05, y1 + 0.1, z0 + .4, z0 + 3.6, shopc)
        elif s0 == 'E': box('flat', x1 + 0.05, x1 + 0.1, y0 + .5, y1 - .5, z0 + .4, z0 + 3.6, shopc)
        else: box('flat', x0 - 0.1, x0 - 0.05, y0 + .5, y1 - .5, z0 + .4, z0 + 3.6, shopc)
        if h > 24 and R.random() < 0.4:
            ac = hexc(R.choice([P['acc'], P['rim'], '#FFAA28']), 2.6)
            box('flat', bx0 + .6, bx1 - .6, (by0 + by1) / 2 - .1, (by0 + by1) / 2 + .1, zt + .4, zt + 2.8, ac)
    if lod >= 2 and h >= 6.0:
        for sd, on in sides.items():
            if on and (x1 - x0 if sd in 'SN' else y1 - y0) >= 5.0:
                facade_local(sd, x0, x1, y0, y1, z0, min(h, zt - z0), P, cn)

# ---------------- ground, trees, route, helix
def lot_class_col(i, j):
    t = (i, j)
    if FRAME == 'f2':
        if t in PLAZA: return hexc('#4a4a70')
        if t in PARK and t not in STREET: return hexc('#1f7a42')
        if t in STREET: return hexc('#2c2842')
        return hexc('#38335a')
    if t in PLAZA: return hexc('#2c2c4a')
    if t in PARK and t not in STREET: return hexc('#0f3a2a')
    if t in STREET: return hexc('#1c1830')
    return hexc('#2a2740')
def build_ground(reg):
    i0, i1, j0, j1 = reg
    for j in range(j0, j1 + 1):
        for i in range(i0, i1 + 1):
            pts = []
            for (a, b) in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)):
                x, y = lot_xy(a, b); pts.append((x, y, vh(a, b)))
            ACC['ground'].add_poly(pts, [(3, 2, 1, 0)], lot_class_col(i, j))
    # far plain below everything
    ACC['ground'].add_poly([(-9000, -9000, -3), (9000, -9000, -3), (9000, 9000, -3), (-9000, 9000, -3)], [(3, 2, 1, 0)], hexc('#14102a'))

TREE_CLEAR = [0, 0, 0]
TREE_P = 0.18
TREE_N = 2
TREE_S = (2.6, 4.6)
def build_street_lines(reg, focus, rad):
    i0, i1, j0, j1 = reg
    for a in CITY['streets']:
        i, j, ai, aj, tr, col = a
        if not (i0 <= i <= i1 and j0 <= j <= j1) or col == '000000' or col == '': continue
        if math.hypot(i - focus[0], j - focus[1]) > rad: continue
        c = hexc('#' + col, 2.4 if tr > 0.3 else 1.1)
        w = 0.5 + 1.2 * min(1.0, tr)
        cx, cy = lot_xy(i + 0.5, j + 0.5); z = gz(cx, cy) + 0.07
        if ai: quad_flat('flat', [(cx - LM / 2, cy - w, z), (cx + LM / 2, cy - w, z), (cx + LM / 2, cy + w, z), (cx - LM / 2, cy + w, z)], c)
        if aj: quad_flat('flat', [(cx - w, cy - LM / 2, z), (cx + w, cy - LM / 2, z), (cx + w, cy + LM / 2, z), (cx - w, cy + LM / 2, z)], c)

def build_trees(reg, focus, rad):
    R2 = random.Random(5)
    i0, i1, j0, j1 = reg
    for j in range(j0, j1 + 1):
        for i in range(i0, i1 + 1):
            if (i, j) not in PARK or (i, j) in STREET or (i, j) in BUILT or (i, j) in PLAZA: continue
            if math.hypot(i - focus[0], j - focus[1]) > rad: continue
            if math.hypot(i - TREE_CLEAR[0], j - TREE_CLEAR[1]) < TREE_CLEAR[2]: continue
            for _ in range(TREE_N):
                if R2.random() > TREE_P: continue
                x, y = lot_xy(i + R2.random(), j + R2.random()); z = gz(x, y)
                s = R2.uniform(*TREE_S)
                tone = hexc(R2.choice(['#1a5a3c', '#16503a', '#1d6a40'])); top = hexc(R2.choice(['#3ea857', '#4fbe5c', '#6fd860'])); shade = R2.uniform(0.7, 1.1)
                def cf(n, tone=tone, top=top, shade=shade):
                    if n.z > 0.45: return (top[0] * shade, top[1] * shade, top[2] * shade, 1)
                    if n.x > 0.3: return (tone[0] * 1.5, tone[1] * 1.5, tone[2] * 1.5, 1)
                    return tone
                add_blob('flat', (x, y, z + s * 1.2), s, s, s * 0.9, cf)
                beam('solid', (x, y, z), (x, y, z + s * 0.9), .35, hexc('#2a1f2a'))

def build_route(pts_lot, node_ids, sel, rw=0.34, rs=1.0, types=None, final_white=False):
    P3 = [LOT(i, j) for (i, j) in pts_lot]
    lc = hexc(LIME, 5.0)
    for a, b in zip(P3, P3[1:]):
        d = Vector((b[0] - a[0], b[1] - a[1], 0))
        if d.length < 1e-6: continue
        n = Vector((-d.y, d.x, 0)).normalized() * rw
        quad_flat('flat', [(a[0] - n.x, a[1] - n.y, a[2] + .12), (b[0] - n.x, b[1] - n.y, b[2] + .12), (b[0] + n.x, b[1] + n.y, b[2] + .12), (a[0] + n.x, a[1] + n.y, a[2] + .12)], lc)
    # chevrons every ~6 m
    acc_d = 0.0
    for a, b in zip(P3, P3[1:]):
        seg = Vector((b[0] - a[0], b[1] - a[1], 0)); L_ = seg.length
        if L_ < 1e-6: continue
        dirn = seg / L_; nrm = Vector((-dirn.y, dirn.x, 0)); k = 0.0
        while k < L_:
            if acc_d >= 6.0:
                acc_d = 0.0; c = Vector(a) + dirn * k
                for sg in (-1, 1):
                    beam('flat', (c.x - dirn.x * 0.9 + nrm.x * sg * 0.9, c.y - dirn.y * 0.9 + nrm.y * sg * 0.9, c.z + .14), (c.x + dirn.x * 0.4, c.y + dirn.y * 0.4, c.z + .14), 0.16 * rs, hexc(LIME, 4.5))
            step = 1.0; k += step; acc_d += step
    for n_i, idx in enumerate(node_ids):
        x, y, z = P3[idx]; t = types[n_i] if types else 'fight'
        c = NCOL[t]
        add_ring('flat', (x, y), 1.1 * rs, 1.5 * rs, hexc(c, 4.5), 32, z=z + .16)
        add_ring('flat', (x, y), 0.1, 1.0 * rs, hexc(c, 1.2), 20, z=z + .15)
        if n_i == sel:
            add_ring('flat', (x, y), 2.0 * rs, 2.25 * rs, hexc('#FFFFFF', 3.0), 32, z=z + .17)
            beam('flat', (x, y, z + .2), (x, y, z + 6.0 * rs), 0.11 * rs, hexc('#EFFFE0', 4.0))
            ph = z + 6.0 * rs
            ACC['flat'].add_poly([(x, y, ph + .1 * rs), (x + 0.8 * rs, y, ph + 1.2 * rs), (x, y, ph + 2.3 * rs), (x - 0.8 * rs, y, ph + 1.2 * rs)], [(0, 1, 2, 3), (3, 2, 1, 0)], hexc('#EFFFE0', 4.0))
NCOL = {'shop': LIME, 'fight': '#FF3A6E', 'event': '#FFD23A', 'elite': PINK, 'rest': CYAN, 'hq': '#FFFFFF'}

def build_hq():
    """BESPOKE Solace HQ set piece: plaza rings, helix, halo. Hand-authored, not procedural."""
    cx_l = SOL[0] + SOL[2] / 2.0; cy_l = SOL[1] + SOL[3] / 2.0
    cx, cy, cz = LOT(cx_l, cy_l)
    coll = bpy.data.collections['ink']
    def mk(name, col):
        m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
        e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value = col
        o = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(e.outputs[0], o.inputs[0]); return m
    strand_m = mk('hx_strand', hexc('#8CFF3C', 1.3)); rim_m = mk('hx_rim', hexc('#EFFFC0', 3.5))
    # plaza rings (radii in metres; plaza is 120 m wide)
    for r, c, k in ((54, LIME, 2.6), (44, '#B8FF78', 1.4), (30, PINK, 2.2), (18, LIME, 2.6)):
        add_ring('flat', (cx, cy), r - .45, r + .45, hexc(c, k), 72, z=cz + .3)
    for a in range(0, 360, 30):
        ar = math.radians(a); beam('flat', (cx + 18 * math.cos(ar), cy + 18 * math.sin(ar), cz + .32), (cx + 54 * math.cos(ar), cy + 54 * math.sin(ar), cz + .32), 0.18, hexc(LIME, 1.4))
    H = 170.0; turns = 2.6; rad = 11.0; N = 200
    def rr(t): return rad * (1.0 + 0.35 * math.sin(math.pi * t) ** 2) * (0.75 + 0.25 * min(1.0, t * 6))
    for s_ in (0, 1):
        cu = bpy.data.curves.new('hx%d' % s_, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 2.7; cu.bevel_resolution = 3; cu.resolution_u = 4
        sp = cu.splines.new('POLY'); sp.points.add(N)
        for i in range(N + 1):
            t = i / N; a = 2 * math.pi * turns * t + s_ * math.pi; r_ = rr(t)
            sp.points[i].co = (cx + r_ * math.cos(a), cy + r_ * math.sin(a), cz + 4 + H * t, 1)
        cu.materials.append(strand_m); ob = bpy.data.objects.new('hx%d' % s_, cu); coll.objects.link(ob)
        cu2 = bpy.data.curves.new('hxr%d' % s_, 'CURVE'); cu2.dimensions = '3D'; cu2.bevel_depth = 0.55; cu2.bevel_resolution = 1; cu2.resolution_u = 4
        sp2 = cu2.splines.new('POLY'); sp2.points.add(N)
        for i in range(N + 1):
            t = i / N; a = 2 * math.pi * turns * t + s_ * math.pi; r_ = rr(t) + 1.1
            sp2.points[i].co = (cx + r_ * math.cos(a), cy + r_ * math.sin(a), cz + 4 + H * t + 1.0, 1)
        cu2.materials.append(rim_m); TEXT_COLL.objects.link(bpy.data.objects.new('hxr%d' % s_, cu2))
    for i in range(3, N - 3, 7):
        t = i / N; z = cz + 4 + H * t; r_ = rr(t); a = 2 * math.pi * turns * t
        p0 = (cx + r_ * math.cos(a), cy + r_ * math.sin(a), z); p1 = (cx - r_ * math.cos(a), cy - r_ * math.sin(a), z)
        beam('flat', p0, p1, 1.0, hexc(PINK if (i // 7) % 2 == 0 else LIME, 3.4))
        add_blob('flat', ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, z), 2.2, 2.2, 1.4, lambda n: hexc('#D8FFB0', 1.6))
    add_ring('flat', (cx, cy), 17.0, 18.8, hexc(PINK, 5.0), 64, z=cz + 4 + H + 8)
    add_ring('flat', (cx, cy), 13.5, 14.5, hexc(LIME, 5.0), 64, z=cz + 4 + H + 8.8)
    beam('flat', (cx, cy, cz + 4), (cx, cy, cz + 4 + H + 8), 1.0, hexc('#CFFF90', 1.6))
    return cx, cy, cz

def camera_for(frame):
    cam = bpy.data.cameras.new('cam'); ob = bpy.data.objects.new('cam', cam); bpy.context.scene.collection.objects.link(ob); bpy.context.scene.camera = ob
    cam.sensor_width = 36; cam.clip_end = 20000; cam.clip_start = 0.5
    if frame == 'f2':
        f, r, u = iso_basis(CAMD['yaw'], CAMD['pitch'])
        T = F2_TARGET
        fb = Vector((f.x, -f.z, f.y)); tb = Vector((T.x * BU, -T.z * BU, T.y * BU))
        cam.type = 'ORTHO'; cam.ortho_scale = F2_ORTHO * BU
        ob.location = tb - fb * 6000.0; ob.rotation_euler = fb.to_track_quat('-Z', 'Y').to_euler()
    else:
        loc, tgt, lens = CAMS[frame]
        ob.location = loc; d = Vector(tgt) - Vector(loc); ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); cam.lens = lens
    return ob

F2_PIX = (1330, 560); F2_ZOOM = float(os.environ.get('NR_ZOOM', '3.0'))
F2_TARGET = iso_unproject(F2_PIX[0], F2_PIX[1], CAMD['target'], CAMD['ortho'])
F2_ORTHO = CAMD['ortho'] / F2_ZOOM
CAMS = {}

def main():
    global FOCUS_L, TEXT_COLL, WS, TREE_P, TREE_N, TREE_S
    clear()
    ink, neon = make_objects(); TEXT_COLL = neon
    WS = float(os.environ.get('NR_WINSCALE', '2.6' if FRAME == 'f2' else '1.0'))
    os.environ['NR_GEMIT'] = os.environ.get('NR_GEMIT', '0.55' if FRAME == 'f2' else '0.06')
    os.environ['NR_BODYK'] = os.environ.get('NR_BODYK', '1.7' if FRAME == 'f2' else '0.5')
    cfgs = {
        'f2': dict(reg=(-84, -8, -62, 6), focus=(-45, -26, -1, 60), tree=(-45, -26, 40)),
        'f3': dict(reg=(-92, 4, -52, 34), focus=(-37, -25, 16, 55), tree=(-37, -30, 40)),
        'f4': dict(reg=(-112, -6, -80, 0), focus=(-64, -37, 18, 60), tree=(-60, -37, 60)),
    }[FRAME]
    FOCUS_L = cfgs['focus']
    CAMS['f3'] = (LOT(-37.5, -27.1, 15.0), LOT(-37.5, -21.0, 10.0), 22)
    if FRAME == 'f2':
        TREE_P = 0.95; TREE_N = 3; TREE_S = (4.0, 7.0)
    TREE_CLEAR[:] = [-37.5, -27.1, 6.0] if FRAME == 'f3' else ([-78.0, -36.5, 6.0] if FRAME == 'f4' else [0, 0, 0])
    os.environ['NR_WINSCALE'] = os.environ.get('NR_WINSCALE', '2.6' if FRAME == 'f2' else '1.0')
    CAMS['f4'] = (LOT(-78.0, -36.5, 13.0), tuple(Vector(LOT(-38.0, -37.0)) + Vector((0, 0, 62.0))), 21)
    cl = {'f2': tuple(Vector(LOT(-45, -26)) + Vector((0, 0, 0))), 'f3': CAMS['f3'][0], 'f4': CAMS['f4'][0]}[FRAME]
    if FRAME == 'f2':
        f, r, u = iso_basis(CAMD['yaw'], CAMD['pitch']); T = F2_TARGET
        CAMLOC[:] = [T.x * BU - f.x * 6000, -T.z * BU + f.z * 6000, T.y * BU - f.y * 6000]
        INK_FIXED[0] = (F2_ORTHO * BU) / 1920.0 * 1.0
        MIST_BOX[0] = (500, 400, 0.01)
    else:
        CAMLOC[:] = list(cl)
    build_ground(cfgs['reg'])
    i0, i1, j0, j1 = cfgs['reg']
    for p in PRISMS:
        c = p['cell']
        if i0 - 2 <= c[0] <= i1 and j0 - 2 <= c[1] <= j1:
            building_data(p)
    build_trees(cfgs['reg'], (cfgs['tree'][0], cfgs['tree'][1]), cfgs['tree'][2])
    if FRAME == 'f2': build_street_lines(cfgs['reg'], (-45, -26), 55)
    # ---- routes
    def blvd(i): return -23.55
    if FRAME in ('f2', 'f3'):
        pts = [(i * 0.5, blvd(i * 0.5) + 0.25 * math.sin(i * 0.5 / 3.0)) for i in range(-136, -52)]
        ids = [k for k, (a, b) in enumerate(pts) if abs(a * 2 - round(a * 2)) < 1e-6 and (round(a) % 4 == 0 if FRAME == 'f2' else round(a) % 3 == 0) and a == round(a)]
        types = ['shop', 'fight', 'event', 'fight', 'elite', 'rest', 'fight', 'shop', 'fight', 'event'] * 3
        sel = min(range(len(ids)), key=lambda q: abs(pts[ids[q]][0] - (-39 if FRAME == 'f3' else -33)))
        big = FRAME == 'f2'
        build_route(pts, ids, sel, rw=0.8 if big else 0.34, rs=2.4 if big else 1.0, types=types)
    if FRAME == 'f4':
        pts = [(i * 0.5, -36.5) for i in range(-160, -104)] + [(-52 + k * 0.5, -36.5 + (-0.5) * (k / 28.0)) for k in range(1, 30)]
        pts = [(a, b) for (a, b) in pts]
        ids = [k for k, (a, b) in enumerate(pts) if a == round(a) and round(a) % 5 == 0]
        types = ['fight', 'event', 'shop', 'fight', 'elite', 'rest', 'fight', 'hq']
        ids = ids[-len(types):]
        build_route(pts, ids, len(ids) - 1, rw=0.34, rs=1.0, types=types)
    hx = build_hq()
    # searchlights from the tallest real towers of the region (corp colour)
    TALL.sort(key=lambda t: -t[0])
    used = []
    for (zt, bx, by, cn) in TALL:
        if all(math.hypot(bx - u[0], by - u[1]) > 90 for u in used) and len(used) < 4:
            used.append((bx, by)); light_beam((bx, by, zt + 6), (0.1, -0.1, 1.0), 160, 1.2, hexc(CORP[cn]['rim'], 3.2), a0=0.42)
    # car streaks on the boulevard (f2/f3) and the avenue (f4)
    R3 = random.Random(11)
    lanes = [(-26.35, 1), (-25.8, 1), (-24.45, -1), (-23.75, -1)] if FRAME != 'f4' else [(-36.8, 1), (-36.2, -1)]
    ax = (-56, -26) if FRAME != 'f4' else (-100, -52)
    for k in range(70):
        jl, dr = R3.choice(lanes); x0_ = lot_xy(R3.uniform(*ax), 0)[0]; Ls = R3.uniform(14, 46)
        y_ = lot_xy(0, jl)[1]; zz = gz(x0_, y_) + 0.14
        c = R3.choice([hexc('#FF2A22', 3.4), hexc('#FF2A22', 3.4), hexc('#FF4A30', 3.0), hexc('#FFFFFF', 3.0), hexc('#FFFFFF', 3.0), hexc('#FFD060', 2.6), hexc(PINK, 2.6)])
        quad_flat('flat', [(x0_, y_ - .09, zz), (x0_ + Ls, y_ - .09, zz), (x0_ + Ls, y_ + .09, zz), (x0_, y_ + .09, zz)], c)
    flush(ink, neon)
    if FRAME != 'f2':
        bx_, by_ = lot_xy(-37 if FRAME == 'f3' else -70, -26 if FRAME == 'f3' else -37)
        MIST_BOX[0] = (300, 200, 8.0); MIST_BOX[1] = (bx_, by_, gz(bx_, by_) + 4.0)
    world(); mist(); camera_for(FRAME); render_setup()
    bpy.ops.render.render(write_still=True)

main()
