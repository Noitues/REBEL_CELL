"""Concept B: SIEGE LANES. Tower-defense read of the network: wave previews at each entry (Thronefall /
Kingdom Rush), routes drawn as lanes with numbered step ticks (Arknights route preview), and an HP ledger
that shows each threat's integrity at every tick, so the death point and leftover damage are visible before
committing. Autoplay is hands-off."""

from __future__ import annotations

from rc_draw import *  # noqa: F403

NAME = "B SIEGE LANES"
XF = MapXf(250, 95, 0.85)
ROUTES = {"COLLECTOR": ["C1", "RELAY", "FW", "HOME"], "AUDITOR": ["C2", "PROXY", "VAULT"], "ENFORCER": ["C2", "PROXY"]}
OFFS = {"COLLECTOR": (0, -14), "AUDITOR": (12, 12), "ENFORCER": (-12, 14)}
# HP ledger with the forecast plan (turret on VAULT, ICE LOCK on RELAY): (node, step, hp after the step) per threat.
LEDGER = {"COLLECTOR": [("RELAY", 1, 8), ("RELAY", 2, 4), ("FW", 3, 1), ("HOME", 4, 0)],
          "AUDITOR": [("VAULT", 1, 4), ("VAULT", 2, 0)],
          "ENFORCER": [("PROXY", 1, 25), ("PROXY", 2, 25), ("PROXY", 6, 25)]}
LEDGER_BARE = {"COLLECTOR": [("RELAY", 1, 12), ("FW", 2, 9), ("HOME", 3, 9)],
               "AUDITOR": [("VAULT", 1, 8), ("VAULT", 6, 8)],
               "ENFORCER": [("PROXY", 1, 25), ("PROXY", 6, 25)]}


def lanes(d, ticks: bool = True) -> None:
    for tid, keys in ROUTES.items():
        ox, oy = OFFS[tid]
        pts = [(XF.p(k)[0] + ox, XF.p(k)[1] + oy) for k in keys]
        for a, b in zip(pts, pts[1:]):
            d.line([a, b], fill=(30, 46, 110), width=22)
        for a, b in zip(pts, pts[1:]):
            arrow(d, a, b, THREAT, 5, 14, shorten=26)


def base(d, states=None, hp=None, lose=None) -> None:
    states, hp, lose = states or {}, hp or {}, lose or {}
    draw_links(d, XF, dim=True)
    lanes(d)
    for k in NODES:
        node(d, XF, k, states.get(k, "ok"), hp.get(k), lose.get(k, 0))


def wave_flag(d, key: str, tids: list[str], arrive: int) -> None:
    x, y = XF.p(key)
    x += 40
    y -= 70
    w = 40 + 44 * len(tids)
    panel(d, (x, y, x + w, y + 56), fill=(18, 26, 64), edge=THREAT)
    for i, t in enumerate(tids):
        threat(d, (x + 26 + i * 44, y + 24), t, 13, show_hp=False)
    text(d, (x + w - 8, y + 6), f"x{len(tids)}", 15, THREAT_LIGHT, "mono", anchor="ra")
    d.line([(x, y + 56), (x - 30, y + 66)], fill=THREAT, width=3)


def ledger_chips(d, ledger, alpha_dim: bool = False) -> None:
    """At each step tick: a chip with the step number and the threat's HP left; a skull where it dies."""
    for tid, rows in ledger.items():
        ox, oy = OFFS[tid]
        mhp = THREATS[tid][1]
        for n, (k, step, hp) in enumerate(rows):
            x, y = XF.p(k)
            x += ox * 3.2 + (n % 2) * 0
            y += oy * 3.2 - 18 * (n if k == rows[0][0] and n else 0)
            dead = hp <= 0
            col = (90, 90, 100) if alpha_dim else (DMG if dead else THREAT_LIGHT)
            d.rounded_rectangle((x - 30, y - 12, x + 30, y + 12), radius=5, fill=BG2, outline=col, width=2)
            text(d, (x - 25, y - 9), str(step), 13, DIM, "mono")
            if dead:
                skull(d, (x + 8, y), 9, DMG)
            else:
                w = 30
                d.rectangle((x - 12, y - 4, x - 12 + w, y + 4), outline=(60, 70, 110))
                d.rectangle((x - 12, y - 4, x - 12 + w * hp / mhp, y + 4), fill=THREAT_LIGHT)


