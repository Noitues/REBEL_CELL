"""HQ kit overlay: anchors from the pose and the locked route grammar on top (drawn at 1920 x 1080), generalised from
hq_halcyon/scripts/hq_overlay.py. The corp's mechanic language lives in hq_mechui.py (MU):
  MU.node_mark(i, state, mech)        -> None | dict(ring=rgb, badge=fn(px)->RGBA, chip=(text, rgb), scan=rgb)
  MU.marks(img, A, ov, mech, pose)    -> img   (telegraphs: pencil rings, link chips, 3D-anchored labels)
  MU.dial(img, x, y, mech, ov)        -> img   (the mechanic's HUD dial, top right)
  MU.rule_note(i, walked, mech)       -> (text, rgb) | None   (the hover note)
  MU.DISPATCH {node: line}, MU.legend_items() -> [(fn(px), label)]
Locked grammar (r3 / V3 dynamic, unchanged): vinyl stickers on each room's cut edge, state rings (lime walked /
current, orange option + number, white ahead, grey past), wax grease-pencil links, the red pencil TARGET, the token.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import hq_cam as CR  # noqa: E402
import hq_graph as G  # noqa: E402
import hq_preset as HP  # noqa: E402
import sidekit as S  # noqa: E402
import ui31 as K  # noqa: E402
import kit44 as KT  # noqa: E402
import hq_mechui as MU  # noqa: E402
from hq_kit import states as ST  # noqa: E402

W, H = 1920, 1080
RED, GOLD = ST.RED, ST.GOLD
STK_PX = {"option": 48, "current": 44, "walked": 36, "reach": 40, "grey": 34, "target": 62, "start": 42}
HZ = HP.PRESET["hq"]
pose_of = CR.pose_of


def _front_srv(i, pose, mt):
    """A room open all round (normal None): its opening is the side facing the camera."""
    r = G.room_rec(i, mt)
    c = pose.loc()
    o = r["o"]
    d = (c[0] - o[0], c[1] - o[1])
    n = max(((0.0, 1.0), (1.0, 0.0), (0.0, -1.0), (-1.0, 0.0)), key=lambda v: v[0] * d[0] + v[1] * d[1])
    t = (n[1], -n[0])
    hw = r["w"] / 2
    z0, z1 = o[2], o[2] + r["h"]
    cx, cy = o[0], o[1]
    return [(cx - t[0] * hw, cy - t[1] * hw, z0), (cx + t[0] * hw, cy + t[1] * hw, z0),
            (cx + t[0] * hw, cy + t[1] * hw, z1), (cx - t[0] * hw, cy - t[1] * hw, z1)]


def anchors(pose, walked, mt=None):
    mt = (len(walked) - 1) if mt is None else mt
    A = {"rooms": {}, "edges": [], "mt": mt}
    for i in G.NODES:
        r = G.room_rec(i, mt)
        if r["n"] is None:
            pts, vis = _front_srv(i, pose, mt), True
        else:
            pts, vis = G.room_front(i, mt), CR.visible_room(i, pose, mt, -0.2 if i == "start" else 0.12)
        q = [pose.proj(p) for p in pts]
        if any(v is None for v in q):
            A["rooms"][i] = dict(front=None, vis=False)
            continue
        b0, b1, t1, t0 = q
        if b1[0] < b0[0]:
            b0, b1, t1, t0 = b1, b0, t0, t1
        A["rooms"][i] = dict(front=[b0, b1, t1, t0], vis=vis)
    for a, b in G.edges(walked, int(mt)):
        path = G.edge_path(a, b, mt)
        pts = [pose.proj(p) for p in path]
        vis = []
        for k in range(len(path) - 1):
            mid = [(path[k][j] + path[k + 1][j]) / 2 for j in range(3)]
            n = G.seg_normal(mid)
            vis.append(CR.visible_n(n, mid, pose, -0.05))
        A["edges"].append(dict(a=a, b=b, pts=pts, vis=vis, type=G.edge_type(a, b)))
    return A


def room_poly(A, i):
    r = A["rooms"].get(i)
    if not r or not r["front"] or not r["vis"]:
        return None
    return r["front"]


def room_scale(A, i):
    p = room_poly(A, i)
    if not p:
        return 1.0
    return max(0.5, math.hypot(p[1][0] - p[0][0], p[1][1] - p[0][1]) / 116.0)


def sticker_xy(A, i, sc):
    p = room_poly(A, i)
    bl, tl = p[0], p[3]
    t = 0.38
    return tl[0] + (bl[0] - tl[0]) * t - 2 * sc, tl[1] + (bl[1] - tl[1]) * t


def on_screen(p, m=40):
    return p and any(-m < q[0] < W + m and -m < q[1] < H + m for q in p)


def poly_mask(poly, grow=0, blur=0, size=(W, H), s=1.0):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon([(x * s, y * s) for x, y in poly], fill=255)
    if grow:
        m = m.filter(ImageFilter.MaxFilter(grow * 2 + 1))
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(m, np.float32) / 255.0


def lum(a):
    return a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11


def grade(plate, A, st, cur, hover, walked, focus=1.0):
    W2, H2 = plate.size
    s = W2 / W
    out = np.asarray(plate.convert("RGB"), np.float32) / 255.0
    dm = Image.new("L", (W2, H2), 0)
    dd = ImageDraw.Draw(dm)
    for e in A["edges"]:
        pts = [(q[0] * s, q[1] * s) for q in e["pts"] if q is not None]
        if len(pts) > 1:
            dd.line(pts, fill=255, width=int(10 * s))
    dm = np.asarray(dm.filter(ImageFilter.GaussianBlur(24 * s)), np.float32) / 255.0
    out = out * (1 - 0.2 * np.clip(dm * 2.0, 0, 1))[..., None]
    if focus > 0:
        yy, xx = np.mgrid[0:H2, 0:W2].astype(np.float32)
        d = np.sqrt(((xx - CR.UCX * s) / (W2 * 0.62)) ** 2 + ((yy - CR.UCY * s) / (H2 * 0.62)) ** 2)
        out = out * (1 - 0.18 * np.clip(d - 0.55, 0, 1)[..., None] * focus)
    mt = A.get("mt")
    if hover:
        br = G.branch(hover, walked, int(mt))[0]
        keep = np.zeros((H2, W2), np.float32)
        for i in sorted(br | {cur}, key=lambda n: G.ORDER[n]):
            p = room_poly(A, i)
            if p:
                keep = np.maximum(keep, poly_mask(p, 8, 8, (W2, H2), s))
        l3 = lum(out)[..., None]
        out = out * keep[..., None] + (out * 0.75 + l3 * 0.25) * 0.62 * (1 - keep[..., None])
    for i in G.NODES:
        p = room_poly(A, i)
        if not p:
            continue
        m = poly_mask(p, 1, 0, (W2, H2), s)[..., None]
        l3 = lum(out)[..., None]
        if st[i] == "grey":
            v = (l3 * 0.55) * 0.5 + np.array((0.06, 0.05, 0.11), np.float32) * 0.5
        elif st[i] == "walked":
            v = (out * 0.55 + l3 * 0.45) * 0.7
        else:
            v = out
        out = out * (1 - m) + v * m
    img = Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    if hover:
        for i in sorted(G.branch(hover, walked, int(mt))[0], key=lambda n: G.ORDER[n]):
            p = room_poly(A, i)
            if p:
                m = Image.fromarray((poly_mask(p, 0, 0, (W2, H2), s) * 255).astype(np.uint8))
                img = K.add_glow(img, m, S.TYPE_COL[G.KIND[i]], int(30 * s), 0.5)
    return img


def number_chip(img, x, y, n, s=1.0, col=S.ORANGE):
    hw, hh = 15 * s, 16 * s
    box = (x - hw, y - hh, x + hw, y + hh)
    img = KT.panel_shadow(img, box, 0, blur=6, k=0.55, off=(0, 3))
    d = K.BD(img)
    d.rectangle(box, fill=col + (255,), outline=(10, 8, 14, 255), width=max(2, int(2 * s)))
    K.text(img, (x, y + 1), str(n), K.F(K.ANTON, int(24 * s)), (14, 10, 6), "mm", 0)
    return img


def draw_nodes(img, A, st, opts, mech, hover=None, hover_k=0.0, ghosts=False, phase=0.0, walked=None):
    hovering = hover is not None and hover_k > 0.3
    mt = A.get("mt")
    br = G.branch(hover, walked, int(mt))[0] if hovering else set()
    order = {"grey": 0, "walked": 1, "reach": 2, "target": 3, "option": 4, "current": 5}
    for i in sorted(G.NODES, key=lambda n: (order[st[n]], G.ORDER[n])):
        r = A["rooms"].get(i)
        if not r or not r["front"]:
            continue
        poly = r["front"]
        if not on_screen(poly, 120):
            continue
        s = st[i]
        kind = G.KIND[i]
        mk = MU.node_mark(i, s, mech) or {}
        if not r["vis"]:
            if ghosts and s != "grey":
                cx = sum(q[0] for q in poly) / 4
                cy = sum(q[1] for q in poly) / 4
                img = S.ring(img, cx, cy, 14, S.STATE_COL[s] if kind != "target" else RED, 3, 0.35)
            continue
        sc = room_scale(A, i)
        ks = min(1.9, max(0.75, sc * 0.8))
        if kind != "target":
            col = mk.get("ring") or S.STATE_COL[s]
            w = 4 if s in ("option", "current") else 2
            w = max(w, int(round(w * min(1.6, sc * 0.7))))
            al = {"grey": 0.35, "reach": 0.8}.get(s, 1.0)
            if hovering and s in ("reach", "option") and i not in br:
                al *= S.MIX_A
            img = S.frame_poly(img, poly, col, w, al, glow=s in ("option", "current") or bool(mk.get("ring")))
            if mk.get("scan"):
                img = ST.scan_lines(img, poly, 0.8 if s == "option" else 0.55, phase, (W, H))
        px = int(STK_PX["target" if kind == "target" else ("start" if kind == "start" else s)] * ks)
        x, y = sticker_xy(A, i, ks)
        if kind == "target":
            x = sum(q[0] for q in poly) / 4
            y = sum(q[1] for q in poly) / 4 - 4
        grey = s == "grey"
        alpha = S.GREY_A + 0.14 if grey else 1.0
        if hovering and s in ("reach", "option") and i not in br:
            alpha = S.MIX_A + 0.15
        lift = 0.55 if (i == hover and hovering) else (0.25 if s == "option" else 0.0)
        yy = y - (5 * ks if (i == hover and hovering) else 0)
        if mk.get("sticker_fn"):
            img = mk["sticker_fn"](img, x, yy, px, alpha)          # the mechanic hides the room's kind (e.g. unread)
        else:
            img = S.sticker(img, kind, x, yy, px, grey=grey, alpha=alpha, hover=lift)
        if kind != "target":
            rc = mk.get("ring") or S.STATE_COL[s]
            w = 5 if s in ("option", "current") else 3
            img = S.ring(img, x, yy, px / 2 + 6 * ks, rc, max(w, int(w * ks * 0.8)), alpha)
        if mk.get("badge") and s not in ("grey",):
            b = mk["badge"](int(px * 0.56))
            img.alpha_composite(b, (int(x + px * 0.16), int(yy - px * 0.66)))
        if s == "option":
            n = opts.index(i) + 1
            img = number_chip(img, x - px / 2 - 20 * ks, y - px * 0.32, n, s=ks, col=S.ORANGE)
        if mk.get("chip") and s in ("option", "current", "reach"):
            txt, cc = mk["chip"]
            cxy = (poly[3][0] + 6 * ks, poly[3][1] - 18 * ks) if mk.get("chip_at") != "below" else                 ((poly[0][0] + poly[1][0]) / 2, max(poly[0][1], poly[1][1]) + 18 * ks)
            img, _ = KT.chip(img, cxy, txt, cc, int(14 * min(1.3, ks)), anchor="lm" if mk.get("chip_at") != "below" else "mm",
                             pad=7)
    return img


def target_mark(img, A):
    poly = room_poly(A, "srv")
    if not poly or not on_screen(poly, 0):
        return img
    cx = sum(p[0] for p in poly) / 4
    cy = sum(p[1] for p in poly) / 4
    rx = math.hypot(poly[1][0] - poly[0][0], poly[1][1] - poly[0][1]) / 2 + 8
    ry = abs(poly[0][1] - poly[3][1]) / 2 + 20
    word = (min(cx + rx + 10, W - 230), max(140, cy - ry - 40))
    pr = S.target_pencil(cx, cy, rx, ry, word)
    img = S.finish_pencil(img, pr)
    img, _ = KT.chip(img, (cx + rx + 12, cy + 6), "CENTRAL SERVER // %s" % HZ["target_name"], (255, 214, 64), 12,
                     anchor="lm", pad=6)
    return img


def token_at(img, A, i, k):
    p = room_poly(A, i)
    if not p:
        return img
    sc = min(1.8, room_scale(A, i))
    return S.token(img, p[1][0] - 30 * sc, p[1][1] - 26 * sc, px=int(44 * max(0.9, min(1.6, sc * 0.8))))


def legend(img, cx=980):
    def ringf(col):
        def f(px):
            im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
            ImageDraw.Draw(im).ellipse([3, 3, px - 4, px - 4], outline=col + (255,), width=3)
            return im
        return f
    import r32ui as U32
    items = [(lambda px, k=k: U32.icon(k, px), lab) for k, lab in (("router", "FIGHT"), ("elite", "ELITE"),
                                                                   ("terminal", "EVENT"), ("modem", "SHOP"))]
    items += [(ringf(S.LIME), "walked"), (ringf(S.ORANGE), "next"), (ringf(S.WHITE), "ahead"), (ringf(S.GREY), "past")]
    items += MU.legend_items()
    img, box = KT.key_strip(img, int(cx - 640), 1030, items, hint="HOVER: SHOW ALL")
    return img


def view_toggle(img, zoom):
    box = (1612, 1030, 1904, 1070)
    img = KT.term(img, box, None, accent=K.CYAN, header=False, seed=35, chamfer=10)
    d = K.BD(img)
    f = K.F(K.MONO, 15)
    on = 0 if zoom > 0.5 else 1
    for k, (lab, a, b) in enumerate([("DECISION", 1622, 1736), ("OVERVIEW", 1740, 1854)]):
        if k == on:
            d.rectangle((a, 1036, b, 1064), fill=(212, 255, 0, 235))
            K.text(img, ((a + b) / 2, 1050), lab, f, (12, 14, 6), "mm", 0)
        else:
            K.text(img, ((a + b) / 2, 1050), lab, f, (150, 190, 205), "mm", 0.4)
    K.text(img, (1880, 1050), "Z", K.F(K.MONO, 13), K.CYAN, "mm", 0.6)
    return img


def overlay(plate, A, ov, ui_k=1.0, phase=0.0):
    """Everything above the world grade, drawn at 1920 x 1080 onto `plate` (RGBA)."""
    import wax_r2 as WX
    walked = ov["walked"]
    hover = ov.get("hover")
    hk = ov.get("hover_k", 0.0)
    zoom = ov.get("zoom", 0.0)
    mt = A.get("mt", len(walked) - 1)
    G.WALK_MID = walked                       # wax_r2 reads G.branch(hover) with the default walk
    if hasattr(G, "set_shot"):
        G.set_shot(ov.get("extra") or {})
    st, opts = G.states(walked, int(mt))
    est = G.edge_states(walked, st, int(mt))
    mech = G.mech(walked, int(mt))
    mech.update(ov.get("extra") or {})
    mech["zoom"] = zoom
    cur = walked[-1]
    img = plate.convert("RGBA")
    ghosts = zoom < 0.5
    k = min(1.6, max(0.8, room_scale(A, cur) * 0.62)) if room_poly(A, cur) else 1.0
    Avis = dict(rooms=A["rooms"], edges=[])
    Aray = dict(rooms=A["rooms"], edges=[])
    for e in A["edges"]:
        segs = list(zip(e["pts"], e["pts"][1:], e["vis"]))
        run, runs = [], []
        for (p, q, v) in segs:
            if p is None or q is None:
                continue
            if run and run[0] != v:
                runs.append(run)
                run = []
            if not run:
                run = [v, [p]]
            run[1].append(q)
        if run:
            runs.append(run)
        for v, pts in runs:
            (Avis if v else Aray)["edges"].append(dict(a=e["a"], b=e["b"], pts=pts))
    rk = ov.get("route", 1.0)
    if rk > 0.01:
        if Aray["edges"]:
            ray = WX.draw_wax(Image.new("RGBA", (W, H), (0, 0, 0, 0)), Aray, est, st, opts, cur, hover=hover, hover_k=hk,
                              k=k * 0.7)
            ray.putalpha(ray.split()[3].point(lambda v: int(v * 0.45)))
            img.alpha_composite(ray)
        img = WX.draw_wax(img, Avis, est, st, opts, cur, hover=hover, hover_k=hk, k=k)
        img = draw_nodes(img, A, st, opts, mech, hover=hover, hover_k=hk, ghosts=ghosts, phase=phase, walked=walked)
        img = MU.marks(img, A, ov, mech, pose_of(ov["pose"]))
        img = target_mark(img, A)
        if not hasattr(G, "RUNNERS"):
            img = token_at(img, A, cur, k)         # several runners: hq_mechui.marks draws a token per lane
        if hover and hk > 0.5:
            p = room_poly(A, hover)
            if p:
                ks = min(1.9, max(0.75, room_scale(A, hover) * 0.8))
                img = S.tag(img, p[3][0] + 8 * ks, p[3][1] - 20 * ks, hover, "option")
    if ui_k <= 0:
        return img
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ui = S.chrome_top(ui, MU.DISPATCH.get(cur, MU.DISPATCH["start"]))
    ui = S.sidebar(ui, len(opts), hover=hover if (hover and hk > 0.5) else None)
    ui = MU.dial(ui, 1630, 10, mech, ov)
    if hover and hk > 0.5:
        rn = MU.rule_note(hover, walked, mech)
        if rn:
            ui, _ = KT.chip(ui, (14, 996), rn[0], rn[1], 13, anchor="lm", pad=8)
    ui = legend(ui)
    ui = view_toggle(ui, zoom)
    if hover and hk > 0.5:
        p = room_poly(A, hover)
        if p:
            ui = S.cursor(ui, sum(q[0] for q in p) / 4 + 6, sum(q[1] for q in p) / 4 + 2)
    if ui_k < 1.0:
        ui.putalpha(ui.split()[3].point(lambda v: int(v * ui_k)))
    img.alpha_composite(ui)
    return img
