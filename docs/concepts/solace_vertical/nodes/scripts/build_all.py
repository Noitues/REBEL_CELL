"""Builds every deliverable of the REST / WORKSHOP / CACHE concept round.

  python build_all.py            writes to D:/rc_art/art-pass/docs/concepts/solace_vertical/nodes/
Needs only Pillow and numpy (no Blender, no GPU). The icons are Doc shape lists (vec.py): one source renders to SVG and to PNG.
"""
import os
import sys
import shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pages import *
from cache_page import cache_page
from common import LEGEND_X
import icons

DEST = "D:/rc_art/art-pass/docs/concepts/solace_vertical/nodes/"
DIRS = {"A": ("KIT", "the family as shipped: round die-cut, dark tinted field, cream pictogram"),
        "B": ("CUTOUT", "the die-cut is the object: pod, cog, ammo can; same field + pictogram family"),
        "C": ("SLAP-TAG", "no field: a saturated glyph with a white contour die-cut (house, wrench, bricks)")}
CAP = {"A": "event-page layout; kind-coloured CRT window; choice stickers; the icon stamped beside the title",
       "B": "the street kit's room is the backdrop; rows as pods / tool-roll pockets; the die-cut as the room's sign",
       "C": "compact terminal; the contour sticker is the hero; orange pencil plan (what CONFIRM / BUY would do)"}


def mk(p):
    os.makedirs(p, exist_ok=True)


def label(img, xy, s, f, col=(235, 240, 250)):
    ImageDraw.Draw(img).text(xy, s, font=f, fill=col)


def icons_x(dr):
    legend(dr, 1.0)
    return LEGEND_X['rest']


