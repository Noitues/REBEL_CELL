"""Render the whole roster and compose every deliverable.

python make_roster.py render      # hero (ss=2) + LOD (ss=1) wheels -> ../scratch/renders
python make_roster.py compose     # all PNG/JPG deliverables from the cached renders
python make_roster.py all
"""
import os
import sys
import textwrap
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
CACHE = os.path.join(OUT, "scratch", "renders")

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from slicelib import PROGRAMS, CORPS, f_num, f_ui, f_mono, bloom, to_img, glyph_rgba, R_OUT
import roster as RS
import roster_wheel as RW

CORP_ORDER = ["meridian", "solace", "halcyon", "orbital", "rebel_cell"]


# ----------------------------------------------------------------- jobs
def jobs():
    out = []
    for c in RS.CLASSES:
        s, m = RS.class_spec(c)
        out.append(("op_" + c, s, m))
    for corp in CORP_ORDER:
        for eid in RS.ENEMY_PICKS[corp]:
            s, m = RS.enemy_spec(eid, corp if eid.startswith("rc_") else None)
            out.append(("en_" + eid, s, m))
        p1, p2, m = RS.boss_specs(corp)
        out.append(("boss_%s_p1" % RS.BOSSES[corp], p1, m))
        out.append(("boss_%s_p2" % RS.BOSSES[corp], p2, m))
    return out


def render_all(only=None):
    os.makedirs(CACHE, exist_ok=True)
    for key, spec, meta in jobs():
        if only and only not in key:
            continue
        t0 = time.time()
        RW.render(spec, ss=2).save(os.path.join(CACHE, key + ".png"))
        RW.render(spec, ss=1, lod=True).save(os.path.join(CACHE, key + "_lod.png"))
        print(key, round(time.time() - t0, 1), flush=True)


def load(key, lod=False):
    im = Image.open(os.path.join(CACHE, key + ("_lod" if lod else "") + ".png")).convert("RGBA")
    return im.crop(im.getbbox())


def fit(im, w, h):
    k = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS), k


def scale_to_r(im, r):
    """Scale a cropped master render (R_OUT = 360) so the slice radius becomes r."""
    k = r / R_OUT
    return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)


# ----------------------------------------------------------------- frame helpers
def background(W, H, tint, seed=3, dim=1.0):
    yy = np.linspace(0, 1, H)[:, None, None]
    top = np.array([0.055, 0.045, 0.075], np.float32)
    bot = np.array([0.02, 0.02, 0.03], np.float32)
    arr = np.tile(top + (bot - top) * yy, (1, W, 1))
    rng = np.random.default_rng(seed)
    city = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(city)
    x = 0
    while x < W:
        bw = int(rng.integers(80, 220))
        bh = int(rng.integers(int(H * 0.25), int(H * 0.6)))
        d.rectangle([x, H - bh, x + bw, H], fill=(14, 13, 20))
        for wy in range(H - bh + 20, H, 26):
            for wx in range(x + 12, x + bw - 12, 22):
                if rng.random() < 0.25:
                    d.rectangle([wx, wy, wx + 8, wy + 10], fill=(55, 50, 75) if rng.random() < 0.8 else (90, 70, 40))
        x += bw + int(rng.integers(6, 30))
    city = np.asarray(city.filter(ImageFilter.GaussianBlur(5)), np.float32) / 255
    arr = arr + city * 0.7
    yy2, xx2 = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.exp(-(((xx2 - W * 0.4) / (W * 0.45)) ** 2 + ((yy2 - H * 0.45) / (H * 0.6)) ** 2))[..., None]
    arr = arr + g * (np.array(tint, np.float32) / 255) * 0.10
    return to_img(arr * dim)


def paste(dst, im, x, y):
    dst.paste(im, (int(x), int(y)), im)


def wrap(d, xy, text, font, fill, width_chars, lh):
    x, y = xy
    for ln in textwrap.wrap(text, width_chars):
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def chip(d, x, y, text, col, font):
    tw = font.getlength(text)
    d.rounded_rectangle([x, y, x + tw + 16, y + 26], radius=6, fill=(14, 12, 20), outline=col, width=2)
    d.text((x + 8, y + 3), text, font=font, fill=col)
    return x + tw + 24


def caption(im, title, sub, accent):
    d = ImageDraw.Draw(im)
    W, H = im.size
    f1, f2 = f_num(38), f_mono(17, bold=False)
    w = max(f1.getlength(title), f2.getlength(sub)) + 40
    d.rectangle([0, H - 82, w, H], fill=(8, 8, 12))
    d.rectangle([0, H - 82, 6, H], fill=accent)
    d.text((22, H - 79), title, font=f1, fill=(255, 255, 255))
    d.text((22, H - 32), sub, font=f2, fill=(200, 200, 210))


