"""f1_hand: the hand (G1-A wheat-paste cards at 1.15x, 4 deg fan, lifted card with a pink offset print, played slots as torn-paper outlines),
SEND IT (G1-A spray slab), the nameplate and the YOU strip.  Game information from the E10 sim state only."""
import os, sys, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from scipy import ndimage as ndi
import st_cards as K
import mu_cards as MC
import mu_ui as UI
from f1_lib import Canvas, tag_text as ptag, font, MARKER_F, PAPER, INK, PINK

CACHE = 'D:/rc_scratch/combat_redesign/punk/mural_graffiti/work_m/'
os.makedirs(CACHE, exist_ok=True)
CARD_SCALE = 1.15
FAN_DEG = 4.0
STEP = 182
LEFT_CX = 962
CY0 = 910
LIFT_S = 1.10
LIFT_CY = 856
HOV_PUSH = 30
REST_V = 0.88

_mem = {}


def card_hi(name, nw, seed=None):
    """2x image of one card (RGBA, canvas = card + 18 px margin each side at 1x)"""
    key = (name, nw, MC.VAR[0])
    if key in _mem:
        return _mem[key]
    fp = CACHE + 'card_%s_%s_%d.png' % (MC.VAR[0], name, nw)
    if os.path.exists(fp):
        im = Image.open(fp).convert('RGBA')
    else:
        K.NW[0] = nw
        sd = {'Brace': 1, 'Spin3': 4, 'Trigger': 7, 'Twist': 10}.get(name, 13)
        im = MC.render_card(name, MC.VAR[0], seed=sd, ss=4, scale=2)
        K.NW[0] = False
        im.save(fp)
    _mem[key] = im
    return im


def shadow_under(im, off=(4, 8), blur=7, alpha=0.6):
    pad = int(blur * 3 + 12)
    big = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    big.paste(im, (pad, pad))
    a = big.split()[3]
    sh = Image.new('L', big.size, 0)
    sh.paste(a, off)
    sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    out = Image.new('RGBA', big.size, (8, 6, 14, 0))
    out.putalpha(sh)
    return out, big, pad


def put(base, im, cx, cy, ang=0.0, scale=1.0, shadow=True, off=(4, 8), blur=7):
    """place a 2x card image at screen centre (cx, cy), card scale (1.15 etc) relative to the 1x design"""
    k = scale / 2.0
    w, h = max(1, int(im.width * k)), max(1, int(im.height * k))
    im = im.resize((w, h), Image.LANCZOS)
    if ang:
        im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
    if shadow:
        sh, big, pad = shadow_under(im, off, blur)
        base.alpha_composite(sh, (int(round(cx - sh.width / 2)), int(round(cy - sh.height / 2))))
        base.alpha_composite(big, (int(round(cx - sh.width / 2)), int(round(cy - sh.height / 2))))
    else:
        base.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))
    return im


def pink_print(im, off=(-9, 7), alpha=0.94):
    """the lifted card's pink offset print: its silhouette in CELL_PINK, shifted, misregistered like a cheap two-colour print"""
    a = im.split()[3]
    a = a.filter(ImageFilter.MaxFilter(3))
    pk = Image.new('RGBA', im.size, (255, 61, 168, 0))
    pk.putalpha(a.point(lambda v: int(v * alpha)))
    out = Image.new('RGBA', (im.width + 40, im.height + 40), (0, 0, 0, 0))
    out.alpha_composite(pk, (20 + off[0] * 2, 20 + off[1] * 2))
    return out


def played_slot(name, nw, size_scale=CARD_SCALE):
    """a played card leaves a torn-paper outline (solid, never dashed) with the card ghosted inside"""
    im = card_hi(name, nw)
    a = np.asarray(im.split()[3], np.float32) / 255.0
    core = ndi.binary_erosion(a > 0.5, iterations=6).astype(np.float32)
    ring = np.clip(ndi.gaussian_filter(((ndi.binary_dilation(a > 0.5, iterations=4)) & ~(ndi.binary_erosion(a > 0.5, iterations=8))).astype(np.float32), 1.0) * 1.3, 0, 1)
    out = np.zeros((im.height, im.width, 4), np.float32)
    # dark glass inside, paper-coloured torn outline, ink under it
    fill = ndi.gaussian_filter(core, 1.5)
    out[..., :3] = (22, 16, 32)
    out[..., 3] = fill * 0.55
    rgba = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')
    ink = Image.new('RGBA', im.size, (12, 10, 22, 0))
    ink.putalpha(Image.fromarray((np.clip(ndi.gaussian_filter(((ndi.binary_dilation(a > 0.5, iterations=6)) & ~(ndi.binary_erosion(a > 0.5, iterations=4))).astype(np.float32), 1.0) * 1.4, 0, 1) * 235).astype(np.uint8)))
    pap = Image.new('RGBA', im.size, (242, 238, 228, 0))
    pap.putalpha(Image.fromarray((ring * 150).astype(np.uint8)))
    res = Image.new('RGBA', im.size, (0, 0, 0, 0))
    res.alpha_composite(rgba)
    res.alpha_composite(ink)
    res.alpha_composite(pap)
    # ghost of the card art
    g = im.copy()
    ga = g.split()[3].point(lambda v: int(v * 0.12))
    gm = Image.fromarray((ndi.binary_erosion(a > 0.5, iterations=9) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1))
    g.putalpha(Image.fromarray(np.minimum(np.asarray(ga), np.asarray(gm))))
    res.alpha_composite(g)
    return res


