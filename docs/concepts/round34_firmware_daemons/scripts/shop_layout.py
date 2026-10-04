"""Round 33 -> shop_v3_layout.png, slice_wheel_compare.png, slice_wheel_offscreen.gif.
The stock wheel is mostly OFFSCREEN (designer's picture): a 12-slice wheel whose centre sits below the
screen, only the top arc shows; the 3 slices at the top are for sale (lit, yellow arc, price tags hanging
from the pegboard), the others are dimmed and padlocked. Removal = the RECYCLE BIN on the sidewalk.

python shop3.py [layout|compare|gif|all]
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
import shop2 as S2
import recycle as RB

BOARD = (520, 92, 1560, 690)
WC = (1010, 1250)
WR = 470
N = 12
OFFER = [11, 0, 1]
NAMES = {11: "PROXY 4 II", 0: "ZERO-DAY 15 II", 1: "SANDBOX 8"}
PRICE = {11: 100, 0: 120, 1: 100}
TAGS = {11: (735, 700), 0: (1010, 690), 1: (1285, 700)}
YEL = (255, 214, 64)
POINTER = True      # round 34 v5: the shop wheel drops its pointer
CENTRE_TH = 9.0     # angle of the centre slice's tag (0 = where the pointer was)

_c = {}


def wheel12():
    if "w" not in _c:
        _c["w"] = L.tile("shop_wheel12.png")
    return _c["w"]


def spun(angle, blur):
    w = wheel12()
    if blur < 1:
        return w.rotate(-angle, Image.BICUBIC) if angle else w
    n = max(3, min(14, int(blur / 3)))
    acc = np.zeros((w.height, w.width, 4), np.float32)
    for j in range(n):
        acc += np.asarray(w.convert("RGBa").rotate(-(angle - blur * j / n), Image.BICUBIC), np.float32)
    return Image.fromarray((acc / n).astype(np.uint8), "RGBa").convert("RGBA")


def wedge(size, c, r0, r1, idx, n=N):
    span = 360 / n
    a0 = -90 + idx * span - span / 2
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.pieslice([c[0] - r1, c[1] - r1, c[0] + r1, c[1] + r1], a0, a0 + span, fill=255)
    return m


def lock_icon(px=46):
    g = L.glyph("state_locked", px, fill=(230, 230, 240), ow=3)
    return g


def wheel_section(img, angle=0.0, blur=0.0, reveal=1.0):
    d = ImageDraw.Draw(img)
    R = WR + 30
    # the wheel housing: a counter-top arc the wheel rises out of
    d.ellipse([WC[0] - R, WC[1] - R, WC[0] + R, WC[1] + R], fill=(12, 10, 16, 255), outline=(110, 100, 130, 255), width=4)
    w = spun(angle, blur)
    img.alpha_composite(w, (WC[0] - w.width // 2, WC[1] - w.height // 2))
    d = ImageDraw.Draw(img)
    for k in range(60):
        a = math.radians(-90 + k * 6)
        r0, r1 = R - 4, R - (16 if k % 5 == 0 else 9)
        d.line([(WC[0] + r0 * math.cos(a), WC[1] + r0 * math.sin(a)), (WC[0] + r1 * math.cos(a), WC[1] + r1 * math.sin(a))], fill=(200, 190, 220, 255), width=2)
    px, py = WC[0], WC[1] - R - 4
    if POINTER:
        d.polygon([(px - 20, py - 24), (px + 20, py - 24), (px, py + 18)], fill=YEL + (255,), outline=L.INK + (255,))
    if reveal > 0:
        dim = Image.new("L", img.size, 0)
        for i in range(N):
            if i not in OFFER:
                dim = ImageChops.lighter(dim, wedge(img.size, WC, 0, WR + 4, i))
        g = img.convert("L").convert("RGBA")
        g = Image.blend(g, Image.new("RGBA", img.size, (8, 6, 12, 255)), 0.6)
        img = Image.composite(g, img, dim.point(lambda v: int(v * reveal)))
        d = ImageDraw.Draw(img)
        span = 360 / N
        # padlocks on every visible locked wedge
        for i in range(N):
            if i in OFFER:
                continue
            a = math.radians(-90 + i * span)
            lx, ly = WC[0] + (WR - 70) * math.cos(a), WC[1] + (WR - 70) * math.sin(a)
            if ly < L.H - 20:
                lk = lock_icon(44)
                lk.putalpha(lk.split()[3].point(lambda v: int(v * reveal)))
                img.alpha_composite(lk, (int(lx - lk.width / 2), int(ly - lk.height / 2)))
        d = ImageDraw.Draw(img)
        for i in OFFER:
            a0 = -90 + i * span - span / 2
            if i == 11:
                a0 -= 360
            d.arc([WC[0] - WR - 4, WC[1] - WR - 4, WC[0] + WR + 4, WC[1] + WR + 4], a0 + 0.6, a0 + span - 0.6, fill=YEL + (int(255 * reveal),), width=7)
            # side edges of the lit wedge
            for aa in (a0 + 0.6, a0 + span - 0.6):
                ra = math.radians(aa)
                d.line([(WC[0] + 150 * math.cos(ra), WC[1] + 150 * math.sin(ra)), (WC[0] + (WR + 4) * math.cos(ra), WC[1] + (WR + 4) * math.sin(ra))], fill=YEL + (int(200 * reveal),), width=4)
    if reveal > 0.5:
        k = min(1.0, (reveal - 0.5) * 2)
        for n, i in enumerate(OFFER):
            # round 34 v4: each tag is tied to its own slice, just outside the rim at the slice's angle
            # (the centre one sits a few degrees right so the pointer stays clear)
            th = [-30.0, CENTRE_TH, 30.0][n]
            ra = math.radians(th - 90)
            rt = R + 34
            tx, ty = WC[0] + rt * math.cos(ra), WC[1] + rt * math.sin(ra)
            drop = (1 - k) * 50
            ty -= drop
            sa = math.radians([-30.0, min(4.0, CENTRE_TH), 30.0][n] - 90)
            ax, ay = WC[0] + (WR + 6) * math.cos(sa), WC[1] + (WR + 6) * math.sin(sa)
            d = ImageDraw.Draw(img)
            d.line([(ax, ay), (tx, ty + 12)], fill=(230, 220, 200, 255), width=2)
            d.ellipse([ax - 5, ay - 5, ax + 5, ay + 5], fill=(170, 170, 180, 255), outline=L.INK + (255,), width=2)
            t = L.price_tag(PRICE[i], seed=300 + n)
            t = L.rotate_rgba(t, -th * 0.8)
            img = L.drop_shadow(img, t, tx - t.width / 2, ty - t.height / 2, blur=4, off=(2, 3), op=0.5)
            d = ImageDraw.Draw(img)
            rn = rt + 52
            nx, ny = WC[0] + rn * math.cos(ra), WC[1] + rn * math.sin(ra) - drop
            if n == 1:
                nx, ny = tx + t.width / 2 + 70, ty + 4
            d.text((nx, ny), NAMES[i], font=L.f_mono(15), fill=(240, 240, 248, 255), anchor="mm", stroke_width=3, stroke_fill=(8, 6, 12, 255))
    return img


def layout_base():
    if "base" in _c:
        return _c["base"].copy()
    img = S2.facade()
    bw, bh = BOARD[2] - BOARD[0], BOARD[3] - BOARD[1]
    img = L.drop_shadow(img, S1.pegboard(bw, bh), BOARD[0], BOARD[1], blur=24, off=(16, 24), op=0.7)
    for txt, x, y, a in (("CARDS", 560, 118, -1.5), ("FIRMWARE", 1190, 118, 1.2), ("DAEMONS", 1190, 500, -1.0)):
        img = L.drop_shadow(img, L.rotate_rgba(S1.dymo(txt), a), x, y, blur=3, off=(2, 3), op=0.6)
    cards = [
        dict(name="Bulwark", cost=2, kind="SYSTEM", art="slice_firewall", pic="slice_firewall", val="12", text="Gain 12 block.", rar="Uncommon"),
        dict(name="Data Surge", cost=2, kind="SYSTEM", art="picto_draw", pic="picto_draw", val="3", text="Draw 3 cards.", rar="Uncommon"),
        dict(name="Feather Touch", cost=0, kind="WHEEL", art="picto_nudge", pic="picto_nudge", val="1", text="One +-1 nudge.", rar="Common"),
    ]
    prices = [55, 60, 50]
    for i, c in enumerate(cards):
        x, y = 640 + i * 215, 320
        img = S1.hook(img, x, y - 150)
        hov = i == 1
        sd = L.card_sticker(c, 180, 240, gloss_k=0.6 if hov else 0.22, seed=20 + i)
        if i == 2:
            sd = L.greyscale(sd, 0.6)
        img = L.place_sticker(img, sd, x, y - (12 if hov else 0), angle=[-2, 0, 2.5][i], scale=1.06 if hov else 1.0, hover=0.8 if hov else 0.0)
        img = S1.tag_on(img, prices[i], x + 40, y + 152, sold=(i == 2), seed=30 + i, angle=-4 + 4 * i)
    buy = L.sticker_word(["BUY 60"], 40, fills=["pink"], seed=41)
    img = L.place_sticker(img, buy, 860, 560, angle=-3)
    # round 34: FIRMWARE + DAEMONS rows are drawn by shop_v3.py
    # the recycle bin on the sidewalk, right of the shop window
    RB.set_scale(0.8)
    size = img.size
    bin_l = RB.scene(size, (1740, 830), 0.0, inside=[], badge=0)
    RB.set_scale(1.0)
    img.alpha_composite(bin_l)
    img = L.drop_shadow(img, L.rotate_rgba(S1.dymo("RECYCLE BIN"), 2), 1630, 560, blur=3, off=(2, 3), op=0.6)
    img = S1.tag_on(img, 50, 1850, 640, seed=111, angle=5)
    # clerk (round 32 position, under the sign)
    cp = S2.clerk_panel()
    img = L.crt_glow_under(img, (60, 728, 480, 1058), L.CYAN, 0.22)
    img = L.paste(img, cp, 60, 728)
    p = L.pen(L.GP_YELLOW, seed=81)
    p.text("ask about the", 372, 884, 21, angle=-5)
    p.text("back room", 380, 912, 24, angle=-5)
    p.text("BUY", 1000, 540, 38, angle=-10)
    p.arrow([(975, 555), (945, 562), (925, 564)], width=7, head=16)
    p.text("bin it", 1610, 700, 32, angle=-8)
    p.arrow([(1600, 725), (1620, 760), (1640, 775)], width=7, head=16)
    img = L.ink(img, p)
    _c["base"] = img
    return img.copy()


def compose(angle=0.0, blur=0.0, reveal=1.0):
    img = layout_base()
    img = wheel_section(img, angle, blur, reveal)
    img = S2.place_leave(img)
    if reveal >= 1:
        pr = L.pen(L.GP_YELLOW, seed=83)
        pr.text("top 3 only", 600, 765, 30, angle=-6)
        pr.arrow([(630, 795), (655, 830), (668, 845)], width=6, head=14)
        img = L.ink(img, pr)
    return img


def make_layout():
    img = compose()
    img = L.bloom(img, 0.2, 0.8, 8)
    L.save(img, "shop_v3_layout.png")


def make_compare():
    left = S2.compose()
    # round 32 wheel, made more obvious: padlocks on the 5 slices that aren't for sale
    span = 360 / S2.N
    for i in range(S2.N):
        if i in S2.OFFER:
            continue
        a = math.radians(-90 + i * span)
        lx, ly = S2.WC[0] + (S2.WR - 44) * math.cos(a), S2.WC[1] + (S2.WR - 44) * math.sin(a)
        lk = lock_icon(34)
        left.alpha_composite(lk, (int(lx - lk.width / 2), int(ly - lk.height / 2)))
    left = left.crop((520, 470, 1440, 988))
    right = compose().crop((440, 560, 1560, 1080))
    canvas = Image.new("RGBA", (L.W, L.H), (11, 10, 16, 255))
    sd = L.sticker_word(["SLICE WHEEL: FULL vs OFFSCREEN"], 52, fills=["yellow"], seed=5)
    canvas = L.place_sticker(canvas, sd, 520, 64, angle=-1.5)
    lw = 900
    l2 = left.resize((lw, int(left.height * lw / left.width)), Image.LANCZOS)
    r2 = right.resize((lw, int(right.height * lw / right.width)), Image.LANCZOS)
    canvas = L.drop_shadow(canvas, l2, 40, 150, blur=12)
    canvas = L.drop_shadow(canvas, r2, 980, 150, blur=12)
    d = ImageDraw.Draw(canvas)
    d.text((40, 680), "A  round 32: the whole wheel on the board (+ padlocks)", font=L.f_num(28), fill=(220, 220, 230, 255))
    d.text((980, 680), "B  designer's version: wheel mostly offscreen, top arc only", font=L.f_num(28), fill=(255, 214, 64, 255))
    notes_a = ["+ you see the whole stock and what you missed", "- small: slices read at ~60 px, tags crowd the wheel",
               "- 8 slices: the 3 for sale are 135 deg of a small dial"]
    notes_b = ["+ big, readable slices; the 3 for sale ARE the visible arc", "+ locked ones peek in at the edges, padlocked",
               "+ reads like a slot reel / roulette rising out of the counter", "- you don't see the rest of the stock (fine: it isn't for sale)"]
    for k, t in enumerate(notes_a):
        d.text((40, 730 + k * 32), t, font=L.f_mono(19), fill=(170, 170, 185, 255))
    for k, t in enumerate(notes_b):
        d.text((980, 730 + k * 32), t, font=L.f_mono(19), fill=(220, 220, 200, 255))
    d.text((980, 880), "RECOMMENDED: B (it looks better, and sale/no-sale is unmissable)", font=L.f_mono(20), fill=(255, 214, 64, 255))
    d.text((40, 1010), "both: for sale = lit + yellow arc + hanging price tag;  not for sale = greyed, dark, padlocked, not clickable", font=L.f_mono(18), fill=(150, 200, 220, 255))
    L.save(canvas, "slice_wheel_compare.png")


def ease_out(t):
    return 1 - (1 - t) ** 3


def make_gif():
    frames, durs = [], []
    total = 360 + 5 * 30
    NS = 30
    box = (440, 560, 1560, 1080)
    prev = total
    for f in range(NS + 1):
        t = f / NS
        ang = total * (1 - ease_out(t))
        blur = min(36.0, abs(prev - ang) * 0.9)
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
    w_, h_ = frames[0].size
    mont = Image.new("RGB", (w_, h_ * 3))
    for k, fi in enumerate((5, NS, len(frames) - 1)):
        mont.paste(frames[fi], (0, h_ * k))
    pal = mont.quantize(colors=220, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [fr.resize((w_ * 3 // 4, h_ * 3 // 4), Image.LANCZOS).quantize(palette=pal, dither=Image.NONE) for fr in frames]
    path = os.path.join(L.OUT, "slice_wheel_offscreen.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=True, disposal=1)
    print("wrote", path, os.path.getsize(path) / 1e6, "MB")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("layout", "all"):
        make_layout()
    if what in ("compare", "all"):
        make_compare()
    if what in ("gif", "all"):
        make_gif()
