"""Round 2 card renderer (cards cluster).  One renderer for the R2 pick ('P') and its one variant ('V'), plus the four LATENT states.
Every element is a function here (list per element in NOTES.md).  Cards are drawn at 3x, rotated at 3x, reduced once.
V keys: frame hdr cost art icon mult title type rules loud hover liner nw   each 'P' | 'V'.
State overlays (latent): lat = ('unaff'|'commit'|'exh'|'key', 'A'|'B'|'C'), key = digit."""
import sys, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from cv_lib import *
from bb_lib import _font
import kglyph2 as KG

K = 3
P = 18
INK_ = (12, 10, 22)
BODY = (16, 18, 30)
DIECUT = (250, 250, 246)
VIOLET = (160, 60, 255)
TXT_HI = (242, 246, 255)
TXT_MID = (175, 192, 214)
TXT_LO = (122, 136, 156)
PLAN = (255, 226, 0)
FAMC = {'TOWER': CYAN, 'WAVE': ORANGE}
BASE_V = dict(fan='P', frame='P', hdr='P', cost='P', art='P', icon='P', mult='P', title='P', type='P', rules='P', loud='P', hover='P', liner='P', nw='P')
BORDER = 12
HDR_H = {'P': 30, 'V': 34}
TYPE_H, TITLE_H, RULES_H = 20, 34, 44
SHADOW = (0.5, 8, (4, 8))
SHADOW_GROWN = (0.5, 14, (8, 16))


def fam_mul(c, m, a=255):
    return tuple(int(v * m) for v in c[:3]) + (a,)


