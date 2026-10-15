"""Storyboard 2D layers at 1920 x 1080 (PIL): the HQ page (round 44 kit), the jack-in transition (terminal, binary rain on
the link, CRT collapse, the wheel slap and the wheel lens), the wall-dissolve bits, the netrun route UI (start state) and
the beat titles. Everything is a function of (plate, t) or (plate, anchors, state); all randomness is seeded.
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

import ui31 as K  # noqa: E402
import kit44 as KT  # noqa: E402
import markers42 as M  # noqa: E402
import r31lib as RL  # noqa: E402
import sidekit as S  # noqa: E402
import compose3 as C3  # noqa: E402
import wax_r2 as WX  # noqa: E402
import sgraph3 as G  # noqa: E402
import cam_rig as R  # noqa: E402
import cityfill as CF  # noqa: E402
import sb_cams as SB  # noqa: E402

W, H = 1920, 1080
LIME, CYAN, ORANGE, PINK = K.LIME, K.CYAN, S.ORANGE, K.PINK
_NET = None


def net():
    global _NET
    if _NET is None:
        _NET = CF.build()
    return _NET


def ease(t):
    return R.ease(t)


def ease_out(t):
    return R.ease_out(t)


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def phase(t, a, b):
    return clamp((t - a) / max(1e-6, b - a))


# ---------------------------------------------------------------- world anchors (any pose)
def street_poly(pose):
    """The netrun street (the border link) from the relay to the Site, on the road centre, projected."""
    d = net()["network"]
    rl, st = d["relay"], d["site"]
    yc = sum(net()["road_y"]) / 2
    pts = [rl, (rl[0], yc, 0.4)]
    n = 24
    for k in range(1, n):
        x = rl[0] + (st[0] - rl[0]) * k / n
        pts.append((x, yc, 0.4))
    pts += [(st[0], yc, 0.4), st]
    q = [pose.proj(p) for p in pts]
    return [p for p in q if p]


def _grid_path(a, b):
    xs, ys = CF.streets()
    sy = min(ys, key=lambda y: (abs(y - a[1]) + abs(y - b[1]), y))
    sx = min(xs, key=lambda x: (abs(x - b[0]), x))
    return [(a[0], a[1], 0.3), (a[0], sy, 0.3), (sx, sy, 0.3), (sx, b[1], 0.3), (b[0], b[1], 0.3)]


def poly_len(p):
    return sum(math.hypot(p[i + 1][0] - p[i][0], p[i + 1][1] - p[i][1]) for i in range(len(p) - 1))


def poly_at(p, s):
    for i in range(len(p) - 1):
        L = math.hypot(p[i + 1][0] - p[i][0], p[i + 1][1] - p[i][1])
        if s <= L or i == len(p) - 2:
            u = 0 if L < 1e-6 else clamp(s / L)
            return (p[i][0] + (p[i + 1][0] - p[i][0]) * u, p[i][1] + (p[i + 1][1] - p[i][1]) * u)
        s -= L
    return p[-1]


def poly_cut(p, frac):
    L = poly_len(p) * frac
    out = [p[0]]
    for i in range(len(p) - 1):
        seg = math.hypot(p[i + 1][0] - p[i][0], p[i + 1][1] - p[i][1])
        if L >= seg:
            out.append(p[i + 1])
            L -= seg
        else:
            u = L / max(seg, 1e-6)
            out.append((p[i][0] + (p[i + 1][0] - p[i][0]) * u, p[i][1] + (p[i + 1][1] - p[i][1]) * u))
            break
    return out


# ---------------------------------------------------------------- the Cell's network on the city
def network_layer(img, pose, t, alpha=1.0, selected=False):
    """Lime links along the street grid with moving packets, uplink risers to the roof markers, the markers (v4)."""
    d = net()["network"]
    nodes = {n["id"]: n for n in d["nodes"]}
    lay = Image.new("L", (W, H), 0)
    dl = ImageDraw.Draw(lay)
    paths = []
    for a, b in d["links"]:
        pa, pb = nodes[a]["pos"], nodes[b]["pos"]
        wp = _grid_path(pa, pb)
        q = [pose.proj(p) for p in wp]
        if any(v is None for v in q):
            continue
        paths.append(q)
        dl.line(q, fill=255, width=3, joint="curve")
        for n_ in (nodes[a], nodes[b]):
            top, base = pose.proj(n_["pos"]), pose.proj((n_["pos"][0], n_["pos"][1], 0.3))
            if top and base:
                dl.line([base, top], fill=200, width=2)
    m = lay.point(lambda v: int(v * alpha))
    img = K.add_glow(img, m, (80, 220, 255), 16, 0.55)
    img = K.over(img, (226, 255, 60), m, 0.95)
    # packets
    pk = Image.new("L", (W, H), 0)
    dp = ImageDraw.Draw(pk)
    for k, q in enumerate(paths):
        L = poly_len(q)
        for j in range(3):
            s = ((t * 0.35 + j / 3.0 + k * 0.137) % 1.0) * L
            x, y = poly_at(q, s)
            dp.ellipse([x - 3, y - 3, x + 3, y + 3], fill=255)
    pk = pk.point(lambda v: int(v * alpha))
    img = K.add_glow(img, pk, (240, 255, 170), 8, 0.8)
    img = K.over(img, (250, 255, 220), pk, 1.0)
    # the border link: the netrun street, dashed (white until the Site is picked)
    sp = street_poly(pose)
    if sp and not selected:
        bl = Image.new("L", (W, H), 0)
        db = ImageDraw.Draw(bl)
        L = poly_len(sp)
        s = 0.0
        while s < L:
            seg = [poly_at(sp, s), poly_at(sp, min(L, s + 10))]
            db.line(seg, fill=255, width=3)
            s += 18
        img = K.over(img, (236, 236, 240), bl.point(lambda v: int(v * alpha * 0.55)), 1.0)
    if alpha < 0.02:
        return img
    # markers (bible 4.5 pins), drawn back to front
    marks = [(n["pos"], n["kind"]) for n in d["nodes"]] + [(p["pos"], p["kind"]) for p in d["pins"]]
    marks.append((d["site"], "site_sel" if selected else "site"))
    order = sorted(marks, key=lambda m_: (pose.proj(m_[0]) or (0, 0))[1])
    lay2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for pos, kind in order:
        q = pose.proj(pos)
        if not q or not (-60 < q[0] < W + 60 and -60 < q[1] < H + 60):
            continue
        x, y = q
        if kind == "core":
            lay2 = M.marker(lay2, x, y, "core", 0, scale=1.2)
        elif kind in ("owned", "relay"):
            lay2 = M.marker(lay2, x, y, "site", 0, "claimed", scale=1.05)
        elif kind == "exploit":
            lay2 = M.marker(lay2, x, y, "exploit", 2, "corporate", "next", "INTEL", scale=1.0)
        elif kind == "heat":
            lay2 = M.marker(lay2, x, y, "heat", 2, "corporate", "notyet", scale=0.95)
        elif kind == "cleared":
            lay2 = M.marker(lay2, x, y, "site", 1, "cleared", "yours", scale=1.0)
        elif kind in ("site", "site_sel"):
            lay2 = M.marker(lay2, x, y, "site", 2, "corporate", "next", scale=1.3 if kind == "site_sel" else 1.15)
    if alpha < 1.0:
        a = lay2.split()[3].point(lambda v: int(v * alpha))
        lay2.putalpha(a)
    img.alpha_composite(lay2)
    return img


# ---------------------------------------------------------------- HQ page furniture (round 44 hq44.py, reused)
def topbar_full(img):
    items = [dict(kind="heat", value=58, w=340, rule="while 50+: enemies +1 resistance"),
             dict(kind="schem", label="SCHEMATICS", value="142"),
             dict(kind="home", label="HOME", value="44", max="/50"),
             dict(kind="exploit", label="EXPLOITS", value="1", max="/3"),
             dict(kind="raid", label="RAIDS", value="1"),
             dict(kind="ice", label="ICE", value="5"),
             dict(kind="crew", label="CREW", value="3", max="/4")]
    img, box = KT.topbar(img, 16, 12, items)
    img = K.term_button(img, (1690, 18, 1904, 78), "VIEW LOADOUT", None)
    return img


def tabs(img):
    rows = [("CREW", "3 / 4", K.CYAN), ("MARKET", "142 SCHEM.", K.CYAN), ("DEFENSE", "ARMORY 0/6", K.CYAN)]
    y = 812
    for name, sub, ac in rows:
        box = (20, y, 214, y + 62)
        img = KT.panel_shadow(img, box, 8, blur=10)
        img = K.term_button(img, box, name, sub, state="pressed" if name == "CREW" else "idle", accent=ac)
        y += 72
    return img


def crew(img, runner):
    cards = [("CELL-9", "breaker", "R2", "READY", K.GREEN, False),
             ("NOVA", "ghost", "R1", "READY", K.GREEN, False),
             ("HEX", "phantom", "R1", "FLATLINED", (150, 150, 162), True)]
    x = 236
    for i, (nm, cls, rk, st, sc, dead) in enumerate(cards):
        sel = runner and i == 0
        p = KT.polaroid(nm, cls, rk, st, sc, dead=dead, w=140, seed=40 + i, selected=sel)
        ang = [-2.2, 1.4, -0.8, 2.0][i]
        y = 822 if sel else 838
        img = KT.paste_polaroid(img, p, x, y, ang, lift=0.5 if sel else 0.0)
        if sel:
            K.text(img, (x + 4, y - 16), "RUNNER", KT.F(K.MONO, 13), K.CYAN, "la", 1.6)
        x += 150
    return img


def work_order_panel(img):
    rows = [("TARGET", "CORE (CELL)"), ("UNITS", "4 IN 1 WAVE"), ("ENTRY SITES", "1 (A)"), ("TRIGGER", "HEAT 50 CROSSED", (170, 30, 25))]
    p = KT.work_order(rows, w=330, seed=52)
    return K.paste_paper(img, p, (26, 104), angle=1.4, sh=0.6)


def toast(img, text):
    box = (840, 1030, 1420, 1068)
    img = KT.panel_shadow(img, box, 0, blur=10)
    img = K.over(img, (2, 2, 8), K.rect_mask(img.size, box), 0.88)
    img = K.holo_panel(img, box, corp="meridian", seed=21, alpha=0.78)
    K.text(img, (866, 1049), text, KT.F(K.MONO, 15), (255, 214, 170), "lm", 0.8)
    return img


def target_edge(img):
    """Meridian HQ (the boss TARGET) is off-screen: the City Grid's red pencil edge marker and its chip."""
    ox, oy = 1800, 330
    tip = (1872, 150)
    pen = KT.pencil(KT.PEN_R, 441)
    pen.arrow([(ox, oy), ((ox + tip[0]) / 2 + 6, (oy + tip[1]) / 2 + 4), tip], width=9, head=26)
    pen.text("TARGET", 1770, 250, 36, angle=-8)
    img, _ = KT.chip(img, (1596, 374), "CENTRAL SERVER  //  EXPLOITS 1/3", K.GOLD, 14, anchor="lm")
    img = KT.spill(img, pen.mask.resize((W, H)), KT.PEN_R, 0.14, 30)
    return KT.ink(img, pen)


