"""Round 39 inner ring v2: a substantial machined ring (bezel, lips, grooves, bolts) with a full
TEXTURE per segment, and the active segment's texture EXTENDING into the outer slice it modifies.

Master geometry: hub 70, ring band 76..126, slices 130..360 (slicelib). Compass angles (0 = up, cw).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import slicelib as SL
import slicekit as K
import hubkit as H
from slicelib import R_IN, R_OUT, f_num, f_ui, f_mono

R0, R1 = 76, 126
HUB = 70
SEG_COL = {
    "SEG_x2": (255, 214, 64), "SEG_pierce": (190, 245, 255), "SEG_corrupt": (255, 40, 160), "SEG_anchor": (190, 200, 215),
    "SEG_accelerator": (255, 160, 40), "SEG_echo": (92, 225, 255), "SEG_blank": (120, 120, 135),
    "SEG_hangar": (176, 140, 255), "SEG_double_status": (200, 90, 255), "SEG_splash": (255, 120, 60),
    "SEG_broadcast": (123, 224, 123), "SEG_sub_needle": (255, 160, 40),
}


def C(*v):
    return np.array(v, np.float32)


def _h(a, b, s=0):
    x = np.sin(a * 12.9898 + b * 78.233 + s * 37.719) * 43758.5453
    return x - np.floor(x)


class G:
    pass


def geom(shape, c, ss):
    g = G()
    Hh, W = shape[:2]
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    dx, dy = xx + 0.5 - c[0], yy + 0.5 - c[1]
    g.rho = np.hypot(dx, dy) / ss  # master units
    g.th = np.degrees(np.arctan2(dx, -dy)) % 360
    g.xx, g.yy, g.ss = xx, yy, ss
    return g


def over(cv, rgb, a):
    a = np.clip(a, 0, 1)[..., None]
    cv[..., :3] = cv[..., :3] * (1 - a) + rgb * a
    cv[..., 3:] = np.maximum(cv[..., 3:], a)


def add(cv, rgb, a):
    a = np.clip(a, 0, None)[..., None]
    cv[..., :3] = cv[..., :3] + rgb * a


# ------------------------------------------------------------------ textures (local coords)
def texture(seg, u, v, rho, t, seed=0):
    """u: arc length (master) from the segment/slice midline, v: 0..1 across the band, rho: master radius.
    Returns (rgb (...,3), alpha)."""
    col = C(*SEG_COL.get(seg, (200, 200, 210))) / 255
    z = np.zeros_like(u)
    if seg == "SEG_x2":  # doubled radial hairline pairs
        P = 13.0
        f = (u / P) % 1.0
        a = (((f > 0.18) & (f < 0.30)) | ((f > 0.42) & (f < 0.54))).astype(np.float32) * 0.75
        return col, a
    if seg == "SEG_pierce":  # chevrons pointing outward, streaming out
        P = 14.0
        x = np.abs(((u / P) % 1.0) - 0.5) * P
        f = ((rho - x * 0.9) / P - t * 2) % 1.0
        return col, (f < 0.28).astype(np.float32) * 0.8
    if seg == "SEG_corrupt":  # pink / green dead blocks, re-rolled 12 x per loop
        q = 6.0
        fr = int(t * 12)
        hsh = _h(np.floor(u / q), np.floor(rho / q), fr + seed)
        a = (hsh > 0.62).astype(np.float32) * 0.85
        rgb = np.where((hsh > 0.82)[..., None], C(0.2, 1.0, 0.5), col)
        return rgb, a
    if seg == "SEG_anchor":  # chain links along the band
        P = 18.0
        f = (u / P + 0.25 * t) % 1.0
        k = np.floor(u / P + 0.25 * t) % 2
        cx = (f - 0.5) * P
        mid = (rho - np.round(rho / 1e6)) * 0 + 0  # placeholder
        rr = np.hypot(cx / 1.0, (v - 0.5) * (R1 - R0) * (1.6 if True else 1)) if False else None
        dv = (v - 0.5) * 22.0
        link = np.hypot(cx / (1.25 if True else 1), np.where(k > 0, dv * 2.2, dv * 1.3))
        a = ((link > 4.5) & (link < 8.2)).astype(np.float32) * 0.9
        return col, a
    if seg == "SEG_accelerator":  # tangential speed streaks running clockwise
        P = 30.0
        row = np.floor(rho / 5.0)
        f = ((u / P) - t * 3 + _h(row, row, 5)) % 1.0
        return col, ((f < 0.30) & ((rho % 5.0) < 2.4)).astype(np.float32) * (1 - f / 0.30) * 0.95
    if seg == "SEG_echo":  # ripples moving outward
        P = 12.0
        f = (rho / P - t * 2) % 1.0
        return col, (np.abs(f - 0.5) < 0.12).astype(np.float32) * 0.8
    if seg == "SEG_hangar":  # bay rails + dock lights
        f = (u / 22.0) % 1.0
        a = ((np.abs(v - 0.2) < 0.06) | (np.abs(v - 0.8) < 0.06)).astype(np.float32) * 0.7
        a = np.maximum(a, ((np.abs(f - 0.5) < 0.08) & (np.abs(v - 0.5) < 0.14)).astype(np.float32) * (0.5 + 0.5 * math.sin(2 * math.pi * t * 2)))
        return col, a
    if seg == "SEG_double_status":  # paired diamonds
        P = 20.0
        x = ((u / P) % 1.0 - 0.5) * P
        y = (v - 0.5) * 30
        a = (((np.abs(x + 3) + np.abs(y)) < 5) | ((np.abs(x - 4) + np.abs(y)) < 5)).astype(np.float32) * 0.85
        return col, a
    if seg == "SEG_splash":  # sideways bursts from the centre
        f = (np.abs(u) / 14.0 - t * 2) % 1.0
        return col, (f < 0.25).astype(np.float32) * 0.8
    if seg == "SEG_broadcast":  # concentric waves from the hub
        f = (rho / 9.0 - t * 2) % 1.0
        return col, ((f < 0.2) & ((u / 8.0) % 1.0 < 0.7)).astype(np.float32) * 0.7
    # blank / default: brushed steel
    n = _h(np.floor(u * 1.5), np.floor(rho * 0.2), 3)
    return C(0.62, 0.64, 0.7), (0.06 + 0.06 * n)


# ------------------------------------------------------------------ the ring
def draw_ring(cv, g, ss, acc, segs, active=0, t=0.3, tex=True, lod=False, rot=0.0):
    """segs[0] is centred under the pointer (compass 0); rot turns the ring (deg)."""
    accf = C(*acc) / 255
    rho, th = g.rho, g.th
    band = (rho >= R0) & (rho <= R1)
    light = 0.78 + 0.32 * np.cos(np.radians(th - 315))
    # outer + inner machined lips
    for (ra, rb, k) in ((R1, R1 + 5, 1.0), (R0 - 5, R0, 0.8)):
        m = (rho >= ra) & (rho <= rb)
        prof = np.sin(np.clip((rho - ra) / (rb - ra), 0, 1) * np.pi)
        over(cv, (C(0.30, 0.31, 0.36) + 0.35 * prof[..., None]) * light[..., None] * k, m.astype(np.float32))
        hair = np.exp(-((rho - (ra + rb) / 2) / 0.6) ** 2) * m
        add(cv, accf * 0.9, hair * 0.8)
    # band base: dark gunmetal with a recessed shading toward both edges
    vv = np.clip((rho - R0) / (R1 - R0), 0, 1)
    recess = 0.55 + 0.45 * np.sin(vv * np.pi)
    over(cv, C(0.075, 0.07, 0.10) * recess[..., None] * light[..., None], band.astype(np.float32))
    for i, seg in enumerate(segs):
        cen = (i * 120 + rot) % 360
        dd = ((th - cen + 180) % 360) - 180
        inseg = band & (np.abs(dd) <= 58)
        u = np.radians(dd) * rho
        if tex:
            rgb, a = texture(seg, u, vv, rho, t, i)
            lit = i == active
            a = a * inseg * (1.0 if lit else 0.55)
            if lod:
                a = inseg * (0.55 if lit else 0.2)
                rgb = C(*SEG_COL.get(seg, (200, 200, 210))) / 255
            over(cv, rgb, a)
        if i == active:  # lit edge + inner glow
            e = inseg * (np.exp(-((rho - R1 + 1.2) / 1.2) ** 2) + np.exp(-((rho - R0 - 1.2) / 1.2) ** 2))
            add(cv, accf, e * 0.9)
        # grooves between segments, with two bolts each
        gdd = ((th - (cen + 60) + 180) % 360) - 180
        groove = band & (np.abs(np.radians(gdd) * rho) < 2.2)
        over(cv, C(0.02, 0.02, 0.03), groove.astype(np.float32))
        add(cv, C(0.5, 0.5, 0.55), (band & (np.abs(np.radians(gdd) * rho - 2.6) < 0.7)).astype(np.float32) * 0.35)
        for rb_ in (R0 + 8, R1 - 8):
            bx = math.sin(math.radians(cen + 60 + 4.5)) * rb_
            by = -math.cos(math.radians(cen + 60 + 4.5)) * rb_
            px = (g.xx + 0.5 - (cv.shape[1] / 2)) / ss
            py = (g.yy + 0.5 - (cv.shape[0] / 2)) / ss
            bd = np.hypot(px - bx, py - by)
            over(cv, C(0.55, 0.56, 0.6) * light[..., None], (bd < 2.6).astype(np.float32))
            over(cv, C(0.1, 0.1, 0.12), ((bd < 0.9)).astype(np.float32))
    # glass sheen over the band (top-left)
    sheen = band * np.exp(-((((th - 315 + 180) % 360) - 180) / 35) ** 2) * 0.10
    add(cv, C(1, 1, 1), sheen)


def ring_glyphs(img, c, ss, segs, active=0, rot=0.0, lod=False):
    """Each segment keeps its glyph on a small dark plate at the segment centre (texture + glyph)."""
    d = ImageDraw.Draw(img)
    rm = (R0 + R1) / 2 * ss
    for i, seg in enumerate(segs):
        a = math.radians(i * 120 + rot)
        x, y = c[0] + rm * math.sin(a), c[1] - rm * math.cos(a)
        pr = (R1 - R0) * 0.36 * ss
        d.ellipse([x - pr, y - pr, x + pr, y + pr], fill=(12, 10, 18, 235), outline=SEG_COL.get(seg, (200, 200, 210)) + (255,), width=max(1, int(1.6 * ss)))
        px = int(pr * 1.45)
        gl = SL.glyph_rgba(seg, px, max(1.2, px * 0.08))
        if i != active:
            gl.putalpha(gl.split()[3].point(lambda v: int(v * 0.75)))
        img.alpha_composite(gl, (int(x - gl.width / 2), int(y - gl.height / 2)))


# ------------------------------------------------------------------ extension into the outer slice
def extend(cv, g, ss, seg, slice_mid, t, strength=1.0, span=60):
    """The aligned segment's texture continues up into the slice it modifies (fading out to the rim,
    thinned under the read block)."""
    rho, th = g.rho, g.th
    dd = ((th - slice_mid + 180) % 360) - 180
    wedge = (np.abs(dd) < span / 2 - 1.5) & (rho > R_IN + 2) & (rho < R_OUT - 4)
    u = np.radians(dd) * rho
    vv = np.clip((rho - R_IN) / (R_OUT - R_IN), 0, 1)
    rgb, a = texture(seg, u, vv, rho, t, 7)
    fade = (1 - vv) ** 0.9
    rc = R_IN + 0.6 * (R_OUT - R_IN)
    win = np.exp(-((u / 70) ** 2 + ((rho - rc) / 60) ** 2) * 1.2)
    a = a * wedge * fade * strength * (1 - 0.8 * win)
    over(cv, rgb, a * 0.85)
    # a soft colour wash rising from the ring
    col = C(*SEG_COL.get(seg, (200, 200, 210))) / 255
    add(cv, col, wedge * np.exp(-(rho - R_IN) / 40) * 0.22 * strength)


# ------------------------------------------------------------------ wheel
def wheel(slices, segs, hub, t=0.3, ss=2, r_px=220, tex=True, ext=True, active=0, rot=0.0, lod=None,
          ext_slices=None, post=None, ring=True):
    """ext_slices: list of (compass_deg, strength) the active segment extends into (default: the top slice)."""
    K.setup()
    lod = (r_px < 100) if lod is None else lod
    M = 48
    Ro = R_OUT * ss
    S = int(2 * (Ro + M * ss))
    c = (S / 2, S / 2)
    base = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(base).ellipse([c[0] - Ro - 8 * ss, c[1] - Ro - 8 * ss, c[0] + Ro + 8 * ss, c[1] + Ro + 8 * ss],
                                 fill=(16, 14, 22, 255), outline=hub["acc"] + (255,), width=int(3 * ss))
    cv = np.asarray(base, np.float32) / 255
    cv = cv.copy()
    for i, sl in enumerate(slices):
        prog, val, tier, state = sl[:4]
        theme = sl[4] if len(sl) > 4 else "player"
        K.draw_slice(cv, c[0], c[1], prog, i * 60 - 30, 60, val, t, ss, tier, state, 5 + i, theme=theme)
    g = geom(cv.shape, c, ss)
    if ring:
        over(cv, C(0.06, 0.055, 0.08), ((g.rho < R_IN) & (g.rho > R0 - 6)).astype(np.float32))
        draw_ring(cv, g, ss, hub["acc"], segs, active, t, tex, lod, rot)
        if ext and segs[active] != "SEG_blank":
            for (mid, k) in (ext_slices or [(0, 1.0)]):
                extend(cv, g, ss, segs[active], mid, t, k)
    img = K.to_rgba(cv)
    if post:
        post(img, c, ss, g)
    if ring and not lod:
        ring_glyphs(img, c, ss, segs, active, rot, lod)
    old = H.HUB_R
    H.HUB_R = HUB
    H.draw_hub(img, c, ss, hub["acc"], hub["emblem"], hub["name"], hub.get("sub", ""), hub.get("mk2", False),
               hub.get("enemy", False), hub.get("breached", False), t, lod, 3)
    H.HUB_R = old
    H.pointer(img, c, ss, Ro)
    k = r_px / R_OUT / ss
    return img.resize((int(S * k), int(S * k)), Image.LANCZOS)
