"""OUTER RINGS: ground elements (backdrop_grade, board_scrim, board_backplate, bezel_ring, bezel_rim_lines).
Each element is one function family with variants 'cur' (E10 as drawn) and 'A','B','C'. Numpy, 1920x1080, board centre C."""
import sys, os, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from e10lib import C, RS, W, H, ROOT

BARE_PATH = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v2/room_bio_bare.png'
_bare = None
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
RHO = np.hypot(XX + 0.5 - C[0], YY + 0.5 - C[1])
TH = (np.degrees(np.arctan2(XX + 0.5 - C[0], -(YY + 0.5 - C[1]))) % 360).astype(np.float32)
INKC = np.array([12, 10, 22], np.float32)
SCRIM_C = np.array([2, 3, 10], np.float32)          # token SCRIM #02030A
FOCUS = (1500, 612)                                   # room frame centre


def bare():
    global _bare
    if _bare is None:
        _bare = np.asarray(Image.open(BARE_PATH).convert('RGB'), np.float32)
    return _bare


def blur(a, px):
    return np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(px)), np.float32)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# ----------------------------------------------------------------------------- backdrop_grade
def focus_mask():
    """feathered hull around the cutaway building (the lit island); 1 inside"""
    d = np.hypot((XX - 1500) / 330.0, (YY - 600) / 270.0)
    return 1 - smooth(0.85, 1.55, d)


def grade(opt):
    """returns the graded backdrop (float RGB). cur = cv_lib.backdrop: blur 2.5 then x0.80."""
    a = bare()
    if opt == 'cur':
        return blur(a, 2.5) * 0.80
    if opt == 'A':          # the room's own grade (city x0.58, focus hull x0.84) is final: E10 adds nothing
        return a.copy()
    if opt == 'B':          # one stated extra dim, no blur: GRADE_DIM = x0.90 everywhere (focus hull lands at x0.76 of source)
        return a * 0.90
    if opt == 'C':          # depth grade, once: city outside the focus hull softens 2 px and dims x0.88; the hull stays sharp and undimmed
        m = focus_mask()[..., None]
        soft = blur(a, 2.0) * 0.88
        return a * m + soft * (1 - m)
    raise KeyError(opt)


# ----------------------------------------------------------------------------- board_scrim
def pool(q, p=4):
    return np.exp(-q ** p)


def scrim(a, opt):
    d = RHO
    if opt == 'cur':      # E10: dim*(1-0.55*pool) relative to the x0.80 grade => x(1 - 0.55 pool)
        q = d / (RS['bz1'] * 1.22)
        return a * (1 - 0.55 * pool(q))[..., None]
    if opt == 'A':        # SCRIM token mixed in by a wide pool; local contrast of the city is flattened inside it (kills the window grid)
        m = 0.62 * (1 - smooth(300, 600, d))
        loc = blur(a, 16)
        flat = 0.80 * (1 - smooth(380, 560, d))
        a2 = loc + (a - loc) * (1 - flat)[..., None]
        return a2 * (1 - m)[..., None] + SCRIM_C * m[..., None]
    if opt == 'B':        # frosted pool: SCRIM token = #02030A at 55 percent + 6 px blur, with a long tail toward the room on the right
        m = 0.55 * (1 - smooth(330, 560, d))
        tail = np.clip((XX - 1000) / 160.0, 0, 1) * (1 - np.clip((XX - 1160) / 260.0, 0, 1)) * (1 - smooth(300, 700, d)) * 0.0
        fr = blur(a, 6)
        w = (1 - smooth(300, 520, d))[..., None]
        a2 = a * (1 - w) + fr * w
        m = np.clip(m + tail, 0, 1)
        return a2 * (1 - m)[..., None] + SCRIM_C * m[..., None]
    if opt == 'C':        # tight contact scrim: near-solid to the outer lane, 40 px feather, thin ink halo beyond; leaves the city and the room untouched outside
        m = 0.80 * (1 - smooth(486, 540, d)) + 0.22 * (1 - smooth(520, 640, d))
        return a * (1 - m)[..., None] + SCRIM_C * m[..., None]
    raise KeyError(opt)


def backdrop(grade_opt='cur', scrim_opt='cur'):
    a = scrim(grade(grade_opt), scrim_opt)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


