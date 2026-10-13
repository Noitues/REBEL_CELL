"""Round 45: how the inner-ring modifiers read on the D4 wheel.

Designer direction (rendered as given):
1. GHOST WEDGE over the outer slice under the needle (hub edge to rim), tinted per modifier family.
2. PATTERN FILL inside the wedge: the modifier's mark tiled large at ~24 % (x2 field, outward chevrons, glitch
   blocks + scan tears, status glyphs). The slice's read block is re-stamped on top.
3. ACTIVE INNER SEGMENT: raised plate, bright tint lips + end caps + glow, and a cream notch tick on the needle line.
   Other segments: dimmed texture + a thin tint notch on the outer lip (the handle). No glyph plates.
4. WORDS ON DEMAND: one plate "x2 DOUBLE" at the wedge's outer edge + a tooltip, only on hover / aim.
5. TWO MODIFIERS: the wedge splits into an inner and an outer band, each with its own pattern.

Reuses the round 41 wheel stack (host D4 render, Comp, read block, firmware socket, state overlay, drone band) and
the round 39/40 locked ring code (ringlock: lips, gunmetal band, segment textures, grooves). Only the inner ring is
re-laid out (variable segment spans) and the old texture extension is replaced by the wedge.
"""
import copy
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R41 = os.path.normpath(os.path.join(HERE, "..", "..", "round41_wheel_stack", "scripts"))
sys.path.insert(0, R41)
OUT = os.path.dirname(HERE)
SCR = os.path.join(OUT, "scratch")

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import stack42 as Q          # sets the v2 drone size
import stack41 as K
import combat41 as C41
import specs14 as S
import sat2 as S2
import ringlock as RL
import slicelib as SL
from slicelib import R_OUT, R_IN, f_num, f_ui, f_mono, glyph_rgba
from frames import INK

SIZE = (2000, 2000)
PINK = (255, 61, 168)
CREAM = (242, 238, 228)
R0, R1 = RL.R0, RL.R1        # ring band 100..127 (master)

# ------------------------------------------------------------------ modifier families (all sizes in MASTER units:
# R_OUT = 360; at combat size r = 220 px one master unit = 0.611 px)
MODS = {
    "DOUBLE":      dict(family="inner", tint=(255, 210, 77), word="DOUBLE", mark="x2", kind="text", size=58,
                        row=68, arc=92, stagger=True, ring="SEG_x2", glyph="SEG_X2",
                        rule="output x2"),
    "PIERCE":      dict(family="inner", tint=(242, 246, 255), word="PIERCE", kind="chevron", size=36,
                        row=30, cols_deg=14.0, ring="SEG_pierce", glyph="SEG_PIERCE",
                        rule="ignores block + shield"),
    "CORRUPT":     dict(family="inner", tint=(60, 255, 140), tint2=(255, 61, 168), word="CORRUPT", kind="glitch",
                        size=22, ring="SEG_corrupt", glyph="SEG_CORRUPT",
                        rule="target's slice becomes CORRUPTED"),
    "OVERCLOCKED": dict(family="status", tint=(255, 122, 26), word="OVERCLOCKED", kind="glyph", size=44,
                        row=64, arc=78, stagger=True, ring="SEG_accelerator", glyph="ST_OVERCLOCKED",
                        rule="x1.5 next trigger, then CORRUPTED"),
    "ENCRYPTED":   dict(family="status", tint=(92, 225, 255), word="ENCRYPTED", kind="glyph", size=44,
                        row=64, arc=78, stagger=True, ring="ENC", glyph="ST_ENCRYPTED",
                        rule="absorbs the next status"),
    "PARASITE":    dict(family="status", tint=(200, 90, 255), word="PARASITE", kind="glyph", size=46,
                        row=66, arc=80, stagger=True, ring="SEG_double_status", glyph="ST_PARASITE",
                        rule="output x0.5"),
    "BLANK":       dict(family="none", tint=(150, 150, 165), word="-", ring="SEG_blank", glyph="SEG_BLANK"),
}
ORDER = ["DOUBLE", "PIERCE", "CORRUPT", "OVERCLOCKED", "ENCRYPTED", "PARASITE"]

