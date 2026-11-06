"""Scene drawing for direction B "ctOS Profiler": infection, conduits, packets, profiler tags, chips, HUD, effects."""
from ctos_common import *
from scipy.spatial import cKDTree

LANES = {'known0': -9, 'known1': -4.5, 'cand0': 0, 'cand1': 4.5, 'cand2': 9, 'hunter0': 0, 'hunter1': 0,
         'sealed_a': 0, 'sealed_b': 4.5, 'sealed_c': 9, 'hunter': 0}
HOME_G = (318.1, 678.8)
HQ_G = (1088.8, 555.0)


# =============================================================== infection
_vor = {}


def _voronoi():
    if 'e' not in _vor:
        rng = np.random.default_rng(11)
        pts = np.c_[rng.uniform(0, W, 1300), rng.uniform(0, H, 1300)]
        tree = cKDTree(pts)
        yy, xx = np.mgrid[0:H:2, 0:W:2]
        q = np.c_[xx.ravel(), yy.ravel()].astype(np.float32)
        d, _ = tree.query(q, k=2)
        e = (d[:, 1] - d[:, 0]).reshape(yy.shape)
        e = np.asarray(Image.fromarray(e.astype(np.float32), 'F').resize((W, H), Image.BILINEAR))
        _vor['e'] = e
    return _vor['e']


def _noise(seed, sigma=34):
    rng = np.random.default_rng(seed)
    n = ndi.gaussian_filter(rng.normal(0, 1, (H, W)).astype(np.float32), sigma)
    return n / (np.abs(n).max() + 1e-6)


def infect(img, centres, radius=130, grow=1.0, seed=5, strength=1.0, keep=0.10, vein=1.0):
    """Bloom A "Necrosis": plum-black body, pink Voronoi veins, hot hairline front, windows dying behind the front.
    centres: list of (x, y, radius_scale) in screen px. grow scales the radius (creep animation)."""
    if not centres:
        return img, None
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    f = np.full((H, W), -9.0, np.float32)
    for cx, cy, rs in centres:
        R = radius * rs * grow
        d = np.sqrt(((xx - cx) / R) ** 2 + ((yy - cy) / (R * ISO)) ** 2)
        f = np.maximum(f, 1 - d)
    f = f + _noise(seed) * 0.55 + _noise(seed + 1, 9) * 0.06
    mask = smoothstep(0.0, 0.025, f)
    depth = np.clip(f / 0.55, 0, 1)
    m3 = mask[..., None]
    plum = np.array(PLUM, np.float32) / 255.0
    L = lum(img)[..., None]
    dead = img * keep + plum * 1.15 + L * 0.03
    lights = smoothstep(0.45, 0.85, lum(img))[..., None]
    out = img * (1 - m3 * 0.92 * strength) + dead * m3 * 0.92 * strength
    # windows dying behind the front: a few survive near the front, none deep inside
    out += img * lights * m3 * ((1 - depth) ** 2.2)[..., None] * 0.55 * np.array([1.0, 0.45, 0.8], np.float32)
    # veins
    ve = np.exp(-(_voronoi() / 1.5) ** 2)
    vein_a = (mask * (0.28 + 0.72 * smoothstep(0.02, 0.5, f)) * strength)[..., None]
    vc = np.array(VEIN, np.float32) / 255.0
    out += ve[..., None] * vc * vein_a * 0.95 * vein + np.exp(-(_voronoi() / 5.0) ** 2)[..., None] * vc * vein_a * 0.22
    # hot hairline front + soft halo
    front = np.exp(-(f / 0.016) ** 2)
    halo = np.exp(-(f / 0.06) ** 2) * (1 - mask * 0.5)
    hc = np.array(HOT, np.float32) / 255.0
    out += front[..., None] * hc * 0.95 * strength + halo[..., None] * vc * 0.20 * strength
    return out, f