def skull(d, c, r, col) -> None:
    x, y = c
    d.ellipse((x - r, y - r, x + r, y + r * 0.6), fill=col)
    d.rectangle((x - r * 0.55, y + r * 0.3, x + r * 0.55, y + r), fill=col)
    d.ellipse((x - r * 0.6, y - r * 0.3, x - r * 0.1, y + r * 0.2), fill=BG)
    d.ellipse((x + r * 0.1, y - r * 0.3, x + r * 0.6, y + r * 0.2), fill=BG)


def hand(d, sel: str | None = None, used=()) -> None:
    for i, a in enumerate(("TURRET", "ICE", "DECOY", "CREW")):
        asset_card(d, 20, 120 + i * 128, a, selected=a == sel, used=a in used)


def wave_panel(d) -> None:
    panel(d, (1050, 100, 1265, 330))
    text(d, (1064, 110), "WAVE", 15, DIM)
    for i, t in enumerate(("COLLECTOR", "AUDITOR", "ENFORCER")):
        y = 150 + i * 60
        threat(d, (1085, y + 10), t, 16, show_hp=False)
        name, hp, dmg, spd, rt, *_ = THREATS[t]
        text(d, (1115, y - 6), f"{hp}", 18, THREAT_LIGHT, "mono")
        swords(d, (1166, y + 4), 7)
        text(d, (1180, y - 6), f"{dmg}", 18, DMG, "mono")
        for s in range(spd):
            d.polygon([(1215 + s * 12, y - 4), (1225 + s * 12, y + 4), (1215 + s * 12, y + 12)], fill=INK)
        text(d, (1115, y + 18), rt, 11, DIM)


def f1():
    img, d = new_frame(NAME, "warning")
    base(d)
    heat_bar(d, 470, 22, 340, 51)
    wave_flag(d, "C1", ["COLLECTOR"], 1)
    wave_flag(d, "C2", ["AUDITOR", "ENFORCER"], 1)
    # Top-center call: raid lands on return; silhouettes; the "why" glyph chain Heat -> shield.
    panel(d, (470, 60, 810, 110), edge=THREAT)
    flame(d, (492, 86), 9, HEAT)
    text(d, (504, 74), "51", 18, HEAT, "mono")
    arrow(d, (530, 85), (575, 85), INK, 3, 9, shorten=0)
    shield(d, (594, 83), 11, THREAT)
    text(d, (614, 72), "RAID ON RETURN TO HQ", 18, INK)
    wave_panel(d)
    header(d, NAME, 1, "Warning: wave flags at each Solace entry (who, how many); lanes show each threat's route; the raid lands on return to HQ")
    return img


def f2():
    img, d = new_frame(NAME, "planning")
    base(d)
    heat_bar(d, 470, 22, 340, 51)
    ledger_chips(d, LEDGER_BARE, alpha_dim=True)
    hand(d, sel="TURRET")
    vx, vy = XF.p("VAULT")
    # Reach-1 ring: the lane segments the turret covers light up yellow.
    for k in ("RELAY", "PROXY", "HOME"):
        d.line([(vx, vy), XF.p(k)], fill=CELL, width=3)
    pencil_circle(d, (vx, vy), 160, CELL, seed=7, width=2)
    d.rounded_rectangle((vx + 36, vy - 20, vx + 76, vy + 20), radius=6, fill=(50, 46, 30), outline=CELL, width=2)
    asset_icon(d, (vx + 56, vy), "TURRET", 12)
    label_tag(d, (vx - 60, vy + 70), "COVERS 3 LANES · 4 / STEP", BG, CELL)
    wave_panel(d)
    header(d, NAME, 2, "Planning: holding TURRET over VAULT lights the lane segments it reaches; grey chips = the raid as it stands")
    return img


