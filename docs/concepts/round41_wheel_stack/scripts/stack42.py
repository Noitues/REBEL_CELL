"""Round 41 v2: smaller drones that extend less, collapsed drone bands (bloom on hover), and the locked inner ring.

Drones (v2):
- SAT_K 0.22 (was 0.30); docked just outside whatever is on the slice:
  no parasite  -> a SHORT stem: drone inner edge at RA + 30;
  parasite     -> NO stem: the drone sits right on the parasite's outer edge (+4).
- COLLAPSED (default, not hovered): the drones on a slice become one more thin band over the slice arc, one tile per
  drone, showing only the drone's current effect (glyph + value) and HP pips.
- HOVERED: the band blooms into the full mini-wheels (own needle, slices, HP).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import frames as F
from frames import INK, CREAM
import slicelib as SL
from slicelib import R_OUT, R_IN, PROGRAMS, f_num, f_ui, glyph_rgba, number_rgba, shadowed
import sat2 as S2
import sat3 as S3
import stack41 as K41
import ringlock as RL

S2.SAT_K = 0.22
SAT_R = (R_OUT + 44) * S2.SAT_K
STEM = 30
PAIR_DA = 12.0
BAND = 34            # collapsed drone band depth
HP_COL = (123, 224, 123)


def drone_inner(c, par_r_out=None):
    """Radius where the drone layer starts on a slice."""
    return (par_r_out + 4) if par_r_out else (c.RA + STEM)


def dock_lobe(c, a_slice, angles, host_spec, rot, r_dock, stem=True):
    RA = c.RA
    i = int(round(((a_slice - rot) % 360) / 60.0)) % 6
    pc = PROGRAMS[host_spec["slots"][i]["program"]]["col"]
    W, H = c.W, c.H
    sc = 0.25
    w, h = int(W * sc), int(H * sc)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    X, Y = xx / sc - c.C[0], yy / sc - c.C[1]
    rho = np.hypot(X, Y)
    th = np.degrees(np.arctan2(X, -Y))
    dth = ((th - a_slice + 180) % 360) - 180
    f = np.clip(1 - np.abs(dth) / 27, 0, 1) ** 0.6 * np.exp(-((rho - (RA + 4)) / 16) ** 2)
    for a in angles:
        da = ((th - a + 180) % 360) - 180
        sx, sy = c.PP(r_dock, a)
        dS = np.hypot(X + c.C[0] - sx, Y + c.C[1] - sy)
        coll = np.exp(-(np.maximum(0, dS - SAT_R - 3) / 12) ** 2) * (dS < SAT_R + 40)
        f = np.maximum(f, coll)
        if stem:
            rr0, rr1 = RA, r_dock - SAT_R
            lat = np.abs(np.radians(da)) * rho
            neck = np.exp(-(lat / 22) ** 2) * ((rho > rr0 - 6) & (rho < rr1 + 16))
            f = np.maximum(f, neck)
    m = Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    m = m.filter(ImageFilter.GaussianBlur(5)).point(lambda v: 255 if v > 110 else 0)
    edge = m.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))
    c.under.paste(Image.new("RGBA", (W, H), (14, 13, 20, 235)), (0, 0), m)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g.paste(Image.new("RGBA", (W, H), pc + (160,)), (0, 0), edge.filter(ImageFilter.MaxFilter(9)))
    c.under.alpha_composite(g.filter(ImageFilter.GaussianBlur(7)))
    c.under.paste(Image.new("RGBA", (W, H), pc + (255,)), (0, 0), edge)


def drones_full(c, sat, a_slice, n, host_spec, rot=0.0, par_r_out=None, lod=False):
    """Hovered: full mini-wheels. Stem only when there is no parasite."""
    angles = [a_slice] if n == 1 else [a_slice - PAIR_DA, a_slice + PAIR_DA]
    r_dock = drone_inner(c, par_r_out) + SAT_R
    dock_lobe(c, a_slice, angles, host_spec, rot, r_dock, stem=par_r_out is None)
    for a in angles:
        c.put_sat(sat, a, offset=r_dock - S2.dock_r(c.RA), lod=lod)


def drones_band(c, sat, a_slice, n, par_r_out=None, hp=None, hovered=False):
    """Collapsed: one thin band over the slice arc, a tile per drone: current effect (glyph + value) + HP pips."""
    acc = S2.sat_acc(sat)
    r0 = drone_inner(c, par_r_out) - (STEM - 6 if par_r_out is None else 0)
    r1 = r0 + BAND
    span = 54.0
    a0 = a_slice - span / 2
    d = ImageDraw.Draw(c.top)
    gl = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    sp = span / n
    prog, val = sat["slots"][0]
    for k in range(n):
        b0, b1 = a0 + k * sp + 0.8, a0 + (k + 1) * sp - 0.8
        poly = [c.PP(r1, b0 + (b1 - b0) * j / 24) for j in range(25)] + [c.PP(r0, b1 - (b1 - b0) * j / 24) for j in range(25)]
        gd.polygon(poly, outline=acc + (200,), width=10)
        d.polygon(poly, fill=(16, 14, 22, 245), outline=acc + (255,), width=3)
        mid = (b0 + b1) / 2
        rc = (r0 + r1) / 2
        arc = math.radians(b1 - b0) * rc
        off = math.degrees(min(arc * 0.18, 20) / rc)
        g = glyph_rgba(prog, 30, 2)
        x, y = c.PP(rc, mid - off)
        c.top.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))
        nimg = number_rgba(str(val), 34, 2)
        x, y = c.PP(rc, mid + off)
        c.top.alpha_composite(nimg, (int(x - nimg.width / 2), int(y - nimg.height / 2)))
        hpv = sat["hp"] if hp is None else hp
        for j in range(sat["hpmax"]):  # HP pips on the band's outer edge
            aa = b0 + (b1 - b0) * (0.25 + 0.5 * (j + 0.5) / sat["hpmax"])
            x, y = c.PP(r1 - 5, aa)
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(HP_COL if j < hpv else (60, 70, 62)) + (255,))
    for side in (0, 1):  # dock ticks into the frame / parasite
        aa = a0 + 6 + side * (span - 12)
        d.line([c.PP(r0 - 6, aa), c.PP(r0, aa)], fill=acc + (255,), width=4)
    if hovered:
        x, y = c.PP(r1 + 18, a_slice + span / 2 - 4)
        d.polygon([(x, y), (x + 16, y + 30), (x + 6, y + 27), (x + 1, y + 40), (x - 4, y + 38), (x + 1, y + 25), (x - 9, y + 24)],
                  fill=(255, 255, 255, 255), outline=INK + (255,))
    c.top.alpha_composite(gl.filter(ImageFilter.GaussianBlur(6)))
    return r1


def ring_locked(c, segs, ext_slots, rot=0.0, t=0.3, lod=False, acc=(255, 61, 168)):
    """Locked inner ring + texture extension into the aligned slices (ext_slots: [(seg index, slice angle)])."""
    R = int(R_OUT + 6)
    x0, y0 = int(c.C[0] - R), int(c.C[1] - R)
    cvs = np.zeros((2 * R, 2 * R, 4), np.float32)
    g = RL.geom(cvs.shape, (R, R), 1)
    RL.over(cvs, RL.C(0.06, 0.055, 0.08), ((g.rho < R_IN) & (g.rho > RL.R0 - 6)).astype(np.float32))
    RL.draw_ring(cvs, g, 1, acc, segs, 0, t, True, lod, rot)
    for si, ang in ext_slots:
        if segs[si] != "SEG_blank":
            RL.extend(cvs, g, 1, segs[si], ang, t, 1.7)
    img = Image.fromarray((np.clip(cvs, 0, 1) * 255).astype(np.uint8), "RGBA")
    if not lod:
        RL.ring_glyphs(img, (R, R), 1, segs, 0, rot, lod)
    c.top.alpha_composite(img, (x0, y0))
