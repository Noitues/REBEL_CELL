"""Round 28: castle_texture_options.png + hq_meridian_close_{night,day}.jpg (recommended t3).

Each variant: the close-up (night, face-on to the gate) finished with the round 11 style pass (backdrop26.finish) and
the city-map crop (the round 27 map crop with the variant's map sprite composited at the HQ's map position - the
shape is locked, so the new sprite covers the old one exactly).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import backdrop26 as B
import city_hq_v5 as CV
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(HERE)
R27 = os.path.join(OUT, "..", "round27_hq_targets")
F = "C:/Windows/Fonts/bahnschrift.ttf"
f1, f2, f3 = ImageFont.truetype(F, 34), ImageFont.truetype(F, 20), ImageFont.truetype(F, 16)
ORANGE = (255, 150, 40)
VARS = [("t1", "meridian_hq_t1", "A  RAW CORRUGATED STEEL", ["deep raised/sunk ribs, door ends + lock bars", "unified Meridian orange, clean", "reads as new kit, a bit plain"]),
        ("t2", "meridian_hq_t2", "B  MIXED LIVERIES + RUST", ["real mixed container colours, white band", "rust patches, stencil codes", "most 'containers', loses Meridian orange"]),
        ("t3", "meridian_hq", "C  WEATHERED MERIDIAN  (RECOMMENDED)", ["burnt orange, heavy rust + grime streaks", "MRDU stencils, hazard stripes, tarps, nets",
                                                                       "owned + used: Meridian and a fortress"]),
        ("t4", "meridian_hq_t4", "D  LIT FORTRESS", ["charcoal walls, white tower band", "lit course seams, floodlight washes", "spectacle, but competes with the wheels"])]


def city_crop(var):
    base = Image.open(os.path.join(R27, "hq_meridian_city.jpg")).convert("RGB")
    CV.MAP = os.path.join(OUT, "scratch", "opt")
    sp = CV.sprite("meridian_hq_%s" % var)
    z = 0.633
    sp = sp.resize((int(sp.width * z / 2), int(sp.height * z / 2)), Image.LANCZOS)
    cx, cy = 550, int(1100 / 2 * 0.62) - 250 * z
    base.paste(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)), sp)
    return base


def main():
    W, H = 2400, 1080
    sh = Image.new("RGB", (W, H), (14, 13, 20))
    d = ImageDraw.Draw(sh)
    d.text((20, 14), "MERIDIAN  -  texture passes on the locked Container Wall fortress (night, face-on to the gate)", font=f1, fill=(240, 236, 226))
    cw = 590
    for i, (var, tag, title, lines) in enumerate(VARS):
        im = B.finish(tag, "night")
        if var == "t3":
            B.calm(im).save(os.path.join(OUT, "hq_meridian_close_night.jpg"), quality=90)
            B.calm(B.finish(tag, "day")).save(os.path.join(OUT, "hq_meridian_close_day.jpg"), quality=90)
        x = 15 + i * (cw + 8)
        c = im.crop((560, 0, 1360, 860)).resize((cw, int(cw * 860 / 800)), Image.LANCZOS)
        sh.paste(c, (x, 64))
        y = 64 + c.height + 8
        d.text((x, y), title, font=f2, fill=ORANGE if var == "t3" else (230, 230, 240))
        for k, ln in enumerate(lines):
            d.text((x, y + 28 + k * 21), ln, font=f3, fill=(200, 200, 210))
        cc = city_crop(var).crop((280, 60, 820, 560)).resize((cw, int(cw * 500 / 540)), Image.LANCZOS)
        cc = cc.crop((0, 0, cw, min(cc.height, H - (y + 100) - 6)))
        sh.paste(cc, (x, y + 96))
        if var == "t3":
            d.rectangle([x - 4, 60, x + cw + 3, H - 4], outline=ORANGE, width=3)
            city_crop(var).save(os.path.join(OUT, "hq_meridian_city.jpg"), quality=90)
    sh.save(os.path.join(OUT, "castle_texture_options.png"), optimize=True)
    print("castle_texture_options.png")


if __name__ == "__main__":
    main()