class Cv(L2):
    def __init__(self, w, h, k=K):
        self.k = k
        self.im = Image.new('RGBA', (int(w * k), int(h * k)), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def tf(self, s, px, kind='anton'):
        return self.tw(s, px, kind)

    def put(self, img, x, y):
        self.im.alpha_composite(img, (int(round(x * self.k)), int(round(y * self.k))))


def arr_img(rgb, a=None):
    rgb = np.clip(rgb, 0, 1)
    if a is None:
        a = np.ones(rgb.shape[:2], np.float32)
    return Image.fromarray((np.dstack([rgb, np.clip(a, 0, 1)]) * 255 + 0.5).astype(np.uint8), 'RGBA')


def grid(w, h, k=K):
    ys, xs = np.mgrid[0:int(round(h * k)), 0:int(round(w * k))].astype(np.float32)
    return (xs + 0.5) / k, (ys + 0.5) / k


def rr_mask(w, h, box, r, k=K):
    m = Image.new('L', (int(w * k), int(h * k)), 0)
    ImageDraw.Draw(m).rounded_rectangle([v * k for v in box], radius=r * k, fill=255)
    return m


# ------------------------------------------------------------------ layout
def layout(V, W, H):
    b = BORDER
    hdr = HDR_H[V['hdr']]
    bx0, by0, bx1, by1 = P + b, P + b, P + W - b, P + H - b
    R = {'body': (bx0, by0, bx1, by1)}
    y = by0
    R['hdr'] = (bx0, y, bx1, y + hdr)
    y += hdr
    art_h = (by1 - by0) - hdr - TITLE_H - TYPE_H - RULES_H
    R['art'] = (bx0, y, bx1, y + art_h)
    y += art_h
    R['title'] = (bx0, y, bx1, y + TITLE_H)
    y += TITLE_H
    R['type'] = (bx0, y, bx1, y + TYPE_H)
    y += TYPE_H
    R['rules'] = (bx0, y, bx1, by1)
    return R, b


# ------------------------------------------------------------------ card_frame
def frame_under(cv, ctx):
    W, H = ctx['W'], ctx['H']
    cv.rect([P, P, P + W, P + H], fill=DIECUT, r=16)
    cv.rect(list(ctx['R']['body']), fill=BODY, r=10)


def frame_over(cv, ctx):
    bx0, by0, bx1, by1 = ctx['R']['body']
    cv.rect([bx0, by0, bx1, by1], outline=INK_, w=3 if ctx['V']['frame'] == 'P' else 4, r=10)


# ------------------------------------------------------------------ card_header_strip
def hdr_draw(cv, ctx):
    x0, y0, x1, y1 = ctx['R']['hdr']
    cv.rect([x0, y0, x1, y1], fill=(8, 10, 19), r=0)
    cv.line([(x0, y1), (x1, y1)], INK_, 3)


def hy_of(ctx):
    h = ctx['R']['hdr']
    return (h[1] + h[3]) / 2 - 0.5


# ------------------------------------------------------------------ cost_badge (the RAM coin)
def coin(cv, cx, cy, d, n, nw=False, digit_px=None, lit=True):
    """ASSEMBLY (Y4): the coin body is obj2.coin_img(d) (lit) or its spent socket (n = 0); the Anton 24 INK digit stays."""
    import obj2
    dp = digit_px or round(d * 24 / 34)
    if n > 0 and lit:
        state, col = 'lit', INK_
    else:
        state, col = 'spent', (TXT_MID if n == 0 else TXT_LO)
    img, sz, kk = obj2.coin_img(d, state, False, False)
    t = img.resize((int(sz * cv.k), int(sz * cv.k)), Image.LANCZOS)
    cv.im.alpha_composite(t, (int(round((cx - sz / 2) * cv.k)), int(round((cy - sz / 2) * cv.k))))
    if nw:
        if n > 0:
            for i in range(n):
                px = cx + (i - (n - 1) / 2) * 8
                cv.ellipse([px - 3, cy - 3, px + 3, cy + 3], fill=col)
    else:
        cv.text((cx, cy + 1.2), str(n), dp, 'anton', fill=col, anchor='mm')


def cost_draw(cv, ctx):
    n = ctx['c']['cost']
    bx0 = ctx['R']['body'][0]
    hy = hy_of(ctx)
    d = 34 if ctx['V']['cost'] == 'P' else 38
    cx = bx0 + 12 + d / 2
    coin(cv, cx, hy, d, n, ctx['nw'], lit=not ctx.get('unaff'))
    ctx['cost_r'] = cx + d / 2


# ------------------------------------------------------------------ art_band
def art_draw(cv, ctx):
    v = ctx['V']['art']
    x0, y0, x1, y1 = ctx['R']['art']
    w, h = x1 - x0, y1 - y0
    fam = np.array(ctx['famc'], np.float32) / 255
    xs, ys = grid(w, h)
    if v == 'P':
        val = 0.44 - 0.12 * (ys / h)
        scan = 1 - 0.12 * (0.5 + 0.5 * np.sin(2 * np.pi * ys / 6.0))
    else:
        val = 0.50 - 0.16 * (ys / h) + 0.06 * np.clip(1 - np.abs(xs - w / 2) / (w * 0.5), 0, 1) * (1 - ys / h)
        scan = 1 - 0.09 * (0.5 + 0.5 * np.sin(2 * np.pi * ys / 8.0))
    rgb = fam[None, None, :] * (val * scan)[..., None]
    cv.put(arr_img(rgb), x0, y0)
    cv.line([(x0, y1), (x1, y1)], INK_, 3)


# ------------------------------------------------------------------ icon + multiplier
def icon_geom(ctx):
    x0, y0, x1, y1 = ctx['R']['art']
    h = y1 - y0
    p = (66 if ctx['V']['icon'] == 'P' else 72)
    p = min(p, h - 8)
    return (x0 + x1) / 2, (y0 + y1) / 2, p


def icon_draw(cv, ctx):
    cx, cy, p = icon_geom(ctx)
    x = ctx['c'].get('x')
    if x and not ctx['nw']:
        sx0, sx1 = ctx['R']['art'][0] + 12, ctx['R']['art'][2] - 12
        tw = cv.tw('×' + x, 34)
        tot = p + 2 + tw
        left = (sx0 + sx1) / 2 - tot / 2
        ctx['mult_xy'] = (left + p + 2, cy + 3)
        cx = left + p / 2
    k = cv.k
    name = KG.card_glyph(ctx['name'])
    g = glyph_rgba(name, int(p * k), max(2, int(p * k * 0.075)))
    sh = Image.new('RGBA', g.size, (0, 0, 0, 0))
    sh.putalpha(g.split()[3].point(lambda a: int(a * 0.55)).filter(ImageFilter.GaussianBlur(2.2 * k)))
    cv.im.alpha_composite(sh, (int(cx * k - g.width / 2), int(cy * k - g.height / 2 + 3 * k)))
    cv.im.alpha_composite(g, (int(cx * k - g.width / 2), int(cy * k - g.height / 2)))


def mult_draw(cv, ctx):
    x = ctx['c'].get('x')
    if not x or ctx['nw']:
        return
    px = 34 if ctx['V']['mult'] == 'P' else 38
    cv.text(ctx['mult_xy'], '×' + x, px, 'anton', fill=(255, 255, 255), anchor='lm', stroke=3)


# ------------------------------------------------------------------ title / type / rules
def fit_px(cv, s, maxw, px0, pxmin, kind='anton'):
    px = px0
    while px > pxmin and cv.tw(s, px, kind) > maxw:
        px -= 1
    return px


def title_draw(cv, ctx):
    if ctx['nw']:
        return
    s = ctx['c'].get('nm', ctx['name'].upper())
    x0, y0, x1, y1 = ctx['R']['title']
    yc = (y0 + y1) / 2
    v = ctx['V']['title']
    px = fit_px(cv, s, (x1 - x0) - 24, 28, 22)
    cv.text((x0 + 12, yc + 1), s, px, 'anton', fill=(255, 255, 255), anchor='lm', stroke=2.2 if v == 'P' else 2.8)


def type_draw(cv, ctx):
    x0, y0, x1, y1 = ctx['R']['type']
    s = ctx['famn']
    fam = ctx['famc']
    yc = (y0 + y1) / 2
    hh = 8.5 if ctx['V']['type'] == 'P' else 9.5
    w = cv.tw(s, 15, 'mono') + 16 if not ctx['nw'] else 46
    cv.rect([x0 + 12, yc - hh, x0 + 12 + w, yc + hh], fill=fam, outline=INK_, w=1.6, r=4)
    if not ctx['nw']:
        cv.text((x0 + 20, yc + 0.5), s, 15, 'mono', fill=INK_, anchor='lm')
    cv.line([(x0 + 16 + w, yc), (x1 - 12, yc)], fam_mul(fam, 0.5)[:3], 1.4)


def reg_font(px, k):
    return _font('IBMPlexSansCondensed-Regular.ttf', int(px * k))


def med_font(px, k):
    return _font('IBMPlexSansCondensed-Medium.ttf', int(px * k))


def wrap_words(text, maxw, px, k):
    words = text.split()
    fr, fm = reg_font(px, k), med_font(px, k)
    sp = fr.getlength(' ') / k
    lines, cur, cw = [], [], 0
    for i, wd in enumerate(words):
        f = fm if i == 0 else fr
        l = f.getlength(wd) / k
        if cur and cw + sp + l > maxw:
            lines.append(cur)
            cur, cw = [], 0
        if cur:
            cw += sp
        cur.append((wd, i == 0, cw))
        cw += l
    lines.append(cur)
    return lines


def rules_draw(cv, ctx):
    if ctx['nw']:
        return
    x0, y0, x1, y1 = ctx['R']['rules']
    txt = ctx['c']['txt']
    k = cv.k
    m = 12
    maxw = (x1 - x0) - m - (22 if ctx['V']['rules'] == 'P' else 18)
    lines = wrap_words(txt, maxw, 16, k)[:2]
    lh = 19
    exh = ctx.get('lat') == ('exh', 'A')
    n_l = len(lines) + (1 if exh else 0)
    if exh:
        lh = 16
    top = (y0 + y1) / 2 - n_l * lh / 2 + lh / 2 + 0.5
    for li, ln in enumerate(lines):
        y = top + li * lh
        for wd, kw, dx in ln:
            col, f = (TXT_HI if kw else TXT_MID), (med_font if kw else reg_font)
            cv.d.text(((x0 + m + dx) * k, y * k), wd, font=f(16, k), fill=col + (255,), anchor='lm')
    if exh:
        y = top + len(lines) * lh
        cv.d.text(((x0 + m) * k, y * k), 'Exhaust.', font=med_font(16, k), fill=TXT_HI + (255,), anchor='lm')


# ------------------------------------------------------------------ loud tab (a TRACE square)
def loud_draw(cv, ctx):
    n = ctx['c'].get('loud') or 0
    if not n:
        return
    v = ctx['V']['loud']
    bx0, by0, bx1, by1 = ctx['R']['body']
    hy = hy_of(ctx)
    h, w = (26, 50) if v == 'P' else (30, 56)
    xr = bx1 - 12
    cv.rect([xr - w, hy - h / 2, xr, hy + h / 2], fill=VIOLET, outline=INK_, w=2.4, r=3)
    import obj2      # ASSEMBLY (Y4): the Trace square (inner hairline construction) leads the tab at 26 px
    img_, sz_, kk_ = obj2.sq_img('lit')
    side_ = 26 + 8 * 26 / 22.0
    t_ = img_.resize((int(side_ * cv.k), int(side_ * cv.k)), Image.LANCZOS)
    cv.im.alpha_composite(t_, (int(round((xr - w + 13 - side_ / 2) * cv.k)), int(round((hy - side_ / 2) * cv.k))))
    cv.glyph('X_EYE', 18 if v == 'P' else 20, (xr - w + 15, hy), (255, 255, 255))
    if not ctx['nw']:
        cv.text((xr - w + 28, hy + 1), '+%d' % n, 20 if v == 'P' else 22, 'anton', fill=(255, 255, 255), anchor='lm', stroke=1.8)
    else:
        for i in range(n):
            cv.rect([xr - w + 30 + i * 7, hy - 6, xr - w + 34 + i * 7, hy + 6], fill=(255, 255, 255), outline=INK_, w=1.0, r=1.5)


# ------------------------------------------------------------------ nowords (cards_nowords)
def nw_draw(cv, ctx):
    if not ctx['nw']:
        return
    bx0, by0, bx1, by1 = ctx['R']['body']
    yt = ctx['R']['title'][1] + TITLE_H / 2
    cv.rect([bx0 + 12, yt - 5.5, bx0 + 12 + 0.62 * (bx1 - bx0), yt + 5.5], fill=(255, 255, 255, 120), r=5)
    yr = ctx['R']['rules'][1]
    for i, f in enumerate((0.62, 0.40)):
        cv.rect([bx0 + 12, yr + 9 + i * 14, bx0 + 12 + f * (bx1 - bx0), yr + 15 + i * 14], fill=(255, 255, 255, 52), r=3)


def rr_path_k(x0, y0, x1, y1, r, n=10):
    pts = []
    for (cx, cy, a0) in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pts.append(pts[0])
    return pts


rr_path = rr_path_k


# ------------------------------------------------------------------ latent states (card_unaffordable / committed / exhaust / key hint)
def lat_top(ctx, im):
    lat = ctx.get('lat')
    if not lat:
        return im
    kind, o = lat
    W, H = ctx['W'], ctx['H']
    k = K
    bx0, by0, bx1, by1 = ctx['R']['body']
    w, h = im.size
    if kind == 'unaff':
        a = np.asarray(im, np.float32) / 255
        xs, ys = grid(w / k, h / k)
        g = a[..., :3].mean(axis=2, keepdims=True)
        if o == 'A':        # dim glass: desaturate, 52 percent value
            a[..., :3] = (a[..., :3] * 0.25 + g * 0.75) * 0.52
        elif o == 'B':      # frosted shutter over art and text; header and cost stay
            m = (ys > ctx['R']['art'][1]).astype(np.float32)[..., None]
            a[..., :3] = a[..., :3] * (1 - m) + m * (g * 0.40 + np.array([0.03, 0.05, 0.09]) * 0.8)
        else:               # diagonal ink hatch
            hat = (0.5 + 0.5 * np.sin(2 * np.pi * (xs + ys) / 9.0) > 0.62).astype(np.float32)[..., None] * 0.55
            a[..., :3] = (a[..., :3] * 0.5 + g * 0.5) * 0.7 * (1 - hat) + np.array([0.05, 0.04, 0.09]) * hat
        out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), 'RGBA')
        out.putalpha(im.split()[3])
        cv2 = Cv(w / k, h / k)
        if o == 'C':
            cv2.rect([bx0, by0, bx1, by1], outline=TXT_LO, w=3, r=10)
        out.alpha_composite(cv2.im)
        cvc = Cv(w / k, h / k)
        d = 34
        coin(cvc, bx0 + 12 + d / 2, hy_of(ctx), d, ctx['c']['cost'], ctx['nw'], lit=False)
        out.alpha_composite(cvc.im)
        return out
    cv2 = Cv(w / k, h / k)
    if kind == 'commit':
        if o == 'A':        # pencil ring around the die-cut
            pts = rr_path_k(P - 4, P - 4, P + W + 4, P + H + 4, 20)
            cv2.line(pts, (6, 3, 8), 10)
            cv2.line(pts, PLAN, 6)
        elif o == 'B':      # wax tick on the art band
            ax0, ay0, ax1, ay1 = ctx['R']['art']
            cx, cy = ax1 - 22, ay0 + 22
            pts = [(cx - 12, cy + 1), (cx - 3, cy + 11), (cx + 14, cy - 11)]
            cv2.line(pts, (6, 3, 8), 11)
            cv2.line(pts, PLAN, 6.5)
        else:               # plan underline across the foot
            y = by1 + 2
            pts = [(bx0 - 4, y + 1), (bx0 + 40, y), (bx1 + 4, y + 1.5)]
            cv2.line(pts, (6, 3, 8), 11)
            cv2.line(pts, PLAN, 6.5)
    elif kind == 'exh':
        if o == 'B':
            x0, y0, x1, y1 = ctx['R']['type']
            yc = (y0 + y1) / 2
            ww = cv2.tw('EXHAUST', 15, 'mono') + 14
            cv2.rect([x1 - 12 - ww, yc - 8.5, x1 - 12, yc + 8.5], fill=TXT_HI, outline=INK_, w=1.6, r=4)
            cv2.text((x1 - 12 - ww + 7, yc + 0.5), 'EXHAUST', 15, 'mono', fill=INK_, anchor='lm')
        elif o == 'C':
            ax0, ay0, ax1, ay1 = ctx['R']['art']
            tape = Cv(100, 24)
            tape.rect([1, 1, 99, 23], fill=TXT_HI, outline=INK_, w=2.2, r=2)
            tape.text((50, 12.5), 'EXHAUST', 15, 'mono', fill=INK_, anchor='mm')
            t = tape.im.rotate(-14, resample=Image.BICUBIC, expand=True)
            cv2.im.alpha_composite(t, (int((ax1 - 62) * k - t.width / 2), int((ay1 - 20) * k - t.height / 2)))
    elif kind == 'key':
        key = str(ctx.get('key', 1))
        hy = hy_of(ctx)
        if o == 'A':
            cx = ctx['cost_r'] + 16
            cv2.rect([cx - 10, hy - 11, cx + 10, hy + 11], fill=(36, 44, 62), outline=INK_, w=2, r=4)
            cv2.rect([cx - 7.5, hy - 9, cx + 7.5, hy + 5.5], fill=(58, 70, 94), r=3)
            cv2.text((cx, hy), key, 16, 'mono', fill=TXT_HI, anchor='mm')
        elif o == 'B':
            cx = (bx0 + bx1) / 2 - 20
            y1 = P + H
            cv2.rect([cx - 15, y1 - 14, cx + 15, y1 + 12], fill=DIECUT, outline=INK_, w=2.4, r=6)
            cv2.text((cx, y1 + 1.5), key, 22, 'anton', fill=INK_, anchor='mm')
        else:
            ax0, ay0, ax1, ay1 = ctx['R']['art']
            cv2.text((ax0 + 12, ay1 - 18), key, 30, 'anton', fill=(255, 255, 255, 120), anchor='lm', stroke=2.2)
    out = im.copy()
    out.alpha_composite(cv2.im)
    return out


