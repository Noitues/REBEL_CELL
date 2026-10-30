"""Direction 3: the Solace broadcast. LOSE = a clean 'contamination contained' feed; WIN = the same feed seized by the Cell."""
import sys, math, random
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/solace_endscreens/scripts')
from ui_lib import *
import d2_city

OUT = 'D:/rc_art/art-pass/docs/concepts/solace_endscreens/'
CYAN = (0, 229, 255, 255)
CELLY = (212, 255, 0, 255)
PINK = (255, 62, 160, 255)
LIME = (150, 255, 70, 255)
WHITE = (240, 255, 236, 255)


def bg():
    img = new((8, 30, 18, 255))
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = yy / h
    a[..., 0] = 8 + 6 * t
    a[..., 1] = 40 - 14 * t
    a[..., 2] = 22 - 4 * t
    for (cx, cy, r, col) in [(0.12, 0.30, 0.55, (30, 110, 40)), (0.80, 0.78, 0.5, (40, 120, 60)), (0.55, 0.0, 0.5, (20, 80, 60))]:
        d = np.sqrt(((xx / w - cx) * 1.8) ** 2 + (yy / h - cy) ** 2)
        g = np.clip(1 - d / r, 0, 1) ** 2
        for c in range(3):
            a[..., c] += g * col[c]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    # soft hex-grid wall (the Solace video wall)
    lay = layer(W, H)
    for r_ in range(0, 14):
        for c_ in range(0, 24):
            x = c_ * 90 + (45 if r_ % 2 else 0)
            y = r_ * 78
            pts = [(x + 40 * math.cos(math.radians(60 * k + 30)), y + 40 * math.sin(math.radians(60 * k + 30))) for k in range(6)]
            poly(lay, pts, outline=(150, 255, 70, 16), width=1.5)
    img.alpha_composite(lay)
    return img


def helix_mark(img, cx, cy, hgt, wid, col, alpha=255, width=6):
    pa, pb = [], []
    n = 80
    for i in range(n + 1):
        t = i / n
        y = cy - hgt / 2 + t * hgt
        x = math.sin(t * 6.283 * 2.2) * wid / 2
        pa.append((cx + x, y))
        pb.append((cx - x, y))
    c = (col[0], col[1], col[2], alpha)
    for i in range(2, n, 4):
        line(img, [pa[i][0], pa[i][1], pb[i][0], pb[i][1]], (col[0], col[1], col[2], alpha // 2), width * 0.55)
    line(img, [c_ for p in pa for c_ in p], c, width)
    line(img, [c_ for p in pb for c_ in p], (col[0], col[1], col[2], int(alpha * 0.7)), width)


def footage(img, box, arr, label, edge, tint=None):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), 'RGB')
    # crop the helix region to the window aspect
    cw = 900
    ch = int(cw * h / w)
    cx0, cy0 = 1000, 120
    im = im.crop((cx0 - 150, cy0, cx0 - 150 + cw, cy0 + ch)).resize((int(w * K), int(h * K)), Image.LANCZOS).convert('RGBA')
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], radius=S(14), fill=255)
    im.putalpha(m)
    img.alpha_composite(im, (S(x0), S(y0)))
    rrect(img, box, 14, outline=edge, width=4)
    # viewfinder corners
    for (px, py, sx, sy) in [(x0 + 18, y0 + 18, 1, 1), (x1 - 18, y0 + 18, -1, 1), (x0 + 18, y1 - 18, 1, -1), (x1 - 18, y1 - 18, -1, -1)]:
        line(img, [px, py + 36 * sy, px, py, px + 36 * sx, py], (255, 255, 255, 220), 3)
    rrect(img, [x0 + 22, y1 - 70, x0 + 22 + tw(label, font('mono', 22)) + 28, y1 - 30], 6, fill=(0, 0, 0, 170))
    text(img, (x0 + 36, y1 - 50), label, font('mono', 22), WHITE, 'lm')


