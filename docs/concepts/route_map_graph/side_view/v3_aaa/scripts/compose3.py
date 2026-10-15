"""V3 dynamic: compose the overlay media on the finished plates (stills, video frames, zoom GIF).

python compose3.py stills            -> D_start, D_mid, D_mid_hover, D_end, O_overview (.png, 1920 x 1080)
python compose3.py frames [a b]      -> ../scratch/fr/f%03d.png (1920 x 1080) for the video frames a..b
The overlay grammar is the parent's (locked): stickers for the type, state rings / cut frames (lime walked, orange
next + number, white ahead, grey past at 26 %), lime walked cable, orange dashed options, white dashed ahead, the
red pencil TARGET, the token, tags only on hover, the node file (with HP on arrival) on hover, the frame UI.
New here: every size follows the room's on-screen size (decision view = big rooms, big stickers); the hover power cut
fades with hover_k; a DECISION / OVERVIEW toggle sits right of the legend.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import sidekit as S  # noqa: E402
import sgraph3 as G  # noqa: E402
import ui31 as K  # noqa: E402
import kit44 as KT  # noqa: E402
import cam_rig as R  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
W, H = 1920, 1080
DISPATCH = {"start": "Jacked in at the relay. Three floors of Lane 15 are open. The Rack is at the end of the street.",
            "mid": "Shop's behind you. Two ways left: the long way has a Rack.",
            "end": "One rail ride between you and Meridian's server. Make it count.",
            "L1_0": "Guard room's clear. There's a plank across to the next block.",
            "L2_0": "The terminal went quiet. A duct runs up to a shop."}
STK_PX = {"option": 48, "current": 44, "walked": 36, "reach": 40, "grey": 34, "target": 62, "start": 42}
POWER_CUT = 0.32          # hover: the rest of the street drops to 32 %


def f2a(img):
    return np.asarray(img.convert("RGB"), np.float32) / 255.0


def a2f(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")


def lum(a):
    return a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11


def poly_ok(p):
    return p and all(q is not None for q in p)


def poly_mask(poly, grow=0, blur=0):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in poly], fill=255)
    if grow:
        m = m.filter(ImageFilter.MaxFilter(grow * 2 + 1))
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(m, np.float32) / 255.0


def room_poly(A, i):
    p = A["rooms"][i]["front"]
    return p if poly_ok(p) else None


def room_scale(A, i):
    p = room_poly(A, i)
    if not p:
        return 1.0
    return max(0.5, math.hypot(p[1][0] - p[0][0], p[1][1] - p[0][1]) / 116.0)


def on_screen(p, m=40):
    return p and any(-m < q[0] < W + m and -m < q[1] < H + m for q in p)


# ---------------------------------------------------------------- world grade
def grade(img, A, st, cur, hover, hover_k, focus):
    a = f2a(img)
    br = G.branch(hover)[0] if hover else set()
    out = a.copy()
    if focus:
        # decision view: a soft spotlight on the usable area (corners -18 %)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - R.UCX) / (W * 0.62)) ** 2 + ((yy - R.UCY) / (H * 0.62)) ** 2)
        out = out * (1 - 0.18 * np.clip(d - 0.55, 0, 1)[..., None] * focus)
    if hover and hover_k > 0:
        keep = np.zeros((H, W), np.float32)
        for i in sorted(br | {cur}):
            p = room_poly(A, i)
            if p:
                keep = np.maximum(keep, poly_mask(p, grow=6, blur=6))
        l3 = lum(out)[..., None]
        dim = (out * 0.6 + l3 * 0.4) * POWER_CUT
        cut = out * (1 - hover_k) + dim * hover_k
        out = out * keep[..., None] + cut * (1 - keep[..., None])
    for i in G.NODES:
        p = room_poly(A, i)
        if not p or not on_screen(p):
            continue
        s = st[i]
        m = poly_mask(p, grow=1)[..., None]
        r = out
        l3 = lum(r)[..., None]
        if s == "grey":
            ghost = np.array((0.06, 0.05, 0.11), np.float32)
            v = (l3 * 0.55) * 0.45 + ghost * 0.55
        elif s == "walked":
            v = (r * 0.5 + l3 * 0.5) * 0.55
        elif hover and i in br:
            v = r * (1 + 0.45 * hover_k)
        elif s == "option":
            v = r * 1.18
        else:
            v = r
        out = out * (1 - m) + v * m
    img = a2f(out)
    if hover and hover_k > 0.05:
        for i in sorted(br, key=lambda n: (G.LAYER[n], G.K[n])):
            p = room_poly(A, i)
            if p:
                m = Image.fromarray((poly_mask(p) * 255).astype(np.uint8))
                img = K.add_glow(img, m, S.TYPE_COL[G.KIND[i]], int(26 * min(2.0, room_scale(A, i))), 0.55 * hover_k)
    return img


# ---------------------------------------------------------------- cables
def cable_style(es, hov_edge, in_branch, hovering):
    if es == "walked":
        return ("solid", S.LIME, 7, 255, 200)
    if hov_edge:
        return ("solid", S.ORANGE, 8, 255, 230)
    if es == "option":
        return ("dashed", S.ORANGE, 8, 255 if not hovering else 150, 160 if not hovering else 0)
    if es == "future":
        if in_branch:
            return ("solid", S.WHITE, 5, 245, 150)
        return ("dashed", S.WHITE, 5, 235 if not hovering else 110, 0)
    return ("solid", S.GREY, 4, int(255 * S.GREY_A), 0)


def clip_pts(pts):
    return [tuple(p) for p in pts if p is not None]


def draw_cables(img, A, est, cur, hover=None, hover_k=0.0, step=None, k=1.0):
    hovering = hover is not None and hover_k > 0.3
    br_e = G.branch(hover)[1] if hovering else set()
    cab = S.Cables()
    order = {"grey": 0, "future": 1, "option": 2, "walked": 3}
    edges = sorted(A["edges"], key=lambda e: (order[est[(e["a"], e["b"])]], e["a"], e["b"]))
    for e in edges:
        key = (e["a"], e["b"])
        es = est[key]
        pts = clip_pts(e["pts"])
        if len(pts) < 2:
            continue
        hov_edge = hovering and e["b"] == hover and e["a"] == cur
        kind, col, w, a, gl = cable_style(es, hov_edge, key in br_e, hovering)
        if step and es == "option" and key != (step[0], step[1]):
            a = int(a * 0.45)
            gl = 0
        w = max(2, int(round(w * k)))
        if kind == "solid":
            cab.solid(pts, col, w, casing=max(2, int(3 * k)) if es != "grey" else 0, a=a, glow=gl)
        else:
            cab.dashed(pts, col, w, on=int((18 if es == "option" else 12) * k), off=int(9 * k), casing=max(2, int(3 * k)), a=a, glow=gl)
    tok = None
    if step:
        e = next(e for e in A["edges"] if e["a"] == step[0] and e["b"] == step[1])
        pts = clip_pts(e["pts"])
        part, tok = S.cut_poly(pts, step[2])
        if len(part) > 1:
            cab.solid(part, S.LIME, max(3, int(7 * k)), casing=3, a=255, glow=220)
    return cab.comp(img, glow_col=(255, 200, 120)), tok


# ---------------------------------------------------------------- nodes
def number_chip(img, x, y, n, s=1.0, col=S.ORANGE):
    hw, hh = 15 * s, 16 * s
    box = (x - hw, y - hh, x + hw, y + hh)
    img = KT.panel_shadow(img, box, 0, blur=6, k=0.55, off=(0, 3))
    d = K.BD(img)
    d.rectangle(box, fill=col + (255,), outline=(10, 8, 14, 255), width=max(2, int(2 * s)))
    K.text(img, (x, y + 1), str(n), K.F(K.ANTON, int(24 * s)), (14, 10, 6), "mm", 0)
    return img


def sticker_xy(A, i, sc):
    """On the room's left cut edge, 38 % down from the top: stacked rooms never share a sticker spot."""
    p = room_poly(A, i)
    bl, tl = p[0], p[3]
    t = 0.38
    return tl[0] + (bl[0] - tl[0]) * t - 2 * sc, tl[1] + (bl[1] - tl[1]) * t


