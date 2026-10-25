"""Concept D, round 3: AUTO-BATTLER LOADOUT under the package: fixed lanes (each threat fights its declared target),
a 3-of-5 draft (turret, ICE, decoy, sentry, railgun; the railgun reaches lanes within 2 hops), one clean definition,
SCUFFED priced 1 per point. Numbers from d3_lane_sim.run(). R2 defects fixed: kill = skull glyph (no letter);
multipliers use the x-sign glyph."""

from __future__ import annotations

from r2_kit import *  # noqa: F403

import concept_d2_loadout as D
from d3_lane_sim import HP as LHP, LANES, POOL, clean, price, run

NAME = "D AUTO-BATTLER r3"
XF = D.XF
PLAN1 = {"PROXY": ["TURRET"], "HOME": ["ICE", "RAILGUN"], "VAULT": ["CREW"]}
PLAN2 = {"PROXY": ["TURRET", "ICE"], "HOME": ["DECOY"], "VAULT": ["CREW"]}
STEP = {"HOME": ["RAILGUN"], "VAULT": ["CREW"]}
R0, R1, R2, RS = run({}), run(PLAN1), run(PLAN2), run(STEP)
RSW = run({"HOME": ["RAILGUN"], "VAULT": ["CREW"], "PROXY": ["TURRET"]})


def skull(d, c, r, col=DMG) -> None:
    x, y = c
    d.ellipse((x - r, y - r, x + r, y + r * 0.6), fill=col)
    d.rectangle((x - r * 0.55, y + r * 0.3, x + r * 0.55, y + r), fill=col)
    d.ellipse((x - r * 0.6, y - r * 0.3, x - r * 0.1, y + r * 0.2), fill=BG)
    d.ellipse((x + r * 0.1, y - r * 0.3, x + r * 0.6, y + r * 0.2), fill=BG)


def strips(d, res, x=840, y=110, upto=None) -> None:
    panel(d, (x - 10, y - 10, x + 428, y + 3 * 92))
    for i, (node_k, tid) in enumerate(LANES):
        r = res[node_k]
        yy = y + i * 92
        node_icon(d, (x + 14, yy + 30), node_k, 30, CELL)
        threat(d, (x + 50, yy + 30), tid, 10, show_hp=False)
        sx, seg = x + 74, 50
        for t in range(6):
            d.rectangle((sx + t * seg, yy + 6, sx + (t + 1) * seg - 2, yy + 56), fill=BG2, outline=PANEL_EDGE)
            text(d, (sx + t * seg + 3, yy + 7), str(t + 1), 10, DIM, "mono")
        per: dict[int, list] = {}
        for (t, kind, n) in r["events"]:
            per.setdefault(t, []).append((kind, n))
        for t, evs in per.items():
            if upto is not None and t > upto:
                continue
            for j, (kind, n) in enumerate(evs[:3]):
                cx, cy = sx + (t - 1) * seg + 11 + j * 15, yy + 34
                if kind == "kill":
                    skull(d, (cx + 4, cy), 9)
                    continue
                col = {"us": CELL, "rail": (255, 240, 160), "them": THREAT, "frozen": HOLD, "soak": DOWN_GREY}[kind]
                d.polygon([(cx, cy - 12), (cx + 8, cy), (cx, cy + 12), (cx - 8, cy)], fill=col)
                if n:
                    text(d, (cx, cy - 6), str(n), 10, BG, "mono", anchor="ma")
        if upto is None:
            if node_k == "HOME" and r["node_after"] < LHP["HOME"]:
                text(d, (x + 400, yy + 18), f"-{LHP['HOME'] - r['node_after']}", 20, DMG, "mono", anchor="ma")
            else:
                D.lane_icon(d, (x + 400, yy + 30), r["outcome"])
                if r["outcome"] == "scuffed":
                    text(d, (x + 400, yy + 48), f"-{LHP[node_k] - r['node_after']}", 12, DMG, "mono", anchor="ma")
        else:
            px = sx + upto * seg
            d.line([(px, yy + 2), (px, yy + 60)], fill=INK, width=3)


def plan_rows(d, x=840, y=420) -> None:
    import concept_g3_merged as Gm
    panel(d, (x - 10, y, x + 428, y + 150))
    for i, (lab, res, plan) in enumerate((("1", R1, PLAN1), ("2", R2, PLAN2))):
        yy = y + 12 + i * 68
        on = i == 0
        d.rounded_rectangle((x, yy, x + 410, yy + 58), radius=6, fill=(50, 46, 30) if on else BG2,
                            outline=CELL if on else PANEL_EDGE, width=3 if on else 1)
        text(d, (x + 12, yy + 14), lab, 24, CELL if on else DIM, "mono")
        node_icon(d, (x + 56, yy + 29), "HOME", 26, CELL)
        hl = LHP["HOME"] - res["HOME"]["node_after"]
        text(d, (x + 72, yy + 16), f"-{hl}", 20, DMG if hl else HOLD, "mono")
        for j, k in enumerate(("VAULT", "PROXY")):
            node_icon(d, (x + 140 + j * 84, yy + 29), k, 26, CELL)
            D.lane_icon(d, (x + 172 + j * 84, yy + 29), res[k]["outcome"])
        coin(d, (x + 316, yy + 29), 9)
        text(d, (x + 330, yy + 16), str(price(res)), 20, INK, "mono")
        if clean(res):
            check(d, (x + 390, yy + 29), 9, STAMP_CLEAN)


