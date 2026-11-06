"""hv_plates: one builder per card effect type (VISUAL_PLAN H h01-h09 + variants).  Each returns the finished 1920x1080 RGB plate.

Hover grammar used on every plate (VISUAL_PLAN H, adapted):
  * lit = what the card touches, everything else x0.40 value, chroma x0.45
  * FOCUS lime corner brackets = legal targets (thin), the aimed target (thick)
  * ghost = the thing at its NEW place, 74 percent, with a grease-pencil yellow outline (PLAN = "proposal"); the origin is veiled
  * motion = L5 arrowed outline; edge colour = owner (pink tower, orange rings/schedule, yellow-pencil unit paths)
  * outcome = HP grammar: pink cross-hatch = lost at this END TURN by us, red hatch = the enemy takes it from you
"""
import sys, os, copy, math, json
sys.dont_write_bytecode = True
import hv_render as R
from hv_render import *
import hv_lib as HL
from hv_lib import PINK, PLAN, HARM, SOAKC, GAIN, SCHED, ENAMEL, LIME, PAPER, INKC, VIOLET, GOLD, CYAN
import a2_kit as K2
import a2_plan as P2m
import wr2_units as WU2
import o_arcs as OA
import r2_arcs as RA
import r2_misc as M2m
import e8lib as E8m

HS_ = R.HS
S = HS_.S

HAND4 = ['Brace', 'Spin3', 'Trigger', 'Twist']
BILL = (1072, 76, 1896, 270)
OBJ = (1072, 278, 1896, 330)
RAMB = (1072, 334, 1896, 386)
HEAD = (1072, 12, 1896, 68)
BEZ = (352, 388)

rmid = lambda dep: sum(CB.ring_geom(dep)) / 2.0


def frames(cards, hand, tag, opt=None, base=None):
    f_live, _, _ = HS_.frame([], opt, 'live', base=base, hand=hand)
    f_plan, st, pv = HS_.frame(cards, opt, tag, base=base, hand=hand)
    return f_live, f_plan


def strip_brace(f):
    g = copy.deepcopy(f)
    g['brace_sectors'] = []
    for w in g['wheel']:
        w['brace'] = False
    return g


def uby(f, uid):
    return [u for u in f['units'] if u['id'] == uid][0]


def tok(u):
    return AU.token_pos(u)


def adj_pos(f):
    a = f['adj']
    return ppx(C, rmid(a['ring']), 60 * a['s'])


# ------------------------------------------------------------------------------------------------ lit regions
def lit_tower(Lt, r=163):
    Lt.disc(r)


def lit_arcs_of(Lt, f, ids=None, pad=4):
    for it in RA.layout_items(f, ids):
        r = OA.LANE_R[min(it['lane'], 2)]
        Lt.wedge(r - OA.HALF - 5, r + OA.HALF + 5, it['a0'] - pad, it['a1'] + pad, 2)


def lit_cells(Lt, f, ids):
    for u in f['units']:
        if u['id'] in ids and u['w'] < 6:
            Lt.poly(HL.cell_poly_unit(u), 5)


def lit_ring(Lt, dep, pad=2):
    ri, ro = CB.ring_geom(dep)
    Lt.annulus(ri - pad, ro + pad)


def lit_adjuster(Lt, f):
    a = f['adj']
    ri, ro = CB.ring_geom(a['ring'])
    Lt.sector(a['s'], ri - 2, ro + 2, 31, 2)


def lit_guns(Lt, f):
    for g in f['guns']:
        p0 = ppx(C, 150, 60 * g['sector'])
        for uid in {x['uid'] for x in g['shots'] if x['uid'] is not None}:
            if uid == 0:
                tp = adj_pos(f)
                lit_adjuster(Lt, f)
            else:
                u = uby(f, uid)
                if u['consumed'] or u['trigdead']:
                    continue
                tp = tok(u)
                lit_cells(Lt, f, {uid})
            Lt.line(p0, tp, 24)


def lit_bezel(Lt):
    Lt.annulus(BEZ[0] - 2, BEZ[1] + 2)


def lit_bill(Lt):
    Lt.box(*BILL, r=8)


def lit_res(Lt):
    Lt.box(*RAMB, r=8)


# ------------------------------------------------------------------------------------------------ marks
def focus_slice(L, s, thick=False):
    K2.focus_brackets(L, 'band', dict(ri=56, ro=161, a0=60 * s - 28, a1=60 * s + 28), 'A', w=5.4 if thick else 3.0, arm=30 if thick else 16, grow=3 if thick else 0)


