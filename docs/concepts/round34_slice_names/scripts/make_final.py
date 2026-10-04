"""Round 17 final package:
  ../glyphs/*.png          every final glyph, 256 px, white on transparent, snake_case names
  ../glyphs/index.txt      file -> glyph id -> meaning (+ aliases)
  ../tiers_final.png       tiers V2 (locked) on every program + a corporation-palette example
  ../slice_system_final.png one-sheet summary of the locked slice system
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
CACHE = os.path.join(OUT, "scratch", "final")

import numpy as np
from PIL import Image, ImageDraw, ImageOps
import slicelib as SL
import slicekit as K
import overlays as O
import glyph_catalog as C
import glyphs17 as G
import make_glyphs as MG
from make_tiers import cvd, grey
from slicelib import f_num, f_ui, f_mono, bloom, PROGRAMS, ORDER

VALUES = {"EXPLOIT": (6, 8, 10), "ZERO-DAY": (12, 15, 18), "FIREWALL": (5, 7, 9), "SANDBOX": (8, 10, 12),
          "PROXY": (4, 5, 6), "PATCH": (3, 4, 6), "VIRUS": (3, 4, 5), "TROJAN": (1, 2, 3), "NULL": (None, None, None)}


def snake(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


# ------------------------------------------------------------------ glyph export
def export_glyphs():
    d = os.path.join(OUT, "glyphs")
    os.makedirs(d, exist_ok=True)
    done = {}
    rows = []
    groups = [("slice", C.PROGRAMS), ("special", C.SPECIALS), ("placeholder", C.PLACEHOLDERS),
              ("status", [s for s in C.STATUSES if s[4] != "predicted"]), ("state", C.STATES), ("picto", C.PICTOS)]
    for prefix, items in groups:
        for it in items:
            gid, label, meaning = it[0], it[1], it[2]
            res = G.resolve(gid)
            if res in done:
                rows.append(("(alias) " + prefix + "_" + snake(label.split("(")[0]), gid, "uses " + done[res]))
                continue
            name = prefix + "_" + snake(label.split("(")[0])
            m = SL.glyph_mask(gid).resize((256, 256), Image.LANCZOS)
            im = Image.new("RGBA", (256, 256), (255, 255, 255, 0))
            im.putalpha(m)
            im.save(os.path.join(d, name + ".png"))
            done[res] = name + ".png"
            rows.append((name + ".png", gid, meaning))
    with open(os.path.join(d, "index.txt"), "w", encoding="utf-8") as f:
        f.write("# Round 17 final glyphs: 256 px, white on transparent (alpha = coverage). file | glyph id | meaning\n")
        for r in rows:
            f.write("%s | %s | %s\n" % r)
    n = len([r for r in rows if not r[0].startswith("(alias)")])
    print("exported", n, "glyphs", flush=True)
    return rows


# ------------------------------------------------------------------ tiers_final
def tiers_final():
    os.makedirs(CACHE, exist_ok=True)
    K.TIER_STYLE, K.TIER_STRENGTH = "a", 2
    W = 2000
    tiles = {}
    for p in ORDER:
        for k in (1, 2, 3):
            tiles[(p, k)] = K.tile(p, VALUES[p][k - 1], t=0.45, tier=k, scale=0.4, seed=ORDER.index(p) + 2)
    corp = {k: K.tile("EXPLOIT", (7, 9, 11)[k - 1], t=0.45, tier=k, scale=0.56, theme="meridian", seed=4) for k in (1, 2, 3)}
    cw_spec = [("EXPLOIT", 7, 1, None, "meridian"), ("FIREWALL", 6, 2, None, "meridian"), ("EXPLOIT", 11, 3, None, "meridian"),
               ("SANDBOX", 8, 1, None, "meridian"), ("ZERO-DAY", 14, 2, None, "meridian"), ("NULL", None, 1, None, "meridian")]
    cwh = K.wheel(cw_spec, t=0.45, r_px=110)
    pw = K.wheel([(p, VALUES[p][k - 1], k, None) for p, k in zip(["EXPLOIT", "FIREWALL", "PROXY", "VIRUS", "ZERO-DAY", "PATCH"], (3, 1, 2, 1, 3, 2))], t=0.45, r_px=60)
    t0 = tiles[("EXPLOIT", 1)]
    H = 130 + 3 * (t0.height + 8) + 60 + corp[1].height + 120
    im = Image.new("RGBA", (W, H), (11, 10, 16, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        d.line([(0, y), (W, y)], fill=(14, 13, 20))
    d.text((40, 18), "SLICE TIERS  (final: option a, V2 strong)", font=f_num(52), fill=(255, 255, 255))
    d.text((44, 80), "placeholder (not in game).  I: matte bezel, screen 60 %.  II: steel bezel + 2.2 px bright line inset with a 10 px gap.  "
           "III: gold bezel + a solid gold strip + heavy gold cross-hatch filling the gap, screen 142 %.  Outline identical; pips 1/2/3.",
           font=f_mono(13, False), fill=(255, 170, 110))
    cw = t0.width + 6
    for j, p in enumerate(ORDER):
        d.text((110 + j * cw + 10, 112), p, font=f_ui(15, b"Bold SemiCondensed"), fill=PROGRAMS[p]["col"])
    y = 134
    for k in (1, 2, 3):
        d.text((44, y + t0.height // 2 - 20), ["I", "II", "III"][k - 1], font=f_num(40), fill=(220, 220, 230))
        for j, p in enumerate(ORDER):
            im.alpha_composite(tiles[(p, k)], (110 + j * cw, y))
        y += t0.height + 8
    # vision strip for EXPLOIT
    vx = 110 + 9 * cw + 20
    d.text((vx, 112), "grey / deutan / protan", font=f_ui(15, b"Bold SemiCondensed"), fill=(220, 220, 230))
    for k in (1, 2, 3):
        for j, fn in enumerate((grey, lambda i: cvd(i, "deutan"), lambda i: cvd(i, "protan"))):
            t = fn(tiles[("VIRUS", k)]).resize((int(t0.width * 0.6), int(t0.height * 0.6)), Image.LANCZOS)
            im.alpha_composite(t, (vx + j * (t.width + 4), 134 + (k - 1) * (t0.height + 8) + 20))
    im.alpha_composite(pw, (vx + 40, y - 10))
    d.text((vx + 60, y - 10 + pw.height), "r = 60 mixed", font=f_mono(12, False), fill=(170, 170, 182))
    # corp example
    y += 30
    d.text((44, y), "CORPORATION PALETTE EXAMPLE  (Meridian Freight skin: same tier rules, the type colour stays on the trim/line)",
           font=f_ui(20, b"Bold SemiCondensed"), fill=(255, 140, 26))
    y += 34
    x = 44
    for k in (1, 2, 3):
        im.alpha_composite(corp[k], (x, y))
        d.text((x + corp[k].width // 2 - 10, y + corp[k].height - 4), ["I", "II", "III"][k - 1], font=f_num(28), fill=(255, 190, 120))
        x += corp[k].width + 14
    im.alpha_composite(cwh, (x + 30, y - 20))
    d.text((x + 50, y - 20 + cwh.height), "r = 110 Meridian wheel, tiers I/II/III mixed", font=f_mono(12, False), fill=(170, 170, 182))
    out = bloom(im.convert("RGB"), 1, 0.25, 0.66)
    out = out.crop((0, 0, W, max(y + corp[1].height + 40, y - 20 + cwh.height + 30)))
    out.save(os.path.join(OUT, "tiers_final.png"))
    print("saved tiers_final.png", out.size, flush=True)


# ------------------------------------------------------------------ slice_system_final
def system_final():
    K.TIER_STYLE, K.TIER_STRENGTH = "a", 2
    W, H = 2400, 1480
    im = Image.new("RGBA", (W, H), (11, 10, 16, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        d.line([(0, y), (W, y)], fill=(14, 13, 20))
    d.text((40, 18), "REBEL_CELL  SLICE SYSTEM  v2  (round 34 program names)", font=f_num(56), fill=(255, 255, 255))
    d.text((44, 106), "Programs renamed (round 34): EXPLOIT->SHIV  ZERO-DAY->OVERFLOW  FIREWALL->BURNWALL  PROXY->DETOUR  PATCH->HOTFIX  VIRUS->INFECT;  "
           "SANDBOX, TROJAN, NULL kept.  Glyphs, screens, tiers and overlays unchanged.", font=f_mono(14, False), fill=(255, 214, 64))
    d.text((44, 84), "Screens & Data slices: a live CRT screen per slice in its own bezel; an upright white glyph + value on a read plate; tier flair inside the border; "
           "state overlays as a separate layer under the read block.", font=f_mono(14, False), fill=(190, 190, 200))

    def head(x, y, t, c):
        d.rectangle([x - 14, y + 4, x - 8, y + 32], fill=c)
        d.text((x, y), t, font=f_num(32), fill=c)

    # 1 glyph excerpt
    head(40, 128, "1  GLYPHS  (excerpt; full set in glyph_set.png, files in glyphs/)", (255, 214, 64))
    items = C.PROGRAMS + C.SPECIALS[:5]
    for i, it in enumerate(items):
        x, y = 40 + i * 156, 170
        t = MG.mark_at(it, 76, "glyph")
        im.alpha_composite(t, (x, y))
        for k, px in enumerate((24, 16)):
            g = MG.mark_at(it, px + 6, "glyph")
            im.alpha_composite(g, (x + 84, y + 6 + k * 36))
        d.text((x, y + 82), it[1], font=f_ui(14, b"Bold SemiCondensed"), fill=it[3])
    y2 = 290
    st = C.STATUSES[:5] + C.STATES
    for i, it in enumerate(st):
        x = 40 + i * 156
        b = MG.badge(it[0], 60, it[3], it[4])
        im.alpha_composite(b, (x, y2))
        d.text((x + 66, y2 + 20), it[1], font=f_ui(13, b"Bold SemiCondensed"), fill=it[3])
    pic = ["PI_SPIN_CW", "PI_NUDGE", "PI_NUDGE_INNER", "PI_RESPIN", "PI_FLIP", "PI_DRAW", "PI_RAM", "PI_BREACH", "PI_UNDOCK", "PI_EXHAUST"]
    for i, gid in enumerate(pic):
        x = 40 + i * 120
        t = MG.tile(56, (150, 150, 170))
        g = MG.glyph(gid, 44)
        t.alpha_composite(g, ((56 - g.width) // 2, (56 - g.height) // 2))
        im.alpha_composite(t, (x, 372))
    mo = MG.picto("PI_MOMENTUM", "^2/5", 50)
    t = MG.tile(56, (150, 150, 170))
    t.alpha_composite(mo, (0, 0))
    im.alpha_composite(t, (40 + 10 * 120, 372))
    mo = MG.picto("PI_MOMENTUM", "2/^5", 50)
    t = MG.tile(56, (150, 150, 170))
    t.alpha_composite(mo, (0, 0))
    im.alpha_composite(t, (40 + 11 * 120 - 50, 372))
    d.text((40 + 10 * 120, 432), "MOMENTUM: big = runs", font=f_mono(11, False), fill=(170, 170, 182))
    # 2 tiers V2
    head(40, 470, "2  TIERS  (V2 strong)", (255, 214, 64))
    x = 40
    for k in (1, 2, 3):
        t = K.tile("EXPLOIT", VALUES["EXPLOIT"][k - 1], t=0.45, tier=k, scale=0.68)
        im.alpha_composite(t, (x, 512))
        d.text((x + t.width // 2 - 10, 512 + t.height - 6), ["I", "II", "III"][k - 1], font=f_num(28), fill=(220, 220, 230))
        x += t.width + 8
    # 3 player firewall
    head(x + 40, 470, "3  PLAYER BURNWALL (DEFEND)", (92, 225, 255))
    fw = K.tile("FIREWALL", 5, t=0.3, tier=2, scale=0.8)
    im.alpha_composite(fw, (x + 40, 512))
    d.text((x + 50, 512 + fw.height - 2), "shots fall from the rim onto a wall by the hub", font=f_mono(12, False), fill=(170, 170, 182))
    # system wheel
    sw = K.wheel([("EXPLOIT", 10, 3, None), ("FIREWALL", 7, 2, None), ("PROXY", 4, 1, "FROZEN"), ("VIRUS", 4, 2, None),
                  ("ZERO-DAY", 12, 1, "OVERCLOCKED"), ("SANDBOX", 12, 3, "ENCRYPTED")], t=0.3, r_px=170)
    im.alpha_composite(sw, (W - sw.width - 30, 440))
    d.text((W - sw.width, 440 + sw.height - 4), "r = 170: tiers + states together", font=f_mono(12, False), fill=(170, 170, 182))
    # 4 state overlays (locked)
    head(40, 815, "4  STATE OVERLAYS  (locked: separate layer, under the read block)", (255, 77, 77))
    trios = {"CORRUPTED": "EXPLOIT", "OVERCLOCKED": "ZERO-DAY", "ENCRYPTED": "FIREWALL", "PARASITE": "PATCH",
             "FROZEN": "PROXY", "LOCKED": "SANDBOX", "BURNING": "EXPLOIT", "EMPOWERED": "VIRUS"}
    vals = {"EXPLOIT": 6, "ZERO-DAY": 12, "FIREWALL": 5, "PATCH": 3, "PROXY": 4, "SANDBOX": 8, "VIRUS": 3}
    for i, stt in enumerate(O.ORDER):
        p = trios[stt]
        t = K.tile(p, vals[p], t=0.3, tier=2, state=stt, scale=0.72, seed=4)
        x = 40 + (i % 4) * 590
        y = 866 + (i // 4) * 300
        im.alpha_composite(t, (x, y))
        gid, kind, bcol, real = O.STATE_INFO[stt]
        bb = MG.badge(gid, 30, bcol, kind)
        im.alpha_composite(bb, (x + t.width + 6, y + 40))
        d.text((x + t.width + 42, y + 44), stt, font=f_ui(20, b"Bold SemiCondensed"), fill=bcol)
        d.text((x + t.width + 8, y + 76), "status" if real else "placeholder", font=f_mono(11, False), fill=(150, 220, 150) if real else (255, 150, 90))
    out = bloom(im.convert("RGB"), 1, 0.25, 0.66)
    out.save(os.path.join(OUT, "slice_system_final_v2.png"))
    print("saved slice_system_final_v2.png", out.size, flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("glyphs", "all"):
        export_glyphs()
    if what in ("tiers", "all"):
        tiers_final()
    if what in ("system", "all"):
        system_final()
