"""raid_d: set 8, the set 7 raid look (direction C) re-staged on the dock rules, plus the sheet.

    python raid_d.py [plan place shop playback site siteplace sheet]      -> raid_v3/set8/r8_*.png, r8_sheet.jpg
    (set 8 as first drawn on the v40 sockets: raid_d_v40.py, the same pieces, writes raid_v3/set8/v40/)

v42 (port-campaign-b 6a99f5c0: scripts/core/raid_dock.gd with slotRule 1, slotShare 0, dockMax / dockMaxHq 0 from
content/config/b_campaign_config.tres; scripts/ui/raid/b_raid_place_model.gd):
- the operative is a fixed post (its R3 class beacon) on its site; in the PURGE the whole crew is recalled to HQ: the first on
  the Safehouse, the rest on the nearest legal cells beside it (dock_rules.beacons_purge) - unchanged from v40;
- each weapon is its own piece docked on a STREET SLOT (route slot): every street (route) cell within dockRadius 3 of the post
  (dockRadiusHq 6 in the PURGE), no cap; ONE PIECE PER SLOT: a weapon, or a street device (barricade, mine, tar, shock fence,
  gate; slotShare 0) - a slot holding a barricade refuses a weapon and a weapon's slot refuses a device.
The slots on each plate come from dock_rules.slots_of run on the plate's own routes (not hand placed).

Pieces (all on the set 7 language):
- street slot = system (cyan) inset outline of the street cell on the ground: faint dashed at rest; solid, bright and lightly
  filled while a weapon card is held and the slot takes it (drawn over the dimmed posts);
- docked weapon = the SAME gear-tag sticker as its CREW card, stuck over a small pad in the owner's role colour, in the street;
- tether = a thin dashed pencil line in the owner's role colour, slot pad -> beacon pad, faded under the route pencil;
- refusal = a red badge glyph, no words (taken: a slot with a dot; device here: the device's own glyph; too far: an arrow across
  the reach line).
"""
import json, math, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import raid_c as C
import raid_v3_city as V
import raid_kit as K
import low_text as LT
import raid_icons as RI
import dock_rules as DR
from raid_kit import (Wax, PEN_Y, PEN_R, SL, IR, TR, S, text, Layer, comp, INK, PAPER, CYAN, TEXT_HI, TEXT_MID, ANTON, MONO,
                      W, H, SS, F_all, glass, stick, S_GAIN, S_HARM, S_HI, S_MID)

G = V.G
OUT = V.OUT + 'set8/'
GOLD = C.GOLD
RED_H = C.RED_H
REF = (226, 34, 48)
say, T = LT.say, LT.T
ORDER = ['KAI', 'VEX', 'MOTH', 'RUNE']

# ------------------------------------------------------------------ the two raids, from the rules
PATHS = [V.RA + [V.SAFE], V.RB + [V.SAFE]]                    # the PURGE at HQ (set 7's Safehouse raid)
P_LEGAL = V.legal_cells(V.RA + V.RB, {V.BARR, V.SAFE})
P_BEACON = DR.beacons_purge(ORDER, V.SAFE, P_LEGAL)          # KAI c7 (on the Safehouse), VEX e5, MOTH a7, RUNE e7
P_SLOT_OF = {o: DR.slots_of(P_BEACON[o], PATHS, V.SAFE, purge=True)[0] for o in ORDER}
P_SLOT = P_SLOT_OF['KAI']                                     # every route cell off the Safehouse: radius 6 covers the district
assert all(v == P_SLOT for v in P_SLOT_OF.values())
P_DEV = {V.BARR: 'BARRICADE'}                                 # the wall on b4 (a street device: it holds its slot)
SPATHS = [V.SA + [V.SITE], V.SB + [V.SITE], V.SC + [V.SITE]]
S_BEACON = {'KAI': V.SITE, 'VEX': V.S_VEX}                   # KAI holds the post on B2 (b6); VEX from C2 on a7
S_SUP = {'KAI': False, 'VEX': True}
S_SLOT_OF = {o: DR.slots_of(S_BEACON[o], SPATHS, V.SITE, supporter=S_SUP[o])[0] for o in S_BEACON}
S_SLOT = sorted(set(S_SLOT_OF['KAI']) | set(S_SLOT_OF['VEX']), key=DR.cid)   # the shared pool (first come)
S_DEV = {}

# the docks per plate: oid -> slot cell (None = card not docked)
P_REST = {'KAI': (3, 6), 'MOTH': (1, 6), 'VEX': None, 'RUNE': None}          # KAI SMG on d7, MOTH JAMMER on b7
P_PLAY = {'KAI': (3, 6), 'MOTH': (1, 6), 'VEX': (1, 0), 'RUNE': (3, 5)}      # + VEX RAIL on b1, RUNE SHOTGUN on d6
S_REST = {'KAI': (1, 4), 'VEX': (1, 6)}                                      # KAI SMG on b5, VEX RAIL on b7
HOVER_P = (3, 5)                                                              # RUNE's SHOTGUN held over d6
HOVER_S = (4, 5)                                                              # VEX's RAIL held over e6: KAI's slot, too far for VEX


def wpn_at(docks, but=None):
    return {c: o for o, c in docks.items() if c is not None and o != but}


def why_p(oid, cell, docks):
    """v42 refusal of oid's held weapon over cell in the PURGE (its own slot counts as free: the card was lifted)"""
    return DR.why42(cell, P_BEACON[oid], PATHS, V.SAFE, wpn_at(docks, oid), P_DEV, purge=True)


def why_s(oid, cell, docks):
    return DR.why42(cell, S_BEACON[oid], SPATHS, V.SITE, wpn_at(docks, oid), S_DEV, supporter=S_SUP[oid])


for _d in (P_REST, P_PLAY):                                   # every dock drawn is legal by the rules
    for _o, _c in _d.items():
        assert _c is None or why_p(_o, _c, _d) is None, (_o, _c, why_p(_o, _c, _d))
for _o, _c in S_REST.items():
    assert why_s(_o, _c, S_REST) is None, (_o, _c)
assert why_p('RUNE', HOVER_P, P_REST) is None
assert why_p('RUNE', V.BARR, P_REST) == 'slot_piece'
assert why_s('VEX', HOVER_S, S_REST) == 'too_far' and HOVER_S in S_SLOT_OF['KAI']


def wname(oid):
    return K.OPS[oid]['wpn']


# ------------------------------------------------------------------ socket, pad, tether, refusal
SLOT_IN = 0.13                                                # the slot outline's inset in the cell (clear of the grid line)
SLOT_REST = (96, 214, 246)


def _slot_quad(cell, inset=SLOT_IN):
    q = G.quad(cell[0], cell[1], inset)
    return q + [q[0]]


