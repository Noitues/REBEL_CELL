"""Netrun-failure screen: shared kit. Compositing only (PIL, numpy). Reuses the v2 end-screen helpers (ui_lib, v2_lib).
Everything is drawn at 2x (ui_lib K) in 1920x1080 base coordinates, then downsampled."""
import sys, os, math, random
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/solace_endscreens/v2/scripts')
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from ui_lib import *            # K, W, H, font, text, rrect, rect, line, poly, ellipse, layer, rotate_paste, sticker, glow, S, tw, draw
import v2_lib as V2

ROOT = 'D:/rc_art/art-pass/docs/concepts/'
OUT = ROOT + 'transitions/netrun_fail/'
FONTS['courier'] = ROOT + 'round32_ui_chrome/fonts/CourierPrime-Regular.ttf'
FONTS['courierb'] = ROOT + 'round32_ui_chrome/fonts/CourierPrime-Bold.ttf'

# ---- tokens (BRIEF 3.3) ----
PINK = (255, 62, 160, 255)
LIME = (150, 255, 70, 255)
CYAN = (92, 225, 255, 255)
HARM = (255, 68, 51, 255)
PRED = (255, 28, 44, 255)          # PENCIL_THREAT
AMBER = (255, 176, 0, 255)
GAIN = (123, 224, 123, 255)
VIOLET = (160, 60, 255, 255)
HI = (242, 246, 255, 255)
MID = (175, 192, 214, 255)
LO = (122, 136, 156, 255)
INK = (12, 10, 22, 255)
TBG = (5, 13, 28, 236)
YEL = (255, 226, 0, 255)


def A(c, a):
    return (c[0], c[1], c[2], int(a))


# ---- the one set of facts every design shows (GDD 4.2 death rule, 11.5 heat, 7.3 armory; r42 HUD chips) ----
FACTS = dict(
    site='SEED VAULT EXCHANGE', op='CELL-9 // BREAKER', rank='R1', node=5, nodes=7, ntype='ELITE ROUTER',
    hp='0/60', foe='THE ADJUSTER', turn=2,
    lost=[('CYCLES', '160'), ('DECK', '18 CARDS'), ('FIRMWARE', '1 CHIP'), ('DAEMONS', '1'), ('ASSETS', '1 UNBANKED')],
    heat0=52, heat1=63, crew0=4, crew1=3, home='50/50',
)

PH_TEXT = {
    1: 'Node reached: "ELITE ROUTER 5 OF 7" (which node the run ended on). Node 3 = router and node 4 = terminal come from the r42 loot and event screens; node 5 is mock.',
    2: 'Last fight: "THE ADJUSTER, TURN 2" is read off the combat plate p1_decide (KILL ADJUSTER objective, turn 2). Whether the game records the killer is assumed.',
    3: 'Unbanked-loss values (Cycles 160, deck 18 cards, Firmware 1, Daemons 1, Assets 1). The categories are GDD 4.2 and 7.3; the numbers are mock (Cycles 160 matches the r42 event HUD).',
    4: 'Heat 52 to 63: "+10 + tier" (GDD 11.5) with tier 1 assumed and ICE below 6. At ICE 6 to 10 deaths add +5 more. 63 crosses the minor-60 line (complication), which no design announces.',
    5: 'Crew 4 to 3: CREW is a stat on the r42 Run HUD; that a death decrements it is inferred from "operative permanently lost" (GDD 4.2).',
    6: 'Home server 50/50: standard slot is 50 (GDD 3.2); the current integrity value is mock. Shown only so the player reads that the campaign is not lost.',
    7: 'DISPATCH copy: the voice rule is GDD 8.2 (clean system text); the words are invented. Also unsettled: DISPATCH appearing on this screen at all.',
    8: 'Exit button "GRID VIEW" (label from the r42 route page; T07 says a lost netrun returns to the raid view). A second button ("view run log") is NOT drawn: no such screen exists.',
    9: 'Rank "R1" (route-page file card) and the kept list ("banked Schematics, Armory assets", GDD 7.3): which items are banked is run-dependent.',
}


