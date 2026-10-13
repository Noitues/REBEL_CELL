"""Round 45 outputs.

python make45.py busy | hover | two | quiet | sheet | combat | compare
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ring45 as R
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import combat41 as C41
from slicelib import R_OUT, f_num, f_ui

W, H = 1920, 1080
OUT, SCR = R.OUT, R.SCR
PC = (481, 490)                          # player wheel centre at combat size (locked round 31)
YEL = (255, 214, 64)
GOLD = R.MODS["DOUBLE"]["tint"]

BUSY = [("DOUBLE", -32, 12), ("PIERCE", 12, 80), ("ENCRYPTED", 80, 128), ("BLANK", 128, 170),
        ("CORRUPT", 170, 250), ("OVERCLOCKED", 250, 292), ("BLANK", 292, 328)]
QUIET = [("BLANK", -60, 60), ("DOUBLE", 60, 180), ("PIERCE", 180, 300)]     # Breaker rank 1: x2 / Pierce / -
TWO = [("DOUBLE", -40, 40), ("PIERCE", 40, 160), ("BLANK", 160, 320)]

_cache = {}


def master(key, segs, mods, **kw):
    if key not in _cache:
        _cache[key] = R.wheel(segs, mods, **kw)
    return _cache[key]


def put_wheel(canvas, img, cc, r_px, centre, shadow=True):
    a, ac, k = R.scaled(img, cc, r_px)
    ox, oy = int(centre[0] - ac[0]), int(centre[1] - ac[1])
    if shadow:
        sh = Image.new("RGBA", a.size, (0, 0, 0, 0))
        sh.putalpha(a.split()[3].point(lambda v: int(v * 0.5)).filter(ImageFilter.GaussianBlur(10 * r_px / 220)))
        canvas.alpha_composite(sh, (ox + 6, oy + 12))
    canvas.alpha_composite(a, (ox, oy))
    return k


def backdrop():
    clean, _ = C41.base_plate()
    return clean.convert("RGBA")


def two_panel(img, cc, title, sub, hover=None):
    """Left: combat size (r 220) at the locked position. Right: 2x close-up (r 440) of the same region."""
    bd = backdrop()
    out = Image.new("RGBA", (W, H), (8, 7, 12, 255))
    left = bd.crop((0, 0, 960, 1080))
    k1 = put_wheel(left, img, cc, 220, PC)
    x0, y0 = 241, 160
    right = bd.crop((x0, y0, x0 + 480, y0 + 540)).resize((960, 1080), Image.LANCZOS)
    c2 = ((PC[0] - x0) * 2, (PC[1] - y0) * 2)
    k2 = put_wheel(right, img, cc, 440, c2)
    if hover:
        hover(left, PC, k1, 1.0)
        hover(right, c2, k2, 2.0)
    out.alpha_composite(left, (0, 0))
    out.alpha_composite(right, (960, 0))
    d = ImageDraw.Draw(out)
    d.line([(960, 0), (960, H)], fill=(255, 214, 64, 255), width=3)
    R.label(out, 14, 12, title)
    R.small(out, 16, 52, sub)
    R.label(out, 974, 12, "2x CLOSE-UP", px=20)
    R.label(out, 14, H - 44, "1:1 COMBAT SIZE  r = 220  (1080p, text 1.0)", px=20)
    return out


# ------------------------------------------------------------------ hover overlays
def hover(img, c, k, s, mods, title, lines, tip=True):
    """Plate at the wedge's outer edge, the cursor on the wedge, the tooltip right of the wheel (1x only)."""
    import math
    box = R.plate(img, c[0], c[1], k, mods)
    a = math.radians(-19)
    R.cursor(img, int(c[0] + 312 * k * math.sin(a)), int(c[1] - 312 * k * math.cos(a)), s)
    if tip:
        R.tooltip(img, c[0] + 219 * s, box[3] + 8 * s, title, lines, R.MODS[mods[0]]["tint"], s)