def slots(img, cells, lit=(), on_glass=False, rest_a=0.74):
    """system: the street slots on the ground, as an inset outline of the street cell (a tile set in the street, not the grid).
    rest = thin dashed, faint; `lit` = the held weapon may dock there now: solid bright outline over an ink edge, light fill,
    a glow (drawn over the dimmed posts with on_glass)"""
    R = Layer()
    L = Layer(); d = L.d
    for cell in cells:
        q = _slot_quad(cell)
        if cell in lit:
            P = [(S(x), S(y)) for x, y in q]
            d.polygon(P[:-1], fill=CYAN + (40,))
            d.line(P, fill=INK + (190,), width=S(6.0), joint='curve')
            d.line(P, fill=CYAN + (255,), width=S(3.0), joint='curve')
        elif not on_glass:
            IR.dash_poly(R.d, q, SLOT_REST, 2.0, on=8, off=6)
    if not on_glass:
        R.im.putalpha(R.im.split()[3].point(lambda v: int(v * rest_a)))
        V.masked_ground(img, R, ghost=0.6)
    if on_glass:                                              # while a card is held the lit slots are an affordance: over the posts
        comp(img, _wrap(L.im.filter(ImageFilter.GaussianBlur(S(4)))))
        comp(img, L)
        return
    if lit:
        gl = L.im.filter(ImageFilter.GaussianBlur(S(4)))
        V.masked_ground(img, _wrap(gl), ghost=0.6)
    V.masked_ground(img, L, ghost=0.6)


def _wrap(im):
    L = Layer(); L.im = im; L.d = ImageDraw.Draw(im); return L


def radius_limits(slots, paths, hq):
    """B-104 #3: a post's dock radius is drawn only where it limits something: some route (street) cell is not among its
    slots.  In the PURGE (radius 6) every route cell is a slot for every post, so no ring is drawn there."""
    return set(slots) != set(DR.road(paths, hq))


def dock_radius(img, oid, bcell, radius=None):
    """the dock radius while a card is held: the Chebyshev square round the beacon, a dashed line in the owner's colour on
    the ground over an ink edge, clipped to the district"""
    cells = set(V.cheb(*bcell, DR.DOCK42['radius'] if radius is None else radius))
    top = K.OPS[oid]['col'][0]
    L = Layer(); d = L.d
    for (c, r) in cells:
        for dc, dr, a, b in ((0, -1, (c, r), (c + 1, r)), (0, 1, (c, r + 1), (c + 1, r + 1)), (-1, 0, (c, r), (c, r + 1)),
                             (1, 0, (c + 1, r), (c + 1, r + 1))):
            if (c + dc, r + dr) not in cells:
                d.line([tuple(S(v) for v in G.sp(*a)), tuple(S(v) for v in G.sp(*b))], fill=INK + (150,), width=S(5))
                IR.dash_poly(d, [G.sp(*a), G.sp(*b)], top, 3.0, on=9, off=6)
    V.masked_ground(img, L, ghost=0.7)


def pad(img, oid, cell):
    """the weapon's stand on its socket: a small pad in the owner's role colour"""
    top, bot = K.OPS[oid]['col']
    x, y = G.cc(*cell)
    rx, ry = 24, 15
    L = Layer(); d = L.d
    d.ellipse([S(x - rx - 3), S(y - ry - 2), S(x + rx + 3), S(y + ry + 2)], fill=INK + (210,))
    d.ellipse([S(x - rx), S(y - ry), S(x + rx), S(y + ry)], fill=bot + (170,), outline=top + (255,), width=S(2.2))
    comp(img, L)


TAG_DY, TAG_S = 20, 0.56
DIM = 0.42                                                    # posts while a card is held: the sockets under the cones read


def tag_at(cell):
    x, y = G.cc(*cell)
    return x, y - TAG_DY


def docked(img, oid, cell, stars=None):
    """the docked weapon: its CREW gear tag, stuck over its pad (the route pencil runs under it, as under the Safehouse)"""
    x, y = tag_at(cell)
    stick(img, C.wpn_c(wname(oid), stars or K.OPS[oid]['stars']), x, y, -4, scale=TAG_S)


def tether(img, oid, cell, bcell, bow=0.16, seed=0, lift_b=0.0):
    """a thin dashed pencil line in the owner's role colour from the socket pad to the beacon pad, bowed, faded"""
    top = K.OPS[oid]['col'][0]
    x0, y0 = G.cc(*cell)
    x1, y1 = G.cc(bcell[0], bcell[1], lift=lift_b)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy) or 1
    cx, cy = mx - dy / n * n * bow, my + dx / n * n * bow
    pts = [((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1)
           for t in np.linspace(0, 1, 80)]
    lens = np.cumsum([0] + [math.dist(a, b) for a, b in zip(pts, pts[1:])])
    tot = lens[-1]
    p = Wax(top, 300 + seed)
    dash, gap, t0 = 14, 9, 26
    while t0 < tot - 30:
        seg = [pt for pt, l in zip(pts, lens) if t0 <= l <= t0 + dash]
        if len(seg) >= 2:
            p.stroke(seg, 3.2, taper=False)
        t0 += dash + gap
    tmp = Image.new('RGBA', img.size, (0, 0, 0, 0))
    p.ink_ss(tmp)
    tmp.putalpha(tmp.split()[3].point(lambda v: int(v * 0.82)))
    img.alpha_composite(tmp)
    L = Layer(); d = L.d                                      # the knot at the beacon end
    d.ellipse([S(x1 - 6), S(y1 - 4), S(x1 + 6), S(y1 + 4)], fill=top + (230,), outline=INK + (230,), width=S(1.5))
    comp(img, L)


def refuse_badge(img, kind, x, y, r=17):
    """a refusal as a glyph: red disc, white mark.  taken = an occupied slot (the slot's tile + a dot); 'dev:<GLYPH>' = the slot
    holds that street device (its own glyph: "<device> here"); far = an arrow across the dashed reach line"""
    L = Layer(); d = L.d
    d.ellipse([S(x - r - 2.5), S(y - r - 2.5), S(x + r + 2.5), S(y + r + 2.5)], fill=INK + (255,))
    d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=REF + (255,), outline=(255, 240, 240, 255), width=S(1.6))
    wc = (255, 255, 255, 255)
    if kind == 'taken':                                       # the slot tile (a diamond, as the cell reads on the ground) + a dot
        h_ = r * 0.66
        P = [(S(x), S(y - h_)), (S(x + h_), S(y)), (S(x), S(y + h_)), (S(x - h_), S(y)), (S(x), S(y - h_))]
        d.line(P, fill=wc, width=S(2.4), joint='curve')
        d.ellipse([S(x - r * 0.22), S(y - r * 0.22), S(x + r * 0.22), S(y + r * 0.22)], fill=wc)
    elif kind.startswith('dev:'):                             # B-104 #5: the device's own small sticker, not a red disc
        dev_badge(img, kind[4:], x, y, r)
        return
    else:
        lx = x - r * 0.05
        for k in range(3):
            y0 = y - r * 0.66 + k * r * 0.5
            d.line([(S(lx), S(y0)), (S(lx), S(y0 + r * 0.3))], fill=wc, width=S(2.4))
        d.line([(S(x - r * 0.62), S(y + r * 0.1)), (S(x + r * 0.5), S(y + r * 0.1))], fill=wc, width=S(2.6))
        d.polygon([(S(x + r * 0.68), S(y + r * 0.1)), (S(x + r * 0.34), S(y - r * 0.18)), (S(x + r * 0.34), S(y + r * 0.38))], fill=wc)
    comp(img, L)