def infect_centres(j, taken, anchors, extra=None):
    cs = []
    for sid in taken:
        if sid in anchors:
            x, y = T(anchors[sid])
            cs.append((x, y - 10, 1.0))
    # bridge along the links between two TAKEN sites (their TAKEN neighbours)
    for l in j['links']:
        if l['a'] in taken and l['b'] in taken and len(l['polyline']) > 1:
            p = TP(clean_path(l['polyline']))
            for k in range(0, int(plen(p)), 40):
                q, _ = sample(p, k)
                cs.append((q[0], q[1], 0.55))
    if extra:
        cs += extra
    return cs


# =============================================================== field effects
def sweep_field(u0, width=70, ang=0.55):
    """diagonal ctOS scan band; returns 0..1 band and the leading-edge line."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = xx * math.cos(ang) + yy * math.sin(ang)
    band = np.exp(-((u - u0) / width) ** 2)
    behind = (u > u0).astype(np.float32) * np.exp(-np.clip(u - u0, 0, 9999) / 700)
    edge = np.exp(-((u - u0) / 2.6) ** 2)
    return band, behind, edge


# =============================================================== base scene
class Scene:
    def __init__(self, j):
        self.j = j
        self.anch = site_anchors(j)
        self.G = Layer()      # ground: conduits, sockets, rings
        self.U = Layer()      # up: heads, tags, chips, HUD
        self.sites = {s['id']: s for s in j['sites']}
        self.mask = territory_mask(j)

    def A(self, sid):
        return T(self.anch[sid])

    def beam_path(self, b, lane_scale=1.0):
        p = clean_path(b['polyline'])
        p = offset_path(p, LANES.get(b['name'], 0) / ZOOM * lane_scale)
        return TP(p)


# ---------- conduits / network
def draw_network(sc, a=1.0):
    G = sc.G
    seen = set()
    for l in sc.j['links']:
        if len(l['polyline']) < 2:
            continue
        key = tuple(sorted((l['a'], l['b'])))
        if key in seen:
            continue
        seen.add(key)
        p = TP(clean_path(l['polyline']))
        G.line(p, (4, 8, 20), 5.5, int(110 * a))
        G.line(p, GRID, 1.2, int(150 * a), glow=0.22 * a, gw=3)
        if l.get('locked'):
            q, _ = sample(p, plen(p) / 2)
            G.poly(hexg(q[0], q[1], 4.5, 0), fill=(6, 18, 36), outline=GRID, w=1.2)


def draw_sites(sc, only=None, dim=1.0, icons=True):
    """Site: iso hex pad on the street, a lance rising from it, a hex icon on top (plum when TAKEN). Tag / chip / marks are drawn by other calls."""
    G, U = sc.G, sc.U
    for sid, s in sc.sites.items():
        if only and sid not in only:
            continue
        x, y = sc.A(sid)
        col = GRID
        iso_hex(G, x, y, 15, (4, 8, 20), w=3, glow=0)
        iso_hex(G, x, y, 15, col, w=1.6, glow=0.55 * dim)
        iso_hex(G, x, y, 7.5, col, w=1.2, glow=0.3 * dim)
        G.line([(x, y), (x, y - 46)], col, 1.2, int(180 * dim), glow=0.25 * dim)
        if icons:
            tk = s['state'] in ('TAKEN', 'INFECTED')
            ic = VEIN if tk else (225, 238, 250)
            site_glyph(U, x, y - 56, 11.5, ic, exploit=s['exploit'], fill=(30, 8, 34) if tk else (5, 12, 28), w=2.0, glow=0.6 * dim)


def draw_hq(sc, pulse=0.0, hot=False):
    """Solace origin: concentric uplink rings on the street and a helix badge. Origin of every raid line."""
    G, U = sc.G, sc.U
    x, y = T(sc.anch['hq'])
    for k, r in enumerate((26, 40, 58)):
        a = 255 if k == 0 else 150
        iso_ring(G, x, y, r + pulse * 14 * (k + 1) / 3, SOLACE, w=2.2 - k * .4, a=a, glow=0.6 - k * .1)
    G.line([(x, y), (x, y - 62)], SOLACE, 2, 220, glow=0.7)
    hexc = (x, y - 78)
    U.poly(hexg(hexc[0], hexc[1], 19, math.pi / 6), fill=(4, 20, 14), outline=SOLACE, w=2.4, glow=0.9)
    for sgn in (1, -1):                                         # the Solace helix, two strands
        pts = [(hexc[0] + sgn * 8 * math.sin(t / 3.2), hexc[1] + t) for t in np.arange(-11, 11.5, 1)]
        U.line(pts, SOLACE, 2.2, glow=0.7)
    for t in (-7, -2, 3, 8):
        U.line([(hexc[0] - 7, hexc[1] + t), (hexc[0] + 7, hexc[1] + t)], SOLACE, 1.1, 190)


def draw_home(sc, hp=44, hpmax=50, hit=0.0, dial=None, yellow=True):
    """HOME: our building. Yellow house on a lance, a double iso ring and an HP segment ring (one segment per 1 HP / 5)."""
    G, U = sc.G, sc.U
    x, y = T(sc.anch['home'])
    col = PENCIL_YEL
    iso_ring(G, x, y, 46, col, w=2.4, glow=0.8)
    iso_ring(G, x, y, 34, col, w=1.4, a=200, glow=0.4)
    G.line([(x, y), (x, y - 56)], col, 2, 230, glow=0.7)
    U.poly(hexg(x, y - 78, 21, math.pi / 6), fill=(24, 20, 2), outline=col, w=2.6, glow=0.9)
    house(U, x, y - 80, 12, col)
    # HP ring: 10 segments around the ground ring (each = 5 HP), the lost ones hollow
    n = 10
    full = hp / hpmax * n
    for k in range(n):
        a0 = -90 + k * 36 + 4
        on = k + 1 <= full + 1e-6
        c = TIER['HOLDS'] if on else (70, 40, 20)
        U.arc(x, y, 62, 62 * ISO, a0, a0 + 28, c, w=5 if on else 3, glow=0.7 if on else 0)
    if hit > 0:
        iso_ring(G, x, y, 46 + hit * 60, WHITE, w=3, glow=1.0)


# ---------- beams
def beam_state(b, **kw):
    d = dict(prog=0.0, alpha=1.0, sealed=False, stop=None, spent=False, hot=False, bead_gap=40.0)
    d.update(kw)
    return d


def _bead(L, t, x, y, r, col, ang, hollow=True, a=255):
    if t == 'D':
        L.ellipse(x, y, r, r, outline=col, w=1.6, a=a, glow=0.6)
    elif t == 'N':
        L.poly(rot_sq(x, y, r * .85, 0), outline=col, w=1.6, glow=0.6)
    else:
        L.poly(tri(x, y, r * 1.2, ang), outline=col, w=1.6, glow=0.6)


def draw_beam(sc, b, st):
    """A raid line as a data-packet train in a conduit. Type = head shape + hue; sealed = ciphered hex beads + letter lock."""
    G, U = sc.G, sc.U
    p = sc.beam_path(b)
    if st.get('clip'):
        keep_n = 1
        while keep_n < len(p) and st['clip'](p[keep_n]):
            keep_n += 1
        p = p[:keep_n + 1] if keep_n < len(p) else p
        if len(p) < 2:
            return p
    Lp = plen(p)
    t = b['type']
    col = BEAM[t]
    al = st['alpha']
    role = b['role']
    sealed = st['sealed'] or role == 'cand'
    if role == 'hunter':
        return draw_hunter(sc, b, st)
    base_col = (200, 210, 235) if sealed else col
    # conduit casing + line
    G.line(p, (1, 2, 8), 9.5, int(190 * al * al))
    if sealed:
        n = int(Lp / 10)
        for k in range(0, n, 2):
            q0, _ = sample(p, k * 10)
            q1, _ = sample(p, min(Lp, k * 10 + 6))
            G.line([q0, q1], base_col, 2.6, int(230 * al), glow=0.5 * al)
    else:
        la = al if st['prog'] <= 0.01 else al * 0.28
        G.line(p, col, 5.6, int(255 * la), glow=1.0 * la, gw=10)
        G.line(p, tuple(int(c * .5 + 255 * .5) for c in col), 1.1, int(200 * la))
    done = st['prog'] * Lp
    if done > 4:                                         # fired part: hot line + dense bead trail
        seg = sub_path(p, 0, done)
        G.line(seg, col, 7.5, int(255 * al), glow=1.2 * al, gw=13)
        G.line(seg, WHITE, 1.8, int(240 * al))
        s = done - 16
        k = 0
        while s > 0 and k < 14:
            q, ang = sample(p, s)
            _bead(U, t, q[0], q[1], max(2.2, 5.2 - k * .25), col, ang, a=int(255 * al))
            s -= 15
            k += 1
    # idle beads ahead (queued packets): the type is readable all along the line
    s = done + st['bead_gap'] * 0.6
    while s < Lp - 10:
        q, ang = sample(p, s)
        if sealed:
            U.poly(hexg(q[0], q[1], 4.6, 0), outline=(215, 225, 250), w=1.5, glow=0.5 * al)
        else:
            _bead(U, t, q[0], q[1], 6.0, col, ang, a=int(230 * al))
        s += st['bead_gap']
    # head
    if st['prog'] <= 0.01 and not sealed and not st.get('nohead'):
        q, ang = sample(p, 26)
        type_glyph(U, t, q[0], q[1], 9.5, col, ang=ang)
    if st['prog'] > 0:
        q, ang = sample(p, done)
        if sealed:
            pass
        else:
            type_glyph(U, t, q[0], q[1], 14 if st['hot'] else 9, col, ang=ang)
            if st['hot']:
                iso_ring(G, q[0], q[1] + 6, 24, col, w=2, glow=0.8)
    if sealed:                                            # letter lock at a spread-out spot on the line
        k = {'cand0': .34, 'cand1': .5, 'cand2': .66, 'sealed_a': .34, 'sealed_b': .5, 'sealed_c': .66}.get(b['name'], .5)
        q, _ = sample(p, Lp * k)
        letter = b.get('chip') or {'sealed_a': 'A', 'sealed_b': 'B', 'sealed_c': 'C', 'cand0': 'A', 'cand1': 'B', 'cand2': 'C'}.get(b['name'], '?')
        U.poly(hexg(q[0], q[1], 13, math.pi / 6), fill=(8, 10, 24), outline=(225, 232, 250), w=2, glow=0.6)
        U.text((q[0], q[1] + 0.5), letter, font('anton', 15), WHITE)
        U.line([(q[0] - 5, q[1] - 16), (q[0] - 5, q[1] - 21), (q[0] + 5, q[1] - 21), (q[0] + 5, q[1] - 16)], (225, 232, 250), 1.6)   # shackle
    if role == 'known' and st['prog'] <= 0.01 and b.get('label') and not st.get('nolabel'):
        n = int(b['label'][1:]) if b['label'][1:].isdigit() else 1
        q, ang = sample(p, 34)
        for i in range(n):                                # K1 / K2 -> ordinal ticks, no text
            U.line([(q[0] + i * 6 - (n - 1) * 3, q[1] - 24), (q[0] + i * 6 - (n - 1) * 3, q[1] - 13)], col, 2.4, glow=0.6)
    return p


def draw_hunter(sc, b, st):
    G, U = sc.G, sc.U
    pts = [sc.A(s) for s in b['site_path']]
    al = st['alpha']
    col = (255, 255, 255)
    # two-street fork: dotted conduit between the Sites on the street polyline
    p = TP(clean_path(b['polyline'])) if b.get('polyline') else pts
    for i in range(0, int(plen(p)), 9):
        q, _ = sample(p, i)
        U.ellipse(q[0], q[1], 1.5, 1.5, fill=col, a=int(190 * al))
    qe, _ = sample(p, plen(p) * 0.5)
    # reticle (revealed last): ring + 4 ticks
    U.ellipse(qe[0], qe[1], 10, 10, outline=col, w=1.6, glow=0.5 * al)
    for k in range(4):
        a = k * math.pi / 2
        U.line([(qe[0] + math.cos(a) * 6, qe[1] + math.sin(a) * 6), (qe[0] + math.cos(a) * 16, qe[1] + math.sin(a) * 16)], col, 1.6, int(220 * al))
    U.ellipse(qe[0], qe[1], 2.5, 2.5, fill=col)
    return p


# =============================================================== chips, cards, tags
def chip(U, x, y, verb, typ=None, w=42, h=28, lit=True, spent=False, accent=CYAN, scale=1.0):
    """CRT chip slotted in a socket: navy glass, cyan edge, gold pins, verb glyph, type pip."""
    w, h = w * scale, h * scale
    x0, y0 = x - w / 2, y - h / 2
    for k in range(5):                                    # gold pins
        U.line([(x0 + 5 + k * (w - 10) / 4, y0 + h), (x0 + 5 + k * (w - 10) / 4, y0 + h + 4)], (230, 180, 60), 1.8)
    U.poly(chamfer(x0, y0, w, h, 6 * scale), fill=(5, 14, 34), outline=accent, w=1.8, glow=0.7 if lit else 0.2)
    verb_glyph(U, verb, x - 5 * scale, y, 7.5 * scale, WHITE if not spent else (110, 120, 140))
    if typ:
        px, py = x0 + w - 9 * scale, y0 + 9 * scale
        type_glyph(U, typ, px, py, 4.2 * scale, glow=0.5)


def verb_glyph(L, verb, x, y, r, col):
    if verb == 'GUARD':
        L.poly(shield_pts(x, y, r), fill=col)
    elif verb == 'SHIFT':
        L.arc(x, y + 1, r * .8, r * .8, 180, 360, col, w=max(2, r * .32), step=10)
        L.poly([(x + r * .8 - r * .5, y + 1), (x + r * 1.1 + r * .5, y + 1), (x + r * .8, y + r * .95)], fill=col)
    elif verb == 'JAM':
        L.line([(x - r, y + r * .5), (x - r * .5, y - r * .6), (x, y + r * .5), (x + r * .5, y - r * .6), (x + r, y + r * .5)], col, max(2, r * .3))


def card(U, x, y, verb, typ, ang=0.0, w=74, h=102, selected=False, dim=False, spent=False):
    """vinyl sticker card (module 13): white die-cut border, ink body, one big verb glyph, the type pip. No words."""
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def R(px, py):
        return (x + px * c - py * s, y + px * s + py * c)
    border = [R(-w / 2, -h / 2), R(w / 2, -h / 2), R(w / 2, h / 2), R(-w / 2, h / 2)]
    a = 130 if dim else 255
    U.poly([(px + 3, py + 5) for px, py in border], fill=(0, 0, 0), a=120)
    U.poly(border, fill=(238, 234, 222) if not dim else (120, 120, 130), a=a)
    inner = [R(-w / 2 + 4, -h / 2 + 4), R(w / 2 - 4, -h / 2 + 4), R(w / 2 - 4, h / 2 - 4), R(-w / 2 + 4, h / 2 - 4)]
    U.poly(inner, fill=(10, 14, 30), a=a)
    gx, gy = R(0, -6)
    verb_glyph(U, verb, gx, gy, 20, (240, 244, 255) if not dim else (130, 140, 160))
    # type pip band
    bx, by = R(0, h / 2 - 17)
    type_glyph(U, typ, bx, by, 8, glow=0.6 if not dim else 0.1)
    if selected:
        U.poly(border, outline=LIME, w=3, glow=1.0, ow=8)


def threat_tag(U, x, y, tier_col, glyph='site', num=None, exploit=False, pct=None, size=1.0, accent=None, ring_fill=None):
    """Profiler tag popping off a Site: chamfered glass, site hex in the tier colour, a number, a tier bar. Anchored by a tether."""
    w, h = 66 * size, 30 * size
    x0, y0 = x - w / 2, y - h / 2
    U.poly(chamfer(x0, y0, w, h, 7 * size), fill=(4, 10, 26), outline=tier_col, w=2.2, glow=0.8, a=240)
    site_glyph(U, x0 + 15 * size, y, 8.5 * size, tier_col, exploit=exploit, w=1.7, glow=0.5)
    if num is not None:
        U.text((x0 + w - 25 * size, y + 1), str(num), font('anton', 17 * size), WHITE, stroke=1.2)
        U.text((x0 + w - 8 * size, y + 4), '%', font('mono', 11 * size), (200, 215, 235))
    if pct is not None:                                   # confidence bar
        U.line([(x0 + 4, y0 + h + 3), (x0 + 4 + (w - 8) * pct, y0 + h + 3)], tier_col, 2.6, glow=0.6)
        U.line([(x0 + 4 + (w - 8) * pct, y0 + h + 3), (x0 + w - 4, y0 + h + 3)], (60, 70, 90), 2.0)


def tag_tether(G, base, top, col):
    G.line([base, top], col, 1.4, 210, glow=0.5)


# =============================================================== marks and effects
def down_mark(U, x, y, seed=1, s=1.0):
    """D28 grease pencil DOWN: one red slash across the Site's hex."""
    grease(U, [(x - 20 * s, y + 18 * s), (x + 4 * s, y - 2 * s), (x + 22 * s, y - 20 * s)], PENCIL_RED, w=5.5 * s, seed=seed)


