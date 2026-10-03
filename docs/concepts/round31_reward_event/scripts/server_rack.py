"""Round 31 -> server_rack.png: RACK BREACHED. Left: what the Rack banked (CRT) + its rare Daemon offer
(stickers). Centre: the upgrade bay, the operative's spinner on the Rack's flash bench. Right: the tier
ladder I -> II -> III (locked V2 strong tiers, from the round 17 kit). Bottom: the Rack's slice drawer
for a swap (dashed = what-if, per the locked path rules).

python server_rack.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import r31lib as L
import sticker_lib19 as SL

BG = os.path.join(L.CONCEPTS, "round26_hq_targets", "site_meridian_night.jpg")
WC = (900, 520)   # wheel centre
WR = 280          # slice outer radius in the wheel render


def wheel_frame(img, c, r):
    """A plain bench rim (the D4 lens & rail frame belongs to the wheel pass): ticks, pointer, hub."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    R = r + 34
    d.ellipse([c[0] - R, c[1] - R, c[0] + R, c[1] + R], outline=(255, 61, 168, 255), width=4)
    d.ellipse([c[0] - R + 10, c[1] - R + 10, c[0] + R - 10, c[1] + R - 10], outline=(110, 40, 90, 255), width=2)
    for k in range(30):
        a = math.radians(-90 + k * 12)
        r0, r1 = R - 10, R - (22 if k % 5 == 0 else 15)
        d.line([(c[0] + r0 * math.cos(a), c[1] + r0 * math.sin(a)), (c[0] + r1 * math.cos(a), c[1] + r1 * math.sin(a))], fill=(255, 140, 210, 255), width=3 if k % 5 == 0 else 2)
    f = L.f_mono(15)
    txt = "CELL-9 // BREAKER // SPINNER ON THE FLASH BENCH // 6 SLICES // "
    for i, ch in enumerate(txt * 2):
        a = -math.pi * 0.95 + i * 0.0335
        if a > math.pi * 0.95 - 0.6:
            break
        x, y = c[0] + (R + 18) * math.cos(a - math.pi / 2), c[1] + (R + 18) * math.sin(a - math.pi / 2)
        g = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
        ImageDraw.Draw(g).text((12, 12), ch, font=f, fill=(255, 120, 200, 230), anchor="mm")
        g = g.rotate(-math.degrees(a), Image.BICUBIC)
        lay.alpha_composite(g, (int(x - 12), int(y - 12)))
    glow = lay.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, glow)
    return Image.alpha_composite(img, lay)


def hub(img, c):
    d = ImageDraw.Draw(img)
    r = 92
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=(16, 12, 22, 255), outline=(255, 61, 168, 255), width=3)
    d.text((c[0], c[1] - 14), "BREAKER", font=L.f_num(30), fill=(255, 255, 255, 255), anchor="mm")
    d.text((c[0], c[1] + 16), "Breaker Core", font=L.f_mono(15), fill=(255, 140, 200, 255), anchor="mm")
    d.text((c[0], c[1] + 40), "RANK 2", font=L.f_mono(14), fill=(160, 120, 150, 255), anchor="mm")
    return img


def bank_panel():
    c = L.CRT(420, 300, L.SCHEM, "BANKED", tag="LOGISTICS DIRECTOR DOWN", seed=21)
    y = 58
    c.paste(L.schem_mark(34, L.SCHEM), 22, y)
    c.text((66, y + 2), "SCHEMATICS", 22, L.SCHEM)
    c.text((400, y - 8), "+17", 44, L.SCHEM, anchor="ra", fnt=L.f_num(48))
    c.text((66, y + 34), "T2 rack  //  safe even if you flatline", 15, (200, 160, 90))
    c.rule(y + 62, dash=True)
    y += 76
    c.paste(L.cycles_mark(28, L.CYCLE), 24, y)
    c.text((66, y + 2), "CYCLES held", 20, L.CYCLE)
    c.text((400, y - 2), "160", 30, L.CYCLE, anchor="ra", fnt=L.f_num(34))
    y += 44
    c.paste(L.heat_mark(26, L.HEAT), 24, y)
    c.text((66, y + 2), "HEAT", 20, L.HEAT)
    c.text((400, y - 2), "+3", 30, L.HEAT, anchor="ra", fnt=L.f_num(34))
    y += 44
    c.text((24, y + 4), "armory: 1 asset banked (ICE LOCK)", 16, (170, 170, 190))
    return c.finish()


