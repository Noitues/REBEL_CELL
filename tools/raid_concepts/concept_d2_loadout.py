"""Concept D, round 2: AUTO-BATTLER LOADOUT on the real map (Mechabellum: fight on the board you deployed on).
R2 changes: the lineup chips sit at the Solace sites with arrows to their targets; slots hang off the target nodes on
the city map; map adjacency is synergy (a Breaker next to a node boosts its turret and ICE); every tick diamond carries
its number; lane results are icons; numbers come from d2_lane_sim (one consistent run per plan); the aftermath is on
the map."""

from __future__ import annotations

from d2_lane_sim import HP as LHP, LANES, run as lane_run
from r2_kit import *  # noqa: F403

NAME = "D AUTO-BATTLER r2"
XF = MapXf(200, 120, 0.80)
PLAN_X = {"PROXY": ["TURRET", "ICE"], "HOME": ["DECOY"], "VAULT": ["CREW"]}
PLAN_Y = {"HOME": ["TURRET", "ICE"], "VAULT": ["DECOY", "CREW"]}
STEP2 = {"PROXY": ["TURRET"], "VAULT": ["CREW"]}


def crew_of(slots):
    return next((n for n, v in slots.items() if "CREW" in v), None)


RX = lane_run(PLAN_X, crew_of(PLAN_X))
RY = lane_run(PLAN_Y, crew_of(PLAN_Y))
R0 = lane_run({}, None)
R2 = lane_run(STEP2, crew_of(STEP2))
R2W = lane_run({"PROXY": ["TURRET", "ICE"], "VAULT": ["CREW"]}, "VAULT")
PATH = {"COLLECTOR": ["C1", "RELAY", "FW", "HOME"], "AUDITOR": ["C2", "PROXY", "VAULT"], "ENFORCER": ["C2", "PROXY"]}


def slots_at(d, key: str, units: list[str], ghost: str | None = None) -> list[tuple]:
    x, y = XF.p(key)
    out = []
    for i in range(2):
        sx, sy = x + 40 + i * 40, y - 18
        u = units[i] if i < len(units) else None
        if u is None and ghost and i == len(units):
            d.rounded_rectangle((sx, sy, sx + 34, sy + 34), radius=5, fill=(70, 64, 30), outline=CELL, width=3)
            asset_icon(d, (sx + 17, sy + 17), ghost, 9, HOLD if ghost == "ICE" else CELL)
        elif u is None:
            d.rounded_rectangle((sx, sy, sx + 34, sy + 34), radius=5, outline=(120, 104, 50), width=2)
            text(d, (sx + 17, sy + 4), "+", 20, (120, 104, 50), anchor="ma")
        else:
            d.rounded_rectangle((sx, sy, sx + 34, sy + 34), radius=5, fill=PANEL, outline=CELL, width=2)
            asset_icon(d, (sx + 17, sy + 17), u, 9, HOLD if u == "ICE" else CELL)
        out.append((sx + 17, sy + 17))
    return out


def lane_icon(d, c, out: str) -> None:
    x, y = c
    col = {"holds": HOLD, "scuffed": HOLD, "down": INK, "taken": THREAT_LIGHT, "breached": STAMP_BREACH}[out]
    d.ellipse((x - 15, y - 15, x + 15, y + 15), fill=BG2, outline=col, width=2)
    if out in ("holds", "scuffed"):
        check(d, (x, y), 7, HOLD)
    elif out == "down":
        bolt(d, (x, y), 10)
    elif out == "taken":
        flag(d, (x, y), 8, THREAT_LIGHT)
    else:
        text(d, (x, y - 10), "X", 20, STAMP_BREACH, "stamp", anchor="ma")


