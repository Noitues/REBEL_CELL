"""Round 16 -> ../firewall_screen.png + ../firewall_fx.gif : the player FIREWALL screen turned round
(shots from the outer arc, wall by the hub)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)

from PIL import Image, ImageDraw, ImageOps
import slicekit as K
import programs
import screens16
from slicelib import f_num, f_ui, f_mono, bloom


def grey(im):
    a = im.split()[3]
    g = ImageOps.grayscale(im.convert("RGB")).convert("RGBA")
    g.putalpha(a)
    return g


def use(new):
    K.setup()
    programs.PLAYER["FIREWALL"] = screens16.firewall if new else programs.firewall


def main():
    use(False)
    old = K.tile("FIREWALL", 5, t=0.3, tier=2, scale=0.62)
    use(True)
    hero = K.tile("FIREWALL", 5, t=0.3, tier=2, scale=0.95)
    strip = [K.tile("FIREWALL", 5, t=f, tier=2, scale=0.5) for f in (0.0, 0.25, 0.5, 0.75)]
    wheel_spec = [("FIREWALL", 5, 2, None), ("EXPLOIT", 6, 2, None), ("FIREWALL", 8, 3, None), ("PROXY", 4, 2, None), ("FIREWALL", 3, 1, None), ("PATCH", 3, 2, None)]
    w60 = K.wheel(wheel_spec, t=0.3, r_px=60)
    w150 = K.wheel(wheel_spec, t=0.3, r_px=150)
    W, H = 1960, 1000
    im = Image.new("RGBA", (W, H), (11, 10, 16, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        d.line([(0, y), (W, y)], fill=(14, 13, 20))
    d.text((40, 18), "ROUND 16  PLAYER FIREWALL SCREEN", font=f_num(54), fill=(255, 255, 255))
    d.text((44, 80), "DEFEND: attacks come from OUTSIDE (the outer arc) and drop inward; the wall stands on the INNER part of the slice, by the hub. "
           "Shots fall, hit the crenellated top, flash, kick sparks back up and heat the bricks.", font=f_mono(14, False), fill=(190, 190, 200))
    im.alpha_composite(hero, (30, 120))
    d.text((40, 120 + hero.height), "new  (hero, t = 0.3)", font=f_ui(18, b"Bold SemiCondensed"), fill=(92, 225, 255))
    ox = 60 + hero.width
    im.alpha_composite(old, (ox, 150))
    d.text((ox + 10, 150 + old.height), "old (rounds 6-15): wall on the OUTER part,", font=f_mono(12, False), fill=(200, 140, 140))
    d.text((ox + 10, 166 + old.height), "shots bouncing up from the hub side", font=f_mono(12, False), fill=(200, 140, 140))
    g = grey(strip[1])
    wx = ox + old.width + 40
    im.alpha_composite(w150, (wx, 110))
    d.text((wx + 40, 110 + w150.height - 6), "r = 150  (FIREWALL at tiers II / III / I)", font=f_mono(12, False), fill=(170, 170, 182))
    im.alpha_composite(w60, (wx + w150.width + 20, 160))
    d.text((wx + w150.width + 40, 160 + w60.height), "r = 60", font=f_mono(12, False), fill=(170, 170, 182))
    gw = grey(w60)
    im.alpha_composite(gw, (wx + w150.width + 20, 200 + w60.height))
    d.text((wx + w150.width + 40, 200 + 2 * w60.height), "r = 60 grey", font=f_mono(12, False), fill=(170, 170, 182))
    sy = max(120 + hero.height + 40, 110 + w150.height + 30, 200 + 2 * w60.height + 30)
    d.text((40, sy), "4-FRAME STRIP  (t = 0, 0.25, 0.5, 0.75; the loop runs 2 volleys of 4 shots)", font=f_ui(20, b"Bold SemiCondensed"), fill=(255, 214, 64))
    for i, s in enumerate(strip):
        im.alpha_composite(s, (30 + i * (s.width + 16), sy + 34))
        d.text((40 + i * (s.width + 16), sy + 34 + s.height), "t = %.2f" % (i * 0.25), font=f_mono(12, False), fill=(170, 170, 182))
    gx = 30 + 4 * (strip[0].width + 16) + 20
    im.alpha_composite(g, (gx, sy + 34))
    d.text((gx + 10, sy + 34 + g.height), "greyscale (t = 0.25)", font=f_mono(12, False), fill=(170, 170, 182))
    out = bloom(im.convert("RGB"), 1, 0.3, 0.64)
    out = out.crop((0, 0, W, sy + 34 + strip[0].height + 30))
    out.save(os.path.join(OUT, "firewall_screen.png"))
    print("saved firewall_screen.png", out.size, flush=True)
    frames = []
    for f in range(24):
        tl = K.tile("FIREWALL", 5, t=f / 24, tier=2, scale=0.62)
        bg = Image.new("RGBA", tl.size, (11, 10, 16, 255))
        bg.alpha_composite(tl)
        frames.append(bg.convert("RGB"))
    pal = frames[12].quantize(colors=255, method=Image.MEDIANCUT)
    q = [fr.quantize(palette=pal, dither=Image.FLOYDSTEINBERG) for fr in frames]
    q[0].save(os.path.join(OUT, "firewall_fx.gif"), save_all=True, append_images=q[1:], duration=70, loop=0, optimize=True)
    print("saved firewall_fx.gif", os.path.getsize(os.path.join(OUT, "firewall_fx.gif")) / 1e6, "MB", flush=True)


if __name__ == "__main__":
    main()
