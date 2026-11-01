"""hv_plates2: HOVER round 2 (VISUAL_PLAN H, R51 review).  One builder per plate h01-h11 (+ variants and insets).

Grammar on every plate:
  LIT / DIM    what the hovered card touches keeps full value; everything else value x0.40, chroma x0.45
  LIFT         the hovered card grows 1.12x and sits on a pink offset print (P: hand-cut, hard edge, no glow)
  FOCUS        lime CORNER brackets only (12 px legs; 2 px = legal target, 3.5 px = the aimed target)
  PLAN         ALL hover motion and proposals are grease pencil: L6 marks and L5 arrowed outlines in PLAN yellow with ink edges
  GHOST        the thing at its new place at 74 percent with a pencil outline; the origin is veiled
  OUTCOME      L7 cross-hatch: pink = lost at this END TURN and ours, red = the enemy takes it from you
  NUMBERS      every number the plan changes is ringed in pencil on the bill (RAM coin ring, TRACE square)
Pink and orange L5 appear only in resolve, never here.
"""
import sys, os, copy, math, json, random
sys.dont_write_bytecode = True
import hv_render as R
from hv_render import *
import hv_lib as HL
import plan_patch_h as PP
from hv_lib import PINK, PLAN, HARM, SOAKC, GAIN, SCHED, ENAMEL, LIME, PAPER, INKC, VIOLET, GOLD, CYAN, TEXT_MID
import a2_kit as K2
import a2_plan as P2m
import wr2_units as WU2
import o_arcs as OA
import r2_arcs as RA
import r2_misc as M2m
import e8lib as E8m
import a2_hover as H2m
import a_hover as HVm
import build10 as B10m

HS_ = R.HS
S = HS_.S
K_DIM, DESAT = 0.40, 0.45

HAND4 = ['Brace', 'Spin3', 'Trigger', 'Twist']
BILL = (1072, 76, 1896, 270)
OBJ = (1072, 278, 1896, 330)
RAMB = (1072, 334, 1896, 386)
HEAD = (1072, 12, 1896, 68)
BEZ = (352, 388)

SLIPS = {}          # plate id -> dict(title, lines): the review slip that lives under the frame, never on the plate
rmid = lambda dep: sum(CB.ring_geom(dep)) / 2.0


def frames(cards, hand, tag, opt=None, base=None):
    f_live, _, _ = HS_.frame([], opt if False else None, 'live', base=base, hand=hand)
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


# ------------------------------------------------------------------------------------------------ FOCUS (corners only)
LEG = 12.0


def focus_slice(L, s, thick=False):
    HL.band_corners(L, 62, 160, 60 * s - 27, 60 * s + 27, w=3.5 if thick else 2.0, leg=LEG)


def focus_cell(L, u, thick=False):
    ri, ro = CB.ring_geom(u['dep'])
    a0 = 60 * u['s'] - 30
    a1 = 60 * (u['s'] + u['w'] - 1) + 30
    HL.band_corners(L, ri + 3, ro - 3, a0 + 2.5, a1 - 2.5, w=3.5 if thick else 2.0, leg=LEG)


def focus_adj(L, f, thick=False):
    a = f['adj']
    ri, ro = CB.ring_geom(a['ring'])
    HL.band_corners(L, ri + 3, ro - 3, 60 * a['s'] - 27.5, 60 * a['s'] + 27.5, w=3.5 if thick else 2.0, leg=LEG)


def focus_col(L, s, thick=False, r0=170, r1=350):
    HL.band_corners(L, r0, r1, 60 * s - 27, 60 * s + 27, w=3.5 if thick else 2.0, leg=LEG)


def focus_tag(L, d, f, thick=False):
    x, y, wd, depth, wv = M2m.tag_geom(L, d, f['rings_wave'][d], 'P')
    HL.rect_corners(L, (x - wd / 2, y - 13, x + wd / 2, y + 13), w=3.5 if thick else 2.0, leg=LEG, pad=4)


# ------------------------------------------------------------------------------------------------ wedge helpers
def wedge_poly(s, r0=46, r1=160, half=29.0):
    n = 14
    return [ppx(C, r1, 60 * s - half + 2 * half * i / n) for i in range(n + 1)] + [ppx(C, r0, 60 * s + half - 2 * half * i / n) for i in range(n + 1)]


