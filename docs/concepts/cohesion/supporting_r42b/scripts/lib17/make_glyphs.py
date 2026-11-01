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
import glyphs17 as G
import glyph_catalog as C
from slicelib import f_num, f_ui, f_mono

BG = (11, 10, 16)


def glyph(name, px):
    """The glyph as shown at px (CHOICE applied; reduced forms at <= 24 px)."""
    return SL.glyph_rgba(G.resolve(name, px), px, max(1.0, px * 0.075))


def picto(name, num, px):
    """Pictogram + its number (cards always show the amount beside the mark)."""
    if not num:
        return glyph(name, px)
    if "/" in num:  # dynamic pair: "^2/5" = big 2 (runs now), small 5; fitted inside a px box
        g = glyph(name, int(px * 0.74))
        parts = []
        for k, p in enumerate(num.split("/")):
            big = p.startswith("^")
            parts.append(SL.number_rgba(p.lstrip("^"), max(7, int(px * (0.62 if big else 0.34))), max(1, px * 0.05),
                                        fill=(255, 255, 255) if big else (170, 170, 186)))
            if k == 0:
                parts.append(SL.number_rgba("/", max(7, int(px * 0.40)), max(1, px * 0.05), fill=(170, 170, 186)))
        nw = sum(q.width for q in parts)
        nh = max(q.height for q in parts)
        grp = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
        x = 0
        for q in parts:
            grp.alpha_composite(q, (x, nh - q.height))
            x += q.width
        lim = int(px * 0.80)
        if grp.width > lim:
            grp = grp.resize((lim, max(1, int(grp.height * lim / grp.width))), Image.LANCZOS)
        S2 = px + 6
        im = Image.new("RGBA", (S2, S2), (0, 0, 0, 0))
        im.alpha_composite(g, (0, 0))
        im.alpha_composite(grp, (S2 - grp.width, S2 - grp.height))
        return im
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


def cell(im, d, x, y, label, meaning, col, maker, tag=None):
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
    if tag:
        d.text((x, y + 121), tag, font=f_mono(10, False), fill=(255, 150, 90) if tag.startswith("placeholder") else (255, 214, 64))


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
    d.text((40, 18), "ROUND 17  FINAL GLYPH SET", font=f_num(54), fill=(255, 255, 255))
    d.text((44, 80), "One flat language: a solid white silhouette, few dark cut-outs, dark rounded outline. Each glyph at 64 / 24 / 16 px, colour and greyscale. "
           "Names from rc.gd (SliceType, Status) and art_asset.md E2/E3/E5.", font=f_mono(15, False), fill=(190, 190, 200))
    x0, y = 40, 120
    cols = 12

    def grid(items, maker_for, y, placeholder_kinds=()):
        for i, it in enumerate(items):
            cx, cy = x0 + (i % cols) * CW, y + (i // cols) * CH
            label, meaning, col = it[1], it[2], it[3] if isinstance(it[3], tuple) else (235, 235, 245)
            kind = it[4] if len(it) == 5 else None
            tag = {"placeholder": "placeholder (not in game)", "renamed": "renamed (game name change pending)"}.get(kind)
            cell(im, d, cx, cy, label, meaning, col, maker_for(it), tag=tag)
        return y + ((len(items) + cols - 1) // cols) * CH

    section(im, d, x0, y, "SLICE TYPES + CORP SPECIALS", "9 programs = 9 SliceTypes; corp specials ride on top of a type; dashed tiles = placeholders (not in game)", (255, 214, 64), W)
    y += 42
    y = grid(C.PROGRAMS + C.SPECIALS + C.PLACEHOLDERS, lambda it: (lambda px, it=it: mark_at(it, px, "glyph")), y)
    y += 6
    section(im, d, x0, y, "STATUSES + SLICE STATES", "circle = helps you  |  diamond = hurts  |  notched circle = helps then hurts  |  dashed = predicted  |  square = neutral", (255, 77, 77), W)
    y += 42
    st_items = C.STATUSES + C.STATES
    for i, it in enumerate(st_items):
        cx, cy = x0 + (i % cols) * CW, y
        is_state = it in C.STATES
        cell(im, d, cx, cy, it[1], it[2], it[3], (lambda px, it=it: badge(it[0], px, it[3], it[4])), tag="placeholder (not in game)" if is_state else None)
    y += CH + 6
    section(im, d, x0, y, "CARD PICTOGRAMS", "the row of marks on a card (art_asset E5); amounts sit bottom-right of the mark", (200, 200, 220), W)
    y += 42
    for i, it in enumerate(C.PICTOS):
        cx, cy = x0 + (i % cols) * CW, y + (i // cols) * CH
        cell(im, d, cx, cy, it[1], it[2], (225, 225, 238), (lambda px, it=it: picto_at(it, px)))
    y += ((len(C.PICTOS) + cols - 1) // cols) * CH
    # ---------------- 16 px confusion scoring over the whole set
    y += 4
    section(im, d, x0, y, "16 px CONFUSION SCORE  (whole set)", "soft-IoU of the 16 px coverage maps, 1.0 = same blob; the 12 closest pairs (round 13 worst was 0.71)", (123, 224, 123), W)
    y += 44
    pairs = C.top_pairs(C.all_ids(), 12)
    for i, (sc, a, b) in enumerate(pairs):
        px_, py_ = x0 + (i % 6) * 390, y + (i // 6) * 64
        d.rounded_rectangle([px_ - 6, py_ - 4, px_ + 372, py_ + 56], radius=8, outline=(55, 55, 72), width=1)
        for j, n in enumerate((a, b)):
            for k, sz in enumerate((24, 16)):
                t = tile(sz + 6, (120, 120, 140))
                g = glyph(n, sz)
                t.alpha_composite(g, ((t.width - g.width) // 2, (t.height - g.height) // 2))
                im.paste(t, (px_ + j * 74 + k * 34, py_ + 4 + (24 - sz) // 2), t)
        colr = (255, 150, 110) if sc > 0.68 else (200, 220, 160)
        d.text((px_ + 156, py_ + 2), "%.2f" % sc, font=f_num(26), fill=colr)
        d.text((px_ + 216, py_ + 6), "%s" % a.replace("PI_", "").replace("ST_", ""), font=f_mono(11, False), fill=(190, 190, 205))
        d.text((px_ + 216, py_ + 24), "%s" % b.replace("PI_", "").replace("ST_", ""), font=f_mono(11, False), fill=(190, 190, 205))
    y += 2 * 64 + 6
    d.text((x0, y), "Kept alike on purpose (not scored): SPIN CW / CCW mirror pair, MOMENTUM = the SPIN arrow (numbers differ), BURN = BURNING, ENCRYPT = ENCRYPTED, HP / TAKE DMG.  "
           "Changes and options: glyph_changes.png.", font=f_mono(12, False), fill=(185, 185, 198))
    im = im.crop((0, 0, W, y + 42)).convert("RGB")
    im.save(os.path.join(OUT, "glyph_set.png"))
    print("saved glyph_set.png", im.size, flush=True)


if __name__ == "__main__":
    compose()
