"""Round 41: multi-drone docking, the parasite pop-up, parasite + drones, and the full per-slice layer stack.

Radial zoning (master units, player wheel: R_IN 130, R_OUT 360, frame edge RA = 414):
  hub/inner ring  < 127   | sub-needle 127-152 | ring texture extension 132-180 | firmware socket ~168
  read block ~268 (always on top) | state badge + xN tab: outer-CW corner | tier inset: screen edge
  frame/telemetry 360-414 | needle blade 336-510 | parasite ATTACHED 420-462 | parasite POPPED 526-616
  drones: beyond whatever ring is on the slice (+20) | card-preview ghost blade: same band as the needle
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import frames as F
from frames import P, Q, INK, CREAM
import slicelib as SL
from slicelib import PROGRAMS, f_num, f_ui, f_mono, glyph_rgba, number_rgba, shadowed, icon_block
import sat2 as S2
import sat3 as S3
from sat2 import Comp, SAT_R, host_image

PAIR_DA = 14.0          # two drones on one slice: +-14 deg (chords clear at the dock radius)
ATTACHED = (6, 48)      # parasite attached: thin band hugging the frame (offsets from RA)
POP_GAP = 16            # popped: starts this far beyond the needle tip (layout A)
POP_DEPTH = 90


def par_radii(c, state, top):
    """state 0 = attached, 1 = popped (tweens between)."""
    a0, a1 = c.RA + ATTACHED[0], c.RA + ATTACHED[1]
    b0, b1 = top + POP_GAP, top + POP_GAP + POP_DEPTH
    e = state * state * (3 - 2 * state)
    return a0 + (b0 - a0) * e, a1 + (b1 - a1) * e


def drone_r(c, par=None, top=None):
    """Dock radius: drones always sit beyond whatever parasite ring is on their slice."""
    base = S2.dock_r(c.RA)
    if par is None:
        return base
    r_in, r_out = par_radii(c, par, top)
    return max(base, r_out + 26 + SAT_R)


def dock_multi(c, a_slice, angles, host_spec, rot=0.0, r_dock=None, glow=1.0):
    """Blended dock with any number of satellites on one slice: one rim band, a neck + collar per satellite."""
    RA = c.RA
    r_dock = r_dock or S2.dock_r(RA)
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
    f = np.clip(1 - np.abs(dth) / 27, 0, 1) ** 0.6 * np.exp(-((rho - (RA + 6)) / 22) ** 2)
    for a in angles:
        da = ((th - a + 180) % 360) - 180
        sx, sy = c.PP(r_dock, a)
        dS = np.hypot(X + c.C[0] - sx, Y + c.C[1] - sy)
        coll = np.exp(-(np.maximum(0, dS - SAT_R - 4) / 18) ** 2) * (dS < SAT_R + 60)
        rr0, rr1 = RA, r_dock - SAT_R
        q = np.clip((rho - rr0) / max(1, rr1 - rr0), 0, 1)
        lat = np.abs(np.radians(da)) * rho
        wneck = 40 - 22 * np.sin(np.pi * q)
        neck = np.exp(-(lat / wneck) ** 2) * ((rho > rr0 - 10) & (rho < rr1 + 30))
        f = np.maximum(f, np.maximum(coll, neck))
    m = Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    m = m.filter(ImageFilter.GaussianBlur(6)).point(lambda v: 255 if v > 110 else 0)
    edge = m.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))
    c.under.paste(Image.new("RGBA", (W, H), (14, 13, 20, 235)), (0, 0), m)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g.paste(Image.new("RGBA", (W, H), pc + (int(170 * glow),)), (0, 0), edge.filter(ImageFilter.MaxFilter(9)))
    c.under.alpha_composite(g.filter(ImageFilter.GaussianBlur(8)))
    c.under.paste(Image.new("RGBA", (W, H), pc + (255,)), (0, 0), edge)


def put_drones(c, sat, a_slice, n, host_spec, rot=0.0, r_dock=None, lod=False, states=None):
    angles = [a_slice] if n == 1 else [a_slice - PAIR_DA, a_slice + PAIR_DA]
    r_dock = r_dock or S2.dock_r(c.RA)
    dock_multi(c, a_slice, angles, host_spec, rot, r_dock)
    for k, a in enumerate(angles):
        st = (states or {}).get(k)
        c.put_sat(sat, a, offset=r_dock - S2.dock_r(c.RA), lod=lod, state=st)


def parasite(c, slot, rot, top, state=0.0, lit=None, lod=False):
    """state 0 attached (thin, glyphs only), 1 popped beyond the needle tip (full: glyph + value)."""
    r_in, r_out = par_radii(c, state, top)
    small = (r_out - r_in) < 70
    S3.parasite2(c, slot, "A", rot=rot, top=top, lit=lit, lod=lod or small, radii=(r_in, r_out))
    return r_in, r_out


# ------------------------------------------------------------------ per-slice layers (combined sheet)
def read_block(c, spec, slot, rot):
    """Re-stamp the slot's glyph + value block on top (the read block always wins)."""
    sl = spec["slots"][slot]
    val = sl["value"] if sl["program"] != "NULL" else None
    blk = shadowed(icon_block(sl["program"], val, 60, 1), 1)
    a = 60 * slot + rot
    x, y = c.PP(SL.R_IN + 0.6 * (SL.R_OUT - SL.R_IN), a)
    c.top.alpha_composite(blk, (int(x - blk.width / 2), int(y - blk.height / 2)))


