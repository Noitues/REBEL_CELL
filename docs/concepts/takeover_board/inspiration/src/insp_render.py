"""insp_render: rendered concept plates for two Takeover action concepts, in the locked style.

    python insp_render.py [pl_rest pl_aim df_rest df_aim sheet]      (default: all five)

PACKET LADDER (pl_*): the screen is a packet-capture flow graph.  Your host lifeline on the left flank, the corp's on the right,
the wheel is the wire.  An action is a thin packet strip on your lifeline (key, name, len = cost, flag = type word, dst = target)
with an info line under it, Wireshark style.  Aiming draws the packet as a numbered arrow along the rim groove to the wedge.
DEFACE (df_*): actions are linocut stencils taped to your wall; held over a wedge, the cut-out shows the pink overprint; lasting
effects stay as sprayed tags.

The wheel, pointers, hub, outcome marks and numbered badges come from ../src/tk_render.py unchanged (imported, not copied); the
wheel is moved to the screen centre by setting tk_render.CX and replacing its polar helper at import time (no file edits).
State data: BOARD and PLAY from ../src/tk_states.py.  One process, PIL / numpy only.
"""
import copy, math, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/takeover/src')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import tk_render as TR                      # also puts the locked src on sys.path and sets the Takeover card plate words
import card_render as CR
from tk_states import BOARD, PLAY, GAIN as S_GAIN, HARM as S_HARM, HI as S_HI, PLAN as S_PLAN, MID as S_MID

OUT = 'D:/rc_art/art-pass/docs/concepts/takeover_board/inspiration/rendered/'
W, H, SS = TR.W, TR.H, TR.SS
S, text, Layer, comp, nb = TR.S, TR.text, TR.Layer, TR.comp, TR.nb

# ---------------------------------------------------------------- the wheel moves to the centre (both flanks work)
TR.CX = 960


def _pol(r, a, cx=None, cy=None):
    cx = TR.CX if cx is None else cx
    cy = TR.CY if cy is None else cy
    return (S(cx + r * math.cos(a)), S(cy + r * math.sin(a)))


TR.pol = _pol
CX, CY = TR.CX, TR.CY
pol = _pol

INK, PAPER, PINK, PINK_D = TR.INK, TR.PAPER, TR.PINK, TR.PINK_D
HARM, HARM_UP, HOT_CORE, GAIN, PLAN, FOCUS, SCHED, CYAN = TR.HARM, TR.HARM_UP, TR.HOT_CORE, TR.GAIN, TR.PLAN, TR.FOCUS, TR.SCHED, TR.CYAN
TEAL, TEAL_D, TEAL_HI, GLAZE, K_TYPE = TR.TEAL, TR.TEAL_D, TR.TEAL_HI, TR.GLAZE, TR.K_TYPE
SLATE, SLATE_LO, CLOCK, CLOCK_LT, CLOCK_GR = TR.SLATE, TR.SLATE_LO, TR.CLOCK, TR.CLOCK_LT, TR.CLOCK_GR
GLASS, TEXT_HI, TEXT_MID = TR.GLASS, TR.TEXT_HI, TR.TEXT_MID
ANTON, PLEX, MONO = TR.ANTON, TR.PLEX, TR.MONO
GLYPH_DIR = TR.LOCKED + '/glyphs/'

# the hand (same as BOARD): key, name, cost, type word, short target (dst), rule (info), glyph borrowed from the locked card
ACTS = [
    dict(id='NUDGE', key='1', nm='NUDGE', cost=0, fam='CONTROL', dst='HUB', info='spin 1 more or 1 less', g='PI_SPIN_CW', tgt='hub'),
    dict(id='WORM', key='2', nm='WORM', cost=1, fam='VIRUS', dst='3 CORP', info='1 virus on 3 corp segments', g='C_HOLD', tgt='seg'),
    dict(id='BREACH', key='3', nm='BREACH', cost=1, fam='FIRE', dst='CORP·ADJ', info='3 damage next to yours', g='C_STRIKE', tgt='seg'),
    dict(id='GUARD', key='4', nm='GUARD', cost=1, fam='BLOCK', dst='YOURS', info='block 3 on yours', g='C_BRACE', tgt='seg'),
    dict(id='TIMEBOMB', key='5', nm='TIME BOMB', cost=4, fam='DELAY', dst='CORP', info='6 damage in 2 turns', g='C_TRIG', tgt='seg',
         why='needs 4 energy'),
]


def plate_cols(fam):
    t = CR.TYPES[fam]
    c = lambda v: tuple(int(round(float(x) * 255)) for x in v)          # card_render keeps colours as 0..1 floats
    return c(t['col']), c(t['dk']), c(t['text'])


def F_all():
    F = TR.fonts()
    F.update(m16=TR.font(MONO, 17), m18=TR.font(MONO, 19), m20=TR.font(MONO, 21), m22=TR.font(MONO, 23), m26=TR.font(MONO, 26),
             a20=TR.font(ANTON, 21), a22=TR.font(ANTON, 23), a24=TR.font(ANTON, 25), a26=TR.font(ANTON, 26), a28=TR.font(ANTON, 28),
             a30=TR.font(ANTON, 30), a34=TR.font(ANTON, 34), a40=TR.font(ANTON, 40), a48=TR.font(ANTON, 48), p19=TR.font(PLEX, 20),
             p21=TR.font(PLEX, 22))
    return F


def tw(d, s, f):
    bb = d.textbbox((0, 0), s, font=f)
    return (bb[2] - bb[0]) / SS


def spans(d, x, y, items, f, gap=9, anchor='lm'):
    for s_, col in items:
        text(d, (x, y), s_, f, col + (255,), anchor=anchor)
        x += tw(d, s_, f) + gap
    return x


def poly_shadow(d, pts, dx=3, dy=4, col=INK):
    d.polygon([(x + S(dx), y + S(dy)) for x, y in pts], fill=col + (255,))


def key_cap(d, x, y, k, f, w=30, h=30, inv=False):
    """the hotkey: an ink key cap with a paper letter (the locked UNDO 'Z' key)"""
    d.rectangle([S(x - w / 2), S(y - h / 2), S(x + w / 2), S(y + h / 2)], fill=(PAPER if inv else INK) + (255,),
                outline=INK + (255,), width=S(2))
    text(d, (x, y + 1), k, f, (INK if inv else PAPER) + (255,))


def ram_coin(d, x, y, n, f, r=15, dim=False, red=False):
    """energy (RAM) as the locked cyan coin; the cost digit sits in it"""
    edge = HARM if red else (CYAN if not dim else (60, 110, 130))
    fill = (90, 20, 26) if red else ((26, 143, 184) if not dim else (16, 40, 50))
    d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=fill + (255,), outline=edge + (255,), width=S(3))
    if n is not None:
        text(d, (x, y + 1), str(n), f, (TEXT_HI if not red else (255, 210, 200)) + (255,))
    else:
        d.ellipse([S(x - 7), S(y - 7), S(x + 7), S(y + 7)], outline=(190, 245, 255, 255), width=S(2))


def type_plate(d, x, y, word, f, skew=7, padx=10, h=30, anchor='l'):
    """the type word on its locked plate colour (teal = aimed at a segment, lilac = not aimed), a slanted print plate"""
    col, dk, tc = plate_cols(word)
    w = tw(d, word, f) + 2 * padx
    x0 = x if anchor == 'l' else x - w / 2
    pts = [(S(x0 + skew), S(y - h / 2)), (S(x0 + w + skew), S(y - h / 2)), (S(x0 + w - skew), S(y + h / 2)), (S(x0 - skew), S(y + h / 2))]
    poly_shadow(d, pts, 2, 3)
    d.polygon(pts, fill=col + (255,), outline=INK + (255,), width=S(2))
    text(d, (x0 + w / 2, y + 1), word, f, tc + (255,))
    return w


def wrap(d, s, f, maxw):
    out, cur = [], ''
    for wd in s.split(' '):
        t = (cur + ' ' + wd).strip()
        if tw(d, t, f) <= maxw:
            cur = t
        else:
            out.append(cur); cur = wd
    out.append(cur)
    return out


