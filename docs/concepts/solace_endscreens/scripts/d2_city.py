"""Direction 2: the helix seen from the city. WIN = helix hacked to Cell colours; LOSE = the Bloom takes the city."""
import sys, math, random
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/solace_endscreens/scripts')
from ui_lib import *
from scipy.spatial import cKDTree

OUT = 'D:/rc_art/art-pass/docs/concepts/solace_endscreens/'
CYAN = (0, 229, 255, 255)
CELLY = (212, 255, 0, 255)
PINK = (255, 62, 160, 255)
LIMEC = (150, 255, 70, 255)
HX, HY = 1440, 560      # focus: helix centre in frame
BASE = (1330, 900)      # plaza centre in frame

src = Image.open(R + 'docs/concepts/tide_raid/G1_parity/r42/plan_r42.png').convert('RGB')
crop = src.crop((960, 0, 1920, 540)).resize((1920, 1080), Image.LANCZOS)
crop = crop.filter(ImageFilter.UnsharpMask(radius=2.2, percent=90, threshold=2))
CITY = np.asarray(crop).astype(np.float32) / 255.0
yy, xx = np.mgrid[0:1080, 0:1920].astype(np.float32)


def noise(seed, sigma, shape=(1080, 1920)):
    rng = np.random.default_rng(seed)
    n = rng.random((shape[0] // 8, shape[1] // 8)).astype(np.float32)
    n = Image.fromarray((n * 255).astype(np.uint8)).resize((shape[1], shape[0]), Image.BICUBIC)
    n = np.asarray(n.filter(ImageFilter.GaussianBlur(sigma))).astype(np.float32) / 255
    return (n - n.min()) / (n.max() - n.min() + 1e-6)


def under_ui_grade(a, base=0.58, inner=0.92, cx=HX, cy=HY, rad=420):
    d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.15) ** 2)
    f = np.exp(-(d / rad) ** 2)
    k = (base + (inner - base) * f)[..., None]
    gray = a.mean(2, keepdims=True)
    a = gray + (a - gray) * (0.85 + 0.15 * f[..., None])
    return np.clip(a * k, 0, 1)


def to_img(a):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), 'RGB').convert('RGBA')
    return im.resize((W * K, H * K), Image.BICUBIC)


def helix_mask():
    return (xx > 1230) & (xx < 1680) & (yy > 120) & (yy < 1000)


def hacked_city():
    a = CITY.copy()
    m = helix_mask()
    mx = a.max(2)
    out, sel = hsv_shift(a, 0.14, 0.50, shift=0.215, sat=1.0, val=1.12, mask=m & (mx > 0.52))
    # the helix's own lime halo ring -> Cell lime
    a = out
    # glitch bands across the helix
    rng = np.random.default_rng(8)
    g = a.copy()
    for i in range(22):
        y0 = int(rng.integers(150, 980))
        hh = int(rng.integers(5, 26))
        dx = int(rng.integers(-70, 70))
        x0, x1 = 1170, 1740
        g[y0:y0 + hh, x0:x1] = np.roll(a[y0:y0 + hh, x0:x1], dx, axis=1)
        if i % 3 == 0:  # cyan scan flash
            g[y0:y0 + 2, x0:x1] = g[y0:y0 + 2, x0:x1] * 0.4 + np.array([0.0, 0.9, 1.0]) * 0.6
    a = g
    a = under_ui_grade(a)
    # extra cyan light spill over the plaza
    d = np.sqrt((xx - BASE[0]) ** 2 + ((yy - BASE[1]) * 1.6) ** 2)
    spill = np.exp(-(d / 260) ** 2)[..., None] * np.array([0.0, 0.55, 0.65])
    a = np.clip(a + spill * 0.45, 0, 1)
    return a