def focus_cell(L, u, thick=False):
    ri, ro = CB.ring_geom(u['dep'])
    a0 = 60 * u['s'] - 30
    a1 = 60 * (u['s'] + u['w'] - 1) + 30
    K2.focus_brackets(L, 'band', dict(ri=ri + 3, ro=ro - 3, a0=a0 + 2.5, a1=a1 - 2.5), 'A', w=5.4 if thick else 3.0, arm=30 if thick else 17, grow=0)


def focus_adj(L, f, thick=False):
    a = f['adj']
    ri, ro = CB.ring_geom(a['ring'])
    K2.focus_brackets(L, 'band', dict(ri=ri + 3, ro=ro - 3, a0=60 * a['s'] - 27.5, a1=60 * a['s'] + 27.5), 'A', w=5.4 if thick else 3.0, arm=28 if thick else 17, grow=0)


def focus_col(L, s, thick=False, r0=166, r1=350):
    K2.focus_brackets(L, 'band', dict(ri=r0, ro=r1, a0=60 * s - 27, a1=60 * s + 27), 'A', w=5.4 if thick else 3.0, arm=34 if thick else 18, grow=0)


def wedge_poly(s, r0=46, r1=160, half=29.0):
    n = 14
    return [ppx(C, r1, 60 * s - half + 2 * half * i / n) for i in range(n + 1)] + [ppx(C, r0, 60 * s + half - 2 * half * i / n) for i in range(n + 1)]


def inset_wedge(s, d):
    r0, r1 = 46 + d, 160 - d
    half = 29.0 - math.degrees(d / ((r0 + r1) / 2.0))
    return wedge_poly(s, r0, r1, half)


def clamp_ghost(L, s, col=PINK):
    """L10 protection = a DOUBLE line (two solid strokes, 3 px apart). P family painted clamp plate over a whole wedge, 55 percent, rivets, pencil edge (= proposal)"""
    whole = wedge_poly(s, 46, 160, 29.4)
    HL.tint_poly(L, whole, col, 34)                     # the wedge itself: a faint wash, the icon stays clear
    r0, r1, half = 124.0, 160.5, 29.6
    band = wedge_poly(s, r0, r1, half)
    HL.tint_poly(L, band, col, 190)                     # the plate: outer 40 percent of the wedge (FX-P), painted, 75 percent
    # dry-brush streaks along the plate (P hand: tapered, wobbling strokes)
    for q, rr in enumerate((131.0, 141.0, 151.0)):
        HL.hand(L, HL.arc(rr, 60 * s - 25, 60 * s + 25, 14), w=4.6, col=HL.PINK_HI, ink=0.0, seed=20 + q + s, taper=True, wobble=1.0)
    # L10 double line on the plate's inner edge: two solid strokes, 3 px apart
    for rr, w, c in ((r0, 4.6, col), (r0 - 7.6, 3.0, PAPER)):
        pts = HL.arc(rr, 60 * s - half + 0.6, 60 * s + half - 0.6, 14)
        L.line(pts, INKC, w + 3.4)
    for rr, w, c in ((r0, 4.6, col), (r0 - 7.6, 3.0, PAPER)):
        pts = HL.arc(rr, 60 * s - half + 0.6, 60 * s + half - 0.6, 14)
        L.line(pts, c, w)
    # side clamps: the same double line up the two radial edges of the plate
    for sg in (-1, 1):
        a = 60 * s + sg * (half - 1.2)
        for off, w, c in ((0.0, 4.6, col), (-sg * math.degrees(7.6 / 142.0), 3.0, PAPER)):
            L.line([ppx(C, r0, a + off), ppx(C, r1, a + off)], INKC, w + 3.4)
        for off, w, c in ((0.0, 4.6, col), (-sg * math.degrees(7.6 / 142.0), 3.0, PAPER)):
            L.line([ppx(C, r0, a + off), ppx(C, r1, a + off)], c, w)
    for rr, aa in ((133, -21), (133, 21), (152, -21), (152, 21)):
        x, y = ppx(C, rr, 60 * s + aa)
        L.ellipse([x - 4.6, y - 4.6, x + 4.6, y + 4.6], fill=INKC)
        L.ellipse([x - 3.0, y - 3.0, x + 3.0, y + 3.0], fill=PAPER)
        L.ellipse([x - 1.6, y - 2.6, x - 0.2, y - 1.2], fill=col)
    HL.pencil_poly(L, wedge_poly(s, 44, 163, 30.2), w=2.8, ink=1.8, seed=s + 3)