def taken_mark(U, x, y, seed=2, s=1.0):
    """D28 grease pencil TAKEN: the cross."""
    grease(U, [(x - 20 * s, y - 20 * s), (x + 20 * s, y + 20 * s)], PENCIL_RED, w=6 * s, seed=seed)
    grease(U, [(x + 20 * s, y - 20 * s), (x - 20 * s, y + 20 * s)], PENCIL_RED, w=6 * s, seed=seed + 7)


def bits(U, x, y, col, n=34, spread=60, seed=3, white=0.35, fnt=None, toward=None):
    """Binary-bits burst (module 16): 0/1 glyphs in the source colour, white-hot near the centre."""
    rnd = random.Random(seed)
    for i in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        d = (rnd.random() ** 0.7) * spread
        px, py = x + math.cos(a) * d, y + math.sin(a) * d * 0.8
        near = d < spread * white
        c = (255, 255, 255) if near else col
        f = font('mono', rnd.choice((10, 12, 14, 17)))
        U.line([(x + math.cos(a) * d * .55, y + math.sin(a) * d * .55 * .8), (px, py)], col, 1.0, 110, glow=0.2)
        U.text((px, py), rnd.choice('01'), f, c, a=int(255 - d / spread * 120), glow=0.5, stroke=0.8, stroke_col=(0, 0, 0))