def greyscale(im):
    a = im.split()[3]
    g = ImageOps.grayscale(im.convert("RGB")).convert("RGBA")
    g.putalpha(a)
    return g


# ----------------------------------------------------------------- operatives
def compose_ops():
    metas = {k: (s, m) for k, s, m in jobs() if k.startswith("op_")}
    for c in RS.CLASSES:
        spec, meta = metas["op_" + c]
        st = RW.CLASS_STYLE[c]
        acc = st["acc"]
        im = background(1920, 1080, acc, seed=RS.CLASSES.index(c) + 2)
        w, k = fit(load("op_" + c), 980, 1050)
        paste(im, w, 20 + (980 - w.width) / 2, 15)
        im = bloom(im, 1, 0.4, 0.62)
        d = ImageDraw.Draw(im)
        x = 1040
        d.text((x, 30), meta["name"].upper(), font=f_num(96), fill=acc)
        role = ("ALTERNATIVE OF " + meta["alt_of"].upper()) if meta["alt_of"] else "BASE CLASS"
        d.text((x + 4, 140), "%s   |   %d HP" % (role, meta["hp"]), font=f_ui(24, b"Bold SemiCondensed"), fill=(230, 230, 240))
        y = wrap(d, (x + 4, 180), meta["desc"], f_mono(18, False), (190, 190, 200), 70, 24) + 16
        fh, fb = f_ui(19, b"Bold SemiCondensed"), f_mono(16, False)
        d.text((x + 4, y), "BEZEL ORNAMENT", font=fh, fill=acc)
        y = wrap(d, (x + 4, y + 26), meta["identity"][0], fb, (215, 215, 225), 78, 21) + 6
        d.text((x + 4, y), "HUB RING", font=fh, fill=acc)
        y = wrap(d, (x + 4, y + 26), meta["identity"][1], fb, (215, 215, 225), 78, 21) + 10
        d.text((x + 4, y), "HUB CORE  -  " + meta["core"]["name"].upper(), font=fh, fill=acc)
        y = wrap(d, (x + 4, y + 26), meta["core"]["desc"], fb, (215, 215, 225), 78, 21) + 10
        d.text((x + 4, y), "INNER RING (rank 1)", font=fh, fill=acc)
        y += 30
        for sid in meta["ring"]:
            gname, lab = RW.SEG_GLYPH[sid]
            g = glyph_rgba(gname, 30, 2.5)
            im.paste(g, (x + 4, y - 4), g)
            d.text((x + 46, y), lab, font=f_ui(18, b"Bold Condensed"), fill=(255, 255, 255))
            d.text((x + 150, y + 1), RS.SEG_DESC[sid], font=fb, fill=(200, 200, 210))
            y += 32
        y += 6
        d.text((x + 4, y), "WHEEL  (content/classes/%s.tres, 6 x 5 ticks)" % c, font=fh, fill=acc)
        y += 30
        xx = x + 4
        cf = f_ui(17, b"Bold Condensed")
        for s in spec["slots"]:
            v = "" if s["program"] == "NULL" else " %d" % s["value"]
            xx = chip(d, xx, y, s["program"] + v, PROGRAMS[s["program"]]["col"], cf)
            if xx > 1840:
                xx, y = x + 4, y + 34
        # small LOD + grey previews
        yb = 790
        lod = scale_to_r(load("op_" + c, lod=True), 100)
        grey = greyscale(scale_to_r(load("op_" + c), 100))
        paste(im, lod, x + 10, yb + 20)
        paste(im, grey, x + 30 + lod.width, yb + 20)
        d.text((x + 10, yb - 6), "r = 100  small variant", font=fb, fill=(170, 170, 180))
        d.text((x + 30 + lod.width, yb - 6), "hero, greyscale", font=fb, fill=(170, 170, 180))
        im.save(os.path.join(OUT, "op_%s.png" % c))
        print("op", c, flush=True)
    # sheet: 4 x 2 at r = 220
    W, H = 2440, 1420
    sh = background(W, H, (255, 61, 168), seed=11)
    d = ImageDraw.Draw(sh)
    d.text((40, 20), "OPERATIVES  -  Screens & Data roster", font=f_num(56), fill=(255, 255, 255))
    d.text((44, 86), "8 classes at r = 220 | class bezel + hub ring per class | alternatives (row 2 right of each base) reuse their base's motif",
           font=f_mono(18, False), fill=(190, 190, 200))
    order = ["breaker", "wrecker", "ghost", "phantom", "rigger", "overclocker", "botnet", "hivemind"]
    for i, c in enumerate(order):
        col, row = i % 4, i // 4
        cx = 30 + col * 600
        cy = 130 + row * 640
        w = scale_to_r(load("op_" + c), 220)
        if w.width > 590:
            w, _ = fit(w, 590, 590)
        paste(sh, w, cx + (600 - w.width) / 2, cy + max(0, (560 - w.height) / 2))
        acc = RW.CLASS_STYLE[c]["acc"]
        name = c.upper() + ("   (alt of %s)" % RS.ALT_OF[c].title() if c in RS.ALT_OF else "   (base)")
        f = f_num(36)
        d.text((cx + 300 - f.getlength(name) / 2, cy + 572), name, font=f, fill=acc)
    sh = bloom(sh, 1, 0.35, 0.62)
    sh.save(os.path.join(OUT, "operatives_sheet.png"))