# wedge + pattern spec (the NOTES table is generated from these)
WEDGE = dict(r_in=R_IN + 3, r_out=R_OUT - 7, inset=5.0, shade=0.25, wash=0.10, halo_a=0.30, edge_px=3.0, edge_a=0.90, glow_px=7, glow_a=0.45,
             pattern_a=0.24, read_clear=0.50, read_rx=96.0, read_ry=50.0, split_r=(R_IN + R_OUT) / 2)
RING = dict(dim_tex=0.42, notch_w=3.0, notch_a=0.90, raise_out=4.0, raise_in=3.0, cap_w=5.0, glow_px=7, glow_a=0.85,
            tick_base=114.0, tick_tip=146.0, tick_w=17.0)


def C(*v):
    return np.array(v, np.float32)


def tint01(kind):
    return C(*MODS[kind]["tint"]) / 255


# ------------------------------------------------------------------ inner ring with variable segment spans
def ring_texture(kind, u, vv, rho, t, i):
    m = MODS[kind]
    if m["ring"] == "ENC":  # small plus / asterisk marks along the band
        P = 10.0
        x = ((u / P) % 1.0 - 0.5) * P
        y = (vv - 0.5) * (R1 - R0)
        a = (((np.abs(x) < 1.0) & (np.abs(y) < 4.0)) | ((np.abs(y) < 1.0) & (np.abs(x) < 4.0))).astype(np.float32) * 0.9
        return tint01(kind), a
    rgb, a = RL.texture(m["ring"], u, vv, rho, t, i)
    if kind not in ("CORRUPT", "BLANK"):
        rgb = tint01(kind)
    return rgb, a


def segs_rotated(segs, rot):
    return [(k, a0 + rot, a1 + rot) for (k, a0, a1) in segs]


def active_index(segs):
    """The segment under the needle (compass 0)."""
    for i, (k, a0, a1) in enumerate(segs):
        if ((0 - a0) % 360) < ((a1 - a0) % 360 or 360):
            return i
    return 0