def f3():
    img, d = new_frame(NAME, "forecast")
    base(d, lose={"VAULT": 3, "FW": 5, "PROXY": 15})
    heat_bar(d, 470, 22, 340, 51)
    vx, vy = XF.p("VAULT")
    asset_icon(d, (vx + 40, vy + 20), "TURRET", 11)
    rx, ry = XF.p("RELAY")
    asset_icon(d, (rx + 40, ry + 20), "ICE", 11, HOLD)
    ledger_chips(d, LEDGER)
    for k in ("HOME", "FW", "VAULT", "SAFE", "RELAY"):
        mark(d, XF, k, "HOLDS")
    mark(d, XF, "PROXY", "TAKEN")
    hand(d, used=("TURRET", "ICE"))
    panel(d, (1030, 100, 1265, 430), edge=STAMP_HOLD)
    text(d, (1045, 112), "IF THE RAID RUNS", 14, DIM)
    text(d, (1045, 135), "CELL HOLDS", 28, STAMP_HOLD, "stamp")
    node_icon(d, (1060, 205), "HOME", 30, CELL)
    text(d, (1085, 192), "50 > 50", 20, INK, "mono")
    node_icon(d, (1060, 245), "PROXY", 30, THREAT_LIGHT)
    flag(d, (1090, 245), 8, THREAT_LIGHT)
    text(d, (1105, 232), "TAKEN", 18, THREAT_LIGHT)
    skull(d, (1060, 290), 10, DMG)
    text(d, (1085, 278), "2 / 3", 20, INK, "mono")
    d.line([(1045, 320), (1250, 320)], fill=PANEL_EDGE)
    text(d, (1045, 330), "CLEAN NEEDS", 13, DIM)
    threat(d, (1065, 370), "ENFORCER", 12, show_hp=False)
    text(d, (1090, 360), "25 MORE DMG", 16, INK, "mono")
    flame(d, (1060, 405), 8, DIM)
    text(d, (1075, 397), "+5   +12", 16, DIM, "mono")
    button(d, (1090, 640, 1265, 690), "START RAID")
    header(d, NAME, 3, "Forecast: HP ledger chips on every lane tick (step, HP left, skull where it dies); per-node tags; what a clean defense still needs")
    return img


def f4():
    img, d = new_frame(NAME, "resolution")
    base(d, hp={"VAULT": 17, "PROXY": 0}, states={"PROXY": "down"}, lose={})
    heat_bar(d, 470, 22, 340, 51)
    step_track(d, 470, 72, 340, 6, 3)
    ledger_chips(d, LEDGER, alpha_dim=True)
    fx, fy = XF.p("FW")
    threat(d, (fx + 34, fy - 10), "COLLECTOR", 17, hp=1)
    d.line([(fx, fy), (fx + 34, fy - 10)], fill=CELL, width=4)
    text(d, (fx + 60, fy - 52), "-3", 24, CELL, "mono")
    dmg_badge(d, (fx - 44, fy - 40), 5)
    px, py = XF.p("PROXY")
    threat(d, (px + 36, py + 10), "ENFORCER", 17)
    dmg_badge(d, (px - 44, py - 40), 9)
    vx, vy = XF.p("VAULT")
    asset_icon(d, (vx + 40, vy + 20), "TURRET", 11)
    skull(d, (vx + 48, vy - 28), 12, DMG)
    speed_controls(d, 1060, 660)
    text(d, (640, 98), "AUTO-PLAYING", 13, DIM, anchor="ma")
    header(d, NAME, 4, "Resolution: step 3/6, tokens advance along lanes; shots and hits drawn on the map; the forecast chips stay as a faint ruler")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    base(d, states={"PROXY": "taken"}, hp={"VAULT": 17, "FW": 25, "PROXY": 0})
    heat_bar(d, 470, 22, 340, 51)
    for k in ("HOME", "FW", "VAULT", "SAFE", "RELAY"):
        mark(d, XF, k, "HOLDS")
    mark(d, XF, "PROXY", "TAKEN")
    px, py = XF.p("PROXY")
    arrow(d, (px + 10, py + 30), XF.p("SAFE"), THREAT, 5, 14, dash_line=True)
    label_tag(d, (px - 120, py + 50), "NEW ENTRY", INK, THREAT)
    stamp(img, (1000, 200), "CELL HOLDS", STAMP_HOLD, 64, -6, "1 TAKEN · NO HEAT")
    panel(d, (20, 520, 500, 690))
    text(d, (36, 532), "LOST", 14, DIM)
    node_icon(d, (60, 578), "PROXY", 34, THREAT_LIGHT)
    text(d, (90, 565), "PROXY: RECLAIM NETRUN", 18, INK)
    asset_icon(d, (60, 630), "ICE", 13, DIM)
    text(d, (90, 618), "ICE LOCK SPENT", 18, DIM)
    button(d, (1090, 640, 1265, 690), "BACK TO HQ")
    header(d, NAME, 5, "Aftermath: TAKEN node keeps the pencil X and becomes a new entry arrow on the map; stamp states the cost; losses named once")
    return img


FRAMES = [f1, f2, f3, f4, f5]
