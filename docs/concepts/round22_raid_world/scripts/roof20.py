"""Round 20 post decals for the node buildings: roof identity (A crown inlay / B uplink pad / C mast, decal-free),
the riser climb to the roof, the Safehouse station slot states, and the stationed-operative boost marks on the street
sockets and links. Same contract as netdecal19.Net: evaluated per pixel on the world position pass, so in Godot each
is a decal / a roof shader reading the same uniforms (variant enum, slot state enum, class colour, emblem index).
"""
import math
import os

import numpy as np
from PIL import Image

import layout as LY
import netdecal19 as ND
from netdecal19 import band, sample, C

HERE = os.path.dirname(os.path.abspath(__file__))
EMBLEMS = os.path.join(os.path.dirname(HERE), "scratch", "emblems")
CLASS_COL = {"breaker": C(1.0, 0.24, 0.66), "wrecker": C(1.0, 0.43, 0.2), "ghost": C(0.36, 0.88, 1.0), "phantom": C(0.86, 0.76, 1.0),
             "rigger": C(0.48, 0.88, 0.48), "overclocker": C(1.0, 0.69, 0.24), "botnet": C(0.38, 0.45, 1.0), "hivemind": C(0.78, 0.35, 1.0)}
CLASS_RGB = {k: tuple(int(v * 255) for v in c) for k, c in CLASS_COL.items()}
WHITE = C(0.95, 0.97, 1.0)
_em = {}


def emblem(name):
    """Class / corp emblem mask (round 6 roster emblems, exported by emblems20.py)."""
    if name not in _em:
        im = Image.open(os.path.join(EMBLEMS, name + ".png")).convert("RGBA").resize((256, 256), Image.LANCZOS)
        _em[name] = np.asarray(im, np.float32)[..., 3] / 255.0
    return _em[name]


def trace3d(net, polys, col, k=1.2, w=0.24, t=None, packets=False):
    """Inlay traces along 3D polylines on any surface (ground, facade, roof)."""
    for poly in polys:
        P = np.array(poly, float)
        lo, hi = P.min(0) - 1.0, P.max(0) + 1.0
        m = ((net.X > lo[0]) & (net.X < hi[0]) & (net.Y > lo[1]) & (net.Y < hi[1]) & (net.Z > lo[2] - 0.5) & (net.Z < hi[2] + 0.5))
        if not m.any():
            continue
        q = np.stack([net.X[m], net.Y[m], net.Z[m]], 1)
        dmin = np.full(q.shape[0], 1e9, np.float32)
        along = np.zeros(q.shape[0], np.float32)
        acc = 0.0
        for i in range(len(P) - 1):
            a, b = P[i], P[i + 1]
            ab = b - a
            L = float(np.linalg.norm(ab))
            tt = np.clip(((q - a) @ ab) / max(1e-6, ab @ ab), 0, 1)
            d = np.linalg.norm(q - (a + tt[:, None] * ab), axis=1)
            closer = d < dmin
            along = np.where(closer, acc + tt * L, along)
            dmin = np.minimum(dmin, d)
            acc += L
        tr = band(dmin, -1, w)
        gr = band(dmin, -1, w * 2.5)
        pulse = band(np.mod(along - (t or 0) * 24.0, 16.0), 0, 1.6) if packets else 0.0
        net.dk[m] *= 1 - 0.45 * gr
        net.em[m] += (tr * k * (1 + 1.5 * pulse))[:, None] * col * net.k


def _surface(net, x0, y0, x1, y1, z, tol=0.45):
    return (net.X > x0) & (net.X < x1) & (net.Y > y0) & (net.Y < y1) & (np.abs(net.Z - z) < tol)


