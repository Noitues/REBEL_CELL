"""Boss Wheel v2 round 3 (v3) sheets for THE TANK (Atlantis).

python sheets_tank.py final      -> atlantis_v3_final.png
python sheets_tank.py arms       -> atlantis_v3_arms.png
python sheets_tank.py frames a b -> D:/rc_scratch/boss_wheel_v2/frames_atlantis_v3/
python sheets_tank.py gif        -> atlantis_v3_anim.gif
python sheets_tank.py emblem     -> atlantis_v3_boss_emblem.png
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
from PIL import Image, ImageChops, ImageDraw  # noqa: E402

import anim as AN  # noqa: E402
import atlantis_v3 as A  # noqa: E402
import bw_kit as K  # noqa: E402
import sheets as SH  # noqa: E402
import sheets3 as S3  # noqa: E402
import wheel_v2 as W  # noqa: E402

OUT = K.OUTDIR
COL = (47, 107, 255)
PHOTO = A.PHOTO
SW, SHH = 1920, 1080
_D = A.TankV3()


def render(S, **st):
    st.setdefault("t", 0.0)
    ctx = W.Ctx(S)
    im, under = _D.compose(ctx, A.SLOTS, st)
    return im, under


def combat_frame(st, label_txt):
    def fake_render(corp, key, S, **kw):
        im, _ = render(S, **st)
        return im, None, None, A.SLOTS
    old = SH.render
    SH.render = fake_render
    SH.CORP_COL["atlantis_v3"] = COL
    SH.CORP_NAME["atlantis_v3"] = "TETHYS DEEP"
    import directions
    directions.CORPS["atlantis_v3"] = dict(name="THE BLACK SMOKER", slots=A.SLOTS, dirs={})
    try:
        old_bd = SH.backdrop
        SH.backdrop = lambda corp: old_bd("atlantis")
        shot = SH.combat_frame("atlantis_v3", "V3", {}, tip=False, label_txt=label_txt)
    finally:
        SH.render = old
        SH.backdrop = old_bd
    return shot


def crop(im, top=0.08, bot=0.90):
    w = im.width
    return im.crop((int(w * 0.12), int(w * top), int(w * 0.88), int(w * bot)))


def final():
    big = Image.new("RGBA", (SW, SHH * 2), SH.BG + (255,))
    rest = dict(hp=0.6, phase=2, landed=False, show_tips=True)
    big.alpha_composite(combat_frame(rest, "BOSS WHEEL v3  |  THE TANK  |  phase 2: 4 arms, the eyes are up"), (0, 0))
    lo = SH.sheet("THE BLACK SMOKER  //  V3 FINAL: THE TANK", "TETHYS DEEP  |  nothing spins: the predators migrate; every arm is a pointer", COL)
    d = ImageDraw.Draw(lo)
    w1, under = render(SH.COMBAT_S, **rest)
    lo.alpha_composite(crop(w1), (40, 120))
    SH.label(d, (48, 104), "COMBAT SIZE 1:1 (r = 236 px), phase 2: arms 1-4 grip SHARK 8, WRECK 6, JELLYFISH 2, ELECTRIC EEL 5", COL, K.f_ui(18, b"Bold Condensed"))
    S2 = SH.COMBAT_S * 2
    w2, _ = render(S2, **rest)
    c2 = w2.width / 2
    cl = w2.crop((int(c2 - 470), int(c2 - 470), int(c2 + 470), int(c2 + 190)))
    lo.alpha_composite(cl, (900, 110))
    d.rectangle([900, 110, 1840, 770], outline=COL + (120,), width=2)
    SH.label(d, (908, 116), "2x CLOSE-UP", COL, K.f_ui(18, b"Bold Condensed"))
    states = [("REST: 4 arms, tips lit by their predator", dict(rest)),
              ("MIGRATING (the 'spin'): fish swim, plaques ride", dict(rest, rot=-20, swim=1.0, blur=10, school=0.4, offsets=[0, 6, -4, 8, -6, 3, -8, 5], plaque_fade=0.7)),
              ("LANDED: arms grip, PERFECT latch", dict(rest, landed=True, grab=1.0, latch=1.0, act={0: 1.0, 2: 0.8}))]
    for j, (nm, s_) in enumerate(states):
        w3, _ = render(SH.COMBAT_S, **s_)
        c3 = w3.width / 2
        crp = w3.crop((int(c3 - 170), int(c3 - 290), int(c3 + 170), int(c3 - 40)))
        xx = 900 + j * 340
        lo.alpha_composite(crp, (xx, 800))
        d.rectangle([xx, 800, xx + 340, 1050], outline=(70, 70, 86), width=1)
        SH.label(d, (xx + 6, 1054), nm, (220, 220, 230), K.f_ui(15, b"Bold Condensed"))
    blurb = ["The tank is fixed. The predators ARE the slices: a spin of N ticks moves the fish N zones, nudges herd them.",
             "Every arm that climbs out of the tank is a pointer; the fight escalates 2 -> 4 -> 6 -> 8 arms, and the creature",
             "rises with them: unseen, then its eyes, its mantle, and at the end the cybernetic kraken, the corporation's brain."]
    for k_, ln in enumerate(blurb):
        SH.label(d, (40, 960 + k_ * 26), ln, (220, 222, 230), K.f_ui(17))
    big.alpha_composite(lo, (0, SHH))
    p = os.path.join(OUT, "atlantis_v3_final.png")
    big.convert("RGB").save(p)
    print(p)


def arms_sheet():
    im = K.rgba((SW, 1150), SH.BG, 255)
    hdr = SH.sheet("THE TANK  //  ARMS + REVEAL", "2 -> 4 -> 6 -> 8 pointers; the creature rises with every phase", COL)
    im.alpha_composite(hdr.crop((0, 0, SW, 100)), (0, 0))
    d = ImageDraw.Draw(im)
    stages = [("PHASE 1  |  HP 100-75 %  |  2 ARMS", "body unseen: a shadow, bubbles, a glint", dict(hp=0.9, phase=1, show_tips=True)),
              ("PHASE 2  |  75-50 %  |  4 ARMS", "the eyes break the surface", dict(hp=0.6, phase=2)),
              ("PHASE 3  |  50-25 %  |  6 ARMS", "the mantle is out, blue rings glow", dict(hp=0.4, phase=3)),
              ("FINAL  |  < 25 %  |  8 ARMS", "THE REVEAL: the cybernetic kraken", dict(hp=0.15, phase=3))]
    for j, (nm, sub, st) in enumerate(stages):
        w, under = render(0.62, **st)
        c = crop(w, 0.14, 0.92)
        c = c.resize((450, int(450 * c.height / c.width)), Image.LANCZOS)
        x = 18 + j * 474
        im.alpha_composite(c, (x, 170))
        SH.label(d, (x + 6, 112), nm, (255, 120, 90) if j == 3 else PHOTO, K.f_ui(21, b"Bold Condensed"))
        SH.label(d, (x + 6, 140), sub, (210, 212, 222), K.f_ui(17))
    # the reveal close-up
    w, _ = render(1.2, hp=0.15, phase=3)
    c = w.width / 2
    rv = w.crop((int(c - 240), int(c - 280), int(c + 240), int(c + 200)))
    im.alpha_composite(rv.resize((420, 420), Image.LANCZOS), (40, 690))
    SH.label(d, (40, 664), "THE REVEAL (close-up)", (255, 120, 90), K.f_ui(21, b"Bold Condensed"))
    rows = ["THE CURVE: 2 arms (100-75 %), 4 (75-50 %), 6 (50-25 %), 8 (< 25 %). Phase pips on the HP arc at 75 / 50 / 25.",
            "Arms emerge in a fixed order (top, bottom, right, left, then the diagonals), so every pointer position is known in advance;",
            "the empty sockets on the tank wall (1-8) show the arms still to come.",
            "",
            "8 ARMS = A SPRINT (designer ruling): with all 8 out, every slice resolves every turn. No damage scaling: the last quarter is",
            "a deliberate race of who kills whom first. The tired-arm 0.5x idea is withdrawn.",
            "",
            "THE REVEAL: the corporation's brain. Cranial plates bolted over the mantle, a TETHYS plate, an antenna beacon, an LED eye",
            "array across the brow, cable tendons down every arm. It climbs OUT of the tank (32 % bigger, over the rim). The REVEAL beat:",
            "hit-stop 3 frames, the water boils white, the two last arms burst out (0.6 s), the plates and cables light up left to right (0.8 s).",
            "Reduce effects: the final art appears at once; no boil, no flicker; the LED array is steady.",
            "",
            "OCTOPUS OR KRAKEN: an octopus (8 arms, bar pupils) is the honest silhouette at r = 60; it is called the Kraken in the fiction."]
    for k_, ln in enumerate(rows):
        SH.label(d, (500, 690 + k_ * 28), ln, (226, 228, 236) if not ln.startswith(("8 ARMS", "THE REVEAL", "THE CURVE")) else (124, 242, 228), K.f_ui(19))
    p = os.path.join(OUT, "atlantis_v3_arms.png")
    im.convert("RGB").save(p)
    print(p)


# ------------------------------------------------------------------ animation (6.5 s)
N = 156
T_M0, T_M1 = 1.0, 2.5          # migration 1: the predators swim 3 zones
T_L1 = 2.5
T_PH = 3.5                     # HP crosses 25 %: the reveal
T_E1 = 4.6
T_M2, T_M3 = 5.0, 5.7          # migration 2: one zone
P_EXP = [2.2, 3.4, 2.8, 4.0, 2.4, 1.6, 3.0, 2.0]   # per-fish easing exponents (mines drift late, sharks surge)


def migrate(t, t0, t1, rot0, delta):
    if t <= t0:
        return rot0, [0.0] * 8, 0.0
    u = min(1.0, (t - t0) / (t1 - t0))
    e = 1 - (1 - u) ** 2.6
    rot = rot0 + delta * e
    offs = [delta * ((1 - (1 - u) ** P_EXP[i]) - e) for i in range(8)]
    swim = math.sin(math.pi * u)
    return rot, offs, swim


def state(f):
    t = f / AN.FPS
    st = dict(t=t, hp=0.27, phase=3, blink=0.0, show_tips=True)
    beat = "IDLE: 6 arms out, the mantle above the water; predators idle in their zones; the arm tips glow with the fish they hold"
    rot, offs, swim = migrate(t, T_M0, T_M1, 0.0, -135.0)
    if t >= T_M2:
        rot, offs, swim = migrate(t, T_M2, T_M3, -135.0, -45.0)
    st.update(rot=rot, offsets=offs, swim=swim)
    if T_M0 < t < T_M1 or T_M2 < t < T_M3:
        st["blur"] = 10 * swim
        st["school"] = (t - T_M0) / (T_M1 - T_M0) if t < T_M1 else (t - T_M2) / (T_M3 - T_M2)
        st["plaque_fade"] = 1 - 0.35 * swim
        beat = "THE 'SPIN': NOTHING TURNS. The predators migrate round the tank (seeded spin = 3 zones); a barracuda school sweeps past"
        st["show_tips"] = False
    if T_L1 <= t < T_PH:
        u = min(1.0, (t - T_L1) / 0.25)
        st.update(landed=True, grab=u, latch=min(1.0, (t - T_L1) / 0.08), act={i: min(1.0, (t - T_L1) / 0.5) for i in range(8)})
        beat = "LAND: each arm grips the predator under it; tips light in its type colour; 6 slices resolve"
    if t >= T_PH:
        st["hp"] = 0.2
        st["n_arms"] = 8
        u = min(1.0, max(0.0, (t - T_PH - 3 / AN.FPS) / 0.6))
        st["emerge"] = AN.ease_out_cubic(u)
        st["emerge_from"] = 6
        st["reveal"] = AN.ease_out_cubic(min(1.0, max(0.0, (t - T_PH - 0.3) / 0.8)))
        beat = "HP < 25 %: THE REVEAL. Arms 7 and 8 burst out; the cybernetic kraken climbs out of the tank: the corporation's brain"
    if t >= T_M2:
        beat = "8 ARMS: the predators migrate one more zone ..."
    if t >= T_M3:
        u = min(1.0, (t - T_M3) / 0.25)
        st.update(landed=True, grab=u, latch=min(1.0, (t - T_M3) / 0.08), act={i: min(1.0, (t - T_M3) / 0.5) for i in range(8)})
        beat = "... and ALL 8 ARMS LAND: every slice resolves. The sprint: who kills whom first."
    return t, st, beat


def frame(f, bd):
    t, st, beat = state(f)
    S = AN.S
    if T_PH <= t < T_PH + 3 / AN.FPS:
        st = dict(st, t=T_PH)
    w, _ = render(S, **st)
    fl = max(0.0, 1 - (t - T_PH) / 0.25) if t >= T_PH else 0.0
    if fl > 0:
        w = K.add(w, K.solid(K.blur(K.ring_mask(w.size, w.width / 2, w.height / 2, 0, 140 * S), 20 * S), (230, 250, 255)), 1.2 * fl)
    shot = bd.copy()
    shot.alpha_composite(K.solid(K.blur(w.split()[3], 12), (0, 0, 0), 0.5), (int(AN.CX - w.width / 2 + 6), int(AN.CY - w.height / 2 + 12)))
    shot.alpha_composite(w, (int(AN.CX - w.width / 2), int(AN.CY - w.height / 2)))
    if T_L1 + 0.05 <= t < T_L1 + 0.8:
        ws = AN.word_sticker("6 ARMS LAND", PHOTO, px=46)
        shot.alpha_composite(ws, (int(AN.CX + 300 - ws.width / 2), int(AN.CY - 420 - ws.height / 2)))
    if T_PH + 0.15 <= t < T_PH + 1.4:
        ws = AN.word_sticker("THE REVEAL", (255, 90, 80))
        shot.alpha_composite(ws, (int(AN.CX - 360 - ws.width / 2), int(AN.CY - 420 - ws.height / 2)))
    if t >= T_M3 + 0.05:
        ws = AN.word_sticker("8 ARMS: EVERY SLICE", (255, 214, 64), px=44)
        shot.alpha_composite(ws, (int(AN.CX + 260 - ws.width / 2), int(AN.CY - 420 - ws.height / 2)))
    S3.N = N
    S3.caption(shot, t, f, beat, [("IDLE", 0.0, T_M0), ("FISH MIGRATE (spin)", T_M0, T_L1), ("6 ARMS LAND", T_L1, T_PH),
                                  ("THE REVEAL: 8 ARMS", T_PH, T_M2), ("MIGRATE + ALL LAND", T_M2, N / AN.FPS)],
               "THE BLACK SMOKER  //  V3  THE TANK", COL)
    return shot


def frames(a, b):
    out = os.path.join(K.SCR, "frames_atlantis_v3")
    os.makedirs(out, exist_ok=True)
    bd = SH.backdrop("atlantis")
    bd = Image.fromarray((np.asarray(bd, np.float32) * 0.8).astype(np.uint8))
    for f in range(a, b + 1):
        p = os.path.join(out, "f_%04d.png" % f)
        if os.path.exists(p):
            continue
        frame(f, bd).convert("RGB").save(p)
        print("frame", f, flush=True)


def emblem():
    """v3 emblem: the cybernetic kraken rising out of the tank: 8 arms, the LED brow, cranial plate."""
    import sheets2 as S2
    im = SH.sheet("THE BLACK SMOKER  //  BOSS EMBLEM (v3)", "the kraken climbing out of the tank: 8 arms, LED brow, plate  |  512 / 128 / 64 / 32 / 16 px", COL)
    d = ImageDraw.Draw(im)

    def mk(px):
        ss = 2
        W_ = px * ss
        o = K.rgba((W_, W_))
        dd = ImageDraw.Draw(o)
        c = W_ / 2
        r = W_ * 0.455
        dd.ellipse([0, 0, W_ - 1, W_ - 1], fill=(250, 248, 244, 255))
        dd.ellipse([c - r, c - r, c + r, c + r], fill=(14, 10, 22, 255))
        dd.ellipse([c - r * 0.93, c - r * 0.93, c + r * 0.93, c + r * 0.93], fill=COL + (255,))
        dd.ellipse([c - r * 0.84, c - r * 0.84, c + r * 0.84, c + r * 0.84], fill=(6, 17, 42, 255))
        k = r / 100
        # the tank rim (an ellipse) the creature climbs out of
        dd.ellipse([c - 60 * k, c + 22 * k, c + 60 * k, c + 52 * k], fill=(30, 90, 130, 255), outline=(14, 10, 22, 255), width=max(1, int(4 * k)))
        body = K.L((W_, W_))
        bd = ImageDraw.Draw(body)
        for j in range(8):
            a0 = j * 45 + 22.5
            sg = 1 if j % 2 else -1
            pts = [K.pol(c, c + 4 * k, (22 + 58 * q / 14) * k, a0 + sg * 20 * math.sin(q / 14 * 3)) for q in range(15)]
            bd.polygon(K.stroke_poly(pts, 13 * k, 4 * k), fill=255)
            x, y = pts[-1]
            tx, ty = K.pol(x, y, 5 * k, a0 + sg * 70)
            bd.ellipse([tx - 5.5 * k, ty - 5.5 * k, tx + 5.5 * k, ty + 5.5 * k], fill=255)
        bd.polygon(K.catmull([(c, c - 58 * k), (c + 34 * k, c - 44 * k), (c + 40 * k, c), (c + 26 * k, c + 30 * k), (c, c + 36 * k),
                              (c - 26 * k, c + 30 * k), (c - 40 * k, c), (c - 34 * k, c - 44 * k)], 10), fill=255)
        skin = (200, 52, 62)
        lay = K.solid(K.grow(body, 5 * k), (14, 10, 22))
        lay.alpha_composite(K.solid(body, skin))
        lay.alpha_composite(K.solid(ImageChops.subtract(body, K.shifted(body, -4 * k, -5 * k)), K.mul(skin, 0.7)))
        ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([c - 26 * k, c - 54 * k, c + 26 * k, c - 36 * k], radius=5 * k, fill=(170, 184, 200, 255), outline=(14, 10, 22, 255), width=max(1, int(2.5 * k)))
        ld.rounded_rectangle([c - 34 * k, c - 12 * k, c + 34 * k, c - 2 * k], radius=4 * k, fill=(24, 16, 22, 255), outline=(14, 10, 22, 255))
        for q in range(5):
            x = c + (-24 + q * 12) * k
            ld.ellipse([x - 3.2 * k, c - 10.2 * k, x + 3.2 * k, c - 3.8 * k], fill=(255, 70, 60, 255))
        for sg in (-1, 1):
            ex, ey = c + sg * 18 * k, c + 12 * k
            ld.ellipse([ex - 9 * k, ey - 6 * k, ex + 9 * k, ey + 6 * k], fill=(14, 10, 22, 255))
            ld.ellipse([ex - 7 * k, ey - 4 * k, ex + 7 * k, ey + 4 * k], fill=(255, 196, 70, 255))
            ld.rectangle([ex - 5 * k, ey - 1.2 * k, ex + 5 * k, ey + 1.2 * k], fill=(14, 10, 22, 255))
        ld.arc([c - 24 * k, c - 52 * k, c + 4 * k, c - 24 * k], 200, 250, fill=(255, 255, 255, 200), width=max(1, int(3 * k)))
        o.alpha_composite(lay)
        return o.resize((px, px), Image.LANCZOS)
    im.alpha_composite(mk(512), (60, 130))
    x = 640
    for px in (256, 128, 64, 32, 16):
        im.alpha_composite(mk(px), (x, 380 - px // 2))
        SH.label(d, (x, 520), "%d px" % px, (200, 200, 210), K.f_mono(16))
        x += px + 40
    im.alpha_composite(K.greyscale(mk(200)), (640, 600))
    SH.label(d, (640, 810), "greyscale", (200, 200, 210), K.f_mono(16))
    for k_, ln in enumerate(["The v3 emblem: the kraken (an octopus, 8 arms) climbing out of its tank, wearing the corp's hardware: the TETHYS",
                             "plate and the LED brow from the reveal. The 8 arms are the 8 pointers. The v2 emblem file now also has 8 arms."]):
        SH.label(d, (60, 940 + k_ * 28), ln, (220, 222, 230), K.f_ui(19))
    p = os.path.join(OUT, "atlantis_v3_boss_emblem.png")
    im.convert("RGB").save(p)
    print(p)


if __name__ == "__main__":
    w = sys.argv[1]
    if w == "final":
        final()
    elif w == "arms":
        arms_sheet()
    elif w == "frames":
        frames(int(sys.argv[2]), int(sys.argv[3]))
    elif w == "gif":
        S3.gif("atlantis_v3")
    elif w == "emblem":
        emblem()
    elif w == "one":
        bd = SH.backdrop("atlantis")
        frame(int(sys.argv[2]), bd).convert("RGB").save(os.path.join(K.SCR, "anim_test.png"))
