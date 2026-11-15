"""insp_v3set: the B-086 state set re-rendered in Deface v3, the reference set for build (designer A-119 rulings).

    python insp_v3set.py [board play forecast resolve wallseal win sheet]      (default: all)

Rulings applied: (1) status = sticker, value = grease pencil (stickers carry no number); (2) pencil may carry forecast numbers.
Words: NAME_MAP E (program, LOADED, RAM, QUEUE / SPENT / DELETED, COMMIT, ROLLBACK [Z], SCHEDULE; pointer and health unchanged).
States: tk_states BOARD / PLAY / FORECAST / RESOLVE / WALLSEAL / WIN.
Reuses insp_deface3 (stickers, wax, wheel) and insp_deface3b (mini stickers, bomb) unchanged; corp board from insp_render.
"""
import copy, math, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/takeover/inspiration')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import insp_deface3 as D3
import insp_deface3b as D3b
from insp_deface3 import (Wax, PEN_Y, PEN_R, SL, IR, TR, S, text, Layer, comp, INK, PAPER, PINK, HARM, CYAN, TEXT_HI, TEXT_MID,
                          ANTON, MONO, ACTS, CX, CY, W, H, SS, F_all, base_image, glass, stick, sticker, liner_outline, POS,
                          pen_outcomes, legal_marks, qpts, polar, pen_badge)
from tk_states import STATES, GAIN as S_GAIN, HARM as S_HARM, HI as S_HI, PLAN as S_PLAN, MID as S_MID, SCHED as S_SCHED

OUT = 'D:/rc_art/art-pass/docs/concepts/takeover_board/v3/'
GAIN, GLASS_ = TR.GAIN, TR.GLASS

# ------------------------------------------------------------------ words (NAME_MAP E) on the shared corp board
WORDS = {'CORP PLAN': 'SCHEDULE'}
_text = TR.text
IR.text = lambda d, xy, s, *a, **k: _text(d, xy, WORDS.get(s, s), *a, **k)
IR.forecast_panel = lambda *a, **k: None          # the HUD panel is drawn here (panel()), so SEND IT can sit right under it
IR.end_turn_btn = lambda *a, **k: None

# status stickers: fixed words, no numbers (ruling 1); colours = the action family that puts them there
D3b.STAT.update({'BLOCK': ((110, 170, 255), (52, 104, 220)), 'VIRUS': ((150, 236, 120), (80, 178, 70)),
                 'WALL': ((255, 92, 186), (226, 30, 140)), 'SHROUD': ((120, 220, 245), (40, 160, 200)),
                 'TRACED': ((255, 196, 96), (230, 140, 30)), 'RETAKEN': ((255, 98, 84), (220, 40, 40))})
STATUS_WORD = {'G': 'BLOCK', 'V': 'VIRUS'}


def act(aid):
    return [x for x in ACTS if x['id'] == aid][0]


def seg_am(i, st):
    return TR.seg_angles(i, st['rot'])[2]


# =============================================================================================== left flank
def health(img, F, hud):
    L = Layer(); d = L.d
    x0, x1, y0, h = 24, 516, 18, 86
    tape = [(S(x0 + 4), S(y0)), (S(x1 - 4), S(y0 + 4)), (S(x1 - 8), S(y0 + h)), (S(x0), S(y0 + h - 4))]
    IR.poly_shadow(d, tape, 4, 5)
    d.polygon(tape, fill=PAPER + (255,), outline=INK + (255,), width=S(3))
    text(d, (x0 + 18, y0 + 26), hud['runner'], F['a26'], INK + (255,), anchor='lm')
    hp, hpm = hud['hp']; lose = hud.get('hp_loss', 0)
    s_ = '%d/%d' % (hp, hpm) if not lose else '%d \u2192 %d' % (hp, hp - lose)
    text(d, (x1 - 20, y0 + 26), s_, F['a28'], (INK if not lose else (200, 24, 30)) + (255,), anchor='rm')
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
    if hud.get('hp_n'):
        bb = d.textbbox((S(x1 - 20), S(y0 + 26)), s_, font=F['a28'], anchor='rm')
        d.rectangle([bb[0] - S(6), bb[1] - S(6), bb[2] + S(6), bb[3] + S(6)], outline=CYAN + (255,), width=S(3))
    comp(img, L)


