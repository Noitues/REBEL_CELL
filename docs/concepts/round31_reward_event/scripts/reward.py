"""Round 31 -> reward_screen.png (A: peel from a loot sheet, recommended), reward_screen_B.png
(B: decompiled out of the beaten wheel) and reward_reveal.gif (A with B's bit assembly as its entrance).

python reward.py [a|b|gif|all]
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import r31lib as L
import sticker_lib19 as SL

BG = os.path.join(L.CONCEPTS, "round26_hq_targets", "site_meridian_night.jpg")

OFFERS = [
    dict(name="Overload", cost=3, kind="HACK", art="slice_exploit", pic="slice_exploit", val="10", text="Deal 10 damage to the target and take 4. Exhaust.", rar="Uncommon"),
    dict(name="Duck", cost=2, kind="SYSTEM", art="slice_proxy", pic="slice_proxy", val="", text="Evade the next incoming attack this turn.", rar="Uncommon"),
    dict(name="Leech Worm", cost=3, kind="HACK", art="status_parasite", pic="status_parasite", val="1/2", text="The enemy slice under your pointer gets a PARASITE (half output). Exhaust.", rar="Rare"),
]
CW, CH = 230, 306
SHEET = (300, 300, 1290, 800)   # loot sheet box
CARD_X = [475, 795, 1115]
CARD_Y = 535
DECK = (150, 960)

_cache = {}


def base(bg_only=False):
    key = ("base", bg_only)
    if key in _cache:
        return _cache[key].copy()
    img = L.backdrop(BG, blur=3, dim=0.55, sat=0.8)
    img = L.vignette(img, 0.7)
    if bg_only:
        _cache[key] = img
        return img.copy()
    _cache[key] = img
    return img.copy()


def liner(w, h, seed=3, empty=()):
    """Sticker backing liner: off-white silicone paper, faint repeat print, kiss-cut slots."""
    im = Image.new("RGBA", (w, h), (236, 234, 228, 255))
    n = Image.effect_noise((w, h), 10)
    im = SL.over(im, (200, 196, 190), n.point(lambda v: max(0, 128 - v) // 2))
    d = ImageDraw.Draw(im)
    f = L.f_mono(15)
    rng = random.Random(seed)
    for row, y in enumerate(range(-40, h + 40, 46)):
        s = "REBEL_CELL  //  PEEL & SLAP  //  NEVER SLEEP  //  " * 6
        d.text((-(row * 37) % 200 - 200, y), s, font=f, fill=(214, 212, 207, 255))
    d = ImageDraw.Draw(im)
    # header + footer print
    d.rectangle([0, 0, w, 48], fill=(26, 24, 32, 255))
    d.text((22, 24), "LOOT SHEET  //  FIGHT WON  //  PICK 1 OF 3", font=L.f_mono(20), fill=(240, 238, 232, 255), anchor="lm")
    d.text((w - 22, 24), "ROUTER 3/7", font=L.f_mono(18), fill=(255, 214, 64, 255), anchor="rm")
    for i in range(46):
        x = w - 220 + i * 4
        d.rectangle([x, h - 34, x + (1 if rng.random() < 0.6 else 2), h - 12], fill=(40, 38, 46, 255))
    d.text((22, h - 22), "x1 CARD TO DECK   //   UNPICKED STICKERS SHRED ON CONTINUE", font=L.f_mono(15), fill=(110, 106, 118, 255), anchor="lm")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=14, fill=255)
    im.putalpha(m)
    return im


def kiss_cut(img, cx, cy, w, h, empty=False):
    """A kiss-cut slot on the liner (visible once the sticker has gone: a slightly glossier ghost)."""
    d = ImageDraw.Draw(img)
    x0, y0 = cx - w / 2, cy - h / 2
    if empty:
        d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=18, fill=(246, 245, 241, 255))
        sh = SL.diag(int(w), int(h), 30).point(SL.band_lut(0.4, 0.15, 0.4))
        lay = Image.new("RGBA", (int(w), int(h)), (255, 255, 255, 0))
        lay.putalpha(sh)
        img.alpha_composite(lay, (int(x0), int(y0)))
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=18, outline=(160, 156, 164, 255), width=2)


def payout_panel(cyc=18, wallet=142):
    c = L.CRT(430, 236, L.CYAN, "PAYOUT", tag="ROUTER DOWN", seed=2)
    y = 58
    c.paste(L.cycles_mark(30, L.CYCLE), 22, y + 2)
    c.text((64, y), "CYCLES", 22, L.CYCLE)
    c.text((410, y - 6), "+%d" % cyc, 40, L.CYCLE, anchor="ra", fnt=L.f_num(44))
    c.text((64, y + 34), "wallet %d -> %d" % (wallet, wallet + cyc), 17, (120, 170, 190))
    c.rule(y + 66, dash=True)
    y += 80
    c.paste(L.glyph("picto_hp", 26, fill=(255, 110, 140)), 24, y + 2)
    c.text((64, y + 2), "HP", 22, (255, 140, 170))
    c.text((410, y - 2), "41/60", 30, (255, 140, 170), anchor="ra", fnt=L.f_num(34))
    c.paste(L.heat_mark(24, L.HEAT), 24, y + 44)
    c.text((64, y + 46), "HEAT  +0  (router)", 18, (220, 150, 120))
    return c.finish()


def firmware_panel(state="offer"):
    c = L.CRT(500, 500, L.LIME, "FIRMWARE DROP", tag="1 SOCKET", seed=3)
    c.text((28, 56), "socket into one slice of your spinner", 17, (150, 200, 120))
    c.rule(86, dash=True)
    # mini spinner
    wh = L.tile("wheel_a.png")
    r = 150
    wh = wh.resize((2 * r + 44, 2 * r + 44), Image.LANCZOS)
    cx, cy = 320, 296
    c.paste(wh, cx - wh.width // 2, cy - wh.height // 2 + 6)
    d = ImageDraw.Draw(c.im)
    # valid sockets: ATK (top) and CRIT (bottom-left) get a dashed outline + socket pip
    ro, ri = 134, 55
    for a_c, ok in ((-90, True), (150, True)):
        for k in range(0, 60, 6):
            a0 = math.radians(a_c - 30 + k)
            a1 = math.radians(a_c - 30 + k + 3)
            d.line([(cx + ro * math.cos(a0), cy + 6 + ro * math.sin(a0)), (cx + ro * math.cos(a1), cy + 6 + ro * math.sin(a1))], fill=L.LIME + (255,), width=4)
        am = math.radians(a_c)
        sx, sy = cx + (ro + 22) * math.cos(am), cy + 6 + (ro + 22) * math.sin(am)
        d.rounded_rectangle([sx - 13, sy - 9, sx + 13, sy + 9], radius=3, fill=(20, 30, 10, 255), outline=L.LIME + (255,), width=2)
    c.text((28, 470), "VALID: ATK + CRIT", 17, L.LIME)
    c.text((472, 470), "drag chip to a lit slot", 15, (120, 150, 110), anchor="ra")
    return c.finish()


def chip_sticker(curl=None):
    art = L.chip_art("Overvolt", "slice_exploit", (126, 210, 60), w=150, rar="Common")
    return L.sticker_from_art(art, border=7, curl=curl, seed=9)


def deck_panel(n=17):
    c = L.CRT(220, 92, L.PINK, None, header=False, seed=4)
    c.text((18, 12), "DECK", 18, (255, 150, 200))
    c.text((200, 2), str(n), 60, L.PINK, anchor="ra", fnt=L.f_num(66))
    c.text((18, 60), "cards", 15, (170, 100, 140))
    return c.finish()


def card_sd(i, curl=None, gloss_k=0.22):
    key = ("card", i, str(curl), gloss_k)
    if key not in _cache:
        _cache[key] = L.card_sticker(OFFERS[i], CW, CH, curl=curl, gloss_k=gloss_k, seed=5 + i)
    return _cache[key]


def word(key, *a, **k):
    if key not in _cache:
        _cache[key] = L.sticker_word(*a, **k)
    return _cache[key]


# ------------------------------------------------------------------ A: peel from a loot sheet
def static_a(sheet_dy=0, title=1.0):
    img = base()
    # spill + dark pool behind the sheet
    img = L.darken_rect(img, (SHEET[0] - 40, SHEET[1] - 30 + sheet_dy, SHEET[2] + 40, SHEET[3] + 50 + sheet_dy), a=170, r=30, blur=40)
    return img


def compose_a(t_assemble=(1, 1, 1), peel=0.0, lift=0.0, fly=0.0, sheet_dy=0, title_k=1.0, deck_n=None, show_fw=True,
              show_pencil=True, hud=True):
    img = static_a(sheet_dy)
    # top-left title + run strip
    if title_k > 0:
        sd = word("fightwon", ["FIGHT WON"], 92, fills=["yellow"], seed=31)
        img = L.place_sticker(img, sd, 318, 112, angle=-3, scale=title_k)
    if hud:
        strip = L.CRT(760, 42, L.CYAN, None, header=False, seed=6)
        strip.text((16, 10), "LOOT  //  NETRUN: MERIDIAN DEPOT 15  //  ROUTER 3 OF 7", 19, L.CYAN)
        img = L.paste(img, strip.finish(scan=0.15), 76, 196)
        pp = payout_panel()
        img = L.crt_glow_under(img, (1440, 40, 1870, 276), L.CYAN, 0.2)
        img = L.paste(img, pp, 1440, 40)
        dp = deck_panel(deck_n if deck_n is not None else 17)
        img = L.crt_glow_under(img, (DECK[0] - 110, DECK[1] - 46, DECK[0] + 110, DECK[1] + 46), L.PINK, 0.25)
        img = L.paste(img, dp, DECK[0] - 110, DECK[1] - 46)
    # liner sheet
    sw, sh = SHEET[2] - SHEET[0], SHEET[3] - SHEET[1]
    ln = liner(sw, sh)
    for i, x in enumerate(CARD_X):
        kiss_cut(ln, x - SHEET[0], CARD_Y - SHEET[1], CW + 10, CH + 10, empty=(i == 1 and fly > 0))
    img = L.drop_shadow(img, ln, SHEET[0], SHEET[1] + sheet_dy, blur=18, off=(10, 16), op=0.6)
    # SKIP (secondary) on the liner's foot
    if show_fw:
        sk = word("skip", ["SKIP"], 46, fills=[(232, 230, 238)], seed=33, extrude=4)
        img = L.place_sticker(img, sk, 795, 862 + sheet_dy, angle=1.5, scale=1.1)
    # cards
    for i, x in enumerate(CARD_X):
        ta = t_assemble[i]
        if ta <= 0:
            continue
        if i == 1 and fly > 0:
            continue
        if i == 1 and (peel > 0 or lift > 0):
            continue
        sd = card_sd(i)
        if ta < 1:
            img = assemble(img, sd, x, CARD_Y + sheet_dy, ta, seed=40 + i)
        else:
            img = L.place_sticker(img, sd, x, CARD_Y + sheet_dy, angle=[-1.5, 0.5, 1.8][i])
    if (peel > 0 or lift > 0) and fly <= 0:
        sd = card_sd(1, curl=dict(corner="br", amount=0.10 + 0.22 * peel) if peel > 0 else None, gloss_k=0.22 + 0.5 * lift)
        img = L.place_sticker(img, sd, CARD_X[1], CARD_Y - 26 * lift + sheet_dy, angle=0.5 - 3 * lift, scale=1 + 0.08 * lift, hover=lift)
    if fly > 0:
        # flies to the deck along the pencil arrow, shrinking
        p0 = (CARD_X[1], CARD_Y - 26)
        p2 = DECK
        p1 = (520, 760)
        t = fly
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        if t < 0.97:
            sd = card_sd(1, gloss_k=0.6)
            img = L.place_sticker(img, sd, x, y, angle=-3 - 25 * t, scale=1.08 * (1 - 0.75 * t), hover=1 - t * 0.6)
    if show_fw:
        img = L.crt_glow_under(img, (1360, 300, 1860, 800), L.LIME, 0.18)
        img = L.paste(img, firmware_panel(), 1360, 300)
        chip = chip_sticker()
        img = L.place_sticker(img, chip, 1462, 500, angle=-6, scale=0.82)
        cont = word("continue", ["CONTINUE"], 66, fills=["pink"], seed=35)
        img = L.place_sticker(img, cont, 1650, 975, angle=-2)
    if show_pencil and fly <= 0 and lift > 0.5:
        p = L.pen(L.GP_YELLOW, seed=7)
        p.arrow([(700, 700), (560, 820), (380, 920), (270, 950)], width=9, head=28)
        img = L.ink(img, p)
        p2 = L.pen(L.GP_YELLOW, seed=8)
        p2.text("+1 = 18", 470, 905, 34, angle=12)
        img = L.ink(img, p2)
    if show_pencil and show_fw:
        p = L.pen(L.GP_YELLOW, seed=9)
        p.arrow([(1515, 545), (1580, 560), (1640, 500), (1676, 448)], width=7, head=20)
        img = L.ink(img, p)
    return img


def assemble(img, sd, cx, cy, t, seed=1):
    """Card sticker builds up from binary bits (reverse of the locked dissolve A): bits rain in and lock
    into place; the solid part grows from the top."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer = L.place_sticker(layer, sd, cx, cy, shadow=0)
    a = np.asarray(layer.split()[3], np.float32)
    ys, xs = np.nonzero(a > 10)
    if len(ys) == 0:
        return img
    y0, y1 = ys.min(), ys.max()
    rng = np.random.default_rng(seed)
    cols = np.arange(img.size[0])
    jag = (np.sin(cols * 0.11 + seed) * 8 + rng.normal(0, 4, img.size[0]))
    cut = y0 + (y1 - y0 + 20) * t
    yy = np.arange(img.size[1])[:, None]
    solid = (yy < (cut + jag[None, :])).astype(np.float32)
    la = np.asarray(layer, np.float32)
    la[..., 3] *= solid
    if t > 0.98:
        img = L.place_sticker(img, sd, cx, cy)
    else:
        img = Image.alpha_composite(img, Image.fromarray(la.astype(np.uint8), "RGBA"))
    # bits: sampled from the unbuilt part, falling into place
    d = ImageDraw.Draw(img)
    f = L.f_mono(15)
    n = 340
    pick = rng.integers(0, len(ys), n)
    src = np.asarray(layer, np.float32)
    for k in pick:
        py, px = ys[k], xs[k]
        if py < cut + jag[px] - 2:
            continue
        rise = (py - cut) * (0.6 + 0.8 * rng.random())
        y = py - rise * 0.15 - 160 * (1 - t) * rng.random()
        x = px + rng.normal(0, 6) * (1 - t)
        c = src[py, px, :3]
        c = tuple(int(min(255, v * 1.3 + 30)) for v in c)
        d.text((x, y), "01"[int(rng.random() * 2)], font=f, fill=c + (int(255 * (0.5 + 0.5 * rng.random())),), anchor="mm")
    return img


