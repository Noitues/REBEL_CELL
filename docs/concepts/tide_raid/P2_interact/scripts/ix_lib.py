"""P1 interactivity concepts: shared library. Extends the H2 scripts (hb / hy / ui / hz): per-element dimming, focus halos,
valid / invalid target marks, what-if preview marks, the 12-outcome tally with a diff row, the guard slots, button glyph
prompts, and the annotation layer (designer-facing, never game UI).

Everything is drawn over the real city plate through the H2 world (World / forecast routes / sites)."""
import os, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from hb import *            # World, KN, RUN, HAND, PROGRAMS, IDLE, TALLY, new_canvas, sealed_layers, locks, hunter, draw_world ...
import hz
import p2kit as PK

OUTD = OUT
FRD = OUT + 'frames/'
CLD = OUT + 'frames/clean/'
os.makedirs(FRD, exist_ok=True)
os.makedirs(CLD, exist_ok=True)

ANN_PAPER = (246, 241, 228)
ANN_INK = (10, 10, 28)
K = 0.643
GREY = hexc('8A90A8')
FOGC = ui.FOG

# ------------------------------------------------------------------ illustrative outcome model (12 outcomes)
# NOT the rules: a tidy stand-in so every frame tells one consistent story. Build supplies the real numbers from
# SolaceTideRules.forecast. Outcome j: sealed A index = j // 4, hunter street = j % 2, B-pick = (j // 2) % 2.
D_, S_, B_, H_, U_ = 'DAMAGED', 'SITES_LOST', 'BREACHED', 'HOLDS', 'UNTOUCHED'
BASE12 = [D_, D_, B_, S_, S_, D_, D_, S_, D_, B_, S_, D_]


def with_guards(base, d_at=None, n_at=None):
    """D guard stops the sealed-B outcomes (j 4..7), N guard stops the sealed-C outcomes (j 8..11)."""
    t = list(base)
    if d_at:
        t[4:8] = [H_, S_, S_, H_]
    if n_at:
        t[8:12] = [H_, D_, H_, S_]
    return t


def counts_of(t):
    c = {}
    for x in t:
        c[x] = c.get(x, 0) + 1
    return c


# ------------------------------------------------------------------ world de-emphasis (focus de-emphasis)
def hole_disc(c, rx, ry=None, soft=.55):
    ry = rx * .8 if ry is None else ry
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - c[0]) / rx) ** 2 + ((yy - c[1]) / ry) ** 2)
    return np.clip((1.0 - d) / soft, 0, 1)


def hole_path(pts, width=150, soft=34):
    ly = Lyr(pbox(pts, width), ss=1)
    ly.line([tuple(p) for p in pts], width, 255)
    return np.clip(blur(ly.full(), soft) * 1.6, 0, 1)


def grade_base(cv, amt=.5, hole=None, dark=.55, desat=.62):
    """CP2077-scanner style world shift: darken and desaturate the city, except inside `hole` (mask 0..1)."""
    a = cv.img
    m = np.full((H, W), amt, np.float32)
    if hole is not None:
        m = m * (1 - np.clip(hole, 0, 1))
    lum = (a * np.array([.3, .59, .11], np.float32)).sum(-1, keepdims=True)
    mm = m[..., None]
    a2 = lum + (a - lum) * (1 - desat * mm)
    cv.img = a2 * (1 - dark * mm)


# ------------------------------------------------------------------ sites / beams layers with per-element k
BRIGHT = {'t1_c', 't1_b', 't2_intel'}      # ranked towers: only Sites a beam stops at get the bright wire (STYLE_CONTRACT sec. 5)


def draw_sites(cv, w, states=None, programs=None, site_k=None, idle=IDLE, home_kw=None, cage_kw=None, tower_alpha=.60, home_k=1.0, bright=None):
    bright = BRIGHT if bright is None else bright
    site_k = site_k or {}
    states = states or {}
    programs = programs or {}
    ck = dict(alpha=.58)
    ck.update(cage_kw or {})
    SC.solace_cage(cv, w.hq, **ck)
    items = [(s['B'][1], 'site', sid) for sid, s in w.sites.items()]
    items.append((w.home[1], 'home', 'home'))
    for _, kind, sid in sorted(items, key=lambda x: x[0]):
        if kind == 'home':
            hk = dict(home_kw or {})
            hk['alpha'] = hk.get('alpha', 1.0) * home_k
            SC.home_deck(cv, w.home, **hk)
            continue
        s = w.sites[sid]
        st = states.get(sid, 'healthy')
        kk = site_k.get(sid, 1.0)
        isidle = sid in idle
        SC.tower(cv, s['B'], s['tier'], st, seed=sum(map(ord, sid)) % 97, alpha=tower_alpha * (.5 if isidle else 1) * kk, hs=.45 if isidle else 1.0, bright=(sid in bright and not isidle))
        pr = programs.get(sid)
        if pr:
            verb, typ = pr
            if verb == 'GUARD':
                ui.firewall(cv, s['B'], typ, k=kk)
            elif verb == 'SHIFT':
                ui.decoy(cv, s['B'], typ, s['tier'], k=kk)
            else:
                ui.tracer(cv, s['B'], typ, k=kk)
        if st == 'DOWN':
            ui.grease_down(cv, (s['B'][0], s['B'][1] - 34), 26, seed=sum(map(ord, sid)) % 50, k=kk)


def beams_layer(cv, w, ks=None, ends=None, heads=True, head_sc=1.8):
    ks = ks or {}
    ends = ends or {}
    for r in KN:
        R = w.routes[r]
        P = PX(R['path'])
        k = ks.get(r, 1.0)
        if k <= 0:
            continue
        hy.ribbon(cv, P, R['typ'], R['ext'], ends.get(r, P.L), k=k, glow=.9 + .1 * k)


def heads_layer(cv, w, ks=None, runs=None, sc=1.8):
    ks = ks or {}
    runs = runs or RUN
    for r in KN:
        k = ks.get(r, 1.0)
        if k <= 0:
            continue
        R = w.routes[r]
        hy.head(cv, PX(R['path']), R['ext'] + runs[r], R['typ'], sc=sc, k=k)


