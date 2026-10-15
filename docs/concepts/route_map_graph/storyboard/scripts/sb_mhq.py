"""Storyboard v3: the mainline HQ page (beats 1-2 and the jack-in backdrop). The city plate is the mainline kit
(m44/unified39 + post40, whose numbers are the mainline's: ink, toon ramp, fog 0.22, haze 0.34, bloom 0.75, spill 0.5,
rain, grade (0.94, 0.92, 1.04)); the live city is post40's own motion language per frame: sky-lane cars with light
streaks, blinking aviation lights, packets on the links, drifting fog patches, falling rain. The network decal and the
markers are round 44 / mainline (hq44.py); the page furniture is the mainline layout (sb_ui).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "m44"))
os.environ.setdefault("NET36", "net_scope.json")
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import post40 as P40  # noqa: E402
import layout36 as L  # noqa: E402
import kit44 as KT  # noqa: E402
import markers42 as M  # noqa: E402
import ui31 as K  # noqa: E402
import sb_mainline as ML  # noqa: E402

ROOT = os.path.dirname(HERE)
P40.SRC = "D:/rc_scratch/storyboard/oc_m"     # v3: the one-city scene's mainline passes (heavy scratch on D:)
NET, NODES = P40.NET, P40.NODES
SELECTED, RELAY = ML.SITE, ML.RELAY
EXPLOITS = {"m2_intel": "INTEL", "m2_breach": "BREACH"}
HEAT_OBJ = ("lose_the_tracking", "forge_the_manifest", "reroute_the_audit", "sink_the_cargo_logs")


N_OWNED_SHOWN = 6      # designer: main's map is mostly city: the CORE + the 6 owned Sites nearest the relay


def shown_ids():
    rx, ry = NODES[RELAY]["lot"]
    owned = sorted([n for n in NET["nodes"] if n["state"] == "owned"],
                   key=lambda n: ((n["lot"][0] - rx) ** 2 + (n["lot"][1] - ry) ** 2, n["id"]))[:N_OWNED_SHOWN]
    s = {n["id"] for n in owned} | {n["id"] for n in NET["nodes"] if n["state"] in ("core", "grey")}
    return s | set(EXPLOITS) | set(HEAT_OBJ) | {SELECTED, RELAY}


def plate(tag, t, selected=False, net_k=1.0):
    """The mainline city at time t (live: sky cars, beacons, packets, fog patches, rain), with the network decal."""
    shown = shown_ids()

    def deco(net):
        if net_k <= 0.01:
            return
        for l in NET["links"]:
            if l["a"] not in shown or l["b"] not in shown:
                continue
            st = l["state"]
            # mainline decal (city_layout grid_graph): claimed links CELL_TURF #D4FF00 thin with a soft NET_CYAN halo
            if st == "owned":
                net.link(l["pts"], np.array([0.83, 1.0, 0.0]), k=1.25 * net_k, w_px=1.1, halo=(0.36, 0.88, 1.0))
            elif st == "border":
                sel = SELECTED in (l["a"], l["b"])
                net.link(l["pts"], P40.LINK_COL["border"], style="dashed", k=(0.9 if sel else 0.45) * net_k, packets=False,
                         w_px=1.0, halo=(0.36, 0.88, 1.0))
            elif st == "grey":
                net.link(l["pts"], P40.LINK_COL["grey"], k=0.45 * net_k, packets=False, w_px=1.0)
    img, cam = P40.finish(tag, decorate=deco, t=t, fog=0.22)
    if net_k <= 0.01:
        return KT.f2p(capture_match(img)), cam
    # the calibration grade applies to the city only: the network decal (lit, on top) keeps its mainline colours
    city, _ = P40.finish(tag, decorate=None, t=t, fog=0.22)
    decal = np.clip(img - city, 0, None)
    return KT.f2p(np.clip(capture_match(city) + decal, 0, 1)), cam


# a calibration grade fitted to the mainline captures (W3_HQ after, the map area): the Blender/Eevee recreation of the
# kit came out brighter and about twice as saturated as the Godot render; this brings the median luma, the chroma and
# the mean colour to the capture's (median 0.214, chroma 0.085, mean (0.25, 0.243, 0.278))
MATCH = dict(sat=0.64, gain=(0.76, 0.76, 0.84))     # designer: a touch more violet in the mids, luma kept


def capture_match(img):
    a = np.asarray(img, np.float32)
    l = a.mean(-1, keepdims=True)
    a = l + (a - l) * MATCH["sat"]
    return np.clip(a * np.array(MATCH["gain"], np.float32), 0, 1)


def prj(cam, lot, z=0.0):
    x, y = L.W(lot)
    return L.project(cam, x, y, z, 1920, 1080)


def markers(img, cam, hover=None):
    shown = shown_ids()
    for k in sorted(shown, key=lambda k: prj(cam, NODES[k]["lot"])[1]):
        n = NODES[k]
        x, y = prj(cam, n["lot"])
        if not (-60 < x < 1980 and -60 < y < 1140):
            continue
        if n["state"] == "core":
            img = M.marker(img, x, y, "core", 0, scale=1.0)
        elif n["state"] == "owned":
            img = M.marker(img, x, y, "site", 0, "claimed", scale=0.85)
        elif n["state"] == "grey":
            img = M.marker(img, x, y, "site", n["tier"], "cleared", "yours", scale=1.05)
        elif k in EXPLOITS:
            av = "next" if n["state"] == "available" else "notyet"
            img = M.marker(img, x, y, "exploit", 2, "corporate", av, EXPLOITS[k], scale=0.95 if av == "notyet" else 1.05)
        elif k in HEAT_OBJ:
            av = "next" if n["state"] == "available" else "notyet"
            img = M.marker(img, x, y, "heat", n["tier"], "corporate", av, scale=0.95 if av == "notyet" else 1.05)
        elif k == SELECTED:
            img = M.marker(img, x, y, "site", n["tier"], "corporate", "next", scale=1.25)
    return img


def link_poly(cam):
    """The border link Returns Processing -> Priority Lane Exchange (the netrun street) on screen."""
    for l in NET["links"]:
        if {l["a"], l["b"]} == {RELAY, SELECTED}:
            pts = l["pts"] if l["a"] == RELAY else list(reversed(l["pts"]))
            out = []
            for p in pts:
                n = 8
                out.append(prj(cam, p))
            # densify for the rain and the pencil
            dense = []
            for a, b in zip(out, out[1:]):
                for i in range(n):
                    dense.append((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n))
            dense.append(out[-1])
            return dense
    return []


def central_server(cam):
    """The boss TARGET: Meridian HQ's Central Server, if it is on screen (mainline: a red pencil circle on it)."""
    return prj(cam, NET["hq"]["meridian"])


