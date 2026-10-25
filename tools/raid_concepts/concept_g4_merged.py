"""Concept G, round 4: G3 with the critic-R3 barriers challenged (each a designer decision, see BARRIERS_R4.md).
- No cascade (sim `no_cascade`): measured, it changes no clean plan; it only removed undrawn damage.
- Graded payout: +4 Schematics salvage per threat killed, +6 if CLEAN; a TAKEN node costs its full install.
  Every plan shows its NET (payout - patch) before commit and on the stamp.
- Raids do not move Heat (D27 challenged): the clean "reward" no longer pulls the next raid closer.
- Verdict tiers CLEAN / HOLDS / BREACHED (D28 challenged); the stamp carries the net.
- Beat pacing (D26 challenged): one beat (about 1 s) per shot or hit, capped at 40 s; replay after the raid.
- Effective numbers on placed pieces (crew x1.5 drawn as a chevron badge, the boosted number printed).
- Three distinct gun silhouettes: turret = crosshair, sentry = twin barrels, railgun = long beam.
- Routes: cobalt with a white core. The dial counts netruns (a netrun hex inside it), same unit everywhere.
- Draft cards preview their best single placement against this raid (nodes lost, struck through).
- Plans 1 and 2 differ in what they leave for the NEXT raid (unpatched SCUFFED draws routes): multi-raid depth.
Every number is sim.py output."""

from __future__ import annotations

from r2_kit import *  # noqa: F403
from sim import INSTALL, NODE_HP as SIM_HP, Plan, run, summary

import concept_g3_merged as G3

NAME = "G MERGED r4"
MOMENTS = ["0_netrun", "1_warning", "2_draft", "3_planning", "4_forecast", "5_resolution", "6_aftermath", "7_next_raid"]
RULE = {"fixed_routes": True, "avoid_home": True, "tiebreak": "weakest", "ice_blocks": True, "no_cascade": True}
SALVAGE, CLEAN_BONUS, BEAT_S, KILLCAM_S, CAP_S = 4, 6, 1.0, 2.0, 40
POOL = ["TURRET", "ICE", "DECOY", "SENTRY", "RAILGUN"]
GUN_DMG = {"TURRET": 4, "SENTRY": 3, "RAILGUN": 8}
P = {
    "BARE": Plan({}, "SAFE", dict(RULE)),
    "RAIL": Plan({"RELAY": ["RAILGUN"]}, "SAFE", dict(RULE)),
    "P1": Plan({"RELAY": ["TURRET", "RAILGUN"], "PROXY": ["ICE"]}, "RELAY", dict(RULE)),
    "P2": Plan({"RELAY": ["ICE"], "PROXY": ["SENTRY", "RAILGUN"]}, "PROXY", dict(RULE)),
    "P3": Plan({"RELAY": ["TURRET", "SENTRY", "RAILGUN"]}, "RELAY", dict(RULE)),
}
PICK = {"P1": ("TURRET", "ICE", "RAILGUN"), "P2": ("ICE", "SENTRY", "RAILGUN"), "P3": ("TURRET", "SENTRY", "RAILGUN")}
R = {k: run(p) for k, p in P.items()}
XF = G3.XF
SHADE, OFF = G3.SHADE, G3.OFF


def kills(r) -> int:
    return len({k for ev in r.steps for k, _ in ev["kills"]})


def price(r) -> int:
    """Patch: home and SCUFFED 1 per point, DOWN half install, TAKEN full install (rebuilt after the reclaim)."""
    return G3.price(r) + sum(INSTALL[k] for k, v in r.nodes.items() if v["outcome"] == "taken")


def payout(r) -> int:
    return SALVAGE * kills(r) + (CLEAN_BONUS if r.clean else 0)


def net(r) -> int:
    return payout(r) - price(r)


def lost(r) -> int:
    return sum(1 for v in r.nodes.values() if v["outcome"] in ("down", "taken"))


def beats(r) -> list[tuple[int, str, tuple]]:
    """One beat per shot, hit or kill, in resolver order (the playout clock)."""
    out = []
    for ev in r.steps:
        for s in ev["shots"]:
            out.append((ev["step"], "shot", s))
        for h in ev["hits"]:
            out.append((ev["step"], "hit", h))
    return out


