"""lc_cards: the LINOCUT card hand.  Same layout as the F1 black-book card (cost badge top left, big icon in an art band, title, type band, rules text, Trace tab top right),
cut and printed in the wheel's two blocks: scissor-cut paper stock, hot-pink second block 3 px off register, carved black key frame, black title on bone (readable), bone-on-black type band.
Variant A = bone stock + pink art band; B = pink stock + black art band (the reverse pull).  render_card(name, variant, seed, ss, scale) -> RGBA at `scale` x with an 18 px margin."""
import math, sys, json
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from f1_lib import Canvas, pol, smooth, warp, outline_mask, font, ANTON_F, MONO_F
from lc_lib import *
import lc_tower as LT

CW, CH, M = 176, 250, 18
NW = [False]
J = json.load(open('D:/rc_scratch/combat_redesign/punk/linocut/state_e10.json'))
PLEX = 'D:/rc_art/art-pass/assets/fonts/IBMPlexSansCondensed-Medium.ttf'
CYAN = (92, 225, 255)
VIOLET = (160, 60, 255)
CARDS = {
    'Brace': dict(fam='TOWER', g='C_BRACE', txt='Block a slice', nm='BRACE', num=None),
    'Spin3': dict(fam='TOWER', g='PI_SPIN_CW', txt='Turn the tower 3', nm='SPIN 3', num='3', mult='3'),
    'Trigger': dict(fam='WAVE', g='C_TRIG', txt='Resolve a unit', nm='TRIGGER', num=None),
    'Twist': dict(fam='WAVE', g='C_TWIST', txt='Turn one ring 1', nm='TWIST', num='1'),
    'Strike': dict(fam='TOWER', g='C_STRIKE', txt='Hit a unit for 2', nm='STRIKE', num='2'),
}
PAL = {
    'A': dict(stock=BONE, band=HOT, ray=KEY, ray2=BONE, disc=BONE, glyph=KEY, glyph_off=HOT_D, frame=KEY, title=KEY, title_off=HOT, title_bg=None, type_bg=KEY, type_fg=BONE, text=KEY, halo=HOT),
    'B': dict(stock=HOT, band=KEY, ray=HOT, ray2=BONE, disc=HOT, glyph=KEY, glyph_off=BONE, frame=KEY, title=KEY, title_off=HOT_D, title_bg=BONE, type_bg=KEY, type_fg=BONE, text=KEY, halo=BONE),
}


def glyph_np(name, px_ss):
    from cv_lib import glyph_rgba
    g = glyph_rgba(name, int(px_ss), max(2, int(px_ss * 0.075)), fill=(255, 255, 255))
    a = np.asarray(g, np.float32) / 255.0
    m = np.clip((a[..., 3] - 0.5) * 3, 0, 1) * (a[..., :3].min(-1) > 0.8)
    return ndi.gaussian_filter(m, 0.4 * px_ss / 66.0)


def place(cv, m, cx, cy):
    """put small mask m (SS px) centred at 1x (cx,cy) onto a full-canvas mask"""
    out = np.zeros((cv.H, cv.W), np.float32)
    ox, oy = int(round(cx * cv.S - m.shape[1] / 2)), int(round(cy * cv.S - m.shape[0] / 2))
    ys0, xs0 = max(0, oy), max(0, ox)
    ys1, xs1 = min(cv.H, oy + m.shape[0]), min(cv.W, ox + m.shape[1])
    if ys1 > ys0 and xs1 > xs0:
        out[ys0:ys1, xs0:xs1] = m[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox]
    return out


def sh(m, dx, dy, S):
    return np.roll(np.roll(m, int(round(dy * S)), 0), int(round(dx * S)), 1)


