"""top_hud design round 2: the right-column HUD of E10 as swappable element functions, AD picks applied.
V[element] = 'A' (the AD pick, refined; default) | 'B' (one variant where listed).  Every element has its own function (el_*) and registers its
screen box in R[...] for the sheet builder.  Render: hud2.render(beat, V, full, extra).  Never `python -`; run by path."""
import sys, os, math, random
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hud_base import *
import cv_chrome as CHR
import kglyph2  # asm: master library (asm_glyphs aliases KA_* to it)

V = {}
R = {}
GUIDES = {'on': False, 'focus': False}

# ---- tokens (BRIEF 3.3, R1 rulings) ----------------------------------------------------------------------------
TBG = (5, 13, 28)
THI = (242, 246, 255)
TMID = (175, 192, 214)
TLO = (122, 136, 156)
HARM = (255, 68, 51)
SOAK = __import__('asm_tokens').SOAK
SCHED = (255, 140, 26)
FOCUS = (212, 255, 0)
PLAN = (255, 226, 0)
GAINC = (123, 224, 123)
LAV = (190, 160, 255)
RAW62 = tuple(int(c * 0.62) for c in HARM)
LBL_PX, LBL_TRK = 18, 0.08                       # the one HUD label spec (rb_patch sets the rebuild's 23 / 0.04: cap 16.1)
SPLIT_LY, SPLIT_YY, SPLIT_GAP, SPLIT_OP = 133, 150, 28, 21    # split row: label y, tally y, gap after a route, operator offset
TW_XMIN_GAP, CHIP_BAR_DX = 40, 444                # WITHOUT TWIST: min gap after the NEXT tallies; option chip outcome bar x
SEGW, SEGH, SEGP, SEGG = 7, 15, 10, 16          # tally_segments A: 7x15 r3, group gap 16
GL = {'Twist': 'KA_twist', 'Trigger': 'KA_trigger', 'Brace': 'KA_brace', 'Hold': 'KA_hold', 'Shove': 'KA_shove', 'Spin2': 'KA_spin2',
      'Spin3': 'KA_spin3', 'Nudge': 'KA_nudge', 'Strike': 'KA_strike', 'Firewall': 'KA_firewall', 'Pull': 'KA_pull'}

# budget (X18): header 56, bill 194, objectives +10 (50), RAM 44, chips 38 / 6, chain rows 23
G = dict(px0=1072, px1=1896, ox=1076, sx0=1078, sx1=1890, gap=8, hdr_h=56, bill_h=194, obj_h=50, ram_h=44, chip_h=38, chip_gap=6, chain_h=23, chain_pad=8)


def v(k):
    return V.get(k, 'A')


def reg(name, box):
    R[name] = tuple(box)


# ------------------------------------------------------------------------------------------------------ text helpers
def ttw(L, s, px, kind='mono', track=0.0):
    return L.tw(s, px, kind) + track * px * max(0, len(s) - 1)


def txt(L, x, y, s, px, col, kind='mono', anchor='lm', track=0.0, alpha=255, stroke=0):
    """text with optional tracking (fraction of px).  anchor l/m/r on x only; vertical m.  returns width (also in nowords)."""
    w = ttw(L, s, px, kind, track)
    if not NOW['words']:
        return w
    col = tuple(col)[:3] + (alpha,)
    if not track:
        L.text((x, y), s, px, kind, fill=col, anchor=anchor, stroke=stroke)
        return w
    x0 = x if anchor[0] == 'l' else (x - w / 2 if anchor[0] == 'm' else x - w)
    for ch in s:
        L.text((x0, y), ch, px, kind, fill=col, anchor='lm')
        x0 += L.tw(ch, px, kind) + track * px
    return w


def tag(L, x, y, s, anchor='lm', alpha=255, col=TMID):
    """the one HUD label spec: mono 18, +8 percent, TEXT_MID (eq_labels / row_tags)."""
    return txt(L, x, y, s, LBL_PX, col, 'mono', anchor, LBL_TRK, alpha)


def rowtag(L, x, y, s, al=255, centre=None):
    """row_tags (SPLIT / NEXT / LANDS / THROUGH).  A: the eq_labels spec, left-set on the row baseline / on the digit edge.
    B: a 3 px cyan row marker leads the row tag; hero tags centre over their digit."""
    if v('row_tags') == 'B':
        if centre is not None:
            return tag(L, centre, y, s, 'mm', al)
        L.rect([x, y - 8, x + 3, y + 8], fill=CYAN + (al,), r=1)
        return 10 + tag(L, x + 10, y, s, 'lm', al)
    return tag(L, x, y, s, 'lm', al)


def digit(L, s, x, y, px, col, stroke, anchor='lm'):
    """Anton digit; in nowords it is hidden here (the proxies replace it) so no stray bar appears (header fix)."""
    if NOW['words']:
        L.text((x, y), s, px, 'anton', fill=col, anchor=anchor, stroke=stroke)
    return L.tw(s, px, 'anton')


# ------------------------------------------------------------------------------------------------------ terminal plate kit
def _scan(L, x0, y0, x1, y1, pitch=4, a=20, inset=6):
    for y in range(int(y0) + inset, int(y1) - inset + 1, pitch):
        L.line([(x0 + inset, y), (x1 - inset, y)], (0, 0, 0, a), 1)


def P(L, box, role='plate', sel=False, col=None, w=None, r=8):
    """terminal_plate_kit A: 93 percent fill, cyan 2 px, r8, 4 px scanlines alpha 20; hero (bill) and selected = 3 px; selected edge PENCIL_PLAN."""
    x0, y0, x1, y1 = box
    hero = role == 'bill'
    edge = col if col is not None else (PLAN if sel else CYAN)
    L.rect(box, fill=TBG + (237,), outline=tuple(edge)[:3] + (235,), w=w if w is not None else (3 if (hero or sel) else 2), r=r)
    _scan(L, x0, y0, x1, y1)


def inset(L, box):
    """flat inset row of the bill (bill_frame A): dark glass, one cyan hairline at the foot; no outline of its own."""
    x0, y0, x1, y1 = box
    L.rect(box, fill=(0, 4, 12, 150), r=5)
    L.line([(x0 + 5, y1), (x1 - 5, y1)], CYAN + (46,), 1.4)


