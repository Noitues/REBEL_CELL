"""Round 14 build.

python make_round14.py preview            # preview_indicator.png
python make_round14.py corp <corp>        # corp_<corp>.png (renders cached in ../scratch/r)
python make_round14.py compare            # corps_compare.jpg (needs the corp renders)
python make_round14.py combat <corp>      # combat_<corp>.png
"""
import json
import math
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
import motifs as MO
import skins as SK
import slicelib as SL
import roster as RS
import roster_wheel as RW
from slicelib import f_num, f_ui, f_mono, R_OUT, PROGRAMS, CORPS

W, H = 1920, 1080
BG = (16, 15, 22)
CORPS5 = ["meridian", "solace", "halcyon", "orbital", "rebel_cell"]


# ------------------------------------------------------------------ cache
def cached(name, spec, ss=1, lod=False, hp_number=False, preview=None, banner_on=True):
    os.makedirs(RC, exist_ok=True)
    p, j = os.path.join(RC, name + ".png"), os.path.join(RC, name + ".json")
    if os.path.exists(p) and os.path.exists(j):
        m = json.load(open(j))
        return Image.open(p).convert("RGBA"), tuple(m["c"]), m["meta"], m["ss"]
    im, c, meta = D.render(spec, ss=ss, lod=lod, hp_number=hp_number, preview=preview, banner_on=banner_on)
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
    return r, (cx, top + ac[1]), a.height


def city_tile(w, h, seed=3, k=0.36, tint=(1.0, 1.0, 1.0)):
    src = Image.open(os.path.join(OUT, "..", "round6_city_restyle", "views", "restyle_night_full.png")).convert("RGB")
    rng = np.random.default_rng(seed)
    x = int(rng.integers(0, max(1, src.width - w)))
    y = int(rng.integers(0, max(1, src.height - h)))
    t = src.crop((x, y, x + w, y + h)).filter(ImageFilter.GaussianBlur(3))
    a = np.asarray(t, np.float32) * k * np.array(tint, np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def label(d, x, y, t, col=(225, 225, 235), size=18, anchor="la"):
    d.text((x, y), t, font=f_ui(size, b"Bold SemiCondensed"), fill=col, anchor=anchor)


def mono(d, x, y, lines, col=(200, 200, 212), size=14, lh=18, hl=None):
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=f_mono(size, False), fill=(hl if (hl and ln.startswith(("P2", "P3", "+"))) else col))


# ================================================================== preview indicator
STYLES = [
    ("ghost", "A  GHOST BLADE", ["hollow dashed blade + ghost window at the landing",
                                 "tick, comet sweep in the telemetry channel (one",
                                 "dot per tick), landing slice dashed in its colour,",
                                 "aim pips under the ghost window."]),
    ("rail", "B  RAIL JUMP", ["the landing slice gets its own hatched rail in",
                              "the ring; chevrons run from the live rail to it;",
                              "a chip outside the rim names it: program, value,",
                              "aim pips. No second blade on the wheel."]),
    ("ticker", "C  TICKER + SPLIT WINDOW", ["tick dots count round the hub edge to the",
                                            "landing; the landing slice is hatched; the live",
                                            "blade window splits: 12 > 5. Quietest on the",
                                            "slices, readable at small size."]),
]
CASES = [("HEAVY SPIN 9", [9], "card"), ("FLICK  spin 1", [1], "card"), ("NUDGE  -1 / +1", [-1, 1], "nudge")]


def card_thumb(name, w=110, h=146):
    import make_combat as MC
    c = [x for x in MC.CARDS if x["name"] == name][0]
    return MC.card_img(c, w, h)