def text_m(cv, text, c, px, fp=ANTON_F, track=0.0, rot=0.0, xs=1.0):
    S = cv.S
    f = font(fp, px * S)
    wt = sum(f.getlength(ch) for ch in text) + track * S * (len(text) - 1)
    pad = int(px * S * 0.8)
    im = Image.new('L', (int(wt + pad * 2), int(px * S * 2.0)), 0)
    d = ImageDraw.Draw(im)
    x = pad
    for ch in text:
        d.text((x, im.height / 2), ch, font=f, fill=255, anchor='lm')
        x += f.getlength(ch) + track * S
    if xs != 1.0:
        im = im.resize((int(im.width * xs), im.height), Image.LANCZOS)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    return place(cv, np.asarray(im, np.float32) / 255.0, c[0], c[1]), wt / S


def card(name, variant='A', seed=0, S=4):
    spec = CARDS[name]
    cost, loud = J['cards'][name]
    p = PAL[variant]
    cv = Canvas(CW + 2 * M, CH + 2 * M, S, seed=seed + 100)
    r = cv.r
    o = M
    nw = NW[0]

    def pt(x, y):
        return (x + o, y + o)

    # ---- stock: scissor-cut rectangle
    def rect_pts(x0, y0, x1, y1, step=(10, 20), amp=1.2):
        a = jag_path(pt(x0, y0), pt(x1, y0), r, step, amp)
        b = jag_path(pt(x1, y0), pt(x1, y1), r, step, amp)[1:]
        c = jag_path(pt(x1, y1), pt(x0, y1), r, step, amp)[1:]
        d = jag_path(pt(x0, y1), pt(x0, y0), r, step, amp)[1:-1]
        return a + b + c + d
    body = cv.poly_mask(rect_pts(0, 0, CW, CH, (9, 19), 1.4))
    halo = sh(ndi.binary_dilation(body > 0.5, iterations=int(2.2 * S)).astype(np.float32), -3.2, 2.6, S)
    cv.over(halo, p['halo'], 1.0)
    cv.over(ink_grain(cv, body, 0.5), p['stock'], 1.0)
    # paper fibre on the stock
    fib = smooth(cv.H, cv.W, 1.6 * S, r)
    cv.over(np.clip((fib - 1.3) * 0.6, 0, 1) * body, BONE_D if variant == 'A' else HOT_D, 0.35)

    # ---- art band
    bx0, by0, bx1, by1 = 11, 11, CW - 11, 128
    band = cv.poly_mask(rect_pts(bx0, by0, bx1, by1, (8, 15), 1.0))
    cv.over(ink_grain(cv, band, 0.6), p['band'], 1.0)
    icx, icy = CW / 2, 70
    # carved rays from the icon: black (A) / pink (B) lenses with a few bone ones
    rays, rays2 = [], []
    for q in range(46):
        a = math.radians(q * 360 / 46 + r.uniform(-3, 3))
        r0 = r.uniform(41, 50)
        r1 = r0 + r.uniform(14, 62)
        pa = (o + icx + r0 * math.cos(a), o + icy + r0 * math.sin(a))
        pb = (o + icx + r1 * math.cos(a), o + icy + r1 * math.sin(a))
        (rays if q % 4 else rays2).append((pa[0], pa[1], pb[0], pb[1], r.uniform(2.2, 5.0), 0))
    bm = band
    cv.over(lens_mask(cv, rays) * bm, p['ray'], 0.97)
    cv.over(lens_mask(cv, rays2) * bm, p['ray2'], 0.9)
    # the seat: a scissor-cut disc, pink/bone offset print, key outline
    seat_pts = jag_disc(pt(icx, icy), 41.0, r, (8, 14), 1.4)
    seat = cv.poly_mask(seat_pts)
    cv.over(sh(seat, 3.0, 2.6, S), HOT if variant == 'B' else HOT_D, 0.0)
    ring = np.clip(outline_mask(seat, S, 3.2), 0, 1)
    cv.over(ring * bm, p['frame'], 1.0)
    cv.over(ink_grain(cv, seat, 0.4), BONE, 1.0)
    gm = glyph_np(spec['g'], 68 * S)
    gp = place(cv, gm, o + icx, o + icy - 1)
    gp = FT_solid(gp, S)
    cv.over(sh(gp, 2.8, 2.6, S), HOT, 1.0)
    cv.over(gp, KEY, 1.0)
    inner = ndi.binary_erosion(gp > 0.5, iterations=int(1.2 * S)).astype(np.float32)
    hi = np.clip(inner - sh(inner, 2.4, 2.4, S), 0, 1)
    cv.over(ndi.gaussian_filter(hi, 0.3 * S), BONE, 0.9)
    # multiplier x3 (Spin 3): black plate, bone figure, in the band's lower right
    if spec.get('mult'):
        plate_pts = [pt(120, 92), pt(158, 88), pt(160, 118), pt(122, 121)]
        plm = cv.poly_mask(plate_pts)
        cv.over(sh(plm, 2.4, 2.4, S), HOT, 1.0)
        cv.over(plm, KEY, 1.0)
        if nw:
            for q in range(int(spec['mult'])):
                st = cv.poly_mask([pt(129 + q * 9, 96), pt(133 + q * 9, 96), pt(133 + q * 9, 114), pt(129 + q * 9, 114)])
                cv.over(st, BONE, 1.0)
        else:
            tm, _ = text_m(cv, '\u00d7' + spec['mult'], pt(141, 104), 27, ANTON_F, 0.0, rot=-3)
            cv.over(tm, BONE, 1.0)
    # key frame carved around the band
    bring = np.clip(outline_mask(band, S, 2.8), 0, 1)
    cv.over(bring, p['frame'], 1.0)

    # ---- title: black on bone with a pink off-register print
    ty = 152
    if p['title_bg'] is not None:
        tb = cv.poly_mask([pt(14, ty - 20), pt(CW - 14, ty - 22), pt(CW - 13, ty + 19), pt(15, ty + 21)])
        tb = cv.poly_mask(jag_path(pt(14, ty - 20), pt(CW - 14, ty - 22), r, (8, 14), 0.9) + jag_path(pt(CW - 14, ty - 22), pt(CW - 13, ty + 19), r, (8, 14), 0.9)[1:]
                          + jag_path(pt(CW - 13, ty + 19), pt(15, ty + 21), r, (8, 14), 0.9)[1:] + jag_path(pt(15, ty + 21), pt(14, ty - 20), r, (8, 14), 0.9)[1:-1])
        cv.over(sh(tb, 2.6, 2.6, S), KEY, 1.0)
        cv.over(ink_grain(cv, tb, 0.4), BONE, 1.0)
    if nw:
        bar = cv.poly_mask([pt(34, ty - 11), pt(CW - 34, ty - 12), pt(CW - 33, ty + 11), pt(35, ty + 12)])
        cv.over(sh(bar, 2.4, 2.4, S), p['title_off'], 1.0)
        cv.over(bar, p['title'], 1.0)
    else:
        f = font(ANTON_F, 100)
        wtn = f.getlength(spec['nm']) / 100.0
        px = min(40.0, 142.0 / (wtn + 0.045 * len(spec['nm'])))
        tm, _ = text_m(cv, spec['nm'], pt(CW / 2, ty + 1), px, ANTON_F, 0.045 * px, rot=1.2)
        tm = np.clip(ndi.gaussian_filter(tm, 0.25 * S) * 1.2, 0, 1)
        cv.over(sh(tm, 2.6, 2.4, S), p['title_off'], 1.0)
        cv.over(tm, p['title'], 1.0)

    # ---- type band: bone-on-black strip, pink off-register
    tyy = 187
    tw = 74 if spec['fam'] == 'TOWER' else 64
    pts = [pt(CW / 2 - tw / 2 - 5, tyy - 11), pt(CW / 2 + tw / 2 + 2, tyy - 11), pt(CW / 2 + tw / 2 + 6, tyy + 11), pt(CW / 2 - tw / 2 - 1, tyy + 11)]
    tb = cv.poly_mask(pts)
    cv.over(sh(tb, 2.4, 2.2, S), HOT if variant == 'A' else BONE, 1.0)
    cv.over(ink_grain(cv, tb, 0.5), p['type_bg'], 1.0)
    if not nw:
        tm, _ = text_m(cv, spec['fam'], pt(CW / 2 + 0.5, tyy + 0.5), 17.5, ANTON_F, 2.6)
        cv.over(tm, p['type_fg'], 1.0)

    # ---- rules text: 21 px+ plex condensed, black ink, a pink cut under the number
    txt = spec['txt']
    px = 23.0
    while font(PLEX, 100).getlength(txt) / 100.0 * px > CW - 30 and px > 19:
        px -= 0.5
    ly = 220
    if nw:
        for q, wq in enumerate((0.7, 0.45)):
            bar = cv.poly_mask([pt(CW / 2 - wq * 70, ly - 8 + q * 16), pt(CW / 2 + wq * 70, ly - 9 + q * 16), pt(CW / 2 + wq * 70, ly - 3 + q * 16), pt(CW / 2 - wq * 70, ly - 2 + q * 16)])
            cv.over(bar, p['text'], 0.9)
    else:
        tm, wtx = text_m(cv, txt, pt(CW / 2 + 0.5, ly), px, PLEX, 0.0, rot=-0.6)
        tm = np.clip(ndi.gaussian_filter(tm, 0.22 * S) * 1.25, 0, 1)
        if variant == 'B':
            cv.over(sh(tm, 1.2, 1.2, S), BONE, 0.0)
        cv.over(tm, p['text'], 0.98)
        if spec.get('num'):
            x1 = CW / 2 + wtx / 2
            ul = lens_mask(cv, [(o + x1 - 15, o + ly + 12.5, o + x1 + 3, o + ly + 12.0, 3.6, 0.5)])
            cv.over(ul, HOT if variant == 'A' else BONE, 1.0)

    # ---- the player's mark: bottom-right carved bolt
    zz = [pt(CW - 52, 241), pt(CW - 44, 233.5), pt(CW - 37, 241), pt(CW - 29, 233.5), pt(CW - 22, 240)]
    zm = lens_mask(cv, [(zz[i][0], zz[i][1], zz[i + 1][0], zz[i + 1][1], 3.4, 0) for i in range(4)], 0.3)
    cv.over(sh(zm, 1.4, 1.4, S), KEY, 1.0)
    cv.over(zm, HOT if variant == 'A' else BONE, 1.0)

    # ---- the black key frame on the stock, inset: broken at the cost badge
    fr_out = cv.poly_mask(rect_pts(5.5, 5.5, CW - 5.5, CH - 5.5, (9, 19), 0.9))
    fr_in = cv.poly_mask(rect_pts(8.6, 8.6, CW - 8.6, CH - 8.6, (9, 19), 0.9))
    frame = np.clip(fr_out - fr_in, 0, 1)
    cv.over(frame * (1 - band), p['frame'], 0.95)
    # re-cover the band so the frame does not cut it
    # ---- cost badge: RAM coin, flat cyan, key outline, black numeral
    ccx, ccy = 18, 20
    cpts = jag_disc(pt(ccx, ccy), 17.2, r, (7, 12), 0.7)
    coin = cv.poly_mask(cpts)
    cv.over(sh(coin, 2.6, 2.8, S), KEY, 1.0)
    cv.over(np.clip(outline_mask(coin, S, 2.8), 0, 1), KEY, 1.0)
    cv.over(coin, CYAN, 1.0)
    cv.over(np.clip(sh(coin, 0, 0, S) - sh(ndi.binary_erosion(coin > 0.5, iterations=int(2.0 * S)).astype(np.float32), 0, 0, S), 0, 1) * 0.0, KEY, 1.0)
    if nw:
        for q in range(int(cost)):
            xq = ccx + (q - (int(cost) - 1) / 2) * 6.0
            st = cv.poly_mask([pt(xq - 1.3, ccy - 8), pt(xq + 1.3, ccy - 8), pt(xq + 1.3, ccy + 8), pt(xq - 1.3, ccy + 8)])
            cv.over(st, KEY, 1.0)
    else:
        tm, _ = text_m(cv, str(cost), pt(ccx + 0.2, ccy + 1.2), 28, ANTON_F, 0.0)
        cv.over(tm, KEY, 1.0)
    # ---- Trace tab (loud)
    if loud:
        lx, lyy = CW - 50, 16
        bxm = cv.poly_mask([pt(lx - 21, lyy - 12), pt(lx + 21, lyy - 13), pt(lx + 21, lyy + 12), pt(lx - 20, lyy + 13)])
        cv.over(sh(bxm, 2.4, 2.4, S), KEY, 1.0)
        cv.over(np.clip(outline_mask(bxm, S, 2.4), 0, 1), BONE, 1.0)
        cv.over(bxm, VIOLET, 1.0)
        eye = cv.poly_mask([pt(lx - 18, lyy), pt(lx - 10, lyy - 6), pt(lx - 2, lyy), pt(lx - 10, lyy + 6)])
        cv.over(eye, BONE, 1.0)
        cv.over(cv.circle_mask(pt(lx - 10, lyy), 2.9), KEY, 1.0)
        if nw:
            for q in range(int(loud)):
                st = cv.poly_mask([pt(lx + 8 + q * 6 - 1.2, lyy - 7), pt(lx + 8 + q * 6 + 1.2, lyy - 7), pt(lx + 8 + q * 6 + 1.2, lyy + 7), pt(lx + 8 + q * 6 - 1.2, lyy + 7)])
                cv.over(st, BONE, 1.0)
        else:
            tm, _ = text_m(cv, '+' + str(loud), pt(lx + 10.5, lyy + 1.2), 20, ANTON_F, 0.0)
            cv.over(tm, BONE, 1.0)
    return cv


