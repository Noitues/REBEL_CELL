"""Round 18: PRIORITY glyph (Meridian RAM drain, replaces JUDGEMENT): a rotating alarm beacon.

A rounded dome on a flat base plate, a small highlight cut-out, 5 short ray strokes fanning out above.
Same language as the round 17 set: one bold white silhouette (512 box), strokes >= 40/512.

python glyph_priority.py   -> ../special_priority.png (256 px, white on transparent) + ../scratch/priority_check.png
and prints the 16 px soft-IoU twin scores against the round 17 slice/special glyph PNGs.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
SET = os.path.join(OUT, "..", "round17_slice_system", "glyphs")
S = 512


def priority():
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    # thick base plate, narrower than the sun's horizon so it reads as an object, not a skyline
    d.rounded_rectangle([140, 404, 372, 480], radius=16, fill=255)
    # tall beacon dome: straight sides with a round top (a bullet / bell lamp)
    d.rectangle([176, 250, 336, 392], fill=255)
    d.ellipse([176, 170, 336, 330], fill=255)
    d.rectangle([158, 380, 354, 392], fill=255)
    d.rectangle([140, 392, 372, 404], fill=0)       # gap between lamp and base
    d.rounded_rectangle([210, 224, 240, 330], radius=14, fill=0)  # highlight
    # 5 short rays fanning out above and beside the dome
    cx, cy = 256, 260
    for a in (-90, -138, -42, -180, 0):
        r0, r1 = 128, 186
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.line([(cx + r0 * ca, cy + r0 * sa), (cx + r1 * ca, cy + r1 * sa)], fill=255, width=42)
        for rr in (r0, r1):
            x, y = cx + rr * ca, cy + rr * sa
            d.ellipse([x - 21, y - 21, x + 21, y + 21], fill=255)
    return m

def cov(mask, px=16):
    m = mask.resize((px, px), Image.BOX).filter(ImageFilter.GaussianBlur(0.6))
    return np.asarray(m, np.float32) / 255.0


def sim(a, b):
    return float(np.minimum(a, b).sum() / max(1e-6, np.maximum(a, b).sum()))


def main():
    m = priority()
    os.makedirs(os.path.join(OUT, "scratch"), exist_ok=True)
    out = Image.new("RGBA", (256, 256), (255, 255, 255, 0))
    out.putalpha(m.resize((256, 256), Image.LANCZOS))
    out.save(os.path.join(OUT, "special_priority.png"))
    c = cov(m)
    scores = []
    for f in sorted(os.listdir(SET)):
        if f.endswith(".png"):
            g = Image.open(os.path.join(SET, f)).convert("RGBA").split()[3]
            g = g.resize((S, S), Image.LANCZOS)
            scores.append((sim(c, cov(g)), f))
    scores.sort(reverse=True)
    for s_, f in scores[:8]:
        print("%.2f  %s" % (s_, f))
    # check sheet: 256 / 64 / 24 / 16 + nearest twins at 16
    W = 900
    im = Image.new("RGB", (W, 330), (11, 10, 16))
    d = ImageDraw.Draw(im)
    x = 10
    for px in (256, 64, 24, 16):
        g = Image.new("RGB", (px, px), (11, 10, 16))
        g.paste((255, 255, 255), (0, 0), m.resize((px, px), Image.LANCZOS))
        im.paste(g, (x, 20))
        x += px + 20
    y = 20
    for s_, f in scores[:4]:
        g = Image.open(os.path.join(SET, f)).convert("RGBA")
        t = Image.new("RGB", (16, 16), (11, 10, 16))
        t.paste((255, 255, 255), (0, 0), g.split()[3].resize((16, 16), Image.LANCZOS))
        im.paste(t.resize((64, 64), Image.NEAREST), (560, y))
        p = Image.new("RGB", (16, 16), (11, 10, 16))
        p.paste((255, 255, 255), (0, 0), m.resize((16, 16), Image.LANCZOS))
        im.paste(p.resize((64, 64), Image.NEAREST), (640, y))
        d.text((720, y + 24), "%.2f  %s" % (s_, f), fill=(200, 200, 210))
        y += 74
    im.save(os.path.join(OUT, "scratch", "priority_check.png"))
    return scores[0][0]


if __name__ == "__main__":
    print("max twin", main())
