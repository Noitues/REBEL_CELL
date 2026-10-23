"""The Godot implementation sheet: then (main 63364307) | now (art/look-nodes) for the map, the legend, the REST and WORKSHOP pages and
the CACHE header, the squint rows and the 16.8 / 41.6 px icon crops at 1:1 and 4x. Reads the captures of nodes_capture.gd."""
import os
import shutil
import sys
sys.path.insert(0, "D:/rc_scratch/solace_v1/nodes/scripts")
from PIL import Image, ImageDraw, ImageFilter, ImageFont

B = "D:/rc_scratch/solace_v1/nodes/"
DEST = "D:/rc_art/art-pass/docs/concepts/solace_vertical/nodes/godot/"
os.makedirs(DEST + "frames", exist_ok=True)
F = "D:/rc_art/godot_look_nodes/assets/fonts/"
anton = lambda s: ImageFont.truetype(F + "Anton-Regular.ttf", s)
mono = lambda s: ImageFont.truetype(F + "ShareTechMono-Regular.ttf", s)


def cap(w, n):
    return Image.open(B + "cap_%s/%s.png" % (w, n)).convert("RGB")


for w in ("then", "now"):
    for n in ("map_overview", "rest", "workshop", "cache"):
        shutil.copy(B + "cap_%s/%s.png" % (w, n), DEST + "frames/%s_%s.png" % (w, n))

W = 2560
COL = 1240
GAP = 40
X0 = (20, 20 + COL + GAP + 20)
SC = COL / 1920.0
rows = []


def pair(title, then_im, now_im, h=None):
    h = h or int(then_im.height * COL / then_im.width)
    rows.append((title, then_im.resize((COL, h), Image.LANCZOS), now_im.resize((COL, h), Image.LANCZOS)))


# map overview (the whole run) and the decision view
pair("MAP  (overview: every kind on one route; 1080p, frozen)", cap("then", "map_overview"), cap("now", "map_overview"))
# legend: the strip at the foot, and the three new rows at 3x
lg = (280, 1010, 1640, 1080)
pair("LEGEND  (the strip at the foot)", cap("then", "map_overview").crop(lg), cap("now", "map_overview").crop(lg))
lz = (790, 1020, 1130, 1076)
pair("LEGEND  rows REST / WORKSHOP / CACHE at 3.6x", cap("then", "map_overview").crop(lz), cap("now", "map_overview").crop(lz))
pair("REST PAGE", cap("then", "rest"), cap("now", "rest"))
pair("WORKSHOP PAGE", cap("then", "workshop"), cap("now", "workshop"))
ch = (0, 100, 960, 400)
pair("CACHE LOOT HEADER  (title stays LOOT; the strip says CACHE; the kind stamp)", cap("then", "cache").crop(ch), cap("now", "cache").crop(ch))

# squint rows: 320 wide and 4 px blur at 1:1 (the map's sticker band)
sq = []
for w in ("then", "now"):
    m = cap(w, "map_overview")
    s = m.resize((320, 180), Image.LANCZOS)
    b = m.crop((120, 600, 1100, 950)).filter(ImageFilter.GaussianBlur(4))
    sq.append((s, b))
# icon crops
spots = {"map": [("REST", (268, 873)), ("WORKSHOP", (268, 797)), ("CACHE", (395, 870))],
         "legend": [("REST", (808, 1047)), ("WORKSHOP", (898, 1047)), ("CACHE", (1027, 1047))]}


def crops(w):
    m = cap(w, "map_overview")
    out = {"map": [], "legend": []}
    for kind, half, z in (("map", 40, 4), ("legend", 16, 8)):
        for name, (x, y) in spots[kind]:
            c = m.crop((x - half, y - half, x + half, y + half))
            out[kind].append((name, c, c.resize((c.width * z, c.height * z), Image.NEAREST)))
    return out


tall = sum(r[1].height + 46 for r in rows)
SQ_H = 180 + 20 + 350 + 60
CR_H = 720
img = Image.new("RGB", (W, 80 + tall + SQ_H + CR_H + 60), (22, 26, 36))
d = ImageDraw.Draw(img)
d.text((20, 14), "NODES  //  Godot implementation  -  then (main 63364307)  |  now (art/look-nodes)", font=anton(34), fill=(246, 243, 232))
d.text((20, 58), "REST / WORKSHOP / CACHE slap-tag stickers (direction C), A's event layout on the pages, CACHE brick crimson; 1920x1080, --reduce-effects", font=mono(17), fill=(160, 178, 200))
y = 80
for title, a, b in rows:
    d.text((20, y + 6), title, font=mono(18), fill=(120, 200, 230))
    d.text((X0[0] + COL - 80, y + 6), "THEN", font=mono(18), fill=(255, 140, 90))
    d.text((X0[1] + COL - 80, y + 6), "NOW", font=mono(18), fill=(150, 255, 150))
    y += 34
    img.paste(a, (X0[0], y))
    img.paste(b, (X0[1], y))
    y += a.height + 12
# squint
d.text((20, y + 6), "SQUINT  (320 px wide, and a 4 px blur at 1:1 over the sticker band)", font=mono(18), fill=(120, 200, 230))
y += 36
for i, w in enumerate(("then", "now")):
    s, b = sq[i]
    img.paste(s, (X0[i], y))
    img.paste(s.convert("L").convert("RGB"), (X0[i] + 330, y))
    img.paste(b.resize((b.width * 2 // 3 + 150, b.height * 2 // 3 + 80)) if False else b, (X0[i], y + 190))
    d.text((X0[i] + 660, y + 8), w.upper() + ": colour | greyscale (320 px); blur below", font=mono(13), fill=(190, 200, 215))
y += 190 + 350 + 20
# icon crops
d.text((20, y + 6), "ICON CROPS  at 1:1 and 4x / 8x (map sticker 41.6 px in an 80 px window; legend swatch 16.8 px in a 32 px window)", font=mono(18), fill=(120, 200, 230))
y += 40
for i, w in enumerate(("then", "now")):
    cs = crops(w)
    d.text((X0[i] + COL - 60, y - 6), w.upper(), font=mono(14), fill=(255, 226, 0))
    for r, kind in enumerate(("map", "legend")):
        x = X0[i]
        yy = y + r * 340
        for name, c1, cz in cs[kind]:
            img.paste(c1, (x, yy))
            img.paste(cz, (x + c1.width + 6, yy))
            d.text((x, yy + cz.height + 2), "%s %s" % (name, "41.6 px" if kind == "map" else "16.8 px"), font=mono(12), fill=(190, 200, 215))
            x += c1.width + 6 + cz.width + 14
y += 680
img = img.crop((0, 0, W, y))
img.save(DEST + "impl_sheet.jpg", quality=90)
print(img.size)
