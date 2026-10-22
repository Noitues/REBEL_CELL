"""Concept A, round 2: TELEGRAPH. Every number is sim.py output (plans BARE, DECOY_ONLY, LURE, SHIELD).
R2 changes: ALL view (whole raid at once) before per-step scrubbing; home first in every forecast; a SCUFFED mark
(held but damaged); glyph stats on cards; loss icons inside the stamp; routes, wave chips and a countdown on the
warning; CLEAN NEEDS and the tightest margin; two saved plans compared side by side."""

from __future__ import annotations

from r2_kit import *  # noqa: F403

NAME = "A TELEGRAPH r2"
XF = MapXf(300, 125, 0.80)
TOFF = {"COLLECTOR": (46, -12), "AUDITOR": (-62, -30), "ENFORCER": (-52, 34)}
ORDER = ["AUDITOR", "COLLECTOR", "ENFORCER"]  # in-step strike order (content id), shown as badges


def base(d, r=None, step=None, dim_links=False) -> None:
    draw_links(d, XF, dim=dim_links)
    st, hp = ({}, {}) if r is None else node_states(r, step)
    for k in NODES:
        lose = 0
        if r is not None and step is None and k in r.nodes:
            lose = r.nodes[k]["before"] - r.nodes[k]["after"]
            node(d, XF, k, st.get(k, "ok"), r.nodes[k]["before"], lose)
        else:
            node(d, XF, k, st.get(k, "ok"), hp.get(k))


def place_assets(d, plan) -> None:
    for n, aa in plan.assets.items():
        x, y = XF.p(n)
        for i, a in enumerate(aa):
            px, py = x - 44 + i * 0, y + 18 + i * 26
            d.ellipse((px - 13, py - 13, px + 13, py + 13), fill=(50, 46, 30), outline=CELL, width=2)
            asset_icon(d, (px, py), a, 8, HOLD if a == "ICE" else CELL)
    if plan.crew:
        x, y = XF.p(plan.crew)
        asset_icon(d, (x + 44, y + 22), "CREW", 10)


def all_view(d, r) -> None:
    """Whole raid at once: every threat's full path, each node's end tag, the striped pips are the total loss."""
    for tid, path in r.paths.items():
        arrow_path(d, XF, path, THREAT, 5)
    for k, info in r.nodes.items():
        mark2(d, XF, k, info)


def threats_at(d, r, step: int) -> None:
    ev = r.steps[step - 1]
    for tid, (site, hp, alive, hold) in ev["threats"].items():
        if site.startswith("C") and not alive:
            continue
        x, y = XF.p(site)
        ox, oy = TOFF[tid]
        killed = any(k[0] == tid for k in ev["kills"])
        if not alive and not killed:
            continue
        threat(d, (x + ox, y + oy), tid, 14, hp=hp, ghost=killed)
        if killed:
            pencil_x(d, (x + ox, y + oy), 14, seed=3)
        if hold > 0:
            asset_icon(d, (x + ox + 20, y + oy - 18), "ICE", 8, HOLD)


def hud(d, n_left: int = 2) -> None:
    heat_bar(d, 470, 22, 340, 51)
    countdown(d, (70, 70), n_left)


def hand(d, sel=None, used=()) -> None:
    for i, a in enumerate(("TURRET", "ICE", "DECOY", "CREW")):
        asset_card2(d, 20 + i * 104, 596, a, selected=a == sel, used=a in used)