def next_raid(r):
    start = dict(SIM_HP)
    for k, v in r.nodes.items():
        start[k] = v["after"] if v["outcome"] != "taken" else 0
    return run(Plan({}, "SAFE", dict(RULE)), start_hp=start), start


NEXT = {k: next_raid(R[k]) for k in ("P1", "P2")}


def card_preview(aid: str) -> int:
    """Nodes lost with only this card, placed at its best node (crew on SAFE as in the bare raid)."""
    best = 99
    for n in SIM_HP:
        best = min(best, lost(run(Plan({n: [aid]}, "SAFE", dict(RULE)))))
    return best


PREVIEW = {a: card_preview(a) for a in POOL}


# ---------- glyphs ----------
def xsign(d, c, r=5, col=INK) -> None:
    x, y = c
    d.line([(x - r, y - r), (x + r, y + r)], fill=col, width=3)
    d.line([(x - r, y + r), (x + r, y - r)], fill=col, width=3)


def piece(d, c, aid: str, r: float, col=CELL) -> None:
    """Distinct silhouettes: turret crosshair, sentry twin barrels, railgun long beam; others from the kit."""
    x, y = c
    if aid == "SENTRY":
        d.rounded_rectangle((x - r * 0.8, y, x + r * 0.8, y + r * 0.8), radius=3, fill=col)
        d.rectangle((x - r * 0.55, y - r, x - r * 0.2, y + 1), fill=col)
        d.rectangle((x + r * 0.2, y - r, x + r * 0.55, y + 1), fill=col)
    elif aid == "RAILGUN":
        d.rectangle((x - r * 1.2, y - r * 0.22, x + r * 1.2, y + r * 0.22), fill=col)
        d.ellipse((x - r * 0.55, y - r * 0.55, x + r * 0.15, y + r * 0.55), outline=col, width=3)
        d.polygon([(x + r * 1.2, y - r * 0.4), (x + r * 1.6, y), (x + r * 1.2, y + r * 0.4)], fill=col)
    else:
        asset_icon(d, c, aid, r, HOLD if aid == "ICE" and col == CELL else col)


def chevron(d, c, r=6, col=CELL) -> None:
    x, y = c
    d.line([(x - r, y + r * 0.5), (x, y - r * 0.5), (x + r, y + r * 0.5)], fill=col, width=3)


def struck(d, xy, a: int, b: int, size=22, col=INK, bg=None) -> None:
    """'a struck through, then b': fewer lost without words."""
    x, y = xy
    if a == b:
        text(d, (x, y), str(b), size, col, "mono")
        return
    text(d, (x, y), str(a), size, (150, 150, 170), "mono")
    d.line([(x - 3, y + size * 0.9), (x + size * 0.75, y + size * 0.15)], fill=DMG, width=2)
    text(d, (x + size * 1.0, y), str(b), size, col, "mono")


def skull(d, c, r=8) -> None:
    x, y = c
    d.ellipse((x - r, y - r, x + r, y + r * 0.55), fill=DMG)
    d.rectangle((x - r * 0.55, y + r * 0.2, x + r * 0.55, y + r), fill=DMG)
    d.ellipse((x - r * 0.65, y - r * 0.4, x - r * 0.1, y + r * 0.1), fill=BG)
    d.ellipse((x + r * 0.1, y - r * 0.4, x + r * 0.65, y + r * 0.1), fill=BG)


def netrun_hex(d, c, r=9, col=CELL, fill=None) -> None:
    d.regular_polygon((c[0], c[1], r), 6, fill=fill, outline=col, width=2)


def dial(d, c, n: int, of: int = 2) -> None:
    """When: segments = netruns left before you are home; a netrun hex inside, so the unit is drawn."""
    x, y = c
    d.ellipse((x - 40, y - 40, x + 40, y + 40), fill=(16, 22, 52), outline=THREAT, width=3)
    for i in range(of):
        a0, a1 = -90 + i * 360 / of + 8, -90 + (i + 1) * 360 / of - 8
        d.arc((x - 50, y - 50, x + 50, y + 50), a0, a1, fill=THREAT if i < n else (40, 46, 80), width=9)
    netrun_hex(d, (x, y - 12), 12, INK)
    text(d, (x, y + 4), str(n), 24, INK, "mono", anchor="ma")