def pressure_layer(cv, w, runs, ks, states):
    """STYLE_CONTRACT pressure: faint plum creep from the HQ cage base, dread shadow ahead of every head, draining ring on DOWN Sites."""
    PK.plum_creep(cv, w.hq, R=150.0, k=.38)
    for r in KN:
        k = (ks or {}).get(r, 1.0)
        if k <= 0:
            continue
        R = w.routes[r]
        PK.dread_shadow(cv, PX(R['path']), R['ext'] + runs[r], k=min(k, 1.0), amt=.38)
    for sid, st in states.items():
        if st == 'DOWN':
            PK.drain_ring(cv, w.sites[sid]['B'], frac=.66)


def plan_base(w, grade=0.0, hole=None, ks=None, sealed_k=.8, programs=None, site_k=None, states=None, idle=IDLE,
              lock_k=.8, hunter_k=.75, home_kw=None, home_k=1.0, ends=None, heads=True, show_locks=True, show_hunter=True,
              head_sc=1.8, runs=None, bright=None, pressure=True):
    cv = new_canvas(w)
    if grade:
        grade_base(cv, grade, hole)
    if pressure:
        pressure_layer(cv, w, runs or RUN, ks, states or {'t1_a': 'DOWN'})
    sk = sealed_k
    if sk > 0:
        sealed_layers(cv, w, k=sk)
    beams_layer(cv, w, ks, ends)
    draw_sites(cv, w, states or {'t1_a': 'DOWN'}, programs or {}, site_k, idle=idle, home_kw=home_kw or dict(hp=44), home_k=home_k, bright=bright)
    if heads:
        heads_layer(cv, w, ks, runs, sc=head_sc)
    if show_locks and lock_k > 0:
        locks(cv, w, k=lock_k)
    if show_hunter and hunter_k > 0:
        hunter(cv, w, k=hunter_k)
    return cv


# ------------------------------------------------------------------ focus halos (lime is ONLY the focus)
def _brackets(cv, B, r, k=1.0, frac=.36, w=5.8):
    """lime FOCUS BRACKETS: the four corners of an iso diamond (a shape no tier ring uses), so lime never reads as amber."""
    P = iso_diamond(B, r)
    ly = Lyr(pbox(P, 16))
    for i in range(4):
        a, b, c = np.array(P[i - 1], float), np.array(P[i], float), np.array(P[(i + 1) % 4], float)
        ly.line([tuple(b + (a - b) * frac), tuple(b), tuple(b + (c - b) * frac)], w, 255)
    cv.over(INK, blur(ly.m, 2.5) * 2.0, .85 * k, ly.off)
    cv.neonL(ly, LIME, core=1.0 * k, g1=(4, .9 * k), g2=(12, .6 * k))
    return P


def halo_site(cv, B, k=1.0, r=88):
    B = np.array(B) + np.array([0, 6])
    _brackets(cv, B, r, k)
    ly = Lyr((B[0] - r - 12, B[1] - r * K - 12, B[0] + r + 12, B[1] + r * K + 12))
    ly.line(ring_pts(B, r * .86, 72), 1.5, 255, dash=(3, 7))
    cv.neonL(ly, LIME, core=.55 * k, g1=None, g2=None)


def halo_home(cv, home, k=1.0, r=124):
    B = np.array(home) + np.array([0, 4])
    _brackets(cv, B, r, k, frac=.3, w=5.2)


def halo_beam(cv, P, s0, s1, k=1.0, wd=11.0):
    """a lime casing hairline pair either side of the ribbon (the ribbon itself stays its pure type hue)."""
    pts = P.sub(s0, s1, 4)
    bb = pbox(pts, 40)
    outer, inner = Lyr(bb), Lyr(bb)
    outer.line([tuple(p) for p in pts], wd + 22, 255)
    inner.line([tuple(p) for p in pts], wd + 14, 255)
    ring = np.clip(outer.m - inner.m, 0, 1)
    cv.add(LIME, ring, .95 * k, outer.off)
    cv.add(LIME, blur(ring, 4), .75 * k, outer.off)
    cv.add(LIME, blur(ring, 11), .35 * k, outer.off)


def halo_rect(cv, x0, y0, x1, y1, r=10, k=1.0):
    ly = Lyr((x0 - 12, y0 - 12, x1 + 12, y1 + 12))
    ly.rr(x0, y0, x1, y1, r, 255, outline=True, ow=4)
    cv.neonL(ly, LIME, core=1.0 * k, g1=(4, .9 * k), g2=(12, .6 * k))


# ------------------------------------------------------------------ preview (uncommitted) marks: dashed white outer outline
def dashed_poly(cv, pts, k=1.0, col=None, w=2.0, dash=(6, 5)):
    col = WHITE * .92 if col is None else col
    pts = list(pts)
    ly = Lyr(pbox(pts, 14))
    ly.line([tuple(p) for p in pts] + [tuple(pts[0])], w, 255, dash=dash)
    cv.neonL(ly, col, core=.9 * k, g1=(2, .35 * k), g2=None)


def pv_ring(cv, B, tier, r=46, k=1.0, pulse=1.0):
    """PREVIEW ring: the tier ring + the second 'uncommitted' channel (white hatch over the band, pulse halo, dashed outline)."""
    hy.target_ring(cv, B, tier, k=k, preview=True, pulse=pulse)


def pv_block(cv, P, s, tier, k=1.0, length=44, half=17, pulse=1.0):
    hy.stop_block(cv, P, s, tier, k=k, preview=True, pulse=pulse)


def pv_tile(cv, c, tier, num=None, r=30, k=1.0, pulse=1.0):
    hy.hex_tile(cv, c, tier, num, r=r, k=k, preview=True, pulse=pulse)


def old_ring(cv, B, tier, r=46, k=1.0):
    """what the ring WAS (before the what-if): a thin dashed ring in the old tier colour, larger than the new one."""
    ly = Lyr((B[0] - r - 30, B[1] - r * K - 30, B[0] + r + 30, B[1] + r * K + 30))
    ly.line(ring_pts(B, r + 22, 72), 2.4, 255, dash=(3, 5))
    cv.neonL(ly, TIER[tier], core=.55 * k, g1=None, g2=None)


