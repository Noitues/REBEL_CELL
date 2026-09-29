"""GLITCH VECTOR CRT - the city as a vector-monitor wireframe (Grease Pencil v3 + EEVEE).

blender -b --factory-startup --python city.py -- <mode> <out.png> [res_scale]
mode: night | heat | nodes_off
  night     : city + elevated highways + flyers + hologram billboards + Grid nodes on one plane
  heat      : same city (same seed) + helicopters, searchlights, drone swarm, red/blue corp rims
  nodes_off : night without the Grid layer (used behind combat and the Modem)
"""
import bpy, sys, os, math, random
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gv_lib as gv
import gv_font as gf

argv = sys.argv[sys.argv.index("--") + 1:]
MODE = argv[0]
OUT = argv[1]
RS = float(argv[2]) if len(argv) > 2 else 1.0
HEAT = MODE == "heat"
SEED = 7031

sc = gv.reset((int(1920 * RS), int(1080 * RS)), samples=6)
rng = random.Random(SEED)

# ------------------------------------------------------------------ camera (iso ortho)
TARGET = Vector((1.0, 1.0, 5.0))
EL, AZ = 57.0, 45.0
cam = gv.camera((0, 0, 0), (EL, 0, AZ), ortho_scale=44)
bpy.context.view_layer.update()  # matrix_world is identity until the depsgraph updates
V =cam.matrix_world.to_3x3() @ Vector((0, 0, -1))
cam.location = TARGET - V * 80
bpy.context.view_layer.update()
V = (cam.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
UPV = (cam.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
gv.bloom(strength=0.9, threshold=0.55, size=0.55)

N = 22
PITCH = 2.4
STREET = 0.62
HALF = N * PITCH / 2
HQ = Vector((-1.2, -1.2, 0))           # HQ block centre (near frame centre, fully framed)
HQ_H = 12.5


def depth_fade(p):
    """0 near camera .. 1 far (top of screen)."""
    d = (Vector(p) - TARGET).dot(V)
    s = (Vector(p) - TARGET).dot(UPV)
    return max(0.0, min(1.0, 0.5 + s / 34.0))


def fade_op(p, near=1.0, far=0.28):
    t = depth_fade(p)
    return near + (far - near) * t


# ------------------------------------------------------------------ layers
occ_verts, occ_faces = [], []
G_struct = gv.GP("struct", blend="ADD")
G_floor = gv.GP("floors", blend="ADD")
G_road = gv.GP("roads", blend="ADD")
G_traffic = gv.GP("traffic", blend="ADD")
G_holo = gv.GP("holo", blend="ADD")
G_sky = gv.GP("sky", blend="ADD")
G_net = gv.GP("net", blend="ADD")


def box_occluder(x0, y0, x1, y1, h, z0=0.0):
    b = len(occ_verts)
    k = 0.015  # shrink so a box's own edges are not hidden by it
    x0, y0, x1, y1, h = x0 + k, y0 + k, x1 - k, y1 - k, h - k
    occ_verts.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                      (x0, y0, h), (x1, y0, h), (x1, y1, h), (x0, y1, h)])
    for f in [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)]:
        occ_faces.append(tuple(b + i for i in f))


def palette_for(x, y, h):
    r = rng.random()
    if Vector((x, y, 0)).length < 9 and h > 4:
        base = "cyan" if r < 0.6 else "phosphor"
    else:
        base = "phosphor" if r < 0.78 else ("cyan" if r < 0.93 else "magenta")
    if HEAT and h > 5 and rng.random() < 0.35:
        base = "harm" if rng.random() < 0.6 else "cyan"
    return base