def hex_shield(U, G, x, y, r, col, a=1.0):
    """Hex shield flash: a dome of hex cells (centre + ring), a bright rim and a ripple."""
    cells = [(0, 0)] + [(math.cos(math.pi / 3 * k), math.sin(math.pi / 3 * k)) for k in range(6)]
    rr = r * 0.52
    for cx, cy in cells:
        pts = hexg(x + cx * rr * 1.75, y + cy * rr * 1.75 * 0.92 - r * .1, rr, math.pi / 6)
        U.poly(pts, fill=col, a=int(55 * a))
        U.poly(pts, outline=col, w=1.6, glow=0.9 * a)
    U.poly(hexg(x, y - r * .1, r * 1.9, math.pi / 6), outline=WHITE, w=2.2, glow=1.0 * a)
    iso_ring(G, x, y + r * .9, r * 2.5, col, w=2.5, glow=1.0 * a)
    iso_ring(G, x, y + r * .9, r * 3.4, col, w=1.4, a=150, glow=0.5 * a)


def impact_flash(G, x, y, col, r=30):
    iso_ring(G, x, y + 6, r, WHITE, w=3, glow=1.0)
    iso_ring(G, x, y + 6, r * 1.8, col, w=2, glow=0.8)
    for k in range(10):
        a = k * math.pi / 5 + 0.2
        G.line([(x + math.cos(a) * r * .5, y + math.sin(a) * r * .5), (x + math.cos(a) * r * 1.3, y + math.sin(a) * r * 1.3)], WHITE, 1.6, glow=0.8)