def nudge_thumb():
    im = Image.new("RGBA", (130, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, (lab, key) in enumerate((("<", "Q"), (">", "E"))):
        x = 32 + k * 64
        d.ellipse([x - 24, 8, x + 24, 56], fill=(16, 14, 22, 240), outline=(255, 61, 168, 255), width=3)
        d.text((x, 32), lab, font=f_num(30), fill=(255, 255, 255), anchor="mm")
    return im


def preview_sheet():
    P0 = S.player()
    Sh = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(Sh)
    d.rectangle([0, 0, 8, 64], fill=(255, 214, 64))
    d.text((26, 6), "CARD-PLAY PREVIEW  (replaces the standing NEXT arrows)", font=f_num(44), fill=(255, 255, 255))
    d.text((26, 56), "Shown only while a spin / nudge card is hovered or aimed: where the pointer will land, the swept arc, and the "
                     "landing slice's value. D4 player wheel (Breaker).", font=f_mono(15, False), fill=(185, 185, 200))
    colw = 636
    for k, (style, title, desc) in enumerate(STYLES):
        x0 = 10 + k * (colw + 1)
        Sh.alpha_composite(city_tile(colw - 8, 990, 70 + k), (x0, 84))
        label(d, x0 + 12, 92, title, (255, 214, 64), 26)
        mono(d, x0 + 12, 126, desc, size=14, lh=18)
        # big case: heavy spin 9
        cname, moves, kind = CASES[0]
        im, c, m, ss = cached("pv_%s_0" % style, P0, preview=dict(style=style, moves=moves))
        place_box(Sh, im, c, ss, (x0 + 4, 200, x0 + colw - 12, 700), 175)
        th = card_thumb("HEAVY SPIN", 96, 128)
        Sh.alpha_composite(th, (x0 + 14, 212))
        label(d, x0 + 18, 712, "HOVER: HEAVY SPIN 9  -> FIREWALL 5", (235, 235, 245), 17)
        # small cases
        for j, (cname, moves, kind) in enumerate(CASES[1:]):
            bx0 = x0 + 4 + j * (colw // 2 - 4)
            im, c, m, ss = cached("pv_%s_%d" % (style, j + 1), P0, preview=dict(style=style, moves=moves, nudge=kind == "nudge"))
            place_box(Sh, im, c, ss, (bx0 + 92, 745, bx0 + colw // 2 - 4, 1046), 98)
            label(d, bx0 + 8, 1050, "HOVER: " + cname, (235, 235, 245), 15)
            th = card_thumb("FLICK", 96, 128) if kind == "card" else nudge_thumb()
            Sh.alpha_composite(th, (bx0 + 2, 790))
    Sh.convert("RGB").save(os.path.join(OUT, "preview_indicator.png"))
    print("preview sheet", flush=True)


# ================================================================== corp sheets
TYPE_NAME = {"EXPLOIT": "ATTACK", "ZERO-DAY": "CRIT", "FIREWALL": "DEFEND", "SANDBOX": "SHIELD", "PATCH": "HEAL",
             "PROXY": "EVADE", "NULL": "MISS"}
LOOPS = {
    "meridian": ["pallet ram: crates ride the rollers and slam the edge",
                 "laser fan sweeps the barcode, PRIORITY stamp lands",
                 "containers stack into a wall, row by row",
                 "film wraps the pallet in diagonal passes",
                 "TARIFF receipt prints out of the slot, line by line",
                 "empty conveyor; a dashed lost-parcel box blinks"],
    "solace": ["injector plunges; three droplets bead off the tip",
               "ECG runs flat, then spikes red: !!",
               "vials fill one after another in the rack",
               "two cells divide; + pulses either side",
               "capsule drips into a cell that turns magenta",
               "flatline crawls; NO PULSE blinks"],
    "halcyon": ["demolition order: red X stamps lot after lot",
                "siren strobes red / blue: ENFORCE",
                "zoning perimeter dashes march round the lot",
                "power line: nodes light gold one by one",
                "citation ticket feeds out: FINE / PAID?",
                "empty plot, PENDING stamp fades in and out"],
    "orbital": ["debris streaks fall into a red reticle",
                "down-link beam fires, flare blooms on the limb",
                "deflector hexes light in a wave",
                "transfer orbit: the burn arrow flips the ellipse",
                "corona rays pulse round the sun disc",
                "empty crosshair drifts: NO LOCK"],
    "rebel_cell": ["> EXECUTE types out; red chevrons push",
                   "> ROOT ACCESS, red tear bars rip across",
                   "> LOCKDOWN: port blocks slam shut",
                   "> SANDBOX/INV holds, inverted guard ring",
                   "ORDER stamp thumps onto the log",
                   "> ORDER VOID, the cursor blinks"],
}
INHERIT = [
    "CORP LEVEL (all enemies + boss): screen material,",
    "  type-panel style, per-type motif loops, bezel",
    "  base, rim language, crest, accent palette.",
    "ENEMY LEVEL: slots, values, readers, orbit, drones,",
    "  hub name/core, RES badge; ELITE adds the gold",
    "  collar, crest lugs and rank chevrons on the blade.",
    "BOSS: threat ring, crest lugs, banner-mounted",
    "  crowned blade, phase pips. PHASE LEVEL: below.",
]


def phase_notes(corp, meta):
    sig = RS.BOSS_SIGNATURE[RS.BOSSES[corp]]
    p2name = sig[1].split(":")[0]
    p2 = ["P2  %s" % p2name, "+ slices re-skin (boss phase 2)", "+ second reader (pin 2, own rail)" if corp != "halcyon" else "+ readers 2 and 3 (pins, own rails)",
          "+ threat ring runs hot"]
    if corp == "orbital":
        p2[2] = "+ second reader, orbit +4 / turn"
    ln = meta["lines"][1]
    t3 = ln.split(":", 1)[1].strip().split(".")[0] if ln.startswith("DISPATCH") else ln.split(":")[0]
    p3 = ["P3  " + t3[:36], "+ armour plates bolt on",
          "+ screens overdrive (scan bands)", "+ drone docks; readers/orbit per data"]
    if corp == "rebel_cell":
        p3[3] = "+ slices MERGE (2 x ZERO-DAY 24)"
    return p2, p3


def material_swatch(corp, w, h, ss=2):
    span = 60.0
    r_out = 2000.0 * ss
    ctx = SL.Ctx(w * ss, h * ss, 0.4, ss, span, r_out, (255, 255, 255), corp, "EXPLOIT", 3)
    ctx.opts = {}
    ctx.special = None
    im = SK.SKINS[corp](ctx, np.random.default_rng(11))
    return im.resize((w, h), Image.LANCZOS).convert("RGBA")


def corp_sheet(corp):
    reg_id, eli_id = S.PICKS[corp]
    A = MO.ACCENT[corp]
    acc = A["a"]
    Sh = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(Sh)
    d.rectangle([0, 0, 8, 64], fill=acc)
    d.text((26, 6), S.CORP_TITLE[corp], font=f_num(46), fill=(255, 255, 255))
    d.text((26 + f_num(46).getlength(S.CORP_TITLE[corp]) + 24, 26), "corp theme kit -> regular -> elite -> boss -> phase upgrades  (D4 frame)",
           font=f_mono(17, False), fill=(185, 185, 200))
    # ---- kit: material, crest, palette, rim, rules
    label(d, 30, 76, "SCREEN MATERIAL", acc)
    Sh.alpha_composite(material_swatch(corp, 300, 180), (30, 100))
    d.rectangle([30, 100, 329, 279], outline=(70, 70, 84))
    label(d, 360, 76, "CREST", acc)
    cr = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
    gl = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
    F.set_centre()
    D.crest(cr, ImageDraw.Draw(cr), ImageDraw.Draw(gl), 1, 90, 90, 62, corp, acc, RW.CORP_EMBLEM[corp])
    Sh.alpha_composite(gl.filter(ImageFilter.GaussianBlur(10)), (350, 96))
    Sh.alpha_composite(cr, (350, 96))
    label(d, 560, 76, "ACCENTS", acc)
    for k, (nm, col) in enumerate([(n, A[n]) for n in ("a", "dim", "hot", "paper", "gold") if n in A]):
        y = 100 + k * 34
        d.rounded_rectangle([560, y, 610, y + 26], radius=5, fill=col, outline=(10, 8, 16))
        d.text((620, y + 4), {"a": "accent", "dim": "dim", "hot": "hot / threat", "paper": "paper / ink-on", "gold": "gold"}[nm] +
               "  #%02X%02X%02X" % col, font=f_mono(14, False), fill=(205, 205, 218))
    label(d, 30, 292, "RIM LANGUAGE  +  TYPE PANEL: %s" % MO.PANEL_NAME[corp].upper(), acc)
    im, c, m, ss = cached("%s_reg" % corp, S.enemy(reg_id, corp, "regular")[0], hp_number=True)
    big, bc = F.fit(im, c, ss, 300)
    crop = big.crop((int(bc[0] - 470), int(bc[1] - 330), int(bc[0] + 20), int(bc[1] - 140)))
    tile = city_tile(490, 190, 5)
    tile.alpha_composite(crop)
    Sh.alpha_composite(tile, (30, 316))
    mono(d, 540, 300, INHERIT, size=14, lh=19)
    # ---- per-type tiles
    label(d, 960, 76, "PER-TYPE SLICE TILES  (corp motif loop; white glyph + value stays universal)", acc)
    for k, (prog, val, sp) in enumerate(TL.KIT_TYPES[corp]):
        cx0 = 960 + (k % 3) * 318
        cy0 = 102 + (k // 3) * 214
        t = TL.tile(prog, val, sp, corp, ss=2, scale=0.58, seed=k + 3)
        Sh.alpha_composite(t, (cx0, cy0))
        nm = (sp.replace("_", " ").upper() if sp else TYPE_NAME.get(prog, prog))
        label(d, cx0 + t.width + 6, cy0 + 4, nm, acc, 17)
        words = LOOPS[corp][k].split()
        lines, cur = [], ""
        for wd in words:
            if len(cur) + len(wd) + 1 > 11:
                lines.append(cur)
                cur = wd
            else:
                cur = (cur + " " + wd).strip()
        lines.append(cur)
        mono(d, cx0 + t.width + 6, cy0 + 28, lines[:7], size=12, lh=15)
    # ---- wheels
    y0 = 528
    d.line([(20, y0), (1900, y0)], fill=(60, 60, 74), width=1)
    boxes = [(10, 560, 360, 1000), (366, 560, 716, 1000), (722, 560, 1112, 1000), (1118, 560, 1508, 1000), (1514, 560, 1910, 1000)]
    reg = S.enemy(reg_id, corp, "regular")
    eli = S.enemy(eli_id, corp, "elite")
    b1, bm = S.boss(corp, 1)
    jobs = [("%s_reg" % corp, reg[0], "REGULAR  " + reg[1]["name"].upper(), [", ".join(reg[1]["mech"][:2])[:44]]),
            ("%s_eli" % corp, eli[0], "ELITE  " + eli[1]["name"].upper(), ["+ gold collar, crest lugs,", "  rank chevrons on the blade"]),
            ("%s_p1" % corp, b1, "BOSS  P1  " + bm["name"].upper(), ["threat ring, crest lugs,", "banner-mount crowned blade, pips"])]
    p2n, p3n = phase_notes(corp, bm)
    jobs += [("%s_p2" % corp, S.boss(corp, 2)[0], "PHASE 2", p2n), ("%s_p3" % corp, S.boss(corp, 3)[0], "PHASE 3", p3n)]
    for k, (name, spec, title, notes) in enumerate(jobs):
        bx = boxes[k]
        Sh.alpha_composite(city_tile(bx[2] - bx[0], 520, 30 + k, 0.30), (bx[0], 536))
        im, c, m, ss = cached(name, spec, hp_number=True)
        place_box(Sh, im, c, ss, (bx[0] + 4, 566, bx[2] - 4, 1000), 125 if k < 2 else 120, valign=1.0)
        label(d, bx[0] + 8, 540, title, (255, 255, 255) if k < 2 else acc, 18)
        mono(d, bx[0] + 8, 1004, notes, size=13, lh=17, hl=(255, 214, 120))
    for k in (2, 3):  # phase arrows
        x = boxes[k][2] + 3
        d.polygon([(x - 6, 610), (x + 6, 620), (x - 6, 630)], fill=(255, 214, 64))
    Sh.convert("RGB").save(os.path.join(OUT, "corp_%s.png" % corp))
    print("corp sheet", corp, flush=True)


def compare():
    Sh = Image.new("RGBA", (W, 1060), BG + (255,))
    d = ImageDraw.Draw(Sh)
    d.text((20, 6), "ROUND 14  BOSSES  -  phase 1 (top) and phase 3 (bottom), D4 frame, corp themes", font=f_num(38), fill=(255, 255, 255))
    for i, corp in enumerate(CORPS5):
        x0 = 8 + i * 382
        Sh.alpha_composite(city_tile(374, 990, 90 + i, 0.30), (x0, 60))
        for row, ph in enumerate((1, 3)):
            spec = S.boss(corp, ph)[0]
            im, c, m, ss = cached("%s_p%d" % (corp, ph), spec, hp_number=True)
            place_box(Sh, im, c, ss, (x0 + 2, 92 + row * 490, x0 + 372, 560 + row * 490), 135)
        label(d, x0 + 8, 64, S.CORP_TITLE[corp].split("  ")[0], MO.ACCENT[corp]["a"], 20)
    Sh.convert("RGB").save(os.path.join(OUT, "corps_compare.jpg"), quality=90)
    print("compare", flush=True)


# ================================================================== combat
def combat(corp):
    import make_combat as MC
    os.makedirs(MC.CACHE, exist_ok=True)
    spec, bm = S.boss(corp, 2)
    jobs = (("player_b", S.player(), "pl_combat"), ("boss", spec, "%s_combat" % corp))
    for key, sp, name in jobs:
        im, c, meta, ss = cached(name, sp)
        im.save(os.path.join(MC.CACHE, key + ".png"))
        with open(os.path.join(MC.CACHE, key + ".txt"), "w") as f:
            f.write("%d %d" % (c[0] / ss, c[1] / ss))
        MC.META[key] = dict(hp_r=meta["hp_r"], ptr_r=meta["ptr_r"])
    acc = MO.ACCENT[corp]["a"]
    hp = spec["hp"]
    L0 = spec["slots"][0]
    MC.BT = dict(bar="NETRUN // %s // UPLINK FIELD 7 // BOSS: %s  PHASE 2" % (CORPS[corp]["name"], bm["name"].upper()),
                 hp=hp, next=(hp[0] - 8, -8), acc=acc, who=bm["name"].upper(), prog=L0["program"], val=L0["value"],
                 chips=[("HIT %d > YOU" % L0["value"], (255, 64, 72)), ("READER 2: %s" % spec["slots"][3]["program"], acc)],
                 width=322, tag_x=1590)

    def plain_base(variant, which, pools):  # no target building for this corp yet: dimmed, cooled city
        a = MC.city_base("night", pools)
        return a * np.array([0.86, 0.94, 1.12], np.float32)
    MC.target_base = plain_base
    MC.SAVE_NAME = "combat_%s.png" % corp
    MC.compose("boss", "night")


if __name__ == "__main__":
    what = sys.argv[1]
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    if what == "preview":
        preview_sheet()
    elif what == "corp":
        corp_sheet(arg)
    elif what == "compare":
        compare()
    elif what == "combat":
        combat(arg)
    print("done", flush=True)