def ram(img, F, hud, cost=0):
    L = Layer(); d = L.d
    x0, y0, x1, y1 = 24, 112, 300, 152
    glass(d, (x0, y0, x1, y1))
    ym = (y0 + y1) / 2
    text(d, (x0 + 16, ym), 'RAM', F['m20'], TEXT_MID + (255,), anchor='lm')
    en, emax = hud['energy']
    for k in range(emax):
        x = x0 + 72 + k * 34
        box = [S(x), S(ym - 11), S(x + 26), S(ym + 11)]
        if k < en - cost:
            d.rectangle(box, fill=(26, 143, 184, 255), outline=CYAN + (255,), width=S(2))
        elif k < en:
            d.rectangle(box, fill=GLASS_ + (255,), outline=CYAN + (255,), width=S(2))
            for t in range(0, 4):
                d.line([(S(x + t * 7), S(ym + 11)), (S(x + t * 7 + 8), S(ym - 11))], fill=HARM + (255,), width=S(2))
        else:
            d.rectangle(box, outline=(60, 110, 130, 255), width=S(2))
    text(d, (x0 + 186, ym), '%d/%d' % (en, emax) if not cost else '%d \u2192 %d' % (en, en - cost), F['a26'],
         (TEXT_HI if not cost else (255, 120, 110)) + (255,), anchor='lm')
    comp(img, L)


def runner_status(img, hud, py):
    """the runner's own statuses (SHROUD 1, TRACED) as stickers by the health tape; the count in pencil"""
    x = 350
    for word, side in sorted(hud.get('status', []), key=lambda w: len(w[0].split())):     # count-less first, so a count has room
        name = word.split()[0]
        stick(img, D3b.mini_sticker(name), x, 132, -4 if side == 'buff' else 5)
        if len(word.split()) > 1:
            py.text('x' + word.split()[1], x + 70, 130, 32, angle=-6)
        x += 118


def flank_left(img, F, st, held=None, cost=0, paid=0, skip=(), py_extra=None):
    hud = st['hud']
    health(img, F, hud)
    ram(img, F, dict(hud, energy=(hud['energy'][0] - paid, hud['energy'][1])), cost=cost)
    py = Wax(PEN_Y, 71); pr = Wax(PEN_R, 72)
    runner_status(img, hud, py)
    names = [c['nm'] for c in st.get('hand', [])]
    loaded = 0
    for aid in ['WORM', 'NUDGE', 'GUARD', 'BREACH', 'TIMEBOMB']:
        a = act(aid)
        if a['nm'] not in names:
            continue
        x, y, ang = POS[aid]
        if aid == held or aid in skip:
            liner_outline(img, a, x, y, ang)
            continue
        loaded += 1
        stick(img, sticker(a, grey=bool(a.get('why'))), x, y, ang)
    if 'TIME BOMB' in names:
        pr.text('needs 4 RAM', 392, 672, 32, angle=-8)
        pr.arrow([(320, 694), (296, 700), (282, 694)], width=5, head=14)
    # piles (terminal): LOADED / QUEUE / SPENT / DELETED, ROLLBACK [Z]
    L = Layer(); d = L.d
    x0, y0, x1, y1 = 24, 824, 516, 872
    glass(d, (x0, y0, x1, y1))
    q, sp = hud['piles']
    x = x0 + 16
    for wd, n in (('LOADED', loaded + (1 if held else 0) - (0 if not skip else 0)), ('QUEUE', q), ('SPENT', sp + len(skip)), ('DELETED', 0)):
        text(d, (x, (y0 + y1) / 2), wd, F['m18'], TEXT_MID + (255,), anchor='lm')
        x += IR.tw(d, wd, F['m18']) + 8
        text(d, (x, (y0 + y1) / 2), str(n), F['a26'], TEXT_HI + (255,), anchor='lm')
        x += 34
    ux0, uy0 = 24, 892
    if not st.get('hand'):                # the fight is over: no rollback
        comp(img, L); py.ink_ss(img); pr.ink_ss(img); return
    d.rectangle([S(ux0), S(uy0), S(ux0 + 220), S(uy0 + 44)], fill=GLASS_ + (230,), outline=CYAN + (255,), width=S(2))
    text(d, (ux0 + 14, uy0 + 22), 'ROLLBACK', F['a24'], TEXT_HI + (255,), anchor='lm')
    text(d, (ux0 + 166, uy0 + 23), '[Z]', F['m18'], TEXT_MID + (255,), anchor='lm')
    comp(img, L)
    py.ink_ss(img); pr.ink_ss(img)