def site_holo(img, reveal=1.0, t=0.0):
    """The decrypted holo Site file; reveal 0..1 runs a decrypt scan from the top (rows scramble until the scan passes)."""
    def extra(im, y):
        K.text(im, (1482, y + 6), "IF CLEARED", KT.F(K.MONO, 14), K.CYAN, "lm", 1.4)
        row = RL.outcome_row([("schem", "+12", True), ("none", "OPENS 2 SITES", True)], size=17, gap=8)
        im.alpha_composite(row, (1482, int(y + 22)))
        K.text(im, (1482, y + 62), "CAN BE YOUR NODE", KT.F(K.MONO, 14), (210, 236, 120), "lm", 1.0)
        return im
    rows = [("TYPE", "Site  //  netrun"), ("LINK", "from RELAY_4"), ("FLATLINE", "HEAT +11 -> 69"), ("sep",)]
    box = (1462, 448, 1898, 760)
    if reveal >= 0.999:
        return KT.holo_file(img, box, "T2  //  PRIORITY LANE EXCHANGE", rows, sub="MERIDIAN FREIGHT  //  SITE FILE 207",
                            extra=extra, seed=9)
    r = random.Random(int(t * 24) * 7 + 3)
    glyph = "01#%$&@!<>/\\=+"
    scr = [rr if len(rr) < 2 else (rr[0], "".join(r.choice(glyph) if ch != " " else " " for ch in rr[1])) for rr in rows]
    full = KT.holo_file(img.copy(), box, "T2  //  PRIORITY LANE EXCHANGE", rows, sub="MERIDIAN FREIGHT  //  SITE FILE 207",
                        extra=extra, seed=9)
    enc = KT.holo_file(img.copy(), box, "T2  //  " + "".join(r.choice(glyph) for _ in range(22)), scr,
                       sub="MERIDIAN FREIGHT  //  ENCRYPTED", seed=9)
    # open: the panel grows from a line (0..0.25), then the decrypt scan runs top to bottom
    o = clamp(reveal / 0.25)
    cy = (box[1] + box[3]) / 2
    hh = (box[3] - box[1]) / 2 * ease_out(o)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rectangle([box[0] - 4, cy - hh - 4, box[2] + 4, cy + hh + 4], fill=255)
    sy = box[1] + (box[3] - box[1] + 20) * clamp((reveal - 0.25) / 0.75)
    ms = Image.new("L", (W, H), 0)
    ImageDraw.Draw(ms).rectangle([0, 0, W, sy], fill=255)
    out = Image.composite(full, enc, ms)
    out = Image.composite(out, img, m)
    if 0.25 < reveal < 1.0:
        d = ImageDraw.Draw(out, "RGBA")
        d.rectangle([box[0], sy - 2, box[2], sy + 2], fill=(150, 255, 230, 200))
    return out


