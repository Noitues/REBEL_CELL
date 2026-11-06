"""R2 outer_rings GROUND: backdrop_grade, board_scrim, board_backplate (+ tower back plate and the 160-165 gap), bezel_ring, bezel_rim_lines, bezel_spokes, sched_track.
Selectors: 'P' = R2 pick, 'V' = the one allowed variant.  Numpy, 1920x1080, board centre C."""
import sys, os, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from e10lib import C, RS, W, H, ROOT
import o_ground as G
from o_ground import aa, rgba, smooth, blur, bare, RHO, TH, XX, YY, INKC, SCRIM_C, ring_alpha, BEZEL_MID, BEZEL_HI, BEZEL_LO, FOCUS

BZ0, BZ1 = RS['bz0'], RS['bz1']
GRADE_CITY_DIM = 0.85            # token: the one grade pass
SCRIM_BLUR = 6                   # token SCRIM: 6 px blur + 55 percent
SCRIM_ALPHA = 0.55
TOWER_R = 190
GAP_R1 = 196
RING_FLOOR = (9, 12, 21)
TOWER_FLOOR = (8, 14, 26)
ENAMEL = (50, 90, 86)            # BEZEL value, below the L2 cells (measured in notes)


# ----------------------------------------------------------------------------- backdrop_grade
def focus_mask(feather):
    d = np.hypot((XX - 1500) / 330.0, (YY - 600) / 270.0)
    return 1 - smooth(feather[0], feather[1], d)


HULL_LIFT_F = 0.50 / 0.84        # fix 1: baked hull x0.84 -> about x0.57-0.60 (0.57 measured: room p95 <= 0.40 on all three rooms)
NEON_SAT_K = 0.33 / 0.55          # fix 1: baked green / neon saturation 0.55 -> about 0.33-0.35


def room_relight(a, m):
    """fix 1: inside the focus hull (weight m) value to x0.60 of source, green + neon saturation 0.55 -> 0.35"""
    mx = a.max(-1); mn = a.min(-1)
    S = (mx - mn) / np.maximum(mx, 1.0)
    V = mx / 255.0
    neon = smooth(0.35, 0.60, S) * smooth(0.35, 0.65, V)
    gr = ((a[..., 1] > a[..., 0] * 1.12) & (a[..., 1] > a[..., 2] * 1.05)).astype(np.float32) * smooth(0.25, 0.5, S)
    w = np.maximum(neon, gr)[..., None]
    lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])[..., None]
    k = 1 - (1 - NEON_SAT_K) * w * m
    return (lum + (a - lum) * k) * (1 - (1 - HULL_LIFT_F) * m)


def grade(opt):
    """P: room focus hull sharp (value lowered by fix 1); city outside the hull 2 px blur and x0.85.  V: same, hull feather 0.95-1.7 (wider ramp)."""
    a = bare()
    fe = (0.85, 1.55) if opt == 'P' else (0.95, 1.75)
    m = focus_mask(fe)[..., None]
    soft = blur(a, 2.0) * GRADE_CITY_DIM
    return room_relight(a, m) * m + soft * (1 - m)


# ----------------------------------------------------------------------------- board_scrim
def scrim_weight(opt):
    d = RHO
    m = SCRIM_ALPHA * (1 - smooth(330, 560, d)) if opt == 'P' else SCRIM_ALPHA * (1 - smooth(300, 520, d))
    w = (1 - smooth(300, 520, d)) if opt == 'P' else (1 - smooth(280, 480, d))
    return m, w


def scrim(a, opt):
    m, w = scrim_weight(opt)
    fr = blur(a, SCRIM_BLUR)
    a2 = a * (1 - w[..., None]) + fr * w[..., None]
    return a2 * (1 - m[..., None]) + SCRIM_C * m[..., None]


def backdrop(grade_opt='P', scrim_opt='P'):
    a = scrim(grade(grade_opt), scrim_opt)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


