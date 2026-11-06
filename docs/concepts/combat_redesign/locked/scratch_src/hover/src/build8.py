"""Build the E8 Shifting Waves plates, round 2 (converged look, display A + H slices). python build8.py <p1|p1b|p2|p2b|p3|nowords|all>
Everything numeric comes from state_e8.json / state_e8b.json (dump8.py: the E8 sim, asserted). HUD quantities are tally segments (groups of 5, a gap between groups);
no digits on units or slices; digits only in the title, the W tabs, the ring labels, the sector digits and the p2b hover tag."""
import sys, json, math
sys.dont_write_bytecode = True
from e8lib import *
from cv_board import render_board
import cv_chrome as CH

OUT = 'D:/rc_tmp/combat_critic/plates/waves_e8/'
J = json.load(open(ROOT + 'state_e8.json'))
JB = json.load(open(ROOT + 'state_e8b.json'))
S0 = json.load(open(ROOT + 'state_cv.json'))
CONS_E8 = S0['consts']
X0, X1 = 1066, 1904
CARDS = {
    'Nudge': dict(cost=1, fam='TOWER', g='PI_SPIN_CW', txt='Turn the tower 1', x='1', nm='NUDGE'),
    'Spin2': dict(cost=1, fam='TOWER', g='PI_SPIN_CW', txt='Turn the tower 2', x='2', nm='SPIN 2'),
    'Spin3': dict(cost=1, fam='TOWER', g='PI_SPIN_CW', txt='Turn the tower 3', x='3', nm='SPIN 3'),
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
SEGC = {'hp': GREEN, 'lose': (255, 120, 110), 'through': RED, 'absorb': CYAN, 'slice': GREEN, 'raw': RED, 'yel': YEL, 'cyan': CYAN, 'rider': (255, 150, 40),
        'gold': GOLD, 'viol': (160, 60, 255)}


# ----------------------------------------------------------------------------- HUD: tally segments (groups of 5 with a gap)
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


def label(L, x, y, s, col=TXT_MID, px=16, alpha=255):
    L.text((x, y), s, px, 'mono', fill=tuple(col) + (alpha,), anchor='lm')
    return L.tw(s, px, 'mono')


def op(L, x, y, s, alpha=255):
    L.text((x, y + 1), s, 28, 'anton', fill=(242, 246, 255, alpha), anchor='mm')


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


def term(L, box, col=CYAN):
    terminal(L, box, col=col)


def header(L, f):
    term(L, (X0, 12, X1, 58))
    L.text((X0 + 18, 35), 'TURN %d  |  SHIFTING WAVES' % f['turn'], 30, 'anton', fill=WHITE, anchor='lm')
    L.text((X0 + 440, 35), 'WAVES %d LEFT' % f['waves_left'], 24, 'anton', fill=ORANGE, anchor='lm')
    x = X0 + 650
    for i in range(6):
        lit = i >= 6 - f['waves_left']
        col = RED if i == 5 else ORANGE
        L.rect([x + i * 20, 25, x + i * 20 + 14, 45], fill=col if lit else (20, 20, 30), outline=col, w=2, r=3)
    L.ellipse([X1 - 40, 19, X1 - 8, 51], fill=(8, 10, 18, 250), outline=YEL, w=2.6)       # "?" legend tab (closed)
    L.text((X1 - 24, 36), '?', 24, 'anton', fill=YEL)


def bill_box(L, f, y, pencil=False, plan_tag=None):
    """ONE hero bill: HP segments, the result tallies, the equation, and a ghost NEXT row. All tallies are groups of 5."""
    pv = f['pv']
    eq = pv['eq']
    h = 164
    L.rect([X0 - 4, y, X1, y + h], fill=(8, 12, 22, 218), outline=WHITE, w=3, r=10)
    label(L, X0 + 10, y + 17, 'YOU', CRT_TXT, 16)
    after = pv['hp_after']
    x = X0 + 62
    for i in range(f['maxhp']):
        kind = 'hp' if i < after else 'lose'
        if i >= f['hp']:
            seg(L, x + i * 18 + (i // 5) * 10, y + 40, 'hp', 14, 22, lit=False)
        else:
            seg(L, x + i * 18 + (i // 5) * 10, y + 40, kind, 14, 22)
    xe = x + f['maxhp'] * 18 + 20
    if pencil:
        L.line([(X0 + 6, y + 60), (xe - 10, y + 62)], (6, 3, 8), 9)
        L.line([(X0 + 6, y + 60), (xe - 10, y + 62)], YEL, 6)
    cx = xe + 24
    w1 = label(L, cx, y + 17, 'THROUGH', TXT_MID, 16)
    if pv['taken']:
        e1 = seg_run(L, cx, y + 40, 'through', pv['taken'], 13, 22, pitch=16)
    else:
        L.glyph('X_HP', 22, (cx + 12, y + 40), GREEN)
        e1 = cx + 30
    cx2 = max(e1, cx + w1) + 24
    w2 = label(L, cx2, y + 17, 'ABSORBED', TXT_MID, 16)
    e2 = seg_run(L, cx2, y + 40, 'absorb', pv['absorbed'], 13, 22, pitch=16)
    cx3 = max(e2, cx2 + w2) + 24
    label(L, cx3, y + 17, 'SLICES', TXT_MID, 16)
    seg_run(L, cx3, y + 40, 'slice', pv['slost'], 13, 22, pitch=16)
    # equation
    yy = y + 99
    terminal(L, (X0 + 2, y + 64, X1 - 4, y + 120))
    groups = [('RAW', 'raw', eq['raw0'], None)]
    if eq['triggered']:
        groups.append(('TRIGGERED', 'yel', eq['triggered'], '-'))
    if eq['tower_from_trigger']:
        groups.append(('TRIGGER LANDS', 'raw', eq['tower_from_trigger'], '+'))
    groups.append(('SHOT', 'cyan', eq['shot_down'], '-'))
    groups.append(('RIDER', 'rider', eq['rider'], '-'))
    x = X0 + 14
    for name, kind, n, o in groups:
        if o:
            op(L, x + 6, yy, o)
            x += 22
        lw = label(L, x, y + 76, name, TXT_MID, 16)
        if n:
            e = seg_run(L, x, yy, kind, n, 9, 18, pitch=12)
        else:
            seg(L, x, yy, 'raw', 9, 18, lit=False)
            e = x + 14
        x = max(e, x + lw) + 6
    op(L, x + 6, yy, '=')
    x += 24
    lw = label(L, x, y + 76, 'LANDS', TXT_MID, 16)
    e = seg_run(L, x, yy, 'raw', eq['lands'], 9, 18, pitch=12)
    x = max(e, x + lw) + 4
    op(L, x + 6, yy, '=')
    x += 24
    # LANDS split in two colours: through (red) + absorbed (cyan)
    lw = label(L, x, y + 76, 'THROUGH', TXT_MID, 16)
    if eq['through']:
        e = seg_run(L, x, yy, 'through', eq['through'], 9, 18, pitch=12)
    else:
        L.text((x + 5, yy + 1), '0', 18, 'mono', fill=GREEN, anchor='mm')
        e = x + 14
    x = max(e, x + lw) + 4
    op(L, x + 6, yy, '+')
    x += 22
    label(L, x, y + 76, 'ABSORBED', TXT_MID, 16)
    seg_run(L, x, yy, 'absorb', eq['absorbed'], 9, 18, pitch=12)
    # ghost NEXT row
    nx = f['next']
    yg = y + 143
    al = 120
    label(L, X0 + 12, yg, 'NEXT', TXT_MID, 16, al)
    x = X0 + 76
    x = (seg_run(L, x, yg, 'through', nx['taken'], 11, 16, al) if nx['taken'] else x + 4) + 26
    x = (seg_run(L, x, yg, 'absorb', nx['absorbed'], 11, 16, al) if nx['absorbed'] else x) + 26
    seg_run(L, x, yg, 'slice', nx['slost'], 11, 16, al)
    if plan_tag:
        L.text((X1 - 16, y + 17), plan_tag, 16, 'mono', fill=YEL, anchor='rm')
    return y + h + 6


def option_chip(L, y, name, lands, through, sel=False, line='solid'):
    """one total-lands bar per option: the bar length = pips that land; red = costs you HP, cyan = absorbed"""
    h = 36
    L.rect([X0 - 4, y, X1, y + h], fill=(6, 10, 20, 235), outline=YEL if sel else (110, 120, 140), w=3 if sel else 2, r=8)
    # line-style sample = the key to the path drawn on the board
    if line == 'solid':
        L.line([(X0 + 10, y + 18), (X0 + 44, y + 18)], (6, 3, 8), 10)
        L.line([(X0 + 10, y + 18), (X0 + 44, y + 18)], YEL, 6)
    else:
        L.line([(X0 + 10, y + 18), (X0 + 44, y + 18)], YEL, 5, dash=(8, 5))
    label(L, X0 + 54, y + 18, name, YEL if sel else WHITE, 16)
    x = X0 + 250
    x = seg_run(L, x, y + 18, 'through', through, 11, 18) if through else x
    seg_run(L, x + (4 if through else 0), y + 18, 'absorb', lands - through, 11, 18) if lands - through else None
    return y + h + 4


def stars_row(L, f, y):
    L.rect([X0 - 4, y, X1, y + 44], fill=(8, 12, 22, 215), outline=(110, 120, 140), w=2, r=8)
    star(L, X0 + 20, y + 22, 'open', 14)
    label(L, X0 + 42, y + 22, 'WIN', GOLD, 16)
    names = {'card': 'TRIGGER HITS', 'daemon': 'KILL ADJUSTER', 'heat': 'TRACE LOW', 'scrap': 'SLICES KEPT'}
    cons = f['consts']
    for i, ch in enumerate(f['challenges']):
        x = X0 + 130 + i * 258
        star(L, x, y + 22, ch['state'], 13)
        lw = label(L, x + 22, y + 22, names[ch['name']], WHITE, 16)
        xx = x + 22 + lw + 10
        if ch['name'] == 'card':
            n = min(f['interf'], cons['STAR_CARD'])
            seg_run(L, xx, y + 22, 'yel', n, 6, 12, pitch=8) if n else None
        elif ch['name'] == 'daemon':
            seg_run(L, xx, y + 22, 'gold', f['adj']['hp'], 6, 12, pitch=8)
        elif ch['name'] == 'heat':
            seg_run(L, xx, y + 22, 'viol', min(f['trace'], 5), 6, 12, pitch=8) if f['trace'] else None
    return y + 48


def ram_trace(L, f, y):
    term(L, (X0 - 4, y, X1, y + 54))
    label(L, X0 + 12, y + 27, 'RAM', CRT_TXT, 16)
    for i in range(f['ram_max']):
        bx = X0 + 58 + i * 34
        on = i < f['ram']
        L.rect([bx, y + 14, bx + 28, y + 40], fill=CYAN if on else (20, 34, 52), outline=CYAN, w=2, r=4)
    label(L, X0 + 230, y + 27, 'TRACE', CRT_TXT, 16)
    for i in range(f['tcap']):
        bx = X0 + 292 + i * 32
        on = i < f['trace']
        L.rect([bx, y + 14, bx + 26, y + 40], fill=(160, 60, 255) if on else (28, 20, 44), outline=(160, 60, 255), w=2, r=4)
        if i == f['tcap'] - 1:
            for q in range(0, 26, 7):
                L.line([(bx + q, y + 40), (bx + q + 8, y + 14)], (255, 255, 255, 110), 2)
    label(L, X0 + 520, y + 27, 'ENDS = HEAT', AMBER, 16)
    seg_run(L, X0 + 640, y + 27, 'gold', f['pv']['trace_after'], 11, 18) if f['pv']['trace_after'] else None
    return y + 58


def stickers(base, L):
    st = vinyl('CELL-9 // BREAKER', 34, PINK, tilt=2)
    shadow_paste(base, st, (22, 968), 0.5, 8, (5, 9))
    se = vinyl('SEND IT', 62, PINK, tilt=-3, pad=(24, 6))
    shadow_paste(base, se, (1655, 968))
    terminal(L, (1740, 922, 1890, 960))
    L.text((1815, 941), 'UNDO [Z]', 18, 'mono', fill=CRT_TXT)
    L.text((1780, 1070), '> turn_resolve.exe', 16, 'mono', fill=TXT_MID)


def chain_strip(L, f, y):
    steps = f['chain']
    h = 29
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
            elif n:
                x = seg_run(L, x, cy, kind, n, 10, 16) + 10
        if i < len(steps) - 1:
            L.line([(X0 + 17, cy + 12), (X0 + 17, cy + h - 12)], WHITE + (110,), 2)
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
        gone = u['consumed'] or u['trigdead']
        if gone:
            cell_outline(L, u, col=YEL if u['consumed'] else RED, w=3)
            ri, ro = CB.ring_geom(u['dep'])
            L.poly(L.band(C, ri + 4, ro - 4, span(u)[0] + 3, span(u)[1] - 3), fill=(6, 3, 8, 105))
            token(L, u, dead=True)
            continue
        lit_cell(L, u)
        cell_outline(L, u)
        fz = u['fate']
        dots = fz['k'] if (fz['kind'] != 'waits' and fz['k']) else (u['dep'] if fz['kind'] == 'waits' else 0)
        token(L, u, dots=dots)
        hp_row(L, u, u['hp'], u['mx'], lose=u['lose'][1], shield=u['sh'], shmx=u['shmx'])
        if u['df'] == 'armor':
            armor_cap(L, u)
        if u['df'] == 'sealed':
            sealed_marks(L, u)
        chevrons(L, u, u['hit'])
        if u['warded']:
            warded_mark(L, u)
        if fz['kind'] == 'dies':
            dead_x(L, u)


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
    """proposal (flagged): two dashed ghost chevrons beside the needle = 'turn the tower 1 either way' (a card, not a button)"""
    for sg in (-1, 1):
        x, y = ppx(C, RS['hp1'] + 12, sg * 13)
        L.poly([(x - 8 * sg, y - 8), (x + 8 * sg, y), (x - 8 * sg, y + 8)], fill=(8, 20, 30, 120), outline=CYAN, w=2.2)


def make(beat):
    NOW['words'] = beat != 'nowords'
    src = JB if beat == 'p1b' else J
    key = {'p1': 'f1', 'p1b': 'f1', 'nowords': 'f1', 'p2': 'f2a', 'p2b': 'f1', 'p3': 'f3'}[beat]
    f = src[key]
    f1 = src['f1']
    bg = backdrop()
    bg.alpha_composite(render_board(board_frame(f, keep_all=(beat == 'p2')), CONS_E8))
    L = L2()
    O.hp_ring(L, f['hp'], f['pv']['hp_after'], f['maxhp'])
    O.bezel(L, f['schedule'], caption=False)
    O.sector_digits(L)
    occ = {(u['dep'], q) for u in f['units'] for q in sectors(u)}
    for d in range(3):
        for q in range(6):
            if (d, q) not in occ:
                O.cell_border(L, d, q, alpha=70)
    wave_arcs(L, arcs_data(f))
    ward_arc(L, f)
    tower_slice_bars(L, f)
    if beat in ('p1', 'p1b', 'nowords', 'p2b'):
        threat_trim(L, f)
    if beat in ('p1', 'p1b', 'nowords'):
        gun_tracers(L, f)
    dim = None
    if beat == 'p2b':
        hv = J['hover']
        Ld = L2()
        draw_units(Ld, f, skip={hv['id']})
        dim = Ld.done()
        dim.putalpha(dim.split()[3].point(lambda v: int(v * 0.36)))
        Lh = L2()
        draw_units(Lh, f, only={hv['id']})
        L.im.alpha_composite(Lh.im)
    else:
        draw_units(L, f)
    adjuster_satellite(L, f['adj'])
    ring_tags(L, f)
    nudge_ghost(L)
    if beat == 'p2':
        trigger_paths(L, f, J['trig_hero'])
        trigger_paths(L, f, J['trig_alt'], dashed=True)
        for u in f['units']:
            if u['consumed'] and NOW['words']:
                x, y = ppx(C, rmid(u['dep']), 60 * (u['s'] + (u['w'] - 1) / 2))
                pencil_x(L, x, y, YEL, 14)
                L.rect([x - 52, y + 18, x + 52, y + 42], fill=(8, 10, 18, 245), outline=YEL, w=2, r=5)
                L.text((x, y + 30), 'CONSUMED', 16, 'mono', fill=YEL)
        angs = {(1, -1): 205, (1, 1): 232, (2, -1): 259, (2, 1): 286}
        for o in J['twist']['options']:
            twist_chip(L, angs[(o['ring'], o['sgn'])], RS['bz0'] + 17, o['pips'], o['ring'], o['sgn'], col=YEL)
    if beat == 'p2b':
        hover_path(L, f)
    if beat == 'p3':
        fx_resolve(L, f)
    # ---- HUD (compact: title, ONE bill box, [options | chain], stars, RAM + TRACE)
    header(L, f)
    y = bill_box(L, f, 66, pencil=(beat == 'p2'), plan_tag=('PLAN: TRIGGER' if beat == 'p2' else ('PLAN: TWIST + TRIGGER + NUDGE' if beat == 'p3' else None)))
    if beat == 'p2':
        y = option_chip(L, y, 'NO TRIGGER', J['f1']['pv']['eq']['lands'], J['f1']['pv']['eq']['through'], line='solid') if False else y
        o1 = J['f1']['pv']['eq']
        o2 = J['f2a']['pv']['eq']
        o3 = J['f2alt']['pv']['eq']
        y = option_chip(L, y, 'NO TRIGGER', o1['lands'], o1['through'], line='none')
        y = option_chip(L, y, 'TRIGGER WORM', o2['lands'], o2['through'], sel=True, line='solid')
        y = option_chip(L, y, 'TRIGGER PAYLOAD', o3['lands'], o3['through'], line='dashed')
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
    name = {'p1': 'p1_decide', 'p1b': 'p1b_decide', 'p2': 'p2_preview', 'p2b': 'p2b_hover', 'p3': 'p3_resolve', 'nowords': 'p1_nowords'}[beat]
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
    txt = '%s%s x%d  HP %d/%d  hit %d (+%d grown)  lands in %d: %d chevrons per slice' % (hv['kind'].upper(), ' ARMOR' if hv['df'] == 'armor' else '', hv['w'], hv['hp'], hv['mx'], hv['hit'], hv['grown'], fz['k'], hv['hit'])
    txt2 = 'after our guns it costs you %d HP: %s' % (sum(h[3] for h in fz['hits']), sl)
    w_ = max(L.tw(txt, 18, 'plex'), L.tw(txt2, 18, 'plex')) + 34
    x0, y0 = 20, 890
    terminal(L, (x0, y0, x0 + w_, y0 + 70), col=YEL)
    L.text((x0 + 16, y0 + 22), txt, 18, 'plex', fill=WHITE, anchor='lm')
    L.text((x0 + 16, y0 + 50), txt2, 18, 'plex', fill=YEL, anchor='lm')


def fx_resolve(L, f):
    """p3 board marks, no digits: cyan streaks for the guns' shots (the bible's bit shards would print 0/1 digits, which read as leaked labels here)"""
    for e in f['log']:
        if e[0] == 'fire' and e[3] is not None:
            s, dep = e[1], e[5]
            L.line([ppx(C, RS['s1'] + 3, 60 * s + 3), pt(CB.ring_geom(dep)[0] + 20, 60 * s, 6)], CYAN + (170,), 2.4, dash=(5, 6))


if __name__ == '__main__':
    beats = ['p1', 'p1b', 'p2', 'p2b', 'p3', 'nowords'] if sys.argv[1] == 'all' else [sys.argv[1]]
    for b in beats:
        make(b)