class PHR:
    def __init__(self):
        self.items = []

    def add(self, box, n):
        self.items.append((tuple(box), n))


# ---------------------------------------------------------------- backdrops (1x, RGB float arrays)
def load_rgb(p):
    return Image.open(p).convert('RGB')


def street_img(zoom=1.0, cx=.5, cy=.5):
    im = load_rgb(ROOT + 'netrun_cel/zoom_rules/round6/street_frame.png')
    if zoom != 1.0:
        w, h = W / zoom, H / zoom
        x0 = min(max(cx * W - w / 2, 0), W - w)
        y0 = min(max(cy * H - h / 2, 0), H - h)
        im = im.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.LANCZOS)
    return im


def to_f(im):
    return np.asarray(im.convert('RGB'), np.float32) / 255.0


def to_img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def lum(a):
    return a @ np.array([0.299, 0.587, 0.114], np.float32)


def grade(a, val=0.5, sat=0.5, tint=(1, 1, 1)):
    l = lum(a)[..., None]
    a = l + (a - l) * sat
    return a * val * np.array(tint, np.float32)


def vignette_f(a, s=0.5, r0=0.5):
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    v = 1 - s * np.clip(d - r0, 0, 1) ** 1.4
    return a * v[..., None]


def scan_f(a, strength=0.18, period=3):
    h = a.shape[0]
    m = np.ones(h, np.float32)
    m[::period] = 1 - strength
    return a * m[:, None, None]


def chroma_f(a, px):
    px = int(round(px))
    if px == 0:
        return a
    o = a.copy()
    o[..., 0] = np.roll(a[..., 0], px, axis=1)
    o[..., 2] = np.roll(a[..., 2], -px, axis=1)
    return o


def static_f(a, amt, seed=1, mono=True):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, amt, a.shape[:2]).astype(np.float32)[..., None]
    return a + n if mono else a + rng.normal(0, amt, a.shape).astype(np.float32)


def bands_f(a, spec, seed=2):
    """spec: list of (y, h, dx, lift). Horizontal tracking tears: shift rows by dx, lift brightness, add jitter."""
    rng = np.random.default_rng(seed)
    o = a.copy()
    for (y, h, dx, lift) in spec:
        y0, y1 = int(max(y, 0)), int(min(y + h, a.shape[0]))
        for r in range(y0, y1):
            j = int(dx * (0.6 + 0.4 * math.sin(r * 0.37 + seed)) + rng.integers(-2, 3))
            o[r] = np.roll(a[r], j, axis=0)
        o[y0:y1] = o[y0:y1] * (1 + lift) + lift * 0.15
    return o


def pink_edge(a, s=0.35):
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    m = np.clip(d - 0.75, 0, 1) ** 1.3 * s
    a = a.copy()
    a[..., 0] += m * 0.55
    a[..., 2] += m * 0.28
    a[..., 1] -= m * 0.05
    return a


def up2(im_rgb):
    return im_rgb.resize((W * K, H * K), Image.LANCZOS).convert('RGBA')


def down(img):
    return img.convert('RGB').resize((W, H), Image.LANCZOS)


# ---------------------------------------------------------------- widgets (base coords)
def glow_text(img, xy, s, f, fill, gcol, radius=10, strength=0.9, anchor='la', stroke=0, stroke_fill=INK):
    Lg = Image.new('RGBA', img.size, (0, 0, 0, 0))
    text(Lg, xy, s, f, gcol, anchor)
    img = glow(img, Lg, radius, strength)
    text(img, xy, s, f, fill, anchor, stroke=stroke, stroke_fill=stroke_fill)
    return img


