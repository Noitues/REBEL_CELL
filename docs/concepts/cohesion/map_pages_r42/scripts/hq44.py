"""Round 44 A: the HQ page (direction B, ruled) built to the design and cleaned (REVIEW D7, f, c).

NET36=net_scope.json python hq44.py [idle] [core]
  idle -> hq_idle.png            JACK IN is the idle verb; the selected Site (Priority Lane Exchange) as a holo file
  core -> hq_node_selected.png   the CORE home node selected: terminal card with PATCH / HEAT SCRUB, UPGRADE sticker
Plate: h_hq (run44.py hq), the unified city at the City Grid look (solid buildings), framed on the Cell's network.
"""
import math
import os
import sys

os.environ.setdefault("NET36", "net_scope.json")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402
import post40 as P  # noqa: E402
import layout36 as L  # noqa: E402
import markers42 as M  # noqa: E402
import r31lib as RL  # noqa: E402

NET, NODES = P.NET, P.NODES
SELECTED = "m2_d"                      # Priority Lane Exchange (T2), across the border link from Returns Processing
EXPLOITS = {"m2_intel": "INTEL", "m2_breach": "BREACH"}
HEAT_OBJ = ("lose_the_tracking", "forge_the_manifest", "reroute_the_audit", "sink_the_cargo_logs")


def shown_ids():
    """Bible 4.5 pins only: yours, cleared, Exploit and Heat-objective Sites, the boss (off-screen here) + the selection."""
    s = {n["id"] for n in NET["nodes"] if n["state"] in ("owned", "core", "grey")}
    s |= set(EXPLOITS) | set(HEAT_OBJ) | {SELECTED}
    return s


def plate():
    shown = shown_ids()

    def deco(net):
        for l in NET["links"]:
            if l["a"] not in shown or l["b"] not in shown:
                continue
            st = l["state"]
            if st == "owned":
                net.link(l["pts"], P.LINK_COL["owned"], k=1.0)
            elif st == "border":
                sel = SELECTED in (l["a"], l["b"])
                net.link(l["pts"], P.LINK_COL["border"], style="dashed", k=1.0 if sel else 0.55, packets=False)
            elif st == "grey":
                net.link(l["pts"], P.LINK_COL["grey"], k=0.5, packets=False)
    hx, hy = L.W((44.0, 28.0))
    img, cam = P.finish("h_hq", decorate=deco, pools=[(hx, hy, 16.0, 0.28)], t=0.25, fog=0.2)
    return KT.f2p(img), cam


def prj(cam, lot):
    return L.project(cam, *L.W(lot), 0.0, 1920, 1080)


def markers(img, cam, selected_core=False):
    shown = shown_ids()
    order = sorted(shown, key=lambda k: prj(cam, NODES[k]["lot"])[1])
    for k in order:
        n = NODES[k]
        x, y = prj(cam, n["lot"])
        sc = 1.15
        if n["state"] == "core":
            img = M.marker(img, x, y, "core", 0, scale=1.25)
        elif n["state"] == "owned":
            img = M.marker(img, x, y, "site", 0, "claimed", scale=sc)
        elif n["state"] == "grey":
            img = M.marker(img, x, y, "site", n["tier"], "cleared", "yours", scale=sc)
        elif k in EXPLOITS:
            av = "next" if n["state"] == "available" else "notyet"
            img = M.marker(img, x, y, "exploit", 2, "corporate", av, EXPLOITS[k], scale=sc * (0.9 if av == "notyet" else 1.0))
        elif k in HEAT_OBJ:
            av = "next" if n["state"] == "available" else "notyet"
            img = M.marker(img, x, y, "heat", n["tier"], "corporate", av, scale=sc * (0.9 if av == "notyet" else 1.0))
        elif k == SELECTED:
            img = M.marker(img, x, y, "site", n["tier"], "corporate", "next", scale=1.3)
    return img


def net_box(cam):
    pts = [prj(cam, n["lot"]) for n in NET["nodes"] if n["state"] in ("owned", "core")] + [prj(cam, NODES[SELECTED]["lot"])]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs) - 110, min(ys) - 120, max(xs) + 110, max(ys) + 90)


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


def tabs(img, active="CREW"):
    rows = [("CREW", "3 / 4", K.CYAN), ("MARKET", "142 SCHEM.", K.CYAN), ("DEFENCE", "RAID PENDING", K.HARM)]
    y = 846
    for name, sub, ac in rows:
        box = (20, y, 214, y + 62)
        img = KT.panel_shadow(img, box, 8, blur=10)
        img = K.term_button(img, box, name, sub, state="pressed" if name == active else "idle", accent=ac)
        y += 72
    return img


