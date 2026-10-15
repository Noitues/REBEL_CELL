"""AAA-2 r2: the route links in wax grease pencil (designer note 2), drawn at 1920 x 1080 like the rest of the overlay.

Medium: ui31.Pencil, the opaque waxy grease pencil of the bible (grain drop-outs, satin edge, dark under-shadow),
in the locked state colours:
  walked  lime wax, solid                     option  orange wax, solid (the hovered option: solid, other one dimmed)
  ahead   white wax dashes (solid on hover)   past    grey wax, translucent (38 %)
A faint glow in the state colour sits under the walked and option wax (what is left of the AAA-2 holo tubes).
The wax never runs under a sticker: every pencil mask is erased inside each node sticker's ring and each option's
number chip, so the links stop short of the icons.
"""
import math
import random

from PIL import Image, ImageDraw

import compose3 as C3
import sgraph3 as G
import sidekit as S
import sticker_lib31 as SL
import ui31 as K

# style: colour, width (px at 1080 before k), dash (on, off) or None, alpha, glow (0-255), pencil seed
WAX = {
    "walked": (S.LIME, 8.0, None, 1.0, 95, 501),
    "option": (S.ORANGE, 8.5, None, 1.0, 110, 502),
    "future": (S.WHITE, 5.2, (14.0, 9.0), 1.0, 0, 503),
    "grey": (S.GREY, 4.0, None, 0.38, 0, 504),
}
WOBBLE = 0.7          # px of hand wobble per vertex before smoothing
CLEAR_PAD = 5.0       # px kept clear round a sticker's ring


def _poly_len(p):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(p, p[1:]))


def _dashes(pts, on, off):
    """Split a polyline into dash polylines by arc length."""
    out, cur, s, phase_on = [], [pts[0]], 0.0, True
    left = on
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        t = 0.0
        while L - t > left:
            t += left
            q = (a[0] + (b[0] - a[0]) * t / L, a[1] + (b[1] - a[1]) * t / L)
            if phase_on:
                cur.append(q)
                if len(cur) > 1:
                    out.append(cur)
                cur = []
            else:
                cur = [q]
            phase_on = not phase_on
            left = on if phase_on else off
        left -= L - t
        if phase_on:
            cur.append(b)
    if phase_on and len(cur) > 1:
        out.append(cur)
    return out


def _smooth(pen, pts):
    pts = [pts[0]] + pen.wobble(pts[1:-1], WOBBLE) + [pts[-1]] if len(pts) > 2 else list(pts)
    # densify long straight runs a little so the wax pressure varies along them
    dense = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 40))
        for i in range(1, n + 1):
            dense.append((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n))
    return SL.catmull(dense, 4)


def sticker_clear_zones(A, st, opts):
    """(x, y, r) circles round every sticker ring and option number chip, as draw_nodes places them."""
    zones = []
    for i in G.NODES:
        poly = C3.room_poly(A, i)
        if not poly:
            continue
        s = st[i]
        kind = G.KIND[i]
        sc = C3.room_scale(A, i)
        ks = min(1.9, max(0.75, sc * 0.8))
        px = int(C3.STK_PX["target" if kind == "target" else ("start" if kind == "start" else s)] * ks)
        x, y = C3.sticker_xy(A, i, ks)
        if kind == "target":
            x = sum(p[0] for p in poly) / 4
            y = sum(p[1] for p in poly) / 4 - 4
        w = 5 if s in ("option", "current") else 3
        zones.append((x, y, px / 2 + 6 * ks + max(w, w * ks * 0.8) / 2 + CLEAR_PAD))
        if s == "option":
            cx, cy = x - px / 2 - 20 * ks, y - px * 0.32
            zones.append((cx, cy, 20 * ks + CLEAR_PAD))
    return zones


def wax_style(es, hov_edge, in_branch, hovering):
    col, w, dash, a, gl, seed = WAX[es if es in WAX else "grey"]
    if hov_edge:
        return S.ORANGE, w + 1.0, None, 1.0, 140, seed
    if es == "option" and hovering:
        return col, w, None, 0.55, 0, seed
    if es == "future" and hovering:
        if in_branch:
            return col, w + 0.4, None, 1.0, 60, seed
        return col, w, dash, 0.42, 0, seed
    return col, w, dash, a, gl, seed


def draw_wax(img, A, est, st, opts, cur, hover=None, hover_k=0.0, k=1.0):
    hovering = hover is not None and hover_k > 0.3
    br_e = G.branch(hover)[1] if hovering else set()
    groups = {}          # (col, alpha, seed) -> (pencil, glow mask)
    order = {"grey": 0, "future": 1, "option": 2, "walked": 3}
    edges = sorted(A["edges"], key=lambda e: (order[est[(e["a"], e["b"])]], e["a"], e["b"]))
    for e in edges:
        key = (e["a"], e["b"])
        es = est[key]
        pts = [tuple(p) for p in e["pts"] if p is not None]
        if len(pts) < 2:
            continue
        hov_edge = hovering and e["b"] == hover and e["a"] == cur
        col, w, dash, a, gl, seed = wax_style(es, hov_edge, key in br_e, hovering)
        gk = (order[es] + (10 if hov_edge else 0), col, a, seed)
        if gk not in groups:
            groups[gk] = (K.Pencil((S.W, S.H), col, seed=seed), Image.new("L", (S.W, S.H), 0), gl)
        pen, gm, _ = groups[gk]
        sm = _smooth(pen, pts)
        ww = max(2.5, w * k)
        if dash:
            for d in _dashes(sm, dash[0] * k, dash[1] * k):
                if _poly_len(d) > 2.0:
                    pen.stroke(d, width=ww, taper=True)
        else:
            pen.stroke(sm, width=ww, taper=True)
        if gl:
            ImageDraw.Draw(gm).line(sm, fill=gl, width=int(ww * 1.6), joint="curve")
    zones = sticker_clear_zones(A, st, opts)
    ss = SL.SS
    for gk in sorted(groups, key=lambda g: (g[0], g[3])):
        pen, gm, gl = groups[gk]
        for (x, y, r) in zones:
            pen.d.ellipse([(x - r) * ss, (y - r) * ss, (x + r) * ss, (y + r) * ss], fill=0)
            ImageDraw.Draw(gm).ellipse([x - r, y - r, x + r, y + r], fill=0)
        col, a = gk[1], gk[2]
        if gl:
            img = K.add_glow(img, gm, col, 9, 0.5)
        if a >= 0.999:
            img = pen.ink(img, shadow=0.85)
        else:
            img = Image.blend(img, pen.ink(img.copy(), shadow=0.6), a)
    return img
