"""The Godot implementation sheet (round 3): then (main c68fe831) | now (art/look-nodes) for the map (decision and overview), the legend, the REST and WORKSHOP
pages, the event page for reference and the CACHE header; the squint rows (map; CACHE before | after; REST, WORKSHOP and event pages side by side); the 16.8 / 41.6 px
icon crops at 1:1 and 4x. Reads the captures of nodes_capture.gd (cap_then / cap_now) and the round 2 'now' frames (the dark CACHE crimson, `before`)."""
import os
import shutil
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

B = "D:/rc_scratch/solace_v1/nodes/"
DEST = "D:/rc_art/art-pass/docs/concepts/solace_vertical/nodes/godot/"
FR = DEST + "frames/"
os.makedirs(FR, exist_ok=True)
F = "D:/rc_art/godot_look_nodes/assets/fonts/"
anton = lambda s: ImageFont.truetype(F + "Anton-Regular.ttf", s)
mono = lambda s: ImageFont.truetype(F + "ShareTechMono-Regular.ttf", s)


def cap(w, n):
    return Image.open(B + "cap_%s/%s.png" % (w, n)).convert("RGB")


for w in ("then", "now"):
    for n in ("map", "map_overview", "rest", "workshop", "event", "cache"):
        shutil.copy(B + "cap_%s/%s.png" % (w, n), FR + "%s_%s.png" % (w, n))

W = 2560
COL = 1240
GAP = 40
X0 = (20, 20 + COL + GAP + 20)
rows = []


def pair(title, then_im, now_im, h=None):
    h = h or int(then_im.height * COL / then_im.width)
    rows.append((title, then_im.resize((COL, h), Image.LANCZOS), now_im.resize((COL, h), Image.LANCZOS)))


pair("MAP  (decision view, the entry's first choices: REST and WORKSHOP are the two numbered rooms; 1080p, frozen)", cap("then", "map"), cap("now", "map"))
pair("MAP  (overview: every kind on one route)", cap("then", "map_overview"), cap("now", "map_overview"))
lg = (280, 1010, 1640, 1080)
pair("LEGEND  (the strip at the foot)", cap("then", "map_overview").crop(lg), cap("now", "map_overview").crop(lg))
lz = (790, 1020, 1130, 1076)
pair("LEGEND  rows REST / WORKSHOP / CACHE at 3.6x", cap("then", "map_overview").crop(lz), cap("now", "map_overview").crop(lz))
pair("REST PAGE  (no RUN column; the backdrop is the event page's: the Site close-up under the same dim)", cap("then", "rest"), cap("now", "rest"))
pair("WORKSHOP PAGE", cap("then", "workshop"), cap("now", "workshop"))
pair("EVENT PAGE  (the reference backdrop; unchanged)", cap("then", "event"), cap("now", "event"))
ch = (0, 100, 960, 400)
pair("CACHE LOOT HEADER  (title stays LOOT; the strip says CACHE; the kind stamp)", cap("then", "cache").crop(ch), cap("now", "cache").crop(ch))


# --- squint helpers -------------------------------------------------------------------------------------------------
def blobs(im, rgb, tol=46, min_px=40):
    """centroids (full-res) of clusters of pixels within `tol` (RGB distance) of `rgb` (the CACHE sticker's red)."""
    a = np.asarray(im, dtype=np.float64)
    m = (np.linalg.norm(a - np.array(rgb), axis=-1) < tol)
    ys, xs = np.nonzero(m)
    out = []
    used = np.zeros(len(xs), bool)
    for i in range(len(xs)):
        if used[i]:
            continue
        near = (np.abs(xs - xs[i]) < 26) & (np.abs(ys - ys[i]) < 26) & ~used
        if near.sum() >= min_px:
            out.append((float(xs[near].mean()), float(ys[near].mean()), int(near.sum())))
        used |= near
    return out