def building(x0, y0, x1, y1, h, cname, crown=False):
    box_occluder(x0, y0, x1, y1, h)
    c = gv.col(cname)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    o = fade_op((cx, cy, h))
    # vertical edges
    for (x, y) in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
        G_struct.line([(x, y, 0), (x, y, h)], c, 0.016, opac=[o * 0.35, o])
    # roof outline + inner roof inset (reads as parapet)
    G_struct.line([(x0, y0, h), (x1, y0, h), (x1, y1, h), (x0, y1, h)], c, 0.018, o, cyclic=True)
    ins = min(x1 - x0, y1 - y0) * 0.18
    G_floor.line([(x0 + ins, y0 + ins, h), (x1 - ins, y0 + ins, h), (x1 - ins, y1 - ins, h), (x0 + ins, y1 - ins, h)],
                 c, 0.009, o * 0.6, cyclic=True)
    # floor scanlines on the two camera-facing facades (x0 side and y0 side)
    step = 0.34
    z = step
    while z < h - 0.1:
        k = 0.55 * (0.35 + 0.65 * z / max(h, 0.1))
        G_floor.line([(x1, y1, z), (x1, y0, z), (x0, y0, z)], c, 0.0075, o * k)
        z += step
    # lit window dashes
    for _ in range(int(h * 2.2)):
        zz = rng.uniform(0.2, h - 0.15)
        if rng.random() < 0.5:
            xx = rng.uniform(x0 + 0.05, x1 - 0.25)
            G_floor.line([(xx, y0 - 0.003, zz), (xx + 0.18, y0 - 0.003, zz)], gv.col("white" if rng.random() < 0.3 else cname), 0.012, o * 0.9)
        else:
            yy = rng.uniform(y0 + 0.05, y1 - 0.25)
            G_floor.line([(x1 + 0.003, yy, zz), (x1 + 0.003, yy + 0.18, zz)], gv.col("white" if rng.random() < 0.3 else cname), 0.012, o * 0.9)
    if crown:
        # antenna + blinking tip
        G_struct.line([(cx, cy, h), (cx, cy, h + 1.2)], c, 0.012, o)
        G_sky.line([(cx, cy, h + 1.2), (cx, cy, h + 1.21)], gv.col("harm"), 0.06, o)


# ------------------------------------------------------------------ blocks + buildings
tall_list = []
for i in range(N):
    for j in range(N):
        bx = -HALF + i * PITCH + STREET / 2
        by = -HALF + j * PITCH + STREET / 2
        bw = PITCH - STREET
        cx, cy = bx + bw / 2, by + bw / 2
        if (Vector((cx, cy, 0)) - HQ).length < 1.0:
            continue  # HQ block handled separately
        dist = Vector((cx, cy, 0)).length
        down = max(0.0, 1.0 - dist / 22.0)
        # sidewalk outline on the ground (very dim)
        G_road.line([(bx, by, 0), (bx + bw, by, 0), (bx + bw, by + bw, 0), (bx, by + bw, 0)],
                    gv.col("phos_dim"), 0.008, fade_op((cx, cy, 0)) * 0.5, cyclic=True)
        split = rng.random()
        parts = []
        if split < 0.35:
            parts = [(bx, by, bx + bw, by + bw)]
        elif split < 0.7:
            m = bw * rng.uniform(0.4, 0.6)
            parts = [(bx, by, bx + m - 0.08, by + bw), (bx + m + 0.08, by, bx + bw, by + bw)]
        else:
            m = bw * 0.5
            parts = [(bx, by, bx + m - 0.07, by + m - 0.07), (bx + m + 0.07, by, bx + bw, by + m - 0.07),
                     (bx, by + m + 0.07, bx + m - 0.07, by + bw), (bx + m + 0.07, by + m + 0.07, bx + bw, by + bw)]
        for (a0, b0, a1, b1) in parts:
            if rng.random() < 0.08:
                continue  # plaza
            h = 0.4 + rng.random() ** 2.2 * (1.5 + 7.5 * down) + 0.6 * down
            h = round(h / 0.34) * 0.34 + 0.34
            du, dv = (cx - HQ.x), (cy - HQ.y)
            along, across = (du - dv) / 1.414, (du + dv) / 1.414
            if 0 < along < 12 and abs(across) < 3.2:
                h = min(h, 0.34 + 0.34 * int(along / 3))
            cn = palette_for(cx, cy, h)
            building(a0 + 0.05, b0 + 0.05, a1 - 0.05, b1 - 0.05, h, cn, crown=h > 5.5 and rng.random() < 0.5)
            if h > 3.2:
                tall_list.append(((a0 + a1) / 2, (b0 + b1) / 2, h, a0, b0, a1, b1))

# ------------------------------------------------------------------ HQ tower (the Cell), fully framed
hx, hy = HQ.x, HQ.y
tiers = [(1.9, 0.0, 4.2), (1.5, 4.2, 8.0), (1.05, 8.0, 10.6), (0.7, 10.6, HQ_H)]
for (r, z0, z1) in tiers:
    box_occluder(hx - r, hy - r, hx + r, hy + r, z1, z0)
    pk = gv.col("pink")
    for (x, y) in [(hx - r, hy - r), (hx + r, hy - r), (hx + r, hy + r), (hx - r, hy + r)]:
        G_struct.line([(x, y, z0), (x, y, z1)], pk, 0.024)
    for z in (z0, z1):
        G_struct.line([(hx - r, hy - r, z), (hx + r, hy - r, z), (hx + r, hy + r, z), (hx - r, hy + r, z)], pk, 0.026, cyclic=True)
    z = z0 + 0.28
    while z < z1 - 0.05:
        G_floor.line([(hx + r, hy + r, z), (hx + r, hy - r, z), (hx - r, hy - r, z)], gv.col("pink"), 0.009, 0.45)
        z += 0.28
    # diagonal bracing (scrappy, hand-built)
    G_floor.line([(hx - r, hy - r, z0), (hx + r, hy - r, z1)], gv.col("magenta"), 0.01, 0.5)
    G_floor.line([(hx + r, hy + r, z0), (hx + r, hy - r, z1)], gv.col("magenta"), 0.01, 0.5)
