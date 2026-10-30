"""Campaign-start page: choosing a corp file folder. Solace folder chosen and open, other corps as closed folders behind.
Pickers shown are only those GDD_ART_COVERAGE lists for G7: corporation, ICE, home server, class."""
import sys, math, random
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/solace_endscreens/v2/scripts')
from v2_lib import *

BUST = R + 'docs/concepts/round39_portraits/portraits_classes_v2.png'
YELLOW = (255, 226, 0, 255)


def tint(c, t, k):
    return tuple(int(c[i] * (1 - k) + t[i] * k) for i in range(3))


def closed_folder(img, x, y, w, h, rot, tone, label, sub, glyph, tabx=40):
    L = layer(w + 60, h + 80)
    # tab
    poly(L, [(tabx - 20, 60), (tabx, 34), (tabx + 300, 34), (tabx + 330, 60)], fill=tone + (255,))
    rrect(L, [10, 58, 10 + w, 58 + h], 12, fill=tone + (255,))
    a = np.asarray(L).astype(np.float32)
    n = noise_img(a.shape[1], a.shape[0], 12, 1.1) * 14 + noise_img(a.shape[1], a.shape[0], 13, 28) * 34
    a[..., :3] = np.clip(a[..., :3] + n[..., None] * (a[..., 3:4] / 255), 0, 255)
    L = Image.fromarray(a.astype(np.uint8), 'RGBA')
    rrect(L, [tabx + 14, 42, tabx + 296, 80], 4, fill=(238, 238, 228, 255), outline=(50, 60, 50, 255), width=1.5)
    glyph(L, tabx + 40, 61)
    text(L, (tabx + 70, 52), label, font('courierb', 17), (30, 36, 30, 255))
    text(L, (tabx + 70, 68), sub, font('courier', 12), (80, 86, 80, 255))
    rotate_paste(img, L, x, y, rot)


def g_eye(L, cx, cy):
    ellipse(L, [cx - 14, cy - 8, cx + 14, cy + 8], outline=(90, 60, 170, 255), width=2.5)
    ellipse(L, [cx - 5, cy - 5, cx + 5, cy + 5], fill=(90, 60, 170, 255))


def g_planet(L, cx, cy):
    ellipse(L, [cx - 9, cy - 9, cx + 9, cy + 9], fill=(60, 150, 200, 255))
    ellipse(L, [cx - 16, cy - 4, cx + 16, cy + 4], outline=(30, 90, 140, 255), width=2)


def g_q(L, cx, cy):
    text(L, (cx, cy), '?', font('anton', 24), (40, 40, 44, 255), 'mm')


def sel_ring(img, box, seed=1):
    x0, y0, x1, y1 = box
    L = layer(1920, 1080)
    grease_rect(L, x0, y0, x1, y1, seed)
    img.alpha_composite(L)


def grease_rect(L, x0, y0, x1, y1, seed):
    r = 10
    pts = [(x0 + r, y0), (x1 - r, y0), (x1, y0 + r), (x1, y1 - r), (x1 - r, y1), (x0 + r, y1), (x0, y1 - r), (x0, y0 + r), (x0 + r, y0), (x0 + r + 24, y0 - 1)]
    grease(L, pts, YELLOW, 6, seed, 1.4)


def lock(img, cx, cy, col=(120, 120, 130, 255)):
    rect(img, [cx - 8, cy - 2, cx + 8, cy + 10], fill=col)
    line(img, [cx - 5, cy - 2, cx - 5, cy - 8, cx + 5, cy - 8, cx + 5, cy - 2], col, 2.5)


def portrait(img, name, cls, box, cx, cy, rot, locked, cost=None, selected=False):
    w, h = 150, 188
    L = layer(w + 20, h + 20)
    rect(L, [10, 10, 10 + w, 10 + h], fill=(240, 240, 232, 255))
    s = Image.open(BUST).convert('RGB').crop(box).resize((int((w - 16) * K), int((w - 16) * K)), Image.LANCZOS)
    a = np.asarray(s).astype(np.float32) / 255
    if locked:
        g = a.mean(2, keepdims=True)
        a = np.repeat(g * 0.55, 3, 2)
    L.alpha_composite(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert('RGBA'), (S(18), S(18)))
    text(L, (10 + w / 2, 10 + h - 24), name, font('hand', 22), BLUE_PEN if not locked else (110, 110, 120, 255), 'mm')
    text(L, (10 + w / 2, 10 + h - 9), cls if not locked else ('UNLOCK %d' % cost), font('mono', 12), (60, 70, 60, 255), 'mm')
    if locked:
        lock(L, 10 + w - 22, 30)
    rotate_paste(img, L, cx, cy, rot)
    if selected:
        tape(img, cx, cy - h / 2 + 4, 0, 90, 28)


