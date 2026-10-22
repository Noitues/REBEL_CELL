"""Concept B, round 2: SIEGE LANES. Every number is sim.py output. R2 changes: one HP ribbon per lane (the lane's width IS
the threat's integrity, narrowing at each hit, a skull where it dies) instead of chip stacks; numbered step dots on the
lane; route glyphs on wave chips; reach shown as lit nodes and lane segments, no polygon; a countdown; loss icons in
the stamp; and a sixth frame: the NEXT raid's warning, where this raid's TAKEN nodes are new entries."""

from __future__ import annotations

from r2_kit import *  # noqa: F403

NAME = "B SIEGE LANES r2"
XF = MapXf(260, 110, 0.84)
PERP = {"COLLECTOR": 0, "AUDITOR": 14, "ENFORCER": -14}


def arrivals(r, tid: str) -> list[tuple[str, int, int]]:
    """(site, step, hp after that step) each time the threat arrives somewhere, starting at its entry with full hp."""
    out = [(r.paths[tid][0], 0, THREATS[tid][1])]
    last = out[0][0]
    for ev in r.steps:
        site, hp, alive, hold = ev["threats"][tid]
        if site != last:
            out.append((site, ev["step"], hp))
            last = site
        elif out and hp != out[-1][2]:
            out[-1] = (out[-1][0], out[-1][1], hp)
    return out


def off(a, b, k: float):
    import math as _m
    L = _m.dist(a, b) or 1
    px, py = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
    return (a[0] + px * k, a[1] + py * k), (b[0] + px * k, b[1] + py * k)


def ribbon(d, r, tid: str, col=THREAT, dim: bool = False) -> None:
    arr = arrivals(r, tid)
    mhp = THREATS[tid][1]
    k = PERP[tid]
    for (s0, st0, hp0), (s1, st1, hp1) in zip(arr, arr[1:]):
        a, b = off(XF.p(s0), XF.p(s1), k)
        w = int(5 + 20 * hp0 / mhp)
        c = (60, 64, 90) if dim else col
        d.line([a, b], fill=c, width=w)
        m = lerp(a, b, 0.62)
        arrow(d, lerp(a, b, 0.4), m, INK if not dim else (90, 90, 110), 2, 9, shorten=0)
        dx, dy = lerp(a, b, 0.82)
        d.ellipse((dx - 10, dy - 10, dx + 10, dy + 10), fill=BG, outline=c, width=2)
        text(d, (dx, dy - 8), str(st1), 13, INK, "mono", anchor="ma")
    s, st, hp = arr[-1]
    if hp <= 0:
        x, y = XF.p(s)
        skull(d, (x + k * 2.2 + 30, y - 30), 11, DMG if not dim else (110, 110, 120))


def skull(d, c, r, col) -> None:
    x, y = c
    d.ellipse((x - r, y - r, x + r, y + r * 0.6), fill=col)
    d.rectangle((x - r * 0.55, y + r * 0.3, x + r * 0.55, y + r), fill=col)
    d.ellipse((x - r * 0.6, y - r * 0.3, x - r * 0.1, y + r * 0.2), fill=BG)
    d.ellipse((x + r * 0.1, y - r * 0.3, x + r * 0.6, y + r * 0.2), fill=BG)


def base(d, r=None, step=None, show_hp=True) -> None:
    draw_links(d, XF, dim=True)
    st, hp = ({}, {}) if r is None else node_states(r, step)
    for k in NODES:
        if r is not None and step is None and k in r.nodes:
            node(d, XF, k, st.get(k, "ok"), r.nodes[k]["before"], r.nodes[k]["before"] - r.nodes[k]["after"])
        else:
            node(d, XF, k, st.get(k, "ok"), hp.get(k))


def place_assets(d, plan) -> None:
    for n, aa in plan.assets.items():
        x, y = XF.p(n)
        for i, a in enumerate(aa):
            px, py = x - 46, y + 14 + i * 26
            d.ellipse((px - 13, py - 13, px + 13, py + 13), fill=(50, 46, 30), outline=CELL, width=2)
            asset_icon(d, (px, py), a, 8, HOLD if a == "ICE" else CELL)


def wave_chips(d) -> None:
    c1, c2 = XF.p("C1"), XF.p("C2")
    threat_chip(d, (c1[0] + 72, c1[1] + 4), "COLLECTOR")
    threat_chip(d, (c2[0] + 74, c2[1] - 60), "AUDITOR")
    threat_chip(d, (c2[0] + 74, c2[1] + 32), "ENFORCER")


