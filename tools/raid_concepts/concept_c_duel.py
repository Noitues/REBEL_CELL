"""Concept C: STRENGTH DUEL. Civilization-style combat preview per node: every targeted node carries a siege
banner with ATTACK vs DEFENSE and a verdict word whose color tracks the margin. The player moves defense into
banners; modifiers are itemised. Resolution plays the duels one by one, hands-off."""

from __future__ import annotations

from rc_draw import *  # noqa: F403

NAME = "C STRENGTH DUEL"
XF = MapXf(260, 110, 0.85)
# Declared targets (from routing rules): node -> attackers. ATK = sum of damage over the raid's 3 beats.
TARGETS = {"HOME": ["COLLECTOR"], "VAULT": ["AUDITOR"], "PROXY": ["ENFORCER"]}
BARE = {"HOME": (15, 50, "HOLDS"), "VAULT": (9, 20, "HOLDS"), "PROXY": (27, 15, "TAKEN")}
PLAN = {"HOME": (15, 50, "HOLDS"), "VAULT": (9, 24, "HOLDS"), "PROXY": (27, 28, "HOLDS")}


def verdict_col(v: str):
    return {"HOLDS": HOLD, "DOWN": INK, "TAKEN": THREAT_LIGHT, "BREACHED": STAMP_BREACH}[v]


def banner(d, key: str, atk: int, dfn: int, v: str, sel: bool = False) -> None:
    """Siege banner over a node: attacker silhouette + ATK (cobalt) | shield + DEF (yellow) | margin bar | verdict."""
    x, y = XF.p(key)
    bx, by = x - 80, y - 108
    panel(d, (bx, by, bx + 160, by + 66), fill=(20, 22, 44), edge=CELL if sel else verdict_col(v), width=3 if sel else 2)
    threat(d, (bx + 20, by + 22), TARGETS[key][0], 10, show_hp=False)
    text(d, (bx + 36, by + 10), str(atk), 22, THREAT_LIGHT, "mono")
    node_icon(d, (bx + 102, by + 22), key, 26, CELL)
    text(d, (bx + 118, by + 10), str(dfn), 22, CELL, "mono")
    tot = atk + dfn
    d.rectangle((bx + 10, by + 40, bx + 150, by + 48), fill=CELL)
    d.rectangle((bx + 10, by + 40, bx + 10 + 140 * atk / tot, by + 48), fill=THREAT)
    text(d, (bx + 80, by + 50), v, 12, verdict_col(v), anchor="ma")
    d.line([(x, by + 66), (x, y - 32)], fill=verdict_col(v), width=2)


def base(d, states=None) -> None:
    states = states or {}
    draw_links(d, XF)
    for k in NODES:
        node(d, XF, k, states.get(k, "ok"))


def defense_tray(d, used=(), sel=None) -> None:
    for i, a in enumerate(("TURRET", "ICE", "DECOY", "CREW")):
        asset_card(d, 20, 110 + i * 128, a, selected=a == sel, used=a in used)


def f1():
    img, d = new_frame(NAME, "warning")
    base(d)
    heat_bar(d, 470, 22, 340, 51)
    for k, (a, df, v) in BARE.items():
        banner(d, k, a, df, v)
        route(d, XF, ["C1", "RELAY", "FW", "HOME"] if k == "HOME" else (["C2", "PROXY", "VAULT"] if k == "VAULT" else ["C2", "PROXY"]),
              THREAT, 3, dash_line=True)
    panel(d, (960, 470, 1265, 690), edge=THREAT)
    shield(d, (990, 500), 14, THREAT)
    text(d, (1015, 488), "SIEGE DECLARED", 22, INK)
    flame(d, (990, 545), 9, HEAT)
    text(d, (1010, 533), "HEAT 51  >  50", 18, HEAT, "mono")
    text(d, (980, 570), "ON RETURN TO HQ", 18, INK)
    text(d, (980, 605), "3 TARGETS", 18, INK)
    for i, k in enumerate(TARGETS):
        node_icon(d, (1100 + i * 40, 615), k, 30, CELL)
    header(d, NAME, 1, "Warning: each target node gets a siege banner, attacker vs defense, verdict word; why (Heat 51 > 50) and when (on return)")
    return img