def build():
    img = desk(0.9)
    # ---- closed corp folders behind (corporation picker: the others)
    closed_folder(img, 280, 262, 520, 260, -3, tint(MANILA, (110, 80, 200), 0.72), 'HALCYON CIVIC', 'best ICE 2', g_eye)
    closed_folder(img, 960, 250, 520, 260, 1.5, tint(MANILA, (50, 140, 215), 0.72), 'ORBITAL COMMONS', 'UNLOCK 160', g_planet, 120)
    closed_folder(img, 1640, 268, 520, 260, 4, tint(MANILA, (40, 40, 48), 0.78), 'CLASSIFIED', 'opens at ICE 10', g_q, 40)
    lock(img, 1300, 170, (190, 190, 200, 255))
    lock(img, 1830, 182, (190, 190, 200, 255))
    # ---- the chosen Solace folder, open, in front
    sh = layer(1920, 1080)
    rrect(sh, [58, 322, 1870, 1060], 16, fill=(0, 0, 0, 200))
    sh = sh.filter(ImageFilter.GaussianBlur(S(18)))
    img.alpha_composite(sh)
    # tab (Solace crest) sits up on the left
    tb = [110, 262, 560, 330]
    poly(img, [(tb[0] - 24, 330), (tb[0], tb[1]), (tb[2], tb[1]), (tb[2] + 30, 330)], fill=MANILA + (255,))
    rrect(img, [50, 330, 960, 1050], 14, fill=(206, 176, 120, 255))
    rrect(img, [960, 330, 1870, 1050], 14, fill=(218, 188, 132, 255))
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    region = np.zeros((h, w), np.float32)
    region[S(330):S(1050), S(50):S(1870)] = 1
    n = noise_img(w, h, 7, 1.2) * 14 + noise_img(w, h, 8, 30) * 40
    xs = np.arange(w, dtype=np.float32) / K
    crease = np.exp(-((xs - 960) / 26) ** 2) * -26 + np.exp(-((xs - 967) / 3) ** 2) * 14
    a[..., :3] += (n[..., None] + crease[None, :, None]) * region[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    rrect(img, [tb[0] + 18, tb[1] + 12, tb[2] - 6, tb[3] - 3], 4, fill=(238, 240, 226, 255), outline=(60, 90, 50, 255), width=1.5)
    crest(img, tb[0] + 54, tb[1] + 36, 22, (30, 120, 40, 255), 2)
    text(img, (tb[0] + 88, tb[1] + 22), 'SOLACE BIOSYSTEMS', font('courierb', 21), PAPER_INK)
    text(img, (tb[0] + 88, tb[1] + 44), 'CORPORATE FILE  //  BEST ICE 6', font('courier', 14), (70, 96, 70, 255))
    # hazard strip
    L = layer(1920, 1080)
    rect(L, [64, 342, 940, 360], fill=(20, 30, 18, 255))
    for k in range(-2, 70):
        x = 64 + k * 22
        poly(L, [(x, 360), (x + 11, 342), (x + 22, 342), (x + 11, 360)], fill=LIME)
    m = Image.new('L', L.size, 0)
    ImageDraw.Draw(m).rectangle(S([64, 342, 940, 360]), fill=255)
    L.putalpha(ImageChops.multiply(L.split()[3], m))
    img.alpha_composite(L)

    # ---- left page: corporation, ICE, home server
    pg = paper_sheet(830, 620, 21)
    d = pg
    text(d, (30, 40), 'NEW CAMPAIGN  //  CHOOSE YOUR FILE', font('courierb', 23), PAPER_INK)
    line(d, [30, 70, 826, 70], PAPER_INK, 2)
    text(d, (30, 100), 'CORPORATION', font('courierb', 20), (24, 110, 40, 255))
    crest(d, 80, 170, 40)
    text(d, (140, 138), 'SOLACE', font('anton', 46), PAPER_INK)
    text(d, (140, 192), 'BIOSYSTEMS   //   best ICE 6', font('courier', 20), (70, 96, 70, 255))
    text(d, (820, 112), 'the others are filed behind', font('hand', 22), BLUE_PEN, 'ra')
    # ICE
    text(d, (30, 250), 'ICE DIFFICULTY  (0-13)', font('courierb', 20), (24, 110, 40, 255))
    for bx, lab in ((34, '-'), (150, '+')):
        rrect(d, [bx, 282, bx + 56, 338], 8, fill=(236, 236, 242, 255), outline=INK, width=3)
        text(d, (bx + 28, 311), lab, font('anton', 40), INK, 'mm')
    text(d, (118, 310), '0', font('anton', 54), PAPER_INK, 'mm')
    text(d, (240, 296), 'ICE 0: the baseline rules.', font('plex', 28), PAPER_INK)
    text(d, (240, 330), 'each step adds one corp rule; ICE 1 opens after your first win', font('courier', 15), (70, 96, 70, 255))
    # home server
    text(d, (30, 398), 'HOME SERVER', font('courierb', 20), (24, 110, 40, 255))
    homes = [('STANDARD', None), ('BUNKER', 40), ('RELAY NEST', 50), ('GHOST HOME', 60), ('FORTRESS', 80)]
    for i, (nm, cost) in enumerate(homes):
        x = 30 + i * 158
        rect(d, [x, 428, x + 148, 520], fill=(250, 248, 238, 255) if cost is None else (222, 226, 214, 255), outline=PAPER_INK, width=2)
        text(d, (x + 74, 458), nm, font('courierb', 17) if cost is None else font('courier', 17), PAPER_INK if cost is None else (120, 130, 120, 255), 'mm')
        if cost is None:
            text(d, (x + 74, 490), 'home server', font('courier', 14), (70, 96, 70, 255), 'mm')
        else:
            lock(d, x + 56, 494, (130, 134, 130, 255))
            text(d, (x + 76, 492), str(cost), font('mono', 16), (120, 130, 120, 255), 'lm')
    text(d, (30, 580), 'Solace Biosystems  //  ICE 0  //  Standard home  //  Breaker', font('mono', 17), (24, 110, 40, 255))
    rotate_paste(img, d, 505, 668, -0.6)
    # selection marks (yellow grease pencil = our pick)
    G = layer(1920, 1080)
    grease_rect(G, 112, 486, 520, 596, 3)
    grease_rect(G, 116, 782, 270, 880, 6)
    grease_rect(G, 100, 664, 300, 730, 5) if False else None
    img.alpha_composite(G)
    # ---- right page: class pickers
    pg2 = paper_sheet(830, 620, 22)
    text(pg2, (30, 40), 'CREW', font('courierb', 23), PAPER_INK)
    text(pg2, (820, 40), 'one operative leads the file', font('hand', 22), BLUE_PEN, 'ra')
    line(pg2, [30, 70, 826, 70], PAPER_INK, 2)
    rotate_paste(img, pg2, 1415, 668, 0.5)
    crew = [('BREAKER', 'class R2', (35, 145, 315, 460), False, None), ('GHOST', 'class R1', (988, 145, 1268, 460), False, None),
            ('HIVEMIND', '', (1465, 625, 1745, 940), True, 60), ('OVERCLOCKER', '', (510, 625, 790, 940), True, 60),
            ('PHANTOM', '', (1465, 145, 1745, 460), True, 60), ('WRECKER', '', (510, 145, 790, 460), True, 60),
            ('BOTNET', '', (988, 625, 1268, 940), True, 80), ('RIGGER', '', (35, 625, 315, 940), True, 80)]
    for i, (nm, cls, box, lk, cost) in enumerate(crew):
        r, c = divmod(i, 4)
        portrait(img, nm, cls, box, 1070 + c * 192, 590 + r * 232, (-2, 1.5, -1, 2.5)[c] * (1 if r == 0 else -1), lk, cost, selected=(i == 0))
    G = layer(1920, 1080)
    grease_rect(G, 990, 490, 1150, 690, 8)
    img.alpha_composite(G)
    # stickers
    sticker(img, 'NEW CAMPAIGN', 340, 62, 340, 68, (255, 226, 0, 255), None, rot=-3, size=52)
    sticker(img, 'TRUST NO ONE', 690, 60, 250, 48, (240, 240, 244, 255), None, rot=2, size=32)
    sticker(img, 'START', 1700, 1000, 250, 90, (255, 62, 160, 255), None, rot=-3, size=66)
    sticker(img, 'BACK', 140, 1010, 150, 52, (236, 236, 242, 255), None, rot=2, size=30)
    stamp(img, "SELECTED", 700, 520, (40, 90, 200, 220), rot=-6, size=34)
    paperclip(img, 960, 372, 8)
    img = vignette(img, 0.35)
    return img


if __name__ == '__main__':
    finish(build(), OUT + 'start_page.png', 5, 7)
    print('ok')