def net_box(cam):
    pts = [prj(cam, n["lot"]) for n in NET["nodes"] if n["state"] in ("owned", "core", "available")]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs) - 70, min(ys) - 90, max(xs) + 70, max(ys) + 70)


def grade(img, cam, focus_lot):
    """Mainline UI scrim (ui_scrim_look.tres): x0.86 inside the network rect, x0.68 outside (sat 0.85), the selected
    Site fully lit in a soft vignette."""
    nb = net_box(cam)
    netm = KT.soft_rect(nb, blur=80)
    fx, fy = prj(cam, focus_lot)
    lit = KT.soft_ellipse(fx, fy - 10, 220, 150, blur=70)
    return KT.grade_map(img, netm, lit, band=0.68, inside=0.86, desat_out=0.15)


# ---------------------------------------------------------------- the page (beats 1-2; the jack-in backdrop)
_SUI = {}


def _furniture(img, runner):
    import sb_ui as U
    ui = K.over(img, (3, 2, 8), KT.soft_l((0, 0, 1920, 96), blur=24), 0.35)
    ui = K.over(ui, (3, 2, 8), KT.soft_l((0, 800, 900, 1080), blur=40), 0.3)
    ui = U.topbar_full(ui)
    ui = U.map_key(ui)
    ui = U.tabs(ui)
    ui = U.crew(ui, runner=runner)
    return U.jack_line(ui)