def bloom_city(p=0.9):
    a = CITY.copy()
    d = np.sqrt((xx - 1400) ** 2 + ((yy - 870) * 1.5) ** 2)
    ax, ay, bx, by = 1450, 170, 1420, 860
    t_ = np.clip(((xx - ax) * (bx - ax) + (yy - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2), 0, 1)
    dseg = np.sqrt((xx - (ax + t_ * (bx - ax))) ** 2 + (yy - (ay + t_ * (by - ay))) ** 2)
    n = noise(5, 14)
    rad = 380 + (1 - p) * 900
    dd_ = np.minimum(d / rad * 300, dseg * 1.0 * 300 / 165)   # island radius ~ 300 in this metric
    infected = (dd_ + (n - 0.5) * 120) > 300
    d = np.minimum(d, dseg * 1.9)
    # voronoi veins
    rng = np.random.default_rng(2)
    seeds = np.stack([rng.uniform(0, 1920, 5200), rng.uniform(0, 1080, 5200)], 1)
    # denser seeds nearer the island edge
    t = cKDTree(seeds)
    pts = np.stack([xx.ravel(), yy.ravel()], 1)
    dd, _ = t.query(pts, k=2)
    edge = ((dd[:, 1] - dd[:, 0]) < 2.4).reshape(1080, 1920)
    edge2 = ((dd[:, 1] - dd[:, 0]) < 1.1).reshape(1080, 1920)
    hatch = (((xx + yy) % 9) < 1.6)
    inf = infected.astype(np.float32)
    inf_soft = np.asarray(Image.fromarray((inf * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))).astype(np.float32) / 255
    # darken, then pink tint
    base = a * (1 - inf_soft[..., None] * 0.35)
    tint = np.array([0.42, 0.04, 0.22])
    base = base + inf_soft[..., None] * tint * 0.45
    veins = (edge & infected)
    hot = (edge2 & infected)
    veins_s = np.asarray(Image.fromarray((veins * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32) / 255
    hot_s = np.asarray(Image.fromarray((hot * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) / 255
    pink = np.array([1.0, 0.24, 0.63])
    base = base * (1 - veins_s[..., None] * 0.85) + pink * veins_s[..., None] * 0.8
    base = base + np.array([1.0, 0.85, 0.9]) * hot_s[..., None] * 0.35
    hv = (hatch & infected & (noise(9, 3) > 0.5)).astype(np.float32)
    base = base + pink * hv[..., None] * 0.10
    # boosted lime island glow
    isl = (1 - inf_soft)
    base = np.clip(base + isl[..., None] * np.array([0.04, 0.12, 0.02]), 0, 1)
    # grade: city steps back, island holds
    f = (1 - inf_soft)
    k = (0.62 + 0.34 * f)[..., None]
    return np.clip(base * k, 0, 1)


def node_net(img, win):
    # the Cell's own network sprouting from the helix across the city
    rng = random.Random(21)
    nodes = [(1330, 905), (1145, 980), (1020, 820), (1230, 700), (1620, 880), (1760, 760), (1550, 1010), (940, 940), (1000, 620), (1250, 330), (1700, 420), (1560, 250), (1780, 140), (1140, 480)]
    edges = [(0, 1), (1, 2), (0, 3), (0, 4), (4, 5), (4, 6), (1, 7), (2, 8), (3, 8), (3, 9), (5, 10), (10, 11), (11, 12), (9, 13), (3, 13)]
    lay = layer(W, H)
    for a, b in edges:
        line(lay, [nodes[a][0], nodes[a][1], nodes[b][0], nodes[b][1]], (0, 229, 255, 200), 3)
    img2 = glow(img, lay, 5, 1.2)
    img2.alpha_composite(lay.resize(img2.size) if lay.size != img2.size else lay)
    for i, (x, y) in enumerate(nodes):
        s = 15 if i == 0 else 10
        c = CELLY if i in (0, 5, 10) else CYAN
        rect(img2, [x - s, y - s, x + s, y + s], fill=(8, 16, 30, 255), outline=c, width=3)
        rect(img2, [x - s / 2.6, y - s / 2.6, x + s / 2.6, y + s / 2.6], fill=c)
    return img2


def panel_rows(img, x, y, rows, f, col, step=30):
    for k, v in rows:
        text(img, (x, y), k, f, col)
        text(img, (x + 250, y), v, f, (232, 240, 250, 255))
        y += step
    return y


def win():
    img = to_img(hacked_city())
    img = node_net(img, True)
    # cell-lime halo ring replacing the pink one at the helix head
    ring = layer(W, H)
    ellipse(ring, [1325, 205, 1565, 282], outline=CELLY, width=5)
    img = glow(img, ring, 6, 1.4)
    img.alpha_composite(ring)
    # helix tag stickers
    sticker(img, 'REBEL_CELL', 1440, 140, 250, 46, PINK, None, rot=5, size=30)
    # CRT audit panel
    x0, y0, x1, y1 = 56, 70, 900, 1000
    crt_panel(img, [x0, y0, x1, y1], CYAN, '> AUDIT // SOLACE BIOSYSTEMS // INCIDENT 7  [CLOSED]', fill=(5, 12, 26, 232))
    text(img, (x0 + 24, y0 + 52), 'CAMPAIGN AUDIT', font('anton', 52), (232, 240, 250, 255))
    mono = font('mono', 22)
    y = panel_rows(img, x0 + 24, y0 + 128, [('SUBJECT .......', 'REBEL_CELL (cell-03)'), ('DURATION ......', '41 days'), ('STATUS ........', 'HELIX COMPROMISED')], mono, CYAN)
    y += 14
    text(img, (x0 + 24, y), 'ACTIVITY', mono, CYAN)
    y += 30
    y = panel_rows(img, x0 + 50, y, [('netruns ......', '8   (1 operative lost)'), ('raids ........', '4   (4 repelled, 1 decisive)'), ('exploits .....', '3 / 3 extracted'), ('schematics ...', '214 earned / 190 spent')], mono, (110, 170, 190, 255))
    y += 14
    text(img, (x0 + 24, y), 'NETWORK AT CLOSURE', mono, CYAN)
    y += 30
    text(img, (x0 + 50, y), 'held 5    disabled 0    seized 0', mono, (232, 240, 250, 255))
    y += 28
    text(img, (x0 + 50, y), 'home server  50 / 50   (peak 7 nodes)', mono, (232, 240, 250, 255))
    y += 48
    text(img, (x0 + 24, y), 'HEAT  (exposure)  peak 82', mono, CYAN)
    gx0, gy0, gx1, gy1 = x0 + 70, y + 34, x0 + 780, y + 150
    seq = [8, 12, 20, 24, 31, 40, 44, 52, 60, 63, 71, 82]
    for v in (25, 50, 75):
        yy_ = gy1 - (gy1 - gy0) * v / 100
        line(img, [gx0, yy_, gx1, yy_], (0, 229, 255, 60), 1)
        text(img, (gx0 - 10, yy_), str(v), font('mono', 15), (110, 170, 190, 255), 'rm')
    pts = [(gx0 + (gx1 - gx0) * i / 11, gy1 - (gy1 - gy0) * v / 100) for i, v in enumerate(seq)]
    line(img, [c for p in pts for c in p], CELLY, 3)
    for p in pts:
        ellipse(img, [p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=CELLY)
    y = gy1 + 34
    text(img, (x0 + 24, y), 'IDENTIFIED OPERATIVES', mono, CYAN)
    y += 30
    for n, r, st, dead in [('BREAKER', 'R3', 'ON SITE', 0), ('GHOST', 'R2', 'DECEASED run 9', 1), ('RIGGER', 'R1', 'ON SITE', 0), ('BOTNET', 'R2', 'ON SITE', 0), ('WRECKER', 'R0', 'ON SITE', 0)]:
        c = (255, 90, 90, 255) if dead else (232, 240, 250, 255)
        text(img, (x0 + 50, y), n + '  ' + r, mono, c)
        text(img, (x0 + 300, y), st, mono, c)
        if dead:
            line(img, [x0 + 50, y + 10, x0 + 200, y + 10], c, 2)
        y += 26
    # result stamp as sticker
    sticker(img, 'CELL HOLDS', 1010, 130, 330, 70, CELLY, None, rot=-3, size=48)
    buttons(img, main_xy=(1330, 1030), new_xy=(1620, 1032))
    return img


def lose():
    img = to_img(bloom_city(0.9))
    # solace notice window (lime holo glass)
    x0, y0, x1, y1 = 56, 230, 900, 810
    lime = (150, 255, 70, 255)
    rrect(img, [x0, y0, x1, y1], 6, fill=(6, 20, 8, 236), outline=lime, width=3)
    rrect(img, [x0, y0, x1, y0 + 46], 6, fill=(90, 190, 40, 255))
    text(img, (x0 + 18, y0 + 10), 'SOLACE BIOSYSTEMS   //   NOTICE', font('mono', 22), (10, 30, 8, 255))
    text(img, (x1 - 16, y0 + 10), 'REF SB-7718/CELL', font('mono', 18), (10, 30, 8, 255), 'ra')
    # seal
    cx, cy = x0 + 100, y0 + 150
    ellipse(img, [cx - 56, cy - 56, cx + 56, cy + 56], outline=lime, width=3)
    ellipse(img, [cx - 46, cy - 46, cx + 46, cy + 46], outline=(150, 255, 70, 120), width=1.5)
    pa, pb = [], []
    for i in range(21):
        t = i / 20
        yv = cy - 30 + t * 60
        xv = math.sin(t * 6.283 * 1.15) * 17
        pa += [cx + xv, yv]
        pb += [cx - xv, yv]
    line(img, pa, lime, 4)
    line(img, pb, (150, 255, 70, 150), 4)
    text(img, (x0 + 190, y0 + 108), 'YOUR CELL HAS BEEN TREATED', font('plex', 40), (240, 255, 235, 255))
    text(img, (x0 + 190, y0 + 160), 'Order 7/88: network assets sterilised, operatives reclassified.', font('plexr', 20), (150, 255, 70, 255))
    text(img, (x0 + 28, y0 + 240), 'HOME SERVER  00/50      //      NODES STERILISED  6/6', font('mono', 22), (220, 245, 215, 255))
    rect(img, [x0 + 28, y0 + 282, x1 - 28, y0 + 308], outline=lime, width=2)
    rect(img, [x0 + 32, y0 + 286, x0 + 32 + (x1 - x0 - 64) * 0.86, y0 + 304], fill=lime)
    text(img, (x0 + 28, y0 + 340), 'WIPE IN', font('mono', 20), lime)
    text(img, (x0 + 28, y0 + 366), '00:02.80', font('mono', 96), (240, 255, 235, 255))
    text(img, (x0 + 28, y0 + 506), 'no appeal is offered.  your station is now a clean surface.', font('mono', 18), (150, 200, 140, 255))
    stamp(img, 'TREATED', x0 + 640, y0 + 400, (150, 255, 70, 235), rot=-7, size=84)
    # helix glow stays as the one clean thing; tide gauge tick for the Bloom
    crt_panel(img, [1400, 60, 1860, 150], (255, 62, 160, 255), '> BLOOM  //  SPREAD', fill=(20, 4, 14, 235))
    rect(img, [1424, 104, 1836, 128], outline=(255, 62, 160, 255), width=2)
    rect(img, [1428, 108, 1428 + 404 * 0.9, 124], fill=(255, 62, 160, 255))
    text(img, (1836, 138), '90 %', font('mono', 16), (255, 150, 200, 255), 'rb')
    buttons(img, main_xy=(1330, 1030), new_xy=(1620, 1032))
    return img


if __name__ == '__main__':
    for nm, fn in (('d2_win.png', win), ('d2_lose.png', lose)):
        img = fn()
        img = vignette(img, 0.3)
        finish(img, OUT + nm, 4, 3)
        print('ok', nm)
