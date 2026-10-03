# Round 26 kit. NOT a module: hq26.py exec()s it after target_corps (setup), heroes24 and heroes25, so it shares
# SOLID / NEON / WIN, box(), beam(), strip(), windows(), cable(), cyl(), dish(), container(), vehicle(), text_obj(), rng.
# Plane helpers take an origin and two unit vectors (ux = along the width, uz = up the panel) plus the outward normal.

LIME26 = (0.83, 1.0, 0.0)      # #D4FF00 turf / links
PINK26 = (1.0, 0.24, 0.66)     # #FF3DA8 verbs
DRED = (1.0, 0.05, 0.07)       # DISPATCH red
DRED2 = (0.62, 0.02, 0.05)
ORIG = [(1.0, 0.62, 0.20), (0.35, 0.85, 1.0), (0.95, 0.92, 0.85), (1.0, 0.35, 0.25)]  # the street's own (un-hijacked) sign colours


def anim(seed):
    """Round 28 motion: the state of one sign / screen / hologram in animation frame FRAME (-1 = the still).
    Seeded by (sign seed, frame) only, so the layout never changes between frames. DISPATCH flickers and glitches more.
    -> dict(off, k (brightness), scroll (glyph rows), swap (content seed shift), glitch (extra row tearing))"""
    fr = globals().get("FRAME", -1)
    if fr < 0:
        return dict(off=False, k=1.0, scroll=0, swap=0, glitch=0.0)
    r = random.Random(seed * 7919 + fr * 104729 + 11)
    disp = globals().get("DISP", False)
    p_off, p_dim = (0.18, 0.25) if disp else (0.05, 0.12)
    roll = r.random()
    k = 0.0 if roll < p_off else (0.45 if roll < p_off + p_dim else 1.0)
    kind = seed % 3  # 0: scrolls, 1: swaps content every few frames, 2: steady
    scroll = fr if kind == 0 else 0
    swap = (fr // (2 if disp else 3)) if kind == 1 else 0
    return dict(off=k == 0.0, k=k, scroll=scroll, swap=swap, glitch=(0.7 if disp and r.random() < 0.5 else 0.0))


def kcol(c, k):
    return tuple(v * k for v in c)


def build_at(fn, dx=0.0, dy=0.0, s=1.0):
    marks = [(acc, len(acc.bm.verts)) for acc in (SOLID, NEON, WIN)]
    objs0 = set(bpy.data.objects)
    fn()
    for acc, m in marks:
        acc.bm.verts.ensure_lookup_table()
        for v in acc.bm.verts[m:]:
            v.co.x = v.co.x * s + dx
            v.co.y = v.co.y * s + dy
            v.co.z *= s
    for o in set(bpy.data.objects) - objs0:
        o.location = (o.location[0] * s + dx, o.location[1] * s + dy, o.location[2] * s)
        o.scale = (s, s, s)


def build_xf(fn, dx=0.0, dy=0.0, rot=0.0):
    """Run a builder in its local frame, then rotate (deg, about z) and move what it added."""
    marks = [(acc, len(acc.bm.verts)) for acc in (SOLID, NEON, WIN)]
    objs0 = set(bpy.data.objects)
    fn()
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for acc, m in marks:
        acc.bm.verts.ensure_lookup_table()
        for v in acc.bm.verts[m:]:
            x, y = v.co.x, v.co.y
            v.co.x, v.co.y = x * c - y * s + dx, x * s + y * c + dy
    for o in set(bpy.data.objects) - objs0:
        x, y, z = o.location
        o.location = (x * c - y * s + dx, x * s + y * c + dy, z)
        r = o.rotation_euler
        o.rotation_euler = (r[0], r[1], r[2] + math.radians(rot))


def L2W(lx, ly):
    c = s = math.sqrt(0.5)
    return (lx * c - ly * s, lx * s + ly * c)


def V3(p):
    return Vector(p)


def pquad(acc, o, ux, uz, n, a0, a1, b0, b1, col, off=0.06, bid=(0, 0, 0)):
    """Rectangle [a0,a1] x [b0,b1] in the plane (o, ux, uz), pushed `off` along n."""
    o, ux, uz, n = V3(o), V3(ux), V3(uz), V3(n)
    pts = [o + ux * a0 + uz * b0 + n * off, o + ux * a1 + uz * b0 + n * off, o + ux * a1 + uz * b1 + n * off, o + ux * a0 + uz * b1 + n * off]
    acc.face([tuple(p) for p in pts], col, bid)


def fist_icon(o, ux, uz, n, s, col, acc=None, back=None, off=0.08, glitch=0.0, seed=0):
    """The Cell's raised fist (same crest as heroes24.fist) on any plane; s = height. glitch shifts rows (DISPATCH)."""
    acc = acc or NEON
    k = s / 14.0
    gr = random.Random(seed)
    if back:
        pquad(SOLID, o, ux, uz, n, -6.5 * k, 6.5 * k, -0.8 * k, 14.8 * k, back, off=off * 0.5, bid=rid())
    parts = []
    for i in range(4):
        x0 = -5.2 * k + i * 2.6 * k
        parts.append((x0, x0 + 2.3 * k, 8.4 * k, 13.2 * k + (0.6 * k if i in (1, 2) else 0)))
    parts.append((-5.2 * k, 5.2 * k, 5.4 * k, 8.0 * k))
    parts.append((-3.6 * k, 3.6 * k, 0.0, 5.0 * k))
    for (a0, a1, b0, b1) in parts:
        sh = (gr.uniform(-1, 1) * 1.6 * k) if glitch and gr.random() < glitch else 0.0
        pquad(acc, o, ux, uz, n, a0 + sh, a1 + sh, b0, b1, col, off=off)


def glyphs(o, ux, uz, n, w, h, col, seed, cols=2, acc=None, off=0.08, dens=0.62, scroll=0):
    """Kanji-like block glyphs filling a w x h panel (column-wise, like tategaki sign lettering).
    scroll (round 28): the text runs up the panel one glyph per step (each cell seeded by its text position)."""
    acc = acc or NEON
    cw = w / cols
    rows = max(1, int(h / cw))
    ch = h / rows
    for i in range(cols):
        for j in range(rows):
            gr = random.Random(seed * 1009 + i * 97 + (j - scroll) % (rows + 3))
            x0, z0 = i * cw + cw * 0.14, j * ch + ch * 0.14
            gw, gh = cw * 0.72, ch * 0.72
            for _ in range(gr.randint(2, 4)):  # strokes of one glyph
                if gr.random() > dens:
                    continue
                if gr.random() < 0.5:
                    zz = z0 + gr.uniform(0, gh * 0.8)
                    pquad(acc, o, ux, uz, n, x0 - w / 2, x0 + gw - w / 2, zz, zz + gh * 0.17, col, off=off)
                else:
                    xx = x0 + gr.uniform(0, gw * 0.8)
                    pquad(acc, o, ux, uz, n, xx - w / 2, xx + gw * 0.17 - w / 2, z0, z0 + gh, col, off=off)


def tag_scrawl(o, ux, uz, n, w, h, col, seed, acc=None, off=0.1):
    """Spray-paint scrawl (Cell graffiti): a few thick slanted strokes and a drip or two."""
    acc = acc or NEON
    gr = random.Random(seed)
    o, ux, uz, n = V3(o), V3(ux), V3(uz), V3(n)
    for _ in range(gr.randint(4, 7)):
        a = Vector((gr.uniform(-w / 2, w / 2), gr.uniform(0.15 * h, 0.9 * h)))
        b = a + Vector((gr.uniform(-0.35, 0.35) * w, gr.uniform(-0.4, 0.4) * h))
        t = gr.uniform(0.05, 0.11) * h
        d = (b - a)
        if d.length < 1e-3:
            continue
        nn = Vector((-d.y, d.x)).normalized() * t
        P = [a + nn, a - nn, b - nn, b + nn]
        acc.face([tuple(o + ux * p.x + uz * p.y + n * off) for p in P], col, (0, 0, 0))
        if gr.random() < 0.4:
            dl = gr.uniform(0.1, 0.3) * h
            acc.face([tuple(o + ux * (a.x - t * 0.3) + uz * a.y + n * off), tuple(o + ux * (a.x + t * 0.3) + uz * a.y + n * off),
                      tuple(o + ux * a.x + uz * (a.y - dl) + n * off)], col, (0, 0, 0))


def screen(o, ux, uz, n, w, h, content, col, col2, seed, frame=(0.10, 0.09, 0.11), depth=0.8, glitch=0.0):
    """A billboard / screen: dark frame box + dim emissive field + content (fist | glyph | tag | bars | text)."""
    o, ux, uz, n = V3(o), V3(ux), V3(uz), V3(n)
    bid = rid()
    # frame body as a slab behind the screen
    c = [o + ux * (-w / 2 - 0.4) + uz * -0.4, o + ux * (w / 2 + 0.4) + uz * -0.4, o + ux * (w / 2 + 0.4) + uz * (h + 0.4),
         o + ux * (-w / 2 - 0.4) + uz * (h + 0.4)]
    back = [p - n * depth for p in c]
    SOLID.face([tuple(p) for p in c], frame, bid)
    for i in range(4):
        j = (i + 1) % 4
        SOLID.face([tuple(c[i]), tuple(back[i]), tuple(back[j]), tuple(c[j])], frame, bid)
    st = anim(seed)
    if st["off"]:  # flickered out this frame: the dead panel only
        pquad(SOLID, o, ux, uz, n, -w / 2, w / 2, 0, h, (0.03, 0.03, 0.04), off=0.05, bid=bid)
        return
    col, col2 = kcol(col, st["k"]), kcol(col2, st["k"])
    if st["swap"] and content in ("glyph", "fist", "tag") and (seed + st["swap"]) % 2:
        content = "glyph" if content != "glyph" else "fist"  # the hijack swaps the ad and the Cell's mark
    seed = seed + st["swap"] * 31
    glitch = max(glitch, st["glitch"])
    pquad(NEON, o, ux, uz, n, -w / 2, w / 2, 0, h, tuple(v * 0.07 for v in col2), off=0.05)
    for s_ in (-1, 1):  # a thin second-colour rule top and bottom (lime + pink takeovers read as two colours)
        pquad(NEON, o, ux, uz, n, -w / 2, w / 2, (h - 0.5) if s_ > 0 else 0.0, h if s_ > 0 else 0.5, col2, off=0.07)
    if content == "fist":
        fist_icon(o + uz * (h * 0.1), ux, uz, n, h * 0.78, col, glitch=glitch, seed=seed + max(0, globals().get("FRAME", -1)), off=0.1)
    elif content == "glyph":
        glyphs(o, ux, uz, n, w * 0.9, h * 0.9, col, seed, cols=max(1, int(w / max(h, 1) * 4)), off=0.1, scroll=st["scroll"])
    elif content == "tag":
        tag_scrawl(o, ux, uz, n, w * 0.9, h, col, seed, off=0.1)
    elif content == "bars":
        gr = random.Random(seed)
        for k in range(6):
            z = h * (0.08 + k * 0.15)
            pquad(NEON, o, ux, uz, n, -w / 2 * 0.9, -w / 2 * 0.9 + w * 0.9 * gr.uniform(0.25, 1.0), z, z + h * 0.08, col, off=0.1)
    # scanlines (thin dark bars): read as a screen up close
    for k in range(int(h / 1.1)):
        z = 0.5 + k * 1.1
        pquad(SOLID, o, ux, uz, n, -w / 2, w / 2, z, z + 0.12, (0.04, 0.03, 0.05), off=0.12, bid=bid)


def blade_sign(base, out, h, wdt, col, seed, content="glyph", z0=4.0, dark=False):
    """Vertical blade sign projecting from a facade: base = point on the wall (z ignored), out = unit vector into the street."""
    b, o = V3((base[0], base[1], 0)), V3((out[0], out[1], 0)).normalized()
    side = Vector((-o.y, o.x, 0))
    p0 = b + o * 0.5 + V3((0, 0, z0))
    bid = rid()
    # the sign body: thin box
    t = 0.35
    box_pts = []
    for (a, c) in ((0, 0), (1, 0), (1, 1), (0, 1)):
        box_pts.append(p0 + o * (a * wdt) + V3((0, 0, c * h)))
    for s_ in (-1, 1):
        q = [tuple(p + side * t * s_) for p in box_pts]
        SOLID.face(q if s_ > 0 else q[::-1], (0.12, 0.10, 0.12), bid)
    SOLID.face([tuple(box_pts[1] - side * t), tuple(box_pts[1] + side * t), tuple(box_pts[2] + side * t), tuple(box_pts[2] - side * t)], (0.12, 0.10, 0.12), bid)
    beam(tuple(b + V3((0, 0, z0 + h * 0.2))), tuple(p0 + V3((0, 0, h * 0.2))), 0.25, (0.2, 0.18, 0.2))
    beam(tuple(b + V3((0, 0, z0 + h * 0.8))), tuple(p0 + V3((0, 0, h * 0.8))), 0.25, (0.2, 0.18, 0.2))
    st = anim(seed)
    if dark or st["off"]:
        return
    col = kcol(col, st["k"])
    oc = p0 + o * (wdt / 2)
    for s_ in (-1, 1):
        nrm = side * s_
        ux = o * (-s_)
        lightbox = (seed % 3 == 0)  # one in three is a light box (bright plate, dark lettering)
        pquad(NEON, oc, ux, V3((0, 0, 1)), nrm, -wdt / 2 + 0.25, wdt / 2 - 0.25, 0.25, h - 0.25, tuple(v * (0.45 if lightbox else 0.07) for v in col), off=t + 0.04)
        if lightbox:
            glyphs(oc + V3((0, 0, 0.3)), ux, V3((0, 0, 1)), nrm, wdt * 0.84, h - 0.6, (0.06, 0.05, 0.07), seed + s_, cols=1, off=t + 0.08, acc=SOLID,
                   scroll=st["scroll"])
            continue
        if content == "fist":
            fist_icon(oc + V3((0, 0, h * 0.55)), ux, V3((0, 0, 1)), nrm, min(h * 0.4, wdt * 1.0), col, off=t + 0.08)
            glyphs(oc + V3((0, 0, 0.4)), ux, V3((0, 0, 1)), nrm, wdt * 0.8, h * 0.45, col, seed + s_, cols=1, off=t + 0.08, scroll=st["scroll"])
        else:
            glyphs(oc + V3((0, 0, 0.3)), ux, V3((0, 0, 1)), nrm, wdt * 0.84, h - 0.6, col, seed + s_ + st["swap"] * 31, cols=1, off=t + 0.08,
                   scroll=st["scroll"])
        # neon outline tube
        for (a, c) in (((-1, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, 0))):
            pa = oc + ux * (a[0] * wdt / 2) + V3((0, 0, a[1] * h)) + nrm * (t + 0.1)
            pc = oc + ux * (c[0] * wdt / 2) + V3((0, 0, c[1] * h)) + nrm * (t + 0.1)
            beam(tuple(pa), tuple(pc), 0.16, col, acc=NEON)


def lantern_string(p0, p1, sag, cols, n=9, size=0.55):
    cable(p0, p1, sag, w=0.08, col=(0.08, 0.07, 0.08))
    P0, P1 = Vector(p0), Vector(p1)
    for t in range(1, n):
        u = t / n
        v = P0.lerp(P1, u) - Vector((0, 0, sag * 4 * u * (1 - u)))
        c = cols[t % len(cols)]
        s = size
        box(v.x - s * 0.7, v.y - s * 0.7, v.z - s * 1.8, v.x + s * 0.7, v.y + s * 0.7, v.z - 0.1, c, facet=False)
        for dz in (-s * 1.85, -0.05):
            NEON.face([(v.x - s * 0.75, v.y - s * 0.75, v.z + dz), (v.x + s * 0.75, v.y - s * 0.75, v.z + dz), (v.x + s * 0.75, v.y + s * 0.75, v.z + dz),
                       (v.x - s * 0.75, v.y + s * 0.75, v.z + dz)], c, (0, 0, 0))
        for (dx, dy) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nrm = Vector((dx, dy, 0))
            ux = Vector((-dy, dx, 0))
            pquad(NEON, Vector((v.x, v.y, v.z - s * 1.8)) + nrm * s * 0.7, ux, Vector((0, 0, 1)), nrm, -s * 0.6, s * 0.6, 0.15, s * 1.6, c, off=0.04)


def vending(x, y, face, col, h=2.2):
    """Vending machine at (x, y) facing `face` (unit xy)."""
    f = Vector((face[0], face[1], 0)).normalized()
    s = Vector((-f.y, f.x, 0))
    c = Vector((x, y, 0))
    pts = [c - s * 0.6 - f * 0.45, c + s * 0.6 - f * 0.45, c + s * 0.6 + f * 0.45, c - s * 0.6 + f * 0.45]
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    box(min(xs), min(ys), 0, max(xs), max(ys), h, (0.78, 0.78, 0.82), facet=False)
    o = c + f * 0.45
    pquad(NEON, o, s, Vector((0, 0, 1)), f, -0.5, 0.5, 0.9, h - 0.15, col, off=0.04)
    pquad(NEON, o, s, Vector((0, 0, 1)), f, -0.5, 0.5, 0.3, 0.6, (0.9, 0.9, 0.95), off=0.04)
    for k in range(4):  # product rows
        pquad(SOLID, o, s, Vector((0, 0, 1)), f, -0.48, 0.48, 1.05 + k * 0.28, 1.12 + k * 0.28, (0.15, 0.12, 0.14), off=0.06)


def wall_box(x0, y0, z0, x1, y1, z1, col, jit=0.004, bid=None, top=True):
    """box() with nearly flat facets, so decals (signs, screens, windows) a few cm off the wall stay visible."""
    bid = bid or rid()
    b = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]
    u = [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    for q in ((b[0], b[1], u[1], u[0]), (b[1], b[2], u[2], u[1]), (b[2], b[3], u[3], u[2]), (b[3], b[0], u[0], u[3])):
        SOLID.facet_quad(*q, col, bid, jit=jit)
    if top:
        SOLID.facet_quad(u[0], u[1], u[2], u[3], col, bid, jit=0.002)
    return bid


def windows2(x0, y0, z0, x1, y1, z1, p=0.35, sx=2.4, sz=3.2, ww=1.1, wh=0.9, cols=None, faces=(0, 1, 2, 3), o=0.2, gr=None):
    """windows() (target_corps) with a larger outset for the flat-faceted wall_box walls."""
    cols = cols or WIN_COLS
    gr = gr or rng
    walls = [((x0, y0 - o), (x1, y0 - o)), ((x1 + o, y0), (x1 + o, y1)), ((x1, y1 + o), (x0, y1 + o)), ((x0 - o, y1), (x0 - o, y0))]
    for fi in faces:
        (ax, ay), (bx, by) = walls[fi]
        L = math.hypot(bx - ax, by - ay)
        nx = int((L - 1.0) / sx)
        nz = int((z1 - z0 - 1.5) / sz)
        if nx < 1 or nz < 1:
            continue
        ux, uy = (bx - ax) / L, (by - ay) / L
        off = (L - nx * sx) / 2
        for i in range(nx):
            for k in range(nz):
                if gr.random() > p:
                    continue
                c = gr.choice(cols)
                s = 0.55 + 0.45 * gr.random()
                c = (c[0] * s, c[1] * s, c[2] * s)
                t0 = off + i * sx + (sx - ww) / 2
                z = z0 + 1.2 + k * sz
                pa = (ax + ux * t0, ay + uy * t0)
                pb = (ax + ux * (t0 + ww), ay + uy * (t0 + ww))
                WIN.face([(pa[0], pa[1], z), (pb[0], pb[1], z), (pb[0], pb[1], z + wh), (pa[0], pa[1], z + wh)], c, (0, 0, 0))