def bill_marks(L, f_live, f_plan):
    """pencil underline under the hero numbers that the plan changes (LANDS / THROUGH): the bill switches to plan values (GDD 9.2)"""
    box = hud2.R.get('hero_pair') or (1416, 78, 1574, 168)
    lv, pl = f_live['pv']['eq'], f_plan['pv']['eq']
    th = str(pl['through'])
    tw = L.tw(th, 58, 'anton')
    xt = box[2] - 8 - tw
    if pl['through'] != lv['through']:
        HL.pencil(L, [(xt, 151), (xt + tw, 150.5)], w=3.2, ink=1.5, seed=3, cap=False)
    if pl['lands'] != lv['lands']:
        ls = str(pl['lands'])
        lw = L.tw(ls, 58, 'anton')
        HL.pencil(L, [(box[0] + 8, 151), (box[0] + 8 + lw, 150.5)], w=3.2, ink=1.5, seed=4, cap=False)


def ram_mark(L, before, after):
    for i in range(after, before):
        x, y = 1149 + 32 * i, 359
        L.ellipse([x - 17, y - 17, x + 17, y + 17], outline=INKC, w=6.6)
        L.ellipse([x - 17, y - 17, x + 17, y + 17], outline=PLAN, w=3.2)


def ram_plus(L, n_at):
    """refund: a pencil plus on the RAM coin that comes back"""
    x, y = 1149 + 32 * n_at, 359
    L.ellipse([x - 17, y - 17, x + 17, y + 17], outline=INKC, w=6.6)
    L.ellipse([x - 17, y - 17, x + 17, y + 17], outline=GAIN, w=3.2)
    for pts in ([(x - 6, y), (x + 6, y)], [(x, y - 6), (x, y + 6)]):
        L.line(pts, INKC, 6.6)
        L.line(pts, GAIN, 3.2)


def trace_mark(L, before, after):
    for i in range(before, after):
        x, y = 1438 + 29 * i, 359
        L.rect([x - 15, y - 15, x + 15, y + 15], outline=INKC, w=6.6, r=5)
        L.rect([x - 15, y - 15, x + 15, y + 15], outline=PLAN, w=3.2, r=5)


def pencil_plus(L, x, y, col=PLAN, s=6):
    for pts in ([(x - s, y), (x + s, y)], [(x, y - s), (x, y + s)]):
        L.line(pts, INKC, 6.6)
        L.line(pts, col, 3.2)


def hatch_cell(L, u, col=PINK, alpha=0.5):
    poly = HL.cell_poly_unit(u)
    k = L.k
    lay = L2()
    PP.hatch_poly(lay, poly, col, pitch=8.0, lw=2.4, base=None, edge=2.6)
    im = lay.im.copy()
    im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    L.im.alpha_composite(im)


def note_slip(L, title, lines, x=1082, y=410, w=700):
    """plate chrome, not game UI: a paper review slip in the free room zone. Names the hover, what is lit / dimmed, flags a showcase copy"""
    if not NOW['words']:
        return
    mw = max([L.tw(ln, 15, 'mono') for ln in lines] + [L.tw(title, 20, 'anton')]) + 30
    w = int(min(w, max(380, mw)))
    h = 18 + 25 * (len(lines) + 1)
    L.rect([x + 3, y + 4, x + w + 3, y + h + 4], fill=(0, 0, 0, 120), r=4)
    L.rect([x, y, x + w, y + h], fill=(242, 238, 228, 244), outline=INKC, w=2, r=4)
    L.rect([x + 12, y - 9, x + 150, y + 13], fill=(255, 226, 0, 255), outline=INKC, w=1.6, r=2)
    L.text((x + 81, y + 2), 'REVIEW NOTE', 13, 'mono', fill=INKC, anchor='mm')
    L.text((x + 14, y + 33), title, 20, 'anton', fill=INKC, anchor='lm')
    for i, ln in enumerate(lines):
        L.text((x + 14, y + 33 + 25 * (i + 1)), ln, 15, 'mono', fill=(34, 30, 48), anchor='lm')


def pink_burst(L, x, y, r=24, seed=1):
    HL.starburst(L, x, y, r, PINK, (255, 255, 255), 11, 2.6, seed)