def record(d, x, y, held: int, clean: int) -> None:
    """Campaign raid record: one shield per raid survived, teal check if clean."""
    for i in range(held):
        cx = x + i * 30
        shield(d, (cx, y), 11, (40, 60, 120), outline=INK)
        check(d, (cx, y), 6, STAMP_CLEAN if i < clean else INK)


def routes(d, r, faint: bool = False) -> None:
    """Cobalt route with a white core; silhouette at the head; skull where it is cut short."""
    for tid, path in getattr(r, "routes", r.paths).items():
        col = (44, 60, 120) if faint else SHADE[tid]
        k = OFF[tid]
        pts = [(XF.p(n)[0] + k, XF.p(n)[1] + k) for n in path]
        for a, b in zip(pts, pts[1:]):
            arrow(d, a, b, col, 6, 13, shorten=30)
            if not faint:
                aa, bb = lerp(a, b, 30 / max(1, ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5)), lerp(b, a, 44 / max(1, ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5))
                d.line([aa, bb], fill=(235, 240, 255), width=2)
        if not faint:
            hx, hy = pts[0]
            threat(d, (hx - 26, hy - 20), tid, 10, show_hp=False)
            for ev in r.steps:
                for kt, site in ev["kills"]:
                    if kt == tid:
                        x, y = XF.p(site)
                        skull(d, (x + k * 2 + 30, y - 24 + k * 2), 9)
    if not faint:
        x, y = XF.p("RELAY")
        route_glyph(d, (x - 40, y + 34), "ENFORCER", 7, CELL)


def place_assets(d, plan) -> None:
    """Placed pieces with their effective number; the crew's x1.5 drawn as a chevron on the boosted pieces."""
    for n, aa in plan.assets.items():
        x, y = XF.p(n)
        boosted = plan.crew == n
        for i, a in enumerate(aa):
            px, py = x - 50, y + 12 + i * 28
            d.ellipse((px - 14, py - 14, px + 14, py + 14), fill=(50, 46, 30), outline=CELL, width=2)
            piece(d, (px, py), a, 8)
            if a in GUN_DMG:
                eff = round(GUN_DMG[a] * (1.5 if boosted else 1.0))
                text(d, (px - 20, py - 9), str(eff), 15, CELL, "mono", anchor="ra")
                if boosted:
                    chevron(d, (px - 20 - 8 * len(str(eff)) - 10, py), 5)
    if plan.crew:
        x, y = XF.p(plan.crew)
        asset_icon(d, (x + 46, y + 22), "CREW", 10)
        chevron(d, (x + 46, y + 2), 6)


def card(d, x, y, aid: str, sel=False, used=False, w=104, h=128, preview=True) -> None:
    edge = CELL if sel else PANEL_EDGE
    fill = (50, 46, 30) if sel else (24, 26, 40) if used else PANEL
    d.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=fill, outline=edge, width=3 if sel else 2)
    col = CELL if not used else DIM
    piece(d, (x + w / 2, y + 30), aid, 16, col)
    sy = y + 62
    if aid in GUN_DMG:
        swords(d, (x + 16, sy + 10), 6, DMG)
        text(d, (x + 26, sy), str(GUN_DMG[aid]), 18, INK, "mono")
        shots = 2 if aid == "SENTRY" else 1
        for i in range(shots):
            d.ellipse((x + 46 + i * 9, sy + 6, x + 53 + i * 9, sy + 13), fill=INK)
        reach = {"TURRET": 1, "SENTRY": 0, "RAILGUN": 2}[aid]
        for i in range(reach):
            d.ellipse((x + 70 - i * 3, sy + 2 - i * 3, x + 86 + i * 3, sy + 18 + i * 3), outline=col, width=2)
    elif aid == "ICE":
        asset_icon(d, (x + 22, sy + 10), "ICE", 7, HOLD)
        for i in range(2):
            d.rectangle((x + 40 + i * 14, sy + 4, x + 50 + i * 14, sy + 16), outline=HOLD, width=2)
    elif aid == "DECOY":
        arrow(d, (x + 14, sy + 10), (x + 50, sy + 10), INK, 3, 8, shorten=0)
        d.ellipse((x + 56, sy + 4, x + 68, sy + 16), fill=CELL)
    if preview:
        d.line([(x + 8, y + 90), (x + w - 8, y + 90)], fill=PANEL_EDGE)
        bolt(d, (x + 18, y + 108), 7)
        flag(d, (x + 32, y + 108), 7, THREAT_LIGHT)
        struck(d, (x + 46, y + 96), lost(R["BARE"]), PREVIEW[aid], 20, INK)


