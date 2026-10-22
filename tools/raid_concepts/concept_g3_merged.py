"""Concept G, round 3: the merged design (A's telegraph base + B's reach rings and next-raid frame + F's path rows +
E's countdown on the netrun map + D's per-threat strip), under the RULES_PROPOSAL package: fixed routes, home is not a
corridor, the weaker-node tie-break, ICE blocks the strike, a 3-of-5 deploy draft, SCUFFED priced at 1 per point, and
cascades drawn. Every number is sim.py output with those rules."""

from __future__ import annotations

import math

from r2_kit import *  # noqa: F403
from sim import INSTALL, Plan, run, summary

NAME = "G MERGED r3"
MOMENTS = ["0_netrun", "1_warning", "2_draft", "3_planning", "4_forecast", "5_resolution", "6_aftermath", "7_next_raid"]
RULE = {"fixed_routes": True, "avoid_home": True, "tiebreak": "weakest", "ice_blocks": True}
P = {
    "BARE": Plan({}, "SAFE", dict(RULE)),
    "RAIL": Plan({"RELAY": ["RAILGUN"]}, "SAFE", dict(RULE)),
    "CLEAN": Plan({"RELAY": ["TURRET", "RAILGUN"], "PROXY": ["ICE"]}, "RELAY", dict(RULE)),
    "DECOY_DRAFT": Plan({"RELAY": ["TURRET"], "FW": ["ICE", "DECOY"]}, "RELAY", dict(RULE)),
}
G = {k: run(p) for k, p in P.items()}
NEXT_START = dict(NODE_HP)
for k, v in G["CLEAN"].nodes.items():
    NEXT_START[k] = v["after"]
NEXT_UNPATCHED = run(Plan({}, "SAFE", dict(RULE)), start_hp=NEXT_START)
NEXT_PATCHED = G["BARE"]
XF = MapXf(300, 125, 0.80)
POOL = ["TURRET", "ICE", "DECOY", "SENTRY", "RAILGUN"]
SHADE = {"COLLECTOR": (61, 107, 255), "AUDITOR": (120, 150, 255), "ENFORCER": (40, 70, 200), "LOCKDOWN": (90, 120, 230)}
OFF = {"COLLECTOR": 0, "AUDITOR": 9, "ENFORCER": -9, "LOCKDOWN": 18}


def price(r) -> int:
    """Coins to put everything back: home and SCUFFED at 1 per point, DOWN at half the install cost."""
    c = r.home_before - r.home_after
    for k, v in r.nodes.items():
        if k == "HOME":
            continue
        if v["outcome"] == "scuffed":
            c += v["before"] - v["after"]
        elif v["outcome"] == "down":
            c += INSTALL[k] // 2
    return c


def lost(r) -> tuple[int, int]:
    lo = losses(r)
    return len(lo["down"]), len(lo["taken"])


def routes(d, r, faint: bool = False) -> None:
    """One thin offset route per threat with its silhouette at the head and step dots; fork glyph where a tie was broken."""
    for tid, path in getattr(r, "routes", r.paths).items():
        col = (44, 60, 120) if faint else SHADE[tid]
        k = OFF[tid]
        pts = []
        for n in path:
            x, y = XF.p(n)
            pts.append((x + k, y + k))
        for a, b in zip(pts, pts[1:]):
            arrow(d, a, b, col, 4, 12, shorten=30)
        if not faint:
            hx, hy = pts[0]
            threat(d, (hx - 26, hy - 20), tid, 10, show_hp=False)
            # where the fixed route is cut short: a skull at the node it dies on
            for ev in r.steps:
                for kt, site in ev["kills"]:
                    if kt == tid:
                        x, y = XF.p(site)
                        sk = (x + k * 2 + 30, y - 24 + k * 2)
                        d.ellipse((sk[0] - 9, sk[1] - 9, sk[0] + 9, sk[1] + 5), fill=DMG)
                        d.rectangle((sk[0] - 5, sk[1] + 2, sk[0] + 5, sk[1] + 9), fill=DMG)
                        d.ellipse((sk[0] - 6, sk[1] - 4, sk[0] - 1, sk[1] + 1), fill=BG)
                        d.ellipse((sk[0] + 1, sk[1] - 4, sk[0] + 6, sk[1] + 1), fill=BG)
    if not faint:
        # The Collector's tie at RELAY (VAULT 20 vs FIREWALL 30): drawn as a cracked-shield fork glyph.
        x, y = XF.p("RELAY")
        route_glyph(d, (x - 40, y + 34), "ENFORCER", 7, CELL)