def build(f_board, f_hud, words, hand, hov, lit_fn, marks_fn, ghosts=None, veil=None, hide=(), arcs_skip=(), note=None, other_dim=0.7, k=0.50, played=None):
    HAND['dim'] = other_dim
    bg, _ = R.board_layer(f_board, words, hide_units=hide, arcs_skip=arcs_skip)
    hud = R.hud_layer(f_hud, words)
    Lt = HL.Lit()
    lit_fn(Lt)
    mask = Lt.mask()
    marks = []
    if veil is not None:
        marks.append(veil)
    if ghosts:
        marks.extend(ghosts)
    Lm = L2()
    NOW['words'] = words
    marks_fn(Lm)
    if note and words:
        note_slip(Lm, *note)
    marks.append(Lm.done())
    hand_lay, hov_info = R.hand_layers(words, hand, hov, played=played)
    stick = R.sticker_layer(words)
    return R.compose(bg, hud, mask, marks, hand_lay, stick, k=k)


def hand_of(card, rest=('Brace', 'Trigger', 'Twist')):
    h = [card] + [c for c in rest if c != card]
    return h[:4], 0


# ================================================================================================ h02 Brace
def brace(words=True, aim=2):
    hand = HAND4
    f_live, f_plan = frames([('Brace', aim)], hand, 'brace')
    fb = strip_brace(f_plan)

    def lit(Lt):
        lit_tower(Lt)
        lit_arcs_of(Lt, f_plan)
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        for s in range(6):
            if s != aim:
                focus_slice(L, s)
        clamp_ghost(L, aim)
        focus_slice(L, aim, thick=True)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        bill_marks(L, f_live, f_plan)
        # the block result on its landing arc: pencil mark on the arc that now stops at the clamp
        for it in RA.layout_items(f_plan):
            u = it['u']
            for q in range(u['w']):
                sec = (it['s0'] + q) % 6
                if u.get('land_brace', {}).get(str(sec)):
                    r = OA.LANE_R[min(it['lane'], 2)]
                    HL.pencil(L, HL.arc(r + 21, 60 * sec - 18, 60 * sec + 18), w=4.0, ink=2.0, seed=sec)

    note = ('HOVER: BRACE', ['aimed: slice at sector %d (TURRET); bill shows plan: THROUGH 6 -> 4' % aim,
                            'lit: 6 slices, landing arcs, bill, RAM  |  dim: rings, queue, rest',
                            'hand: approved state hand'])
    return build(fb, f_plan, words, hand, 0, lit, marks, note=note)


# ================================================================================================ h01 tower turns
def spin(card='Spin3', words=True):
    spec = {'Spin3': (('Spin3', 3), 3, ['Brace', 'Spin3', 'Trigger', 'Twist'], 1), 'Spin2': (('Spin2', 2), 2, ['Brace', 'Spin2', 'Trigger', 'Twist'], 1),
            'Nudge': (('Nudge', 1), 1, ['Brace', 'Nudge', 'Trigger', 'Twist'], 1)}[card]
    act, n, hand, hov = spec
    f_live, f_plan = frames([act], hand, card.lower())
    showcase = card != 'Spin3'

    def lit(Lt):
        lit_tower(Lt)
        lit_ring(Lt, 0)
        lit_guns(Lt, f_plan)
        lit_arcs_of(Lt, f_plan)
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        a0 = 8.0
        a1 = a0 + 60 * n - 16
        HL.channel(L, HL.arc(64, a0, a1, 40), col=PINK, w=15, head=22, chev=True, fill=(10, 8, 20, 170))
        # preview cue: the tower rim in grease pencil (= this is a proposal, not the live tower)
        HL.pencil(L, HL.arc(167.5, 0.5, 359.5, 120), w=3.4, ink=1.8, grain=True, cap=False, seed=7)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        bill_marks(L, f_live, f_plan)

    ttl = 'HOVER: %s (turn the tower %d)' % (card.upper(), n)
    lines = ['tower shown at the plan angle (clockwise x%d), pencil rim = proposal' % n,
             'tracers, landing marks, bill = plan values: THROUGH %d -> %d' % (f_live['pv']['eq']['through'], f_plan['pv']['eq']['through']),
             'lit: tower, ring NOW, guns, arcs, bill  |  dim: rings +1/+2, queue']
    if showcase:
        lines.append('hand swapped for the showcase; board = approved state')
    return build(f_plan, f_plan, words, hand, hov, lit, marks, note=(ttl, lines))