DEV_COL = dict(K.DEV, SHOCK=((150, 255, 236), (40, 190, 200)), GATE=((255, 120, 150), (200, 40, 80)))
DEV_GLYPH = {'BARRICADE', 'MINE', 'SENTRY'}                   # in raid_icons; TAR, SHOCK (fence), GATE are drawn here (badge size only)


def _dev_mark(d, kind, x, y, s, col):
    """TAR / SHOCK (fence) / GATE at badge size (s = half the glyph box), white with an ink edge, in screen px"""
    def ln(pts, w):
        P = [(S(a), S(b)) for a, b in pts]
        d.line(P, fill=INK + (255,), width=S(w + 2.2), joint='curve')
        d.line(P, fill=col, width=S(w), joint='curve')
    if kind == 'TAR':                                         # a puddle with a drip
        for (cx, cy, rx, ry), f in (((x, y + s * 0.35, s * 0.95, s * 0.42), INK + (255,)), ((x, y + s * 0.35, s * 0.8, s * 0.3), col)):
            d.ellipse([S(cx - rx), S(cy - ry), S(cx + rx), S(cy + ry)], fill=f)
        d.ellipse([S(x - s * 0.3), S(y - s * 0.75), S(x + s * 0.3), S(y - s * 0.05)], fill=col, outline=INK + (255,), width=S(1.2))
    elif kind == 'SHOCK':                                     # two posts, a bolt between them
        ln([(x - s * 0.8, y - s * 0.8), (x - s * 0.8, y + s * 0.8)], 2.4)
        ln([(x + s * 0.8, y - s * 0.8), (x + s * 0.8, y + s * 0.8)], 2.4)
        ln([(x - s * 0.55, y - s * 0.35), (x + s * 0.1, y - s * 0.05), (x - s * 0.1, y + s * 0.15), (x + s * 0.55, y + s * 0.45)], 2.0)
    elif kind == 'GATE':                                      # a boom barrier: post + striped arm
        ln([(x - s * 0.75, y - s * 0.2), (x - s * 0.75, y + s * 0.85)], 2.6)
        ln([(x - s * 0.75, y - s * 0.2), (x + s * 0.9, y - s * 0.2)], 3.0)
        for k in range(3):
            xx = x - s * 0.35 + k * s * 0.45
            d.line([(S(xx), S(y - s * 0.32)), (S(xx + s * 0.14), S(y - s * 0.08))], fill=REF + (255,), width=S(2.0))


def dev_badge(img, kind, x, y, r=17):
    """B-104 #5 "device here": the slot's own device as a small sticker (its vinyl colours, white glyph, die-cut edge), with a
    small red no-mark on its corner: the player sees WHAT blocks the slot, not just that something does"""
    top, bot = DEV_COL[kind]
    w, h = r * 2.5, r * 2.1
    L = Layer(); d = L.d
    x0, y0, x1, y1 = x - w / 2, y - h / 2, x + w / 2, y + h / 2
    d.rounded_rectangle([S(x0 - 4), S(y0 - 4), S(x1 + 4), S(y1 + 4)], radius=S(8), fill=INK + (255,))
    d.rounded_rectangle([S(x0 - 2.2), S(y0 - 2.2), S(x1 + 2.2), S(y1 + 2.2)], radius=S(7), fill=(250, 250, 252, 255))
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], radius=S(6), fill=bot + (255,))
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y0 + h * 0.5)], radius=S(6), fill=top + (255,))
    d.rectangle([S(x0), S(y0 + h * 0.3), S(x1), S(y0 + h * 0.5)], fill=top + (255,))
    if kind == 'BARRICADE':                                   # the hazard band, the barricade's identity
        for k in range(6):
            xx = x0 + 3 + k * w / 5.5
            d.polygon([(S(xx), S(y1 - 5)), (S(xx + 4), S(y1 - 5)), (S(xx + 1), S(y1)), (S(xx - 3), S(y1))], fill=INK + (255,))
    comp(img, L)
    G2 = Layer()
    if kind in DEV_GLYPH:
        C.gpaste(G2.im, kind, x, y - (2 if kind == 'BARRICADE' else 0), r * 1.35, (255, 255, 255))
    else:
        _dev_mark(G2.d, kind, x, y, r * 0.62, (255, 255, 255, 255))
    comp(img, G2)
    N = Layer(); d = N.d                                      # the no-mark, top right corner
    nx, ny, nr = x1 + 1, y0 - 1, r * 0.5
    d.ellipse([S(nx - nr - 2), S(ny - nr - 2), S(nx + nr + 2), S(ny + nr + 2)], fill=INK + (255,))
    d.ellipse([S(nx - nr), S(ny - nr), S(nx + nr), S(ny + nr)], fill=REF + (255,), outline=(255, 240, 240, 255), width=S(1.4))
    d.line([(S(nx - nr * 0.55), S(ny + nr * 0.55)), (S(nx + nr * 0.55), S(ny - nr * 0.55))], fill=(255, 255, 255, 255), width=S(2.4))
    comp(img, N)


SUP_AT = (-64, 46)                                            # the chip under the supporter's docked tag
SUP_HELD = (0, 70)                                            # ... and under the held card
SUP_PCT = DR.DOCK42.get('sup_pct', 15)                        # dockSupPct 15, dockSupKeep 1 (b_campaign_config @ 6a99f5c0)


def sup_chip(img, oid, x, y, s=1.0):
    """B-104 #4 supporter share, no word (the word is pending): an ink pill in the supporter's colour with a pie (the 15 %
    slice filled), the number, and a link (its guns stay with it, dockSupKeep 1)"""
    top, bot = K.OPS[oid]['col']
    F = F_all()
    L = Layer(); d = L.d
    w, h = 132 * s, 34 * s
    x0, y0 = x - w / 2, y - h / 2
    d.rounded_rectangle([S(x0 - 2.5), S(y0 - 2.5), S(x0 + w + 2.5), S(y0 + h + 2.5)], radius=S(h / 2 + 2), fill=(250, 250, 252, 255))
    d.rounded_rectangle([S(x0), S(y0), S(x0 + w), S(y0 + h)], radius=S(h / 2), fill=INK + (245,), outline=top + (255,), width=S(2))
    pc, pr_ = (x0 + h * 0.55, y), h * 0.33                    # the pie: full disc outline, the share filled
    d.ellipse([S(pc[0] - pr_), S(pc[1] - pr_), S(pc[0] + pr_), S(pc[1] + pr_)], fill=(70, 70, 86, 255), outline=(255, 255, 255, 255), width=S(1.6))
    d.pieslice([S(pc[0] - pr_), S(pc[1] - pr_), S(pc[0] + pr_), S(pc[1] + pr_)], -90, -90 + 360 * SUP_PCT / 100, fill=top + (255,))
    text(d, (pc[0] + pr_ + 27 * s, y - 1), '%d%%' % SUP_PCT, F['a40'] if s > 1.2 else F.get('a30', F['a40']), TEXT_HI + (255,), stroke=0)
    lx, ly, lr = x0 + w - h * 0.55, y, h * 0.18               # the link: two interlocked rings
    for ox in (-lr * 0.75, lr * 0.75):
        d.ellipse([S(lx + ox - lr), S(ly - lr * 0.75), S(lx + ox + lr), S(ly + lr * 0.75)], outline=(255, 255, 255, 255), width=S(1.8))
    comp(img, L)
    say('%d%%' % SUP_PCT)


