"""objectives cluster, design round 2: the stars row (OBJECTIVES) and the RAM / TRACE / HEAT terminal (RESOURCES) of the E10 column.
Self-contained drawing code, one function per element (see NOTES_R2 in the sheets folder for the map):
  objectives_frame -> el_obj_frame        star_glyph -> star_tile / el_star / fail_mark      win_label -> el_win_label
  challenge_labels -> layout in objectives_row + ch_label                                      challenge_tallies -> el_tally
  challenge_trigger_hits -> trig_tally     ram_trace_frame -> el_res_frame      ram_trace_labels -> el_res_label
  ram_pips -> coin_img (the screen-wide RAM coin: cards import it)     trace_pips -> sq_img     trace_cap_hatch -> el_cap
  ends_heat -> flame_img / el_heat_pips    ram_refund_pop -> pop_rays (+ coin plus)
V[element] = 'A' (AD pick, refined) | 'B' (the one variant).  Rows plug into hud2 (top_hud R2 reference copy) via hud2.objectives_row / hud2.ram_row.
Never run python - ; run by path."""
import sys, os, math, copy
sys.dont_write_bytecode = True
from build10 import *
import build10 as B10
from PIL import Image, ImageDraw, ImageFilter

V = {}
R = {}

# ------------------------------------------------------------------------------------------------------ tokens (BRIEF 3.3 / 3.11)
TBG = (5, 13, 28)
THI = (242, 246, 255)
TMID = (175, 192, 214)
TLO = (122, 136, 156)
HARM = (255, 68, 51)
RGOLD = (255, 210, 77)       # reward gold #FFD24D: stars met, WIN label (with the star shape only)
BOSSG = (255, 196, 40)       # BOSS_GOLD #FFC428: the Adjuster tally (matches wave_rings' board bar)
HEATC = (255, 176, 0)        # CRT_AMBER #FFB000: Heat
VIO = (160, 60, 255)         # TRACE_VIOLET #A03CFF
CRM = (255, 244, 214)        # CREAM: enemy HP (the TRIGGER HITS tally is the AD's pick: cream)
CY = CYAN                    # NET_CYAN #5CE1FF
SOAKC = __import__('asm_tokens').SOAK      # SOAK #6A6CFF (cvd check only)
FOCUS = (212, 255, 0)
NAMES = {'card': 'TRIGGER HITS', 'daemon': 'KILL ADJUSTER', 'heat': 'TRACE LOW', 'scrap': 'SLICES KEPT'}
PX0, PX1 = 1072, 1896        # column x1072..1896 (BRIEF 3.11 rule 14)
OBJ_H, RES_H = 48, 50        # budget: p1 stack bottom <= y384 -> 278 + 48 + 8 + 50 = 384
TRK = 0.08                   # mono caps tracking (type ladder)
LBL_PX, WIN_PX = 18, 22      # mono label / WIN size (rb_patch sets the rebuild's 23 / 23: cap 16.1)
OBJ_MIN_GAP = 0              # objectives row: below this gap per challenge the row wraps to the 2 x 2 grid (rb_patch: 22)


def v(k):
    return V.get(k, 'A')


def reg(n, b):
    R[n] = tuple(b)


# ------------------------------------------------------------------------------------------------------ helpers
def ttw(L, s, px, kind='mono', track=0.0):
    return L.tw(s, px, kind) + track * px * max(0, len(s) - 1)


def txt(L, x, y, s, px, col, kind='mono', anchor='lm', track=0.0):
    w = ttw(L, s, px, kind, track)
    if not NOW['words']:
        return w
    col = tuple(col)[:3] + (255,)
    if not track:
        L.text((x, y), s, px, kind, fill=col, anchor=anchor)
        return w
    x0 = x if anchor[0] == 'l' else (x - w / 2 if anchor[0] == 'm' else x - w)
    for ch in s:
        L.text((x0, y), ch, px, kind, fill=col, anchor='lm')
        x0 += L.tw(ch, px, kind) + track * px
    return w