# ---------------------------------------------------------------- shared: backdrop, flank scrims, the wheel
def base_image():
    img = TR.backdrop()
    L = Layer(); d = L.d
    # calm the flanks under the panels (the room still reads at the very edges)
    a = np.zeros((H * SS, W * SS), np.float32)
    xx = np.arange(W * SS, dtype=np.float32)[None, :] / SS
    for x0, x1 in ((0, 530), (1390, W)):
        m = np.clip(np.minimum(xx - x0 + 60, x1 - xx + 60) / 60.0, 0, 1)
        a = np.maximum(a, np.repeat(m, H * SS, 0) * 0.55)
    lay = Image.new('RGBA', (W * SS, H * SS), INK + (0,))
    lay.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    img.alpha_composite(lay)
    return img


def draw_wheel(img, st, F, statuses=True):
    s2 = copy.deepcopy(st)
    if not statuses:
        for g in s2['segs']:
            g['st'] = []
    TR.draw_rim(img, s2)
    L = Layer()
    for i, g in enumerate(s2['segs']):
        if g['owner'] != 'us':
            a0, a1, am = TR.seg_angles(i, s2['rot'])
            TR.draw_corp_seg(L, g, a0, a1, am)
    comp(img, L)
    TR.draw_runner_segs(img, s2['segs'], s2['rot'])
    TR.draw_segment_marks(img, s2, F['seg_type'], F['seg_num'], F['seg_small'])
    TR.draw_hub(img, s2, F['hub_big'], F['mid'], F['hub_small'])
    TR.draw_pointers(img, s2)
    s3 = dict(s2); s3['pencil'] = None
    TR.draw_overlays(img, s3, F['tag'], F['seg_small'])          # FOCUS corners on the legal targets while aiming


def run_health(d, F, x0, x1, y0, h=86):
    """the YOU strip: punk paper taped on (health pips; the forecast loss as the red loss hatch)"""
    hud = BOARD['hud']
    tape = [(S(x0 + 4), S(y0)), (S(x1 - 4), S(y0 + 4)), (S(x1 - 8), S(y0 + h)), (S(x0), S(y0 + h - 4))]
    poly_shadow(d, tape, 4, 5)
    d.polygon(tape, fill=PAPER + (255,), outline=INK + (255,), width=S(3))
    text(d, (x0 + 18, y0 + 26), hud['runner'], F['a26'], INK + (255,), anchor='lm')
    hp, hpm = hud['hp']; lose = hud['hp_loss']
    text(d, (x1 - 20, y0 + 26), '%d \u2192 %d' % (hp, hp - lose), F['a28'], (200, 24, 30, 255), anchor='rm')
    pw, gap = (x1 - x0 - 40 - 2 * (hpm - 1)) / hpm, 2.0
    for k in range(hpm):
        x = x0 + 18 + k * (pw + gap); box = [S(x), S(y0 + 50), S(x + pw), S(y0 + 74)]
        if k < hp - lose:
            d.rectangle(box, fill=GAIN + (255,), outline=INK + (255,), width=S(2))
        elif k < hp:
            d.rectangle(box, fill=PAPER + (255,))
            for t in range(-1, 3):
                d.line([(S(x + t * 6), S(y0 + 74)), (S(x + t * 6 + 10), S(y0 + 50))], fill=HARM + (255,), width=S(2.2))
            d.rectangle(box, outline=INK + (255,), width=S(2))
        else:
            d.rectangle(box, fill=(196, 190, 176, 255), outline=INK + (255,), width=S(2))


def glass(d, box, edge=CYAN, alpha=226, w=2):
    TR.glass(d, box, edge, alpha, w)


def energy_status(d, F, x0, x1, y0, y1, word='ENERGY'):
    glass(d, (x0, y0, x1, y1))
    ym = (y0 + y1) / 2
    text(d, (x0 + 16, ym), word, F['m20'], TEXT_MID + (255,), anchor='lm')
    en, emax = BOARD['hud']['energy']
    for k in range(emax):
        ram_coin(d, x0 + 116 + k * 36, ym, None, F['a22'], r=14)
    sx = x0 + 246
    for wd, side in BOARD['hud']['status']:
        col = CYAN if side == 'buff' else (255, 181, 71)
        w_ = tw(d, wd, F['m20'])
        d.rounded_rectangle([S(sx - 8), S(ym - 15), S(sx + w_ + 8), S(ym + 15)], radius=S(12), outline=col + (255,), width=S(2))
        text(d, (sx, ym), wd, F['m20'], col + (255,), anchor='lm')
        sx += w_ + 30


def forecast_panel(d, F, box, st, aim_hint=None):
    """system glass: OWNED with its forecast, then the HUD forecast lines (designer 2026-11-15: totals at rest; the play line
    while aiming)"""
    x0, y0, x1, y1 = box
    glass(d, box)
    owned = sum(1 for g in st['segs'] if g['owner'] == 'us')
    oa = st['hud']['owned_after']
    text(d, (x0 + 18, y0 + 24), 'OWNED', F['m20'], TEXT_MID + (255,), anchor='lm')
    text(d, (x0 + 18, y0 + 62), '%d/12' % owned, F['num'], TEXT_HI + (255,), anchor='lm')
    text(d, (x0 + 128, y0 + 64), '\u2192 %d' % oa, F['mid'], (GAIN if oa >= owned else HARM) + (255,), anchor='lm')
    text(d, (x0 + 230, y0 + 24), 'END TURN FORECAST', F['m20'], TEXT_MID + (255,), anchor='lm')
    fc = st['hud']['forecast']
    tot = fc[-1]                     # the totals line: END TURN +n taken -n lost -> owned n · HP a -> b
    spans(d, x0 + 230, y0 + 62, [(tot[1][0], tot[1][1]), (tot[2][0], tot[2][1])], F['a28'], gap=16)
    hp_s = tot[4][0].replace('· HP', 'health')
    text(d, (x0 + 230, y0 + 100), hp_s, F['a28'], S_HARM + (255,), anchor='lm')
    y = y0 + 140
    if len(fc) > 1:
        d.line([(S(x0 + 14), S(y - 12)), (S(x1 - 14), S(y - 12))], fill=(40, 90, 110, 255), width=S(1.5))
        play = fc[0]
        x = spans(d, x0 + 18, y + 14, [play[0]], F['a28'])
        for k, ln in enumerate(wrap(d, play[1][0], F['a26'], x1 - x - 16)):
            text(d, (x, y + 14 + 34 * k), ln, F['a26'], S_HI + (255,), anchor='lm')
        y += 50
    if aim_hint:
        for k, ln in enumerate(aim_hint):
            text(d, (x0 + 18, y + 12 + 28 * k), ln, F['m20'], TEXT_MID + (255,), anchor='lm')


def end_turn_btn(d, F, x0, y0, x1, y1, sub=None):
    pts = [(S(x0), S(y0 + 6)), (S(x1), S(y0)), (S(x1 - 4), S(y1)), (S(x0 + 4), S(y1 - 4))]
    poly_shadow(d, pts, 6, 8)
    d.polygon(pts, fill=PINK + (255,), outline=INK + (255,), width=S(4))
    text(d, ((x0 + x1) / 2, (y0 + y1) / 2 - (12 if sub else 0)), 'END TURN', F['end'], (255, 255, 255, 255), stroke=2.4, sfill=INK + (255,))
    if sub:
        text(d, ((x0 + x1) / 2, y1 - 22), sub, F['m20'], INK + (255,))


def undo_tab(d, F, x0, y0, x1, y1, word='UNDO'):
    d.polygon([(S(x0 + 3), S(y0 + 4)), (S(x1 + 3), S(y0 + 2)), (S(x1 + 3), S(y1 + 4)), (S(x0 + 3), S(y1 + 4))], fill=INK + (255,))
    d.polygon([(S(x0), S(y0)), (S(x1), S(y0 - 2)), (S(x1), S(y1)), (S(x0), S(y1))], fill=PAPER + (255,), outline=INK + (255,), width=S(2))
    text(d, (x0 + 16, (y0 + y1) / 2), word, F['undo'], INK + (255,), anchor='lm')
    key_cap(d, x1 - 24, (y0 + y1) / 2, 'Z', F['key'], 28, 30)


