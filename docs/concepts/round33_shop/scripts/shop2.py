"""Round 32 -> shop_v2.png and shop_slice_wheel.gif: the shop renamed MAINFRAME (placeholder blue neon
sign until round32_mainframe_sign lands), the clerk screen moved under the sign, a grease-pencil note on
the clerk instead of the MODEM sticker, SLICES sold from a wheel that spins on entry (top 3 for sale),
PURGE (the rm -rf key) for removal, Microchips / Daemons left as labelled placeholders, and a louder
LEAVE sticker.

python shop2.py [still|gif|all]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import r31lib as L
import sticker_lib19 as SL
import shop as S1
import removal as RM

BG = os.path.join(L.CONCEPTS, "round27_modem_sign_flicker", "market_normal.png")
BOARD = (520, 92, 1890, 950)
WALLET = 160
WC = (720, 790)      # slice wheel centre
WR = 130             # slice outer radius on screen
N = 8
OFFER = [7, 0, 1]    # indices under / beside the pointer once it stops (0 = at the pointer)
NAMES = ["ZERO-DAY 15 II", "SANDBOX 8", "EXPLOIT 10 III", "PATCH 4 II", "TROJAN 1", "FIREWALL 7 II", "VIRUS 3", "PROXY 5 II"]
PRICE = {7: 100, 0: 120, 1: 100}
BLUE = (70, 150, 255)

_cache = {}


# ------------------------------------------------------------------ facade with the placeholder MAINFRAME sign
def facade():
    if "facade" in _cache:
        return _cache["facade"].copy()
    im = Image.open(BG).convert("RGB")
    a = np.asarray(im, np.float32) / 255
    mx, mn = a.max(2), a.min(2)
    d = np.maximum(mx - mn, 1e-6)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    # the pink sign spill becomes blue (the sign's new colour); only the left facade
    xx = np.arange(a.shape[1])[None, :]
    region = np.clip((760 - xx) / 200.0, 0, 1)
    pinkish = ((hue > 280) | (hue < 10)) & (sat > 0.3)
    k = (pinkish * region)[..., None]
    blue = np.stack([0.22 * mx, 0.52 * mx, mx], -1)
    a = a * (1 - k) + blue * k
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    # plate: blank the old letters, draw MAINFRAME as blue tubes
    dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([60, 36, 204, 680], radius=14, fill=(10, 12, 24, 255))
    tube = Image.new("L", im.size, 0)
    f = L.font(L.BAHN, 66, b"SemiBold Condensed")
    for i, ch in enumerate("MAINFRAME"):
        y = 76 + i * 66
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).text((132, y), ch, font=f, fill=255, anchor="mm")
        edge = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(5)), m.filter(ImageFilter.MinFilter(3)))
        tube = ImageChops.lighter(tube, edge)
    glow = tube.filter(ImageFilter.GaussianBlur(10))
    im = SL.over(im, BLUE, glow.point(lambda v: min(255, v * 2)))
    im = SL.over(im, (190, 225, 255), tube)
    dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([56, 32, 208, 684], radius=16, outline=BLUE + (255,), width=3)
    dd.rectangle([62, 690, 202, 712], fill=(10, 10, 16, 220))
    dd.text((132, 701), "PLACEHOLDER SIGN", font=L.f_mono(13), fill=(150, 190, 255, 255), anchor="mm")
    im = im.convert("RGB")
    from PIL import ImageEnhance
    im = ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(1.5))).enhance(0.66).convert("RGBA")
    im = L.vignette(im, 0.5)
    _cache["facade"] = im
    return im.copy()


# ------------------------------------------------------------------ slice wheel
def wheel_img():
    if "wheel" not in _cache:
        w = L.tile("shop_wheel.png")
        k = WR / 300.0
        _cache["wheel"] = w.resize((int(w.width * k), int(w.height * k)), Image.LANCZOS)
    return _cache["wheel"]


def spun(angle, blur_deg=0.0):
    w = wheel_img()
    if blur_deg < 1:
        return w.rotate(-angle, Image.BICUBIC) if angle else w
    n = max(3, int(blur_deg / 3))
    acc = np.zeros((w.height, w.width, 4), np.float32)
    for j in range(n):
        a = angle - blur_deg * j / n
        acc += np.asarray(w.convert("RGBa").rotate(-a, Image.BICUBIC), np.float32)
    acc /= n
    return Image.fromarray(acc.astype(np.uint8), "RGBa").convert("RGBA")


def wedge_mask(size, c, r, idx, grow=6):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    span = 360 / N
    a0 = -90 + idx * span - span / 2
    d.pieslice([c[0] - r - grow, c[1] - r - grow, c[0] + r + grow, c[1] + r + grow], a0, a0 + span, fill=255)
    return m


def slice_section(img, angle=0.0, blur=0.0, reveal=1.0, show_tags=True):
    d = ImageDraw.Draw(img)
    # mount: a dark disc cut into the pegboard + bezel
    R = WR + 26
    d.ellipse([WC[0] - R, WC[1] - R, WC[0] + R, WC[1] + R], fill=(10, 8, 14, 255), outline=(90, 80, 104, 255), width=3)
    w = spun(angle, blur)
    img.alpha_composite(w, (WC[0] - w.width // 2, WC[1] - w.height // 2))
    d = ImageDraw.Draw(img)
    for k in range(30):
        a = math.radians(-90 + k * 12)
        r0, r1 = R - 4, R - (14 if k % 5 == 0 else 9)
        d.line([(WC[0] + r0 * math.cos(a), WC[1] + r0 * math.sin(a)), (WC[0] + r1 * math.cos(a), WC[1] + r1 * math.sin(a))], fill=(200, 190, 220, 255), width=2)
    d.ellipse([WC[0] - 50, WC[1] - 50, WC[0] + 50, WC[1] + 50], fill=(16, 12, 22, 255), outline=BLUE + (255,), width=3)
    d.text((WC[0], WC[1] - 8), "STOCK", font=L.f_num(24), fill=(255, 255, 255, 255), anchor="mm")
    d.text((WC[0], WC[1] + 16), "spun on entry", font=L.f_mono(11), fill=(150, 190, 255, 255), anchor="mm")
    # pointer at the top
    px, py = WC[0], WC[1] - R - 6
    d.polygon([(px - 18, py - 26), (px + 18, py - 26), (px, py + 14)], fill=(255, 214, 64, 255), outline=L.INK + (255,))
    if reveal > 0:
        # everything that isn't for sale goes dark + grey
        dim = Image.new("L", img.size, 0)
        for i in range(N):
            if i not in OFFER:
                dim = ImageChops.lighter(dim, wedge_mask(img.size, WC, WR, i, grow=2))
        sub = img.crop((0, 0) + img.size)
        g = sub.convert("L").convert("RGBA")
        g = Image.blend(g, Image.new("RGBA", img.size, (8, 6, 12, 255)), 0.55)
        img = Image.composite(g, img, dim.point(lambda v: int(v * reveal)))
        # offered wedges get a pencil-yellow lit outline from the shop's lights
        d = ImageDraw.Draw(img)
        span = 360 / N
        for i in OFFER:
            a0 = -90 + i * span - span / 2
            if i == 7:
                a0 -= 360
            d.arc([WC[0] - WR - 3, WC[1] - WR - 3, WC[0] + WR + 3, WC[1] + WR + 3], a0 + 1, a0 + span - 1, fill=(255, 214, 64, int(255 * reveal)), width=5)
    if show_tags and reveal > 0.5:
        for n, i in enumerate(OFFER):
            ang = math.radians(-90 + (i if i != 7 else -1) * 360 / N)
            tx, ty = WC[0] + (WR + 88) * math.cos(ang), WC[1] + (WR + 70) * math.sin(ang)
            drop = (1 - min(1.0, (reveal - 0.5) * 2)) * 40
            img = S1.tag_on(img, PRICE[i], tx + 30, ty - drop, seed=200 + n, angle=[-8, 0, 8][n])
            d = ImageDraw.Draw(img)
            d.text((tx + 30, ty - drop + 34), NAMES[i], font=L.f_mono(13), fill=(230, 230, 240, 255), anchor="mm", stroke_width=3, stroke_fill=(8, 6, 12, 255))
    return img


# ------------------------------------------------------------------ placeholders
def placeholder(img, box, title, note):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    for x in range(x0, x1, 18):
        d.line([(x, y0), (min(x + 9, x1), y0)], fill=(150, 140, 170, 255), width=2)
        d.line([(x, y1), (min(x + 9, x1), y1)], fill=(150, 140, 170, 255), width=2)
    for y in range(y0, y1, 18):
        d.line([(x0, y), (x0, min(y + 9, y1))], fill=(150, 140, 170, 255), width=2)
        d.line([(x1, y), (x1, min(y + 9, y1))], fill=(150, 140, 170, 255), width=2)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=(10, 8, 14, 130))
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    d.text(((x0 + x1) / 2, (y0 + y1) / 2 - 14), title, font=L.f_num(30), fill=(200, 195, 215, 255), anchor="mm")
    d.text(((x0 + x1) / 2, (y0 + y1) / 2 + 18), note, font=L.f_mono(15), fill=(150, 145, 165, 255), anchor="mm")
    return img


# ------------------------------------------------------------------ clerk + leave
def clerk_panel():
    c = L.CRT(420, 330, L.CYAN, "MAINFRAME // CLERK", tag="SHOP", seed=71)
    px = 18
    face = [(1, 0), (2, 0), (5, 0), (6, 0), (1, 1), (2, 1), (5, 1), (6, 1),
            (0, 4), (7, 4), (1, 5), (6, 5), (2, 6), (3, 6), (4, 6), (5, 6)]
    ox, oy = 34, 60
    for (gx, gy) in face:
        c.d.rectangle([ox + gx * px, oy + gy * px, ox + gx * px + px - 3, oy + gy * px + px - 3], fill=L.CYAN + (255,))
    c.text((206, 62), "NO REFUNDS.", 21, (200, 245, 255))
    c.text((206, 92), "NO NAMES.", 21, (200, 245, 255))
    c.text((206, 122), "CYCLES ONLY.", 21, (200, 245, 255))
    c.rule(200, dash=True)
    c.paste(L.cycles_mark(34, L.CYCLE), 24, 220)
    c.text((72, 224), "WALLET", 22, L.CYCLE)
    c.text((396, 206), str(WALLET), 52, L.CYCLE, anchor="ra", fnt=L.f_num(56))
    c.text((24, 286), "card 50-75   slice 100 (MISS 150)   bin 50+", 14, (110, 170, 190))
    return c.finish()


def leave_sticker():
    if "leave" not in _cache:
        art = SL.lettering(["LEAVE"], 92, ["holo"], key_w=6, extrude=8, seed=91, jitter=4.0, pad=24, holo_seed=5)
        _cache["leave"] = SL.build_sticker(art, border=12, holo_border=False, gloss_k=0.35, seed=91)
        arr = Image.new("RGBA", (220, 120), (0, 0, 0, 0))
        d = ImageDraw.Draw(arr)
        for k in range(3):
            x = 20 + k * 60
            d.polygon([(x, 14), (x + 40, 14), (x + 86, 60), (x + 40, 106), (x, 106), (x + 46, 60)], fill=(255, 61, 168, 255), outline=L.INK + (255,))
        _cache["arrow"] = L.sticker_from_art(arr, border=8, seed=92)
        _cache["tag"] = L.sticker_word(["THE MAINFRAME"], 26, fills=["pink"], seed=93, extrude=3, border=7)
    return _cache["leave"], _cache["arrow"], _cache["tag"]


def place_leave(img, wiggle=0.0):
    lv, ar, tg = leave_sticker()
    img = L.place_sticker(img, ar, 1790 + wiggle * 8, 985, angle=-4, scale=0.7)
    img = L.place_sticker(img, lv, 1580, 985, angle=-5, scale=0.85)
    img = L.place_sticker(img, tg, 1610, 1045, angle=3, scale=0.95)
    return img


# ------------------------------------------------------------------ the whole shop
def shop_base():
    """Everything except the slice section (cached for the GIF)."""
    if "base" in _cache:
        return _cache["base"].copy()
    img = facade()
    bw, bh = BOARD[2] - BOARD[0], BOARD[3] - BOARD[1]
    img = L.drop_shadow(img, S1.pegboard(bw, bh), BOARD[0], BOARD[1], blur=24, off=(16, 24), op=0.7)
    for txt, x, y, a in (("CARDS", 560, 118, -1.5), ("MICROCHIPS", 1300, 118, 1.2), ("SLICES", 560, 560, 0.8), ("DAEMONS", 1140, 560, -1.0), ("PURGE A CARD", 1520, 560, 1.4)):
        img = L.drop_shadow(img, L.rotate_rgba(S1.dymo(txt), a), x, y, blur=3, off=(2, 3), op=0.6)
    cards = [
        dict(name="Bulwark", cost=2, kind="SYSTEM", art="slice_firewall", pic="slice_firewall", val="12", text="Gain 12 block.", rar="Uncommon"),
        dict(name="Data Surge", cost=2, kind="SYSTEM", art="picto_draw", pic="picto_draw", val="3", text="Draw 3 cards.", rar="Uncommon"),
        dict(name="Feather Touch", cost=0, kind="WHEEL", art="picto_nudge", pic="picto_nudge", val="1", text="One +-1 nudge.", rar="Common"),
    ]
    prices = [55, 60, 50]
    for i, c in enumerate(cards):
        x, y = 680 + i * 220, 330
        img = S1.hook(img, x, y - 150)
        hov = i == 1
        sd = L.card_sticker(c, 190, 253, gloss_k=0.6 if hov else 0.22, seed=20 + i)
        if i == 2:
            sd = L.greyscale(sd, 0.6)
        img = L.place_sticker(img, sd, x, y - (14 if hov else 0), angle=[-2, 0, 2.5][i], scale=1.06 if hov else 1.0, hover=0.8 if hov else 0.0)
        img = S1.tag_on(img, prices[i], x + 40, y + 160, sold=(i == 2), seed=30 + i, angle=-4 + 4 * i)
    buy = L.sticker_word(["BUY 60"], 44, fills=["pink"], seed=41)
    img = L.place_sticker(img, buy, 920, 545, angle=-3)
    img = placeholder(img, (1290, 170, 1860, 500), "MICROCHIPS", "placeholder: own design pass")
    img = placeholder(img, (1140, 610, 1490, 920), "DAEMONS", "placeholder: own design pass")
    # PURGE: the rm -rf key (recommended removal, see removal_options.png)
    key = RM.keycap(230)
    img = L.drop_shadow(img, key, 1570, 640, blur=10, off=(6, 10), op=0.6)
    img = S1.tag_on(img, 50, 1800, 885, seed=110, angle=4)
    d = ImageDraw.Draw(img)
    d.text((1685, 905), "drop a card on the key", font=L.f_mono(14), fill=(220, 210, 230, 255), anchor="mm", stroke_width=3, stroke_fill=(8, 6, 12, 255))
    # clerk, moved down under the sign
    cp = clerk_panel()
    img = L.crt_glow_under(img, (60, 728, 480, 1058), L.CYAN, 0.22)
    img = L.paste(img, cp, 60, 728)
    p = L.pen(L.GP_YELLOW, seed=81)
    p.text("ask about the", 372, 884, 21, angle=-5)
    p.text("back room", 380, 912, 24, angle=-5)
    p.text("BUY", 1065, 520, 40, angle=-10)
    p.arrow([(1040, 535), (1005, 545), (985, 548)], width=7, head=16)
    img = L.ink(img, p)
    strip = L.CRT(620, 42, BLUE, None, header=False, seed=72)
    strip.text((16, 10), "05 MAINFRAME  //  LAYER 3 OF 7", 19, (150, 190, 255))
    img = L.paste(img, strip.finish(scan=0.15), 540, 990)
    _cache["base"] = img
    return img.copy()


def compose(angle=0.0, blur=0.0, reveal=1.0, wiggle=0.0):
    img = shop_base()
    img = slice_section(img, angle, blur, reveal)
    img = place_leave(img, wiggle)
    if reveal >= 1:
        pr = L.pen(L.GP_YELLOW, seed=83)
        pr.text("top 3 only", 1005, 900, 28, angle=-8)
        img = L.ink(img, pr)
    return img


def make_still():
    img = compose()
    img = L.bloom(img, 0.2, 0.8, 8)
    L.save(img, "shop_v2.png")


def ease_out(t):
    return 1 - (1 - t) ** 3


def make_gif():
    frames, durs = [], []
    total = 2 * 360 + 3 * 45       # ends exactly on angle 0 (ZERO-DAY at the pointer)
    NS = 30
    box = (520, 470, 1440, 988)    # crop for the GIF: the slice section + its neighbours
    prev = total
    for f in range(NS + 1):
        t = f / NS
        ang = total * (1 - ease_out(t))
        blur = min(40.0, abs(prev - ang) * 0.9)
        prev = ang
        img = compose(angle=ang if f < NS else 0.0, blur=blur if f < NS else 0.0, reveal=0.0)
        frames.append(img.crop(box).convert("RGB"))
        durs.append(50)
        print("spin", f, flush=True)
    for f in range(10):
        img = compose(reveal=(f + 1) / 10)
        frames.append(img.crop(box).convert("RGB"))
        durs.append(60)
    durs[NS] = 350
    durs[-1] = 1800
    pal = frames[-1].quantize(colors=200, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [fr.quantize(palette=pal, dither=Image.NONE) for fr in frames]
    path = os.path.join(L.OUT, "shop_slice_wheel.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=True, disposal=1)
    print("wrote", path, os.path.getsize(path) / 1e6, "MB")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("still", "all"):
        make_still()
    if what in ("gif", "all"):
        make_gif()
