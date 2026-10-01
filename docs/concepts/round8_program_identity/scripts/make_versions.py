"""Round 7 deliverables. python make_versions.py [render|compose|all]"""
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
from slicelib import PROGRAMS, CORPS, f_num, f_ui, f_mono, bloom, to_img, R_OUT
import roster as RS
import roster_wheel as RW
import versions as V
import mascots as M

SUBJECTS = ["breaker", "route_optimizer", "the_manifest"]
SUBJ_NAME = {"breaker": "BREAKER (player)", "route_optimizer": "ROUTE OPTIMIZER (Meridian regular)",
             "the_manifest": "THE MANIFEST (Meridian boss)"}
VNAME = {0: "CURRENT (round 6)", 1: "V1  PROGRAM CARTRIDGES", 2: "V2  LIVING PROGRAMS", 3: "V3  MIXED MEDIA"}
VACC = {0: (200, 200, 210), 1: (255, 61, 168), 2: (92, 225, 255), 3: (255, 176, 60)}
VDESC = {
    1: ["Slices: every program has its own cartridge shell moulded in its colour, and its own silhouette:",
        "  FIREWALL brick teeth / VIRUS organic cell edge / EXPLOIT cracked jagged edge / SANDBOX riveted box",
        "  + corner brackets / PROXY offset double frame / PATCH taped seam / TROJAN gift band + bow /",
        "  ZERO-DAY glowing seal / NULL broken, unplugged frame. A 'NAME.exe' tab sits on each rim edge.",
        "Border: a sculpted ring. Breaker = heavy riveted plates + crowbar clamp; Meridian = corrugated band,",
        "  container corner-castings and twist-locks; boss = armoured segments.",
        "Boss extra: an outer orbit of armoured satellite modules, each showing one of its programs."],
    2: ["Slices: a signature mascot lives in every screen as a watermark behind the glyph:",
        "  FIREWALL brick golem / ZERO-DAY skull / VIRUS worm / TROJAN horse / PROXY mask / PATCH bandage-heart /",
        "  EXPLOIT cracked padlock / SANDBOX cube-with-a-face / NULL unplugged plug. (In motion each one acts:",
        "  the golem stomps on hits, the worm crawls and eats pixels, the padlock springs on the injected line.)",
        "Border: a live readout strip. The bezel is a thin screen scrolling class/corp telemetry",
        "  (CELL-9 // BREAKER // RIG OK ...) with emblem badges at the free cardinal points.",
        "Boss extra: a projected hologram crown (face, halo, corp emblem) + a 2nd concentric ring of its programs."],
    3: ["Slices: each C screen sits in its own physical housing: anodised metal in the program colour,",
        "  brushed, with a hard bevel, 4 screws, vent slots and an engraved MOD-<PROGRAM> plate.",
        "Border (player): a salvaged ring: vinyl stickers, scratches, tape and a grease-pencil tally.",
        "Border (enemy): a clean machined corporate ring, engraved name, corp logo, orange pattern band.",
        "Boss extra: conduits plugged into the bezel from off-screen, two power gauges on the rim and",
        "  a 3-lamp phase meter built into the rim (P1 lit)."],
}


def specs():
    b, _ = RS.class_spec("breaker")
    b["key"] = "breaker"
    r, _ = RS.enemy_spec("route_optimizer")
    r["key"] = "route_optimizer"
    m, _, _ = RS.boss_specs("meridian")
    m["key"] = "the_manifest"
    return {"breaker": b, "route_optimizer": r, "the_manifest": m}


def render_all():
    os.makedirs(CACHE, exist_ok=True)
    sp = specs()
    for k, s in sp.items():
        for v in (0, 1, 2, 3):
            t0 = time.time()
            if v == 0:
                hero, lod = RW.render(s, ss=2), RW.render(s, ss=1, lod=True)
            else:
                hero, lod = V.render_v(s, v, ss=2), V.render_v(s, v, ss=1, lod=True)
            hero.save(os.path.join(CACHE, "%s_v%d.png" % (k, v)))
            lod.save(os.path.join(CACHE, "%s_v%d_lod.png" % (k, v)))
            print(k, v, round(time.time() - t0, 1), flush=True)
    # program strips (all 9 programs per version, player theme)
    for v in (1, 2, 3):
        for p in ["EXPLOIT", "ZERO-DAY", "FIREWALL", "SANDBOX", "PROXY", "PATCH", "VIRUS", "TROJAN", "NULL"]:
            val = PROGRAMS[p]["val"]
            V.render_tile(p, val, v, ss=2, scale=0.5).save(os.path.join(CACHE, "tile_v%d_%s.png" % (v, p)))
        print("tiles", v, flush=True)