# ------------------------------------------------------------------ assembly
def card_hi(name, V, state='rest', nw=False, W=176, H=232, card=None, lat=None, key=None):
    old = NOW['words']
    NOW['words'] = True
    try:
        import cv_chrome as CH
        c = card or CH.CARDS[name]
        ctx = dict(name=name, c=c, V=V, nw=nw, W=W, H=H, famn=c['fam'], famc=FAMC[c['fam']], state=state, lat=lat, key=key)
        ctx['unaff'] = bool(lat and lat[0] == 'unaff')
        ctx['R'], ctx['b'] = layout(V, W, H)
        cw, ch = W + 2 * P, H + 2 * P
        cv = Cv(cw, ch)
        frame_under(cv, ctx)
        body = Cv(cw, ch)
        hdr_draw(body, ctx)
        art_draw(body, ctx)
        icon_draw(body, ctx)
        mult_draw(body, ctx)
        if nw:
            nw_draw(body, ctx)
        title_draw(body, ctx)
        type_draw(body, ctx)
        rules_draw(body, ctx)
        topl = Cv(cw, ch)
        cost_draw(topl, ctx)
        loud_draw(topl, ctx)
        bx0, by0, bx1, by1 = ctx['R']['body']
        m = rr_mask(cw, ch, [bx0, by0, bx1, by1], 10)
        body.im.putalpha(ImageChops.multiply(body.im.split()[3], m))
        cv.im.alpha_composite(body.im)
        frame_over(cv, ctx)
        cv.im.alpha_composite(topl.im)
        im = lat_top(ctx, cv.im)
        if state == 'hover':
            im = peel(im, ctx, 46 if V['hover'] == 'P' else 58)
        return im, ctx
    finally:
        NOW['words'] = old


