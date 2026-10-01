"""Task 1: VIRUS / PROXY rework sheet -> ../slices_rework.png (1920 x 1080).

Rows: VIRUS (top), PROXY (bottom). Columns: round 6 (old), options A, B, C.
Each column: hero tile (60-degree, upright value block), r = 60 wheel (small LOD variant) in colour
and greyscale, and the hero tile in greyscale.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
CACHE = os.path.join(OUT, "scratch", "rework")

from PIL import Image, ImageDraw, ImageOps
import numpy as np
from slicelib import render_tile_image, f_num, f_ui, f_mono, bloom, PROGRAMS, R_OUT
import screens10 as S10
import combat_specs as CS
import combat_wheel as CWL

OPTS = ["OLD", "A", "B", "C"]
REC = {"VIRUS": "A", "PROXY": "A"}
DESC = {
    ("VIRUS", "OLD"): ("ROUND 6", "spiked capsid, toned cells"),
    ("VIRUS", "A"): ("A  POISON VIAL", "blotches eat a hex dump, drips run"),
    ("VIRUS", "B"): ("B  SKULL DROP", "ooze slides from the rim, pools"),
    ("VIRUS", "C"): ("C  BIOHAZARD", "round 6 toned cells kept"),
    ("PROXY", "OLD"): ("ROUND 6", "double chevron, bold reroute"),
    ("PROXY", "A"): ("A  MASK + GHOST TRAIL", "route hops, afterimages step aside"),
    ("PROXY", "B"): ("B  DODGE ARROW", "packet sidesteps a trace lock"),
    ("PROXY", "C"): ("C  MASK + RELAY HOPS", "onion hops, tracker left behind"),
}
VAL = {"VIRUS": 3, "PROXY": 4}


def grey(im):
    a = im.split()[3]
    g = ImageOps.grayscale(im.convert("RGB")).convert("RGBA")
    g.putalpha(a)
    return g


def render_assets():
    os.makedirs(CACHE, exist_ok=True)
    for prog in ("VIRUS", "PROXY"):
        for opt in OPTS:
            kw = {"virus": REC["VIRUS"], "proxy": REC["PROXY"]}
            kw[prog.lower()] = opt
            S10.select(**kw)
            tile = render_tile_image(prog, 60, VAL[prog], 0.55, ss=2, opts=dict(upright=True), scale=0.78, seed=3)
            tile.save(os.path.join(CACHE, "tile_%s_%s.png" % (prog, opt)))
            spec, _ = CS.player(41)
            spec["hp_number"] = False
            w, _c = CWL.render(spec, ss=2, lod=True)
            w = w.crop(w.getbbox())
            k = 60 / R_OUT
            w = w.resize((int(w.width * k), int(w.height * k)), Image.LANCZOS)
            w.save(os.path.join(CACHE, "small_%s_%s.png" % (prog, opt)))
            print(prog, opt, flush=True)


def compose():
    W, H = 1920, 1080
    im = Image.new("RGB", (W, H), (11, 10, 16))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 4):  # faint scanline texture
        d.line([(0, y), (W, y)], fill=(14, 13, 20))
    d.text((40, 22), "VIRUS + PROXY REWORK", font=f_num(54), fill=(255, 255, 255))
    d.text((44, 86), "round 10  |  Screens & Data (C) slice language  |  hero tile, r = 60 wheel (colour + greyscale), hero greyscale",
           font=f_mono(17, False), fill=(190, 190, 200))
    cw = 318
    for r, prog in enumerate(("VIRUS", "PROXY")):
        y0 = 130 + r * 470
        col = PROGRAMS[prog]["col"]
        d.rectangle([0, y0, 8, y0 + 440], fill=col)
        d.text((26, y0 - 4), prog, font=f_num(40), fill=col)
        d.text((26 + f_num(40).getlength(prog) + 14, y0 + 12),
               "AFFLICT  |  poison  |  violet #C85AFF" if prog == "VIRUS" else "EVADE  |  slip the trace  |  green #7BE07B",
               font=f_ui(19, b"Bold SemiCondensed"), fill=(220, 220, 230))
        for c, opt in enumerate(OPTS):
            x0 = 30 + c * cw
            tile = Image.open(os.path.join(CACHE, "tile_%s_%s.png" % (prog, opt)))
            ty = y0 + 52
            if REC[prog] == opt:
                d.rounded_rectangle([x0 - 6, ty - 8, x0 + tile.width + 6, y0 + 436], radius=10, outline=(255, 214, 64), width=3)
                d.text((x0 + tile.width - 120, ty - 6), "RECOMMENDED", font=f_ui(16, b"Bold SemiCondensed"), fill=(255, 214, 64))
            im.paste(tile, (x0, ty), tile)
            t1, t2 = DESC[(prog, opt)]
            d.text((x0 + 4, ty + tile.height + 2), t1, font=f_ui(19, b"Bold SemiCondensed"), fill=col if opt != "OLD" else (170, 170, 180))
            d.text((x0 + 4, ty + tile.height + 26), t2, font=f_mono(14, False), fill=(185, 185, 195))
            sm = Image.open(os.path.join(CACHE, "small_%s_%s.png" % (prog, opt)))
            sy = ty + tile.height + 50
            im.paste(sm, (x0, sy), sm)
            gs = grey(sm)
            im.paste(gs, (x0 + sm.width + 4, sy), gs)


        # legend under the first column
    # right panel
    x = 1310
    d.rectangle([x - 20, 130, W - 30, 1040], fill=(16, 15, 22), outline=(40, 38, 50))
    fh, fb = f_ui(21, b"Bold SemiCondensed"), f_mono(15, False)
    y = 148
    lines = [
        ("RECOMMENDED: VIRUS A", (200, 90, 255)),
        ("Poison vial: a silhouette nothing else on the", None),
        ("wheel shares (ZERO-DAY owns the skull, so the", None),
        ("skull-drop B competes with it at r = 60).", None),
        ("Screen: violet blotches eat a scrolling hex dump;", None),
        ("brightest pixel 0.5 of violet, so it sits", None),
        ("level with EXPLOIT / FIREWALL, not above.", None),
        ("", None),
        ("RECOMMENDED: PROXY A", (123, 224, 123)),
        ("Guy Fawkes-style mask: moustache, smile and", None),
        ("goatee survive down to ~24 px; it says 'anonymous", None),
        ("/ masked' where the chevrons said 'fast forward'.", None),
        ("Screen keeps round 6's bold reroute and adds the", None),
        ("dodge: the route and packet leave 3 afterimages", None),
        ("stepped sideways. B's dodge arrow is the fallback", None),
        ("if a face icon is unwanted; it blurs below r = 60.", None),
        ("", None),
        ("RULES KEPT", (255, 214, 64)),
        ("Frame, bezel, LED, scanlines, read plate: C.", None),
        ("Glyph + value block stays upright as the wheel", None),
        ("spins (new): no 6/9 confusion at the bottom.", None),
        ("Greyscale: each glyph is a unique silhouette.", None),
    ]
    for t, c in lines:
        if c:
            d.text((x, y), t, font=fh, fill=c)
            y += 30
        else:
            d.text((x, y), t, font=fb, fill=(200, 200, 210))
            y += 21
    # greyscale row: all eight hero tiles
    d.text((x, 690), "GREYSCALE  (hero tiles: old, A, B, C)", font=fh, fill=(220, 220, 230))
    for r, prog in enumerate(("VIRUS", "PROXY")):
        for c, opt in enumerate(OPTS):
            tile = grey(Image.open(os.path.join(CACHE, "tile_%s_%s.png" % (prog, opt))))
            tile = tile.resize((int(tile.width * 0.46), int(tile.height * 0.46)), Image.LANCZOS)
            im.paste(tile, (x - 8 + c * 146, 730 + r * 150), tile)
            d.text((x - 8 + c * 146 + 50, 730 + r * 150 + tile.height - 2), ("old" if opt == "OLD" else opt) + (" *" if REC[prog] == opt else ""),
                   font=f_mono(14, False), fill=(170, 170, 180))
    d.text((30, 1046), "small wheel = Breaker mock with VIRUS in slot 2 and PROXY in slot 5 (other row's slice at its recommended option)",
           font=f_mono(14, False), fill=(150, 150, 160))
    im = bloom(im, 1, 0.35, 0.62)
    im.save(os.path.join(OUT, "slices_rework.png"))


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("render", "all"):
        render_assets()
    if what in ("compose", "all"):
        compose()
    print("done")