def load(name):
    im = Image.open(os.path.join(CACHE, name + ".png")).convert("RGBA")
    return im.crop(im.getbbox())


def fit(im, w, h):
    k = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)


def scale_r(im, r, base=R_OUT):
    k = r / base
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)


def background(W, H, tint, seed=3):
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
                    d.rectangle([wx, wy, wx + 8, wy + 10], fill=(55, 50, 75))
        x += bw + int(rng.integers(6, 30))
    city = np.asarray(city.filter(ImageFilter.GaussianBlur(5)), np.float32) / 255
    yy2, xx2 = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.exp(-(((xx2 - W * 0.35) / (W * 0.45)) ** 2 + ((yy2 - H * 0.45) / (H * 0.6)) ** 2))[..., None]
    arr = arr + city * 0.7 + g * (np.array(tint, np.float32) / 255) * 0.10
    return to_img(arr)


def paste(dst, im, x, y):
    dst.paste(im, (int(x), int(y)), im)


def grey(im):
    a = im.split()[3]
    g = ImageOps.grayscale(im.convert("RGB")).convert("RGBA")
    g.putalpha(a)
    return g


def acc_of(k):
    return (255, 61, 168) if k == "breaker" else CORPS["meridian"]["col"]


# ----------------------------------------------------------------- per-version files
def compose_versions():
    for v in (1, 2, 3):
        for k in SUBJECTS:
            im = background(1920, 1080, acc_of(k), seed=v * 7 + SUBJECTS.index(k))
            w = fit(load("%s_v%d" % (k, v)), 1120, 1060)
            paste(im, w, 20 + (1120 - w.width) / 2, 10 + (1060 - w.height) / 2)
            im = bloom(im, 1, 0.4, 0.62)
            d = ImageDraw.Draw(im)
            x = 1170
            d.text((x, 24), VNAME[v], font=f_num(54), fill=VACC[v])
            d.text((x + 2, 88), SUBJ_NAME[k], font=f_ui(24, b"Bold SemiCondensed"), fill=(235, 235, 245))
            y = 128
            for ln in VDESC[v]:
                for sub in textwrap.wrap(ln, 72, subsequent_indent="  ") or [""]:
                    d.text((x + 2, y), sub, font=f_mono(14, False), fill=(200, 200, 210))
                    y += 19
            y += 10
            d.text((x + 2, y), "ALL 9 PROGRAMS IN THIS VERSION", font=f_ui(18, b"Bold SemiCondensed"), fill=VACC[v])
            y += 28
            progs = ["EXPLOIT", "ZERO-DAY", "FIREWALL", "SANDBOX", "PROXY", "PATCH", "VIRUS", "TROJAN", "NULL"]
            cw = 245
            for i, p in enumerate(progs):
                t = load("tile_v%d_%s" % (v, p))
                t = fit(t, cw - 10, 150)
                cx = x + (i % 3) * cw
                cy = y + (i // 3) * 190
                paste(im, t, cx + (cw - t.width) / 2, cy)
                lab = p if v != 2 else "%s: %s" % (p, M.MASCOT_OF[p])
                f = f_ui(15, b"Bold Condensed")
                d.text((cx + cw / 2 - f.getlength(lab) / 2, cy + 156), lab, font=f, fill=PROGRAMS[p]["col"])
            im.save(os.path.join(OUT, "v%d_%s.png" % (v, k)))
            print("v", v, k, flush=True)


# ----------------------------------------------------------------- compare grid
def compose_compare():
    cell_w, cell_h = 640, 660
    lw = 240
    W, H = lw + 4 * cell_w, 150 + 3 * (cell_h + 20)
    im = background(W, H, (255, 140, 26), seed=99)
    d = ImageDraw.Draw(im)
    d.text((30, 18), "ROUND 7  -  SPINNER VERSIONS SIDE BY SIDE", font=f_num(56), fill=(255, 255, 255))
    d.text((34, 84), "same three subjects, real content data | rows: Breaker / Route Optimizer / The Manifest | columns: current, V1, V2, V3",
           font=f_mono(18, False), fill=(190, 190, 200))
    for c in range(4):
        x = lw + c * cell_w
        f = f_num(34)
        d.text((x + cell_w / 2 - f.getlength(VNAME[c]) / 2, 112), VNAME[c], font=f, fill=VACC[c])
    for r, k in enumerate(SUBJECTS):
        y = 160 + r * (cell_h + 20)
        d.rectangle([0, y, 8, y + cell_h], fill=acc_of(k))
        for i, ln in enumerate(textwrap.wrap(SUBJ_NAME[k], 14)):
            d.text((24, y + cell_h / 2 - 40 + i * 40), ln, font=f_num(34), fill=acc_of(k))
        for c in range(4):
            w = fit(load("%s_v%d" % (k, c)), cell_w - 20, cell_h - 10)
            paste(im, w, lw + c * cell_w + (cell_w - w.width) / 2, y + (cell_h - w.height) / 2)
    for c in range(1, 4):
        x = lw + c * cell_w
        d.line([(x, 150), (x, H - 10)], fill=(60, 60, 70), width=2)
    im = bloom(im, 1, 0.3, 0.65)
    im.convert("RGB").save(os.path.join(OUT, "compare.jpg"), quality=88)


def compose_bosses():
    cw, ch = 1000, 1250
    W, H = 3 * cw, ch + 260
    im = background(W, H, CORPS["meridian"]["col"], seed=77)
    d = ImageDraw.Draw(im)
    d.text((30, 18), "THE MANIFEST  -  three boss treatments", font=f_num(56), fill=(255, 255, 255))
    labs = {1: "V1: orbit of armoured satellite modules", 2: "V2: hologram crown + 2nd ring of programs",
            3: "V3: conduits, power gauges, phase meter in the rim"}
    for i, v in enumerate((1, 2, 3)):
        w = fit(load("the_manifest_v%d" % v), cw - 30, ch - 20)
        paste(im, w, i * cw + (cw - w.width) / 2, 100 + (ch - w.height))
        f = f_num(36)
        d.text((i * cw + cw / 2 - f.getlength(VNAME[v]) / 2, H - 120), VNAME[v], font=f, fill=VACC[v])
        f2 = f_ui(22, b"SemiBold")
        d.text((i * cw + cw / 2 - f2.getlength(labs[v]) / 2, H - 72), labs[v], font=f2, fill=(220, 220, 230))
    im = bloom(im, 1, 0.35, 0.62)
    im.convert("RGB").save(os.path.join(OUT, "v_bosses_compare.jpg"), quality=88)


def compose_small():
    cell_w = 560
    lw = 220
    W, H = lw + 4 * cell_w, 170 + 3 * 560
    im = background(W, H, (92, 225, 255), seed=55)
    im = to_img(np.asarray(im, np.float32) / 255 * 0.7)
    d = ImageDraw.Draw(im)
    d.text((30, 18), "SMALL + GREY  -  every version at r = 60 (small variant), plus greyscale", font=f_num(48), fill=(255, 255, 255))
    d.text((34, 78), "each cell: r = 60 colour | r = 60 greyscale | below: hero render in greyscale at r = 140",
           font=f_mono(17, False), fill=(190, 190, 200))
    for c in range(4):
        f = f_num(30)
        d.text((lw + c * cell_w + cell_w / 2 - f.getlength(VNAME[c]) / 2, 116), VNAME[c], font=f, fill=VACC[c])
    for r, k in enumerate(SUBJECTS):
        y = 160 + r * 560
        for i, ln in enumerate(textwrap.wrap(SUBJ_NAME[k], 14)):
            d.text((24, y + 200 + i * 36), ln, font=f_num(30), fill=acc_of(k))
        for c in range(4):
            x = lw + c * cell_w
            lod = load("%s_v%d_lod" % (k, c))
            base = R_OUT * (1.2 if k == "the_manifest" else 1.0)
            s60 = scale_r(lod, 60 * (1.2 if k == "the_manifest" else 1.0), base * (1.2 if k == "the_manifest" else 1.0))
            s60 = scale_r(lod, 60)
            paste(im, s60, x + 20, y + 10)
            paste(im, grey(s60), x + 40 + s60.width, y + 10)
            hero = grey(scale_r(load("%s_v%d" % (k, c)), 140))
            hero = fit(hero, cell_w - 30, 340) if hero.width > cell_w - 30 or hero.height > 340 else hero
            paste(im, hero, x + (cell_w - hero.width) / 2, y + 205)
    im.save(os.path.join(OUT, "small_and_grey.png"))


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    t0 = time.time()
    if what in ("render", "all"):
        render_all()
    if what in ("compose", "all"):
        compose_versions()
        compose_compare()
        compose_bosses()
        compose_small()
    print("done", what, round(time.time() - t0, 1))