# ------------------------------------------------------------------ beacon (set 7's, with a lifted base for a post on a sticker)
def beacon(img, oid, c, r, lift0=0.0, alpha=1.0, height=8.5):
    """V.beacon with its pad lifted by lift0 BU: a post on the Safehouse / the site sticker stands on the sticker's roof"""
    if lift0 == 0.0:
        return V.beacon(img, oid, c, r, alpha, height)
    g0 = G.cc
    try:
        G.cc = lambda cc, rr, lift=0.0: g0(cc, rr, lift + lift0)
        return V.beacon(img, oid, c, r, alpha, height)
    finally:
        G.cc = g0


# ------------------------------------------------------------------ CREW: the full roster, each operative with its weapon card
def crew8(img, docks, held=None, away=None, kills=None, stars=None, merge=False):
    """option B roster.  The operative is always posted (its beacon), so it has no tick of its own; its weapon card does:
    docked = flat, with a pencil tick and a small socket mark; not docked = the card's corner peels (bible 2.10: the focus
    curl, 'pick me up'); held = the liner outline of the card"""
    def fn(Lm):
        py, pr = Wax(PEN_Y, 91), Wax(PEN_R, 92)
        for oid, (x, y, ang) in K.CREW_POS.items():
            o = K.OPS[oid]
            gone = bool(away and oid in away)
            stick(Lm, C.op_c(oid, grey=gone), x, y, ang)
            say(oid)
            wx, wy, wa = x + K.WPN_OFF[0], y + K.WPN_OFF[1], K.WPN_OFF[2]
            st = (stars or {}).get(oid, o['stars'])
            if oid == held:
                K.liner(Lm, C.wpn_c(o['wpn'], st), wx, wy, wa, 0.82)
            else:
                is_d = (not gone) and docks.get(oid) is not None
                stick(Lm, C.wpn_c(o['wpn'], st, curl=None if (is_d or gone) else 0.22, grey=gone), wx, wy, wa, scale=0.82)
                if is_d:                                      # tick + a pencil slot tile (the street cell), under the card's right end
                    tx, ty = wx + 44, wy + 52
                    py.tick(tx - 14, ty, 13, 6)
                    cx_, cy_ = tx + 26, ty - 2
                    py.stroke(py.wobble([(cx_, cy_ - 9), (cx_ + 14, cy_), (cx_, cy_ + 9), (cx_ - 14, cy_), (cx_, cy_ - 9)], 0.4), 4.2, taper=False)
            if gone:
                pr.text(away[oid], x - 4, y + 106, 34, angle=-6); say(away[oid])
            if kills and oid in kills:
                py.x(x - 30, y + 106, 12, 6); py.text(str(kills[oid]), x + 10, y + 108, 40, angle=-6); say(str(kills[oid]))
        if merge:
            p = Wax(PEN_Y, 7)
            K.pen_star(p, 250, 742, 14); p.text('+', 280, 744, 34); K.pen_star(p, 310, 742, 14)
            p.arrow([(336, 744), (356, 742), (378, 743)], width=5, head=10)
            K.pen_star(p, 404, 742, 14); K.pen_star(p, 436, 740, 14)
            p.arrow([(534, 428), (546, 452), (534, 474)], width=5, head=12)
            p.ink_ss(Lm)
        py.ink_ss(Lm); pr.ink_ss(Lm)
        if merge:
            sx, sy, sa = K.CREW_POS['RUNE']
            stick(Lm, C.wpn_c('SHOTGUN', 1, cost=3, curl=0.16), sx + K.WPN_OFF[0] - 8, sy + K.WPN_OFF[1] - 58, 3, scale=0.84, lift=0.7)
    V.ui(img, fn, (0, 0))


def left8(img, core=8, lose=0, rnd=1, rmax=4, credits=7, cost=0, undo=True, **crew):
    LT.core_lt(img, core, lose)
    LT.rows_lt(img, rnd, rmax, credits, cost)
    crew8(img, **crew)
    if undo:
        LT.undo_lt(img)


def strip8(img, items, box=(560, 956, 1360, 1008)):
    """C.strip_c plus one kind: ('refuse', kind) = the refusal badge"""
    out = []
    for it in items:
        if it[0] == 'refuse':
            out.append(('_gap', it[1]))
        else:
            out.append(it)
    marks = []
    orig = C.strip_c

    # measure + draw with C.strip_c, reserving 40 px for each badge via a blank 'glyph' slot
    items2 = [('glyph', 'tab', (0, 0, 0), 32) if it[0] == '_gap' else it for it in out]
    # draw the strip with a transparent placeholder glyph, then the badge on top at the same x
    x0, y0, x1, y1 = box
    ym = (y0 + y1) / 2
    L = Layer(); d = L.d
    wdt = 0
    f = TR.font(ANTON, 30)
    for it in items2:
        k = it[0]
        wdt += {'chip': 36, 'ico': 38, 'sep': 26, 'unit': 36}.get(k, 0)
        if k == 'txt':
            wdt += d.textlength(it[1], font=f) / SS + 12
        elif k == 'glyph':
            wdt += (it[3] if len(it) > 3 else 32) + 8
        elif k == 'ticks':
            wdt += it[2] * 14 + 10
        elif k == 'stars':
            wdt += it[1] * 24 + 4
    cx = (x0 + x1) / 2
    bx0 = cx - wdt / 2 - 22
    x = bx0 + 22
    for it, it2 in zip(out, items2):
        if it[0] == '_gap':
            marks.append((it[1], x + 18))
        k = it2[0]
        if k == 'txt':
            x += d.textlength(it2[1], font=f) / SS + 12
        elif k == 'glyph':
            x += (it2[3] if len(it2) > 3 else 32) + 8
        elif k == 'ticks':
            x += it2[2] * 14 + 10
        elif k == 'stars':
            x += it2[1] * 24 + 4
        else:
            x += {'chip': 36, 'ico': 38, 'sep': 26, 'unit': 36}.get(k, 0)
    g0 = C.gpaste
    C.gpaste = lambda im, name, x, y, px, col=(255, 255, 255), alpha=255: (px if col == (0, 0, 0) and name == 'tab' else g0(im, name, x, y, px, col, alpha))
    try:
        C.strip_c(img, items2, box)
    finally:
        C.gpaste = g0
    for kind, mx in marks:
        refuse_badge(img, kind, mx, ym, 16)