# =============================================================== HUD
def hud(sc, hp=44, hpmax=50, heat=80, healthy=8, infected=0, line=9, raid=1, queued=1, words=True, hurt=False, flash_inf=0.0):
    """Raid counters only (HOME, HEAT, INFECTED/healthy deck strip, RAID pips). Numbers and glyphs, no words."""
    U = sc.U

    def plate(x, y, w, h, col=CYAN):
        U.poly(chamfer(x, y, w, h, 9), fill=(4, 10, 26), outline=col, w=1.8, glow=0.5, a=232)
        for yy in range(int(y + 4), int(y + h - 3), 6):
            U.line([(x + 6, yy), (x + w - 6, yy)], (30, 70, 110), 0.6, 40)
    # HOME
    plate(28, 24, 168, 56)
    U.poly(shield_pts(56, 52, 13), fill=TIER['HOLDS'] if not hurt else TIER['DAMAGED'])
    U.text((112, 52), str(hp), font('anton', 36), WHITE, stroke=1.2)
    U.text((167, 58), f'/{hpmax}', font('mono', 16), (170, 195, 220))
    # HEAT
    plate(206, 24, 150, 56, (255, 122, 26))
    flame(U, 232, 52, 12, (255, 122, 26))
    U.text((284, 52), str(heat), font('anton', 36), WHITE, stroke=1.2)
    for k, c in enumerate(((120, 130, 150), (255, 176, 0), (255, 122, 26), (255, 68, 51))):
        U.line([(318 + k * 8, 66), (318 + k * 8, 46 - k * 3)], c, 4.5)
    # deck strip: healthy cells (teal) | INFECTED cells (plum + pink rim); skull tick at the CITY LOST line
    tot = healthy + infected
    cw = 17
    wcell = max(tot, line) * (cw + 3) + 70
    plate(366, 24, wcell, 56, (200, 215, 235))
    x = 386
    for k in range(healthy):
        U.poly(chamfer(x, 40, cw, 24, 4), fill=TIER['HOLDS'], a=235)
        x += cw + 3
    for k in range(infected):
        U.poly(chamfer(x, 40, cw, 24, 4), fill=(44, 12, 50), outline=VEIN, w=1.6, glow=0.5 + flash_inf)
        U.line([(x + 4, 44), (x + cw - 4, 60)], VEIN, 1.2)
        x += cw + 3
    xl = 386 + line * (cw + 3) - 1.5
    U.line([(xl, 34), (xl, 70)], PENCIL_RED, 2.2, glow=0.5)
    skull(U, xl, 30, 5.5, (255, 255, 255), eye=(60, 8, 12))
    # RAID pips (top right)
    pw = 40 + (raid + queued) * 22
    xr = W - 28 - pw
    plate(xr, 24, pw, 56, (200, 215, 235))
    U.poly(shield_pts(xr + 22, 52, 11), outline=(220, 230, 245), w=2)
    for k in range(raid + queued):
        c = TIER['LOST'] if k < raid else None
        U.ellipse(xr + 52 + k * 22, 52, 7, 7, fill=(255, 176, 0) if k < raid else None, outline=(255, 176, 0), w=2)


def hand(sc, cards, y=996, picked=None, dim_all=False, lift=None):
    """The hand: vinyl sticker cards in a shallow fan along the bottom. cards = [(verb, type, state)]."""
    U = sc.U
    n = len(cards)
    gap = 86
    x0 = W / 2 + 90 - gap * (n - 1) / 2
    for i, (verb, typ, st) in enumerate(cards):
        a = (i - (n - 1) / 2) * 2.2
        yy = y + abs(i - (n - 1) / 2) ** 2 * 1.6
        sel = picked == i
        if sel:
            yy -= 34
        card(U, x0 + i * gap, yy, verb, typ, ang=a if not sel else 0, selected=sel, dim=(st == 'dim') or dim_all)