def FT_solid(m, S):
    return np.clip((ndi.gaussian_filter(m, 0.5 * S / 4 * 1.5) - 0.45) * 6, 0, 1)


def down(cv, scale):
    W2, H2 = int(cv.w * scale), int(cv.h * scale)
    P = Image.fromarray(np.clip(cv.P, 0, 255).astype(np.uint8), 'RGB').resize((W2, H2), Image.LANCZOS)
    A = Image.fromarray(np.clip(cv.A * 255, 0, 255).astype(np.uint8), 'L').resize((W2, H2), Image.LANCZOS)
    P2 = np.asarray(P, np.float32)
    A2 = np.asarray(A, np.float32) / 255.0
    rgb = P2 / np.maximum(A2, 1e-4)[..., None]
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), A2 * 255]).astype(np.uint8), 'RGBA')


def render_card(name, variant=None, seed=0, ss=4, scale=2):
    v = LT.VARIANT[0]
    cv = card(name, v, seed, 4)
    im = down(cv, scale)
    return print_texture(im, seed=seed + 5, dens=0.006, pink_dens=0.004)


if __name__ == '__main__':
    import time
    import asm_r2
    asm_r2.setup()
    v = sys.argv[1] if len(sys.argv) > 1 else 'A'
    LT.VARIANT[0] = v
    t = time.time()
    names = ['Brace', 'Spin3', 'Trigger', 'Twist']
    ims = [render_card(n, v, seed=i * 3 + 1) for i, n in enumerate(names)]
    sheet = Image.new('RGBA', (ims[0].width * 4 + 40, ims[0].height + 20), (40, 36, 62, 255))
    for i, im in enumerate(ims):
        sheet.alpha_composite(im, (10 + i * (im.width + 6), 10))
    sheet.save('D:/rc_scratch/combat_redesign/punk/linocut/out/lc_cards_%s.png' % v)
    print('cards', round(time.time() - t, 1))