def channel_bug(img, win):
    rrect(img, [60, 50, 300, 106], 10, fill=LIME if not win else (60, 60, 70, 255))
    text(img, (82, 78), 'SOLACE', font('anton', 38), (10, 40, 8, 255), 'lm')
    text(img, (206, 78), 'LIVE', font('anton', 38), (200, 20, 40, 255) if not win else (160, 160, 170, 255), 'lm')
    ellipse(img, [186, 70, 198, 82], fill=(220, 30, 50, 255) if not win else (120, 120, 120, 255))
    text(img, (324, 78), 'BIOSYSTEMS NEWS  //  SB-7718/CELL' if not win else 'BIOSYSTEMS NEWS  //  SIGNAL LO\u0338ST', font('mono', 22), (200, 240, 190, 255), 'lm')


def tear(img, seed, n, maxdx, y0=0, y1=H, hmax=60):
    a = np.asarray(img).copy()
    rng = np.random.default_rng(seed)
    for i in range(n):
        yb = int(rng.integers(y0 * K, y1 * K))
        hh = int(rng.integers(4 * K, hmax * K))
        dx = int(rng.integers(-maxdx * K, maxdx * K))
        a[yb:yb + hh] = np.roll(a[yb:yb + hh], dx, axis=1)
    return Image.fromarray(a, 'RGBA')


def kv_row(img, x, y, k, v, f, kc, vc, gap=270):
    text(img, (x, y), k, f, kc)
    text(img, (x + gap, y), v, f, vc)


def lose():
    img = bg()
    channel_bug(img, False)
    text(img, (1860, 78), '23:41   BIOSAFETY BULLETIN', font('mono', 22), (200, 240, 190, 255), 'rm')
    # headline
    text(img, (84, 180), 'CONTAMINATION', font('anton', 138), WHITE)
    text(img, (84, 332), 'CONTAINED', font('anton', 138), LIME)
    rect(img, [92, 506, 700, 513], fill=LIME)
    text(img, (92, 540), 'Your Cell has been treated.', font('plex', 52), WHITE)
    text(img, (92, 606), 'All strains accounted for.  Thank you for staying calm.', font('plexr', 30), (190, 230, 180, 255))
    # footage window: clean city, no hue edits other than a dim
    arr = d2_city.CITY * 0.95
    footage(img, [1010, 130, 1860, 600], arr, 'LIVE  //  HELIX PARK  //  ALL CLEAR', LIME)
    # lower third
    rrect(img, [60, 790, 1860, 960], 14, fill=(236, 248, 230, 242))
    rrect(img, [60, 790, 330, 960], 14, fill=LIME)
    text(img, (195, 875), 'STATUS', font('anton', 36), (10, 40, 8, 255), 'mm')
    text(img, (195, 925), 'TREATED', font('anton', 56), (10, 40, 8, 255), 'mm')
    dk = (16, 46, 22, 255)
    text(img, (370, 812), 'HOME SERVER', font('mono', 22), (60, 110, 60, 255))
    text(img, (370, 840), '00/50', font('anton', 66), dk)
    text(img, (720, 812), 'NODES STERILISED', font('mono', 22), (60, 110, 60, 255))
    text(img, (720, 840), '6/6', font('anton', 66), dk)
    text(img, (1100, 812), 'WIPE IN', font('mono', 22), (60, 110, 60, 255))
    text(img, (1100, 840), '00:02.80', font('anton', 66), dk)
    rect(img, [1480, 850, 1830, 880], outline=dk, width=3)
    rect(img, [1484, 854, 1484 + 342 * 0.86, 876], fill=(90, 200, 50, 255))
    text(img, (1480, 900), 'no appeal is offered.', font('mono', 18), (60, 110, 60, 255))
    text(img, (90, 990), 'a clean cell is a happy cell  ///  operatives reclassified, protocol S-7  ///  heat peak 100', font('mono', 18), (150, 200, 140, 255))
    buttons(img, main_xy=(1330, 1040), new_xy=(1620, 1042))
    return img


