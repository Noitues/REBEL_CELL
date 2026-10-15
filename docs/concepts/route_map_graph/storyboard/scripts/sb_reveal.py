"""Storyboard v2 (designer re-plan): the street-level REVEAL and the MARKERS, as 2D compositing over two street renders
of the same OVERVIEW camera, walls closed (S_ovc) and walls open (S_ov). Light is linear and the camera holds still,
so a room's wall going is the open render inside its dissolved cells, plus its light spill growing round it.

Order (designer): the start room's wall breaks into bits; then, layer by layer to the TARGET, the grease-pencil link
from the previous layer writes on, then that layer's walls dissolve. Then the markers: stickers slap on, the state rings
and room frames draw in, the option numbers pop, and the red pencil TARGET circle and word write on last. The route UI
(top strip, DISPATCH, dossier, ROUTE panel, key strip, toggle) arrives with the markers.

All timing lives in REVEAL / MARKS below (seconds from the beat's start).
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import compose3 as C3  # noqa: E402
import sidekit as S  # noqa: E402
import sgraph3 as G  # noqa: E402
import sticker_lib31 as SL  # noqa: E402
import ui31 as K  # noqa: E402
import wax_r2 as WX  # noqa: E402
import sb_ui as U  # noqa: E402

W, H = 1920, 1080
REVEAL = dict(first=0.35, link=0.22, wall=0.25, stagger=0.06)
MARKS = dict(sticker=0.18, stagger=0.025, ring=0.40, ring_at=0.15, numbers_at=0.45, numbers=0.12, target_at=0.60,
             target=0.40, ui_at=0.0, ui=0.35)


def layers():
    return sorted(set(G.LAYER[i] for i in G.NODES))


def wall_start(i):
    """When room i's wall starts to dissolve (s from the reveal start)."""
    L = G.LAYER[i]
    rooms = sorted([j for j in G.NODES if G.LAYER[j] == L], key=lambda j: G.K[j])
    k = rooms.index(i)
    if L == 0:
        return k * REVEAL["stagger"]
    return link_start(L) + REVEAL["link"] + k * REVEAL["stagger"]


def link_start(L):
    """The links from layer L-1 into layer L write on from here (s)."""
    return REVEAL["first"] + (L - 1) * (REVEAL["link"] + REVEAL["wall"])


def reveal_len():
    return max(wall_start(i) for i in G.NODES) + REVEAL["wall"]


def marks_len():
    return MARKS["target_at"] + MARKS["target"]


def wall_k(i, tr):
    return U.clamp((tr - wall_start(i)) / REVEAL["wall"])


def link_k(e, tr):
    L = G.LAYER[e["b"]]
    return U.clamp((tr - link_start(L)) / REVEAL["link"])