def clamp_ghost(L, s, col=PINK):
    """L10 protection = a DOUBLE line.  P family clamp plate over the outer 40 percent of one wedge; rivets; pencil edge (= proposal)"""
    whole = wedge_poly(s, 46, 160, 29.4)
    HL.tint_poly(L, whole, col, 34)
    r0, r1, half = 124.0, 160.5, 29.6
    band = wedge_poly(s, r0, r1, half)
    HL.tint_poly(L, band, col, 200)
    for q, rr in enumerate((131.0, 141.0, 151.0)):
        HL.hand(L, HL.arc(rr, 60 * s - 25, 60 * s + 25, 14), w=4.6, col=HL.PINK_HI, ink=0.0, seed=20 + q + s, taper=True, wobble=1.0)
    for rr, w, c in ((r0, 4.6, col), (r0 - 7.6, 3.0, PAPER)):
        pts = HL.arc(rr, 60 * s - half + 0.6, 60 * s + half - 0.6, 14)
        L.line(pts, INKC, w + 3.4)
    for rr, w, c in ((r0, 4.6, col), (r0 - 7.6, 3.0, PAPER)):
        pts = HL.arc(rr, 60 * s - half + 0.6, 60 * s + half - 0.6, 14)
        L.line(pts, c, w)
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