# ----------------------------------------------------------------------------- helpers: AA discs / rings as alpha
def aa(x):
    return np.clip(x + 0.5, 0, 1)


def ring_alpha(r0, r1):
    return aa(RHO - r0) * aa(r1 - RHO)


def rgba(rgb, alpha):
    """float rgb (H,W,3) or tuple, alpha (H,W) -> RGBA image"""
    if isinstance(rgb, tuple) or (hasattr(rgb, 'ndim') and rgb.ndim == 1):
        rgb = np.broadcast_to(np.array(rgb, np.float32), (H, W, 3))
    out = np.dstack([np.clip(rgb, 0, 255), np.clip(alpha, 0, 1) * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


# ----------------------------------------------------------------------------- board_backplate
PLATE_R = {'cur': RS['bz0'], 'A': 516, 'B': 516, 'C': 516}


def plate(opt):
    """returns an RGBA layer: the board ground. cur is the cached E10 layer."""
    if opt == 'cur':
        return Image.open(ROOT + 'cache/cur_plate.png')
    if opt == 'A':       # one disc to the outer lane: near-black, soft radial value (a touch lighter at the hub), ink edge
        R = 516
        al = aa(R - RHO)
        v = 14 + 10 * np.exp(-(RHO / 300.0) ** 2)
        col = np.stack([v * 0.8, v * 1.05, v * 1.25], -1)
        ink = aa(RHO - (R - 3)) * aa(R + 2 - RHO)
        col = col * (1 - ink[..., None]) + INKC * ink[..., None]
        return rgba(col, al * 0.96)
    if opt == 'B':       # ring-structured ground: plate to the bezel as now, plus a separate dark landing annulus (glass) with its own ink edges and a gutter at the bezel
        R0, R1 = 394, 516
        inner = aa(RS['bz0'] - RHO)
        ann = ring_alpha(R0, R1)
        col = np.zeros((H, W, 3), np.float32) + np.array([8, 10, 18], np.float32)
        col = col + (np.array([4, 7, 9], np.float32) * (1 - (RHO - R0) / (R1 - R0))[..., None]).clip(0)
        edge = (aa(1.6 - np.abs(RHO - R1)) + aa(1.6 - np.abs(RHO - R0))).clip(0, 1)
        col = col * (1 - edge[..., None]) + INKC * edge[..., None]
        a = np.maximum(inner, ann * 0.93)
        col2 = np.where(inner[..., None] > 0.5, np.array([5, 6, 11], np.float32), col)
        return rgba(col2, a)
    if opt == 'C':       # section-slab ground: near-black with a 45 degree hatch (the cutaway's cut-edge language) at 6 percent, fading outward; hatch breaks at the lane gutters
        R = 516
        al = aa(R - RHO)
        hat = (((XX + YY) % 7.0) < 1.1).astype(np.float32)
        v = 12 + 8 * np.exp(-(RHO / 320.0) ** 2) + hat * 9 * (1 - smooth(300, 516, RHO))
        col = np.stack([v * 0.8, v * 1.1, v * 1.2], -1)
        ink = aa(RHO - (R - 3)) * aa(R + 1.5 - RHO)
        col = col * (1 - ink[..., None]) + INKC * ink[..., None]
        return rgba(col, al * 0.97)
    raise KeyError(opt)


# ----------------------------------------------------------------------------- bezel_ring (material) and bezel_rim_lines
BZ0, BZ1 = RS['bz0'], RS['bz1']
# Solace material tokens (teal enamel family of the cutaway's wainscot / floor): BEZEL_MID is the one value step the ticks and highlights key off
BEZEL_MID = (52, 92, 88)
BEZEL_HI = (110, 156, 146)
BEZEL_LO = (22, 46, 48)


def _light(th):
    return np.cos(np.radians(th - 315))


def bezel_material(opt):
    """float RGB (H,W,3) of the bezel material inside r BZ0..BZ1 (alpha handled by the caller)"""
    u = np.clip((RHO - BZ0) / (BZ1 - BZ0), 0, 1)
    rng = np.random.default_rng(7)
    if opt == 'A':       # teal enamel: smooth, circumferential micro-grain (constant along the ring, so it reads brushed round the ring, not as motion streaks)
        grain = rng.random(1200).astype(np.float32)[(RHO * 8).astype(np.int32) % 1200] * 0.06
        base = np.array(BEZEL_MID, np.float32)
        k = (0.86 + 0.14 * np.sin(np.pi * u) + 0.10 * _light(TH) + grain)
        return base[None, None] * k[..., None]
    if opt == 'B':       # section slab: dark slate-teal with the cutaway's 45 degree hatch
        base = np.array([30, 52, 54], np.float32)
        hat = (((XX + YY) % 9.0) < 1.6).astype(np.float32)
        k = 0.92 + 0.10 * _light(TH) + 0.10 * np.sin(np.pi * u)
        return base[None, None] * k[..., None] + hat[..., None] * np.array([24, 34, 34], np.float32) * 0.8
    if opt == 'C':       # pale anodised sage: lighter plate, fine concentric grain, strong ink edges, top-left bevel
        base = np.array([118, 142, 132], np.float32)
        grain = (np.sin(RHO * 5.5) * 0.025)
        k = 0.84 + 0.20 * np.sin(np.pi * u) + 0.12 * _light(TH) + grain
        return base[None, None] * k[..., None]
    raise KeyError(opt)


def bezel_ink(alpha_ring):
    """ink edges (2.4 px) at both ring edges"""
    e = aa(1.2 - np.abs(RHO - BZ0)) + aa(1.2 - np.abs(RHO - BZ1))
    return np.clip(e, 0, 1)


def bezel_layer(opt):
    """RGBA bezel. cur = E10 brushed Meridian ring WITH its orange glows (cached). A/B/C = Solace materials with plain ink edges only."""
    if opt == 'cur':
        return Image.open(ROOT + 'cache/cur_bezel.png')
    if opt == 'cur_norim':
        return Image.open(ROOT + 'cache/cur_bezel_norim.png')
    al = ring_alpha(BZ0 - 1.2, BZ1 + 1.2)
    col = bezel_material(opt)
    ink = bezel_ink(al)[..., None]
    col = col * (1 - ink) + INKC * ink
    return rgba(col, al)


def rim_layer(opt, mat='A'):
    """bezel_rim_lines: ink edges are in the ring; this adds the one hairline highlight (top-left) and any groove. cur = baked orange glows (already inside cur_bezel)."""
    if opt in ('cur', 'none'):
        return None
    hi = np.array(BEZEL_HI if mat != 'C' else (214, 232, 220), np.float32)
    lo = np.array(BEZEL_LO, np.float32)
    out = np.zeros((H, W, 4), np.float32)
    lg = np.clip(_light(TH), 0, 1)               # 1 at 315 deg (top-left)
    lgs = np.clip(-_light(TH), 0, 1)
    if opt == 'A':       # one hairline highlight just inside the outer ink edge, strongest top-left, none bottom-right
        e = aa(0.7 - np.abs(RHO - (BZ1 - 2.6)))
        a = e * (0.15 + 0.85 * lg ** 1.5)
        out[..., :3] = hi
        out[..., 3] = a
        # and the same on the inner edge, weaker
        e2 = aa(0.7 - np.abs(RHO - (BZ0 + 2.6)))
        o2 = e2 * (0.10 + 0.55 * lgs ** 1.5)
        out[..., :3] = np.where(o2[..., None] > a[..., None], lo * 0.6, hi)
        out[..., 3] = np.maximum(a, o2)
    elif opt == 'B':     # engraved groove: 1.6 px ink-dark groove 4 px inside the outer edge, with a light lip on its lower-right side only (light from top-left)
        g = aa(0.9 - np.abs(RHO - (BZ1 - 5.5)))
        lip = aa(0.6 - np.abs(RHO - (BZ1 - 7.0))) * (0.2 + 0.8 * lgs)
        out[..., :3] = lo * 0.4
        out[..., 3] = g * 0.85
        out[..., :3] = np.where(lip[..., None] > g[..., None], hi, out[..., :3])
        out[..., 3] = np.maximum(out[..., 3], lip * 0.8)
    elif opt == 'C':     # double ink: a second ink line 3 px inside each edge (reads as a pressed lip), no light at all
        e = aa(0.8 - np.abs(RHO - (BZ1 - 3.4))) + aa(0.8 - np.abs(RHO - (BZ0 + 3.4)))
        out[..., :3] = INKC
        out[..., 3] = np.clip(e, 0, 1) * 0.9
    else:
        raise KeyError(opt)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')