BUSY_TIP = ("INNER RING  //  SHIM 6", [(u"×2 DOUBLE   6 -> 12", GOLD), "covers 70%: whole slice",
                                         ("E next: PIERCE", (170, 175, 190)), ("Q/E INNER: turn ring", (170, 175, 190))])
TWO_TIP = ("2 MODIFIERS  //  SHIM 6", [(u"1 ×2 DOUBLE  inner ring", GOLD),
                                        ("2 CORRUPT   from card", R.MODS["CORRUPT"]["tint"]),
                                        "inner band = 1st", ("6 -> 12, then CORRUPTED", (170, 175, 190))])


def hover_busy(img, c, k, s):
    hover(img, c, k, s, ["DOUBLE"], BUSY_TIP[0], BUSY_TIP[1], tip=s == 1.0)


def hover_two(img, c, k, s):
    hover(img, c, k, s, ["DOUBLE", "CORRUPT"], TWO_TIP[0], TWO_TIP[1], tip=s == 1.0)


# ------------------------------------------------------------------ outputs
def busy(hover=False):
    img, cc, info = master("busy", BUSY, ["DOUBLE"])
    out = two_panel(img, cc, "BUSY RING" + ("  //  HOVERED" if hover else ""),
                    "x2 DOUBLE in effect on SHIM 6; the DOUBLE segment covers only 70% of the slice (PIERCE covers the rest)."
                    if not hover else "Words on demand: one plate at the wedge's outer edge + the tooltip, only while hovered / aiming.",
                    hover_busy if hover else None)
    if not hover:  # strip: the ring turned (E INNER) -> the wedge follows the segment under the needle
        d = ImageDraw.Draw(out)
        d.rectangle([0, 800, 959, 1030], fill=(8, 7, 12, 235))
        d.line([(0, 800), (959, 800)], fill=YEL + (255,), width=2)
        R.small(out, 16, 806, "Q / E INNER turns the ring; the wedge follows whichever segment is under the needle (shown at 0.5x):", (255, 214, 64), 16)
        for j, (rot, cap) in enumerate(((0, "now: x2 DOUBLE"), (-50, "E: PIERCE in effect"), (45, "Q: blank under needle - no wedge"))):
            segs = [(kk, a0 + rot, a1 + rot) for kk, a0, a1 in BUSY]
            im2, cc2, _ = master("busy%d" % rot, segs, None if rot == 45 else (["DOUBLE"] if rot == 0 else ["PIERCE"]))
            cx = 165 + j * 315
            k = put_wheel(out, im2, cc2, 110, (cx, 1030 - 12), shadow=False) if False else None
            a, ac, kk = R.scaled(im2, cc2, 110)
            crop = a.crop((int(ac[0] - 125), int(ac[1] - 125), int(ac[0] + 125), int(ac[1] + 40)))
            out.alpha_composite(crop, (cx - 125, 836))
            R.small(out, cx - 120, 1004, cap, (220, 220, 230), 15)
    name = "busy_ring_hover.png" if hover else "busy_ring.png"
    out.convert("RGB").save(os.path.join(OUT, name))
    print(name, flush=True)


def two():
    img, cc, info = master("two", TWO, ["DOUBLE", "CORRUPT"])
    out = two_panel(img, cc, "TWO MODIFIERS: SPLIT WEDGE  //  HOVERED",
                    "Inner band x2 DOUBLE, outer band CORRUPT (max 2). One plate; the tooltip lists both in order.", hover_two)
    out.convert("RGB").save(os.path.join(OUT, "two_mods.png"))
    print("two_mods.png", flush=True)


def quiet():
    img, cc, info = master("quiet", QUIET, None)
    out = two_panel(img, cc, "QUIET RING: NOTHING IN EFFECT",
                    "Breaker rank 1 ring (x2 / Pierce / -) with the blank segment under the needle: no wedge, only the notches.")
    out.convert("RGB").save(os.path.join(OUT, "quiet_ring.png"))
    print("quiet_ring.png", flush=True)