def cascades(d, r) -> None:
    for ev in r.steps:
        for src, dst, c in ev.get("cascades", []):
            a, b = XF.p(src), XF.p(dst)
            arrow(d, a, b, DMG, 3, 10, dash_line=True, shorten=34)
            m = lerp(a, b, 0.5)
            text(d, (m[0] + 6, m[1] - 10), f"-{c}", 15, DMG, "mono")


def base(d, r=None, step=None, start=None) -> None:
    draw_links(d, XF)
    st, hp = ({}, {}) if r is None else node_states(r, step)
    for k in NODES:
        if r is not None and step is None and k in r.nodes:
            node(d, XF, k, st.get(k, "ok"), r.nodes[k]["before"], r.nodes[k]["before"] - r.nodes[k]["after"])
        elif start is not None and k in start:
            node(d, XF, k, "ok", start[k])
        else:
            node(d, XF, k, st.get(k, "ok"), hp.get(k))


def tags(d, r) -> None:
    for k, info in r.nodes.items():
        mark2(d, XF, k, info)


def place_assets(d, plan) -> None:
    for n, aa in plan.assets.items():
        x, y = XF.p(n)
        for i, a in enumerate(aa):
            px, py = x - 46, y + 12 + i * 26
            d.ellipse((px - 13, py - 13, px + 13, py + 13), fill=(50, 46, 30), outline=CELL, width=2)
            asset_icon(d, (px, py), "TURRET" if a in ("SENTRY", "RAILGUN") else a, 8, HOLD if a == "ICE" else CELL)
            if a == "RAILGUN":
                text(d, (px, py - 30), "8", 13, CELL, "mono", anchor="ma")
    if plan.crew:
        x, y = XF.p(plan.crew)
        asset_icon(d, (x + 46, y + 22), "CREW", 10)


def card(d, x, y, aid: str, sel=False, used=False, w=96, h=112) -> None:
    """Glyph-stat cards; SENTRY / RAILGUN drawn like the turret with their own numbers."""
    if aid in ("TURRET", "ICE", "DECOY", "CREW"):
        asset_card2(d, x, y, aid, w, h, sel, used)
        return
    edge = CELL if sel else PANEL_EDGE
    fill = (50, 46, 30) if sel else (24, 26, 40) if used else PANEL
    d.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=fill, outline=edge, width=3 if sel else 2)
    col = CELL if not used else DIM
    asset_icon(d, (x + w / 2, y + 36), "TURRET", 18 if aid == "RAILGUN" else 12, col)
    if aid == "RAILGUN":
        d.line([(x + 20, y + 36), (x + w - 20, y + 36)], fill=col, width=5)
    else:
        asset_icon(d, (x + w / 2 + 16, y + 28), "TURRET", 8, col)
    sy = y + 76
    dmg, reach, shots = (8, 2, 1) if aid == "RAILGUN" else (3, 0, 2)
    swords(d, (x + 18, sy + 10), 7, DMG)
    text(d, (x + 30, sy), f"{dmg}", 20, INK, "mono")
    for i in range(shots):
        d.ellipse((x + 50 + i * 9, sy + 6, x + 57 + i * 9, sy + 13), fill=INK)
    for i in range(reach):
        d.ellipse((x + 70 - i * 3, sy + 2 - i * 3, x + 86 + i * 3, sy + 18 + i * 3), outline=col, width=2)


