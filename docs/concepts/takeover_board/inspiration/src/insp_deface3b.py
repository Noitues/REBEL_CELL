"""insp_deface3b: DEFACE v3, the missing states (sibling of insp_deface3.py, which it imports unchanged).

    python insp_deface3b.py [df3_worm df3_invalid df3_status sheet]      (default: all)

df3_worm     WORM peeled and aimed at three corp segments: three yellow pencil loops numbered 1-3 in pick order, one pencil line
             from the sticker through them, +1 virus on each in pencil, the HUD play line.
df3_invalid  BREACH held over your own NODE: it will not stick (stays curled, lifted), a red pencil slash on the wedge and the
             reason written beside it; the legal wedges stay looped in yellow.
df3_status   bible 1.2 "temporary effect words are stickers": your statuses as small stickers (BLOCK 2, VIRUS 1, SEAL), the corp's
             own seal stays an enamel lid; a TIME BOMB on a corp segment with its turn count and its 6 damage in pencil; the
             VIRUS sticker hovered (peel curl, CRT tooltip, its numbered pencil arrow).
"""
import copy, math, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/takeover/inspiration')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import insp_deface3 as D3
from insp_deface3 import (Wax, PEN_Y, PEN_R, SL, IR, TR, S, text, Layer, comp, INK, PAPER, CYAN, TEXT_HI, TEXT_MID, ANTON, MONO,
                          ACTS, BOARD, PLAY, CX, CY, W, H, SS, F_all, base_image, glass, stick, sticker, draw_wheel, pen_outcomes,
                          legal_marks, qpts, polar, pen_badge, left, right, MODE, _shape)
from tk_states import GAIN as S_GAIN, HARM as S_HARM, HI as S_HI, PLAN as S_PLAN, MID as S_MID

OUT = D3.OUT


def act(aid):
    return [x for x in ACTS if x['id'] == aid][0]


def seg_am(i, st):
    return TR.seg_angles(i, st['rot'])[2]


# =============================================================================================== 1. WORM: three targets
WORM_T = [3, 4, 5]                 # CACHE, TURRET, NODE (corp), picked in this order
WORM_HELD = (1230, 128, 6)


def render_worm():
    F = F_all()
    st = copy.deepcopy(BOARD)
    st['focus'] = []
    st['hud'] = copy.deepcopy(BOARD['hud'])
    st['hud']['forecast'] = [[('WORM', S_PLAN), ('1 virus on CACHE, TURRET, NODE', S_HI)], BOARD['hud']['forecast'][-1]]
    MODE.update(hint=['3 of 3 picked (click a loop to drop it).', 'Enter: slap  \u00b7  Esc: stick back'], steps=None)
    img = base_image()
    draw_wheel(img, st, F)
    left(img, F, held='WORM', cost=1)
    py, pr = Wax(PEN_Y, 41), Wax(PEN_R, 42)
    # the targets, in pick order: a loop round each label, its number at the loop's outer corner, +1 virus by it
    for n, i in enumerate(WORM_T, 1):
        am = seg_am(i, st)
        x, y = polar(280, am)
        py.circle(x, y, 60, 72, width=6, tilt=am + math.pi / 2, start=-1.6 + n)
        bx, by = polar(350, am - 0.20)
        pen_badge(py, str(n), bx, by, 30)
        vx, vy = polar(200, am - 0.20)          # the virus outcome at the wedge's inner edge, beside any integrity mark
        py.text('+V', vx, vy, 30, angle=-6)
    # one pencil line from the sticker, outside the rim, into loop 1, then on to 2 and 3 (the pick order)
    a3, a4, a5 = (seg_am(i, st) for i in WORM_T)
    route = [(WORM_HELD[0] + 40, WORM_HELD[1] + 96)] + [polar(424, a_) for a_ in np.linspace(math.radians(-40), a3 - 0.12, 6)] + [polar(346, a3 - 0.05)]
    py.arrow(route, width=7, head=22)
    py.arrow(qpts(polar(338, a3 + 0.14), polar(386, (a3 + a4) / 2), polar(340, a4 - 0.13), 8), width=5, head=16)
    py.arrow(qpts(polar(338, a4 + 0.14), polar(386, (a4 + a5) / 2), polar(340, a5 - 0.13), 8), width=5, head=16)
    pen_outcomes(py, pr, st, skip=(5,))
    nx, ny = polar(TR.R_IN + 8, seg_am(5, st) + 0.13)       # NODE's own integrity mark, moved aside for its +V
    py.arrow([(nx - 34, ny + 2), (nx - 18, ny), (nx - 4, ny + 1)], width=5, head=11)
    py.text('4', nx + 14, ny, 36, angle=4)
    py.ink_ss(img); pr.ink_ss(img)
    stick(img, sticker(act('WORM'), curl=True), WORM_HELD[0], WORM_HELD[1], WORM_HELD[2], scale=0.9, lift=1.0)
    right(img, F, st)
    return img