def win():
    img = bg()
    channel_bug(img, True)
    # headline, struck
    text(img, (84, 180), 'CONTAMINATION', font('anton', 138), WHITE)
    text(img, (84, 332), 'CONTAINED', font('anton', 138), (140, 175, 140, 255))
    line(img, [60, 428, 640, 420], PINK, 14)
    text(img, (84, 450), 'FAILED', font('anton', 150), CELLY)
    # the tear and RGB split on the broadcast layer only
    img = tear(img, 4, 9, 34, 150, 620, 26)
    img = rgb_split(img, 4)
    # seized footage: the hacked helix
    arr = d2_city.hacked_city()
    footage(img, [1010, 120, 1860, 520], arr, 'FEED OVERRIDE  //  HELIX PARK', CYAN)
    sticker(img, 'REBEL_CELL', 1700, 528, 260, 48, PINK, None, rot=-4, size=32)
    # CRT audit window seizing the lower right
    x0, y0, x1, y1 = 1010, 550, 1860, 996
    crt_panel(img, [x0, y0, x1, y1], CYAN, '> AUDIT // SOLACE BIOSYSTEMS  [CLOSED]', fill=(5, 12, 26, 236))
    mono = font('mono', 20)
    wh = (232, 240, 250, 255)
    y = y0 + 48
    for k, v in [('SUBJECT', 'REBEL_CELL (cell-03)'), ('DURATION', '41 days'), ('STATUS', 'SIGNAL SEIZED')]:
        kv_row(img, x0 + 24, y, k + ' ....', v, mono, CYAN, wh, 160)
        y += 25
    y += 8
    for k, v in [('netruns', '8  (1 operative lost)'), ('raids', '4  (4 repelled, 1 decisive)'), ('exploits', '3 / 3 extracted'), ('schematics', '214 earned / 190 spent')]:
        kv_row(img, x0 + 24, y, k + ' ..', v, mono, (110, 170, 190, 255), wh, 160)
        y += 25
    y += 8
    kv_row(img, x0 + 24, y, 'NETWORK', 'held 5   disabled 0   seized 0', mono, CYAN, wh, 160)
    y += 25
    kv_row(img, x0 + 24, y, 'HOME SERVER', '50 / 50   (peak 7 nodes)', mono, CYAN, wh, 160)
    y += 38
    text(img, (x0 + 24, y), 'HEAT  peak 82', mono, CYAN)
    gx0, gy0, gx1, gy1 = x0 + 70, y + 26, x1 - 40, y + 26 + 56
    seq = [8, 12, 20, 24, 31, 40, 44, 52, 60, 63, 71, 82]
    pts = [(gx0 + (gx1 - gx0) * i / 11, gy1 - (gy1 - gy0) * v / 100) for i, v in enumerate(seq)]
    for v in (25, 50, 75):
        yy_ = gy1 - (gy1 - gy0) * v / 100
        line(img, [gx0, yy_, gx1, yy_], (0, 229, 255, 60), 1)
    line(img, [c for p in pts for c in p], CELLY, 3)
    # operatives: one line
    text(img, (x0 + 24, gy1 + 12), 'OPERATIVES  BREAKER R3 | GHOST R2 (deceased) | RIGGER R1 | BOTNET R2 | WRECKER R0', font('mono', 15), (150, 200, 220, 255))
    # lower-left seized ticker
    rrect(img, [60, 790, 940, 960], 10, fill=(5, 12, 26, 236), outline=PINK, width=3)
    text(img, (84, 812), '> TRANSMISSION OVERRIDDEN', font('mono', 24), PINK)
    text(img, (84, 848), 'this segment is brought to you by', font('mono', 20), wh)
    text(img, (84, 878), 'the cell.  your contaminant is loose.', font('mono', 20), wh)
    text(img, (84, 920), 'clean cells are not happy cells.', font('mono', 20), CELLY)
    stamp(img, 'SIGNAL SEIZED', 560, 690, (255, 62, 160, 235), rot=-6, size=70)
    buttons(img, main_xy=(1330, 1040), new_xy=(1620, 1042))
    return img


if __name__ == '__main__':
    for nm, fn in (('d3_win.png', win), ('d3_lose.png', lose)):
        img = fn()
        img = vignette(img, 0.3)
        # scanlines
        a = np.asarray(img).copy()
        a[::3 * K // 2 * 2, :, :3] = (a[::3 * K // 2 * 2, :, :3] * 0.88).astype(np.uint8)
        img = Image.fromarray(a, 'RGBA')
        finish(img, OUT + nm, 4, 5)
        print('ok', nm)