# ================================================================================================ h03 Trigger
def trigger(words=True, variant='f1'):
    hand = HAND4
    if variant == 'f1':
        f_live, f_plan = frames([('Trigger', 4)], hand, 'trigger')
    else:       # f2: Twist already played (approved best line), then the Trigger hover shows the refund
        f_live, f_plan = frames([('Twist', (1, 1)), ('Trigger', 4)], hand, 'trigger2')
        f_live, _, _ = HS_.frame([('Twist', (1, 1))], None, 'live2', hand=hand)
    tr_units = [4, 5, 6, 7]
    fb = copy.deepcopy(f_live)
    victim = uby(fb, 1)
    victim['lose'] = [0, victim['hp']]
    tgt = uby(f_live, 4)
    kills = [e for e in f_plan['tlog'] if e[0] == 'trig_unit']

    def lit(Lt):
        lit_cells(Lt, f_live, set(tr_units) | {1})
        lit_arcs_of(Lt, f_plan)
        for s in (3, 4):
            Lt.sector(s, 40, 163, 30, 2)
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        for uid in tr_units:
            if uid != 4:
                focus_cell(L, uby(f_live, uid))
        hatch_cell(L, victim, PINK, 0.55)
        # per covered sector: a pencil L5 path from the Trigger unit down to what it hits
        for e in kills:
            sec = e[1]
            ang = 60 * sec + 13
            r0 = CB.ring_geom(tgt['dep'])[1] - 6
            r1 = CB.ring_geom(0)[0] + 30
            pts = [ppx(C, r0, ang), ppx(C, r1, ang)]
            HL.channel(L, pts, col=PLAN, w=13, head=19, chev=True, fill=(10, 8, 20, 200), tail_dot=True)
        # the kill: pink starburst on the dead unit (no word) + the refund coin
        kx, ky = ppx(C, rmid(0) + 2, 60 * 4 + 8)
        pink_burst(L, kx, ky, 25, 3)
        if f_plan['refunds']:
            cx, cy = ppx(C, rmid(0) - 4, 60 * 3 + 40)
            K2.refund_token(L, cx, cy, 32, 'A')
        focus_cell(L, tgt, thick=True)
        if f_plan['refunds']:
            ram_plus(L, f_plan['ram'] - 1)
        else:
            ram_mark(L, f_live['ram'], f_plan['ram'])
        bill_marks(L, f_live, f_plan)
        trace_mark(L, f_live['trace'], f_plan['trace'])

    ttl = 'HOVER: TRIGGER (aimed: Payload, ring +1)'
    lines = ['pencil paths = the Payload resolves NOW down sectors 3 and 4',
             'pink hatch = the Packet is lost this END TURN; the kill refunds 1 RAM',
             'lit: legal units, the victim, slices 3-4, bill, RAM/TRACE  |  dim: rest']
    if variant == 'f2':
        lines.append('shown after TWIST (approved best line, f2): refund is live')
    if variant == 'f2':
        return build(fb, f_plan, words, ['Brace', 'Spin3', 'Trigger'], 2, lit, marks, arcs_skip={1, 4}, note=(ttl, lines), played=['Twist'])
    return build(fb, f_plan, words, hand, 2, lit, marks, arcs_skip={1, 4}, note=(ttl, lines))


# ================================================================================================ h04 Twist
def twist(words=True, ring=1, d=1):
    hand = HAND4
    f_live, f_plan = frames([('Twist', (ring, d))], hand, 'twist')
    changed = [u['id'] for u in f_plan['units'] if u['dep'] == ring and uby(f_live, u['id']).get('land_sectors') != u.get('land_sectors')]
    veil_ids = set(changed)

    def lit(Lt):
        lit_ring(Lt, 1)
        lit_ring(Lt, 2)
        lit_bezel(Lt)
        lit_arcs_of(Lt, f_plan)
        lit_bill(Lt)
        lit_res(Lt)
        Lt.box(1060, 6, 1908, 70, 10)

    def marks(L):
        # the chosen ring: one sector turn, an orange L5 sweep in the free cell, clockwise = +1
        r = rmid(ring)
        a_mid = 60 * 1 if ring == 1 else 60 * 0
        pts = HL.arc(r, a_mid - 24 * d, a_mid + 24 * d, 20)
        HL.channel(L, pts, col=SCHED, w=16, head=22, chev=True, fill=(10, 8, 20, 190))
        # ring-tag badge (E10 twist pill, kept: plan family)
        P2m.twist_badge(L, f_plan, 'A')
        # other legal ring (+2): thin focus on its tag side: a bracket on the ring band
        ro = 2 if ring == 1 else 1
        ri_, ro_ = CB.ring_geom(ro)
        K2.focus_brackets(L, 'band', dict(ri=ri_ + 2, ro=ro_ - 2, a0=-28, a1=28), 'A', w=3.0, arm=16, grow=0)
        K2.focus_brackets(L, 'band', dict(ri=CB.ring_geom(ring)[0] + 2, ro=CB.ring_geom(ring)[1] - 2, a0=-28, a1=28), 'A', w=5.4, arm=28, grow=0)
        bill_marks(L, f_live, f_plan)

    # ghosts: the affected landing arcs at their new sectors (pencil outlined), veiled live arcs
    ghosts = []
    La = L2()
    A2.landing_arcs(La, f_plan, {}, only=veil_ids)
    a = La.done()
    ghosts.append(a)
    Lo = L2()
    for it in RA.layout_items(f_plan, veil_ids):
        r = OA.LANE_R[min(it['lane'], 2)]
        HL.pencil(Lo, HL.arc(r + OA.HALF + 4, it['a0'] + 4, it['a1'] - 2), w=3.4, ink=1.8, seed=it['u']['id'], cap=False)
    ghosts.append(Lo.done())
    ttl = 'HOVER: TWIST (aimed: ring +1, clockwise)'
    lines = ['orange L5 sweep = ring +1 turns one extra sector at END TURN',
             'pencil-edged arcs = the landings after the twist (Payload %s, Packet %s)' % (
                 [u for u in f_plan['units'] if u['id'] == 4][0]['land_sectors'], [u for u in f_plan['units'] if u['id'] == 5][0]['land_sectors']),
             'lit: rings +1/+2, bezel, arcs, bill  |  dim: ring NOW, tower']
    return build(f_live, f_plan, words, hand, 3, lit, marks, ghosts=ghosts, arcs_skip=veil_ids, note=(ttl, lines))