def ladder_panel():
    c = L.CRT(560, 610, L.CYAN, "SLICE FLASH", tag="EXPLOIT // SLOT 1", seed=22)
    d = c.d
    tiles = [L.tile("big_tile_EXPLOIT_6_1.png"), L.tile("big_tile_EXPLOIT_8_2.png"), L.tile("big_tile_EXPLOIT_10_3.png")]
    ys = [70, 250, 430]
    caps = [("I", "base", "6 dmg"), ("II", "NOW", "8 dmg"), ("III", "NEXT", "10 dmg")]
    for i, (t, y) in enumerate(zip(tiles, ys)):
        t = t.resize((int(t.width * 0.78), int(t.height * 0.78)), Image.LANCZOS)
        if i == 0:
            a = t.split()[3].point(lambda v: int(v * 0.45))
            t.putalpha(a)
        x = 40
        c.paste(t, x, y)
        tier, state, val = caps[i]
        col = {0: (110, 130, 150), 1: (255, 255, 255), 2: (255, 214, 64)}[i]
        d.text((330, y + 26), "TIER " + tier, font=L.f_num(40), fill=col + (255,))
        d.text((332, y + 76), state + "  //  " + val, font=L.f_mono(18), fill=col + (255,))
        if i == 1:
            d.text((332, y + 102), "steel bezel + inset line", font=L.f_mono(14), fill=(140, 170, 190, 255))
        if i == 2:
            d.text((332, y + 102), "gold strip + cross-hatch", font=L.f_mono(14), fill=(200, 170, 90, 255))
            d.text((332, y + 122), "brighter screen", font=L.f_mono(14), fill=(200, 170, 90, 255))
        if i < 2:
            ax = 170
            ay0, ay1 = y + 150, ys[i + 1] + 4
            for yy in range(ay0, ay1 - 12, 9):
                d.line([(ax, yy), (ax, yy + 4)], fill=L.CYAN + (200,), width=3)
            d.polygon([(ax - 10, ay1 - 14), (ax + 10, ay1 - 14), (ax, ay1)], fill=L.CYAN + (255,))
    d.text((24, 584), "silhouette never changes: tier reads by shape + colour", font=L.f_mono(14), fill=(110, 150, 170, 255))
    return c.finish()


def drawer_panel():
    c = L.CRT(980, 220, L.LIME, "RACK DRAWER // SWAP A SLICE", tag="OVERWRITE 1 SLOT", seed=23)
    names = ["big_tile_SANDBOX_8_1.png", "big_tile_PATCH_4_2.png", "big_tile_ZERODAY_15_2.png", "big_tile_TROJAN_1_1.png"]
    labels = ["SANDBOX 8", "PATCH 4  II", "ZERO-DAY 15  II", "TROJAN 1"]
    for i, n in enumerate(names):
        t = L.tile(n)
        t = t.resize((int(t.width * 0.58), int(t.height * 0.58)), Image.LANCZOS)
        x = 30 + i * 238
        c.d.rounded_rectangle([x - 8, 52, x + t.width + 8, 196], radius=8, outline=(80, 120, 60, 255), width=2)
        c.paste(t, x, 58)
        c.text((x + t.width / 2, 186), labels[i], 15, (170, 230, 140), anchor="ms")
    return c.finish()


def daemon_offer(img):
    lay = L.paper(420, 330, seed=8, tint=(232, 230, 224), fold=False)
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 0, 420, 40], fill=(26, 24, 32, 255))
    d.text((16, 20), "RARE DAEMON  //  PICK 1", font=L.f_mono(18), fill=(240, 238, 232, 255), anchor="lm")
    img = L.drop_shadow(img, lay, 60, 650, blur=14)
    for i, (nm, gl, col) in enumerate((("Feedback Loop", "picto_again", (255, 61, 168)), ("Log Wiper", "status_cleanse", (92, 225, 255)))):
        art = L.daemon_art(nm, gl, col, w=150, rar="Rare")
        sd = L.sticker_from_art(art, border=7, seed=30 + i)
        img = L.place_sticker(img, sd, 168 + i * 205, 820, angle=[-4, 3][i])
    d = ImageDraw.Draw(img)
    d.text((80, 958), "run-wide rule; banked with the operative", font=L.f_mono(15), fill=(70, 66, 80, 255))
    return img


