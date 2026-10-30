"""Direction 1: the Solace specimen file (lab bench, Petri dish, biosafety incident paper)."""
import sys, math, random
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/solace_endscreens/scripts')
from ui_lib import *

OUT = 'D:/rc_art/art-pass/docs/concepts/solace_endscreens/'
INK = (10, 18, 14, 255)
CITY = Image.open(R + 'docs/concepts/tide_raid/G1_parity/r42/plan_r42.png').convert('RGB')
LIME = (150, 255, 70, 255)          # Solace #96FF46
CELLY = (212, 255, 0, 255)          # Cell lime #D4FF00
CYAN = (0, 229, 255, 255)
PINK = (255, 62, 160, 255)
PAPER = (232, 240, 226, 255)
PAPER_INK = (20, 44, 28, 255)


def bench():
    img = new((8, 16, 12, 255))
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # lamp pool from top-left, falling off to the right bottom
    d = np.sqrt(((xx - w * 0.30) / w) ** 2 + ((yy - h * 0.05) / h) ** 2)
    pool = np.clip(1 - d * 1.5, 0, 1) ** 1.6
    a[..., 0] += pool * 22
    a[..., 1] += pool * 60
    a[..., 2] += pool * 28
    # brushed steel streaks
    rng = np.random.default_rng(3)
    streak = rng.normal(0, 1, (h, 1)).astype(np.float32)
    streak = np.asarray(Image.fromarray(((streak * 20 + 128).clip(0, 255)).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))).astype(np.float32) - 128
    a[..., :3] += (streak[:, :1] * 0.20)[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    d = draw(img)
    # pegboard dots
    for y in range(40, 1080, 44):
        for x in range(30, 1920, 44):
            d.ellipse(S([x - 2, y - 2, x + 2, y + 2]), fill=(0, 0, 0, 90))
    # bench edge rule + cable
    line(img, [0, 1050, 1920, 1050], (150, 255, 70, 50), 2)
    return img


def petri(img, cx, cy, r, win):
    # shadow
    sh = layer(2 * r + 80, 2 * r + 80)
    ellipse(sh, [40 + 14, 40 + 22, 40 + 14 + 2 * r, 40 + 22 + 2 * r], fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(S(18)))
    img.alpha_composite(sh, (S(cx - r - 40), S(cy - r - 40)))
    # glass base
    ellipse(img, [cx - r, cy - r, cx + r, cy + r], fill=(150, 205, 190, 70), outline=INK, width=5)
    ellipse(img, [cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10], fill=(18, 40, 30, 255), outline=INK, width=3)
    ra = r - 24
    # agar: 3 toon bands
    base = (130, 196, 74, 255) if win else (150, 190, 120, 255)
    ellipse(img, [cx - ra, cy - ra, cx + ra, cy + ra], fill=base, outline=INK, width=4)
    shade = layer(2 * ra + 8, 2 * ra + 8)
    ellipse(shade, [4 + 26, 4 + 30, 4 + 2 * ra + 26, 4 + 2 * ra + 30], fill=(60, 110, 40, 255) if win else (96, 130, 80, 255))
    m = Image.new('L', shade.size, 0)
    ImageDraw.Draw(m).ellipse(S([4, 4, 4 + 2 * ra, 4 + 2 * ra]), fill=255)
    shade.putalpha(ImageChops.multiply(shade.split()[3], m))
    img.alpha_composite(shade, (S(cx - ra - 4), S(cy - ra - 4)))
    hi = layer(2 * ra + 8, 2 * ra + 8)
    ellipse(hi, [4 - 30, 4 - 34, 4 + 2 * ra - 30, 4 + 2 * ra - 34], fill=(214, 255, 130, 255) if win else (220, 236, 200, 255))
    hi.putalpha(ImageChops.multiply(hi.split()[3], m))
    img.alpha_composite(hi, (S(cx - ra - 4), S(cy - ra - 4)))
    # restore the lit centre band
    ellipse(img, [cx - ra + 28, cy - ra + 30, cx + ra - 30, cy + ra - 28], fill=base)
    ellipse(img, [cx - ra, cy - ra, cx + ra, cy + ra], outline=INK, width=4)
    rng = random.Random(11 if win else 12)
    cols = [CYAN, PINK, CELLY]
    if win:
        # colony growth from near the centre, three hues, each a toon blob with ink line
        pts = []
        for i in range(210):
            ang = rng.uniform(0, 6.283)
            rad = (rng.random() ** 0.62) * ra * 0.80
            pts.append((cx - 18 + math.cos(ang) * rad * 0.95, cy + 10 + math.sin(ang) * rad, rng.uniform(5, 15)))
        pts.sort(key=lambda p: p[2])
        for k, (x, y, rr) in enumerate(pts):
            c = cols[(k * 7 + int(x)) % 3]
            ellipse(img, [x - rr, y - rr, x + rr, y + rr], fill=c, outline=INK, width=2.5)
            ellipse(img, [x - rr * 0.55, y - rr * 0.65, x - rr * 0.05, y - rr * 0.15], fill=(255, 255, 255, 140))
        # tendrils reaching the rim
        for i in range(9):
            ang = rng.uniform(-1.0, 1.4) + 0.0
            pts2 = [(cx - 18, cy + 10)]
            for s_ in range(1, 16):
                rr_ = ra * s_ / 15
                aa = ang + math.sin(s_ * 0.9 + i) * 0.17
                pts2.append((cx - 18 + math.cos(aa) * rr_, cy + 10 + math.sin(aa) * rr_))
            line(img, pts2, INK, 5)
            line(img, pts2, cols[i % 3], 2.6)
    else:
        # the culture, killed: grey-brown specks, a cleared ring, no hue left
        ring = layer(2 * ra + 8, 2 * ra + 8)
        ellipse(ring, [4 + ra * 0.38, 4 + ra * 0.38, 4 + ra * 1.62, 4 + ra * 1.62], fill=(238, 244, 232, 220), outline=(255, 255, 255, 255), width=3)
        ring.putalpha(ImageChops.multiply(ring.split()[3], m))
        img.alpha_composite(ring, (S(cx - ra - 4), S(cy - ra - 4)))
        for i in range(70):
            ang = rng.uniform(0, 6.283)
            rad = (rng.random() ** 0.6) * ra * 0.34
            x, y = cx - 10 + math.cos(ang) * rad, cy + 6 + math.sin(ang) * rad
            rr = rng.uniform(2.5, 7)
            ellipse(img, [x - rr, y - rr, x + rr, y + rr], fill=(88, 84, 76, 255), outline=INK, width=1.5)
        # blue-grey tint where the Cell hues used to be
        ellipse(img, [cx - ra * 0.11, cy - ra * 0.11, cx + ra * 0.11, cy + ra * 0.11], outline=(0, 229, 255, 90), width=2)
    # glass highlights
    d = draw(img)
    for (a0, a1, wd, al) in [(200, 262, 9, 150), (292, 308, 5, 110), (20, 36, 5, 70)]:
        d.arc(S([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4]), a0, a1, fill=(255, 255, 255, al), width=S(wd))
    ellipse(img, [cx - r, cy - r, cx + r, cy + r], outline=INK, width=5)
    return ra


def paper_card(w, h, title_band=None, band=LIME):
    L = layer(w + 20, h + 20)
    rect(L, [10, 10, 10 + w, 10 + h], fill=PAPER)
    # paper tooth
    a = np.asarray(L).astype(np.float32)
    rng = np.random.default_rng(5)
    n = rng.normal(0, 3.5, a.shape[:2])[..., None]
    a[..., :3] = np.clip(a[..., :3] + n * (a[..., 3:4] / 255), 0, 255)
    L = Image.fromarray(a.astype(np.uint8), 'RGBA')
    return L


def solace_seal(img, cx, cy, r, color=(30, 120, 40, 255)):
    ellipse(img, [cx - r, cy - r, cx + r, cy + r], outline=color, width=3)
    ellipse(img, [cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8], outline=color, width=1.5)
    # helix glyph
    pts_a, pts_b = [], []
    for i in range(0, 21):
        t = i / 20
        y = cy - r * 0.55 + t * r * 1.1
        x = math.sin(t * 6.283 * 1.15) * r * 0.30
        pts_a.append((cx + x, y))
        pts_b.append((cx - x, y))
    line(img, pts_a, color, 4)
    line(img, pts_b, (color[0], color[1], color[2], 150), 4)
    for i in range(1, 20, 3):
        line(img, [pts_a[i], pts_b[i]], color, 2)


def heat_graph(L, x0, y0, x1, y1, ink, win):
    for v in (25, 50, 75):
        y = y1 - (y1 - y0) * v / 100
        draw(L).line(S([x0, y, x1, y]), fill=(60, 80, 60, 150), width=S(1))
        text(L, (x0 - 12, y), str(v), font('mono', 15), (70, 90, 70, 255), 'rm')
    seq = [8, 12, 20, 24, 31, 40, 44, 52, 60, 63, 71, 82] if win else [10, 18, 25, 38, 45, 60, 71, 84, 96, 100, 100, 100]
    pts = [(x0 + (x1 - x0) * i / (len(seq) - 1), y1 - (y1 - y0) * min(v, 100) / 100) for i, v in enumerate(seq)]
    line(L, pts, ink, 2)
    for i, p in enumerate(pts):
        r_ = 5 if i in (3, 7, len(pts) - 1) else 3
        ellipse(L, [p[0] - r_, p[1] - r_, p[0] + r_, p[1] + r_], fill=(200, 30, 40, 255) if r_ == 5 else ink)


def polaroid(img, crop, caption, cx, cy, rot, w=160, h=196):
    L = layer(w + 20, h + 20)
    rect(L, [10, 10, 10 + w, 10 + h], fill=(236, 240, 232, 255))
    im = CITY.crop(crop).resize((int((w - 28) * K), int((h - 66) * K)), Image.LANCZOS).convert('RGBA')
    # under-UI grade so the city sits back
    a = np.asarray(im).astype(np.float32)
    a[..., :3] *= 0.78
    im = Image.fromarray(a.astype(np.uint8), 'RGBA')
    L.alpha_composite(im, (S(24), S(24)))
    rect(L, [24, 24, 10 + w - 14, 24 + h - 66], outline=INK, width=2)
    text(L, (10 + w / 2, 10 + h - 34), caption, font('hand', 15), (30, 60, 130, 255), 'mm')
    # tape
    rect(L, [10 + w / 2 - 34, 4, 10 + w / 2 + 34, 24], fill=(214, 220, 170, 200))
    rotate_paste(img, L, cx, cy, rot)


def personnel(img, win, x, y, w=700):
    h = 330
    L = paper_card(w, h)
    text(L, (28, 26), 'SAMPLE LOG   //   IDENTIFIED OPERATIVES', font('courierb', 22), PAPER_INK)
    line(L, [28, 56, w - 6, 56], PAPER_INK, 2)
    rows = [('BREAKER', 'R3', '7 runs', 'ON SITE (stationed)', False),
            ('GHOST', 'R2', 'Server Rack', 'DECEASED  run 9', not win),
            ('RIGGER', 'R1', 'elite router', 'DECEASED  run 4' if not win else 'ON SITE (reserve)', not win),
            ('BOTNET', 'R2', '5 runs', 'ON SITE (reserve)', False),
            ('WRECKER', 'R0', 'the final run', 'DECEASED  run 11' if not win else 'ON SITE', False)]
    for i, (n, r_, sub, st, dead) in enumerate(rows):
        yy = 84 + i * 48
        ellipse(L, [30, yy - 4, 62, yy + 28], outline=PAPER_INK, width=2)
        text(L, (46, yy + 12), n[0], font('anton', 20), PAPER_INK, 'mm')
        text(L, (78, yy), n + '   ' + r_, font('courierb', 21), PAPER_INK)
        text(L, (78, yy + 24), sub, font('courier', 15), (70, 96, 70, 255))
        dead2 = 'DECEASED' in st
        text(L, (360, yy + 2), st, font('courier', 19), (176, 36, 36, 255) if dead2 else PAPER_INK)
        if dead2:
            line(L, [78, yy + 13, 330, yy + 13], PAPER_INK, 2)
    rotate_paste(img, L, x + w / 2 + 10, y + h / 2 + 10, 0.6)


def report(img, win):
    w, h = 1000, 930
    L = paper_card(w, h)
    # letterhead
    solace_seal(L, 84, 92, 40)
    text(L, (146, 62), 'SOLACE BIOSYSTEMS', font('plex', 38), (24, 110, 40, 255))
    text(L, (146, 108), 'BIOSAFETY DIVISION  //  INCIDENT 7' if win else 'BIOSAFETY DIVISION  //  STERILISATION 7', font('plexr', 24), PAPER_INK)
    rect(L, [40, 148, w - 20, 154], fill=(100, 220, 60, 255))
    text(L, (40, 176), 'CONTAINMENT REPORT' if win else 'CERTIFICATE OF TREATMENT', font('courierb', 50), (12, 28, 16, 255))
    ink = PAPER_INK
    f = font('courier', 23)
    if win:
        rows = [('SUBJECT .......', 'REBEL_CELL   (cell-03)'),
                ('DURATION ......', '41 days'),
                ('STATUS ........', 'ESCAPED CONTAINMENT')]
    else:
        rows = [('SUBJECT .......', 'REBEL_CELL   (cell-03)'),
                ('HOME SERVER ...', '00/50'),
                ('NODES STERILISED', '6/6')]
    y = 256
    for k, v in rows:
        text(L, (44, y), k, f, ink)
        text(L, (300, y), v, f, ink)
        y += 32
    if win:
        y = 372
        text(L, (44, y), 'ACTIVITY', f, ink)
        for k, v in [('netruns .......', '8    (1 operative lost)'), ('raids .........', '4    (4 repelled, 1 decisive)'),
                     ('exploits ......', '3 / 3 extracted'), ('schematics ....', '214 earned / 190 spent')]:
            y += 32
            text(L, (74, y), k, f, ink)
            text(L, (300, y), v, f, ink)
        y += 58
        text(L, (44, y), 'NETWORK AT CLOSURE', f, ink)
        y += 32
        text(L, (74, y), 'held 5     disabled 0     seized 0', f, ink)
        y += 32
        text(L, (74, y), 'home server   50 / 50    (peak 7 nodes)', f, ink)
        y += 62
        text(L, (44, y), "HEAT (subject's exposure), peak 82:", f, ink)
        heat_graph(L, 96, y + 34, 800, y + 34 + 150, ink, True)
    else:
        y = 372
        text(L, (44, y), 'WIPE IN', font('mono', 22), (24, 110, 40, 255))
        text(L, (44, y + 24), '00:02.80', font('mono', 100), (12, 28, 16, 255))
        # progress bar
        rect(L, [44, y + 150, w - 60, y + 178], outline=ink, width=2)
        rect(L, [48, y + 154, 48 + (w - 112) * 0.86, y + 174], fill=(100, 220, 60, 255))
        text(L, (44, y + 200), 'no appeal is offered.  your station is now a clean surface.', font('courier', 21), ink)
        text(L, (44, y + 232), 'specimen sterilised under protocol S-7  /  all strains accounted for', font('courier', 19), (70, 96, 70, 255))
        y += 288
        text(L, (44, y), 'HEAT (subject\'s exposure), peak 100:', f, ink)
        heat_graph(L, 96, y + 34, 800, y + 34 + 130, ink, False)
    text(L, (44, h - 20), 'filed by: M. OKAFOR, BIOSAFETY 7', font('courier', 18), (70, 96, 70, 255), 'ls')
    text(L, (w - 120, h - 22), 'M.Okafor', font('hand', 40), (30, 60, 150, 255), 'rs')
    rotate_paste(img, L, 1300, 520, -0.7)


def run(win):
    img = bench()
    petri(img, 320, 305, 225, win)
    if win:
        rng = random.Random(4)
        cols = [CYAN, PINK, CELLY]
        x, y = 470, 478
        for i in range(30):
            x += rng.uniform(8, 20)
            y += rng.uniform(6, 16) * (1 if i < 10 else -0.2)
            rr = max(3, 11 - i * 0.28)
            ellipse(img, [x - rr, y - rr, x + rr, y + rr], fill=cols[i % 3], outline=INK, width=2)
        text(img, (60, 40), 'CELL-03  //  NOT CONTAINED', font('mono', 22), CELLY)
        sticker(img, 'REBEL_CELL', 190, 540, 230, 46, (255, 62, 160, 255), (20, 8, 20, 255), rot=-4, size=32)
    else:
        text(img, (60, 40), 'CELL-03  //  TREATED', font('mono', 22), LIME)
        sticker(img, 'STERILE', 190, 540, 200, 50, (150, 255, 70, 255), (14, 40, 10, 255), rot=3, size=36)
    polaroid(img, (1560, 40, 1900, 400), 'HOME SERVER' + (' 50/50' if win else ' 0/50'), 640, 150, -6)
    polaroid(img, (1320, 540, 1700, 880), 'BEACON', 700, 335, 3)
    polaroid(img, (480, 330, 880, 700), 'NODES AT THE END', 625, 520, -3)
    personnel(img, win, 30, 640, 700)
    report(img, win)
    if win:
        stamp(img, 'CONTAINMENT FAILED', 1590, 640, (205, 40, 50, 235), rot=-7, size=54)
        postit(img, (1550, 120, 1860, 290), (170, 226, 255, 245), 'contaminant is\nin the supply\nline. who left\nthe lid off?', rot=4, size=27)
        postit(img, (1620, 760, 1890, 940), (170, 255, 120, 245), 'it hums the\nSolace jingle.\nflag it.', rot=-4, size=26, fg=(30, 70, 40, 255))
    else:
        stamp(img, 'STERILE', 1400, 405, (30, 140, 40, 240), rot=-7, size=96)
        postit(img, (1560, 100, 1870, 270), (200, 255, 150, 245), 'all strains\naccounted for.\nlid sealed.', rot=3, size=27, fg=(30, 70, 40, 255))
        postit(img, (1630, 770, 1890, 930), (255, 226, 80, 245), 'they will be\nback. log the\nPHANTOM.', rot=-4, size=26)
    return img


if __name__ == '__main__':
    for win in (True, False):
        img = run(win)
        buttons(img, main_xy=(1470, 1030), new_xy=(1740, 1032))
        img = vignette(img, 0.35)
        finish(img, OUT + ('d1_win.png' if win else 'd1_lose.png'), 5, 1 if win else 2)
        print('ok', win)