# ================================================================================================ h05 Strike
def strike(words=True, aim=5):
    hand, hov = hand_of('Strike')
    f_live, f_plan = frames([('Strike', aim)], hand, 'strike')
    fb = copy.deepcopy(f_live)
    tgt = uby(fb, aim)
    tgt['lose'] = [0, min(tgt['hp'], 2)]
    all_ids = {u['id'] for u in f_live['units']}
    dies = tgt['hp'] <= 2

    def lit(Lt):
        lit_cells(Lt, f_live, all_ids)
        lit_adjuster(Lt, f_live)
        lit_arcs_of(Lt, f_plan)
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        for u in f_live['units']:
            if u['id'] != aim and u['w'] < 6:
                focus_cell(L, u)
        focus_adj(L, f_live)
        if dies:
            hatch_cell(L, tgt, PINK, 0.5)
        x, y = tok(tgt)
        pink_burst(L, x + 22, y - 10, 30, 5)
        HL.speed_lines(L, x + 22, y - 10, 90, 5, 34, 64, PINK)
        focus_cell(L, tgt, thick=True)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        bill_marks(L, f_live, f_plan)

    ttl = 'HOVER: STRIKE (aimed: Packet, ring +1, 2 HP)'
    lines = ['pink hatch = both HP of the Packet are lost this END TURN (ours)',
             'pink burst + speed lines = the hit; the unit never lands',
             'lit: every unit in range, arcs, bill  |  dim: tower, schedule',
             'hand swapped for the showcase; board = approved state']
    return build(fb, f_plan, words, hand, hov, lit, marks, arcs_skip={aim}, note=(ttl, lines))