# =============================================================================================== 2. BREACH over an illegal wedge
def render_invalid():
    F = F_all()
    st = copy.deepcopy(BOARD)
    st['focus'] = [2, 10]
    st['hud'] = copy.deepcopy(BOARD['hud'])
    st['hud']['forecast'] = [[('BREACH', S_PLAN), ("can't go on your NODE", S_HARM)], BOARD['hud']['forecast'][-1]]
    MODE.update(hint=['rule: 3 damage to a corp segment next to', 'yours.  Legal: CORE, FIREWALL (looped)'], steps=None)
    img = base_image()
    draw_wheel(img, st, F)
    left(img, F, held='BREACH', cost=1)
    py, pr = Wax(PEN_Y, 51), Wax(PEN_R, 52)
    legal_marks(py, st)
    # the red "invalid" mark on the wedge under the sticker: a circle with a slash (the bible's nudge-lock mark), and the reason
    am = seg_am(0, st)
    x, y = polar(262, am)
    pr.circle(x, y, 58, 58, width=7, start=-2.4, tilt=0)
    pr.stroke(pr.wobble([(x - 40, y + 40), (x + 40, y - 40)], 0.8), 7)
    pr.text("it's yours:", 1250, 120, 34, angle=-4)
    pr.text('needs a corp seg', 1252, 166, 30, angle=-4)
    pr.text('next to yours', 1250, 206, 30, angle=-4)
    pr.arrow([(1146, 238), (1080, 252), (1022, 270)], width=5, head=16)
    pen_outcomes(py, pr, st)
    py.ink_ss(img); pr.ink_ss(img)
    # the sticker hovers over the wedge but will not stick: still curled, tilted, lifted (long soft shadow), off to the left
    stick(img, sticker(act('BREACH'), curl=True), 836, 148, 14, scale=0.9, lift=1.0)
    right(img, F, st)
    return img


# =============================================================================================== 3. statuses as stickers
STAT = {'BLOCK 2': ((110, 170, 255), (52, 104, 220)), 'VIRUS 1': ((150, 236, 120), (80, 178, 70)), 'SEAL': ((255, 92, 186), (226, 30, 140))}


def mini_sticker(word, curl=False):
    """a temporary effect word as a small die-cut vinyl sticker (bible 1.2): pill body, ink key, Anton word"""
    f = ImageFont.truetype(ANTON, S(22))
    w = int(ImageDraw.Draw(Image.new('L', (8, 8))).textlength(word, font=f) / SS) + 24
    h, pad = 34, 40
    CW, CH = S(w + 2 * pad), S(h + 2 * pad)
    body = Image.new('L', (CW, CH), 0)
    ImageDraw.Draw(body).rounded_rectangle([S(pad), S(pad), S(pad + w), S(pad + h)], radius=S(9), fill=255)
    art = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    key = body.filter(ImageFilter.MaxFilter(S(2) * 2 + 1))
    art = SL.over(art, SL.INK_DEEP, SL.shift(key, S(2), S(3)))
    art = SL.over(art, INK, key)
    top, bot = STAT[word]
    tex = SL.vgrad_tex(CW, CH, top, bot); tex.putalpha(body)
    art = Image.alpha_composite(art, tex)
    d = ImageDraw.Draw(art)
    d.text((S(pad + w / 2), S(pad + h / 2 + 1)), word, font=f, fill=PAPER + (255,), anchor='mm', stroke_width=S(2), stroke_fill=INK + (255,))
    return SL.build_sticker(art, border=5, close=6, gloss_k=0.22, curl=dict(corner='tr', amount=0.20) if curl else None)


def bomb_sticker():
    w, h, pad = 64, 58, 40
    CW, CH = S(w + 2 * pad), S(h + 2 * pad)
    body = Image.new('L', (CW, CH), 0)
    body.paste(_shape('bomb', w, h, 3), (S(pad), S(pad)))
    art = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    key = body.filter(ImageFilter.MaxFilter(S(2) * 2 + 1))
    art = SL.over(art, SL.INK_DEEP, SL.shift(key, S(2), S(3)))
    art = SL.over(art, INK, key)
    tex = SL.vgrad_tex(CW, CH, (255, 170, 70), (236, 110, 30)); tex.putalpha(body)
    art = Image.alpha_composite(art, tex)
    return SL.build_sticker(art, border=5, close=6, gloss_k=0.22)


BOMB_ON = 6                         # the TIME BOMB sits on corp RELAY (free space below the rim for its countdown)


