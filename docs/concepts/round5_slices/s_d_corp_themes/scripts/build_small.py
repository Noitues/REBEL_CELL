"""Builds small_and_grey.png: wheels at outer radius 60 px (full shader and small-size LOD),
and hero size in greyscale."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageOps
import slicelib as sl
import themes as th
import wheel as wl
from data import WHEELS
from build_wheels import get_wheel

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = ["player", "meridian", "solace", "orbital", "rebel", "halcyon"]


def lod_wheel(k):
    W = WHEELS[k]
    return wl.render_wheel(k, W["slices"], W["name"], W["corp"], t=0.3, seed=3, lod=True)


def small_row(fr, d, imgs, y, note):
    sc = 60.0 / sl.R_OUT
    for i, (k, img) in enumerate(zip(KEYS, imgs)):
        s = int(img.width * sc)
        im = img.resize((s, s), Image.LANCZOS)
        cx = 330 + i * 265
        fr.alpha_composite(im, (int(cx - s / 2), y))
        lab = th.THEMES[k]["name"].split(" (")[0]
        f = sl.font(16, "SemiBold")
        bb = f.getbbox(lab)
        d.text((cx - (bb[2] - bb[0]) / 2, y + s - 2), lab, font=f, fill=(190, 190, 200, 255))
    d.text((24, y + 60), note, font=sl.font(22, "SemiBold"), fill=(235, 235, 245, 255))


def main():
    fr = wl.background(seed=5)
    d = ImageDraw.Draw(fr)
    d.text((24, 10), "READABILITY: r = 60 px, 1:1 (top two rows)  //  hero size in greyscale (bottom)",
           font=sl.font(34), fill=(240, 240, 248, 255))
    small_row(fr, d, [get_wheel(k) for k in KEYS], 58, "FULL SHADER")
    small_row(fr, d, [lod_wheel(k) for k in KEYS], 262, "SMALL LOD")
    d.text((24, 262 + 92), "flat corp tint,\nglyph x1.55", font=sl.mono(14, False), fill=(170, 170, 185, 255))
    for i, k in enumerate(["player", "meridian", "rebel"]):
        img = get_wheel(k)
        s = int(img.width * 0.55)
        g = ImageOps.grayscale(img.convert("RGB").resize((s, s), Image.LANCZOS))
        a = img.split()[3].resize((s, s), Image.LANCZOS)
        fr.alpha_composite(Image.merge("RGBA", (g, g, g, a)), (int(330 + i * 630 - s / 2), 472))
        f = sl.font(20, "SemiBold")
        lab = th.THEMES[k]["name"] + "  -  greyscale"
        bb = f.getbbox(lab)
        d.text((330 + i * 630 - (bb[2] - bb[0]) / 2, 1050), lab, font=f, fill=(200, 200, 210, 255))
    fr.convert("RGB").save(os.path.join(OUT, "small_and_grey.png"))
    print("wrote small_and_grey.png")


if __name__ == "__main__":
    main()