# ------------------------------------------------------------------ hover (card_hover_grow)
def peel(im, ctx, s=46):
    k = K
    W, H = ctx['W'], ctx['H']
    x1, y1 = P + W, P + H
    w, h = im.size
    xs, ys = grid(w / k, h / k)
    cut = (xs - (x1 - s)) + (ys - (y1 - s)) > s
    alpha = np.asarray(im.split()[3], np.float32) / 255
    new = im.copy()
    new.putalpha(Image.fromarray((np.where(cut, 0, alpha) * 255).astype(np.uint8)))
    tri = [((x1 - s) * k, y1 * k), (x1 * k, (y1 - s) * k), ((x1 - s) * k, (y1 - s) * k)]
    mk = Image.new('L', im.size, 0)
    ImageDraw.Draw(mk).polygon(tri, fill=255)
    sh = mk.filter(ImageFilter.GaussianBlur(5 * k)).point(lambda v: int(v * 0.55))
    shl = Image.new('RGBA', im.size, (0, 0, 0, 0))
    shl.putalpha(ImageChops.multiply(sh.transform(im.size, Image.AFFINE, (1, 0, -3 * k, 0, 1, -3 * k)), new.split()[3]))
    new.alpha_composite(shl)
    g = np.clip(((xs - (x1 - s)) + (ys - (y1 - s))) / s, 0, 1)
    shade = 0.80 + 0.20 * (1 - g)
    rgb = np.dstack([np.full(g.shape, 250 / 255, np.float32) * shade, np.full(g.shape, 250 / 255, np.float32) * shade, np.full(g.shape, 246 / 255, np.float32) * shade])
    new.alpha_composite(arr_img(rgb, np.asarray(mk, np.float32) / 255))
    dd = ImageDraw.Draw(new)
    dd.line([((x1 - s) * k, y1 * k), (x1 * k, (y1 - s) * k)], fill=INK_ + (255,), width=int(2.2 * k))
    dd.line([((x1 - s) * k, y1 * k), ((x1 - s) * k, (y1 - s) * k), (x1 * k, (y1 - s) * k)], fill=INK_ + (255,), width=int(2.2 * k))
    return new