# ----------------------------------------------------------------- enemies
def compose_enemies():
    metas = {k: (s, m) for k, s, m in jobs() if k.startswith("en_")}
    for corp in CORP_ORDER:
        acc = CORPS[corp]["col"]
        im = background(1920, 1080, acc, seed=CORP_ORDER.index(corp) + 20)
        for i, eid in enumerate(RS.ENEMY_PICKS[corp]):
            w, k = fit(load("en_" + eid), 620, 700)
            paste(im, w, i * 640 + (640 - w.width) / 2, 90 + (700 - w.height) / 2)
        im = bloom(im, 1, 0.4, 0.62)
        d = ImageDraw.Draw(im)
        d.text((30, 14), CORPS[corp]["name"], font=f_num(54), fill=acc)
        d.text((36 + f_num(54).getlength(CORPS[corp]["name"]) + 20, 38), "2 regulars + 1 elite  |  corp skin inside C's screen frame, type by glyph + accent rim + tab",
               font=f_mono(17, False), fill=(190, 190, 200))
        for i, eid in enumerate(RS.ENEMY_PICKS[corp]):
            s, m = metas["en_" + eid]
            x = i * 640 + 30
            y = 800
            d.text((x, y), m["name"].upper(), font=f_num(40), fill=(255, 255, 255))
            rc = (255, 210, 90) if m["role"] == "Elite" else (200, 200, 210)
            d.text((x + f_num(40).getlength(m["name"].upper()) + 14, y + 12), "%s  |  %d HP" % (m["role"].upper(), m["hp"]),
                   font=f_ui(20, b"Bold SemiCondensed"), fill=rc)
            y = wrap(d, (x, y + 48), m["desc"], f_mono(15, False), (190, 190, 200), 64, 19) + 6
            xx = x
            cf = f_ui(15, b"Bold Condensed")
            for mm in m["mech"]:
                if xx + cf.getlength(mm) + 20 > x + 600:
                    xx, y = x, y + 32
                xx = chip(d, xx, y, mm, acc, cf)
        im.save(os.path.join(OUT, "enemies_%s.png" % corp))
        print("enemies", corp, flush=True)
    # sheet: 5 rows (corps) x 3
    W, H = 2400, 2260
    sh = background(W, H, (255, 140, 26), seed=31)
    d = ImageDraw.Draw(sh)
    d.text((30, 14), "ENEMIES  -  15 wheels, 5 corporation skins", font=f_num(56), fill=(255, 255, 255))
    for r, corp in enumerate(CORP_ORDER):
        y0 = 90 + r * 432
        d.rectangle([0, y0, 8, y0 + 420], fill=CORPS[corp]["col"])
        d.text((24, y0 + 10), CORPS[corp]["name"], font=f_num(34), fill=CORPS[corp]["col"])
        for i, eid in enumerate(RS.ENEMY_PICKS[corp]):
            s, m = metas["en_" + eid]
            w, k = fit(load("en_" + eid), 660, 360)
            x0 = 300 + i * 700
            paste(sh, w, x0 + (700 - w.width) / 2, y0 + 4)
            lab = "%s  |  %s" % (m["name"].upper(), m["role"].upper())
            f = f_num(28)
            d.text((x0 + 350 - f.getlength(lab) / 2, y0 + 372), lab, font=f,
                   fill=(255, 210, 90) if m["role"] == "Elite" else (235, 235, 245))
    sh = bloom(sh, 1, 0.3, 0.65)
    sh.convert("RGB").save(os.path.join(OUT, "enemies_sheet.jpg"), quality=88)