# ================================================================================================ h06 Shove
def shove(words=True, uid=5, d=1, bump=False):
    hand, hov = hand_of('Shove')
    f_live, f_plan = frames([('Shove', (uid, d))], hand, 'shove')
    ids01 = {u['id'] for u in f_live['units'] if u['dep'] <= 1}
    u0 = uby(f_live, uid)
    u1 = uby(f_plan, uid)
    fb = copy.deepcopy(f_live)
    ghosts = []
    veil = None
    nb = None
    if bump:
        # the neighbour in the way
        occ = set((u0['s'] + d * (i + 1)) % 6 for i in range(1)) if u0['w'] == 1 else {(u0['s'] + u0['w'] - 1 + 1) % 6}
        nb = [u for u in f_live['units'] if u['dep'] == u0['dep'] and u['id'] != uid and ((u['s'] + k) % 6 in occ for k in range(u['w']))]
        nb = [u for u in f_live['units'] if u['dep'] == u0['dep'] and u['id'] != uid and any((u['s'] + k) % 6 in occ for k in range(u['w']))][0]
        uby(fb, uid)['lose'][1] += 1
        uby(fb, nb['id'])['lose'][1] += 1
    else:
        ghosts.append(R.ghost_units(f_plan, {uid}, words))
        veil = R.veil_cells(f_live, {uid}, 0.6)

    def lit(Lt):
        lit_ring(Lt, 0)
        lit_ring(Lt, 1)
        lit_adjuster(Lt, f_live)
        lit_arcs_of(Lt, f_plan)
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        for u in f_live['units']:
            if u['dep'] <= 1 and u['id'] != uid and u['w'] < 6:
                focus_cell(L, u)
        r = rmid(u0['dep'])
        if not bump:
            p0 = tok(u0)
            p1 = tok(u1)
            a_from = math.degrees(math.atan2(p0[0] - C[0], -(p0[1] - C[1])))
            a_to = math.degrees(math.atan2(p1[0] - C[0], -(p1[1] - C[1])))
            if d > 0 and a_to < a_from:
                a_to += 360
            if d < 0 and a_to > a_from:
                a_to -= 360
            sh = math.degrees(34.0 / r)
            pts = HL.arc(r, a_from + d * sh, a_to - d * sh, 24)
            HL.channel(L, pts, col=SCHED, w=14, head=20, chev=True, fill=(10, 8, 20, 190))
            ri_, ro_ = CB.ring_geom(u1['dep'])
        else:
            a_edge = 60 * (u0['s'] + u0['w'] - 1 + (0.5 if d > 0 else -0.5)) if d > 0 else 60 * (u0['s'] - 0.5)
            pts = HL.arc(r, a_edge - 44 * d, a_edge + 8 * d, 16)
            HL.channel(L, pts, col=SCHED, w=14, head=20, chev=True, fill=(10, 8, 20, 190))
            # bump: two small bursts at the shared edge, pink hatch on 1 HP of both
            bx, by = ppx(C, r, a_edge + 12 * d)
            pink_burst(L, bx, by, 24, 2)
        focus_cell(L, u0, thick=True)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        bill_marks(L, f_live, f_plan)
        trace_mark(L, f_live['trace'], f_plan['trace'])

    ttl = 'HOVER: SHOVE (aimed: %s%s)' % (u0['kind'], ' bumps its neighbour' if bump else ', one sector clockwise')
    lines = ['orange L5 arrow = the unit slides one sector' if not bump else 'burst = collision: both units lose 1 HP, neither moves',
             'ghost with pencil edge = its new cell, new landing arc' if not bump else 'pink hatch = the 1 HP each loses at this END TURN (ours)',
             'lit: rings NOW and +1, arcs, bill, RAM/TRACE  |  dim: ring +2, schedule',
             'hand swapped for the showcase; board = approved state']
    return build(fb, f_plan, words, hand, hov, lit, marks, ghosts=ghosts, veil=veil, hide=(), arcs_skip={uid} if not bump else (), note=(ttl, lines))


# ================================================================================================ h07 Pull
def pull(words=True, uid=7):
    hand, hov = hand_of('Pull')
    f_live, f_plan = frames([('Pull', uid)], hand, 'pull')
    u0 = uby(f_live, uid)
    u1 = uby(f_plan, uid)
    ghosts = [R.ghost_units(f_plan, {uid}, words)]
    veil = R.veil_cells(f_live, {uid}, 0.6)

    def lit(Lt):
        lit_cells(Lt, f_live, {uid})
        lit_cells(Lt, f_plan, {uid})
        lit_arcs_of(Lt, f_plan, {uid})
        lit_arcs_of(Lt, f_live, {uid})
        Lt.annulus(rmid(1) - 4, rmid(1) + 4) if False else None
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        a = 60 * u0['s'] + 19
        r_in = rmid(1) + 10
        r_out = CB.ring_geom(2)[1] - 3
        pts = [ppx(C, r_out, a), ppx(C, r_in, a)]
        HL.channel(L, pts, col=SCHED, w=16, head=24, chev=True, fill=(10, 8, 20, 200), tail_dot=False)
        focus_cell(L, u0, thick=True)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        bill_marks(L, f_live, f_plan)
        trace_mark(L, f_live['trace'], f_plan['trace'])

    ttl = 'HOVER: PULL (the only legal unit: Packet, ring +2)'
    lines = ['orange L5 arrow = the unit moves one ring inward (now enters +1)',
             'ghost with pencil edge = its new cell; its landing arc moves a turn nearer',
             'no other unit has a free inner cell: they stay dim, no brackets',
             'hand swapped for the showcase; board = approved state']
    return build(f_live, f_plan, words, hand, hov, lit, marks, ghosts=ghosts, veil=veil, arcs_skip={uid}, note=(ttl, lines))


