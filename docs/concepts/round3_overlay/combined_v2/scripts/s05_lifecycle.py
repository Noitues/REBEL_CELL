"""05_lifecycle.png: the SEND IT verb sticker and the grease-pencil target moving together on combat.

APPEAR  SEND IT slaps on (ghost in the air, squash on contact, shine sweep); the red circle draws.
IDLE    the sticker's corner flutters and the holo foil shifts; a glint runs across the wax.
EXIT    the sticker peels off from its lifted corner and curls away; a palm smears the pencil.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from kit import *  # noqa
import s01_combat as C

CROP = (1320, 380, 1920, 1080)        # 600 x 700
PW, PH = 600, 700


def frame(stage, base):
    img = C.pencil_composite(base, C.pencil_layer(np.random.default_rng(101), **{
        "appear": dict(progress=0.55), "idle": dict(progress=1.0, glint=0.80), "exit": dict(wipe=0.76)}[stage]))
    img = glass(img, np.random.default_rng(11), C.SMUDGES, band_pos=0.30)
    nx, ny, na = C.NOTE_POS
    img = place_sticker(img, C.stickers()[1], nx, ny, angle=na)
    cx, cy, ang = C.SEND_POS
    if stage == "appear":
        # ghost: in the air, over-rotated and bigger; then the squash on contact with the shine mid-sweep
        img = place_sticker(img, C.send_it(gloss_pos=0.0, curl=None), cx - 30, cy - 90, angle=ang + 13,
                            scale=1.24, hover=1.0, opacity=0.3, shadow=0.6)
        img = place_sticker(img, C.send_it(gloss_pos=0.58, curl=None), cx, cy + 6, angle=ang + 2,
                            squash=(1.13, 0.84), shadow=1.2)
    elif stage == "idle":
        img = place_sticker(img, C.send_it(phase=0.22, curl=dict(corner="tr", amount=0.20)), cx, cy, angle=ang,
                            opacity=0.35, shadow=0.0)
        img = place_sticker(img, C.send_it(phase=0.40, gloss_pos=0.42, curl=dict(corner="tr", amount=0.08)),
                            cx, cy, angle=ang)
    else:
        img = place_sticker(img, C.send_it(phase=0.55, gloss_pos=0.62,
                                           curl=dict(corner="tr", amount=0.62, bend=0.25, flap_shadow=0.6)),
                            cx - 40, cy + 36, angle=ang - 12, scale=0.96, hover=0.7)
    x0, y0, x1, y1 = CROP
    return f2pil(img[y0:y1, x0:x1])


def build():
    base = C.combat_base()
    sheet = Image.new("RGB", (W, H), (13, 13, 17))
    d = ImageDraw.Draw(sheet)
    d.text((45, 40), "SEND IT  /  KIT LIFECYCLE  v2", font=MK.bahn(32, "Bold"), fill=(236, 236, 230))
    d.text((45, 84), "holo verb sticker + grease-pencil target, moving together on the combat screen",
           font=MK.bahn(19, "SemiLight"), fill=(150, 150, 158))
    caps = [("01  APPEAR", "0.00 - 0.45 s",
             "SEND IT drops in from 1.24x, over-rotated 13 deg, and slaps:\nsquash 1.13 / 0.84 (90 ms), one overshoot, shine sweep.\n"
             "The red pencil circle draws in writing order."),
            ("02  IDLE", "loop",
             "The top-right corner flutters 0.08 <-> 0.20 (2.4 s).\nThe holo foil hue drifts; the gloss band breathes.\n"
             "A thin glint runs across the wax every ~3 s."),
            ("03  EXIT", "0.30 s with the page",
             "The sticker peels from its lifted corner (fold 0 -> 0.6),\nlifts (shadow blurs) and curls away down-left.\n"
             "A palm drags the pencil into a red haze. EXECUTE stays.")]
    for i, st in enumerate(("appear", "idle", "exit")):
        x = 45 + i * (PW + 30)
        y = 130
        sheet.paste(Image.new("RGB", (PW + 4, PH + 4), (44, 44, 52)), (x - 2, y - 2))
        sheet.paste(frame(st, base), (x, y))
        t, tm, body = caps[i]
        d.rectangle((x, y + PH + 22, x + 6, y + PH + 52), fill=K_PINK)
        d.text((x + 18, y + PH + 18), t, font=MK.bahn(26, "Bold"), fill=(240, 240, 236))
        d.text((x + PW, y + PH + 22), tm, font=MK.bahn(18, "SemiLight"), fill=(160, 160, 168), anchor="ra")
        d.multiline_text((x + 18, y + PH + 60), body, font=MK.bahn(17, "SemiLight"), fill=(175, 175, 182), spacing=6)
    sheet.save(os.path.join(OUT, "05_lifecycle.png"))
    print("saved 05_lifecycle.png")


if __name__ == "__main__":
    build()
