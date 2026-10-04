"""daemon_set.png: all 24 Daemon sigils on their CRT tiles (real names + .tres effects), the trigger-family colours,
the rarity treatment, greyscale and 48 / 24 / 16 px checks.

python daemon_set.py
"""
from PIL import Image, ImageDraw
import fwlib as F
L = F.L


def main():
    img = F.bg(seed=11)
    d = F.header(img, "DAEMONS  (24)",
                 "A Daemon is a process the Cell keeps running: a sigil on a small CRT tile. Phosphor colour = WHEN it fires (trigger family); bezel + pips = rarity. 24 unique sigils, none a slice glyph or card picto.")
    F.section(d, 32, 118, "THE SET  -  tile 104 px", L.CYAN)
    cw, chh = 158, 296
    for i, dm in enumerate(F.DAEMONS):
        did, name, rar, fam, eff, counter = dm
        col, row = i % 8, i // 8
        x0, y0 = 32 + col * cw, 160 + row * chh
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([x0, y0, x0 + cw - 8, y0 + chh - 10], radius=10, fill=(20, 18, 28, 255), outline=(44, 40, 58, 255))
        t = F.daemon_tile(did, 104, t=0.3 + i * 0.07)
        cx = x0 + (cw - 8) / 2
        img.alpha_composite(t, (int(cx - 52), y0 + 10))
        d = ImageDraw.Draw(img)
        nm = name.upper()
        f = L.f_num(23)
        while f.getlength(nm) > cw - 16:
            f = L.f_num(f.size - 1)
        d.text((cx, y0 + 134), nm, font=f, fill=(245, 245, 250, 255), anchor="mm")
        d.text((cx, y0 + 156), F.RAR_NAME[rar], font=L.f_mono(12), fill=F.RAR_COL[rar] + (255,), anchor="mm")
        d.text((cx, y0 + 172), fam, font=L.f_mono(12), fill=F.FAM[fam] + (255,), anchor="mm")
        fnt = L.f_ui(14, b"Regular")
        lines = F.wrap(eff, fnt, cw - 22)
        for k, ln in enumerate(lines[:5]):
            d.text((cx, y0 + 194 + k * 17), ln, font=fnt, fill=(200, 200, 212, 255), anchor="mm")
    # ---- families
    X0 = 1314
    d = ImageDraw.Draw(img)
    F.section(d, X0, 118, "PHOSPHOR = TRIGGER FAMILY", L.CYAN)
    for k, (fam, col) in enumerate(F.FAM.items()):
        y = 162 + k * 30
        d.rounded_rectangle([X0 + 4, y, X0 + 26, y + 22], radius=5, fill=tuple(int(c * 0.2) for c in col) + (255,), outline=col + (255,), width=2)
        d.text((X0 + 38, y + 11), fam, font=L.f_num(20), fill=col + (255,), anchor="lm")
        d.text((X0 + 130, y + 11), F.FAM_NOTE[fam], font=L.f_mono(14), fill=(200, 200, 212, 255), anchor="lm")
    # ---- rarity
    F.section(d, X0, 350, "RARITY  (bezel + pips)", L.CYAN)
    for k, did in enumerate(("salvager", "warm_boot", "twin_pointer")):
        t = F.daemon_tile(did, 96, t=0.05)
        img.alpha_composite(t, (X0 + 10 + k * 190, 392))
        d = ImageDraw.Draw(img)
        r = F.DM[did][2]
        d.text((X0 + 58 + k * 190, 500), F.RAR_NAME[r], font=L.f_mono(14), fill=F.RAR_COL[r] + (255,), anchor="mm")
        d.text((X0 + 58 + k * 190, 518), ["gunmetal, 1 pip", "cyan edge, 2 pips", "gold + brackets, 3"][k], font=L.f_mono(12), fill=(170, 170, 185, 255), anchor="mm")
    # ---- size checks
    F.section(d, X0, 548, "48 px  colour / greyscale", L.CYAN)
    for i, dm in enumerate(F.DAEMONS):
        t = F.daemon_tile(dm[0], 44, t=0.3)
        img.alpha_composite(t, (X0 + 4 + (i % 12) * 48, 590 + (i // 12) * 48))
        img.alpha_composite(F.grey(t), (X0 + 4 + (i % 12) * 48, 694 + (i // 12) * 48))
    d = ImageDraw.Draw(img)
    F.section(d, X0, 798, "24 px tile", L.CYAN)
    for i, dm in enumerate(F.DAEMONS):
        t = F.daemon_tile(dm[0], 22, t=0.3)
        img.alpha_composite(t, (X0 + 4 + i * 24, 840))
    F.section(d, X0, 876, "16 px bare sigil (tooltip rows, tray header)", L.CYAN)
    for i, dm in enumerate(F.DAEMONS):
        m = F.icon(dm[0], 16)
        lay = Image.new("RGBA", (16, 16), F.FAM[dm[3]] + (0,))
        lay.putalpha(m)
        img.alpha_composite(lay, (X0 + 6 + i * 24, 918))
        lay2 = Image.new("RGBA", (16, 16), (255, 255, 255, 0))
        lay2.putalpha(m)
        img.alpha_composite(lay2, (X0 + 6 + i * 24, 942))
    d = ImageDraw.Draw(img)
    notes = ["Idle: scan bar rolls (period 2.4 s, phase per slot), sigil breathes",
             "+/-12 % glow, heartbeat LED blinks once per period.",
             "Fire: white flash, sigil x1.14, RGB split, LED solid (0.35 s).",
             "Counters sit under the tile (see daemon_row.png)."]
    for k, s in enumerate(notes):
        d.text((X0, 976 + k * 20), s, font=L.f_mono(14), fill=(190, 200, 215, 255))
    L.save(img, "daemon_set.png")


if __name__ == "__main__":
    main()