# =============================================================================================== right flank
def panel(img, F, st, lines=(), hint=None, totals=True):
    """the system-layer HUD panel: OWNED (+ after), the COMMIT forecast totals (designer ruling), then lines, then a hint.
    returns its bottom y"""
    x0, y0, x1 = 1404, 620, 1898
    h = 18 + (118 if totals else 0) + 34 * len(lines) + 28 * len(hint or []) + 14
    L = Layer(); d = L.d
    glass(d, (x0, y0, x1, y0 + h))
    y = y0
    hud = st['hud']
    if totals:
        owned = sum(1 for g in st['segs'] if g['owner'] == 'us')
        text(d, (x0 + 18, y0 + 24), 'OWNED', F['m20'], TEXT_MID + (255,), anchor='lm')
        text(d, (x0 + 18, y0 + 62), '%d/12' % owned, F['num'], TEXT_HI + (255,), anchor='lm')
        oa = hud.get('owned_after')
        if oa is not None:
            text(d, (x0 + 128, y0 + 64), '\u2192 %d' % oa, F['mid'], (GAIN if oa >= owned else HARM) + (255,), anchor='lm')
        tot = hud.get('totals')
        if tot:
            text(d, (x0 + 230, y0 + 24), tot[0], F['m20'], TEXT_MID + (255,), anchor='lm')
            IR.spans(d, x0 + 230, y0 + 62, tot[1], F['a28'], gap=16)
            if tot[2]:
                text(d, (x0 + 230, y0 + 100), tot[2][0], F['a28'], tot[2][1] + (255,), anchor='lm')
        y = y0 + 124
        if lines or hint:
            d.line([(S(x0 + 14), S(y)), (S(x1 - 14), S(y))], fill=(40, 90, 110, 255), width=S(1.5))
    for k, line in enumerate(lines):
        x = x0 + 18
        f = F['a26'] if k == 0 else F['a24']
        for s_, col in line:
            text(d, (x, y + 22 + 34 * k), s_, f, col + (255,), anchor='lm')
            x += IR.tw(d, s_, f) + 10
    y += 34 * len(lines)
    for k, ln in enumerate(hint or []):
        text(d, (x0 + 18, y + 22 + 28 * k), ln, F['m18'], TEXT_MID + (255,), anchor='lm')
    comp(img, L)
    return y0 + h


_STK = {}


def verb_sticker(word, top, bot, size=72):
    if word not in _STK:
        art = SL.lettering([word], size, [('grad', top, bot)], key_w=5, extrude=7, seed=3, jitter=3)
        _STK[word] = SL.build_sticker(art, border=10, gloss_k=0.22)
    return _STK[word]


