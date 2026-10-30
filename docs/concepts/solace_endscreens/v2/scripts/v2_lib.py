"""v2 folder-memo helpers: desk, manila folder, memo paper, routing slip, clip, tape, grease pencil, prints."""
import sys, math, random
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/solace_endscreens/v2/scripts')
from ui_lib import *

OUT = 'D:/rc_art/art-pass/docs/concepts/solace_endscreens/v2/'
INK = (10, 18, 14, 255)
LIME = (150, 255, 70, 255)
CELLY = (212, 255, 0, 255)
CYAN = (0, 229, 255, 255)
PINK = (255, 62, 160, 255)
RED = (255, 28, 44, 255)
PAPER = (236, 241, 230, 255)
PAPER_INK = (20, 44, 28, 255)
BLUE_PEN = (30, 60, 150, 255)
MANILA = (214, 184, 128)


def noise_img(w, h, seed, sigma):
    rng = np.random.default_rng(seed)
    n = rng.random((h // 4 + 2, w // 4 + 2)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(sigma))
    a = np.asarray(im).astype(np.float32) / 255
    return (a - a.mean())


def desk(dark=1.0):
    img = new((8, 16, 12, 255))
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w * 0.5) / w) ** 2 + ((yy - h * 0.1) / h) ** 2)
    pool = np.clip(1 - d * 1.4, 0, 1) ** 1.6
    a[..., 0] += pool * 20
    a[..., 1] += pool * 52
    a[..., 2] += pool * 26
    rng = np.random.default_rng(3)
    st = rng.normal(0, 1, (h, 1)).astype(np.float32)
    st = np.asarray(Image.fromarray(((st * 20 + 128).clip(0, 255)).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))).astype(np.float32) - 128
    a[..., :3] += (st[:, :1] * 0.2)[..., None]
    img = Image.fromarray(np.clip(a * dark, 0, 255).astype(np.uint8), 'RGBA')
    d = draw(img)
    for y in range(40, 1080, 44):
        for x in range(30, 1920, 44):
            d.ellipse(S([x - 2, y - 2, x + 2, y + 2]), fill=(0, 0, 0, 90))
    return img


def crest(img, cx, cy, r, color=(30, 120, 40, 255), w=3):
    ellipse(img, [cx - r, cy - r, cx + r, cy + r], outline=color, width=w)
    ellipse(img, [cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8], outline=color, width=max(1, w / 2))
    pa, pb = [], []
    for i in range(0, 21):
        t = i / 20
        y = cy - r * 0.55 + t * r * 1.1
        x = math.sin(t * 6.283 * 1.15) * r * 0.30
        pa.append((cx + x, y))
        pb.append((cx - x, y))
    line(img, [c for p in pa for c in p], color, w + 1)
    line(img, [c for p in pb for c in p], (color[0], color[1], color[2], 150), w + 1)
    for i in range(1, 20, 3):
        line(img, [pa[i][0], pa[i][1], pb[i][0], pb[i][1]], color, max(1, w - 1))


