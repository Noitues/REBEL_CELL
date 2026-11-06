"""Build the E10 Shifting Waves plates (converged look, display A + H slices + Brace / soak / rim landing chips).
python build9.py <p1|p2|p2b|p3|nowords|all>.  Everything numeric comes from state_e10.json (dump10.py: the E10 sim, asserted).
HUD quantities are tally segments (groups of 5); the hero is one big "lands -> through" pair; no digits on units or slices; digits only in the title, W chips, ring tags, sector digits,
the hero pair and the p2b hover tag."""
import sys, json, math
sys.dont_write_bytecode = True
from e10lib import *
import cv_board as CB9
from cv_board import render_board
import cv_chrome as CH

OUT = 'D:/rc_tmp/combat_critic/plates/waves_e10/'
J = json.load(open(ROOT + 'state_e10.json'))
S0 = json.load(open(ROOT + 'state_cv.json'))
CONS = S0['consts']
CB9.HUB['col'] = CYAN
X0, X1 = 1066, 1904
CARDS = {
    'Nudge': dict(cost=1, fam='TOWER', g='PI_SPIN_CW', txt='Turn the tower 1', x='1', nm='NUDGE'),
    'Spin2': dict(cost=1, fam='TOWER', g='PI_SPIN_CW', txt='Turn the tower 2', x='2', nm='SPIN 2'),
    'Spin3': dict(cost=1, fam='TOWER', g='PI_SPIN_CW', txt='Turn the tower 3', x='3', nm='SPIN 3'),
    'Brace': dict(cost=1, fam='TOWER', g='C_BRACE', txt='Block a slice', nm='BRACE'),
    'Firewall': dict(cost=2, fam='WAVE', g='BURN', txt='Burn 2 units', nm='FIREWALL'),
    'Pull': dict(cost=0, fam='WAVE', g='C_PULL', txt='Pull a unit in', nm='PULL'),
    'Shove': dict(cost=2, fam='WAVE', g='C_SHOVE', txt='Slide a unit 1', nm='SHOVE'),
    'Twist': dict(cost=0, fam='WAVE', g='C_TWIST', txt='Turn one ring 1', nm='TWIST'),
    'Hold': dict(cost=0, fam='WAVE', g='C_HOLD', txt='Pause the wave', nm='HOLD'),
    'Trigger': dict(cost=1, fam='WAVE', g='C_TRIG', txt='Resolve a unit', nm='TRIGGER'),
    'Strike': dict(cost=1, fam='TOWER', g='C_STRIKE', txt='Hit a unit for 2', nm='STRIKE'),
}
for k, v in CARDS.items():
    v['cost'], v['loud'] = J['cards'][k]
CH.CARDS.update(CARDS)
SEGC = {'hp': GREEN, 'lose': (255, 120, 110), 'through': RED, 'absorb': CYAN, 'slice': GREEN, 'raw': RED, 'yel': YEL, 'cyan': CYAN, 'rider': LAV, 'braced': CREAM,
        'gold': GOLD, 'viol': (160, 60, 255), 'soak': SOAK_C}
ICON = {'Trigger': 'C_TRIG', 'Spin2': 'PI_SPIN_CW', 'Nudge': 'PI_SPIN_CW', 'Brace': 'C_BRACE', 'Shove': 'C_SHOVE', 'Hold': 'C_HOLD', 'Twist': 'C_TWIST', 'Firewall': 'BURN', 'Strike': 'C_STRIKE'}


# ----------------------------------------------------------------------------- HUD parts
def seg(L, x, y, kind, w=11, h=18, alpha=255, lit=True):
    col = SEGC[kind]
    if lit:
        L.rect([x, y - h / 2, x + w, y + h / 2], fill=col + (alpha,), outline=INK + (alpha,), w=1.6, r=3)
        if kind == 'lose':
            L.line([(x, y + h / 2), (x + w, y - h / 2)], (255, 255, 255, alpha), 1.8)
    else:
        L.rect([x, y - h / 2, x + w, y + h / 2], fill=(14, 20, 24, alpha), outline=(70, 86, 92, alpha), w=1.4, r=3)