def lab(rgb):
    c = np.asarray(rgb, dtype=np.float64) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = M @ c / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def dot_contrast(sq, cx, cy):
    """dE76 between the 320 px image's pixel at the blob and its surrounding ring (radius 4 to 7 px), and the colours."""
    a = np.asarray(sq, dtype=np.float64)
    x, y = int(round(cx * 320 / 1920)), int(round(cy * 320 / 1920))
    ring = []
    for dy in range(-7, 8):
        for dx in range(-7, 8):
            r = (dx * dx + dy * dy) ** 0.5
            if 4 <= r <= 7 and 0 <= y + dy < a.shape[0] and 0 <= x + dx < a.shape[1]:
                ring.append(a[y + dy, x + dx])
    centre = a[max(0, y - 1):y + 2, max(0, x - 1):x + 2].reshape(-1, 3).mean(0)
    bg = np.median(np.array(ring), axis=0)
    return float(np.linalg.norm(lab(centre) - lab(bg))), tuple(int(v) for v in centre), tuple(int(v) for v in bg)


AFTER_RED = (210, 44, 64)
BEFORE_RED = (136, 8, 28)
before_ov = Image.open(FR + "r2_now_map_overview.png").convert("RGB")
after_ov = cap("now", "map_overview")
sqb = before_ov.resize((320, 180), Image.LANCZOS)
sqa = after_ov.resize((320, 180), Image.LANCZOS)
cb = ca = [(395, 871, 0), (863, 868, 0)]  # the two CACHE stickers of the overview (same layout in both runs)
stats = {"before": [dot_contrast(sqb, x, y) for x, y, n in cb], "after": [dot_contrast(sqa, x, y) for x, y, n in ca]}
print("CACHE dots at 320 px (dE76 against the ring round them, centre colour, ring colour):")
for k, v in stats.items():
    print(k, [("%.0f" % dd, c, bg) for dd, c, bg in v])


def squint_marked(sq, pts):
    big = sq.resize((960, 540), Image.NEAREST)
    dr = ImageDraw.Draw(big)
    for x, y, n in pts:
        cx, cy = x * 960 / 1920, y * 540 / 1080
        dr.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), outline=(255, 255, 255), width=2)
    return big


def page_strip(w):
    out = Image.new("RGB", (3 * 330, 180 + 10 + 180), (22, 26, 36))
    for i, n in enumerate(("rest", "workshop", "event")):
        im = cap(w, n)
        out.paste(im.resize((320, 180), Image.LANCZOS), (i * 330, 0))
        out.paste(im.filter(ImageFilter.GaussianBlur(4)).resize((320, 180), Image.LANCZOS), (i * 330, 190))
    return out


tall = sum(r[1].height + 46 for r in rows)
SQ_H = 40 + 548 + 30 + 34 + 410
PG_H = 40 + 400
CR_H = 760
img = Image.new("RGB", (W, 80 + tall + SQ_H + PG_H + CR_H + 120), (22, 26, 36))
d = ImageDraw.Draw(img)
d.text((20, 14), "NODES  //  Godot implementation, round 3  -  then (main c68fe831)  |  now (art/look-nodes)", font=anton(34), fill=(246, 243, 232))
d.text((20, 58), "slap-tag stickers, hot brick-red CACHE (#D22C40), A's event layout without the RUN column, event-level page backdrop; 1920x1080, --reduce-effects", font=mono(17), fill=(160, 178, 200))
y = 80
for title, a, b in rows:
    d.text((20, y + 6), title, font=mono(18), fill=(120, 200, 230))
    d.text((X0[0] + COL - 80, y + 6), "THEN", font=mono(18), fill=(255, 140, 90))
    d.text((X0[1] + COL - 80, y + 6), "NOW", font=mono(18), fill=(150, 255, 150))
    y += 34
    img.paste(a, (X0[0], y))
    img.paste(b, (X0[1], y))
    y += a.height + 12

