"""Round 14 -> ../glyph_changes.png : every changed glyph, old (round 13) -> new, with the options asked
for. Each option shows 64 px + 16 px and its nearest 16 px twin in the whole set (soft IoU)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)

from PIL import Image, ImageDraw, ImageFilter
import slicelib as SL
import glyphs15 as G
import glyph_catalog as C
from make_glyphs import tile, grey
from slicelib import f_num, f_ui, f_mono


def rgba_from_mask(m, px):
    """Same look as slicelib.glyph_rgba, from a raw 512 mask."""
    outline_px = max(1.0, px * 0.075)
    pad = int(outline_px * 2 + 4)
    mm = m.resize((px, px), Image.LANCZOS)
    big = Image.new("L", (px + 2 * pad, px + 2 * pad), 0)
    big.paste(mm, (pad, pad))
    o = big.filter(ImageFilter.GaussianBlur(outline_px * 0.55)).point(lambda v: min(255, v * 7))
    out = Image.new("RGBA", big.size, (12, 10, 22, 0))
    out.putalpha(o)
    out.paste(Image.new("RGBA", big.size, (255, 255, 255, 255)), (0, 0), big)
    return out


def on_tile(g, sz, col):
    t = tile(sz, col)
    t.alpha_composite(g, ((sz - g.width) // 2, (sz - g.height) // 2))
    return t


def chosen(opt):
    base = opt.split("@")[0]
    if "@" not in opt:
        return True
    return G.CHOICE.get(base) == opt


def main():
    ids = C.all_ids()
    W, H = 2460, 860
    im = Image.new("RGBA", (W, H), (11, 10, 16, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        d.line([(0, y), (W, y)], fill=(14, 13, 20))
    d.text((40, 18), "ROUND 15  GLYPH CHANGES  old (round 14 pick) -> new", font=f_num(54), fill=(255, 255, 255))
    d.text((44, 80), "Each option at 64 px and 16 px; 'twin' = the most alike glyph in the whole round 15 set at 16 px (soft IoU, lower is better; "
           "under 0.62 is clear).  Gold frame = chosen for glyph_set.png.", font=f_mono(14, False), fill=(190, 190, 200))
    col_w, row_h = 1215, 120
    for i, (label, ref, opts, note) in enumerate(C.CHANGES):
        x0 = 30 + (i // 6) * (col_w + 10)
        y0 = 120 + (i % 6) * row_h
        d.rounded_rectangle([x0 - 6, y0 - 4, x0 + col_w - 10, y0 + row_h - 10], radius=8, outline=(50, 48, 66), width=1)
        d.text((x0, y0), label, font=f_ui(17, b"Bold SemiCondensed"), fill=(255, 214, 64))
        d.text((x0, y0 + 22), note, font=f_mono(11, False), fill=(175, 175, 190))
        ox = x0 + 4
        if ref is not None:
            om = C.old_mask(ref)
            gb, gs = rgba_from_mask(om, 56), rgba_from_mask(om, 16)
            im.alpha_composite(on_tile(gb, 64, (110, 90, 90)), (ox, y0 + 40))
            im.alpha_composite(on_tile(gs, 22, (110, 90, 90)), (ox + 70, y0 + 60))
            d.text((ox, y0 + 40 + 62), "old (r14)", font=f_mono(10, False), fill=(200, 140, 140))
        else:
            d.text((ox + 6, y0 + 66), "new", font=f_ui(18, b"Bold SemiCondensed"), fill=(170, 170, 185))
        d.text((x0 + 108, y0 + 58), "->", font=f_num(30), fill=(200, 200, 210))
        bx = x0 + 150
        for k, o in enumerate(opts):
            ox = bx + 205 + k * 215 if k or True else bx
            ox = x0 + 150 + k * 262
            if "#" in o:  # a dynamic pictogram state
                from make_glyphs import picto
                nm, num = o.split("#")
                gb, gs = picto(nm, num, 60), picto(nm, num, 22)
                small_name = nm
            else:
                m = SL.glyph_mask(o)
                gb = rgba_from_mask(m, 56)
                small_name = G.SMALL.get(o, o)
                gs = rgba_from_mask(SL.glyph_mask(small_name), 16)
            ch = chosen(o) or (o == "ST_CLEANSE@S")
            if ch:
                d.rounded_rectangle([ox - 4, y0 + 34, ox + 250, y0 + 108], radius=8, outline=(255, 200, 70), width=2)
            im.alpha_composite(on_tile(gb, 64, (90, 100, 130)), (ox, y0 + 40))
            im.alpha_composite(on_tile(gs, 22, (90, 100, 130)), (ox + 70, y0 + 40))
            im.alpha_composite(on_tile(grey(gs), 22, (90, 90, 90)), (ox + 70, y0 + 66))
            tag = o.split("@")[1] if "@" in o else ""
            if "#" in o:
                tag = "no spin yet" if o.endswith("^2/5") else "after a spin"
            d.text((ox + 98, y0 + 40), ("option " + tag) if tag else "new", font=f_ui(14, b"Bold SemiCondensed"), fill=(255, 214, 64) if ch else (210, 210, 220))
            base = o.split("@")[0].split("#")[0]
            ex = {base, o}
            if base in ("BURN", "ST_BURNING"):
                ex |= {"BURN", "ST_BURNING"}
            if base == "PI_MOMENTUM":
                ex |= {"PI_SPIN_CW"}
            sc, tw = C.nearest(C.cov(SL.glyph_mask(small_name)), ids, exclude=ex)
            colr = (255, 140, 110) if sc > 0.68 else ((255, 214, 120) if sc > 0.62 else (150, 225, 150))
            d.text((ox + 98, y0 + 60), "twin %.2f" % sc, font=f_ui(14, b"Bold SemiCondensed"), fill=colr)
            d.text((ox + 98, y0 + 80), tw.replace("PI_", "").replace("ST_", "")[:16], font=f_mono(10, False), fill=(165, 165, 180))
    im.convert("RGB").save(os.path.join(OUT, "glyph_changes.png"))
    print("saved glyph_changes.png", flush=True)


if __name__ == "__main__":
    main()