# ---------------------------------------------------------------- the walls (closed -> open per room)
def reveal_plate(closed, opened, A, tr):
    """closed / opened: finished street plates (same camera). Returns the plate with every room's wall at its dissolve
    progress: open render in the dissolved cells, the light spill growing round the room, lime / cyan edge cells."""
    c = np.asarray(closed.convert("RGB"), np.float32) / 255
    o = np.asarray(opened.convert("RGB"), np.float32) / 255
    if o.shape != c.shape:
        o = np.asarray(opened.convert("RGB").resize(closed.size, Image.LANCZOS), np.float32) / 255
    Hh, Ww = c.shape[:2]
    s = Ww / float(W)
    inside = np.zeros((Hh, Ww), np.float32)
    spill = np.zeros((Hh, Ww), np.float32)
    edge = np.zeros((Hh, Ww, 3), np.float32)
    for i in G.NODES:
        d = wall_k(i, tr)
        if d <= 0:
            continue
        p = A["rooms"][i]["front"]
        if not p or any(q is None for q in p):
            continue
        poly = [(q[0] * s, q[1] * s) for q in p]
        m = Image.new("L", (Ww, Hh), 0)
        ImageDraw.Draw(m).polygon(poly, fill=255)
        mq = np.asarray(m, np.float32) / 255
        if d >= 1:
            inside = np.maximum(inside, mq)
            spill = np.maximum(spill, np.asarray(m.filter(ImageFilter.GaussianBlur(28 * s)), np.float32) / 255 * 1.6)
            continue
        # bit cells: about 0.7 BU on the wall (the room is 10-17 BU wide)
        x0, x1 = min(q[0] for q in poly), max(q[0] for q in poly)
        y0, y1 = min(q[1] for q in poly), max(q[1] for q in poly)
        n = max(6, int(14 * (x1 - x0) / max(1.0, 160 * s)) + 8)
        cw = max(2.0, (x1 - x0) / n)
        gx = int(math.ceil((x1 - x0) / cw)) + 1
        gy = int(math.ceil((y1 - y0) / cw)) + 1
        rng = np.random.default_rng(1300 + G.NODES.index(i))
        cells = rng.random((gy, gx)).astype(np.float32)
        yy, xx = np.mgrid[0:Hh, 0:Ww]
        ci = np.clip(((xx - x0) / cw).astype(np.int32), 0, gx - 1)
        cj = np.clip(((yy - y0) / cw).astype(np.int32), 0, gy - 1)
        nz = cells[cj, ci]
        gone = (nz < d).astype(np.float32) * mq
        ring = ((nz >= d) & (nz < d + 0.10)).astype(np.float32) * mq
        inside = np.maximum(inside, gone)
        sp = Image.fromarray((gone * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(28 * s))
        spill = np.maximum(spill, np.asarray(sp, np.float32) / 255 * 1.6 * d)
        col = np.where((cells[cj, ci] > 0.55)[..., None], np.array([0.83, 1.0, 0.0]), np.array([0.2, 0.9, 1.0]))
        edge += ring[..., None] * col
    k = np.clip(np.maximum(inside, spill), 0, 1)[..., None]
    out = c + (o - c) * k
    out = out + edge * 0.85
    eg = Image.fromarray((np.clip(edge, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5 * s))
    out = out + np.asarray(eg, np.float32) / 255 * 0.6
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8))