def net_box(d, x, y, r, w=248) -> None:
    """Net payout, worded by glyphs: skull x kills x4, clean check +6, coin minus patch, = net."""
    panel(d, (x, y, x + w, y + 104), edge=STAMP_CLEAN if r.clean else STAMP_HOLD, width=2)
    skull(d, (x + 18, y + 22), 8)
    xsign(d, (x + 36, y + 22), 4)
    text(d, (x + 46, y + 10), str(kills(r)), 20, INK, "mono")
    coin(d, (x + 82, y + 22), 8)
    text(d, (x + 94, y + 10), f"+{SALVAGE * kills(r)}", 20, INK, "mono")
    d.ellipse((x + 146, y + 8, x + 172, y + 34), fill=(20, 60, 60) if r.clean else BG2, outline=STAMP_CLEAN if r.clean else DIM, width=2)
    check(d, (x + 159, y + 21), 6, STAMP_CLEAN if r.clean else DIM)
    text(d, (x + 180, y + 10), f"+{CLEAN_BONUS if r.clean else 0}", 20, INK if r.clean else DIM, "mono")
    coin(d, (x + 18, y + 62), 8, DIM)
    text(d, (x + 30, y + 50), f"-{price(r)}", 20, DMG, "mono")
    d.line([(x + 96, y + 46), (x + 96, y + 80)], fill=PANEL_EDGE, width=2)
    coin(d, (x + 124, y + 64), 12)
    n = net(r)
    text(d, (x + 142, y + 46), f"{n:+d}", 30, STAMP_CLEAN if n > 0 else DMG, "mono")


def plan_row(d, x, y, label, r, on, pick, nxt=None) -> None:
    d.rounded_rectangle((x, y, x + 248, y + 104), radius=6, fill=(50, 46, 30) if on else BG2,
                        outline=CELL if on else PANEL_EDGE, width=3 if on else 1)
    text(d, (x + 10, y + 6), label, 22, CELL if on else DIM, "mono")
    for i, a in enumerate(pick):
        piece(d, (x + 50 + i * 30, y + 20), a, 8)
    if r.clean:
        d.ellipse((x + 146, y + 6, x + 172, y + 32), fill=(20, 60, 60), outline=STAMP_CLEAN, width=2)
        check(d, (x + 159, y + 19), 6, STAMP_CLEAN)
    coin(d, (x + 196, y + 20), 9)
    n = net(r)
    text(d, (x + 208, y + 8), f"{n:+d}", 20, STAMP_CLEAN if n > 0 else DMG, "mono")
    node_icon(d, (x + 22, y + 56), "HOME", 22, CELL)
    hl = r.home_before - r.home_after
    text(d, (x + 36, y + 45), f"-{hl}", 17, DMG if hl else HOLD, "mono")
    bolt(d, (x + 92, y + 56), 7)
    flag(d, (x + 106, y + 56), 7, THREAT_LIGHT)
    text(d, (x + 118, y + 45), str(lost(r)), 17, INK, "mono")
    sc = [k for k, v in r.nodes.items() if v["outcome"] == "scuffed" and k != "HOME"]
    for i, k in enumerate(sc[:3]):
        node_icon(d, (x + 156 + i * 30, y + 56), k, 20, CELL)
        d.polygon([(x + 166 + i * 30, y + 46), (x + 166 + i * 30, y + 54), (x + 158 + i * 30, y + 46)], fill=DMG)
    if nxt is not None:
        # what this plan leaves for the next raid: nodes the next raid takes or downs if nothing is patched
        d.line([(x + 8, y + 76), (x + 240, y + 76)], fill=PANEL_EDGE)
        flame(d, (x + 20, y + 91), 7, HEAT)
        arrow(d, (x + 32, y + 90), (x + 52, y + 90), DIM, 2, 6, shorten=0)
        bolt(d, (x + 66, y + 90), 7)
        flag(d, (x + 80, y + 90), 7, THREAT_LIGHT)
        text(d, (x + 92, y + 80), str(lost(nxt)), 16, INK, "mono")


