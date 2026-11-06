"""Round 14: corp-level slice identity.

Every corp has
  - a screen MATERIAL (skins.py, round 6),
  - a TYPE PANEL style: the framed widget on the screen's inner band where the type motif plays,
  - a MOTIF per slice type (ATTACK, CRITICAL, DEFEND, SHIELD, EVADE, HEAL, AFFLICT/special, MISS),
    drawn as one frame of a short loop (the loop is described in NOTES.md),
  - a faint type wash behind the read plate.
The white glyph + value block on the dark read plate stays universal (slicelib).

draw(ctx, im, corp, tier, phase) -> PIL RGB image. Texture space: y = 0 is the slice's outer edge,
x = W/2 is the slice midline, ctx.halfw(y) is the visible half width at row y.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from slicelib import PROGRAMS, CORPS, f_mono, f_ui, f_num

ACCENT = {
    "meridian": dict(a=(255, 140, 26), dim=(120, 60, 14), hot=(255, 46, 40), paper=(150, 138, 114), ink=(26, 20, 14)),
    "solace": dict(a=(150, 255, 70), dim=(50, 110, 20), hot=(255, 70, 150), paper=(240, 250, 226), ink=(16, 34, 8)),
    "halcyon": dict(a=(176, 110, 255), dim=(78, 40, 140), hot=(255, 50, 70), paper=(238, 224, 255), ink=(24, 10, 44),
                    gold=(255, 170, 40)),
    "orbital": dict(a=(205, 240, 255), dim=(60, 80, 130), hot=(255, 255, 255), paper=(244, 248, 255), ink=(4, 6, 18),
                    gold=(255, 215, 120)),
    "rebel_cell": dict(a=(255, 40, 52), dim=(110, 10, 18), hot=(255, 230, 230), paper=(255, 210, 210), ink=(20, 3, 6)),
}
PANEL_NAME = {"meridian": "shipping label", "solace": "frosted capsule", "halcyon": "blueprint title block",
              "orbital": "HUD brackets", "rebel_cell": "torn terminal"}


def kind_of(ctx):
    sp = getattr(ctx, "special", None)
    if sp:
        return "SPECIAL:" + sp
    return PROGRAMS[ctx.prog]["kind"]


# ------------------------------------------------------------------ panel (corp widget frame)
def panel_box(ctx):
    W, H, ss = ctx.W, ctx.H, ctx.ss
    y0, y1 = H * 0.585, H * 0.94
    hw = min(ctx.halfw(y1) * 0.9, 130 * ss)
    return (W / 2 - hw, y0, W / 2 + hw, y1)


def draw_panel(d, corp, box, ss, tier):
    x0, y0, x1, y1 = box
    A = ACCENT[corp]
    edge = A["a"] if tier != "elite" else (255, 205, 90)
    if corp == "meridian":  # shipping label: paper with a black top bar
        d.rectangle(box, fill=A["paper"] + (215,))
        d.rectangle([x0, y0, x1, y0 + 6 * ss], fill=(20, 16, 12, 255))
        d.text((x0 + 3 * ss, y0 - 0.5 * ss), "MRD // HANDLE WITH", font=f_mono(5 * ss), fill=A["a"] + (255,))
    elif corp == "solace":  # frosted capsule
        r = (y1 - y0) / 2
        d.rounded_rectangle(box, radius=r, fill=(190, 255, 230, 60), outline=A["a"] + (220,), width=max(1, int(1.5 * ss)))
        d.rounded_rectangle([x0 + 3 * ss, y0 + 2 * ss, x1 - 3 * ss, y0 + 6 * ss], radius=2 * ss, fill=(255, 255, 255, 60))
    elif corp == "halcyon":  # blueprint title block
        d.rectangle(box, fill=(10, 12, 50, 210), outline=A["paper"] + (230,), width=max(1, ss))
        d.line([(x0, y1 - 7 * ss), (x1, y1 - 7 * ss)], fill=A["paper"] + (180,), width=max(1, ss // 2 or 1))
        d.line([(x1 - 26 * ss, y1 - 7 * ss), (x1 - 26 * ss, y1)], fill=A["paper"] + (180,), width=max(1, ss // 2 or 1))
        d.text((x0 + 2 * ss, y1 - 6.5 * ss), "H-CIV DWG", font=f_mono(5 * ss), fill=A["paper"] + (230,))
    elif corp == "orbital":  # HUD corner brackets
        L = 8 * ss
        d.rectangle(box, fill=(6, 12, 40, 130))
        for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            d.line([(cx, cy + sy * L), (cx, cy), (cx + sx * L, cy)], fill=A["paper"] + (255,), width=max(1, int(1.5 * ss)))
    else:  # torn terminal
        d.rectangle(box, fill=(10, 0, 3, 220))
        rng = np.random.default_rng(int(x0) % 97)
        for k in range(5):
            yy = y0 + rng.random() * (y1 - y0)
            d.line([(x0, yy), (x0 + rng.random() * (x1 - x0) * 0.4, yy)], fill=A["a"] + (160,), width=max(1, ss))
        d.rectangle(box, outline=A["a"] + (200,), width=max(1, ss))
    if tier == "elite":
        d.rectangle([x0 - 2 * ss, y0 - 2 * ss, x1 + 2 * ss, y1 + 2 * ss], outline=edge + (255,), width=max(1, int(1.6 * ss)))


# ------------------------------------------------------------------ motif helpers
def chev(d, cx, cy, s, col, w, up=True):
    k = -1 if up else 1
    d.line([(cx - s, cy - k * s * 0.5), (cx, cy + k * s * 0.5), (cx + s, cy - k * s * 0.5)], fill=col, width=w, joint="curve")


def star(d, cx, cy, r, col, n=4):
    d.line([(cx - r, cy), (cx + r, cy)], fill=col, width=1)
    d.line([(cx, cy - r), (cx, cy + r)], fill=col, width=1)
    d.ellipse([cx - r * 0.25, cy - r * 0.25, cx + r * 0.25, cy + r * 0.25], fill=col)


# ------------------------------------------------------------------ MERIDIAN
def m_meridian(d, kind, b, ss, t, rng, A):
    x0, y0, x1, y1 = b
    W, Hh = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 3 * ss
    O, ink, hot = A["a"], A["ink"], A["hot"]
    lw = max(1, int(1.6 * ss))
    if kind == "ATTACK":  # pallet ram: crates race along a roller conveyor
        yb = y1 - 6 * ss
        d.line([(x0 + 2 * ss, yb), (x1 - 2 * ss, yb)], fill=ink + (255,), width=lw)
        for x in np.arange(x0 + 6 * ss, x1 - 4 * ss, 9 * ss):
            d.ellipse([x - 3 * ss, yb - 1 * ss, x + 3 * ss, yb + 5 * ss], outline=ink + (255,), width=max(1, ss))
        for k, xx in enumerate((cx - 26 * ss, cx + 10 * ss)):
            d.rectangle([xx, yb - 14 * ss, xx + 16 * ss, yb - 1 * ss], fill=O + (255,), outline=ink + (255,), width=max(1, ss))
            d.line([(xx + 8 * ss, yb - 14 * ss), (xx + 8 * ss, yb - 1 * ss)], fill=ink + (255,), width=max(1, ss))
            for s in range(3):
                d.line([(xx - (5 + s * 5) * ss, yb - (4 + s * 4) * ss), (xx - (1 + s * 5) * ss, yb - (4 + s * 4) * ss)], fill=ink + (200,), width=max(1, ss))
        chev(d, x1 - 12 * ss, yb - 9 * ss, 4 * ss, hot + (255,), lw, up=False)
    elif kind == "CRITICAL":  # PRIORITY stamp + laser fan over a barcode
        for x in np.arange(x0 + 6 * ss, x1 - 6 * ss, 2.6 * ss):
            if rng.random() < 0.7:
                d.line([(x, y0 + 9 * ss), (x, y1 - 6 * ss)], fill=ink + (255,), width=max(1, int(ss * rng.integers(1, 3) * 0.7)))
        for a in (-0.5, 0, 0.5):
            d.line([(cx, y0 + 7 * ss), (cx + a * W * 0.6, y1)], fill=hot + (220,), width=max(1, ss))
        f = f_num(int(13 * ss))
        s = "PRIORITY"
        tw = f.getlength(s)
        st = Image.new("RGBA", (int(tw + 10 * ss), int(18 * ss)), (0, 0, 0, 0))
        ds = ImageDraw.Draw(st)
        ds.rectangle([0, 0, st.width - 1, st.height - 1], outline=hot + (255,), width=max(1, int(1.5 * ss)))
        ds.text((5 * ss, 0), s, font=f, fill=hot + (255,))
        st = st.rotate(-12, expand=True, resample=Image.BICUBIC)
        return ("paste", st, (int(cx - st.width / 2), int(cy - st.height / 2)))
    elif kind == "DEFEND":  # container wall
        rows, bw, bh = 3, 22 * ss, 7.5 * ss
        for r in range(rows):
            off = (r % 2) * bw / 2
            for x in np.arange(x0 + 3 * ss - off, x1, bw):
                xa, xb = max(x0 + 3 * ss, x), min(x1 - 3 * ss, x + bw - 1.5 * ss)
                if xb - xa < 4 * ss:
                    continue
                yy = y0 + 9 * ss + r * (bh + 1.5 * ss)
                col = O if (r + int(x / bw)) % 3 else (60, 120, 170)
                d.rectangle([xa, yy, xb, yy + bh], fill=col + (255,), outline=ink + (255,), width=max(1, ss))
                for xc in np.arange(xa + 3 * ss, xb, 3 * ss):
                    d.line([(xc, yy + 1.5 * ss), (xc, yy + bh - 1.5 * ss)], fill=ink + (110,), width=max(1, ss // 2 or 1))
    elif kind == "SHIELD":  # shrink-wrap over a pallet
        d.rectangle([cx - 24 * ss, y0 + 11 * ss, cx + 24 * ss, y1 - 6 * ss], fill=O + (255,), outline=ink + (255,), width=max(1, ss))
        for k in range(-4, 6):
            xx = cx - 24 * ss + k * 10 * ss
            d.line([(xx, y1 - 6 * ss), (xx + 16 * ss, y0 + 11 * ss)], fill=(255, 255, 255, 120), width=int(2.4 * ss))
        d.rectangle([cx - 28 * ss, y1 - 6 * ss, cx + 28 * ss, y1 - 3 * ss], fill=ink + (255,))
    elif kind == "EVADE":  # reroute: lane with a hard detour arrow
        d.line([(x0 + 4 * ss, cy + 4 * ss), (x1 - 4 * ss, cy + 4 * ss)], fill=ink + (120,), width=int(2 * ss))
        d.line([(x0 + 6 * ss, cy + 4 * ss), (cx - 6 * ss, cy + 4 * ss), (cx - 6 * ss, y0 + 10 * ss), (x1 - 12 * ss, y0 + 10 * ss)],
               fill=O + (255,), width=int(3 * ss), joint="curve")
        d.polygon([(x1 - 6 * ss, y0 + 10 * ss), (x1 - 13 * ss, y0 + 5 * ss), (x1 - 13 * ss, y0 + 15 * ss)], fill=O + (255,))
        d.line([(cx + 4 * ss, cy), (cx + 14 * ss, cy + 8 * ss)], fill=hot + (255,), width=lw)
        d.line([(cx + 14 * ss, cy), (cx + 4 * ss, cy + 8 * ss)], fill=hot + (255,), width=lw)
    elif kind == "HEAL":  # restock: pallet + progress
        d.rectangle([x0 + 8 * ss, y0 + 12 * ss, x1 - 8 * ss, y0 + 18 * ss], outline=ink + (255,), width=max(1, ss))
        d.rectangle([x0 + 9 * ss, y0 + 13 * ss, x0 + 9 * ss + (x1 - x0 - 18 * ss) * 0.72, y0 + 17 * ss], fill=O + (255,))
        d.text((x0 + 8 * ss, y0 + 20 * ss), "RESTOCK 72%", font=f_mono(6 * ss), fill=ink + (255,))
    elif kind.startswith("SPECIAL"):  # tariff: a receipt printing out of a slot
        d.rectangle([cx - 30 * ss, y1 - 7 * ss, cx + 30 * ss, y1 - 3 * ss], fill=ink + (255,))
        d.polygon([(cx - 15 * ss, y1 - 7 * ss), (cx + 15 * ss, y1 - 7 * ss), (cx + 15 * ss, y0 + 8 * ss),
                   (cx + 10 * ss, y0 + 5 * ss), (cx + 5 * ss, y0 + 8 * ss), (cx, y0 + 5 * ss), (cx - 5 * ss, y0 + 8 * ss),
                   (cx - 10 * ss, y0 + 5 * ss), (cx - 15 * ss, y0 + 8 * ss)], fill=(255, 255, 250, 255), outline=ink + (255,))
        fm = f_mono(5 * ss)
        for i, s in enumerate(("TARIFF", "RAM -3", "$$ DUE")):
            d.text((cx - 13 * ss, y0 + 10 * ss + i * 6 * ss), s, font=fm, fill=(hot if i == 1 else ink) + (255,))
    else:  # MISS: empty conveyor, lost parcel outline
        yb = y1 - 6 * ss
        d.line([(x0 + 2 * ss, yb), (x1 - 2 * ss, yb)], fill=ink + (160,), width=lw)
        for k in range(0, 8):
            xx = cx - 12 * ss + k * 3 * ss
            if k % 2 == 0:
                d.line([(xx, yb - 16 * ss), (xx + 1.5 * ss, yb - 16 * ss)], fill=ink + (200,), width=max(1, ss))
        d.rectangle([cx - 12 * ss, yb - 16 * ss, cx + 12 * ss, yb - 1 * ss], outline=ink + (150,), width=max(1, ss))
        d.text((cx - 3 * ss, yb - 15 * ss), "?", font=f_num(int(13 * ss)), fill=ink + (200,))
    return None


# ------------------------------------------------------------------ SOLACE
def m_solace(d, kind, b, ss, t, rng, A):
    x0, y0, x1, y1 = b
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 1 * ss
    M, hot, paper = A["a"], A["hot"], A["paper"]
    lw = max(1, int(1.6 * ss))
    if kind == "ATTACK":  # injector
        d.rounded_rectangle([cx - 26 * ss, cy - 5 * ss, cx + 12 * ss, cy + 5 * ss], radius=2 * ss, fill=(220, 255, 240, 200), outline=M + (255,), width=lw)
        d.rectangle([cx - 24 * ss, cy - 3 * ss, cx - 4 * ss, cy + 3 * ss], fill=M + (255,))
        d.line([(cx + 12 * ss, cy), (cx + 28 * ss, cy)], fill=paper + (255,), width=lw)
        d.line([(cx - 32 * ss, cy - 7 * ss), (cx - 32 * ss, cy + 7 * ss)], fill=paper + (255,), width=int(2 * ss))
        for k in range(3):
            d.ellipse([cx + (31 + k * 5) * ss, cy - 1.5 * ss, cx + (34 + k * 5) * ss, cy + 1.5 * ss], fill=M + (255 - k * 70,))
    elif kind == "CRITICAL":  # overdose spike
        pts, x = [], x0 + 4 * ss
        while x < x1 - 4 * ss:
            u = (x - x0) / (x1 - x0)
            v = 0
            if 0.42 < u < 0.47:
                v = -16
            elif 0.47 < u < 0.52:
                v = 12
            elif 0.52 < u < 0.55:
                v = -6
            pts.append((x, cy + 3 * ss + v * ss))
            x += 1.2 * ss
        d.line(pts, fill=hot + (255,), width=int(2.2 * ss))
        d.text((x1 - 16 * ss, y0 + 3 * ss), "!!", font=f_num(int(12 * ss)), fill=hot + (255,))
    elif kind == "DEFEND":  # vial rack
        n = 6
        for k in range(n):
            xx = x0 + 8 * ss + k * (x1 - x0 - 16 * ss) / (n - 1)
            d.rounded_rectangle([xx - 3.5 * ss, y0 + 6 * ss, xx + 3.5 * ss, y1 - 6 * ss], radius=3.5 * ss, fill=(200, 255, 230, 90), outline=M + (255,), width=max(1, ss))
            lvl = y0 + (12 + (k * 5) % 9) * ss
            d.rounded_rectangle([xx - 2 * ss, lvl, xx + 2 * ss, y1 - 7.5 * ss], radius=2 * ss, fill=M + (255,))
        d.line([(x0 + 3 * ss, y1 - 4 * ss), (x1 - 3 * ss, y1 - 4 * ss)], fill=paper + (255,), width=lw)
    elif kind == "SHIELD":  # membrane
        for k in range(4):
            r = (8 + k * 7) * ss
            d.arc([cx - r * 1.5, cy - r + 6 * ss, cx + r * 1.5, cy + r + 6 * ss], 190, 350, fill=M + (255 - k * 50,), width=lw)
        d.ellipse([cx - 4 * ss, cy + 1 * ss, cx + 4 * ss, cy + 9 * ss], fill=M + (255,))
    elif kind == "HEAL":  # mitosis with + pulses
        for (xx, r) in ((cx - 9 * ss, 9 * ss), (cx + 9 * ss, 9 * ss)):
            d.ellipse([xx - r, cy - r, xx + r, cy + r], fill=(40, 160, 110, 120), outline=M + (255,), width=lw)
            d.ellipse([xx - 3 * ss, cy - 3 * ss, xx + 3 * ss, cy + 3 * ss], fill=M + (255,))
        for xx in (x0 + 8 * ss, x1 - 8 * ss):
            d.line([(xx - 4 * ss, cy), (xx + 4 * ss, cy)], fill=paper + (255,), width=int(2 * ss))
            d.line([(xx, cy - 4 * ss), (xx, cy + 4 * ss)], fill=paper + (255,), width=int(2 * ss))
    elif kind == "EVADE":  # capsule slips sideways with after-images
        for k in range(4):
            xx = cx - 18 * ss + k * 10 * ss
            al = 60 + k * 60
            d.rounded_rectangle([xx - 8 * ss, cy - 4 * ss, xx + 8 * ss, cy + 4 * ss], radius=4 * ss, fill=M + (al,))
    elif kind.startswith("SPECIAL"):  # dose: capsule drips into a cell that turns magenta
        d.rounded_rectangle([cx - 10 * ss, y0 + 4 * ss, cx + 10 * ss, y0 + 11 * ss], radius=3.5 * ss, fill=paper + (255,), outline=M + (255,))
        d.rectangle([cx, y0 + 4 * ss, cx + 10 * ss, y0 + 11 * ss], fill=hot + (255,))
        for k in range(2):
            yy = y0 + (14 + k * 4) * ss
            d.ellipse([cx - 1.5 * ss, yy, cx + 1.5 * ss, yy + 3 * ss], fill=hot + (255,))
        r = 9 * ss
        d.ellipse([cx - r * 1.4, y1 - 4 * ss - 2 * r, cx + r * 1.4, y1 - 4 * ss], fill=(120, 0, 50, 160), outline=hot + (255,), width=lw)
    else:  # MISS: flatline
        d.line([(x0 + 4 * ss, cy + 2 * ss), (x1 - 4 * ss, cy + 2 * ss)], fill=M + (180,), width=lw)
        d.text((cx - 14 * ss, y0 + 3 * ss), "NO PULSE", font=f_mono(5 * ss), fill=paper + (200,))
    return None


# ------------------------------------------------------------------ HALCYON
def m_halcyon(d, kind, b, ss, t, rng, A):
    x0, y0, x1, y1 = b
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 - 2 * ss
    V, hot, paper, gold = A["a"], A["hot"], A["paper"], A["gold"]
    lw = max(1, int(1.4 * ss))
    if kind == "ATTACK":  # demolition order: lots with red X
        for k in range(4):
            xx = x0 + 6 * ss + k * (x1 - x0 - 12 * ss) / 4
            w = (x1 - x0 - 12 * ss) / 4 - 2 * ss
            d.rectangle([xx, y0 + 5 * ss, xx + w, y1 - 11 * ss], outline=paper + (230,), width=max(1, ss))
            if k in (1, 2):
                d.line([(xx, y0 + 5 * ss), (xx + w, y1 - 11 * ss)], fill=hot + (255,), width=int(2 * ss))
                d.line([(xx + w, y0 + 5 * ss), (xx, y1 - 11 * ss)], fill=hot + (255,), width=int(2 * ss))
    elif kind == "CRITICAL":  # siren strobe
        w = (x1 - x0) / 2
        d.rectangle([x0 + 3 * ss, y0 + 4 * ss, cx, y1 - 10 * ss], fill=hot + (200,))
        d.rectangle([cx, y0 + 4 * ss, x1 - 3 * ss, y1 - 10 * ss], fill=(60, 120, 255, 200))
        f = f_num(int(10 * ss))
        s = "ENFORCE"
        d.text((cx - f.getlength(s) / 2, y0 + 5 * ss), s, font=f, fill=(255, 255, 255, 255))
    elif kind == "DEFEND":  # bollard line, plan view
        d.line([(x0 + 4 * ss, cy + 2 * ss), (x1 - 4 * ss, cy + 2 * ss)], fill=paper + (180,), width=max(1, ss))
        for x in np.arange(x0 + 8 * ss, x1 - 4 * ss, 9 * ss):
            d.ellipse([x - 3.2 * ss, cy - 1.2 * ss, x + 3.2 * ss, cy + 5.2 * ss], fill=V + (255,), outline=paper + (255,), width=max(1, ss))
    elif kind == "SHIELD":  # zoning perimeter
        bx = [x0 + 8 * ss, y0 + 4 * ss, x1 - 8 * ss, y1 - 11 * ss]
        for i in range(int((bx[2] - bx[0]) / (6 * ss))):
            xx = bx[0] + i * 6 * ss
            d.line([(xx, bx[1]), (xx + 3 * ss, bx[1])], fill=gold + (255,), width=lw)
            d.line([(xx, bx[3]), (xx + 3 * ss, bx[3])], fill=gold + (255,), width=lw)
        d.line([(bx[0], bx[1]), (bx[0], bx[3])], fill=gold + (255,), width=lw)
        d.line([(bx[2], bx[1]), (bx[2], bx[3])], fill=gold + (255,), width=lw)
        d.text((cx - 12 * ss, cy - 4 * ss), "ZONE R-2", font=f_mono(5 * ss), fill=paper + (255,))
    elif kind == "HEAL":  # utility restore: power line with lit nodes
        d.line([(x0 + 4 * ss, cy + 2 * ss), (x1 - 4 * ss, cy + 2 * ss)], fill=paper + (160,), width=max(1, ss))
        n = 5
        for k in range(n):
            xx = x0 + 8 * ss + k * (x1 - x0 - 16 * ss) / (n - 1)
            on = k < 3
            d.ellipse([xx - 3 * ss, cy - 1 * ss, xx + 3 * ss, cy + 5 * ss], fill=(gold if on else (40, 44, 90)) + (255,), outline=paper + (255,))
    elif kind == "EVADE":  # detour sign
        d.line([(x0 + 6 * ss, cy + 6 * ss), (cx - 4 * ss, cy + 6 * ss), (cx - 4 * ss, cy - 3 * ss), (x1 - 10 * ss, cy - 3 * ss)],
               fill=gold + (255,), width=int(2.4 * ss))
        d.polygon([(x1 - 4 * ss, cy - 3 * ss), (x1 - 11 * ss, cy - 8 * ss), (x1 - 11 * ss, cy + 2 * ss)], fill=gold + (255,))
    elif kind.startswith("SPECIAL"):  # citation ticket
        d.rectangle([cx - 22 * ss, y0 + 3 * ss, cx + 22 * ss, y1 - 10 * ss], fill=paper + (255,), outline=V + (255,), width=max(1, ss))
        for k in range(5):
            d.ellipse([cx - 22 * ss + k * 10 * ss, y0 + 1.5 * ss, cx - 19 * ss + k * 10 * ss, y0 + 4.5 * ss], fill=A["ink"] + (255,))
        d.text((cx - 19 * ss, y0 + 6 * ss), "FINE  §12", font=f_mono(6 * ss), fill=A["ink"] + (255,))
        d.text((cx + 4 * ss, y0 + 12 * ss), "PAID?", font=f_num(int(9 * ss)), fill=hot + (255,))
    else:  # MISS: permit pending
        d.rectangle([cx - 20 * ss, y0 + 4 * ss, cx + 20 * ss, y1 - 11 * ss], outline=paper + (130,), width=max(1, ss))
        d.text((cx - 16 * ss, cy - 3 * ss), "PENDING", font=f_mono(6 * ss), fill=paper + (180,))
    return None


# ------------------------------------------------------------------ ORBITAL
def m_orbital(d, kind, b, ss, t, rng, A):
    x0, y0, x1, y1 = b
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    B, hot, paper, gold = A["a"], A["hot"], A["paper"], A["gold"]
    lw = max(1, int(1.5 * ss))
    if kind == "ATTACK":  # kinetic strike: streaks into a reticle
        r = 7 * ss
        d.ellipse([cx + 8 * ss - r, cy - r, cx + 8 * ss + r, cy + r], outline=hot + (255,), width=lw)
        d.line([(cx + 8 * ss - r - 4 * ss, cy), (cx + 8 * ss + r + 4 * ss, cy)], fill=hot + (255,), width=max(1, ss))
        d.line([(cx + 8 * ss, cy - r - 4 * ss), (cx + 8 * ss, cy + r + 4 * ss)], fill=hot + (255,), width=max(1, ss))
        for k in range(3):
            d.line([(x0 + (6 + k * 6) * ss, y0 + 4 * ss), (cx + 2 * ss, cy - (2 - k * 2) * ss)], fill=paper + (220 - k * 50,), width=lw)
    elif kind == "CRITICAL":  # down-link beam + flare
        d.polygon([(cx - 4 * ss, y0), (cx + 4 * ss, y0), (cx + 12 * ss, y1), (cx - 12 * ss, y1)], fill=(255, 245, 210, 170))
        d.line([(cx, y0), (cx, y1)], fill=(255, 255, 255, 255), width=int(2 * ss))
        d.line([(x0 + 4 * ss, y1 - 6 * ss), (x1 - 4 * ss, y1 - 6 * ss)], fill=gold + (230,), width=lw)
    elif kind == "DEFEND":  # deflector hex panels
        r = 5 * ss
        for row in range(2):
            for k in range(-4, 5):
                xx = cx + k * r * 1.75 + (row % 2) * r * 0.87
                yy = y0 + 9 * ss + row * r * 1.5
                if xx < x0 + 4 * ss or xx > x1 - 4 * ss:
                    continue
                hx = [(xx + r * math.cos(math.radians(30 + 60 * j)), yy + r * math.sin(math.radians(30 + 60 * j))) for j in range(6)]
                d.polygon(hx, fill=(60, 110, 230, 200), outline=paper + (255,))
    elif kind == "SHIELD":  # rings round a planet limb
        r = 30 * ss
        d.ellipse([cx - r, y1 - 8 * ss, cx + r, y1 - 8 * ss + 2 * r], fill=(40, 70, 170, 255), outline=B + (255,), width=lw)
        for k in range(3):
            rr = r + (6 + k * 5) * ss
            d.arc([cx - rr * 1.3, y1 - 8 * ss - (6 + k * 5) * ss, cx + rr * 1.3, y1 - 8 * ss + 2 * rr], 190, 350, fill=paper + (220 - k * 60,), width=lw)
    elif kind == "HEAL":  # station-keeping trail with repair sparkle
        d.arc([x0 + 4 * ss, y0 + 4 * ss, x1 - 4 * ss, y1 + 18 * ss], 190, 350, fill=B + (255,), width=lw)
        star(d, cx + 10 * ss, y0 + 7 * ss, 5 * ss, (255, 255, 255, 255))
        d.line([(cx - 20 * ss, cy), (cx - 12 * ss, cy)], fill=gold + (255,), width=int(2 * ss))
        d.line([(cx - 16 * ss, cy - 4 * ss), (cx - 16 * ss, cy + 4 * ss)], fill=gold + (255,), width=int(2 * ss))
    elif kind == "EVADE":  # transfer orbit with burn arrows
        d.ellipse([x0 + 6 * ss, y0 + 4 * ss, x1 - 6 * ss, y1 - 4 * ss], outline=B + (255,), width=lw)
        d.ellipse([cx - 14 * ss, cy - 5 * ss, cx + 14 * ss, cy + 5 * ss], outline=paper + (150,), width=max(1, ss))
        d.polygon([(x1 - 8 * ss, cy), (x1 - 14 * ss, cy - 4 * ss), (x1 - 14 * ss, cy + 4 * ss)], fill=gold + (255,))
    elif kind.startswith("SPECIAL"):  # solar flare: corona
        r = 9 * ss
        for k in range(14):
            a = math.radians(k * 360 / 14)
            L = r * (1.6 + 0.6 * (k % 2))
            d.line([(cx + r * math.cos(a), cy + r * math.sin(a)), (cx + L * math.cos(a), cy + L * math.sin(a))], fill=gold + (255,), width=lw)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 240, 200, 255))
    else:  # MISS: no lock
        r = 8 * ss
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=paper + (130,), width=max(1, ss))
        d.text((cx - 12 * ss, cy + r + 1 * ss), "NO LOCK", font=f_mono(5 * ss), fill=paper + (170,))
    return None


# ------------------------------------------------------------------ REBEL_CELL (DISPATCH)
def m_rebel(d, kind, b, ss, t, rng, A):
    x0, y0, x1, y1 = b
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R, paper = A["a"], A["paper"]
    fm = f_mono(6 * ss)
    lines = {"ATTACK": ["> EXECUTE 0x0E", "> TARGET: CELL"], "CRITICAL": ["> ROOT ACCESS", "> OVERRIDE !!"],
             "DEFEND": ["> LOCKDOWN", "> PORTS SHUT"], "SHIELD": ["> SANDBOX/INV", "> HOLD"],
             "HEAL": ["> RESTORE IMG", "> 72%"], "EVADE": ["> REROUTE", "> GHOST NODE"], "MISS": ["> ORDER VOID", "> ..."]}
    ls = lines.get(kind, ["> ORDER 0x11", "> COMPLY"])
    for i, s in enumerate(ls):
        d.text((x0 + 4 * ss, y0 + 3 * ss + i * 7 * ss), s, font=fm, fill=(R if i == 0 else paper) + (255,))
    if kind == "CRITICAL":
        for k in range(3):
            yy = y0 + (18 + k * 3) * ss
            d.rectangle([x0 + rng.random() * 20 * ss, yy, x1 - rng.random() * 20 * ss, yy + 1.5 * ss], fill=R + (255,))
    elif kind == "DEFEND":
        for x in np.arange(x0 + 4 * ss, x1 - 6 * ss, 10 * ss):
            d.rectangle([x, y1 - 9 * ss, x + 8 * ss, y1 - 4 * ss], fill=R + (180,), outline=(255, 120, 120, 255))
    elif kind.startswith("SPECIAL"):
        f = f_num(int(10 * ss))
        s = "ORDER"
        d.rectangle([x1 - f.getlength(s) - 8 * ss, y1 - 13 * ss, x1 - 3 * ss, y1 - 3 * ss], outline=R + (255,), width=max(1, ss))
        d.text((x1 - f.getlength(s) - 5.5 * ss, y1 - 13.5 * ss), s, font=f, fill=R + (255,))
    elif kind == "ATTACK":
        for k in range(3):
            chev(d, x1 - (10 + k * 7) * ss, y1 - 8 * ss, 3 * ss, R + (255 - k * 60,), max(1, int(1.5 * ss)), up=False)
    # player-colour fringe tears
    for k, c in enumerate(((255, 61, 168), (92, 225, 255))):
        yy = y0 + rng.random() * (y1 - y0)
        d.line([(x0, yy), (x1, yy)], fill=c + (120,), width=max(1, ss))
    return None


class IntDraw:
    """ImageDraw proxy that rounds 'width' to int (motifs run at a fractional ss scale)."""

    def __init__(self, d):
        self.d = d

    def __getattr__(self, name):
        fn = getattr(self.d, name)

        def call(*a, **k):
            if "width" in k:
                k["width"] = max(1, int(round(k["width"])))
            if "radius" in k:
                k["radius"] = int(round(k["radius"]))
            return fn(*a, **k)
        return call


MOTIF = {"meridian": m_meridian, "solace": m_solace, "halcyon": m_halcyon, "orbital": m_orbital, "rebel_cell": m_rebel}


# ------------------------------------------------------------------ entry
def type_wash(im, ctx, col, k):
    """Faint type-colour wash from the outer edge so the material carries a type hint around the plate."""
    a = np.asarray(im, np.float32) / 255
    H = a.shape[0]
    y = np.linspace(0, 1, H)[:, None, None]
    w = np.clip(1 - y / 0.55, 0, 1) ** 2 * k
    a = a * (1 - w) + (np.array(col, np.float32) / 255) * w
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def overdrive(im, ctx, corp, rng):
    """Phase 3: the screen content intensifies (contrast, accent scan bands, flicker blocks)."""
    a = np.asarray(im, np.float32) / 255
    a = np.clip((a - 0.5) * 1.3 + 0.5 + 0.04, 0, 1)
    acc = np.array(ACCENT[corp]["a"], np.float32) / 255
    H, W = a.shape[:2]
    ss = ctx.ss
    for k in range(5):
        y = int(rng.integers(0, max(1, H - 4 * ss)))
        h = int(rng.integers(1, 4)) * ss
        a[y:y + h] = a[y:y + h] * 0.4 + acc * 0.7
    for k in range(10):
        x, y = int(rng.integers(0, W - 6 * ss)), int(rng.integers(0, H - 6 * ss))
        a[y:y + 3 * ss, x:x + int(rng.integers(3, 12)) * ss] = acc * (0.6 + 0.4 * rng.random())
    return Image.fromarray((a * 255).astype(np.uint8))


def draw(ctx, im, corp, tier="regular", phase=1):
    kind = kind_of(ctx)
    k = kind.split(":")[0] if kind.startswith("SPECIAL") else kind
    tcol = PROGRAMS[ctx.prog]["col"]
    im = type_wash(im, ctx, tcol, 0.16 if tier != "boss" else 0.10)
    rng = np.random.default_rng(31 + ctx.seed)
    if phase >= 3:
        im = overdrive(im, ctx, corp, rng)
    im = im.convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    box = panel_box(ctx)
    draw_panel(d, corp, box, ctx.ss, tier)
    res = MOTIF[corp](IntDraw(d), kind if not kind.startswith("SPECIAL") else "SPECIAL", box, ctx.ss * 1.3, ctx.t, rng, ACCENT[corp])
    if res and res[0] == "paste":
        ov.alpha_composite(res[1], res[2])
    im.alpha_composite(ov)
    return im.convert("RGB")
