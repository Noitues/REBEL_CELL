"""Round 16 build.

python make_round16.py preview          # preview_A2.png
python make_round16.py corp <corp>      # corp_<corp>.png + motion_<corp>.gif
python make_round16.py compare          # corps_compare.jpg (5 bosses x phases 1-3 + Halcyon / Orbital squint test)
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
SCR = os.path.join(OUT, "scratch")
RC = os.path.join(SCR, "r")

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import frames as F
import d4corp as D
import specs14 as S
import tiles as TL
import kits16 as K
import motifs as MO
import skins as SK
import slicelib as SL
import roster_wheel as RW
from slicelib import f_num, f_ui, f_mono

W, H = 1920, 1080
BG = (16, 15, 22)
CORPS5 = ["meridian", "solace", "halcyon", "orbital", "rebel_cell"]
TITLE = {"meridian": "MERIDIAN FREIGHT SYSTEMS", "solace": "SOLACE BIOSYSTEMS", "halcyon": "HALCYON CIVIC",
         "orbital": "ORBITAL COMMONS", "rebel_cell": "REBEL_CELL"}
NOTE = {
    "meridian": "Every animation stays above the preset barcode strip. Animations are upright on every slice. HQ note (out of scope): cranes.",
    "solace": "Syringe point inside the slice; beaker pours straight down into a test tube; round cells split apart; capsules keep falling.",
    "halcyon": "Palette pushed to violet + amber civic (away from Orbital). ATTACK: three options. CRIT: the door just closes. MISS: option A.",
    "orbital": "Palette pushed to cold cyan + white space (away from Halcyon). SOLAR FLARE: the flare flies off, a new one forms.",
    "rebel_cell": "The player's slices in red. SHIELD reworked (QUARANTINE hex barrier); DEFEND: attacks fall from the outer arc onto an inner wall.",
}
TIER_TXT = {1: "I  primary border", 2: "II  secondary / threat border", 3: "III  inset line + hatched gap"}


def cached(name, spec, ss=1, hp_number=False, preview=None):
    os.makedirs(RC, exist_ok=True)
    p, j = os.path.join(RC, name + ".png"), os.path.join(RC, name + ".json")
    if os.path.exists(p) and os.path.exists(j):
        m = json.load(open(j))
        return Image.open(p).convert("RGBA"), tuple(m["c"]), m["meta"], m["ss"]
    im, c, meta = D.render(spec, ss=ss, hp_number=hp_number, preview=preview)
    im.save(p)
    json.dump(dict(c=c, meta=meta, ss=ss), open(j, "w"))
    print("rendered", name, flush=True)
    return im, c, meta, ss


def place_box(sheet, im, c, ss, box, r_want, valign=0.5):
    x0, y0, x1, y1 = box
    r = r_want
    while True:
        a, ac = F.fit(im, c, ss, r)
        if max(ac[0], a.width - ac[0]) * 2 <= (x1 - x0) and a.height <= (y1 - y0):
            break
        r *= 0.96
    cx = (x0 + x1) / 2
    top = y0 + ((y1 - y0) - a.height) * valign
    sheet.alpha_composite(a, (int(cx - ac[0]), int(top)))
    return r


def city_tile(w, h, seed=3, k=0.32):
    src = Image.open(os.path.join(OUT, "..", "round6_city_restyle", "views", "restyle_night_full.png")).convert("RGB")
    rng = np.random.default_rng(seed)
    x = int(rng.integers(0, max(1, src.width - w)))
    y = int(rng.integers(0, max(1, src.height - h)))
    t = src.crop((x, y, x + w, y + h)).filter(ImageFilter.GaussianBlur(3))
    return Image.fromarray((np.asarray(t, np.float32) * k).astype(np.uint8)).convert("RGBA")


def label(d, x, y, t, col=(225, 225, 235), size=18):
    d.text((x, y), t, font=f_ui(size, b"Bold SemiCondensed"), fill=col)


def mono(d, x, y, lines, col=(200, 200, 212), size=14, lh=18):
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=f_mono(size, False), fill=col)


def wrap(s, n):
    out, cur = [], ""
    for w_ in s.split():
        if cur and len(cur) + len(w_) + 1 > n:
            out.append(cur)
            cur = w_
        else:
            cur = (cur + " " + w_).strip()
    out.append(cur)
    return out


# ================================================================== preview A2
def preview_sheet():
    Sh = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(Sh)
    d.rectangle([0, 0, 8, 64], fill=(255, 214, 64))
    d.text((26, 6), "CARD-PLAY PREVIEW  A2  -  ghost blades for every needle, drones ride their slice", font=f_num(42), fill=(255, 255, 255))
    d.text((26, 56), "Hover HEAVY SPIN 9: a spin turns the slices clockwise, so each needle lands 9 ticks anticlockwise and each "
                     "docked drone ends 9 ticks clockwise. No arrowheads, no aim pips, no gates.", font=f_mono(15, False), fill=(185, 185, 200))
    Sh.alpha_composite(city_tile(1180, 990, 7), (10, 84))
    s, m = S.boss("halcyon", 2)
    s = copy.deepcopy(s)
    s["drones"] = [dict(name="Civic Drone", hp=5), dict(name="Civic Drone", hp=5)]
    s["drone_angles"] = [98, 296]
    s["full_blades"] = True
    s["variant"] = "pvA2"
    im, c, mm, ss = cached("pvA2_civic", s, preview=dict(style="A2", moves=9), hp_number=True)
    place_box(Sh, im, c, ss, (14, 110, 1186, 1070), 250)
    label(d, 24, 92, "THE CIVIC CORE  P2  -  3 needles (0 / 10 / 20), 2 docked Civic Drones", (255, 214, 64), 20)
    x0 = 1200
    Sh.alpha_composite(city_tile(710, 470, 17), (x0, 84))
    P0 = S.player()
    P1 = copy.deepcopy(P0)
    P1["drones"] = [dict(name="Drone", hp=5)]
    P1["drone_angles"] = [148]
    P1["variant"] = "drone"
    im1, c1, _, ss1 = cached("pvA2_player", P0, preview=dict(style="A2", moves=1))
    place_box(Sh, im1, c1, ss1, (x0 + 4, 112, x0 + 352, 548), 118)
    label(d, x0 + 10, 92, "PLAYER  FLICK 1 (one needle)", (235, 235, 245), 16)
    im2, c2, _, ss2 = cached("pvA2_player_drone", P1, preview=dict(style="A2", moves=9))
    place_box(Sh, im2, c2, ss2, (x0 + 358, 112, x0 + 706, 548), 118)
    label(d, x0 + 366, 92, "PLAYER  HEAVY SPIN 9 + a docked drone", (235, 235, 245), 16)
    lines = [
        "RULES",
        "- every needle: the same full ghost blade, value window",
        "  in the landing slice's colour; a small index tab",
        "  (1 / 2 / 3) on each blade when there are several",
        "- the real needles get the same index tabs",
        "- landing slices: dashed outline in the slice colour",
        "- trace: plain line OUTSIDE the rim, from a dot at",
        "  the needle to its ghost blade (no arrowheads: they",
        "  fought the threat ring's red chevrons)",
        "- docked drones ride their slice: a dashed ghost drone",
        "  where it ENDS UP + a dashed trace along the drone",
        "  orbit (corp colour), tagged 'ENDS HERE'",
        "- no aim pips, no gates",
    ]
    for i, ln in enumerate(lines):
        d.text((x0 + 10, 570 + i * 26), ln, font=f_mono(16, False), fill=(255, 214, 64) if ln == "RULES" else (205, 205, 218))
    Sh.convert("RGB").save(os.path.join(OUT, "preview_A2.png"))
    print("preview_A2", flush=True)


# ================================================================== corp sheet + gif
def material_swatch(corp, w, h, ss=2):
    ctx = SL.Ctx(w * ss, h * ss, 0.4, ss, 60.0, 2000.0 * ss, (255, 255, 255), corp, "EXPLOIT", 3)
    ctx.opts = {}
    ctx.special = None
    return SK.SKINS[corp](ctx, np.random.default_rng(11)).resize((w, h), Image.LANCZOS).convert("RGBA")


def crest_img(corp, size=150):
    cr = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gl = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    F.set_centre()
    D.crest(cr, ImageDraw.Draw(cr), ImageDraw.Draw(gl), 1, size / 2, size / 2, size * 0.34, corp, MO.ACCENT[corp]["a"], RW.CORP_EMBLEM[corp])
    out = gl.filter(ImageFilter.GaussianBlur(10))
    out.alpha_composite(cr)
    return out


FRAMES4 = (0.0, 0.25, 0.5, 0.75)


def corp_sheet(corp):
    A = MO.ACCENT[corp]
    acc = A["a"]
    Sh = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(Sh)
    d.rectangle([0, 0, 8, 64], fill=acc)
    d.text((26, 4), TITLE[corp], font=f_num(44), fill=(255, 255, 255))
    d.text((26, 52), NOTE[corp], font=f_mono(15, False), fill=(185, 185, 200))
    kit = K.KIT[corp]
    rows_n = (len(kit) + 1) // 2
    row_h = 512 / rows_n
    tsc = min(0.47, (row_h - 26) / 263)
    for k, (prog, val, sp, sk, lab, desc) in enumerate(kit):
        col, row = k % 2, k // 2
        x0, y0 = 20 + col * 950, int(80 + row * row_h)
        frames = [TL.tile(prog, val, sp, corp, ss=2, scale=tsc, seed=k + 3, t=t, scene_kind=sk, corp_tier=1) for t in FRAMES4]
        label(d, x0, y0, lab, acc, 16)
        x = x0
        for fi, fr in enumerate(frames):
            Sh.alpha_composite(fr, (x, y0 + 20))
            x += fr.width + 4
        mono(d, x + 10, y0 + 24, wrap(desc, 28), size=13, lh=17)
    yk = 600
    d.line([(20, yk - 6), (1900, yk - 6)], fill=(60, 60, 74), width=1)
    label(d, 24, yk, "SCREEN MATERIAL", acc, 15)
    Sh.alpha_composite(material_swatch(corp, 200, 110), (24, yk + 22))
    label(d, 250, yk, "CREST", acc, 15)
    Sh.alpha_composite(crest_img(corp, 150), (236, yk + 10))
    label(d, 24, yk + 142, "ACCENTS", acc, 15)
    for i, (nm, c_) in enumerate([(n, A[n]) for n in ("a", "dim", "hot", "paper", "gold") if n in A]):
        y = yk + 164 + i * 24
        d.rounded_rectangle([24, y, 56, y + 18], radius=4, fill=c_, outline=(10, 8, 16))
        d.text((64, y + 1), {"a": "accent", "dim": "dim", "hot": "hot / threat", "paper": "paper", "gold": "gold"}[nm] + "  #%02X%02X%02X" % c_,
               font=f_mono(12, False), fill=(205, 205, 218))
    label(d, 24, yk + 292, "SLICE TIERS (corp palette)", acc, 15)
    p, v, sp_, sk, lab, desc = kit[0]
    for ti in (1, 2, 3):
        t_ = TL.tile(p, v, sp_, corp, ss=2, scale=0.36, seed=3, t=0.5, scene_kind=sk, corp_tier=ti)
        x = 24 + (ti - 1) * 148
        Sh.alpha_composite(t_, (x, yk + 316))
        mono(d, x, yk + 316 + t_.height + 2, wrap(TIER_TXT[ti], 18), size=11, lh=13)
    reg_id, eli_id = S.PICKS[corp]
    reg = S.enemy(reg_id, corp, "regular")
    eli = S.enemy(eli_id, corp, "elite")
    b1, bm = S.boss(corp, 1)
    reg[0]["corp_tier"], eli[0]["corp_tier"], b1["corp_tier"] = 1, 2, 3
    jobs = [("%s_reg" % corp, reg[0], "REGULAR  " + reg[1]["name"].upper() + "  (tier I)"),
            ("%s_eli" % corp, eli[0], "ELITE  " + eli[1]["name"].upper() + "  (tier II)"),
            ("%s_p1" % corp, b1, "BOSS  " + bm["name"].upper() + "  (tier III)")]
    for k, (name, spec, title) in enumerate(jobs):
        bx0 = 480 + k * 476
        Sh.alpha_composite(city_tile(470, 470, 30 + k), (bx0, yk))
        im, c, m, ss = cached(name, spec, hp_number=True)
        place_box(Sh, im, c, ss, (bx0 + 4, yk + 26, bx0 + 466, yk + 468), 150, valign=1.0)
        label(d, bx0 + 8, yk + 4, title, acc if k == 2 else (255, 255, 255), 16)
    Sh.convert("RGB").save(os.path.join(OUT, "corp_%s.png" % corp))
    print("corp sheet", corp, flush=True)
    motion_gif(corp)


def motion_gif(corp, n=12):
    kit = K.KIT[corp]
    cols = 4 if len(kit) <= 8 else 5
    rows = (len(kit) + cols - 1) // cols
    frames = []
    for fi in range(n):
        t = fi / n
        tl = [TL.tile(p, v, sp, corp, ss=1, scale=0.5, seed=k + 3, t=t, scene_kind=sk, corp_tier=1) for k, (p, v, sp, sk, lab, desc) in enumerate(kit)]
        tw, th = tl[0].width, tl[0].height
        im = Image.new("RGBA", (cols * (tw + 8) + 8, rows * (th + 26) + 8), BG + (255,))
        dd = ImageDraw.Draw(im)
        for k, t_ in enumerate(tl):
            x, y = 8 + (k % cols) * (tw + 8), 8 + (k // cols) * (th + 26)
            dd.text((x + 4, y), kit[k][4], font=f_ui(14, b"Bold SemiCondensed"), fill=MO.ACCENT[corp]["a"])
            im.alpha_composite(t_, (x, y + 18))
        frames.append(im.convert("RGB").quantize(colors=160, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
    p = os.path.join(OUT, "motion_%s.gif" % corp)
    frames[0].save(p, save_all=True, append_images=frames[1:], duration=110, loop=0, optimize=True)
    print("gif", corp, os.path.getsize(p) // 1024, "KB", flush=True)


# ================================================================== compare + squint
def compare():
    Wc, Hc = 1920, 1720
    Sh = Image.new("RGBA", (Wc, Hc), BG + (255,))
    d = ImageDraw.Draw(Sh)
    d.text((20, 6), "ROUND 16  BOSSES  -  phase 1 / 2 / 3, upright corp animations, corp tier III borders", font=f_num(38), fill=(255, 255, 255))
    for i, corp in enumerate(CORPS5):
        x0 = 8 + i * 382
        Sh.alpha_composite(city_tile(374, 1330, 90 + i), (x0, 60))
        label(d, x0 + 8, 64, TITLE[corp], MO.ACCENT[corp]["a"], 20)
        for row, ph in enumerate((1, 2, 3)):
            spec = S.boss(corp, ph)[0]
            spec["corp_tier"] = 3
            im, c, m, ss = cached("%s_p%d" % (corp, ph), spec, hp_number=True)
            place_box(Sh, im, c, ss, (x0 + 2, 92 + row * 436, x0 + 372, 520 + row * 436), 120)
            d.text((x0 + 10, 96 + row * 436), "P%d" % ph, font=f_num(24), fill=(255, 214, 64))
    # squint test: all five regulars small, sharp and blurred (Halcyon vs Orbital must separate)
    y0 = 1400
    d.line([(20, y0 - 6), (1900, y0 - 6)], fill=(60, 60, 74), width=1)
    label(d, 24, y0, "SQUINT TEST  -  regular wheels at r = 46: sharp (left) and blurred 'from afar' (right). Halcyon = violet + amber, Orbital = cold cyan + white.", (255, 214, 64), 18)
    strip = Image.new("RGBA", (920, 270), (24, 22, 30, 255))
    for i, corp in enumerate(CORPS5):
        reg_id, _ = S.PICKS[corp]
        spec = S.enemy(reg_id, corp, "regular")[0]
        spec["corp_tier"] = 1
        im, c, m, ss = cached("%s_reg" % corp, spec, hp_number=True)
        place_box(strip, im, c, ss, (i * 184, 10, i * 184 + 184, 240), 46)
        ImageDraw.Draw(strip).text((i * 184 + 92, 250), corp.upper(), font=f_ui(15, b"Bold SemiCondensed"), fill=MO.ACCENT[corp]["a"], anchor="mm")
    Sh.alpha_composite(strip, (20, y0 + 30))
    blur = strip.resize((strip.width // 6, strip.height // 6), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.6)).resize(strip.size, Image.BILINEAR)
    Sh.alpha_composite(blur, (980, y0 + 30))
    Sh.convert("RGB").save(os.path.join(OUT, "corps_compare.jpg"), quality=90)
    print("compare", flush=True)


if __name__ == "__main__":
    what = sys.argv[1]
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    if what == "preview":
        preview_sheet()
    elif what == "corp":
        corp_sheet(arg)
    elif what == "compare":
        compare()
    print("done", flush=True)