def threat_strip(d, r, tid: str, x, y) -> None:
    """D's per-threat readout: one cell per step, where it stands, what it hits, its HP; skull where it dies."""
    panel(d, (x, y, x + 60 + 62 * len(r.steps), y + 74), edge=SHADE[tid])
    threat(d, (x + 30, y + 30), tid, 14)
    for i, ev in enumerate(r.steps):
        cx = x + 60 + i * 62
        site, hp, alive, hold = ev["threats"][tid]
        dead = any(k[0] == tid for k in ev["kills"])
        d.rectangle((cx, y + 8, cx + 58, y + 66), fill=BG2, outline=PANEL_EDGE)
        text(d, (cx + 4, y + 8), str(i + 1), 10, DIM, "mono")
        if not alive and not dead:
            continue
        if site.startswith("C"):
            shield(d, (cx + 18, y + 30), 8, CORP)
        else:
            node_icon(d, (cx + 18, y + 30), site, 22, CELL)
        hit = sum(h[2] for h in ev["hits"] if h[0] == tid)
        if dead:
            text(d, (cx + 44, y + 18), "", 14, DMG)
            d.ellipse((cx + 34, y + 18, cx + 54, y + 38), fill=DMG)
            d.ellipse((cx + 38, y + 23, cx + 43, y + 28), fill=BG)
            d.ellipse((cx + 45, y + 23, cx + 50, y + 28), fill=BG)
        elif hold:
            asset_icon(d, (cx + 44, y + 28), "ICE", 7, HOLD)
        elif hit:
            text(d, (cx + 56, y + 18), f"-{hit}", 15, DMG, "mono", anchor="ra")
        mhp = THREATS[tid][1]
        d.rectangle((cx + 6, y + 52, cx + 52, y + 58), outline=(60, 70, 110))
        if hp > 0:
            d.rectangle((cx + 6, y + 52, cx + 6 + 46 * hp / mhp, y + 58), fill=SHADE[tid])


def plan_row(d, x, y, label, r, on, pick) -> None:
    d.rounded_rectangle((x, y, x + 238, y + 92), radius=6, fill=(50, 46, 30) if on else BG2,
                        outline=CELL if on else PANEL_EDGE, width=3 if on else 1)
    text(d, (x + 10, y + 6), label, 22, CELL if on else DIM, "mono")
    for i, a in enumerate(pick):
        asset_icon(d, (x + 48 + i * 26, y + 20), "TURRET" if a in ("SENTRY", "RAILGUN") else a, 8, HOLD if a == "ICE" else CELL)
        if a == "RAILGUN":
            d.line([(x + 40 + i * 26, y + 20), (x + 56 + i * 26, y + 20)], fill=CELL, width=3)
    dn, tk = lost(r)
    node_icon(d, (x + 22, y + 62), "HOME", 24, CELL)
    hl = r.home_before - r.home_after
    text(d, (x + 36, y + 50), f"-{hl}", 18, DMG if hl else HOLD, "mono")
    bolt(d, (x + 96, y + 62), 8)
    text(d, (x + 108, y + 50), str(dn), 18, INK, "mono")
    flag(d, (x + 138, y + 62), 8, THREAT_LIGHT)
    text(d, (x + 150, y + 50), str(tk), 18, INK, "mono")
    coin(d, (x + 186, y + 62), 9)
    text(d, (x + 200, y + 50), str(price(r)), 18, INK, "mono")
    if r.clean:
        d.ellipse((x + 200, y + 6, x + 228, y + 34), fill=(20, 60, 60), outline=STAMP_CLEAN, width=2)
        check(d, (x + 214, y + 20), 7, STAMP_CLEAN)


def hud(d, n=2) -> None:
    heat_bar(d, 470, 22, 340, 51)
    countdown(d, (70, 70), n)