# hex crown
hexr = 1.25
crown = [(hx + hexr * math.cos(math.radians(60 * k + 30)), hy + hexr * math.sin(math.radians(60 * k + 30)), HQ_H + 0.9) for k in range(6)]
G_struct.line(crown, gv.col("pink"), 0.035, cyclic=True)
G_struct.line([(x, y, z - 0.35) for (x, y, z) in crown], gv.col("pink"), 0.02, 0.7, cyclic=True)
for (x, y, z) in crown:
    G_floor.line([(hx, hy, HQ_H), (x, y, z)], gv.col("pink"), 0.01, 0.6)
G_struct.line([(hx, hy, HQ_H), (hx, hy, HQ_H + 3.0)], gv.col("pink"), 0.018)
for k in range(4):
    zz = HQ_H + 1.3 + k * 0.4
    G_floor.line([(hx - 0.3 + k * 0.05, hy, zz), (hx + 0.3 - k * 0.05, hy, zz)], gv.col("pink"), 0.01, 0.8)
G_sky.line([(hx, hy, HQ_H + 3.0), (hx, hy, HQ_H + 3.01)], gv.col("acid"), 0.09)
# broadcast rings around the antenna (vector ripples)
for k in range(3):
    rr = 0.5 + k * 0.55
    ring = [(hx + rr * math.cos(a / 24 * 6.283), hy + rr * math.sin(a / 24 * 6.283), HQ_H + 3.0) for a in range(24)]
    G_sky.line(ring, gv.col("acid"), 0.012, 0.6 - k * 0.17, cyclic=True)

# ------------------------------------------------------------------ elevated highways (three levels)
def catmull(pts, seg=10):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = (Vector(P[i - 1]), Vector(P[i]), Vector(P[i + 1]), Vector(P[i + 2]))
        for k in range(seg):
            t = k / seg
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                                    (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(P[-2]))
    return out


def street(k):
    return -HALF + k * PITCH