def hot_mark(d, x, y, w=34):
    """the locked HOT mark (armed this END TURN): a HARM arc with its white-hot core"""
    pts = [(S(x - w / 2 + w * t / 12), S(y + 6 - 10 * math.sin(math.pi * t / 12))) for t in range(13)]
    d.line(pts, fill=HARM_UP + (255,), width=S(9))
    d.line(pts[1:-1], fill=HOT_CORE + (255,), width=S(3))


def plan_ticket(d, F, x0, y0, x1, y1, k, nm, sub, point=None):
    """the locked corp plan ticket (enamel; NOW has the live SCHEDULE edge; T+1 / T+2 step down in value 100 / 72 / 52 %)
    point: None = a plain ticket; 'left' = a packet strip pointing at the lifeline on its left"""
    v = (1.0, 0.72, 0.52)[k]
    body = tuple(int(c * v) for c in (196, 205, 214))
    edge = SCHED if k == 0 else tuple(int(c * v) for c in TEAL)
    if point == 'left':
        pts = [(S(x0 + 16), S(y0)), (S(x1), S(y0)), (S(x1), S(y1)), (S(x0 + 16), S(y1)), (S(x0), S((y0 + y1) / 2))]
    else:
        pts = [(S(x0), S(y0)), (S(x1), S(y0)), (S(x1), S(y1)), (S(x0), S(y1))]
    poly_shadow(d, pts, 3, 4)
    d.polygon(pts, fill=body + (255,), outline=edge + (255,), width=S(4 if k == 0 else 2))
    tx = x0 + (28 if point else 14)
    text(d, (tx, y0 + 22), ('NOW  ' if k == 0 else 'T+%d  ' % k) + nm, F['tick'], INK + (255,), anchor='lm')
    text(d, (tx, y0 + 50), sub, F['m18'], (40, 46, 56, 255), anchor='lm')


def numbered_arrow(d, pts, col, dashed=False, w=5.5, head=True):
    """the B-088 arrow (ink casing, colour core, triangle head); dashed = aimed, not yet sent"""
    pts = [tuple(p) for p in pts]
    if dashed:
        seglen, gap = S(16), S(10)
        acc, on = 0.0, True
        cur = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            L_ = math.dist(a, b); t = 0.0
            while t < L_:
                lim = (seglen if on else gap) - acc
                step = min(lim, L_ - t)
                t += step; acc += step
                p = (a[0] + (b[0] - a[0]) * t / L_, a[1] + (b[1] - a[1]) * t / L_)
                if on:
                    cur.append(p)
                if acc >= (seglen if on else gap) - 1e-6:
                    if on and len(cur) > 1:
                        d.line(cur, fill=INK + (255,), width=S(w + 5))
                        d.line(cur, fill=col + (255,), width=S(w))
                    on = not on; acc = 0.0; cur = [p]
        if on and len(cur) > 1:
            d.line(cur, fill=INK + (255,), width=S(w + 5)); d.line(cur, fill=col + (255,), width=S(w))
    else:
        d.line(pts, fill=INK + (255,), width=S(w + 4.5)); d.line(pts, fill=col + (255,), width=S(w))
    if not head:
        return
    v = np.array(pts[-1]) - np.array(pts[-3]); v = v / (np.linalg.norm(v) + 1e-6); nrm = np.array([-v[1], v[0]])
    tip = np.array(pts[-1]) + v * S(6)
    d.polygon([tuple(tip), tuple(tip - v * S(22) + nrm * S(12)), tuple(tip - v * S(22) - nrm * S(12))], fill=col + (255,), outline=INK + (255,))


def label_tag(d, F, x, y, n, lab, col, numcol=None):
    """the B-088 label: number badge then a short amount, on an ink tag with a hard drop"""
    w_ = tw(d, lab, F['oc'])
    box = [S(x - 4), S(y - 17), S(x + 48 + w_ + 12), S(y + 17)]
    d.rectangle([box[0] + S(3), box[1] + S(4), box[2] + S(3), box[3] + S(4)], fill=INK + (255,))
    d.rectangle(box, fill=INK + (255,), outline=col + (255,), width=S(2))
    nb(d, x + 18, y, n, numcol or col, F['nb'])
    text(d, (x + 48, y + 1), lab, F['oc'], col + (255,), anchor='lm')


# =============================================================================================== PACKET LADDER
LX = 500          # your lifeline
RX = 1420         # the corp's lifeline
ROW0, PITCH = 254, 100


def lifeline(d, x, y0, y1, side):
    if side == 'runner':     # a linocut ink rule with the pink misprint
        d.line([(S(x + 3), S(y0)), (S(x + 3), S(y1))], fill=PINK + (255,), width=S(5))
        d.line([(S(x), S(y0)), (S(x), S(y1))], fill=INK + (255,), width=S(5))
        d.line([(S(x - 1), S(y0)), (S(x - 1), S(y1))], fill=(70, 62, 70, 255), width=S(1))
    else:                    # the corp's: gunmetal with the Solace teal edge
        d.line([(S(x), S(y0)), (S(x), S(y1))], fill=TEAL + (255,), width=S(7))
        d.line([(S(x), S(y0)), (S(x), S(y1))], fill=CLOCK + (255,), width=S(3))


def port(d, x, y, state):
    """a port on a lifeline: idle (paper), lit (pink, the picked packet), dead (red ring: RST), corp (teal)"""
    r = 8 if state != 'lit' else 11
    fill = {'idle': PAPER, 'lit': PINK, 'dead': INK, 'corp': CLOCK_LT}[state]
    edge = {'idle': INK, 'lit': INK, 'dead': HARM, 'corp': TEAL}[state]
    d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=fill + (255,), outline=edge + (255,), width=S(3))


def packet_strip(L, F, a, yc, state):
    """one action = one packet strip: an RFC-style header row (no art), pointing at its port on your lifeline.
    Fields: key | name | len (cost, RAM coin) | flag (type word on the locked plate) | dst (target rule).  The info line under the
    strip is the payload in words.  state: idle | lit | dim | dead"""
    d = L.d
    x0, x1, h = 28, LX - 16, 46
    if state == 'lit':
        x0 += 12; x1 += 6
    y0, y1 = yc - h / 2, yc + h / 2
    # torn left edge (the strip is torn off a print run), arrow tip at the port
    rng = np.random.default_rng(int(a['key']) * 7)
    left = [(x0 + rng.uniform(-3, 3), y0 + (y1 - y0) * t / 5) for t in range(6)]
    pts = [(S(x), S(y)) for x, y in left[::-1]]
    pts = [(S(x0), S(y0))] + [(S(x1 - 18), S(y0)), (S(x1), S(yc)), (S(x1 - 18), S(y1)), (S(x0), S(y1))] + [(S(x), S(y)) for x, y in left[1:-1][::-1]]
    if state == 'lit':          # the pink scissor halo of the picked packet
        halo = [(x - S(6), y - S(6)) for x, y in pts[:1]] + [(S(x1 - 18 + 2), S(y0 - 7)), (S(x1 + 10), S(yc)), (S(x1 - 18 + 2), S(y1 + 7)), (S(x0 - 7), S(y1 + 7)), (S(x0 - 7), S(y0 - 7))]
        d.polygon(halo, fill=PINK + (255,))
    poly_shadow(d, pts, 3, 4)
    paper = PAPER if state in ('idle', 'lit') else ((188, 184, 176) if state == 'dim' else (150, 146, 140))
    d.polygon(pts, fill=paper + (255,), outline=INK + (255,), width=S(2.6))
    ink = INK if state != 'dead' else (70, 64, 70)
    # fields (hairline field rules, as in a header diagram)
    fx = [x0 + 44, x0 + 186, x0 + 236, x0 + 340]
    for x in fx:
        d.line([(S(x), S(y0 + 7)), (S(x), S(y1 - 7))], fill=ink + (255,), width=S(1.6))
    key_cap(d, x0 + 22, yc, a['key'], F['m20'], 28, 30)
    nmf = F['a30'] if tw(d, a['nm'], F['a30']) < 132 else F['a26']
    text(d, (x0 + 52, yc + 1), a['nm'], nmf, ink + (255,), anchor='lm')
    ram_coin(d, x0 + 211, yc, a['cost'], F['a22'], r=15, red=(state == 'dead'))
    col, dk, tc = plate_cols(a['fam'])
    type_plate(d, x0 + 288, yc, a['fam'], F['a20'], skew=5, padx=8, h=28, anchor='c')
    text(d, (x0 + 348, yc + 1), a['dst'], F['m18'], ink + (255,), anchor='lm')
    # the info line: the payload in words (Wireshark's Info column)
    icol = (TEXT_HI if state == 'lit' else TEXT_MID) if state != 'dead' else (150, 120, 120)
    text(d, (x0 + 52, y1 + 17), a['info'], F['m20'], icol + (255,), anchor='lm')
    if state == 'dead':          # RST: the packet is refused, with the reason
        d.rectangle([S(x0 - 2), S(y0 - 2), S(x1 - 14), S(y1 + 2)], outline=HARM + (255,), width=S(3))
        rx0, rx1 = x0 + 278, x1 + 6
        ty = y1 + 17
        tab = [(S(rx0), S(ty - 14)), (S(rx1), S(ty - 16)), (S(rx1 - 2), S(ty + 14)), (S(rx0 + 2), S(ty + 15))]
        poly_shadow(d, tab, 2, 3)
        d.polygon(tab, fill=HARM + (255,), outline=INK + (255,), width=S(2))
        text(d, ((rx0 + rx1) / 2, ty), 'RST \u00b7 ' + a['why'], F['a20'], INK + (255,))