def strips(d, res, x=840, y=110, upto: int | None = None) -> None:
    """One tick strip per lane: yellow diamonds = our hits, cobalt = theirs, teal = frozen, grey = soaked; number inside."""
    panel(d, (x - 10, y - 10, x + 428, y + 3 * 92))
    for i, (node_k, tid) in enumerate(LANES):
        r = res[node_k]
        yy = y + i * 92
        node_icon(d, (x + 14, yy + 30), node_k, 30, CELL)
        threat(d, (x + 50, yy + 30), tid, 10, show_hp=False)
        sx = x + 74
        seg = 50
        for t in range(6):
            d.rectangle((sx + t * seg, yy + 6, sx + (t + 1) * seg - 2, yy + 56), fill=BG2, outline=PANEL_EDGE)
            text(d, (sx + t * seg + 3, yy + 7), str(t + 1), 10, DIM, "mono")
        per_tick: dict[int, list] = {}
        for (t, kind, n) in r["events"]:
            per_tick.setdefault(t, []).append((kind, n))
        for t, evs in per_tick.items():
            if upto is not None and t > upto:
                continue
            for j, (kind, n) in enumerate(evs[:2]):
                cx = sx + (t - 1) * seg + 14 + j * 22
                cy = yy + 34
                col = {"us": CELL, "them": THREAT, "frozen": HOLD, "soak": DOWN_GREY, "kill": DMG}[kind]
                if kind == "kill":
                    text(d, (cx, cy - 12), "X", 22, DMG, "stamp", anchor="ma")
                    continue
                d.polygon([(cx, cy - 13), (cx + 11, cy), (cx, cy + 13), (cx - 11, cy)], fill=col)
                if n:
                    text(d, (cx, cy - 7), str(n), 12, BG, "mono", anchor="ma")
        if upto is None or upto >= 6:
            if node_k == "HOME" and r["node_after"] < LHP["HOME"]:
                text(d, (x + 400, yy + 18), f"-{LHP['HOME'] - r['node_after']}", 20, DMG, "mono", anchor="ma")
            else:
                lane_icon(d, (x + 400, yy + 30), r["outcome"])
        if upto is not None:
            px = sx + upto * seg
            d.line([(px, yy + 2), (px, yy + 60)], fill=INK, width=3)


def lineup(d, ghost: bool = False) -> None:
    c1, c2 = XF.p("C1"), XF.p("C2")
    threat_chip(d, (c1[0] + 10, c1[1] - 56), "COLLECTOR", scale=0.85)
    threat_chip(d, (c2[0] - 66, c2[1] + 64), "AUDITOR", scale=0.85)
    threat_chip(d, (c2[0] + 18, c2[1] + 64), "ENFORCER", scale=0.85)


def base(d, res=None) -> None:
    draw_links(d, XF)
    for k in NODES:
        if res and k in res:
            r = res[k]
            st = {"down": "down", "taken": "taken"}.get(r["outcome"], "ok")
            node(d, XF, k, st, LHP[k], LHP[k] - r["node_after"] if st == "ok" else 0)
        else:
            node(d, XF, k)


def hud(d) -> None:
    heat_bar(d, 470, 22, 340, 51)
    countdown(d, (70, 70), 2)


def f1():
    img, d = new_frame(NAME, "warning")
    base(d)
    hud(d)
    why_chain(d, 560, 52)
    for tid, p in PATH.items():
        arrow_path(d, XF, p, (44, 70, 170), 4, dash_line=True)
    for k in ("HOME", "VAULT", "PROXY"):
        slots_at(d, k, [])
    lineup(d)
    strips(d, R0)
    header(d, NAME, 1, "Warning: the Solace lineup (two-number chips) at its sites, arrows to targets; each target shows 2 empty slots; the raid as it stands, per lane")
    return img


def f2():
    img, d = new_frame(NAME, "planning")
    base(d)
    hud(d)
    for tid, p in PATH.items():
        arrow_path(d, XF, p, (44, 70, 170), 4, dash_line=True)
    slots_at(d, "HOME", [])
    vs = slots_at(d, "VAULT", ["CREW"])
    ps = slots_at(d, "PROXY", ["TURRET"], ghost="ICE")
    # Map adjacency = synergy: the Breaker on VAULT is next to PROXY, so PROXY's turret and ICE are boosted.
    d.line([vs[0], ps[0]], fill=HOLD, width=4)
    d.line([vs[0], ps[1]], fill=HOLD, width=4)
    m = lerp(vs[0], ps[1], 0.5)
    label_tag(d, (m[0] + 6, m[1] - 10), "+2  +1", BG, HOLD, 14)
    lineup(d)
    strips(d, R2W)
    # what-if: PROXY lane flips from TAKEN to HOLDS with the ICE.
    lane_icon(d, (1210, 330), R2["PROXY"]["outcome"])
    arrow(d, (1188, 330), (1150, 330), INK, 3, 8, shorten=0)
    for i, a in enumerate(("TURRET", "ICE", "DECOY", "CREW")):
        asset_card2(d, 20 + i * 104, 596, a, selected=a == "ICE", used=a in ("TURRET", "CREW"))
    header(d, NAME, 2, "Planning: Breaker in VAULT's slot is map-adjacent to PROXY: its turret +2, ICE +1 tick (teal links); dropping ICE flips the PROXY lane DOWN > HOLDS")
    return img