def commit_verb(img, F, y_top, word='SEND IT', system='COMMIT'):
    """the pink verb sticker over the washed-out system word (bible 1.3), just under the HUD panel"""
    cy = min(max(y_top + 92, 860), 1000)
    k = 0.9 if y_top < 880 else 0.74                  # a tall panel (hover steps): a smaller verb so both fit
    L = Layer(); d = L.d
    if system:
        text(d, (1770, cy - 4), system, TR.font(MONO, 84), (120, 200, 230, 95), anchor='mm')
        text(d, (1770, cy + (74 if k > 0.8 else 62)), 'END TURN [SPACE]', F['m18'], (120, 200, 230, 170), anchor='mm')
    comp(img, L)
    stick(img, verb_sticker(word, (255, 110, 196), (222, 24, 136)), 1772, cy, 4, scale=k)


def flank_right(img, F, st, lines=(), hint=None, totals=True, verb='SEND IT', system='COMMIT'):
    IR.df_right(img, F, st, False)
    yb = panel(img, F, st, lines, hint, totals)
    commit_verb(img, F, yb, verb, system)


# =============================================================================================== wheel + statuses
def wheel(img, F, st, hover=None):
    s2 = copy.deepcopy(st)
    for g in s2['segs']:
        g['st'] = [x for x in g.get('st', []) if x[1] != 'runner']     # yours become stickers
    walls, seals = s2.pop('walls', []), s2.pop('seals', [])
    D3.draw_wheel(img, s2, F)
    s3 = dict(s2, walls=[w for w in walls if w[1] == 'corp'], seals=[x for x in seals if x[1] == 'corp'])
    TR.draw_walls_seals(img, s3, F['seg_small'])                      # the corp's: enamel (unchanged)


def wheel_stickers(img, st, py, skip=()):
    """your statuses, walls and seals as stickers; their counts in pencil beside them (ruling 1)"""
    for i, g in enumerate(st['segs']):
        if i in skip:
            continue
        for word, side in g.get('st', []):
            if side != 'runner':
                continue
            am = seg_am(i, st)
            da = 0.16 if math.sin(am) > 0 else -0.17
            x, y = polar(TR.R_OUT - 30, am + da)
            stick(img, D3b.mini_sticker(STATUS_WORD[word[0]]), x, y, -5 if da < 0 else 5)
            vx, vy = polar(TR.R_OUT - 78, am + da * 1.15)
            py.text('x' + word[1:], vx, vy, 32, angle=-6)
    for i, side in st.get('seals', []):
        if side != 'runner':
            continue
        am = seg_am(i, st)
        da = 0.16                                          # the corner away from the boundary (where a WALL sticker may sit)
        x, y = polar(TR.R_OUT - 30, am + da)
        stick(img, D3b.mini_sticker('SEAL'), x, y, 6)
        vx, vy = polar(TR.R_OUT + 30, am + da + 0.12)        # its turns in pencil just outside, on the rope
        py.text('1 turn', vx, vy, 28, angle=-6)
    for b, side in st.get('walls', []):
        if side != 'runner':
            continue
        a = TR.seg_angles(b, st['rot'])[1] + 0.012
        x, y = polar(268, a)
        stick(img, D3b.mini_sticker('WALL'), x, y, -math.degrees(a))
        vx, vy = polar(196, a)
        py.text('1 turn', vx, vy, 28, angle=-6)


# =============================================================================================== plates
def plate_board():
    F = F_all(); st = copy.deepcopy(STATES['board'])
    img = base_image()
    wheel(img, F, st)
    py, pr = Wax(PEN_Y, 1), Wax(PEN_R, 2)
    wheel_stickers(img, st, py)
    pen_outcomes(py, pr, st)
    py.ink_ss(img); pr.ink_ss(img)
    flank_left(img, F, st)
    st['hud']['totals'] = ('COMMIT FORECAST', [('+0 taken', S_GAIN), ('\u22121 lost', S_HARM)], ('health 27 \u2192 26', S_HARM))
    flank_right(img, F, st)
    return img


HELD = (1226, 112, 7)             # held top right: clear of the health tape, the status stickers and every pencil mark