def reveal_bits(img, A, tr):
    """The 2D bits: 0/1 glyphs lifting and scattering off each wall while it dissolves (0.55 s life)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    any_ = False
    for k, i in enumerate(sorted(G.NODES, key=lambda j: (G.LAYER[j], G.K[j]))):
        ts = wall_start(i)
        if not (ts - 0.02 < tr < ts + REVEAL["wall"] + 0.55):
            continue
        p = A["rooms"][i]["front"]
        if not p or any(q is None for q in p):
            continue
        r = random.Random(900 + k)
        x0, x1 = min(q[0] for q in p), max(q[0] for q in p)
        y0, y1 = min(q[1] for q in p), max(q[1] for q in p)
        n = int(min(70, 14 + (x1 - x0) * (y1 - y0) / 120))
        for j in range(n):
            born = ts + r.random() * REVEAL["wall"]
            age = tr - born
            u, v = r.random(), r.random()
            vx, vy = r.uniform(-50, 50), -r.uniform(40, 130)
            ch = r.choice("01")
            col = U.LIME if r.random() < 0.6 else U.CYAN
            sz = r.choice((11, 13, 15))
            if age < 0 or age > 0.55:
                continue
            x = x0 + (x1 - x0) * u + vx * age
            y = y0 + (y1 - y0) * v + vy * age - 40 * age * age
            d.text((x, y), ch, font=U.bitfont(sz), fill=col + (int(255 * (1 - age / 0.55) ** 1.3),), anchor="mm")
            any_ = True
    if not any_:
        return img
    g = lay.split()[3].filter(ImageFilter.GaussianBlur(4))
    img = K.over(img.convert("RGBA"), U.LIME, g, 0.5)
    img.alpha_composite(lay)
    return img


# ---------------------------------------------------------------- the links writing on (wax pencil, truncated by arc)
def _cut(pts, k):
    if k >= 1:
        return pts
    L = WX._poly_len(pts) * k
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        if L >= seg:
            out.append(b)
            L -= seg
        else:
            u = L / max(seg, 1e-6)
            out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
            break
    return out


def draw_links(img, A, tr, zones=True):
    st, opts = G.states(SB_WALK())
    est = G.edge_states(SB_WALK(), st)
    order = {"grey": 0, "future": 1, "option": 2, "walked": 3}
    groups = {}
    k = min(1.6, max(0.8, C3.room_scale(A, SB_WALK()[-1]) * 0.62))
    for e in sorted(A["edges"], key=lambda e: (order[est[(e["a"], e["b"])]], e["a"], e["b"])):
        lk = link_k(e, tr)
        if lk <= 0:
            continue
        es = est[(e["a"], e["b"])]
        pts = [tuple(p) for p in e["pts"] if p is not None]
        if len(pts) < 2:
            continue
        col, w, dash, a, gl, seed = WX.wax_style(es, False, False, False)
        gk = (order[es], col, a, seed)
        if gk not in groups:
            groups[gk] = (K.Pencil((W, H), col, seed=seed), Image.new("L", (W, H), 0), gl)
        pen, gm, _ = groups[gk]
        sm = _cut(WX._smooth(pen, pts), lk)
        if len(sm) < 2:
            continue
        ww = max(2.5, w * k)
        if dash:
            for dd in WX._dashes(sm, dash[0] * k, dash[1] * k):
                if WX._poly_len(dd) > 2.0:
                    pen.stroke(dd, width=ww, taper=True)
        else:
            pen.stroke(sm, width=ww, taper=True)
        if gl:
            ImageDraw.Draw(gm).line(sm, fill=gl, width=int(ww * 1.6), joint="curve")
    zs = WX.sticker_clear_zones(A, st, opts) if zones else []
    ss = SL.SS
    for gk in sorted(groups, key=lambda g: (g[0], g[3])):
        pen, gm, gl = groups[gk]
        for (x, y, r) in zs:
            pen.d.ellipse([(x - r) * ss, (y - r) * ss, (x + r) * ss, (y + r) * ss], fill=0)
            ImageDraw.Draw(gm).ellipse([x - r, y - r, x + r, y + r], fill=0)
        if gl:
            img = K.add_glow(img, gm, gk[1], 9, 0.5)
        img = pen.ink(img, shadow=0.85)
    return img


def SB_WALK():
    import sb_cams as SB
    return SB.WALK


# ---------------------------------------------------------------- the markers (stickers slap, rings draw, numbers, TARGET)
def _arc(img, x, y, r, col, w, k, alpha=1.0):
    if k <= 0:
        return img
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).arc([x - r, y - r, x + r, y + r], -90, -90 + 360 * k, fill=255, width=int(w))
    img = SL.over(img, (6, 5, 10), SL.scale_mask(SL.shift(m, 1, 2), alpha))
    return SL.over(img, col, SL.scale_mask(m, alpha))


def _frame(img, poly, col, w, k):
    if k <= 0:
        return img
    pts = list(poly) + [poly[0]]
    pts = _cut(pts, k)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).line(pts, fill=255, width=int(w), joint="curve")
    img = K.add_glow(img, m, col, 8, 0.5)
    return SL.over(img, col, m)


def draw_marks(img, A, tm):
    """tm: seconds from the markers' start. Stickers slap (scale 1.35 -> 1, 0.18 s, staggered), the room frames and the
    state rings draw on, the option numbers pop, the token lands; the red pencil TARGET writes on last."""
    walked = SB_WALK()
    st, opts = G.states(walked)
    nodes = sorted(G.NODES, key=lambda n: (G.LAYER[n], G.K[n]))
    for idx, i in enumerate(nodes):
        poly = C3.room_poly(A, i)
        if not poly or not C3.on_screen(poly, 120):
            continue
        s = st[i]
        kind = G.KIND[i]
        sc = C3.room_scale(A, i)
        ks = min(1.9, max(0.75, sc * 0.8))
        rk = U.clamp((tm - MARKS["ring_at"] - idx * MARKS["stagger"]) / MARKS["ring"])
        if kind != "target":
            col = S.STATE_COL[s]
            w = 4 if s in ("option", "current") else 2
            w = max(w, int(round(w * min(1.6, sc * 0.7))))
            img = _frame(img, poly, col, w, rk)
        px = int(C3.STK_PX["target" if kind == "target" else ("start" if kind == "start" else s)] * ks)
        x, y = C3.sticker_xy(A, i, ks)
        if kind == "target":
            x = sum(p[0] for p in poly) / 4
            y = sum(p[1] for p in poly) / 4 - 4
        pk = U.clamp((tm - idx * MARKS["stagger"]) / MARKS["sticker"])
        if pk > 0:
            slap = 1.0 + 0.35 * (1 - U.ease_out(pk))
            img = S.sticker(img, kind, x, y, int(px * slap), alpha=1.0, hover=0.25 if s == "option" else 0.0)
        if kind != "target":
            w2 = 5 if s in ("option", "current") else 3
            img = _arc(img, x, y, px / 2 + 6 * ks, S.STATE_COL[s], max(w2, int(w2 * ks * 0.8)), rk)
        if s == "option":
            nk = U.clamp((tm - MARKS["numbers_at"]) / MARKS["numbers"])
            if nk > 0:
                n = opts.index(i) + 1
                img = C3.number_chip(img, x - px / 2 - 20 * ks, y - px * 0.32, n, s=ks * (0.6 + 0.4 * U.ease_out(nk)),
                                     col=S.ORANGE)
    cur = walked[-1]
    if tm >= MARKS["numbers_at"]:
        k = min(1.6, max(0.8, C3.room_scale(A, cur) * 0.62))
        img = C3.token_at(img, A, cur, k)
    tk = U.clamp((tm - MARKS["target_at"]) / MARKS["target"])
    if tk > 0:
        img = target_write(img, A, tk)
    return img


def target_write(img, A, k):
    """The red pencil TARGET circle and word, written on (an angular wipe round the circle, then the word left to right)."""
    poly = C3.room_poly(A, "L7_0")
    if not poly:
        return img
    cx = sum(p[0] for p in poly) / 4
    cy = sum(p[1] for p in poly) / 4
    rx = math.hypot(poly[1][0] - poly[0][0], poly[1][1] - poly[0][1]) / 2 + 6
    ry = abs(poly[0][1] - poly[3][1]) / 2 + 20
    word = (min(cx - rx - 30, W - 230), max(140, cy - ry - 26))
    pr = S.target_pencil(cx, cy, rx, ry, word)
    ss = SL.SS
    mw, mh = pr.mask.size
    yy, xx = np.mgrid[0:mh, 0:mw].astype(np.float32)
    ang = (np.degrees(np.arctan2(yy / ss - cy, xx / ss - cx)) + 90.0) % 360.0
    in_circle = (np.abs((xx / ss - cx) / (rx + 30)) ** 2 + np.abs((yy / ss - cy) / (ry + 30)) ** 2) < 1.6
    kc = U.clamp(k / 0.6)
    kw = U.clamp((k - 0.6) / 0.4)
    wx0 = word[0] - 20
    wx1 = word[0] + 230
    keep = np.where(in_circle, ang <= 360.0 * kc, (xx / ss) <= wx0 + (wx1 - wx0) * kw)
    m = np.asarray(pr.mask, np.float32) * keep
    pr.mask = Image.fromarray(m.astype(np.uint8))
    pr.d = ImageDraw.Draw(pr.mask)
    return S.finish_pencil(img, pr)


def route_chrome(img, A, zoom, alpha=1.0):
    """The route page furniture (no route marks): top strip + DISPATCH, dossier + ROUTE panel, key strip, toggle."""
    st, opts = G.states(SB_WALK())
    ui = S.chrome_top(img.copy(), C3.DISPATCH["start"])
    ui = S.sidebar(ui, len(opts))
    ui = S.legend(ui, hot=False, cx=1010)
    ui = C3.view_toggle(ui, zoom)
    return ui if alpha >= 1 else Image.blend(img.convert("RGBA"), ui.convert("RGBA"), alpha)