def main():
    img = L.backdrop(BG, blur=4, dim=0.5, sat=0.75, crop=(380, 260, 1700, 1002))
    img = L.vignette(img, 0.75)
    img = L.darken_rect(img, (WC[0] - 360, WC[1] - 360, WC[0] + 360, WC[1] + 360), a=190, r=360, blur=50)
    # wheel on the bench
    wh = L.tile("wheel_c.png")
    lift = Image.new("RGBA", img.size, (0, 0, 0, 0))
    img = L.paste(img, wh, WC[0] - wh.width // 2, WC[1] - wh.height // 2)
    img = wheel_frame(img, WC, WR)
    img = hub(img, WC)
    # selected slice (EXPLOIT, slot 1 at the top): lift highlight
    d = ImageDraw.Draw(img)
    # tier ladder
    lp = ladder_panel()
    img = L.crt_glow_under(img, (1320, 150, 1880, 760), L.CYAN, 0.18)
    img = L.paste(img, lp, 1320, 150)
    # drawer
    dp = drawer_panel()
    img = L.crt_glow_under(img, (520, 830, 1500, 1050), L.LIME, 0.15)
    img = L.paste(img, dp, 520, 836)
    # banked + daemon
    bp = bank_panel()
    img = L.crt_glow_under(img, (40, 220, 460, 520), L.SCHEM, 0.15)
    img = L.paste(img, bp, 40, 236)
    img = daemon_offer(img)
    # title
    sd = L.sticker_word(["RACK BREACHED"], 84, fills=["yellow"], seed=41)
    img = L.place_sticker(img, sd, 400, 110, angle=-3)
    strip = L.CRT(520, 42, L.CYAN, None, header=False, seed=24)
    strip.text((16, 10), "SERVER RACK 7/7  //  MERIDIAN DEPOT 15", 19, L.CYAN)
    img = L.paste(img, strip.finish(scan=0.15), 760, 40)
    # buttons
    up = L.sticker_word(["UPGRADE"], 70, fills=["pink"], seed=43)
    img = L.place_sticker(img, up, 1660, 850, angle=-2)
    sk = L.sticker_word(["SKIP"], 44, fills=[(232, 230, 238)], seed=44, extrude=4)
    img = L.place_sticker(img, sk, 1740, 990, angle=2)
    # grease pencil: the plan
    p = L.pen(L.GP_YELLOW, seed=12)
    top = (WC[0], WC[1] - 200)
    p.circle(top[0], top[1] + 10, 150, 78, width=9, start=-2.6)
    p.arrow([(top[0] + 150, top[1] - 20), (1100, 170), (1250, 220), (1325, 470)], width=9, head=26)
    img = L.ink(img, p)
    # what-if swap: dashed (locked rule: dashed = what-if)
    p2 = L.pen(L.GP_YELLOW, seed=13)
    pts = SL.catmull([(625, 860), (560, 760), (600, 560), (690, 400)], 18)
    for i in range(0, len(pts) - 3, 6):
        p2.stroke(pts[i:i + 4], width=7, taper=False)
    ex, ey = pts[-1]
    px_, py_ = pts[-4]
    ang = math.atan2(ey - py_, ex - px_)
    for s in (-0.5, 0.5):
        a = ang + math.pi + s
        p2.stroke([(ex + 22 * math.cos(a), ey + 22 * math.sin(a)), (ex, ey)], width=7, taper=False)
    p2.text("or swap?", 520, 700, 30, angle=-70)
    img = L.ink(img, p2)
    img = L.bloom(img, 0.22, 0.78, 8)
    L.save(img, "server_rack.png")


if __name__ == "__main__":
    main()