def jack_sticker(img, gloss=None, press=0.0, pop=1.0):
    sd = KT.sticker("JACK IN", 84, "pink", seed=31)
    if gloss is not None:
        sd = KT.rainbow_sweep(sd, pos=gloss, k=0.55)
    sc = (0.4 + 0.6 * ease_out(pop) + 0.08 * math.sin(math.pi * clamp(pop)) ) * (1.0 - 0.07 * press)
    img = KT.place_sticker(img, sd, 1730, 904, angle=-3, scale=sc, spill_col=K.PINK, spill_k=0.3 * (1 - 0.5 * press))
    if press > 0:
        img = K.over(img, (0, 0, 0), KT.sticker_mask(sd, 1730, 904, -3, sc), 0.25 * press)
    return img


_SUI = {}


def central_server(pose=None):
    """The boss TARGET in view (mainline: the red pencil circle on the Central Server, its chip above): by rule the
    tallest fill building projecting into the band right of the network, left of the Site card."""
    pose = pose or SB.AERIAL
    best = None
    for b in net()["buildings"]:
        x0, y0, x1, y1 = b["rect"]
        c = ((x0 + x1) / 2, (y0 + y1) / 2, b["h"])
        q = SB.AERIAL.proj(c)
        if q and 1230 < q[0] < 1420 and 380 < q[1] < 600 and (best is None or (b["h"], -b["id"]) > (best[0], -best[1])):
            best = (b["h"], b["id"], c)
    return best[2] if best else (400.0, 300.0, 80.0)


