"""ACTIONS kit: shared sticker material (die-cut, plate, ink, one shadow, vinyl gradient), non-word glyphs, wax pencil, refund token.
Everything draws at 1080p coordinates. Sticker pieces return RGBA at 1x (so shadow_paste can lift them). Lifted by the assembler as-is."""
import sys, math, random
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from e10lib import *
import bb_lib as BB

LIME = (150, 255, 70)          # 2.10 focus language
VY_TOP, VY_BOT = (255, 238, 96), (255, 182, 14)       # vinyl yellow #FFEE60 -> #FFB60E
VC_TOP, VC_BOT = (150, 240, 255), (44, 178, 228)      # vinyl cyan, a step off the terminal cyan
PAPER = (250, 250, 247)
SHADOW = dict(k=0.5, blur=8, off=(4, 8))               # ONE shadow for stickers and cards
S3 = 3                                                 # supersample


def border_for(size):
    """die-cut border = 0.14 x type size, max 12 px"""
    return max(3, min(12, int(round(0.14 * size))))


# ----------------------------------------------------------------------------- PIL stroke helpers (supersampled space)
def pstroke(d, pts, col, w, closed=False, cap=True):
    pts = list(pts)
    if closed:
        pts = pts + [pts[0]]
    d.line(pts, fill=col, width=int(round(w)), joint='curve')
    if cap:
        r = w / 2
        for (x, y) in (pts[0], pts[-1]):
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)


def pink(d, pts, col, w, ink=INK, iw=None, closed=False):
    """inked stroke: ink under, colour over"""
    iw = iw if iw is not None else w * 0.45 + 1
    pstroke(d, pts, ink, w + iw, closed)
    pstroke(d, pts, col, w, closed)


# ----------------------------------------------------------------------------- non-word glyphs (drawn into a PIL draw, centre cx,cy, radius R; px at supersample scale)
def g_go_ring(d, cx, cy, R, col, ink=INK):
    """arrow through a ring: the committing verb"""
    w = R * 0.22
    n = 40
    ring = [(cx + R * 0.62 * math.cos(2 * math.pi * i / n), cy + R * 0.62 * math.sin(2 * math.pi * i / n)) for i in range(n)]
    pink(d, ring, col, w, ink, closed=True)
    pink(d, [(cx - R * 1.0, cy), (cx + R * 0.78, cy)], col, w * 1.05, ink)
    pink(d, [(cx + R * 0.38, cy - R * 0.5), (cx + R * 1.02, cy), (cx + R * 0.38, cy + R * 0.5)], col, w * 1.05, ink)


def g_go_bar(d, cx, cy, R, col, ink=INK):
    """arrow into a bar: the line is crossed, the turn ends"""
    w = R * 0.24
    pink(d, [(cx - R * 1.0, cy), (cx + R * 0.45, cy)], col, w, ink)
    pink(d, [(cx + R * 0.0, cy - R * 0.5), (cx + R * 0.55, cy), (cx + R * 0.0, cy + R * 0.5)], col, w, ink)
    pink(d, [(cx + R * 0.95, cy - R * 0.8), (cx + R * 0.95, cy + R * 0.8)], col, w * 1.1, ink)


def g_enter(d, cx, cy, R, col, ink=INK):
    """the commit key: return arrow"""
    w = R * 0.24
    pink(d, [(cx + R * 0.85, cy - R * 0.8), (cx + R * 0.85, cy + R * 0.25), (cx - R * 0.65, cy + R * 0.25)], col, w, ink)
    pink(d, [(cx - R * 0.2, cy - R * 0.35), (cx - R * 0.85, cy + R * 0.25), (cx - R * 0.2, cy + R * 0.85)], col, w, ink)


def _head(pts_end, dirv, size):
    ex, ey = pts_end
    out = []
    for sg in (1, -1):
        a = dirv + math.pi + sg * 0.62
        out.append((ex + size * math.cos(a), ey + size * math.sin(a)))
    return out


def g_undo(d, cx, cy, R, col, ink=INK, w=None):
    """counter-clockwise arrow: arc over the top, head at the left end"""
    w = w or R * 0.26
    pts = []
    for i in range(0, 231, 8):
        a = math.radians(-20 - i)
        pts.append((cx + R * 0.7 * math.cos(a), cy + R * 0.7 * math.sin(a)))
    pink(d, pts, col, w, ink)
    a = math.radians(-20 - 230)
    dirv = math.atan2(-math.cos(a), math.sin(a))
    h1, h2 = _head(pts[-1], dirv, R * 0.62)
    pink(d, [h1, pts[-1], h2], col, w, ink)