def result_panel(d, r, x=1030, y=100) -> None:
    lo = losses(r)
    panel(d, (x, y, x + 238, y + 170), edge=STAMP_HOLD if not r.clean else STAMP_CLEAN)
    node_icon(d, (x + 26, y + 30), "HOME", 32, CELL)
    hl = r.home_before - r.home_after
    text(d, (x + 50, y + 16), f"{r.home_before}>{r.home_after}", 22, DMG if hl else HOLD, "mono")
    d.ellipse((x + 12, y + 60, x + 40, y + 88), fill=(48, 50, 58), outline=DOWN_GREY, width=2)
    bolt(d, (x + 26, y + 74), 10)
    text(d, (x + 50, y + 62), f"{len(lo['down'])}", 22, INK, "mono")
    flag(d, (x + 110, y + 74), 10, THREAT_LIGHT)
    text(d, (x + 128, y + 62), f"{len(lo['taken'])}", 22, INK, "mono")
    skull(d, (x + 26, y + 124), 11, DMG)
    text(d, (x + 50, y + 112), f"{len(r.killed)}/3", 22, INK, "mono")
    coin(d, (x + 128, y + 124), 10)
    text(d, (x + 146, y + 112), f"-{repair_cost(r)}", 22, INK, "mono")


def f1():
    img, d = new_frame(NAME, "warning")
    r = RUNS["BARE"]
    base(d)
    heat_bar(d, 470, 22, 340, 51)
    why_chain(d, 560, 52)
    countdown(d, (70, 70), 2)
    for tid in r.paths:
        ribbon(d, r, tid, (44, 70, 170))
    wave_chips(d)
    header(d, NAME, 1, "Warning: lanes at full width (= full HP) from each entry, wave chips with route glyphs, the countdown and the Heat cause")
    return img


def f2():
    img, d = new_frame(NAME, "planning")
    r = RUNS["BARE"]
    base(d, r)
    heat_bar(d, 470, 22, 340, 51)
    countdown(d, (70, 70), 2)
    for tid in r.paths:
        ribbon(d, r, tid, dim=True)
    for k, info in r.nodes.items():
        mark2(d, XF, k, info)
    # Holding TURRET over HOME: the nodes within reach 1 get yellow rings; their lane ends light up.
    hx, hy = XF.p("HOME")
    for k in ("FW", "VAULT", "SAFE"):
        x, y = XF.p(k)
        d.ellipse((x - 40, y - 40, x + 40, y + 40), outline=CELL, width=3)
        d.line([(hx, hy), (x, y)], fill=CELL, width=2)
    d.ellipse((hx - 40, hy - 40, hx + 40, hy + 40), outline=CELL, width=3)
    d.rounded_rectangle((hx - 74, hy + 10, hx - 40, hy + 44), radius=6, fill=(50, 46, 30), outline=CELL, width=2)
    asset_icon(d, (hx - 57, hy + 27), "TURRET", 9)
    for i, a in enumerate(("TURRET", "ICE", "DECOY", "CREW")):
        asset_card2(d, 20, 140 + i * 120, a, selected=a == "TURRET")
    header(d, NAME, 2, "Planning: grey ribbons = the raid as it stands (home -20, 3 DOWN, 1 TAKEN); holding TURRET over HOME rings the 4 nodes it reaches")
    return img


def f3():
    img, d = new_frame(NAME, "forecast")
    r = RUNS["SHIELD"]
    base(d, r)
    heat_bar(d, 470, 22, 340, 51)
    countdown(d, (70, 70), 2)
    for tid in r.paths:
        ribbon(d, r, tid)
    for k, info in r.nodes.items():
        mark2(d, XF, k, info)
    place_assets(d, PLANS["SHIELD"])
    result_panel(d, r)
    # The saved alternative, one line: plan 1 (lure) for comparison.
    alt = RUNS["LURE"]
    panel(d, (1030, 286, 1268, 340))
    text(d, (1044, 296), "1", 22, DIM, "mono")
    node_icon(d, (1084, 312), "HOME", 26, DIM)
    text(d, (1100, 300), f"-{alt.home_before - alt.home_after}", 18, DMG, "mono")
    bolt(d, (1160, 312), 9)
    text(d, (1172, 300), "0", 18, INK, "mono")
    flag(d, (1210, 312), 8, THREAT_LIGHT)
    text(d, (1224, 300), "0", 18, INK, "mono")
    for i, a in enumerate(("TURRET", "ICE", "DECOY", "CREW")):
        asset_card2(d, 20, 140 + i * 120, a, used=a != "CREW")
    button(d, (1090, 640, 1265, 690), "START RAID")
    header(d, NAME, 3, "Forecast, plan 2 (shield home): ribbons narrow at each hit, skulls where threats die; home 50>50 but 2 DOWN, 2 TAKEN; plan 1 kept for comparison")
    return img