def plate_play():
    F = F_all(); st = copy.deepcopy(STATES['play'])
    img = base_image()
    wheel(img, F, st)
    a = act('BREACH')
    py, pr = Wax(PEN_Y, 3), Wax(PEN_R, 4)
    wheel_stickers(img, st, py)
    legal_marks(py, st)
    am = seg_am(st['aim'], st)
    route = [(HELD[0] + 10, HELD[1] + 100)] + [polar(446, a_) for a_ in np.linspace(math.radians(-58), am - 0.10, 6)] + [polar(330, am - 0.02)]
    py.arrow(route, width=7, head=24)
    py.text('-3', polar(392, math.radians(-46))[0], polar(392, math.radians(-46))[1], 36, angle=-10)
    pen_outcomes(py, pr, st)
    py.ink_ss(img); pr.ink_ss(img)
    flank_left(img, F, st, held='BREACH', cost=1)
    stick(img, sticker(a, curl=True), HELD[0], HELD[1], HELD[2], scale=0.98, lift=1.0)
    st['hud']['totals'] = ('COMMIT FORECAST', [('+1 taken', S_GAIN), ('\u22121 lost', S_HARM)], ('health 27 \u2192 26', S_HARM))
    flank_right(img, F, st, lines=[[('BREACH', S_PLAN), ('on FIREWALL 2: 3 damage, takes it', S_HI)]],
                hint=['rule: 3 damage, a corp segment next to yours', 'Enter: slap  \u00b7  Esc: stick back'])
    return img


def ice_arrows(py, pr, st, played=False):
    """B-088 steps feeding your ICE, as numbered pencil arrows (the D3 hover geometry)"""
    a_ice = seg_am(11, st); a_core = seg_am(10, st)
    p0 = polar(TR.R_HUB + 12, math.radians(-90)); p1 = polar(236, math.radians(-109))
    pr.arrow(qpts(p0, polar(196, math.radians(-94)), p1, 8), width=7, head=20)
    pen_badge(pr, '11.1', 1018, 422, 24); pr.text('-2', 1074, 424, 32)
    q0 = polar(334, a_core + 0.04); q1 = polar(336, math.radians(-129))
    pr.arrow(qpts(q0, polar(410, math.radians(-138)), q1, 10), width=7, head=20)
    lx, ly = polar(474, math.radians(-146))
    pen_badge(pr, '13.1', lx - 12, ly, 24); pr.text('-3', lx + 46, ly + 2, 32)
    a0, a1, _ = TR.seg_angles(11, st['rot'])
    py.stroke(py.wobble([polar(TR.R_OUT - 14, a) for a in np.linspace(a0 + 0.06, a1 - 0.06, 10)], 0.6), 7)
    bx, by = polar(478, math.radians(-118))
    pen_badge(py, '11.2', bx - 40, by, 24); py.text('BLOCK 2', bx + 64, by + 2, 30, angle=-3)
    py.stroke(py.wobble([(bx + 10, by + 18), polar(TR.R_OUT + 4, a_ice + 0.02)], 0.6), 4)


def plate_forecast():
    F = F_all(); st = copy.deepcopy(STATES['forecast'])
    img = base_image()
    wheel(img, F, st)
    py, pr = Wax(PEN_Y, 7), Wax(PEN_R, 8)
    wheel_stickers(img, st, py)
    ice_arrows(py, pr, st)
    pen_outcomes(py, pr, st, skip=(11,))
    x, y = polar(TR.R_IN + 10, math.radians(-128))
    pr.text('LOST -1 HP', x, y, 28, angle=-4)
    pen_badge(pr, '16.1', 874, 442, 22)
    py.ink_ss(img); pr.ink_ss(img)
    flank_left(img, F, st)
    st['hud']['totals'] = ('COMMIT FORECAST', [('+0 taken', S_GAIN), ('\u22121 lost', S_HARM)], ('health 27 \u2192 26', S_HARM))
    fc = st['hud']['forecast']
    lines = [fc[0]] + [[(n, c), (t.replace('run health', 'health'), m)] for (n, c), (t, m) in [tuple(x) for x in fc[1:]]]
    flank_right(img, F, st, lines=lines)
    return img


