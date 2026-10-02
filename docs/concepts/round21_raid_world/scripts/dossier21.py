"""Round 21: the campaign summary as the CORPORATION's file on you: an open manila dossier on a desk.

Typed papers carry the stats (letterhead of the corp that took you down), polaroids show the network at the end,
and post-it notes are written by a corporate AUDITOR (neat blue ballpoint, not the Cell's grease pencil): MOST
TROUBLESOME instead of MVP. Only our own UI (NEW CAMPAIGN / MAIN MENU) stays vinyl sticker, on the desk.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import ui19 as U
import lost20 as LO
import roof20 as RF

SL = U.SL
W, H = 1920, 1080
FONTS = "C:/Windows/Fonts/"
TYPE = FONTS + "cour.ttf"
TYPE_B = FONTS + "courbd.ttf"
PEN = FONTS + "Inkfree.ttf"
SERIF_B = FONTS + "georgiab.ttf"
BAHN = FONTS + "bahnschrift.ttf"
INKB = (28, 40, 110)          # auditor's ballpoint
PAPER = (240, 236, 226)
RED_STAMP = (196, 30, 40)


def F(p, s):
    return ImageFont.truetype(p, int(s))


def grain(w, h, seed, k=10):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, k, (h // 2 + 1, w // 2 + 1)).astype(np.float32)
    n = np.asarray(Image.fromarray(np.clip(n + 128, 0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) - 128
    return n


def sheet(w, h, col, seed, k=8):
    a = np.zeros((h, w, 3), np.float32) + np.array(col, np.float32)
    a += grain(w, h, seed, k)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def manila(w, h, seed):
    im = sheet(w, h, (222, 196, 140), seed, 9)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    for _ in range(int(w * h / 900)):                         # paper fibres
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        a = rng.uniform(0, math.pi)
        L = rng.uniform(3, 9)
        d.line([(x, y), (x + L * math.cos(a), y + L * math.sin(a))], fill=(190, 160, 110, 255), width=1)
    return im


def place(canvas, item, cx, cy, angle=0.0, shadow=0.55, blur=10, off=(8, 12)):
    """Paste an RGBA item rotated about its centre with a soft drop shadow (canvas: RGBA, modified copy returned)."""
    it = item.rotate(angle, Image.BICUBIC, expand=True)
    a = it.split()[3]
    sh = Image.new("RGBA", it.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * shadow)))
    pad = blur * 3
    shp = Image.new("RGBA", (it.size[0] + 2 * pad, it.size[1] + 2 * pad), (0, 0, 0, 0))
    shp.paste(sh, (pad, pad))
    shp = shp.filter(ImageFilter.GaussianBlur(blur))
    x, y = int(cx - it.size[0] / 2), int(cy - it.size[1] / 2)
    canvas.alpha_composite(shp, (max(0, x - pad + off[0]), max(0, y - pad + off[1])))
    canvas.alpha_composite(it, (x, y))
    return canvas


def typed(d, x, y, lines, size=19, col=(34, 30, 34), lh=None, font=TYPE):
    lh = lh or int(size * 1.35)
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=F(font, size), fill=col + (255,))
    return y + len(lines) * lh


def stamp(text, size, col, angle, seed=1):
    """Rubber stamp: framed text, uneven ink."""
    f = F(SL.ANTON, size)
    tw = int(f.getlength(text))
    im = Image.new("RGBA", (tw + 60, size + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([6, 6, tw + 54, size + 54], outline=col + (255,), width=6)
    d.text((30, 30 + size * 0.05), text, font=f, fill=col + (255,), anchor="lt")
    rng = np.random.default_rng(seed)
    a = np.asarray(im.split()[3], np.float32)
    n = grain(im.size[0], im.size[1], seed, 60)
    a = a * np.clip(0.55 + n / 120 + rng.uniform(0, 0.2), 0, 1)
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im.rotate(angle, Image.BICUBIC, expand=True)


def postit(text_lines, col, w=230, h=210, seed=1, size=27):
    im = Image.new("RGBA", (w, h + 10), (0, 0, 0, 0))
    body = sheet(w, h, col, seed, 5)
    g = np.linspace(1.0, 0.86, h)[:, None, None]                 # the bottom lifts off the page: darker
    b = np.asarray(body, np.float32)
    b[..., :3] *= g
    body = Image.fromarray(b.astype(np.uint8))
    top = Image.new("RGBA", (w, 34), tuple(int(c * 0.93) for c in col) + (255,))
    body.paste(top, (0, 0))
    im.paste(body, (0, 0))
    d = ImageDraw.Draw(im)
    y = 46
    for ln in text_lines:
        d.text((16, y), ln, font=F(PEN, size), fill=INKB + (255,))
        y += int(size * 1.2)
    return im


def polaroid(photo, caption, w=300, seed=1):
    ph = photo.resize((w - 30, w - 30), Image.LANCZOS).convert("RGB")
    a = np.asarray(ph, np.float32) / 255.0
    lum = a.mean(axis=2, keepdims=True)
    a = lum + (a - lum) * 0.8                                    # print: a bit less saturated, warm, flash vignette
    a = a * np.array([1.04, 1.0, 0.92]) + 0.03
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]] / a.shape[0]
    a = a * (1 - 0.35 * ((xx - 0.5) ** 2 + (yy - 0.5) ** 2) * 2)[..., None]
    ph = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    im = sheet(w, int(w * 1.2), (246, 244, 238), seed, 4)
    im.paste(ph, (15, 15))
    d = ImageDraw.Draw(im)
    d.text((w / 2, w * 1.2 - 34), caption, font=F(PEN, 24), fill=INKB + (255,), anchor="mm")
    return im


def tape(w=110, h=34, angle=0):
    im = Image.new("RGBA", (w, h), (236, 230, 200, 150))
    return im.rotate(angle, Image.BICUBIC, expand=True)


def heat_chart(w, h, data):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for th in (25, 50, 75):
        y = h - 18 - (h - 30) * th / 100
        for x in range(30, w, 10):
            d.line([(x, y), (x + 5, y)], fill=(120, 110, 110, 255))
        d.text((2, y), str(th), font=F(TYPE, 13), fill=(80, 70, 70, 255), anchor="lm")
    pts = [(30 + (w - 40) * i / (len(data) - 1), h - 18 - (h - 30) * v / 100) for i, v in enumerate(data)]
    d.line(pts, fill=(30, 30, 40, 255), width=2)
    for i, p in enumerate(pts):
        r = 3 if i not in (2, 5, 9, 10) else 5
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=(30, 30, 40, 255) if r == 3 else RED_STAMP + (255,))
    return im


def letterhead(d, im, x, y, w):
    st = LO.CORP_STYLE["HALCYON"]
    im.alpha_composite(LO.seal(st, 92), (x, y))
    d.text((x + 108, y + 14), "HALCYON CIVIC", font=F(BAHN, 32), fill=(70, 46, 150, 255))
    d.text((x + 110, y + 54), "COMPLIANCE DIVISION  //  AUDIT 7", font=F(BAHN, 17), fill=(90, 80, 120, 255))
    d.line([(x, y + 104), (x + w, y + 104)], fill=(70, 46, 150, 255), width=3)


def desk():
    a = np.zeros((H, W, 3), np.float32) + np.array([30, 24, 30], np.float32)
    a += grain(W, H, 3, 6)[..., None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    lamp = np.exp(-(((xx - 600) / 1300) ** 2 + ((yy - 200) / 900) ** 2))
    a = a * (0.5 + 1.1 * lamp[..., None]) + np.array([30, 20, 6], np.float32) * lamp[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


FL = (110, 100, 955, 1040)      # left inner panel (x0, y0, x1, y1)
FR = (955, 100, 1800, 1040)


def left_panel(photos):
    """Inner left of the folder: polaroids of the network at the end + the personnel strip + auditor notes."""
    w, h = FL[2] - FL[0], FL[3] - FL[1]
    im = manila(w, h, 11)
    d = ImageDraw.Draw(im)
    d.line([(w - 3, 0), (w - 3, h)], fill=(170, 140, 90, 255), width=4)            # the spine crease
    caps = ["HOME SERVER - 0/50", "BEACON - whose?", "NODES AT THE END"]
    pos = [(170, 230, -6), (470, 210, 4), (700, 260, -3)]
    for i, (ph, cap, (cx, cy, ang)) in enumerate(zip(photos, caps, pos)):
        pol = polaroid(ph, cap, 290, seed=20 + i)
        im = place(im, pol, cx, cy, ang, shadow=0.45, blur=8)
        im = place(im, tape(100, 30, ang + 8), cx - 10, cy - 172, 0, shadow=0.0)
    # personnel strip: a typed sheet with the operatives (emblem prints) and fates
    ps = sheet(760, 400, PAPER, 31, 6)
    dp = ImageDraw.Draw(ps)
    dp.text((24, 18), "PERSONNEL  //  IDENTIFIED OPERATIVES", font=F(TYPE_B, 20), fill=(30, 28, 32, 255))
    dp.line([(24, 48), (736, 48)], fill=(30, 28, 32, 255), width=2)
    ops = [("breaker", "BREAKER", "R3", "AT LARGE (stationed)", "7 runs"), ("ghost", "GHOST", "R2", "DECEASED  run 9", "Server Rack"),
           ("rigger", "RIGGER", "R1", "DECEASED  run 4", "elite router"), ("botnet", "BOTNET", "R2", "AT LARGE (reserve)", "5 runs"),
           ("wrecker", "WRECKER", "R0", "DECEASED  run 11", "the final run")]
    for i, (c, nm, rk, fate, note) in enumerate(ops):
        y = 66 + i * 64
        g = Image.open(os.path.join(RF.EMBLEMS, c + ".png")).split()[3].resize((48, 48), Image.LANCZOS)
        ps.paste(Image.new("RGBA", (48, 48), (40, 38, 44, 255)), (28, y), g)
        dp.text((96, y + 4), "%-8s %s" % (nm, rk), font=F(TYPE_B, 20), fill=(30, 28, 32, 255))
        dp.text((330, y + 4), fate, font=F(TYPE, 19), fill=(150, 20, 30, 255) if fate.startswith("DECEASED") else (30, 28, 32, 255))
        dp.text((96, y + 28), note, font=F(TYPE, 15), fill=(90, 86, 90, 255))
        if fate.startswith("DECEASED"):
            dp.line([(96, y + 15), (300, y + 15)], fill=(30, 28, 32, 200), width=2)       # struck through
    im = place(im, ps, 420, 690, 1.2, shadow=0.4)
    # auditor post-its
    im = place(im, postit(["MOST", "TROUBLESOME", "-> BREAKER"], (255, 120, 170), 230, 200, 41, 30), 700, 610, 7, shadow=0.45)
    im = place(im, postit(["2 still at large.", "stationed one", "never logged in."], (255, 232, 90), 230, 190, 42, 24), 700, 880, -6, shadow=0.45)
    return im


def right_panel():
    """Inner right: the audit report (stats), an annex underneath, the CASE CLOSED stamp and auditor notes."""
    w, h = FR[2] - FR[0], FR[3] - FR[1]
    im = manila(w, h, 12)
    # annex sheet underneath, peeking out
    an = sheet(700, 820, (232, 228, 216), 33, 6)
    da = ImageDraw.Draw(an)
    da.text((30, 720), "ANNEX B  //  RESIDUAL RISK", font=F(TYPE_B, 20), fill=(30, 28, 32, 255))
    typed(da, 30, 752, ["subject retains: PHANTOM class, ICE 6 (Halcyon),", "home-server variant BUNKER"], 16)
    im = place(im, an, 430, 500, -4, shadow=0.35)
    # the report
    rp = sheet(700, 830, PAPER, 34, 6)
    d = ImageDraw.Draw(rp)
    letterhead(d, rp, 30, 26, 640)
    d.text((30, 150), "AUDIT REPORT", font=F(SERIF_B, 34), fill=(30, 28, 32, 255))
    y = typed(d, 30, 200, ["SUBJECT ....... REBEL_CELL  (cell 03)", "DURATION ...... 41 days",
                           "STATUS ........ PROCESSED  (raid: COMPLIANCE SWEEP)", "", "ACTIVITY", "  netruns ..... 8   (3 operatives lost)",
                           "  raids ....... 4   (3 repelled, 1 decisive)", "  exploits .... 2 / 3 extracted",
                           "  schematics .. 214 earned / 190 spent", "", "NETWORK AT CLOSURE", "  held 3   disabled 1   seized 1",
                           "  home server  0 / 50   (peak: 7 nodes)", "", "HEAT (subject's exposure), peak 82:"], 18)
    rp.alpha_composite(heat_chart(620, 150, [6, 14, 26, 31, 44, 52, 58, 66, 70, 77, 82]), (40, y + 6))
    d.text((30, 790), "filed by: A. VANCE, AUDIT 7", font=F(TYPE, 16), fill=(70, 66, 70, 255))
    d.text((420, 776), "A.Vance", font=F(PEN, 34), fill=INKB + (255,))
    im = place(im, rp, 410, 470, 1.5, shadow=0.45)
    im = place(im, stamp("CASE CLOSED", 64, RED_STAMP, 12, seed=5), 560, 300, 0, shadow=0.0)
    im = place(im, postit(["heat spiked", "after run 8.", "why weren't", "we told?"], (150, 220, 255), 220, 220, 43, 25), 730, 150, 6, shadow=0.45)
    im = place(im, postit(["they'll be", "back. flag", "the PHANTOM."], (180, 240, 140), 210, 190, 44, 25), 735, 790, -5, shadow=0.45)
    return im


def front_cover():
    w, h = FR[2] - FR[0], FR[3] - FR[1]
    im = manila(w, h, 13)
    d = ImageDraw.Draw(im)
    lab = sheet(420, 150, (246, 244, 238), 50, 4)
    dl = ImageDraw.Draw(lab)
    dl.text((20, 18), "HALCYON CIVIC  //  AUDIT 7", font=F(BAHN, 22), fill=(70, 46, 150, 255))
    dl.text((20, 56), "SUBJECT: REBEL_CELL", font=F(TYPE_B, 24), fill=(30, 28, 32, 255))
    dl.text((20, 96), "CELL 03  //  41 DAYS", font=F(TYPE, 20), fill=(30, 28, 32, 255))
    im = place(im, lab, w / 2, 240, 0, shadow=0.25, blur=4)
    im = place(im, stamp("PROCESSED", 70, (110, 70, 200), -10, seed=6), w / 2 + 40, 520, 0, shadow=0.0)
    im.alpha_composite(LO.seal(LO.CORP_STYLE["HALCYON"], 140), (int(w / 2 - 70), 700))
    d.line([(2, 0), (2, h)], fill=(170, 140, 90, 255), width=4)
    return im


def tab():
    im = manila(300, 60, 14)
    m = Image.new("L", (300, 60), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 299, 80], 18, fill=255)
    im.putalpha(m)
    ImageDraw.Draw(im).text((24, 30), "CELL-03 / CLOSED", font=F(TYPE_B, 20), fill=(60, 50, 40, 255), anchor="lm")
    return im


def compose(photos, cover_open=1.0, buttons=True):
    """cover_open 0 (closed) .. 1 (open). The front cover swings about the spine from the right half to the left."""
    cv = desk()
    cv.alpha_composite(tab(), (FR[2] - 360, FR[1] - 52))
    rp = right_panel()
    cv = place(cv, rp, (FR[0] + FR[2]) / 2, (FR[1] + FR[3]) / 2, 0, shadow=0.6, blur=16, off=(10, 16))
    th = math.pi * cover_open
    if cover_open >= 1.0:
        lp = left_panel(photos)
        cv = place(cv, lp, (FL[0] + FL[2]) / 2, (FL[1] + FL[3]) / 2, 0, shadow=0.6, blur=16, off=(10, 16))
    else:
        c = math.cos(th)
        if c > 0:                                         # front cover still over the right half, foreshortened
            fc = front_cover()
            wv = max(2, int((FR[2] - FR[0]) * c))
            fc = fc.resize((wv, fc.size[1]), Image.BILINEAR)
            sh = 1 - 0.5 * (1 - c)
            arr = np.asarray(fc, np.float32)
            arr[..., :3] *= sh
            cv.alpha_composite(Image.fromarray(arr.astype(np.uint8)), (FR[0], FR[1]))
        else:                                             # inner side landing on the left half
            lp = left_panel(photos)
            wv = max(2, int((FL[2] - FL[0]) * -c))
            lp = lp.resize((wv, lp.size[1]), Image.BILINEAR)
            arr = np.asarray(lp, np.float32)
            arr[..., :3] *= 0.6 + 0.4 * (-c)
            cv.alpha_composite(Image.fromarray(arr.astype(np.uint8)), (FL[2] - wv, FL[1]))
    if buttons:
        cvf = np.asarray(cv.convert("RGB"), np.float32) / 255.0
        b1 = U.word_sticker(["NEW CAMPAIGN"], 36, [U.FILL_PINK], seed=21, border=12)
        cvf = U.place(cvf, b1, 1590, 1030, angle=-2)
        b2 = U.word_sticker(["MAIN MENU"], 24, [("grad", (230, 230, 236), (170, 170, 182))], seed=22, border=10)
        cvf = U.place(cvf, b2, 1350, 1046, angle=3)
        cv = Image.fromarray((np.clip(cvf, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    return cv.convert("RGB")