def draw_nodes(img, A, st, opts, hover=None, hover_k=0.0, step=None):
    hovering = hover is not None and hover_k > 0.3
    br = G.branch(hover)[0] if hovering else set()
    order = {"grey": 0, "walked": 1, "reach": 2, "target": 3, "option": 4, "current": 5}
    for i in sorted(G.NODES, key=lambda n: (order[st[n]], G.LAYER[n], G.K[n])):
        poly = room_poly(A, i)
        if not poly or not on_screen(poly, 120):
            continue
        s = st[i]
        kind = G.KIND[i]
        sc = room_scale(A, i)
        ks = min(1.9, max(0.75, sc * 0.8))
        if kind != "target":
            col = S.STATE_COL[s]
            w = 4 if s in ("option", "current") else 2
            w = max(w, int(round(w * min(1.6, sc * 0.7))))
            al = {"grey": 0.35, "reach": 0.8}.get(s, 1.0)
            if hovering and s in ("reach", "option") and i not in br:
                al *= S.MIX_A
            if step and s == "option" and i != step[1]:
                al *= 0.5
            img = S.frame_poly(img, poly, col, w, al, glow=s in ("option", "current") or (i == hover and hovering))
        px = STK_PX["target" if kind == "target" else ("start" if kind == "start" else s)]
        px = int(px * ks)
        x, y = sticker_xy(A, i, ks)
        if kind == "target":
            x = sum(p[0] for p in poly) / 4
            y = sum(p[1] for p in poly) / 4 - 4
        grey = s == "grey"
        alpha = S.GREY_A + 0.14 if grey else 1.0
        if hovering and s in ("reach", "option") and i not in br:
            alpha = S.MIX_A + 0.15
        if step and s == "option" and i != step[1]:
            alpha *= 0.55
        lift = 0.55 if (i == hover and hovering) else (0.25 if s == "option" else 0.0)
        yy = y - (5 * ks if (i == hover and hovering) else 0)
        img = S.sticker(img, kind, x, yy, px, grey=grey, alpha=alpha, hover=lift)
        if kind != "target":
            w = 5 if s in ("option", "current") else 3
            img = S.ring(img, x, yy, px / 2 + 6 * ks, S.STATE_COL[s], max(w, int(w * ks * 0.8)), alpha)
        if s == "option":
            n = opts.index(i) + 1
            img = number_chip(img, x - px / 2 - 20 * ks, y - px * 0.32, n, s=ks, col=S.ORANGE)
    return img


