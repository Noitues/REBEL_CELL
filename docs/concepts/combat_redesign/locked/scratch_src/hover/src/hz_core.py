"""hz_core: hover plates (roadmap step 5) on the FINAL locked board (O-29 fix pass).
Board, tower, cards, HUD and skins come from the locked generator (lw_render -> f1_render._render); this module only adds:
  frames      live and plan frames from the E10 sim (hover_sim, read only): every ghost and landing is the sim's plan frame, never a shifted copy
  dim         value x0.40, chroma x0.45 outside the lit mask; the hand not in play at 70 percent; UNDO / SEND IT / nameplate at 62 percent
  marks       FOCUS corners (lime), PLAN arrowed outlines and pencil marks (PLAN yellow), ghosts at 74 percent with a pencil edge
  checks      draw asserts (board frame + ghost arcs vs the plan frame), collision + occluder check with the hover marks as their own classes, dash audit
Env CORP=neutral|solace|meridian selects the skin (installed at import by lw_render)."""
import sys, os, copy, json, math, hashlib
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np

HERE = 'D:/rc_scratch/combat_redesign/locked/hover/'
TEXTLOG = []
_otext = ImageDraw.ImageDraw.text


def _t(self, xy, text, *a, **k):
    TEXTLOG.append(str(text))
    return _otext(self, xy, text, *a, **k)


ImageDraw.ImageDraw.text = _t

import lw_render as LW
R = LW.R
A = R.A
FH = R.FH
B10 = A.B10
import hover_sim as HS
import hv_lib_h2 as HL
from hv_lib_h2 import PINK, PLAN, HARM, SOAKC, GAIN, LIME, PAPER, INKC
from cv_lib import C, W, H, L2, ppx, NOW
import cv_board as CB
import r2_arcs as RA
import r2_misc as M2m
import a2_plan as P2m
import a2_kit as K2
import a2_hover as H2m
import asm_units as AU
import hud2
import card_render as CR

S = HS.S
CORP = os.environ.get('CORP', 'neutral')
K_DIM, DESAT = 0.40, 0.45
HAND_K = 0.70            # the cards not in play
STICK_K = 0.62           # UNDO, SEND IT, nameplate while a card is hovered
GHOST_A = 0.74
H4 = ['Brace', 'Spin3', 'Trigger', 'Twist']

# HUD boxes (final board, measured on the rendered plates)
BILL = (1072, 76, 1896, 270)
RAMB = (1072, 334, 1896, 386)
HEAD = (1072, 12, 1896, 68)
YOU = (1072, 98, 1410, 150)
RAM_X0, RAM_DX, RAM_Y = 1149.5, 31.9, 359.0
TR_X0, TR_DX = 1439.5, 28.1

# tower and board radii (final board)
T_IN, T_OUT, T_PAGE, T_HALO = 71.0, 177.0, 192.0, 197.2
BAND = (391.0, 417.0)
LANES = RA.LANE_R            # [436, 453, 470] (set by f1_render)
HALF = RA.HALF
rmid = lambda dep: sum(CB.ring_geom(dep)) / 2.0

# ------------------------------------------------------------------------------------------------ checks: mask capture (as asm_render), switchable
MASKS = {}
LOGD = []
CAP = {'on': True}


def AD(name, got, want):
    LOGD.append(dict(name=name, ok=bool(got == want), got=str(got), want=str(want)))


B10.AD = AD


def _cap(cls, owner, fn_name, Lidx=0):
    orig = getattr(owner, fn_name)

    def wrap(*a, **k):
        if not CAP['on']:
            return orig(*a, **k)
        L = a[Lidx]
        T = L2()
        a2 = list(a)
        a2[Lidx] = T
        r = orig(*a2, **k)
        L.im.alpha_composite(T.im)
        m = np.asarray(T.im.split()[3].resize((W, H), Image.BOX)) >= 128
        MASKS[cls] = MASKS.get(cls, np.zeros((H, W), bool)) | m
        return r
    setattr(owner, fn_name, wrap)