def render_status():
    F = F_all()
    st = copy.deepcopy(BOARD)
    # changes for this plate: your SEAL on your FIREWALL, the corp's own seal on SPAWNER, a TIME BOMB (played on an earlier
    # turn) on TURRET; the stamped status chips of yours are replaced by stickers
    for g in st['segs']:
        g['st'] = [s_ for s_ in g.get('st', []) if s_[1] != 'runner']
    st['seals'] = [(7, 'corp')]
    MODE.update(hint=None, steps=None)
    img = base_image()
    draw_wheel(img, st, F)
    TR.draw_walls_seals(img, st, F['seg_small'])                     # the corp seal: the enamel glaze lid + SEALED (unchanged)
    py, pr = Wax(PEN_Y, 61), Wax(PEN_R, 62)
    pen_outcomes(py, pr, st)
    # hover: the VIRUS 1 sticker on corp NODE; its numbered pencil arrow to the integrity it changes (A3 step 5)
    a5 = seg_am(5, st)
    vx, vy = polar(TR.R_OUT - 28, a5 - 0.17)
    ox, oy = polar(TR.R_IN + 8, a5)
    py.arrow(qpts((vx - 6, vy - 26), polar(262, a5 - 0.24), (ox + 26, oy - 4), 8), width=5, head=16)
    lx, ly = polar(448, a5 - 0.06)                          # below the rim, by the hovered sticker
    pen_badge(py, '5.1', lx - 14, ly, 22); py.text('-1', lx + 38, ly + 2, 30)
    # the bomb's countdown and its forecast, in pencil, outside the rim by TURRET
    a4 = seg_am(BOMB_ON, st)
    bx, by = 846, 1012
    py.text('2', bx, by, 40)
    py.circle(bx, by, 24, 24, width=5)
    py.text('turns, then -6', bx + 132, by, 30, angle=-3)
    py.arrow([(bx + 16, by - 30), (bx + 30, by - 58), (bx + 36, by - 82)], width=5, head=14)
    py.ink_ss(img); pr.ink_ss(img)
    # your effect stickers, on the wedge's free corner
    places = [(11, 'BLOCK 2', -0.17), (1, 'SEAL', 0.16), (5, 'VIRUS 1', -0.17)]
    for i, word, da in places:
        am = seg_am(i, st)
        x, y = polar(TR.R_OUT - 30, am + da)
        hov = word == 'VIRUS 1'
        stick(img, mini_sticker(word, curl=hov), x, y, -(math.degrees(am + da) + 90) * 0 + (-6 if da < 0 else 6), scale=1.12 if hov else 1.0, lift=0.6 if hov else 0.0)
    x, y = polar(TR.R_OUT - 30, a4 + 0.24)
    stick(img, bomb_sticker(), x, y, -8, scale=0.86)
    # the CRT tooltip for the hovered status (system layer)
    L = Layer(); d = L.d
    x0, y0, x1, y1 = 1366, 786, 1898, 896
    glass(d, (x0, y0, x1, y1))
    text(d, (x0 + 16, y0 + 24), 'VIRUS 1', F['a26'], (150, 236, 120, 255), anchor='lm')
    text(d, (x0 + 120, y0 + 25), 'on corp NODE, put there by WORM', F['m18'], TEXT_MID + (255,), anchor='lm')
    text(d, (x0 + 16, y0 + 58), '-1 integrity each END TURN (step 5.1)', F['m20'], TEXT_HI + (255,), anchor='lm')
    text(d, (x0 + 16, y0 + 88), 'this END TURN: NODE 5 -> 4', F['m20'], TEXT_HI + (255,), anchor='lm')
    comp(img, L)
    left(img, F)
    right(img, F, st)
    return img


# =============================================================================================== sheet
def sheet():
    names = [('df3_worm', 'WORM, three targets', 'loops 1-3 in pick order, one pencil line through them, +V on each'),
             ('df3_invalid', 'BREACH on your NODE', "won't stick: curled, red slash and the reason; legal wedges looped"),
             ('df3_status', 'statuses as stickers', 'BLOCK / VIRUS / SEAL stickers, corp seal enamel, TIME BOMB countdown, hover')]
    tw_, th_ = 900, 506
    pad, cap = 14, 64
    sh = Image.new('RGB', (3 * tw_ + 4 * pad, th_ + cap + 2 * pad + 56), (14, 14, 18))
    d = ImageDraw.Draw(sh)
    f = ImageFont.truetype(MONO, 18); fa = ImageFont.truetype(ANTON, 24); fb = ImageFont.truetype(ANTON, 32)
    d.text((pad, 12), 'DEFACE v3, the missing states', font=fb, fill=TEXT_HI)
    for k, (n, t, c) in enumerate(names):
        im = Image.open(OUT + n + '.png').resize((tw_, th_), Image.LANCZOS)
        x = pad + k * (tw_ + pad); y = 60
        sh.paste(im, (x, y))
        d.text((x + 4, y + th_ + 6), '%s   %s.png' % (t, n), font=fa, fill=TEXT_HI)
        d.text((x + 4, y + th_ + 40), c, font=f, fill=TEXT_MID)
    sh.save(OUT + 'df3_states_sheet.jpg', quality=90)
    print('ok', OUT + 'df3_states_sheet.jpg')


R = dict(df3_worm=render_worm, df3_invalid=render_invalid, df3_status=render_status)

if __name__ == '__main__':
    for n in (sys.argv[1:] or ['df3_worm', 'df3_invalid', 'df3_status', 'sheet']):
        if n == 'sheet':
            sheet(); continue
        img = R[n]()
        img.resize((W, H), Image.LANCZOS).convert('RGB').save(OUT + n + '.png')
        print('ok', OUT + n + '.png')