def old_tile(cv, c, tier, r=24, k=.6):
    """what the tile WAS: a small ghost hex outline with the old glyph, in the old tier colour."""
    col = TIER[tier]
    e, g = Lyr((c[0] - r - 12, c[1] - r - 12, c[0] + r + 12, c[1] + r + 12)), Lyr((c[0] - r - 12, c[1] - r - 12, c[0] + r + 12, c[1] + r + 12))
    e.line(hy.hexpts(c, r) + [hy.hexpts(c, r)[0]], 2.0, 255, dash=(4, 4))
    g_tier(g, tier, c, r * .56)
    cv.neonL(e, col, core=.8 * k, g1=None, g2=None)
    cv.neonL(g, col, core=.7 * k, g1=None, g2=None)


def arrow_chip(cv, a, b, col=None, k=1.0, w=2.6, head=11, dash=None):
    """a short grease-pencil style arrow from a to b."""
    col = WHITE * .9 if col is None else col
    a = np.array(a, float); b = np.array(b, float)
    d = b - a
    L = np.hypot(*d)
    if L < 1:
        return
    u = d / L
    n = np.array([-u[1], u[0]])
    ly = Lyr(pbox([a, b], 20))
    ly.line([tuple(a), tuple(b - u * head * .5)], w, 255, dash=dash)
    ly.poly([tuple(b), tuple(b - u * head + n * head * .55), tuple(b - u * head - n * head * .55)], 255)
    cv.over(INK, blur(ly.m, 2.5) * 1.8, .7 * k, ly.off)
    cv.neonL(ly, col, core=1.0 * k, g1=(2, .4 * k), g2=None)


# ------------------------------------------------------------------ drop-target marks
def type_chip(cv, c, typ, r=15, k=1.0, col=None):
    col = TYPE_COL[typ] if col is None else col
    ui.glyph_disc(cv, c, r, col, lambda l, c_, r_: g_type(l, typ, c_, r_), gscale=.66, k=k, ring_w=2.4)


def pad_ring(cv, B, col, r=44, k=1.0, fill=.14, w=3.6, dash=None, white=.15):
    bx = (B[0] - r - 14, B[1] - r * K - 14, B[0] + r + 14, B[1] + r * K + 14)
    ring, fl, cas = Lyr(bx), Lyr(bx), Lyr(bx)
    pts = ring_pts(B, r, 72)
    ring.line(pts + [pts[0]], w, 255, dash=dash)
    cas.line(pts + [pts[0]], w + 5, 255)
    fl.poly(pts, 255)
    cv.over(INK, blur(cas.m, 2), .75 * k, cas.off)
    cv.add(col, fl.m, fill * k, fl.off)
    cv.neonL(ring, col, core=1.0 * k, g1=(3, .8 * k), g2=(9, .45 * k), white=white)


def mk_match(cv, B, typ, k=1.0, strong=True, r=44):
    """MATCH: this Site is on a KNOWN beam of the card's type: pad ring in the type hue + the type glyph standing above it."""
    pad_ring(cv, B, TYPE_COL[typ], r=r, k=k, fill=.2 if strong else .1)
    type_chip(cv, (B[0], B[1] - 108), typ, 15, k=k)
    ly = Lyr((B[0] - 6, B[1] - 100, B[0] + 6, B[1] - 10))
    ly.line([(B[0], B[1] - 94), (B[0], B[1] - 14)], 1.4, 255, dash=(2, 4))
    cv.neonL(ly, TYPE_COL[typ], core=.7 * k, g1=None, g2=None)


def g_qmark(ly, c, r):
    ly.arc((c[0], c[1] - r * .32), r * .52, 180, 380, max(2.4, r * .3))
    ly.line([(c[0] + r * .38, c[1] + r * .08), (c[0], c[1] + r * .34), (c[0], c[1] + r * .52)], max(2.4, r * .3), 255)
    ly.ell((c[0], c[1] + r * .92), max(1.8, r * .17), v=255)


def mk_maybe(cv, B, k=1.0, r=44):
    """MAYBE: only a sealed route passes (its type is hidden): fog-lavender dotted ring + '?' chip. Never leaks the type."""
    pad_ring(cv, B, FOGC, r=r, k=k * .9, fill=.08, w=3.0, dash=(2.5, 5.5))
    c = (B[0], B[1] - 108)
    ui.glyph_disc(cv, c, 15, FOGC, g_qmark, gscale=.62, k=k, ring_w=2.4)


def g_neq(ly, c, r):
    ly.line([(c[0] - r * .8, c[1] - r * .3), (c[0] + r * .8, c[1] - r * .3)], max(2.2, r * .22), 255)
    ly.line([(c[0] - r * .8, c[1] + r * .3), (c[0] + r * .8, c[1] + r * .3)], max(2.2, r * .22), 255)
    ly.line([(c[0] + r * .45, c[1] - r * .95), (c[0] - r * .45, c[1] + r * .95)], max(2.2, r * .22), 255)


def mk_dud(cv, B, card_typ, beam_typ, k=1.0, r=44):
    """DUD (soft): the card is legal here but the beam is another type: grey ring + [card glyph != beam glyph]."""
    pad_ring(cv, B, GREY, r=r, k=k * .8, fill=.05, w=3.0, dash=(8, 6))
    y = B[1] - 106
    type_chip(cv, (B[0] - 32, y), card_typ, 13, k=k * .95)
    ly = Lyr((B[0] - 14, y - 14, B[0] + 14, y + 14))
    g_neq(ly, (B[0], y), 9)
    cv.over(INK, blur(ly.m, 3) * 1.6, .85 * k, ly.off)
    cv.neonL(ly, WHITE * .9, core=1.0 * k, g1=(2, .4 * k), g2=None)
    type_chip(cv, (B[0] + 32, y), beam_typ, 13, k=k * .95)