# ------------------------------------------------------------------ B: decompiled from the beaten wheel
def compose_b():
    img = base()
    cx, cy = 960, 800
    img = L.darken_rect(img, (cx - 640, cy - 560, cx + 640, cy + 200), a=150, r=60, blur=60)
    # the beaten wheel's empty spot (enemy defeated v2 leaves an empty ring that says who was beaten)
    d = ImageDraw.Draw(img)
    R = 250
    ring = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ring)
    for k in range(0, 360, 9):
        dr.arc([cx - R, cy - R * 0.42, cx + R, cy + R * 0.42], k, k + 5, fill=(255, 150, 60, 200), width=4)
    dr.ellipse([cx - 70, cy - 30, cx + 70, cy + 30], outline=(255, 150, 60, 160), width=3)
    ring = ring.filter(ImageFilter.GaussianBlur(0.6))
    glow = ring.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, glow)
    img = Image.alpha_composite(img, ring)
    d = ImageDraw.Draw(img)
    d.text((cx, cy + 4), "CARGO HAULER", font=L.f_num(30), fill=(255, 170, 90, 230), anchor="mm")
    d.text((cx, cy + 34), "beaten  //  turn 4", font=L.f_mono(16), fill=(200, 130, 80, 220), anchor="mm")
    # light columns from the wreck to each offer
    pos = [(560, 500, -7), (960, 470, 0), (1360, 500, 7)]
    beams = Image.new("RGBA", img.size, (0, 0, 0, 0))
    db = ImageDraw.Draw(beams)
    for (x, y, a) in pos:
        db.polygon([(cx - 40 + (x - cx) * 0.25, cy), (cx + 40 + (x - cx) * 0.25, cy), (x + 90, y + 120), (x - 90, y + 120)], fill=(92, 225, 255, 34))
    beams = beams.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img, beams)
    ts = [1.0, 1.0, 0.62]
    for i, (x, y, a) in enumerate(pos):
        sd = card_sd(i)
        if ts[i] < 1:
            img = assemble(img, sd, x, y, ts[i], seed=60 + i)
        else:
            img = L.place_sticker(img, sd, x, y, angle=a * 0.4, hover=0.6 if i == 1 else 0.3, scale=1.05 if i == 1 else 1.0)
    # bit streams rising from the ring
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(5)
    f = L.f_mono(14)
    for _ in range(420):
        tx = rng.choice([560, 960, 1360])
        u = rng.random()
        x0 = cx + (tx - cx) * 0.25 + rng.normal(0, 24)
        x = x0 + (tx - x0) * u + rng.normal(0, 10)
        y = cy - (cy - 640) * u + rng.normal(0, 6)
        col = (92, 225, 255) if rng.random() < 0.6 else (255, 61, 168)
        d.text((x, y), "01"[int(rng.random() * 2)], font=f, fill=col + (int(80 + 160 * (1 - u)),), anchor="mm")
    # chip coming out of the wreck, right
    chip = chip_sticker()
    img = L.place_sticker(img, chip, 1640, 600, angle=8, scale=0.9, hover=0.4)
    d = ImageDraw.Draw(img)
    fw = L.CRT(330, 120, L.LIME, "FIRMWARE", seed=11)
    fw.text((18, 54), "OVERVOLT  ATK+CRIT +25%", 17, L.LIME)
    fw.text((18, 82), "drop on a lit slot", 15, (120, 150, 110))
    img = L.paste(img, fw.finish(), 1480, 730)
    # header: system line (CRT) + title sticker
    sd = word("fightwon", ["FIGHT WON"], 92, fills=["yellow"], seed=31)
    img = L.place_sticker(img, sd, 960, 95, angle=-2)
    strip = L.CRT(900, 42, L.CYAN, None, header=False, seed=6)
    strip.text((16, 10), "DECOMPILING ROUTER 3/7 ...  87%   //   PICK 1 CARD", 19, L.CYAN)
    img = L.paste(img, strip.finish(scan=0.15), 510, 178)
    # payout counter as rising numerals
    pp = payout_panel()
    img = L.paste(img, pp, 60, 700)
    sk = word("skip", ["SKIP"], 46, fills=[(232, 230, 238)], seed=33, extrude=4)
    img = L.place_sticker(img, sk, 960, 1000, scale=1.0)
    cont = word("continue", ["CONTINUE"], 66, fills=["pink"], seed=35)
    img = L.place_sticker(img, cont, 1660, 990, angle=-2)
    return img