def sprite(L, x, y, w, h, fn, k=8, pad=6):
    """small supersampled tile: fn(d, T, k), T maps screen px -> tile px"""
    x0 = int(math.floor(x)) - pad
    y0 = int(math.floor(y)) - pad
    tw = int(math.ceil(w)) + 2 * pad + 1
    th = int(math.ceil(h)) + 2 * pad + 1
    t = Image.new('RGBA', (tw * k, th * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    fn(d, lambda X, Y: ((X - x0) * k, (Y - y0) * k), k)
    t = t.resize((tw * L.k, th * L.k), Image.LANCZOS)
    L.im.alpha_composite(t, (x0 * L.k, y0 * L.k))


def ln(d, T, k, pts, col, w):
    pp = [T(x, y) for x, y in pts]
    d.line(pp, fill=col, width=int(round(w * k)), joint='curve')
    for p in (pp[0], pp[-1]):
        d.ellipse([p[0] - w * k / 2, p[1] - w * k / 2, p[0] + w * k / 2, p[1] + w * k / 2], fill=col)


def _dil(m, d):
    return m.filter(ImageFilter.GaussianBlur(d)).point(lambda p: 255 if p > 41 else 0)


def _ero(m, d):
    return m.filter(ImageFilter.GaussianBlur(d)).point(lambda p: 255 if p > 214 else 0)


def _rnd(m, rk):
    n = 2 * int(rk) + 1
    return m.filter(ImageFilter.MinFilter(n)).filter(ImageFilter.MaxFilter(n))


def _lay(img, mask, col):
    img.paste(Image.new('RGBA', img.size, tuple(col) + ((255,) if len(col) == 3 else ())), (0, 0), mask)


def star_pts(cx, cy, r, inner=0.5, rot=-90):
    out = []
    for i in range(10):
        a = math.radians(rot + 36 * i)
        rr_ = r if i % 2 == 0 else r * inner
        out.append((cx + rr_ * math.cos(a), cy + rr_ * math.sin(a)))
    return out


def tile_paste(L, img, cx, cy, szw, szh, k):
    t = img.resize((szw * L.k, szh * L.k), Image.LANCZOS)
    L.im.alpha_composite(t, (int(round(cx - szw / 2)) * L.k, int(round(cy - szh / 2)) * L.k))


def scan(L, x0, y0, x1, y1, pitch=4, a=20, inset=6):
    for y in range(int(y0) + inset, int(y1) - inset + 1, pitch):
        L.line([(x0 + inset, y), (x1 - inset, y)], (0, 0, 0, a), 1)


def kit_plate(L, box, edge=CY):
    """terminal_plate_kit A: 93 percent fill, cyan 2 px, r8, 4 px scanlines alpha 20 (same call as hud2.P)"""
    import hud2      # ASSEMBLY (Y5): hud2.P is the kit plate
    hud2.P(L, box, 'plate', col=edge)


def gone_pip(L, x, cy, w=7, h=15):
    """HP grammar: gone = dark socket + solid 1.4 px hairline"""
    L.rect([x, cy - h / 2, x + w, cy + h / 2], fill=(8, 14, 22, 255), outline=TLO + (255,), w=1.4, r=3)


def cap_pip(L, x, cy, col, w=7, h=15):
    """HP grammar kept segment: rounded r3, ink keyline"""
    L.rect([x, cy - h / 2, x + w, cy + h / 2], fill=tuple(col) + (255,), outline=INK + (255,), w=1.3, r=3)


# ------------------------------------------------------------------------------------------------------ objectives_frame
def el_obj_frame(L, box, win_bay=None):
    """A: the twin kit plate (same call as the RAM plate), 48 px.  B: + a WIN bay (inset dark glass with a reward-gold hairline foot, the bill's inset language)"""
    kit_plate(L, box)
    if v('objectives_frame') == 'B' and win_bay:
        bx0, bx1 = win_bay
        y0, y1 = box[1], box[3]
        L.rect([bx0, y0 + 6, bx1, y1 - 6], fill=(0, 4, 12, 150), r=5)
        L.line([(bx0 + 5, y1 - 6), (bx1 - 5, y1 - 6)], RGOLD + (96,), 1.4)


# ------------------------------------------------------------------------------------------------------ star_glyph
_STC = {}
STAR_BIG, STAR_SMALL = 20, 15.5


def star_tile(state, big):
    key = (state, big)
    if key in _STC:
        return _STC[key]
    k = 8
    r = STAR_BIG if big else STAR_SMALL
    sz = int(2 * r + 8)
    c = sz / 2
    img = Image.new('RGBA', (sz * k, sz * k), (0, 0, 0, 0))

    def M(fn):
        m = Image.new('L', (sz * k, sz * k), 0)
        fn(ImageDraw.Draw(m))
        return m
    sr = r - 2.6
    m = _rnd(M(lambda dd: dd.polygon([(x * k, y * k) for x, y in star_pts(c, c + 0.5, sr, 0.5)], fill=255)), 0.95 * k)
    _lay(img, _dil(m, 2.5 * k), INK)                       # sticker keyline in every state
    if state == 'open':                                     # white outline on dark glass
        _lay(img, m, THI)
        _lay(img, _ero(m, 2.0 * k), (14, 20, 36))
    elif state == 'met':                                    # reward gold, shaded rim, soft highlight
        _lay(img, m, (226, 170, 40))
        _lay(img, _ero(m, 1.5 * k), RGOLD)
        hl = _rnd(M(lambda dd: dd.polygon([(x * k, y * k) for x, y in star_pts(c - 0.1 * sr, c + 0.5 - 0.14 * sr, sr * 0.55, 0.5)], fill=255)), 0.6 * k)
        _lay(img, hl, (255, 234, 150))
    else:                                                   # failed: dark star, muted rim (the slash sits BESIDE it)
        _lay(img, m, (132, 98, 106))
        _lay(img, _ero(m, 2.0 * k), (30, 24, 34))
    _STC[key] = (img, sz, k)
    return _STC[key]


FAIL_SLOT = 14


def fail_mark(L, x, cy):
    """failed marker beside the star (never over its body).  A: HARM slash (ink keyline); B: the HP-grammar lost-now pip (HARM, white 2 px slash, ink)"""
    if v('star_glyph') == 'B':
        cap_pip(L, x - 3.5, cy + 1, HARM, 7, 15)
        L.line([(x - 3.0, cy + 7.5), (x + 3.0, cy - 5.5)], INK, 4.2)
        L.line([(x - 3.0, cy + 7.5), (x + 3.0, cy - 5.5)], (255, 255, 255), 2)
    else:
        def fn(d, T, k):
            pts = [(x - 3.6, cy + 8.2), (x + 3.6, cy - 6.4)]
            ln(d, T, k, pts, INK + (255,), 6.6)
            ln(d, T, k, pts, HARM + (255,), 3.4)
        sprite(L, x - 8, cy - 10, 16, 20, fn)


def star_w(big, state):
    r = STAR_BIG if big else STAR_SMALL
    return 2 * r + (FAIL_SLOT if state == 'failed' else 0)


def el_star(L, x, cy, state, big):
    """x = left edge of the star cell; returns the right edge (including the failed slot)"""
    r = STAR_BIG if big else STAR_SMALL
    img, sz, k = star_tile(state, big)
    tile_paste(L, img, x + r, cy, sz, sz, k)
    if state == 'failed':
        fail_mark(L, x + 2 * r + 6.5, cy)
    return x + star_w(big, state)


# ------------------------------------------------------------------------------------------------------ win_label (A: mono 22 reward gold +10 percent; AD overruled B)
def win_w(L):
    return ttw(L, 'WIN', WIN_PX, 'mono', 0.10)


def el_win_label(L, x, cy):
    txt(L, x, cy, 'WIN', WIN_PX, RGOLD, track=0.10)
    return x + win_w(L)


# ------------------------------------------------------------------------------------------------------ challenge labels / tallies
def ch_w(L, name):
    return ttw(L, NAMES[name], LBL_PX, 'mono', TRK)


def ch_label(L, x, cy, name):
    txt(L, x, cy, NAMES[name], LBL_PX, THI, track=TRK)


TW, TH, TP, TG = 7, 15, 10, 14        # capsule w, h, pitch, group gap (bill tally geometry; group gap tighter than the bill's 16 to fit the row)


def tpos(n):
    return [i * TP + (i // 5) * (TG - (TP - TW)) for i in range(n)]


def tally_width(n):
    return tpos(n)[-1] + TW if n else 0


def tally_spec(f, name):
    """(lit, total sockets, colour) of a challenge tally; None = no tally (SLICES KEPT has none)"""
    cons = f['consts']
    if name == 'card':
        return min(f['interf'], cons['STAR_CARD']), cons['STAR_CARD'], CRM
    if name == 'daemon':
        return f['adj']['hp'], f['adj'].get('mx') or cons['EHP'], BOSSG
    if name == 'heat':
        n = min(f['trace'], 5)
        return n, n, VIO
    return None


def tally_w(f, name, lead=0):
    t = tally_spec(f, name)
    if t is None or t[1] == 0:
        return 0
    w = tally_width(t[1])
    if name == 'card' and v('challenge_trigger_hits') == 'B':
        w += 26
    if name != 'card' and v('challenge_tallies') == 'B' and name in ('daemon', 'heat'):
        w += 22
    return w


def el_tally(L, f, x, cy, name):
    """challenge_tallies A: HP-grammar capsules in groups of 5; Adjuster BOSS_GOLD, Trace violet; gone socket for HP lost.  B: + a lead mark in the board shape
    (gold boss diamond / violet Trace square).  SLICES KEPT has no tally (content guard: no new display).  TRIGGER HITS = trig_tally"""
    t = tally_spec(f, name)
    if t is None:
        return 0
    n, tot, col = t
    if name == 'card':
        return trig_tally(L, x, cy, n, tot)
    if v('challenge_tallies') == 'B':
        ic = x + 8
        if name == 'daemon':
            L.poly([(ic, cy - 9.5), (ic + 8, cy), (ic, cy + 9.5), (ic - 8, cy)], fill=BOSSG, outline=INK, w=2)
        else:
            L.rect([ic - 7, cy - 7, ic + 7, cy + 7], fill=VIO + (255,), outline=INK + (255,), w=1.8, r=3)
        x += 22
    for i, o in enumerate(tpos(tot)):
        if i < n:
            cap_pip(L, x + o, cy, col)
        else:
            gone_pip(L, x + o, cy)
    return tally_w(f, name)


def trig_tally(L, x, cy, n, tot):
    """challenge_trigger_hits A: cream pips, 8 sockets in groups of 5 (5 + 3), LATENT.  B: + the Trigger card glyph as the lead mark"""
    if v('challenge_trigger_hits') == 'B':
        L.glyph('KA_trigger', 22, (x + 11, cy), THI)
        x += 26
    for i, o in enumerate(tpos(tot)):
        if i < n:
            cap_pip(L, x + o, cy, CRM)
        else:
            gone_pip(L, x + o, cy)
    return tally_w({'consts': {'STAR_CARD': tot}, 'interf': n}, 'card')


# ------------------------------------------------------------------------------------------------------ objectives row (frame + stars + labels + tallies)
def objectives_row(L, f, y):
    chs = [dict(c) for c in f['challenges']]
    win_state = f.get('win_state', 'open')
    xa, xb = PX0 + 16, PX1 - 16
    ww = win_w(L)
    wcell = star_w(True, win_state) + 10 + ww
    xdiv = xa + wcell + 14
    for c in chs:
        c['lw'] = ch_w(L, c['name'])
        c['tw'] = tally_w(f, c['name'])
        c['w'] = star_w(False, c['state']) + 7 + c['lw'] + ((10 + c['tw']) if c['tw'] else 0)
    # the 4th challenge (LATENT TRIGGER HITS) wraps to a 2 x 2 grid; so does a row whose gaps would fall under OBJ_MIN_GAP (2026-11-03: 23 px labels)
    two = len(chs) > 3 or (sum(c['w'] for c in chs) + len(chs) * OBJ_MIN_GAP > xb - xdiv)
    H = 84 if two else OBJ_H
    box = (PX0, y, PX1, y + H)
    el_obj_frame(L, box, (xa - 10, xdiv - 7))
    reg('obj_plate', box)
    cyw = y + H / 2
    sx = el_star(L, xa, cyw, win_state, True)
    reg('star_win', (xa, cyw - STAR_BIG, xa + 2 * STAR_BIG, cyw + STAR_BIG))
    el_win_label(L, sx + 10, cyw)
    reg('win_label', (sx + 10, cyw - 16, sx + 10 + ww, cyw + 16))
    L.line([(xdiv, y + 9), (xdiv, y + H - 9)], CY + (77,), 1.4)
    rows = [chs[i:i + 2] for i in range(0, len(chs), 2)] if two else [chs]
    if two:
        # grid: two columns, equal gaps, first row = challenges 0-1 (card, scrap), second = 2-3
        cw = [max(rows[0][j]['w'], rows[1][j]['w'] if j < len(rows[1]) else 0) for j in range(2)]
        g = (xb - xdiv - sum(cw)) / 2.0
        colx = [xdiv + g, xdiv + g * 2 + cw[0]]
    idx = 0
    for ri, rw in enumerate(rows):
        cyr = (y + H / 4 + ri * H / 2) if two else cyw
        if not two:
            g = (xb - xdiv - sum(c['w'] for c in rw)) / len(rw)
            x = xdiv + g
        for ji, c in enumerate(rw):
            if two:
                x = colx[ji]
            sx_ = el_star(L, x, cyr, c['state'], False)
            lx = sx_ + 7 - (FAIL_SLOT if False else 0)
            ch_label(L, lx, cyr, c['name'])
            if c['tw']:
                el_tally(L, f, lx + c['lw'] + 10, cyr, c['name'])
            reg('star_%d' % idx, (x, cyr - STAR_SMALL, x + 2 * STAR_SMALL, cyr + STAR_SMALL))
            reg('ch_%d' % idx, (lx - 2, cyr - 14, x + c['w'] + 2, cyr + 14))
            reg('tally_%d' % idx, (lx + c['lw'] + 8, cyr - 12, x + c['w'] + 2, cyr + 12))
            if not two:
                x += c['w'] + g
            idx += 1
    R['_gap'] = (g,)
    return y + H


# ------------------------------------------------------------------------------------------------------ RAM / TRACE / HEAT
_CT = {}


def coin_img(d=24, state='lit', plus=False, inner_spent=False):
    """THE RAM coin (the screen-wide master; the card cost badge and the refund token call this).  d = cyan disc diameter in px.
    lit: NET_CYAN disc, ink keyline 1.8 outside, inner ring hairline at INK 60 percent.  spent: dark socket, 2 px cyan ring at 50 percent.
    plus: 3 px INK plus (refund token).  Returns (RGBA tile at 8x, size px, k)"""
    key = (d, state, plus, inner_spent)
    if key in _CT:
        return _CT[key]
    k = 8
    s = d / 24.0
    sz = int(math.ceil(d + 8))
    c = sz / 2
    img = Image.new('RGBA', (sz * k, sz * k), (0, 0, 0, 0))
    g = ImageDraw.Draw(img)
    r = d / 2

    def disc(rr, **kw):
        g.ellipse([(c - rr) * k, (c - rr) * k, (c + rr) * k, (c + rr) * k], **kw)
    disc(r + 1.8 * s, fill=INK + (255,))
    if state == 'lit':
        disc(r, fill=CY + (255,))
        ri = r * 0.66
        m = Image.new('L', img.size, 0)
        md = ImageDraw.Draw(m)
        md.ellipse([(c - ri) * k, (c - ri) * k, (c + ri) * k, (c + ri) * k], outline=255, width=int(round(1.2 * s * k)))
        _lay(img, m.point(lambda p: int(p * 0.6)), INK)
    else:
        disc(r, fill=(3, 8, 18, 255))
        m = Image.new('L', img.size, 0)
        md = ImageDraw.Draw(m)
        md.ellipse([(c - r) * k, (c - r) * k, (c + r) * k, (c + r) * k], outline=255, width=int(round(2.0 * s * k)))
        _lay(img, m.point(lambda p: int(p * 0.5)), CY)
        if inner_spent:
            ri = r * 0.66
            m2 = Image.new('L', img.size, 0)
            ImageDraw.Draw(m2).ellipse([(c - ri) * k, (c - ri) * k, (c + ri) * k, (c + ri) * k], outline=255, width=int(round(1.2 * s * k)))
            _lay(img, m2.point(lambda p: int(p * 0.22)), CY)
    if plus:
        a = r * 0.5
        w = 3.0 * s
        for p0, p1 in (((c, c - a), (c, c + a)), ((c - a, c), (c + a, c))):
            g.line([(p0[0] * k, p0[1] * k), (p1[0] * k, p1[1] * k)], fill=INK + (255,), width=int(round(w * k)))
    _CT[key] = (img, sz, k)
    return _CT[key]


def draw_coin(L, cx, cy, d=24, state='lit', plus=False):
    img, sz, k = coin_img(d, state, plus, v('ram_pips') == 'B')
    tile_paste(L, img, cx, cy, sz, sz, k)


_ST = {}
SQ = 22


def sq_img(state='lit'):
    """TRACE square: 22 px r3, violet + ink keyline.  A: inner hairline square at INK 60 percent (the coin's construction); B: top-light strip (R1).
    unlit: near-black socket, faint violet hairline (1.4 px solid: the 'gone' socket grammar)"""
    kind = v('trace_pips')
    key = (state, kind)
    if key in _ST:
        return _ST[key]
    k = 8
    sz = SQ + 8
    c = sz / 2
    img = Image.new('RGBA', (sz * k, sz * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    h = SQ / 2
    d.rounded_rectangle([(c - h - 1.8) * k, (c - h - 1.8) * k, (c + h + 1.8) * k, (c + h + 1.8) * k], radius=int(4.8 * k), fill=INK + (255,))
    if state == 'lit':
        d.rounded_rectangle([(c - h) * k, (c - h) * k, (c + h) * k, (c + h) * k], radius=int(3 * k), fill=VIO + (255,))
        if kind == 'A':
            m = Image.new('L', img.size, 0)
            ImageDraw.Draw(m).rounded_rectangle([(c - h + 4.4) * k, (c - h + 4.4) * k, (c + h - 4.4) * k, (c + h - 4.4) * k], radius=int(1.6 * k), outline=255, width=int(round(1.2 * k)))
            _lay(img, m.point(lambda p: int(p * 0.6)), INK)
        else:
            d.rounded_rectangle([(c - h + 2) * k, (c - h + 2) * k, (c + h - 2) * k, (c - h + 5.5) * k], radius=int(1.5 * k), fill=(196, 140, 255, 255))
    else:
        d.rounded_rectangle([(c - h) * k, (c - h) * k, (c + h) * k, (c + h) * k], radius=int(3 * k), fill=(10, 5, 20, 255))
        m = Image.new('L', img.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([(c - h) * k, (c - h) * k, (c + h) * k, (c + h) * k], radius=int(3 * k), outline=255, width=int(round(1.4 * k)))
        _lay(img, m.point(lambda p: int(p * 0.55)), VIO)
    _ST[key] = (img, sz, k)
    return _ST[key]


def draw_sq(L, cx, cy, state):
    img, sz, k = sq_img(state)
    tile_paste(L, img, cx, cy, sz, sz, k)


def el_cap(L, cx, cy, lit):
    """trace_cap_hatch A (the AD's B pick): white padlock + ink on the cap pip.  B: on the unlit pip the lock is violet-tinted and turns white when the cap is reached"""
    tint = v('trace_cap_hatch') == 'B' and not lit
    body = (176, 128, 236) if tint else THI

    def fn(d, T, k):
        bw, bh = 11.4, 8.6
        by = cy + 2.6
        sh = [(cx - 3.5, by - bh / 2 + 0.4), (cx - 3.5, by - bh / 2 - 3.0), (cx - 1.8, by - bh / 2 - 4.7), (cx + 1.8, by - bh / 2 - 4.7), (cx + 3.5, by - bh / 2 - 3.0), (cx + 3.5, by - bh / 2 + 0.4)]
        ln(d, T, k, sh, INK + (255,), 5.0)
        ln(d, T, k, sh, body + (255,), 2.2)
        a, b = T(cx - bw / 2 - 1.5, by - bh / 2 - 1.5), T(cx + bw / 2 + 1.5, by + bh / 2 + 1.5)
        d.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=int(3 * k), fill=INK + (255,))
        a, b = T(cx - bw / 2, by - bh / 2), T(cx + bw / 2, by + bh / 2)
        d.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=int(2 * k), fill=body + (255,))
        e0, e1 = T(cx - 1.5, by - 1.9), T(cx + 1.5, by + 1.1)
        d.ellipse([e0[0], e0[1], e1[0], e1[1]], fill=INK + (255,))
        a, b = T(cx - 0.7, by - 0.4), T(cx + 0.7, by + 2.6)
        d.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=int(0.4 * k), fill=INK + (255,))
    sprite(L, cx - SQ / 2, cy - SQ / 2, SQ, SQ, fn)


# ---- flame (Heat's alone) -----------------------------------------------------------------------------------------
def _cr(pts, n=10):
    """closed Catmull-Rom through pts"""
    out = []
    m = len(pts)
    for i in range(m):
        p0, p1, p2, p3 = pts[(i - 1) % m], pts[i], pts[(i + 1) % m], pts[(i + 2) % m]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[a]) + (-p0[a] + p2[a]) * t + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t2 + (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * t3) for a in (0, 1)))
    return out


FLA = [(0.16, -1.0), (0.46, -0.52), (0.84, -0.02), (0.88, 0.46), (0.52, 0.92), (0.0, 1.0), (-0.52, 0.92), (-0.88, 0.46), (-0.8, -0.06), (-0.52, -0.46), (-0.38, -0.1), (-0.2, -0.58)]
FLB = [(0.1, -1.0), (0.3, -0.55), (0.52, -0.2), (0.62, -0.5), (0.9, 0.0), (0.88, 0.5), (0.5, 0.92), (0.0, 1.0), (-0.5, 0.92), (-0.88, 0.5), (-0.84, -0.04), (-0.56, -0.5), (-0.4, -0.12), (-0.2, -0.6)]
_FT = {}


def flame_img(w=22, h=22, kind='A'):
    key = (w, h, kind)
    if key in _FT:
        return _FT[key]
    k = 8
    szw, szh = int(w + 8), int(h + 8)
    cx, cy = szw / 2, szh / 2
    P0 = _cr(FLA if kind == 'A' else FLB)
    img = Image.new('RGBA', (szw * k, szh * k), (0, 0, 0, 0))
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).polygon([((cx + px * w / 2) * k, (cy + py * h / 2) * k) for px, py in P0], fill=255)
    m = _rnd(m, 0.9 * k)
    _lay(img, _dil(m, 1.9 * k), INK)
    _lay(img, m, HEATC)
    core = Image.new('L', img.size, 0)
    ImageDraw.Draw(core).polygon([((cx + px * w / 2 * 0.46) * k, (cy + 0.36 * h / 2 + py * h / 2 * 0.5) * k) for px, py in P0], fill=255)
    core = _rnd(core, 0.7 * k)
    _lay(img, core, (255, 226, 140))
    _FT[key] = (img, szw, szh, k)
    return _FT[key]


