"""Boss Wheel v2 round 3 (v3) sheets for THE PANTHEON (Roman).

python sheets3.py final        -> roman_v3_final.png
python sheets3.py mechanic     -> roman_v3_mechanic.png
python sheets3.py frames a b   -> D:/rc_scratch/boss_wheel_v2/frames_roman_v3/f_####.png
python sheets3.py gif          -> roman_v3_anim.gif
python sheets3.py emblem       -> roman_v3_boss_emblem.png
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import anim as AN  # noqa: E402
import bw_kit as K  # noqa: E402
import directions  # noqa: E402
import emoji_hand as EH  # noqa: E402
import fresco as FR  # noqa: E402
import roman_v3 as RV  # noqa: E402
import sheets as SH  # noqa: E402
import wheel_v2 as W  # noqa: E402

OUT = K.OUTDIR
BASE = dict(asc=0, wrath_slots={2}, cracks={5: 2, 1: 1})
CORP, KEY = "roman_v3", "V3"
COL = (232, 186, 90)
SW, SHH = 1920, 1080


def render(S, **kw):
    D, slots = directions.get(CORP, KEY)
    st = dict(forecast=0, gesture=0.0, still=True, asc=0)
    st.update(kw)
    ctx = W.Ctx(S, t=st.pop("t", 0.0), phase=st.pop("phase", 1), hp=st.pop("hp", 0.86), rot=st.pop("rot", 0.0), **st)
    return W.compose(D, ctx, slots), D, ctx, slots


def crop_wheel(w, top=0.03, bot=0.86):
    cw = w.width
    return w.crop((int(cw * 0.12), int(cw * top), int(cw * 0.88), int(cw * bot)))


def combat_frame(boss_state):
    """The round 41 v4 combat composition (via sheets.combat_frame) with this boss."""
    SH.CORP_COL[CORP] = COL
    SH.CORP_NAME[CORP] = "AURELIAN CONCORD"
    return SH.combat_frame(CORP, KEY, boss_state, tip=False, label_txt="BOSS WHEEL v3  |  THE PANTHEON  |  r = 236 px")


def final():
    big = Image.new("RGBA", (SW, SHH * 2), SH.BG + (255,))
    big.alpha_composite(combat_frame(dict(BASE, forecast=0)), (0, 0))
    lo = SH.sheet("THE ROSTRUM  //  V3 FINAL: THE PANTHEON", "AURELIAN CONCORD  |  fresco gods + ASCENDANT + OMENS", COL)
    d = ImageDraw.Draw(lo)
    w1, D, ctx, slots = render(SH.COMBAT_S, **BASE)
    lo.alpha_composite(crop_wheel(w1), (40, 120))
    SH.label(d, (48, 104), "COMBAT SIZE 1:1: MARS ascendant (28), JUPITER NEXT, MINERVA wrathful (COUNTER), omens on VULCAN", COL, K.f_ui(18, b"Bold Condensed"))
    S2 = SH.COMBAT_S * 2
    w2, _, _, _ = render(S2, **BASE)
    c2 = w2.width / 2
    cl = w2.crop((int(c2 - 470), int(c2 - 640 * S2), int(c2 + 470), int(c2 - 640 * S2 + 660)))
    lo.alpha_composite(cl, (900, 110))
    d.rectangle([900, 110, 1840, 770], outline=COL + (120,), width=2)
    SH.label(d, (908, 116), "2x CLOSE-UP", COL, K.f_ui(18, b"Bold Condensed"))
    states = [("REST: the emperor deliberates", dict(BASE)),
              ("HIT: PERFECT on ascendant MARS (28)", dict(BASE, gesture=-1.0, landed=0, tier="PERFECT", latch=1.0, act_slot=0, act=0.8)),
              ("WHIFF: lands on PLUTO (the void)", dict(BASE, gesture=1.0, landed=3, tier="GOOD", rot=-180))]
    for j, (nm, s_) in enumerate(states):
        w3, _, _, _ = render(SH.COMBAT_S, **s_)
        c3 = w3.width / 2
        crp = w3.crop((int(c3 - 170), int(c3 - 700 * SH.COMBAT_S), int(c3 + 170), int(c3 - 700 * SH.COMBAT_S + 250)))
        xx = 900 + j * 340
        lo.alpha_composite(crp, (xx, 800))
        d.rectangle([xx, 800, xx + 340, 1050], outline=(70, 70, 86), width=1)
        SH.label(d, (xx + 6, 1054), nm, (220, 220, 230), K.f_ui(15, b"Bold Condensed"))
    for k_, ln in enumerate(D.blurb):
        SH.label(d, (40, 960 + k_ * 26), ln, (220, 222, 230), K.f_ui(17))
    big.alpha_composite(lo, (0, SHH))
    p = os.path.join(OUT, "roman_v3_final.png")
    big.convert("RGB").save(p)
    print(p)


def slice_crop(w, S, i_top_rot=True):
    c = w.width / 2
    return w.crop((int(c - 240 * S), int(c - 372 * S), int(c + 240 * S), int(c - 40 * S)))


def mechanic():
    import roman_v3 as RV_
    im = K.rgba((SW, 1460), SH.BG, 255)
    hdr = SH.sheet("THE PANTHEON  //  ASCENDANT + OMENS", "one god gilded x2, moving each turn; your hits crack gods; 3 cracks = WRATHFUL (flipped)", COL)
    im.alpha_composite(hdr.crop((0, 0, SW, 100)), (0, 0))
    d = ImageDraw.Draw(im)
    S = 1.0
    rot = -120            # Minerva (slot 2) under the needle
    states = [("1  NORMAL", "DEFRAG 12: Minerva guards", dict(asc=None, cracks={2: 1})),
              ("2  ASCENDANT", "DEFRAG 24: gilded, x2", dict(asc=2, cracks={2: 1})),
              ("3  WRATHFUL", "3 cracks: guard -> COUNTER, SHIM 12", dict(asc=None, wrath_slots={2})),
              ("4  ASCENDANT + WRATHFUL", "SHIM 24: gold over cracks, bleeding light", dict(asc=2, wrath_slots={2}, gesture=-0.15))]
    cols = [(220, 220, 230), (255, 210, 77), (255, 90, 60), (255, 160, 60)]
    for j, (nm, sub, st) in enumerate(states):
        w, _, _, _ = render(S, rot=rot, forecast=None, **st)
        c = slice_crop(w, S)
        c = c.resize((440, int(440 * c.height / c.width)), Image.LANCZOS)
        x = 20 + j * 470
        im.alpha_composite(c, (x, 160))
        SH.label(d, (x + 6, 112), nm, cols[j], K.f_ui(24, b"Bold Condensed"))
        SH.label(d, (x + 6, 140), sub, (210, 212, 222), K.f_ui(17))
    SH.label(d, (30, 520), "DANGER TELEGRAPH (state 4): the gilding is announced a turn ahead on a wrathful god -> the NEXT tab turns red-gold, the fresco bleeds light", (255, 170, 80), K.f_ui(19, b"Bold Condensed"))
    SH.label(d, (30, 546), "through the gold leaf, and the emperor's thumb trembles over the box (+-6 deg at 9 Hz; reduce effects: a static half-turned thumb).", (255, 170, 80), K.f_ui(19, b"Bold Condensed"))
    # a whole-wheel example mid-fight
    w, _, _, _ = render(0.62, asc=1, asc_next=2, wrath_slots={1, 4}, cracks={0: 2, 2: 1, 5: 1}, forecast=None)
    c = crop_wheel(w, 0.02, 0.86)
    c = c.resize((560, int(560 * c.height / c.width)), Image.LANCZOS)
    im.alpha_composite(c, (20, 640))
    SH.label(d, (30, 590), "MID-FIGHT: JUPITER ascendant + wrathful (x2, +CORRUPT),", COL, K.f_ui(18, b"Bold Condensed"))
    SH.label(d, (30, 614), "MERCURY wrathful, omens on MARS / MINERVA / VULCAN", COL, K.f_ui(18, b"Bold Condensed"))
    # the god table
    x0, y0 = 620, 640
    SH.label(d, (x0, y0 - 34), "THE GODS (real boss actions, GDD 2.5 / 2.6 / 2.9 + corp specials)", COL, K.f_ui(22, b"Bold Condensed"))
    hdrs = [("GOD", 0), ("NORMAL", 150), ("WRATHFUL (3 cracks)", 560)]
    for h, dx in hdrs:
        SH.label(d, (x0 + dx, y0), h, (255, 255, 255), K.f_ui(19, b"Bold Condensed"))
    rows = [("MARS", "SHIM 14 (attack)", RV_.SLOTS[0]), ("JUPITER", "OVERFLOW 24 (the lightning crit)", RV_.SLOTS[1]),
            ("MINERVA", "DEFRAG 12 (block)", RV_.SLOTS[2]), ("MERCURY", "RESIST 2 (boss spin resistance until its next turn)", RV_.SLOTS[4]),
            ("VULCAN", "INFECT 3 (burn = CORRUPTED)", RV_.SLOTS[5]), ("PLUTO", "NULL (nothing)", RV_.SLOTS[3]),
            ("NEPTUNE*", "SHIM 10 SWEEP (phase 3, replaces Mercury)", None)]
    for k_, (g, n, sl) in enumerate(rows):
        y = y0 + 36 + k_ * 34
        d.line([(x0, y - 6), (x0 + 1270, y - 6)], fill=(50, 50, 64), width=1)
        SH.label(d, (x0, y), g, COL, K.f_ui(19, b"Bold Condensed"))
        SH.label(d, (x0 + 150, y), n, (220, 222, 230), K.f_ui(18))
        SH.label(d, (x0 + 560, y), sl["wrath"]["text"] if sl else "(cannot crack: it arrives in phase 3)", (255, 140, 110), K.f_ui(18))
    rules = ["GILDING: fixed clockwise order, one god per boss turn, skips Pluto; starts on the god opposite the needle at combat start.",
             "  Deterministic (no RNG) so the telegraph is always true; Respin/Flip move the wheel, not the gilding (it belongs to the god).",
             "OMENS: each player hit that deals damage adds 1 crack to the god under the boss's needle this turn (max 1 per turn per god).",
             "  3 cracks = WRATHFUL for the rest of the fight. The preview/HP chips show the flipped value the moment the god breaks.",
             "THE BET: hitting while the boss sits on a weak god (Pluto, Mercury) breaks a god that hurts more when wrathful; the gilding",
             "  then decides when that hurts. Phase 3: two gods ascend at once. Reduce effects: no glints/bleed; frames, tags and pips stay.",
             "GDD FLAGS: RESIST as a slice effect (today only a passive or hub trait, GDD 2.5); a wrathful slice changes type mid-fight",
             "  (preview must recompute; rewind may not cross the crack); Pluto turning hostile changes the only 'miss' (Cold Exit etc.)."]
    for k_, ln in enumerate(rules):
        SH.label(d, (x0, y0 + 300 + k_ * 26), ln, (226, 228, 236) if not ln.startswith("GDD") else (255, 200, 120), K.f_ui(18))
    # C stays a proposal
    SH.label(d, (x0, y0 + 520), "Not chosen: C THE SENATE VOTE (a second voting layer; strong for an elite, too much HUD for this boss).", (150, 156, 170), K.f_ui(17))
    pn = FR.paint("neptune", 300, K.TYPE_COL["SHIM"], 0.0, 0.4, 0.8, seed=6)
    im.alpha_composite(pn.resize((200, 200), Image.LANCZOS), (620, 1220))
    SH.label(d, (840, 1260), "* NEPTUNE: seven gods, six slices. In phase 3 the sea rises over Mercury's panel (tesserae wash, 0.8 s):", (92, 225, 255), K.f_ui(19, b"Bold Condensed"))
    SH.label(d, (840, 1288), "SHIM 10 SWEEP (hits every target). Mercury's cracks carry over to Neptune.", (220, 222, 230), K.f_ui(18))
    p = os.path.join(OUT, "roman_v3_mechanic.png")
    im.convert("RGB").save(p)
    print(p)


# ------------------------------------------------------------------ animation
N = 156
T_G0, T_G1 = 0.3, 1.1           # the gilding migrates VULCAN -> MARS
T_SPIN0, T_LAND = 1.2, 2.7
T_PH0 = 4.4


def state(f):
    t = f / AN.FPS
    # the wheel rests with Jupiter (1) under the needle; it lands on Minerva (2): -120 (+ two turns)
    rot, speed = AN._spin(t, -60.0, -840.0)
    st = dict(t=t, rot=rot, phase=1, hp=0.74, dmg=0.1, gesture=0.0, still=False, asc=1, asc_next=2, wrath_slots={2},
              cracks={5: 2, 0: 1}, forecast=1 if t < T_SPIN0 else None)
    beat = "IDLE: JUPITER is ascendant; MINERVA is NEXT - and MINERVA is WRATHFUL (3 cracks). The telegraph turns red-gold."
    if T_G0 <= t:
        u = min(1.0, (t - T_G0) / (T_G1 - T_G0))
        st.update(asc_from=1, asc_to=2, asc_mix=AN.ease_out_cubic(u), asc=2 if u >= 0.5 else 1, asc_next=4 if u >= 0.5 else 2)
        beat = "TURN START: the gilding moves onto wrathful MINERVA: ASCENDANT + WRATHFUL = SHIM 24. The fresco bleeds light; the thumb trembles."
        st["gesture"] = 0.12 * math.sin(t * 2 * math.pi * 9) if u >= 0.5 else 0.0
    if T_SPIN0 <= t < T_LAND:
        st["blur"] = min(40.0, speed * 1.4)
        a = math.radians(rot)
        k = min(1.0, speed / 12.0)
        st["par"] = (6 * k * math.cos(a), 6 * k * math.sin(a))
        st["under_lag"] = 2.5 * k
        st["gesture"] = 0.12 * math.sin(t * 2 * math.pi * 9)
        beat = "SPIN: the floor of gods turns under the emperor's box (blur + parallax); the thumb keeps trembling"
    if t >= T_LAND:
        st.update(landed=2, tier="PERFECT", latch=min(1.0, (t - T_LAND) / 0.08), flash=max(0.0, 1 - (t - T_LAND) / 0.25),
                  flash_col=(255, 120, 60), pop=max(0.0, 1 - abs(t - T_LAND - 0.15) / 0.2))
        beat = "LAND: PERFECT on MINERVA, ascendant + wrathful: her guard is a COUNTERATTACK x2: SHIM 24"
    if t >= T_LAND + 0.1:
        u = (t - T_LAND - 0.1) / 0.6
        st["act_slot"] = 2
        st["act"] = min(1.0, max(0.0, u)) if t < 3.9 else max(0.0, 1 - (t - 3.9) / 0.4)
        st["gesture"] = -AN.ease_out_cubic(max(0.0, min(1.0, (t - T_LAND - 0.15) / 0.3)))
        beat = "MINERVA'S SHIELD STRIKES (SHIM 24)  |  THE EMPEROR: THUMB DOWN"
    if t >= 3.95:
        st["cracks"] = {5: 2, 0: 1, 2: 3}
    if t >= T_PH0:
        st.update(hp=0.62, tier=None, latch=0.0, landed=None, act=0.0, gesture=-max(0.0, 1 - (t - T_PH0) / 0.4))
        beat = "YOUR HIT CRACKS VULCAN (3/3): VULCAN TURNS WRATHFUL  |  PHASE 2: the apotheosis sky burns, the laurel sets its gems"
        if t >= T_PH0 + 0.3:
            st["wrath_slots"] = {2, 5}
    return t, st, beat


def frame(f, bd):
    D, slots = directions.get(CORP, KEY)
    t, st, beat = state(f)
    S = AN.S
    if t >= T_PH0:
        u = min(1.0, max(0.0, (t - T_PH0 - 3 / AN.FPS) / 1.0))
        frz = t < T_PH0 + 3 / AN.FPS
        s1 = dict(st, phase=1, dmg=0.1)
        s2 = dict(st, phase=2, dmg=0.1 + 0.4 * u)
        if frz:
            s1["t"] = s2["t"] = T_PH0
        a = W.compose(D, W.Ctx(S, **s1), slots) if u < 1 else None
        D2, _ = directions.get(CORP, KEY)
        b = W.compose(D2, W.Ctx(S, **s2), slots)
        w = Image.blend(a, b, AN.ease_out_cubic(u)) if a is not None else b
        fl = max(0.0, 1 - (t - T_PH0) / 0.18)
        if fl > 0:
            w = K.add(w, K.solid(K.blur(w.split()[3], 2), (255, 255, 255)), 0.7 * fl)
    else:
        w = W.compose(D, W.Ctx(S, **st), slots)
    shot = bd.copy()
    shot.alpha_composite(K.solid(K.blur(w.split()[3], 12), (0, 0, 0), 0.5), (int(AN.CX - w.width / 2 + 6), int(AN.CY - w.height / 2 + 12)))
    shot.alpha_composite(w, (int(AN.CX - w.width / 2), int(AN.CY - w.height / 2)))
    if T_LAND + 0.05 <= t < T_LAND + 0.8:
        ws = AN.word_sticker("PERFECT  x2  WRATH", K.PERFECT_GOLD)
        shot.alpha_composite(ws, (int(AN.CX + 300 - ws.width / 2), int(AN.CY - 420 - ws.height / 2)))
    if T_G0 + 0.2 <= t < T_G1 + 0.4:
        ws = AN.word_sticker("MINERVA ASCENDS - WRATHFUL", (255, 170, 80), px=40)
        shot.alpha_composite(ws, (int(AN.CX - 360 - ws.width / 2), int(AN.CY - 400 - ws.height / 2)))
    if T_PH0 + 0.15 <= t < T_PH0 + 1.3:
        ws = AN.word_sticker("VULCAN WRATHFUL  |  PHASE 2", (255, 120, 60), px=40)
        shot.alpha_composite(ws, (int(AN.CX - 380 - ws.width / 2), int(AN.CY - 400 - ws.height / 2)))
    caption(shot, t, f, beat, [("IDLE", 0.0, T_G0), ("THE GILDING MOVES", T_G0, T_SPIN0), ("SPIN", T_SPIN0, T_LAND), ("LAND + ACT", T_LAND, T_PH0),
                               ("OMEN + PHASE 2", T_PH0, N / AN.FPS)], "THE ROSTRUM  //  V3  THE PANTHEON", COL)
    return shot


def caption(shot, t, f, beat, beats, title, col):
    d = ImageDraw.Draw(shot)
    x0 = 1260
    d.rounded_rectangle([x0, 120, 1890, 980], radius=12, fill=(8, 8, 14, 220), outline=col + (160,), width=2)
    d.text((x0 + 24, 140), "BOSS WHEEL v3", font=K.f_anton(40), fill=(255, 255, 255))
    d.text((x0 + 24, 196), title, font=K.f_ui(22, b"Bold Condensed"), fill=col)
    for j, (nm, a0, a1) in enumerate(beats):
        y = 260 + j * 54
        on = a0 <= t < a1
        d.rounded_rectangle([x0 + 24, y, x0 + 600, y + 42], radius=8, fill=(col + (60,)) if on else (24, 24, 34, 255),
                            outline=col + (255,) if on else (60, 60, 76, 255), width=2)
        d.text((x0 + 40, y + 21), nm, font=K.f_ui(22, b"Bold Condensed"), fill=(255, 255, 255) if on else (130, 130, 150), anchor="lm")
        d.text((x0 + 590, y + 21), "%.1f-%.1f s" % (a0, a1), font=K.f_mono(17), fill=(200, 200, 210) if on else (100, 100, 120), anchor="rm")
    words, lines, cur = beat.split(" "), [], ""
    for wd in words:
        if K.f_ui(22).getlength(cur + " " + wd) > 570:
            lines.append(cur)
            cur = wd
        else:
            cur = (cur + " " + wd).strip()
    lines.append(cur)
    for j, ln in enumerate(lines):
        d.text((x0 + 24, 560 + j * 32), ln, font=K.f_ui(22), fill=(230, 232, 240))
    d.rectangle([x0 + 24, 930, x0 + 600, 940], fill=(40, 40, 54))
    d.rectangle([x0 + 24, 930, x0 + 24 + 576 * f / (N - 1), 940], fill=col)
    d.text((x0 + 24, 900), "t = %.2f s   frame %d / %d   24 fps" % (t, f, N), font=K.f_mono(17), fill=(170, 170, 190))


def frames(a, b):
    out = os.path.join(K.SCR, "frames_roman_v3")
    os.makedirs(out, exist_ok=True)
    bd = SH.backdrop("roman")
    bd = Image.fromarray((np.asarray(bd, np.float32) * 0.8).astype(np.uint8))
    for f in range(a, b + 1):
        p = os.path.join(out, "f_%04d.png" % f)
        if os.path.exists(p):
            continue
        frame(f, bd).convert("RGB").save(p)
        print("frame", f, flush=True)


def gif(name="roman_v3"):
    src = os.path.join(K.SCR, "frames_%s" % name)
    fr = [Image.open(os.path.join(src, "f_%04d.png" % f)).convert("RGB").resize((960, 540), Image.LANCZOS).quantize(colors=200, method=Image.MEDIANCUT)
          for f in range(0, N, 2)]
    p = os.path.join(OUT, "%s_anim.gif" % name)
    fr[0].save(p, save_all=True, append_images=fr[1:], duration=int(1000 / 12), loop=0)
    print(p, os.path.getsize(p) // 1024, "KB")


def emblem():
    """The V3 emblem: the VERDICT hand (kept, it is still the needle) in front of a gilt apotheosis sunburst."""
    im = SH.sheet("THE PANTHEON  //  BOSS EMBLEM (v3)", "the VERDICT hand before the apotheosis sunburst: 512 / 128 / 64 / 32 / 16 px, greyscale", COL)
    d = ImageDraw.Draw(im)

    def mk(px):
        ss = 2
        W_ = px * ss
        o = K.rgba((W_, W_))
        dd = ImageDraw.Draw(o)
        c = W_ / 2
        r = W_ * 0.455
        dd.ellipse([0, 0, W_ - 1, W_ - 1], fill=(250, 248, 244, 255))
        dd.ellipse([c - r, c - r, c + r, c + r], fill=(26, 14, 22, 255))
        dd.ellipse([c - r * 0.93, c - r * 0.93, c + r * 0.93, c + r * 0.93], fill=(232, 186, 90, 255))
        dd.ellipse([c - r * 0.84, c - r * 0.84, c + r * 0.84, c + r * 0.84], fill=(40, 60, 120, 255))
        for j in range(16):
            a = math.radians(j * 22.5)
            dd.polygon([(c, c), (c + r * 0.84 * math.cos(a - 0.09), c + r * 0.84 * math.sin(a - 0.09)), (c + r * 0.84 * math.cos(a + 0.09), c + r * 0.84 * math.sin(a + 0.09))],
                       fill=(255, 210, 100, 255))
        h = EH.hand_rgba(int(W_ * 0.74), -1.0, outline=14)
        o.alpha_composite(h, (int(c - h.width / 2), int(c - h.height / 2 + W_ * 0.035)))
        return o.resize((px, px), Image.LANCZOS)
    im.alpha_composite(mk(512), (60, 130))
    x = 640
    for px in (256, 128, 64, 32, 16):
        im.alpha_composite(mk(px), (x, 380 - px // 2))
        SH.label(d, (x, 520), "%d px" % px, (200, 200, 210), K.f_mono(16))
        x += px + 40
    im.alpha_composite(K.greyscale(mk(200)), (640, 600))
    SH.label(d, (640, 810), "greyscale", (200, 200, 210), K.f_mono(16))
    for k_, ln in enumerate(["The needle stays the emperor's box with the VERDICT hand, so the emblem stays the same drawing; the sunburst",
                             "(the apotheosis sky of the hub) ties it to THE PANTHEON. Sunburst rays drop out below 32 px; the hand carries it."]):
        SH.label(d, (60, 940 + k_ * 28), ln, (220, 222, 230), K.f_ui(19))
    p = os.path.join(OUT, "roman_v3_boss_emblem.png")
    im.convert("RGB").save(p)
    print(p)


if __name__ == "__main__":
    w = sys.argv[1]
    if w == "final":
        final()
    elif w == "mechanic":
        mechanic()
    elif w == "frames":
        frames(int(sys.argv[2]), int(sys.argv[3]))
    elif w == "gif":
        gif()
    elif w == "emblem":
        emblem()
    elif w == "one":
        bd = SH.backdrop("roman")
        frame(int(sys.argv[2]), bd).convert("RGB").save(os.path.join(K.SCR, "anim_test.png"))