def target_mark(img, A):
    poly = room_poly(A, "L7_0")
    if not poly or not on_screen(poly, 0):
        return img
    cx = sum(p[0] for p in poly) / 4
    cy = sum(p[1] for p in poly) / 4
    rx = math.hypot(poly[1][0] - poly[0][0], poly[1][1] - poly[0][1]) / 2 + 6
    ry = abs(poly[0][1] - poly[3][1]) / 2 + 20
    word = (min(cx - rx - 30, W - 230), max(140, cy - ry - 26))
    pr = S.target_pencil(cx, cy, rx, ry, word)
    return S.finish_pencil(img, pr)


def token_at(img, A, i, k):
    p = room_poly(A, i)
    if not p:
        return img
    sc = min(1.8, room_scale(A, i))
    return S.token(img, p[1][0] - 30 * sc, p[1][1] - 26 * sc, px=int(44 * max(0.9, min(1.6, sc * 0.8))))


def view_toggle(img, zoom):
    """DECISION / OVERVIEW toggle right of the legend; Z, the button or the scroll wheel switch it."""
    box = (1612, 1030, 1904, 1070)
    img = KT.term(img, box, None, accent=K.CYAN, header=False, seed=35, chamfer=10)
    d = K.BD(img)
    f = K.F(K.MONO, 15)
    on = 0 if zoom < 0.5 else 1
    segs = [("DECISION", 1622, 1736), ("OVERVIEW", 1740, 1854)]
    for k, (lab, a, b) in enumerate(segs):
        if k == on:
            d.rectangle((a, 1036, b, 1064), fill=(212, 255, 0, 235))
            K.text(img, ((a + b) / 2, 1050), lab, f, (12, 14, 6), "mm", 0)
        else:
            K.text(img, ((a + b) / 2, 1050), lab, f, (150, 190, 205), "mm", 0.4)
    K.text(img, (1880, 1050), "Z", K.F(K.MONO, 13), K.CYAN, "mm", 0.6)
    return img