def sheet():
    types = [("RED ATTACK  SHIM 6", -60.0), ("TEAL DEFEND  DEFRAG 5", -240.0)]
    rows = [None] + R.ORDER
    k1, k2 = 220 / R_OUT, 440 / R_OUT
    box = (-196, -372, 196, -96)       # master, around the top slice
    w1, h1 = int((box[2] - box[0]) * k1), int((box[3] - box[1]) * k1)
    w2, h2 = int((box[2] - box[0]) * k2), int((box[3] - box[1]) * k2)
    LW, top, gap = 300, 110, 22
    rowh = h2 + gap
    SW = 1920
    SH = top + rowh * len(rows) + 20
    out = Image.new("RGBA", (SW, SH), (14, 13, 20, 255))
    d = ImageDraw.Draw(out)
    R.label(out, 14, 12, "PATTERN SHEET  //  every modifier at 1:1 and 2:1 on an attack and a shield slice")
    R.small(out, 16, 52, "wedge: shade 25% + tint wash 10% + 3 px tint edge;  marks at 24% (halved under the read block) over a 30% ink halo", (200, 205, 220), 16)
    for t_i, (tname, prog) in enumerate(types):
        xb = LW + t_i * (w1 + w2 + 60)
        d.text((xb, top - 34), tname + "   1:1  |  2:1", font=f_ui(18, b"Bold SemiCondensed"), fill=(240, 240, 250))
    for r_i, kind in enumerate(rows):
        y = top + r_i * rowh
        if kind:
            m = R.MODS[kind]
            d.rounded_rectangle([14, y + 10, LW - 14, y + 120], radius=8, fill=(10, 9, 16), outline=m["tint"], width=2)
            d.text((28, y + 18), kind, font=f_num(28), fill=m["tint"])
            d.text((28, y + 54), m["family"] + " / " + m["rule"], font=f_ui(13, b"SemiBold"), fill=(200, 205, 220))
            d.text((28, y + 76), "tint #%02X%02X%02X" % m["tint"], font=f_ui(15, b"SemiBold"), fill=(200, 205, 220))
            d.text((28, y + 96), "mark %s" % m["kind"], font=f_ui(15, b"SemiBold"), fill=(200, 205, 220))
        else:
            d.text((28, y + 18), "NONE", font=f_num(28), fill=(200, 200, 210))
            d.text((28, y + 54), "the slice, no modifier", font=f_ui(14, b"SemiBold"), fill=(200, 205, 220))
        for t_i, (tname, prog) in enumerate(types):
            segs = [(kind or "BLANK", -30, 30), ("BLANK", 30, 330)]
            img, cc, _ = R.wheel(segs, [kind] if kind else None, rot=prog, typical=False)
            reg = img.crop((int(cc[0] + box[0]), int(cc[1] + box[1]), int(cc[0] + box[2]), int(cc[1] + box[3])))
            a = reg.resize((w1, h1), Image.LANCZOS)
            b = reg.resize((w2, h2), Image.LANCZOS)
            xb = LW + t_i * (w1 + w2 + 60)
            out.alpha_composite(a, (xb, y + (h2 - h1) // 2))
            out.alpha_composite(b, (xb + w1 + 20, y))
            print("sheet", kind, tname, flush=True)
    out.convert("RGB").save(os.path.join(OUT, "pattern_sheet.png"))
    print("pattern_sheet.png", flush=True)


def combat():
    import combat42 as C42
    import combat44 as C44
    orig = C42.wheel
    img, cc, info = master("busy", BUSY, ["DOUBLE"])

    def wheel(spec, sat, worst, is_player, r_px, rot=0.0, hover=None, pop=1.0, lod=False):
        if not is_player:
            return orig(spec, sat, worst, is_player, r_px, rot, hover, pop, lod)
        yy, xx = np.mgrid[0:img.height, 0:img.width].astype(np.float32)
        outside = np.hypot(xx - cc[0], yy - cc[1]) > 360 * 1.15 + 4
        al = np.asarray(img.split()[3], np.float32) / 255 * outside
        a, ac, k = R.scaled(img, cc, r_px)
        alim = Image.fromarray((al * 255).astype(np.uint8)).resize(a.size, Image.BILINEAR)
        return a, ac, alim

    C42.wheel = wheel
    for hov in (False, True):
        shot, off, hits = C44.screen(False, tip=False, marks=False)
        if hov:
            hover_busy(shot, PC, 220 / R_OUT, 1.0)
        R.label(shot, W - 560, H - 44, "ROUND 45 IN COMBAT  //  round 41 typical v4" + ("  //  hovered" if hov else ""), px=20)
        name = "in_combat_hover.png" if hov else "in_combat.png"
        shot.convert("RGB").save(os.path.join(OUT, name))
        print(name, flush=True)
    C42.wheel = orig


def compare():
    src = Image.open(r"D:\Godot\rebel_cell\docs\art_review\PLAN1\W1B_W2_GROUP.jpg").convert("RGBA")
    y0 = 14150
    before = src.crop((0, y0, 785, y0 + 990))
    after = src.crop((815, y0, 1600, y0 + 990))
    s = 0.6
    pw, ph = int(785 * s), int(990 * s)
    img, cc, _ = master("busy", BUSY, ["DOUBLE"])
    out = Image.new("RGBA", (pw * 4 + 50, ph + 120), (10, 9, 14, 255))
    bd = backdrop()
    panels = []
    for hov in (False, True):
        # build-sheet scale: the build wheel's frame (r ~350 px on the sheet) <-> concept frame
        r_sheet = 304
        cv = Image.new("RGBA", (785, 990), (0, 0, 0, 255))
        cv.alpha_composite(bd.crop((90, 120, 875, 1110)) if False else bd.crop((0, 0, 785, 990)).resize((785, 990)))
        cen = (392, 640)
        k = put_wheel(cv, img, cc, r_sheet, cen)
        if hov:
            hover(cv, cen, k, k / (220 / R_OUT), ["DOUBLE"], BUSY_TIP[0], BUSY_TIP[1], tip=False)
        panels.append(cv)
    caps = [("CURRENT BUILD: before", "tiny icons, illegible", (255, 90, 90)),
            ("CURRENT BUILD: after W2-A5/A6", "standing plates hit slices + hub name", (255, 90, 90)),
            ("ROUND 45 CONCEPT", "ghost wedge + pattern, lit segment", (123, 224, 123)),
            ("ROUND 45 CONCEPT, hovered", "words on demand: plate + tooltip", (123, 224, 123))]
    for j, im in enumerate([before, after] + panels):
        x = 10 + j * (pw + 10)
        out.alpha_composite(im.resize((pw, ph), Image.LANCZOS), (x, 100))
        R.label(out, x, 14, caps[j][0], col=caps[j][2], px=20)
        R.small(out, x + 4, 56, caps[j][1], (220, 220, 230), 16)
    out.convert("RGB").save(os.path.join(OUT, "compare.jpg"), quality=92)
    print("compare.jpg", flush=True)


def hover_busy_small(img, c, k):
    s = k / (220 / R_OUT)
    box = R.plate(img, c[0], c[1], k, ["DOUBLE"])
    R.cursor(img, int((box[0] + box[2]) / 2 - 10 * s), int(box[1] + 22 * s), s)
    lines = [(u"\u00d72 DOUBLE  output x2: SHIM 6 -> 12", GOLD), "covers 70% - applies to all of it"]
    R.tooltip(img, 300, 40, "INNER RING // ON SHIM 6", lines, GOLD, s)


if __name__ == "__main__":
    os.makedirs(SCR, exist_ok=True)
    for w in sys.argv[1:]:
        {"busy": lambda: busy(False), "hover": lambda: busy(True), "two": two, "quiet": quiet, "sheet": sheet,
         "combat": combat, "compare": compare}[w]()
    print("done")
