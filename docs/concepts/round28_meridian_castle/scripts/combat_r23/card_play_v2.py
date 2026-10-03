"""Round 19 / 1 + 2: card play v2 with the locked CARD-PLAY PREVIEW, and the three dissolves as separate GIFs.

While HEAVY SPIN is hovered (and while it is aimed), the round 17 preview plays on THE MANIFEST: the chevron
chase runs from the top needle 9 ticks anticlockwise, then a ghost blade + dashed slice outline fade in where
the needle will land (EXPLOIT 14). Slap -> dissolve A -> the wheel spins and the ghost rides the slices up to
the real blade, meeting it exactly (preview == result).

python card_play_v2.py            # card_play_v2.gif + card_play_v2_storyboard.png
python card_play_v2.py dissolves  # dissolve_A_bitstream.gif, dissolve_B_scanline.gif, dissolve_C_crumble.gif
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from PIL import Image, ImageDraw

import plates as P
import fxlib as FX
import card_play as CP
import preview as PV
from fxlib import seg, ease_out_cubic

OUT = P.OUT
T_CHASE = (900, 1500)
T_GHOST = (1400, 1600)
T_LABEL = (1560, CP.T_PEEL[0] + 120)


def hook(img, t):
    if t < T_CHASE[0]:
        return img
    chase = min(1.0, seg(t, *T_CHASE)) if t < T_CHASE[1] else 1.0
    ghosts = seg(t, *T_GHOST)
    rot = CP.spin_rot(t) if t >= CP.T_SPIN[0] else 0.0
    ghosts *= 1 - seg(t, CP.T_SPIN[1] + 60, CP.T_SPIN[1] + 320)
    chev = 1 - seg(t, CP.T_SPIN[0], CP.T_SPIN[0] + 200)
    PV.draw(img, chase=chase, ghosts=ghosts, rot=rot, chev_alpha=chev, labels=T_LABEL[0] <= t < T_LABEL[1])
    # the ghost meets the real blade: a white ring on the blade window + a LANDED tag
    if CP.T_SPIN[1] - 40 <= t < CP.T_SPIN[1] + 500:
        q = seg(t, CP.T_SPIN[1] - 40, CP.T_SPIN[1] + 260)
        d = ImageDraw.Draw(img)
        c = PV.pt(P.BOSS["r"] * 1.24, 0)
        r = 30 + 40 * ease_out_cubic(q)
        if q < 1:
            d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=(255, 255, 255, int(230 * (1 - q))), width=5)
        PV.label(d, (c[0] + 74, c[1] + 4), "LANDED  =  PREVIEW", "EXPLOIT 14 under needle 1", size=20)
    return img


CP.PREVIEW_HOOK = hook

KEYS = [
    (760, "01 HOVER", ["Card lifts (ease-out-back) and the", "preview starts on the target."]),
    (1160, "02 CHEVRON CHASE", ["Nine chevrons outside the rim light in turn", "from needle 1, 9 ticks anticlockwise."]),
    (1640, "03 GHOST LANDING", ["Ghost blade + dashed slice: EXPLOIT 14.", "Labels only while the card waits."]),
    (2200, "04 PEEL + AIM", ["Preview holds (chevrons ghosted) under", "the dragged card and the grease aim."]),
    (2640, "05 SLAP", ["Squash 1.13 / 0.86, shadow snaps; the", "preview stays as the promise."]),
    (3000, "06 DISSOLVE A", ["Bit stream (round 19: 17 px cells, one", "trail copy, dark rim: readable 0/1)."]),
    (3720, "07 SPIN", ["Chevrons fade (200 ms); the ghost rides", "the slices towards the real blade."]),
    (4360, "08 LANDED = PREVIEW", ["Ghost meets the blade: ring + tag;", "EXPLOIT 14 under needle 1, as shown."]),
]


def main():
    frames, durs, crops = [], [], {}
    keyt = {k[0] for k in KEYS}
    CROP = (840, 120, 1740, 1080)
    for t in range(0, CP.T_END, int(FX.DT)):
        img = CP.frame(t)
        frames.append(img.convert("RGB").resize((960, 540), Image.LANCZOS))
        durs.append(int(FX.DT))
        if t in keyt:
            crops[t] = img.convert("RGB").crop(CROP).resize((675, 720), Image.LANCZOS)
        if t % 800 == 0:
            print("t", t, flush=True)
    durs[-1] = 900
    size = FX.save_gif(frames, durs, os.path.join(OUT, "card_play_v2.gif"))
    print("gif", size // 1024, "KB", flush=True)
    cells = [(crops[t], lab, "%d ms" % t, caps) for t, lab, caps in KEYS]
    FX.storyboard(cells, os.path.join(OUT, "card_play_v2_storyboard.png"),
                  "CARD PLAY v2  -  preview (chevron chase + ghost landing) -> slap -> dissolve A -> spin lands on the ghost",
                  "Crops of the 1920x1080 D4 combat screen (no standing NEXT arrows), shown at 0.75. Times from clip start; hover at 560 ms, press at %d ms." % CP.T_PEEL[0],
                  cols=4,
                  note_lines=["preview = round 17 rule: ONE chevron set (needle 1), ghost blade + dashed slice at each landing; no trace lines. It holds while the card is hovered or aimed.",
                              "during the spin the ghost is parented to the slice disc, so it reaches the real blade exactly when the wheel lands (preview must equal the result)."])
    print("done", flush=True)


DIS = [("A", "dissolve_A_bitstream.gif", "A  BIT STREAM"), ("B", "dissolve_B_scanline.gif", "B  SCANLINE DECODE"),
       ("C", "dissolve_C_crumble.gif", "C  GLYPH CRUMBLE")]


def dissolves():
    c = CP.SLAP_C
    box = (c[0] - 260, c[1] - 260, c[0] + 260, c[1] + 260)
    t0, t1 = CP.T_SQUASH[0] - 120, CP.T_SPIN[0] + 360
    for style, name, title in DIS:
        frames, durs = [], []
        for t in range(t0, t1, int(FX.DT)):
            img = CP.frame(t, style).convert("RGB").crop(box)
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([10, 10, 30 + P.mono(22).getlength(title + "   +0000 ms"), 46], radius=6, fill=(10, 9, 15))
            d.text((20, 15), "%s   +%d ms" % (title, max(0, t - CP.T_DISSOLVE[0])), font=P.mono(22), fill=(255, 214, 64))
            frames.append(img)
            durs.append(int(FX.DT))
        durs[-1] = 700
        size = FX.save_gif(frames, durs, os.path.join(OUT, name), size=(520, 520))
        print(name, size // 1024, "KB", flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "main"
    if what == "test":
        for a in sys.argv[2:]:
            CP.frame(int(a)).convert("RGB").save(os.path.join(P.SCR, "v2_%s.png" % a))
            print("test", a, flush=True)
    elif what == "dissolves":
        dissolves()
    else:
        main()