def furniture(img, runner):
    """The fixed page furniture, solved once on flat plates (affine in the background) and applied per frame."""
    if runner not in _SUI:
        o0 = np.asarray(_furniture(Image.new("RGBA", (1920, 1080), (0, 0, 0, 255)), runner).convert("RGB"), np.float32) / 255
        o1 = np.asarray(_furniture(Image.new("RGBA", (1920, 1080), (128, 128, 128, 255)), runner).convert("RGB"), np.float32) / 255
        _SUI[runner] = (np.clip((o1 - o0) / (128 / 255.0), 0, 1), o0)
    m, b = _SUI[runner]
    a = np.asarray(img.convert("RGB"), np.float32) / 255
    return Image.fromarray((np.clip(a * m + b, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")


def target_pencil(img, cam):
    x, y = central_server(cam)
    if not (80 < x < 1840 and 120 < y < 1000):
        # off-screen: the City Grid's red pencil edge marker toward it, its chip clear of the pencil (bible 4.1)
        cx_, cy_ = 960.0, 500.0
        ang = math.atan2(y - cy_, x - cx_)
        ex = min(1780.0, max(140.0, cx_ + math.cos(ang) * 900))
        ey = min(980.0, max(170.0, cy_ + math.sin(ang) * 420))
        tip = (ex, ey)
        base = (ex - math.cos(ang) * 170, ey - math.sin(ang) * 170)
        pen = KT.pencil(KT.PEN_R, 441)
        pen.arrow([base, ((base[0] + tip[0]) / 2 + 6, (base[1] + tip[1]) / 2 + 4), tip], width=9, head=26)
        pen.text("TARGET", base[0] + 70, base[1] + 30, 40, angle=8)
        img = KT.spill(img, pen.mask.resize((1920, 1080)), KT.PEN_R, 0.14, 30)
        img = KT.ink(img, pen)
        img, _ = KT.chip(img, (min(1500, base[0] - 40), base[1] + 70), "CENTRAL SERVER  //  EXPLOITS 1/3", K.GOLD, 14, anchor="lm")
        return img
    pen = KT.pencil(KT.PEN_R, 441)
    ring = [(x + 66 * math.cos(-2.4 + 2 * math.pi * 1.08 * k / 48), y - 30 + 38 * math.sin(-2.4 + 2 * math.pi * 1.08 * k / 48))
            for k in range(49)]
    pen.stroke(ring, width=8)
    pen.text("TARGET", x - 40, y - 4, 40, angle=-6)
    img = KT.spill(img, pen.mask.resize((1920, 1080)), KT.PEN_R, 0.14, 30)
    img = KT.ink(img, pen)
    img, _ = KT.chip(img, (x - 160, y - 110), "CENTRAL SERVER  //  EXPLOITS 1/3", K.GOLD, 14, anchor="lm")
    return img


def page(plate_img, cam, t, ui_k=1.0):
    """The mainline HQ page at time t (beats 1-2; from the press on, the jack-in layers go on top)."""
    import sb_ui as U
    import sb_cams as SB
    T = SB.T
    sel = t >= T["click"]
    img = grade(plate_img, cam, NODES[SELECTED]["lot"])
    hover = T["hover_site"] <= t < T["to_jack"]
    img = markers(img, cam)
    img = target_pencil(img, cam)
    ui = furniture(img, sel)
    sx, sy = prj(cam, NODES[SELECTED]["lot"])
    rest, jack = (1010, 600), (1730, 910)
    if t < T["b2"]:
        cx, cy = rest[0] + 6 * math.sin(t * 1.3), rest[1] + 4 * math.cos(t * 0.9)
    elif t < T["hover_site"]:
        u = U.ease(U.phase(t, T["b2"], T["hover_site"]))
        cx, cy = rest[0] + (sx + 8 - rest[0]) * u, rest[1] + (sy - 12 - rest[1]) * u
    elif t < T["to_jack"]:
        cx, cy = sx + 8, sy - 12
    else:
        u = U.ease(U.phase(t, T["to_jack"], T["press"] - 0.1))
        cx, cy = sx + 8 + (jack[0] - sx - 8) * u, sy - 12 + (jack[1] - sy + 12) * u
    if hover:       # mainline (ART_R1 1a): only the hovered Site's tag
        ui, _ = KT.chip(ui, (sx + 30, sy - 52), "Priority Lane Exchange", K.LIME, 13, anchor="lm", bright=True)
    if t >= T["hover_site"]:
        ui = U.site_holo(ui, U.phase(t, T["hover_site"], T["hover_site"] + 0.55), t)
    if sel:
        pu = U.phase(t, T["click"], T["click"] + 0.35)
        if pu < 1:
            m = Image.new("L", (1920, 1080), 0)
            r_ = 20 + 60 * U.ease_out(pu)
            ImageDraw.Draw(m).ellipse([sx - r_, sy - 18 - r_, sx + r_, sy - 18 + r_], outline=255, width=4)
            ui = K.add_glow(ui, m, U.ORANGE, 8, 1.0)
        pen = KT.pencil(U.ORANGE, 442)
        cu = U.phase(t, T["click"] + 0.05, T["click"] + 0.35)
        if cu > 0:
            ring = [(sx + 44 * math.cos(-2.2 + 2 * math.pi * 1.1 * k / 40), sy - 18 + 32 * math.sin(-2.2 + 2 * math.pi * 1.1 * k / 40))
                    for k in range(41)]
            pen.stroke(U.poly_cut(ring, cu), width=9)
        lu = U.phase(t, T["click"] + 0.35, T["gloss"])
        if lu > 0:
            lp = [(x, y - 6) for x, y in link_poly(cam)]
            cut = U.poly_cut(lp, U.ease(lu))
            if len(cut) > 1:
                (pen.arrow(cut, width=8, head=22) if lu >= 1 else pen.stroke(cut, width=8))
        ui = KT.spill(ui, pen.mask.resize((1920, 1080)), U.ORANGE, 0.14, 30)
        ui = KT.ink(ui, pen)
        pop = U.phase(t, T["click"] + 0.05, T["click"] + 0.3)
        gloss = -0.1 + 1.2 * U.phase(t, T["gloss"], T["gloss"] + 0.8) if T["gloss"] <= t <= T["gloss"] + 0.8 else None
        press = math.sin(math.pi * U.phase(t, T["press"], T["press"] + 0.25)) if t >= T["press"] else 0.0
        ui = U.jack_sticker(ui, gloss, press, pop)
    ui = U.on_air(ui, t)
    if t < T["b3"]:
        ui = KT.cursor(ui, cx, cy)
    return ui if ui_k >= 1 else Image.blend(img.convert("RGBA"), ui, ui_k)