def g_undo_tick(d, cx, cy, R, col, ink=INK, w=None):
    """a back arrow with a tail: shaft left, head left"""
    w = w or R * 0.26
    pink(d, [(cx + R * 0.9, cy + R * 0.5), (cx + R * 0.9, cy - R * 0.1), (cx - R * 0.5, cy - R * 0.1)], col, w, ink)
    pink(d, [(cx + R * 0.05, cy - R * 0.7), (cx - R * 0.75, cy - R * 0.1), (cx + R * 0.05, cy + R * 0.5)], col, w, ink)


def g_tick(d, cx, cy, R, col, ink=None, w=None):
    w = w or R * 0.3
    pts = [(cx - R * 0.8, cy + R * 0.05), (cx - R * 0.25, cy + R * 0.6), (cx + R * 0.85, cy - R * 0.6)]
    if ink:
        pstroke(d, pts, ink, w + 3)
    pstroke(d, pts, col, w)


def g_breaker(d, cx, cy, R, col, ink=INK):
    """class emblem: a ring broken by a bolt (the Breaker breaks the line)"""
    w = R * 0.24
    n = 30
    arc1 = [(cx + R * 0.8 * math.cos(math.radians(a)), cy + R * 0.8 * math.sin(math.radians(a))) for a in range(-20, 232, 9)]
    arc2 = [(cx + R * 0.8 * math.cos(math.radians(a)), cy + R * 0.8 * math.sin(math.radians(a))) for a in range(262, 338, 9)]
    pink(d, arc1, col, w, ink)
    pink(d, arc2, col, w, ink)
    pink(d, [(cx + R * 0.35, cy - R * 0.95), (cx - R * 0.15, cy - R * 0.1), (cx + R * 0.2, cy + R * 0.1), (cx - R * 0.4, cy + R * 0.95)], col, w * 0.9, ink)


def tally(d, x, y, n, h, col, ink=INK, w=None, gap=None):
    """n tally strokes in groups of 5 (5th is the slash). returns width"""
    w = w or max(2, h * 0.16)
    gap = gap or h * 0.34
    xx = x
    k = 0
    while k < n:
        g = min(5, n - k)
        for i in range(min(g, 4)):
            pstroke(d, [(xx + i * gap, y - h / 2), (xx + i * gap, y + h / 2)], ink, w + 2.5)
        for i in range(min(g, 4)):
            pstroke(d, [(xx + i * gap, y - h / 2), (xx + i * gap, y + h / 2)], col, w)
        if g == 5:
            pstroke(d, [(xx - gap * 0.5, y + h * 0.35), (xx + 3 * gap + gap * 0.5, y - h * 0.35)], ink, w + 2.5)
            pstroke(d, [(xx - gap * 0.5, y + h * 0.35), (xx + 3 * gap + gap * 0.5, y - h * 0.35)], col, w)
            xx += 3 * gap + gap * 1.6
        else:
            xx += (g - 1) * gap + gap * 1.6
        k += g
    return xx - x


# ----------------------------------------------------------------------------- the one sticker material
def _mask(shape, w, h, S, r):
    m = Image.new('L', (int(w * S), int(h * S)), 0)
    d = ImageDraw.Draw(m)
    if shape == 'circle':
        d.ellipse([0, 0, w * S - 1, h * S - 1], fill=255)
    elif shape == 'tag':        # pentagon pointing left: the verb points back into the board
        n = h * 0.34
        d.polygon([(0, h * S / 2), (n * S, 0), (w * S - 1, 0), (w * S - 1, h * S - 1), (n * S, h * S - 1)], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(r * S * 0.55)).point(lambda v: 255 if v > 128 else 0)
    else:
        d.rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=r * S, fill=255)
    return m