# ------------------------------------------------------------------------------------------------ the bill: pencil-ringed numbers
def bill_marks(L, f_live, f_plan):
    """a pencil ring round each hero number the plan changes (LANDS / THROUGH).  GDD 9.2: the bill switches to plan values."""
    lv, pl = f_live['pv']['eq'], f_plan['pv']['eq']
    if not NOW['words']:
        bx = hud2.R['hero_nowords_proxy']
        yy = (bx[1] + bx[3]) / 2
        run = lambda x0, n: (x0, x0 + max(0, n - 1) * 17 + (max(0, n - 1) // 5) * 12 + 13)
        l0, l1 = run(bx[0] + 6, pl['lands'])
        t0, t1 = run(l1 + 14 + 52, pl['through'])
        if pl['through'] != lv['through']:
            HL.pencil_oval(L, (t0 + t1) / 2, yy, (t1 - t0) / 2 + 11, 27, seed=3)
        if pl['lands'] != lv['lands']:
            HL.pencil_oval(L, (l0 + l1) / 2, yy, (l1 - l0) / 2 + 11, 27, seed=4)
        return
    box = hud2.R.get('hero_pair') or (1416, 78, 1574, 168)
    th = str(pl['through'])
    tw = L.tw(th, 58, 'anton')
    cy = 128
    if pl['through'] != lv['through']:
        xt = box[2] - 8 - tw
        HL.pencil_oval(L, xt + tw / 2, cy, tw / 2 + 11, 29, seed=3)
    if pl['lands'] != lv['lands']:
        ls = str(pl['lands'])
        lw = L.tw(ls, 58, 'anton')
        HL.pencil_oval(L, box[0] + 8 + lw / 2, cy, lw / 2 + 11, 29, seed=4)


def ram_mark(L, before, after):
    for i in range(after, before):
        x, y = 1149 + 32 * i, 359
        HL.pencil_oval(L, x, y, 19, 19, seed=11 + i, w=3.2, ink=1.6)


def ram_plus(L, n_at):
    """refund: the RAM coin that comes back, a pencil plus in GAIN"""
    x, y = 1149 + 32 * n_at, 359
    L.ellipse([x - 17, y - 17, x + 17, y + 17], outline=INKC, w=6.6)
    L.ellipse([x - 17, y - 17, x + 17, y + 17], outline=GAIN, w=3.2)
    for pts in ([(x - 6, y), (x + 6, y)], [(x, y - 6), (x, y + 6)]):
        L.line(pts, INKC, 6.6)
        L.line(pts, GAIN, 3.2)


def trace_mark(L, before, after):
    for i in range(before, after):
        x, y = 1411 + 29 * i, 359
        HL.pencil_box(L, (x - 15, y - 15, x + 15, y + 15), seed=21 + i, w=3.0, ink=1.6)


def hatch_cell(L, u, col=PINK, alpha=0.55):
    poly = HL.cell_poly_unit(u)
    lay = L2()
    PP.hatch_poly(lay, poly, col, pitch=8.0, lw=2.4, base=None, edge=2.6)
    im = lay.im.copy()
    im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    L.im.alpha_composite(im)


def pink_burst(L, x, y, r=24, seed=1):
    HL.starburst(L, x, y, r, PINK, (255, 255, 255), 11, 2.6, seed)


def pc(L, pts, w=13, head=19, **kw):
    """a PLAN L5 arrowed outline: the one motion mark of every hover"""
    HL.channel(L, pts, col=PLAN, w=w, head=head, chev=True, fill=kw.pop('fill', (10, 8, 20, 190)), **kw)


# ------------------------------------------------------------------------------------------------ assembler
def build(f_board, f_hud, words, hand, hov, lit_fn, marks_fn, ghosts=None, veil=None, hide=(), arcs_skip=(), slip=None, other_dim=0.7, played=None, pid=None,
          post_fn=None):
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
    marks.append(Lm.done())
    hand_lay, hov_info = R.hand_layers(words, hand, hov, played=played)
    stick = R.sticker_layer(words)
    img = R.compose(bg, hud, mask, marks, hand_lay, stick, k=K_DIM, desat=DESAT)
    if post_fn:
        img = post_fn(img, words)
    if slip and pid:
        SLIPS[pid] = dict(title=slip[0], lines=slip[1])
    return img


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
        # the block result on its landing arc: a pencil bar across the arc that now stops at the clamp
        for it in RA.layout_items(f_plan):
            u = it['u']
            for q in range(u['w']):
                sec = (it['s0'] + q) % 6
                if u.get('land_brace', {}).get(str(sec)):
                    r = OA.LANE_R[min(it['lane'], 2)]
                    HL.pencil(L, HL.arc(r + 21, 60 * sec - 18, 60 * sec + 18), w=4.0, ink=2.0, seed=sec)

    slip = ('HOVER: BRACE  (h02, protect a slice)',
            ['aimed: the slice at sector %d (TURRET); the bill shows the plan: THROUGH %d -> %d' % (aim, f_live['pv']['eq']['through'], f_plan['pv']['eq']['through']),
             'lit: all six slices (legal), the landing arcs, bill, RAM   |   dim: rings, queue, header, objectives',
             'marks: lime corners on every slice, thick on the aimed one; clamp plate ghost with the L10 double edge; pencil bar on the arc that now stops',
             'hand: the approved state hand'])
    return build(fb, f_plan, words, hand, 0, lit, marks, slip=slip, pid='h02_brace')


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
        # the tower turns n sectors clockwise: one PLAN L5 arc round the hub, a pencil rim on the tower at its plan angle
        a0 = 8.0
        a1 = a0 + 60 * n - 16
        pc(L, HL.arc(64, a0, a1, 40), w=13, head=20)
        HL.pencil(L, HL.arc(167.5, 0.5, 359.5, 120), w=2.8, ink=1.6, grain=True, cap=False, seed=7)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        bill_marks(L, f_live, f_plan)

    slip = ('HOVER: %s  (h01, turn the tower %d)' % (card.upper(), n),
            ['the tower is drawn at the plan angle (clockwise x%d); the pencil rim = proposal; the PLAN arc shows the turn' % n,
             'guns, tracers and landing marks are at plan values: THROUGH %d -> %d' % (f_live['pv']['eq']['through'], f_plan['pv']['eq']['through']),
             'lit: tower, ring NOW, guns and targets, arcs, bill   |   dim: rings +1 / +2, queue']
            + (['hand swapped for the showcase; board = approved state'] if showcase else []))
    return build(f_plan, f_plan, words, hand, hov, lit, marks, slip=slip, pid='h01_tower_turn' if card == 'Spin3' else 'h01_' + card.lower())


# ================================================================================================ h03 Trigger
def trigger(words=True, variant='f1'):
    hand = HAND4
    if variant == 'f1':
        f_live, f_plan = frames([('Trigger', 4)], hand, 'trigger')
    else:
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
        for e in kills:
            sec = e[1]
            ang = 60 * sec + 13
            r0 = CB.ring_geom(tgt['dep'])[1] - 6
            r1 = CB.ring_geom(0)[0] + 30
            pc(L, [ppx(C, r0, ang), ppx(C, r1, ang)], w=13, head=19, fill=(10, 8, 20, 200), tail_dot=True)
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

    slip = ('HOVER: TRIGGER  (h03, resolve a unit now; aimed: Payload, ring +1)%s' % ('  AFTER TWIST' if variant == 'f2' else ''),
            ['pencil arrows = the Payload resolves NOW down sectors 3 and 4; the lime corners mark the other legal units',
             'pink hatch = the Packet is lost this END TURN (ours); pink burst = the kill; the kill refunds 1 RAM (coin with plus)',
             'pencil ring on the numbers the plan changes; pencil square = the TRACE the card adds',
             'lit: legal units, the victim, slices 3-4, bill, RAM / TRACE   |   dim: everything else']
            + (['shown after TWIST (approved best line f2): the refund is live'] if variant == 'f2' else []))
    pid = 'h03_trigger' if variant == 'f1' else 'h03_trigger_after_twist'
    if variant == 'f2':
        return build(fb, f_plan, words, ['Brace', 'Spin3', 'Trigger'], 2, lit, marks, arcs_skip={1, 4}, slip=slip, played=['Twist'], pid=pid)
    return build(fb, f_plan, words, hand, 2, lit, marks, arcs_skip={1, 4}, slip=slip, pid=pid)


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
        r = rmid(ring)
        a_mid = 60 * 1 if ring == 1 else 60 * 0
        pts = HL.arc(r, a_mid - 24 * d, a_mid + 24 * d, 20)
        pc(L, pts, w=16, head=22)
        P2m.twist_badge(L, f_plan, 'A')
        ro = 2 if ring == 1 else 1
        focus_tag(L, ro, f_plan)
        focus_tag(L, ring, f_plan, thick=True)
        bill_marks(L, f_live, f_plan)

    ghosts = []
    La = L2()
    A2.landing_arcs(La, f_plan, {}, only=veil_ids)
    ghosts.append(La.done())
    Lo = L2()
    for it in RA.layout_items(f_plan, veil_ids):
        r = OA.LANE_R[min(it['lane'], 2)]
        HL.pencil(Lo, HL.arc(r + OA.HALF + 4, it['a0'] + 4, it['a1'] - 2), w=3.4, ink=1.8, seed=it['u']['id'], cap=False)
    ghosts.append(Lo.done())
    slip = ('HOVER: TWIST  (h04, turn one ring; aimed: ring +1, clockwise)',
            ['PLAN arrow along ring +1 = the ring turns one extra sector at END TURN; the twist pill on the ring tag is the plan badge',
             'pencil-edged arcs = the landings after the twist (Payload %s, Packet %s)' % (
                 uby(f_plan, 4)['land_sectors'], uby(f_plan, 5)['land_sectors']),
             'lime corners on the two legal ring tags, thick on the aimed ring',
             'lit: rings +1 / +2, bezel, arcs, bill   |   dim: ring NOW, tower'])
    return build(f_live, f_plan, words, hand, 3, lit, marks, ghosts=ghosts, arcs_skip=veil_ids, slip=slip, pid='h04_twist')


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

    slip = ('HOVER: STRIKE  (h05, damage a unit; aimed: Packet, ring +1, 2 HP)',
            ['pink hatch = both HP of the Packet are lost this END TURN (ours); pink burst and speed lines = the hit; its landing arc is gone',
             'lime corners on every unit in range (legal), thick on the aimed Packet',
             'lit: every unit in range, arcs, bill   |   dim: tower, schedule',
             'hand swapped for the showcase; board = approved state'])
    return build(fb, f_plan, words, hand, hov, lit, marks, arcs_skip={aim}, slip=slip, pid='h05_strike')


# ================================================================================================ h06 Shove
def shove(words=True, uid=5, d=1, bump=False):
    hand, hov = hand_of('Shove')
    f_live, f_plan = frames([('Shove', (uid, d))], hand, 'shove')
    u0 = uby(f_live, uid)
    u1 = uby(f_plan, uid)
    fb = copy.deepcopy(f_live)
    ghosts = []
    veil = None
    nb = None
    if bump:
        occ = {(u0['s'] + u0['w'] - 1 + 1) % 6} if u0['w'] > 1 else set((u0['s'] + d * (i + 1)) % 6 for i in range(1))
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

    BUMP = {}

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
            pc(L, HL.arc(r, a_from + d * sh, a_to - d * sh, 24), w=14, head=20)
        else:
            a_edge = 60 * (u0['s'] + u0['w'] - 1 + (0.5 if d > 0 else -0.5)) if d > 0 else 60 * (u0['s'] - 0.5)
            pc(L, HL.arc(r, a_edge - 44 * d, a_edge + 8 * d, 16), w=14, head=20)
            bx, by = ppx(C, r, a_edge + 12 * d)
            BUMP['xy'] = (bx, by)
            pink_burst(L, bx, by, 24, 2)
        focus_cell(L, u0, thick=True)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        bill_marks(L, f_live, f_plan)
        trace_mark(L, f_live['trace'], f_plan['trace'])

    slip = ('HOVER: SHOVE  (h06, move a unit sideways; aimed: %s%s)' % (u0['kind'], ' bumps its neighbour' if bump else ', one sector clockwise'),
            (['PLAN arrow = the unit slides one sector; the ghost with the pencil edge is its new cell and new landing arc; the origin is veiled'] if not bump else
             ['pink burst = the collision: both units lose 1 HP and neither moves; pink hatch = the 1 HP each loses at this END TURN (ours)']) +
            ['lime corners on the other units on rings NOW and +1, thick on the aimed unit',
             'lit: rings NOW and +1, the Adjuster, arcs, bill, RAM / TRACE   |   dim: ring +2, schedule',
             'hand swapped for the showcase; board = approved state'])
    img = build(fb, f_plan, words, hand, hov, lit, marks, ghosts=ghosts, veil=veil, arcs_skip={uid} if not bump else (), slip=slip,
                pid='h06_shove' if not bump else 'h06_shove_bump')
    if bump:
        img.info_xy = BUMP.get('xy')
    return img


# ================================================================================================ h07 Pull
def pull(words=True, uid=7):
    hand, hov = hand_of('Pull')
    f_live, f_plan = frames([('Pull', uid)], hand, 'pull')
    u0 = uby(f_live, uid)
    ghosts = [R.ghost_units(f_plan, {uid}, words)]
    veil = R.veil_cells(f_live, {uid}, 0.6)

    def lit(Lt):
        lit_cells(Lt, f_live, {uid})
        lit_cells(Lt, f_plan, {uid})
        lit_arcs_of(Lt, f_plan, {uid})
        lit_arcs_of(Lt, f_live, {uid})
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        a = 60 * u0['s'] + 19
        r_in = rmid(1) + 10
        r_out = CB.ring_geom(2)[1] - 3
        pc(L, [ppx(C, r_out, a), ppx(C, r_in, a)], w=16, head=24, fill=(10, 8, 20, 200))
        focus_cell(L, u0, thick=True)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        bill_marks(L, f_live, f_plan)
        trace_mark(L, f_live['trace'], f_plan['trace'])

    slip = ('HOVER: PULL  (h07, move a unit inward; the only legal unit: Packet, ring +2)',
            ['PLAN arrow = the unit moves one ring inward (it now enters ring +1); the ghost with the pencil edge is its new cell; its landing arc moves a turn nearer',
             'no other unit has a free inner cell, so the rest stay dim and get no corners',
             'lit: the unit, its destination, its two arcs, bill, RAM / TRACE   |   dim: everything else',
             'hand swapped for the showcase; board = approved state'])
    return build(f_live, f_plan, words, hand, hov, lit, marks, ghosts=ghosts, veil=veil, arcs_skip={uid}, slip=slip, pid='h07_pull')


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
        # the step slides one slot later: a PLAN arrow just outside the bezel; the live cell becomes a HOLD cell: pencil outline round it
        pc(L, HL.arc(398, 66, 104, 20), w=13, head=19, fill=(10, 8, 20, 200))
        HL.pencil(L, HL.arc(386, 1.5, 38.5, 16), w=3.4, ink=1.8, seed=5, cap=False)
        HL.pencil(L, HL.arc(351, 1.5, 38.5, 16), w=3.4, ink=1.8, seed=6, cap=False)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        bill_marks(L, f_live, f_plan)

    slip = ('HOVER: HOLD  (h08, stop the rings this turn)',
            ['schedule 2 . 0 . 0  ->  0 . 2 . 0: the step slides one slot later (PLAN arrow outside the bezel); the live cell becomes a HOLD cell (pencil outline)',
             'landing arcs are recomputed at plan value (Payload and Packet land elsewhere)',
             'lit: bezel, all rings, arcs, bill   |   dim: tower interior, the rest',
             'hand swapped for the showcase; board = approved state'])
    return build(f_plan, f_plan, words, hand, hov, lit, marks, slip=slip, pid='h08_hold')


# ================================================================================================ h09 Firewall
def firewall(words=True, sec=0):
    hand, hov = hand_of('Firewall')
    f_live, f_plan = frames([('Firewall', sec)], hand, 'firewall')
    burn = [uby(f_live, 4), uby(f_live, 6)]
    fb = copy.deepcopy(f_live)
    uby(fb, 6)['lose'][1] += 1

    def lit(Lt):
        Lt.sector(sec, 160, 354, 31, 3)
        lit_cells(Lt, f_live, {4, 6})
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        for s in range(6):
            if s not in (sec,) and f_live['fw'][s] == 0 and s in (0, 1, 2, 4, 5):
                focus_col(L, s)
        poly = [ppx(C, 354, 60 * sec - 28 + 56 * i / 20) for i in range(21)] + [ppx(C, 163, 60 * sec + 28 - 56 * i / 20) for i in range(21)]
        HL.tint_poly(L, poly, PINK, 38)
        # the flame band, drawn as a proposal: four wavy pencil strokes up the column, then the pencil outline
        for q, off in enumerate((-17, -6, 6, 17)):
            pts = []
            for i in range(30):
                r = 176 + (172) * i / 29
                wob = math.sin(i * 0.9 + q * 1.7) * 3.4
                pts.append(ppx(C, r, 60 * sec + off + wob / r * 57.3))
            HL.pencil(L, pts, w=4.6, ink=2.0, seed=11 + q, grain=True, cap=False)
        HL.pencil_poly(L, poly, w=3.0, ink=1.8, seed=9)
        for u in burn:
            x, y = tok(u)
            pink_burst(L, x + 24, y - 16, 19, u['id'])
        focus_col(L, sec, thick=True)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        bill_marks(L, f_live, f_plan)
        trace_mark(L, f_live['trace'], f_plan['trace'])

    slip = ('HOVER: FIREWALL  (h09, burn a sector; aimed: the sector-%d column)' % sec,
            ['pink wash + pencil flame strokes = the next 2 units entering the column burn (-1 HP); lime corners on the other legal columns',
             'bursts: the armoured Payload (loses 0) and the 9-wide Packet that steps in (pink hatch on the HP it loses)',
             'lit: the column, the two units, bill, RAM / TRACE   |   dim: tower, other columns',
             'hand swapped for the showcase; board = approved state'])
    return build(fb, f_plan, words, hand, hov, lit, marks, slip=slip, pid='h09_firewall')


# ================================================================================================ h10 soak toggle
def soak(words=True, idx=1):
    """END TURN soak toggle (not a card): hover a slice's soak and its funnel appears; the hatch on the pip and the HP saved show on the YOU strip"""
    hand = HAND4
    f_live, _, _ = HS_.frame([], None, 'live', hand=hand)
    f_plan, st, pv = HS_.frame([], [idx], 'soak', hand=hand)
    sec = [w['sector'] for w in f_plan['wheel'] if w['soak']][0]

    def lit(Lt):
        lit_tower(Lt)
        lit_arcs_of(Lt, f_plan)
        Lt.box(1072, 76, 1560, 270, 8)       # the bill's YOU / SOAK / SPLIT block
        lit_bill(Lt)

    def marks(L):
        for s in range(6):
            if s != sec:
                focus_slice(L, s)
        # the funnel ghost on the hovered slice: a SOAK trapezoid narrowing inward from the rim (outside the icon), chevrons pointing in, pencil edge = proposal
        HL.tint_poly(L, wedge_poly(sec, 46, 160, 29.4), SOAKC, 40)
        a = 60 * sec
        band = [ppx(C, 160, a - 27 + 54 * i / 16) for i in range(17)] + [ppx(C, 145, a + 27 - 54 * i / 16) for i in range(17)]
        HL.tint_poly(L, band, SOAKC, 235)
        L.line(band + [band[0]], INKC, 3.6)
        L.line(HL.arc(147.5, a - 25.5, a + 25.5, 14), (160, 196, 255), 1.6)
        for da in (-15, 0, 15):
            ch = [ppx(C, 141, a + da - 6), ppx(C, 128, a + da), ppx(C, 141, a + da + 6)]
            L.line(ch, INKC, 8.0)
            L.line(ch, PAPER, 3.6)
        HL.pencil_poly(L, wedge_poly(sec, 44, 163, 30.2), w=2.8, ink=1.8, seed=sec + 3)
        focus_slice(L, sec, thick=True)
        bill_marks(L, f_live, f_plan)
        # the HP the soak saves: a pencil ring round the YOU strip's pending run
        hp_l, hp_p = f_live['pv']['hp_after'], f_plan['pv']['hp_after']
        if hp_p != hp_l:
            HL.pencil_box(L, (1308, 107, 1394, 137), seed=31, pad=4)

    slip = ('HOVER: SOAK  (h10, END TURN soak toggle; hovered: the slice at sector %d)' % sec,
            ['SOAK indigo funnel on the hovered slice = this slice takes the overflow; the pip inside hatches in SOAK indigo (lost at END TURN, your choice)',
             'bill at plan values: THROUGH %d -> %d; the pencil box on the YOU strip = the HP the soak saves (%d -> %d after the turn)' % (
                 f_live['pv']['eq']['through'], f_plan['pv']['eq']['through'], f_live['pv']['hp_after'], f_plan['pv']['hp_after']),
             'lit: tower, landing arcs, the bill   |   dim: rings, queue, cards idle',
             'no card is lifted: the toggle is an END TURN choice, so the hand only dims'])
    return build(f_plan, f_plan, words, hand, None, lit, marks, slip=slip, pid='h10_soak')


# ================================================================================================ h11 unit hover
def unit(words=True, uid=6):
    """hover a unit (the kept p2b form): pencil route, lime corners on the cell, the slices it lands on, the E10 hover tag (content parked)"""
    hand = HAND4
    f, _, _ = HS_.frame([], None, 'live', hand=hand)
    u = uby(f, uid)
    hv = B10m.J['hover']
    path = hv['path']
    land = [h[0] for h in hv['fate']['hits']]
    pts = []
    for i in range(len(path) - 1):
        (d0, s0), (d1, s1) = path[i], path[i + 1]
        r0, r1 = rmid(d0), rmid(d1)
        a0, a1 = 60 * s0, 60 * s1
        if a1 < a0:
            a1 += 360
        for j in range(0 if i == 0 else 1, 21):
            t = j / 20
            pts.append(ppx(C, r0 + (r1 - r0) * t, a0 + (a1 - a0) * t))
    cells = set()
    for (d_, s_) in path:
        cells.add((d_, s_))

    def lit(Lt):
        lit_cells(Lt, f, {uid})
        for s in land:
            Lt.sector(s, 40, 163, 30, 2)
        # the cells along the route
        for (d_, s_) in path:
            ri, ro = CB.ring_geom(d_)
            Lt.sector(s_, ri - 1, ro + 1, 30, 1)
        lit_arcs_of(Lt, f, {uid})
        lit_bill(Lt)
        Lt.box(1088, 400, 1500, 560, 8)

    def marks(L):
        pc(L, pts, w=13, head=19, tail_dot=True)
        # slices it lands on: a pencil rim arc in the trim slot
        for s in land:
            HL.pencil(L, HL.arc(139.5, 60 * s - 25, 60 * s + 25, 14), w=4.4, ink=2.0, seed=s + 40, cap=False)
        focus_cell(L, u, thick=True)

    def post(img, words_):
        Lx = L2()
        NOW['words'] = words_
        if words_:
            H2m.hover_tag(Lx, f, 'A')
        else:
            H2m.hover_tag_nowords(Lx, f)
        im = img.convert('RGBA')
        im.alpha_composite(Lx.done())
        return im.convert('RGB')

    slip = ('HOVER: UNIT  (h11, inspect a unit: the kept p2b form; Packet x3 on ring +2)',
            ['PLAN arrow = the unit\'s route inward; it lands on the pencil-marked slices; thick lime corners on its cell; the pencil leader joins the cell to its tag',
             'the hover tag keeps its E10 form and content (designer note 8: content rulings parked)',
             'lit: the unit, its route, the slices it lands on, its arcs, the bill   |   dim: everything else; the hand idles'])
    return build(f, f, words, hand, None, lit, marks, arcs_skip=(), slip=slip, pid='h11_unit', post_fn=post)


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'brace'
    args = sys.argv[2:]
    fn = globals()[which]
    cv = lambda a: int(a) if a.lstrip('-').isdigit() else (a == 'True' if a in ('True', 'False') else a)
    im = fn(*[cv(a) for a in args]) if args else fn()
    outd = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'out')
    tag = which + ('_' + '_'.join(args) if args else '')
    im.save(os.path.join(outd, 'v2_%s.png' % tag))
    print('ok', tag)
