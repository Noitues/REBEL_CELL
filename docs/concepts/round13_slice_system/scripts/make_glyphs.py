"""Round 13 -> ../glyph_set.png : the full glyph pass at 64 / 24 / 16 px, colour + greyscale,
plus the 16 px confusion fixes (old vs new) measured with glyph_catalog.similarity.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)

from PIL import Image, ImageDraw, ImageOps
import slicelib as SL
import glyphs13 as G
import glyph_catalog as C
from slicelib import f_num, f_ui, f_mono

BG = (11, 10, 16)


def glyph(name, px):
    return SL.glyph_rgba(name, px, max(1.0, px * 0.075))


def picto(name, num, px):
    """Pictogram + its number (cards always show the amount beside the mark)."""
    if not num:
        return glyph(name, px)
    g = glyph(name, int(px * 0.80))
    n = SL.number_rgba(num, max(7, int(px * 0.62)), max(1, px * 0.06))
    W = max(px + 6, g.width + n.width // 2)
    H = max(px + 6, g.height)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im.alpha_composite(g, (0, 0))
    im.alpha_composite(n, (W - n.width, H - n.height))
    return im


def badge(name, px, col, kind):
    """Status mark: circle = helps, diamond = hurts, notched circle = mixed, dashed = predicted."""
    ss = 4
    S = px * ss
    m = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(m)
    w = max(2, int(S * 0.07))
    dark = (20, 16, 28, 255)
    if kind in ("hurt",):
        d.polygon([(S / 2, 1), (S - 1, S / 2), (S / 2, S - 1), (1, S / 2)], fill=dark, outline=col + (255,))
        d.line([(S / 2, 1), (S - 1, S / 2), (S / 2, S - 1), (1, S / 2), (S / 2, 1)], fill=col + (255,), width=w)
        gs = 0.50
    elif kind == "predicted":
        d.polygon([(S / 2, 1), (S - 1, S / 2), (S / 2, S - 1), (1, S / 2)], fill=(20, 16, 28, 150))
        pts = [(S / 2, 1), (S - 1, S / 2), (S / 2, S - 1), (1, S / 2), (S / 2, 1)]
        for i in range(4):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            for k in range(4):
                t0, t1 = k / 4 + 0.03, k / 4 + 0.16
                d.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)], fill=col + (255,), width=w)
        gs = 0.50
    elif kind == "neutral":
        d.rounded_rectangle([1, 1, S - 2, S - 2], radius=S * 0.18, fill=dark, outline=col + (255,), width=w)
        gs = 0.62
    else:
        d.ellipse([1, 1, S - 2, S - 2], fill=dark, outline=col + (255,), width=w)
        if kind == "mixed":  # notch: a hurt-diamond bite at the bottom = 'then it turns'
            d.polygon([(S / 2, S * 0.70), (S * 0.66, S * 0.86), (S / 2, S), (S * 0.34, S * 0.86)], fill=col + (255,))
        gs = 0.60
    m = m.resize((px, px), Image.LANCZOS)
    g = glyph(name, max(6, int(px * gs)))
    if kind == "predicted":
        a = g.split()[3].point(lambda v: int(v * 0.55))
        g.putalpha(a)
    m.alpha_composite(g, ((px - g.width) // 2, (px - g.height) // 2 - (1 if kind == "mixed" else 0)))
    return m


def tile(px, col, dashed=False):
    """The coloured plate a glyph sits on (a stand-in for the slice's dark screen)."""
    ss = 3
    S = px * ss
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fill = tuple(int(c * 0.30) for c in col) + (255,)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=S * 0.16, fill=fill)
    w = max(2, int(S * 0.035))
    if dashed:
        n = 10
        for i in range(n):
            t0, t1 = i / n, i / n + 0.55 / n
            for (a, b) in (((t0 * S, 0), (t1 * S, 0)), ((t0 * S, S - 1), (t1 * S, S - 1)), ((0, t0 * S), (0, t1 * S)), ((S - 1, t0 * S), (S - 1, t1 * S))):
                d.line([a, b], fill=col + (255,), width=w * 2)
    else:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=S * 0.16, outline=col + (255,), width=w)
    return im.resize((px, px), Image.LANCZOS)


def grey(im):
    a = im.split()[3]
    g = ImageOps.grayscale(im.convert("RGB")).convert("RGBA")
    g.putalpha(a)
    return g