def ring_var(c, segs, t=0.3, acc=PINK):
    """segs: [(kind, a0, a1)] clockwise compass degrees covering 360. Draws the ring into c.top; returns the active
    index. Locked look (lips, recessed gunmetal band, grooves + bolts, glass sheen) from ringlock.draw_ring."""
    act = active_index(segs)
    R = int(R_IN + 24)
    cvs = np.zeros((2 * R, 2 * R, 4), np.float32)
    g = RL.geom(cvs.shape, (R, R), 1)
    rho, th = g.rho, g.th
    accf = C(*acc) / 255
    RL.over(cvs, C(0.06, 0.055, 0.08), ((rho < R_IN) & (rho > R0 - 6)).astype(np.float32))
    light = 0.78 + 0.32 * np.cos(np.radians(th - 315))
    for (ra, rb, k) in ((R1, R1 + 5, 1.0), (R0 - 5, R0, 0.8)):
        m = (rho >= ra) & (rho <= rb)
        prof = np.sin(np.clip((rho - ra) / (rb - ra), 0, 1) * np.pi)
        RL.over(cvs, (C(0.30, 0.31, 0.36) + 0.35 * prof[..., None]) * light[..., None] * k, m.astype(np.float32))
        RL.add(cvs, accf * 0.9, np.exp(-((rho - (ra + rb) / 2) / 0.6) ** 2) * m * 0.8)
    band = (rho >= R0) & (rho <= R1)
    vv = np.clip((rho - R0) / (R1 - R0), 0, 1)
    recess = 0.55 + 0.45 * np.sin(vv * np.pi)
    RL.over(cvs, C(0.075, 0.07, 0.10) * recess[..., None] * light[..., None], band.astype(np.float32))
    px = g.xx + 0.5 - R
    py = g.yy + 0.5 - R
    for i, (kind, a0, a1) in enumerate(segs):
        mid, half = (a0 + a1) / 2, (a1 - a0) / 2
        dd = ((th - mid + 180) % 360) - 180
        inseg = band & (np.abs(dd) <= half)
        u = np.radians(dd) * rho
        rgb, a = ring_texture(kind, u, vv, rho, t, i)
        RL.over(cvs, rgb, a * inseg * (1.0 if i == act else RING["dim_tex"]))
        # the handle: a thin tint notch along the outer lip of every segment
        if kind != "BLANK":
            lat = np.abs(np.radians(dd) * rho) <= (np.radians(half) * rho - 3.0)
            notch = (rho >= R1 - RING["notch_w"]) & (rho <= R1) & lat
            RL.over(cvs, tint01(kind), notch.astype(np.float32) * RING["notch_a"])
        # groove at the segment's clockwise end, two bolts when there is room
        gdd = ((th - a1 + 180) % 360) - 180
        groove = band & (np.abs(np.radians(gdd) * rho) < 2.2)
        RL.over(cvs, C(0.02, 0.02, 0.03), groove.astype(np.float32))
        RL.add(cvs, C(0.5, 0.5, 0.55), (band & (np.abs(np.radians(gdd) * rho - 2.6) < 0.7)).astype(np.float32) * 0.35)
        if a1 - a0 >= 30:
            for rb_ in (R0 + 8, R1 - 9):
                bx, by = math.sin(math.radians(a1 - 4.5)) * rb_, -math.cos(math.radians(a1 - 4.5)) * rb_
                bd = np.hypot(px - bx, py - by)
                RL.over(cvs, C(0.55, 0.56, 0.6) * light[..., None], (bd < 2.4).astype(np.float32))
                RL.over(cvs, C(0.1, 0.1, 0.12), (bd < 0.9).astype(np.float32))
    # ---- the active segment: a raised plate (the band widened 3 in / 4 out), full texture, tint lips + end caps
    kind, a0, a1 = segs[act]
    mid, half = (a0 + a1) / 2, (a1 - a0) / 2
    dd = ((th - mid + 180) % 360) - 180
    ra, rb = R0 - RING["raise_in"], R1 + RING["raise_out"]
    plate = (rho >= ra) & (rho <= rb) & (np.abs(dd) <= half)
    tf = tint01(kind)
    vv2 = np.clip((rho - ra) / (rb - ra), 0, 1)
    RL.over(cvs, (C(0.13, 0.125, 0.16) + 0.05 * np.sin(vv2 * np.pi)[..., None]) * light[..., None] * 1.15, plate.astype(np.float32))
    rgb, a = ring_texture(kind, np.radians(dd) * rho, vv2, rho, t, act)
    RL.over(cvs, rgb, a * plate * 1.0)
    if kind == "BLANK":
        tf = C(*CREAM) / 255 * 0.8
    lipe = plate * (np.exp(-((rho - rb + 1.0) / 1.1) ** 2) + np.exp(-((rho - ra - 1.0) / 1.1) ** 2))
    RL.over(cvs, tf, np.clip(lipe, 0, 1) * 0.95)
    for edge in (-half, half):
        e = np.abs(np.radians(dd - edge) * rho) < RING["cap_w"] / 2
        RL.over(cvs, tf, (e & (rho >= ra - 2) & (rho <= rb + 2)).astype(np.float32))
    sheen = band * np.exp(-((((th - 315 + 180) % 360) - 180) / 35) ** 2) * 0.10
    RL.add(cvs, C(1, 1, 1), sheen)
    img = Image.fromarray((np.clip(cvs, 0, 1) * 255).astype(np.uint8), "RGBA")
    # glow around the raised plate (tint), under the plate's own pixels
    pm = Image.fromarray((plate * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
    glow = Image.new("RGBA", img.size, tuple(int(v * 255) for v in tf) + (0,))
    glow.putalpha(pm.filter(ImageFilter.GaussianBlur(RING["glow_px"])).point(lambda v: int(v * RING["glow_a"])))
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(img)
    c.top.alpha_composite(out, (int(c.C[0] - R), int(c.C[1] - R)))
    return act


def notch_tick(c, kind):
    """Cream tick on the needle line, rooted on the active plate's outer lip, tip into the slice's hub edge."""
    d = ImageDraw.Draw(c.top)
    b0, tip, w = RING["tick_base"], RING["tick_tip"], RING["tick_w"]
    pts = [c.PP(b0, -math.degrees(w / 2 / b0)), c.PP(tip, 0), c.PP(b0, math.degrees(w / 2 / b0))]
    d.polygon(pts, fill=CREAM + (255,), outline=INK + (255,))
    d.line([pts[0], pts[1], pts[2]], fill=INK + (255,), width=2)
    x, y = c.PP(b0 + 5, 0)
    col = MODS[kind]["tint"] if kind != "BLANK" else (120, 120, 130)
    d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=col + (255,))


# ------------------------------------------------------------------ the ghost wedge + pattern fill
def _half(r):
    return 30.0 - math.degrees(WEDGE["inset"] / r)


def band_poly(c, a_mid, r0, r1, n=48):
    outer = [c.PP(r1, a_mid - _half(r1) + 2 * _half(r1) * j / n) for j in range(n + 1)]
    inner = [c.PP(r0, a_mid + _half(r0) - 2 * _half(r0) * j / n) for j in range(n + 1)]
    return outer + inner


def _stamp(kind, size, tint):
    m = MODS[kind]
    if m["kind"] == "text":
        f = f_num(int(size))
        bb = f.getbbox(u"×2")
        im = Image.new("RGBA", (bb[2] - bb[0] + 6, bb[3] - bb[1] + 6), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((3 - bb[0], 3 - bb[1]), u"×2", font=f, fill=tint + (255,))
        return im
    if m["kind"] == "chevron":
        w, h, th_ = size, size * 0.55, size * 0.24
        im = Image.new("RGBA", (int(w + 4), int(h + th_ + 4)), (0, 0, 0, 0))
        ImageDraw.Draw(im).polygon([(2, 2 + h), (2 + w / 2, 2), (2 + w, 2 + h), (2 + w, 2 + h + th_ * 0.2),
                                    (2 + w / 2, 2 + th_ * 1.05), (2, 2 + h + th_ * 0.2)], fill=tint + (255,))
        return im
    gm = SL.glyph_mask(m["glyph"]).resize((int(size), int(size)), Image.LANCZOS)
    im = Image.new("RGBA", gm.size, tint + (0,))
    im.putalpha(gm)
    return im


def pattern(c, kind, a_mid, r0, r1, t=0.3, seed=3):
    """Full-alpha marks (tint) of one modifier, laid out in the slice's own polar frame (rotates with the slice)."""
    m = MODS[kind]
    L = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    tint = m["tint"]
    if m["kind"] in ("text", "glyph"):
        st = _stamp(kind, m["size"], tint)
        j, r = 0, r0 + m["row"] * 0.55
        while r < r1 + m["row"] * 0.3:
            off = 0.5 if (m["stagger"] and j % 2) else 0.0
            umax = math.radians(32) * r
            n = int(umax / m["arc"]) + 2
            for k in range(-n, n + 1):
                ang = a_mid + math.degrees((k + off) * m["arc"] / r)
                im = st.rotate(-ang, resample=Image.BICUBIC, expand=True)
                x, y = c.PP(r, ang)
                L.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
            r += m["row"]
            j += 1
    elif m["kind"] == "chevron":
        st = _stamp(kind, m["size"], tint)
        ph = (t * 2.0) % 1.0          # streams outward: 2 rows per loop second
        for k in range(-2, 3):
            ang = a_mid + k * m["cols_deg"]
            r = r0 + m["row"] * (ph - 0.5)
            while r < r1 + m["row"]:
                im = st.rotate(-ang, resample=Image.BICUBIC, expand=True)
                x, y = c.PP(r, ang)
                L.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
                r += m["row"]
    else:  # glitch: dead blocks (green, some pink) in polar cells + 3 scan tears with a ghost split
        rng = np.random.RandomState(seed)
        d = ImageDraw.Draw(L)
        q = m["size"]
        r = r0 + 2
        while r < r1:
            arc = math.radians(64) * r
            u = -arc / 2
            while u < arc / 2:
                w = q * rng.choice([1, 1, 2, 3])
                h = rng.random_sample()
                if h > 0.55:
                    col = m["tint2"] if h > 0.88 else tint
                    a0, a1 = a_mid + math.degrees(u / r), a_mid + math.degrees((u + w - 2) / r)
                    poly = [c.PP(r, a0), c.PP(r, a1), c.PP(r + q - 2, a1), c.PP(r + q - 2, a0)]
                    d.polygon(poly, fill=col + (255,))
                u += w
            r += q
        for k in range(3):
            rt = r0 + (r1 - r0) * (0.18 + 0.3 * k + 0.08 * rng.random_sample())
            s0 = -34 + 20 * rng.random_sample()
            s1 = s0 + 30 + 30 * rng.random_sample()
            sh = (3 + 3 * rng.random_sample()) * (1 if k % 2 else -1)
            for col, dr, wd in ((m["tint2"], 0, 5), (tint, sh, 3)):
                pts = [c.PP(rt + dr, a_mid + s0 + (s1 - s0) * j / 30) for j in range(31)]
                d.line(pts, fill=col + (255,), width=wd)
    return L


def _mask(c, poly):
    mk = Image.new("L", (c.W, c.H), 0)
    ImageDraw.Draw(mk).polygon(poly, fill=255)
    return mk


def read_clear_mask(c, a_mid):
    """1 - read_clear inside the read block's ellipse (soft), 1 elsewhere."""
    rc = R_IN + 0.6 * (R_OUT - R_IN)
    x, y = c.PP(rc, a_mid)
    m = Image.new("L", (c.W, c.H), 255)
    rx, ry = WEDGE["read_rx"], WEDGE["read_ry"]
    e = Image.new("L", (int(2 * rx + 40), int(2 * ry + 40)), 0)
    ImageDraw.Draw(e).ellipse([20, 20, 20 + 2 * rx, 20 + 2 * ry], fill=int(255 * WEDGE["read_clear"]))
    e = e.filter(ImageFilter.GaussianBlur(10)).rotate(-a_mid, expand=True)
    inv = Image.new("L", m.size, 0)
    inv.paste(e, (int(x - e.width / 2), int(y - e.height / 2)))
    return Image.fromarray((255 - np.asarray(inv, np.int32)).clip(0, 255).astype(np.uint8))


def wedge(c, a_mid, mods, t=0.3, seed=3):
    """Ghost wedge on the slice centred at a_mid. mods: 1 or 2 names (2 -> inner band = mods[0], outer = mods[1])."""
    r_in, r_out = WEDGE["r_in"], WEDGE["r_out"]
    bands = [(mods[0], r_in, r_out)] if len(mods) == 1 else [(mods[0], r_in, WEDGE["split_r"] - 2), (mods[1], WEDGE["split_r"] + 2, r_out)]
    clear = np.asarray(read_clear_mask(c, a_mid), np.float32) / 255
    out = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    for kind, r0, r1 in bands:
        mk = _mask(c, band_poly(c, a_mid, r0, r1))
        tint = MODS[kind]["tint"]
        dark = Image.new("RGBA", (c.W, c.H), (6, 5, 10, 0))
        dark.putalpha(mk.point(lambda v: int(v * WEDGE["shade"])))
        out.alpha_composite(dark)
        wash = Image.new("RGBA", (c.W, c.H), tint + (0,))
        wash.putalpha(mk.point(lambda v: int(v * WEDGE["wash"])))
        out.alpha_composite(wash)
        P = pattern(c, kind, a_mid, r0, r1, t, seed)
        m01 = np.asarray(mk, np.float32) / 255 * clear
        halo = P.split()[3].filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(3))
        ha = np.asarray(halo, np.float32) / 255 * m01 * WEDGE["halo_a"]
        H_ = Image.new("RGBA", (c.W, c.H), (6, 5, 10, 0))
        H_.putalpha(Image.fromarray((ha * 255).astype(np.uint8)))
        out.alpha_composite(H_)
        pa = np.asarray(P.split()[3], np.float32) / 255 * m01 * WEDGE["pattern_a"]
        P.putalpha(Image.fromarray((pa * 255).astype(np.uint8)))
        out.alpha_composite(P)
    # edges: the full wedge outline in the (inner) tint; a split line when banded
    gl = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    ed = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    for kind, r0, r1 in bands:
        tint = MODS[kind]["tint"]
        poly = band_poly(c, a_mid, r0, r1)
        ImageDraw.Draw(gl).line(poly + poly[:1], fill=tint + (int(255 * WEDGE["glow_a"]),), width=12, joint="curve")
        ImageDraw.Draw(ed).line(poly + poly[:1], fill=tint + (int(255 * WEDGE["edge_a"]),), width=int(WEDGE["edge_px"]), joint="curve")
    out.alpha_composite(gl.filter(ImageFilter.GaussianBlur(WEDGE["glow_px"])))
    out.alpha_composite(ed)
    c.top.alpha_composite(out)


# ------------------------------------------------------------------ the wheel (round 41 typical stack, new ring)
def make_spec(top_prog=None):
    spec = copy.deepcopy(S.player())
    if top_prog:
        spec["slots"][1]["program"], spec["slots"][1]["value"] = top_prog
    return spec


def wheel(segs, wedge_mods, rot=-60.0, t=0.3, spec=None, typical=True, seed=3):
    """Player BREAKER wheel at MASTER scale with the round 41 typical layers, the round 45 ring and wedge.
    rot -60 puts slot 1 (SHIM 6) under the needle. Returns (RGBA master image, centre, info)."""
    spec = copy.deepcopy(spec or make_spec())
    spec["slot_tier"] = {0: 2, 3: 1}
    spec["variant"] = "v2t"
    h = S2.host_image(spec, rot, hp_number=False)
    c = S2.Comp(h, SIZE)
    act = ring_var(c, segs, t)
    if wedge_mods:
        wedge(c, 0.0, wedge_mods, t, seed)
    needle = int(round(((-rot) % 360) / 60.0)) % 6
    for i in range(6):
        if typical and i == 1:
            K.firmware_socket(c, i, rot)
        if typical and i == 3:
            C41.state_overlay(c, i, rot, i, 1)
    for i in range(6):
        C41.read_block(c, spec, i, rot)
    notch_tick(c, segs[act][0])
    if typical:
        Q.drones_band(c, S2.BOTNET_DRONE, 60 * 1 + rot, 1)
    return c.image(), c.C, dict(active=act, needle=needle, spec=spec)


def scaled(img, cc, r_px):
    k = r_px / R_OUT
    return img.resize((int(img.width * k), int(img.height * k)), Image.LANCZOS), (cc[0] * k, cc[1] * k), k


# ------------------------------------------------------------------ hover words (screen space)
def plate(img, cx, cy, k, mods, a_mid=0.0):
    """One plate at the wedge's outer edge, clockwise of the blade: glyph + word per modifier."""
    d = ImageDraw.Draw(img)
    s = k / (220 / R_OUT)               # 1.0 at combat size, 2.0 at the 2x close-up
    f = f_num(int(22 * s))
    parts = []
    for kind in mods:
        m = MODS[kind]
        if m["kind"] == "text":
            g = None
        else:
            g = glyph_rgba(m["glyph"], int(22 * s), max(1.5, 1.6 * s), fill=m["tint"])
        parts.append((kind, g, (u"×2 " if m["kind"] == "text" else "") + m["word"]))
    pad, gap = int(8 * s), int(5 * s)
    wsum = 0
    for kind, g, txt in parts:
        wsum += (g.width + gap if g else 0) + f.getlength(txt)
    wsum += (len(parts) - 1) * int(18 * s) + 2 * pad
    hh = int(32 * s)
    ang = math.radians(a_mid + 9.0)
    rr = (R_OUT - 14) * k
    x0 = cx + rr * math.sin(ang)
    yc = cy - rr * math.cos(ang)
    if x0 + wsum > img.width - 8:      # no room clockwise: mirror to the counter-clockwise side of the blade
        x0 = cx - rr * math.sin(ang) - wsum
    box = [x0, yc - hh / 2, x0 + wsum, yc + hh / 2]
    acc = MODS[mods[0]]["tint"]
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([box[0] + 3 * s, box[1] + 4 * s, box[2] + 3 * s, box[3] + 4 * s], radius=int(6 * s), fill=(0, 0, 0, 150))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4 * s)))
    d.rounded_rectangle(box, radius=int(6 * s), fill=(12, 10, 18, 242), outline=acc + (255,), width=max(2, int(2 * s)))
    # leader tick into the wedge rim
    lx, ly = cx + (R_OUT - 40) * k * math.sin(ang), cy - (R_OUT - 40) * k * math.cos(ang)
    if box[2] < cx:
        lx = cx - (lx - cx)
    d.line([((box[0] + 10 * s) if box[0] > cx else (box[2] - 10 * s), box[3]), (lx, ly)], fill=acc + (255,), width=max(2, int(2 * s)))
    x = box[0] + pad
    for j, (kind, g, txt) in enumerate(parts):
        col = MODS[kind]["tint"]
        if j:
            d.text((x - int(13 * s), yc), "+", font=f, fill=(200, 200, 210), anchor="lm")
        if g:
            img.alpha_composite(g, (int(x), int(yc - g.height / 2)))
            x += g.width + gap
        d.text((x, yc + 1 * s), txt, font=f, fill=col + (255,), anchor="lm")
        x += f.getlength(txt) + int(18 * s)
    return box


