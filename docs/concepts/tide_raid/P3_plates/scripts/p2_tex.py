"""P2 mark textures (punch #3 / #10): tier rings and stop blocks, bolder, with an ink under-stroke and a white rim; SITES LOST is an ink-black plate
with a white rim and a bold ochre diagonal hatch.   python p2_tex.py -> WORK/tex/ring_<tier>.png, block_<tier>.png"""
import numpy as np
from PIL import Image, ImageDraw
import p1lib as L

TIERC = {'UNTOUCHED': 'B8FFF2', 'HOLDS': '19C9B4', 'SITES_LOST': 'C98410', 'DAMAGED': 'FF9A00', 'BREACHED': 'FF3347'}
TIER_R = {'UNTOUCHED': 11.4, 'HOLDS': 12.6, 'SITES_LOST': 12.6, 'DAMAGED': 13.8, 'BREACHED': 15.0}     # P3: x1.2 (the tower fills the middle of the ring)
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


BANDW = {'UNTOUCHED': 1.5, 'HOLDS': 3.8, 'SITES_LOST': 3.8, 'DAMAGED': 3.8, 'BREACHED': 2.4}     # P3 value ladder: band weight is part of the tier read


def ring_tex(tier, N=1536):
    """P3 VALUE LADDER (survives 320 px greyscale): UNTOUCHED = thin pale hollow ring | HOLDS = heavy teal ring + translucent teal disc, bars |
    DAMAGED = heavy amber ring + HALF-filled amber disc (north-west half), chevrons | BREACHED = double red ring + dark-red filled disc, crosshatch |
    SITES LOST = solid ink-black disc, white rim in and out, ochre hatch band (darkest, most solid mark)."""
    half = ring_size(tier)
    bw = BANDW[tier]
    ax = (np.arange(N) + .5) / N * 2 - 1
    X, Y = np.meshgrid(ax * half, ax * half)
    rho = np.hypot(X, Y); th = np.arctan2(Y, X)
    r = TIER_R[tier]
    col = hexc(TIERC[tier])
    rgb = np.zeros((N, N, 3), np.float32); a = np.zeros((N, N), np.float32)
    px = 2 * half / N

    def cov(d0, d1):      # coverage of annulus d0 < rho < d1 with 1 px AA
        return np.clip(np.minimum(rho - d0, d1 - rho) / px + .5, 0, 1)
    disc = cov(-1, r - bw)
    ink = cov(r - bw - INKW, r + INKW)
    a = ink * 0.93; rgb[:] = INK
    # interior fills (the value ladder)
    if tier == 'HOLDS':
        rgb = rgb * (1 - disc[..., None] * .5) + col[None, None] * .55 * disc[..., None] * .5
        a = np.maximum(a, disc * 0.55)
        rgb = np.where(disc[..., None] > 0, col[None, None] * 0.7, rgb)
    elif tier == 'DAMAGED':
        half_m = (X + Y < 0).astype(np.float32)       # north-west half
        d2 = disc * half_m
        rgb = rgb * (1 - d2[..., None]) + col[None, None] * d2[..., None]
        a = np.maximum(a, d2 * 0.88)
    elif tier == 'BREACHED':
        d2 = disc * 1.0
        dk = np.array([0.62, 0.07, 0.13], np.float32)
        rgb = rgb * (1 - d2[..., None]) + dk[None, None] * d2[..., None]
        a = np.maximum(a, d2 * 0.92)
    elif tier == 'SITES_LOST':
        rgb = rgb * (1 - disc[..., None]) + INK[None, None] * disc[..., None]
        a = np.maximum(a, disc * 0.97)
    band = cov(r - bw, r)
    fill = np.broadcast_to(col, (N, N, 3)).copy()
    if tier == 'SITES_LOST':
        d = (X + Y) / 1.6
        stripes = ((d % 1.25) < 0.62)
        fill = np.where(stripes[..., None], col[None, None], INK[None, None])
    elif tier == 'HOLDS':
        bars = (np.mod(th, 2 * np.pi / 22) < 2 * np.pi / 22 * 0.3)
        fill = np.where(bars[..., None], INK[None, None], col[None, None])
    elif tier == 'DAMAGED':
        k = 2 * np.pi / 14
        ph = np.mod(th, k) / k
        ch = np.abs(ph - .5) * 2 * 0.9 + (rho - (r - bw / 2)) / bw * 0.9
        chev = (np.abs(np.mod(ch * 2.0, 1.0) - .5) < 0.2) & (np.abs(rho - (r - bw / 2)) < bw / 2)
        fill = np.where(chev[..., None], INK[None, None], col[None, None])
    elif tier == 'BREACHED':
        d1 = np.mod((X + Y) * 1.1, 1.0) < 0.22
        d2_ = np.mod((X - Y) * 1.1, 1.0) < 0.22
        fill = np.where((d1 | d2_)[..., None], INK[None, None], col[None, None])
        # crosshatch inside the dark disc too
        h1 = (np.mod((X + Y) * 0.7, 1.0) < 0.16) | (np.mod((X - Y) * 0.7, 1.0) < 0.16)
        hh = (disc * h1)[..., None]
        rgb = rgb * (1 - hh * .75) + WHITE[None, None] * hh * .75
    else:
        fill = np.broadcast_to(col, (N, N, 3)).copy()
    rgb = rgb * (1 - band[..., None]) + fill * band[..., None]
    a = np.maximum(a, band)
    # white rim: inner edge (all) + outer edge too for SITES LOST / UNTOUCHED
    rim_in = cov(r - bw, r - bw + RIM)
    rgb = rgb * (1 - rim_in[..., None]) + WHITE * rim_in[..., None]
    if tier in ('SITES_LOST', 'UNTOUCHED', 'HOLDS'):
        rim_out = cov(r - RIM, r)
        rgb = rgb * (1 - rim_out[..., None]) + WHITE * rim_out[..., None]
    if tier == 'BREACHED':      # second heavy ring outside the ink: double ring
        o2 = cov(r + INKW + 0.2, r + INKW + 0.2 + 1.3)
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
    # P3 value ladder on the block: UNTOUCHED hollow | HOLDS filled bright | DAMAGED half-filled | BREACHED dark red | SITES LOST ink
    fillc = {'SITES_LOST': ink, 'UNTOUCHED': (0, 0, 0, 0), 'BREACHED': (118, 16, 28, 255)}.get(tier, col + (255,))
    d.polygon(octo(b2), fill=fillc)
    if tier == 'DAMAGED':
        d.rectangle([W_ / 2, b2 + 1, W_ - b2 - 1, H_ - b2 - 1], fill=(0, 0, 0, 0))
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
        inkpat = False
    clip = Image.new('L', (W_, H_), 0); ImageDraw.Draw(clip).polygon(octo(b2), fill=255)
    mask = np.minimum(np.asarray(pat, np.float32), np.asarray(clip, np.float32)) / 255
    pc = np.array(ink[:3] if inkpat else col, np.float32)
    arr = np.asarray(im, np.float32).copy()
    if tier == 'UNTOUCHED':
        pc = np.array(col, np.float32); arr[..., 3] = np.maximum(arr[..., 3], mask * 255)
    if tier == 'BREACHED':
        pc = np.array(col, np.float32)
    if tier == 'DAMAGED':
        mask = mask * (np.arange(W_)[None, :] < W_ / 2)
    arr[..., :3] = arr[..., :3] * (1 - mask[..., None]) + pc * mask[..., None]
    Image.fromarray(arr.astype(np.uint8), 'RGBA').resize((W_ // SS, H_ // SS), Image.LANCZOS).save(L.WORK + 'tex/block_%s.png' % tier)


if __name__ == '__main__':
    for t in TIERC:
        ring_tex(t)
        block_tex(t)
    print('tex ok')
