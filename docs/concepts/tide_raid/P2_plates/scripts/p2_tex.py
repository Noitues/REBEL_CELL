"""P2 mark textures (punch #3 / #10): tier rings and stop blocks, bolder, with an ink under-stroke and a white rim; SITES LOST is an ink-black plate
with a white rim and a bold ochre diagonal hatch.   python p2_tex.py -> WORK/tex/ring_<tier>.png, block_<tier>.png"""
import numpy as np
from PIL import Image, ImageDraw
import p1lib as L

TIERC = {'UNTOUCHED': 'B8FFF2', 'HOLDS': '19C9B4', 'SITES_LOST': 'C98410', 'DAMAGED': 'FF9A00', 'BREACHED': 'FF3347'}
TIER_R = {'UNTOUCHED': 9.5, 'HOLDS': 10.5, 'SITES_LOST': 10.5, 'DAMAGED': 11.5, 'BREACHED': 12.5}
BAND = 2.8       # BU
INKW = 1.3       # BU under-stroke each side
RIM = 0.45
PAD = 1.6        # BU beyond the ink
INK = np.array([6, 4, 18], np.float32) / 255
WHITE = np.array([1, 1, 1], np.float32)


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255


def ring_size(tier):
    return TIER_R[tier] + INKW + PAD     # half-size of the quad in BU


def ring_tex(tier, N=1536):
    half = ring_size(tier)
    ax = (np.arange(N) + .5) / N * 2 - 1
    X, Y = np.meshgrid(ax * half, ax * half)
    rho = np.hypot(X, Y); th = np.arctan2(Y, X)
    r = TIER_R[tier]
    col = hexc(TIERC[tier])
    rgb = np.zeros((N, N, 3), np.float32); a = np.zeros((N, N), np.float32)
    px = 2 * half / N

    def cov(d0, d1):      # coverage of annulus d0 < rho < d1 with 1 px AA
        return np.clip(np.minimum(rho - d0, d1 - rho) / px + .5, 0, 1)
    ink = cov(r - BAND - INKW, r + INKW)
    a = ink * 0.93; rgb[:] = INK
    band = cov(r - BAND, r)
    fill = np.broadcast_to(col, (N, N, 3)).copy()
    if tier == 'SITES_LOST':
        fill[:] = INK
        stripes = ((th * 9 * rho / r + rho * 1.4) % 1.0) < 0.5      # diagonal-ish hatch winding with the ring
        # straight diagonal hatch in plate space reads better than a spiral
        d = (X + Y) / 1.6
        stripes = ((d % 1.25) < 0.62)
        fill = np.where(stripes[..., None], col[None, None], INK[None, None])
    elif tier == 'HOLDS':
        bars = (np.mod(th, 2 * np.pi / 28) < 2 * np.pi / 28 * 0.22)
        fill = np.where(bars[..., None], INK[None, None], col[None, None])
    elif tier == 'DAMAGED':
        k = 2 * np.pi / 18
        ph = np.mod(th, k) / k
        ch = np.abs(ph - .5) * 2 * 0.9 + (rho - (r - BAND / 2)) / BAND * 0.9
        chev = (np.abs(np.mod(ch * 2.0, 1.0) - .5) < 0.14) & (np.abs(rho - (r - BAND / 2)) < BAND / 2)
        fill = np.where(chev[..., None], INK[None, None], col[None, None])
    elif tier == 'BREACHED':
        d1 = np.mod((X + Y) * 1.3, 1.0) < 0.16
        d2 = np.mod((X - Y) * 1.3, 1.0) < 0.16
        fill = np.where((d1 | d2)[..., None], INK[None, None], col[None, None])
    else:
        kk = 2 * np.pi / 24
        rc_ = r - BAND / 2
        dots = np.hypot(rho - rc_, (np.mod(th, kk) - kk / 2) * rc_) < 0.62
        fill = np.where(dots[..., None], INK[None, None], col[None, None])
    rgb = rgb * (1 - band[..., None]) + fill * band[..., None]
    a = np.maximum(a, band)
    # white rim: inner edge (all) + outer edge too for SITES LOST
    rim_in = cov(r - BAND, r - BAND + RIM)
    rgb = rgb * (1 - rim_in[..., None]) + WHITE * rim_in[..., None]
    if tier == 'SITES_LOST':
        rim_out = cov(r - RIM, r)
        rgb = rgb * (1 - rim_out[..., None]) + WHITE * rim_out[..., None]
    if tier == 'BREACHED':      # second thin ring outside the ink: stamp-like
        o2 = cov(r + INKW + 0.1, r + INKW + 0.1 + 0.6)
        rgb = rgb * (1 - o2[..., None]) + col[None, None] * o2[..., None]
        a = np.maximum(a, o2)
    out = np.concatenate([rgb, a[..., None]], -1)
    Image.fromarray((np.clip(out, 0, 1) * 255 + .5).astype(np.uint8), 'RGBA').resize((1024, 1024), Image.LANCZOS).save(L.WORK + 'tex/ring_%s.png' % tier)