def slots(n):
    out = []
    for i in range(n):
        a = (i - (n - 1) / 2) * -FAN_DEG
        th = math.radians(a)
        out.append(dict(cx=LEFT_CX + i * STEP, cy=CY0 + 905.0 * th * th, ang=a))
    return out


def hand_lists(J, beat):
    BE = {'p1': 'f1', 'nowords': 'f1', 'p2': 'f2', 'p2b': 'f1', 'p3': 'f2'}
    f = J[BE[beat]]
    f1 = J['f1']
    played = [a[0] for a in f['played']]
    hand = list(f['hand'])
    if beat == 'p3':
        hand = list(f1['hand'])
        for c_ in played:
            hand.remove(c_)
    hover_i = hand.index('Trigger') if beat == 'p2' else None
    return hand, (played if beat == 'p3' else []), hover_i


def draw_hand(base, J, beat, nw=False, lift=None, dim_others=None):
    """lift: override of the lifted card name (hover plates)"""
    hand, played, hov = hand_lists(J, beat)
    if lift is not None:
        hov = hand.index(lift)
    n = len(hand) + len(played)
    sl = slots(n)
    if hov is not None:
        for k_ in range(hov + 1, n):
            sl[k_]['cx'] += HOV_PUSH
    for i, nm in enumerate(hand):
        if i == hov:
            continue
        s = sl[i]
        ci = card_hi(nm, nw)
        k_ = REST_V * (dim_others or 1.0)          # the rest of the hand sits at 88 percent value; only the lifted card is at full value (AD: peak order SEND IT > ... > lifted card > tower slices > rest of the hand)
        a_ = np.asarray(ci).astype(np.float32)
        a_[..., :3] *= k_
        ci = Image.fromarray(a_.astype(np.uint8), 'RGBA')
        put(base, ci, s['cx'], s['cy'], s['ang'], CARD_SCALE)
    for j, nm in enumerate(played):
        s = sl[len(hand) + j]
        put(base, played_slot(nm, nw), s['cx'], s['cy'], s['ang'], CARD_SCALE, shadow=False)
        if not nw:
            lay = Canvas(260, 80, 3, seed=j + 3)
            from f1_lib import letters
            letters(lay, 'PLAYED', (130, 40), 24, fnt=MARKER_F, fill=PAPER, ink=INK, ink_w=1.4, outline=True, miss=(0.5, 0.4), spacing=0.6, rot=0)
            tim = lay.down()
            tim = tim.rotate(s['ang'], resample=Image.BICUBIC, expand=True)
            base.alpha_composite(tim, (int(s['cx'] - tim.width / 2), int(s['cy'] + 40 - tim.height / 2)))
    if hov is not None:
        s = sl[hov]
        im = card_hi(hand[hov], nw)
        k = LIFT_S * CARD_SCALE / 2.0
        w, h = int(im.width * k), int(im.height * k)
        sm = im.resize((w, h), Image.LANCZOS)
        pp = pink_print(sm)
        base.alpha_composite(pp, (int(s['cx'] - pp.width / 2), int(LIFT_CY - pp.height / 2)))
        put(base, im, s['cx'], LIFT_CY, 0, LIFT_S * CARD_SCALE, shadow=True, off=(6, 12), blur=10)
    return sl


_ui = {}


def ui_img(kind, nw, f=None, seed=0):
    key = (kind, nw, MC.VAR[0], None if f is None else (f["hp"], f["pv"]["hp_after"]))
    if key in _ui:
        return _ui[key]
    if kind == 'send':
        r = UI.send_it(ss=3, scale=1, nw=nw)
    elif kind == 'name':
        r = UI.nameplate(ss=3, scale=1, nw=nw)
    else:
        r = UI.you_strip(f, ss=3, nw=nw)
    _ui[key] = r
    return r


def place_ui(base, kind, nw, f=None, shadow=(2, 4, 5, 0.5)):
    im, (x0, y0) = ui_img(kind, nw, f)
    base.alpha_composite(im, (x0, y0))