def mk_none(cv, B, k=1.0, r=40):
    """NONE (no beam reaches / DOWN): a grey hollow ring cut by a hairline slash; nothing lights."""
    ly = Lyr((B[0] - r - 12, B[1] - r * K - 12, B[0] + r + 12, B[1] + r * K + 12))
    ly.line(ring_pts(B, r, 60), 2.2, 255, dash=(3, 6))
    ly.line([(B[0] - r * .5, B[1] + r * K * .5), (B[0] + r * .5, B[1] - r * K * .5)], 2.0, 255)
    cv.neonL(ly, GREY, core=.75 * k, g1=None, g2=None)


def refuse(cv, c, r=26, k=1.0, seed=3, col=None):
    """the red grease-pencil circle-slash (the nudge-lock mark): a hard refusal."""
    col = GREASE_R if col is None else col
    ly = Lyr((c[0] - r - 14, c[1] - r - 14, c[0] + r + 14, c[1] + r + 14))
    ring = []
    rng = np.random.RandomState(seed)
    for a in np.linspace(-20, 345, 28):
        rr = r + rng.uniform(-1.6, 1.6)
        ring.append((c[0] + rr * math.cos(math.radians(a)), c[1] + rr * math.sin(math.radians(a))))
    ly.line(ring, 6.0, 255)
    ui.scribble(ly, (c[0] - r * .72, c[1] + r * .72), (c[0] + r * .72, c[1] - r * .72), 6.0, seed + 1, 2, 1.6)
    cv.over(INK, blur(ly.m, 3) * 1.6, .7 * k, ly.off)
    cv.add(col, ly.m, 1.0 * k, ly.off)
    cv.add(col, blur(ly.m, 5), .4 * k, ly.off)


def g_equal_walls(ly, c, r):
    ly.line([(c[0] - r * .8, c[1] - r * .32), (c[0] + r * .8, c[1] - r * .32)], max(2.2, r * .24), 255)
    ly.line([(c[0] - r * .8, c[1] + r * .32), (c[0] + r * .8, c[1] + r * .32)], max(2.2, r * .24), 255)


def mk_same(cv, B, typ, k=1.0, r=44):
    """SAME (soft): another guard already covers this: the existing wall stays lit, a '=' chip says 'already this'."""
    pad_ring(cv, B, GREY, r=r, k=k * .8, fill=.04, w=3.0, dash=(8, 6))
    c = (B[0], B[1] - 108)
    ui.glyph_disc(cv, c, 15, WHITE * .9, g_equal_walls, gscale=.62, k=k, ring_w=2.4)


def slots(cv, c, filled, k=1.0, limit_flash=False, hl=None):
    """the 2 guard slots (the solace_tide_max_placed limit as two physical sockets). filled: list of None | (verb, typ)."""
    for i, f in enumerate(filled):
        p = (c[0] + (i - (len(filled) - 1) / 2) * 76, c[1])
        r = 31
        bx = (p[0] - r - 14, p[1] - r - 14, p[0] + r + 14, p[1] + r + 14)
        o, e = Lyr(bx), Lyr(bx)
        o.poly(hy.hexpts(p, r + 4), 255)
        e.line(hy.hexpts(p, r) + [hy.hexpts(p, r)[0]], 3.0, 255, dash=None if f else (6, 5))
        cv.overL(o, INK, .9 * k)
        col = (TYPE_COL[f[1]] if f else LATT_D)
        if limit_flash:
            col = GREASE_R
        cv.neonL(e, col, core=1.0 * k, g1=(3, .7 * k), g2=(9, .4 * k))
        if f:
            g = Lyr(bx)
            ui.VERB_FN[f[0]](g, p, 13)
            cv.neonL(g, WHITE * .9, core=1.0 * k, g1=(2, .4 * k), g2=None)
            tg = Lyr(bx)
            g_type(tg, f[1], (p[0], p[1] - 22), 7)
            cv.neonL(tg, TYPE_COL[f[1]], core=1.0 * k, g1=(2, .5 * k), g2=None)
        if hl == i:
            hh = Lyr(bx)
            hh.line(hy.hexpts(p, r + 9) + [hy.hexpts(p, r + 9)[0]], 4, 255)
            cv.neonL(hh, LIME, core=1.0 * k, g1=(4, .9 * k), g2=(12, .6 * k))


# ------------------------------------------------------------------ the 12-outcome tally (+ diff row)
def _cnt(tiers):
    c = {t: 0 for t in TIERS}
    for t in tiers:
        c[t] += 1
    return c


SLOT_W = 112
TALLY_C = (372, 1002)


def tally_token(cv, c, tier, n, r=25, k=1.0, delta=None, ghost=False):
    """one pictogram of the tally: the tier tile (the same hex + glyph the Site tile uses) x its count. Zero = a dim empty slot."""
    kk = k * (1.0 if n else .22)
    if ghost:
        kk *= .8
    hy.hex_tile(cv, c, tier, None, r=r, k=kk)
    ui.ntext(cv, (c[0] + r + 9, c[1] + 1), str(n), int(r * 1.55), TIER[tier] if tier != 'SITES_LOST' else PK.WARM, anchor='lm', stroke=3, k=kk)
    if delta:
        ui.ntext(cv, (c[0] + r + 9 + (24 if n < 10 else 40), c[1] - r * .55), ('+%d' % delta) if delta > 0 else (chr(0x2212) + '%d' % -delta), int(r * 1.5),
                 WHITE, anchor='lm', stroke=3.0, k=k, glow=False)


def soft_pool(cv, c, rx, ry, k=.62):
    """a soft ink pool under a floating pictogram group (a shadow, not a panel)."""
    ly = Lyr((c[0] - rx - 60, c[1] - ry - 60, c[0] + rx + 60, c[1] + ry + 60), ss=1)
    ly.ell(c, rx, ry, 255)
    cv.over(INK, blur(ly.m, 34), k, ly.off)


def tally_xs(c, nslots=5):
    return [c[0] + (i - (nslots - 1) / 2) * SLOT_W for i in range(nslots)]