def pl_left(img, F, aim):
    L = Layer(); d = L.d
    run_health(d, F, 24, 516, 18)
    energy_status(d, F, 24, 516, 112, 152, word='RAM')
    # OUTBOX: column header (one, like a capture list), lifeline, packets in key order
    text(d, (28, 196), 'OUTBOX', F['a24'], TEXT_HI + (255,), anchor='lm')
    text(d, (118, 197), 'your packets, keys 1-5', F['m18'], TEXT_MID + (255,), anchor='lm')
    hdr = [(36, '#'), (80, 'PACKET'), (224, 'LEN'), (298, 'FLAG'), (376, 'DST')]
    for x, s_ in hdr:
        text(d, (x, 226), s_, F['m16'], (120, 140, 160, 255), anchor='lm')
    d.line([(S(28), S(238)), (S(LX - 16), S(238))], fill=(70, 80, 96, 255), width=S(1))
    lifeline(d, LX, 180, 736, 'runner')
    text(d, (LX - 6, 172), 'rhee@cell', F['m18'], PINK + (255,), anchor='rm')
    for i, a in enumerate(ACTS):
        yc = ROW0 + 22 + i * PITCH
        st = 'dead' if a.get('why') else ('lit' if aim and a['id'] == 'BREACH' else ('dim' if aim else 'idle'))
        packet_strip(L, F, a, yc, st)
        port(d, LX, yc, {'dead': 'dead', 'lit': 'lit'}.get(st, 'idle'))
    # piles on the lifeline's foot: the game words first, the capture words as the picture
    yy = 790
    d.line([(S(28), S(yy - 20)), (S(LX - 16), S(yy - 20))], fill=(70, 80, 96, 255), width=S(1))
    piles = [('DRAW', 'queued', BOARD['hud']['piles'][0]), ('DISCARD', 'sent', BOARD['hud']['piles'][1]), ('EXHAUST', 'dropped', 0)]
    for k, (wd, cap, n) in enumerate(piles):
        x = 36 + k * 156
        text(d, (x, yy + 16), str(n), F['a40'], TEXT_HI + (255,), anchor='lm')
        text(d, (x + 36, yy + 6), wd, F['a22'], TEXT_HI + (255,), anchor='lm')
        text(d, (x + 36, yy + 32), cap, F['m18'], TEXT_MID + (255,), anchor='lm')
    if aim:
        text(d, (36, 950), 'dst lit on the wheel: CORE, FIREWALL', F['m18'], FOCUS + (255,), anchor='lm')
    undo_tab(d, F, 28, 870, 236, 920, word='UNDO')
    text(d, (250, 895), 'rollback the last packet', F['m18'], TEXT_MID + (255,), anchor='lm')
    comp(img, L)


def pl_right(img, F, st, aim):
    L = Layer(); d = L.d
    hud = st['hud']
    # the corp host header: enamel, teal edge
    x0, x1 = 1404, 1898
    box = [S(x0), S(18), S(x1), S(160)]
    d.rectangle([box[0] + S(3), box[1] + S(4), box[2] + S(3), box[3] + S(4)], fill=INK + (255,))
    d.rectangle(box, fill=SLATE + (255,), outline=TEAL + (255,), width=S(3))
    d.rectangle([S(x0 + 3), S(21), S(x1 - 3), S(30)], fill=TEAL_D + (255,))
    text(d, (x0 + 18, 56), 'solace.sys', F['m22'], TEAL_HI + (255,), anchor='lm')
    text(d, (x1 - 18, 56), hud['kind'], F['a28'], K_TYPE + (255,), anchor='rm')
    for k, ln in enumerate(wrap(d, hud['rule'], F['m20'], x1 - x0 - 36)):
        text(d, (x0 + 18, 96 + 28 * k), ln, F['m20'], TEXT_MID + (255,), anchor='lm')
    # INBOUND: the plan as packets on the corp lifeline (they fire at END TURN)
    text(d, (RX + 26, 196), 'INBOUND', F['a24'], TEXT_HI + (255,), anchor='lm')
    text(d, (RX + 126, 197), 'corp plan, fires on END TURN', F['m18'], TEXT_MID + (255,), anchor='lm')
    lifeline(d, RX, 180, 560, 'corp')
    text(d, (RX, 170), '', F['m18'], TEAL + (255,))
    for k, (nm, sub) in enumerate(hud['plan']):
        y = 226 + k * 84
        plan_ticket(d, F, RX + 14, y, x1, y + 66, k, nm, sub, point='left')
        port(d, RX, y + 33, 'corp')
    # ARMED: the HOT legend (the arcs on the wheel)
    y = 488
    text(d, (RX + 26, y), 'ARMED', F['a24'], TEXT_HI + (255,), anchor='lm')
    text(d, (RX + 108, y + 1), 'pointers land this END TURN', F['m18'], TEXT_MID + (255,), anchor='lm')
    x = RX + 40
    for i, g in enumerate(st['segs']):
        if g.get('armed') and g['owner'] != 'us':
            hot_mark(d, x + 16, y + 40)
            text(d, (x + 40, y + 42), g['type'], F['m20'], K_TYPE + (255,), anchor='lm')
            x += 40 + tw(d, g['type'], F['m20']) + 30
    # the system glass: owned, the END TURN totals, the play line
    hint = ['click a lit wedge or Enter to send,', 'Tab walks the legal wedges, Esc drops it'] if aim else None
    fb = 590 + (270 if aim else 136)
    forecast_panel(d, F, (x0, 590, x1, fb), st, aim_hint=hint)
    end_turn_btn(d, F, 1640, 900, 1898, 1036, sub='SPACE \u00b7 send')
    comp(img, L)


def pl_top(img, F, st):
    L = Layer(); d = L.d
    x0, x1, y0, y1 = 566, 1354, 14, 58
    glass(d, (x0, y0, x1, y1))
    hud = st['hud']
    text(d, (x0 + 18, 37), hud['title'], F['m22'], TEXT_HI + (255,), anchor='lm')
    x = x0 + 360
    text(d, (x, 37), 'TURN', F['m20'], TEXT_MID + (255,), anchor='lm')
    text(d, (x + 52, 37), str(hud['turn']), F['a28'], TEXT_HI + (255,), anchor='lm')
    text(d, (x + 96, 37), 'ESCALATION', F['m20'], TEXT_MID + (255,), anchor='lm')
    text(d, (x + 222, 37), hud['esc'], F['a26'], TEXT_HI + (255,), anchor='lm')
    comp(img, L)