def crew(img, runner=True):
    cards = [("CELL-9", "breaker", "R2", "READY", K.GREEN, False),
             ("NOVA", "ghost", "R1", "ON RETURNS PROC.", K.CYAN, False),
             ("RIG-4", "rigger", "R0", "READY", K.GREEN, False),
             ("HEX", "phantom", "R1", "FLATLINED", (150, 150, 162), True)]
    x = 236
    anchors = {}
    for i, (nm, cls, rk, st, sc, dead) in enumerate(cards):
        sel = runner and i == 0
        p = KT.polaroid(nm, cls, rk, st, sc, dead=dead, w=140, seed=40 + i, selected=sel)
        ang = [-2.2, 1.4, -0.8, 2.0][i]
        y = 858 if sel else 878
        img = KT.paste_polaroid(img, p, x, y, ang, lift=0.5 if sel else 0.0)
        anchors[nm] = (x + 70, y)
        if sel:
            img = K.text(img, (x + 4, y - 16), "RUNNER", KT.F(K.MONO, 13), K.CYAN, "la", 1.6) and img
        x += 150
    return img, anchors


def work_order_panel(img):
    rows = [("TARGET", "CORE (CELL)"), ("UNITS", "4 IN 1 WAVE"), ("ENTRY SITES", "1 (A)"), ("TRIGGER", "HEAT 50 CROSSED", (170, 30, 25))]
    p = KT.work_order(rows, w=330, seed=52)
    return K.paste_paper(img, p, (26, 104), angle=1.4, sh=0.6)


def target_edge(img, cam):
    """The TARGET is off-screen (Meridian HQ, top right): the City Grid's red pencil edge marker + its chip clear of it."""
    hx, hy = prj(cam, NET["hq"]["meridian"])
    ox, oy = 1600, 290
    ang = math.atan2(hy - oy, hx - ox)
    tip = (ox + math.cos(ang) * 170, oy + math.sin(ang) * 170)
    pen = KT.pencil(KT.PEN_R, 441)
    pen.arrow([(ox, oy), ((ox + tip[0]) / 2 + 6, (oy + tip[1]) / 2 + 4), tip], width=9, head=26)
    pen.text("TARGET", 1748, 200, 40, angle=8)
    img, _ = KT.chip(img, (1596, 344), "CENTRAL SERVER  //  EXPLOITS 1/3", K.GOLD, 14, anchor="lm")
    return img, pen


def name_tag(img, cam, nid, text, col):
    x, y = prj(cam, NODES[nid]["lot"])
    f = KT.F(K.MONO, 13)
    w = f.getlength(text) + 20
    img, box = KT.chip(img, (x - 84 - w, y - 34), text, col, 13, anchor="lm", bright=True)
    return img


def site_holo(img):
    def extra(im, y):
        K.text(im, (1486, y + 6), "IF CLEARED", KT.F(K.MONO, 14), K.CYAN, "lm", 1.4)
        row = RL.outcome_row([("schem", "+12", True), ("heat", "+3", False), ("none", "OPENS 2", True)], size=17, gap=8)
        im.alpha_composite(row, (1486, int(y + 22)))
        return im
    rows = [("TYPE", "Priority exchange  //  router run"), ("REWARDS", "+12 Schematics, firmware"),
            ("LINK", "from RETURNS PROCESSING"), ("sep",)]
    return KT.holo_file(img, (1466, 586, 1902, 872), "T2  //  PRIORITY LANE EXCHANGE", rows, sub="MERIDIAN FREIGHT  //  SITE FILE 207",
                        extra=extra, seed=9)


def core_card(img):
    box = (1466, 560, 1902, 896)
    img = KT.term(img, box, "CORE  //  HOME SERVER", tag="YOURS", tag_col=K.LIME, seed=17)
    f, fv = KT.F(K.MONO, 16), KT.F(K.MONO, 18)
    y = 612
    K.text(img, (1486, y), "INTEGRITY", f, K.DIM, "lm", 1.2)
    img = K.live_number(img, (1640, y + 2), "44", 30, K.LIME, "lm", 1.0, 0.35)
    K.text(img, (1680, y + 6), "/ 50", f, K.DIM, "lm", 0.8)
    d = K.BD(img)
    for i in range(10):
        xa = 1740 + i * 14
        d.rectangle([xa, y - 7, xa + 10, y + 7], fill=(K.LIME + (255,)) if i < 9 else (40, 52, 30, 255))
    rows = [("DEFENCES", "TURRET  +  ICE LOCK"), ("LINKS", "3 powered"), ("STATIONED", "none")]
    y += 38
    for a, b in rows:
        K.text(img, (1486, y), a, f, K.DIM, "lm", 1.2)
        K.text(img, (1640, y), b, fv, (220, 236, 246), "lm", 0.6)
        y += 30
    d = K.BD(img)
    d.line([(1484, y - 6), (1884, y - 6)], fill=K.CYAN + (90,), width=1)
    K.text(img, (1486, y + 12), "> HQ ACTIONS", KT.F(K.MONO, 14), K.CYAN, "lm", 1.4)
    y += 30
    img = K.term_button(img, (1484, y, 1884, y + 54), "PATCH  +6 INTEGRITY", "20 SCHEMATICS   [P]", state="hover")
    y += 62
    img = K.term_button(img, (1484, y, 1884, y + 54), "HEAT SCRUB  -5 HEAT", "30 SCHEMATICS   [H]")
    return img