def draw_flame(L, cx, cy):
    img, sw, sh, k = flame_img(20, 22, 'A' if v('ends_heat') == 'A' else 'B')
    tile_paste(L, img, cx, cy, sw, sh, k)


# ---- refund pop (inside the pip gap) -----------------------------------------------------------------------------
def pop_rays(L, cx, cy, d=24):
    """ram_refund_pop A: six cyan ray ticks (N, S and the four diagonals) kept inside the pip gap + plate margin, ink-edged, never reaching a neighbour; the plus is on the coin.
    B: fanned ticks above and below only (nothing sideways)"""
    r = d / 2 + 1.8
    if v('ram_refund_pop') == 'B':
        rays = [(-90, 5.2), (-90 - 30, 4.0), (-90 + 30, 4.0), (90, 5.2), (90 - 30, 4.0), (90 + 30, 4.0)]
    else:
        rays = [(-90, 5.4), (-45, 4.4), (-135, 4.4), (90, 5.4), (45, 4.4), (135, 4.4)]

    def fn(dd, T, k):
        for ang, ll in rays:
            a = math.radians(ang)
            r0 = r + 1.6 + (0.4 if abs(math.sin(a)) < 0.9 else 0)
            p0 = (cx + r0 * math.cos(a), cy + r0 * math.sin(a))
            p1 = (p0[0] + ll * math.cos(a), p0[1] + ll * math.sin(a))
            ln(dd, T, k, [p0, p1], INK + (255,), 4.8)
        for ang, ll in rays:
            a = math.radians(ang)
            r0 = r + 1.6 + (0.4 if abs(math.sin(a)) < 0.9 else 0)
            p0 = (cx + r0 * math.cos(a), cy + r0 * math.sin(a))
            p1 = (p0[0] + ll * math.cos(a), p0[1] + ll * math.sin(a))
            ln(dd, T, k, [p0, p1], (190, 242, 255, 255), 2.2)
    sprite(L, cx - 20, cy - 20, 40, 40, fn)