def vinyl2(w, h, size, content, top=VY_TOP, bot=VY_BOT, tilt=-3, mat='A', shape='rr', ink=INK, border=None, grad=True, r_in=10, r_out=16):
    """One sticker. w,h = plate size (1x px). content(draw, S, w, h) draws the plate content at supersample S in plate-local coordinates.
    Die-cut border 0.14 x size (max 12), plate with 3 px ink edge, r_out 16 / r_in 10, vinyl gradient. mat: A matte gradient, B halftone print, C gloss lacquer."""
    S = S3
    b = border if border is not None else border_for(size)
    pad = b + 3
    cw, ch = w + 2 * pad, h + 2 * pad
    plate = _mask(shape, w, h, S, r_in)
    # die-cut mask = plate grown by b (round), on the big canvas
    big = Image.new('L', (cw * S, ch * S), 0)
    big.paste(plate, (pad * S, pad * S))
    grown = big.filter(ImageFilter.GaussianBlur(b * S / 1.7)).point(lambda v: 255 if v > 14 else 0).filter(ImageFilter.GaussianBlur(S * 0.6))
    pm = np.asarray(big, np.float32) / 255
    gm = np.asarray(grown, np.float32) / 255
    rgba = np.zeros((ch * S, cw * S, 4), np.float32)
    rgba[..., :3] = np.array(PAPER, np.float32)
    rgba[..., 3] = gm * 255
    # paper edge: a slightly greyer rim (cut edge)
    rim = np.clip(gm - np.asarray(grown.filter(ImageFilter.GaussianBlur(S * 1.6)), np.float32) / 255 * 1.0, 0, 1)
    rgba[..., :3] -= rim[..., None] * 18
    # plate fill: vertical vinyl gradient
    yy = (np.arange(ch * S, dtype=np.float32) - pad * S) / (h * S)
    t = np.clip(yy, 0, 1)[:, None, None]
    top_, bot_ = np.array(top, np.float32), np.array(bot, np.float32)
    fill = top_ * (1 - t) + bot_ * t if grad else np.broadcast_to(top_, (ch * S, 1, 3))
    fill = np.broadcast_to(fill, (ch * S, cw * S, 3)).copy()
    if mat == 'C':
        # lacquer: specular band + warm edge darkening
        xx = (np.arange(cw * S, dtype=np.float32) - pad * S) / (w * S)
        band = np.clip(1 - np.abs((yy[:, None] * 1.0 - 0.18 - 0.0 * xx[None, :])) / 0.16, 0, 1)
        band = band * np.clip(1.15 - xx[None, :] * 0.9, 0.15, 1)
        fill += band[..., None] * 70
        fill -= np.clip(yy[:, None] - 0.78, 0, 1)[..., None] * 60 * 0.5
    if mat == 'B':
        # halftone print: dots darken toward the bottom, plus fine paper grain
        gy, gx = np.mgrid[0:ch * S, 0:cw * S].astype(np.float32)
        pitch = 4.2 * S
        u = (gx * 0.866 + gy * 0.5) % pitch - pitch / 2
        v = (-gx * 0.5 + gy * 0.866) % pitch - pitch / 2
        rr = np.hypot(u, v)
        rad = pitch * 0.5 * np.clip(t[:, :, 0], 0, 1) ** 1.1 * 0.95
        dots = (rr < rad).astype(np.float32)
        fill = fill * (1 - dots[..., None] * 0.22) + np.array([120, 40, 0], np.float32) * dots[..., None] * 0.22
        rng = np.random.default_rng(3)
        fill += rng.normal(0, 3.5, (ch * S, cw * S, 1))
    # ink edge 3 px on the plate
    er = np.asarray(Image.fromarray((pm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(S * 1.5)), np.float32) / 255
    inner = np.clip((er - 0.5) * 3 + 0.5, 0, 1)
    ink_edge = np.clip(pm - np.asarray(Image.fromarray((pm * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(int(3 * S) | 1)), np.float32) / 255, 0, 1)
    plate_rgb = fill
    out = rgba.copy()
    out[..., :3] = out[..., :3] * (1 - pm[..., None]) + plate_rgb * pm[..., None]
    out[..., :3] = out[..., :3] * (1 - ink_edge[..., None]) + np.array(ink, np.float32) * ink_edge[..., None]
    if mat == 'A':
        # matte vinyl: thin light line just inside the ink at the top
        hl = np.clip(np.asarray(Image.fromarray(np.clip((pm - np.roll(pm, 4 * S, 0)) * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(S * 0.8)), np.float32) / 255, 0, 1) * (1 - ink_edge)
        out[..., :3] += hl[..., None] * 60
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(img)
    # content in plate-local coords: translate by pad
    class Off:
        def __init__(s, dd):
            s.dd = dd

    content(d, S, pad * S, pad * S, w, h)
    if mat == 'C':
        # peel curl: bottom right corner lifts, a lighter triangle with a soft inner shade
        cs = int(h * 0.30 * S)
        x1, y1 = (pad + w) * S - int(4 * S), (pad + h) * S - int(4 * S)
        tri = Image.new('RGBA', img.size, (0, 0, 0, 0))
        td = ImageDraw.Draw(tri)
        td.polygon([(x1, y1 - cs), (x1, y1), (x1 - cs, y1)], fill=(0, 0, 0, 0))
        sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.polygon([(x1 + 2 * S, y1 - cs), (x1 + 2 * S, y1 + 2 * S), (x1 - cs, y1 + 2 * S)], fill=(255, 255, 255, 120))
        sh = sh.filter(ImageFilter.GaussianBlur(S * 0.8))
        ma = Image.new('L', img.size, 0)
        ImageDraw.Draw(ma).polygon([(x1, y1 - cs), (x1, y1), (x1 - cs, y1)], fill=255)
        img = Image.composite(Image.alpha_composite(img, sh), img, Image.fromarray((np.asarray(ma) > 0).astype(np.uint8) * 255).filter(ImageFilter.GaussianBlur(0)))
    img = img.rotate(tilt, resample=Image.BICUBIC, expand=True)
    return img.resize((int(img.width / S), int(img.height / S)), Image.LANCZOS)


def put_sticker(base, im, xy):
    shadow_paste(base, im, xy, SHADOW['k'], SHADOW['blur'], SHADOW['off'])


def text_ink(d, xy, s, px, S, col=INK, anchor='mm'):
    d.text(xy, s, font=anton(int(px * S)), fill=col, anchor=anchor)


# ----------------------------------------------------------------------------- wax grease pencil (the player's plan): ink under, wax over with grain, wobble
def wax(L, pts, col=YEL, w=7, seed=1, wobble=0.8, ink=True, grain=1.0, taper=False):
    """pts at 1080p; draws into L (2x). wax texture = streaked alpha noise; ink keyline = w + 4.5."""
    k = L.k
    rng = np.random.default_rng(seed)
    # resample + wobble
    P = []
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 3))
        for i in range(n):
            P.append([x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n])
    P.append(list(pts[-1]))
    P = np.array(P, np.float32)
    if len(P) > 3 and wobble:
        ph = rng.uniform(0, 6.28, 2)
        s = np.arange(len(P), dtype=np.float32)
        P[:, 0] += wobble * np.sin(s / 7.0 + ph[0])
        P[:, 1] += wobble * np.sin(s / 6.0 + ph[1])
    pad = int(w + 12)
    x0, y0 = int(P[:, 0].min()) - pad, int(P[:, 1].min()) - pad
    x1, y1 = int(P[:, 0].max()) + pad, int(P[:, 1].max()) + pad
    bw, bh = (x1 - x0) * k, (y1 - y0) * k
    pp = [((x - x0) * k, (y - y0) * k) for x, y in P]

    def stroke_mask(wd):
        m = Image.new('L', (bw, bh), 0)
        d = ImageDraw.Draw(m)
        if taper:
            n = len(pp)
            for i in range(n - 1):
                f = 0.55 + 0.45 * min(1, i / (n * 0.25))
                d.line([pp[i], pp[i + 1]], fill=255, width=max(1, int(wd * k * f)))
        else:
            d.line(pp, fill=255, width=max(1, int(wd * k)), joint='curve')
        r = wd * k / 2
        for (x, y) in (pp[0], pp[-1]):
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)
        return np.asarray(m, np.float32) / 255
    out = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
    if ink:
        mi = stroke_mask(w + 4.5)
        a = np.dstack([np.broadcast_to(np.array([6, 3, 8], np.float32), (bh, bw, 3)), mi * 235])
        out = Image.alpha_composite(out, Image.fromarray(a.astype(np.uint8), 'RGBA'))
    mw = stroke_mask(w)
    nz = rng.random((bh, bw)).astype(np.float32)
    nz = np.asarray(Image.fromarray((nz * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.9 * k / 2)), np.float32) / 255
    nz = (nz - nz.mean()) / (nz.std() + 1e-6)
    streak = np.asarray(Image.fromarray((rng.random((bh, bw)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2 * k / 2)), np.float32) / 255
    streak = (streak - streak.mean()) / (streak.std() + 1e-6)
    al = np.clip(0.9 + 0.09 * nz * grain + 0.07 * streak * grain, 0, 1)
    al = np.where(nz * grain > 1.9, 0.5, al)                 # wax skips
    # darker rim of the wax
    inner = np.asarray(Image.fromarray((mw * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(max(3, int(1.6 * k)) | 1)), np.float32) / 255
    rimm = np.clip(mw - inner, 0, 1)
    c = np.array(col, np.float32)
    rgb = np.broadcast_to(c, (bh, bw, 3)) * (1 - rimm[..., None] * 0.18) * (0.93 + 0.07 * np.clip(streak, -1, 1)[..., None])
    a = np.dstack([rgb, mw * al * 255])
    out = Image.alpha_composite(out, Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))
    L.im.alpha_composite(out, (x0 * k, y0 * k))


def wax_x(L, x, y, r=12, col=YEL, seed=3, w=5, circle=False):
    """pencil X: two overshooting strokes, slightly off-square; optional hand circle"""
    rng = random.Random(seed)
    j = lambda: rng.uniform(-1.6, 1.6)
    wax(L, [(x - r + j(), y - r * 0.9 + j()), (x + r * 1.08 + j(), y + r * 1.05 + j())], col, w, seed, 0.5)
    wax(L, [(x + r * 0.95 + j(), y - r * 1.0 + j()), (x - r * 1.08 + j(), y + r * 0.95 + j())], col, w, seed + 1, 0.5)
    if circle:
        pts = [(x + (r + 9) * math.cos(math.radians(a)) + j() * 0.5, y + (r + 9) * math.sin(math.radians(a)) + j() * 0.5) for a in range(-40, 345, 15)]
        wax(L, pts, col, 3.4, seed + 2, 0.6)


# ----------------------------------------------------------------------------- the refund token: ONE design, a fixed size ladder (board 44, chip 30, row 28, strip 20)
def refund_token(L, cx, cy, size=40, opt='A'):
    """+1 RAM refunded. One design, a fixed ladder: board 44 (full), row 30 / chip 26 (reduced), strip 20 (pip + plus only).
    A: pip + plus + cyan spark star; B: pip + pop ticks above; C: pip in a white ink ring (+ ticks at board size)."""
    pw, ph = size * 0.86, size * 0.62
    big = size >= 40
    mid = 24 <= size < 40
    pip = dict(fill=CYAN, outline=INK, w=max(2, size * 0.07), r=max(2, size * 0.1))
    if opt == 'A':
        if big:
            n = 8
            pts = []
            for i in range(2 * n):
                rr = size * (0.78 if i % 2 == 0 else 0.5)
                a = math.radians(-90 + 180 * i / n)
                pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
            L.poly(pts, fill=(190, 244, 255), outline=INK, w=2)
        elif mid:
            L.rect([cx - pw / 2 - 3, cy - ph / 2 - 3, cx + pw / 2 + 3, cy + ph / 2 + 3], fill=(190, 244, 255), outline=INK, w=1.6, r=4)
    elif opt == 'B':
        if big or mid:
            ang = (-150, -110, -70, -30) if big else (-120, -90, -60)
            for a in ang:
                p0 = ppx((cx, cy), size * (0.66 if big else 0.52), 90 + a)
                p1 = ppx((cx, cy), size * (0.9 if big else 0.68), 90 + a)
                L.line([p0, p1], INK, 5.2 if big else 4.4)
                L.line([p0, p1], CYAN, 2.8 if big else 2.2)
    else:
        if big:
            L.ellipse([cx - size * 0.72, cy - size * 0.72, cx + size * 0.72, cy + size * 0.72], fill=(8, 14, 26, 235), outline=WHITE, w=max(2, size * 0.06))
            for i in range(6):
                a = 30 + 60 * i
                p0 = ppx((cx, cy), size * 0.72, a)
                p1 = ppx((cx, cy), size * 0.92, a)
                L.line([p0, p1], INK, 5)
                L.line([p0, p1], WHITE, 2.4)
        elif mid:
            L.ellipse([cx - size * 0.56, cy - size * 0.56, cx + size * 0.56, cy + size * 0.56], outline=WHITE, w=2)
    L.rect([cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2], **pip)
    t = ph * 0.30
    wd = max(2.2, size * 0.085)
    L.line([(cx, cy - t), (cx, cy + t)], INK, wd)
    L.line([(cx - t, cy), (cx + t, cy)], INK, wd)