_cap('digits', A.S2, 'digits')
_cap('labels', A.S2, 'labels')
_cap('tags', A.M2, 'ring_tags')
_cap('tags', A.P2, 'refund_place')
_cap('badges', A.P2, 'twist_badge')
_cap('badges', A.AU, 'warded_badge')
_cap('badges', A.AU, 'dead_badge')
_cap('tags', A.H2, 'hover_tag')
_cap('tags', A.H2, 'hover_tag_nowords')
_cap('leader', A.H2, 'leader')
_cap('tickets', A.M2, 'future')
_cap('tape', A.S2, 'live_cell')
_cap('tape', A.S2, 'live_label')
_cap('tape', A.S2, 'chevrons')
_cap('plates', A.S2, 'hold_cell')
_cap('plates', A.S2, 'hold_live')
_cap('plates', A.S2.S, 'plus_cell')
_cap('arcs', RA, 'landing_arcs')
R.A2 = RA
_cap('units', R, 'draw_units')
MARKS = ('digits', 'labels', 'tags', 'badges', 'tickets', 'leader')
OCCLUDERS = ('tape', 'plates', 'hand')
HOVER_CLASSES = ('hover', 'ghost', 'inset')
ALLOWED = {('labels', 'plates'), ('leader', 'tape'), ('leader', 'plates')}


def reset_checks():
    GHOST_ARCS.clear() if 'GHOST_ARCS' in globals() else None
    CORNER_LOG.clear() if 'CORNER_LOG' in globals() else None
    MASKS.clear()
    LOGD.clear()
    TEXTLOG.clear()
    del R.DASH_LOG[:]
    del R.DOT_LOG[:]
    A.AU.BADGE_LOG.clear()


def add_mask(cls, rgba, thr=128):
    m = np.asarray(rgba.split()[3]) >= thr
    MASKS[cls] = MASKS.get(cls, np.zeros((H, W), bool)) | m


# ------------------------------------------------------------------------------------------------ frames
def frames(cards, hand, opt=None):
    f_live, _, _ = HS.frame([], None, 'live', hand=hand)
    f_plan, st, pv = HS.frame(cards, opt, 'plan', hand=hand)
    return f_live, f_plan


def uby(f, uid):
    return [u for u in f['units'] if u['id'] == uid][0]


def fw_hits(cards, hand):
    """Firewall burns, with the unit id: the sim's hurt() wrapped during the plan preview"""
    out = []
    oh = S.hurt

    def hurt(st, d, u, n, src):
        r = oh(st, d, u, n, src)
        if src == 'fw':
            out.append(dict(uid=u['id'], kind=u['kind'], hp_lost=r, ring=d))
        return r
    S.hurt = hurt
    try:
        HS.frame(cards, None, 'fwprobe', hand=hand)
    finally:
        S.hurt = oh
    return out


def as_dying(u, lost=None, cause='ours'):
    """display a unit the plan removes: HP lost at THIS END TURN (hatched by the board's own HP grammar), no landing arc"""
    u = copy.deepcopy(u)
    hp_lost = u['hp'] if lost is None else lost
    u['lose'] = [0, hp_lost]
    u['fate'] = dict(kind='dies', k=0, hits=[], tohp=0)
    for k in ('land_hit', 'land_sectors', 'land_through', 'land_soak', 'land_brace', 'land_abs', 'wear', 'jam'):
        u.pop(k, None)
    u['consumed'] = False
    u['trigdead'] = False
    return u


def as_waiting(u):
    u = copy.deepcopy(u)
    u['fate'] = dict(kind='waits', k=None, hits=[], tohp=0)
    for k in ('land_hit', 'land_sectors', 'land_through', 'land_soak', 'land_brace', 'land_abs', 'wear', 'jam'):
        u.pop(k, None)
    u['consumed'] = False
    u['trigdead'] = False
    return u


def replace_unit(f, u):
    f['units'] = [u if x['id'] == u['id'] else x for x in f['units']]


def ftag(f, extra=''):
    return 'hz_' + hashlib.md5((json.dumps(f, sort_keys=True, default=str) + extra).encode()).hexdigest()[:12]