def target_pencil(img, pose=None):
    pose = pose or SB.AERIAL
    q = pose.proj(central_server())
    if not q:
        return img
    x, y = q
    pen = KT.pencil(KT.PEN_R, 441)
    ring = [(x + 62 * math.cos(-2.4 + 2 * math.pi * 1.08 * k / 48), y + 34 * math.sin(-2.4 + 2 * math.pi * 1.08 * k / 48))
            for k in range(49)]
    pen.stroke(ring, width=8)
    pen.text("TARGET", x - 40, y + 20, 40, angle=-6)
    img = KT.spill(img, pen.mask.resize((W, H)), KT.PEN_R, 0.14, 30)
    img = KT.ink(img, pen)
    img, _ = KT.chip(img, (x - 190, y - 100), "CENTRAL SERVER  //  EXPLOITS 1/3", K.GOLD, 14, anchor="lm")
    return img


ON_AIR = ("I have the tapes. The voice giving the orders in the district does not breathe between sentences.   ***   "
          "vs Meridian Freight Systems  |  ICE 5   ***   ")


def on_air(img, t):
    """The mainline foot band: ON AIR label and the scrolling corp-news ticker (PLAN1 W3_HQ, all panels)."""
    box = (0, 1044, W, 1080)
    img = K.over(img, (3, 4, 10), K.rect_mask(img.size, box), 0.9)
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(0, 1044), (W, 1044)], fill=K.CYAN + (140,), width=1)
    d.rectangle([0, 1046, 250, 1078], fill=(92, 225, 255, 235))
    K.text(img, (125, 1062), "ON AIR", KT.F(K.MONO, 18), (8, 20, 30), "mm", 2.0)
    f = KT.F(K.MONO, 17)
    txt = ON_AIR * 4
    off = (t * 70.0) % f.getlength(ON_AIR)
    lay = Image.new("RGBA", (W - 262, 34), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((-off, 17), txt, font=f, fill=(150, 230, 250, 255), anchor="lm")
    img.alpha_composite(lay, (262, 1045))
    return img


def map_key(img):
    return K.term_button(img, (1712, 112, 1892, 152), "MAP KEY", None)


def jack_line(img):
    box = (1478, 982, 1902, 1036)
    img = KT.term(img, box, None, accent=K.CYAN, header=False, seed=91, chamfer=8)
    K.text(img, (1888, 998), "> jack --from RELAY_4 --to", KT.F(K.MONO, 14), (200, 225, 240), "rm", 0.4)
    K.text(img, (1888, 1020), "PRIORITY_LANE_EXCHANGE", KT.F(K.MONO, 14), (200, 225, 240), "rm", 0.4)
    return img


def _draw_static(img, runner):
    ui = K.over(img, (3, 2, 8), KT.soft_l((0, 0, 1920, 96), blur=24), 0.35)
    ui = K.over(ui, (3, 2, 8), KT.soft_l((0, 800, 900, 1080), blur=40), 0.3)
    ui = target_pencil(ui)
    ui = topbar_full(ui)
    ui = map_key(ui)
    ui = tabs(ui)
    ui = crew(ui, runner=runner)
    return jack_line(ui)


def static_ui(img, runner):
    """The HQ page's fixed furniture, drawn once on two flat plates and solved per pixel (out = img * m + b): every
    operation is affine in the background, so the per-frame cost is one multiply-add."""
    if runner not in _SUI:
        o0 = np.asarray(_draw_static(Image.new("RGBA", (W, H), (0, 0, 0, 255)), runner).convert("RGB"), np.float32) / 255
        o1 = np.asarray(_draw_static(Image.new("RGBA", (W, H), (128, 128, 128, 255)), runner).convert("RGB"), np.float32) / 255
        _SUI[runner] = (np.clip((o1 - o0) / (128 / 255.0), 0, 1), o0)
    m, b = _SUI[runner]
    a = np.asarray(img.convert("RGB"), np.float32) / 255
    return Image.fromarray((np.clip(a * m + b, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")


def hq_page(plate, t, ui_alpha=1.0, pose=None):
    """Beats 1-2 (and the backdrop of beat 3) at time t (s)."""
    T = SB.T
    pose = pose or SB.AERIAL
    img = plate.convert("RGBA")
    sel = t >= T["click"]
    d = net()["network"]
    sx, sy = pose.proj(d["site"])
    # world grade: the network's area keeps its light, the rest steps back (round 44 grade_map, lighter here)
    img = network_layer(img, pose, t, 1.0, selected=sel)
    ui = static_ui(img, sel)
    # cursor path: rest -> the Site -> JACK IN
    rest = (1010, 560)
    jack = (1730, 910)
    if t < T["b2"]:
        cx, cy = rest[0] + 6 * math.sin(t * 1.3), rest[1] + 4 * math.cos(t * 0.9)
    elif t < T["hover_site"]:
        u = ease(phase(t, T["b2"], T["hover_site"]))
        cx, cy = rest[0] + (sx + 8 - rest[0]) * u, rest[1] + (sy - 4 - rest[1]) * u
    elif t < T["to_jack"]:
        cx, cy = sx + 8, sy - 4
    else:
        u = ease(phase(t, T["to_jack"], T["press"] - 0.1))
        cx, cy = sx + 8 + (jack[0] - sx - 8) * u, sy - 4 + (jack[1] - sy + 4) * u
    if T["hover_site"] <= t < T["to_jack"]:
        ui, _ = KT.chip(ui, (sx + 34, sy - 46), "Priority Lane Exchange", K.LIME, 13, anchor="lm", bright=True)
    if t >= T["hover_site"]:
        ui = site_holo(ui, phase(t, T["hover_site"], T["hover_site"] + 0.55), t)
    if sel:
        # the click pulse, the pencil circle, then the orange pencil plan along the border link (relay -> Site)
        pu = phase(t, T["click"], T["click"] + 0.35)
        if pu < 1:
            m = Image.new("L", (W, H), 0)
            r_ = 20 + 60 * ease_out(pu)
            ImageDraw.Draw(m).ellipse([sx - r_, sy - 18 - r_, sx + r_, sy - 18 + r_], outline=255, width=4)
            ui = K.add_glow(ui, m.point(lambda v: int(v * (1 - pu))), ORANGE, 8, 1.0)
        pen = KT.pencil(ORANGE, 442)
        cu = phase(t, T["click"] + 0.05, T["click"] + 0.35)
        if cu > 0:
            ring = [(sx + 50 * math.cos(-2.2 + 2 * math.pi * 1.1 * k / 40), sy - 18 + 38 * math.sin(-2.2 + 2 * math.pi * 1.1 * k / 40))
                    for k in range(41)]
            pen.stroke(poly_cut(ring, cu), width=9)
        lu = phase(t, T["click"] + 0.35, T["gloss"])
        if lu > 0:
            sp = street_poly(pose)
            sp = [(x, y - 4) for x, y in sp]
            cut = poly_cut(sp, ease(lu))
            if len(cut) > 1:
                if lu >= 1:
                    pen.arrow(cut, width=8, head=22)
                else:
                    pen.stroke(cut, width=8)
        ui = KT.spill(ui, pen.mask.resize((W, H)), ORANGE, 0.14, 30)
        ui = KT.ink(ui, pen)
        pop = phase(t, T["click"] + 0.05, T["click"] + 0.3)
        gloss = None
        if T["gloss"] <= t <= T["gloss"] + 0.8:
            gloss = -0.1 + 1.2 * phase(t, T["gloss"], T["gloss"] + 0.8)
        press = 0.0
        if t >= T["press"]:
            press = math.sin(math.pi * phase(t, T["press"], T["press"] + 0.25))
        ui = jack_sticker(ui, gloss, press, pop)
    ui = on_air(ui, t)
    if t < T["b3"]:
        ui = KT.cursor(ui, cx, cy)
    if ui_alpha < 1.0:
        ui = Image.blend(img, ui, ui_alpha)
    return ui


# ---------------------------------------------------------------- jack-in: terminal, bits, CRT, wheel
TERM_BOX = (560, 330, 1360, 650)
LINES = [("> jack --from RELAY_4 --to PRIORITY_LANE", (220, 236, 246), 0.00, 0.55),
         ("  routing ....... 3 hops via LANE_15", (150, 200, 220), 0.60, 0.85),
         ("  handshake ..... meridian/fw 2.31  OK", (150, 200, 220), 0.88, 1.15),
         ("  CONNECTED", LIME, 1.22, 1.30)]


def terminal(img, t):
    """t = seconds since the press (beat 3). Opens 0.15 s, types the four lines, then (crt) collapses line -> dot."""
    T = SB.T
    t0 = T["b3"]
    lt = t - t0
    crt = phase(t, T["crt"], T["dive"])
    if crt >= 1.0:
        return img
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay = KT.term(lay, TERM_BOX, "CELL-9  //  TERMINAL", seed=77)
    f = KT.F(K.MONO, 24)
    y = TERM_BOX[1] + 74
    for s, col, a, b in LINES:
        n = int(len(s) * phase(lt, a, b))
        if n > 0:
            sz = 34 if s.strip() == "CONNECTED" else 24
            K.text(lay, (TERM_BOX[0] + 30, y), s[:n], KT.F(K.MONO, sz), col, "lm", 0.6)
        y += 52
    if (int(lt * 4) % 2 == 0) and crt == 0:
        last = max([k for k, (s, c, a, b) in enumerate(LINES) if lt >= a] or [0])
        s, c, a, b = LINES[last]
        n = int(len(s) * phase(lt, a, b))
        xe = TERM_BOX[0] + 30 + f.getlength(s[:n]) + 6
        ImageDraw.Draw(lay).rectangle([xe, TERM_BOX[1] + 62 + 52 * last, xe + 12, TERM_BOX[1] + 86 + 52 * last],
                                      fill=(226, 230, 240, 235))
    op = ease_out(phase(lt, 0.0, 0.15))
    cx, cy = (TERM_BOX[0] + TERM_BOX[2]) / 2, (TERM_BOX[1] + TERM_BOX[3]) / 2
    sx_, sy_ = 1.0, max(0.02, op)
    glow = 0.0
    if crt > 0:
        if crt < 0.55:                  # squash to a bright line
            u = ease(crt / 0.55)
            sy_ = max(0.006, 1.0 - u)
            glow = u
        else:                           # the line shrinks to a dot, which fades
            u = ease((crt - 0.55) / 0.45)
            sy_ = 0.006
            sx_ = max(0.01, 1.0 - u)
            glow = 1.0 - 0.6 * u
    bw = int((TERM_BOX[2] - TERM_BOX[0] + 60) * sx_)
    bh = max(2, int((TERM_BOX[3] - TERM_BOX[1] + 60) * sy_))
    crop = lay.crop((TERM_BOX[0] - 30, TERM_BOX[1] - 30, TERM_BOX[2] + 30, TERM_BOX[3] + 30)).resize((max(2, bw), bh), Image.BILINEAR)
    if glow > 0:
        wl = Image.new("RGBA", crop.size, (235, 255, 245, int(255 * min(1.0, glow ** 2.2))))
        crop = Image.alpha_composite(crop, wl)
    out = img.copy()
    out.alpha_composite(crop, (int(cx - crop.width / 2), int(cy - crop.height / 2)))
    if glow > 0:
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).rectangle([cx - crop.width / 2, cy - crop.height / 2 - 1, cx + crop.width / 2, cy + crop.height / 2 + 1], fill=255)
        out = K.add_glow(out, m, (180, 255, 230), 18, 0.9 * glow)
    return out


_BITF = None


def bitfont(sz):
    return KT.F(K.MONO, sz)


def link_rain(img, pts, t, t0, alpha=1.0, seed=5):
    """Binary rain along the chosen link only: 0/1 glyphs fall onto the link line and stream along it toward the Site."""
    if alpha <= 0.01 or len(pts) < 2:
        return img
    lt = t - t0
    L = poly_len(pts)
    r = random.Random(seed)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    n = 150
    for k in range(n):
        s0 = r.random()
        born = r.random() * 0.6
        spd = r.uniform(0.18, 0.4)
        ch = r.choice("01")
        col = LIME if r.random() < 0.6 else CYAN
        sz = r.choice((14, 16, 18, 22))
        age = lt - born
        if age < 0:
            continue
        fall = clamp(age / 0.25)
        s = ((s0 + max(0.0, age - 0.25) * spd) % 1.0) * L
        x, y = poly_at(pts, s)
        y = y - 90 * (1 - ease_out(fall)) + r.uniform(-6, 6)
        a = int(255 * alpha * (0.5 + 0.5 * r.random()) * min(1.0, age * 6))
        d.text((x, y), ch, font=bitfont(sz), fill=col + (a,), anchor="mm")
    g = lay.split()[3].filter(ImageFilter.GaussianBlur(6))
    img = K.over(img, LIME, g, 0.55 * alpha)
    img.alpha_composite(lay)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).line(pts, fill=255, width=3)
    img = K.add_glow(img, m, LIME, 10, 0.6 * alpha * clamp(lt / 0.3))
    return img


def wheel(img, cx, cy, r, spin, alpha=1.0, hub_open=0.0):
    """The operative's wheel: a 30-tick ring with a hub (lime / cyan), spinning; hub_open > 0 opens the hub (the lens)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    w = max(3, int(r * 0.09))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(20, 26, 30, int(230 * alpha)), width=int(w * 2.2))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=LIME + (int(255 * alpha),), width=w)
    for k in range(30):
        a = spin + 2 * math.pi * k / 30
        r0, r1 = r * 0.80, r * (0.95 if k % 5 else 1.02)
        col = CYAN if k % 5 else LIME
        d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))],
               fill=col + (int(255 * alpha),), width=max(2, int(r * 0.03)))
    hr = r * 0.32 * (1 + 2.2 * hub_open)
    if hub_open < 0.98:
        d.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], outline=PINK + (int(255 * alpha * (1 - hub_open)),),
                  width=max(2, int(r * 0.05)))
    g = lay.split()[3].filter(ImageFilter.GaussianBlur(max(4, r * 0.06)))
    img = K.over(img, LIME, g, 0.5 * alpha)
    img.alpha_composite(lay)
    return img


def jack_in(page_img, t):
    """Beat 3 before the dive, over the frozen HQ page (its UI dims under the terminal)."""
    T = SB.T
    img = page_img
    img = K.over(img, (2, 2, 8), Image.new("L", (W, H), 255), 0.25 * ease(phase(t, T["b3"], T["b3"] + 0.3)))
    sp = street_poly(SB.AERIAL)
    if t >= T["rain"]:
        img = link_rain(img, sp, t, T["rain"], 1.0)
    img = terminal(img, t)
    return img


def dive_over(img, t, pose, page_layer=None):
    """The first moments of the dive: the HQ UI fades out, the rain on the link fades, the wheel lens flies past."""
    T = SB.T
    lt = t - T["dive"]
    if page_layer is not None and lt < 0.3:
        img = Image.blend(img, page_layer, 1.0 - ease(lt / 0.3))
    sp = street_poly(pose)
    ra = 1.0 - ease(clamp(lt / 0.6))
    if ra > 0:
        img = link_rain(img, sp, t, T["rain"], ra)
    return img


# ---------------------------------------------------------------- the wall-dissolve bits (2D half of the dissolve)
def wall_bits(img, A, t):
    """Bits lift and scatter off each route wall while it dissolves (0.5 s life each), in the Cell's lime / cyan."""
    t0 = SB.T["dive"] + SB.WALL_START * SB.DIVE_S
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    any_ = False
    for k, i in enumerate(SB.wall_order()):
        ts = t0 + k * SB.WALL_STAGGER
        if not (ts - 0.02 < t < ts + SB.WALL_DUR + 0.55):
            continue
        p = A["rooms"][i]["front"]
        if not p or any(q is None for q in p):
            continue
        r = random.Random(900 + k)
        x0, x1 = min(q[0] for q in p), max(q[0] for q in p)
        y0, y1 = min(q[1] for q in p), max(q[1] for q in p)
        area = max(1.0, (x1 - x0) * (y1 - y0))
        n = int(min(90, 10 + area / 90))
        for j in range(n):
            born = ts + r.random() * SB.WALL_DUR
            age = t - born
            u, v = r.random(), r.random()
            vx, vy = r.uniform(-60, 60), -r.uniform(40, 140)
            ch = r.choice("01")
            col = LIME if r.random() < 0.6 else CYAN
            sz = r.choice((10, 12, 14, 16))
            if age < 0 or age > 0.55:
                continue
            x = x0 + (x1 - x0) * u + vx * age
            y = y0 + (y1 - y0) * v + vy * age - 40 * age * age
            a = int(255 * (1 - age / 0.55) ** 1.3)
            d.text((x, y), ch, font=bitfont(sz), fill=col + (a,), anchor="mm")
            any_ = True
    if not any_:
        return img
    g = lay.split()[3].filter(ImageFilter.GaussianBlur(4))
    img = K.over(img, LIME, g, 0.5)
    img.alpha_composite(lay)
    return img


# ---------------------------------------------------------------- the netrun route UI (the run start)
def route_grade(plate, A, st, cur, hover, hk, focus):
    """compose_aaa.grade (the r3 route grade) for any state, plus the decision spotlight vignette and the hover cut."""
    out = np.asarray(plate.convert("RGB"), np.float32) / 255.0
    br = G.branch(hover)[0] if hover else set()
    dm = Image.new("L", (W, H), 0)
    dd = ImageDraw.Draw(dm)
    for e in A["edges"]:
        pts = [tuple(q) for q in e["pts"] if q is not None]
        if len(pts) > 1:
            dd.line(pts, fill=255, width=10)
    dm = np.asarray(dm.filter(ImageFilter.GaussianBlur(24)), np.float32) / 255.0
    out = out * (1 - 0.2 * np.clip(dm * 2.0, 0, 1))[..., None]
    if focus > 0:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dd_ = np.sqrt(((xx - R.UCX) / (W * 0.62)) ** 2 + ((yy - R.UCY) / (H * 0.62)) ** 2)
        out = out * (1 - 0.18 * np.clip(dd_ - 0.55, 0, 1)[..., None] * focus)
    if hover and hk > 0:
        keep = np.zeros((H, W), np.float32)
        for i in sorted(br | {cur}):
            p = C3.room_poly(A, i)
            if p:
                keep = np.maximum(keep, C3.poly_mask(p, grow=8, blur=8))
        l3 = (out[..., 0] * 0.3 + out[..., 1] * 0.59 + out[..., 2] * 0.11)[..., None]
        dim = (out * 0.75 + l3 * 0.25) * 0.62
        cut = out * (1 - hk) + dim * hk
        out = out * keep[..., None] + cut * (1 - keep[..., None])
    img = Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    if hover and hk > 0.05:
        for i in sorted(br, key=lambda n: (G.LAYER[n], G.K[n])):
            p = C3.room_poly(A, i)
            if p:
                m = Image.fromarray((C3.poly_mask(p) * 255).astype(np.uint8))
                img = K.add_glow(img, m, S.TYPE_COL[G.KIND[i]], 30, 0.5 * hk)
    return img


def route_ui(plate, A, state):
    walked = SB.WALK
    hover = state.get("hover")
    hk = state.get("hover_k", 0.0)
    zoom = state.get("zoom", 0.0)
    st, opts = G.states(walked)
    est = G.edge_states(walked, st)
    cur = walked[-1]
    img = route_grade(plate, A, st, cur, hover if hk > 0 else None, hk, 1.0 - zoom)
    return route_overlay(img, A, state)


def route_overlay(img, A, state):
    walked = SB.WALK
    hover = state.get("hover")
    hk = state.get("hover_k", 0.0)
    zoom = state.get("zoom", 0.0)
    st, opts = G.states(walked)
    est = G.edge_states(walked, st)
    cur = walked[-1]
    k = min(1.6, max(0.8, C3.room_scale(A, cur) * 0.62))
    img = WX.draw_wax(img, A, est, st, opts, cur, hover=hover, hover_k=hk, k=k)
    img = C3.draw_nodes(img, A, st, opts, hover=hover, hover_k=hk)
    img = C3.target_mark(img, A)
    img = C3.token_at(img, A, cur, k)
    if hover and hk > 0.5:
        p = C3.room_poly(A, hover)
        ks = min(1.9, max(0.75, C3.room_scale(A, hover) * 0.8))
        img = S.tag(img, p[3][0] + 8 * ks, p[3][1] - 20 * ks, hover, "option")
    img = S.chrome_top(img, C3.DISPATCH["start"])
    img = S.sidebar(img, len(opts), hover=hover if (hover and hk > 0.5) else None)
    img = S.legend(img, hot=False, cx=1010)
    img = C3.view_toggle(img, zoom)
    if state.get("cursor"):
        img = KT.cursor(img, *state["cursor"])
    return img


# ---------------------------------------------------------------- beat titles
BEATS = [(0.0, "1  HQ"), (SB.T["b2"], "2  SELECT"), (SB.T["b3"], "3  JACK IN"), (SB.T["b4"], "4  REVEAL"),
         (SB.T["mark"], "5  MARK"), (SB.T["b5"], "6  ZOOM"), (SB.T["b6"], "7  CHOOSE")]


def beat_of(t):
    return [b for b in BEATS if t >= b[0]][-1][1]


def title(img, t):
    s = beat_of(t)
    f = KT.F(K.MONO, 16)
    d = ImageDraw.Draw(img, "RGBA")
    tw = f.getlength(s) + f.getlength("   %5.2f s" % t)
    x0 = W - 14 - tw - 16
    d.rectangle([x0, 0, W - 6, 22], fill=(0, 0, 0, 170))
    d.text((x0 + 8, 11), s, font=f, fill=(255, 255, 255, 235), anchor="lm")
    d.text((W - 14, 11), "%5.2f s" % t, font=f, fill=(170, 180, 190, 220), anchor="rm")
    return img