routes = [
    # (control points, colour of rails)
    ([(street(0) - 3, street(9), 1.3), (street(6), street(9), 1.3), (street(9), street(11), 1.6),
      (street(13), street(11), 1.6), (street(17), street(8), 1.4), (street(23) + 3, street(8), 1.4)], "cyan"),
    ([(street(12), street(-1) - 3, 2.6), (street(12), street(6), 2.6), (street(11), street(10), 3.0),
      (street(14), street(15), 3.2), (street(14), street(23) + 3, 3.2)], "cyan"),
    ([(street(-1) - 3, street(15), 4.3), (street(5), street(16), 4.4), (street(8), street(13), 4.6),
      (street(8), street(5), 4.3), (street(16), street(3), 4.0), (street(23) + 3, street(3), 4.0)], "phosphor"),
    ([(street(4), street(-1) - 3, 2.0), (street(4), street(7), 2.0), (street(2), street(12), 2.2),
      (street(2), street(23) + 3, 2.2)], "phosphor"),
]
# double-deck: the high skyway gets a lower magenta deck under it (several levels of traffic)
routes.append(([(x, y, z - 1.5) for (x, y, z) in routes[2][0]], "magenta"))
for ri, (ctrl, cn) in enumerate(routes):
    path = catmull(ctrl, 14)
    # dense resample
    dense = [Vector(path[0])]
    for a, b in zip(path, path[1:]):
        a, b = Vector(a), Vector(b)
        n = max(1, int((b - a).length / 0.18))
        for s in range(1, n + 1):
            dense.append(a.lerp(b, s / n))
    L = len(dense)
    tang = [(dense[min(L - 1, i + 1)] - dense[max(0, i - 1)]).normalized() for i in range(L)]
    perp = [Vector((-t.y, t.x, 0)).normalized() for t in tang]
    w = 0.42
    for side in (-1, 1):
        rail = [tuple(dense[i] + perp[i] * w * side) for i in range(L)]
        G_road.line(rail, gv.col(cn), 0.026, opac=[fade_op(p) for p in rail])
        G_road.line(rail, gv.col(cn), 0.09, opac=[fade_op(p) * 0.1 for p in rail])
        rail2 = [tuple(dense[i] + perp[i] * w * side - Vector((0, 0, 0.1))) for i in range(L)]
        G_road.line(rail2, gv.col(cn), 0.008, opac=[fade_op(p) * 0.5 for p in rail2])
    # lane dashes
    for i in range(0, L - 2, 3):
        G_road.line([tuple(dense[i]), tuple(dense[i + 1])], gv.col(cn), 0.007, fade_op(dense[i]) * 0.45)
    # pylons
    for i in range(0, L, 16):
        p = dense[i]
        if abs(p.x) < HALF and abs(p.y) < HALF:
            G_road.line([tuple(p), (p.x, p.y, 0)], gv.col(cn), 0.012, opac=[fade_op(p) * 0.7, fade_op(p) * 0.1])
            box_occluder(p.x - 0.12, p.y - 0.12, p.x + 0.12, p.y + 0.12, p.z - 0.12)
    # deck occluder (thin slab so the city below is hidden under the road)
    for i in range(0, L - 1):
        a0 = dense[i] - perp[i] * w; a1 = dense[i] + perp[i] * w
        b0 = dense[i + 1] - perp[i + 1] * w; b1 = dense[i + 1] + perp[i + 1] * w
        bi = len(occ_verts)
        occ_verts.extend([tuple(a0 - Vector((0, 0, 0.12))), tuple(a1 - Vector((0, 0, 0.12))),
                          tuple(b1 - Vector((0, 0, 0.12))), tuple(b0 - Vector((0, 0, 0.12)))])
        occ_faces.append((bi, bi + 1, bi + 2, bi + 3))
    # traffic: phosphor persistence trails, two directions
    nveh = int(L / 1.1)
    for v in range(nveh):
        lane = rng.choice((-1, 1))
        i0 = rng.randrange(0, L - 12)
        ln = rng.randint(5, 11)
        seg = list(range(i0, i0 + ln))
        if lane < 0:
            seg = seg[::-1]
        pts = [tuple(dense[k] + perp[k] * (0.2 * lane) + Vector((0, 0, 0.04))) for k in seg]
        head = "white" if lane > 0 else "harm"
        tail = "cyan" if lane > 0 else "magenta"
        cols = [gv.col(tail) for _ in pts[:-1]] + [gv.col(head)]
        opac = [((k + 1) / ln) ** 2 * fade_op(pts[-1]) for k in range(ln)]
        radii = [0.01 + 0.03 * (k / ln) ** 2 for k in range(ln)]
        G_traffic.line(pts, gv.col(tail), 0.02, radii=radii, opac=opac, cols=cols)

# street-level traffic: dashed vector streams
for k in range(1, N):
    for axis in (0, 1):
        if rng.random() < 0.45:
            continue
        s = street(k)
        for v in range(rng.randint(3, 9)):
            t0 = rng.uniform(-HALF, HALF - 2)
            ln = rng.uniform(0.6, 1.8)
            npt = 7
            lane = rng.choice((-0.12, 0.12))
            pts = []
            for q in range(npt):
                t = t0 + ln * q / (npt - 1)
                pts.append((t, s + lane, 0.02) if axis == 0 else (s + lane, t, 0.02))
            if lane < 0:
                pts = pts[::-1]
            opac = [((q + 1) / npt) ** 2 * fade_op(pts[-1]) * 0.8 for q in range(npt)]
            G_traffic.line(pts, gv.col("amber" if lane > 0 else "cyan"), 0.014, opac=opac)