def rim_bits(img, a_from, a_to, col, n=34, seed=3, leave_to=None):
    """FX (bible 3.20): 0/1 shards in the attacker's colour from the hit point, curving round the rim (never across the face);
    the first few white-hot; then off the rim toward the health tape"""
    L = Layer(); d = L.d
    rng = np.random.default_rng(seed)
    f = TR.font(MONO, 22)
    for k in range(n):
        t = k / (n - 1)
        a = a_from + (a_to - a_from) * t
        r = TR.R_RIM + 6 + rng.normal(0, 7)
        x, y = polar(r, a)
        c = (255, 248, 240) if k < 4 else col
        al = int(255 * (0.55 + 0.45 * (1 - t)))
        d.text((S(x), S(y)), '1' if rng.random() < 0.5 else '0', font=f, fill=c + (al,), anchor='mm', stroke_width=S(1), stroke_fill=c + (al,))
    if leave_to:
        x0, y0 = polar(TR.R_RIM + 6, a_to)
        for k in range(12):
            t = (k + 1) / 13
            x = x0 + (leave_to[0] - x0) * t + rng.normal(0, 6)
            y = y0 + (leave_to[1] - y0) * t + 20 * math.sin(math.pi * t)
            d.text((S(x), S(y)), '1' if k % 2 else '0', font=f, fill=col + (int(230 - 120 * t),), anchor='mm', stroke_width=S(1), stroke_fill=col + (int(230 - 120 * t),))
    comp(img, L)


def plate_resolve():
    F = F_all(); st = copy.deepcopy(STATES['resolve'])
    st['hub'] = dict(top='COMMIT', big='13', bot='COUNTER', col=TR.SCHED)
    st['trace'] = []
    img = base_image()
    wheel(img, F, st)
    py, pr = Wax(PEN_Y, 9), Wax(PEN_R, 10)
    wheel_stickers(img, st, py)
    # the retake: the temporary word sticker on the wedge (it will dissolve to bits), corp-teal shards round the rim to health
    a_ice = seg_am(11, st)
    rim_bits(img, a_ice - 0.05, a_ice - 0.62, TR.TEAL_HI, leave_to=(250, 100))
    x, y = polar(TR.R_IN + 6, a_ice - 0.05)               # on the wedge's inner edge (no outcome marks during the replay)
    stick(img, D3b.mini_sticker('RETAKEN'), x, y, -8, scale=1.0)
    ice_arrows(py, pr, st, played=True)
    # 8.1: RELAY repairs CORE +2, round the dark inner ring (never across the face)
    a6, a10 = seg_am(6, st), seg_am(10, st)
    path = [polar(186, a6 + 0.05)] + [polar(150, a_) for a_ in np.linspace(a6 + 0.25, a10 - 0.30, 10)] + [polar(184, a10 - 0.05)]
    pr.arrow(path, width=6, head=18)
    lx, ly = polar(152, math.radians(172))
    pen_badge(pr, '8.1', lx - 18, ly, 22); pr.text('+2', lx + 30, ly + 2, 30)
    py.ink_ss(img); pr.ink_ss(img)
    flank_left(img, F, st)
    st['hud']['totals'] = ('COMMIT REPLAY', [('step 13 of 16', S_SCHED)], ('health 27 \u2192 26 at 16', S_HARM))
    flank_right(img, F, st, lines=[[('13.1', S_SCHED), ('CORE counterattack: \u22123, retakes ICE', S_HI)],
                                   [('done', S_MID), ('8.1  11.1  11.2', S_MID)]], hint=['Space: skip the replay'])
    return img