# ----------------------------------------------------------------------------- board_backplate (+ tower plate + gap)
def plate(opt):
    """ground under the board: ring floor to the bezel, tower back plate to r160, 5 px ink gutter 160-165, landing annulus 394-516 with a gutter at the bezel."""
    R0, R1 = 424, 488
    inner = aa(BZ0 - RHO)
    ann = ring_alpha(R0, R1)
    col = np.zeros((H, W, 3), np.float32) + np.array([8, 10, 18], np.float32)
    col = col + (np.array([4, 7, 9], np.float32) * (1 - (RHO - R0) / (R1 - R0))[..., None]).clip(0)
    edge = (aa(1.6 - np.abs(RHO - R1)) + aa(1.6 - np.abs(RHO - R0))).clip(0, 1)
    col = col * (1 - edge[..., None]) + INKC * edge[..., None]
    a = np.maximum(inner, ann * 0.93)
    # ring floor (glass, a step lighter than the cells' dark so empty cells and their gaps read)
    floor = np.zeros((H, W, 3), np.float32) + np.array(RING_FLOOR, np.float32)
    col = np.where(inner[..., None] > 0.5, floor, col)
    # tower back plate: cool near-black disc with a soft lift at the hub; opt V adds the cutaway's 45 degree cut-edge hatch at 5 percent
    tw = aa(TOWER_R - RHO)
    lift = np.exp(-(RHO / 120.0) ** 2)
    tcol = np.zeros((H, W, 3), np.float32) + np.array(TOWER_FLOOR, np.float32) + lift[..., None] * np.array([6, 10, 14], np.float32)
    if opt == 'V':
        hat = (((XX + YY) % 8.0) < 1.2).astype(np.float32)
        tcol = tcol + hat[..., None] * np.array([6, 10, 12], np.float32) * (1 - smooth(60, 160, RHO))[..., None]
    col = col * (1 - tw[..., None]) + tcol * tw[..., None]
    # gutter 160-165: INK, with a cool hairline on the plate side (the plate is a mounted part, the rings run around it)
    gut = aa(RHO - (TOWER_R - 1.0)) * aa(GAP_R1 - RHO)
    col = col * (1 - gut[..., None]) + INKC * gut[..., None]
    hl = aa(0.7 - np.abs(RHO - (TOWER_R - 2.6))) * (0.25 + 0.5 * np.clip(-np.cos(np.radians(TH - 315)), 0, 1) * 0 + 0.5 * np.clip(np.cos(np.radians(TH - 315)), 0, 1))
    col = col * (1 - hl[..., None] * 0.55) + np.array([90, 130, 150], np.float32) * (hl[..., None] * 0.55)
    return rgba(col, np.maximum(a, tw))


# ----------------------------------------------------------------------------- bezel (enamel, track, spokes, rim hairline)
def _light(th):
    return np.cos(np.radians(th - 315))


def bezel_material(scale=1.0):
    u = np.clip((RHO - BZ0) / (BZ1 - BZ0), 0, 1)
    rng = np.random.default_rng(7)
    grain = rng.random(1200).astype(np.float32)[(RHO * 8).astype(np.int32) % 1200] * 0.06
    base = np.array(ENAMEL, np.float32) * scale
    k = 0.86 + 0.14 * np.sin(np.pi * u) + 0.10 * _light(TH) + grain
    # enamel gloss: a soft specular lobe on the top-left quadrant, centred on the outer third of the ring
    gl = np.clip(_light(TH), 0, 1) ** 3 * np.exp(-((u - 0.78) / 0.16) ** 2) * 0.16
    return base[None, None] * (k + gl)[..., None]


def spoke_mask(r0, r1, half_w=4.0):
    m = np.zeros((H, W), np.float32)
    for k in range(6):
        dth = np.radians(((TH - (30 + 60 * k) + 180) % 360) - 180)
        perp = RHO * np.sin(dth)
        m = np.maximum(m, aa(half_w - np.abs(perp)) * (np.cos(dth) > 0) * aa(RHO - r0) * aa(r1 - RHO))
    return m


def bezel_layer(opt, rim='P'):
    """RGBA: enamel + ink edges + sched track + 8 px ink spokes at the six sector boundaries (30 + 60k) + top-left hairline.  V = without the track."""
    al = ring_alpha(BZ0 - 1.2, BZ1 + 1.2)
    col = bezel_material(1.12 if opt == 'V' else 1.0)
    if opt in ('P', 'V'):
        tr = ring_alpha(356.6, 385.2)
        col = col * (1 - tr[..., None] * 0.42)
        te = (aa(0.75 - np.abs(RHO - 356.6)) + aa(0.75 - np.abs(RHO - 385.2))).clip(0, 1)
        col = col * (1 - te[..., None] * 0.9) + INKC * (te[..., None] * 0.9)
    ink = G.bezel_ink(al)[..., None]
    col = col * (1 - ink) + INKC * ink
    sp = spoke_mask(BZ0 - 0.5, BZ1 + 0.5, 4.0)[..., None]
    col = col * (1 - sp) + INKC * sp
    # hairline: strongest top-left on the outer edge, weaker on the inner edge (R1 pick A)
    hi = np.array(BEZEL_HI, np.float32)
    lg = np.clip(_light(TH), 0, 1)
    e = aa(0.7 - np.abs(RHO - (BZ1 - 2.6))) * (0.15 + 0.85 * lg ** 1.5) * (1 - sp[..., 0])
    if rim == 'V':       # variant: a second, weaker hairline on the inner edge (lit lower-right wall) so the ring reads as a raised part from both sides
        e2 = aa(0.7 - np.abs(RHO - (BZ0 + 2.6))) * (0.10 + 0.5 * np.clip(-_light(TH), 0, 1) ** 1.5) * (1 - sp[..., 0])
        e = np.maximum(e, e2 * 0.8)
    col = col * (1 - e[..., None] * 0.85) + hi * (e[..., None] * 0.85)
    return rgba(col, al)