def split_text(img, xy, s, f, fill=HI, px=5, anchor='la', stroke=0):
    """RGB-split title (a glitched feed)."""
    text(img, (xy[0] - px, xy[1]), s, f, (0, 255, 255, 150), anchor)
    text(img, (xy[0] + px, xy[1]), s, f, (255, 0, 130, 150), anchor)
    text(img, xy, s, f, fill, anchor, stroke=stroke, stroke_fill=INK)


def term_panel(img, box, edge=PINK, title='', tag=None, bg=TBG, tag_col=LO):
    x0, y0, x1, y1 = box
    rrect(img, box, 8, fill=bg, outline=A(edge, 120), width=2)
    rrect(img, [x0 + 5, y0 + 5, x1 - 5, y1 - 5], 6, outline=A(edge, 40), width=1)
    line(img, [x0 + 4, y0 + 46, x1 - 4, y0 + 46], A(edge, 90), 1)
    # corner brackets (r42 look)
    n = 26
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        line(img, [cx + sx * n, cy, cx, cy, cx, cy + sy * n], edge, 3.5)
    text(img, (x0 + 20, y0 + 12), title, font('mono', 22), edge)
    if tag:
        text(img, (x1 - 46, y0 + 15), tag, font('mono', 17), tag_col, 'ra')
        rect(img, [x1 - 38, y0 + 18, x1 - 24, y0 + 32], fill=edge)


def chip(img, x, y, label, col, size=22, h=34, fillA=26):
    """Rounded tag, like the event screen's -12 HP chip. Returns right edge."""
    f = font('anton', size)
    w = tw(label, f) + 26
    rrect(img, [x, y, x + w, y + h], 6, fill=A(col, fillA), outline=col, width=2)
    text(img, (x + w / 2, y + h / 2 + 1), label, f, col, 'mm')
    return x + w


def heat_meter(img, x, y, w, h, v0, v1, show_delta=True):
    """Route-page heat bar (cyan to amber to dark red, ticks 25/50/75) with the added segment hatched pink."""
    for i in range(int(w)):
        t = i / w
        c = (int(92 + (255 - 92) * min(t * 2, 1)), int(225 - (225 - 140) * min(t * 2, 1) - 120 * max(t - .5, 0) * 2),
             int(255 - 255 * min(t * 2, 1)))
        line(img, [x + i, y, x + i, y + h], (c[0], c[1], c[2], 70 if t * 100 > v1 else 255), 1.2)
    # added segment
    xa, xb = x + w * v0 / 100, x + w * v1 / 100
    rect(img, [xa, y, xb, y + h], fill=A(PINK, 215))
    for k in range(int(xa), int(xb) + int(h), 7):
        line(img, [k, y + h, k + h, y], A(INK, 150), 2)
    rect(img, [x, y, x + w, y + h], outline=A(MID, 200), width=1.5)
    for v in (25, 50, 75):
        line(img, [x + w * v / 100, y - 4, x + w * v / 100, y + h + 4], HI, 2)
    return xb


def sword_glyph(img, cx, cy, s, col, rot=-45):
    L = layer(s * 2, s * 2)
    c = s
    line(L, [c, c + s * .62, c, c - s * .62], INK, s * .32)
    line(L, [c, c + s * .62, c, c - s * .62], col, s * .2)
    line(L, [c - s * .36, c + s * .2, c + s * .36, c + s * .2], INK, s * .3)
    line(L, [c - s * .34, c + s * .2, c + s * .34, c + s * .2], col, s * .17)
    rotate_paste(img, L, cx, cy, rot, shadow=False)