def tally12(cv, tiers, c, r=25, gap=34, group_gap=14, k=1.0, lit=None, dim_k=.32, seed=3):
    """P2 pictogram tally (replaces the 12 waxy marks): five fixed slots, tier tile x count. `lit` = outcome indices to highlight
    (lock / hunter inspect): the bright count is the lit share, and a 12-pip bar under the row shows n of 12."""
    cnt = _cnt([tiers[j] for j in (lit if lit is not None else range(len(tiers)))])
    xs = tally_xs(c)
    soft_pool(cv, (c[0], c[1] + 6), 290, 62, .6 * k)
    for x, t in zip(xs, TIERS):
        tally_token(cv, (x, c[1]), t, cnt[t], r=r, k=k)
    if lit is not None:
        pips12(cv, (c[0], c[1] + r + 20), len(lit), k=k)
    return {t: (x, c[1]) for x, t in zip(xs, TIERS)}


def pips12(cv, c, n, k=1.0, total=12, gap=15):
    ly = Lyr((c[0] - total * gap / 2 - 10, c[1] - 12, c[0] + total * gap / 2 + 10, c[1] + 12))
    dim = Lyr((c[0] - total * gap / 2 - 10, c[1] - 12, c[0] + total * gap / 2 + 10, c[1] + 12))
    for i in range(total):
        p = (c[0] + (i - (total - 1) / 2) * gap, c[1])
        (ly if i < n else dim).ell(p, 4.6, v=255)
    cv.over(INK, blur(np.maximum(ly.m, dim.m), 2.5) * 1.5, .7 * k, ly.off)
    cv.over(WHITE, ly.m, .98 * k, ly.off)
    cv.over(WHITE, dim.m, .28 * k, dim.off)


def tally_diff(cv, old, new, c, r=25, gap=34, group_gap=14, k=1.0, row=64):
    """P2 before -> after as columns, not hairlines. Five fixed tier columns: the before count is a small ghost token on the top row,
    the after count a full token on the bottom row, a chevron joins them and a signed delta (+2 / -1) marks every column that changed.
    Never more than five things to read, however many of the 12 outcomes moved. Identical rows: a single '=' badge."""
    co, cn = _cnt(old), _cnt(new)
    xs = tally_xs(c)
    changed = [t for t in TIERS if co[t] != cn[t]]
    soft_pool(cv, (c[0], c[1] - row / 2 + 6), 300, 100, .66 * k)
    for x, t in zip(xs, TIERS):
        ch = t in changed
        tally_token(cv, (x, c[1]), t, cn[t], r=r, k=k, delta=(cn[t] - co[t]) if ch else None)
        yo = c[1] - row
        tally_token(cv, (x - 4, yo), t, co[t], r=r * .7, k=k * (.8 if ch else .4), ghost=True)
        if ch:
            ar = Lyr((x - 14, yo + 14, x + 14, c[1] - r - 2))
            ar.line([(x - 9, yo + 20), (x, yo + 30), (x + 9, yo + 20)], 3.4, 255)
            cv.over(INK, blur(ar.m, 2) * 1.6, .7 * k, ar.off)
            cv.over(WHITE, ar.m, .98 * k, ar.off)
    if not changed:
        ui.glyph_disc(cv, (xs[0] - 82, c[1] - row / 2), 19, WHITE * .92, g_equal_walls, gscale=.62, k=k, ring_w=2.6)
    return {t: (x, c[1]) for x, t in zip(xs, TIERS)}


def tally_underlines(cv, tiers, lit, c, r=21, gap=34, group_gap=14, k=1.0):
    pass


def tray(cv, x0, y0, x1, y1, k=1.0):
    """P2: no panel behind the tally. The tokens carry their own ink plates (pictogram-only, STYLE_CONTRACT wordless rule)."""
    pass


# ------------------------------------------------------------------ intent pair chip: [beam head glyph] -> [tier tile]
def pair_chip(cv, c, typ, tier, num=None, k=1.0, passthrough=False):
    """one line of the Site read-out: which beam type (its head silhouette) -> what it does here (tier tile)."""
    th = (c[0] - 34, c[1])
    type_chip(cv, th, typ, 15, k=k)
    ar = Lyr((c[0] - 22, c[1] - 10, c[0] + 4, c[1] + 10))
    ar.line([(c[0] - 18, c[1]), (c[0] - 2, c[1])], 2.2, 255)
    ar.poly([(c[0] + 3, c[1]), (c[0] - 6, c[1] - 6), (c[0] - 6, c[1] + 6)], 255)
    cv.neonL(ar, WHITE * .85, core=.9 * k, g1=None, g2=None)
    if passthrough:
        ui.glyph_disc(cv, (c[0] + 24, c[1]), 14, TIER['UNTOUCHED'], lambda l, c_, r_: g_tier(l, 'UNTOUCHED', c_, r_), gscale=.62, k=k * .85, ring_w=2.2)
    else:
        hy.hex_tile(cv, (c[0] + 28, c[1]), tier, num, r=19, k=k)


# ------------------------------------------------------------------ prompts: platform-agnostic button glyphs (game UI)
def _pill(cv, x0, y0, x1, y1, k=1.0, col=None):
    ui.crt_chip(cv, x0, y0, x1, y1, col=LATT_D if col is None else col, k=k, r=(y1 - y0) / 2)


def g_face(ly, c, r, which):
    """four face buttons in a diamond; `which` in S E W N filled (the pressed one), the other three hollow."""
    pos = {'N': (0, -1), 'S': (0, 1), 'W': (-1, 0), 'E': (1, 0)}
    rr = r * .36
    for kname, (dx, dy) in pos.items():
        p = (c[0] + dx * r * .62, c[1] + dy * r * .62)
        if kname == which:
            ly.ell(p, rr * 1.05, v=255)
        else:
            ly.ell(p, rr, v=255, outline=True, ow=max(1.4, r * .08))


def g_shoulder(ly, c, r, which):
    """bumper = outlined bar, trigger = filled bar with a knocked-out letter; L or R inside (layout-neutral)."""
    side = 'L' if which.startswith('L') else 'R'
    trig = which.endswith('T')
    w_, h_ = r * 1.25, r * (.62 if not trig else .8)
    ly.rr(c[0] - w_, c[1] - h_, c[0] + w_, c[1] + h_, h_ * .6, 255, outline=not trig, ow=max(2.0, r * .12))
    ly.text((c[0], c[1] + 1), side, r * (.95 if not trig else .95), 0 if trig else 255, stroke=0)