d.text((20, y + 6), "SQUINT  CACHE as a red dot: 320 px wide map (shown 3x, nearest), the CACHE stickers ringed.  BEFORE = round 2's dark crimson #88081C | AFTER = #D22C40", font=mono(18), fill=(120, 200, 230))
y += 36
img.paste(squint_marked(sqb, cb), (X0[0], y))
img.paste(squint_marked(sqa, ca), (X0[1], y))
d.text((X0[0] + 4, y + 4), "BEFORE (#88081C)", font=mono(14), fill=(255, 255, 255))
d.text((X0[1] + 4, y + 4), "AFTER (#D22C40)", font=mono(14), fill=(255, 255, 255))
y += 548
bt = "  ".join("%.0f" % v[0] for v in stats["before"]) or "-"
at = "  ".join("%.0f" % v[0] for v in stats["after"]) or "-"
d.text((X0[0], y), "dE76 of each CACHE dot against its surround at 320 px:  " + bt, font=mono(14), fill=(190, 200, 215))
d.text((X0[1], y), "dE76 of each CACHE dot against its surround at 320 px:  " + at, font=mono(14), fill=(190, 200, 215))
y += 30
d.text((20, y + 6), "SQUINT  4 px blur at 1:1 over the sticker band (map overview), BEFORE | AFTER", font=mono(18), fill=(120, 200, 230))
y += 34
for i, im in enumerate((before_ov, after_ov)):
    img.paste(im.crop((300, 560, 1500, 960)).filter(ImageFilter.GaussianBlur(4)), (X0[i], y))
y += 410
d.text((20, y + 6), "SQUINT  REST | WORKSHOP | event pages side by side (320 px wide; below each, a 4 px blur): the terminal must lead, not the city", font=mono(18), fill=(120, 200, 230))
y += 40
for i, w in enumerate(("then", "now")):
    img.paste(page_strip(w), (X0[i], y))
    d.text((X0[i] + 700, y + 4), "THEN (main): REST | WORKSHOP | event" if w == "then" else "NOW: REST | WORKSHOP | event", font=mono(13), fill=(255, 226, 0))
y += 400


def crops(w):
    m = cap(w, "map_overview")
    dm = cap(w, "map")
    out = {"map": [], "legend": []}
    pts = {"REST": (838, 593), "WORKSHOP": (838, 448)}
    for name in ("REST", "WORKSHOP"):
        x, yy = pts[name]
        c = dm.crop((x - 40, yy - 40, x + 40, yy + 40))
        out["map"].append((name, c, c.resize((320, 320), Image.NEAREST)))
    x, yy = 1020, 572
    c = dm.crop((int(x) - 40, int(yy) - 40, int(x) + 40, int(yy) + 40))
    out["map"].append(("CACHE", c, c.resize((320, 320), Image.NEAREST)))
    for name, (x, yy) in (("REST", (808, 1047)), ("WORKSHOP", (898, 1047)), ("CACHE", (1027, 1047))):
        c = m.crop((x - 16, yy - 16, x + 16, yy + 16))
        out["legend"].append((name, c, c.resize((256, 256), Image.NEAREST)))
    return out


d.text((20, y + 6), "ICON CROPS  at 1:1 and 4x / 8x (map sticker 41.6 px in an 80 px window of the decision view; legend swatch 16.8 px in a 32 px window)", font=mono(18), fill=(120, 200, 230))
y += 40
for i, w in enumerate(("then", "now")):
    cs = crops(w)
    d.text((X0[i] + COL - 60, y - 6), w.upper(), font=mono(14), fill=(255, 226, 0))
    for r, kind in enumerate(("map", "legend")):
        x = X0[i]
        yy = y + r * 360
        for name, c1, cz in cs[kind]:
            img.paste(c1, (x, yy))
            img.paste(cz, (x + c1.width + 6, yy))
            d.text((x, yy + cz.height + 2), "%s %s" % (name, "41.6 px" if kind == "map" else "16.8 px"), font=mono(12), fill=(190, 200, 215))
            x += c1.width + 6 + cz.width + 14
y += 720
img = img.crop((0, 0, W, y))
img.save(DEST + "impl_sheet.jpg", quality=90)
print(img.size)