def toast(img, text):
    box = (840, 1030, 1420, 1068)
    img = KT.panel_shadow(img, box, 0, blur=10)
    img = K.over(img, (2, 2, 8), K.rect_mask(img.size, box), 0.88)
    img = K.holo_panel(img, box, corp="meridian", seed=21, alpha=0.78)
    K.text(img, (866, 1049), text, KT.F(K.MONO, 15), (255, 214, 170), "lm", 0.8)
    return img


def build(mode):
    base, cam = plate()
    nb = net_box(cam)
    netm = KT.soft_rect(nb, blur=80)
    focus = NODES["core"]["lot"] if mode == "core" else NODES[SELECTED]["lot"]
    fx, fy = prj(cam, focus)
    lit = KT.soft_ellipse(fx, fy - 10, 250, 170, blur=70)
    img = KT.grade_map(base, netm, lit)
    img = markers(img, cam)
    # the world under the panels steps back further (bands under the bars, bible 3.1 / 4.1)
    img = K.over(img, (3, 2, 8), KT.soft_l((0, 0, 1920, 96), blur=24), 0.35)
    img = K.over(img, (3, 2, 8), KT.soft_l((0, 830, 900, 1080), blur=40), 0.3)
    img, tpen = target_edge(img, cam)
    if mode == "idle":
        img = name_tag(img, cam, SELECTED, "PRIORITY LANE EXCHANGE", K.GOLD)
    else:
        img = name_tag(img, cam, "core", "CORE  //  HOME SERVER", K.LIME)
    img = work_order_panel(img)
    img = topbar_full(img)
    img = tabs(img, "CREW")
    img, anchors = crew(img, runner=(mode == "idle"))
    if mode == "idle":
        img = site_holo(img)
        sd = KT.rainbow_sweep(KT.sticker("JACK IN", 84, "pink", seed=31), pos=0.56, k=0.55)
        img = KT.place_sticker(img, sd, 1712, 968, angle=-3, spill_col=K.PINK, spill_k=0.3)
        K.text(img, (1902, 1062), "> jack --to PRIORITY_LANE  [SPACE]", KT.F(K.MONO, 13), (120, 170, 190), "ra", 0.6,
               alpha=150)
        img = toast(img, "INTERCEPTED // MERIDIAN: lane audit moved up a shift")
        # the one plan: CELL-9 runs Priority Lane Exchange (yellow pencil, solid = will happen)
        sx, sy = prj(cam, NODES[SELECTED]["lot"])
        ppen = KT.pencil(KT.PEN_Y, 442)
        ppen.circle(sx, sy - 18, 46, 34, width=9)
        dx_, dy_ = prj(cam, NODES["m1_d"]["lot"])          # the run goes over the border link from Returns Processing
        ppen.arrow([(dx_ + 14, dy_ - 46), (dx_ + 96, dy_ - 120), (sx - 30, sy + 26)], width=9, head=24)
        img = KT.spill(img, ppen.mask.resize((1920, 1080)), KT.PEN_Y, 0.12, 30)
        img = KT.ink(img, ppen)
    else:
        img = core_card(img)
        sd = KT.sticker("UPGRADE", 76, "pink", seed=33)
        img = KT.place_sticker(img, sd, 1700, 978, angle=-2.5, spill_col=K.PINK, spill_k=0.28)
        K.text(img, (1902, 1062), "> upgrade core --mk2   60 SCHEMATICS  [U]", KT.F(K.MONO, 13), (120, 170, 190), "ra", 0.6, alpha=150)
        cx, cy = prj(cam, NODES["core"]["lot"])
        img = K.focus_brackets(img, (cx - 30, cy - 52, cx + 30, cy + 14), gap=6, ln=12, w=3)
        img = KT.cursor(img, cx + 14, cy - 10)
    img = KT.spill(img, tpen.mask.resize((1920, 1080)), KT.PEN_R, 0.14, 30)
    img = KT.ink(img, tpen)
    return RL.bloom(img, 0.10, 0.84, 8)


if __name__ == "__main__":
    which = sys.argv[1:] or ["idle", "core"]
    if "idle" in which:
        KT.save(build("idle"), "hq_idle.png")
    if "core" in which:
        KT.save(build("core"), "hq_node_selected.png")