def g_stick(ly, c, r, dirs=''):
    ly.ell(c, r * .42, v=255, outline=True, ow=max(1.8, r * .1))
    ly.ell(c, r * .16, v=255)
    for d, (dx, dy) in {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}.items():
        p = (c[0] + dx * r * .78, c[1] + dy * r * .78)
        n = (-dy, dx)
        tri = [(p[0] + dx * r * .22, p[1] + dy * r * .22), (p[0] - dx * r * .14 + n[0] * r * .2, p[1] - dy * r * .14 + n[1] * r * .2),
               (p[0] - dx * r * .14 - n[0] * r * .2, p[1] - dy * r * .14 - n[1] * r * .2)]
        if d in dirs or dirs == 'all':
            ly.poly(tri, 255)
        else:
            ly.line(tri + [tri[0]], max(1.4, r * .07), 255)


def g_dpad(ly, c, r, dirs=''):
    t = r * .3
    pl = [(c[0] - t, c[1] - r), (c[0] + t, c[1] - r), (c[0] + t, c[1] - t), (c[0] + r, c[1] - t), (c[0] + r, c[1] + t), (c[0] + t, c[1] + t),
          (c[0] + t, c[1] + r), (c[0] - t, c[1] + r), (c[0] - t, c[1] + t), (c[0] - r, c[1] + t), (c[0] - r, c[1] - t), (c[0] - t, c[1] - t)]
    ly.line(pl + [pl[0]], max(1.6, r * .09), 255)
    for d, (dx, dy) in {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}.items():
        if d in dirs:
            p = (c[0] + dx * r * .62, c[1] + dy * r * .62)
            ly.ell(p, r * .2, v=255)


def g_key(ly, c, r, text, w=None):
    w = r * 1.5 if w is None else w
    ly.rr(c[0] - w / 2, c[1] - r * .62, c[0] + w / 2, c[1] + r * .62, r * .2, 255, outline=True, ow=max(1.8, r * .1))
    return text


def g_mouse(ly, c, r, which='L'):
    ly.rr(c[0] - r * .5, c[1] - r * .85, c[0] + r * .5, c[1] + r * .85, r * .45, 255, outline=True, ow=max(1.8, r * .1))
    ly.line([(c[0], c[1] - r * .85), (c[0], c[1] - r * .1)], max(1.4, r * .08), 255)
    ly.line([(c[0] - r * .5, c[1] - r * .1), (c[0] + r * .5, c[1] - r * .1)], max(1.4, r * .08), 255)
    if which == 'L':
        ly.poly([(c[0] - r * .5 + 2, c[1] - r * .1), (c[0], c[1] - r * .1), (c[0], c[1] - r * .85 + 3), (c[0] - r * .3, c[1] - r * .8)], 255)
    elif which == 'R':
        ly.poly([(c[0] + r * .5 - 2, c[1] - r * .1), (c[0], c[1] - r * .1), (c[0], c[1] - r * .85 + 3), (c[0] + r * .3, c[1] - r * .8)], 255)


def btn_w(kind, arg, r):
    """half-width of a button glyph."""
    if kind == 'shoulder':
        return r * 1.3
    if kind == 'key':
        return r * (.9 if len(arg) == 1 else (.55 + .42 * len(arg)))
    if kind == 'mouse':
        return r * .62
    return r


def draw_btn(cv, c, kind, arg='', r=17, k=1.0, col=None, text=None):
    """one button glyph as game UI: kind face|shoulder|stick|dpad|key|mouse. Returns its half-width."""
    col = WHITE * .92 if col is None else col
    wd = btn_w(kind, arg, r)
    bx = (c[0] - wd - 8, c[1] - r * 1.4, c[0] + wd + 8, c[1] + r * 1.4)
    ly = Lyr(bx)
    if kind == 'face':
        g_face(ly, c, r, arg)
    elif kind == 'shoulder':
        g_shoulder(ly, c, r, arg)
    elif kind == 'stick':
        g_stick(ly, c, r, arg)
    elif kind == 'dpad':
        g_dpad(ly, c, r, arg)
    elif kind == 'mouse':
        g_mouse(ly, c, r, arg)
    elif kind == 'key':
        g_key(ly, c, r, arg, w=wd * 2)
    cv.over(INK, blur(ly.m, 3) * 1.7, .8 * k, ly.off)
    cv.neonL(ly, col, core=1.0 * k, g1=(2, .4 * k), g2=None)
    if kind == 'key':
        ui.ntext(cv, (c[0], c[1] + 1), arg, int(r * (1.0 if len(arg) == 1 else .78)), col, stroke=2, white=.2, k=k, glow=False)
    return wd


