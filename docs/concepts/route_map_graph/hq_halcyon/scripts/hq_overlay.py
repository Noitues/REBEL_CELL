"""HQ Halcyon overlay: anchors from the orbit pose, and the locked route grammar on top (drawn at 1920 x 1080).

Locked grammar (r3 / V3 dynamic, unchanged): vinyl node stickers on each room's cut edge, the state ring (lime walked /
current, orange option + number, white ahead, grey past), wax grease-pencil links (lime walked, orange next, white
dashed ahead, grey past), the red pencil TARGET, the operative token, the frame UI.
HQ additions (PROPOSALS, flagged in NOTES):
  IN THE EYE   a scanned room: red ring (bible: red = danger / locked), a small red eye badge on the sticker, red holo
               scan lines over the room's opening (the 3D lockdown plane is the same language), the chip "IN THE EYE"
               on options. Its rule word (SPOTTED / LOCKED) is shown on hover and in the legend
  CLIMB        shortcuts climb straight up the outside of a face (gold rail + gantry in 3D); the link is ordinary wax
               in its state colour, with a gold "CLIMB n/2" chip at its foot
  X-RAY        rooms on faces turned away are hidden; on hover-show-all / OVERVIEW they ghost through at 30 %
  EYE COMPASS  a lighthouse dial (top right): the pyramid from above, the watched sector now, the next step's sector
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
import sidekit as S  # noqa: E402
import ui31 as K  # noqa: E402
import kit44 as KT  # noqa: E402

W, H = 1920, 1080
STK_PX = {"option": 48, "current": 44, "walked": 36, "reach": 40, "grey": 34, "target": 62, "start": 42}
from hq_kit import states as ST  # noqa: E402
RED, GOLD = ST.RED, ST.GOLD
SECTOR_WORD = {0: "NORTH", 45: "NORTH-EAST", 90: "EAST", 135: "SOUTH-EAST", 180: "SOUTH", 225: "SOUTH-WEST",
               270: "WEST", 315: "NORTH-WEST"}
DISPATCH = {
    "n3": "The eye's on the south-east corner. The long way's lit. The rail goes straight up: climb it.",
    "n9": "Eye's swung north-east: the gallery's in it. The rail to the top is dark. One climb, then the vault.",
    "start": "Halcyon Civic. Twenty-one floors the long way round. The eye turns every step: time it.",
    "n5": "Gallery's clear. Keep walking the south face.",
    "n6": "Corner coming up. The stairs climb the east face.",
    "n7": "East face. The eye's coming round behind you. Move.",
}


def sector_word(az):
    return SECTOR_WORD.get(int(round(az / 45.0)) * 45 % 360, "%d" % az)


def face_of_point(p):
    return (1 if p[0] > 0 else 3) if abs(p[0]) >= abs(p[1]) else (2 if p[1] > 0 else 0)


def pose_of(js):
    loc, tgt = js["loc"], js["tgt"]
    d = [tgt[k] - loc[k] for k in range(3)]
    dist = math.sqrt(sum(v * v for v in d))
    yaw = math.degrees(math.atan2(d[0], d[1]))
    pitch = -math.degrees(math.asin(d[2] / dist))
    return CR.Pose(tgt, yaw, pitch, dist, js["lens"], js.get("shift_x", 0.0), js.get("shift_y", 0.0))


def anchors(pose, walked):
    A = {"rooms": {}, "edges": []}
    for i in G.NODES:
        if i == "start":
            x, y, z = G.start_pos()
            pts = [(x - 4, y - 3.2, 0.5), (x + 4, y - 3.2, 0.5), (x + 4, y - 3.2, 4.6), (x - 4, y - 3.2, 4.6)]
            vis = CR.visible_face(0, pose, 0.05) or CR.visible_face(3, pose, 0.05)   # the gate stands south-west
        elif i == "srv":
            c = pose.loc()
            f = max(range(4), key=lambda f_: G.N[f_][0] * c[0] + G.N[f_][1] * c[1])
            pts = G.room_front(i, f)
            vis = True
        else:
            pts = G.room_front(i)
            vis = CR.visible_face(G.FACE[i], pose)
        q = [pose.proj(p) for p in pts]
        if any(v is None for v in q):
            A["rooms"][i] = dict(front=None, vis=False)
            continue
        b0, b1, t1, t0 = q
        if b1[0] < b0[0]:
            b0, b1, t1, t0 = b1, b0, t0, t1
        A["rooms"][i] = dict(front=[b0, b1, t1, t0], vis=vis)
    for a, b in G.edges(walked):
        path = G.edge_path(a, b)
        hm = G.hidden_mid(a, b)
        pts = [pose.proj(p) for p in path]
        vis = []
        for k in range(len(path) - 1):
            if hm and hm[0] <= k < hm[1]:
                vis.append(False)
            else:
                mid = [(path[k][j] + path[k + 1][j]) / 2 for j in range(3)]
                vis.append(CR.visible_face(face_of_point(mid), pose, -0.05))
        A["edges"].append(dict(a=a, b=b, pts=pts, vis=vis, type=G.edge_type(a, b)))
    return A


# ------------------------------------------------------------------ the helpers wax_r2 reads (C3 API)
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


# ------------------------------------------------------------------ the world grade at plate resolution
def lum(a):
    return a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11


def grade(plate, A, st, cur, hover, walked, scanned, focus=1.0):
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
    if hover:
        br = G.branch(hover, walked)[0]
        keep = np.zeros((H2, W2), np.float32)
        for i in sorted(br | {cur}):
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
        for i in sorted(G.branch(hover, walked)[0], key=lambda n: G.ORDER[n]):
            p = room_poly(A, i)
            if p:
                m = Image.fromarray((poly_mask(p, 0, 0, (W2, H2), s) * 255).astype(np.uint8))
                img = K.add_glow(img, m, S.TYPE_COL[G.KIND[i]], int(30 * s), 0.5)
    return img


# ------------------------------------------------------------------ overlay pieces
def scan_lines(img, poly, k=1.0, phase=0.0):
    """Red holo scan lines over a scanned room's opening (hq_kit.states)."""
    return ST.scan_lines(img, poly, k, phase, (W, H))