def label(img, text):
    L.caption(img, text, x=24, y=1066, size=16)
    return img


def make_a():
    img = compose_a(peel=0.6, lift=1.0)
    img = L.bloom(img, 0.25, 0.75, 8)
    L.save(img, "reward_screen.png")


def make_b():
    img = compose_b()
    img = L.bloom(img, 0.25, 0.75, 8)
    L.save(img, "reward_screen_B.png")


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def make_gif():
    frames = []
    durs = []
    N = 50
    for f in range(N):
        if f < 6:
            k = ease(f / 5)
            img = compose_a(t_assemble=(0, 0, 0), sheet_dy=int(700 * (1 - 0)), title_k=0.0, hud=True, show_fw=False, show_pencil=False)
            sd = word("fightwon", ["FIGHT WON"], 92, fills=["yellow"], seed=31)
            sc = 1.5 - 0.5 * k if f < 5 else 1.0
            img = L.place_sticker(img, sd, 318, 112, angle=-3, scale=sc, hover=1 - k)
        elif f < 12:
            k = ease((f - 6) / 5)
            img = compose_a(t_assemble=(0, 0, 0), sheet_dy=int(700 * (1 - k)), show_fw=False, show_pencil=False)
        elif f < 28:
            tt = (f - 12) / 15
            ts = tuple(ease((tt - 0.2 * i) / 0.6) for i in range(3))
            img = compose_a(t_assemble=ts, show_fw=(f >= 24), show_pencil=False)
        elif f < 36:
            k = ease((f - 28) / 7)
            img = compose_a(peel=0.6 * k, lift=k)
        elif f < 40:
            img = compose_a(peel=0.6, lift=1.0)
        else:
            k = ease((f - 40) / 7)
            img = compose_a(peel=0.0, lift=0.0, fly=max(0.01, k), deck_n=18 if k > 0.95 else 17, show_pencil=False)
        img = img.convert("RGB").resize((960, 540), Image.LANCZOS)
        frames.append(img)
        durs.append(70 if f < 40 else 60)
        print("frame", f, flush=True)
    durs[39] = 900
    durs[-1] = 1400
    pal = frames[38].quantize(colors=180, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [fr.quantize(palette=pal, dither=Image.NONE) for fr in frames]
    path = os.path.join(L.OUT, "reward_reveal.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=True, disposal=1)
    print("wrote", path, os.path.getsize(path) / 1e6, "MB")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("a", "all"):
        make_a()
    if what in ("b", "all"):
        make_b()
    if what in ("gif", "all"):
        make_gif()