def f2():
    img, d = new_frame(NAME, "planning")
    base(d)
    heat_bar(d, 470, 22, 340, 51)
    banner(d, "HOME", *BARE["HOME"])
    banner(d, "VAULT", *BARE["VAULT"])
    banner(d, "PROXY", 27, 15, "TAKEN", sel=True)
    defense_tray(d, sel="TURRET")
    # Itemised duel card for the selected PROXY banner, Civ-style, with the dragged TURRET's what-if line.
    panel(d, (900, 100, 1265, 470), edge=CELL)
    text(d, (915, 112), "PROXY SIEGE", 18, INK)
    threat(d, (950, 175), "ENFORCER", 22, show_hp=False)
    text(d, (950, 215), "27", 40, THREAT_LIGHT, "mono", anchor="ma")
    node_icon(d, (1180, 175), "PROXY", 50, CELL)
    text(d, (1180, 215), "15", 40, CELL, "mono", anchor="ma")
    text(d, (1065, 190), "VS", 24, DIM, anchor="ma")
    rows = [("+", "9 x 3 STRIKES", "27", THREAT_LIGHT), ("", "", "", DIM), ("+", "NODE INTEGRITY", "15", CELL),
            ("+", "TURRET (DRAGGING)", "+8", CELL), ("+", "SAFEHOUSE CREW", "+0", DIM)]
    for i, (sgn, lbl, val, col) in enumerate(rows):
        y = 280 + i * 28
        if lbl:
            text(d, (915, y), lbl, 15, col)
            text(d, (1250, y), val, 16, col, "mono", anchor="ra")
    d.line([(915, 425), (1250, 425)], fill=PANEL_EDGE)
    text(d, (915, 434), "TAKEN  >  DOWN", 18, INK)
    header(d, NAME, 2, "Planning: PROXY banner selected; itemised duel (attack lines vs defense lines); dragging TURRET adds +8 and moves TAKEN to DOWN")
    return img


def f3():
    img, d = new_frame(NAME, "forecast")
    base(d)
    heat_bar(d, 470, 22, 340, 51)
    for k, v in PLAN.items():
        banner(d, k, *v)
    px, py = XF.p("PROXY")
    asset_icon(d, (px + 40, py + 20), "TURRET", 11)
    asset_icon(d, (px - 40, py + 20), "CREW", 11)
    vx, vy = XF.p("VAULT")
    asset_icon(d, (vx + 40, vy + 20), "ICE", 11, HOLD)
    defense_tray(d, used=("TURRET", "CREW", "ICE"))
    panel(d, (960, 470, 1265, 690), edge=STAMP_CLEAN)
    text(d, (975, 480), "IF THE SIEGE RUNS", 14, DIM)
    text(d, (975, 502), "CLEAN DEFENSE", 30, STAMP_CLEAN, "stamp")
    text(d, (975, 552), "3 / 3 HOLD", 20, INK, "mono")
    flame(d, (985, 598), 9, HEAT)
    text(d, (1000, 586), "+5 HEAT   +12 SCH", 18, INK, "mono")
    text(d, (975, 625), "PROXY MARGIN: 1", 16, STAMP_HOLD)
    button(d, (1090, 645, 1255, 685), "START SIEGE")
    header(d, NAME, 3, "Forecast: three banners all HOLDS (PROXY by a margin of 1); a clean defense and its +5 Heat, +12 Schematics are stated before commit")
    return img


def f4():
    img, d = new_frame(NAME, "resolution")
    base(d)
    heat_bar(d, 470, 22, 340, 51)
    banner(d, "HOME", *PLAN["HOME"])
    banner(d, "VAULT", *PLAN["VAULT"])
    step_track(d, 470, 72, 340, 3, 3, "DUEL")
    text(d, (640, 98), "AUTO-PLAYING", 13, DIM, anchor="ma")
    # Center-stage duel for PROXY: the two bars push against each other; strike 2 of 3 lands.
    px, py = XF.p("PROXY")
    panel(d, (px - 200, py - 230, px + 200, py - 60), fill=(16, 18, 36), edge=CELL, width=3)
    threat(d, (px - 150, py - 160), "ENFORCER", 30, hp=25)
    node_icon(d, (px + 150, py - 160), "PROXY", 70, CELL)
    d.rectangle((px - 110, py - 110, px + 110, py - 92), fill=CELL)
    d.rectangle((px - 110, py - 110, px - 110 + 220 * 18 / 46, py - 92), fill=THREAT)
    text(d, (px - 110, py - 88), "18 / 27", 16, THREAT_LIGHT, "mono")
    text(d, (px + 110, py - 88), "28", 16, CELL, "mono", anchor="ra")
    dmg_badge(d, (px + 150, py - 215), 9)
    speed_controls(d, 1060, 660)
    header(d, NAME, 4, "Resolution: duels play one at a time on their own node; attack fills against defense strike by strike; no input")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    base(d)
    heat_bar(d, 470, 22, 340, 55, raid_at=None)
    for k in ("HOME", "VAULT", "PROXY", "FW", "SAFE", "RELAY"):
        mark(d, XF, k, "HOLDS")
    stamp(img, (1000, 230), "CLEAN DEFENSE", STAMP_CLEAN, 60, -6, "+5 HEAT · +12 SCHEMATICS")
    panel(d, (20, 540, 520, 690))
    text(d, (36, 552), "AFTER", 14, DIM)
    asset_icon(d, (60, 600), "TURRET", 14, CELL)
    text(d, (85, 588), "TURRET 10 > 3", 18, INK, "mono")
    flame(d, (60, 650), 10, HEAT)
    text(d, (85, 638), "HEAT 51 > 56 · NEXT RAID 75", 18, HEAT, "mono")
    button(d, (1090, 640, 1265, 690), "BACK TO HQ")
    header(d, NAME, 5, "Aftermath: clean defense stamp in teal with its payout; worn turret and new Heat stated; HOLDS ticks stay on the map until the next raid")
    return img


FRAMES = [f1, f2, f3, f4, f5]