def plan_rows(d, x=840, y=420) -> None:
    panel(d, (x - 10, y, x + 428, y + 150))
    for i, (lab, res, plan) in enumerate((("1", RX, PLAN_X), ("2", RY, PLAN_Y))):
        yy = y + 12 + i * 68
        on = i == 0
        d.rounded_rectangle((x, yy, x + 410, yy + 58), radius=6, fill=(50, 46, 30) if on else BG2,
                            outline=CELL if on else PANEL_EDGE, width=3 if on else 1)
        text(d, (x + 12, yy + 14), lab, 24, CELL if on else DIM, "mono")
        node_icon(d, (x + 60, yy + 29), "HOME", 28, CELL)
        hl = LHP["HOME"] - res["HOME"]["node_after"]
        text(d, (x + 78, yy + 16), f"-{hl}", 20, DMG if hl else HOLD, "mono")
        for j, k in enumerate(("VAULT", "PROXY")):
            node_icon(d, (x + 150 + j * 110, yy + 29), k, 28, CELL)
            lane_icon(d, (x + 186 + j * 110, yy + 29), res[k]["outcome"])
        n_lost = sum(1 for r in res.values() if r["outcome"] in ("down", "taken"))
        flag(d, (x + 370, yy + 29), 9, THREAT_LIGHT)
        text(d, (x + 384, yy + 16), str(n_lost), 20, INK, "mono")


def f3():
    img, d = new_frame(NAME, "forecast")
    base(d, RX)
    hud(d)
    for tid, p in PATH.items():
        arrow_path(d, XF, p, THREAT, 4)
    slots_at(d, "HOME", PLAN_X["HOME"])
    slots_at(d, "VAULT", PLAN_X["VAULT"])
    slots_at(d, "PROXY", PLAN_X["PROXY"])
    lineup(d)
    strips(d, RX)
    plan_rows(d)
    button(d, (1090, 640, 1265, 690), "START RAID")
    header(d, NAME, 3, "Forecast: plan 1 holds all three lanes (home -15, no node lost) vs plan 2 (home untouched, PROXY taken); every hit numbered in the strips")
    return img


def f4():
    img, d = new_frame(NAME, "resolution")
    base(d)
    heat_bar(d, 470, 22, 340, 51)
    slots_at(d, "HOME", PLAN_X["HOME"])
    slots_at(d, "VAULT", PLAN_X["VAULT"])
    ps = slots_at(d, "PROXY", PLAN_X["PROXY"])
    t = 3
    strips(d, RX, upto=t)
    px, py = XF.p("PROXY")
    threat(d, (px + 20, py + 62), "ENFORCER", 16, hp=25 - sum(n for tt, k, n in RX["PROXY"]["events"] if k == "us" and tt <= t))
    d.line([ps[0], (px + 20, py + 62)], fill=CELL, width=4)
    hx, hy = XF.p("HOME")
    threat(d, (hx - 60, hy + 20), "COLLECTOR", 16)
    vx, vy = XF.p("VAULT")
    threat(d, (vx - 56, vy + 30), "AUDITOR", 14)
    dmg_badge(d, (vx - 30, vy - 44), 3)
    text(d, (640, 70), "TICK 3 / 6 · AUTO", 16, DIM, anchor="ma")
    speed_controls(d, 1060, 660)
    header(d, NAME, 4, "Resolution: units fire from their map slots at threats parked on the node; a playhead runs the strips; zero input")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    base(d, RX)
    heat_bar(d, 470, 22, 340, 51, raid_at=None)
    for k in ("HOME", "VAULT", "PROXY"):
        r = RX[k]
        mark2(d, XF, k, {"outcome": r["outcome"] if r["outcome"] != "breached" else "down", "before": LHP[k], "after": r["node_after"]})

    class _R:
        home_before = 50
        home_after = RX["HOME"]["node_after"]
        clean = False
        breached = False
        nodes = {k: {"outcome": v["outcome"]} for k, v in RX.items()}
    stamp_losses(img, d, (1000, 200), _R)
    panel(d, (20, 560, 640, 700))
    for i, (a, s) in enumerate((("DECOY", f"12>{RX['HOME']['decoy_after']}"), ("ICE", "0"), ("TURRET", "10"), ("CREW", "+1"))):
        asset_icon(d, (60 + i * 150, 600), a, 14, CELL if a != "ICE" else DIM)
        text(d, (84 + i * 150, 588), s, 20, INK if a != "ICE" else DIM, "mono")
    button(d, (1090, 640, 1265, 690), "BACK TO HQ")
    header(d, NAME, 5, "Aftermath on the map: home -15 in the stamp, scuffed nodes keep -N; each unit's wear (decoy soaked, ICE spent, Breaker +1 XP)")
    return img


FRAMES = [f1, f2, f3, f4, f5]

if __name__ == "__main__":
    for nm, r in (("X", RX), ("Y", RY), ("STEP2", R2), ("R2W", R2W)):
        print(nm, {k: (v["outcome"], v["node_after"], v["events"]) for k, v in r.items()})
