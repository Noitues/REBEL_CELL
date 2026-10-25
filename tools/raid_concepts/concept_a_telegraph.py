"""Concept A: TELEGRAPH. Into the Breach-style exact intents for the WHOLE raid, scrubbed on a step timeline;
plan once, commit, then the raid auto-plays with zero input (speed / skip only)."""

from __future__ import annotations

from rc_draw import *  # noqa: F403

NAME = "A TELEGRAPH"
XF = MapXf(280, 105, 0.82)


def hud(d, round_no: int | None = None, cp: int = 3) -> None:
    heat_bar(d, 470, 22, 340, 51)
    if round_no is not None:
        timeline(d, round_no)


# Strikes per step for the scrubber: (threat, node) pairs that hit at that step in the planned raid.
TIMELINE = {1: ["COLLECTOR", "AUDITOR", "ENFORCER"], 2: ["COLLECTOR", "AUDITOR", "ENFORCER"], 3: ["COLLECTOR", "ENFORCER"],
            4: ["ENFORCER"], 5: ["ENFORCER"], 6: ["ENFORCER"]}


def timeline(d, now: int) -> None:
    """Step scrubber: six cells, each with the silhouettes that strike in that step; the scrubbed step is lit."""
    x0, y0 = 470, 60
    text(d, (x0 - 10, y0 + 12), "STEP", 13, DIM, anchor="ra")
    for s in range(1, 7):
        x = x0 + (s - 1) * 58
        lit = s == now
        d.rounded_rectangle((x, y0, x + 52, y0 + 40), radius=5, fill=(50, 46, 30) if lit else PANEL,
                            outline=CELL if lit else PANEL_EDGE, width=3 if lit else 1)
        text(d, (x + 5, y0 + 2), str(s), 12, CELL if lit else DIM, "mono")
        for j, t in enumerate(TIMELINE[s]):
            threat(d, (x + 14 + j * 13, y0 + 26), t, 6, show_hp=False)


def base(d, states=None, hp=None, lose=None) -> None:
    states, hp, lose = states or {}, hp or {}, lose or {}
    draw_links(d, XF)
    for k in NODES:
        node(d, XF, k, states.get(k, "ok"), hp.get(k), lose.get(k, 0))


def order_panel(d, rows) -> None:
    panel(d, (1030, 110, 1265, 110 + 60 * len(rows) + 46))
    text(d, (1045, 120), "ATTACK ORDER", 15, DIM)
    for i, (tid, tgt, dmg, held) in enumerate(rows):
        y = 150 + i * 60
        order_badge(d, (1060, y + 18), i + 1)
        threat(d, (1105, y + 18), tid, 15, show_hp=False)
        arrow(d, (1130, y + 18), (1180, y + 18), THREAT, 4, 10, shorten=0)
        node_icon(d, (1200, y + 18), tgt, 30, CELL)
        if held:
            asset_icon(d, (1240, y + 18), "ICE", 11, HOLD)
        else:
            text(d, (1242, y + 8), f"-{dmg}", 20, DMG, "mono", anchor="ma")


def f1():
    img, d = new_frame(NAME, "warning")
    base(d)
    hud(d)
    # Threats parked on corp sites, with their first move telegraphed dashed (what-if).
    threat(d, lerp(XF.p("C1"), XF.p("RELAY"), 0.25), "COLLECTOR")
    threat(d, lerp(XF.p("C2"), XF.p("PROXY"), 0.15), "AUDITOR")
    threat(d, lerp(XF.p("C2"), XF.p("PROXY"), 0.42), "ENFORCER")
    # Banner top-left: raid incoming, why, when.
    panel(d, (20, 90, 380, 260), edge=THREAT)
    shield(d, (52, 125), 16, THREAT)
    text(d, (80, 110), "RAID INCOMING", 26, INK)
    flame(d, (52, 175), 10, HEAT)
    text(d, (80, 162), "YOUR HEAT CROSSED 50", 17, HEAT)
    text(d, (80, 195), "STRIKES WHEN YOU", 17, INK)
    text(d, (80, 217), "RETURN TO HQ", 17, INK)
    for i, t in enumerate(("COLLECTOR", "AUDITOR", "ENFORCER")):
        threat(d, (60 + i * 50, 300), t, 14, show_hp=False)
    text(d, (220, 290), "x3", 24, THREAT_LIGHT, "mono")
    # Return-trip track: the netrun map's last nodes, a red line where the raid lands.
    panel(d, (20, 560, 380, 690))
    text(d, (36, 572), "THIS NETRUN", 14, DIM)
    for i in range(5):
        cx = 60 + i * 64
        d.ellipse((cx - 12, 618, cx + 12, 642), fill=CELL if i < 3 else PANEL, outline=CELL, width=2)
        if i < 4:
            d.line([(cx + 12, 630), (cx + 52, 630)], fill=CELL_DIM, width=3)
    node_icon(d, (60 + 5 * 64, 630), "HOME", 34, CELL)
    shield(d, (60 + 5 * 64, 600), 9, THREAT)
    header(d, NAME, 1, "Warning: Heat 51 queues a raid; three threats wait at Solace sites; it lands when you get home")
    return img