def act_glyph(cv, c, name, r=14, k=1.0, col=None):
    """the action a prompt performs, as an icon (wordless): place / cancel / pick / cycle / pin / peek / undo / confirm."""
    col = WHITE * .92 if col is None else col
    ly = Lyr((c[0] - r * 1.5, c[1] - r * 1.5, c[0] + r * 1.5, c[1] + r * 1.5))
    if name == 'place':
        ly.poly(hy.hexpts(c, r * 1.0), 255, outline=255, ow=2)
        ly.poly(hy.hexpts(c, r * .98), 0)
        ly.line(hy.hexpts(c, r) + [hy.hexpts(c, r)[0]], 2.2, 255)
        ly.poly([(c[0] - r * .45, c[1] - r * .2), (c[0] + r * .45, c[1] - r * .2), (c[0], c[1] + r * .5)], 255)
    elif name == 'cancel':
        ly.line([(c[0] - r * .7, c[1] - r * .7), (c[0] + r * .7, c[1] + r * .7)], 3.2, 255)
        ly.line([(c[0] + r * .7, c[1] - r * .7), (c[0] - r * .7, c[1] + r * .7)], 3.2, 255)
    elif name == 'pick':
        ly.rr(c[0] - r * .6, c[1] - r * .85, c[0] + r * .6, c[1] + r * .85, r * .15, 255, outline=True, ow=2.2)
        ly.poly([(c[0], c[1] - r * 1.25), (c[0] - r * .35, c[1] - r * .9), (c[0] + r * .35, c[1] - r * .9)], 255)
    elif name == 'cycle':
        ly.poly([(c[0] - r * 1.0, c[1]), (c[0] - r * .35, c[1] - r * .55), (c[0] - r * .35, c[1] + r * .55)], 255)
        ly.poly([(c[0] + r * 1.0, c[1]), (c[0] + r * .35, c[1] - r * .55), (c[0] + r * .35, c[1] + r * .55)], 255)
    elif name == 'peek':      # what-if: an eye over a tally
        g_eye(ly, c, r * .95)
    elif name == 'undo':
        ly.arc((c[0], c[1]), r * .7, 40, 330, 3.0)
        ly.poly([(c[0] + r * .2, c[1] - r * 1.15), (c[0] + r * .2, c[1] - r * .25), (c[0] + r * 1.0, c[1] - r * .72)], 255)
    elif name == 'forecast':  # to the forecast: the tally row
        for i in range(3):
            ly.ell((c[0] + (i - 1) * r * .75, c[1]), r * .26, v=255, outline=(i != 1), ow=2)
    elif name == 'pin':
        ly.poly([(c[0], c[1] + r * 1.0), (c[0] - r * .35, c[1] - r * .2), (c[0] + r * .35, c[1] - r * .2)], 255)
        ly.ell((c[0], c[1] - r * .55), r * .45, v=255)
    elif name == 'hold':
        ly.rr(c[0] - r * .7, c[1] - r * .8, c[0] - r * .15, c[1] + r * .8, r * .1, 255)
        ly.rr(c[0] + r * .15, c[1] - r * .8, c[0] + r * .7, c[1] + r * .8, r * .1, 255)
    elif name == 'wheel':
        ly.line(ring_pts(c, r * .9, 40, k=1.0), 2.4, 255)
        for i in range(5):
            a = math.radians(-90 + i * 72)
            ly.ell((c[0] + r * .9 * math.cos(a), c[1] + r * .9 * math.sin(a)), r * .2, v=255)
    cv.over(INK, blur(ly.m, 3) * 1.7, .8 * k, ly.off)
    cv.neonL(ly, col, core=1.0 * k, g1=(2, .4 * k), g2=None)


def prompt_row(cv, c, items, k=1.0, r=22, gap=26, align='c'):
    """a pill of [button glyph(s)] -> action icon pairs. items: list of (buttons, action); buttons = (kind, arg) or a list of
    them shown together (a pair such as LB RB)."""
    laid = []
    for btns, act in items:
        if isinstance(btns, tuple):
            btns = [btns]
        w_ = sum(2 * btn_w(b[0], b[1], r) + 10 for b in btns) + 2.4 * r
        laid.append((btns, act, w_))
    tot = sum(w for _, _, w in laid) + gap * (len(laid) - 1) + 36
    x = c[0] - tot / 2 if align == 'c' else c[0]
    _pill(cv, x, c[1] - r - 12, x + tot, c[1] + r + 12, k=k)
    x += 18
    for btns, act, w_ in laid:
        xx = x
        for b in btns:
            wd = btn_w(b[0], b[1], r)
            draw_btn(cv, (xx + wd, c[1]), b[0], b[1], r=r, k=k)
            xx += 2 * wd + 10
        act_glyph(cv, (xx + r * .9, c[1]), act, r=r * .9, k=k)
        x += w_ + gap
    return tot


# ------------------------------------------------------------------ annotation layer (designer-facing, not game UI)
class Ann:
    def __init__(self):
        self.items = []

    def note(self, text, xy, to=None, side=None, size=19, elbow=None):
        """a dark chip with text at xy (centre); to = the point the leader ends on (a dot)."""
        self.items.append(('note', text, np.array(xy, float), None if to is None else np.array(to, float), size, elbow))
        return self

    def badge(self, n, xy, r=17):
        self.items.append(('badge', str(n), np.array(xy, float), r))
        return self

    def title(self, text, sub=''):
        self.items.append(('title', text, sub))
        return self

    def circle(self, xy, r, dash=True):
        self.items.append(('circle', np.array(xy, float), r, dash))
        return self

    def box(self, x0, y0, x1, y1, dash=True):
        self.items.append(('box', (x0, y0, x1, y1), dash))
        return self

    def draw(self, im):
        im = im.convert('RGBA')
        ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        fnt = lambda s: font(s, False, 560, 78)
        for it in self.items:
            if it[0] == 'circle':
                _, c, r, dash = it
                if dash:
                    for a in range(0, 360, 14):
                        d.arc((c[0] - r, c[1] - r, c[0] + r, c[1] + r), a, a + 8, fill=(255, 255, 255, 215), width=2)
                else:
                    d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), outline=(255, 255, 255, 215), width=2)
            elif it[0] == 'box':
                _, (x0, y0, x1, y1), dash = it
                pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
                for a, b in zip(pts[:-1], pts[1:]):
                    L = math.hypot(b[0] - a[0], b[1] - a[1])
                    u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
                    t = 0
                    while t < L:
                        t2 = min(t + 8, L)
                        d.line([(a[0] + u[0] * t, a[1] + u[1] * t), (a[0] + u[0] * t2, a[1] + u[1] * t2)], fill=(255, 255, 255, 215), width=2)
                        t += 14
        for it in self.items:
            if it[0] == 'note':
                _, text, xy, to, size, elbow = it
                f = fnt(size)
                lines = text.split('\n')
                ws = [d.textlength(l, font=f) for l in lines]
                w_, h_ = max(ws) + 22, len(lines) * (size + 4) + 14
                x0, y0 = xy[0] - w_ / 2, xy[1] - h_ / 2
                x0 = min(max(x0, 8), W - 8 - w_)
                y0 = min(max(y0, 8), H - 8 - h_)
                if to is not None:
                    # leader from the chip edge nearest the target
                    cx = min(max(to[0], x0 + 8), x0 + w_ - 8)
                    cy = min(max(to[1], y0 + 6), y0 + h_ - 6)
                    if x0 <= to[0] <= x0 + w_:
                        cy = y0 if to[1] < y0 else y0 + h_
                    else:
                        cx = x0 if to[0] < x0 else x0 + w_
                    pts = [(cx, cy)] + ([tuple(elbow)] if elbow is not None else []) + [tuple(to)]
                    d.line(pts, fill=(10, 10, 28, 230), width=5)
                    d.line(pts, fill=(246, 241, 228, 245), width=2)
                    d.ellipse((to[0] - 5, to[1] - 5, to[0] + 5, to[1] + 5), fill=(246, 241, 228, 255), outline=(10, 10, 28, 255), width=2)
                d.rounded_rectangle((x0, y0, x0 + w_, y0 + h_), 9, fill=(10, 12, 30, 226), outline=(246, 241, 228, 200), width=2)
                for i, l in enumerate(lines):
                    d.text((x0 + 11, y0 + 8 + i * (size + 4)), l, font=f, fill=(240, 243, 255, 255))
            elif it[0] == 'badge':
                _, t, xy, r = it
                d.ellipse((xy[0] - r, xy[1] - r, xy[0] + r, xy[1] + r), fill=(246, 241, 228, 255), outline=(10, 10, 28, 255), width=3)
                d.text((xy[0], xy[1] + 1), t, font=fnt(int(r * 1.25)), fill=(10, 10, 28, 255), anchor='mm')
            elif it[0] == 'title':
                _, text, sub = it
                f1, f2 = fnt(26), fnt(18)
                w1 = d.textlength(text, font=f1)
                w2 = d.textlength(sub, font=f2) if sub else 0
                ww = max(w1, w2) + 34
                x0 = W / 2 - ww / 2
                hh = 46 if not sub else 66
                d.rounded_rectangle((x0, 10, x0 + ww, 10 + hh), 10, fill=(246, 241, 228, 240), outline=(10, 10, 28, 255), width=2)
                d.text((W / 2, 10 + (23 if not sub else 22)), text, font=f1, fill=(10, 10, 28, 255), anchor='mm')
                if sub:
                    d.text((W / 2, 10 + 49), sub, font=f2, fill=(60, 58, 80, 255), anchor='mm')
        return Image.alpha_composite(im, ov).convert('RGB')


