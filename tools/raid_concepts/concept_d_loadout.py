"""Concept D: AUTO-BATTLER LOADOUT. The raid is a lineup match (Super Auto Pets / Backpack Battles / The Bazaar):
the corp reveals its lineup per target lane; the player slots defenses (units with triggers and adjacency
synergies) into each node's slots; a deterministic sim strip per lane shows every hit on a tick timeline before
committing. Then the battle auto-plays with zero input."""

from __future__ import annotations

from rc_draw import *  # noqa: F403

NAME = "D AUTO-BATTLER LOADOUT"
LANES = [("HOME", "COLLECTOR"), ("VAULT", "AUDITOR"), ("PROXY", "ENFORCER")]
LANE_Y = [150, 330, 510]
MINI = MapXf(990, 470, 0.33)


def unit_card(d, x, y, tid: str, hp: int | None = None, w: int = 120, h: int = 140) -> None:
    name, mhp, dmg, spd, rt, *_ = THREATS[tid]
    hp = mhp if hp is None else hp
    panel(d, (x, y, x + w, y + h), fill=(18, 26, 64), edge=THREAT, width=3)
    threat(d, (x + w / 2, y + 50), tid, 24, show_hp=False)
    d.ellipse((x - 10, y + h - 34, x + 26, y + h + 2), fill=THREAT, outline=INK, width=2)
    text(d, (x + 8, y + h - 27), str(hp), 18, INK, "mono", anchor="ma")
    d.ellipse((x + w - 26, y + h - 34, x + w + 10, y + h + 2), fill=DMG, outline=INK, width=2)
    text(d, (x + w - 8, y + h - 27), str(dmg), 18, INK, "mono", anchor="ma")
    for s in range(spd):
        d.polygon([(x + w - 30 + s * 12, y + 8), (x + w - 20 + s * 12, y + 16), (x + w - 30 + s * 12, y + 24)], fill=INK)


def node_card(d, x, y, key: str, slots: list[str | None], hp: int | None = None, w: int = 300, h: int = 140) -> list[tuple]:
    panel(d, (x, y, x + w, y + h), fill=(40, 36, 24), edge=CELL, width=3)
    d.ellipse((x + 12, y + 30, x + 82, y + 100), fill=(34, 36, 58), outline=CELL, width=3)
    node_icon(d, (x + 47, y + 65), key, 42, CELL)
    mhp = NODE_HP[key]
    hp_pips(d, x + 47, y + 112, mhp if hp is None else hp, mhp, w=6 if mhp > 30 else 8)
    centers = []
    for i, a in enumerate(slots):
        sx = x + 100 + i * 96
        box = (sx, y + 20, sx + 84, y + 120)
        if a is None:
            d.rounded_rectangle(box, radius=6, outline=(110, 96, 50), width=2)
            text(d, (sx + 42, y + 58), "+", 28, (110, 96, 50), anchor="ma")
        else:
            d.rounded_rectangle(box, radius=6, fill=PANEL, outline=CELL, width=2)
            asset_icon(d, (sx + 42, y + 58), a, 18)
        centers.append((sx + 42, y + 70))
    return centers


def synergy(d, a, b, s: str) -> None:
    d.line([a, b], fill=HOLD, width=4)
    m = lerp(a, b, 0.5)
    label_tag(d, (m[0] - 20, m[1] - 50), s, BG, HOLD, 13)


def sim_strip(d, x, y, w, events: list[tuple[int, str]], result: str, dim: bool = False) -> None:
    """Deterministic tick strip (The Bazaar-style): yellow pips = our hits, cobalt pips = their hits; result chip at the end."""
    ticks = 6
    seg = w / ticks
    d.rectangle((x, y, x + w, y + 30), fill=BG2, outline=PANEL_EDGE)
    for t in range(1, ticks):
        d.line([(x + t * seg, y), (x + t * seg, y + 30)], fill=PANEL_EDGE)
    for t, who in events:
        cx = x + (t - 0.5) * seg + (-10 if who == "us" else 10)
        col = (CELL if who == "us" else THREAT) if not dim else (90, 90, 100)
        d.polygon([(cx, y + 4), (cx + 8, y + 15), (cx, y + 26), (cx - 8, y + 15)], fill=col)
    vcol = {"HOLDS": HOLD, "DOWN": INK, "TAKEN": THREAT_LIGHT}[result]
    d.rounded_rectangle((x + w + 10, y, x + w + 100, y + 30), radius=6, fill=BG2, outline=vcol, width=2)
    text(d, (x + w + 55, y + 6), result, 15, vcol, anchor="ma")