# ------------------------------------------------------------------------------------------------------ segments (tally_segments, empty_socket, HP grammar)
def seg(L, x, y, kind, w=SEGW, h=SEGH, al=255):
    """one HP-grammar segment, r3, ink keyline.  kinds: hp lose gone through lands raw absorb cyan soak braced rider yel ptl slice gold viol"""
    box = [x, y - h / 2, x + w, y + h / 2]
    if kind == 'gone':    # dark socket + solid 1.4 px hairline
        L.rect(box, fill=(8, 14, 22, al), outline=TLO + (al,), w=1.4, r=3)
        return
    col = {'hp': GAINC, 'slice': GAINC, 'lose': HARM, 'through': HARM, 'lands': HARM, 'raw': RAW62, 'absorb': CYAN, 'cyan': CYAN, 'soak': SOAK,
           'braced': CYAN, 'rider': LAV, 'yel': PLAN, 'ptl': HARM, 'gold': GOLD, 'viol': (160, 60, 255)}[kind]
    L.rect(box, fill=col + (al,), outline=INK + (al,), w=1.2 if w < 9 else 1.6, r=3)
    cx = x + w / 2
    if kind == 'lose':    # lost now: HARM + white 2 px slash + ink
        L.line([(x + 0.5, y + h / 2 - 1), (x + w - 0.5, y - h / 2 + 1)], INK + (al,), 4.2)
        L.line([(x + 0.5, y + h / 2 - 1), (x + w - 0.5, y - h / 2 + 1)], (255, 255, 255, al), 2)
    elif kind == 'soak':  # lost to soak: SOAK + ink chevron notch
        pts = [(cx - w * 0.3, y - h * 0.14), (cx, y + h * 0.1), (cx + w * 0.3, y - h * 0.14)]
        L.line(pts, INK + (al,), 1.8)
    elif kind == 'braced':   # brace tally: cyan with the clamp bar
        L.line([(x + 1.2, y), (x + w - 1.2, y)], INK + (al,), 1.8)
    elif kind == 'ptl':   # trigger pierce that reaches the tower: HARM + white tick
        L.line([(x + 1.2, y + h * 0.18), (x + w - 1.2, y - h * 0.18)], (255, 255, 255, al), 1.7)