_CREST = []


def eye_badge(px):
    """The IN THE EYE badge: Halcyon's crest (the eye) on red (hq_kit.states)."""
    if not _CREST:
        import crests15
        _CREST.append(crests15.eye())
    return ST.eye_badge(px, _CREST[0])


def number_chip(img, x, y, n, s=1.0, col=S.ORANGE):
    hw, hh = 15 * s, 16 * s
    box = (x - hw, y - hh, x + hw, y + hh)
    img = KT.panel_shadow(img, box, 0, blur=6, k=0.55, off=(0, 3))
    d = K.BD(img)
    d.rectangle(box, fill=col + (255,), outline=(10, 8, 14, 255), width=max(2, int(2 * s)))
    K.text(img, (x, y + 1), str(n), K.F(K.ANTON, int(24 * s)), (14, 10, 6), "mm", 0)
    return img


def draw_nodes(img, A, st, opts, scanned, hover=None, hover_k=0.0, ghosts=False, phase=0.0):
    hovering = hover is not None and hover_k > 0.3
    br = G.branch(hover)[0] if hovering else set()
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
        if not r["vis"]:
            if ghosts and s != "grey":
                # x-ray: a ghost ring through the pyramid (rooms on the far faces)
                cx = sum(q[0] for q in poly) / 4
                cy = sum(q[1] for q in poly) / 4
                img = S.ring(img, cx, cy, 14, S.STATE_COL[s] if kind != "target" else RED, 3, 0.35)
            continue
        sc = room_scale(A, i)
        ks = min(1.9, max(0.75, sc * 0.8))
        in_eye = i in scanned
        if kind != "target":
            col = RED if in_eye and s in ("option", "reach") else S.STATE_COL[s]
            w = 4 if s in ("option", "current") else 2
            w = max(w, int(round(w * min(1.6, sc * 0.7))))
            al = {"grey": 0.35, "reach": 0.8}.get(s, 1.0)
            if hovering and s in ("reach", "option") and i not in br:
                al *= S.MIX_A
            img = S.frame_poly(img, poly, col, w, al, glow=s in ("option", "current") or in_eye)
            if in_eye:
                img = scan_lines(img, poly, 0.8 if s == "option" else 0.55, phase)
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
        img = S.sticker(img, kind, x, yy, px, grey=grey, alpha=alpha, hover=lift)
        if kind != "target":
            rc = RED if in_eye and s in ("option", "reach") else S.STATE_COL[s]
            w = 5 if s in ("option", "current") else 3
            img = S.ring(img, x, yy, px / 2 + 6 * ks, rc, max(w, int(w * ks * 0.8)), alpha)
        if in_eye and s in ("option", "reach"):
            b = eye_badge(int(px * 0.5))
            img.alpha_composite(b, (int(x + px * 0.18), int(yy - px * 0.62)))
        if s == "option":
            n = opts.index(i) + 1
            img = number_chip(img, x - px / 2 - 20 * ks, y - px * 0.32, n, s=ks, col=S.ORANGE)
            if in_eye:
                img, _ = KT.chip(img, (poly[3][0] + 6 * ks, poly[3][1] - 18 * ks), "IN THE EYE", RED, int(14 * min(1.3, ks)),
                                 anchor="lm", pad=7)
    return img