INTENTS_R1 = [("COLLECTOR", "RELAY", 5, False), ("AUDITOR", "VAULT", 3, False), ("ENFORCER", "PROXY", 9, False)]


def telegraphs(d, held_enforcer: bool = False, turret_kill: bool = False) -> None:
    # Moves (cobalt arrows) and strikes (red striped target tile + order + damage), exact, on the board.
    route(d, XF, ["C1", "RELAY"])
    route(d, XF, ["C2", "PROXY", "VAULT"])
    for i, (tid, tgt, dmg, _) in enumerate(INTENTS_R1):
        held = held_enforcer and tid == "ENFORCER"
        x, y = XF.p(tgt)
        if not held:
            pencil_circle(d, (x, y), 44, DMG, seed=i, width=3)
            dmg_badge(d, (x + 46, y - 36), dmg)
        order_badge(d, (x - 46, y - 36), i + 1)
    threat(d, lerp(XF.p("C1"), XF.p("RELAY"), 0.25), "COLLECTOR")
    threat(d, lerp(XF.p("C2"), XF.p("PROXY"), 0.15), "AUDITOR")
    threat(d, lerp(XF.p("C2"), XF.p("PROXY"), 0.42), "ENFORCER", ghost=held_enforcer)
    if held_enforcer:
        p = lerp(XF.p("C2"), XF.p("PROXY"), 0.42)
        asset_icon(d, (p[0] + 30, p[1] - 26), "ICE", 14, HOLD)


def hand(d, used=()) -> None:
    for i, a in enumerate(("TURRET", "ICE", "DECOY", "CREW")):
        asset_card(d, 130 + i * 106, 570, a, selected=(a == "ICE" and "ICE" not in used), used=a in used)


def f2():
    img, d = new_frame(NAME, "planning")
    base(d, lose={"RELAY": 5, "VAULT": 3, "PROXY": 9})
    hud(d, 1, 3)
    telegraphs(d)
    order_panel(d, INTENTS_R1)
    hand(d)
    # Dragging ICE LOCK toward the Enforcer: ghost card + dashed yellow plan line (what-if).
    e = lerp(XF.p("C2"), XF.p("PROXY"), 0.42)
    dashed(d, (290, 570), (e[0] - 10, e[1] + 30), CELL, 3)
    d.rounded_rectangle((e[0] - 30, e[1] + 30, e[0] + 30, e[1] + 80), radius=6, outline=CELL, width=2, fill=(50, 46, 30))
    asset_icon(d, (e[0], e[1] + 55), "ICE", 13)
    label_tag(d, (e[0] + 40, e[1] + 40), "PROXY -9  ->  -0", BG, CELL)
    button(d, (1090, 640, 1265, 690), "START RAID")
    header(d, NAME, 2, "Planning: scrubber at step 1; every move and strike drawn on the board in order; dragging ICE LOCK onto the Enforcer shows PROXY -9 -> 0")
    return img