def tpos(n, w=SEGW, pitch=SEGP, gap=SEGG):
    out = []
    for i in range(n):
        out.append(i * pitch + (i // 5) * (gap - (pitch - w)))
    return out


def twidth(n, w=SEGW, pitch=SEGP, gap=SEGG):
    if n == 0:
        return w
    return tpos(n, w, pitch, gap)[-1] + w


def tally(L, x, y, kind, n, w=SEGW, h=SEGH, al=255, pitch=SEGP, gap=SEGG):
    """n segments in groups of 5 (0 -> one gone pip); returns end x"""
    if n == 0:
        seg(L, x, y, 'gone', w, h, al)
        return x + w
    for i, o in enumerate(tpos(n, w, pitch, gap)):
        seg(L, x + o, y, kind, w, h, al)
    return x + twidth(n, w, pitch, gap)


def opdraw(L, x, y, s, al=255):
    """operators A: vector bars + ink on the tally centreline"""
    t, s_ = 4.0, 8

    def bar(a, b, c, d):
        L.line([(x + a, y + b), (x + c, y + d)], INK + (al,), t + 3.4)
        L.line([(x + a, y + b), (x + c, y + d)], THI + (al,), t)
    if s == '-':
        bar(-s_, 0, s_, 0)
    elif s == '+':
        bar(-s_, 0, s_, 0)
        bar(0, -s_, 0, s_)
    else:
        bar(-s_, -4.4, s_, -4.4)
        bar(-s_, 4.4, s_, 4.4)


def arrow(L, x, y, col, w=26, h=7, al=255):
    L.poly([(x, y - 3.4), (x + w - 10, y - 3.4), (x + w - 10, y - h), (x + w, y), (x + w - 10, y + h), (x + w - 10, y + 3.4), (x, y + 3.4)], fill=col + (al,), outline=INK + (al,), w=1.6)


def wax(L, pts, col, w=7, seed=3, ink=True, wob=0.9):
    """grease-pencil stroke: ink edge, 3 offset passes, grain specks"""
    rnd = random.Random(seed)
    (xa, ya), (xb, yb) = pts[0], pts[-1]
    n = max(2, int(math.hypot(xb - xa, yb - ya) / 5))
    ph = rnd.uniform(0, 6)
    base = []
    for i in range(n + 1):
        t = i / n
        base.append((xa + (xb - xa) * t, ya + (yb - ya) * t + math.sin(t * 9 + ph) * wob + rnd.uniform(-.35, .35)))
    if ink:
        L.line(base, INK + (255,), w + 4.5)
    for dy, al, ww in ((0, 255, w), (-1.4, 150, w * 0.5), (1.5, 110, w * 0.45)):
        L.line([(x, y + dy) for x, y in base], col + (al,), ww)
    for i in range(int(n * 0.5)):
        t = rnd.random()
        x = xa + (xb - xa) * t
        y = ya + (yb - ya) * t + rnd.uniform(-w / 2.3, w / 2.3)
        L.ellipse([x - .8, y - .8, x + .8, y + .8], fill=INK + (60,))


# ------------------------------------------------------------------------------------------------------ destinations (route_arrows)
def dest_hub(L, x, y):
    """hub ring, cyan: the board hub drawn small (ring + core)"""
    L.ellipse([x - 11, y - 11, x + 11, y + 11], fill=(6, 14, 26, 255), outline=INK, w=4.6)
    L.ellipse([x - 9, y - 9, x + 9, y + 9], outline=CYAN, w=2.4)
    L.ellipse([x - 3.5, y - 3.5, x + 3.5, y + 3.5], fill=CYAN, outline=INK, w=1.2)
    return x + 12


def dest_funnel(L, x, y, pip=True):
    """slice destination: funnel outlined in SOAK with its notch, the slice HP pip (GAIN) under"""
    pts = [(x - 13, y - 9), (x + 13, y - 9), (x + 6.5, y + 3), (x - 6.5, y + 3)]
    L.poly(pts, fill=(8, 10, 40, 255), outline=INK, w=5)
    L.poly(pts, fill=(8, 10, 40, 255), outline=SOAK, w=2.2)
    L.line([(x - 4, y - 5), (x, y - 1), (x + 4, y - 5)], SOAK, 1.8)
    if pip:
        L.rect([x - 7, y + 6, x + 7, y + 11], fill=GAINC, outline=INK, w=1.2, r=2)
    return x + 14


def dest_hp(L, x, y):
    """fix 5: HP destination = ONE GAIN segment (10 x 11, not the 7 px tally width) inside a 1.4 px white socket bracket (the you_hp_tally socket construction).
    It is not a tally segment, so it cannot read as a count of 2.  Same x extent and gap as the hub / funnel icons (returns x + 12)."""
    for lw, col in ((4.2, INK), (1.4, (255, 255, 255))):
        L.line([(x - 5.5, y - 9.5), (x - 9, y - 9.5), (x - 9, y + 9.5), (x - 5.5, y + 9.5)], col, lw)
        L.line([(x + 5.5, y - 9.5), (x + 9, y - 9.5), (x + 9, y + 9.5), (x + 5.5, y + 9.5)], col, lw)
    seg(L, x - 5, y, 'hp', 10, 11)
    return x + 12


DEST = {'hub': dest_hub, 'funnel': dest_funnel, 'hp': dest_hp}


# ------------------------------------------------------------------------------------------------------ focus brackets (actions owns the drawing; this mirrors bible 2.10)
def focus_brackets(L, box, off=7, n=10):
    import a2_kit      # ASSEMBLY (Y5): a2_kit.focus_brackets (A) is the only focus drawing
    a2_kit.focus_brackets(L, 'rect', dict(box=tuple(box)), 'A', grow=off)


# ------------------------------------------------------------------------------------------------------ small drawn marks
def qmark(L, cx, cy, s, col, w=2.8, inkw=0):
    """a drawn '?' (survives nowords): hook + stem + dot"""
    r = s * 0.28
    arc = [(cx + r * math.cos(math.radians(a)), cy - s * 0.18 - r * math.sin(math.radians(a))) for a in range(200, -50, -14)]
    stem = [arc[-1], (cx + 0.02 * s, cy + s * 0.08), (cx, cy + s * 0.14)]
    dot = [cx - w * 0.9, cy + s * 0.3 - w * 0.9, cx + w * 0.9, cy + s * 0.3 + w * 0.9]
    if inkw:
        L.line(arc + stem[1:], INK, w + inkw)
        L.ellipse([dot[0] - inkw / 2, dot[1] - inkw / 2, dot[2] + inkw / 2, dot[3] + inkw / 2], fill=INK)
    L.line(arc + stem[1:], col, w)
    L.ellipse(dot, fill=col)


def coin(L, cx, cy, d=22, plus=True):
    import obj2      # ASSEMBLY (Y4)
    obj2.draw_coin(L, cx, cy, d, 'lit', plus=plus)


# ------------------------------------------------------------------------------------------------------ HEADER
def el_header_plate(L, f):
    box = (G['px0'], 12, G['px1'], 12 + G['hdr_h'])
    P(L, box, 'header')
    reg('header_plate', box)
    return box


def el_header_title(L, f, box):
    """small TURN + keylined Anton 44 digit + cyan hairline divider + mode Anton 26.  nowords: the digit is hidden (E10 did)."""
    k = v('header_title')
    cy = (box[1] + box[3]) / 2
    x = box[0] + 20
    turn = f['turn']
    w1 = txt(L, x, cy + 3, 'TURN', 22, TMID, 'anton', 'lm')
    xd = x + w1 + 8
    if k == 'A':
        wd = digit(L, str(turn), xd, cy + 1, 44, WHITE, 2.4)
        xd += wd + 16
        if NOW['words']:
            L.line([(xd, cy - 15), (xd, cy + 15)], CYAN + (210,), 2)
    else:     # B: the digit sits in a keyed cell wedge (the schedule-cell shape), no divider line
        wd = L.tw(str(turn), 44, 'anton')
        if NOW['words']:
            pts = [(xd - 4, cy + 20), (xd + 2, cy - 20), (xd + wd + 8, cy - 20), (xd + wd + 14, cy + 20)]
            L.poly(pts, fill=CYAN + (40,), outline=CYAN + (230,), w=2)
        digit(L, str(turn), xd + 5, cy + 1, 44, WHITE, 2.4)
        xd += wd + 24
    txt(L, xd + (14 if k == 'A' else 0), cy + 3, 'SHIFTING WAVES', 26, WHITE, 'anton', 'lm', stroke=1.6)
    e = xd + 14 + L.tw('SHIFTING WAVES', 26, 'anton')
    reg('header_title', (x - 6, box[1], e + 6, box[3]))
    return e


def el_help(L, box):
    """help button A: 30 px kit chip, cyan hairline, drawn white ?; B: ?-only ring; focus state = lime brackets"""
    k = v('help_button')
    cy = (box[1] + box[3]) / 2
    cx = box[2] - 20 - 15
    if k == 'A':
        L.rect([cx - 15, cy - 15, cx + 15, cy + 15], fill=(4, 10, 20, 235), outline=CYAN + (150,), w=1.8, r=6)
        qmark(L, cx, cy, 24, THI, 2.8)
    else:     # B: a cyan-edged ring chip with an ink-keyed ?
        L.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(4, 10, 20, 240), outline=CYAN + (230,), w=2)
        qmark(L, cx, cy, 24, THI, 2.8, inkw=2.2)
    if GUIDES.get('focus'):
        focus_brackets(L, (cx - 15, cy - 15, cx + 15, cy + 15))
    reg('help_button', (cx - 26, cy - 26, cx + 26, cy + 26))
    return cx - 22


def wedge(L, x, cy, w, h, col, lit, sk=3):
    pts = [(x + sk, cy - h / 2), (x + w, cy - h / 2), (x + w - sk, cy + h / 2), (x, cy + h / 2)]
    if lit:
        L.poly(pts, fill=col, outline=INK, w=1.8)
    else:
        L.poly(pts, fill=(18, 18, 28), outline=col, w=1.8)


def el_waves_left(L, f, box, xr):
    """waves_left: A = label in an orange-edged chip + wedge pips (bezel-cell shape), climax pip HARM; B = chip fused around the pips"""
    k = v('waves_left')
    cy = (box[1] + box[3]) / 2
    n = f['waves_left']
    s = 'WAVES %d LEFT' % n
    pw, pp = 16, 19
    xs = xr - 6 * pp + (pp - pw)
    lw = L.tw(s, 20, 'anton')
    if k == 'A':
        for i in range(6):
            wedge(L, xs + i * pp, cy, pw, 20, HARM if i == 5 else SCHED, i >= 6 - n)
        wc = lw + 22
        xc = xs - 16 - wc
        if NOW['words']:
            L.rect([xc, cy - 15, xc + wc, cy + 15], fill=(26, 14, 4, 235), outline=SCHED, w=2, r=6)
            L.text((xc + wc / 2, cy + 1.5), s, 20, 'anton', fill=SCHED, anchor='mm')
        reg('waves_left', (xc - 6, box[1], xr + 6, box[3]))
    else:
        xe = xr + 10
        xc = xs - 16 - lw - 14 - 8
        if NOW['words']:
            L.rect([xc, cy - 17, xe, cy + 17], fill=(26, 14, 4, 235), outline=SCHED, w=2, r=7)
            L.text((xc + 14, cy + 1.5), s, 20, 'anton', fill=SCHED, anchor='lm')
            L.line([(xs - 10, cy - 11), (xs - 10, cy + 11)], SCHED + (120,), 1.4)
        for i in range(6):
            wedge(L, xs + i * pp, cy, pw, 20, HARM if i == 5 else SCHED, i >= 6 - n)
        reg('waves_left', (xc - 6, box[1], xe + 6, box[3]))


def header(L, f):
    box = el_header_plate(L, f)
    el_header_title(L, f, box)
    xh = el_help(L, box)
    el_waves_left(L, f, box, xh - 16)
    reg('header', box)
    return box[3]


# ------------------------------------------------------------------------------------------------------ BILL
def el_bill_frame(L, y):
    box = (G['px0'], y, G['px1'], y + G['bill_h'])
    P(L, box, 'bill')
    reg('bill_frame', box)
    return box


def hp_tally(L, f, x, y):
    """you_hp_tally A: HP grammar (kept GAIN, lost now HARM + slash, gone = socket), YOU inline.  returns end x"""
    hp, mx, after = f['hp'], f['maxhp'], f['pv']['hp_after']
    w_, h_, p_, gg = 12, 20, 16, 14
    txt(L, G['ox'] + 8, y, 'YOU', LBL_PX, THI, 'mono', 'lm', LBL_TRK)
    pos = tpos(mx, w_, p_, gg)
    for i in range(mx):
        xi = x + pos[i]
        k_ = 'gone' if i >= hp else ('hp' if i < after else 'lose')
        seg(L, xi, y, k_, w_, h_)
    e = x + pos[-1] + w_
    R['_hp_pos'] = (x + pos[0], x + pos[max(0, min(hp, mx) - 1)] + w_, y + h_ / 2)
    reg('you_hp_tally', (G['ox'] + 2, y - 18, e + 6, y + 18))
    return e


def hero_pair(L, x, y, lands, through):
    """hero_pair A: Anton 58, 4 px keyline, row tags on the digit's left edge, neutral TEXT_HI arrow"""
    if not NOW['words']:
        return hero_nw(L, x, y, lands, through)
    tcol = HARM if through else GAINC
    wl = L.tw(str(lands), 58, 'anton')
    rowtag(L, x, y - 40, 'LANDS', centre=x + wl / 2)
    L.text((x, y), str(lands), 58, 'anton', fill=WHITE, anchor='lm', stroke=4)
    ax = x + wl + 14
    arrow(L, ax, y, THI, 40, 14)
    xt = ax + 40 + 14
    rowtag(L, xt, y - 40, 'THROUGH', centre=xt + L.tw(str(through), 58, 'anton') / 2)
    L.text((xt, y), str(through), 58, 'anton', fill=tcol, anchor='lm', stroke=4)
    reg('hero_pair', (x - 6, y - 52, xt + L.tw(str(through), 58, 'anton') + 8, y + 38))
    reg('row_tags_hero', R['hero_pair'])


def hero_nw(L, x, y, lands, through):
    """hero_nowords_proxy A: hero-size grouped segments on one baseline, neutral arrow, HARM through"""
    sw, sh, sp = 13, 30, 17
    tcol = 'through' if through else 'hp'
    e1 = x
    for i in range(lands):
        xi = x + i * sp + (i // 5) * 12
        L.rect([xi, y - sh / 2, xi + sw, y + sh / 2], fill=WHITE + (255,), outline=INK, w=2, r=3)
        e1 = xi + sw
    ax = e1 + 14
    arrow(L, ax, y, THI, 38, 14)
    xt = ax + 52
    e2 = xt
    for i in range(through):
        xi = xt + i * sp + (i // 5) * 12
        L.rect([xi, y - sh / 2, xi + sw, y + sh / 2], fill=HARM + (255,), outline=INK, w=2, r=3)
        e2 = xi + sw
    reg('hero_nowords_proxy', (x - 6, y - 24, e2 + 6, y + 24))


# ---- equation row -----------------------------------------------------------------------------------------------
def trig_form(L, x, y, n, al=255):
    """trig_groups A: PENCIL_PLAN segments at the secondary size 7x12 (the plan removed them)"""
    for o in tpos(n):
        seg(L, x + o, y, 'yel', 7, 12, al)
    return x + twidth(n)


def trig_lands_form(L, x, y, n):
    """trig_lands_group (LATENT): A = HARM segments with a white pierce tick; B = hollow HARM cells led by the hit chevron"""
    if v('trig_lands_group') == 'A':
        for o in tpos(n):
            seg(L, x + o, y, 'ptl')
        return x + twidth(n)
    L.line([(x, y - 7), (x + 6, y), (x, y + 7)], INK, 7.5)
    L.line([(x, y - 7), (x + 6, y), (x, y + 7)], HARM, 3.4)
    x0 = x + 12
    for o in tpos(n):
        L.rect([x0 + o, y - SEGH / 2, x0 + o + SEGW, y + SEGH / 2], fill=(40, 6, 10), outline=HARM, w=2, r=3)
    return x0 + twidth(n)


def group_w(name, kind, n):
    return twidth(n)


def draw_group(L, x, y, name, kind, n, al=255):
    if name == 'TRIG':
        return trig_form(L, x, y, n, al)
    if name == 'TRIG LANDS':
        return trig_lands_form(L, x, y, n)
    return tally(L, x, y, kind, n, al=al)


def el_eq_row(L, f, y, eq):
    """RAW - TRIG - SHOT - BRACE - RIDER = LANDS: equal subtraction columns, RAW / LANDS at their own width, operators centred in equal gutters,
    labels centred over their tally, tallies centred in their column"""
    sx0, sx1 = G['sx0'], G['sx1']
    inset(L, (sx0, y + 72, sx1, y + 116))
    items = [('RAW', 'raw', eq['raw0'], None)]
    if eq['triggered']:
        items.append(('TRIG', 'yel', eq['triggered'], '-'))
    if eq['tower_from_trigger']:
        items.append(('TRIG LANDS', 'ptl', eq['tower_from_trigger'], '+'))
    items += [('SHOT', 'cyan', eq['shot_down'], '-'), ('BRACE', 'braced', eq['braced'], '-'), ('RIDER', 'rider', eq['rider'], '-'), ('LANDS', 'lands', eq['lands'], '=')]
    ly, yy = y + 84, y + 103
    avail = sx1 - sx0 - 32
    own = ('RAW', 'LANDS')
    for sub, gut in ((96, 40), (90, 34), (84, 28), (78, 22), (72, 18)):
        cws = [max(twidth(n), 24) if name in own else max(sub, twidth(n) + 4) for name, kind, n, o in items]
        if name_w(L, items) and sum(cws) + gut * (len(items) - 1) <= avail:
            break
    x = sx0 + 16
    bx = {}
    for (name, kind, n, o), cw in zip(items, cws):
        if o:
            opdraw(L, x - gut / 2, yy, o)
        tw_ = twidth(n)
        tag(L, x + cw / 2, ly, name, 'mm')
        draw_group(L, x + (cw - tw_) / 2, yy, name, kind, n)
        bx[name] = (x, cw, tw_)
        x += cw + gut
    reg('eq_row', (sx0, y + 72, sx1, y + 116))
    reg('eq_labels', (sx0, y + 72, sx1, y + 116))
    reg('operators', (sx0, y + 72, sx1, y + 116))
    reg('tally_segments', (sx0, y + 72, sx1, y + 116))
    if 'BRACE' in bx and 'RIDER' in bx:
        reg('empty_socket', (bx['BRACE'][0] - 4, y + 74, bx['RIDER'][0] + bx['RIDER'][1] + 4, y + 114))
    if 'TRIG' in bx:
        reg('trig_groups', (bx['TRIG'][0] - 14, y + 74, bx['TRIG'][0] + bx['TRIG'][1] + 14, y + 114))
    if 'TRIG LANDS' in bx:
        reg('trig_lands_group', (bx['TRIG LANDS'][0] - 14, y + 74, bx['TRIG LANDS'][0] + bx['TRIG LANDS'][1] + 14, y + 114))


def name_w(L, items):
    return True


# ---- split row ----------------------------------------------------------------------------------------------------
def route(L, x, y, col, dest):
    """route_arrows A: bold arrow in the route colour + the destination as drawn on the board; returns end x"""
    arrow(L, x, y, col, 26, 7)
    return DEST[dest](L, x + 26 + 14, y) + 4


def el_split_row(L, f, y, eq):
    """split_row A: one baseline per row, label above a centred tally, then arrow + destination on the SAME baseline; SOAK label TEXT_MID"""
    sx0, sx1 = G['sx0'], G['sx1']
    inset(L, (sx0, y + 120, sx1, y + 164))
    ly, yy = y + SPLIT_LY, y + SPLIT_YY
    x = sx0 + 16
    tg = rowtag(L, x, yy, 'SPLIT')
    x += tg + 26
    cols = {}
    groups = [('ABSORBED', 'absorb', eq['absorbed'], CYAN, 'hub'), ('SOAK', 'soak', eq['soaked'], SOAK, 'funnel'), ('YOU', 'through', eq['through'], HARM, 'hp')]
    r0 = x
    for gi, (name, kind, n, rc, dest) in enumerate(groups):
        if gi:
            opdraw(L, x - SPLIT_OP, yy, '+')
        lw = ttw(L, name, LBL_PX, 'mono', LBL_TRK)
        bw = max(lw, twidth(n))
        tag(L, x + bw / 2, ly, name, 'mm')
        tally(L, x + (bw - twidth(n)) / 2, yy, kind, n)
        cols[name] = x
        xe = x + bw + 12
        xe = route(L, xe, yy, rc, dest)
        x = xe + SPLIT_GAP
    R['_split_cols'] = cols
    reg('split_row', (sx0, y + 120, sx1, y + 164))
    reg('route_arrows', (r0, y + 124, x - 20, y + 164))


def el_next_row(L, f, y, tw_pay=None):
    """next_row A: icon-led groups, aligned to the split row's group columns, ghost at 60 percent.  B: ghost = dashed (later) outlines."""
    k = v('next_row')
    nx = f['next']
    yg = y + 179
    inset(L, (G['sx0'], y + 168, G['sx1'], y + 189))
    rowtag(L, G['sx0'] + 16, yg, 'NEXT', 153)
    cols = R.get('_split_cols', {'ABSORBED': G['sx0'] + 110, 'SOAK': G['sx0'] + 350, 'YOU': G['sx0'] + 520})
    e_all = G['sx0'] + 100
    for name, kind, n, dest in (('ABSORBED', 'absorb', nx['absorbed'], 'hub'), ('SOAK', 'soak', nx['slost'], 'funnel'), ('YOU', 'through', nx['taken'], 'hp')):
        x = cols[name]
        DEST[dest](L, x + 12, yg - (2 if dest == 'funnel' else 0))
        xt = x + 34
        if k == 'A':
            e = tally(L, xt, yg, 'lose' if kind == 'soak' else kind, n, al=153, h=13) if n else xt
        else:
            e = xt
            col = {'absorb': CYAN, 'soak': SOAK, 'through': HARM}[kind]
            for o in tpos(n):
                L.rect([xt + o, yg - 6.5, xt + o + SEGW, yg + 6.5], fill=col + (60,), r=3)
                L.line([(xt + o, yg - 6.5), (xt + o + SEGW, yg - 6.5), (xt + o + SEGW, yg + 6.5), (xt + o, yg + 6.5), (xt + o, yg - 6.5)], col + (255,), 1.6)
            e = xt + twidth(n) if n else xt
        e_all = max(e_all, e)
    reg('next_row', (G['sx0'], y + 168, G['sx1'], y + 189))
    if tw_pay:
        without_twist(L, f, yg, tw_pay, nx, e_all + TW_XMIN_GAP)


def without_twist(L, f, yg, tp, nx, xmin):
    """without_twist_row A: twist disc + label, hollow bad case, PENCIL_PLAN arrow, solid result.  B: bad case struck by a wax line"""
    k = v('without_twist_row')
    wo = tp['without']['taken']
    lab_w = ttw(L, 'WITHOUT TWIST', LBL_PX, 'mono', LBL_TRK)
    need = 24 + 8 + lab_w + 14 + wo * SEGP + 10 + 26 + 10 + nx['taken'] * SEGP
    xt = max(xmin, G['sx1'] - 16 - need)
    L.ellipse([xt, yg - 12, xt + 24, yg + 12], fill=(30, 26, 6), outline=PLAN, w=2.2)
    L.glyph(GL['Twist'], 17, (xt + 12, yg), PLAN)
    x = xt + 32 + txt(L, xt + 32, yg, 'WITHOUT TWIST', LBL_PX, PLAN, 'mono', 'lm', LBL_TRK) + 14
    xs0 = x
    for i in range(wo):
        L.rect([x + i * SEGP, yg - SEGH / 2, x + i * SEGP + SEGW, yg + SEGH / 2], fill=(30, 8, 8), outline=HARM, w=1.8, r=3)
    x += wo * SEGP + 10
    if k == 'A':
        arrow(L, x, yg, PLAN, 26, 7)
        x += 36
    else:
        wax(L, [(xs0 - 3, yg + 1), (xs0 + wo * SEGP - 1, yg - 1)], PLAN, 3.4, seed=4)
        x += 12
    for i in range(nx['taken']):
        seg(L, x + i * SEGP, yg, 'through')
    e = x + nx['taken'] * SEGP
    reg('without_twist_row', (xt - 8, yg - 16, e + 10, yg + 16))


# ---- plan marks -----------------------------------------------------------------------------------------------------
def el_plan_underline(L, f, y):
    """plan_pencil_underline A: wax 7 px + ink exactly under the HP width.  B: ruled tick at the end"""
    k = v('plan_pencil_underline')
    a, b, yb = R['_hp_pos']
    yu = yb + 8
    wax(L, [(a, yu), (b, yu + 1)], PLAN, 7, seed=5)
    if k == 'B':
        L.line([(b, yu - 8), (b, yu + 7)], INK, 7.5)
        L.line([(b, yu - 7), (b, yu + 6)], PLAN, 4)
    reg('plan_pencil_underline', (G['ox'], yb - 26, b + 14, yu + 14))


def el_best_tag(L, y, txtm='BEST LINE'):
    """best_line_tag A: dark chip + plan-yellow hairline, right aligned in the bill header line.  B: tab hung on the top edge"""
    k = v('best_line_tag')
    xr = G['px1'] - 20
    w = ttw(L, txtm, LBL_PX, 'mono', LBL_TRK)
    if k == 'A':
        L.rect([xr - w - 20, y + 6, xr, y + 30], fill=(26, 22, 4, 245), outline=PLAN, w=1.8, r=6)
        txt(L, xr - 10 - w, y + 18, txtm, LBL_PX, PLAN, 'mono', 'lm', LBL_TRK)
        reg('best_line_tag', (xr - w - 28, y, xr + 8, y + 38))
    else:
        x0, x1 = xr - w - 24, xr
        L.rect([x0 - 2, y - 15, x1 + 2, y + 6], fill=INK, r=6)
        L.rect([x0, y - 13, x1, y + 6], fill=(26, 22, 4, 255), outline=PLAN, w=1.8, r=6)
        L.rect([x0 + 2, y - 11, x1 - 2, y + 6], fill=(26, 22, 4, 255))
        txt(L, x0 + 12, y - 3, txtm, LBL_PX, PLAN, 'mono', 'lm', LBL_TRK)
        reg('best_line_tag', (x0 - 8, y - 22, x1 + 8, y + 14))


def bill_box(L, f, y, pencil=False, plan_tag=None, twist_pay=None, extra=None):
    eq = f['pv']['eq']
    el_bill_frame(L, y)
    x = G['ox'] + 56
    e = hp_tally(L, f, x, y + 46)
    if pencil:
        el_plan_underline(L, f, y)
    hero_pair(L, e + 34, y + 54, eq['lands'], eq['through'])
    if plan_tag:
        el_best_tag(L, y, plan_tag)
    el_eq_row(L, f, y, eq)
    el_split_row(L, f, y, eq)
    el_next_row(L, f, y, twist_pay)
    return y + G['bill_h']


# ------------------------------------------------------------------------------------------------------ OPTIONS (p2)
def chip_glyphs(L, x, cy, plan, soak, refund):
    """option_plan_glyphs A: 24 px library glyphs, white silhouettes, Brace = cyan clamp, soak = SOAK token with notch, refund = coin + plus"""
    items = [c[0] for c in plan if c[0] in GL]
    for i, nm in enumerate(items):
        L.glyph(GL[nm], 24, (x + 12, cy), CYAN if nm == 'Brace' else THI)
        x += 28
        if i < len(items) - 1:
            L.ellipse([x, cy - 1.6, x + 3, cy + 1.4], fill=TLO)
            x += 5
    if soak:
        x += 6
        dest_funnel(L, x + 14, cy + 3, pip=False)
        x += 32
    if refund:
        x += 6
        coin(L, x + 11, cy, 22, True)
        x += 26
    return x


def chip_name(L, x, cy, name):
    """option_name_label A: mono 18 TEXT_MID, BEST in plan yellow"""
    if name.startswith('BEST: '):
        w = txt(L, x, cy, 'BEST: ', LBL_PX, PLAN, 'mono', 'lm', LBL_TRK)
        txt(L, x + w + 1, cy, name[6:], LBL_PX, THI, 'mono', 'lm', LBL_TRK)
    else:
        txt(L, x, cy, name, LBL_PX, TMID, 'mono', 'lm', LBL_TRK)


def chip_bar(L, x, cy, eq):
    """option_outcome_bar A: the split row's fixed order, group gaps, empty slots as gone pips"""
    for kind, n in (('absorb', eq['absorbed']), ('soak', eq['soaked']), ('through', eq['through'])):
        w = twidth(n if n else 1)
        e = tally(L, x, cy, kind, n)
        x = max(e, x + 14) + 16
    return x


def chip_pair(L, cy, eq):
    """option_pair A: the hero grammar small: keylined digits, neutral arrow"""
    xr = G['px1'] - 20
    ln, th = eq['lands'], eq['through']
    tcol = HARM if th else GAINC
    if not NOW['words']:
        return
    wt = L.tw(str(th), 26, 'anton')
    L.text((xr, cy + 1), str(th), 26, 'anton', fill=tcol, anchor='rm', stroke=3)
    arrow(L, xr - wt - 36, cy, THI, 26, 8)
    L.text((xr - wt - 44, cy + 1), str(ln), 26, 'anton', fill=WHITE, anchor='rm', stroke=3)


def option_chip(L, y, name, plan, soak, eq, sel=False, refund=False):
    h = G['chip_h']
    P(L, (G['px0'], y, G['px1'], y + h), 'chip', sel)
    cy = y + h / 2
    ox = G['ox']
    chip_glyphs(L, ox + 12, cy, plan, soak, refund)
    chip_name(L, ox + 196, cy, name)
    chip_bar(L, ox + CHIP_BAR_DX, cy, eq)
    chip_pair(L, cy, eq)
    return y + h + G['chip_gap']


# ------------------------------------------------------------------------------------------------------ CHAIN (p3)
def chain_glyph(L, st, x, cy):
    """chain_step_glyphs A: white library silhouettes; LANDS = the HARM chevron glyph (not the boss skull), B tints only that glyph HARM"""
    nm = st['name']
    col = THI
    if nm in ('TWIST', 'TRIGGER', 'BRACE'):
        L.glyph(GL[nm.title()], 22, (x, cy), CYAN if (nm == 'BRACE' and False) else col)
    elif nm == 'GUNS':       # tracer mark: dashed line ending in a bead
        L.line([(x - 10, cy), (x + 2, cy)], INK, 6)
        L.line([(x - 10, cy), (x + 2, cy)], col, 3)                  # R51: no dashed line on the combat screen: the tracer mark is one solid stroke ending in a bead
        L.ellipse([x + 0.5, cy - 5, x + 11, cy + 5], fill=col, outline=INK, w=1.6)
    elif nm == 'LANDS':      # the landing (hit) chevron pair
        cc = HARM if v('chain_step_glyphs') == 'B' else col
        for q in (0, 1):
            pts = [(x - 9, cy - 9 + q * 7), (x, cy - 2 + q * 7), (x + 9, cy - 9 + q * 7)]
            L.line(pts, INK, 7.5)
            L.line(pts, cc, 4)
    else:                    # RINGS STEP: schedule cell wedge with the step chevron
        L.poly([(x - 12, cy + 7), (x - 10, cy - 7), (x - 1, cy - 7), (x - 3, cy + 7)], fill=col, outline=INK, w=1.8)
        L.poly([(x + 3, cy + 7), (x + 1, cy - 7), (x + 10, cy - 7), (x + 12, cy + 7)], fill=(8, 14, 26), outline=col, w=2)


def chain_strip(L, f, y):
    """chain_strip A: kit table, hairline dividers, trimmed padding; discs = mono numerals; names mono 18 TEXT_MID; fixed tally column, prose column"""
    steps = f['chain']
    h = G['chain_h']
    x0, x1, ox = G['px0'], G['px1'], G['ox']
    ph = G['chain_pad'] + len(steps) * h
    P(L, (x0, y, x1, y + ph), 'chain')
    yy = y + G['chain_pad'] / 2
    xt0, xp0 = ox + 236, ox + 236 + 134
    for i, st in enumerate(steps):
        cy = yy + h / 2
        if i:
            L.line([(x0 + 10, yy), (x1 - 10, yy)], CYAN + (46,), 1.2)
        if NOW['words']:
            L.text((ox + 14, cy + 1), str(i + 1), LBL_PX, 'mono', fill=TMID + (255,), anchor='mm')
        chain_glyph(L, st, ox + 50, cy)
        txt(L, ox + 76, cy, st['name'], LBL_PX, TMID, 'mono', 'lm', LBL_TRK)
        xt = xt0
        kinds = {'raw': 'lands'}
        for k_, n in st['pips']:
            if k_ in ('txt', 'refund') or not n:
                continue
            xt = tally(L, xt, cy, kinds.get(k_, k_), n) + 16
        for k_, n in st['pips']:
            if k_ == 'refund':
                coin(L, xt + 9, cy, 20, True)
                xt += 28
        for k_, n in st['pips']:
            if k_ == 'txt':
                txt(L, xp0, cy, n, LBL_PX, TMID, 'mono', 'lm', 0.0)
        reg('chain_row_%d' % i, (x0, yy, x1, yy + h))
        yy += h
    reg('chain_strip', (x0, y, x1, y + ph))
    return y + ph


# ------------------------------------------------------------------------------------------------------ other column plates (placeholders for the layout: objectives and RAM keep their own clusters' drawing)
def star5(L, x, y, state, r=15):
    pts = []
    for i in range(10):
        a = -90 + 36 * i
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(math.radians(a)), y + rr * math.sin(math.radians(a))))
    if state == 'met':
        L.poly(pts, fill=GOLD, outline=INK, w=2)
    elif state == 'failed':
        L.poly(pts, fill=(40, 30, 34), outline=(150, 80, 80), w=2)
    else:
        L.poly(pts, fill=None, outline=WHITE, w=2.2)


def objectives_row(L, f, y):
    x0, x1, ox = G['px0'], G['px1'], G['ox']
    h = G['obj_h']
    P(L, (x0, y, x1, y + h), 'objectives')
    cy = y + h / 2
    star5(L, ox + 20, cy, 'open', 14)
    txt(L, ox + 42, cy, 'WIN', 22, GOLD, 'mono', 'lm', 0.08)
    names = {'card': 'TRIGGER HITS', 'daemon': 'KILL ADJUSTER', 'heat': 'TRACE LOW', 'scrap': 'SLICES KEPT'}
    cons = f['consts']
    x = ox + 120
    for i, ch in enumerate(f['challenges']):
        star5(L, x, cy, ch['state'], 13)
        lw = txt(L, x + 22, cy, names[ch['name']], 16, THI, 'mono', 'lm', 0.04)
        xx = x + 22 + lw + 10
        x = xx + 30 + (66 if ch['name'] in ('card', 'daemon', 'heat') else 0)
        if ch['name'] == 'card':
            n = min(f['interf'], cons['STAR_CARD'])
            if n:
                tally(L, xx, cy, 'yel', n, 6, 12, pitch=8, gap=10)
        elif ch['name'] == 'daemon':
            tally(L, xx, cy, 'gold', f['adj']['hp'], 4, 12, pitch=6, gap=8)
        elif ch['name'] == 'heat' and f['trace']:
            tally(L, xx, cy, 'viol', min(f['trace'], 5), 6, 12, pitch=8, gap=10)
    reg('objectives', (x0, y, x1, y + h))
    return y + h


def ram_row(L, f, y):
    x0, x1, ox = G['px0'], G['px1'], G['ox']
    h = G['ram_h']
    P(L, (x0, y, x1, y + h), 'ram')
    cy = y + h / 2
    txt(L, ox + 12, cy, 'RAM', LBL_PX, TMID, 'mono', 'lm', LBL_TRK)
    for i in range(f['ram_max']):
        bx = ox + 62 + i * 30
        if i < f['ram']:
            coin(L, bx + 12, cy, 24, False)
        else:
            L.ellipse([bx, cy - 12, bx + 24, cy + 12], fill=(8, 14, 22), outline=CYAN, w=2)
    txt(L, ox + 230, cy, 'TRACE', LBL_PX, TMID, 'mono', 'lm', LBL_TRK)
    for i in range(f['tcap']):
        bx = ox + 300 + i * 30
        on = i < f['trace']
        L.rect([bx, cy - 11, bx + 22, cy + 11], fill=(160, 60, 255) if on else (28, 20, 44), outline=INK if on else (160, 60, 255), w=2, r=3)
    txt(L, ox + 520, cy, 'ENDS = HEAT', LBL_PX, AMBER, 'mono', 'lm', LBL_TRK)
    if f['pv']['trace_after']:
        tally(L, ox + 660, cy, 'gold', f['pv']['trace_after'], 8, 16, pitch=11, gap=14)
    reg('ram', (x0, y, x1, y + h))
    return y + h


# ------------------------------------------------------------------------------------------------------ ground: scrim slabs
def scrim_layers(base, col_bottom):
    """hud_scrim A: two soft SCRIM slabs (column, hand), 24 px feather, a pure alpha shape: nothing is blurred under it, the room hull stays sharp"""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([G['px0'] - 18, 0, W, col_bottom + 14], radius=18, fill=(2, 3, 10, 140))
    d.rounded_rectangle([960, 836, W, H], radius=24, fill=(2, 3, 10, 120))
    lay = lay.filter(ImageFilter.GaussianBlur(12))
    base.alpha_composite(lay)


# ------------------------------------------------------------------------------------------------------ the column
def draw_hud(L, f, beat, extra=None):
    R.clear()
    extra = extra or {}
    f = dict(f)
    if extra.get('through0'):
        pv = dict(f['pv']); eq = dict(pv['eq']); eq.update(through=0, absorbed=eq['absorbed'] + eq['through']); pv['eq'] = eq; pv['hp_after'] = f['hp']; f['pv'] = pv
    if extra.get('waves3'):
        f['waves_left'] = 3
    if extra.get('hp_gone'):
        f['hp'] = 11
    if extra.get('trig_lands'):
        pv = dict(f['pv']); eq = dict(pv['eq']); eq['tower_from_trigger'] = 2; pv['eq'] = eq; f['pv'] = pv
    if extra.get('soaked'):
        pv = dict(f['pv']); eq = dict(pv['eq']); eq.update(soaked=3, absorbed=3); pv['eq'] = eq; f['pv'] = pv
    yb = header(L, f)
    y = yb + G['gap']
    pencil = beat == 'p2'
    tp = J['twist_payoff'] if beat in ('p2', 'p3') else None
    y = bill_box(L, f, y, pencil=pencil, plan_tag='BEST LINE' if beat in ('p2', 'p3') else None, twist_pay=tp) + G['gap']
    if beat == 'p2':
        y0 = y
        lines = [('TRIGGER ONLY', J['meta']['lines']['trigger'][0], J['meta']['lines']['trigger'][1], J['f2t']['pv']['eq'], J['f2t']['refunds'] > 0, False),
                 ('BRACE + SOAK ONLY', J['meta']['lines']['brace'][0], J['meta']['lines']['brace'][1], J['f2b']['pv']['eq'], False, False),
                 ('BEST: ALL THREE', J['meta']['hero'], J['meta']['hero_end'], f['pv']['eq'], f['refunds'] > 0, True)]
        for nm, plan, soak, eq, refund, sel in lines:
            y = option_chip(L, y, nm, plan, soak, eq, sel=sel, refund=refund)
        y = y - G['chip_gap'] + G['gap']
        for nm in ('option_chips', 'option_plan_glyphs', 'option_name_label', 'option_outcome_bar', 'option_pair'):
            reg(nm, (G['px0'], y0, G['px1'], y - G['gap']))
    elif beat == 'p3':
        y = chain_strip(L, f, y) + G['gap']
        for nm in ('chain_step_discs', 'chain_step_glyphs', 'chain_step_names', 'chain_result_tallies', 'chain_result_prose'):
            reg(nm, R['chain_strip'])
    y = objectives_row(L, f, y) + G['gap']
    y = ram_row(L, f, y)
    reg('_column', (G['px0'], 12, G['px1'], y))
    reg('layout_grid', (G['px0'] - 40, 0, G['px1'] + 24, y + 20))
    reg('terminal_plate_kit', (G['px0'] - 12, 6, G['px1'] + 12, y + 8))
    reg('hud_scrim', (G['px0'] - 120, 0, 1920, 640))
    reg('row_tags', R['bill_frame'])
    return y


# ------------------------------------------------------------------------------------------------------ render
_base = {}
OUTD = ROOT + 'out2/'
os.makedirs(OUTD, exist_ok=True)


def base_for(beat):
    if beat not in _base:
        _base[beat] = Image.open(CACHE + 'base_%s.png' % beat).convert('RGBA')
    return _base[beat].copy()


def stickers2(base, L):
    st = vinyl('CELL-9 // BREAKER', 34, CYAN, tilt=2)
    shadow_paste(base, st, (22, 968), 0.5, 8, (5, 9))
    se = vinyl('SEND IT', 62, YEL, tilt=-3, pad=(24, 6))
    shadow_paste(base, se, (1655, 968))
    L.text((1780, 1070), '> turn_resolve.exe', 16, 'mono', fill=TXT_MID)      # actions' bottom hint, as E10 (UNDO is not drawn here: actions owns it)


def render(beat, Vd=None, full=False, extra=None):
    V.clear()
    V.update(Vd or {})
    NOW['words'] = beat != 'nowords'
    base = base_for(beat)
    f = J[BEATKEY[beat]]
    L = L2()
    bottom = draw_hud(L, f, 'p1' if beat in ('nowords', 'p2b') else beat, extra)
    scrim_layers(base, bottom)
    base.alpha_composite(L.done())
    if full:
        played = [a[0] for a in f['played']]
        hand = list(f['hand'])
        if beat == 'p3':
            hand = list(J['f1']['hand'])
            for c_ in played:
                hand.remove(c_)
        hover_i = hand.index('Trigger') if beat == 'p2' else None
        CHR.hand(base, hand, x0=1000, hover=hover_i, played=played if beat == 'p3' else (), cy0=948)
        L3 = L2()
        stickers2(base, L3)
        base.alpha_composite(L3.done())
    return base, dict(R)
