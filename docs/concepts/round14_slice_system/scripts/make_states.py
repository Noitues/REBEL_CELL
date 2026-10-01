"""Round 13 -> ../states.png (each overlay on 3 slice colours, hero + r = 60 + greyscale)
            -> ../states_fx.gif (each overlay's idle loop).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
CACHE = os.path.join(OUT, "scratch", "states")

from PIL import Image, ImageDraw, ImageOps
import slicekit as K
import overlays as O
import make_glyphs as MG
from slicelib import f_num, f_ui, f_mono, bloom

VAL = {"EXPLOIT": 6, "ZERO-DAY": 12, "FIREWALL": 5, "SANDBOX": 8, "PROXY": 4, "PATCH": 3, "VIRUS": 3, "TROJAN": 2, "NULL": None}
TRIOS = {
    "CORRUPTED": ("EXPLOIT", "FIREWALL", "PROXY"),
    "OVERCLOCKED": ("ZERO-DAY", "SANDBOX", "PATCH"),
    "ENCRYPTED": ("FIREWALL", "VIRUS", "EXPLOIT"),
    "PARASITE": ("TROJAN", "EXPLOIT", "PATCH"),
    "FROZEN": ("PROXY", "EXPLOIT", "VIRUS"),
    "LOCKED": ("SANDBOX", "ZERO-DAY", "PROXY"),
    "BURNING": ("EXPLOIT", "FIREWALL", "TROJAN"),
    "EMPOWERED": ("PATCH", "VIRUS", "FIREWALL"),
}
FILL = ["NULL", "SANDBOX", "PATCH", "TROJAN", "ZERO-DAY", "FIREWALL"]
TEXT = {
    "CORRUPTED": "hurts. full-slice glitch: bands of the whole slice tear sideways, pink + green split on outline + screen",
    "OVERCLOCKED": "helps, then hurts. round 13 look at 45 %: hot bezel, arcs, shimmer show the slice through; x1.5 chip",
    "ENCRYPTED": "helps. a field of * scrolling radially outward (up the wedge) behind the value; cyan rim",
    "PARASITE": "hurts. the tick itself latched on, large + translucent, pumping; hub side drained; x0.5 chip",
    "FROZEN": "kept from round 13: ice crust from the bezel, cold glass, cracks, glints",
    "LOCKED": "rows of padlocks scroll left -> right; screen dimmed, steel bezel",
    "BURNING": "kept from round 13 (procedural flames; the 2-peak shape is its badge mark)",
    "EMPOWERED": "HUGE translucent gold arrows rise outward behind the value; rim glow + halo",
}


def grey(im):
    a = im.split()[3]
    g = ImageOps.grayscale(im.convert("RGB")).convert("RGBA")
    g.putalpha(a)
    return g


def wheel_for(state):
    trio = TRIOS[state]
    sl = []
    fill = [p for p in FILL if p not in trio]
    for i in range(6):
        if i % 2 == 0:
            p = trio[i // 2]
            sl.append((p, VAL[p], 2, state))
        else:
            p = fill[i // 2]
            sl.append((p, VAL[p], 2, None))
    return sl


def render():
    os.makedirs(CACHE, exist_ok=True)
    for st in O.ORDER:
        for j, p in enumerate(TRIOS[st]):
            K.tile(p, VAL[p], t=0.3, tier=2, state=st, scale=0.46, seed=j + 4).save(os.path.join(CACHE, "%s_%d.png" % (st, j)))
        K.wheel(wheel_for(st), t=0.3, r_px=60).save(os.path.join(CACHE, "%s_w.png" % st))
        print(st, flush=True)


def compose():
    W, H = 2040, 1180
    im = Image.new("RGBA", (W, H), (11, 10, 16, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        d.line([(0, y), (W, y)], fill=(14, 13, 20))
    d.text((40, 18), "ROUND 14  SLICE STATE OVERLAYS", font=f_num(54), fill=(255, 255, 255))
    d.text((44, 80), "A separate layer over ANY slice, under the read block: the value is never covered (overlays thin to <= 35 % in the read window). "
           "Mark badge in the outer corner: circle helps, diamond hurts, notched = helps then hurts, square = neutral.", font=f_mono(14, False), fill=(190, 190, 200))
    bw, bh = 1000, 262
    for i, st in enumerate(O.ORDER):
        x0 = 30 + (i % 2) * (bw + 10)
        y0 = 118 + (i // 2) * bh
        gid, kind, bcol, real = O.STATE_INFO[st]
        d.rounded_rectangle([x0 - 8, y0 - 4, x0 + bw - 14, y0 + bh - 14], radius=10, outline=(50, 48, 66), width=1)
        b = MG.badge(gid, 34, bcol, kind)
        im.alpha_composite(b, (x0, y0 + 2))
        d.text((x0 + 42, y0), st, font=f_num(30), fill=bcol)
        tag = "STATUS (in game: rc.gd Status)" if real else "placeholder (not in game)"
        d.text((x0 + 42 + f_num(30).getlength(st) + 14, y0 + 12), tag, font=f_mono(12, False), fill=(150, 220, 150) if real else (255, 150, 90))
        d.text((x0, y0 + 40), TEXT[st], font=f_mono(12, False), fill=(185, 185, 198))
        tx = x0
        ty = y0 + 62
        tiles = [Image.open(os.path.join(CACHE, "%s_%d.png" % (st, j))) for j in range(3)]
        for t in tiles:
            im.alpha_composite(t, (tx - 8, ty))
            tx += t.width - 22
        w = Image.open(os.path.join(CACHE, "%s_w.png" % st))
        im.alpha_composite(w, (tx, ty + 20))
        d.text((tx + 34, ty + 20 + w.height - 2), "r = 60", font=f_mono(11, False), fill=(150, 150, 165))
        gx = tx + w.width + 6
        g = grey(tiles[0])
        g = g.resize((int(g.width * 0.75), int(g.height * 0.75)), Image.LANCZOS)
        im.alpha_composite(g, (gx, ty + 30))
        gw = grey(w)
        im.alpha_composite(gw, (gx + g.width + 4, ty + 20))
        d.text((gx + 10, ty + 32 + g.height), "greyscale", font=f_mono(11, False), fill=(150, 150, 165))
    out = bloom(im.convert("RGB"), 1, 0.28, 0.66)
    out.save(os.path.join(OUT, "states.png"))
    print("saved states.png", flush=True)


def gif(frames=24):
    cells = []
    for f in range(frames):
        t = f / frames
        row = []
        for j, st in enumerate(O.ORDER):
            p = TRIOS[st][0]
            row.append(K.tile(p, VAL[p], t=t, tier=2, state=st, scale=0.5, seed=4))
        cells.append(row)
        print("frame", f, flush=True)
    cw, ch = max(c.width for c in cells[0]), max(c.height for c in cells[0])
    W, H = 4 * (cw - 10) + 20, 2 * (ch + 24) + 10
    ims = []
    for f in range(frames):
        im = Image.new("RGBA", (W, H), (11, 10, 16, 255))
        d = ImageDraw.Draw(im)
        for j, st in enumerate(O.ORDER):
            x, y = 10 + (j % 4) * (cw - 10), 6 + (j // 4) * (ch + 24)
            im.alpha_composite(cells[f][j], (x - 4, y + 18))
            d.text((x + cw // 2 - 4, y + 2), st, font=f_ui(16, b"Bold SemiCondensed"), fill=O.STATE_INFO[st][2], anchor="mt")
        ims.append(im.convert("RGB"))
    pal = ims[len(ims) // 2].quantize(colors=255, method=Image.MEDIANCUT)
    q = [a.quantize(palette=pal, dither=Image.FLOYDSTEINBERG) for a in ims]
    q[0].save(os.path.join(OUT, "states_fx.gif"), save_all=True, append_images=q[1:], duration=70, loop=0, optimize=True)
    print("saved gif", os.path.getsize(os.path.join(OUT, "states_fx.gif")) / 1e6, "MB", flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("render", "all"):
        render()
    if what in ("compose", "all"):
        compose()
    if what in ("gif", "all"):
        gif()