# ---- resources row ----------------------------------------------------------------------------------------------
def res_label_w(L, s):
    return ttw(L, s, LBL_PX, 'mono', TRK)


def el_res_label(L, x, cy, s, col=TMID):
    txt(L, x, cy, s, LBL_PX, col, track=TRK)


def el_res_frame(L, box, bays):
    """ram_trace_frame B (AD pick): kit plate + two hairline bay dividers (1.4 px at 30 percent).  C: the bays as three dark insets (the bill's inset language), no dividers"""
    kit_plate(L, box)
    x0, y0, x1, y1 = box
    if v('ram_trace_frame') == 'A':
        for dx in bays['div']:
            L.line([(dx, y0 + 9), (dx, y1 - 9)], CY + (77,), 1.4)
    else:
        for bx0, bx1 in bays['cells']:
            L.rect([bx0, y0 + 6, bx1, y1 - 6], fill=(0, 4, 12, 150), r=5)
            L.line([(bx0 + 5, y1 - 6), (bx1 - 5, y1 - 6)], CY + (46,), 1.4)


RAM_P, TR_P, HT_P = 32, 28, 28
GAP_L = 12


def resources_row(L, f, y):
    H = RES_H
    box = (PX0, y, PX1, y + H)
    cy = y + H / 2
    rn, tn = f['ram_max'], f['tcap']
    hn = f['pv']['trace_after']
    labs = ['RAM', 'TRACE', 'ENDS = HEAT']
    lw = [res_label_w(L, s) for s in labs]
    rws = (rn - 1) * RAM_P + 24 + 3.6
    tws = (tn - 1) * TR_P + SQ + 3.6
    hws = ((hn - 1) * HT_P + 22) if hn else 0
    zw = [lw[0] + GAP_L + rws, lw[1] + GAP_L + tws, lw[2] + ((GAP_L + hws) if hn else 0)]
    xa, xb = PX0 + 20, PX1 - 20
    g = (xb - xa - sum(zw)) / 2.0
    xs = [xa, xa + zw[0] + g, xa + zw[0] + zw[1] + 2 * g]
    bays = dict(div=[xs[1] - g / 2, xs[2] - g / 2], cells=[(xs[0] - 12, xs[0] + zw[0] + 12), (xs[1] - 12, xs[1] + zw[1] + 12), (xs[2] - 12, xs[2] + zw[2] + 12)])
    el_res_frame(L, box, bays)
    reg('res_plate', box)
    R['_bays'] = tuple(bays['div'])
    # RAM
    el_res_label(L, xs[0], cy, 'RAM')
    reg('ram_label', (xs[0], cy - 14, xs[0] + lw[0], cy + 14))
    px = xs[0] + lw[0] + GAP_L
    for i in range(rn):
        ccx = px + 13.8 + i * RAM_P
        lit = i < f['ram']
        refund = bool(f.get('refunds')) and i == f['ram'] - 1 and i >= 0
        if refund:
            pop_rays(L, ccx, cy)
        draw_coin(L, ccx, cy, 24, 'lit' if lit else 'spent', plus=refund)
        if refund:
            reg('ram_refund', (ccx - 24, cy - 24, ccx + 24, cy + 24))
    reg('ram_pips', (px - 4, cy - 18, px + rws + 4, cy + 18))
    # TRACE
    el_res_label(L, xs[1], cy, 'TRACE')
    reg('trace_label', (xs[1], cy - 14, xs[1] + lw[1], cy + 14))
    px = xs[1] + lw[1] + GAP_L
    for i in range(tn):
        ccx = px + 12.8 + i * TR_P
        lit = i < f['trace']
        draw_sq(L, ccx, cy, 'lit' if lit else 'unlit')
        if i == tn - 1:
            el_cap(L, ccx, cy, lit)
            reg('cap_pip', (ccx - 16, cy - 16, ccx + 16, cy + 16))
    reg('trace_pips', (px - 4, cy - 18, px + tws + 4, cy + 18))
    # ENDS = HEAT
    el_res_label(L, xs[2], cy, 'ENDS = HEAT', HEATC)
    reg('heat_label', (xs[2], cy - 14, xs[2] + lw[2], cy + 14))
    px = xs[2] + lw[2] + GAP_L
    for i in range(hn):
        draw_flame(L, px + 11 + i * HT_P, cy)
    reg('heat_pips', (px - 4, cy - 18, px + max(hws, 22) + 4, cy + 18))
    return y + H


# ------------------------------------------------------------------------------------------------------ plug into the top_hud R2 column
import hud2


def install():
    hud2.objectives_row = objectives_row
    hud2.ram_row = resources_row
    hud2.G['obj_h'] = OBJ_H
    hud2.G['ram_h'] = RES_H


install()