def f0():
    """Netrun map: the raid's dial and chips appear on the netrun itself, at the return node."""
    img, d = new_frame(NAME, "netrun")
    heat_bar(d, 470, 22, 340, 51)
    why_chain(d, 560, 52)
    nodes = [(160, 380), (330, 300), (330, 460), (520, 380), (700, 300), (700, 460), (880, 380)]
    links = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 6), (5, 6)]
    for a, b in links:
        d.line([nodes[a], nodes[b]], fill=CELL_DIM, width=4)
    for i, (x, y) in enumerate(nodes):
        done = i <= 3
        d.regular_polygon((x, y, 26), 6, fill=(50, 46, 30) if done else PANEL, outline=CELL, width=3)
        if i == 3:
            asset_icon(d, (x, y), "CREW", 12)
    hx, hy = 1060, 380
    d.line([nodes[6], (hx, hy)], fill=CELL_DIM, width=4)
    d.ellipse((hx - 40, hy - 40, hx + 40, hy + 40), fill=(34, 36, 58), outline=CELL, width=4)
    node_icon(d, (hx, hy), "HOME", 50, CELL)
    countdown(d, (hx, hy - 120), 2)
    for i, t in enumerate(("COLLECTOR", "AUDITOR", "ENFORCER")):
        threat_chip(d, (hx - 80 + i * 80, hy + 110), t, scale=0.75)
    for i in (4, 6):
        pass
    d.line([(hx, hy + 44), (hx, hy + 70)], fill=THREAT, width=3)
    header(d, NAME, 0, "Netrun map: the raid is announced here: dial = 2 map nodes until home, the three chips wait at home; Heat 51 > 50 is the cause")
    return img


def f1():
    img, d = new_frame(NAME, "warning")
    r = G["BARE"]
    base(d)
    hud(d)
    why_chain(d, 560, 52)
    routes(d, r)
    # F's path rows: each threat's route as node icons, its two numbers, where it ends.
    panel(d, (930, 100, 1268, 330))
    for i, t in enumerate(("COLLECTOR", "AUDITOR", "ENFORCER")):
        y = 118 + i * 70
        threat_chip(d, (972, y + 22), t, scale=0.6)
        for j, n in enumerate(r.paths[t][1:]):
            x = 1024 + j * 52
            node_icon(d, (x, y + 22), n, 30, CELL)
            if j:
                arrow(d, (x - 40, y + 22), (x - 14, y + 22), SHADE[t], 3, 7, shorten=0)
    tags(d, r)
    header(d, NAME, 1, "Warning at HQ: fixed routes drawn end to end (they will not change), path rows per threat; outcome tags of the raid as it stands")
    return img


def f2():
    img, d = new_frame(NAME, "draft")
    r = G["BARE"]
    base(d, r)
    hud(d)
    routes(d, r, faint=True)
    tags(d, r)
    panel(d, (300, 520, 980, 700), edge=CELL)
    for i, a in enumerate(POOL):
        sel = a in ("TURRET", "ICE", "RAILGUN")
        card(d, 320 + i * 108, 540, a, sel=sel)
    for i in range(3):
        d.rounded_rectangle((870 + 0, 548 + i * 48, 960, 584 + i * 48), radius=6, fill=CELL, outline=CELL)
        text(d, (915, 554 + i * 48), str(i + 1), 18, BG, "mono", anchor="ma")
    header(d, NAME, 2, "Draft: take 3 of the 5 Armory pieces into this raid (turret, ICE, railgun picked); the raid as it stands stays visible behind")
    return img