def manila_folder(img, tab_label, tab_sub, hazard=True):
    """An open manila folder, two halves, tab on the left half with the Solace crest."""
    X0, Y0, X1, Y1 = 50, 96, 1870, 1030
    base = layer(1920, 1080)
    # drop shadow
    sh = layer(1920, 1080)
    rrect(sh, [X0 + 8, Y0 + 14, X1 + 8, Y1 + 14], 16, fill=(0, 0, 0, 190))
    sh = sh.filter(ImageFilter.GaussianBlur(S(16)))
    img.alpha_composite(sh)
    # tab
    tb = [124, 52, 540, 52 + 56]
    poly(img, [(tb[0] - 26, Y0), (tb[0], tb[1] + 2), (tb[2], tb[1] + 2), (tb[2] + 30, Y0)], fill=MANILA + (255,))
    # halves
    rrect(img, [X0, Y0, 960, Y1], 14, fill=(206, 176, 120, 255))
    rrect(img, [960, Y0, X1, Y1], 14, fill=(218, 188, 132, 255))
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    # fibre grain + edge shading + crease gradient in the folder area only
    region = np.zeros((h, w), np.float32)
    region[S(Y0):S(Y1), S(X0):S(X1)] = 1
    n = noise_img(w, h, 7, 1.2) * 14 + noise_img(w, h, 8, 30) * 40
    xs = np.arange(w, dtype=np.float32) / K
    crease = np.exp(-((xs - 960) / 26) ** 2) * -26 + np.exp(-((xs - 967) / 3) ** 2) * 14
    edge = np.clip((np.minimum(xs - X0, X1 - xs)) / 70, 0, 1)[None, :] * 0.0
    a[..., :3] += (n[..., None] + crease[None, :, None]) * region[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    # tab content (re-draw over grain): label strip with crest and the file number
    rrect(img, [tb[0] + 18, tb[1] + 10, tb[2] - 6, tb[3] - 3], 4, fill=(238, 240, 226, 255), outline=(60, 90, 50, 255), width=1.5)
    crest(img, tb[0] + 52, tb[1] + 31, 20, (30, 120, 40, 255), 2)
    text(img, (tb[0] + 82, tb[1] + 20), tab_label, font('courierb', 19), PAPER_INK)
    text(img, (tb[0] + 82, tb[1] + 40), tab_sub, font('courier', 13), (70, 96, 70, 255))
    # hazard strip along the folder head (left half)
    if hazard:
        L = layer(1920, 1080)
        rect(L, [X0 + 14, Y0 + 12, 940, Y0 + 30], fill=(20, 30, 18, 255))
        for k in range(-2, 80):
            x = X0 + 14 + k * 22
            poly(L, [(x, Y0 + 30), (x + 11, Y0 + 12), (x + 22, Y0 + 12), (x + 11, Y0 + 30)], fill=LIME)
        m = Image.new('L', L.size, 0)
        ImageDraw.Draw(m).rectangle(S([X0 + 14, Y0 + 12, 940, Y0 + 30]), fill=255)
        L.putalpha(ImageChops.multiply(L.split()[3], m))
        img.alpha_composite(L)
    return img


def paper_sheet(w, h, seed=5):
    L = layer(w + 24, h + 24)
    rect(L, [12, 12, 12 + w, 12 + h], fill=PAPER)
    a = np.asarray(L).astype(np.float32)
    n = noise_img(a.shape[1], a.shape[0], seed, 0.9) * 22
    a[..., :3] = np.clip(a[..., :3] + n[..., None] * (a[..., 3:4] / 255), 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def heat_graph(L, x0, y0, x1, y1, win):
    for v in (25, 50, 75):
        y = y1 - (y1 - y0) * v / 100
        line(L, [x0, y, x1, y], (60, 80, 60, 150), 1)
        text(L, (x0 - 10, y), str(v), font('mono', 14), (70, 90, 70, 255), 'rm')
    seq = [8, 12, 20, 24, 31, 40, 44, 52, 60, 63, 71, 82] if win else [10, 18, 25, 38, 45, 60, 71, 84, 96, 100, 100, 100]
    pts = [(x0 + (x1 - x0) * i / (len(seq) - 1), y1 - (y1 - y0) * min(v, 100) / 100) for i, v in enumerate(seq)]
    line(L, [c for p in pts for c in p], PAPER_INK, 2)
    for i, p in enumerate(pts):
        r_ = 5 if i in (3, 7, len(pts) - 1) else 3
        ellipse(L, [p[0] - r_, p[1] - r_, p[0] + r_, p[1] + r_], fill=(200, 30, 40, 255) if r_ == 5 else PAPER_INK)


def memo(win, w=850, h=900):
    """The corp internal memo: same fields as the Halcyon dossier, Solace voice."""
    L = paper_sheet(w, h)
    ink = PAPER_INK
    f = font('courier', 20)
    fb = font('courierb', 20)
    crest(L, 82, 86, 38)
    text(L, (136, 54), 'SOLACE BIOSYSTEMS', font('plex', 36), (24, 110, 40, 255))
    text(L, (136, 98), 'INTERNAL MEMORANDUM  //  NOT FOR DISTRIBUTION', font('plexr', 21), ink)
    rect(L, [40, 134, w - 10, 140], fill=(100, 220, 60, 255))
    rows = [('TO:', 'BIOSAFETY DIVISION'), ('FROM:', 'SECURITY OPS (M. OKAFOR)'),
            ('RE:', 'ACTIVITY OF CELL-03 (REBEL_CELL)' if win else 'DISPOSAL OF CELL-03 (REBEL_CELL)')]
    y = 160
    for k, v in rows:
        text(L, (44, y), k, fb, ink)
        text(L, (130, y), v, f, ink)
        y += 28
    line(L, [40, y + 6, w - 10, y + 6], ink, 1.5)
    y += 26
    if win:
        for k, v in [('STATUS ..........', 'ESCAPED CONTAINMENT'), ('DURATION ........', '41 days')]:
            text(L, (44, y), k, f, ink); text(L, (270, y), v, f, ink); y += 28
        y += 8
        text(L, (44, y), 'ACTIVITY', fb, ink); y += 28
        for k, v in [('netruns .........', '8   (1 operative lost)'), ('raids ...........', '4   (4 repelled, 1 decisive)'),
                     ('exploits ........', '3 / 3 extracted'), ('schematics ......', '214 earned / 190 spent')]:
            text(L, (66, y), k, f, ink); text(L, (270, y), v, f, ink); y += 28
        y += 8
        text(L, (44, y), 'NETWORK AT CLOSURE', fb, ink); y += 28
        text(L, (66, y), 'held 5    disabled 0    seized 0', f, ink); y += 28
        text(L, (66, y), 'home server   50 / 50    (peak 7 nodes)', f, ink); y += 40
        text(L, (44, y), "HEAT (subject's exposure), peak 82:", f, ink)
        heat_graph(L, 96, y + 40, w - 70, y + 40 + 120, True)
    else:
        for k, v in [('HOME SERVER ......', '00/50'), ('NODES STERILISED ..', '6/6')]:
            text(L, (44, y), k, f, ink); text(L, (310, y), v, f, ink); y += 28
        y += 10
        text(L, (44, y), 'WIPE IN', font('mono', 21), (24, 110, 40, 255))
        text(L, (44, y + 24), '00:02.80', font('mono', 92), (12, 28, 16, 255))
        y += 140
        rect(L, [44, y, w - 60, y + 26], outline=ink, width=2)
        rect(L, [48, y + 4, 48 + (w - 112) * 0.86, y + 22], fill=(100, 220, 60, 255))
        y += 44
        text(L, (44, y), 'no appeal is offered.  your station is now a clean surface.', font('courier', 19), ink)
        y += 28
        text(L, (44, y), 'sterilised under protocol S-7 / all strains accounted for', font('courier', 17), (70, 96, 70, 255))
        y += 46
        text(L, (44, y), "HEAT (subject's exposure), peak 100:", f, ink)
        heat_graph(L, 96, y + 40, w - 70, y + 40 + 100, False)
    text(L, (44, h - 8), 'filed by: M. OKAFOR, BIOSAFETY 7', font('courier', 17), (70, 96, 70, 255), 'ls')
    text(L, (w - 40, h - 14), 'M.Okafor', font('hand', 42), BLUE_PEN, 'rs')
    return L


def paperclip(img, cx, cy, rot=8, col=(190, 196, 204, 255)):
    L = layer(70, 150)
    pts = [(46, 20), (46, 116), (24, 116), (24, 30), (36, 30), (36, 100)]
    # nested loops
    line(L, [46, 126, 46, 36, 36, 20, 24, 36, 24, 118, 14, 128, 14, 40, 26, 10, 46, 10, 58, 28, 58, 126], (60, 64, 72, 255), 7)
    line(L, [46, 126, 46, 36, 36, 20, 24, 36, 24, 118, 14, 128, 14, 40, 26, 10, 46, 10, 58, 28, 58, 126], col, 4)
    rotate_paste(img, L, cx, cy, rot, sh=(3, 5, 14, 90))


def tape(img, cx, cy, rot=-8, w=110, h=34):
    L = layer(w, h)
    rect(L, [0, 0, w, h], fill=(226, 222, 168, 170))
    for k in range(0, int(w), 6):
        line(L, [k, 0, k + 3, 3], (226, 222, 168, 170), 1)
    rect(L, [0, 0, w, 3], fill=(255, 255, 240, 70))
    rotate_paste(img, L, cx, cy, rot, shadow=True, sh=(1, 3, 6, 60))


def pin(img, cx, cy, col=(220, 40, 60, 255)):
    ellipse(img, [cx - 11, cy - 3, cx + 13, cy + 14], fill=(0, 0, 0, 90))
    ellipse(img, [cx - 10, cy - 12, cx + 10, cy + 8], fill=col, outline=(70, 10, 20, 255), width=2)
    ellipse(img, [cx - 6, cy - 9, cx + 1, cy - 3], fill=(255, 255, 255, 190))


def routing_slip(img, cx, cy, rot, win, w=330, h=280):
    L = layer(w + 20, h + 20)
    rect(L, [10, 10, 10 + w, 10 + h], fill=(246, 232, 190, 255))
    rect(L, [10, 10, 10 + w, 40], fill=(96, 200, 60, 255))
    text(L, (22, 25), 'ROUTING SLIP  //  SB-7718', font('courierb', 18), (10, 40, 8, 255), 'lm')
    rows = [('BIOSAFETY', 'MO', True), ('SECURITY OPS', 'RK', True), ('LEGAL', 'TL' if win else 'TL', not win), ('ARCHIVE', '', not win)]
    yy = 64
    for name, ini, chk in rows:
        rect(L, [24, yy, 44, yy + 20], outline=PAPER_INK, width=2)
        if chk:
            line(L, [27, yy + 10, 33, yy + 17, 44, yy + 2], BLUE_PEN, 3)
        text(L, (56, yy + 10), name, font('courier', 17), PAPER_INK, 'lm')
        line(L, [190, yy + 20, 300, yy + 20], PAPER_INK, 1.2)
        if chk and ini:
            text(L, (245, yy + 18), ini, font('hand', 30), BLUE_PEN, 'ms')
        yy += 40
    text(L, (24, yy + 8), 'ACTION:', font('courierb', 16), PAPER_INK)
    text(L, (100, yy + 8), 'NOTE + ' + ('PURSUE' if win else 'CLOSE'), font('hand', 24), BLUE_PEN)
    text(L, (24, yy + 40), 'RETURN TO FILE BY 06:00', font('courier', 14), (110, 90, 40, 255))
    rotate_paste(img, L, cx, cy, rot)


def sample_log(img, win, x, y, w=840, h=290):
    L = paper_sheet(w, h, 11)
    text(L, (30, 34), 'SAMPLE LOG   //   IDENTIFIED OPERATIVES', font('courierb', 22), PAPER_INK)
    line(L, [30, 62, w - 4, 62], PAPER_INK, 2)
    rows = [('BREAKER', 'R3', '7 runs', 'ON SITE (stationed)'),
            ('GHOST', 'R2', 'Server Rack', 'DECEASED  run 9'),
            ('RIGGER', 'R1', 'elite router', 'DECEASED  run 4' if not win else 'ON SITE (reserve)'),
            ('BOTNET', 'R2', '5 runs', 'ON SITE (reserve)'),
            ('WRECKER', 'R0', 'the final run', 'DECEASED  run 11' if not win else 'ON SITE')]
    for i, (n, r_, sub, st) in enumerate(rows):
        yy = 74 + i * 42
        ellipse(L, [30, yy, 62, yy + 32], outline=PAPER_INK, width=2)
        text(L, (46, yy + 17), n[0], font('anton', 20), PAPER_INK, 'mm')
        dead = 'DECEASED' in st
        text(L, (78, yy), n + '   ' + r_, font('courierb', 21), PAPER_INK)
        text(L, (78, yy + 23), sub, font('courier', 15), (70, 96, 70, 255))
        text(L, (430, yy + 4), st, font('courier', 20), (176, 36, 36, 255) if dead else PAPER_INK)
        if dead or (n == 'GHOST'):
            line(L, [78, yy + 12, 330, yy + 12], PAPER_INK, 2)
    rotate_paste(img, L, x + w / 2 + 12, y + h / 2 + 12, 0.5)


def grease(L, pts, col=RED, width=7, seed=0, wob=2.2):
    """Wax grease pencil: wobbly, opaque, dark under-shadow and a sheen line."""
    rng = random.Random(seed)
    pp = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 14))
        for k in range(n):
            t = k / n
            pp.append((x0 + (x1 - x0) * t + rng.uniform(-wob, wob), y0 + (y1 - y0) * t + rng.uniform(-wob, wob)))
    pp.append(pts[-1])
    flat = [c for p in pp for c in p]
    line(L, [c + 2 for c in flat], (30, 0, 6, 150), width + 3)
    line(L, flat, (col[0], col[1], col[2], 245), width)
    line(L, [c - 1.2 for c in flat], (255, 200, 205, 80), max(1.5, width * 0.25))