# ------------------------------------------------------------------ liner (played_liner)
def liner_hi(name, V, W=176, H=232, card=None):
    old = NOW['words']
    NOW['words'] = True
    try:
        import cv_chrome as CH
        c = card or CH.CARDS[name]
        v = V['liner']
        fam = FAMC[c['fam']]
        cw, ch = W + 2 * P, H + 2 * P
        cv = Cv(cw, ch)
        gname = KG.card_glyph(name)
        if v == 'P':
            cv.rect([P, P, P + W, P + H], fill=(8, 10, 20, 170), r=16)
            gcol, tcol = (150, 165, 188), (206, 218, 236)
        else:
            cv.rect([P, P, P + W, P + H], fill=(8, 10, 20, 178), r=16)
            cv.rect([P + 12, P + 12, P + W - 12, P + H - 12], fill=fam_mul(fam, 0.18, 120), r=8)
            gcol, tcol = fam_mul(fam, 0.85)[:3], fam_mul(fam, 1.0)[:3]
        pts = rr_path(P + 1.5, P + 1.5, P + W - 1.5, P + H - 1.5, 15)
        cv.line(pts, (225, 232, 245, 230), 2.4, dash=(9, 6))
        g = glyph_rgba(gname, int(54 * K), int(54 * K * 0.075), fill=gcol)
        g.putalpha(g.split()[3].point(lambda a: int(a * 0.8)))
        cv.im.alpha_composite(g, (int((P + W / 2) * K - g.width / 2), int((P + H / 2 - 12) * K - g.height / 2)))
        cv.text((P + W / 2, P + H / 2 + 44), 'PLAYED', 19, 'mono', fill=tcol, anchor='mm', stroke=2)
        return cv.im
    finally:
        NOW['words'] = old