# ------------------------------------------------------------------------------------------------ lit mask helpers
def _annulus_or(self, r0, r1, c=C):
    """lit annulus that ADDS to the mask (hv_lib's version clears the inner disc, which erased earlier lit regions)"""
    s_ = self.ss
    m = Image.new('L', self.im.size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse([(c[0] - r1) * s_, (c[1] - r1) * s_, (c[0] + r1) * s_, (c[1] + r1) * s_], fill=255)
    d.ellipse([(c[0] - r0) * s_, (c[1] - r0) * s_, (c[0] + r0) * s_, (c[1] + r0) * s_], fill=0)
    self.im = ImageChops.lighter(self.im, m)
    self.d = ImageDraw.Draw(self.im)


HL.Lit.annulus = _annulus_or


def lit_tower(Lt, r=T_HALO + 3):
    Lt.disc(r)


def lit_arcs_of(Lt, f, ids=None, pad=4):
    for it in RA.layout_items(f, ids):
        r = LANES[min(it['lane'], 2)]
        Lt.wedge(r - HALF - 6, r + HALF + 6, it['a0'] - pad, it['a1'] + pad, 2)


def lit_cells(Lt, f, ids, grow=5):
    for u in f['units']:
        if u['id'] in ids and u['w'] < 6:
            Lt.poly(HL.cell_poly_unit(u), grow)


def lit_ring(Lt, dep, pad=2):
    ri, ro = CB.ring_geom(dep)
    Lt.annulus(ri - pad, ro + pad)


def lit_adjuster(Lt, f):
    a = f['adj']
    ri, ro = CB.ring_geom(a['ring'])
    Lt.sector(a['s'], ri - 2, ro + 2, 31, 2)


def lit_bill(Lt):
    Lt.box(*BILL, r=8)


def lit_res(Lt):
    Lt.box(*RAMB, r=8)


def lit_head(Lt):
    Lt.box(*HEAD, r=8)


def lit_guns(Lt, f):
    for g in f['guns']:
        p0 = ppx(C, 150, 60 * g['sector'])
        for uid in {x['uid'] for x in g['shots'] if x['uid'] is not None}:
            if uid == 0:
                a = f['adj']
                tp = ppx(C, rmid(a['ring']), 60 * a['s'])
                lit_adjuster(Lt, f)
            else:
                u = uby(f, uid)
                if u['consumed'] or u['trigdead']:
                    continue
                tp = AU.token_pos(u)
                lit_cells(Lt, f, {uid})
            Lt.line(p0, tp, 26)


# ------------------------------------------------------------------------------------------------ FOCUS corners
LEG = 12.0


CORNER_LOG = []


def _forbid(strict):
    m = np.zeros((H, W), bool)
    for c in MARKS + (('units',) if strict else ()):
        if c in MASKS:
            m |= MASKS[c]
    return m


def safe_corners(L, ri, ro, a0, a1, w=2.0, leg=LEG, tag=''):
    """FOCUS corners on a ring band, one corner at a time: a corner that would touch a board mark (digit, label, tag, badge, ticket) or a unit
    slides inward along the band (up to 12 deg / 8 px); if it never clears, it is left out and logged"""
    forb_s, forb = _forbid(True), _forbid(False)
    for r, dr in ((ri, 1), (ro, -1)):
        for a, da in ((a0, 1), (a1, -1)):
            done = False
            for forbid, lab in ((forb_s, 'clear'), (forb, 'over_unit')):
                for k in range(0, 9):
                    rr = r + dr * k * 1.0
                    aa = a + da * k * 1.5
                    T = L2()
                    poly = [ppx(C, rr + dr * leg, aa), ppx(C, rr, aa)] + [ppx(C, rr, aa + da * math.degrees(leg / rr) * i / 4) for i in range(1, 5)]
                    HL._ink_then(T, [poly], LIME, w)
                    im = T.done()
                    m = np.asarray(im.split()[3]) >= 40
                    if not (m & forbid).any():
                        L.im.alpha_composite(T.im)
                        CORNER_LOG.append(dict(tag=tag, r=round(r), a=round(a, 1), slide=k, ok=lab))
                        done = True
                        break
                if done:
                    break
            if not done:
                CORNER_LOG.append(dict(tag=tag, r=round(r), a=round(a, 1), slide=None, ok='dropped'))


def focus_slice(L, s, thick=False):
    HL.band_corners(L, T_IN + 4, T_PAGE - 4, 60 * s - 26.5, 60 * s + 26.5, w=3.5 if thick else 2.0, leg=LEG)


def focus_cell(L, u, thick=False):
    ri, ro = CB.ring_geom(u['dep'])
    a0 = 60 * u['s'] - 30
    a1 = 60 * (u['s'] + u['w'] - 1) + 30
    safe_corners(L, ri + 3.5, ro - 3.5, a0 + 2.5, a1 - 2.5, w=3.5 if thick else 2.0, tag='unit %d' % u['id'])


def focus_adj(L, f, thick=False):
    a = f['adj']
    ri, ro = CB.ring_geom(a['ring'])
    safe_corners(L, ri + 3.5, ro - 3.5, 60 * a['s'] - 27.5, 60 * a['s'] + 27.5, w=3.5 if thick else 2.0, tag='adjuster')


def focus_col(L, s, thick=False, r0=T_HALO + 4, r1=CB.ring_geom(2)[1] - 6):
    safe_corners(L, r0, r1, 60 * s - 21.5, 60 * s + 21.5, w=3.5 if thick else 2.0, tag="column %d" % s)


def tag_box(d, f):
    L = L2()
    x, y, wd, depth, wv = M2m.tag_geom(L, d, f['rings_wave'][d], 'P')
    return (x - wd / 2, y - 13, x + wd / 2, y + 13)


def focus_tag(L, d, f, thick=False):
    HL.rect_corners(L, tag_box(d, f), w=3.5 if thick else 2.0, leg=10, pad=5)


# ------------------------------------------------------------------------------------------------ PLAN marks
def pc(L, pts, w=13, head=19, **kw):
    """PLAN L5 arrowed outline: the one motion mark of every hover (yellow edges, ink keyline, dark floor, chevrons)"""
    HL.channel(L, pts, col=PLAN, w=w, head=head, chev=True, fill=kw.pop('fill', (10, 8, 20, 200)), **kw)


def hud_xy():
    return dict(hero=hud2.R.get('hero_pair'), hero_nw=hud2.R.get('hero_nowords_proxy'))


def bill_marks(L, f_live, f_plan, words):
    """a pencil ring round each hero number the plan changes (LANDS / THROUGH).  GDD 9.2: the bill shows plan values."""
    lv, pl = f_live['pv']['eq'], f_plan['pv']['eq']
    out = []
    if not words:
        bx = hud2.R.get('hero_nowords_proxy')
        if not bx:
            return out
        yy = (bx[1] + bx[3]) / 2
        run = lambda x0, n: (x0, x0 + max(0, n - 1) * 17 + (max(0, n - 1) // 5) * 12 + 13)
        l0, l1 = run(bx[0] + 6, pl['lands'])
        t0, t1 = run(l1 + 14 + 52, pl['through'])
        if pl['through'] != lv['through']:
            HL.pencil_oval(L, (t0 + t1) / 2, yy, (t1 - t0) / 2 + 11, 24, seed=3); out.append('through')
        if pl['lands'] != lv['lands']:
            HL.pencil_oval(L, (l0 + l1) / 2, yy, (l1 - l0) / 2 + 11, 24, seed=4); out.append('lands')
        return out
    box = hud2.R.get('hero_pair')
    cy = (box[1] + box[3]) / 2 + 7
    if pl['through'] != lv['through']:
        tw = L.tw(str(pl['through']), 58, 'anton')
        xt = box[2] - 8 - tw
        HL.pencil_oval(L, xt + tw / 2, cy, tw / 2 + 13, 24, seed=3); out.append('through')
    if pl['lands'] != lv['lands']:
        lw = L.tw(str(pl['lands']), 58, 'anton')
        HL.pencil_oval(L, box[0] + 6 + lw / 2, cy, lw / 2 + 13, 24, seed=4); out.append('lands')
    return out


def you_pip_x(i):
    g, k = divmod(i, 5)
    return 1068 + 72 + g * (5 * 15.6 + 8) + k * 15.6        # lw_ui.you_strip: xs + group + pitch; pip 12.6 x 17 at y 123


def you_mark(L, f_live, f_plan):
    """the YOU strip's HP after the turn changes: a pencil ring round exactly the pips that change (kept <-> lost at END TURN)"""
    a, b = sorted((f_live['pv']['hp_after'], f_plan['pv']['hp_after']))
    if a == b:
        return False
    x0, x1 = you_pip_x(a), you_pip_x(b - 1) + 12.6
    HL.pencil_oval(L, (x0 + x1) / 2, 123, (x1 - x0) / 2 + 9, 17, seed=31, w=3.0, ink=1.6)
    return [a, b]


def _pip_x(kind, i):
    """pip centres from the HUD's own registry (obj2.resources_row: ram_pips / trace_pips boxes, RAM_P 32, TR_P 28)"""
    import obj2
    if kind == 'ram':
        b = obj2.R['ram_pips']
        return b[0] + 4 + 13.8 + i * obj2.RAM_P, (b[1] + b[3]) / 2
    b = obj2.R['trace_pips']
    return b[0] + 4 + 12.8 + i * obj2.TR_P, (b[1] + b[3]) / 2


def ram_mark(L, before, after):
    for i in range(after, before):
        x, y = _pip_x('ram', i)
        HL.pencil_oval(L, x, y, 18.5, 18.5, seed=11 + i, w=3.2, ink=1.6)


def ram_plus(L, n_at):
    """refund: the HUD already draws the refunded coin (plus and rays); the plan rings it in GAIN pencil"""
    x, y = _pip_x('ram', n_at)
    HL.pencil_oval(L, x, y, 21, 21, seed=41, w=3.2, ink=1.6, col=GAIN)


def trace_mark(L, before, after):
    for i in range(before, after):
        x, y = _pip_x('trace', i)
        HL.pencil_box(L, (x - 13, y - 13, x + 13, y + 13), seed=21 + i, w=3.0, ink=1.6, pad=2)


def pink_burst(L, x, y, r=22, seed=1):
    HL.starburst(L, x, y, r, PINK, (255, 255, 255), 11, 2.6, seed)


def cell_angle_span(u):
    return 60 * u['s'] - 30, 60 * (u['s'] + u['w'] - 1) + 30


# ------------------------------------------------------------------------------------------------ ghosts
GHOST_ARCS = []


def alpha_img(im, a):
    im = im.copy()
    im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    return im


def ghost_units(f_plan, ids, words, beat='p1', alpha=GHOST_A, outline=True, arcs=True):
    """ghost of units `ids` as the PLAN frame has them: cell + token + chevrons + HP row, and their plan landing arcs, at 74 percent; pencil edge on the cell"""
    NOW['words'] = words
    CAP['on'] = False
    try:
        Lg = L2()
        A.paint_cells(Lg, f_plan, beat, which=set(ids), with_base=False)
        A.draw_units(Lg, f_plan, beat, only=set(ids))
        out = alpha_img(Lg.done(), alpha)
        reg0 = len(RA.REG['arcs'])
        if arcs:
            La = L2()
            RA.landing_arcs(La, f_plan, {}, only=set(ids))
            ga = alpha_img(La.done(), alpha)
            add_mask('arcs', ga, 128)
            GHOST_ARCS.append(ga)
        rows = RA.REG['arcs'][reg0:]
    finally:
        CAP['on'] = True
    if outline:
        Lo = L2()
        for u in f_plan['units']:
            if u['id'] in ids and not (u['consumed'] or u['trigdead']) and u['w'] < 6:
                HL.pencil_poly(Lo, HL.cell_poly_unit(u), w=3.6, col=PLAN, ink=2.0, seed=u['id'])
        out.alpha_composite(Lo.done())
    return out, rows


def ghost_arcs(f_plan, ids, alpha=1.0):
    CAP['on'] = False
    try:
        reg0 = len(RA.REG['arcs'])
        La = L2()
        RA.landing_arcs(La, f_plan, {}, only=set(ids))
        rows = RA.REG['arcs'][reg0:]
    finally:
        CAP['on'] = True
    im = La.done()
    return (alpha_img(im, alpha) if alpha < 1 else im), rows


def assert_ghost_rows(tag, f_plan, ids, rows):
    """the ghost landing arcs == the PLAN frame (same rules as B10.draw_asserts)"""
    for u in f_plan['units']:
        if u['id'] not in ids or u['consumed'] or u['trigdead'] or u['fate']['kind'] != 'lands' or 'land_hit' not in u:
            continue
        rr = [r for r in rows if r['uid'] == u['id']]
        AD('%s ghost unit %d arc rows == plan landing sectors' % (tag, u['id']), sorted(r['sector'] for r in rr), sorted(u['land_sectors']))
        AD('%s ghost unit %d diamonds per sector == plan HP through' % (tag, u['id']), {str(r['sector']): r['diamonds'] for r in rr}, u['land_through'])
        AD('%s ghost unit %d chevrons per sector == plan hit at landing' % (tag, u['id']), sorted(set(r['solid'] + r['hollow'] for r in rr)), [u['land_hit']])
        AD('%s ghost unit %d turns-until dots == plan k' % (tag, u['id']), sorted(set(r['k'] for r in rr)), [u['fate']['k']])
        AD('%s ghost unit %d soak / clamp marks == plan' % (tag, u['id']), ({str(r['sector']): r['soak'] for r in rr}, {str(r['sector']): r['brace'] for r in rr}), (u['land_soak'], u['land_brace']))


def tower_layer(f, tag, nw):
    """the full tower of frame f (the locked spinner), as an RGBA board layer"""
    tw = R.tower_img(f, tag, skip=None, hot=True, hov_sectors=None, nw=nw, trim=True)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ox, oy = int(C[0] - R.FT.CT[0]), int(C[1] - R.FT.CT[1])
    lay.alpha_composite(tw, (ox, oy))
    return lay


def wedge_mask(r0, r1, a0, a1, feather=0.8):
    m = Image.new('L', (W * 2, H * 2), 0)
    n = 40
    pts = [ppx(C, r1, a0 + (a1 - a0) * i / n) for i in range(n + 1)] + [ppx(C, r0, a1 - (a1 - a0) * i / n) for i in range(n + 1)]
    ImageDraw.Draw(m).polygon([(x * 2, y * 2) for x, y in pts], fill=255)
    return m.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(feather))


def wedge_pts(s, r0, r1, half, n=16):
    return [ppx(C, r1, 60 * s - half + 2 * half * i / n) for i in range(n + 1)] + [ppx(C, r0, 60 * s + half - 2 * half * i / n) for i in range(n + 1)]


def veil_cells(f, ids, k=0.6):
    L = L2()
    for u in f['units']:
        if u['id'] in ids and u['w'] < 6:
            HL.tint_poly(L, HL.cell_poly_unit(u), (8, 10, 20), 255 * k)
    return L.done()


# ------------------------------------------------------------------------------------------------ hand + UI
_oslots = FH.slots
HOV = {'i': None, 'dx': 0.0}


def _slots(n):
    sl = _oslots(n)
    if HOV['i'] is not None and HOV['dx']:
        for s_ in sl:                 # the whole fan slides right, so the lifted card covers its neighbour exactly as a normal lift does
            s_['cx'] += HOV['dx']
    return sl


FH.slots = _slots


def _set_hand(hand, played=()):
    def hl(J, beat):
        return list(hand), list(played), None
    FH.hand_lists = hl


def ui_layers(words, f_hud, hand, lift, played=()):
    """the hand (lifted card at full value on its pink offset print, the rest at 70 percent) and the player UI (62 percent)"""
    _set_hand(hand, played)
    HOV['i'] = hand.index(lift) if lift is not None else None
    yy_, xx_ = np.mgrid[0:H, 0:W]
    d_ = np.hypot(xx_ - C[0], yy_ - C[1])
    lift0 = 866
    best = None

    def draw(dx, ly):
        HOV['dx'] = float(dx)
        FH.LIFT_CY = ly
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        FH.draw_hand(lay, A.J, 'p1', nw=not words, lift=lift, dim_others=HAND_K / FH.REST_V)
        hm = np.asarray(lay.split()[3]) >= 128
        return lay, not (hm & (d_ < FH.HAND_MIN_R)).any()
    # the lifted card must keep every pixel outside wheel radius 455 (O-29 fix 3): first lift it a little less, then slide it right; least total move wins
    for ly in (866, 874, 882, 890, 898, 906):
        for dx in range(0, 61, 4):
            if best is not None and dx + 0.15 * (ly - lift0) >= best[0]:
                break
            lay, ok = draw(dx, ly)
            if ok:
                best = (dx + 0.15 * (ly - lift0), dx, ly)
                break
        if lift is None:
            break
    if best is None:
        best = (0, 0, lift0)
    hand_lay, ok = draw(best[1], best[2])
    HOV['lift_cy'] = best[2]
    FH.LIFT_CY = lift0
    HOV['used_dx'] = HOV['dx']
    st = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lay, info = R.AS.stack_layer(words, {})
    m = Image.new('L', lay.size, 0)
    dr = ImageDraw.Draw(m)
    dr.rectangle([1655, 850, 1895, 899], fill=255)
    dr.rectangle([1660, 1028, 1900, 1060], fill=255)
    lay.putalpha(ImageChops.multiply(lay.split()[3], m))
    FH.place_ui(st, 'name', not words)
    FH.place_ui(st, 'send', not words)
    st.alpha_composite(lay)
    a = np.asarray(st).astype(np.float32)
    a[..., :3] *= STICK_K
    st = Image.fromarray(a.astype(np.uint8), 'RGBA')
    return hand_lay, st


# ------------------------------------------------------------------------------------------------ the assembler
def board(beat, f_board, f_hud, tag, words, arcs_skip=(), hide_units=(), hover_unit=None):
    """board + tower + HUD (+ YOU strip) of the locked generator, no hand / UI.  Draw asserts run on f_board."""
    NOW['words'] = words
    you = lambda bg, f: FH.place_ui(bg, 'you', not words, f_hud)
    img = R._render(beat, frame=f_board, hud_frame=f_hud, tag=tag, with_ui=False, arcs_skip=arcs_skip, hide_units=hide_units, extra=you,
                    hover_unit=hover_unit)
    return img.convert('RGBA')


def run_board_asserts(beat_a, f_board, tag):
    for e_ in A.AU.BADGE_LOG:
        for k_ in ('tag', 'tray', 'chev', 'glyph', 'band'):
            AD('%s unit %d %s badge (%s side) px on %s' % (tag, e_['uid'], e_['badge'], e_['side'], k_), e_['hits'][k_], 0)
    try:
        B10.draw_asserts(beat_a, f_board)
    except Exception as e:
        LOGD.append(dict(name='draw_asserts crashed', ok=False, got=repr(e)[:200], want=''))


Z_ORDER = {}


def compose(bg, lit_mask, ghosts, marks, hand_lay, stick, insets=(), top=()):
    """dim, ghosts, hover marks, then the board's own marks (digits, labels, tags, badges, tickets) put back on top: a hover mark never covers
    game words.  The pixels a mark would have covered before that are counted in Z_ORDER (reported), and kept low by placing marks clear."""
    base = HL.dim_image(bg.convert('RGB'), lit_mask, k=K_DIM, desat=DESAT).convert('RGBA')
    img = base.copy()
    for g in GHOST_ARCS:
        img.alpha_composite(g)
    for g in ghosts:
        img.alpha_composite(g)
        add_mask('ghost', g, 160)
    for m in marks:
        img.alpha_composite(m)
        add_mask('hover', m, 128)
    for t in top:
        img.alpha_composite(t)
        add_mask('hover', t, 128)
    keep = np.zeros((H, W), bool)
    for c in MARKS + ('tape', 'plates'):
        if c in MASKS and c != 'leader':
            keep |= MASKS[c]
    keep = np.asarray(Image.fromarray((keep * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) > 0
    Z_ORDER.clear()
    for hk in ('ghost', 'hover'):
        if hk in MASKS:
            Z_ORDER['%s under board marks px' % hk] = int((MASKS[hk] & keep).sum())
            MASKS[hk] = MASKS[hk] & ~keep
    a = np.asarray(img).copy()
    b = np.asarray(base)
    a[keep] = b[keep]
    img = Image.fromarray(a, 'RGBA')
    img.alpha_composite(hand_lay)            # as the locked board: the hand, then the nameplate, SEND IT and UNDO on top
    img.alpha_composite(stick)
    MASKS['hand'] = np.asarray(hand_lay.split()[3]) >= 128
    for ins in insets:
        img.alpha_composite(ins)
        add_mask('inset', ins, 128)
    return img.convert('RGB')


def collision_report(allowed_extra=()):
    allowed = set(ALLOWED) | set(allowed_extra)
    yy_, xx_ = np.mgrid[0:H, 0:W]
    holes = np.zeros((H, W), bool)
    for s_ in range(6):
        hx_, hy_ = A.S2.digit_xy(s_)
        holes |= np.hypot(xx_ - hx_, yy_ - hy_) <= A.S2.BOSS_R + A.S2.DIGIT_GAP
    for c_ in ('tape', 'plates'):
        if c_ in MASKS:
            MASKS[c_] = MASKS[c_] & ~holes
    if 'leader' in MASKS and 'tags' in MASKS:
        MASKS['tags'] = MASKS['tags'] & ~MASKS['leader']
    rep = {}
    occ = {}
    for mk in MARKS:
        for oc in OCCLUDERS:
            if (mk, oc) in allowed or mk not in MASKS or oc not in MASKS:
                continue
            occ['%s x %s' % (mk, oc)] = int((MASKS[mk] & MASKS[oc]).sum())
    hov = {}
    for hk in HOVER_CLASSES:
        if hk not in MASKS:
            continue
        for oc in MARKS + OCCLUDERS:
            if (hk, oc) in allowed or oc not in MASKS:
                continue
            ov_ = MASKS[hk] & MASKS[oc]
            hov['%s x %s' % (hk, oc)] = int(ov_.sum())
            if ov_.any():
                ys_, xs_ = np.nonzero(ov_)
                rep.setdefault('hover_overlap_bbox', {})['%s x %s' % (hk, oc)] = [int(xs_.min()), int(ys_.min()), int(xs_.max()), int(ys_.max())]
    info = {}
    for hk in HOVER_CLASSES:
        for oc in ('units', 'arcs'):
            if hk in MASKS and oc in MASKS:
                info['%s x %s' % (hk, oc)] = int((MASKS[hk] & MASKS[oc]).sum())
    hb = {}
    if 'hand' in MASKS:
        hm = MASKS['hand']
        d_ = np.hypot(xx_ - C[0], yy_ - C[1])
        hb['hand_min_r_px'] = round(float(d_[hm].min()), 1) if hm.any() else None
        hb['hand_px_inside_r455'] = int((hm & (d_ < FH.HAND_MIN_R)).sum())
        hb['hand_px_on_board_marks'] = int(sum((hm & MASKS[c_]).sum() for c_ in MARKS + ('tape', 'plates') if c_ in MASKS))
        hb['pass'] = hb['hand_px_inside_r455'] == 0 and hb['hand_px_on_board_marks'] == 0
    cls = sorted(c for c in MASKS if c not in ('units', 'arcs'))
    pairs = {}
    for i in range(len(cls)):
        for j in range(i + 1, len(cls)):
            a, b = cls[i], cls[j]
            if b in OCCLUDERS + HOVER_CLASSES or a in OCCLUDERS + HOVER_CLASSES:
                continue
            if (a, b) in allowed or (b, a) in allowed:
                continue
            pairs['%s x %s' % (a, b)] = int((MASKS[a] & MASKS[b]).sum())
    rep['mark_pairs_px'] = pairs
    rep['mark_pairs_pass'] = all(v == 0 for v in pairs.values())
    rep['occlusion_px'] = occ
    rep['occlusion_pass'] = all(v == 0 for v in occ.values())
    rep['hover_vs_marks_px'] = hov
    rep['hover_vs_marks_pass'] = all(v == 0 for v in hov.values())
    rep['hover_over_units_arcs_px_info'] = info
    rep['hand_vs_board'] = hb
    rep['mask_px'] = {c: int(MASKS[c].sum()) for c in sorted(MASKS)}
    rep['allowed_pairs'] = sorted('%s x %s' % p for p in allowed)
    return rep


lum = lambda a: 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def squint(img, region=None):
    s = img.resize((img.width // 16, img.height // 16), Image.BOX).filter(ImageFilter.GaussianBlur(1.0))
    l = lum(np.asarray(s, np.float32) / 255.0)
    if region is not None:
        yy, xx = np.mgrid[0:l.shape[0], 0:l.shape[1]]
        l = l[region(xx * 16 + 8, yy * 16 + 8)]
    return dict(mean=round(float(l.mean()), 4), p95=round(float(np.percentile(l, 95)), 4), loud=round(float((l > 0.38).mean()), 4))


def squint_set(img, lit_mask):
    lm = np.asarray(lit_mask.resize((W // 16, H // 16), Image.BOX)) >= 128
    d_ = lambda x, y: np.hypot(x - C[0], y - C[1])
    s = img.resize((W // 16, H // 16), Image.BOX).filter(ImageFilter.GaussianBlur(1.0))
    l = lum(np.asarray(s, np.float32) / 255.0)
    out = dict(plate=squint(img), tower=squint(img, lambda x, y: d_(x, y) <= 212), rings=squint(img, lambda x, y: (d_(x, y) >= 214) & (d_(x, y) <= 430)),
               hand=squint(img, lambda x, y: (x >= 840) & (x <= 1660) & (y >= 780)), hud=squint(img, lambda x, y: (x >= 1070) & (y <= 400)))
    lit = l[lm]
    dim = l[~lm]
    out['lit_mean'] = round(float(lit.mean()), 4) if lit.size else None
    out['dim_mean'] = round(float(dim.mean()), 4) if dim.size else None
    out['lit_share'] = round(float(lm.mean()), 4)
    out['lit_vs_dim'] = round(out['lit_mean'] / max(1e-6, out['dim_mean']), 2) if lit.size and dim.size else None
    return out