def tooltip(img, x0, y0, title, lines, acc, s=1.0):
    d = ImageDraw.Draw(img)
    f1, f2 = f_ui(int(17 * s), b"Bold SemiCondensed"), f_mono(int(15 * s), False)
    w = max([f2.getlength(l if isinstance(l, str) else l[0]) for l in lines] + [f1.getlength(title)]) + 28 * s
    h = 34 * s + 22 * s * len(lines) + 8 * s
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=int(8 * s), fill=(10, 9, 16, 245), outline=acc + (255,), width=max(2, int(2 * s)))
    d.text((x0 + 14 * s, y0 + 8 * s), title, font=f1, fill=acc + (255,))
    for j, ln in enumerate(lines):
        txt, col = (ln, (220, 220, 230)) if isinstance(ln, str) else ln
        d.text((x0 + 14 * s, y0 + 34 * s + j * 22 * s), txt, font=f2, fill=col + (255,))
    return (x0, y0, x0 + w, y0 + h)


def cursor(img, x, y, s=1.0):
    d = ImageDraw.Draw(img)
    p = [(0, 0), (16, 30), (6, 27), (1, 40), (-4, 38), (1, 25), (-9, 24)]
    d.polygon([(x + a * s, y + b * s) for a, b in p], fill=(255, 255, 255, 255), outline=INK + (255,))


def label(img, x, y, txt, col=(255, 214, 64), px=24, bg=(10, 9, 16, 230)):
    d = ImageDraw.Draw(img)
    f = f_num(px)
    tw = f.getlength(txt)
    d.rounded_rectangle([x, y, x + tw + 20, y + px + 10], radius=6, fill=bg, outline=col, width=2)
    d.text((x + 10, y + 3), txt, font=f, fill=col)
    return x + tw + 20


def small(img, x, y, txt, col=(200, 205, 220), px=16):
    ImageDraw.Draw(img).text((x, y), txt, font=f_ui(px, b"SemiBold"), fill=col)
