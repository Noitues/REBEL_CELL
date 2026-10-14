"""Side view: compose V1 / V2 / V3 (start, mid, hover, step GIF) on the finished plates + the locked overlay media.

python compose.py [V1|V2|V3|all] [stills|gif|both]
  V1 "Cutaway street": the night side elevation (plate_side); route floors cut open; lit cables + skybridges.
  V2 "Section drawing": the same passes restyled as a corp schematic section plate (hatched cut walls, blueprint
     ground); rooms keep their light; the plan is yellow grease pencil (solid = the step, dashed = what-if).
  V3 "Dollhouse dolly": the 3/4 perspective street (plate_tq); hover = power cut + the branch's rooms bloom;
     the step GIF dollies the camera with the token.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import json  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance  # noqa: E402

import sidekit as S  # noqa: E402
import sgraph as G  # noqa: E402
import ui31 as K  # noqa: E402
import kit44 as KT  # noqa: E402

OUT = S.OUT
SCR = S.SCR
W, H = 1920, 1080
DISPATCH = {"start": "Jacked in at the relay. Three floors of Lane 15 are open. The Rack is at the end of the street.",
            "mid": "Shop's behind you. Two ways left: the long way has a Rack."}
STK_PX = {"option": 48, "current": 44, "walked": 36, "reach": 40, "grey": 34, "target": 62, "start": 42}
TAGS = {"V1": "side", "V2": "side", "V3": "tq"}
_cache = {}


def anchors(tag):
    if tag not in _cache:
        _cache[tag] = json.load(open(os.path.join(SCR, "bl", "anchors_%s.json" % tag)))
    return _cache[tag]


def f2a(img):
    return np.asarray(img.convert("RGB"), np.float32) / 255.0


def a2f(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")


def poly_mask(poly, grow=0, blur=0):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in poly], fill=255)
    if grow:
        m = m.filter(ImageFilter.MaxFilter(grow * 2 + 1))
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(m, np.float32) / 255.0


def room_poly(A, i):
    return A["rooms"][i]["front"]


def lum(a):
    return a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11


# ---------------------------------------------------------------- V2 base: the section plate
def section_plate():
    if "section" in _cache:
        return _cache["section"].copy()
    plate = f2a(Image.open(os.path.join(SCR, "plate_side.png")))
    sem = np.asarray(Image.open(os.path.join(SCR, "sem_side.png")).convert("RGB"), np.float32)
    cls = sem[..., 0]
    near = lambda v: np.abs(cls - v * 255) < 9  # noqa: E731
    sky = cls < 12
    fac, gnd, cut, room, link, far = near(0.1), near(0.2), near(0.3), near(0.5), near(0.7), near(0.85)
    yy, xx = np.mgrid[0:H, 0:W]
    navy = np.array((0.03, 0.06, 0.15), np.float32)
    img = np.broadcast_to(navy, (H, W, 3)).copy()
    grid = ((xx % 40 == 0) | (yy % 40 == 0)).astype(np.float32) * 0.06 + ((xx % 200 == 0) | (yy % 200 == 0)) * 0.08
    cyan = np.array((0.36, 0.88, 1.0), np.float32)
    img = img + cyan * grid[..., None]
    # far city: faint schematic silhouettes
    img = np.where(far[..., None], np.array((0.05, 0.09, 0.2), np.float32) + lum(plate)[..., None] * 0.12 * cyan, img)
    # facades: dark section fill; windows kept as a cool trace of the plate
    fill = np.array((0.06, 0.07, 0.15), np.float32)
    img = np.where(fac[..., None], fill + np.clip(lum(plate) - 0.25, 0, 1)[..., None] * 0.55 * np.array((0.6, 0.8, 1.0)), img)
    # cut walls + slabs: poche with a 45 deg hatch
    hatch = (((xx + yy) % 7) < 2).astype(np.float32)
    poche = np.array((0.13, 0.12, 0.24), np.float32)
    img = np.where(cut[..., None], poche + hatch[..., None] * 0.42 * cyan, img)
    # the ground section: cross hatch (earth), the conduit keeps its glow
    xh = ((((xx + yy) % 12) < 1) | (((xx - yy) % 12) < 1)).astype(np.float32)
    img = np.where(gnd[..., None], np.array((0.05, 0.06, 0.13), np.float32) + xh[..., None] * 0.28 * cyan
                   + np.clip(plate - 0.35, 0, 1) * 0.8, img)
    img = np.where(link[..., None], np.array((0.16, 0.3, 0.42), np.float32), img)
    img = np.where(room[..., None], plate * 1.08, img)
    # schematic ink: id / normal edges from the 2880 passes, drawn cyan (dark ink stays inside the rooms)
    ids = np.asarray(Image.open(os.path.join(SCR, "bl", "side_id.png")).convert("RGB"), np.float32) / 255
    e = np.zeros(ids.shape[:2], np.float32)
    for dy, dx in ((0, 1), (1, 0)):
        d = np.abs(ids - np.roll(np.roll(ids, -dy, 0), -dx, 1)).sum(axis=2)
        e = np.maximum(e, (d > 0.03).astype(np.float32))
    e = np.asarray(Image.fromarray((e * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).resize((W, H), Image.LANCZOS),
                   np.float32) / 255
    e = np.where(room | sky, 0, e) * np.where(far, 0.35, 0.8)
    img = img * (1 - e[..., None]) + cyan * e[..., None]
    _cache["section"] = a2f(img)
    return _cache["section"].copy()


def section_notes(img):
    """Schematic annotation: level ruler, column grid bubbles (S, 1..6, T), section title."""
    d = ImageDraw.Draw(img)
    f = K.F(K.MONO, 13)
    cy = (92, 225, 255)
    x = 302
    for lv in range(0, 11):
        y = G.GROUND_Y - lv * G.FLOOR_H * G.PX
        d.line([(x, y), (x + 10, y)], fill=cy + (200,), width=2)
        K.text(img, (x + 14, y), "+%02d" % lv, f, cy, "lm", 0.3)
    d.line([(x, G.GROUND_Y), (x, G.GROUND_Y - 10 * G.FLOOR_H * G.PX)], fill=cy + (140,), width=1)
    for l in range(8):
        x0, x1 = G.col_x(l)
        cx = (x0 + x1) / 2 * G.PX
        y = 972
        d.line([(cx, G.GROUND_Y + 4), (cx, y - 14)], fill=cy + (110,), width=1)
        d.ellipse([cx - 14, y - 14, cx + 14, y + 14], outline=cy + (230,), width=2, fill=(5, 13, 28, 220))
        K.text(img, (cx, y + 1), "T" if l == 7 else str(l), K.F(K.MONO, 15), cy, "mm", 0)
    K.text(img, (372, 140), "SECTION A-A  //  LANE 15  //  RELAY_4 > DEPOT_15", K.F(K.MONO, 14), cy, "lm", 0.6)
    K.text(img, (372, 160), "MERIDIAN FREIGHT  //  SCHEMATIC 1:200  //  GRID = STEP, LEVEL = FLOOR", K.F(K.MONO, 12), (120, 170, 200), "lm", 0.6)
    return img


# ---------------------------------------------------------------- world layer
def base(variant):
    if variant == "V2":
        return section_plate()
    key = "plate_" + TAGS[variant]
    if key not in _cache:
        _cache[key] = Image.open(os.path.join(SCR, key + ".png")).convert("RGBA")
    return _cache[key].copy()


def grade(img, A, st, hover, variant, cut_k=0.0, cur=None):
    """Room light by state; hover blooms the branch. cut_k: V3 power cut (0..1) outside the branch."""
    a = f2a(img)
    br = G.branch(hover)[0] if hover else set()
    out = a.copy()
    if cut_k > 0:
        keep = np.zeros((H, W), np.float32)
        for i in sorted(br | ({cur} if cur else set())):
            keep = np.maximum(keep, poly_mask(room_poly(A, i), grow=6, blur=6))
        l3 = lum(a)[..., None]
        dim = (a * 0.6 + l3 * 0.4) * (1 - 0.68 * cut_k)
        out = a * keep[..., None] + dim * (1 - keep[..., None])
    for i in G.NODES:
        s = st[i]
        m = poly_mask(room_poly(A, i), grow=1)[..., None]
        r = out
        l3 = lum(r)[..., None]
        if s == "grey":
            ghost = np.array((0.06, 0.05, 0.11), np.float32)
            v = (l3 * 0.55) * 0.45 + ghost * 0.55
        elif s == "walked":
            v = (r * 0.5 + l3 * 0.5) * 0.55
        elif hover and i in br:
            v = r * 1.45
        elif hover and s in ("reach", "option") and i not in br:
            v = (r * 0.6 + l3 * 0.4) * (0.55 if variant != "V3" else 0.7)
        elif s == "option":
            v = r * 1.18
        else:
            v = r
        out = out * (1 - m) + v * m
    img = a2f(out)
    if hover:
        for i in sorted(br, key=lambda n: (G.LAYER[n], G.K[n])):
            m = Image.fromarray((poly_mask(room_poly(A, i)) * 255).astype(np.uint8))
            img = K.add_glow(img, m, S.TYPE_COL[G.KIND[i]], 26, 0.55)
    return img


def cable_style(es, hover_edge=False, in_branch=False, hover=False):
    if es == "walked":
        return ("solid", S.LIME, 7, 255, 200)
    if hover_edge:
        return ("solid", S.ORANGE, 8, 255, 230)
    if es == "option":
        return ("dashed", S.ORANGE, 8, 255 if not hover else 150, 160 if not hover else 0)
    if es == "future":
        if in_branch:
            return ("solid", S.WHITE, 5, 245, 150)
        return ("dashed", S.WHITE, 5, 235 if not hover else 130, 0)
    return ("solid", S.GREY, 4, int(255 * S.GREY_A), 0)


def draw_cables(img, A, est, hover=None, variant="V1", walk_partial=None, cur=None):
    br_e = G.branch(hover)[1] if hover else set()
    cab = S.Cables()
    order = {"grey": 0, "future": 1, "option": 2, "walked": 3}
    edges = sorted(A["edges"], key=lambda e: (order[est[(e["a"], e["b"])]], e["a"], e["b"]))
    for e in edges:
        key = (e["a"], e["b"])
        es = est[key]
        pts = [tuple(p) for p in e["pts"]]
        hov_edge = hover is not None and e["b"] == hover and e["a"] == cur
        kind, col, w, a, gl = cable_style(es, hov_edge, key in br_e, hover is not None)
        if variant == "V2" and es in ("future", "option") and not hov_edge:
            w = max(3, w - 2)
        if kind == "solid":
            cab.solid(pts, col, w, casing=3 if es != "grey" else 0, a=a, glow=gl)
        else:
            cab.dashed(pts, col, w, on=18 if es == "option" else 12, off=9, casing=3, a=a, glow=gl)
    if walk_partial:
        pts, t = walk_partial
        part, q = S.cut_poly(pts, t)
        if len(part) > 1:
            cab.solid(part, S.LIME, 7, casing=3, a=255, glow=220)
    return cab.comp(img, glow_col=(255, 200, 120))


def sticker_pos(A, i, scale):
    p = room_poly(A, i)
    tl = p[3]
    return tl[0] - 2 * scale, tl[1] - 6 * scale


def room_scale(A, i):
    p = room_poly(A, i)
    return max(0.6, (p[1][0] - p[0][0]) / 116.0)


def draw_nodes(img, A, st, opts, hover=None, variant="V1", numbers=True, extra_alpha=None):
    br = G.branch(hover)[0] if hover else set()
    order = {"grey": 0, "walked": 1, "reach": 2, "target": 3, "option": 4, "current": 5}
    for i in sorted(G.NODES, key=lambda n: (order[st[n]], G.LAYER[n], G.K[n])):
        s = st[i]
        kind = G.KIND[i]
        sc = room_scale(A, i)
        poly = room_poly(A, i)
        # the room's cut edge in its state colour
        if kind != "target":
            col = S.STATE_COL[s]
            w = 4 if s in ("option", "current") else 2
            al = {"grey": 0.35, "reach": 0.8}.get(s, 1.0)
            if hover and s in ("reach", "option") and i not in br:
                al *= S.MIX_A
            img = S.frame_poly(img, poly, col, w, al, glow=s in ("option", "current") or (i == hover))
        px = STK_PX["target" if kind == "target" else ("start" if kind == "start" else s)]
        px = int(px * min(1.25, sc))
        x, y = sticker_pos(A, i, sc)
        if kind == "target":
            cx = sum(p[0] for p in poly) / 4
            cy = sum(p[1] for p in poly) / 4
            x, y = cx, cy - 4
        grey = s == "grey"
        alpha = S.GREY_A + 0.14 if grey else 1.0
        if hover and s in ("reach", "option") and i not in br:
            alpha = S.MIX_A + 0.15
        if extra_alpha and i in extra_alpha:
            alpha *= extra_alpha[i]
        lift = 0.55 if i == hover else (0.25 if s == "option" else 0.0)
        img = S.sticker(img, kind, x, y - (5 if i == hover else 0), px, grey=grey, alpha=alpha, hover=lift)
        if kind != "target":
            w = 5 if s in ("option", "current") else 3
            img = S.ring(img, x, y - (5 if i == hover else 0), px / 2 + 6, S.STATE_COL[s], w, alpha)
        if numbers and s == "option":
            n = opts.index(i) + 1
            img = S.number_chip(img, x - px / 2 - 4, y - px / 2 - 14, n)
    return img


def target_mark(img, A):
    poly = room_poly(A, "L7_0")
    cx = sum(p[0] for p in poly) / 4
    cy = sum(p[1] for p in poly) / 4
    rx = (poly[1][0] - poly[0][0]) / 2 + 4
    ry = (poly[0][1] - poly[3][1]) / 2 + 20
    pr = S.target_pencil(cx, cy, rx, ry, (cx - rx - 30, cy - ry - 26))
    return S.finish_pencil(img, pr)


def token_at(img, A, i, pos=None):
    if pos is None:
        p = room_poly(A, i)
        sc = room_scale(A, i)
        pos = (p[1][0] - 30 * sc, p[1][1] - 26 * sc)
    return S.token(img, pos[0], pos[1], px=int(44 * min(1.2, room_scale(A, i))))


def pencil_plan(img, A, walked, hover):
    """V2: the plan in yellow wax. Solid = the step CONFIRM will take; dashed = the what-if branch behind it."""
    cur = walked[-1]
    pen = KT.pencil(S.PEN_Y, 517)
    br_n, br_e = G.branch(hover)
    for e in A["edges"]:
        key = (e["a"], e["b"])
        pts = [(x, y - 7) for x, y in e["pts"]]
        if e["a"] == cur and e["b"] == hover:
            pen.stroke(pts, width=9)
        elif key in br_e:
            # dashed what-if: short wax dashes along the link
            L = S.poly_len(pts)
            s = 0.0
            while s < L:
                a_, _ = S.cut_poly(pts, s / L)
                b_, _ = S.cut_poly(pts, min(1, (s + 24) / L))
                seg = b_[len(a_) - 1:]
                if len(seg) > 1:
                    pen.stroke(seg, width=7, taper=False)
                s += 38
    p = room_poly(A, hover)
    cx = sum(q[0] for q in p) / 4
    cy = sum(q[1] for q in p) / 4
    pen.circle(cx, cy, (p[1][0] - p[0][0]) / 2 + 14, (p[0][1] - p[3][1]) / 2 + 14, width=7)
    return S.finish_pencil(img, pen, S.PEN_Y)


# ---------------------------------------------------------------- a whole frame
def frame(variant, walked, hover=None, step=None, cam=None):
    """step: (edge pts, t, next_walked or None) for the GIF. cam: (zoom, cx, cy) for the V3 dolly crop."""
    tag = TAGS[variant]
    A = anchors(tag)
    st, opts = G.states(walked)
    est = G.edge_states(walked, st)
    cur = walked[-1]
    img = base(variant)
    cut = 1.0 if (variant == "V3" and hover) else 0.0
    img = grade(img, A, st, hover, variant, cut_k=cut, cur=cur)
    if variant == "V2":
        img = section_notes(img)
    walk_partial = None
    tok = None
    if step:
        pts, t = step
        walk_partial = (pts, t)
        _, tok = S.cut_poly(pts, t)
    img = draw_cables(img, A, est, hover=hover, variant=variant, walk_partial=walk_partial, cur=cur)
    img = draw_nodes(img, A, st, opts, hover=hover, variant=variant)
    img = target_mark(img, A)
    if variant == "V2" and hover:
        img = pencil_plan(img, A, walked, hover)
    if tok:
        img = S.token(img, tok[0], tok[1] - 20, px=46)
    else:
        img = token_at(img, A, cur)
    if hover:
        p = room_poly(A, hover)
        sc = room_scale(A, hover)
        x, y = sticker_pos(A, hover, sc)
        img = S.tag(img, x + 30 * sc, y - 22 * sc, hover, "option")
    if cam:
        z, cx, cy = cam
        w2, h2 = W / z, H / z
        x0 = min(max(0, cx - w2 / 2), W - w2)
        y0 = min(max(0, cy - h2 / 2), H - h2)
        img = img.crop((int(x0), int(y0), int(x0 + w2), int(y0 + h2))).resize((W, H), Image.LANCZOS)
    # chrome
    key = "mid" if len(walked) > 1 else "start"
    img = S.chrome_top(img, DISPATCH[key])
    img = S.sidebar(img, len(opts), hover=hover)
    img = S.legend(img, hot=False)
    if hover:
        p = room_poly(A, hover)
        cx = sum(q[0] for q in p) / 4
        cy = sum(q[1] for q in p) / 4
        img = S.cursor(img, cx + 6, cy + 2)
    return img


def stills(variant):
    for name, walked, hover in (("start", G.WALK_START, None), ("mid", G.WALK_MID, None), ("hover", G.WALK_MID, G.HOVER_MID)):
        img = frame(variant, walked, hover)
        S.save(img, os.path.join(OUT, "%s_%s.png" % (variant, name)))


def ease(t):
    return t * t * (3 - 2 * t)


def gif(variant):
    A = anchors(TAGS[variant])
    walked = G.WALK_MID
    nxt = G.HOVER_MID
    e = next(e for e in A["edges"] if e["a"] == walked[-1] and e["b"] == nxt)
    pts = [tuple(p) for p in e["pts"]]
    frames, durs = [], []
    n_move = 12
    p0 = room_poly(A, walked[-1])
    start_tok = (p0[1][0] - 30, p0[1][1] - 26)
    pts_full = [start_tok] + pts
    for k in range(3):                       # CONFIRM pressed: the picked option holds
        frames.append(frame(variant, walked, hover=nxt if k < 2 else None, step=(pts_full, 0.0) if k == 2 else None,
                            cam=_cam(variant, A, pts_full, 0.0)))
        durs.append(90)
    for k in range(n_move):
        t = ease((k + 1) / n_move)
        frames.append(frame(variant, walked, step=(pts_full, t), cam=_cam(variant, A, pts_full, t)))
        durs.append(70)
    after = walked + [nxt]
    for k in range(4):
        frames.append(frame(variant, after, cam=_cam(variant, A, pts_full, 1.0)))
        durs.append(90 if k < 3 else 700)
    small = [f.convert("RGB").resize((960, 540), Image.LANCZOS) for f in frames]
    S.save_gif(small, durs, os.path.join(OUT, "%s_step.gif" % variant))


def _cam(variant, A, pts, t):
    if variant != "V3":
        return None
    _, q = S.cut_poly(pts, t)
    z = 1.0 + 0.22 * math.sin(math.pi * min(1, max(0, t)) * 0.5 + 0.0) if t > 0 else 1.0
    z = 1.0 + 0.22 * ease(min(1.0, t * 1.6)) if t > 0 else 1.0
    return (z, q[0] + 120, q[1] - 40)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    what = sys.argv[2] if len(sys.argv) > 2 else "both"
    for v in (["V1", "V2", "V3"] if which == "all" else [which]):
        if what in ("stills", "both"):
            stills(v)
        if what in ("gif", "both"):
            gif(v)