def rim_route(y_port, a_target, r=382):
    """the packet runs from your port along the rim groove (the wire) to the target wedge, then turns in"""
    dy = y_port - CY
    dx = -math.sqrt(max(r * r - dy * dy, 0))
    a_in = math.atan2(dy, dx)
    if a_in > 0:
        a_in -= 2 * math.pi
    a_end = a_target
    while a_end < a_in:
        a_end += 2 * math.pi
    pts = [(S(LX + 12), S(y_port))]
    pts += [pol(r, a_in + (a_end - a_in) * t / 60) for t in range(61)]
    return pts


R_ARROW_END = 318


def pl_aim_overlay(img, F, st):
    L = Layer(); d = L.d
    i_b = 2
    y_port = ROW0 + 22 + i_b * PITCH
    a_t = TR.seg_angles(st['aim'], st['rot'])[2]
    route = rim_route(y_port, a_t - 0.06)
    numbered_arrow(d, route, PINK, dashed=True, head=False)
    # the turn-in: solid, from the groove into the wedge, with the head
    stub = [pol(382 - 64 * u * u, a_t - 0.06 + 0.06 * (1 - (1 - u) ** 2)) for u in np.linspace(0, 1, 12)]
    numbered_arrow(d, stub, PINK)
    # the packet label rides the arrow over the top of the rim: P1 = your first packet this turn
    x, y = CX + 446 * math.cos(math.radians(-60)), CY + 446 * math.sin(math.radians(-60))
    label_tag(d, F, x - 10, y, 'P1', 'BREACH \u22123', PINK)
    comp(img, L)


def render_pl(aim):
    st = PLAY if aim else BOARD
    F = F_all()
    img = base_image()
    draw_wheel(img, st, F)
    if aim:
        pl_aim_overlay(img, F, st)
    TR.draw_outcomes(img, st, F)
    pl_top(img, F, st)
    pl_left(img, F, aim)
    pl_right(img, F, st, aim)
    return img


# =============================================================================================== DEFACE
_GLY = {}


def glyph_mask(name, px):
    """the locked card glyph as an L mask, long side = px (SS px)"""
    if name not in _GLY:
        _GLY[name] = Image.open(GLYPH_DIR + name + '.png').convert('L')
    g = _GLY[name]
    g = g.crop(g.getbbox())
    k = px / max(g.size)
    return g.resize((max(1, int(g.width * k)), max(1, int(g.height * k))), Image.LANCZOS)