# ---------------------------------------------------------------- one frame
def frame(plate, A, state):
    walked = state["walked"]
    hover = state.get("hover")
    hk = state.get("hover_k", 1.0 if hover else 0.0)
    zoom = state.get("zoom", 0.0)
    step = state.get("step")
    st, opts = G.states(walked)
    est = G.edge_states(walked, st)
    cur = walked[-1]
    img = plate.convert("RGBA")
    img = grade(img, A, st, cur, hover if hk > 0 else None, hk, focus=1.0 - zoom)
    k = min(1.6, max(0.8, room_scale(A, cur) * 0.62))
    img, tok = draw_cables(img, A, est, cur, hover=hover, hover_k=hk, step=step, k=k)
    img = draw_nodes(img, A, st, opts, hover=hover, hover_k=hk, step=step)
    img = target_mark(img, A)
    if tok:
        img = S.token(img, tok[0], tok[1] - 20 * k, px=int(46 * max(0.9, min(1.5, k))))
    else:
        img = token_at(img, A, cur, k)
    if hover and hk > 0.5:
        p = room_poly(A, hover)
        ks = min(1.9, max(0.75, room_scale(A, hover) * 0.8))
        x, y = sticker_xy(A, hover, ks)
        tl = p[3]
        img = S.tag(img, tl[0] + 8 * ks, tl[1] - 20 * ks, hover, "option")
    key = "start" if len(walked) == 1 else ("end" if len(walked) >= 7 else DISPATCH.get(cur) and cur or "mid")
    img = S.chrome_top(img, DISPATCH[key])
    img = S.sidebar(img, len(opts), hover=hover if (hover and hk > 0.5) else None)
    img = S.legend(img, hot=False, cx=1010)
    img = view_toggle(img, zoom)
    if hover and hk > 0.5:
        p = room_poly(A, hover)
        cx = sum(q[0] for q in p) / 4
        cy = sum(q[1] for q in p) / 4
        img = S.cursor(img, cx + 6, cy + 2)
    return img


def save(img, path):
    from r31lib import bloom
    img = bloom(img, 0.10, 0.84, 8)
    img.convert("RGB").save(path)
    return img


def stills(names=None):
    st = R.stills()
    for name in names or list(st):
        A = json.load(open(os.path.join(SCR, "bl", "anchors_%s.json" % name)))
        plate = Image.open(os.path.join(SCR, "plate_%s.png" % name))
        img = frame(plate, A, st[name][1])
        save(img, os.path.join(ROOT, "%s.png" % name))
        print("saved", name, flush=True)


def one_frame(k):
    fr, _ = R.timeline()
    name = "v%03d" % k
    bl = os.path.join(SCR, "blv")
    out = os.path.join(SCR, "fr", "f%03d.png" % k)
    if os.path.exists(out):
        return k
    import post3
    plate = post3.finish(name, bl, t=k / R.FPS, rain_n=2200)
    A = json.load(open(os.path.join(bl, "anchors_%s.json" % name)))
    img = frame(plate, A, fr[k][1])
    save(img, out)
    return k


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "stills":
        stills(sys.argv[2:] or None)
    elif what == "frames":
        from multiprocessing import Pool
        fr, _ = R.timeline()
        a = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        b = int(sys.argv[3]) if len(sys.argv) > 3 else len(fr)
        os.makedirs(os.path.join(SCR, "fr"), exist_ok=True)
        with Pool(5) as pool:
            for k in pool.imap_unordered(one_frame, range(a, b)):
                print("frame", k, flush=True)