def f3():
    img, d = new_frame(NAME, "planning")
    r = G["RAIL"]
    base(d, r)
    hud(d)
    routes(d, r)
    cascades(d, r)
    tags(d, r)
    place_assets(d, P["RAIL"])
    # B's reach rings: the railgun (reach 2) on RELAY rings every node within 2 hops.
    for k in ("FW", "VAULT", "HOME", "PROXY", "RELAY"):
        x, y = XF.p(k)
        d.ellipse((x - 40, y - 40, x + 40, y + 40), outline=CELL, width=2)
    w, b = G["RAIL"], G["BARE"]
    dn0, tk0 = lost(b)
    dn1, tk1 = lost(w)
    d.rounded_rectangle((20, 140, 250, 210), radius=6, fill=CELL)
    bolt(d, (36, 175), 9, BG)
    flag(d, (54, 175), 9, BG)
    text(d, (70, 162), f"{dn0 + tk0} > {dn1 + tk1}", 22, BG, "mono")
    node_icon(d, (150, 175), "VAULT", 26, BG)
    check(d, (176, 175), 7, BG)
    threat_strip(d, r, "ENFORCER", 20, 600)
    for i, a in enumerate(("TURRET", "ICE")):
        card(d, 330 + i * 104 + 380, 596, a, sel=a == "TURRET")
    header(d, NAME, 3, "Planning: railgun on RELAY rings what it reaches; what-if lost 2 > 1 (VAULT now holds); dashed red spill = cascade when PROXY falls; Enforcer strip per step")
    return img


def f4():
    img, d = new_frame(NAME, "forecast")
    r = G["CLEAN"]
    base(d, r)
    hud(d)
    routes(d, r)
    cascades(d, r)
    tags(d, r)
    place_assets(d, P["CLEAN"])
    panel(d, (1020, 100, 1268, 330))
    plan_row(d, 1025, 110, "1", r, True, ("TURRET", "ICE", "RAILGUN"))
    plan_row(d, 1025, 216, "2", G["DECOY_DRAFT"], False, ("TURRET", "ICE", "DECOY"))
    panel(d, (1020, 346, 1268, 450), edge=STAMP_CLEAN)
    d.ellipse((1036, 362, 1072, 398), fill=(20, 60, 60), outline=STAMP_CLEAN, width=3)
    check(d, (1054, 380), 9, STAMP_CLEAN)
    flame(d, (1100, 384), 10, HEAT)
    text(d, (1116, 370), "+5", 22, INK, "mono")
    coin(d, (1180, 382), 10)
    text(d, (1196, 370), "+12", 22, INK, "mono")
    coin(d, (1046, 424), 9, DIM)
    text(d, (1062, 412), f"-{price(r)}", 20, DIM, "mono")
    threat_strip(d, r, "ENFORCER", 20, 600)
    button(d, (1060, 640, 1268, 690), "START RAID")
    header(d, NAME, 4, "Forecast: plan 1 is CLEAN (+5 Heat, +12) and costs 8 to patch; plan 2 (decoy draft) is also clean but costs 38; the Enforcer dies at step 3")
    return img


def f5():
    img, d = new_frame(NAME, "resolution")
    r = G["CLEAN"]
    s = 2
    base(d, r, step=s)
    heat_bar(d, 470, 22, 340, 51)
    step_track(d, 470, 70, 340, len(r.steps), s)
    routes(d, r, faint=True)
    place_assets(d, P["CLEAN"])
    ev = r.steps[s - 1]
    pos = {}
    for tid, (site, hp, alive, hold) in ev["threats"].items():
        dead = any(k[0] == tid for k in ev["kills"])
        if not alive and not dead:
            continue
        x, y = XF.p(site)
        p = (x + 44, y - 8 + OFF[tid] * 3)
        pos[tid] = p
        threat(d, p, tid, 15, hp=hp, ghost=dead)
        if dead:
            pencil_x(d, p, 16, seed=4)
        if hold:
            asset_icon(d, (p[0] + 24, p[1] - 22), "ICE", 8, HOLD)
    for i, (site, gun, tid, dmg, left) in enumerate(ev["shots"]):
        sx, sy = XF.p(site)
        if tid in pos:
            d.line([(sx, sy), pos[tid]], fill=CELL, width=4)
            order_badge(d, lerp((sx, sy), pos[tid], 0.5), i + 1, CELL)
            text(d, (pos[tid][0] + 18, pos[tid][1] - 44), f"-{dmg}", 22, CELL, "mono")
    speed_controls(d, 1060, 660)
    text(d, (640, 96), "AUTO", 13, DIM, anchor="ma")
    header(d, NAME, 5, "Resolution (step 2 of 4, no input): numbered shots: turret kills the Collector on VAULT, railgun brings the frozen Enforcer to 1")
    return img