def place(d, slots, ghost=None):
    out = {}
    for k in ("HOME", "VAULT", "PROXY"):
        units = [("TURRET" if u in ("SENTRY",) else u) for u in slots.get(k, [])]
        units = [u if u != "RAILGUN" else "TURRET" for u in units]
        out[k] = D.slots_at(d, k, units, ghost=ghost if k == "PROXY" else None)
        for i, u in enumerate(slots.get(k, [])):
            if u == "RAILGUN":
                cx, cy = out[k][i]
                d.line([(cx - 12, cy), (cx + 12, cy)], fill=CELL, width=4)
    return out


def f1():
    img, d = new_frame(NAME, "warning")
    D.base(d)
    D.hud(d)
    why_chain(d, 560, 52)
    for tid, p in D.PATH.items():
        arrow_path(d, XF, p, (44, 70, 170), 4, dash_line=True)
    place(d, {})
    D.lineup(d)
    strips(d, R0)
    header(d, NAME, 1, "Warning: the Solace lineup at its sites, fixed arrows to targets; empty slots; per-lane strips of the raid as it stands")
    return img


def f2():
    img, d = new_frame(NAME, "draft + planning")
    D.base(d)
    D.hud(d)
    for tid, p in D.PATH.items():
        arrow_path(d, XF, p, (44, 70, 170), 4, dash_line=True)
    s = place(d, STEP, ghost="TURRET")
    # railgun reach 2 from HOME: rings on the three lane nodes it reaches
    for k in ("HOME", "VAULT", "PROXY"):
        x, y = XF.p(k)
        d.ellipse((x - 38, y - 38, x + 38, y + 38), outline=CELL, width=2)
    D.lineup(d)
    strips(d, RS)
    px, py = XF.p("PROXY")
    d.rounded_rectangle((px + 120, py - 30, px + 250, py + 14), radius=6, fill=CELL)
    D.lane_icon(d, (px + 145, py - 8), RS["PROXY"]["outcome"])
    arrow(d, (px + 165, py - 8), (px + 200, py - 8), BG, 3, 8, shorten=0)
    D.lane_icon(d, (px + 222, py - 8), RSW["PROXY"]["outcome"])
    import concept_g3_merged as Gm
    for i, a in enumerate(POOL):
        Gm.card(d, 20 + i * 104, 596, a, sel=a in ("TURRET", "ICE", "RAILGUN"), used=a == "RAILGUN")
    header(d, NAME, 2, "Draft + planning: turret, ICE, railgun drafted; railgun in HOME's slot reaches all three lanes (rings); dragging the turret into PROXY's slot")
    return img


def f3():
    img, d = new_frame(NAME, "forecast")
    D.base(d)
    D.hud(d)
    for tid, p in D.PATH.items():
        arrow_path(d, XF, p, THREAT, 4)
    place(d, PLAN1)
    D.lineup(d)
    strips(d, R1)
    plan_rows(d)
    button(d, (1090, 640, 1265, 690), "START RAID")
    header(d, NAME, 3, f"Forecast: plan 1 is CLEAN (home untouched, nothing lost), patch {price(R1)}; plan 2 (no railgun) holds too but home -{LHP['HOME'] - R2['HOME']['node_after']}")
    return img


def f4():
    img, d = new_frame(NAME, "resolution")
    D.base(d)
    heat_bar(d, 470, 22, 340, 51)
    place(d, PLAN1)
    t = 2
    strips(d, R1, upto=t)
    for (n, tid) in LANES:
        x, y = XF.p(n)
        hp = THREATS[tid][1] - sum(v for tt, k, v in R1[n]["events"] if k in ("us", "rail") and tt <= t)
        if hp > 0:
            threat(d, (x - 60, y + 30), tid, 14, hp=hp)
    text(d, (640, 70), "TICK 2 / 6 · AUTO", 16, DIM, anchor="ma")
    speed_controls(d, 1060, 660)
    header(d, NAME, 4, "Resolution: lanes fight side by side from their map slots; a playhead runs the strips; zero input")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    D.base(d)
    heat_bar(d, 470, 22, 340, 56, raid_at=None)
    for k in ("HOME", "VAULT", "PROXY"):
        r = R1[k]
        mark2(d, XF, k, {"outcome": r["outcome"], "before": LHP[k], "after": r["node_after"]})

    class _R:
        home_before = 50
        home_after = R1["HOME"]["node_after"]
        clean = clean(R1)
        breached = False
        nodes = {k: {"outcome": v["outcome"]} for k, v in R1.items()}
    stamp_losses(img, d, (1000, 200), _R)
    panel(d, (20, 560, 700, 700))
    i = 0
    for k, v in R1.items():
        if v["outcome"] != "scuffed":
            continue
        x = 40 + i * 220
        node_icon(d, (x + 20, 610), k, 34, CELL)
        loss = LHP[k] - v["node_after"]
        text(d, (x + 44, 598), f"-{loss}", 20, DMG, "mono")
        arrow(d, (x + 84, 610), (x + 114, 610), INK, 3, 8, shorten=0)
        coin(d, (x + 134, 610), 10)
        text(d, (x + 150, 598), str(loss), 20, INK, "mono")
        i += 1
    button(d, (1090, 640, 1265, 690), "BACK TO HQ")
    header(d, NAME, 5, "Aftermath on the map: CLEAN stamp with payout; each scuffed node with its patch price")
    return img


FRAMES = [f1, f2, f3, f4, f5]

if __name__ == "__main__":
    for nm, r in (("R0", R0), ("R1", R1), ("R2", R2), ("RS", RS)):
        print(nm, clean(r), price(r), {k: (v["outcome"], v["node_after"]) for k, v in r.items()})