def stencil_text_mask(s, f):
    """letters for a stencil: Anton with stencil bridges (a thin vertical gap through each letter)"""
    d0 = ImageDraw.Draw(Image.new('L', (8, 8)))
    bb = d0.textbbox((0, 0), s, font=f)
    w_, h_ = bb[2] - bb[0] + 8, bb[3] - bb[1] + 8
    m = Image.new('L', (w_, h_), 0); dm = ImageDraw.Draw(m)
    dm.text((4 - bb[0], 4 - bb[1]), s, font=f, fill=255)
    x = 4 - bb[0]
    gw = max(2, int(h_ * 0.07))
    for ch in s:
        cw = d0.textlength(ch, font=f)
        if False:
            cx_ = int(x + cw * 0.5)
            dm.rectangle([cx_ - gw // 2, int(h_ * 0.30), cx_ + gw // 2, int(h_ * 0.62)], fill=0)
        x += cw
    return m


def overspray(mask, rad, density, seed):
    """pink spray residue: speckle in a ring around the cut, thinning out with distance"""
    a = np.asarray(mask, np.float32) / 255.0
    near = np.asarray(mask.filter(ImageFilter.GaussianBlur(rad)), np.float32) / 255.0
    near = np.clip(near * 2.2, 0, 1) * (1 - a)
    rng = np.random.default_rng(seed)
    sp = (rng.random(a.shape) < near * density).astype(np.float32)
    return Image.fromarray((np.clip(sp, 0, 1) * 255).astype(np.uint8))


def stencil(a, sc, mode):
    """one action as a cut stencil.  Returns (RGBA at SS, (vx, vy) = the virtual wheel centre in the image: the wedge's apex).
    sc: 1.0 = wheel scale (held over a wedge), <1 = on the wall.  mode: wall | dead | held"""
    hub = a['tgt'] == 'hub'
    if hub:
        r1 = 80 * sc / 0.7
        size = int(S(2 * r1 + 60)); vx = vy = size // 2
        M = Image.new('L', (size, size), 0); dm = ImageDraw.Draw(M)
        dm.ellipse([vx - S(r1), vy - S(r1), vx + S(r1), vy + S(r1)], fill=255)
        g_c, g_px = (vx, vy - S(r1 * 0.30)), S(r1 * 0.62)
        n_c, n_px = (vx, vy + S(r1 * 0.30)), r1 * 0.40
        t_c = (vx, vy + S(r1 * 0.80))
    else:
        r0, r1 = (TR.R_IN - 8) * sc, (TR.R_OUT + 10) * sc
        hw = math.radians(16.5)
        size = int(S(2 * r1 + 60)); vx = vy = size // 2
        M = Image.new('L', (size, size), 0); dm = ImageDraw.Draw(M)
        pts = [(vx + S(r1 * math.sin(-hw + 2 * hw * t / 30)), vy - S(r1 * math.cos(-hw + 2 * hw * t / 30))) for t in range(31)]
        pts += [(vx + S(r0 * math.sin(hw - 2 * hw * t / 30)), vy - S(r0 * math.cos(hw - 2 * hw * t / 30))) for t in range(31)]
        dm.polygon(pts, fill=255)
        rr = lambda f: r0 + f * (r1 - r0)
        n_c, n_px = (vx, vy - S(rr(0.80))), 40 * sc
        held = mode == 'held'
        g_c, g_px = (vx, vy - S(rr(0.56 if held else 0.47))), S(66 * sc)
        t_c = (vx, vy - S(rr(0.33 if held else 0.17)))
    # cuts: glyph + name
    C = Image.new('L', M.size, 0)
    gm = glyph_mask(a['g'], g_px)
    C.paste(gm, (int(g_c[0] - gm.width / 2), int(g_c[1] - gm.height / 2)), gm)
    nf = TR.ImageFont.truetype(ANTON, int(S(n_px)))
    tm = stencil_text_mask(a['nm'], nf)
    maxw = S(2 * (r0 + 0.80 * (r1 - r0)) * math.sin(math.radians(14.0)) * 0.88) if not hub else S(1.5 * r1)
    if tm.width > maxw:
        tm = tm.resize((int(maxw), int(tm.height * maxw / tm.width)), Image.LANCZOS)
    C.paste(tm, (int(n_c[0] - tm.width / 2), int(n_c[1] - tm.height / 2)), tm)
    Ca = np.asarray(C, np.float32) / 255.0
    Ma = np.asarray(M, np.float32) / 255.0
    sheet = Image.fromarray((np.clip(Ma * (1 - Ca), 0, 1) * 255).astype(np.uint8))
    im = Image.new('RGBA', M.size, (0, 0, 0, 0))
    # pink scissor halo + linocut key with block drop around the outer shape (the runner's print)
    rng = np.random.default_rng(len(a['nm']) * 13)
    halo = M.filter(ImageFilter.MaxFilter(S(4) * 2 + 1))
    nz = Image.fromarray((rng.random((M.height // 6 + 1, M.width // 6 + 1)) * 255).astype(np.uint8)).resize(M.size, Image.NEAREST)
    halo2 = Image.fromarray(np.where(np.asarray(nz) > 110, np.asarray(halo), np.asarray(M.filter(ImageFilter.MaxFilter(S(2) * 2 + 1)))).astype(np.uint8))
    if mode != 'held':
        im.paste(Image.new('RGBA', M.size, PINK + (255,)), (0, 0), halo2)
    TR.ink_key(im, M, key=2.2, drop=(3, 4) if mode != 'held' else (5, 7))
    paper = PAPER if mode != 'dead' else (150, 146, 140)
    if mode == 'held':
        paper = (236, 230, 216)
    im.paste(Image.new('RGBA', M.size, paper + (255,)), (0, 0), sheet)
    # paper tooth: faint ink fibres
    fib = (rng.random((M.height, M.width)) < 0.012).astype(np.float32) * Ma * (1 - Ca)
    im.paste(Image.new('RGBA', M.size, (190, 182, 166, 255)), (0, 0), Image.fromarray((fib * 255).astype(np.uint8)))
    # old overspray round every cut (it is a used spray stencil) and the cut edge in ink
    os_ = overspray(C, S(5 * sc + 2), 0.55 if mode != 'dead' else 0.25, len(a['nm']))
    os_a = np.asarray(os_, np.float32) / 255.0 * Ma
    im.paste(Image.new('RGBA', M.size, (PINK if mode != 'dead' else (170, 120, 140)) + (255,)), (0, 0), Image.fromarray((os_a * 255).astype(np.uint8)))
    edge = np.clip(np.asarray(C.filter(ImageFilter.MaxFilter(3)), np.float32) / 255.0 - Ca, 0, 1) * Ma
    im.paste(Image.new('RGBA', M.size, INK + (255,)), (0, 0), Image.fromarray((edge * 255).astype(np.uint8)))
    if mode == 'held':            # the paint through the cut-out: the result, in the runner's pink
        im.paste(Image.new('RGBA', M.size, PINK + (255,)), (0, 0), C)
        dots = overspray(C, S(3), 0.35, 5)
        im.paste(Image.new('RGBA', M.size, (255, 120, 196, 255)), (0, 0), dots)
    # the type word: a tape label across the narrow end, in the locked plate colour
    d = ImageDraw.Draw(im)
    f = TR.font(ANTON, 22 if sc < 0.9 else 26)
    col, dk, tc = plate_cols(a['fam'])
    bb = d.textbbox((0, 0), a['fam'], font=f)
    w_ = bb[2] - bb[0] + S(18); h_ = S(30 if sc < 0.9 else 34)
    x0, y0 = t_c[0] - w_ / 2, t_c[1] - h_ / 2
    tp = [(x0 + S(4), y0), (x0 + w_ + S(6), y0 + S(2)), (x0 + w_ - S(4), y0 + h_), (x0 - S(6), y0 + h_ - S(2))]
    d.polygon([(x + S(2), y + S(3)) for x, y in tp], fill=INK + (255,))
    d.polygon(tp, fill=(col if mode != 'dead' else tuple(int(c * 0.6) for c in col)) + (255,), outline=INK + (255,), width=S(2))
    d.text((t_c[0], t_c[1] + S(1)), a['fam'], font=f, fill=tc + (255,), anchor='mm')
    return im, (vx, vy)


def place(base, im, v, at, rot_deg):
    """paste a stencil so its virtual centre lands on `at` (1x px), rotated (degrees, PIL: positive = counter-clockwise)"""
    r = im.rotate(rot_deg, resample=Image.BICUBIC, center=v)
    base.alpha_composite(r, (int(S(at[0]) - v[0]), int(S(at[1]) - v[1])))


def tape(d, x, y, ang_deg, w=34, h=12, col=(226, 214, 168)):
    a = math.radians(ang_deg); c, s_ = math.cos(a), math.sin(a)
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    P = [(S(x + px * c - py * s_), S(y + px * s_ + py * c)) for px, py in pts]
    d.polygon(P, fill=col + (215,))


def payload_tag(d, F, x, y, a, state):
    """the cyan glass payload tag pinned under a stencil: cost (RAM coin) + the rule in words; red when it can't be used"""
    w_ = 154
    edge = {'idle': (70, 150, 170), 'lit': PINK, 'dead': HARM}[state]
    lines = wrap(d, a['info'], F['p19'], w_ - 48)
    if state == 'dead':
        lines = ["CAN'T USE"] + wrap(d, a['why'], F['p19'], w_ - 48)
    h_ = 18 + 22 * len(lines)
    d.line([(S(x), S(y - 12)), (S(x), S(y))], fill=(120, 140, 160, 255), width=S(2))
    d.rectangle([S(x - w_ / 2), S(y), S(x + w_ / 2), S(y + h_)], fill=GLASS + (235,), outline=edge + (255,), width=S(2 if state == 'idle' else 3))
    ram_coin(d, x - w_ / 2 + 20, y + 20, a['cost'], F['a22'], r=14, red=(state == 'dead'))
    for k, ln in enumerate(lines[:3]):
        col = (TEXT_HI if state != 'dead' else (255, 150, 140))
        text(d, (x - w_ / 2 + 40, y + 20 + 22 * k), ln, F['p19'], col + (255,), anchor='lm')


WALL = (16, 150, 522, 790)
SLOTS = {'NUDGE': (108, 296, -3), 'WORM': (268, 214, 2), 'BREACH': (432, 216, -2), 'GUARD': (180, 500, 3), 'TIMEBOMB': (360, 502, -2)}
WSC = 0.74


def df_wall_bg(img):
    """the runner's wall: dark concrete with torn paste-up scraps (kept quiet so the stencils lead)"""
    x0, y0, x1, y1 = WALL
    rng = np.random.default_rng(3)
    w_, h_ = S(x1 - x0), S(y1 - y0)
    n = rng.normal(0, 1, (h_ // 4 + 1, w_ // 4 + 1)).astype(np.float32)
    n = np.asarray(Image.fromarray(((n * 18) + 128).clip(0, 255).astype(np.uint8)).resize((w_, h_), Image.BICUBIC), np.float32) - 128
    base = np.array((34, 32, 38), np.float32)[None, None, :] + n[..., None] * 0.35
    wall = Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(wall)
    for k in range(9):             # old torn posters, low contrast
        cx_, cy_ = rng.uniform(0, w_), rng.uniform(0, h_)
        r_ = rng.uniform(S(30), S(90))
        pts = [(cx_ + r_ * math.cos(t) * rng.uniform(0.6, 1.2), cy_ + r_ * math.sin(t) * rng.uniform(0.5, 1.1)) for t in np.linspace(0, 2 * math.pi, 11)]
        d.polygon(pts, fill=(58, 54, 58, 255) if k % 3 else (64, 44, 58, 255))
    L = Layer()
    L.im.paste(wall, (S(x0), S(y0)))
    dd = L.d
    poly = [(S(x0), S(y0)), (S(x1), S(y0)), (S(x1), S(y1)), (S(x0), S(y1))]
    dd.line(poly + [poly[0]], fill=INK + (255,), width=S(3))
    comp(img, L)


def pile_icon(d, F, x, y, kind, wd, cap, n):
    if kind == 'roll':            # the uncut roll: a paper roll seen end-on, spiral
        d.rectangle([S(x - 2), S(y - 22), S(x + 64), S(y + 22)], fill=PAPER + (255,), outline=INK + (255,), width=S(2))
        d.ellipse([S(x - 22), S(y - 22), S(x + 22), S(y + 22)], fill=(226, 220, 206, 255), outline=INK + (255,), width=S(3))
        for r in (14, 8):
            d.arc([S(x - r), S(y - r), S(x + r), S(y + r)], 30, 320, fill=INK + (255,), width=S(2))
    elif kind == 'peeled':        # peeled stencils: two torn sheets, curled, with spray on them
        for k, (dx, rot) in enumerate(((0, -8), (14, 6))):
            a = math.radians(rot)
            pts = [(-20, -24), (22, -22), (26, 20), (-6, 26), (-24, 10)]
            P = [(S(x + 18 + dx + px * math.cos(a) - py * math.sin(a)), S(y + px * math.sin(a) + py * math.cos(a))) for px, py in pts]
            d.polygon([(px + S(2), py + S(3)) for px, py in P], fill=INK + (255,))
            d.polygon(P, fill=(PAPER if k else (214, 206, 190)) + (255,), outline=INK + (255,), width=S(2))
        d.ellipse([S(x + 30), S(y - 8), S(x + 42), S(y + 4)], fill=PINK + (255,))
    else:                         # burnt: a charred, curled sheet
        pts = [(-22, -22), (20, -24), (24, 18), (-4, 24), (-24, 6)]
        P = [(S(x + 18 + px), S(y + py)) for px, py in pts]
        d.polygon(P, fill=(60, 48, 44, 255), outline=INK + (255,), width=S(2))
        d.line([(S(x + 4), S(y + 18)), (S(x + 38), S(y - 18))], fill=(180, 90, 40, 255), width=S(2))
    text(d, (x + 84, y - 8), wd + '  %d' % n, F['a26'], TEXT_HI + (255,), anchor='lm')
    text(d, (x + 84, y + 20), cap, F['m18'], TEXT_MID + (255,), anchor='lm')


def df_left(img, F, aim):
    L = Layer(); d = L.d
    run_health(d, F, 24, 516, 18)
    energy_status(d, F, 24, 516, 108, 140 + 0)
    comp(img, L)
    df_wall_bg(img)
    L = Layer(); d = L.d
    text(d, (32, 176), 'YOUR WALL', F['a24'], PAPER + (255,), anchor='lm')
    text(d, (152, 177), 'hand: hold a stencil over a wedge', F['m18'], TEXT_MID + (255,), anchor='lm')
    comp(img, L)
    for a in ACTS:
        x, y, rot = SLOTS[a['id']]
        held = aim and a['id'] == 'BREACH'
        mode = 'dead' if a.get('why') else 'wall'
        if held:              # its place on the wall: a dashed ghost and the tape left behind
            L = Layer(); d = L.d
            sc = WSC
            r0, r1, hw = (TR.R_IN - 8) * sc, (TR.R_OUT + 10) * sc, math.radians(16.5)
            vy = y + r1 * 0.98
            pts = [(x + r1 * math.sin(-hw + 2 * hw * t / 20), vy - r1 * math.cos(-hw + 2 * hw * t / 20)) for t in range(21)]
            pts += [(x + r0 * math.sin(hw - 2 * hw * t / 20), vy - r0 * math.cos(hw - 2 * hw * t / 20)) for t in range(21)]
            pts.append(pts[0])
            dash_poly(d, pts, (150, 140, 150), 2)
            tape(d, pts[0][0] + 6, pts[0][1] + 4, 40); tape(d, pts[20][0] - 6, pts[20][1] + 4, -40)
            text(d, (x, vy - (r0 + r1) / 2), 'held', F['m18'], PINK + (255,))
            comp(img, L)
        else:
            if a['tgt'] == 'hub':
                im, v = stencil(a, WSC, mode)
                place(img, im, v, (x, y), rot)
                L = Layer(); d = L.d
                tape(d, x - 40, y - 66, -30); tape(d, x + 44, y - 62, 28)
                key_cap(d, x - 64, y - 52, a['key'], F['m20'], inv=True)
                comp(img, L)
            else:
                sc = WSC
                r1 = (TR.R_OUT + 10) * sc
                vy = y + r1 * 0.98                  # the sheet's outer arc tops out near y - r1 + ...; y is the visual top
                im, v = stencil(a, sc, mode)
                place(img, im, v, (x, vy), rot)
                L = Layer(); d = L.d
                hw = math.radians(16.5)
                tl = (x + r1 * math.sin(-hw), vy - r1 * math.cos(-hw)); tr_ = (x + r1 * math.sin(hw), vy - r1 * math.cos(hw))
                tape(d, tl[0] + 4, tl[1] + 6, 40); tape(d, tr_[0] - 4, tr_[1] + 6, -40)
                key_cap(d, tl[0] - 4, tl[1] - 2, a['key'], F['m20'], inv=True)
                if mode == 'dead':           # can't use: a red X of tape across it
                    cy_ = vy - (TR.R_IN - 8 + 0.47 * (TR.R_OUT - TR.R_IN + 18)) * sc
                    p0 = (x - 74, cy_ + 22); p1 = (x + 74, cy_ - 16)
                    d.line([(S(p0[0] + 2), S(p0[1] + 4)), (S(p1[0] + 2), S(p1[1] + 4))], fill=INK + (255,), width=S(34))
                    d.line([(S(p0[0]), S(p0[1])), (S(p1[0]), S(p1[1]))], fill=HARM + (255,), width=S(30))
                    ang_ = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
                    tl_ = Image.new('RGBA', (S(160), S(40)), (0, 0, 0, 0))
                    ImageDraw.Draw(tl_).text((S(80), S(21)), 'NO RAM', font=F['a24'], fill=INK + (255,), anchor='mm')
                    tl_ = tl_.rotate(-ang_, resample=Image.BICUBIC, expand=True)
                    L.im.alpha_composite(tl_, (int(S(x) - tl_.width / 2), int(S((p0[1] + p1[1]) / 2) - tl_.height / 2)))
                comp(img, L)
        # the payload tag under the stencil (cost + rule), pinned
        L = Layer(); d = L.d
        ty = (y + WSC * 80 / 0.7 + 14) if a['tgt'] == 'hub' else (y + (TR.R_OUT + 10) * WSC * 0.98 - (TR.R_IN - 8) * WSC + 10)
        payload_tag(d, F, x, ty, a, 'dead' if a.get('why') else ('lit' if held else 'idle'))
        comp(img, L)
    L = Layer(); d = L.d
    piles = [('roll', 'DRAW', 'the uncut roll', BOARD['hud']['piles'][0]), ('peeled', 'DISCARD', 'peeled', BOARD['hud']['piles'][1]),
             ('burnt', 'EXHAUST', 'burnt', 0)]
    # the piles sit at the wall's foot
    for k, (kind, wd, cap, n) in enumerate(piles):
        pile_icon(d, F, 40 + (k % 2) * 250, 840 + (k // 2) * 74, kind, wd, cap, n)
    undo_tab(d, F, 300, 892, 508, 940, word='UNDO')
    if aim:
        text(d, (32, 1010), 'BREACH fits CORE and FIREWALL (next to yours)', F['m18'], FOCUS + (255,), anchor='lm')
    comp(img, L)


def dash_poly(d, pts, col, w, on=8, off=6):
    acc, draw_on = 0.0, True
    for a, b in zip(pts, pts[1:]):
        L_ = math.dist(a, b); t = 0.0
        while t < L_:
            lim = (on if draw_on else off) - acc
            step = min(lim, L_ - t)
            p = (a[0] + (b[0] - a[0]) * t / L_, a[1] + (b[1] - a[1]) * t / L_)
            q = (a[0] + (b[0] - a[0]) * (t + step) / L_, a[1] + (b[1] - a[1]) * (t + step) / L_)
            if draw_on:
                d.line([(S(p[0]), S(p[1])), (S(q[0]), S(q[1]))], fill=col + (255,), width=S(w))
            t += step; acc += step
            if acc >= (on if draw_on else off) - 1e-6:
                draw_on = not draw_on; acc = 0.0


def spray_tag(img, F, st):
    """lasting effects you put on a wedge stay as sprayed tags (pink spray, soft edge, drips) on the wedge's outer edge"""
    L = Layer()
    m = Image.new('L', (W * SS, H * SS), 0); dm = ImageDraw.Draw(m)
    drips = []
    for i, g in enumerate(st['segs']):
        for j, (word, side) in enumerate(g.get('st', [])):
            if side != 'runner':
                continue
            a0, a1, am = TR.seg_angles(i, st['rot'])
            da = 0.16 if math.sin(am) > 0 else -0.17      # the free corner of the wedge, clear of its label group
            x, y = CX + (TR.R_OUT - 30) * math.cos(am + da), CY + (TR.R_OUT - 30) * math.sin(am + da)
            dm.text((S(x), S(y)), word, font=F['a30'], fill=255, anchor='mm')
            bb = dm.textbbox((S(x), S(y)), word, font=F['a30'], anchor='mm')
            for k, fx in enumerate((0.22, 0.7)):
                drips.append((bb[0] + (bb[2] - bb[0]) * fx, bb[3] - S(3), S(5 + 5 * k)))
    for x, y, ln in drips:
        dm.line([(x, y), (x, y + ln)], fill=255, width=S(3)); dm.ellipse([x - S(2.6), y + ln - S(2.6), x + S(2.6), y + ln + S(2.6)], fill=255)
    sp = overspray(m, S(5), 0.3, 9)
    key = m.filter(ImageFilter.MaxFilter(S(2.5) * 2 + 1))
    L.im.paste(Image.new('RGBA', m.size, PINK + (255,)), (0, 0), sp)
    L.im.paste(Image.new('RGBA', m.size, INK + (255,)), (0, 0), key)
    L.im.paste(Image.new('RGBA', m.size, PINK + (255,)), (0, 0), m)
    comp(img, L)


def df_right(img, F, st, aim):
    L = Layer(); d = L.d
    hud = st['hud']
    x0, x1 = 1404, 1898
    # the compliance board: slate enamel, teal edge, rivets; clean (nothing of yours is on it)
    y0, y1 = 18, 600
    d.rectangle([S(x0 + 4), S(y0 + 5), S(x1 + 4), S(y1 + 5)], fill=INK + (255,))
    d.rectangle([S(x0), S(y0), S(x1), S(y1)], fill=(48, 55, 66, 255), outline=TEAL + (255,), width=S(3))
    d.rectangle([S(x0 + 3), S(y0 + 3), S(x1 - 3), S(y0 + 44)], fill=(70, 80, 94, 255))
    d.line([(S(x0 + 3), S(y0 + 44)), (S(x1 - 3), S(y0 + 44))], fill=TEAL + (255,), width=S(2))
    for rx, ry in ((x0 + 12, y0 + 12), (x1 - 12, y0 + 12), (x0 + 12, y1 - 12), (x1 - 12, y1 - 12)):
        d.ellipse([S(rx - 4), S(ry - 4), S(rx + 4), S(ry + 4)], fill=CLOCK_LT + (255,), outline=INK + (255,), width=S(1))
    text(d, (x0 + 28, y0 + 23), 'SOLACE', F['a24'], TEAL_HI + (255,), anchor='lm')
    text(d, (x0 + 118, y0 + 24), 'compliance board', F['m20'], K_TYPE + (255,), anchor='lm')
    text(d, (x1 - 28, y0 + 24), hud['title'].split(' · ')[0], F['m20'], TEXT_MID + (255,), anchor='rm')
    # the notice: wheel kind + rule
    text(d, (x0 + 22, y0 + 76), hud['kind'], F['a30'], K_TYPE + (255,), anchor='lm')
    text(d, (x1 - 22, y0 + 76), 'T1 FIGHT', F['a26'], TEXT_MID + (255,), anchor='rm')
    for k, ln in enumerate(wrap(d, hud['rule'], F['m20'], x1 - x0 - 44)):
        text(d, (x0 + 22, y0 + 112 + 27 * k), ln, F['m20'], TEXT_MID + (255,), anchor='lm')
    y = y0 + 186
    text(d, (x0 + 22, y), 'TURN', F['m20'], TEXT_MID + (255,), anchor='lm')
    text(d, (x0 + 78, y), str(hud['turn']), F['a30'], K_TYPE + (255,), anchor='lm')
    text(d, (x0 + 130, y), 'ESCALATION', F['m20'], TEXT_MID + (255,), anchor='lm')
    text(d, (x0 + 256, y), hud['esc'], F['a28'], K_TYPE + (255,), anchor='lm')
    y += 34
    text(d, (x0 + 22, y), 'CORP PLAN', F['m20'], TEXT_MID + (255,), anchor='lm')
    for k, (nm, sub) in enumerate(hud['plan']):
        yy = y + 20 + k * 80
        plan_ticket(d, F, x0 + 22, yy, x1 - 22, yy + 66, k, nm, sub)
    y = y + 20 + 3 * 80 + 24
    text(d, (x0 + 22, y), 'ARMED', F['m20'], TEXT_MID + (255,), anchor='lm')
    x = x0 + 100
    for i, g in enumerate(st['segs']):
        if g.get('armed') and g['owner'] != 'us':
            hot_mark(d, x + 16, y - 2)
            text(d, (x + 40, y), g['type'], F['m20'], K_TYPE + (255,), anchor='lm')
            x += 40 + tw(d, g['type'], F['m20']) + 26
    hint = ['click or Enter: spray it', 'Esc: put it back on the wall'] if aim else None
    fb = 620 + (270 if aim else 136)
    forecast_panel(d, F, (x0, 620, x1, fb), st, aim_hint=hint)
    end_turn_btn(d, F, 1640, 912, 1898, 1048, sub='SPACE')
    comp(img, L)


def df_held(img, F, st):
    """aim: the BREACH stencil held over the target wedge, turned to it, slightly off-true; the cut-out shows the pink paint"""
    a = [x for x in ACTS if x['id'] == 'BREACH'][0]
    im, v = stencil(a, 1.0, 'held')
    am = TR.seg_angles(st['aim'], st['rot'])[2]
    rot = -(math.degrees(am) + 90) - 1.2           # PIL: positive = counter-clockwise; the wedge points up in the stencil
    off = 4
    at = (CX + off * math.cos(am + 0.6), CY + off * math.sin(am + 0.6))
    # a soft drop shadow: it is held above the wheel
    sh = im.split()[3].point(lambda p: int(p * 0.55))
    shadow = Image.new('RGBA', im.size, INK + (0,)); shadow.putalpha(sh.filter(ImageFilter.GaussianBlur(S(6))))
    place(img, shadow, v, (at[0] + 10, at[1] + 14), rot)
    place(img, im, v, at, rot)


def render_df(aim):
    st = copy.deepcopy(PLAY if aim else BOARD)
    F = F_all()
    img = base_image()
    draw_wheel(img, st, F, statuses=False)
    spray_tag(img, F, st)
    if aim:
        df_held(img, F, st)
    TR.draw_outcomes(img, st, F)
    df_left(img, F, aim)
    df_right(img, F, st, aim)
    return img


# =============================================================================================== sheet
def sheet():
    names = [('pl_rest', 'PACKET LADDER, rest', 'packets on your lifeline: len = cost, flag = type word, dst = target'),
             ('pl_aim', 'PACKET LADDER, aim', 'BREACH runs along the rim groove to FIREWALL as packet P1; the wedge shows TAKEN'),
             ('df_rest', 'DEFACE, rest', 'stencils taped on your wall; lasting effects sprayed on as tags; the corp compliance board'),
             ('df_aim', 'DEFACE, aim', 'the BREACH stencil held over FIREWALL; the cut-out shows the pink paint; TAKEN')]
    tw_, th_ = 940, 529
    pad, cap = 14, 64
    sh = Image.new('RGB', (2 * tw_ + 3 * pad, 2 * (th_ + cap) + 3 * pad + 50), (14, 14, 18))
    d = ImageDraw.Draw(sh)
    f = TR.ImageFont.truetype(MONO, 17); fa = TR.ImageFont.truetype(ANTON, 22); fb = TR.ImageFont.truetype(ANTON, 30)
    d.text((pad, 14), 'TAKEOVER ACTIONS, RENDERED: PACKET LADDER (top) and DEFACE (bottom)', font=fb, fill=TEXT_HI)
    for k, (n, t, c) in enumerate(names):
        im = Image.open(OUT + n + '.png').resize((tw_, th_), Image.LANCZOS)
        x = pad + (k % 2) * (tw_ + pad); y = 60 + pad + (k // 2) * (th_ + cap + pad)
        sh.paste(im, (x, y))
        d.text((x + 4, y + th_ + 6), '%s   %s.png' % (t, n), font=fa, fill=TEXT_HI)
        d.text((x + 4, y + th_ + 38), c, font=f, fill=TEXT_MID)
    sh.save(OUT + 'render_sheet.jpg', quality=90)
    print('ok', OUT + 'render_sheet.jpg')


R = dict(pl_rest=lambda: render_pl(False), pl_aim=lambda: render_pl(True), df_rest=lambda: render_df(False), df_aim=lambda: render_df(True))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for n in (sys.argv[1:] or ['pl_rest', 'pl_aim', 'df_rest', 'df_aim', 'sheet']):
        if n == 'sheet':
            sheet(); continue
        img = R[n]()
        img.resize((W, H), Image.LANCZOS).convert('RGB').save(OUT + n + '.png')
        print('ok', OUT + n + '.png')
