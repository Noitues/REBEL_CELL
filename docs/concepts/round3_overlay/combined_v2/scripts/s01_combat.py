"""01_combat.png: crew ID + note card (object stickers), target on slice 6 + HIT IT (grease pencil),
SEND IT (holo verb sticker) slapped at an angle over the washed EXECUTE button."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from kit import *  # noqa
import render_all as RA   # A: washed EXECUTE button

# EXECUTE text sits at y 893 on a slab 852..958: the sticker covers the lower half of the slab
# (SPIN BOTH WHEELS) and leaves the machine word readable above it.
SEND_POS = (1752, 968, 5.0)


def combat_base():
    base = pil2f(Image.open(BASE_COMBAT))
    # old overlay mark: the tan tape strip by ROUND 3 -> removed (D's inpaint)
    yy, xx = np.mgrid[0:H, 0:W]
    lum = base.mean(-1)
    tape = ((xx > 805) & (xx < 895) & (yy > 10) & (yy < 50) & (lum > 0.45)).astype(np.float32)
    base = LP.inpaint(base, LP.dilate(tape, 2.0), 300)
    # D: light spill from the spinner rims and the VS crystal (tuned: 1.4 -> 1.15)
    base = light_spill(base, [ring_mask(560, 410, 205, 250), ring_mask(1360, 410, 205, 250),
                              box_mask(905, 345, 1015, 470)], gain=1.15)
    return RA.washed_execute(base)


def pencil_strokes():
    rng = np.random.default_rng(5101)
    st = [(T.hand_circle(1444, 504, 50, 46, rng, turns=1.15), 7.5, PAL_F["red"])]
    st += T.letter_strokes("HIT IT", 1676, 438, 44, 10.5, PAL_F["red"], rng, angle=-0.06)
    st += T.arrow_strokes(T.bezier((1600, 462), (1530, 470), (1500, 494)), 7.5, PAL_F["red"], rng, head=22)
    return st


def pencil_layer(rng, progress=1.0, glint=None, wipe=None):
    """Grease pencil: crisp printed reticle on slice 6, red wax circle, HIT IT + arrow.

    progress draws the strokes in writing order; wipe (0..1) is A's palm smear."""
    L = T.Layer(rng)
    T.print_reticle(L, 1444, 502, 74, (247, 33, 31, 200 if progress >= 1 else int(200 * progress)))
    L.flush_print()
    for pts, wd, col in T.cut_strokes(pencil_strokes(), progress):
        L.wax_stroke(pts, wd, col)
    L.light(glint=glint, glint_gain=1.4)
    if wipe is not None:
        RA.apply_wipe(L, wipe, np.random.default_rng(7))
    return L


SMUDGES = [(330, 980, 70, 52, 0.4, "print"), (1060, 140, 62, 48, -0.6, "print"), (920, 690, 320, 74, -0.25, "wipe")]


def stickers():
    crew = PC.crew_card(curl=dict(corner="br", amount=0.09))
    note = note_card("SLICE 6 CRACKED\nBACKDOOR FIRST\nTHEN BRUTE IT", curl=dict(corner="tr", amount=0.12))
    return crew, note


CREW_POS = (172, 300, 4)
NOTE_POS = (1752, 600, -3)


def send_it(phase=0.0, gloss_pos=0.32, curl="default"):
    if curl == "default":
        curl = dict(corner="tr", amount=0.09)
    return verb_sticker("SEND IT", 74, holo=True, seed=7, curl=curl, holo_phase=phase, gloss_pos=gloss_pos)


def build(save=True):
    rng = np.random.default_rng(101)
    img = combat_base()
    img = pencil_composite(img, pencil_layer(rng))
    img = glass(img, np.random.default_rng(11), SMUDGES, band_pos=0.30)
    pre_stickers = img.copy()
    crew, note = stickers()
    img = place_sticker(img, crew, CREW_POS[0], CREW_POS[1], angle=CREW_POS[2])
    img = place_sticker(img, note, NOTE_POS[0], NOTE_POS[1], angle=NOTE_POS[2])
    img = place_sticker(img, send_it(), SEND_POS[0], SEND_POS[1], angle=SEND_POS[2])
    if save:
        f2pil(img).save(os.path.join(OUT, "01_combat.png"))
        print("saved 01_combat.png")
    return img, pre_stickers


if __name__ == "__main__":
    build()
