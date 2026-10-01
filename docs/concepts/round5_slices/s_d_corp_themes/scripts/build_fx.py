"""Builds shader_fx.gif (looping behaviours) and shader_fx_strip.png (frames over time)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import slicelib as sl
import themes as th

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMES = 24
PAD = 22

PROGS = [
    ("meridian", "ATTACK", 6, False, "MERIDIAN", "conveyor + scan"),
    ("solace", "HEAL", 6, False, "SOLACE", "divide + heartbeat"),
    ("halcyon", "DEFEND", 8, False, "HALCYON", "grid traffic"),
    ("orbital", "CRITICAL", 14, False, "ORBITAL", "satellite + glint"),
    ("rebel", "AFFLICT", 5, False, "REBEL_CELL", "horizontal tear"),
    ("halcyon", "ATTACK", 10, True, "HALCYON BOSS", "gilded counter-flow"),
]


def tile(theme, typ, val, t, rich, seed):
    box = sl.tile_box(3, pad=PAD)
    ctx = sl.Ctx(*box, half_deg=18, t=t, seed=seed, accent=sl.TYPES[typ][1], typ=typ, ticks=3)
    fn = th.THEMES[theme]["tex"]
    tex = (lambda c: fn(c, rich=True)) if rich else fn
    img, em = sl.render_tile(ctx, tex, val, {})
    return sl.add_glow(img, sl.emis_to_img(em), radii=((5, 0.8), (14, 0.5)))


def label(d, cx, y, a, b, col):
    f1, f2 = sl.font(20), sl.mono(13, False)
    for txt, f, c, dy in ((a, f1, col, 0), (b, f2, (190, 190, 200, 255), 24)):
        bb = f.getbbox(txt)
        d.text((cx - (bb[2] - bb[0]) / 2, y + dy), txt, font=f, fill=c)


def main():
    s = 0.62
    cw = 190
    frames = []
    strip_ts = [0.0, 0.17, 0.33, 0.5, 0.67, 0.83]
    strip_tiles = {}
    for fi in range(FRAMES):
        t = fi / FRAMES
        fr = Image.new("RGBA", (len(PROGS) * cw + 20, 250), (10, 9, 15, 255))
        d = ImageDraw.Draw(fr)
        for i, (theme, typ, val, rich, a, b) in enumerate(PROGS):
            img = tile(theme, typ, val, t, rich, seed=i + 1)
            img = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
            x = 10 + i * cw + (cw - img.width) // 2
            fr.alpha_composite(img, (x, 4))
            col = (255, 205, 110, 255) if rich else tuple(int(v * 255) for v in sl.hexrgb(th.THEMES[theme]["col"])) + (255,)
            label(d, 10 + i * cw + cw / 2, 194, a, b, col)
            for st in strip_ts:
                if abs(st - t) < 1e-6 or (fi == round(st * FRAMES) and (i, st) not in strip_tiles):
                    strip_tiles[(i, st)] = img
        frames.append(fr.convert("RGB"))
    pal = [f.quantize(colors=200, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
    p = os.path.join(OUT, "shader_fx.gif")
    pal[0].save(p, save_all=True, append_images=pal[1:], duration=90, loop=0, optimize=True, disposal=1)
    print("gif", os.path.getsize(p) / 1e6, "MB")
    # strip: rows = programs, cols = loop phase
    W, H = 1920, 1080
    strip = Image.new("RGBA", (W, H), (9, 8, 14, 255))
    d = ImageDraw.Draw(strip)
    d.text((24, 12), "SHADER BEHAVIOURS OVER ONE LOOP", font=sl.font(38), fill=(240, 240, 248, 255))
    rh = 160
    for j, st in enumerate(strip_ts):
        d.text((330 + j * 255 + 70, 62), "t = %.2f" % st, font=sl.mono(16, False), fill=(160, 160, 175, 255))
    for i, (theme, typ, val, rich, a, b) in enumerate(PROGS):
        y = 84 + i * rh
        col = (255, 205, 110, 255) if rich else tuple(int(v * 255) for v in sl.hexrgb(th.THEMES[theme]["col"])) + (255,)
        d.rectangle([0, y, 6, y + rh - 10], fill=col)
        d.text((22, y + 30), a, font=sl.font(26), fill=col)
        d.text((22, y + 64), sl.TYPES[typ][0] + "  -  " + b, font=sl.mono(15, False), fill=(200, 200, 210, 255))
        for j, st in enumerate(strip_ts):
            img = strip_tiles[(i, st)]
            sc = (rh - 6) / img.height
            im = img.resize((int(img.width * sc), int(img.height * sc)), Image.LANCZOS)
            strip.alpha_composite(im, (330 + j * 255 + (255 - im.width) // 2 - 20, y))
    strip.convert("RGB").save(os.path.join(OUT, "shader_fx_strip.png"))
    print("wrote strip")


if __name__ == "__main__":
    main()