def end_panel(d, r, x=450, y=596) -> None:
    """End-of-raid list, home first, then every changed node, with integrity before > after."""
    panel(d, (x, y, x + 560, y + 112))
    rows = [("HOME", r.nodes["HOME"])] + [(k, v) for k, v in r.nodes.items() if k != "HOME" and v["before"] != v["after"]]
    for i, (k, v) in enumerate(rows[:6]):
        cx = x + 18 + (i % 3) * 180
        cy = y + 14 + (i // 3) * 48
        col = {"down": DOWN_GREY, "taken": THREAT_LIGHT}.get(v["outcome"], CELL)
        node_icon(d, (cx + 14, cy + 14), k, 28, col)
        text(d, (cx + 34, cy + 2), f"{v['before']}>{v['after']}", 18, INK, "mono")
        if v["outcome"] == "down":
            bolt(d, (cx + 140, cy + 14), 10)
        elif v["outcome"] == "taken":
            flag(d, (cx + 140, cy + 14), 9, THREAT_LIGHT)


def f1():
    img, d = new_frame(NAME, "warning")
    r = RUNS["BARE"]
    base(d, dim_links=False)
    hud(d)
    why_chain(d, 470, 52)
    for tid, path in r.paths.items():
        arrow_path(d, XF, path, (44, 70, 170), 4, dash_line=True)
    c1, c2 = XF.p("C1"), XF.p("C2")
    threat_chip(d, (c1[0] + 70, c1[1] - 10), "COLLECTOR")
    threat_chip(d, (c2[0] + 70, c2[1] - 50), "AUDITOR")
    threat_chip(d, (c2[0] + 70, c2[1] + 40), "ENFORCER")
    # When: the netrun's remaining map nodes, home at the end.
    panel(d, (20, 140, 250, 230))
    for i in range(3):
        cx = 44 + i * 52
        d.ellipse((cx - 11, 174, cx + 11, 196), fill=CELL if i < 1 else PANEL, outline=CELL, width=2)
        d.line([(cx + 11, 185), (cx + 41, 185)], fill=CELL_DIM, width=3)
    node_icon(d, (44 + 3 * 52, 185), "HOME", 34, CELL)
    shield(d, (44 + 3 * 52 + 14, 168), 7, THREAT)
    header(d, NAME, 1, "Warning: why (Heat 51 crosses 50), when (2 map nodes until home), who (two-number chips with route glyphs), where (dashed routes)")
    return img


def f2():
    img, d = new_frame(NAME, "planning")
    r = RUNS["BARE"]
    base(d, r)
    hud(d)
    step_cells(d, 300, 56, r, 0, all_lit=True)
    all_view(d, r)
    hand(d, sel="DECOY")
    fx, fy = XF.p("FW")
    dashed(d, (280, 596), (fx - 20, fy + 40), CELL, 3)
    d.rounded_rectangle((fx - 70, fy + 20, fx - 30, fy + 60), radius=6, fill=(50, 46, 30), outline=CELL, width=2)
    asset_icon(d, (fx - 50, fy + 40), "DECOY", 10)
    # What-if, from the DECOY_ONLY run vs BARE: home loss and lost-node count.
    w = RUNS["DECOY_ONLY"]
    lb, lw = losses(r), losses(w)
    nb = len(lb["down"]) + len(lb["taken"])
    nw = len(lw["down"]) + len(lw["taken"])
    tx, ty = 20, 300
    d.rounded_rectangle((tx, ty, tx + 230, ty + 64), radius=6, fill=CELL)
    node_icon(d, (tx + 22, ty + 18), "HOME", 26, BG)
    text(d, (tx + 40, ty + 6), f"-{r.home_before - r.home_after} > -{w.home_before - w.home_after}", 18, BG, "mono")
    bolt(d, (tx + 22, ty + 46), 9, BG)
    flag(d, (tx + 40, ty + 46), 8, BG)
    text(d, (tx + 56, ty + 36), f"{nb} > {nw}", 18, BG, "mono")
    header(d, NAME, 2, "Planning: ALL view of the raid as it stands (home -20, 3 DOWN, 1 TAKEN); dragging DECOY onto FIREWALL previews: home -20 > -12, lost 4 > 0")
    return img


def plan_compare(d, sel: str = "LURE", x=1030, y=110) -> None:
    panel(d, (x, y, x + 238, y + 236))
    for i, (pid, label) in enumerate((("LURE", "1"), ("SHIELD", "2"))):
        r = RUNS[pid]
        yy = y + 12 + i * 110
        on = pid == sel
        d.rounded_rectangle((x + 10, yy, x + 228, yy + 98), radius=6, fill=(50, 46, 30) if on else BG2,
                            outline=CELL if on else PANEL_EDGE, width=3 if on else 1)
        text(d, (x + 22, yy + 6), label, 22, CELL if on else DIM, "mono")
        lo = losses(r)
        node_icon(d, (x + 64, yy + 22), "HOME", 26, CELL)
        text(d, (x + 80, yy + 10), f"-{r.home_before - r.home_after}", 18, DMG if r.home_after < r.home_before else HOLD, "mono")
        d.ellipse((x + 132, yy + 10, x + 156, yy + 34), fill=(48, 50, 58), outline=DOWN_GREY, width=2)
        bolt(d, (x + 144, yy + 22), 9)
        text(d, (x + 162, yy + 10), str(len(lo["down"])), 18, INK, "mono")
        flag(d, (x + 192, yy + 22), 9, THREAT_LIGHT)
        text(d, (x + 206, yy + 10), str(len(lo["taken"])), 18, INK, "mono")
        coin(d, (x + 32, yy + 66), 9)
        text(d, (x + 48, yy + 54), f"-{repair_cost(r)}", 18, INK, "mono")
        if lo["taken"]:
            text(d, (x + 110, yy + 54), f"+{len(lo['taken'])}", 18, INK, "mono")
            d.regular_polygon((x + 160, yy + 66, 10), 6, outline=CELL, width=2)
            text(d, (x + 175, yy + 56), "NET", 13, DIM)


def f3():
    img, d = new_frame(NAME, "forecast")
    r = RUNS["LURE"]
    base(d, r)
    hud(d)
    step_cells(d, 300, 56, r, 0, all_lit=True)
    all_view(d, r)
    place_assets(d, PLANS["LURE"])
    plan_compare(d, "LURE")
    # CLEAN NEEDS + tightest margin, from the run: the Enforcer reaches home with 17 left; Proxy ends at 3.
    panel(d, (1030, 356, 1268, 470), edge=STAMP_CLEAN)
    text(d, (1044, 364), "CLEAN", 14, STAMP_CLEAN)
    threat(d, (1060, 410), "ENFORCER", 12, show_hp=False)
    arrow(d, (1080, 410), (1120, 410), THREAT, 3, 8, shorten=0)
    node_icon(d, (1136, 410), "HOME", 26, CELL)
    text(d, (1158, 398), "17", 22, THREAT_LIGHT, "mono")
    flame(d, (1052, 452), 8, DIM)
    text(d, (1066, 442), "+5   +12", 16, DIM, "mono")
    end_panel(d, r)
    hand(d, used=("TURRET", "ICE", "DECOY"))
    d.rectangle((0, 0, 0, 0))
    button(d, (1030, 640, 1268, 690), "START RAID")
    header(d, NAME, 3, "Forecast: plan 1 (lure into the firewall) vs plan 2 (shield home) side by side; home first; clean needs 17 more on the Enforcer")
    return img


def f4():
    img, d = new_frame(NAME, "resolution")
    r = RUNS["LURE"]
    s = 3
    base(d, r, step=s)
    place_assets(d, PLANS["LURE"])
    heat_bar(d, 470, 22, 340, 51)
    step_track(d, 470, 70, 340, len(r.steps), s)
    text(d, (640, 96), "AUTO", 13, DIM, anchor="ma")
    threats_at(d, r, s)
    ev = r.steps[s - 1]
    for i, (site, gun, tid, dmg, left) in enumerate(ev["shots"]):
        tsite = ev["threats"][tid][0]
        sx, sy = XF.p(site)
        tx, ty = XF.p(tsite)
        ox, oy = TOFF[tid]
        d.line([(sx, sy), (tx + ox, ty + oy)], fill=CELL, width=4)
        text(d, (tx + ox + 18, ty + oy - 40), f"-{dmg}", 22, CELL, "mono")
    for tid, site, dmg, left in ev["hits"]:
        x, y = XF.p(site)
        dmg_badge(d, (x - 46, y - 40), dmg)
    speed_controls(d, 1060, 660)
    header(d, NAME, 4, "Resolution (step 3 of 5, no input): ICE holds both at the home door, the home turret kills the Auditor, the firewall gun wears the Collector")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    r = RUNS["LURE"]
    base(d, r)
    heat_bar(d, 470, 22, 340, 51, raid_at=None)
    for k, info in r.nodes.items():
        mark2(d, XF, k, info)
    stamp_losses(img, d, (1010, 190), r)
    panel(d, (20, 560, 640, 700))
    node_icon(d, (60, 600), "HOME", 34, CELL)
    text(d, (84, 588), "-9", 22, DMG, "mono")
    arrow(d, (130, 600), (170, 600), INK, 3, 9, shorten=0)
    coin(d, (190, 600), 10)
    text(d, (206, 588), "9", 22, INK, "mono")
    lo = losses(r)
    d.ellipse((260, 588, 284, 612), fill=(20, 60, 60), outline=HOLD, width=2)
    check(d, (272, 600), 6, HOLD)
    text(d, (292, 588), f"x{len(lo['scuffed'])}", 22, INK, "mono")
    flame(d, (60, 660), 10, DIM)
    text(d, (80, 648), "+0   (+5 +12 MISSED)", 20, DIM, "mono")
    button(d, (1090, 640, 1265, 690), "BACK TO HQ")
    header(d, NAME, 5, "Aftermath: stamp carries the losses as icons (home -9); patch cost 9; 4 nodes scuffed, kept on the map; the missed clean bonus shown")
    return img


FRAMES = [f1, f2, f3, f4, f5]