def f4():
    img, d = new_frame(NAME, "resolution")
    r = RUNS["SHIELD"]
    s = 5
    base(d, r, step=s)
    heat_bar(d, 470, 22, 340, 51)
    step_track(d, 470, 70, 340, len(r.steps), s)
    for tid in r.paths:
        ribbon(d, r, tid, dim=True)
    place_assets(d, PLANS["SHIELD"])
    ev = r.steps[s - 1]
    for tid, (site, hp, alive, hold) in ev["threats"].items():
        if not alive:
            continue
        x, y = XF.p(site)
        threat(d, (x + 40, y - 6 + PERP[tid]), tid, 15, hp=hp)
        if hold:
            asset_icon(d, (x + 64, y - 26 + PERP[tid]), "ICE", 8, HOLD)
    for site, gun, tid, dmg, left in ev["shots"]:
        sx, sy = XF.p(site)
        tx, ty = XF.p(ev["threats"][tid][0])
        d.line([(sx, sy), (tx + 40, ty - 6 + PERP[tid])], fill=CELL, width=4)
        text(d, (tx + 60, ty - 50), f"-{dmg}", 22, CELL, "mono")
    for tid, site, dmg, left in ev["hits"]:
        x, y = XF.p(site)
        dmg_badge(d, (x - 46, y - 40), dmg)
    speed_controls(d, 1060, 660)
    header(d, NAME, 4, "Resolution (step 5 of 10, no input): the Auditor is held at the home door and shot; the Enforcer hits the Relay; ribbons stay as the ruler")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    r = RUNS["SHIELD"]
    base(d, r)
    heat_bar(d, 470, 22, 340, 51, raid_at=None)
    for k, info in r.nodes.items():
        mark2(d, XF, k, info)
    lo = losses(r)
    for k in lo["taken"]:
        x, y = XF.p(k)
        arrow(d, (x, y), XF.p("HOME"), THREAT, 4, 12, dash_line=True)
    stamp_losses(img, d, (1010, 170), r)
    panel(d, (20, 560, 700, 700))
    for i, k in enumerate(lo["taken"] + lo["down"]):
        cx = 50 + i * 165
        taken = k in lo["taken"]
        node_icon(d, (cx, 600), k, 34, THREAT_LIGHT if taken else DOWN_GREY)
        if taken:
            flag(d, (cx + 24, 588), 7, THREAT_LIGHT)
        else:
            bolt(d, (cx + 24, 590), 8)
        arrow(d, (cx + 34, 600), (cx + 74, 600), INK, 3, 9, shorten=0)
        if taken:
            d.regular_polygon((cx + 94, 600, 13), 6, outline=CELL, width=3)
            text(d, (cx + 94, 630), "1 RUN", 13, DIM, anchor="ma")
        else:
            coin(d, (cx + 94, 600), 11)
            text(d, (cx + 112, 588), str(INSTALL[k] // 2), 20, INK, "mono")
    button(d, (1090, 640, 1265, 690), "BACK TO HQ")
    header(d, NAME, 5, "Aftermath: stamp shows 2 DOWN + 2 TAKEN as icons; TAKEN nodes keep the X and point a new lane at home; each loss with its fix (netrun or coins)")
    return img


def f6():
    img, d = new_frame(NAME, "next raid")
    r = RUNS["SHIELD"]
    lo = losses(r)
    draw_links(d, XF, dim=True)
    st, _ = node_states(r)
    for k in NODES:
        if k in lo["taken"]:
            x, y = XF.p(k)
            d.regular_polygon((x, y, 32), 6, fill=(20, 30, 70), outline=CORP, width=3)
            shield(d, (x, y - 2), 14, CORP)
            pencil_x(d, (x, y), 26, seed=9)
        else:
            node(d, XF, k, st.get(k, "ok"), r.nodes[k]["after"] if k in r.nodes else None)
    heat_bar(d, 470, 22, 340, 76, raid_at=75)
    why_chain(d, 560, 52, 76, 75)
    countdown(d, (70, 70), 3)
    for k in lo["taken"]:
        x, y = XF.p(k)
        d.line([(x, y), XF.p("HOME")], fill=(44, 70, 170), width=20)
        arrow(d, (x, y), XF.p("HOME"), INK, 3, 10)
    for k, nm in zip(lo["taken"], ("ENFORCER", "COLLECTOR")):
        x, y = XF.p(k)
        threat_chip(d, (x + 30, y - 70), nm)
    label_tag(d, (20, 160), "1 HOP", INK, THREAT, 18)
    node_icon(d, (40, 210), "HOME", 34, CELL)
    header(d, NAME, 6, "Next raid (Heat 76): the two TAKEN nodes are now Solace entries one hop from home; the old loss shapes the new lanes")
    return img


FRAMES = [f1, f2, f3, f4, f5, f6]
