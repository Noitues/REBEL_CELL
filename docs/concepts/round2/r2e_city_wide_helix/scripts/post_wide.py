"""Composite the wide-city passes: pale smog backdrop -> faded outer city (back) -> district + HQ + overlay
(full colour) -> faded outer city (front rows, translucent over the district) -> rain/smog -> HUD.

usage: python post_wide.py <pass_dir> <out_dir>
"""
import json
import os
import sys
from PIL import Image, ImageEnhance, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from post import smog, rain, grain, radial

W, H = 1920, 1080


def fade(im, pale, alpha=0.5, desat=0.7, lift=0.35):
    """Outer city: keep building colours but desaturate ~30%, lighten toward the pale smog, ~50% alpha."""
    a = im.getchannel("A")
    rgb = ImageEnhance.Color(im.convert("RGB")).enhance(desat)
    rgb = Image.blend(rgb, pale.convert("RGB"), lift)
    out = rgb.convert("RGBA")
    out.putalpha(a.point(lambda v: int(v * alpha)))
    return out


def main(pd, od):
    ld = lambda n: Image.open(os.path.join(pd, "pass_%s.png" % n)).convert("RGBA")
    pale = radial((W, H), "#d6cdb4", "#a89e82", cy=0.4, rx=0.9, ry=0.9).convert("RGBA")
    img = pale.copy()
    img = Image.alpha_composite(img, fade(ld("outb"), pale, alpha=0.55))
    img = Image.alpha_composite(img, ld("dist"))
    img = Image.alpha_composite(img, fade(ld("outf"), pale, alpha=0.5))
    img = smog(img, "day", seed=8)
    img = rain(img, "day", n=700)
    img = grain(img, 6)
    img = Image.alpha_composite(img.convert("RGBA"), ld("hud")).convert("RGB")
    img.save(os.path.join(od, "city_day.png"), optimize=True)
    meta = json.load(open(os.path.join(pd, "meta.json")))
    x0, y0, x1, y1 = meta["hq_bbox"]
    pad = 70
    box = (max(0, int(x0 - pad)), max(0, int(y0 - pad)), min(W, int(x1 + pad)), min(H, int(y1 + pad)))
    crop = img.crop(box)
    crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
    crop.save(os.path.join(od, "hq_closeup.png"), optimize=True)
    print("wrote", od, box)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