def stamp_box(img, d, c, r, size=60) -> None:
    if r.breached:
        word, col = "BREACHED", STAMP_BREACH
    elif r.clean:
        word, col = "CLEAN", STAMP_CLEAN
    else:
        word, col = "HOLDS", STAMP_HOLD
    stamp(img, c, word, col, size, -5)
    net_box(d, c[0] - 124, c[1] + 56, r)


def base(d, r=None, step=None, start=None) -> None:
    G3.base(d, r, step, start)


def tags(d, r) -> None:
    G3.tags(d, r)


def hud(d, n=2, heat=51) -> None:
    heat_bar(d, 470, 22, 340, heat)
    dial(d, (70, 70), n)


def heat_ticks(d, x=470, y=22, w=340) -> None:
    """Raid size at each Heat threshold: threat count as small cobalt shields above the 25/50/75/100 marks."""
    for m, n in ((25, 2), (50, 3), (75, 4), (100, 5)):
        tx = x + w * m / 100
        for i in range(n):
            shield(d, (tx - (n - 1) * 5 + i * 10, y - 8), 4, THREAT, outline=THREAT)


# ---------- frames ----------
def f0():
    img, d = new_frame(NAME, "netrun")
    heat_bar(d, 470, 40, 340, 51)
    heat_ticks(d, 470, 40)
    why_chain(d, 560, 70)
    nodes = [(160, 380), (330, 300), (330, 460), (520, 380), (700, 300), (700, 460), (880, 380)]
    links = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 6), (5, 6)]
    for a, b in links:
        d.line([nodes[a], nodes[b]], fill=CELL_DIM, width=4)
    for i, (x, y) in enumerate(nodes):
        done = i <= 3
        netrun_hex(d, (x, y), 26, CELL, (50, 46, 30) if done else PANEL)
        if i == 3:
            asset_icon(d, (x, y), "CREW", 12)
    hx, hy = 1060, 380
    d.line([nodes[6], (hx, hy)], fill=CELL_DIM, width=4)
    d.ellipse((hx - 40, hy - 40, hx + 40, hy + 40), fill=(34, 36, 58), outline=CELL, width=4)
    node_icon(d, (hx, hy), "HOME", 50, CELL)
    dial(d, (hx, hy - 120), 2)
    for i, (x, y) in enumerate(nodes[4:6] + nodes[6:]):
        pass
    for i, t in enumerate(("COLLECTOR", "AUDITOR", "ENFORCER")):
        threat_chip(d, (hx - 80 + i * 80, hy + 110), t, scale=0.75)
    d.line([(hx, hy + 44), (hx, hy + 70)], fill=THREAT, width=3)
    record(d, hx - 15, hy + 190, 1, 1)
    header(d, NAME, 0, "Netrun map: dial = 2 netruns (hex inside) until home; raid size per Heat tier above the bar; the record: 1 raid held clean")
    return img


def f1():
    img, d = new_frame(NAME, "warning")
    r = R["BARE"]
    base(d)
    hud(d)
    why_chain(d, 560, 52)
    routes(d, r)
    panel(d, (930, 100, 1268, 330))
    for i, t in enumerate(("COLLECTOR", "AUDITOR", "ENFORCER")):
        y = 118 + i * 70
        threat_chip(d, (972, y + 22), t, scale=0.6)
        for j, n in enumerate(r.routes[t][1:]):
            x = 1024 + j * 52
            node_icon(d, (x, y + 22), n, 30, CELL)
            if j:
                arrow(d, (x - 40, y + 22), (x - 14, y + 22), SHADE[t], 3, 7, shorten=0)
    tags(d, r)
    plan_row(d, 1020, 350, "0", r, False, ())
    record(d, 960, 490, 1, 1)
    header(d, NAME, 1, f"Warning at HQ: fixed routes (cobalt, white core) end to end; no cascade, so every tag has a drawn cause; the bare raid nets {net(r):+d}")
    return img