def seg_run(L, x, y, kind, n, w=11, h=18, alpha=255, pitch=None):
    pitch = pitch or w + 4
    for i in range(n):
        seg(L, x + i * pitch + (i // 5) * 10, y, kind, w, h, alpha)
    return x + n * pitch + max(0, (n - 1) // 5) * 10 + (4 if n == 0 else 0)


def empty_run(L, x, y, w=9, h=18):
    seg(L, x, y, 'raw', w, h, lit=False)
    return x + w + 6


def label(L, x, y, s, col=TXT_MID, px=16, alpha=255):
    L.text((x, y), s, px, 'mono', fill=tuple(col) + (alpha,), anchor='lm')
    return L.tw(s, px, 'mono')


def op(L, x, y, s, alpha=255):
    L.text((x, y + 1), s, 28, 'anton', fill=(242, 246, 255, alpha), anchor='mm')


def arrow_r(L, x, y, col, w=26, h=9):
    L.poly([(x, y - 4), (x + w - 10, y - 4), (x + w - 10, y - h), (x + w, y), (x + w - 10, y + h), (x + w - 10, y + 4), (x, y + 4)], fill=col, outline=INK, w=1.6)


def star(L, x, y, state, r=15):
    pts = []
    for i in range(10):
        a = -90 + 36 * i
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(math.radians(a)), y + rr * math.sin(math.radians(a))))
    if state == 'met':
        L.poly(pts, fill=GOLD, outline=INK, w=2)
    elif state == 'failed':
        L.poly(pts, fill=(40, 30, 34), outline=(150, 80, 80), w=2)
        L.line([(x - r, y + r), (x + r, y - r)], RED, 3.5)
    else:
        L.poly(pts, fill=None, outline=WHITE, w=2.2)


def header(L, f):
    terminal(L, (X0, 12, X1, 58))
    L.text((X0 + 18, 35), 'TURN %d  |  SHIFTING WAVES' % f['turn'], 30, 'anton', fill=WHITE, anchor='lm')
    L.text((X0 + 440, 35), 'WAVES %d LEFT' % f['waves_left'], 24, 'anton', fill=ORANGE, anchor='lm')
    x = X0 + 650
    for i in range(6):
        lit = i >= 6 - f['waves_left']
        col = RED if i == 5 else ORANGE
        L.rect([x + i * 20, 25, x + i * 20 + 14, 45], fill=col if lit else (20, 20, 30), outline=col, w=2, r=3)
    L.ellipse([X1 - 40, 19, X1 - 8, 51], fill=(8, 10, 18, 250), outline=YEL, w=2.6)
    L.text((X1 - 24, 36), '?', 24, 'anton', fill=YEL)


def hero_pair(L, x, y, lands, through):
    """THE number: lands -> through (big)"""
    label(L, x, y - 36, 'LANDS', TXT_MID, 16)
    L.text((x + 4, y), str(lands), 58, 'anton', fill=WHITE, anchor='lm', stroke=2.5)
    ax = x + 50
    arrow_r(L, ax, y, YEL, 34, 11)
    label(L, ax + 46, y - 36, 'THROUGH', TXT_MID, 16)
    L.text((ax + 50, y), str(through), 58, 'anton', fill=RED if through else GREEN, anchor='lm', stroke=2.5)


def bill_box(L, f, y, pencil=False, plan_tag=None, twist_pay=None):
    pv = f['pv']
    eq = pv['eq']
    h = 202
    L.rect([X0 - 4, y, X1, y + h], fill=(8, 12, 22, 218), outline=WHITE, w=3, r=10)
    label(L, X0 + 10, y + 17, 'YOU', CRT_TXT, 16)
    after = pv['hp_after']
    x = X0 + 56
    for i in range(f['maxhp']):
        xx = x + i * 17 + (i // 5) * 9
        if i >= f['hp']:
            seg(L, xx, y + 46, 'hp', 13, 22, lit=False)
        else:
            seg(L, xx, y + 46, 'hp' if i < after else 'lose', 13, 22)
    xe = x + f['maxhp'] * 17 + 18
    if pencil:
        L.line([(X0 + 6, y + 66), (xe - 8, y + 68)], (6, 3, 8), 9)
        L.line([(X0 + 6, y + 66), (xe - 8, y + 68)], YEL, 6)
    hero_pair(L, xe + 20, y + 54, eq['lands'], eq['through'])
    if plan_tag:
        L.text((X1 - 16, y + 17), plan_tag, 16, 'mono', fill=YEL, anchor='rm')
    # equation to LANDS
    yy = y + 100
    terminal(L, (X0 + 2, y + 74, X1 - 4, y + 120))
    groups = [('RAW', 'raw', eq['raw0'], None)]
    if eq['triggered']:
        groups.append(('TRIG', 'yel', eq['triggered'], '-'))
    if eq['tower_from_trigger']:
        groups.append(('TRIG LANDS', 'raw', eq['tower_from_trigger'], '+'))
    groups.append(('SHOT', 'cyan', eq['shot_down'], '-'))
    groups.append(('BRACE', 'braced', eq['braced'], '-'))
    groups.append(('RIDER', 'rider', eq['rider'], '-'))
    x = X0 + 12
    for name, kind, n, o in groups:
        if o:
            op(L, x + 6, yy, o)
            x += 22
        lw = label(L, x, y + 84, name, TXT_MID, 16)
        e = seg_run(L, x, yy, kind, n, 9, 18, pitch=12) if n else empty_run(L, x, yy)
        x = max(e, x + lw) + 4
    op(L, x + 6, yy, '=')
    x += 24
    lw = label(L, x, y + 84, 'LANDS', TXT_MID, 16)
    seg_run(L, x, yy, 'raw', eq['lands'], 9, 18, pitch=12)
    # the split: LANDS routes to absorbed / the marked slices / YOU
    yb = y + 146
    terminal(L, (X0 + 2, y + 124, X1 - 4, y + 168))
    x = X0 + 14
    label(L, x, yb - 16 + 4, 'SPLIT', TXT_MID, 16)
    x += 62
    lw = label(L, x, yb - 14, 'ABSORBED', TXT_MID, 16)
    e = seg_run(L, x, yb + 6, 'absorb', eq['absorbed'], 11, 18, pitch=14) if eq['absorbed'] else empty_run(L, x, yb + 6, 11)
    x = max(e, x + lw) + 22
    op(L, x - 12, yb + 4, '+')
    lw = label(L, x + 8, yb - 14, 'SOAK', SOAK_C, 16)
    x2 = x + 8 + lw + 8
    L.line([(x2, yb - 14), (x2 + 16, yb - 14)], INK, 8)
    arrow_r(L, x2 + 2, yb - 14, SOAK_C, 22, 8)
    L.rect([x2 + 28, yb - 19, x2 + 48, yb - 9], fill=GREEN, outline=INK, w=1.6, r=5)      # the slice bar
    e = seg_run(L, x + 8, yb + 6, 'soak', eq['soaked'], 11, 18, pitch=14) if eq['soaked'] else empty_run(L, x + 8, yb + 6, 11)
    x = max(e, x2 + 52) + 22
    op(L, x - 12, yb + 4, '+')
    lw = label(L, x + 8, yb - 14, 'YOU', RED, 16)
    x3 = x + 8 + lw + 8
    arrow_r(L, x3, yb - 14, RED, 22, 8)
    seg(L, x3 + 28, yb - 14, 'hp', 13, 14)
    seg_run(L, x + 8, yb + 6, 'through', eq['through'], 11, 18, pitch=14) if eq['through'] else empty_run(L, x + 8, yb + 6, 11)
    # ghost NEXT
    nx = f['next']
    yg = y + 186
    al = 120
    label(L, X0 + 12, yg, 'NEXT', TXT_MID, 16, al)
    x = X0 + 76
    x = (seg_run(L, x, yg, 'through', nx['taken'], 11, 14, al) if nx['taken'] else x + 4) + 26
    x = (seg_run(L, x, yg, 'absorb', nx['absorbed'], 11, 14, al) if nx['absorbed'] else x) + 26
    seg_run(L, x, yg, 'slice', nx['slost'], 11, 14, al)
    if twist_pay:
        xt = X0 + 372
        L.ellipse([xt - 12, yg - 12, xt + 12, yg + 12], fill=(30, 26, 6), outline=YEL, w=2.2)
        L.glyph('C_TWIST', 17, (xt, yg), YEL)
        lw = label(L, xt + 20, yg, 'WITHOUT TWIST', YEL, 16)
        for i in range(twist_pay['without']['taken']):
            L.rect([xt + 28 + lw + i * 15, yg - 8, xt + 38 + lw + i * 15, yg + 8], fill=None, outline=RED, w=2.4, r=3)
        L.text((xt + 36 + lw + twist_pay['without']['taken'] * 15 + 20, yg), '>', 20, 'anton', fill=YEL, anchor='mm')
        for i in range(nx['taken']):
            seg(L, xt + 44 + lw + twist_pay['without']['taken'] * 15 + 24 + i * 15, yg, 'through', 10, 16)
    return y + h + 8


def option_chip(L, y, name, plan, soak, eq, sel=False, solid=True, refund=False):
    h = 40
    L.rect([X0 - 4, y, X1, y + h], fill=(6, 10, 20, 235), outline=YEL if sel else (110, 120, 140), w=3 if sel else 2, r=8)
    x = X0 + 10
    for c in plan:
        g = ICON.get(c[0])
        if g:
            L.glyph(g, 20, (x + 10, y + 20), CREAM if c[0] == 'Brace' else (YEL if c[0] == 'Trigger' else CYAN))
            x += 26
    if soak:
        for dx in (0, 6):
            p = [(x + dx, y + 13), (x + dx + 6, y + 23), (x + dx, y + 27)]
            L.line([(x + dx - 3, y + 14), (x + dx + 4, y + 21), (x + dx - 3, y + 28)], INK, 6)
            L.line([(x + dx - 3, y + 14), (x + dx + 4, y + 21), (x + dx - 3, y + 28)], SOAK_C, 3.4)
        x += 18
    if refund:
        burst(L, x + 12, y + 20, 7, 15, 9)
        L.rect([x + 28, y + 12, x + 46, y + 28], fill=CYAN, outline=INK, w=1.6, r=3)
        L.line([(x + 37, y + 15), (x + 37, y + 25)], INK, 2.6)
        L.line([(x + 32, y + 20), (x + 42, y + 20)], INK, 2.6)
        x += 54
    label(L, X0 + 190 if x < X0 + 185 else x + 8, y + 20, name, YEL if sel else WHITE, 16)
    x = X0 + 400
    # one total-lands bar: red = costs HP, orange = soaked by slices, cyan = absorbed
    x = seg_run(L, x, y + 20, 'through', eq['through'], 11, 20, pitch=13) if eq['through'] else x
    n_so, n_ab = eq['soaked'], eq['absorbed']
    xx = x + (6 if eq['through'] else 0)
    if n_so:
        xx = seg_run(L, xx, y + 20, 'soak', n_so, 11, 20, pitch=13) + 4
    if n_ab:
        seg_run(L, xx, y + 20, 'absorb', n_ab, 11, 20, pitch=13)
    L.text((X1 - 16, y + 20), '%d > %d' % (eq['lands'], eq['through']), 24, 'anton', fill=WHITE, anchor='rm', stroke=2)
    return y + h + 4


def stars_row(L, f, y):
    L.rect([X0 - 4, y, X1, y + 44], fill=(8, 12, 22, 215), outline=(110, 120, 140), w=2, r=8)
    star(L, X0 + 20, y + 22, 'open', 14)
    label(L, X0 + 42, y + 22, 'WIN', GOLD, 16)
    names = {'card': 'TRIGGER HITS', 'daemon': 'KILL ADJUSTER', 'heat': 'TRACE LOW', 'scrap': 'SLICES KEPT'}
    cons = f['consts']
    for i, ch in enumerate(f['challenges']):
        x = X0 + 120 + i * 238
        star(L, x, y + 22, ch['state'], 13)
        lw = label(L, x + 22, y + 22, names[ch['name']], WHITE, 16)
        xx = x + 22 + lw + 10
        if ch['name'] == 'card':
            n = min(f['interf'], cons['STAR_CARD'])
            seg_run(L, xx, y + 22, 'yel', n, 6, 12, pitch=8) if n else None
        elif ch['name'] == 'daemon':
            seg_run(L, xx, y + 22, 'gold', f['adj']['hp'], 4, 12, pitch=6)
        elif ch['name'] == 'heat':
            seg_run(L, xx, y + 22, 'viol', min(f['trace'], 5), 6, 12, pitch=8) if f['trace'] else None
    return y + 48


def ram_trace(L, f, y):
    terminal(L, (X0 - 4, y, X1, y + 48))
    label(L, X0 + 12, y + 24, 'RAM', CRT_TXT, 16)
    for i in range(f['ram_max']):
        bx = X0 + 58 + i * 34
        L.rect([bx, y + 11, bx + 28, y + 37], fill=CYAN if i < f['ram'] else (20, 34, 52), outline=CYAN, w=2, r=4)
        if f.get('refunds') and i == f['ram'] - 1 and i >= 0:
            burst(L, bx + 14, y + 24, 20, 30, 12)
            L.rect([bx, y + 11, bx + 28, y + 37], fill=CYAN, outline=INK, w=2.4, r=4)
            L.line([(bx + 14, y + 17), (bx + 14, y + 31)], INK, 3.4)
            L.line([(bx + 7, y + 24), (bx + 21, y + 24)], INK, 3.4)
    label(L, X0 + 230, y + 24, 'TRACE', CRT_TXT, 16)
    for i in range(f['tcap']):
        bx = X0 + 292 + i * 32
        on = i < f['trace']
        L.rect([bx, y + 11, bx + 26, y + 37], fill=(160, 60, 255) if on else (28, 20, 44), outline=(160, 60, 255), w=2, r=4)
        if i == f['tcap'] - 1:
            for q in range(0, 26, 7):
                L.line([(bx + q, y + 37), (bx + q + 8, y + 11)], (255, 255, 255, 110), 2)
    label(L, X0 + 520, y + 24, 'ENDS = HEAT', AMBER, 16)
    seg_run(L, X0 + 640, y + 24, 'gold', f['pv']['trace_after'], 11, 18) if f['pv']['trace_after'] else None
    return y + 52


def stickers(base, L):
    st = vinyl('CELL-9 // BREAKER', 34, CYAN, tilt=2)
    shadow_paste(base, st, (22, 968), 0.5, 8, (5, 9))
    se = vinyl('SEND IT', 62, YEL, tilt=-3, pad=(24, 6))
    shadow_paste(base, se, (1655, 968))
    terminal(L, (1740, 922, 1890, 960))
    L.text((1815, 941), 'UNDO [Z]', 18, 'mono', fill=CRT_TXT)
    L.text((1780, 1070), '> turn_resolve.exe', 16, 'mono', fill=TXT_MID)


def chain_strip(L, f, y):
    steps = f['chain']
    h = 24
    L.rect([X0 - 4, y, X1, y + 12 + len(steps) * h], fill=(8, 12, 22, 218), outline=(110, 120, 140), w=2, r=8)
    yy = y + 6
    for i, st in enumerate(steps):
        cy = yy + h / 2
        L.ellipse([X0 + 6, cy - 11, X0 + 28, cy + 11], fill=(10, 9, 16), outline=WHITE, w=2)
        L.text((X0 + 17, cy + 1), str(i + 1), 16, 'anton', fill=WHITE)
        L.glyph(st['glyph'], 20, (X0 + 50, cy), tuple(st['col']))
        L.text((X0 + 68, cy), st['name'], 16, 'mono', fill=tuple(st['col']), anchor='lm')
        x = X0 + 250
        for kind, n in st['pips']:
            if kind == 'txt':
                L.text((x, cy), n, 16, 'mono', fill=TXT_MID, anchor='lm')
                x += L.tw(n, 16, 'mono') + 10
            elif kind == 'refund':
                burst(L, x + 14, cy, 7, 14, 9)
                L.rect([x + 30, cy - 9, x + 56, cy + 9], fill=CYAN, outline=INK, w=2, r=3)
                L.line([(x + 43, cy - 5), (x + 43, cy + 5)], INK, 3)
                L.line([(x + 38, cy), (x + 48, cy)], INK, 3)
                x += 68
            elif n:
                x = seg_run(L, x, cy, kind, n, 10, 16) + 10
        yy += h
    return y + 12 + len(steps) * h + 4


# ----------------------------------------------------------------------------- board
def arcs_data(f):
    out = []
    board = {w for w in f['rings_wave'] if w >= 0}
    for i, w in enumerate(f['lineup']):
        units = [(k, wd) for k, wd, s in w]
        st = 'future' if i >= f['nfut'] else ('board' if i in board else 'resolved')
        out.append(dict(wave=i, state=st, units=units, climax=i == len(f['lineup']) - 1))
    return out


def board_frame(f, keep_all=False):
    fr = dict(S0['f1'])
    fr['wheel'] = [dict(t=w['t'], hp=w['hp'], sector=w['sector'], mx=w['mx']) for w in f['wheel']]
    fr['units'] = [dict(id=u['id'], kind=u['kind'], dep=u['dep'], s=u['s'], w=u['w'], hp=u['hp']) for u in f['units'] if keep_all or not (u['consumed'] or u['trigdead'])]
    fr['adjuster'] = None
    return fr


def draw_units(L, f, only=None, skip=None):
    for u in f['units']:
        if only is not None and u['id'] not in only:
            continue
        if skip is not None and u['id'] in skip:
            continue
        if u['consumed'] or u['trigdead']:
            cell_outline(L, u, col=YEL if u['consumed'] else RED, w=3)
            ri, ro = CB.ring_geom(u['dep'])
            L.poly(L.band(C, ri + 4, ro - 4, span(u)[0] + 3, span(u)[1] - 3), fill=(6, 3, 8, 105))
            token(L, u, dead=True)
            continue
        lit_cell(L, u)
        cell_outline(L, u)
        token(L, u)
        hp_row(L, u, u['hp'], u['mx'], lose=u['lose'][1], shield=u['sh'], shmx=u['shmx'])
        if u['df'] == 'armor':
            armor_cap(L, u)
        grow = max(0, u['land_hit'] - u['hit']) if (u['fate']['kind'] == 'lands' and 'land_hit' in u) else 0
        chevrons_h(L, u, u['hit'], grow)
        if u['warded']:
            warded_mark(L, u)
        if u['fate']['kind'] == 'dies':
            dead_x(L, u)


def twist_badge(L, f):
    """the Twist played this turn: a yellow twist badge on its ring's tag (ring +1 turns one extra sector clockwise at END TURN)"""
    ring, dirn = f['twr']
    if not dirn:
        return
    ri, ro = CB.ring_geom(ring)
    x, y = ppx(C, (ri + ro) / 2, 30)
    lane = LANE[ring]
    s = lane['name'] + (' W%d' % (f['rings_wave'][ring] + 1) if f['rings_wave'][ring] >= 0 else '')
    wd = L.tw(s, 17, 'anton') + 14
    bx, by = x + wd / 2 + 24, y
    L.ellipse([bx - 17, by - 17, bx + 17, by + 17], fill=(26, 22, 4, 250), outline=YEL, w=3)
    L.glyph('C_TWIST', 24, (bx, by), YEL)
    for q in (0, 1):
        xx = bx + 25 + q * 9
        L.line([(xx - 4, by - 8), (xx + 4, by), (xx - 4, by + 8)], INK, 6.5)
        L.line([(xx - 4, by - 8), (xx + 4, by), (xx - 4, by + 8)], YEL, 3.4) if q == 0 or abs(dirn) > 1 else None


def refund_marks(L, f):
    """E10: a Trigger kill pays +1 RAM (once a turn): a gold burst on the killed unit's cell and a cyan RAM pip popping out of it"""
    if not f.get('refunds'):
        return
    kl = f['kills'][-1]
    ri, ro = CB.ring_geom(kl['dep'])
    x, y = ppx(C, (ri + ro) / 2, 60 * kl['sector'])
    burst(L, x, y, 14, 30, 12)
    ram_pip_pop(L, x + 30, y - 24)
    if NOW['words']:
        L.rect([x - 40, y + 24, x + 44, y + 46], fill=(8, 10, 18, 245), outline=(255, 214, 64), w=2, r=5)
        L.text((x + 2, y + 35), 'REFUND', 16, 'mono', fill=(255, 214, 64))


def wave_arcs10(L, arcs):
    """FUTURE waves: thin arcs outside the landing lanes (compact: 19 px apart), unit glyphs on them, a W<n> tab staggered at the arc start"""
    r = 492
    fut = [a for a in arcs if a['state'] == 'future']
    for i, a in enumerate(fut):
        col_w = RED if a.get('climax') else ORANGE
        L.line(L.arc_pts(C, r, E8.ARC_START, E8.ARC_START + 359, 120), col_w + (235,), 3)
        ang = E8.ARC_START
        for (kind, w) in a['units']:
            a1 = ang + 60 * w
            kc = KCOL.get(kind, WHITE)
            m = (ang + a1) / 2
            x, y = ppx(C, r, m)
            L.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(10, 12, 22, 240), outline=kc, w=2)
            L.glyph(KIND[kind][1], 13, (x, y), WHITE)
            for q in range(1, w):
                x2, y2 = ppx(C, r, ang + 60 * q)
                L.ellipse([x2 - 3, y2 - 3, x2 + 3, y2 + 3], fill=WHITE + (200,))
            ang = a1
        if a.get('climax'):
            for k in range(E8.ARC_START, E8.ARC_START + 360, 14):
                L.line([ppx(C, r - 5, k), ppx(C, r + 5, k + 6)], (255, 226, 0, 190), 2.4)
        if NOW['words']:
            x, y = ppx(C, r, E8.ARC_START - 3.6 - 3.2 * i)
            lab = 'W%d' % (a['wave'] + 1)
            L.rect([x - 22, y - 11, x + 22, y + 11], fill=(8, 10, 18, 255), outline=col_w, w=2, r=5)
            L.text((x, y + 1), lab, 16, 'mono', fill=col_w)
        r += 17


def ring_tags(L, f):
    for d in range(3):
        ri, ro = CB.ring_geom(d)
        x, y = ppx(C, (ri + ro) / 2, 30)
        lane = LANE[d]
        w_ = f['rings_wave'][d]
        s = lane['name'] + (' W%d' % (w_ + 1) if w_ >= 0 else '')
        wd = L.tw(s, 17, 'anton') + 14
        L.rect([x - wd / 2, y - 12, x + wd / 2, y + 12], fill=(8, 10, 18, 245), outline=lane['col'], w=2, r=6)
        L.text((x, y + 1), s, 17, 'anton', fill=lane['col'], anchor='mm')


def nudge_ghost(L):
    for sg in (-1, 1):
        x, y = ppx(C, RS['hp1'] + 12, sg * 13)
        L.poly([(x - 8 * sg, y - 8), (x + 8 * sg, y), (x - 8 * sg, y + 8)], fill=(8, 20, 30, 120), outline=CYAN, w=2.2)


LOGD = []


def AD(name, got, want):
    ok = got == want
    LOGD.append('%s  %s: %s == %s' % ('PASS' if ok else 'FAIL', name, got, want))
    assert ok, (name, got, want)


def draw_asserts(beat, f):
    """what was drawn (e10lib.REG) == the asserted frame: every chevron, diamond, soak mark, clamp and dot on the arcs, every body chevron, the Adjuster bar, the hero pair"""
    tag = beat
    alive = [u for u in f['units'] if not (u['consumed'] or u['trigdead']) and u['fate']['kind'] == 'lands' and 'land_hit' in u]
    if beat == 'p2b':
        alive = [u for u in alive if u['id'] == J['hover']['id']]
    for u in alive:
        rows = [r for r in REG['arcs'] if r['uid'] == u['id']]
        AD('%s unit %d arc rows == landing sectors' % (tag, u['id']), sorted(r['sector'] for r in rows), sorted(u['land_sectors']))
        AD('%s unit %d chevrons per sector (solid + hollow) == hit at landing' % (tag, u['id']), sorted(set(r['solid'] + r['hollow'] for r in rows)), [u['land_hit']])
        AD('%s unit %d hollow chevrons == growth to come' % (tag, u['id']), sorted(set(r['hollow'] for r in rows)), [max(0, u['land_hit'] - min(u['hit'], u['land_hit']))])
        AD('%s unit %d diamonds per sector == HP through (sim)' % (tag, u['id']), {str(r['sector']): r['diamonds'] for r in rows}, u['land_through'])
        AD('%s unit %d soak marks / clamps per sector == sim' % (tag, u['id']), ({str(r['sector']): r['soak'] for r in rows}, {str(r['sector']): r['brace'] for r in rows}), (u['land_soak'], u['land_brace']))
        AD('%s unit %d turns-until dots == forecast k' % (tag, u['id']), sorted(set(r['k'] for r in rows)), [u['fate']['k']])
    if beat != 'p2b':
        k0 = [r for r in REG['arcs'] if r['k'] == 0]
        AD('%s sum of this-turn diamonds == hero THROUGH (%d)' % (tag, f['pv']['eq']['through']), sum(r['diamonds'] for r in k0), f['pv']['eq']['through'])
        AD('%s arcs drawn == units that land' % tag, sorted(set(r['uid'] for r in REG['arcs'])), sorted(u['id'] for u in alive))
        for b in REG['bodies']:
            u = [x for x in f['units'] if x['id'] == b['uid']][0]
            AD('%s unit %d body chevrons: solid == hit now, hollow == growth to come' % (tag, u['id']), (b['solid'], b['hollow']), (u['hit'], max(0, u['land_hit'] - u['hit']) if (u['fate']['kind'] == 'lands' and 'land_hit' in u) else 0))
    if REG['adj']:
        AD('%s Adjuster bar segments == sim HP, lost == sim hp_after' % tag, (REG['adj']['segments'], REG['adj']['lost']), (f['adj']['hp'], f['adj']['hp'] - f['adj']['hp_after']))
        AD('%s Adjuster body on ring +%d sector %d (sim)' % (tag, f['adj']['ring'], f['adj']['s']), (REG['adj']['ring'], REG['adj']['sector']), (f['adj']['ring'], f['adj']['s']))
    AD('%s hero pair == sim bill (lands, through)' % tag, (f['pv']['eq']['lands'], f['pv']['eq']['through']), (f['pv']['eq']['lands'], f['pv']['taken']))


def make(beat):
    reg_reset()
    NOW['words'] = beat != 'nowords'
    CB9.HUB['name'] = 'Breaker' if beat != 'nowords' else ''
    key = {'p1': 'f1', 'nowords': 'f1', 'p2': 'f2', 'p2b': 'f1', 'p3': 'f2'}[beat]
    f = J[key]
    f1 = J['f1']
    bg = backdrop()
    dim_ids = [u['id'] for u in f['units'] if u['id'] != J['hover']['id']] if beat == 'p2b' else None
    bg.alpha_composite(grade_units(render_board(board_frame(f, keep_all=(beat == 'p2')), CONS), f, keep_all=(beat == 'p2'), dim_ids=dim_ids))
    L = L2()
    O.hp_ring(L, f['hp'], f['pv']['hp_after'], f['maxhp'])
    bezel9(L, f['schedule'])
    O.sector_digits(L)
    occ = {(u['dep'], q) for u in f['units'] for q in sectors(u)}
    for d in range(3):
        for q in range(6):
            if (d, q) not in occ:
                O.cell_border(L, d, q, alpha=70)
    wave_arcs10(L, arcs_data(f))
    ward_arc(L, f)
    tower_slice_bars(L, f)
    if beat in ('p1', 'nowords', 'p2b'):
        threat_trim(L, f)
    dim = None
    if beat == 'p2b':
        hv = J['hover']
        Ld = L2()
        draw_units(Ld, f, skip={hv['id']})
        dim = Ld.done()
        dim.putalpha(dim.split()[3].point(lambda v: int(v * 0.36)))
        Lh = L2()
        draw_units(Lh, f, only={hv['id']})
        hu_ = [u for u in f['units'] if u['id'] == hv['id']][0]
        cell_outline(Lh, hu_, col=YEL, w=5)
        L.im.alpha_composite(Lh.im)
    else:
        draw_units(L, f)
    adjuster_body(L, f['adj'])
    if beat in ('p1', 'nowords'):
        gun_tracers10(L, f)
    if beat != 'p2b':
        landing_arcs(L, f)
    else:
        landing_arcs(L, f, only={J['hover']['id']})
    ring_tags(L, f)
    nudge_ghost(L)
    if beat in ('p2', 'p3'):
        twist_badge(L, f)
        refund_marks(L, f)
    if beat == 'p2':
        for tr in J['trigs']:
            trigger_paths(L, f, dict(tr, entries=[e for e in tr['entries'] if e[0] != 'refund']))
    if beat == 'p2b':
        hover_path(L, f)
    if beat == 'p3':
        for e_ in f['log']:
            if e_[0] == 'fire' and e_[3] is not None:
                s_, dep_ = e_[1], e_[5]
                L.line([ppx(C, RS['s1'] + 3, 60 * s_ + 3), pt(CB.ring_geom(dep_)[0] + 20, 60 * s_, 6)], CYAN + (170,), 2.4, dash=(5, 6))
    header(L, f)
    y = bill_box(L, f, 66, pencil=(beat == 'p2'), plan_tag=('BEST LINE' if beat in ('p2', 'p3') else None), twist_pay=(J['twist_payoff'] if beat in ('p2', 'p3') else None))
    if beat == 'p2':
        y = option_chip(L, y, 'TRIGGER ONLY', J['meta']['lines']['trigger'][0], J['meta']['lines']['trigger'][1], J['f2t']['pv']['eq'], refund=J['f2t']['refunds'] > 0)
        y = option_chip(L, y, 'BRACE + SOAK ONLY', J['meta']['lines']['brace'][0], J['meta']['lines']['brace'][1], J['f2b']['pv']['eq'])
        y = option_chip(L, y, 'BEST: ALL THREE', J['meta']['hero'], J['meta']['hero_end'], f['pv']['eq'], sel=True, refund=f['refunds'] > 0)
    elif beat == 'p3':
        y = chain_strip(L, f, y)
    y = stars_row(L, f, y + 2)
    y = ram_trace(L, f, y)
    base = bg
    if dim is not None:
        base.alpha_composite(dim)
    base.alpha_composite(L.done())
    played = [a[0] for a in f['played']]
    hand = list(f['hand'])
    if beat == 'p3':
        hand = list(f1['hand'])
        for c_ in played:
            hand.remove(c_)
    hover_i = hand.index('Trigger') if beat == 'p2' else None
    CH.hand(base, hand, x0=1000, hover=hover_i, played=played if beat == 'p3' else (), cy0=948)
    L3 = L2()
    stickers(base, L3)
    if beat == 'p2b':
        hover_tag(L3, f)
    base.alpha_composite(L3.done())
    draw_asserts(beat, f)
    name = {'p1': 'p1_decide', 'p2': 'p2_preview', 'p2b': 'p2b_hover', 'p3': 'p3_resolve', 'nowords': 'p1_nowords'}[beat]
    base.convert('RGB').save(OUT + name + '.png')
    print('saved', name, flush=True)


def hover_path(L, f):
    hv = J['hover']
    path = hv['path']
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
    pencil_line(L, pts, YEL, 8)
    x, y = pts[-1]
    a = math.atan2(y - pts[-3][1], x - pts[-3][0])
    L.poly([(x + 4 * math.cos(a), y + 4 * math.sin(a)), (x - 22 * math.cos(a) + 13 * math.sin(a), y - 22 * math.sin(a) - 13 * math.cos(a)),
            (x - 22 * math.cos(a) - 13 * math.sin(a), y - 22 * math.sin(a) + 13 * math.cos(a))], fill=YEL, outline=INK, w=2)
    for (sec, sl, hit, tohp) in hv['fate']['hits']:
        L.line(L.arc_pts(C, RS['s1'] + 2, 60 * sec - 25, 60 * sec + 25), YEL, 6)


def hover_tag(L, f):
    hv = J['hover']
    fz = hv['fate']
    sl = ' + '.join('%s %d' % (h[1], h[3]) for h in fz['hits'])
    txt = '%s%s x%d  HP %d/%d  hit %d now (+%d grown)  lands in %d: %d per slice' % (hv['kind'].upper(), ' ARMOR' if hv['df'] == 'armor' else '', hv['w'], hv['hp'], hv['mx'], hv['hit'], hv['grown'], fz['k'], fz['hits'][0][2])
    txt2 = 'after our guns it costs you %d HP: %s' % (sum(h[3] for h in fz['hits']), sl)
    w_ = max(L.tw(txt, 18, 'plex'), L.tw(txt2, 18, 'plex')) + 34
    x0, y0 = 20, 22
    terminal(L, (x0, y0, x0 + w_, y0 + 70), col=YEL)
    L.text((x0 + 16, y0 + 22), txt, 18, 'plex', fill=WHITE, anchor='lm')
    L.text((x0 + 16, y0 + 50), txt2, 18, 'plex', fill=YEL, anchor='lm')


if __name__ == '__main__':
    beats = ['p1', 'p2', 'p2b', 'p3', 'nowords'] if sys.argv[1] == 'all' else [sys.argv[1]]
    for b in beats:
        make(b)
    if sys.argv[1] == 'all':
        open(ROOT + 'assert_draw_log.txt', 'w').write(chr(10).join(LOGD) + chr(10))
        print('draw asserts', len(LOGD))