def roof(net, key, variant, slot=None, cls=None, t=0.0, climb=True, state="ok"):
    """slot (Safehouse, variant B): None / 'empty' / 'hover' / 'stationed' / 'recall' (+ cls for the class colour).
    state: ok / dim / dead (follows the node like the street riser)."""
    s = LY.roof_spec(key, variant)
    x0, y0, x1, y1 = s["lot"]
    h = s["top"]
    lc = net.lc
    kst = {"ok": 1.0, "dim": 0.3, "dead": 0.0}[state]
    if climb:
        trace3d(net, LY.climb_paths(key, variant), lc, k=1.2 * kst, t=t, packets=kst > 0.5)
    rh, fh = net.rh, net.fh
    gname = ND.GLYPH_OF[LY.NODES[key][2]]
    if variant == "A":
        m = _surface(net, x0 + 0.4, y0 + 0.4, x1 - 0.4, y1 - 0.4, h)
        if not m.any():
            return
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = net.X[m] - cx, net.Y[m] - cy
        cheb = np.maximum(np.abs(dx), np.abs(dy))
        hs = (x1 - x0) / 2
        a = dx * rh[0] + dy * rh[1]
        b = dx * fh[0] + dy * fh[1]
        ring1 = band(cheb, hs - 1.9, hs - 1.6)
        ring2 = band(cheb, hs - 3.0, hs - 2.75)
        kk = np.mod(np.where(np.abs(dx) > np.abs(dy), dy, dx) + 0.9, 1.8) - 0.9
        pins = band(cheb, hs - 1.55, hs - 0.7) * band(np.abs(kk), -1, 0.32)
        g = sample(ND.glyph(gname), a, b, 4.2)
        diag = band(np.abs(np.abs(dx) - np.abs(dy)), -1, 0.22) * (cheb > 4.6) * (cheb < hs - 3.0)
        em = (ring1 * 1.3 + ring2 * 0.8 + pins * 0.9 + g * 1.2 + diag * 0.9) * kst
        net.dk[m] *= 1 - 0.5 * np.clip(ring1 + ring2 + g, 0, 1)
        net.em[m] += em[:, None] * lc * net.k
    elif variant == "B":
        px, py, hs = s["pad"]
        z = h + s["pad_h"]
        m = _surface(net, px - hs - 0.05, py - hs - 0.05, px + hs + 0.05, py + hs + 0.05, z, 0.3)
        if not m.any():
            return
        dx, dy = net.X[m] - px, net.Y[m] - py
        cheb = np.maximum(np.abs(dx), np.abs(dy))
        r = np.hypot(dx, dy)
        a = dx * rh[0] + dy * rh[1]
        b = dx * fh[0] + dy * fh[1]
        ang = np.mod(np.arctan2(dy, dx) / (2 * math.pi) - t * 0.25, 1.0)
        col = lc
        frame = band(cheb, hs * 0.86, hs * 0.95)
        kk = np.mod(np.where(np.abs(dx) > np.abs(dy), dy, dx) + 0.7, 1.4) - 0.7
        pins = band(cheb, hs * 0.95, hs * 1.02) * band(np.abs(kk), -1, 0.26) * (np.minimum(np.abs(dx), np.abs(dy)) < hs * 0.8)
        notch = ((dx + hs * 0.8) + (dy + hs * 0.8) < hs * 0.35)
        em = np.zeros((dx.shape[0], 3), np.float32)
        dk = np.ones(dx.shape[0], np.float32)
        if slot is None:          # any node: the pad is the street socket's twin (frame, pins, node glyph)
            g = sample(ND.glyph(gname), a, b, hs * 0.55)
            em += ((frame * 1.3 + pins * 0.9 + notch * 0.8 + g * 1.2) * kst)[:, None] * col
            dk *= 1 - 0.5 * np.clip(frame + g, 0, 1)
        else:                     # Safehouse: the station slot
            ccol = CLASS_COL.get(cls, lc) if cls else lc
            R0, R1 = hs * 0.58, hs * 0.7
            if slot == "empty":     # dashed ring = an open slot (glyph language: dashed = available / predicted)
                ring = band(r, R0, R1) * (np.mod(ang * 16, 1.0) < 0.55)
                plus = (band(np.abs(a), -1, 0.22) * (np.abs(b) < 1.3) + band(np.abs(b), -1, 0.22) * (np.abs(a) < 1.3))
                em += (frame * 1.0 + pins * 0.6 + notch * 0.6 + ring * 1.3 + plus * 1.1)[:, None] * col
            elif slot == "hover":   # a valid drop: solid white ring + frame, the slot floods with the class colour
                pul = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 2)
                ring = band(r, R0, R1)
                em += (frame * 1.6 + pins * 1.2 + ring * 2.0)[:, None] * WHITE
                em += (band(r, -1, R0) * (0.25 + 0.25 * pul))[:, None] * ccol
                ring2 = band(r, R1 + 0.3 + pul * 0.8, R1 + 0.6 + pul * 0.8) * (cheb < hs * 0.84)
                em += (ring2 * 1.0)[:, None] * ccol
            elif slot == "stationed":
                ring = band(r, R0, R1)
                ticks = band(r, R1 + 0.2, R1 + 0.9) * (np.mod(ang * 24, 1.0) < 0.3)
                em += (frame * 1.0 + pins * 0.7 + notch * 0.6)[:, None] * col
                em += (ring * 1.6 + ticks * 1.0)[:, None] * ccol
                dk *= 1 - 0.4 * np.clip(ring, 0, 1)
            elif slot == "recall":  # the class ring unwinds (dashes retract) and the slot reads open again
                ring = band(r, R0, R1) * (ang > min(1.0, t))
                em += (frame * 1.0 + pins * 0.6)[:, None] * col + (ring * 1.4)[:, None] * ccol
            elif slot == "emblem":  # option R2: the operative's emblem decal on the pad (no figure)
                g = sample(emblem(cls), a, b, hs * 0.62)
                em += (frame * 1.0 + pins * 0.6 + notch * 0.6)[:, None] * col + (g * 1.6 + band(r, R1 + 0.2, R1 + 0.6) * 1.2)[:, None] * ccol
                dk *= 1 - 0.6 * np.clip(g, 0, 1)
        net.dk[m] *= dk
        net.em[m] += em * net.k