def f3():
    img, d = new_frame(NAME, "forecast")
    base(d, lose={"RELAY": 5, "VAULT": 3})
    hud(d, 1, 1)
    telegraphs(d, held_enforcer=True)
    # Turret placed on VAULT (yellow plan glyph), shot line onto the Auditor's landing.
    vx, vy = XF.p("VAULT")
    asset_icon(d, (vx + 38, vy + 22), "TURRET", 12)
    order_panel(d, [("COLLECTOR", "RELAY", 5, False), ("AUDITOR", "VAULT", 3, False), ("ENFORCER", "PROXY", 9, True)])
    for k in ("RELAY", "VAULT", "FW", "SAFE", "HOME"):
        mark(d, XF, k, "HOLDS")
    mark(d, XF, "PROXY", "DOWN")
    # End-of-round result strip: what this round costs, exactly. Later rounds unknown until revealed.
    panel(d, (560, 560, 1010, 690))
    text(d, (575, 570), "END OF RAID (ALL 6 STEPS)", 14, DIM)
    node_icon(d, (600, 620), "RELAY", 30, CELL)
    text(d, (625, 607), "15 > 10", 20, INK, "mono")
    node_icon(d, (760, 620), "VAULT", 30, CELL)
    text(d, (785, 607), "20 > 17", 20, INK, "mono")
    node_icon(d, (900, 620), "PROXY", 30, DOWN_GREY)
    bolt(d, (900, 620), 12)
    text(d, (925, 607), "DOWN", 18, INK)
    text(d, (575, 655), "CELL HOLDS  ·  NOT CLEAN: +0 HEAT", 15, STAMP_HOLD)
    hand(d, used=("ICE", "TURRET"))
    button(d, (1090, 640, 1265, 690), "START RAID")
    header(d, NAME, 3, "Forecast: ICE LOCK holds the Enforcer 2 steps, turret on VAULT; every node tagged with its end-of-raid result; PROXY still falls at step 4")
    return img


def f4():
    img, d = new_frame(NAME, "resolution")
    base(d, hp={"RELAY": 10}, lose={"VAULT": 3})
    hud(d)
    step_track(d, 470, 70, 340, 6, 1, "STEP")
    text(d, (640, 96), "AUTO-PLAYING  ·  NO INPUT", 13, DIM, anchor="ma")
    # Strike 1 done (RELAY -5 shown as a fading floater); strike 2 resolving: Auditor on VAULT.
    rx, ry = XF.p("RELAY")
    text(d, (rx + 30, ry - 70), "-5", 26, DMG, "mono")
    threat(d, (rx + 34, ry + 6), "COLLECTOR", 16)
    vx, vy = XF.p("VAULT")
    threat(d, (vx + 40, vy - 30), "AUDITOR", 18, hp=4)
    asset_icon(d, (vx + 38, vy + 22), "TURRET", 12)
    d.line([(vx + 38, vy + 22), (vx + 40, vy - 30)], fill=CELL, width=4)
    text(d, (vx + 70, vy - 50), "-4", 24, CELL, "mono")
    order_badge(d, (vx - 46, vy - 36), 2)
    pencil_circle(d, (vx, vy), 44, DMG, seed=3, width=5)
    dmg_badge(d, (vx + 46, vy + 46), 3)
    e = XF.p("PROXY")
    threat(d, (e[0] + 40, e[1] + 20), "ENFORCER", 18, ghost=True)
    asset_icon(d, (e[0] + 70, e[1] - 6), "ICE", 14, HOLD)
    speed_controls(d, 1060, 660)
    header(d, NAME, 4, "Resolution: hands-off autoplay; strikes fire in numbered order on a fixed board; shots and damage on the units; speed/skip only")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    base(d, states={"PROXY": "down"}, hp={"RELAY": 6, "VAULT": 11, "HOME": 45, "PROXY": 0})
    hud(d)
    mark(d, XF, "PROXY", "DOWN")
    for k in ("RELAY", "VAULT", "HOME", "FW", "SAFE"):
        mark(d, XF, k, "HOLDS")
    stamp(img, (1010, 330), "CELL HOLDS", STAMP_HOLD, 70, -6, "HOME 50 > 45  ·  1 DOWN")
    panel(d, (20, 520, 520, 690))
    text(d, (36, 532), "COST OF THIS RAID", 14, DIM)
    node_icon(d, (60, 580), "PROXY", 34, DOWN_GREY)
    bolt(d, (60, 580), 14)
    text(d, (90, 566), "REPAIR  4", 20, INK, "mono")
    asset_icon(d, (260, 580), "ICE", 14, DIM)
    text(d, (285, 566), "SPENT", 18, DIM)
    flame(d, (60, 640), 10, DIM)
    text(d, (90, 627), "+0 HEAT   (CLEAN = +5, +12)", 18, DIM, "mono")
    button(d, (1090, 640, 1265, 690), "BACK TO HQ")
    header(d, NAME, 5, "Aftermath: big CELL HOLDS stamp with its cost line; DOWN bolt stays on the map; repair price, spent assets and missed clean bonus listed")
    return img


FRAMES = [f1, f2, f3, f4, f5]