def f6():
    img, d = new_frame(NAME, "aftermath")
    r = G["CLEAN"]
    base(d, r)
    heat_bar(d, 470, 22, 340, 56, raid_at=None)
    tags(d, r)
    stamp_losses(img, d, (1010, 190), r)
    panel(d, (20, 560, 700, 700))
    i = 0
    for k, v in r.nodes.items():
        if v["outcome"] != "scuffed":
            continue
        x = 40 + i * 220
        node_icon(d, (x + 20, 610), k, 34, CELL)
        text(d, (x + 44, 598), f"-{v['before'] - v['after']}", 20, DMG, "mono")
        arrow(d, (x + 84, 610), (x + 114, 610), INK, 3, 8, shorten=0)
        coin(d, (x + 134, 610), 10)
        text(d, (x + 150, 598), str(v["before"] - v["after"]), 20, INK, "mono")
        i += 1
    flame(d, (50, 668), 10, HEAT)
    text(d, (66, 656), "51 > 56", 20, HEAT, "mono")
    button(d, (1090, 640, 1265, 690), "BACK TO HQ")
    header(d, NAME, 6, "Aftermath: CLEAN stamp with +5 Heat, +12 Schematics; each scuffed node and its patch price (1 per point); Heat 51 > 56")
    return img


def f7():
    img, d = new_frame(NAME, "next raid")
    r = NEXT_UNPATCHED
    base(d, start=NEXT_START)
    heat_bar(d, 470, 22, 340, 76, raid_at=75)
    why_chain(d, 560, 52, 76, 75)
    countdown(d, (70, 70), 3)
    routes(d, r)
    tags(d, r)
    # Inset: the same raid if RELAY and PROXY are patched first (the Enforcer stays on PROXY).
    panel(d, (950, 420, 1268, 700))
    mini = MapXf(950, 440, 0.38)
    for a, b in LINKS:
        d.line([mini.p(a), mini.p(b)], fill=CELL_DIM, width=2)
    for k in NODES:
        x, y = mini.p(k)
        if k.startswith("C"):
            shield(d, (x, y), 7, CORP)
            continue
        o = NEXT_PATCHED.nodes[k]["outcome"]
        col = THREAT_LIGHT if o == "taken" else (DOWN_GREY if o == "down" else CELL)
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(34, 36, 58), outline=col, width=2)
        if o == "taken":
            pencil_x(d, (x, y), 9, seed=2)
    for tid, path in NEXT_PATCHED.paths.items():
        for a, b in zip(path, path[1:]):
            arrow(d, mini.p(a), mini.p(b), SHADE[tid], 2, 7, shorten=10)
    coin(d, (980, 680), 9)
    text(d, (996, 668), str(price(G["CLEAN"])), 18, INK, "mono")
    dn_u, tk_u = lost(r)
    dn_p, tk_p = lost(NEXT_PATCHED)
    flag(d, (1060, 680), 8, THREAT_LIGHT)
    text(d, (1074, 668), f"{dn_u + tk_u} > {dn_p + tk_p}", 18, INK, "mono")
    header(d, NAME, 7, f"Next raid (Heat 76), unpatched: RELAY at 10 is now weakest, so the Enforcer's route reaches it ({dn_u + tk_u} lost); inset: patched first ({dn_p + tk_p} lost)")
    return img


FRAMES = [f0, f1, f2, f3, f4, f5, f6, f7]

if __name__ == "__main__":
    for k, r in G.items():
        print(k, summary(r), "price", price(r), r.paths)
    print("NEXT_UNPATCHED", summary(NEXT_UNPATCHED), NEXT_UNPATCHED.paths)