def plate_wallseal():
    F = F_all(); st = copy.deepcopy(STATES['wallseal'])
    img = base_image()
    wheel(img, F, st)
    py, pr = Wax(PEN_Y, 11), Wax(PEN_R, 12)
    wheel_stickers(img, st, py)
    pen_outcomes(py, pr, st)
    py.ink_ss(img); pr.ink_ss(img)
    flank_left(img, F, st)
    st['hud']['totals'] = ('COMMIT FORECAST', [('+0 taken', S_GAIN), ('\u22121 lost', S_HARM)], ('health 27 \u2192 26', S_HARM))
    flank_right(img, F, st, lines=[[('WALL', S_HI), ('blocks a boundary, 1 turn', S_MID)], [('SEAL', S_HI), ('immune this turn', S_MID)]])
    return img


def plate_win():
    F = F_all(); st = copy.deepcopy(STATES['win'])
    st['hud']['runner'] = BOARD_RUNNER
    img = base_image()
    wheel(img, F, st)
    # the result: the result stamp sticker on the hub, a yellow pencil OURS NOW and a ring round the wheel (bible 2.? reward screen)
    py = Wax(PEN_Y, 13)
    py.circle(CX, CY, 424, 424, width=8, start=-2.6, over=0.5, tilt=0)
    py.text('OURS NOW', 735, 62, 56, angle=-6)
    py.ink_ss(img)
    art = SL.lettering(['WHEEL TAKEN'], 66, [('grad', (255, 238, 96), (255, 182, 14))], key_w=5, extrude=7, seed=5, jitter=3)
    stick(img, SL.build_sticker(art, border=10, gloss_k=0.22), CX, CY - 4, -5, scale=0.9)
    flank_left(img, F, st)
    st['hud']['owned_after'] = None
    st['hud']['totals'] = ('RESULT', [('FIGHT WON', S_GAIN)], ('the site is yours', S_HI))
    flank_right(img, F, st, lines=[[('health 24 / 30', S_HI), ('kept for the street', S_MID)], [('+6 credits', (255, 210, 77))]],
                verb='CONTINUE', system=None)
    return img


BOARD_RUNNER = STATES['board']['hud']['runner']


# ------------------------------------------------------------------ WORM (build B-091): one pick; the selector adds the rest
WORM_PICK = 4                       # the hovered legal wedge: corp TURRET
WORM_ORDER = [4, 3, 5]              # target_and_corp_nb: the target, then its corp neighbours (tie-break: content id, then node id)


def plate_worm():
    F = F_all(); st = copy.deepcopy(STATES['board'])
    img = base_image()
    wheel(img, F, st)
    py, pr = Wax(PEN_Y, 21), Wax(PEN_R, 22)
    wheel_stickers(img, st, py)
    for n, i in enumerate(WORM_ORDER, 1):
        am = seg_am(i, st)
        x, y = polar(280, am)
        py.circle(x, y, 56, 70, width=7 if n == 1 else 5, tilt=am + math.pi / 2, start=-1.6 + n)
        bx, by = polar(356, am - 0.20)                # the pick number at the loop's outer corner
        pen_badge(py, str(n), bx, by, 30)
        lx, ly = polar(276, am)                       # +V beside the integrity, inside the loop
        py.text('+V', lx + 44, ly + 2, 28, angle=-6)
    a4, a3, a5 = (seg_am(i, st) for i in WORM_ORDER)
    # one line, in order: sticker -> 1 TURRET; 1 -> 2 CACHE (inside the rim); 2 -> 3 NODE round the outside of the rim
    route = [(WORM_HELD[0] + 12, WORM_HELD[1] + 100)] + [polar(446, a_) for a_ in np.linspace(math.radians(-50), a4 - 0.06, 7)] + [polar(346, a4 + 0.02)]
    py.arrow(route, width=7, head=22)
    py.arrow(qpts(polar(330, a4 - 0.16), polar(372, (a4 + a3) / 2), polar(334, a3 + 0.15), 8), width=5, head=16)
    # 2 -> 3 passes TURRET through the dark inner ring (never round the outside again, which would cross line 1)
    py.arrow([polar(212, a3 + 0.10), polar(160, a3 + 0.16)] + [polar(150, a_) for a_ in np.linspace(a3 + 0.3, a5 - 0.32, 6)] + [polar(172, a5 + 0.10), polar(214, a5 + 0.10)], width=5, head=16)
    pen_outcomes(py, pr, st, skip=(5,))
    nx, ny = polar(TR.R_IN + 6, seg_am(5, st) - 0.16)
    py.arrow([(nx - 34, ny + 2), (nx - 18, ny), (nx - 4, ny + 1)], width=5, head=11)
    py.text('4', nx + 14, ny, 36, angle=4)
    py.ink_ss(img); pr.ink_ss(img)
    flank_left(img, F, st, held='WORM', cost=1)
    stick(img, sticker(act('WORM'), curl=True), WORM_HELD[0], WORM_HELD[1], WORM_HELD[2], scale=0.9, lift=1.0)
    st['hud']['totals'] = ('COMMIT FORECAST', [('+0 taken', S_GAIN), ('−1 lost', S_HARM)], ('health 27 → 26', S_HARM))
    flank_right(img, F, st, lines=[[('WORM', S_PLAN), ('on TURRET: 1 virus on', S_HI)], [('TURRET, CACHE, NODE', S_HI)]],
                hint=['rule: the target, then its corp neighbours', 'Enter: slap  ·  Esc: stick back'])
    return img