def block_tex(tier, SS=3):
    """13.5 x 10 BU stop block (u across the street, v along): chamfered plate, ink border, white rim, tier pattern."""
    W_, H_ = 576 * SS, 432 * SS
    col = tuple(int(c * 255) for c in hexc(TIERC[tier]))
    ink = tuple(int(c * 255) for c in INK) + (255,)
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ch = H_ * .22

    def octo(m):
        return [(m + ch, m), (W_ - m - ch, m), (W_ - m, m + ch), (W_ - m, H_ - m - ch), (W_ - m - ch, H_ - m), (m + ch, H_ - m), (m, H_ - m - ch), (m, m + ch)]
    d.polygon(octo(0), fill=ink)
    b = H_ * .12
    d.polygon(octo(b), fill=(255, 255, 255, 255))
    b2 = b + H_ * .035
    fillc = ink if tier == 'SITES_LOST' else col + (255,)
    d.polygon(octo(b2), fill=fillc)
    m0 = b2 + H_ * .02
    # pattern mask via a separate image clipped to the inner octagon
    pat = Image.new('L', (W_, H_), 0); pd = ImageDraw.Draw(pat)
    if tier == 'HOLDS':
        for i in range(9):
            x = b2 + (W_ - 2 * b2) * (i + .5) / 9
            pd.rectangle([x - W_ * .017, b2, x + W_ * .017, H_ - b2], fill=255)
        inkpat = True
    elif tier == 'SITES_LOST':
        for i in range(-8, 22):
            x = i * W_ / 14
            pd.polygon([(x, H_), (x + W_ * .05, H_), (x + W_ * .05 + H_ * .8, 0), (x + H_ * .8, 0)], fill=255)
        inkpat = False
    elif tier == 'DAMAGED':
        for i in range(7):
            x = W_ * (i + .3) / 7
            pd.line([(x, b2), (x + W_ * .07, H_ / 2), (x, H_ - b2)], fill=255, width=int(H_ * .06))
        inkpat = True
    elif tier == 'BREACHED':
        for i in range(-6, 18):
            x = i * W_ / 12
            pd.line([(x, H_), (x + H_ * .8, 0)], fill=255, width=int(H_ * .03))
            pd.line([(x, 0), (x + H_ * .8, H_)], fill=255, width=int(H_ * .03))
        inkpat = True
    else:
        for i in range(6):
            cx = W_ * (i + .5) / 6
            pd.ellipse([cx - H_ * .12, H_ / 2 - H_ * .12, cx + H_ * .12, H_ / 2 + H_ * .12], fill=255)
        inkpat = True
    clip = Image.new('L', (W_, H_), 0); ImageDraw.Draw(clip).polygon(octo(b2), fill=255)
    mask = np.minimum(np.asarray(pat, np.float32), np.asarray(clip, np.float32)) / 255
    pc = np.array(ink[:3] if inkpat else col, np.float32)
    arr = np.asarray(im, np.float32)
    arr[..., :3] = arr[..., :3] * (1 - mask[..., None]) + pc * mask[..., None]
    Image.fromarray(arr.astype(np.uint8), 'RGBA').resize((W_ // SS, H_ // SS), Image.LANCZOS).save(L.WORK + 'tex/block_%s.png' % tier)


if __name__ == '__main__':
    for t in TIERC:
        ring_tex(t)
        block_tex(t)
    print('tex ok')