# ------------------------------------------------------------------ the PURGE map (set 7's Safehouse raid on v40)
def purge_map(img, F, docks, held=None, hover=None, pencil='rest', seed=0, sticks=True, show_slots=True):
    """grid, route tint, street slots, beacons, tethers, barricade, route pencil, notes, docked weapons, Safehouse + KAI's post"""
    V.draw_grid(img, F, labels=False)
    V.routes_ground(img)
    why = {c: why_p(held, c, docks) for c in P_SLOT} if held else {}
    lit = [c for c in P_SLOT if held and why[c] is None]
    if show_slots:
        slots(img, P_SLOT, lit=lit)
    if held and radius_limits(P_SLOT_OF[held], PATHS, V.SAFE):   # B-104 #3: only where it limits something (never, here)
        dock_radius(img, held, P_BEACON[held], DR.DOCK42['radius_hq'])
    for oid, c in docks.items():                              # stands first (on the ground), under the beacons' cones
        if c is not None:
            pad(img, oid, c)
    for oid in sorted([o for o in ORDER if o != 'KAI'], key=lambda o: G.cc(*P_BEACON[o])[1]):
        beacon(img, oid, *P_BEACON[oid], alpha=DIM if held else 1.0)
    if held:
        slots(img, lit, lit=lit, on_glass=True)
    for k, (oid, c) in enumerate(docks.items()):
        if c is not None:
            tether(img, oid, c, P_BEACON[oid], bow=0.16 if oid != 'VEX' else -0.10, seed=k,
                   lift_b=0.0 if oid == 'KAI' else 0.0)
    bx, by = G.cc(*V.BARR)
    stick(img, C.dev_c('BARRICADE'), bx, by - 6, -33, scale=V.STICK['barricade'])
    py, pr = Wax(PEN_Y, 11 + seed), Wax(PEN_R, 12 + seed)
    ps = Wax(PEN_Y, 13 + seed)
    V.routes(pr); say('A', 'B')
    V.wall_hp(py, 6, 3); say('6 \u2192 3')
    lx, ly = V.leak_at()
    sx, sy = G.cc(*V.SAFE)
    strike = None
    if pencil == 'rest':
        LT.pen_drop(pr, lx - 26, ly - 2, 17); pr.text('2', lx + 12, ly, 38, angle=-6); say('2')
        pr.arrow([(lx + 12, ly - 22), (lx + 22, ly - 40), (sx - 8, sy + 46)], width=6, head=14)
        K.pen_arrow_num(pr, 8, 6, sx - 150, sy + 10, 30); say('8 \u2192 6')
    elif pencil == 'place':
        hc, hr = hover
        reach = K.OPS[held]['reach']
        c0, c1, r0, r1 = max(hc - reach, 0), min(hc + reach + 1, G.nc), max(hr - reach, 0), min(hr + reach + 1, G.nr)
        V.pen_hatch_quad(py, [G.sp(c0, r0), G.sp(c1, r0), G.sp(c1, r1), G.sp(c0, r1)], step=26)
        hx, hy = G.cc(*hover)
        py.text('+3', hx + 104, hy - 40, 40, angle=-6); say('+3')
        LT.pen_drop(pr, lx - 26, ly - 2, 17); pr.text('2', lx + 12, ly, 38, angle=-6); say('2')
        py.tick(sx - 128, sy + 14, 18, 7)
        py.text('0', lx + 4, ly + 42, 40, angle=-6); say('0')
        strike = (lx, ly)
    tmp = Image.new('RGBA', img.size, (0, 0, 0, 0))
    py.ink_ss(img); pr.ink_ss(img)
    if strike:
        lx, ly = strike
        ps.stroke(ps.wobble([(lx - 50, ly + 8), (lx + 50, ly - 8)], 0.6), 6, taper=False)
        ps.ink_ss(img)
    beacon(img, 'KAI', *P_BEACON['KAI'], lift0=3.2, alpha=DIM if held else 1.0)
    stick(img, LT.safe_lt(), sx, sy - 12, -3, scale=V.STICK['safe'])
    if sticks:                                                # the docked tags read over the Safehouse and the posts
        for oid, c in sorted(docks.items(), key=lambda kv: G.cc(*kv[1])[1] if kv[1] else 0):
            if c is not None:
                docked(img, oid, c)
    if held:
        badges(img, why, P_DEV)
    if hover:                                                 # the hovered legal slot: its outline in yellow pencil (valid)
        hover_slot(img, hover)


BADGE_AT = {}                                                 # per-cell badge offsets where the default spot is covered


def badges(img, why, devs):
    """the refusal badges of a held weapon: beside every slot it may not take (taken by a weapon / holding a street device)"""
    for c, w in sorted(why.items(), key=lambda kv: DR.cid(kv[0])):
        if w not in ('socket_taken', 'slot_piece'):
            continue
        x, y = G.cc(*c)
        ox, oy = BADGE_AT.get(c, (44, 4))
        refuse_badge(img, 'taken' if w == 'socket_taken' else 'dev:' + devs[c], x + ox, y + oy)


def hover_slot(img, cell, col=PEN_Y, seed=45):
    ph = Wax(col, seed)
    ph.stroke(ph.wobble(_slot_quad(cell, 0.06), 0.6), 7, taper=False)
    ph.ink_ss(img)


# ------------------------------------------------------------------ plates
def plate_plan():
    F = F_all(); img = C.blank()
    purge_map(img, F, P_REST)
    V.units_at_rest(img); say('5', '3')
    left8(img, 8, 2, docks=P_REST)
    C.right_c(img, F, V.ROUNDS, heat=100)
    C.strip_c(img, C.PLAN_STRIP)
    return img


def held_card(img, oid, hx, hy, ok=True):
    """the weapon card trails the pointer (Takeover drag: spring lag, lifted, tilted, streaks); a yellow pencil arrow to the
    hovered socket when it is legal"""
    hold = (hx + 150, hy + 128)
    L = Layer(); d = L.d
    for k, (ox, oy) in enumerate(((40, 30), (56, 12), (24, 46))):
        d.line([(S(hold[0] + ox), S(hold[1] + oy)), (S(hold[0] + ox + 34), S(hold[1] + oy + 42))], fill=(235, 230, 255, 80 - k * 18), width=S(3))
    comp(img, L)
    if ok:
        py = Wax(PEN_Y, 44)
        py.arrow([(hold[0] - 70, hold[1] - 34), (hold[0] - 92, hold[1] - 56), (hx + 50, hy + 30)], width=6, head=16)
        py.ink_ss(img)
    o = K.OPS[oid]
    stick(img, C.wpn_c(o['wpn'], o['stars'], curl=0.3), hold[0], hold[1], 12, scale=0.82 * V.UI_S, lift=1.0)
    V.cursor(img, hx + 10, hy + 8)
    return hold


