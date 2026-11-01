"""Round 31 -> shop_interior.png: the Modem shop UI over the MARKET NEON facade (round 27, F1b night).
A pegboard wall in the shop window holds the stock as stickers on hooks with kraft price tags; sections
are label-maker tape; the shopkeeper is the facade's pixel smiley on a CRT (the Cell's wallet sits there);
BUY / SHRED notes are grease pencil; LEAVE THE MODEM is the big action sticker.

python shop.py
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import r31lib as L
import sticker_lib19 as SL

BG = os.path.join(L.CONCEPTS, "round27_modem_sign_flicker", "market_normal.png")
BOARD = (520, 92, 1890, 950)
WALLET = 160


def pegboard(w, h):
    rng = np.random.default_rng(3)
    a = np.zeros((h, w, 3), np.float32)
    a[:] = (38, 30, 44)
    n = rng.normal(0, 3, (h, w, 1))
    a += n
    # neon spill from the sign on the left (pink) and the street (cyan) at the bottom right
    xx = np.arange(w)[None, :]
    yy = np.arange(h)[:, None]
    pink = np.exp(-((xx + 200) / 700.0) ** 2) * 60
    cyan = np.exp(-(((xx - w) / 600.0) ** 2 + ((yy - h) / 400.0) ** 2)) * 30
    a[..., 0] += pink
    a[..., 2] += pink * 0.7 + cyan
    a[..., 1] += cyan * 0.8
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    for y in range(24, h, 32):
        for x in range(24, w, 32):
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(12, 10, 16, 255))
            d.arc([x - 4, y - 4, x + 4, y + 4], 200, 340, fill=(70, 60, 80, 255))
    d.rectangle([0, 0, w - 1, h - 1], outline=(14, 12, 18, 255), width=10)
    d.rectangle([10, 10, w - 11, h - 11], outline=(70, 60, 82, 255), width=2)
    return im


def dymo(text, size=26):
    f = L.font(L.ANTON, size)
    tw = int(f.getlength(text))
    w, h = tw + 36, int(size * 1.5)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=3, fill=(18, 18, 22, 255))
    d.rectangle([0, 3, w - 1, 5], fill=(40, 40, 46, 255))
    d.text((w / 2 + 1, h / 2 + 2), text, font=f, fill=(0, 0, 0, 255), anchor="mm")
    d.text((w / 2, h / 2), text, font=f, fill=(236, 236, 240, 255), anchor="mm")
    return im


def hook(img, x, y):
    d = ImageDraw.Draw(img)
    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(150, 150, 160, 255), outline=(30, 30, 36, 255), width=2)
    d.line([(x, y), (x, y + 22)], fill=(170, 170, 180, 255), width=4)
    return img


def tag_on(img, price, x, y, sold=False, afford=True, seed=1, angle=0):
    t = L.price_tag(price, sold=sold, afford=afford, seed=seed)
    t = L.rotate_rgba(t, angle)
    d = ImageDraw.Draw(img)
    d.line([(x - 40, y - 34), (x - t.width / 2 + 10, y)], fill=(230, 220, 200, 255), width=2)
    return L.drop_shadow(img, t, x - t.width / 2, y - t.height / 2, blur=4, off=(2, 3), op=0.5)


def clerk_panel():
    c = L.CRT(420, 380, L.CYAN, "MODEM // CLERK", tag="CYBER SHOP", seed=71)
    # the facade's pixel smiley, now talking
    px = 22
    face = [(1, 0), (2, 0), (5, 0), (6, 0), (1, 1), (2, 1), (5, 1), (6, 1),
            (0, 4), (7, 4), (1, 5), (6, 5), (2, 6), (3, 6), (4, 6), (5, 6)]
    ox, oy = 40, 64
    for (gx, gy) in face:
        c.d.rectangle([ox + gx * px, oy + gy * px, ox + gx * px + px - 3, oy + gy * px + px - 3], fill=L.CYAN + (255,))
    c.text((236, 66), "NO REFUNDS.", 22, (200, 245, 255))
    c.text((236, 98), "NO NAMES.", 22, (200, 245, 255))
    c.text((236, 130), "CYCLES ONLY.", 22, (200, 245, 255))
    c.rule(232, dash=True)
    c.paste(L.cycles_mark(36, L.CYCLE), 26, 252)
    c.text((76, 256), "WALLET", 22, L.CYCLE)
    c.text((396, 240), str(WALLET), 52, L.CYCLE, anchor="ra", fnt=L.f_num(56))
    c.text((26, 312), "card 50-75  chip 75-150  daemon 150-250", 14, (110, 170, 190))
    c.text((26, 336), "slice overwrite 100 (MISS 150)  shred 50+", 14, (110, 170, 190))
    return c.finish()


def shredder():
    w, h = 250, 250
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 60, w - 20, h - 10], radius=14, fill=(52, 48, 58, 255), outline=L.INK + (255,), width=4)
    d.rounded_rectangle([40, 40, w - 40, 84], radius=8, fill=(26, 24, 30, 255), outline=L.INK + (255,), width=4)
    d.rectangle([56, 58, w - 56, 66], fill=(4, 4, 6, 255))
    # card going in, shredded strips below
    d.polygon([(80, 0), (170, 10), (165, 60), (78, 56)], fill=(255, 196, 40, 255), outline=L.INK + (255,))
    for i in range(9):
        x = 70 + i * 13
        d.rectangle([x, 150, x + 8, 150 + 30 + (i * 7) % 26], fill=(255, 196, 40, 255) if i % 2 else (200, 150, 30, 255), outline=L.INK + (255,))
    d.rectangle([40, 110, w - 40, 146], fill=(20, 18, 24, 255))
    d.text((w / 2, 128), "SHRED", font=L.font(L.ANTON, 28), fill=(255, 90, 90, 255), anchor="mm")
    return im


def main():
    img = L.backdrop(BG, blur=2, dim=0.62, sat=0.95)
    img = L.vignette(img, 0.55)
    bw, bh = BOARD[2] - BOARD[0], BOARD[3] - BOARD[1]
    img = L.drop_shadow(img, pegboard(bw, bh), BOARD[0], BOARD[1], blur=24, off=(16, 24), op=0.7)
    # section labels
    for txt, x, y, a in (("CARDS", 560, 118, -1.5), ("MICROCHIPS", 1300, 118, 1.2), ("SLICES", 560, 560, 0.8), ("DAEMONS", 1110, 560, -1.0), ("REMOVE A CARD", 1520, 560, 1.4)):
        img = L.drop_shadow(img, L.rotate_rgba(dymo(txt), a), x, y, blur=3, off=(2, 3), op=0.6)
    # cards (hover = Data Surge, lifted, with its BUY sticker)
    cards = [
        dict(name="Bulwark", cost=2, kind="SYSTEM", art="slice_firewall", pic="slice_firewall", val="12", text="Gain 12 block.", rar="Uncommon"),
        dict(name="Data Surge", cost=2, kind="SYSTEM", art="picto_draw", pic="picto_draw", val="3", text="Draw 3 cards.", rar="Uncommon"),
        dict(name="Feather Touch", cost=0, kind="WHEEL", art="picto_nudge", pic="picto_nudge", val="1", text="One +-1 nudge.", rar="Common"),
    ]
    prices = [55, 60, 50]
    for i, c in enumerate(cards):
        x, y = 680 + i * 220, 330
        img = hook(img, x, y - 150)
        hov = i == 1
        sd = L.card_sticker(c, 190, 253, gloss_k=0.6 if hov else 0.22, seed=20 + i)
        if i == 2:
            sd = L.greyscale(sd, 0.6)
        img = L.place_sticker(img, sd, x, y - (14 if hov else 0), angle=[-2, 0, 2.5][i], scale=1.06 if hov else 1.0, hover=0.8 if hov else 0.0)
        img = tag_on(img, prices[i], x + 40, y + 160, sold=(i == 2), seed=30 + i, angle=-4 + 4 * i)
    buy = L.sticker_word(["BUY 60"], 44, fills=["pink"], seed=41)
    img = L.place_sticker(img, buy, 900, 545, angle=-3)
    # microchips
    chips = [("Overvolt", "slice_exploit", (126, 210, 60), "Common", 90), ("Static Coat", "slice_sandbox", (92, 225, 255), "Common", 85)]
    for i, (nm, gl, col, rar, pr) in enumerate(chips):
        x, y = 1440 + i * 250, 320
        img = hook(img, x, y - 130)
        sd = L.sticker_from_art(L.chip_art(nm, gl, col, w=170, rar=rar), border=7, seed=50 + i)
        img = L.place_sticker(img, sd, x, y, angle=[2, -2][i])
        img = tag_on(img, pr, x + 40, y + 150, seed=60 + i, angle=3 - 6 * i)
    # slices (overwrite a slot): tiles on a backing card
    tiles = [("tile_SANDBOX_8_1.png", 100), ("tile_ZERODAY_12_1.png", 100)]
    for i, (fn, pr) in enumerate(tiles):
        x, y = 680 + i * 250, 720
        img = hook(img, x, y - 110)
        t = L.tile(fn)
        card = Image.new("RGBA", (t.width + 30, t.height + 50), (0, 0, 0, 0))
        dc = ImageDraw.Draw(card)
        dc.rounded_rectangle([0, 0, card.width - 1, card.height - 1], radius=12, fill=(20, 18, 26, 255))
        card.alpha_composite(t, (15, 12))
        dc.text((card.width / 2, card.height - 20), "OVERWRITE 1 SLOT", font=L.f_mono(13), fill=(170, 230, 140, 255), anchor="mm")
        sd = L.sticker_from_art(card, border=7, seed=70 + i)
        img = L.place_sticker(img, sd, x, y, angle=[-2, 1.5][i])
        img = tag_on(img, pr, x + 50, y + 125, seed=80 + i, angle=-3 + 6 * i)
    # daemons
    dms = [("Warm Boot", "picto_ram", (255, 190, 60), "Uncommon", 180), ("Salvager", "picto_again", (61, 255, 139), "Common", 160)]
    for i, (nm, gl, col, rar, pr) in enumerate(dms):
        x, y = 1200 + i * 190, 740
        img = hook(img, x, y - 120)
        sd = L.sticker_from_art(L.daemon_art(nm, gl, col, w=150, rar=rar), border=7, seed=90 + i)
        img = L.place_sticker(img, sd, x, y, angle=[-3, 2][i])
        img = tag_on(img, pr, x + 40, y + 120, afford=(pr <= WALLET), seed=100 + i, angle=-2 + 5 * i)
    # shred
    sh = shredder()
    img = L.drop_shadow(img, sh, 1580, 630, blur=10)
    img = tag_on(img, 50, 1800, 880, seed=110, angle=4)
    # clerk terminal over the shop window, + its spill
    cp = clerk_panel()
    img = L.crt_glow_under(img, (60, 540, 480, 920), L.CYAN, 0.25)
    img = L.paste(img, cp, 60, 540)
    # grease pencil notes: BUY / SHRED (art_asset G18), and "too much" on the daemon you can't afford
    p = L.pen(L.GP_YELLOW, seed=81)
    p.text("BUY", 1040, 590, 40, angle=-10)
    p.arrow([(1010, 580), (985, 565), (968, 556)], width=7, head=16)
    p.text("SHRED THE BUG?", 1640, 528, 28, angle=-4)
    img = L.ink(img, p)
    pr = L.pen(L.GP_RED, seed=82)
    pr.circle(1240, 865, 56, 30, width=7)
    pr.text("-20 SHORT", 1250, 925, 26, angle=-4)
    img = L.ink(img, pr)
    # title + leave
    sd = L.sticker_word(["MODEM"], 76, fills=["pink"], seed=83)
    img = L.place_sticker(img, sd, 330, 470, angle=-4)
    lv = L.sticker_word(["LEAVE THE MODEM"], 56, fills=[(232, 230, 238)], seed=84)
    img = L.place_sticker(img, lv, 1620, 1012, angle=-1.5)
    strip = L.CRT(620, 42, L.CYAN, None, header=False, seed=72)
    strip.text((16, 10), "05 MODEM CYBER SHOP  //  LAYER 3 OF 7", 19, L.CYAN)
    img = L.paste(img, strip.finish(scan=0.15), 540, 990)
    img = L.bloom(img, 0.2, 0.8, 8)
    L.save(img, "shop_interior.png")


if __name__ == "__main__":
    main()