def shaft_chips(img, A, est, walked, overview=False):
    """A gold CLIMB n/2 chip beside every climb on offer (options; in the overview every climb still ahead)."""
    used = G.shortcuts_used(walked)
    for e in A["edges"]:
        if e["type"] != "climb":
            continue
        es = est[(e["a"], e["b"])]
        if not (es == "option" or (overview and es == "future")) or not e["vis"][1]:
            continue
        pts = [q for q in e["pts"] if q is not None]
        if len(pts) < 4:
            continue
        m = pts[len(pts) // 2]
        if not (0 < m[0] < W and 0 < m[1] < H):
            continue
        img, _ = KT.chip(img, (m[0] + 14, m[1]), "CLIMB %d/%d" % (used + 1, G.CP["max_shortcuts"]), GOLD,
                         13, anchor="lm", pad=6)
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
    img, _ = KT.chip(img, (cx + rx + 12, cy + 6), "CENTRAL SERVER // THE PANOPTICON", (255, 214, 64), 12, anchor="lm", pad=6)
    return img


def _unused():
    return img


def token_at(img, A, i, k):
    p = room_poly(A, i)
    if not p:
        return img
    sc = min(1.8, room_scale(A, i))
    return S.token(img, p[1][0] - 30 * sc, p[1][1] - 26 * sc, px=int(44 * max(0.9, min(1.6, sc * 0.8))))


def eye_compass(img, x, y, az, az_next):
    """The lighthouse dial: the pyramid from above (north up), the watched 90 degree sector now (red) and next (dashed)."""
    box = (x, y, x + 276, y + 150)
    img = KT.term(img, box, "THE EYE", accent=RED, seed=29)
    cx, cy, r = x + 66, y + 92, 44

    def pt(a, rr):
        return (cx + rr * math.sin(math.radians(a)), cy - rr * math.cos(math.radians(a)))
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.polygon([(cx, cy)] + [pt(az - 45 + 9 * k, r) for k in range(11)], fill=RED + (110,))
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    for k in range(10):
        if k % 2 == 0:
            d.line([pt(az_next - 45 + 9 * k, r), pt(az_next - 45 + 9 * (k + 1), r)], fill=(255, 150, 150, 230), width=3)
    d.line([(cx, cy), pt(az_next - 45, r)], fill=(255, 150, 150, 160), width=1)
    d.line([(cx, cy), pt(az_next + 45, r)], fill=(255, 150, 150, 160), width=1)
    for s_ in (0.62, 0.42, 0.22):
        h = r * s_
        d.rectangle([(cx - h, cy - h), (cx + h, cy + h)], outline=(200, 214, 230, 255), width=2)
    d.line([pt(az, 0), pt(az, r + 4)], fill=RED + (255,), width=3)
    K.text(img, pt(0, r + 10), "N", K.F(K.MONO, 11), (150, 168, 190), "mm", 0.2)
    f = K.F(K.MONO, 14)
    K.text(img, (x + 122, y + 62), "NOW:  " + sector_word(az), f, RED, "lm", 0.3)
    K.text(img, (x + 122, y + 86), "NEXT: " + sector_word(az_next), f, (255, 160, 160), "lm", 0.3)
    K.text(img, (x + 122, y + 112), "turns 45 deg a step", K.F(K.MONO, 12), (150, 168, 190), "lm", 0.3)
    return img


def legend(img, cx=1010):
    def ringf(col, dash=False):
        def f(px):
            im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
            ImageDraw.Draw(im).ellipse([3, 3, px - 4, px - 4], outline=col + (255,), width=3)
            return im
        return f

    def eyef(px):
        return eye_badge(px)
    import r32ui as U32
    items = [(lambda px, k=k: U32.icon(k, px), lab) for k, lab in (("router", "FIGHT"), ("elite", "ELITE"),
                                                                   ("terminal", "EVENT"), ("modem", "SHOP"))]
    items += [(ringf(S.LIME), "walked"), (ringf(S.ORANGE), "next"), (ringf(S.WHITE), "ahead"), (ringf(S.GREY), "past"),
              (eyef, "in the eye"), (ringf(GOLD), "climb")]
    f = K.F(K.MONO, 15)
    w = sum(int(30 + f.getlength(lab) + 18) for _, lab in items) + f.getlength("|  HOVER: SHOW ALL") + 40
    img, box = KT.key_strip(img, int(cx - w / 2), 1030, items, hint="HOVER: SHOW ALL")
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


def rule_note(img, i, walked):
    """The hover note under the node file: what the eye means for this room (rule word per preset consequence)."""
    sc, f = G.scanned(walked)
    if i in sc:
        s = ST.rule_word(G.EYEP["consequence"])
        col = RED
    else:
        s = "CLEAR: the eye is on the %s" % sector_word(f).lower()
        col = (140, 255, 170)
    img, _ = KT.chip(img, (14, 996), s, col, 13, anchor="lm", pad=8)
    return img


def overlay(plate, A, ov, part="all", ui_k=1.0, phase=0.0):
    """Everything above the world grade, drawn at 1920 x 1080 onto `plate` (RGBA)."""
    import wax_r2 as WX
    walked = ov["walked"]
    hover = ov.get("hover")
    hk = ov.get("hover_k", 0.0)
    zoom = ov.get("zoom", 0.0)
    st, opts = G.states(walked)
    est = G.edge_states(walked, st)
    sc, f = G.scanned(walked)
    cur = walked[-1]
    img = plate.convert("RGBA")
    ghosts = zoom < 0.5                       # x-ray ghosts: OVERVIEW (and the legend hover, not mocked here)
    k = min(1.6, max(0.8, room_scale(A, cur) * 0.62))
    # wax on the visible segments; x-ray segments (behind the pyramid, or the shaft through the core) at 45 %, dashed
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
    if Aray["edges"] and ghosts:              # x-ray links: OVERVIEW (and the legend hover) only
        ray = WX.draw_wax(Image.new("RGBA", (W, H), (0, 0, 0, 0)), Aray, est, st, opts, cur, hover=hover, hover_k=hk, k=k * 0.7)
        a = ray.split()[3].point(lambda v: int(v * 0.45))
        ray.putalpha(a)
        img.alpha_composite(ray)
    img = WX.draw_wax(img, Avis, est, st, opts, cur, hover=hover, hover_k=hk, k=k)
    img = draw_nodes(img, A, st, opts, set(sc), hover=hover, hover_k=hk, ghosts=ghosts, phase=phase)
    img = shaft_chips(img, A, est, walked, overview=zoom < 0.5)
    img = target_mark(img, A)
    img = token_at(img, A, cur, k)
    if hover and hk > 0.5:
        p = room_poly(A, hover)
        if p:
            ks = min(1.9, max(0.75, room_scale(A, hover) * 0.8))
            img = S.tag(img, p[3][0] + 8 * ks, p[3][1] - 20 * ks, hover, "option")
    if ui_k <= 0:
        return img
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ui = S.chrome_top(ui, DISPATCH.get(cur, DISPATCH["start"]))
    ui = S.sidebar(ui, len(opts), hover=hover if (hover and hk > 0.5) else None)
    ui = eye_compass(ui, 1630, 10, ov.get("eye_az", f), G.eye_az(len(walked)))
    if hover and hk > 0.5:
        ui = rule_note(ui, hover, walked)
    ui = legend(ui, cx=980)
    ui = view_toggle(ui, zoom)
    if hover and hk > 0.5:
        p = room_poly(A, hover)
        if p:
            ui = S.cursor(ui, sum(q[0] for q in p) / 4 + 6, sum(q[1] for q in p) / 4 + 2)
    if ui_k < 1.0:
        ui.putalpha(ui.split()[3].point(lambda v: int(v * ui_k)))
    img.alpha_composite(ui)
    return img