# ------------------------------------------------------------------ flying vehicles (vector glyphs + trails)
for f in range(16 if not HEAT else 8):
    z = rng.uniform(6.5, 9.5)
    cx, cy = rng.uniform(-18, 18), rng.uniform(-18, 18)
    r = rng.uniform(6, 14)
    a0 = rng.uniform(0, 6.283)
    span = rng.uniform(0.35, 0.8) * rng.choice((-1, 1))
    n = 18
    pts = [(cx + r * math.cos(a0 + span * q / n), cy + r * math.sin(a0 + span * q / n), z + 0.3 * math.sin(q / 4)) for q in range(n + 1)]
    op = [((q + 1) / (n + 1)) ** 2.5 * 0.8 for q in range(n + 1)]
    G_sky.line(pts, gv.col("cyan"), 0.012, opac=op)
    hx2, hy2, hz2 = pts[-1]
    d = Vector(pts[-1]) - Vector(pts[-2]); d.z = 0; d.normalize()
    pp = Vector((-d.y, d.x, 0))
    nose = Vector(pts[-1]) + d * 0.35
    glyph = [tuple(Vector(pts[-1]) - d * 0.2 + pp * 0.28), tuple(nose), tuple(Vector(pts[-1]) - d * 0.2 - pp * 0.28),
             tuple(Vector(pts[-1]) - d * 0.05)]
    G_sky.line(glyph, gv.col("white"), 0.02, cyclic=True)
    G_sky.line([tuple(Vector(pts[-1]) + pp * 0.3), tuple(Vector(pts[-1]) + pp * 0.301)], gv.col("gain"), 0.04)
    G_sky.line([tuple(Vector(pts[-1]) - pp * 0.3), tuple(Vector(pts[-1]) - pp * 0.301)], gv.col("harm"), 0.04)

# ------------------------------------------------------------------ hologram billboards
holo_mesh_v, holo_mesh_f = [], []
tall_list.sort(key=lambda t: (-t[2], t[0], t[1]))
chosen = []
for t in tall_list:
    if len(chosen) >= 10:
        break
    if all(math.hypot(t[0] - c[0], t[1] - c[1]) > 5.0 for c in chosen) and (Vector((t[0], t[1], 0)) - HQ).length > 3.5:
        chosen.append(t)
GLYPHS = "ABCDEFGHKMNPRSTUVWXYZ0123456789#"
for bi, (cx, cy, h, a0, b0, a1, b1) in enumerate(chosen):
    cn = ["magenta", "cyan", "magenta", "acid", "violet"][bi % 5] if not HEAT else ["harm", "magenta", "cyan"][bi % 3]
    c = gv.col(cn)
    face_x = bi % 2 == 0  # billboard on the x0 face or the y0 face (both face the camera)
    wdt = rng.uniform(2.4, 3.8)
    hgt = wdt * rng.uniform(0.5, 1.1)
    zb = max(1.0, h - hgt - rng.uniform(0.2, 1.0))
    off = 0.35
    if face_x:
        xw = a1 + off
        yc = (b0 + b1) / 2
        corners = [(xw, yc - wdt / 2, zb), (xw, yc + wdt / 2, zb), (xw, yc + wdt / 2, zb + hgt), (xw, yc - wdt / 2, zb + hgt)]
        uvec = Vector((0, 1, 0))
    else:
        yw = b0 - off
        xc = (a0 + a1) / 2
        corners = [(xc - wdt / 2, yw, zb), (xc + wdt / 2, yw, zb), (xc + wdt / 2, yw, zb + hgt), (xc - wdt / 2, yw, zb + hgt)]
        uvec = Vector((1, 0, 0))
    o = fade_op(corners[0])
    G_holo.line(corners, c, 0.02, o, cyclic=True)
    # corner ticks outside the frame
    c0 = Vector(corners[0])
    # scanlines
    rows = int(hgt / 0.07)
    for r_ in range(rows):
        zz = zb + (r_ + 0.5) * hgt / rows
        p0 = c0 + Vector((0, 0, zz - zb))
        G_holo.line([tuple(p0), tuple(p0 + uvec * wdt)], c, 0.004, o * 0.22)
    # illegible text rows + a big original logo mark
    lines = rng.randint(2, 4)
    for r_ in range(lines):
        zz = zb + hgt * (0.78 - r_ * 0.2)
        s = hgt * 0.11
        x = 0.12 * wdt
        while x < wdt * (0.92 if r_ else 0.6):
            ch = rng.choice(GLYPHS)
            for pl in gf.layout(ch, s, slant=0.1):
                pts = []
                for (gx, gy) in pl:
                    jx, jy = rng.uniform(-0.3, 0.3) * s / 6, rng.uniform(-0.6, 0.6) * s / 6  # scrambled -> illegible
                    p = c0 + uvec * (x + gx + jx) + Vector((0, 0, zz - zb + gy + jy))
                    pts.append(tuple(p))
                G_holo.line(pts, c if r_ else gv.col("white"), 0.008, o * (0.95 if r_ == 0 else 0.6))
            x += s * 0.85
    # logo: concentric shape at right
    lc = c0 + uvec * wdt * 0.78 + Vector((0, 0, hgt * 0.3))
    kind = bi % 3
    rr = hgt * 0.17
    ring = []
    for q in range(25):
        a = q / 24 * 6.283
        if kind == 0:
            ring.append(tuple(lc + uvec * rr * math.cos(a) + Vector((0, 0, rr * math.sin(a)))))
        elif kind == 1:
            ring.append(tuple(lc + uvec * rr * math.cos(round(a / 2.094) * 2.094) + Vector((0, 0, rr * math.sin(round(a / 2.094) * 2.094)))))
        else:
            ring.append(tuple(lc + uvec * rr * math.cos(round(a / 1.571) * 1.571 + 0.785) + Vector((0, 0, rr * math.sin(round(a / 1.571) * 1.571 + 0.785)))))
    G_holo.line(ring, gv.col("white"), 0.014, o)
    # translucent additive fill
    b_ = len(holo_mesh_v)
    holo_mesh_v.extend(corners)
    holo_mesh_f.append((b_, b_ + 1, b_ + 2, b_ + 3))
    # projector on the ground/roof below, beams to the corners
    pr = Vector(((corners[0][0] + corners[1][0]) / 2, (corners[0][1] + corners[1][1]) / 2, 0.05))
    pr = pr + (Vector((1.4, 0, 0)) if face_x else Vector((0, -1.4, 0)))
    for cc in corners:
        G_holo.line([tuple(pr), cc], c, 0.006, opac=[o * 0.7, o * 0.08])
    G_holo.line([tuple(pr), tuple(pr + Vector((0, 0, 0.01)))], c, 0.05, o)