def mini_map(d, marks=None) -> None:
    marks = marks or {}
    panel(d, (970, 450, 1265, 690))
    for a, b in LINKS:
        d.line([MINI.p(a), MINI.p(b)], fill=CELL_DIM, width=2)
    for k in NODES:
        x, y = MINI.p(k)
        if k.startswith("C"):
            shield(d, (x, y), 7, CORP)
        else:
            st = marks.get(k)
            col = DOWN_GREY if st == "DOWN" else (THREAT_LIGHT if st == "TAKEN" else CELL)
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(34, 36, 58), outline=col, width=2)
            if st == "TAKEN":
                pencil_x(d, (x, y), 9, seed=5)
            if st == "DOWN":
                bolt(d, (x, y), 8)


def board(d, slots, hp=None) -> dict:
    hp = hp or {}
    centers = {}
    for (key, tid), y in zip(LANES, LANE_Y):
        centers[key] = node_card(d, 30, y - 70, key, slots[key], hp.get(key))
        unit_card(d, 820, y - 70, tid)
        arrow(d, (810, y), (640, y), THREAT, 4, 12, dash_line=True, shorten=0)
    return centers


EVENTS_PLAN = {
    "HOME": [(3, "us"), (3, "them"), (4, "us")],
    "VAULT": [(1, "us"), (1, "them"), (2, "us")],
    "PROXY": [(1, "them"), (2, "us"), (2, "them"), (3, "us"), (4, "us"), (5, "us")],
}


def f1():
    img, d = new_frame(NAME, "warning")
    heat_bar(d, 470, 22, 340, 51)
    text(d, (640, 70), "INCOMING LINEUP", 30, INK, anchor="ma")
    for i, (key, tid) in enumerate(LANES):
        x = 290 + i * 250
        unit_card(d, x, 140, tid, w=160, h=190)
        arrow(d, (x + 80, 350), (x + 80, 420), THREAT, 5, 14, shorten=0)
        d.ellipse((x + 45, 430, x + 115, 500), fill=(34, 36, 58), outline=CELL, width=3)
        node_icon(d, (x + 80, 465), key, 44, CELL)
        text(d, (x + 80, 510), NODE_NAME[key], 14, INK, anchor="ma")
    panel(d, (20, 560, 460, 690), edge=THREAT)
    flame(d, (50, 595), 10, HEAT)
    text(d, (70, 582), "HEAT 51 > 50 : SOLACE SENDS 3", 18, HEAT)
    text(d, (40, 630), "FIGHT STARTS WHEN YOU RETURN TO HQ", 17, INK)
    mini_map(d)
    header(d, NAME, 1, "Warning: the corp's lineup is revealed as unit cards (HP, damage, speed), each pointing at the node it will attack")
    return img


def f2():
    img, d = new_frame(NAME, "planning")
    heat_bar(d, 470, 22, 340, 51)
    c = board(d, {"HOME": [None, None], "VAULT": ["TURRET", None], "PROXY": ["CREW", None]})
    # Dragging ICE LOCK into PROXY's second slot: ghost + synergy line with the Breaker (+1 step hold).
    gx, gy = c["PROXY"][1]
    d.rounded_rectangle((gx - 42, gy - 50, gx + 42, gy + 50), radius=6, fill=(50, 46, 30), outline=CELL, width=3)
    asset_icon(d, (gx, gy - 12), "ICE", 18)
    synergy(d, c["PROXY"][0], (gx, gy), "+1 HOLD")
    sim_strip(d, 470, 480, 240, [(1, "them"), (2, "them"), (3, "us"), (3, "them")], "TAKEN", dim=True)
    label_tag(d, (470, 440), "WITH ICE: DOWN > HOLDS", BG, CELL)
    for key, y in zip(("HOME", "VAULT"), LANE_Y):
        sim_strip(d, 470, y + 60, 240, [(3, "them")] if key == "HOME" else [(1, "us"), (1, "them"), (2, "us")],
                  "HOLDS")
    tray_y = 640
    for i, a in enumerate(("TURRET", "ICE", "DECOY")):
        d.rounded_rectangle((360 + i * 70, tray_y, 420 + i * 70, tray_y + 50), radius=6, fill=PANEL,
                            outline=CELL if a != "ICE" else (60, 60, 70), width=2)
        asset_icon(d, (390 + i * 70, tray_y + 25), a, 14, CELL if a != "ICE" else DIM)
    header(d, NAME, 2, "Planning: each lane = your node card with slots vs their unit; dragging ICE LOCK next to the Breaker shows a synergy (+1 hold) and flips the lane")
    return img