def f2():
    img, d = new_frame(NAME, "draft")
    r = R["BARE"]
    base(d, r)
    hud(d)
    routes(d, r, faint=True)
    tags(d, r)
    panel(d, (260, 500, 1020, 700), edge=CELL)
    for i, a in enumerate(POOL):
        card(d, 280 + i * 116, 520, a, sel=a in PICK["P1"])
    for i in range(3):
        d.rounded_rectangle((880, 528 + i * 52, 1000, 568 + i * 52), radius=6, fill=CELL if i < 3 else PANEL)
        piece(d, (940, 548 + i * 52), PICK["P1"][i], 9, BG)
    header(d, NAME, 2, f"Draft (3 of 5): each card previews its best single placement against this raid: nodes lost {lost(r)} struck to N; turret, ICE, railgun taken")
    return img


def f3():
    img, d = new_frame(NAME, "planning")
    r = R["RAIL"]
    base(d, r)
    hud(d)
    routes(d, r)
    tags(d, r)
    place_assets(d, P["RAIL"])
    for k in ("FW", "VAULT", "HOME", "PROXY", "RELAY"):
        x, y = XF.p(k)
        d.ellipse((x - 40, y - 40, x + 40, y + 40), outline=CELL, width=2)
    b = R["BARE"]
    d.rounded_rectangle((20, 140, 250, 210), radius=6, fill=CELL)
    bolt(d, (36, 175), 9, BG)
    flag(d, (54, 175), 9, BG)
    struck(d, (70, 162), lost(b), lost(r), 22, BG)
    coin(d, (150, 175), 10, BG)
    text(d, (164, 162), f"{net(r):+d}", 22, BG, "mono")
    G3.threat_strip(d, r, "ENFORCER", 20, 600)
    for i, a in enumerate(("TURRET", "ICE")):
        card(d, 710 + i * 116, 560, a, sel=a == "TURRET", preview=False, h=96)
    header(d, NAME, 3, f"Planning: railgun on RELAY rings its reach; what-if lost {lost(b)} > {lost(r)}, net {net(b):+d} > {net(r):+d}; effective numbers printed on placed pieces; Enforcer strip")
    return img


def f4():
    img, d = new_frame(NAME, "forecast")
    r = R["P1"]
    base(d, r)
    hud(d)
    routes(d, r)
    tags(d, r)
    place_assets(d, P["P1"])
    panel(d, (1012, 96, 1272, 470))
    plan_row(d, 1018, 104, "1", R["P1"], True, PICK["P1"], NEXT["P1"][0])
    plan_row(d, 1018, 222, "2", R["P2"], False, PICK["P2"], NEXT["P2"][0])
    plan_row(d, 1018, 340, "3", R["P3"], False, PICK["P3"])
    G3.threat_strip(d, r, "ENFORCER", 20, 600)
    net_box(d, 1018, 500, r)
    button(d, (1060, 640, 1268, 690), "START RAID")
    header(d, NAME, 4, f"Forecast: plan 1 CLEAN net {net(R['P1']):+d} (next raid {lost(NEXT['P1'][0])} lost); plan 2 CLEAN net {net(R['P2']):+d} (next {lost(NEXT['P2'][0])}); plan 3 all guns net {net(R['P3']):+d}")
    return img


