"""Boss Wheel v2: the deliverable sheets.

python sheets.py dir roman A          -> roman_wheel_A.png   (combat size + 2x close-up + needle states)
python sheets.py final roman A        -> roman_wheel_final.png (full combat frame next to the player wheel)
python sheets.py phases roman A       -> roman_phases.png
python sheets.py emblem roman|atlantis -> <corp>_boss_emblem.png
python sheets.py readability ROMAN_KEY ATL_KEY
python sheets.py compare ROMAN_KEY ATL_KEY
python sheets.py system
Every random draw is seeded; nothing reads the clock.
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
from PIL import Image, ImageChops, ImageDraw, ImageFilter  # noqa: E402

import bw_kit as K  # noqa: E402
import directions  # noqa: E402
import wheel_v2 as W  # noqa: E402

OUT = K.OUTDIR
R41 = os.path.join(K.WT, "docs", "concepts", "round41_wheel_stack", "scripts")
R41C = os.path.join(K.SCR, "r41")
SW, SH = 1920, 1080
BG = (14, 12, 18)
CORP_COL = {"roman": (41, 219, 166), "atlantis": (47, 107, 255)}
CORP_NAME = {"roman": "AURELIAN CONCORD", "atlantis": "TETHYS DEEP"}
COMBAT_S = 236 / 360.0


def render(corp, key, S, **kw):
    D, slots = directions.get(corp, key)
    st = dict(forecast=0, gesture=0.0, still=True)
    st.update(kw)
    ctx = W.Ctx(S, t=st.pop("t", 0.0), phase=st.pop("phase", 1), hp=st.pop("hp", 0.86), rot=st.pop("rot", 0.0), **st)
    return W.compose(D, ctx, slots), D, ctx, slots


def sheet(title, sub, col):
    im = K.rgba((SW, SH), BG, 255)
    d = ImageDraw.Draw(im)
    for y in range(SH):
        pass
    vg = K.vignette((SW, SH), SW / 2, SH / 2, SW * 0.7, 0.5)
    im.alpha_composite(K.solid(vg, (0, 0, 0)))
    d = ImageDraw.Draw(im)
    d.text((40, 24), title, font=K.f_anton(46), fill=(255, 255, 255))
    tw = K.f_anton(46).getlength(title)
    d.text((40 + tw + 24, 44), sub, font=K.f_mono(20), fill=col)
    d.line([(40, 92), (SW - 40, 92)], fill=col + (90,), width=2)
    return im


def label(d, xy, txt, col=(200, 205, 215), f=None, anchor="la"):
    d.text(xy, txt, font=f or K.f_ui(20), fill=col, anchor=anchor)


def paste_centered(base, im, cx, cy):
    base.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))


# ------------------------------------------------------------------ direction sheet
def dir_sheet(corp, key):
    D0, _ = directions.get(corp, key)
    col = CORP_COL[corp]
    im = sheet("%s  //  BOSS WHEEL v2  %s" % (directions.CORPS[corp]["name"], D0.title), CORP_NAME[corp] + "  |  one template, named layer slots", col)
    d = ImageDraw.Draw(im)
    # 1) combat size (r = 236 px), cropped canvas
    w1, D, ctx, slots = render(corp, key, COMBAT_S, gesture=0.0)
    cw = w1.width
    crop = w1.crop((int(cw * 0.12), int(cw * 0.02), int(cw * 0.88), int(cw * 0.88)))
    paste_centered(im, crop, 40 + crop.width / 2, 110 + crop.height / 2)
    label(d, (48, 104), "COMBAT SIZE  1:1  (r = 236 px, rest, forecast on SHIM)", col, K.f_ui(18, b"Bold Condensed"))
    # 2) 2x close-up of the needle rig + top slices
    w2, D, ctx2, _ = render(corp, key, COMBAT_S * 2, gesture=0.0)
    c2 = w2.width / 2
    x0, y0 = c2 - 470, c2 - 640 * ctx2.S * 1.0
    cl = w2.crop((int(x0), int(max(0, y0)), int(x0 + 940), int(max(0, y0) + 660)))
    bx, by = 900, 110
    im.alpha_composite(cl, (bx, by))
    d.rectangle([bx, by, bx + cl.width, by + cl.height], outline=col + (120,), width=2)
    label(d, (bx + 8, by + 6), "2x CLOSE-UP", col, K.f_ui(18, b"Bold Condensed"))
    # 3) the needle reacting: rest / hit / whiff (1x crops)
    states = [("REST", 0.0, None, None), ("HIT  (lands on SHIM, PERFECT)", -1.0 if corp == "roman" else 1.0, 0, "PERFECT"),
              ("WHIFF / BLOCKED  (lands on the blank)", 1.0 if corp == "roman" else -1.0, 3, "GOOD")]
    yb = 800
    for j, (nm, g, landed, tier) in enumerate(states):
        kw = dict(gesture=g)
        if landed is not None:
            kw.update(landed=landed, tier=tier, latch=1.0 if tier == "PERFECT" else 0.0, rot=-60 * landed)
        w3, _, ctx3, _ = render(corp, key, COMBAT_S, **kw)
        c3 = w3.width / 2
        cr = w3.crop((int(c3 - 170), int(c3 - 470 * COMBAT_S - 0), int(c3 + 170), int(c3 - 470 * COMBAT_S + 250)))
        cr = w3.crop((int(c3 - 170), int(c3 - 700 * COMBAT_S), int(c3 + 170), int(c3 - 700 * COMBAT_S + 250)))
        xx = 900 + j * 340
        im.alpha_composite(cr, (xx, yb))
        d.rectangle([xx, yb, xx + 340, yb + 250], outline=(70, 70, 86), width=1)
        label(d, (xx + 6, yb + 254), nm, (220, 220, 230), K.f_ui(15, b"Bold Condensed"))
    # 4) blurb
    yy = 110 + crop.height + 8
    for k_, ln in enumerate(D0.blurb):
        label(d, (48, yy + k_ * 24), ln, (220, 222, 230), K.f_ui(18))
    p = os.path.join(OUT, "%s_wheel_%s.png" % (corp, key))
    im.convert("RGB").save(p)
    print(p)


# ------------------------------------------------------------------ the combat frame (round 41 v4 composition)
def _r41():
    sys.path.insert(1, R41)
    cwd = os.getcwd()
    os.chdir(R41)
    import combat44 as C44  # noqa
    os.chdir(cwd)
    return C44


def backdrop(corp):
    plate = os.path.join(r"D:\rc_scratch\new_corps", "roman_hq_plate.png" if corp == "roman" else "atlantis_hq_plate.png")
    bd = Image.open(plate).convert("RGB").resize((SW, SH), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.5))
    a = np.asarray(bd, np.float32)
    yy, xx = np.mgrid[0:SH, 0:SW].astype(np.float32)
    pool = np.zeros((SH, SW), np.float32)
    for (cx, cy, r) in ((481, 490, 220), (1438, 520, 236)):
        q = np.hypot(xx - cx, yy - cy) / (r * 1.25)
        pool = np.maximum(pool, np.exp(-q ** 4))
    dim = 0.80 * (1 - 0.5 * pool)
    return Image.fromarray(np.clip(a * dim[..., None], 0, 255).astype(np.uint8)).convert("RGBA")


def combat_frame(corp, key, boss_state=None, tip=True, label_txt=None):
    C44 = _r41()
    shot = backdrop(corp)
    jpg = Image.open(os.path.join(R41C, "hud_jpg.png")).convert("RGBA")
    pw = Image.open(os.path.join(R41C, "player_typ.png"))
    pc = json.load(open(os.path.join(R41C, "player_typ.json")))
    st = dict(gesture=0.0)
    st.update(boss_state or {})
    bw, D, ctx, slots = render(corp, key, COMBAT_S, **st)
    for img, (cx, cy), (ox, oy) in ((pw, (481, 490), (pc["cx"], pc["cy"])), (bw, (1438, 520), (bw.width / 2, bw.height / 2))):
        sh = K.solid(K.blur(img.split()[3], 10), (0, 0, 0), 0.5)
        shot.alpha_composite(sh, (int(cx - ox + 6), int(cy - oy + 12)))
        shot.alpha_composite(img, (int(cx - ox), int(cy - oy)))
    d = ImageDraw.Draw(shot)
    for name, bx in C44.KEEP.items():
        if name == "status bar":
            continue
        shot.paste(jpg.crop(bx), bx[:2])
    # status bar redrawn for this boss
    x0, y0, x1, y1 = 634, 10, 1288, 76
    d.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=(10, 9, 16, 235), outline=(70, 70, 90), width=2)
    d.text(((x0 + x1) / 2, 30), "TURN 3   |   FREE NUDGE 1", font=K.f_num(30), fill=(255, 255, 255), anchor="mm")
    sub = "NETRUN // %s // CENTRAL SERVER // BOSS: %s" % (CORP_NAME[corp], directions.CORPS[corp]["name"])
    d.text(((x0 + x1) / 2, 62), sub, font=K.f_mono(15), fill=(200, 205, 215), anchor="mm")
    st_ = C44.sticker()
    shot.alpha_composite(st_, C44.STICKER_XY)
    acc = CORP_COL[corp]
    for who, a in (("player", (255, 61, 168)), ("boss", acc)):
        for k_, (x, y, gname, kk) in enumerate(C44.NUDGE[who]):
            C44.nudge(d, shot, x, y, gname, kk, a)
    C44.hp_and_chips(shot, C44.P_HP[0], C44.P_HP[1], 41, 60, [("dmg", None, "-14")])
    bb, bchips = C44.hp_and_chips(shot, C44.B_HP[0], C44.B_HP[1], 340, 400, [("dmg", None, "-8"), ("abs", "SHIELD", "4"), ("gain", "SHIELD", "+4")])
    if tip:
        nm = directions.CORPS[corp]["name"]
        sl = slots[0]
        lines = ["IF YOU SEND IT NOW  -  %s" % nm, "YOU: ZERO-DAY 12 (GOOD)", "   - its SHIELD 4 (absorbed)", "   = -8 HP  (340 -> 332)",
                 "IT: %s %d (PERFECT) -> -%d HP to you" % (sl["type"], sl["value"], sl["value"]), "    hub passive: +4 SHIELD"]
        C44.tooltip(shot, bchips[0], lines, acc)
    if label_txt:
        f = K.f_num(26)
        tw = f.getlength(label_txt)
        d = ImageDraw.Draw(shot)
        d.rounded_rectangle([SW - tw - 30, SH - 40, SW - 10, SH - 6], radius=6, fill=(10, 9, 16, 230), outline=(255, 214, 64), width=2)
        d.text((SW - tw - 20, SH - 40), label_txt, font=f, fill=(255, 214, 64))
    return shot


def final(corp, key):
    shot = combat_frame(corp, key, dict(forecast=0, gesture=0.0), tip=False,
                        label_txt="BOSS WHEEL v2  |  %s %s  |  r = 236 px" % (corp.upper(), key))
    p = os.path.join(OUT, "%s_wheel_final.png" % corp)
    shot.convert("RGB").save(p)
    print(p)


# ------------------------------------------------------------------ phases + damage cracks
PHASE_STATES = [("PHASE 1  |  HP 100 %", dict(phase=1, hp=1.0, dmg=0.0)),
                ("PHASE 2  |  HP 66 %  (crossed the first pip)", dict(phase=2, hp=0.62, dmg=0.35)),
                ("PHASE 3  |  HP 33 %", dict(phase=3, hp=0.30, dmg=0.7)),
                ("PHASE 3  |  HP 10 %  (cracks at full)", dict(phase=3, hp=0.1, dmg=1.0))]
PHASE_NOTES = {
    "roman": ["P1: half-empty stands, 12 torches, crowd idle.", "P2: the stands fill, 24 torches, fire in the arches, blood on the sand.",
              "P3: the colosseum burns: fires on the tiers, the bust's eye turns red, the arena floor cracks.",
              "Damage: cracks open on the bezel, the arcade and the sand as HP falls (dmg = 1 - HP/max)."],
    "atlantis": ["P1: the octopus dozes: two arms on the rim, the lids half shut.", "P2: it wakes: four arms grip, red lights in the trench, gauges climb.",
                 "P3: six arms, the eye turns red, the water darkens, the vent roars.",
                 "Damage: cracks open on the bezel, the collar and the floor ring as HP falls."],
}


PHASE_NOTES_D = {
    "roman": ["P1: half-empty stands, gates shut, braziers cold; chariots race, fighters spar, the captives wait.",
              "P2 (66 %): the crowd fills, braziers light at the four gates, the portcullises lift and lions walk in; blood on the sand.",
              "P3 (33 %): the stands burn, embers drift over the floor, the arena glows red at the wall.",
              "Damage: cracks open across the sand, the bezel (the arena wall) and the gates as HP falls (dmg = 1 - HP/max)."],
    "atlantis": ["P1: the octopus dozes: lids half shut, mottled red-brown skin, the blue rings dull.",
                 "P2 (66 %): it wakes: the eyes open wide, the skin flushes orange-red, the blue rings bioluminesce.",
                 "P3 (33 %): the eyes turn red, the skin goes crimson, the rings blaze; the vent roars.",
                 "Damage: cracks open across the web (under-ring) and the bezel as HP falls."],
}


def phases(corp, key):
    col = CORP_COL[corp]
    D0, _ = directions.get(corp, key)
    im = K.rgba((SW, 1920), BG, 255)
    hdr = sheet("%s  //  PHASES + DAMAGE" % directions.CORPS[corp]["name"], "%s  |  phase 2/3 transform the art layers; cracks track HP" % D0.title, col)
    im.alpha_composite(hdr.crop((0, 0, SW, 100)), (0, 0))
    d = ImageDraw.Draw(im)
    S = 0.72
    for j, (nm, st) in enumerate(PHASE_STATES):
        kw = dict(st)
        if corp == "atlantis":
            kw["blink"] = 0.5 if kw["phase"] == 1 else 0.0
            kw.setdefault("rot", 180.0)
        if kw["phase"] >= 2:
            kw["gates"] = 1.0
        if kw["phase"] == 3:
            kw["wrath"] = 1.0
        w, D, ctx, _ = render(corp, key, S, **kw)
        cw = w.width
        cr = w.crop((int(cw * 0.1), int(cw * (0.12 if corp == "atlantis" else 0.03)), int(cw * 0.9), int(cw * (0.92 if corp == "atlantis" else 0.86))))
        tw = 780
        cr = cr.resize((tw, int(tw * cr.height / cr.width)), Image.LANCZOS)
        xx = 100 + (j % 2) * 900
        yy = 140 + (j // 2) * 840
        im.alpha_composite(cr, (xx, yy))
        label(d, (xx + 10, yy - 30), nm, col, K.f_ui(24, b"Bold Condensed"))
    notes = PHASE_NOTES_D[corp] if key == "D" else PHASE_NOTES[corp]
    for k_, ln in enumerate(notes):
        label(d, (40, 1800 + k_ * 28), ln, (220, 222, 230), K.f_ui(20))
    label(d, (1000, 1800), "Phase beat (ART_BIBLE 3.16 v3 kept): 120 ms hit-stop, white flash on the wheel only,", (170, 176, 190), K.f_ui(18))
    label(d, (1000, 1830), "the pip rings, the banner flips; then the art layers cross-fade over 0.8-1.0 s.", (170, 176, 190), K.f_ui(18))
    label(d, (1000, 1860), "Reduce effects: an instant swap, no flash, no hit-stop.", (170, 176, 190), K.f_ui(18))
    p = os.path.join(OUT, "%s_phases.png" % corp)
    im.convert("RGB").save(p)
    print(p)


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "dir":
        dir_sheet(sys.argv[2], sys.argv[3])
    elif what == "final":
        final(sys.argv[2], sys.argv[3])
    elif what == "phases":
        phases(sys.argv[2], sys.argv[3])