def f3():
    img, d = new_frame(NAME, "forecast")
    heat_bar(d, 470, 22, 340, 51)
    c = board(d, {"HOME": ["DECOY", None], "VAULT": ["TURRET", None], "PROXY": ["CREW", "ICE"]})
    synergy(d, c["PROXY"][0], c["PROXY"][1], "+1 HOLD")
    for key, y in zip(("HOME", "VAULT", "PROXY"), LANE_Y):
        sim_strip(d, 470, y + 60, 240, EVENTS_PLAN[key], "HOLDS")
    panel(d, (970, 80, 1265, 200), edge=STAMP_CLEAN)
    text(d, (985, 90), "SIM RESULT", 14, DIM)
    text(d, (985, 110), "CLEAN DEFENSE", 30, STAMP_CLEAN, "stamp")
    flame(d, (995, 172), 9, HEAT)
    text(d, (1012, 160), "+5   +12", 20, INK, "mono")
    mini_map(d)
    button(d, (360, 645, 600, 690), "START RAID")
    header(d, NAME, 3, "Forecast: every lane's tick strip shows each hit (yellow ours, cobalt theirs) and the lane result; total = clean defense")
    return img


def f4():
    img, d = new_frame(NAME, "resolution")
    heat_bar(d, 470, 22, 340, 51)
    c = board(d, {"HOME": ["DECOY", None], "VAULT": ["TURRET", None], "PROXY": ["CREW", "ICE"]}, hp={"PROXY": 6})
    for key, y in zip(("HOME", "VAULT", "PROXY"), LANE_Y):
        sim_strip(d, 470, y + 60, 240, [e for e in EVENTS_PLAN[key] if e[0] <= 2], "HOLDS")
        d.line([(470 + 240 * 2 / 6, y + 52), (470 + 240 * 2 / 6, y + 98)], fill=INK, width=3)
    # Lane 3 mid-fight: ice hit on the Enforcer card, -9 floater on PROXY.
    y = LANE_Y[2]
    asset_icon(d, (880, y - 80), "ICE", 16, HOLD)
    dmg_badge(d, (80, y - 82), 9)
    d.line([c["PROXY"][1], (820, y)], fill=CELL, width=4)
    text(d, (640, 68), "TICK 2 / 6  ·  AUTO-PLAYING", 16, DIM, anchor="ma")
    speed_controls(d, 1060, 660)
    header(d, NAME, 4, "Resolution: the lanes fight side by side; a playhead runs along the tick strips; hits flash on the cards; zero input")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    heat_bar(d, 470, 22, 340, 56, raid_at=None)
    stamp(img, (640, 300), "CLEAN DEFENSE", STAMP_CLEAN, 72, -5, "+5 HEAT · +12 SCHEMATICS")
    panel(d, (20, 520, 600, 690))
    text(d, (36, 532), "LINEUP AFTER", 14, DIM)
    for i, (a, s) in enumerate((("TURRET", "10 > 6"), ("ICE", "SPENT"), ("CREW", "XP +1"), ("DECOY", "12 > 12"))):
        asset_icon(d, (70 + i * 140, 590), a, 16, CELL if s != "SPENT" else DIM)
        text(d, (70 + i * 140, 625), s, 16, INK if s != "SPENT" else DIM, "mono", anchor="ma")
    mini_map(d)
    button(d, (1090, 400, 1265, 440), "BACK TO HQ")
    header(d, NAME, 5, "Aftermath: stamp with payout; every unit's wear listed; the HQ map keeps the marks (none this time)")
    return img


FRAMES = [f1, f2, f3, f4, f5]