holo_fill = gv.mesh_from("holo_fill", holo_mesh_v, holo_mesh_f, gv.emit_mat("holo_fill", gv.col("magenta" if not HEAT else "harm"), 1.0, 0.06))

# ------------------------------------------------------------------ Grid nodes + links on one plane (feedback 7.4)
NET_Z = 7.2
if MODE == "night":
    nodes = [("HQ", HQ.x, HQ.y, "pink"), ("RACK", 6.5, -4.5, "acid"), ("CLINIC", 9.0, 5.0, "acid"),
             ("DEPOT", 1.5, 9.5, "cyan"), ("RELAY", -13.0, -2.0, "cyan"), ("VAULT", 14.5, 11.0, "orange"),
             ("DOCKS", -6.0, -10.5, "cyan"), ("TOWER", 15.5, -2.5, "orange"), ("SPIRE", 4.0, 16.0, "orange")]
    links = [(0, 1, "turf"), (1, 2, "turf"), (0, 3, "open"), (0, 4, "open"), (2, 5, "threat"), (1, 7, "threat"),
             (3, 8, "threat"), (0, 6, "open"), (2, 3, "open"), (7, 5, "threat")]
    # faint plane grid, only around nodes (reads as a sheet of glass the map lives on)
    for gxv in range(-20, 22, 2):
        pts = [(gxv, yy, NET_Z) for yy in range(-20, 22, 2)]
        G_net.line(pts, gv.col("cyan"), 0.005, opac=[0.12 * max(0.0, 1 - Vector((gxv, yy, 0)).length / 22) for (_, yy, _) in pts])
        pts = [(yy, gxv, NET_Z) for yy in range(-20, 22, 2)]
        G_net.line(pts, gv.col("cyan"), 0.005, opac=[0.12 * max(0.0, 1 - Vector((yy, gxv, 0)).length / 22) for (yy, _, _) in pts])
    for (a, b, kind) in links:
        pa = Vector((nodes[a][1], nodes[a][2], NET_Z)); pb = Vector((nodes[b][1], nodes[b][2], NET_Z))
        d = (pb - pa); Ld = d.length; d.normalize()
        pa2, pb2 = pa + d * 0.9, pb - d * 0.9
        if kind == "turf":
            G_net.line([tuple(pa2), tuple(pb2)], gv.col("acid"), 0.05)
            G_net.line([tuple(pa2), tuple(pb2)], gv.col("acid"), 0.13, 0.18)
        elif kind == "open":
            G_net.line([tuple(pa2), tuple(pb2)], gv.col("cyan"), 0.018, 0.7)
        else:
            # corp threat route: chevrons
            pp = Vector((-d.y, d.x, 0))
            n = int((Ld - 1.8) / 0.55)
            for q in range(n):
                cc = pa2 + d * (q * 0.55 + 0.2)
                G_net.line([tuple(cc - d * 0.15 + pp * 0.18), tuple(cc + d * 0.08), tuple(cc - d * 0.15 - pp * 0.18)],
                           gv.col("orange"), 0.028, 0.95)
    for (name, x, y, cn) in nodes:
        c = gv.col(cn)
        rr = 0.85 if name != "HQ" else 1.1
        hexa = [(x + rr * math.cos(math.radians(60 * k)), y + rr * math.sin(math.radians(60 * k)), NET_Z) for k in range(6)]
        G_net.line(hexa, c, 0.04, cyclic=True)
        hexb = [(x + rr * 0.7 * math.cos(math.radians(60 * k)), y + rr * 0.7 * math.sin(math.radians(60 * k)), NET_Z) for k in range(6)]
        G_net.line(hexb, c, 0.014, 0.6, cyclic=True)
        # glow pool on the plane
        gv.disc("npool_" + name, rr * 2.4, gv.radial_glow_mat("np_" + name, c, 0.9, 2.2), loc=(x, y, NET_Z - 0.01))
        # label in vector type, laid flat on the plane (same plane as the node)
        for pl in gf.layout(name, 0.55):
            w = gf.width(name, 0.55)
            G_net.line([(x + rr + 0.3 + gx, y - 0.9 - gy * 0.0 + gy, NET_Z) for (gx, gy) in pl], c, 0.016, 0.95)
    # HQ tower pierces the plane: collar ring
    col_r = 1.9
    G_net.line([(HQ.x + col_r * math.cos(a / 30 * 6.283), HQ.y + col_r * math.sin(a / 30 * 6.283), NET_Z) for a in range(30)],
               gv.col("pink"), 0.02, 0.8, cyclic=True)

