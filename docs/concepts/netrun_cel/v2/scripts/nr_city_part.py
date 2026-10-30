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