def f5():
    img, d = new_frame(NAME, "resolution")
    r = R["P1"]
    s = 2
    bt = beats(r)
    now = sum(1 for b in bt if b[0] < s) + 2
    total = len(bt)
    secs = min(CAP_S, total * BEAT_S + kills(r) * KILLCAM_S)
    base(d, r, step=s)
    heat_bar(d, 470, 22, 340, 51)
    step_track(d, 470, 70, 340, total, now, "BEAT")
    text(d, (640, 104), f"0:{int(now * BEAT_S):02d} / 0:{int(secs):02d}", 16, DIM, "mono", anchor="ma")
    routes(d, r, faint=True)
    place_assets(d, P["P1"])
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
    # kill-cam inset on the beat's kill
    kl = ev["kills"]
    if kl:
        tid, site = kl[0]
        panel(d, (930, 110, 1268, 300), fill=(16, 18, 36), edge=CELL, width=3)
        threat(d, (1010, 200), tid, 34, hp=0, ghost=True)
        pencil_x(d, (1010, 200), 36, seed=6)
        node_icon(d, (1180, 200), site, 60, CELL)
        skull(d, (1100, 160), 12)
        coin(d, (1090, 262), 10)
        text(d, (1106, 250), f"+{SALVAGE}", 22, INK, "mono")
    speed_controls(d, 1060, 660)
    header(d, NAME, 5, f"Resolution, no input: one beat (~1 s) per shot or hit plus a 2 s kill-cam per kill: {total} beats, {int(secs)} s (cap {CAP_S}); numbered shots; kill-cam pays salvage on each kill")
    return img


def f6():
    img, d = new_frame(NAME, "aftermath")
    r = R["P1"]
    base(d, r)
    heat_bar(d, 470, 22, 340, 51, raid_at=None)
    tags(d, r)
    stamp_box(img, d, (1010, 170), r)
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
    text(d, (66, 656), "51 = 51", 20, HEAT, "mono")
    record(d, 760, 640, 2, 2)
    button(d, (1090, 640, 1265, 690), "BACK TO HQ")
    header(d, NAME, 6, f"Aftermath: CLEAN tier stamp with the net ({net(r):+d} = salvage {SALVAGE * kills(r)} + clean {CLEAN_BONUS} - patch {price(r)}); Heat unchanged; record gains a clean shield")
    return img


def f7():
    img, d = new_frame(NAME, "next raid")
    r, start = NEXT["P1"]
    r2, _ = NEXT["P2"]
    base(d, start=start)
    heat_bar(d, 470, 22, 340, 76, raid_at=75)
    why_chain(d, 560, 52, 76, 75)
    dial(d, (70, 70), 2)
    routes(d, r)
    tags(d, r)
    panel(d, (950, 420, 1268, 700))
    mini = MapXf(950, 440, 0.38)
    for a, b in LINKS:
        d.line([mini.p(a), mini.p(b)], fill=CELL_DIM, width=2)
    for k in NODES:
        x, y = mini.p(k)
        if k.startswith("C"):
            shield(d, (x, y), 7, CORP)
            continue
        o = r2.nodes[k]["outcome"]
        col = THREAT_LIGHT if o == "taken" else (DOWN_GREY if o == "down" else CELL)
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(34, 36, 58), outline=col, width=2)
        if o == "taken":
            pencil_x(d, (x, y), 9, seed=2)
    for tid, path in r2.routes.items():
        for a, b in zip(path, path[1:]):
            arrow(d, mini.p(a), mini.p(b), SHADE[tid], 2, 7, shorten=10)
    text(d, (966, 664), "2", 22, DIM, "mono")
    bolt(d, (1010, 680), 8)
    flag(d, (1024, 680), 8, THREAT_LIGHT)
    struck(d, (1040, 668), lost(r), lost(r2), 18, INK)
    header(d, NAME, 7, f"Next raid (Heat 76) after plan 1, unpatched: scuffed RELAY draws the Enforcer ({lost(r)} lost); inset: after plan 2 (RELAY untouched): {lost(r2)} lost")
    return img


FRAMES = [f0, f1, f2, f3, f4, f5, f6, f7]

if __name__ == "__main__":
    for k, r in R.items():
        print(k, summary(r), "kills", kills(r), "price", price(r), "net", net(r), "beats", len(beats(r)))
    for k, (r, s) in NEXT.items():
        print("NEXT", k, summary(r), "lost", lost(r), r.routes)
    print("PREVIEW", PREVIEW, "bare lost", lost(R["BARE"]))