# ------------------------------------------------------------------ Heat: helicopters, searchlights, drones
cones_v, cones_f = [], []
if HEAT:
    helis = [(-9.0, 4.0, 10.5, 30), (7.5, -7.0, 9.5, -60), (12.0, 9.0, 11.0, 150)]
    for (x, y, z, yaw) in helis:
        d = Vector((math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), 0))
        pp = Vector((-d.y, d.x, 0))
        d, pp = d * 1.6, pp * 1.6   # bigger glyphs read at 1080p
        c0 = Vector((x, y, z))
        body = [tuple(c0 + d * (0.9 * math.cos(a / 16 * 6.283)) + pp * (0.42 * math.sin(a / 16 * 6.283))) for a in range(16)]
        G_sky.line(body, gv.col("white"), 0.03, cyclic=True)
        G_sky.line([tuple(c0 - d * 0.8), tuple(c0 - d * 2.3)], gv.col("white"), 0.025)
        G_sky.line([tuple(c0 - d * 2.3 + pp * 0.3), tuple(c0 - d * 2.3 - pp * 0.3)], gv.col("white"), 0.02)
        for k in range(3):
            rr = 2.5 + k * 0.1
            G_sky.line([tuple(c0 + Vector((rr * math.cos(a / 32 * 6.283), rr * math.sin(a / 32 * 6.283), 0.35))) for a in range(33)],
                       gv.col("cyan"), 0.008, 0.45 - k * 0.12)
        for k in range(2):
            a = math.radians(yaw + 40 + k * 90)
            G_sky.line([tuple(c0 + Vector((1.6 * math.cos(a), 1.6 * math.sin(a), 0.35))), tuple(c0 + Vector((-1.6 * math.cos(a), -1.6 * math.sin(a), 0.35)))],
                       gv.col("white"), 0.014, 0.8)
        G_sky.line([tuple(c0 + pp * 0.45), tuple(c0 + pp * 0.451)], gv.col("harm"), 0.09)
        G_sky.line([tuple(c0 - pp * 0.45), tuple(c0 - pp * 0.451)], gv.col("cyan"), 0.09)
        # searchlight cone to the ground
        tgt = Vector((x + rng.uniform(-3, 3), y + rng.uniform(-3, 3), 0))
        rr = 2.2
        ring = [tgt + Vector((rr * math.cos(a / 20 * 6.283), rr * 0.7 * math.sin(a / 20 * 6.283), 0.05)) for a in range(20)]
        G_sky.line([tuple(p) for p in ring], gv.col("white"), 0.03, 0.9, cyclic=True)
        for p in ring[::5]:
            G_sky.line([tuple(c0), tuple(p)], gv.col("white"), 0.016, opac=[0.9, 0.4])
        b_ = len(cones_v)
        cones_v.append(tuple(c0))
        cones_v.extend(tuple(p) for p in ring)
        for k in range(20):
            cones_f.append((b_, b_ + 1 + k, b_ + 1 + (k + 1) % 20))
        gv.disc("spot%d" % len(cones_v), rr * 1.3, gv.radial_glow_mat("spotm%d" % len(cones_v), gv.col("white"), 0.55, 1.6), loc=(tgt.x, tgt.y, 0.06))
    # searchlights from rooftops (NOTICED sweep, now aggressive)
    for (x, y, z, tx, ty) in [(-14, -6, 5.0, -6, -2), (4, 12, 6.0, 0, 4), (16, -12, 4.5, 8, -4)]:
        c0 = Vector((x, y, z))
        tgt = Vector((tx, ty, 0))
        ring = [tgt + Vector((1.6 * math.cos(a / 20 * 6.283), 1.6 * math.sin(a / 20 * 6.283), 0.05)) for a in range(20)]
        b_ = len(cones_v)
        cones_v.append(tuple(c0)); cones_v.extend(tuple(p) for p in ring)
        for k in range(20):
            cones_f.append((b_, b_ + 1 + k, b_ + 1 + (k + 1) % 20))
        G_sky.line([tuple(p) for p in ring], gv.col("amber"), 0.02, 0.8, cyclic=True)
        gv.disc("sp2%d" % b_, 2.0, gv.radial_glow_mat("sp2m%d" % b_, gv.col("amber"), 0.5, 1.8), loc=(tx, ty, 0.06))
    # drone swarm: blinking vector glyphs (diamond + cross), red/blue, some "off" in this frame
    for q in range(70):
        x, y, z = rng.uniform(-16, 16), rng.uniform(-16, 16), rng.uniform(4.5, 8.5)
        s = 0.3
        on = rng.random() < 0.6
        cn = "harm" if q % 2 == 0 else "cyan"
        a = 1.0 if on else 0.25
        G_sky.line([(x - s, y, z), (x, y - s, z), (x + s, y, z), (x, y + s, z)], gv.col(cn), 0.015, a, cyclic=True)
        G_sky.line([(x - s * 1.6, y - s * 1.6, z), (x + s * 1.6, y + s * 1.6, z)], gv.col(cn), 0.008, a * 0.6)
        G_sky.line([(x - s * 1.6, y + s * 1.6, z), (x + s * 1.6, y - s * 1.6, z)], gv.col(cn), 0.008, a * 0.6)
        if on:
            G_sky.line([(x, y, z), (x, y, z + 0.01)], gv.col(cn), 0.07)
            # short persistence trail
            dx, dy = rng.uniform(-1, 1), rng.uniform(-1, 1)
            G_sky.line([(x + dx * k * 0.25, y + dy * k * 0.25, z) for k in range(6)][::-1], gv.col(cn), 0.01,
                       opac=[(k + 1) / 6 * 0.5 for k in range(6)])
    gv.mesh_from("cones", cones_v, cones_f, gv.emit_mat("cone", gv.col("white"), 1.0, 0.014))

