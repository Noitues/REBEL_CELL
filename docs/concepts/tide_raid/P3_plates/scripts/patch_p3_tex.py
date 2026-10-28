s = open('p2_tex.py').read()
a = s.index('def ring_tex')
b = s.index('def block_tex')
new_ring = '''BANDW = {'UNTOUCHED': 1.5, 'HOLDS': 3.8, 'SITES_LOST': 3.8, 'DAMAGED': 3.8, 'BREACHED': 2.4}     # P3 value ladder: band weight is part of the tier read


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
        dk = np.array([0.45, 0.06, 0.10], np.float32)
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
        h1 = (np.mod((X + Y) * 0.9, 1.0) < 0.12) | (np.mod((X - Y) * 0.9, 1.0) < 0.12)
        hh = (disc * h1)[..., None]
        rgb = rgb * (1 - hh * .6) + col[None, None] * hh * .6
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


'''
s = s[:a] + new_ring + s[b:]
open('p2_tex.py', 'w').write(s)
print('ok')