def grease_circle(L, cx, cy, r, col=RED, width=7, seed=0):
    pts = []
    rng = random.Random(seed)
    for i in range(0, 38):
        t = i / 36 * 6.283 * 1.04
        rr = r * (1 + 0.05 * math.sin(t * 2 + seed))
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
    grease(L, pts, col, width, seed, 1.5)


def glossy_print(img, pic, cx, cy, rot, border=22, caption=None, tapes=True, gloss=True):
    """pic: PIL RGB(A) at K scale. White-bordered glossy photo print with sheen, curl shadow and tape."""
    pw, ph = pic.width / K, pic.height / K
    w, h = pw + border * 2, ph + border * 2 + (34 if caption else 0)
    L = layer(w + 20, h + 20)
    rect(L, [10, 10, 10 + w, 10 + h], fill=(240, 240, 234, 255))
    L.alpha_composite(pic.convert('RGBA'), (S(10 + border), S(10 + border)))
    rect(L, [10 + border, 10 + border, 10 + border + pw, 10 + border + ph], outline=(0, 0, 0, 90), width=1)
    if gloss:
        G = layer(w + 20, h + 20)
        poly(G, [(10 + border, 10 + border), (10 + border + pw * 0.62, 10 + border), (10 + border, 10 + border + ph * 0.5)], fill=(255, 255, 255, 26))
        poly(G, [(10 + border + pw * 0.70, 10 + border), (10 + border + pw * 0.80, 10 + border), (10 + border, 10 + border + ph * 0.66), (10 + border, 10 + border + ph * 0.58)], fill=(255, 255, 255, 18))
        L.alpha_composite(G)
    if caption:
        text(L, (10 + w / 2, 10 + h - 20), caption, font('hand', 24), BLUE_PEN, 'mm')
    rotate_paste(img, L, cx, cy, rot)
    if tapes:
        tape(img, cx - w / 2 + 40, cy - h / 2 + 12, -35)
        tape(img, cx + w / 2 - 40, cy - h / 2 + 12, 35)


def stamp_ink(img, s, cx, cy, color, rot, size):
    stamp(img, s, cx, cy, color, rot, size)