def node_icon(img, cx, cy, kind, ring, r=30, fillc=(8, 14, 28, 255), dim=1.0):
    """Route-page node: ring + dark disc + a pictogram. kinds F fight, E elite, T terminal, M modem, R rack."""
    ellipse(img, [cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5], fill=A(INK, int(140 * dim)))
    ellipse(img, [cx - r, cy - r, cx + r, cy + r], fill=fillc, outline=ring, width=4)
    ellipse(img, [cx - r + 7, cy - r + 7, cx + r - 7, cy + r - 7], outline=A(ring, 90), width=1.5)
    g = ring
    if kind == 'F':
        sword_glyph(img, cx, cy, r * .55, g)
    elif kind == 'E':
        for k in range(8):
            a = k * math.pi / 4
            line(img, [cx + math.cos(a) * r * .24, cy + math.sin(a) * r * .24, cx + math.cos(a) * r * .55, cy + math.sin(a) * r * .55], g, 4)
        ellipse(img, [cx - r * .24, cy - r * .24, cx + r * .24, cy + r * .24], outline=g, width=3.5)
    elif kind == 'T':
        rect(img, [cx - r * .5, cy - r * .38, cx + r * .5, cy + r * .24], outline=g, width=3.5)
        line(img, [cx - r * .24, cy + r * .5, cx + r * .24, cy + r * .5], g, 3.5)
        line(img, [cx, cy + r * .24, cx, cy + r * .5], g, 3.5)
        line(img, [cx - r * .28, cy - r * .1, cx - r * .06, cy + .04, cx + r * .26, cy - r * .22], g, 3)
    elif kind == 'M':
        rrect(img, [cx - r * .44, cy - r * .22, cx + r * .44, cy + r * .4], 4, outline=g, width=3.5)
        line(img, [cx - r * .26, cy - r * .22, cx - r * .26, cy - r * .5, cx + r * .26, cy - r * .5, cx + r * .26, cy - r * .22], g, 3.5)
    elif kind == 'R':
        rect(img, [cx - r * .42, cy - r * .5, cx + r * .42, cy + r * .5], outline=g, width=3.5)
        for k in range(3):
            yy = cy - r * .28 + k * r * .28
            line(img, [cx - r * .26, yy, cx + r * .26, yy], g, 3)


def hand(img, xy, s, size, col, rot=0, anchor='la', fontname='marker'):
    f = font(fontname, size)
    w = tw(s, f) + 30
    L = layer(w + 30, size * 1.9)
    text(L, (15, size * .25), s, f, A(INK, 150), 'la', stroke=0)
    text(L, (12, size * .22), s, f, col, 'la')
    rotate_paste(img, L, xy[0], xy[1], rot, shadow=False)


def breaker_bust(w=280, h=315):
    return load_rgb(ROOT + 'round39_portraits/portraits_classes_v2.png').crop((35, 145, 315, 460)).resize((int(w * K), int(h * K)), Image.LANCZOS)


def save_png(img2x, path, g=4, seed=1):
    """finish: light grain, downsample."""
    img2x = grain(img2x, g, seed)
    out = down(img2x)
    out.save(path)
    return out


def ph_overlay(img_rgb, items):
    im = img_rgb.convert('RGBA')
    L = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    f = ImageFont.truetype(FONTS['anton'], 24)
    for (box, n) in items:
        x0, y0, x1, y1 = [int(v) for v in box]
        for x in range(x0, x1, 12):
            d.line([x, y0, min(x + 6, x1), y0], fill=(255, 176, 0, 255), width=3)
            d.line([x, y1, min(x + 6, x1), y1], fill=(255, 176, 0, 255), width=3)
        for y in range(y0, y1, 12):
            d.line([x0, y, x0, min(y + 6, y1)], fill=(255, 176, 0, 255), width=3)
            d.line([x1, y, x1, min(y + 6, y1)], fill=(255, 176, 0, 255), width=3)
        d.rectangle([x0 - 2, y0 - 26, x0 + 28, y0 - 2], fill=(255, 176, 0, 255))
        d.text((x0 + 14, y0 - 14), str(n), font=f, fill=(12, 10, 22, 255), anchor='mm')
    im.alpha_composite(L)
    return im.convert('RGB')