def plate_place():
    F = F_all(); img = C.blank()
    purge_map(img, F, P_REST, held='RUNE', hover=HOVER_P, pencil='place')
    V.units_at_rest(img); say('5', '3')
    held_card(img, 'RUNE', *G.cc(*HOVER_P))
    left8(img, 8, 0, docks=P_REST, held='RUNE')
    C.right_c(img, F, V.ROUNDS, unfold=True, heat=100)
    C.strip_c(img, [('ico', 'place', GOLD), ('sep',), ('chip', 'B'), ('ico', 'drop', S_HARM), ('txt', '2 \u2192 0', S_GAIN), ('sep',),
                    ('ico', 'heart', RED_H), ('txt', '8', S_GAIN), ('sep',), ('ico', 'skull', S_HI), ('txt', '8/8', S_HI)])
    return img


def plate_shop():
    F = F_all(); img = C.blank()
    purge_map(img, F, P_PLAY, seed=4, pencil='none')
    V.units_at_rest(img); say('5', '3')
    py = Wax(PEN_Y, 61)                                       # the merge lands on the docked shotgun: two stars on its socket
    x, y = tag_at(P_PLAY['RUNE'])
    K.pen_star(py, x + 50, y - 26, 10); K.pen_star(py, x + 72, y - 30, 10)
    py.ink_ss(img)
    left8(img, 8, 0, cost=3, docks=P_PLAY, merge=True)
    C.right_c(img, F, V.ROUNDS, peeled='SHOTGUN', heat=100)
    C.strip_c(img, [('glyph', 'SHOTGUN', TEXT_HI, 44), ('stars', 1), ('txt', '+', K.S_PLAN), ('stars', 1), ('txt', '\u2192', S_MID), ('stars', 2), ('sep',),
                    ('ico', 'coin', CYAN), ('txt', '7 \u2192 4', S_HI)])
    return img


def plate_playback():
    F = F_all(); img = C.blank()
    V.draw_grid(img, F, labels=False)
    V.routes_ground(img)                                      # no slot marks in playback: the map is locked, slots are a plan mark
    for oid in ('VEX', 'RUNE'):                               # reach outlines from the slots the shots leave
        V.reach_outline(img, V.cheb(*P_PLAY[oid], K.OPS[oid]['reach']), K.OPS[oid]['col'][0], alpha=130)
    for oid, c in P_PLAY.items():
        pad(img, oid, c)
    for oid in sorted([o for o in ORDER if o != 'KAI'], key=lambda o: G.cc(*P_BEACON[o])[1]):
        beacon(img, oid, *P_BEACON[oid])
    for k, (oid, c) in enumerate(P_PLAY.items()):
        tether(img, oid, c, P_BEACON[oid], bow=0.16 if oid != 'VEX' else -0.10, seed=k, lift_b=0.0 if oid == 'KAI' else 0.0)
    bx_, by_ = G.cc(*V.BARR)
    stick(img, C.dev_c('BARRICADE'), bx_, by_ - 6, -33, scale=V.STICK['barricade'])
    V.unit(img, 'trooper', *G.cc(*V.ENT_A), 1.0, count=3, alpha=0.38)
    V.unit(img, 'bike', *G.cc(*V.ENT_B), 1.0, count=1, alpha=0.38)
    say('3', '1')
    hx, hy = G.cc(*V.BARR_UP)                                 # b3: the trooper held at the wall
    bc = (4, 5)                                               # e6: the bike, slowed, under RUNE's shotgun and KAI's SMG
    bx, by = G.cc(*bc)
    L = Layer()
    ux, uy = G.cc(5, 5)[0] - bx, G.cc(5, 5)[1] - by
    for k in range(5):
        L.d.line([(S(bx + ux * (0.35 + k * 0.12)), S(by - 28 + uy * (0.35 + k * 0.12))), (S(bx + ux * (0.45 + k * 0.12)), S(by - 28 + uy * (0.45 + k * 0.12)))],
                 fill=(170, 230, 230, 140 - k * 24), width=S(3))
    comp(img, L)
    pr0 = Wax(PEN_R, 10); V.routes(pr0); pr0.ink_ss(img); say('A', 'B')
    sx, sy = G.cc(*V.SAFE)
    beacon(img, 'KAI', *P_BEACON['KAI'], lift0=3.2)
    stick(img, LT.safe_lt(), sx, sy - 12, -3, scale=V.STICK['safe'])
    for oid, c in sorted(P_PLAY.items(), key=lambda kv: G.cc(*kv[1])[1]):
        docked(img, oid, c)
    V.unit(img, 'trooper', hx, hy, 0.5, pips=('H',), r=22)
    V.unit(img, 'bike', bx, by, 0.5, pips=('S',), r=22); say('H', 'S')
    ex, ey = G.cc(*V.BARR_UP2)                                # b2: the kill
    vx, vy = tag_at(P_PLAY['VEX']); rx, ry = tag_at(P_PLAY['RUNE']); kx, ky = tag_at(P_PLAY['KAI'])
    V.tracer(img, (vx, vy), (hx + 8, hy - 28), K.OPS['VEX']['col'][1])
    V.tracer(img, (vx, vy), (ex + 4, ey - 24), K.OPS['VEX']['col'][1])
    V.tracer(img, (rx, ry), (bx - 12, by - 28), K.OPS['RUNE']['col'][1])
    V.tracer(img, (kx, ky), (bx + 6, by - 20), K.OPS['KAI']['col'][1])
    V.unit_bits(img, 'trooper', ex, ey, spread=52)
    py = Wax(PEN_Y, 9)
    py.text('2', hx + 58, hy - 82, 32, angle=-6); py.text('1', bx + 58, by - 82, 32, angle=-6); say('2', '1')
    V.wall_hp(py, 6, 4); say('6 \u2192 4')
    for (x, y) in ((vx - 56, vy - 16), (rx - 30, ry - 40)):    # kill tallies beside the guns that made them
        py.x(x, y, 11, 6)
    py.ink_ss(img)
    K.pop(img, F, hx - 76, hy - 80, '\u22124'); K.pop(img, F, bx + 40, by - 108, '\u22123'); say('4', '3')
    L = Layer(); d = L.d                                      # HELD + BOMBARD x2 (set 7's pill)
    px_, py_ = hx - 214, hy - 34
    d.rounded_rectangle([S(px_ - 70 + 3), S(py_ - 24 + 4), S(px_ + 76 + 3), S(py_ + 24 + 4)], radius=S(24), fill=INK + (255,))
    d.rounded_rectangle([S(px_ - 70), S(py_ - 24), S(px_ + 76), S(py_ + 24)], radius=S(24), fill=(255, 110, 196, 255), outline=INK + (255,), width=S(3))
    pc = V.PIP['H'][0]
    d.ellipse([S(px_ - 58), S(py_ - 16), S(px_ - 26), S(py_ + 16)], fill=pc + (255,), outline=INK + (255,), width=S(2.5))
    T(d, (px_ - 42, py_ + 1), 'H', 22, INK, anchor='mm')
    T(d, (px_ - 20, py_ + 1), '+', 26, INK, anchor='mm')
    comp(img, L)
    C.gpaste(img, 'MINE', px_ + 10, py_ - 1, 34)
    L = Layer(); T(L.d, (px_ + 32, py_ + 2), '\u00d72', 26, INK); comp(img, L)
    left8(img, 8, 0, docks=P_PLAY)
    C.right_c(img, F, V.ROUNDS, locked=True, busy=True, heat=100)
    C.strip_c(img, [('ticks', 3, 8), ('sep',), ('ico', 'skull', S_GAIN), ('txt', '2', S_GAIN), ('sep',), ('ico', 'drop', S_HI), ('txt', '0', S_HI), ('sep',),
                    ('glyph', 'BARRICADE', TEXT_HI, 30), ('txt', '1', S_HI), ('sep',), ('unit', 'trooper', 0.5), ('txt', '4', S_MID)])
    return img