WORM_HELD = (1226, 112, 7)


def sheet():
    names = [('v3_board', 'board', 'rest: programs on the glass; statuses = sticker + pencil value'),
             ('v3_play', 'play', 'BREACH peeled; pencil to FIREWALL 2; legal loops; TAKEN'),
             ('v3_worm', 'worm', 'one pick (TURRET); selector adds CACHE, NODE; loops 1-3'),
             ('v3_forecast', 'forecast', 'your ICE hovered: numbered pencil arrows + HUD steps'),
             ('v3_resolve', 'resolve', 'COMMIT replay at 13: played steps, RETAKEN, teal bits'),
             ('v3_wallseal', 'wall and seal', 'corp enamel; your WALL / SEAL stickers, turns in pencil'),
             ('v3_win', 'win', '12/12: WHEEL TAKEN, pencil OURS NOW, CONTINUE')]
    tw_, th_ = 700, 394
    pad, cap = 12, 58
    cols = 4
    sh = Image.new('RGB', (cols * tw_ + (cols + 1) * pad, 2 * (th_ + cap) + 3 * pad + 50), (14, 14, 18))
    d = ImageDraw.Draw(sh)
    f = ImageFont.truetype(MONO, 15); fa = ImageFont.truetype(ANTON, 22); fb = ImageFont.truetype(ANTON, 30)
    d.text((pad, 10), 'TAKEOVER in DEFACE v3: the B-086 state set (reference for build)', font=fb, fill=TEXT_HI)
    for k, (n, t, c) in enumerate(names):
        im = Image.open(OUT + n + '.png').resize((tw_, th_), Image.LANCZOS)
        x = pad + (k % cols) * (tw_ + pad); y = 54 + pad + (k // cols) * (th_ + cap + pad)
        sh.paste(im, (x, y))
        d.text((x + 4, y + th_ + 4), '%s   %s.png' % (t, n), font=fa, fill=TEXT_HI)
        d.text((x + 4, y + th_ + 34), c, font=f, fill=TEXT_MID)
    sh.save(OUT + 'v3_sheet.jpg', quality=90)
    print('ok', OUT + 'v3_sheet.jpg')


R = dict(board=plate_board, play=plate_play, worm=plate_worm, forecast=plate_forecast, resolve=plate_resolve, wallseal=plate_wallseal, win=plate_win)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for n in (sys.argv[1:] or ['board', 'play', 'worm', 'forecast', 'resolve', 'wallseal', 'win', 'sheet']):
        if n == 'sheet':
            sheet(); continue
        img = R[n]()
        img.resize((W, H), Image.LANCZOS).convert('RGB').save(OUT + 'v3_%s.png' % n)
        print('ok', OUT + 'v3_%s.png' % n)