# ------------------------------------------------------------------ ground grid (vector floor)
for k in range(0, N + 1):
    s = street(k) - STREET / 2 + 0.0
    for axis in (0, 1):
        pts = [((t, s + STREET / 2, 0.0) if axis == 0 else (s + STREET / 2, t, 0.0)) for t in [-HALF + q * 1.2 for q in range(int(2 * HALF / 1.2) + 1)]]
        G_road.line(pts, gv.col("phos_dim"), 0.006, opac=[fade_op(p) * 0.35 for p in pts])

# ------------------------------------------------------------------ build
from mathutils.bvhtree import BVHTree
import time
t0 = time.time()
bvh = BVHTree.FromPolygons(occ_verts, occ_faces, all_triangles=False)
for g in (G_road, G_struct, G_floor, G_traffic, G_holo):
    g.hidden_line(bvh, V, step=0.09)
print("hidden-line pass %.1fs" % (time.time() - t0))
for g in (G_road, G_struct, G_floor, G_traffic, G_holo, G_sky, G_net):
    g.flush()
gv.render(OUT)
# screen positions of near/high things (helicopters, the HQ) so the tilt-shift can keep them sharp
import json
from bpy_extras.object_utils import world_to_camera_view
def _px(p):
    v = world_to_camera_view(sc, cam, Vector(p))
    return [round(v.x * sc.render.resolution_x), round((1 - v.y) * sc.render.resolution_y)]
near = {"hq_top": _px((HQ.x, HQ.y, HQ_H + 3.0)), "hq_base": _px((HQ.x, HQ.y, 0))}
if HEAT:
    near["helis"] = [_px((x, y, z)) for (x, y, z, _) in helis]
json.dump(near, open(os.path.splitext(OUT)[0] + ".json", "w"))
print("CITY DONE", MODE, OUT)