def site_map(img, F, docks, held=None, hover=None):
    V.draw_grid(img, F, labels=False)
    for cells, lt in ((V.SA, 'A'), (V.SB, 'B'), (V.SC, 'C')):
        V.route_ground(img, cells, V.S_ENT[lt], V.SITE)
    V.end_cell(img, V.SITE, col=(150, 236, 130))
    why = {c: why_s(held, c, docks) for c in S_SLOT} if held else {}
    lit = [c for c in S_SLOT if held and why[c] is None]
    if held and radius_limits(S_SLOT_OF[held], SPATHS, V.SITE):   # the dock radius round the owner's beacon, in its colour,
        dock_radius(img, held, S_BEACON[held])                  # only where it limits something (B-104 #3)
    slots(img, S_SLOT, lit=lit)                               # the shared pool; a slot of KAI's only stays at rest
    for oid, c in docks.items():
        if c is not None and oid != held:
            pad(img, oid, c)
    beacon(img, 'VEX', *S_BEACON['VEX'], alpha=DIM if held else 1.0)
    if held:
        slots(img, lit, lit=lit, on_glass=True)
    for k, (oid, c) in enumerate(docks.items()):
        if c is not None and oid != held:
            tether(img, oid, c, S_BEACON[oid], bow=0.22, seed=20 + k, lift_b=0.0 if oid == 'KAI' else 0.0)
    sx, sy = G.cc(*V.SITE)
    cx, cy = G.cc(*V.SCORE)
    py, pr = Wax(PEN_Y, 11), Wax(PEN_R, 12)
    for cells, lt in ((V.SA, 'A'), (V.SB, 'B'), (V.SC, 'C')):
        K.route(pr, V.route_line(cells, V.S_ENT[lt], V.SITE), off=0, head=False)
        K.entry_mark(pr, *V.edge_pt(V.S_ENT[lt], cells[0]), lt); say(lt)
    pr.ink_ss(img)
    key = ('corehex',)
    if key not in LT._C:
        w, h, pad_ = 100, 64, 44
        body = Image.new('L', (S(w + 2 * pad_), S(h + 2 * pad_)), 0)
        ImageDraw.Draw(body).polygon([(S(pad_ + x * w), S(pad_ + y * h)) for x, y in [(0.25, 0), (0.75, 0), (1, 0.5), (0.75, 1), (0.25, 1), (0, 0.5)]], fill=255)
        LT._C[key] = K.vinyl(body, LT.PINK_T, LT.PINK_B, lambda d, art: C.ico_c(d, 'heart', pad_ + w / 2, pad_ + h / 2, 22, (255, 236, 244)), border=7, ext=5)
    stick(img, LT._C[key], cx, cy - 4, 3, scale=V.STICK['core'] * 1.2)
    L = Layer(); text(L.d, (cx + 30, cy + 150), '8/8', F['a40'], TEXT_HI + (255,), stroke=2, sfill=INK + (255,)); comp(img, L); say('8/8')
    for oid, c in sorted(docks.items(), key=lambda kv: G.cc(*kv[1])[1]):
        if c is not None and oid != held:
            docked(img, oid, c)
            if S_SUP.get(oid):                            # B-104 #4: the supporter's share on its docked gun
                tx, ty = tag_at(c)
                sup_chip(img, oid, tx + SUP_AT[0], ty + SUP_AT[1])
    beacon(img, 'KAI', *S_BEACON['KAI'], lift0=3.0, alpha=DIM if held else 1.0)
    stick(img, K.place_sticker('B2', None, (150, 236, 130), (62, 170, 70), shape='socket', w=96, h=84), sx, sy - 10, -3, scale=V.STICK['site']); say('B2')
    vx, vy = G.cc(*S_BEACON['VEX'], lift=8.5)
    py.arrow([(468, 772), (490, 720), (vx - 30, vy + 94), (vx - 18, vy + 70)], width=6, head=16)
    py.text('C2', 470, 800, 38, angle=-6); say('C2')
    pr = Wax(PEN_R, 13)
    bx_, by_ = G.cc(*V.SB[0])
    LT.pen_drop(pr, bx_ + 86, by_ - 8, 17); pr.text('1', bx_ + 120, by_ - 6, 38, angle=-5); say('1')
    K.pen_arrow_num(pr, 8, 7, cx + 130, cy + 176, 30); say('8 \u2192 7')
    py.ink_ss(img); pr.ink_ss(img)
    for lt, kind, n in (('A', 'trooper', 3), ('B', 'riot', 2), ('C', 'drone', 2)):
        V.unit(img, kind, *G.cc(*V.S_ENT[lt]), 1.0, count=n); say(str(n))
    if held:
        badges(img, why, S_DEV)


SITE_STRIP = [('chip', 'A'), ('ico', 'drop', S_GAIN), ('txt', '0', S_GAIN), ('sep',), ('chip', 'B'), ('ico', 'drop', S_HARM), ('txt', '1', S_HARM), ('sep',),
              ('chip', 'C'), ('ico', 'drop', S_GAIN), ('txt', '0', S_GAIN), ('sep',), ('ico', 'heart', RED_H), ('txt', '8 \u2192 7', S_HARM), ('sep',),
              ('ico', 'skull', S_HI), ('txt', '6/7', S_HI)]


def plate_site():
    F = F_all(); img = C.blank()
    site_map(img, F, S_REST)
    C.who_defends(img, F)
    C.evac_chip(img)
    left8(img, 8, 1, rnd=1, rmax=3, docks=S_REST, away={'MOTH': 'A1', 'RUNE': 'D4'})
    C.right_c(img, F, V.SROUNDS)
    C.strip_c(img, SITE_STRIP)
    return img


