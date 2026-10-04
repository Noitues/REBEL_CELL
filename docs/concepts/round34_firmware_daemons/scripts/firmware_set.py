"""firmware_set.png: all 18 Firmware chips (real names, rarity, valid slices, effect) at shop size, socketed on an
r=220 wheel and on r=60 wheels, plus a greyscale check.

python firmware_set.py
"""
from PIL import Image, ImageDraw
import fwlib as F
L = F.L

DEMO_SLICES = [("EXPLOIT", 8, 2, None), ("FIREWALL", 5, 1, "ENCRYPTED"), ("PROXY", 4, 1, None),
               ("VIRUS", 3, 1, None), ("ZERO-DAY", 12, 1, "OVERCLOCKED"), ("NULL", None, 1, None)]
DEMO_FW = ["overvolt", "hardened", "counterstrike", "mirror", "burner", "recycler"]
SMALL_SLICES = [("EXPLOIT", 6, 1, None), ("FIREWALL", 5, 1, None), ("PROXY", 4, 1, None),
                ("PATCH", 4, 1, None), ("ZERO-DAY", 12, 1, None), ("NULL", None, 1, None)]
SMALL_FW = ["leech", "static_coat", None, "nanite_mesh", "tracer", None]


def main():
    img = F.bg(seed=3)
    d = F.header(img, "FIRMWARE  (18)",
                 "A faceted die that SOCKETS into the inner, hub-side band of one slice, pins into the core (GDD 6.1: one socket per slice). LED + pips = rarity. Glyph = effect family.")
    # ---------------- the 18
    F.section(d, 32, 118, "THE SET  -  shop size (100 px), real content names + .tres effects")
    cw, chh = 203, 300
    for i, f in enumerate(F.FIRMWARE):
        fid, name, rar, types, eff = f
        col, row = i % 6, i // 6
        x0, y0 = 32 + col * cw, 164 + row * chh
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([x0, y0, x0 + cw - 10, y0 + chh - 12], radius=10, fill=(20, 18, 28, 255), outline=(44, 40, 58, 255))
        ch = F.chip(fid, 100)
        img.alpha_composite(ch, (int(x0 + (cw - 10) / 2 - ch.width / 2), y0 + 4))
        d = ImageDraw.Draw(img)
        cx = x0 + (cw - 10) / 2
        d.text((cx, y0 + 150), name.upper(), font=L.f_num(26), fill=(245, 245, 250, 255), anchor="mm")
        rc = F.RAR_COL[rar]
        d.text((cx, y0 + 174), F.RAR_NAME[rar] + "  ·  " + F.allowed_text(types), font=L.f_mono(13), fill=rc + (255,), anchor="mm")
        fnt = L.f_ui(15, b"Regular")
        for k, ln in enumerate(F.wrap(eff, fnt, cw - 30)[:4]):
            d.text((cx, y0 + 198 + k * 19), ln, font=fnt, fill=(200, 200, 212, 255), anchor="mm")
    # ---------------- on the wheel
    d = ImageDraw.Draw(img)
    F.section(d, 1268, 118, "SOCKETED  -  r = 220", L.CYAN)
    w = F.socket_wheel(DEMO_SLICES, DEMO_FW, 220, "demo")
    img.alpha_composite(w, (1268 + 300 - w.width // 2, 146))
    d = ImageDraw.Draw(img)
    d.text((1268, 650), "chip = inner band on the midline, pins into the core (round 34)", font=L.f_mono(13), fill=(170, 200, 220, 255))
    d.text((1268, 668), "Hardened = chip + its permanent ENCRYPTED; Burner = chip + OVERCLOCKED", font=L.f_mono(13), fill=(170, 200, 220, 255))
    # r = 60
    F.section(d, 1268, 698, "r = 60 + r = 110  (LOD)", L.CYAN)
    ws = F.socket_wheel(SMALL_SLICES, SMALL_FW, 60, "small")
    img.alpha_composite(ws, (1268, 738))
    img.alpha_composite(F.grey(ws), (1268 + 140, 738))
    w2 = F.socket_wheel(SMALL_SLICES, SMALL_FW, 110, "small110")
    img.alpha_composite(w2, (1650, 712))
    d = ImageDraw.Draw(img)
    d.text((1268 + 68, 880), "colour", font=L.f_mono(12), fill=(160, 160, 175, 255), anchor="mm")
    d.text((1268 + 208, 880), "greyscale", font=L.f_mono(12), fill=(160, 160, 175, 255), anchor="mm")
    d.text((1650 + w2.width // 2, 966), "r = 110 (enemy / mini spinner)", font=L.f_mono(12), fill=(160, 160, 175, 255), anchor="mm")
    # greyscale check of the set (48 px)
    F.section(d, 1268, 890, "GREYSCALE  (pips carry rarity)", (200, 200, 210))
    for i, f in enumerate(F.FIRMWARE):
        c = F.chip(f[0], 32, grey=True)
        img.alpha_composite(c, (1268 + (i % 9) * 41, 932 + (i // 9) * 50))
    d = ImageDraw.Draw(img)
    # rarity legend
    lx = 1660
    for r in range(3):
        y = 984 + r * 28
        d.ellipse([lx, y, lx + 14, y + 14], fill=F.RAR_COL[r] + (255,), outline=(0, 0, 0, 255))
        for k in range(F.RAR_PIPS[r]):
            d.rectangle([lx + 24 + k * 9, y + 2, lx + 29 + k * 9, y + 12], fill=(235, 235, 245, 255))
        d.text((lx + 56, y + 7), F.RAR_NAME[r], font=L.f_mono(14), fill=F.RAR_COL[r] + (255,), anchor="lm")
    L.save(img, "firmware_set.png")


if __name__ == "__main__":
    main()