def mark_at(item, px, kind_of_list):
    gid, label, meaning, col, kind = item if len(item) == 5 else (item[0], item[1], item[2], (230, 230, 240), "picto")
    if kind_of_list == "status":
        return badge(gid, px, col, kind)
    if kind_of_list == "state":
        return badge(gid, px, col, kind)
    on = tile(px, col, dashed=(kind == "placeholder"))
    g = glyph(gid, int(px * 0.78))
    on.alpha_composite(g, ((px - g.width) // 2, (px - g.height) // 2))
    return on


def picto_at(item, px):
    gid, label, meaning, num = item
    on = tile(px, (150, 150, 170))
    g = picto(gid, num, int(px * 0.78))
    if g.width > px or g.height > px:
        g = g.resize((min(px, g.width), min(px, g.height)), Image.LANCZOS)
    on.alpha_composite(g, ((px - g.width) // 2, (px - g.height) // 2))
    return on


CW, CH = 196, 138


def cell(im, d, x, y, label, meaning, col, maker, placeholder=False):
    big, mid, sml = maker(76), maker(30), maker(20)
    im.paste(big, (x, y + 42), big)
    im.paste(mid, (x + 84, y + 42), mid)
    im.paste(sml, (x + 84 + 36, y + 47), sml)
    gm, gs = grey(maker(30)), grey(maker(20))
    im.paste(gm, (x + 84, y + 84), gm)
    im.paste(gs, (x + 84 + 36, y + 89), gs)
    d.text((x + 146, y + 50), "24", font=f_mono(10, False), fill=(110, 110, 125))
    d.text((x + 146, y + 60), "16", font=f_mono(10, False), fill=(110, 110, 125))
    d.text((x + 146, y + 94), "grey", font=f_mono(10, False), fill=(110, 110, 125))
    d.text((x, y), label, font=f_ui(16, b"Bold SemiCondensed"), fill=col)
    import textwrap
    for k, ln in enumerate(textwrap.wrap(meaning, 30)[:2]):
        d.text((x, y + 19 + k * 11), ln, font=f_mono(10, False), fill=(170, 170, 182))
    if placeholder:
        d.text((x, y + 121), "placeholder (not in game)", font=f_mono(10, False), fill=(255, 150, 90))


def section(im, d, x, y, title, sub, col, w):
    d.rectangle([x - 14, y + 4, x - 8, y + 30], fill=col)
    d.text((x, y), title, font=f_num(30), fill=col)
    tw = f_num(30).getlength(title)
    d.text((x + tw + 16, y + 12), sub, font=f_mono(13, False), fill=(170, 170, 185))


def compose():
    W, H = 2400, 1640
    im = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        d.line([(0, y), (W, y)], fill=(14, 13, 20))
    d.text((40, 18), "ROUND 13  GLYPH SET", font=f_num(54), fill=(255, 255, 255))
    d.text((44, 80), "One flat language: a solid white silhouette, few dark cut-outs, dark rounded outline. Each glyph at 64 / 24 / 16 px, colour and greyscale. "
           "Names from rc.gd (SliceType, Status) and art_asset.md E2/E3/E5.", font=f_mono(15, False), fill=(190, 190, 200))
    x0, y = 40, 120
    cols = 12

    def grid(items, maker_for, y, placeholder_kinds=()):
        for i, it in enumerate(items):
            cx, cy = x0 + (i % cols) * CW, y + (i // cols) * CH
            label, meaning, col = it[1], it[2], it[3] if isinstance(it[3], tuple) else (235, 235, 245)
            cell(im, d, cx, cy, label, meaning, col, maker_for(it), placeholder=(len(it) == 5 and it[4] in placeholder_kinds))
        return y + ((len(items) + cols - 1) // cols) * CH

    section(im, d, x0, y, "SLICE TYPES + CORP SPECIALS", "9 programs = 9 SliceTypes; corp specials ride on top of a type; dashed tiles = placeholders (not in game)", (255, 214, 64), W)
    y += 42
    y = grid(C.PROGRAMS + C.SPECIALS[:3], lambda it: (lambda px, it=it: mark_at(it, px, "glyph")), y)
    y = grid(C.SPECIALS[3:] + C.PLACEHOLDERS, lambda it: (lambda px, it=it: mark_at(it, px, "glyph")), y, ("placeholder",))
    y += 6
    section(im, d, x0, y, "STATUSES + SLICE STATES", "circle = helps you  |  diamond = hurts  |  notched circle = helps then hurts  |  dashed = predicted  |  square = neutral", (255, 77, 77), W)
    y += 42
    st_items = C.STATUSES + C.STATES
    for i, it in enumerate(st_items):
        cx, cy = x0 + (i % cols) * CW, y
        is_state = it in C.STATES
        cell(im, d, cx, cy, it[1], it[2], it[3], (lambda px, it=it: badge(it[0], px, it[3], it[4])), placeholder=is_state)
    y += CH + 6
    section(im, d, x0, y, "CARD PICTOGRAMS", "the row of marks on a card (art_asset E5); amounts sit bottom-right of the mark", (200, 200, 220), W)
    y += 42
    for i, it in enumerate(C.PICTOS):
        cx, cy = x0 + (i % cols) * CW, y + (i // cols) * CH
        cell(im, d, cx, cy, it[1], it[2], (225, 225, 238), (lambda px, it=it: picto_at(it, px)))
    y += ((len(C.PICTOS) + cols - 1) // cols) * CH
    # fill the free slots of the last pictogram row with the confusion panel header space
    # ---------------- confusion fixes
    y += 4
    section(im, d, x0, y, "16 px CONFUSIONS FIXED", "soft-IoU of the 16 px coverage maps (1.0 = same blob); old shape left, new right", (123, 224, 123), W)
    y += 44
    fx = x0
    for old, partner, why, fix in C.FIXES:
        new_s = C.similarity(C.m16(old), C.m16(partner))
        G.BYPASS.add(old)
        SL._glyph_cache.clear()
        o_big, o_sm = glyph(old, 56), glyph(old, 16)
        old_s = C.similarity(C.m16(old), C.m16(partner))
        G.BYPASS.discard(old)
        SL._glyph_cache.clear()
        n_big, n_sm = glyph(old, 56), glyph(old, 16)
        p_big, p_sm = glyph(partner, 56), glyph(partner, 16)
        bw = 560
        d.rounded_rectangle([fx - 8, y - 6, fx + bw - 24, y + 150], radius=10, outline=(60, 60, 80), width=1)
        for k, (a, b, s, tag, colr) in enumerate(((o_big, o_sm, old_s, "BEFORE", (255, 110, 110)), (n_big, n_sm, new_s, "AFTER", (123, 224, 123)))):
            bx = fx + k * 262
            d.text((bx, y), "%s  %.2f" % (tag, s), font=f_ui(15, b"Bold SemiCondensed"), fill=colr)
            im.paste(a, (bx, y + 22), a)
            im.paste(p_big, (bx + 76, y + 22), p_big)
            for j, g in enumerate((b, p_sm)):
                t = tile(22, (120, 120, 140))
                t.alpha_composite(g, ((22 - g.width) // 2, (22 - g.height) // 2))
                im.paste(t, (bx + 160 + j * 28, y + 40), t)
            d.text((bx + 160, y + 66), "16 px", font=f_mono(10, False), fill=(120, 120, 135))
            if k == 0:
                d.text((bx + 222, y + 50), "->", font=f_num(28), fill=(200, 200, 210))
        d.text((fx, y + 104), why, font=f_mono(11, False), fill=(200, 170, 170))
        d.text((fx, y + 122), "fix: " + fix, font=f_mono(11, False), fill=(170, 220, 170))
        fx += bw
    y += 166
    d.text((x0, y), "Kept alike on purpose: SPIN CW / CCW (mirror pair, the arrowhead side + the card text differ), BURN = BURNING mark, ENCRYPT = ENCRYPTED mark "
           "(the program applies the status), HP / TAKE DMG (same heart, cracked).  Caught while drafting: RAM stick vs ENCRYPT pill -> chip;  INERTIA kettlebell vs LOCKED padlock -> anvil.",
           font=f_mono(12, False), fill=(185, 185, 198))
    im = im.crop((0, 0, W, y + 42)).convert("RGB")
    im.save(os.path.join(OUT, "glyph_set.png"))
    print("saved glyph_set.png", im.size, flush=True)


if __name__ == "__main__":
    compose()