def plate_siteplace():
    F = F_all(); img = C.blank()
    site_map(img, F, S_REST, held='VEX', hover=HOVER_S)
    hx, hy = G.cc(*HOVER_S)
    pr = Wax(PEN_R, 71)                                       # refused: a red circle struck through, the too-far badge beside it
    pr.circle(hx, hy, 50, 32, width=6, start=-2.2, over=0.5, tilt=0)
    pr.stroke(pr.wobble([(hx - 34, hy + 22), (hx + 34, hy - 22)], 0.6), 6, taper=False)
    pr.ink_ss(img)
    refuse_badge(img, 'far', hx - 4, hy - 62, 19)
    hold = held_card(img, 'VEX', hx, hy, ok=False)
    sup_chip(img, 'VEX', hold[0] + SUP_HELD[0], hold[1] + SUP_HELD[1])   # the share travels with the held gun (B-104 #4)
    C.who_defends(img, F)
    C.evac_chip(img)
    left8(img, 8, 1, rnd=1, rmax=3, docks=S_REST, held='VEX', away={'MOTH': 'A1', 'RUNE': 'D4'})
    C.right_c(img, F, V.SROUNDS)
    strip8(img, [('ico', 'place', GOLD), ('refuse', 'far'), ('sep',)] + SITE_STRIP)
    return img


def devkey():
    """check strip (not a plate): the five street devices' 'device here' badges at plate size (1:1) and x2, on the place
    plate's ground round b4"""
    base = Image.open(OUT + 'r8_place.png').convert('RGBA')
    bx, by = G.cc(*V.BARR)
    crop = base.crop((int(bx - 330), int(by - 70), int(bx + 330), int(by + 70)))
    img = C.blank()
    for k, kind in enumerate(['BARRICADE', 'MINE', 'TAR', 'SHOCK', 'GATE']):
        dev_badge(img, kind, bx - 260 + k * 130, by, 17)
    over = img.resize(base.size, Image.LANCZOS).crop((int(bx - 330), int(by - 70), int(bx + 330), int(by + 70)))
    one = crop.copy(); one.alpha_composite(over)
    big = one.resize((one.width * 2, one.height * 2), Image.LANCZOS).convert('RGB')   # x2, in two halves under the 1:1 row
    out = Image.new('RGB', (one.width, one.height * 5), (14, 14, 18))
    out.paste(one.convert('RGB'), (0, 0))
    out.paste(big.crop((0, 0, one.width, big.height)), (0, one.height))
    out.paste(big.crop((one.width, 0, big.width, big.height)), (0, one.height * 3))
    out.save(OUT + 'r8_devhere_key.png')
    print('ok', OUT + 'r8_devhere_key.png', flush=True)


# ------------------------------------------------------------------ main + sheet
PLATES = dict(plan=plate_plan, place=plate_place, shop=plate_shop, playback=plate_playback, site=plate_site, siteplace=plate_siteplace)
CAPS = dict(plan='PURGE at rest: 4 posts at HQ; 13 street slots; SMG d7, jammer b7; B leaks 2',
            place="RUNE's shotgun held: 10 free slots lit; d7, b7 taken, b4 holds the barricade; d6 +3",
            shop='between rounds: SHOTGUN merged onto the docked one (stays on d6), credits 7 -> 4',
            playback='tick 3/8: shots leave the slots (rail b1, shotgun d6, SMG d7); no slot marks',
            site='B2 site raid: KAI on B2, VEX from C2 on a7; 7 shared slots; SMG b5, rail b7',
            siteplace="VEX's rail lifted: radius 3; b4 c6 d6 b7 lit, b5 taken; e6 (KAI's) too far")


def sheet(counts):
    names = list(PLATES)
    tw_, th_ = 700, 394
    pad_, cap = 12, 76
    cols = 3
    sh = Image.new('RGB', (cols * tw_ + (cols + 1) * pad_, 2 * (th_ + cap) + 3 * pad_ + 50), (14, 14, 18))
    d = ImageDraw.Draw(sh)
    f = ImageFont.truetype(MONO, 15); fa = ImageFont.truetype(ANTON, 22); fb = ImageFont.truetype(ANTON, 30)
    d.text((pad_, 10), 'RAID set 8 (DRAFT, v42): set 7 direction C on the v42 route slots: posts on the site, weapons docked on street slots', font=fb, fill=TEXT_HI)
    for k, n in enumerate(names):
        im = Image.open(OUT + 'r8_%s.png' % n).resize((tw_, th_), Image.LANCZOS)
        x = pad_ + (k % cols) * (tw_ + pad_); y = 54 + pad_ + (k // cols) * (th_ + cap + pad_)
        sh.paste(im, (x, y))
        c = counts.get(n, {})
        d.text((x + 4, y + th_ + 4), '%s   r8_%s.png' % (n, n), font=fa, fill=TEXT_HI)
        d.text((x + 4, y + th_ + 34), CAPS[n], font=f, fill=TEXT_MID)
        d.text((x + 4, y + th_ + 54), 'words on screen %s, corp document words %s' % (c.get('words', '?'), c.get('doc_words', '?')), font=f, fill=TEXT_MID)
    sh.save(OUT + 'r8_sheet.jpg', quality=90)
    print('ok', OUT + 'r8_sheet.jpg', flush=True)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    CJ = 'D:/rc_scratch/raid_v3/insp/d_counts.json'
    counts = json.load(open(CJ, encoding='utf-8')) if os.path.exists(CJ) else {}
    print('purge beacons', {k: G.name(*v) for k, v in P_BEACON.items()}, 'slots', [G.name(*c) for c in P_SLOT], flush=True)
    print('purge radius drawn:', any(radius_limits(P_SLOT_OF[o], PATHS, V.SAFE) for o in ORDER),
          '| site radius drawn:', {o: radius_limits(S_SLOT_OF[o], SPATHS, V.SITE) for o in S_BEACON}, flush=True)
    print('site slots', {o: [G.name(*c) for c in v] for o, v in S_SLOT_OF.items()}, flush=True)
    todo = [a for a in sys.argv[1:] if not a.startswith('--')] or list(PLATES) + ['sheet']
    for n in todo:
        if n == 'sheet':
            sheet(counts); continue
        if n == 'devkey':
            devkey(); continue
        LT.SHOWN.clear(); LT.DOC.clear(); LT.SMALL.clear()
        ov = PLATES[n]()
        V.finish(ov).save(OUT + 'r8_%s.png' % n)
        c = LT.classify(LT.SHOWN); c['doc_words'] = LT.classify(LT.DOC)['words']; c['small'] = list(LT.SMALL); c['shown'] = list(LT.SHOWN)
        counts[n] = c
        print('ok', n, {k: v for k, v in c.items() if k != 'shown'}, flush=True)
    json.dump(counts, open(CJ, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
