"""Storyboard v2: the city-alive tables (the r3 idle loop's, post_loop.py, same seeds), shared by the Blender renders
(sign flicker on moving shots through the signs' `pwo`) and the 2D composite (every flicker layer on held shots).
Designer rule: city-alive activity never pauses, in any beat. Everything is periodic in 96 frames (4 s at 24 fps) and
indexed by the video frame (f % 96), so every shot is in phase with every other.
"""
import numpy as np

NF = 96
RNG = np.random.default_rng(9700)
BUZZ = 0.86 + 0.14 * RNG.random(NF)
BUZZ[[30, 31]] = (0.22, 0.55)
BUZZ[71] = 0.35
FLICK = np.ones(NF)
FLICK[52:59] = (0.2, 1.0, 0.08, 0.9, 0.3, 1.0, 0.95)
BROKEN = 0.9 + 0.1 * RNG.random(NF)
BROKEN[10:23] = (0.1, 1.0, 0.0, 0.0, 1.0, 0.15, 0.0, 0.0, 0.0, 0.0, 0.7, 0.0, 1.0)
BROKEN[64:71] = (0.0, 1.0, 0.0, 0.6, 0.0, 0.0, 1.0)
WIN = {"win_0": [(24, 70)], "win_1": [(60, 96), (0, 6)], "win_2": [(40, 52)]}
STROBE_PH = {"strobe_0": 0, "strobe_1": 9, "strobe_2": 17}
BILL_A = set(range(0, 46))
BILL_B = set(range(48, 94))
BILL_GLITCH = {46, 47, 94, 95}
HOLO_ROLL = {"holo_solace": 1, "holo_orbital": 2, "holo_halcyon": 1}
HOLO_GLITCH = {"holo_solace": (37, 38), "holo_orbital": (77,), "holo_halcyon": (15, 16)}


def gain(g, f):
    f = f % NF
    if g == "sign_buzz":
        return float(BUZZ[f])
    if g == "sign_flicker":
        return float(FLICK[f])
    if g == "sign_broken":
        return float(BROKEN[f])
    if g in WIN:
        return 0.0 if any(a <= f < b for a, b in WIN[g]) else 1.0
    if g in STROBE_PH:
        ph = (f - STROBE_PH[g]) % 24
        return 2.2 if ph < 2 else 0.12
    if g == "bill_a":
        return 1.0 if f in BILL_A else 0.0
    if g == "bill_b":
        return 1.0 if f in BILL_B else 0.0
    return 1.0
