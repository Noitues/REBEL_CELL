"""The three image-slot contents. All return a PIL image at K scale (2x)."""
import sys, math, random
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/solace_endscreens/v2/scripts')
from v2_lib import *
from vor import edge_dist

SRC_HQ = R + 'docs/concepts/golden_plates/hq_solace_overview.png'      # 2560x1440 Cycles plate
SRC_R42 = R + 'docs/concepts/tide_raid/G1_parity/r42/plan_r42.png'
SRC_BUST = R + 'docs/concepts/round39_portraits/portraits_classes_v2.png'


def to_rgb(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), 'RGB')


def blur(a, s):
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(s))).astype(np.float32) / 255


def smooth_noise(h, w, seed, sigma):
    rng = np.random.default_rng(seed)
    n = rng.random((h // 8 + 2, w // 8 + 2)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(sigma))
    a = np.asarray(im).astype(np.float32) / 255
    return (a - a.min()) / (a.max() - a.min() + 1e-6)


# ---------------------------------------------------------------- A: the helix print
CROP_A = (880, 60, 1940, 1380)      # 1060 x 1320 portrait (8x10-ish), helix centred


def helix_print(win, out_w=440, out_h=548):
    src = Image.open(SRC_HQ).convert('RGB').crop(CROP_A)
    a = np.asarray(src).astype(np.float32) / 255
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    if win:
        # the helix hacked: lime -> cyan, halo -> Cell lime, torn bands, the Cell's network inked over the park
        m = (xx > 250) & (xx < 720) & (yy > 40) & (yy < 1270)
        a, _ = hsv_shift(a, 0.17, 0.46, shift=0.225, sat=1.0, val=1.12, mask=m & (a.max(2) > 0.42))
        ring = (xx > 300) & (xx < 680) & (yy > 60) & (yy < 260)
        a, _ = hsv_shift(a, 0.80, 1.0, shift=0.27, sat=1.0, val=1.05, mask=ring)
        rng = np.random.default_rng(8)
        g = a.copy()
        for i in range(34):
            y0 = int(rng.integers(120, 1250))
            hh = int(rng.integers(3, 20))
            dx = int(rng.integers(-60, 60))
            g[y0:y0 + hh, 220:760] = np.roll(a[y0:y0 + hh, 220:760], dx, axis=1)
            if i % 4 == 0:
                g[y0:y0 + 2, 220:760] = g[y0:y0 + 2, 220:760] * 0.35 + np.array([0.0, 0.9, 1.0]) * 0.65
        a = g
        # a cool cast over the park from the hacked helix
        d = np.sqrt((xx - 450) ** 2 + ((yy - 1000) * 1.3) ** 2)
        a = np.clip(a + (np.exp(-(d / 380) ** 2))[..., None] * np.array([0.0, 0.10, 0.14]), 0, 1)
    else:
        # the Bloom: pink necrosis over the towers, one lime island (park + helix column), pink creeping up the helix
        n = smooth_noise(h, w, 5, 18)
        ex, ey, rx, ry = 470, 1060, 560, 360
        de = np.sqrt(((xx - ex) / rx) ** 2 + ((yy - ey) / ry) ** 2)
        ax, ay, bx, by = 450, 160, 425, 1180
        tt = np.clip(((xx - ax) * (bx - ax) + (yy - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2), 0, 1)
        ds = np.sqrt((xx - (ax + tt * (bx - ax))) ** 2 + (yy - (ay + tt * (by - ay))) ** 2) / 175
        dm = np.minimum(de, ds) + (n - 0.5) * 0.35
        infected = dm > 1.0
        ed = edge_dist(h, w, 2600, 2)
        edge = (ed < 1.6)
        hot = (ed < 0.65)
        inf_soft = blur(infected.astype(np.float32), 3)
        base = a * (1 - inf_soft[..., None] * 0.30)
        base = base + inf_soft[..., None] * np.array([0.40, 0.03, 0.20]) * 0.45
        v_ = blur((edge & infected).astype(np.float32), 0.7)
        hv = blur((hot & infected).astype(np.float32), 0.6)
        pink = np.array([1.0, 0.24, 0.63])
        base = base * (1 - v_[..., None] * 0.8) + pink * v_[..., None] * 0.85 + np.array([1, 0.85, 0.9]) * hv[..., None] * 0.3
        a = np.clip(base, 0, 1)
        # the helix itself is catching: lower third turns pink (as in the A3d plates)
        hm = (xx > 250) & (xx < 720) & (yy > 760) & (yy < 1270) & (n > 0.38)
        a, _ = hsv_shift(a, 0.17, 0.46, shift=0.63, sat=1.0, val=1.0, mask=hm & (a.max(2) > 0.42))
    out = to_rgb(a).resize((out_w * K, out_h * K), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
    if win:
        # network inked over the print (drawn at K scale on the downsampled print)
        L = Image.new('RGBA', out.size, (0, 0, 0, 0))
        sx, sy = out.width / w, out.height / h
        nodes = [(450, 1180), (190, 1020), (700, 1110), (120, 760), (800, 800), (260, 560), (760, 470), (900, 1250)]
        edges = [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6), (1, 7), (2, 7)]
        dl = ImageDraw.Draw(L)
        for p, q in edges:
            dl.line([nodes[p][0] * sx, nodes[p][1] * sy, nodes[q][0] * sx, nodes[q][1] * sy], fill=(0, 229, 255, 215), width=int(2.5 * K))
        out = out.convert('RGBA')
        G = L.filter(ImageFilter.GaussianBlur(5))
        out.alpha_composite(G)
        out.alpha_composite(L)
        dl = ImageDraw.Draw(out)
        for i, (x, y) in enumerate(nodes):
            s_ = (7 if i else 10) * K
            c = (212, 255, 0, 255) if i == 0 else (0, 229, 255, 255)
            dl.rectangle([x * sx - s_, y * sy - s_, x * sx + s_, y * sy + s_], fill=(6, 14, 30, 255), outline=c, width=int(2 * K))
            dl.rectangle([x * sx - s_ / 2.6, y * sy - s_ / 2.6, x * sx + s_ / 2.6, y * sy + s_ / 2.6], fill=c)
    out = out.convert('RGBA')
    # print finish: scan stamp + corner marks
    L = Image.new('RGBA', out.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    f = font('mono', 15)
    d.text((14 * K, 12 * K), 'CAM H-07   HELIX PARK' if True else '', font=f, fill=(255, 190, 60, 235))
    d.text((out.width - 14 * K, 12 * K), '23:41:07' if win else '23:58:52', font=f, fill=(255, 190, 60, 235), anchor='ra')
    d.text((14 * K, out.height - 12 * K), 'SB-7718 / FIG.1', font=f, fill=(255, 190, 60, 235), anchor='ld')
    out.alpha_composite(L)
    return out


# ---------------------------------------------------------------- B: the aerial survey map
def survey_map(win, w=800, h=480):
    src = Image.open(SRC_R42).convert('RGB').crop((0, 0, 1920, 1152 if False else 1080))
    base = src.resize((w * K, int(w * K * 1080 / 1920)), Image.LANCZOS)
    base = base.crop((0, 0, w * K, h * K)) if base.height >= h * K else base.resize((w * K, h * K))
    a = np.asarray(base).astype(np.float32) / 255
    g = a.mean(2, keepdims=True)
    # survey print: faded colour on warm paper, lime park keeps a little life
    a = g + (a - g) * 0.42
    a = a * 0.80 + 0.14
    paper = np.array([0.93, 0.92, 0.84])
    a = a * 0.72 + paper * a.mean(2, keepdims=True) * 0.46
    a = np.clip(a, 0, 1)
    img = to_rgb(a).convert('RGBA')
    L = layer(w, h)
    # survey grid + labels
    for i in range(1, 8):
        x = w * i / 8
        line(L, [x, 0, x, h], (20, 50, 30, 120), 1.2)
        text(L, (x - w / 16, 14), 'ABCDEFGH'[i - 1], font('mono', 15), (20, 50, 30, 230), 'ma')
    text(L, (w * 7.5 / 8, 14), 'H', font('mono', 15), (20, 50, 30, 230), 'ma')
    text(L, (w / 16, 14), 'A', font('mono', 15), (20, 50, 30, 230), 'ma')
    for j in range(1, 5):
        y = h * j / 5
        line(L, [0, y, w, y], (20, 50, 30, 120), 1.2)
        text(L, (10, y - h / 10), str(j), font('mono', 15), (20, 50, 30, 230), 'lm')
    text(L, (10, h * 0.9), '5', font('mono', 15), (20, 50, 30, 230), 'lm')
    # title block
    rect(L, [w - 250, h - 54, w - 8, h - 8], fill=(240, 240, 226, 235), outline=(20, 50, 30, 255), width=1.5)
    text(L, (w - 240, h - 46), 'SOLACE BIOSYSTEMS', font('courierb', 14), PAPER_INK)
    text(L, (w - 240, h - 28), 'SITE SURVEY 7 / GRID 7A', font('courier', 13), PAPER_INK)
    # north arrow
    poly(L, [(34, 66), (46, 100), (34, 92), (22, 100)], fill=(20, 50, 30, 255))
    text(L, (34, 54), 'N', font('mono', 15), (20, 50, 30, 255), 'mm')
    img.alpha_composite(L)
    nodes = [(560, 130, 'HQ'), (110, 260, 1), (260, 150, 2), (430, 270, 3), (600, 340, 4), (330, 400, 5), (700, 230, 6), (180, 410, 7), (470, 90, 8)]
    edges = [(1, 2), (2, 3), (3, 4), (4, 6), (3, 5), (5, 7), (1, 7), (2, 8), (8, 0), (6, 0), (4, 5)]
    G = layer(w, h)
    pos = {i: (n[0], n[1]) for i, n in enumerate(nodes)}
    if win:
        for k, (p, q) in enumerate(edges):
            grease(G, [pos[p], pos[q]], RED, 6, k, 2.2)
        for i, (x, y, lab) in enumerate(nodes):
            grease_circle(G, x, y, 22 if i else 30, RED, 6, i)
            if i:
                text(G, (x + 28, y - 30), str(lab), font('hand', 28), RED)
        text(G, (x := 60, 440), 'the whole thing is theirs', font('hand', 30), RED)
        grease(G, [(120, 98), (190, 140), (180, 118), (192, 142), (170, 134)], RED, 5, 3, 1.2)
    else:
        # the network, crossed out, and the Bloom crawling in from the edges
        rng = np.random.default_rng(4)
        hh, ww = h * K, w * K
        yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
        n = smooth_noise(hh, ww, 9, 22)
        cx, cy = 560 * K, 130 * K
        d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.3) ** 2)
        dm = d / (170 * K) + (n - 0.5) * 0.9
        infected = dm > 1.0
        ed = edge_dist(hh, ww, 1800, 4)
        e = blur(((ed < 1.3) & infected).astype(np.float32), 0.7)
        hot = blur(((ed < 0.5) & infected).astype(np.float32), 0.6)
        arr = np.asarray(img).astype(np.float32) / 255
        arr = arr[..., :3]
        inf_s = blur(infected.astype(np.float32), 3)
        arr = arr * (1 - inf_s[..., None] * 0.35) + inf_s[..., None] * np.array([0.5, 0.05, 0.25]) * 0.35
        arr = arr * (1 - e[..., None] * 0.85) + np.array([1.0, 0.24, 0.63]) * e[..., None] * 0.9 + hot[..., None] * 0.25
        img = to_rgb(np.clip(arr, 0, 1)).convert('RGBA')
        img.alpha_composite(L)
        for k, (p, q) in enumerate(edges):
            grease(G, [pos[p], pos[q]], (160, 20, 36, 200), 5, k, 2.2)
        for i, (x, y, lab) in enumerate(nodes):
            grease_circle(G, x, y, 22 if i else 30, (170, 20, 36, 230), 5, i)
            grease(G, [(x - 24, y - 24), (x + 24, y + 24)], RED, 7, i + 20, 1.5)
            grease(G, [(x + 24, y - 24), (x - 24, y + 24)], RED, 7, i + 40, 1.5)
        grease(G, [(20, 36), (780, 450)], RED, 6, 77, 3)
        text(G, (60, 440), 'network lost. do not restore.', font('hand', 30), RED)
        img.alpha_composite(G)
        return img.convert('RGB')
    img.alpha_composite(G)
    return img.convert('RGB')


# ---------------------------------------------------------------- C: CCTV contact strip
BUSTS = [('BREAKER', 'R3', (35, 145, 315, 460), 'CAM 04  LOBBY'), ('GHOST', 'R2', (988, 145, 1268, 460), 'CAM 11  DOCK'),
         ('RIGGER', 'R1', (35, 625, 315, 940), 'CAM 19  ROOF')]


def cctv_frame(win, i, fw=240, fh=150):
    name, rk, box, cam = BUSTS[i]
    s = Image.open(SRC_BUST).convert('RGB').crop(box)
    # crop to the head, 16:10
    cw = s.width
    ch = int(cw * fh / fw)
    s = s.crop((0, 44, cw, 44 + ch)).resize((fw * K, fh * K), Image.LANCZOS)
    a = np.asarray(s).astype(np.float32) / 255
    g = a.mean(2, keepdims=True)
    a = np.clip(g * np.array([0.55, 1.0, 0.62]) * 1.25 + 0.02, 0, 1)
    rng = np.random.default_rng(i + 3)
    a += rng.normal(0, 0.05, a.shape[:2])[..., None]
    yy = np.arange(a.shape[0])[:, None, None]
    a *= np.where((yy // K) % 3 == 0, 0.82, 1.0)
    a *= 0.92
    if not win:
        a *= 0.45
    f = to_rgb(np.clip(a, 0, 1)).convert('RGBA')
    L = layer(fw, fh)
    green = (150, 255, 110, 255)
    text(L, (8, 6), cam, font('mono', 14), green)
    ellipse(L, [fw - 58, 9, fw - 48, 19], fill=(255, 50, 50, 255))
    text(L, (fw - 44, 6), 'REC', font('mono', 14), green)
    text(L, (8, fh - 8), ('23:3%d:%02d' % (i + 1, 11 + i * 17)) if win else ('00:0%d:%02d' % (i, 20 + i * 9)), font('mono', 14), green, 'ld')
    if win:
        bx0, by0, bx1, by1 = fw * 0.32, fh * 0.14, fw * 0.86, fh * 0.92
        for (px, py, sx, sy) in [(bx0, by0, 1, 1), (bx1, by0, -1, 1), (bx0, by1, 1, -1), (bx1, by1, -1, -1)]:
            line(L, [px, py + 18 * sy, px, py, px + 18 * sx, py], green, 2.5)
        rect(L, [bx0, by1 - 22, bx1, by1], fill=(0, 0, 0, 170))
        text(L, ((bx0 + bx1) / 2, by1 - 11), 'ID MATCH ' + name + ' ' + rk, font('mono', 13), green, 'mm')
    else:
        # redacted / processed
        rect(L, [fw * 0.18, fh * 0.30, fw * 0.82, fh * 0.50], fill=(8, 8, 10, 255))
        text(L, (fw / 2, fh * 0.40), '[ REDACTED ]', font('mono', 15), (150, 150, 150, 255), 'mm')
        text(L, (fw - 8, fh - 8), 'RECLASSIFIED', font('mono', 13), (255, 90, 90, 255), 'rd')
    f.alpha_composite(L)
    return f


def cctv_strip(win):
    fw, fh = 240, 150
    W_, H_ = fw + 62, 3 * (fh + 24) + 70
    L = layer(W_, H_)
    rect(L, [0, 0, W_, H_], fill=(14, 18, 14, 255))
    for i in range(3):
        y = 38 + i * (fh + 24)
        # sprocket holes
        for k in range(0, int(fh), 22):
            rect(L, [8, y + k + 4, 20, y + k + 14], fill=(230, 232, 220, 255))
            rect(L, [W_ - 20, y + k + 4, W_ - 8, y + k + 14], fill=(230, 232, 220, 255))
        L.alpha_composite(cctv_frame(win, i), (S(31), S(y)))
        text(L, (31, y - 10), 'FRAME %02d' % (i + 1), font('mono', 13), (230, 232, 220, 255))
    text(L, (W_ / 2, H_ - 18), 'SB-CCTV  //  CELL-03', font('mono', 14), (230, 232, 220, 255), 'mm')
    return L
