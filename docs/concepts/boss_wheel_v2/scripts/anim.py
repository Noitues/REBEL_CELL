"""Boss Wheel v2: the animation reel (~6.5 s, 24 fps): idle, spin (blur + parallax), land (PERFECT latch), the slice
figure acts, the needle reacts, a phase change (hit-stop, flash, art cross-fade, cracks).

python anim.py frames <corp> <key> <first> <last>   -> D:/rc_scratch/boss_wheel_v2/frames_<corp>/f_####.png
python anim.py gif <corp>                           -> <corp>_anim.gif (960x540, 12 fps: every 2nd frame)
Encode the mp4 with Blender's FFmpeg: blender -b -P encode_mp4.py -- <frames dir> <out.mp4> <n>
Deterministic: time comes from the frame index only; every random draw is seeded.
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import bw_kit as K  # noqa: E402
import directions  # noqa: E402
import sheets as SH  # noqa: E402
import wheel_v2 as W  # noqa: E402

FPS = 24
N = 156                       # 6.5 s
S = 0.86
CX, CY = 700, 610
T_IDLE, T_SPIN0, T_LAND, T_ACT1, T_PH0, T_PH1 = 1.2, 1.2, 2.7, 3.9, 4.4, 5.4
ROT0 = -120.0                 # rest: the forecast is slot 2
SPIN_TO = -720.0              # two turns, lands on slot 0 (the attack slice)
CFG = {  # per final: rest rotation, landing rotation (slot 0 under the needle), the needle's angle
    ("roman", "D"): dict(rot0=-120.0, rot1=-720.0),
    ("atlantis", "D"): dict(rot0=60.0, rot1=-540.0),      # beak at 6 o'clock: slot i sits there when 60 i + rot = 180
}

ACT_NAME = {"roman": "THE CHARIOT CHARGES", "atlantis": "THE HARPOON FIRES"}
HIT_G = {"roman": -1.0, "atlantis": 1.0}        # the needle's 'hit' pose (thumb down / lure squeeze)
HIT_WORD = {"roman": "THUMB DOWN: HIT", "atlantis": "THE ARM SQUEEZES: HIT"}
PH_WORD = {"roman": "PHASE 2: THE STANDS FILL, THE ARCHES BURN", "atlantis": "PHASE 2: THE OCTOPUS WAKES"}
ACT_NAME[("roman", "D")] = "THE CHARIOT SURGES, THE LION POUNCES"
ACT_NAME[("atlantis", "D")] = "THE TWO BORDER ARMS GRAB THE SLICE, THE BEAK SNAPS, THE HARPOON FIRES"
PH_WORD[("roman", "D")] = "PHASE 2: THE CROWD FILLS, BRAZIERS LIGHT, THE GATES OPEN AND BEASTS WALK IN"
PH_WORD[("atlantis", "D")] = "PHASE 2: THE EYES OPEN WIDE, THE SKIN FLUSHES, THE BLUE RINGS GLOW"
HIT_WORD[("roman", "D")] = "THUMB DOWN: HIT"
HIT_WORD[("atlantis", "D")] = "THE BEAK SNAPS: HIT"


def ease_out_cubic(u):
    return 1 - (1 - u) ** 3


def spin_rot(t, rot0=None, rot1=None):
    ROT0_ = ROT0 if rot0 is None else rot0
    SPIN_TO_ = SPIN_TO if rot1 is None else rot1
    return _spin(t, ROT0_, SPIN_TO_)


def _spin(t, ROT0, SPIN_TO):
    if t < T_SPIN0:
        return ROT0, 0.0
    if t >= T_LAND:
        return SPIN_TO, 0.0
    u = (t - T_SPIN0) / (T_LAND - T_SPIN0)
    e = 1 - (1 - u) ** 3.2
    rot = ROT0 + (SPIN_TO - ROT0) * e
    du = 1.0 / FPS / (T_LAND - T_SPIN0)
    e2 = 1 - (1 - min(1, u + du)) ** 3.2
    speed = abs((SPIN_TO - ROT0) * (e2 - e))   # deg per frame
    return rot, speed


def state_at(corp, f, key="A"):
    t = f / FPS
    cfg = CFG.get((corp, key), {})
    rot, speed = spin_rot(t, cfg.get("rot0"), cfg.get("rot1"))
    ck = (corp, key)
    act_name = ACT_NAME.get(ck, ACT_NAME[corp])
    hit_word = HIT_WORD.get(ck, HIT_WORD[corp])
    ph_word = PH_WORD.get(ck, PH_WORD[corp])
    st = dict(t=t, rot=rot, phase=1, hp=0.74, dmg=0.12, gesture=0.0, still=False)
    beat = "IDLE: crowd / torches / the arms sway, the forecast slice glows"
    if corp == "atlantis":
        st["blink"] = 0.5
        beat = "IDLE: the arms sway, the octopus dozes, bubbles; the forecast slice glows"
    st["forecast"] = 2 if t < T_SPIN0 else None
    st["spin_speed"] = -speed
    st["inner_rot"] = rot
    if key == "D" and corp == "roman":
        beat = "IDLE: chariots gallop the track, the fighters spar, the captives wait, the crowd stirs"
    if key == "D" and corp == "atlantis":
        beat = "IDLE: the arms ripple, the head breathes, the forecast slice glows under the beak"
    if T_SPIN0 <= t < T_LAND:
        st["blur"] = min(40.0, speed * 1.4)
        a = math.radians(rot)
        k = min(1.0, speed / 12.0)
        st["par"] = (6 * k * math.cos(a), 6 * k * math.sin(a))
        st["under_lag"] = 2.5 * k
        beat = "SPIN: motion blur on the art, parallax between the layers (back plate lags, rim art leads)"
    if t >= T_LAND:
        st["landed"] = 0
        st["tier"] = "PERFECT"
        lu = min(1.0, (t - T_LAND) / 0.08)
        st["latch"] = lu
        st["flash"] = max(0.0, 1 - (t - T_LAND) / 0.25)
        st["flash_col"] = K.PERFECT_GOLD
        st["pop"] = max(0.0, 1 - abs(t - T_LAND - 0.15) / 0.2)
        beat = "LAND: PERFECT, the jaws latch the blade"
    if t >= T_LAND + 0.1:
        u = min(1.0, (t - T_LAND - 0.1) / 0.7)
        st["act_slot"] = 0
        st["act"] = math.sin(math.pi * min(1.0, u)) if u < 1 else 0.0
        st["act"] = min(1.0, u * 1.4) if t < T_ACT1 else max(0.0, 1 - (t - T_ACT1) / 0.4)
        g0 = 0.0
        gu = min(1.0, (t - T_LAND - 0.15) / 0.3)
        st["gesture"] = g0 + (HIT_G[corp] - g0) * ease_out_cubic(max(0.0, gu))
        beat = "THE SLICE ACTS: %s  |  NEEDLE: %s" % (act_name, hit_word)
        st["finisher"] = st["act"]
        st["grab"] = min(1.0, (t - T_LAND) / 0.25) if t < T_PH0 else 0.0
        bu = (t - T_LAND - 0.1) / 0.3
        st["beak"] = math.sin(math.pi * min(1.0, max(0.0, bu))) if bu < 1 else 0.0
    if t >= T_PH0:
        st["hp"] = 0.62
        st["tier"] = None
        st["latch"] = 0.0
        st["landed"] = None
        st["forecast"] = None
        g_back = max(0.0, 1 - (t - T_PH0) / 0.4)
        st["gesture"] = HIT_G[corp] * g_back
        st["act"] = 0.0
        beat = ph_word
    return t, st, beat


def render_state(D, slots, st, phase_mix=None):
    ctx = W.Ctx(S, **st)
    return W.compose(D, ctx, slots)


def word_sticker(txt, col, px=54, edge=(20, 12, 4)):
    f = K.f_anton(px)
    t = K.text_img(txt, f, fill=col, stroke=3, edge=edge)
    pad = 14
    body = K.rgba((t.width + pad * 2, t.height + pad * 2))
    d = ImageDraw.Draw(body)
    d.rounded_rectangle([0, 0, body.width - 1, body.height - 1], radius=14, fill=(16, 12, 10, 240))
    body.alpha_composite(t, (pad, pad))
    cut = K.grow(body.split()[3], 6)
    out = K.solid(cut, (246, 244, 238))
    out.alpha_composite(body)
    return K.drop_shadow(out, 4, 6, 5, 0.6)


def frame(corp, key, f, base_bd):
    D, slots = directions.get(corp, key)
    t, st, beat = state_at(corp, f, key)
    # hit-stop: 3 frames frozen right as the pip is crossed
    freeze = T_PH0 <= t < T_PH0 + 3 / FPS
    if T_PH0 <= t:
        u = min(1.0, max(0.0, (t - T_PH0 - 3 / FPS) / (T_PH1 - T_PH0)))
        st1 = dict(st, phase=1, dmg=0.12, gates=0.0)
        st2 = dict(st, phase=2, dmg=0.12 + 0.28 * u, gates=u)
        if corp == "atlantis":
            st1["blink"] = 0.5
            st2["blink"] = max(0.0, 0.5 - u)
        if freeze:
            st1["t"] = st2["t"] = T_PH0
        a = render_state(D, slots, st1) if u < 1 else None
        D2, _ = directions.get(corp, key)
        b = render_state(D2, slots, st2)
        w = Image.blend(a, b, ease_out_cubic(u)) if a is not None else b
        fl = max(0.0, 1 - (t - T_PH0) / 0.18)
        if fl > 0:   # white flash on the wheel only (never full screen)
            m = K.blur(w.split()[3], 2)
            w = K.add(w, K.solid(m, (255, 255, 255)), 0.7 * fl)
    else:
        w = render_state(D, slots, st)
    shot = base_bd.copy()
    shot.alpha_composite(K.solid(K.blur(w.split()[3], 12), (0, 0, 0), 0.5), (int(CX - w.width / 2 + 6), int(CY - w.height / 2 + 12)))
    shot.alpha_composite(w, (int(CX - w.width / 2), int(CY - w.height / 2)))
    d = ImageDraw.Draw(shot)
    # temporary labels (vinyl words, ~0.75 s then they would dissolve to bits)
    if T_LAND + 0.05 <= t < T_LAND + 0.8:
        ws = word_sticker("PERFECT", K.PERFECT_GOLD)
        k = min(1.0, (t - T_LAND - 0.05) / 0.08)
        ws = ws.resize((max(1, int(ws.width * (0.6 + 0.4 * k))), max(1, int(ws.height * (0.6 + 0.4 * k)))), Image.LANCZOS)
        shot.alpha_composite(ws, (int(CX + 300 - ws.width / 2), int(CY - 420 - ws.height / 2)))
    if T_PH0 + 0.15 <= t < T_PH0 + 1.3:
        ws = word_sticker("PHASE 2", (255, 120, 60) if corp == "roman" else (255, 90, 110))
        shot.alpha_composite(ws, (int(CX - 380 - ws.width / 2), int(CY - 400 - ws.height / 2)))
    # caption panel (right)
    x0 = 1260
    d.rounded_rectangle([x0, 120, 1890, 980], radius=12, fill=(8, 8, 14, 220), outline=SH.CORP_COL[corp] + (160,), width=2)
    d.text((x0 + 24, 140), "BOSS WHEEL v2", font=K.f_anton(40), fill=(255, 255, 255))
    d.text((x0 + 24, 196), "%s  //  %s" % (directions.CORPS[corp]["name"], D.title), font=K.f_ui(22, b"Bold Condensed"), fill=SH.CORP_COL[corp])
    beats = [("IDLE", 0.0, T_SPIN0), ("SPIN", T_SPIN0, T_LAND), ("LAND", T_LAND, T_LAND + 0.15), ("ACT + NEEDLE", T_LAND + 0.15, T_PH0),
             ("PHASE 2", T_PH0, N / FPS)]
    for j, (nm, a0, a1) in enumerate(beats):
        y = 260 + j * 54
        on = a0 <= t < a1
        d.rounded_rectangle([x0 + 24, y, x0 + 600, y + 42], radius=8, fill=(SH.CORP_COL[corp] + (60,)) if on else (24, 24, 34, 255),
                            outline=SH.CORP_COL[corp] + (255,) if on else (60, 60, 76, 255), width=2)
        d.text((x0 + 40, y + 21), nm, font=K.f_ui(22, b"Bold Condensed"), fill=(255, 255, 255) if on else (130, 130, 150), anchor="lm")
        d.text((x0 + 590, y + 21), "%.1f-%.1f s" % (a0, a1), font=K.f_mono(17), fill=(200, 200, 210) if on else (100, 100, 120), anchor="rm")
    # wrap the beat text
    words = beat.split(" ")
    lines, cur = [], ""
    for wd in words:
        if K.f_ui(22).getlength(cur + " " + wd) > 570:
            lines.append(cur)
            cur = wd
        else:
            cur = (cur + " " + wd).strip()
    lines.append(cur)
    for j, ln in enumerate(lines):
        d.text((x0 + 24, 560 + j * 32), ln, font=K.f_ui(22), fill=(230, 232, 240))
    # timeline
    d.rectangle([x0 + 24, 930, x0 + 600, 940], fill=(40, 40, 54))
    d.rectangle([x0 + 24, 930, x0 + 24 + 576 * f / (N - 1), 940], fill=SH.CORP_COL[corp])
    d.text((x0 + 24, 900), "t = %.2f s   frame %d / %d   24 fps" % (t, f, N), font=K.f_mono(17), fill=(170, 170, 190))
    return shot


def frames(corp, key, a, b):
    out = os.path.join(K.SCR, "frames_%s" % corp)
    os.makedirs(out, exist_ok=True)
    bd = SH.backdrop(corp)
    bd = Image.fromarray((np.asarray(bd, np.float32) * 0.8).astype(np.uint8))
    for f in range(a, b + 1):
        p = os.path.join(out, "f_%04d.png" % f)
        if os.path.exists(p):
            continue
        im = frame(corp, key, f, bd)
        im.convert("RGB").save(p)
        print("frame", f, flush=True)


def gif(corp):
    src = os.path.join(K.SCR, "frames_%s" % corp)
    fr = []
    for f in range(0, N, 2):
        im = Image.open(os.path.join(src, "f_%04d.png" % f)).convert("RGB").resize((960, 540), Image.LANCZOS)
        fr.append(im.quantize(colors=200, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG))
    p = os.path.join(K.OUTDIR, "%s_anim.gif" % corp)
    fr[0].save(p, save_all=True, append_images=fr[1:], duration=int(1000 / 12), loop=0, optimize=False)
    print(p, os.path.getsize(p) // 1024, "KB")


if __name__ == "__main__":
    if sys.argv[1] == "frames":
        frames(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    elif sys.argv[1] == "gif":
        gif(sys.argv[2])
    elif sys.argv[1] == "one":
        bd = SH.backdrop(sys.argv[2])
        frame(sys.argv[2], sys.argv[3], int(sys.argv[4]), bd).convert("RGB").save(os.path.join(K.SCR, "anim_test.png"))
