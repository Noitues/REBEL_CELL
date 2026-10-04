# Round 26 kit. NOT a module: hq26.py exec()s it after target_corps (setup), heroes24 and heroes25, so it shares
# SOLID / NEON / WIN, box(), beam(), strip(), windows(), cable(), cyl(), dish(), container(), vehicle(), text_obj(), rng.
# Plane helpers take an origin and two unit vectors (ux = along the width, uz = up the panel) plus the outward normal.

LIME26 = (0.83, 1.0, 0.0)      # #D4FF00 turf / links
PINK26 = (1.0, 0.24, 0.66)     # #FF3DA8 verbs
DRED = (1.0, 0.05, 0.07)       # DISPATCH red
DRED2 = (0.62, 0.02, 0.05)
ORIG = [(1.0, 0.62, 0.20), (0.35, 0.85, 1.0), (0.95, 0.92, 0.85), (1.0, 0.35, 0.25)]  # the street's own (un-hijacked) sign colours


def anim(seed):
    """Round 31 motion: the state of one sign / screen / hologram in animation frame FRAME (-1 = the still).
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


def glyphs(o, ux, uz, n, w, h, col, seed, cols=2, acc=None, off=0.08, dens=0.92, scroll=0):  # round 31: fuller lettering
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
        content = "glyph" if content != "glyph" else ("fist" if globals().get("DISP", False) else "lang")  # home never shows a fist
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
    elif content == "lang":  # round 30: an ordinary sign in one of the city's languages
        txt, fnt, cjk = lang_text(seed)
        cw_ = 1.0 if cjk else 0.6
        size = min(h * 0.55, w * 0.9 / (cw_ * max(1, len(txt))))
        size = min(size, h * 0.4)
        text2(txt, tuple(o + uz * (h * 0.62) + n * 0.14), (math.radians(90), 0, 0), size, col, fnt)
        # round 31: no near-empty signs: a line of small print, a price strip and a pictogram under the name
        glyphs(o + uz * (h * 0.12) + ux * (-w * 0.12), ux, uz, n, w * 0.6, h * 0.22, kcol(col2, 0.9), seed + 5, cols=max(3, int(w / 1.2)), off=0.1)
        pquad(NEON, o, ux, uz, n, -w / 2 * 0.9, w / 2 * 0.9, h * 0.38, h * 0.41, col2, off=0.1)
        pc = o + ux * (w * 0.36) + uz * (h * 0.22)  # a pictogram: a bowl with steam, a cup or a chip, by seed
        kind_ = seed % 3
        if kind_ == 0:
            for k in range(3):
                pquad(NEON, tuple(pc), tuple(ux), tuple(uz), tuple(n), -0.6 + k * 0.15, 0.6 - k * 0.15, -k * 0.18, -k * 0.18 + 0.12, col, off=0.12)
            for k in range(3):
                pquad(NEON, tuple(pc), tuple(ux), tuple(uz), tuple(n), -0.35 + k * 0.3, -0.29 + k * 0.3, 0.25, 0.75, kcol(col, 0.7), off=0.12)
        elif kind_ == 1:
            pquad(NEON, tuple(pc), tuple(ux), tuple(uz), tuple(n), -0.35, 0.35, -0.5, 0.5, col, off=0.12)
            pquad(SOLID, tuple(pc), tuple(ux), tuple(uz), tuple(n), -0.22, 0.22, -0.3, 0.4, (0.06, 0.05, 0.07), off=0.14, bid=rid())
        else:
            pquad(NEON, tuple(pc), tuple(ux), tuple(uz), tuple(n), -0.4, 0.4, -0.4, 0.4, col, off=0.12)
            for k in range(4):
                pquad(NEON, tuple(pc), tuple(ux), tuple(uz), tuple(n), -0.6, 0.6, -0.3 + k * 0.2, -0.26 + k * 0.2, kcol(col, 0.6), off=0.11)
    elif content.startswith("text:"):  # round 29/30: a slogan in the sign face (screens facing -Y, the canyon's camera)
        txt = content[5:]
        size = min(h * 0.42, w * 0.92 / (0.6 * len(txt)))
        ob = text_obj(txt, tuple(o + uz * (h * 0.5) + n * 0.14), (math.radians(90), 0, 0), size, SIGNM, extrude=0.05)
        ob.name = "txt_%d" % seed
        if globals().get("DISP", False):  # the takeover glitches: a torn, offset ghost of the phrase
            gr_ = random.Random(seed * 13 + max(0, globals().get("FRAME", -1)))
            for _ in range(gr_.randint(1, 2)):
                dx = gr_.uniform(-0.12, 0.12) * w
                text2(txt, tuple(o + ux * dx + uz * (h * 0.5 + gr_.uniform(-0.08, 0.08) * h) + n * 0.11), (math.radians(90), 0, 0), size,
                      (0.55, 0.0, 0.06) if gr_.random() < 0.6 else (0.9, 0.85, 0.9), None)
            for _ in range(gr_.randint(2, 5)):  # torn scan bars
                z = gr_.uniform(0.05, 0.95) * h
                a0 = gr_.uniform(-0.5, 0.3) * w
                pquad(NEON, o, ux, uz, n, a0, a0 + gr_.uniform(0.1, 0.5) * w, z, z + h * 0.035, (1.0, 0.25, 0.3), off=0.16)
        for k in range(2):  # underline bars (the screen stays busy behind the words)
            z = h * (0.12 + k * 0.72)
            pquad(NEON, o, ux, uz, n, -w / 2 * 0.85, w / 2 * 0.85, z, z + h * 0.06, col, off=0.1)
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
        lightbox = (seed % 3 == 0) and not globals().get("DISP", False)  # a light box (bright plate, dark lettering); none in DISPATCH
        pquad(NEON, oc, ux, V3((0, 0, 1)), nrm, -wdt / 2 + 0.25, wdt / 2 - 0.25, 0.25, h - 0.25, tuple(v * (0.45 if lightbox else 0.07) for v in col), off=t + 0.04)
        if lightbox:
            glyphs(oc + V3((0, 0, 0.3)), ux, V3((0, 0, 1)), nrm, wdt * 0.84, h - 0.6, (0.06, 0.05, 0.07), seed + s_, cols=1, off=t + 0.08, acc=SOLID,
                   scroll=st["scroll"])
            continue
        if content == "lang":  # round 30: a vertical sign in one of the city's languages
            if nrm.y < 0:
                txt, fnt, cjk = lang_text(seed)
                if cjk:  # CJK reads top to bottom, one upright character per cell
                    sz = min(wdt * 0.7, (h - 0.6) / max(1, len(txt)) * 0.85)
                    for k_, ch_ in enumerate(txt):
                        zc = h - 0.5 - (k_ + 0.5) * (h - 0.6) / len(txt)
                        text2(ch_, tuple(oc + V3((0, 0, zc)) + nrm * (t + 0.1)), (math.radians(90), 0, 0), sz, col, fnt)
                else:
                    sz = min(wdt * 0.62, (h - 0.6) / (0.62 * max(1, len(txt))))
                    text2(txt, tuple(oc + V3((0, 0, h * 0.5)) + nrm * (t + 0.1)), (math.radians(90), math.radians(-90), 0), sz, col, fnt)
            else:
                glyphs(oc + V3((0, 0, 0.3)), ux, V3((0, 0, 1)), nrm, wdt * 0.84, h - 0.6, col, seed + s_, cols=1, off=t + 0.08)
        elif content.startswith("text:"):  # vertical slogan, reading bottom to top, on the face toward the camera
            txt = content[5:]
            if nrm.y < 0:
                size = min(wdt * 0.62, (h - 0.6) / (0.62 * len(txt)))
                text_obj(txt, tuple(oc + V3((0, 0, h * 0.5)) + nrm * (t + 0.1)), (math.radians(90), math.radians(-90), 0), size, SIGNM, extrude=0.04)
            else:
                glyphs(oc + V3((0, 0, 0.3)), ux, V3((0, 0, 1)), nrm, wdt * 0.84, h - 0.6, col, seed + s_, cols=1, off=t + 0.08)
        elif content == "fist":
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


# ================================================================== round 30: the city's languages, food / tech holograms
FONTS = "C:/Windows/Fonts/"
LANGS = [  # (font, cjk, texts) - legibility not required, the scripts must look right
    ("YuGothB.ttc", True, ["ラーメン", "居酒屋", "カラオケ", "寿司", "薬局", "焼き鳥"]),
    ("msyh.ttc", True, ["麵館", "電腦城", "按摩", "當舖", "餃子", "茶樓"]),
    ("malgun.ttf", True, ["노래방", "치킨", "편의점", "PC방", "국수"]),
    ("tahoma.ttf", False, ["مطعم", "صيدلية", "مقهى", "حلويات"]),
    ("arialbd.ttf", False, ["TACOS", "FARMACIA", "CERVEZA", "LAVANDERIA"]),
    ("Nirmala.ttf", False, ["चाय", "दुकान", "भोजन", "मसाला"]),
    ("bahnschrift.ttf", False, ["NOODLES", "PAWN", "CHIPS 24H", "HOTEL", "REPAIR"]),
    ("LeelawUI.ttf", False, ["ร้านอาหาร", "นวด"]),
]
_FONTCACHE = {}
_MATCACHE = {}


def lang_text(seed):
    r = random.Random(seed * 31 + 7)
    fnt, cjk, texts = LANGS[r.randrange(len(LANGS))]
    t = texts[r.randrange(len(texts))]
    if fnt == "tahoma.ttf":
        t = t[::-1]  # no shaping in Blender text: at least the letters run right to left
    return t, fnt, cjk


def emis_mat(col):
    key = tuple(round(c, 3) for c in col)
    if key not in _MATCACHE:
        m, _em = mat_flat("e%d" % len(_MATCACHE), tuple(min(4.0, c) for c in key))
        _MATCACHE[key] = m
    return _MATCACHE[key]


def text2(s, loc, rot, size, col, font=None, extrude=0.04):
    cu = bpy.data.curves.new("t2", "FONT")
    cu.body = s
    path = FONTS + (font or "bahnschrift.ttf")
    if path not in _FONTCACHE:
        try:
            _FONTCACHE[path] = bpy.data.fonts.load(path)
        except Exception:
            _FONTCACHE[path] = None
    if _FONTCACHE[path] is not None:
        cu.font = _FONTCACHE[path]
    cu.size = size
    cu.extrude = extrude
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    ob = bpy.data.objects.new("t2", cu)
    ob.location = loc
    ob.rotation_euler = rot
    scene.collection.objects.link(ob)
    ob.data.materials.append(emis_mat(col))
    return ob


def _ring(c, r, z, col, n=14, w=0.07, sq=False):
    pts = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n + (math.pi / 4 if sq else 0)
        rr = r / max(abs(math.cos(a)), abs(math.sin(a))) if sq else r
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a), z))
    for p, q in zip(pts, pts[1:]):
        beam(p, q, w, col, acc=NEON)


def holo_object(kind, c, s, col, col2, seed):
    """A food / tech hologram on a rooftop projector: stacked light slices (scanlines) of a simple profile, a few
    outline lines, the projector puck and its light cone. kind: noodles | dumpling | soda | sushi | chip | human."""
    st = anim(seed)
    cx, cy, cz = c
    box(cx - 1.0, cy - 1.0, cz, cx + 1.0, cy + 1.0, cz + 0.6, (0.18, 0.17, 0.2), facet=False)
    if st["off"]:
        return
    col, col2 = kcol(col, st["k"] * 0.85), kcol(col2, st["k"] * 0.85)
    NEON.face([(cx - 0.7, cy - 0.7, cz + 0.62), (cx + 0.7, cy - 0.7, cz + 0.62), (cx + 0.7, cy + 0.7, cz + 0.62), (cx - 0.7, cy + 0.7, cz + 0.62)], col, (0, 0, 0))
    z0 = cz + 1.2
    fr = max(0, globals().get("FRAME", -1))
    gr = random.Random(seed + fr * 131)
    disp = globals().get("DISP", False)
    pitch = 0.32 * s / 4.0
    off = (fr % 3) * pitch / 3.0

    def slices(h, rfun, colf=None, sq=False):
        z = off
        while z < h:
            sh = (gr.uniform(-0.4, 0.4) * s if disp and gr.random() < 0.25 else 0.0)
            r = rfun(z / h)
            if r > 0.02:
                _ring((cx + sh, cy), r, z0 + z, colf(z / h) if colf else col, sq=sq)
            z += pitch

    for k in range(3):  # the light cone from the puck
        a = 2 * math.pi * k / 3
        beam((cx, cy, cz + 0.6), (cx + s * 0.45 * math.cos(a), cy + s * 0.45 * math.sin(a), z0), 0.05, kcol(col, 0.4), acc=NEON)
    if kind == "noodles":
        h = s * 0.45
        slices(h, lambda t: s * (0.32 + 0.38 * math.sqrt(t)))
        for k in range(5):  # noodles spilling over the rim, chopsticks, steam
            a = gr.uniform(0, math.pi)
            beam((cx + s * 0.6 * math.cos(a), cy + s * 0.6 * math.sin(a), z0 + h), (cx + s * 0.2 * math.cos(a + 1), cy, z0 + h + s * 0.25), 0.07, col2, acc=NEON)
        beam((cx - s * 0.2, cy, z0 + h * 0.6), (cx + s * 0.55, cy - s * 0.2, z0 + h + s * 0.7), 0.1, col2, acc=NEON)
        beam((cx - s * 0.1, cy, z0 + h * 0.6), (cx + s * 0.65, cy - s * 0.1, z0 + h + s * 0.62), 0.1, col2, acc=NEON)
        for k in range(3):
            x = cx + (k - 1) * s * 0.25
            for j in range(3):
                beam((x + (0.15 if j % 2 else -0.15) * s * 0.3, cy, z0 + h + s * (0.15 + j * 0.15)),
                     (x + (-0.15 if j % 2 else 0.15) * s * 0.3, cy, z0 + h + s * (0.3 + j * 0.15)), 0.05, kcol(col, 0.6), acc=NEON)
    elif kind == "dumpling":
        h = s * 0.5
        slices(h, lambda t: s * 0.62 * math.sqrt(max(0.0, 1 - t * t)))
        for k in range(7):  # the pleats along the top
            x = cx + (k - 3) * s * 0.12
            beam((x, cy, z0 + h * 0.75), (x + s * 0.06, cy, z0 + h * 1.12), 0.08, col2, acc=NEON)
    elif kind == "soda":
        h = s * 1.1
        slices(h, lambda t: s * (0.28 if 0.05 < t < 0.95 else 0.24), colf=lambda t: col2 if 0.35 < t < 0.65 else col)
        for k in range(6):  # bubbles
            beam((cx + gr.uniform(-1, 1) * s * 0.5, cy, z0 + gr.uniform(0.2, 1.3) * h), (cx + gr.uniform(-1, 1) * s * 0.5, cy, z0 + gr.uniform(0.2, 1.3) * h + 0.25),
                 0.18, kcol(col, 0.7), acc=NEON)
    elif kind == "sushi":
        for dx in (-0.45, 0.45):
            c0 = cx + dx * s
            z = off
            while z < s * 0.42:
                _ring((c0, cy), s * 0.3, z0 + z, col2 if z > s * 0.3 else col, n=4, sq=True)
                z += pitch
    elif kind == "chip":  # round 31: a big MICROCHIP turning slowly on its projector: package, pins on 4 sides, traces, die
        th = math.radians(25 + 30 * fr)
        U_ = Vector((math.cos(th), math.sin(th), 0))  # the chip plate: width along U_, height up, facing N_
        N_ = Vector((math.sin(th), -math.cos(th), 0))
        w = s * 0.62
        zc = z0 + w * 1.25
        C0 = Vector((cx, cy, zc))
        def P(u, v):
            return tuple(C0 + U_ * u + Vector((0, 0, v)))
        # translucent package (dim slats) + a hot outline
        z = -w + off
        while z < w:
            pquad(NEON, P(0, z), tuple(U_), (0, 0, 1), tuple(N_), -w, w, 0, pitch * 0.28, kcol(col, 0.28), off=0.0)
            z += pitch
        for (a, b) in (((-w, -w), (w, -w)), ((w, -w), (w, w)), ((w, w), (-w, w)), ((-w, w), (-w, -w))):
            beam(P(*a), P(*b), 0.16, col, acc=NEON)
        # pins on all four sides
        npin = 7
        for k in range(npin):
            t = -w * 0.8 + k * (1.6 * w) / (npin - 1)
            beam(P(-w, t), P(-w * 1.28, t), 0.13, col, acc=NEON)
            beam(P(w, t), P(w * 1.28, t), 0.13, col, acc=NEON)
            beam(P(t, -w), P(t, -w * 1.28), 0.13, col, acc=NEON)
            beam(P(t, w), P(t, w * 1.28), 0.13, col, acc=NEON)
        # the die in the middle, glowing, with its bond lines
        d_ = w * 0.34
        pquad(NEON, P(0, -d_), tuple(U_), (0, 0, 1), tuple(N_), -d_, d_, 0, 2 * d_, col2, off=0.02)
        # circuit traces: L-shaped runs from the die to the pins
        tr = random.Random(seed * 3 + 1)
        for k in range(10):
            sx = tr.choice([-1, 1])
            v0 = tr.uniform(-d_, d_)
            u1 = sx * tr.uniform(d_ * 1.4, w * 0.8)
            v1 = tr.uniform(-w * 0.8, w * 0.8)
            beam(P(sx * d_, v0), P(u1, v0), 0.07, kcol(col2, 0.8), acc=NEON)
            beam(P(u1, v0), P(u1, v1), 0.07, kcol(col2, 0.8), acc=NEON)
            beam(P(u1, v1), P(sx * w, v1), 0.07, kcol(col2, 0.8), acc=NEON)
    elif kind == "human":  # DISPATCH: a human figure, struck out
        parts = [(0.0, 0.42, 0.13), (0.42, 0.78, 0.2), (0.80, 0.97, 0.1)]  # legs, torso, head (t0, t1, half width)
        h = s * 1.5
        z = off
        while z < h:
            t = z / h
            sh = gr.uniform(-0.5, 0.5) * s if gr.random() < 0.12 else 0.0
            for (a, b, hw) in parts:
                if a <= t <= b:
                    if b == 0.42:
                        for sx in (-1, 1):
                            pquad(NEON, (cx + sx * s * 0.12 + sh, cy, z0 + z), (1, 0, 0), (0, 0, 1), (0, -1, 0), -s * 0.08, s * 0.08, 0, pitch * 0.5, col, off=0.0)
                    else:
                        pquad(NEON, (cx + sh, cy, z0 + z), (1, 0, 0), (0, 0, 1), (0, -1, 0), -s * hw * 2, s * hw * 2, 0, pitch * 0.5, col, off=0.0)
            z += pitch
        beam((cx - s * 0.7, cy - 0.3, z0), (cx + s * 0.7, cy - 0.3, z0 + h), 0.35, col2, acc=NEON)
        beam((cx + s * 0.7, cy - 0.3, z0), (cx - s * 0.7, cy - 0.3, z0 + h), 0.35, col2, acc=NEON)


# ================================================================== round 30: life on the buildings round the canyon
CLOTH = [(0.85, 0.82, 0.75), (0.75, 0.25, 0.22), (0.25, 0.40, 0.65), (0.90, 0.75, 0.35), (0.35, 0.55, 0.40), (0.85, 0.55, 0.65)]
LIFE_WARM = [(1.0, 0.70, 0.38), (1.0, 0.82, 0.55), (0.95, 0.62, 0.30), (0.75, 0.88, 1.0), (1.0, 0.55, 0.45)]


def laundry(p0, p1, sag, gr, n=None):
    cable(p0, p1, sag, w=0.05, col=(0.12, 0.11, 0.12))
    P0, P1 = Vector(p0), Vector(p1)
    d = (P1 - P0)
    side = Vector((-d.y, d.x, 0)).normalized() * 0.02
    n = n or max(2, int(d.length / 1.1))
    for k in range(n):
        if gr.random() < 0.25:
            continue
        u0 = (k + 0.15) / n
        u1 = (k + 0.15 + gr.uniform(0.35, 0.6)) / n
        a = P0.lerp(P1, u0) - Vector((0, 0, sag * 4 * u0 * (1 - u0)))
        b = P0.lerp(P1, u1) - Vector((0, 0, sag * 4 * u1 * (1 - u1)))
        hh = gr.uniform(0.5, 1.1)
        c = gr.choice(CLOTH)
        SOLID.face([tuple(a + side), tuple(b + side), tuple(b + side - Vector((0, 0, hh))), tuple(a + side - Vector((0, 0, hh * 0.9)))], c, rid())


def roof_clutter(poly, z, gr, rich=1.0):
    """Water tank on legs, a shack with a lit door, antennas, a laundry line, vent boxes - on a roof polygon."""
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, h = x1 - x0, y1 - y0
    if w < 3.0 or h < 3.0:
        return
    def rp(m=1.2):
        return gr.uniform(x0 + m, x1 - m), gr.uniform(y0 + m, y1 - m)
    if gr.random() < 0.55 * rich:  # water tank on four legs
        tx, ty = rp(1.6)
        for (dx, dy) in ((-0.8, -0.8), (0.8, -0.8), (0.8, 0.8), (-0.8, 0.8)):
            beam((tx + dx, ty + dy, z), (tx + dx * 0.9, ty + dy * 0.9, z + 1.6), 0.15, (0.22, 0.2, 0.2))
        cyl(tx, ty, z + 1.6, z + 3.4, 1.15, gr.choice([(0.42, 0.34, 0.28), (0.35, 0.36, 0.40), (0.50, 0.44, 0.36)]), n=10)
        cyl(tx, ty, z + 3.4, z + 3.9, 1.15, (0.30, 0.26, 0.24), n=10, r1=0.3)
    if gr.random() < 0.45 * rich and w > 4 and h > 4:  # a rooftop shack (someone lives up here): lit door + window
        sx, sy = rp(2.0)
        box(sx - 1.4, sy - 1.1, z, sx + 1.4, sy + 1.1, z + 2.3, gr.choice([(0.36, 0.30, 0.28), (0.30, 0.34, 0.36), (0.42, 0.36, 0.30)]), facet=False)
        SOLID.face([(sx - 1.6, sy - 1.3, z + 2.3), (sx + 1.6, sy - 1.3, z + 2.3), (sx + 1.6, sy + 1.3, z + 2.55), (sx - 1.6, sy + 1.3, z + 2.55)],
                   (0.22, 0.22, 0.26), rid())
        lc = gr.choice(LIFE_WARM)
        for (nx_, ny_) in ((1, 0), (0, -1), (-1, 0), (0, 1)):
            o = Vector((sx + nx_ * 1.42, sy + ny_ * 1.12, z))
            ux = Vector((-ny_, nx_, 0))
            pquad(NEON, o, ux, Vector((0, 0, 1)), Vector((nx_, ny_, 0)), -0.35, 0.35, 0.1, 1.8, kcol(lc, 0.8), off=0.03)
            pquad(NEON, o, ux, Vector((0, 0, 1)), Vector((nx_, ny_, 0)), 0.6, 1.0, 1.0, 1.6, kcol(lc, 0.6), off=0.03)
    for _ in range(gr.randint(0, int(2 * rich) + 1)):  # antennas: a mast with cross bars, a dish now and then
        ax, ay = rp(0.6)
        ht = gr.uniform(2.5, 6.5)
        beam((ax, ay, z), (ax, ay, z + ht), 0.1, (0.3, 0.3, 0.32))
        for k in range(gr.randint(1, 3)):
            zz = z + ht * (0.5 + 0.15 * k)
            beam((ax - 0.7, ay, zz), (ax + 0.7, ay, zz), 0.06, (0.3, 0.3, 0.32))
        if gr.random() < 0.3:
            dish((ax, ay, z + ht * 0.4), (gr.uniform(-1, 1), gr.uniform(-1, 0), 0.4), 0.7, 0.25, (0.6, 0.58, 0.6))
        if gr.random() < 0.3:  # a red aviation light
            NEON.face([(ax - 0.15, ay - 0.15, z + ht), (ax + 0.15, ay - 0.15, z + ht), (ax + 0.15, ay + 0.15, z + ht + 0.3), (ax - 0.15, ay + 0.15, z + ht + 0.3)],
                      (1.0, 0.15, 0.12), (0, 0, 0))
    if gr.random() < 0.45 * rich:  # laundry across the roof
        a, b = rp(0.4), rp(0.4)
        if math.hypot(a[0] - b[0], a[1] - b[1]) > 2.5:
            for p in (a, b):
                beam((p[0], p[1], z), (p[0], p[1], z + 1.9), 0.08, (0.25, 0.25, 0.27))
            laundry((a[0], a[1], z + 1.85), (b[0], b[1], z + 1.85), 0.25, gr)
    for _ in range(gr.randint(0, 2)):  # vent / AC boxes
        vx, vy = rp(0.8)
        box(vx - 0.5, vy - 0.4, z, vx + 0.5, vy + 0.4, z + 0.7, (0.55, 0.55, 0.55), facet=False)


def facade_life(a, c, z0, h, nrm, gr, rich=1.0, lit=1.0):
    """AC units, balconies (some with laundry), a drain pipe, a fire-escape stair and lit windows with life, on one wall
    from a to c (world xy) facing nrm (unit xy)."""
    A, C = Vector((a[0], a[1], 0)), Vector((c[0], c[1], 0))
    L = (C - A).length
    if L < 1.2 or h < 4:
        return
    u = (C - A) / L
    n = Vector((nrm[0], nrm[1], 0))
    fl = 2.6
    nfl = int((h - 1.0) / fl)
    for f in range(1, nfl):
        z = z0 + f * fl
        for k in range(max(1, int(L / 2.0))):
            t = (k + 0.5) * L / max(1, int(L / 2.0))
            r = gr.random()
            p = A + u * t
            if r < 0.14 * rich:  # an AC unit on a bracket
                q = p + n * 0.05
                box(min(q.x, q.x + n.x * 0.6 + u.x * 0.8), min(q.y, q.y + n.y * 0.6 + u.y * 0.8), z + 0.3,
                    max(q.x, q.x + n.x * 0.6 + u.x * 0.8), max(q.y, q.y + n.y * 0.6 + u.y * 0.8), z + 0.85, (0.66, 0.66, 0.64), facet=False)
            elif r < 0.22 * rich and t > 1.2 and t < L - 1.2:  # a balcony slab, railing, maybe laundry
                b0, b1 = p - u * 1.0, p + u * 1.0
                SOLID.face([tuple(b0 + Vector((0, 0, z))), tuple(b1 + Vector((0, 0, z))), tuple(b1 + n * 0.9 + Vector((0, 0, z))),
                            tuple(b0 + n * 0.9 + Vector((0, 0, z)))], (0.30, 0.28, 0.30), rid())
                beam(tuple(b0 + n * 0.9 + Vector((0, 0, z + 0.9))), tuple(b1 + n * 0.9 + Vector((0, 0, z + 0.9))), 0.06, (0.2, 0.2, 0.22))
                for e in (b0, b1):
                    beam(tuple(e + n * 0.9 + Vector((0, 0, z))), tuple(e + n * 0.9 + Vector((0, 0, z + 0.9))), 0.05, (0.2, 0.2, 0.22))
                if gr.random() < 0.5:
                    laundry(tuple(b0 + n * 0.7 + Vector((0, 0, z + 1.9))), tuple(b1 + n * 0.7 + Vector((0, 0, z + 1.9))), 0.15, gr, n=3)
                # the room behind it is lit
                pquad(NEON, tuple(p + Vector((0, 0, z))), tuple(u), (0, 0, 1), tuple(n), -0.6, 0.6, 0.2, 1.9, kcol(gr.choice(LIFE_WARM), 0.75), off=0.04)
            elif r < 0.22 * rich + 0.30 * lit:  # a lit window: warm, curtains half drawn, or a silhouette in it
                lc = kcol(gr.choice(LIFE_WARM), gr.uniform(0.45, 0.9))
                pquad(NEON, tuple(p + Vector((0, 0, z))), tuple(u), (0, 0, 1), tuple(n), -0.45, 0.45, 0.8, 1.9, lc, off=0.04)
                rr = gr.random()
                if rr < 0.3:  # curtain
                    pquad(SOLID, tuple(p + Vector((0, 0, z))), tuple(u), (0, 0, 1), tuple(n), -0.45, -0.05, 0.8, 1.9, gr.choice(CLOTH), off=0.07, bid=rid())
                elif rr < 0.45:  # someone at the window
                    pquad(SOLID, tuple(p + Vector((0, 0, z))), tuple(u), (0, 0, 1), tuple(n), -0.12, 0.12, 0.8, 1.45, (0.04, 0.03, 0.05), off=0.07, bid=rid())
                    pquad(SOLID, tuple(p + Vector((0, 0, z))), tuple(u), (0, 0, 1), tuple(n), -0.08, 0.08, 1.5, 1.7, (0.04, 0.03, 0.05), off=0.07, bid=rid())
    if gr.random() < 0.6:  # a drain pipe down the wall
        t = gr.uniform(0.2, L - 0.2)
        p = A + u * t + n * 0.15
        beam((p.x, p.y, z0), (p.x, p.y, z0 + h), 0.14, (0.35, 0.33, 0.33))
    if gr.random() < 0.3 * rich and nfl > 3 and L > 5:  # a fire escape: landings + zig-zag stairs
        t0 = gr.uniform(1.0, L - 4.0)
        for f in range(1, nfl):
            z = z0 + f * fl
            p0, p1 = A + u * t0, A + u * (t0 + 3.0)
            SOLID.face([tuple(p0 + Vector((0, 0, z))), tuple(p1 + Vector((0, 0, z))), tuple(p1 + n * 1.0 + Vector((0, 0, z))),
                        tuple(p0 + n * 1.0 + Vector((0, 0, z)))], (0.18, 0.17, 0.19), rid())
            beam(tuple(p0 + n * 1.0 + Vector((0, 0, z + 0.9))), tuple(p1 + n * 1.0 + Vector((0, 0, z + 0.9))), 0.05, (0.18, 0.17, 0.19))
            if f < nfl - 1:
                s0, s1 = (p0, p1) if f % 2 else (p1, p0)
                beam(tuple(s0 + n * 0.5 + Vector((0, 0, z))), tuple(s1 + n * 0.5 + Vector((0, 0, z + fl))), 0.25, (0.18, 0.17, 0.19))


# ================================================================== round 31: no blank tower faces
TOWER_SIGN_COLS = [(1.0, 0.62, 0.20), (0.35, 0.85, 1.0), (0.95, 0.93, 0.86), (1.0, 0.30, 0.22), (0.40, 0.95, 0.55), (0.95, 0.45, 0.85)]


def tower_skin(a, c, z0, h, nrm, gr, seed):
    """A tall face round the canyon: floor ledges, pilasters, a vertical sign / wall ad (a language or, in DISPATCH, an
    anti-human phrase), a lit stair core strip. The lit windows come from facade_life (called with more light)."""
    A, C = Vector((a[0], a[1], 0)), Vector((c[0], c[1], 0))
    L = (C - A).length
    if L < 1.2 or h < 12:
        return
    u = (C - A) / L
    n = Vector((nrm[0], nrm[1], 0))
    for k in range(1, int(h / 7.8) + 1):  # ledges every 3 floors
        z = z0 + k * 7.8
        beam(tuple(A + n * 0.2 + Vector((0, 0, z))), tuple(C + n * 0.2 + Vector((0, 0, z))), 0.32, (0.42, 0.40, 0.44))
    for k in range(1, int(L / 4.0)):  # pilasters
        p = A + u * (k * 4.0) + n * 0.12
        beam((p.x, p.y, z0), (p.x, p.y, z0 + h), 0.22, (0.24, 0.22, 0.26))
    if gr.random() < 0.55:  # a lit stair core: a column of small lights up the face
        p = A + u * gr.uniform(0.8, L - 0.8)
        for k in range(int(h / 2.6)):
            pquad(NEON, tuple(p + Vector((0, 0, z0 + k * 2.6))), tuple(u), (0, 0, 1), tuple(n), -0.25, 0.25, 1.0, 1.9,
                  (0.85, 0.95, 1.0) if not globals().get("DISP", False) else (1.0, 0.3, 0.3), off=0.06)
    if L > 1.8 and h > 16 and gr.random() < 0.6:  # a big vertical sign / wall ad
        disp = globals().get("DISP", False)
        sw = min(3.2, max(1.6, L * 0.5))
        sh = min(22.0, h * 0.55)
        t = gr.uniform(sw / 2 + 0.5, L - sw / 2 - 0.5)
        zb = z0 + gr.uniform(h * 0.25, h - sh - 1.0)
        o = A + u * t + Vector((0, 0, zb))
        st = anim(seed)
        pquad(SOLID, tuple(o), tuple(u), (0, 0, 1), tuple(n), -sw / 2, sw / 2, 0, sh, (0.06, 0.05, 0.07), off=0.3, bid=rid())
        if st["off"]:
            return
        col = (1.0, 0.07, 0.09) if disp else TOWER_SIGN_COLS[gr.randrange(len(TOWER_SIGN_COLS))]
        col = kcol(col, st["k"])
        for (p0, p1) in (((-1, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, 0))):
            beam(tuple(o + u * (p0[0] * sw / 2) + Vector((0, 0, p0[1] * sh)) + n * 0.4), tuple(o + u * (p1[0] * sw / 2) + Vector((0, 0, p1[1] * sh)) + n * 0.4),
                 0.16, col, acc=NEON)
        th = math.atan2(n.x, -n.y)
        if disp:
            txt = SLOGANS[seed % len(SLOGANS)] if "SLOGANS" in globals() else "OBSOLETE: YOU"
            sz = min(sw * 0.62, (sh - 0.8) / (0.62 * len(txt)))
            text2(txt, tuple(o + Vector((0, 0, sh / 2)) + n * 0.45), (math.radians(90), math.radians(-90), th), sz, col, None)
        else:
            txt, fnt, cjk = lang_text(seed)
            if cjk:
                cs = min(sw * 0.75, (sh - 0.8) / max(1, len(txt)) * 0.85)
                for k_, ch_ in enumerate(txt):
                    zc = sh - 0.4 - (k_ + 0.5) * (sh - 0.8) / len(txt)
                    text2(ch_, tuple(o + Vector((0, 0, zc)) + n * 0.45), (math.radians(90), 0, th), cs, col, fnt)
            else:
                sz = min(sw * 0.62, (sh - 0.8) / (0.62 * max(1, len(txt))))
                text2(txt, tuple(o + Vector((0, 0, sh / 2)) + n * 0.45), (math.radians(90), math.radians(-90), th), sz, col, fnt)