def boost(net, key, cls, kind="own", t=0.0):
    """The stationed operative's bonus on a street socket: class-colour corner brackets outside the frame and the
    class emblem in a chip at the socket's front corner. kind='shared' (adjacency) = dashed brackets, hollow chip."""
    n = LY.NODES[key]
    x, y = n[0], n[1]
    S = ND.PAD_S * (1.15 if key == "core" else 1.0)
    m = net._box(x, y, S * 1.75)
    if not m.any():
        return
    dx, dy = net.X[m] - x, net.Y[m] - y
    ax, ay = np.abs(dx), np.abs(dy)
    cheb = np.maximum(ax, ay)
    col = CLASS_COL[cls]
    corner = (np.minimum(ax, ay) > S * 0.62)
    br = band(cheb, S * 1.18, S * 1.3) * corner
    if kind == "shared":
        per = np.mod((np.arctan2(dy, dx)) / (2 * math.pi) * 40, 1.0)
        br = br * (per < 0.55)
    # emblem chip at the front corner (screen-down = -fh)
    fx, fy = -net.fh[0], -net.fh[1]
    cx, cy = x + fx * S * 1.62, y + fy * S * 1.62
    ddx, ddy = net.X[m] - cx, net.Y[m] - cy
    rr = np.hypot(ddx, ddy)
    a = ddx * net.rh[0] + ddy * net.rh[1]
    b = ddx * net.fh[0] + ddy * net.fh[1]
    disc = band(rr, -1, 3.0)
    edge = band(rr, 2.6, 3.1)
    g = sample(emblem(cls), a, b, 2.1)
    em = br * 1.5 + edge * 1.4
    if kind == "own":
        net.dk[m] *= 1 - 0.75 * disc
        em = em + g * 1.6
    else:
        net.dk[m] *= 1 - 0.5 * disc
        em = em + g * 0.7 + band(rr, 3.4, 3.7) * (np.mod(np.arctan2(ddy, ddx) * 4 / math.pi + t * 4, 1.0) < 0.5) * 1.0
    net.em[m] += em[:, None] * col * net.k


def share_link(net, a, b, cls, t=0.0, k=1.0):
    """Adjacency share: class-colour chevrons running down the middle trace of the link from a to b."""
    pa, pb = np.array(LY.pt(a), float), np.array(LY.pt(b), float)
    s, ac, L = ND.seg_coords(net.X, net.Y, pa, pb)
    m = (s > ND.PAD_S * 1.0) & (s < L - ND.PAD_S * 1.0) & (np.abs(ac) < 4.5) & net.G
    if not m.any():
        return
    ss, aa = s[m], ac[m]
    ph = np.mod(ss - t * 40.0, 9.0)
    chev = band(np.abs(ph - 4.5 + np.abs(aa) * 0.9), -1, 0.45) * (np.abs(aa) < 1.6)
    under = band(np.abs(aa), -1, 0.5)
    net.em[m] += ((chev * 1.8 + under * 0.5) * k)[:, None] * CLASS_COL[cls] * net.k