def emit(name, cv, ann=None, post=True, vig=.38, scan=.07, fringe=1.5, quality=93, folder=None):
    """save the finished frame: frames/NAME.jpg = annotated, frames/clean/NAME.jpg = game UI only."""
    a = finish(cv, vig=vig, scan=scan, fringe=fringe) if post else cv.out()
    im = to_img(a)
    cl = (CLD if folder is None else folder + 'clean/')
    os.makedirs(cl, exist_ok=True)
    im.save(cl + name + '.jpg', quality=quality, subsampling=0)
    if ann is not None:
        im = ann.draw(im)
    fd = FRD if folder is None else folder
    im.save(fd + name + '.jpg', quality=quality, subsampling=0)
    print('saved', name)
    return im


# ------------------------------------------------------------------ common HUD / hand
def std_hud(cv, **kw):
    hy.hud(cv, kw.get('home', 44), 50, 80, 8, 0)


def std_hand(cv, cards=None, y=992, lift=None, skip=None, k=1.0, spread=108):
    hy.hand(cv, cards or HAND, y=y, lift=lift, skip=skip, k=k, spread=spread)
    return card_centres(cards or HAND, y, lift, spread)


def card_centres(cards, y=992, lift=None, spread=108, sc=.9):
    n = len(cards)
    x0 = W / 2 - (n - 1) / 2 * spread
    out = []
    for i in range(n):
        t = i - (n - 1) / 2
        out.append((x0 + i * spread, y + abs(t) ** 1.6 * 8 - (34 if lift == i else 0)))
    return out


TIERS = hy.TIERS
K = 0.643


def hand_custom(cv, cards=None, y=992, lifts=None, lime=None, ks=None, spread=108, sc=.9, skip=(), glow=None):
    """the hand with per-card lift (px), lime focus (index) and per-card k. glow: {idx: typ} adds a type-hue underlight."""
    cards = cards or HAND
    lifts = lifts or {}
    ks = ks or {}
    glow = glow or {}
    n = len(cards)
    x0 = W / 2 - (n - 1) / 2 * spread
    out = []
    for i, (verb, typ) in enumerate(cards):
        t = i - (n - 1) / 2
        yy = y + abs(t) ** 1.6 * 8 - lifts.get(i, 0)
        c = (x0 + i * spread, yy)
        out.append(c)
        if i in skip:
            continue
        if i in glow:
            gl = Lyr((c[0] - 70, c[1] - 90, c[0] + 70, c[1] + 90))
            gl.rr(c[0] - 50, c[1] - 66, c[0] + 50, c[1] + 66, 14, 255)
            cv.add(TYPE_COL[glow[i]], blur(gl.m, 14), .55, gl.off)
        hy.vcard(cv, c, verb, typ, -t * 3.4, lime=(lime == i), k=ks.get(i, 1.0), sc=sc)
    return out


def home_range(cv, home, hp=44, hp_max=50, mid=6, worst=12, k=1.0):
    """HOME ring range preview: the likely loss (orange, drawn by home_deck preview) plus the worst case in BREACHED red."""
    R = 74
    ly = Lyr(pbox([(home[0] - R - 20, home[1] - R * K - 20), (home[0] + R + 20, home[1] + R * K + 20)], 10))
    for i in range(hp - worst, hp - mid):
        ang = -90 + i * 360 / hp_max
        a0 = math.radians(ang)
        p0 = (home[0] + (R - 7) * math.cos(a0), home[1] + (R - 7) * K * math.sin(a0))
        p1 = (home[0] + (R + 5) * math.cos(a0), home[1] + (R + 5) * K * math.sin(a0))
        ly.line([p0, p1], 3, 255)
    cv.neonL(ly, TIER['BREACHED'], core=.9 * k, g1=(3, .7 * k), g2=(10, .4 * k))