def ring_extension(c, slot, rot, col=(255, 205, 90)):
    """Inner-ring segment texture extending into the slice root (round 39/40, locked look: a hatch band)."""
    a = 60 * slot + rot
    lay = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in range(-60, 61, 3):
        p0 = c.PP(SL.R_IN + 4, a + k * 0.45)
        p1 = c.PP(SL.R_IN + 52, a + k * 0.45 + 4)
        d.line([p0, p1], fill=col + (120,), width=4)
    mask = Image.new("L", (c.W, c.H), 0)
    md = ImageDraw.Draw(mask)
    poly = [c.PP(SL.R_IN + 52, a - 26 + 52 * j / 30) for j in range(31)] + [c.PP(SL.R_IN + 4, a + 26 - 52 * j / 30) for j in range(31)]
    md.polygon(poly, fill=255)
    out = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    out.paste(lay, (0, 0), mask)
    c.top.alpha_composite(out.filter(ImageFilter.GaussianBlur(0.6)))


def firmware_socket(c, slot, rot, glyph="ST_OVERCLOCKED"):
    a = 60 * slot + rot
    x, y = c.PP(168, a)
    d = ImageDraw.Draw(c.top)
    r = 26
    d.rounded_rectangle([x - r, y - r, x + r, y + r], radius=8, fill=(40, 40, 50, 255), outline=(200, 200, 215, 255), width=3)
    for k in range(5):
        px = x - 16 + k * 8
        d.line([(px, y + r), (px, y + r + 8)], fill=(255, 205, 90, 255), width=3)
    d.ellipse([x - r + 5, y - r + 5, x - r + 11, y - r + 11], fill=(123, 224, 123, 255))
    g = glyph_rgba("PI_RAM", 32, 2)
    c.top.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))


def sub_needle(c, slot, rot):
    """60 % cream blade rooted on the inner ring's outer lip (r 127), pointing out; tip stops at the slice lip."""
    a = 60 * slot + rot
    d = ImageDraw.Draw(c.top)
    pts = [c.PP(127, a - 3.4), c.PP(150, a), c.PP(127, a + 3.4)]
    pts = [Qp for Qp in pts]
    d.polygon([c.PP(122, a - 4.2), c.PP(122, a + 4.2), c.PP(150, a)], fill=CREAM + (255,), outline=INK + (255,))


def state_overlay(c, slot, rot, stacks=2):
    """OVERCLOCKED overlay (warm wash, 45 %) + corner badge (outer clockwise) + xN tab + x1.5 rule tag."""
    a = 60 * slot + rot
    mask = Image.new("L", (c.W, c.H), 0)
    md = ImageDraw.Draw(mask)
    poly = [c.PP(SL.R_OUT - 12, a - 27 + 54 * j / 40) for j in range(41)] + [c.PP(SL.R_IN + 12, a + 27 - 54 * j / 40) for j in range(41)]
    md.polygon(poly, fill=255)
    wash = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wash)
    for k in range(10):
        r = SL.R_IN + 20 + k * 22
        arc = [c.PP(r, a - 27 + 54 * j / 30) for j in range(31)]
        wd.line(arc, fill=(255, 150, 40, 70), width=8)
    out = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    out.paste(wash, (0, 0), mask)
    c.top.alpha_composite(out)
    bx, by = c.PP(SL.R_OUT - 46, a + 21)
    d = ImageDraw.Draw(c.top)
    r = 22
    d.ellipse([bx - r, by - r, bx + r, by + r], fill=(20, 16, 10, 255), outline=(255, 176, 60, 255), width=3)
    g = glyph_rgba("ST_OVERCLOCKED", 30, 2, fill=(255, 190, 90))
    c.top.alpha_composite(g, (int(bx - g.width / 2), int(by - g.height / 2)))
    if stacks > 1:
        f = f_num(20)
        s = "x%d" % stacks
        tw = f.getlength(s)
        d.rounded_rectangle([bx + 8, by - r - 10, bx + 18 + tw, by - r + 14], radius=5, fill=INK + (255,), outline=(255, 176, 60, 255), width=2)
        d.text((bx + 13, by - r - 10), s, font=f, fill=(255, 230, 190, 255))
    f = f_num(17)
    d.rounded_rectangle([bx - 20, by + r + 2, bx + 22, by + r + 22], radius=4, fill=(255, 176, 60, 255))
    d.text((bx - 15, by + r + 1), "x1.5", font=f, fill=INK + (255,))