# ================================================================================================ h08 Hold
def hold(words=True):
    hand, hov = hand_of('Hold')
    f_live, f_plan = frames([('Hold', 0)], hand, 'hold')

    def lit(Lt):
        lit_bezel(Lt)
        for dp in range(3):
            lit_ring(Lt, dp)
        lit_arcs_of(Lt, f_plan)
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        # the step slides one slot later: an orange L5 arrow just outside the bezel, from where the +2 sits now to where it will sit
        HL.channel(L, HL.arc(398, 66, 104, 20), col=SCHED, w=13, head=19, chev=True, fill=(10, 8, 20, 200))
        # the live cell becomes a HOLD cell: pencil outline round it (proposal)
        HL.pencil(L, HL.arc(386, 1.5, 38.5, 16), w=3.4, ink=1.8, seed=5, cap=False)
        HL.pencil(L, HL.arc(351, 1.5, 38.5, 16), w=3.4, ink=1.8, seed=6, cap=False)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        bill_marks(L, f_live, f_plan)

    ttl = 'HOVER: HOLD (rings do not turn this END TURN)'
    lines = ['schedule: 2 . 0 . 0  ->  0 . 2 . 0 (the step slides one slot later)',
             'landing arcs recomputed at plan value (Payload, Packet land elsewhere)',
             'lit: bezel, all rings, arcs, bill  |  dim: tower interior, rest',
             'hand swapped for the showcase; board = approved state']
    return build(f_plan, f_plan, words, hand, hov, lit, marks, note=(ttl, lines))


# ================================================================================================ h09 Firewall
def firewall(words=True, sec=0):
    hand, hov = hand_of('Firewall')
    f_live, f_plan = frames([('Firewall', sec)], hand, 'firewall')
    fw_log = [e for e in f_plan['log'] if e[0] == 'fw']
    burn = [uby(f_live, 4), uby(f_live, 6)]
    fb = copy.deepcopy(f_live)
    uby(fb, 6)['lose'][1] += 1           # the Packet that steps in loses 1 HP at END TURN (pink = ours); the armoured Payload loses 0

    def lit(Lt):
        Lt.sector(sec, 160, 354, 31, 3)
        lit_cells(Lt, f_live, {4, 6})
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        for s in range(6):
            if s not in (sec,) and f_live['fw'][s] == 0 and s in (0, 1, 2, 4, 5):
                focus_col(L, s)
        # the burn band ghost: pink flame strokes + 22 percent wash through all three rings of the aimed sector
        band = HL.Lit  # noqa
        poly = [ppx(C, 354, 60 * sec - 28 + 56 * i / 20) for i in range(21)] + [ppx(C, 163, 60 * sec + 28 - 56 * i / 20) for i in range(21)]
        HL.tint_poly(L, poly, PINK, 46)
        for q, off in enumerate((-17, -6, 6, 17)):
            pts = []
            for i in range(26):
                r = 172 + (176) * i / 25
                wob = math.sin(i * 0.9 + q * 1.7) * 3.2
                pts.append(ppx(C, r, 60 * sec + off + wob / r * 57.3))
            HL.hand(L, pts, w=5.8, col=PINK, seed=11 + q, wobble=0.8)
        HL.pencil_poly(L, poly, w=3.0, ink=1.8, seed=9)
        # units that will step into the column: pink hatch on the HP they lose; armour holds the Payload
        for u in burn:
            x, y = tok(u)
            pink_burst(L, x + 24, y - 16, 19, u['id'])
        focus_col(L, sec, thick=True)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        bill_marks(L, f_live, f_plan)
        trace_mark(L, f_live['trace'], f_plan['trace'])

    ttl = 'HOVER: FIREWALL (aimed: sector %d column)' % sec
    lines = ['pink burn band = the next 2 units entering the column burn (-1 HP)',
             'bursts: the Payload (armoured) and the 9-wide Packet that will step in',
             'lit: the column, the 2 units, bill, RAM/TRACE  |  dim: tower, other columns',
             'hand swapped for the showcase; board = approved state']
    return build(fb, f_plan, words, hand, hov, lit, marks, note=(ttl, lines))


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'brace'
    args = sys.argv[2:]
    fn = globals()[which]
    cv = lambda a: int(a) if a.lstrip('-').isdigit() else (a == 'True' if a in ('True', 'False') else a)
    im = fn(*[cv(a) for a in args]) if args else fn()
    outd = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'out')
    tag = which + ('_' + '_'.join(args) if args else '')
    im.save(os.path.join(outd, 'hover_%s.png' % tag))
    print('ok', tag)