# ----------------------------------------------------------------- bosses
def compose_bosses():
    bm = {}
    for corp in CORP_ORDER:
        p1, p2, m = RS.boss_specs(corp)
        bm[corp] = m
        eid = RS.BOSSES[corp]
        acc = CORPS[corp]["col"]
        im = background(1920, 1080, acc, seed=CORP_ORDER.index(corp) + 40)
        for i in (1, 2):
            w, k = fit(load("boss_%s_p%d" % (eid, i)), 930, 880)
            paste(im, w, (i - 1) * 960 + (960 - w.width) / 2, 6)
        im = bloom(im, 1, 0.45, 0.6)
        d = ImageDraw.Draw(im)
        fh, fb = f_ui(20, b"Bold SemiCondensed"), f_mono(15, False)
        ph = m["phases"]
        for i in (1, 2):
            x = (i - 1) * 960 + 40
            y = 892
            if i == 1:
                head = "PHASE 1  (100%% - %d%%)" % (ph[0]["threshold"] * 100)
                sig, mech, line = m["sig"][0], m["mech1"], m["desc"]
            else:
                head = "PHASE 2  (below %d%%)  -  %s" % (ph[0]["threshold"] * 100, ph[0]["behavior"])
                sig, mech, line = m["sig"][1], m["mech2"], '"%s"' % ph[0]["line"]
            d.text((x, y), head, font=f_num(30), fill=acc)
            y = wrap(d, (x, y + 38), sig, fb, (225, 225, 235), 100, 19)
            y = wrap(d, (x, y + 2), line, fb, (170, 170, 180), 100, 19) + 4
            xx = x
            cf = f_ui(15, b"Bold Condensed")
            for mm in mech:
                if xx + cf.getlength(mm) + 20 > x + 880:
                    xx, y = x, y + 30
                xx = chip(d, xx, y, mm, acc, cf)
        d.line([(960, 120), (960, 860)], fill=(60, 60, 70), width=2)
        im.save(os.path.join(OUT, "boss_%s.png" % eid))
        print("boss", eid, flush=True)
    W, H = 2400, 1360
    sh = background(W, H, (232, 20, 30), seed=51)
    d = ImageDraw.Draw(sh)
    d.text((30, 14), "BOSSES  -  phase 1 (top) and phase 2 (bottom), 120% wheels", font=f_num(56), fill=(255, 255, 255))
    for i, corp in enumerate(CORP_ORDER):
        eid = RS.BOSSES[corp]
        for p in (1, 2):
            w, k = fit(load("boss_%s_p%d" % (eid, p)), 470, 600)
            paste(sh, w, i * 480 + (480 - w.width) / 2, 100 + (p - 1) * 620)
        name = bm[corp]["name"].upper()
        f = f_num(26)
        d.text((i * 480 + 240 - f.getlength(name) / 2, 1320), name, font=f, fill=CORPS[corp]["col"])
    sh = bloom(sh, 1, 0.3, 0.65)
    sh.convert("RGB").save(os.path.join(OUT, "bosses_sheet.jpg"), quality=88)


# ----------------------------------------------------------------- contact sheet
def compose_contact():
    W, H = 2400, 1500
    sh = background(W, H, (92, 225, 255), seed=61, dim=0.8)
    d = ImageDraw.Draw(sh)
    d.text((30, 14), "ROUND 6 ROSTER  -  contact sheet (small variant: r = 100, bosses r = 120)", font=f_num(48), fill=(255, 255, 255))
    rows = [("OPERATIVES", ["op_" + c for c in RS.CLASSES]),
            ("ENEMIES", ["en_" + e for corp in CORP_ORDER for e in RS.ENEMY_PICKS[corp]][:8]),
            ("", ["en_" + e for corp in CORP_ORDER for e in RS.ENEMY_PICKS[corp]][8:]),
            ("BOSSES  P1 / P2", ["boss_%s_p%d" % (RS.BOSSES[c], p) for c in CORP_ORDER for p in (1, 2)])]
    y = 90
    for title, keys in rows:
        if title:
            d.text((30, y), title, font=f_ui(22, b"Bold SemiCondensed"), fill=(200, 200, 210))
        x = 30
        cell = (W - 60) / max(8, len(keys))
        for k in keys:
            w = scale_to_r(load(k, lod=True), 120 if k.startswith("boss") else 100)  # bosses at 120%
            if w.width > cell - 6 or w.height > 330:
                w, _ = fit(w, cell - 6, 330)
            paste(sh, w, x + (cell - w.width) / 2, y + 28)
            x += cell
        y += 350
    sh = bloom(sh, 1, 0.3, 0.65)
    sh.convert("RGB").save(os.path.join(OUT, "contact_sheet.jpg"), quality=86)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    only = sys.argv[2] if len(sys.argv) > 2 else None
    t0 = time.time()
    if what in ("render", "all"):
        render_all(only)
    if what in ("compose", "all", "ops"):
        compose_ops()
    if what in ("compose", "all", "enemies"):
        compose_enemies()
    if what in ("compose", "all", "bosses"):
        compose_bosses()
    if what in ("compose", "all", "contact"):
        compose_contact()
    print("done", what, round(time.time() - t0, 1))