def main():
    for sub in ("icons", "pages", "cache", "map", "legend", "scripts"):
        mk(DEST + sub)
    # ---- icons: SVG + PNG ------------------------------------------------------------------------------------------
    for dr in "ABC":
        for k in icons.KINDS:
            doc = icons.make(dr, k)
            open(DEST + "icons/%s_%s.svg" % (dr, k), "w").write(doc.svg())
            doc.render(scale=512 / 130.0, ss=3).save(DEST + "icons/%s_%s_512.png" % (dr, k))
            doc.render(scale=1.0, ss=6).save(DEST + "icons/%s_%s_130.png" % (dr, k))
    # ---- pages -----------------------------------------------------------------------------------------------------
    pg = {}
    for dr in "ABC":
        for k in ("rest", "workshop"):
            im = page(dr, k)
            im.save(DEST + "pages/%s_%s_page.png" % (dr, k))
            pg[(dr, k)] = im
        cp = cache_page(dr)
        cp.save(DEST + "cache/%s_cache_loot.png" % dr)
        pg[(dr, "cache")] = cp
    # ---- map, squint, blur, legend ----------------------------------------------------------------------------------
    maps, legs, blur = {}, {}, {}
    for dr in "ABC":
        m = build_map(dr)
        m.save(DEST + "map/%s_map.png" % dr)
        sq = squint(m, 320)
        sq.save(DEST + "map/%s_squint_320.png" % dr)
        sq.convert("L").save(DEST + "map/%s_squint_320_grey.png" % dr)
        bs = blur_strip(m, (0, 380, 1920, 900), 4)
        bs.save(DEST + "map/%s_blur4_strip.png" % dr)
        crop = m.crop((590, 490, 1130, 830)).filter(ImageFilter.GaussianBlur(4))
        maps[dr], blur[dr] = (m, sq), crop
        lg = legend(dr, 1.0)
        lg.save(DEST + "legend/%s_legend_1x.png" % dr)
        legend(dr, 2.0).save(DEST + "legend/%s_legend_2x.png" % dr)
        legs[dr] = lg
    # the map at 2x of the icon (a 4K-ish read): the sticker rows only
    # ---- icon sheet (big) -------------------------------------------------------------------------------------------
    ex = ["fight", "elite", "event", "shop", "rack"]
    IS = Image.new("RGB", (3 * 300 + 5 * 120 + 80, 3 * 330 + 120), (36, 40, 52))
    for r, dr in enumerate("ABC"):
        y = 90 + r * 330
        label(IS, (20, y - 30), "%s  %s" % (dr, DIRS[dr][0]), anton(34))
        for c, k in enumerate(icons.KINDS):
            im = icons.make(dr, k).render(scale=2.3, ss=3)
            IS.paste(im, (20 + c * 300, y + 10), im)
        for c, k in enumerate(ex):
            im = shipped(k).resize((110, int(110 * shipped(k).height / shipped(k).width)), Image.LANCZOS)
            IS.paste(im, (20 + 3 * 300 + 30 + c * 120, y + 100), im)
    label(IS, (20 + 3 * 300 + 30, 56), "SHIPPED FAMILY (for reference, 110 px)", mono(18))
    IS.save(DEST + "icon_sheet.jpg", quality=92)

    # ---- the sheet --------------------------------------------------------------------------------------------------
    W = 2560
    ROW = 560
    HEAD = 96
    BAND = 520
    SH = Image.new("RGB", (W, HEAD + 3 * ROW + BAND + 20), (22, 26, 36))
    d = ImageDraw.Draw(SH)
    d.text((20, 14), "NODES  //  REST / WORKSHOP / CACHE  -  concept round, three directions (art-pass, Solace list item 4, B-058)", font=anton(34), fill=(246, 243, 232))
    d.text((20, 58), "rows A / B / C   |   media: node icons = vinyl sticker, node pages = CRT terminal (ART_BIBLE 1.2)   |   map icon px measured: die-cut 41.6 px at 1080p (radius_px 26 x k)   |   legend swatch 16.8 px",
           font=mono(17), fill=(160, 178, 200))
    cols = [20, 380, 936, 1720, 2180]
    heads = ["ICONS  2x / 1x map size / legend size", "SQUINT  320 px wide  +  4 px blur at 1:1", "REST PAGE  1920x1080", "WORKSHOP PAGE  1920x1080", ""]
    for x, h in zip(cols, heads):
        d.text((x, HEAD - 22), h, font=mono(15), fill=(120, 200, 230))
    for r, dr in enumerate("ABC"):
        y0 = HEAD + r * ROW
        d.line((20, y0 - 4, W - 20, y0 - 4), fill=(60, 70, 90), width=2)
        # c1: icons
        d.text((cols[0], y0 + 4), "%s  %s" % (dr, DIRS[dr][0]), font=anton(40), fill=(255, 226, 0))
        # description wrapped
        words = DIRS[dr][1].split()
        line, yy = "", y0 + 56
        for w_ in words:
            if tw(line + " " + w_, mono(14)) > 330:
                d.text((cols[0], yy), line, font=mono(14), fill=(190, 200, 215))
                yy += 17
                line = w_
            else:
                line = (line + " " + w_).strip()
        d.text((cols[0], yy), line, font=mono(14), fill=(190, 200, 215))
        for c, k in enumerate(icons.KINDS):
            cx = cols[0] + 50 + c * 112
            im2 = icons.make(dr, k).render(scale=84 / 130.0, ss=5)
            SH.paste(im2, (int(cx - 42), y0 + 128), im2)
            im1 = icons.make(dr, k).render(scale=42 / 130.0, ss=6)
            SH.paste(im1, (int(cx - 21), y0 + 228), im1)
            im17 = icons.make(dr, k).render(scale=17 / 130.0, ss=8)
            SH.paste(im17, (int(cx - 8), y0 + 284), im17)
            d.text((cx, y0 + 318), k.upper(), font=mono(13), fill=(190, 200, 215), anchor="mm")
        d.text((cols[0], y0 + 340), "the family at map size (42 px art):", font=mono(13), fill=(150, 165, 185))
        fx = cols[0]
        for k in ex + list(icons.KINDS):
            if k in icons.KINDS:
                im = icons.make(dr, k).render(scale=40 / 130.0, ss=6)
            else:
                a = shipped(k)
                im = a.resize((40, int(40 * a.height / a.width)), Image.LANCZOS)
            SH.paste(im, (fx, y0 + 362), im)
            fx += 42
        d.text((cols[0], y0 + 410), "greyscale (shape-only) family:", font=mono(13), fill=(150, 165, 185))
        fx = cols[0]
        for k in ex + list(icons.KINDS):
            if k in icons.KINDS:
                im = icons.make(dr, k).render(scale=40 / 130.0, ss=6)
            else:
                a = shipped(k)
                im = a.resize((40, int(40 * a.height / a.width)), Image.LANCZOS)
            g = Image.new("RGBA", im.size, (22, 26, 36, 255))
            g.alpha_composite(im)
            g = g.convert("L").convert("RGB")
            SH.paste(g, (fx, y0 + 432))
            fx += 42
        # c2: squint + blur
        m, sq = maps[dr]
        SH.paste(sq, (cols[1], y0 + 4))
        SH.paste(sq.convert("L").convert("RGB").resize((200, 112)), (cols[1] + 330, y0 + 4))
        d.text((cols[1] + 330, y0 + 120), "greyscale squint", font=mono(12), fill=(150, 165, 185))
        SH.paste(blur[dr], (cols[1], y0 + 186))
        d.text((cols[1], y0 + 530), "4 px blur, 1:1 crop (REST / WORKSHOP / CACHE next options, elite, fight)", font=mono(12), fill=(150, 165, 185))
        # c3 / c4 pages
        for c, k in ((2, "rest"), (3, "workshop")):
            im = pg[(dr, k)].resize((760, 428), Image.LANCZOS)
            SH.paste(im, (cols[c], y0 + 4))
        d.text((cols[2], y0 + 436), CAP[dr], font=mono(14), fill=(190, 200, 215))
        # the legend: the 1x strip as the game draws it, and the three new rows at 2x
        lg = legs[dr]
        SH.paste(lg, (cols[2], y0 + 466), lg)
        lg2 = legend(dr, 2.0)
        x0c = int(2 * (icons_x(dr) - 8))
        part = lg2.crop((x0c, 0, min(lg2.width, x0c + 640), lg2.height))
        SH.paste(part, (cols[2] + 880, y0 + 462), part)
        d.text((cols[2], y0 + 512), "RouteLegend strip at 1x (left) and its REST / WORKSHOP / CACHE rows at 2x (right)", font=mono(13), fill=(150, 165, 185))
    # bottom band: the CACHE loot header, three frames
    by = HEAD + 3 * ROW + 4
    d.line((20, by - 4, W - 20, by - 4), fill=(60, 70, 90), width=2)
    d.text((20, by + 2), "CACHE  -  the loot page with a stash header (title LOOT stays; the kind stamp, strip word CACHE and the sheet header words change; the loot sheet, PAYOUT and cards are untouched)", font=mono(15), fill=(120, 200, 230))
    for i, dr in enumerate("ABC"):
        im = pg[(dr, "cache")].resize((820, 461), Image.LANCZOS)
        SH.paste(im, (20 + i * 840, by + 28))
        d.text((30 + i * 840, by + 34), dr, font=anton(30), fill=(255, 226, 0))
    SH.save(DEST + "sheet.jpg", quality=90)
    print("sheet", SH.size)
    # scripts
    for f in os.listdir(os.path.dirname(os.path.abspath(__file__))):
        if f.endswith(".py") and f not in ("probe.py", "probe2.py", "tmp_cat.py", "contact_existing.py", "preview_icons.py", "test_map.py", "test_page.py", "squint_test.py"):
            shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), f), DEST + "scripts/" + f)


if __name__ == "__main__":
    main()
