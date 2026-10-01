"""Builds corp_sheet.png: 5 corporation rows x 5 programs (3-tick) + 2-tick and 5-tick variants."""
import os
import sys
import math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import slicelib as sl
import themes as th
import wheel as wl
from data import SHEET, STILL_T

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAD = 22


def tile(theme, typ, val, ticks, t, seed):
    box = sl.tile_box(ticks, pad=PAD)
    ctx = sl.Ctx(*box, half_deg=ticks * sl.TICK_DEG / 2, t=t, seed=seed, accent=sl.TYPES[typ][1],
                 typ=typ, ticks=ticks)
    img, em = sl.render_tile(ctx, th.THEMES[theme]["tex"], val, {})
    return sl.add_glow(img, sl.emis_to_img(em), radii=((5, 0.8), (14, 0.5)))


def main():
    Wf, Hf = 1920, 1080
    frame = Image.new("RGBA", (Wf, Hf), (9, 8, 14, 255))
    d = ImageDraw.Draw(frame)
    for x in range(0, Wf, 40):
        d.line([(x, 0), (x, Hf)], fill=(14, 13, 21, 255))
    for y in range(0, Hf, 40):
        d.line([(0, y), (Wf, y)], fill=(14, 13, 21, 255))
    d.text((24, 12), "CORPORATION SLICE THEMES", font=sl.font(40), fill=(240, 240, 248, 255))
    d.text((520, 24), "one material family per corp  //  type = glyph + accent rim + outer tab  //  value in white",
           font=sl.mono(18, False), fill=(170, 170, 185, 255))
    s = 0.62
    row_h = 202
    y0 = 70
    col_x = [430 + i * 172 for i in range(5)]
    v2_x, v5_x = 1325, 1468
    d.text((v2_x + 10, 52), "2-TICK", font=sl.font(18, "SemiBold"), fill=(150, 150, 165, 255))
    d.text((v5_x + 80, 52), "5-TICK", font=sl.font(18, "SemiBold"), fill=(150, 150, 165, 255))
    for ri, (theme, progs, v2, v5) in enumerate(SHEET):
        T = th.THEMES[theme]
        col = tuple(int(v * 255) for v in sl.hexrgb(T["col"]))
        ry = y0 + ri * row_h
        band = Image.new("RGBA", (Wf, row_h - 6), col + (14,))
        frame.alpha_composite(band, (0, ry))
        d.rectangle([0, ry, 6, ry + row_h - 7], fill=col + (255,))
        # label column
        d.text((22, ry + 14), T["name"], font=sl.font(30), fill=col + (255,))
        e = Image.new("L", (64, 64), 0)
        wl.draw_emblem(ImageDraw.Draw(e), theme, 32, 32, 52)
        frame.paste(Image.new("RGBA", (64, 64), col + (255,)), (330, ry + 60), e)
        f = sl.mono(15, False)
        yy = ry + 60
        for label, txt in (("TEX", T["texture"]), ("FX ", T["behaviour"])):
            words = txt.split()
            line = ""
            first = True
            for wd in words:
                if len(line) + len(wd) + 1 > 30:
                    d.text((22, yy), ("%s  " % label if first else "     ") + line, font=f, fill=(205, 205, 215, 255))
                    yy += 20
                    line, first = wd, False
                else:
                    line = (line + " " + wd).strip()
            d.text((22, yy), ("%s  " % label if first else "     ") + line, font=f, fill=(205, 205, 215, 255))
            yy += 26
        # tiles
        base_t = STILL_T.get(theme, 0.3)
        items = [(p, 3, col_x[i]) for i, p in enumerate(progs)] + [(v2, 2, v2_x), (v5, 5, v5_x)]
        for k, ((typ, val), ticks, x) in enumerate(items):
            img = tile(theme, typ, val, ticks, (base_t + k * 0.11) % 1.0, seed=ri * 20 + k)
            img = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
            frame.alpha_composite(img, (int(x), int(ry + 2)))
            prog = sl.TYPES[typ][0]
            tcol = tuple(int(v * 255) for v in sl.hexrgb(sl.TYPES[typ][1]))
            fl = sl.font(20)
            bb = fl.getbbox(prog)
            cx = x + img.width / 2
            d.text((cx - (bb[2] - bb[0]) / 2, ry + 2 + img.height - 6), prog, font=fl, fill=tcol + (255,))
    frame.convert("RGB").save(os.path.join(OUT, "corp_sheet.png"))
    print("wrote corp_sheet.png")


if __name__ == "__main__":
    main()
