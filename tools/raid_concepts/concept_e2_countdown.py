"""Concept E, round 2: COUNTDOWN + ALLOCATION. R2 changes:
- One rule, computed here: notch = the strike a node will take (attackers stacked on the notch as silhouettes);
  fill = defense (FW gun 3, turret 6, ICE 5, crew-hour 2). Shortfall = notch - fill: <= 0 HOLDS untouched; else the
  node loses the shortfall: SCUFFED if < integrity, DOWN if >= integrity, TAKEN if >= 2x integrity. Home loses it.
- Allocation is split over the two HQ visits of the countdown (3 crew-hours each), so the netrun in between matters.
- Hard calls are icon cards (evacuate = TAKEN + refund; go dark = +1 netrun, +4 Heat, +3 crew-hours).
- The strike is watchable: the front crosses the map node by node; each node is a beat where the attackers slam the
  gauge and the shortfall lands as a number.
"""

from __future__ import annotations

from r2_kit import *  # noqa: F403

NAME = "E COUNTDOWN r2"
XF = MapXf(220, 120, 0.84)
NOTCH = {"HOME": [("COLLECTOR", 15)], "FW": [("COLLECTOR", 5)], "RELAY": [("COLLECTOR", 5)],
         "VAULT": [("AUDITOR", 9)], "PROXY": [("ENFORCER", 27), ("AUDITOR", 3)]}
VALUE = {"FWGUN": 3, "TURRET": 6, "ICE": 5, "HOUR": 2}
REFUND = {"PROXY": 5}
ORDER = ["PROXY", "RELAY", "VAULT", "FW", "HOME"]  # the order the front reaches them (right to left)


def outcome(alloc: dict, evac=()) -> dict:
    out = {}
    for n, atk in NOTCH.items():
        notch = sum(v for _, v in atk)
        fill = (VALUE["FWGUN"] if n == "FW" else 0) + sum(VALUE[k] * c for k, c in alloc.get(n, {}).items())
        short = notch - fill
        integ = NODE_HP[n]
        if n in evac:
            o, loss = "taken", integ
        elif short <= 0:
            o, loss = "holds", 0
        elif n == "HOME":
            o, loss = ("breached" if short >= integ else "scuffed"), short
        elif short >= 2 * integ:
            o, loss = "taken", integ
        elif short >= integ:
            o, loss = "down", integ
        else:
            o, loss = "scuffed", short
        out[n] = {"notch": notch, "fill": fill, "short": short, "outcome": o, "before": integ, "after": max(0, integ - loss)}
    return out


VISIT1 = {"PROXY": {"HOUR": 3}}
PLAN1 = {"PROXY": {"HOUR": 4, "TURRET": 1, "ICE": 1}, "HOME": {"HOUR": 2}}
PLAN2 = {"HOME": {"HOUR": 2, "TURRET": 1, "ICE": 1}, "VAULT": {"HOUR": 4}}
R0, RV1 = outcome({}), outcome(VISIT1)
RP1, RP2 = outcome(PLAN1), outcome(PLAN2, evac=("PROXY",))
SCALE = 3.0


def countdown_big(d, n: int, of: int = 2, word: bool = True) -> None:
    x, y = 640, 92
    d.ellipse((x - 46, y - 46, x + 46, y + 46), fill=(16, 22, 52), outline=THREAT, width=5)
    for i in range(of):
        a0, a1 = -90 + i * 360 / of + 6, -90 + (i + 1) * 360 / of - 6
        d.arc((x - 56, y - 56, x + 56, y + 56), a0, a1, fill=THREAT if i < n else (40, 46, 80), width=9)
    text(d, (x, y - 30), str(n), 48, INK, "mono", anchor="ma")
    d.regular_polygon((x - 70, y + 52, 9), 6, outline=THREAT_LIGHT, width=2)
    text(d, (x - 56, y + 42), "x", 14, THREAT_LIGHT, "mono")


def front(d, x: int) -> None:
    for i in range(0, H, 18):
        d.line([(x, i), (x + 40, i + 30)], fill=(40, 60, 140), width=6)
    d.line([(x, 0), (x, H)], fill=THREAT, width=4)


def gauge(d, key: str, r: dict, add: int = 0, drained: bool = False) -> None:
    x, y = XF.p(key)
    gx, gy = x + 40, y + 34
    hmax = 32 * SCALE
    d.rectangle((gx, gy - hmax, gx + 18, gy), fill=BG2, outline=PANEL_EDGE, width=2)
    f = min(r["fill"], 32)
    if f > 0 and not drained:
        d.rectangle((gx + 2, gy - f * SCALE, gx + 16, gy - 2), fill=CELL)
    if add:
        d.rectangle((gx + 2, gy - (f + add) * SCALE, gx + 16, gy - f * SCALE), fill=(255, 240, 160))
    ny = gy - min(r["notch"], 32) * SCALE
    d.line([(gx - 4, ny), (gx + 22, ny)], fill=THREAT, width=4)
    for i, (tid, v) in enumerate(NOTCH[key]):
        threat(d, (gx + 34 + i * 22, ny), tid, 8, show_hp=False)
    text(d, (gx + 26 + 22 * len(NOTCH[key]), ny - 10), str(r["notch"]), 15, THREAT_LIGHT, "mono")
    if r["short"] > 0 and (drained or add == 0):
        d.rectangle((gx + 2, ny, gx + 16, gy - f * SCALE), outline=DMG, width=2)


def base(d, r=None, end=False) -> None:
    draw_links(d, XF)
    for k in NODES:
        if r and end and k in r:
            st = {"down": "down", "taken": "taken"}.get(r[k]["outcome"], "ok")
            node(d, XF, k, st, r[k]["before"], r[k]["before"] - r[k]["after"] if st == "ok" else 0, show_hp=True)
        else:
            node(d, XF, k)


def tags(d, r) -> None:
    for k, v in r.items():
        mark2(d, XF, k, {"outcome": v["outcome"] if v["outcome"] != "breached" else "down", "before": v["before"], "after": v["after"]})


def pool(d, left: int, total: int = 3, x=20, y=600) -> None:
    panel(d, (x, y, x + 210, y + 90))
    for i in range(total):
        col = CELL if i < left else (60, 60, 70)
        d.rounded_rectangle((x + 16 + i * 62, y + 18, x + 66 + i * 62, y + 72), radius=6, fill=col)
        asset_icon(d, (x + 41 + i * 62, y + 40), "CREW", 13, BG if i < left else (40, 40, 50))
        text(d, (x + 41 + i * 62, y + 54), "+2", 13, BG if i < left else (40, 40, 50), "mono", anchor="ma")


def hard_calls(d, x=990, y=330) -> None:
    panel(d, (x, y, x + 278, y + 200))
    node_icon(d, (x + 30, y + 40), "PROXY", 34, CELL)
    arrow(d, (x + 54, y + 40), (x + 90, y + 40), INK, 3, 8, shorten=0)
    flag(d, (x + 110, y + 40), 10, THREAT_LIGHT)
    text(d, (x + 132, y + 28), "+", 22, INK, "mono")
    coin(d, (x + 160, y + 40), 10)
    text(d, (x + 176, y + 28), str(REFUND["PROXY"]), 22, INK, "mono")
    d.line([(x + 14, y + 86), (x + 264, y + 86)], fill=PANEL_EDGE)
    d.ellipse((x + 12, y + 108, x + 52, y + 148), outline=THREAT, width=3)
    text(d, (x + 32, y + 116), "+1", 18, INK, "mono", anchor="ma")
    flame(d, (x + 80, y + 132), 10, HEAT)
    text(d, (x + 94, y + 118), "+4", 22, HEAT, "mono")
    asset_icon(d, (x + 160, y + 130), "CREW", 12)
    text(d, (x + 180, y + 118), "+3", 22, INK, "mono")


def result_box(d, r, x=990, y=110, label=None) -> None:
    lo = [k for k, v in r.items() if v["outcome"] in ("down", "taken")]
    hl = r["HOME"]["before"] - r["HOME"]["after"]
    panel(d, (x, y, x + 278, y + 96), edge=STAMP_HOLD)
    if label:
        text(d, (x + 12, y + 8), label, 22, CELL, "mono")
    node_icon(d, (x + 60, y + 30), "HOME", 30, CELL)
    text(d, (x + 80, y + 18), f"-{hl}", 22, DMG if hl else HOLD, "mono")
    flag(d, (x + 160, y + 30), 10, THREAT_LIGHT)
    text(d, (x + 176, y + 18), str(sum(1 for k in lo if r[k]["outcome"] == "taken")), 22, INK, "mono")
    bolt(d, (x + 222, y + 30), 10)
    text(d, (x + 236, y + 18), str(sum(1 for k in lo if r[k]["outcome"] == "down")), 22, INK, "mono")
    sc = sum(1 for v in r.values() if v["outcome"] == "scuffed" and v is not r["HOME"])
    d.ellipse((x + 50, y + 58, x + 74, y + 82), fill=(20, 60, 60), outline=HOLD, width=2)
    check(d, (x + 62, y + 70), 6, HOLD)
    text(d, (x + 82, y + 58), f"x{sc}", 20, INK, "mono")


def f1():
    img, d = new_frame(NAME, "warning")
    front(d, 1220)
    base(d)
    heat_bar(d, 60, 22, 340, 51)
    why_chain(d, 60, 52)
    countdown_big(d, 2)
    for k in NOTCH:
        gauge(d, k, R0[k])
    tags(d, R0)
    result_box(d, R0)
    header(d, NAME, 1, "Warning: dial = 2 netruns to the strike; the front at the map edge; each gauge's cobalt notch (with who causes it) vs your fill; outcome tags now")
    return img


def f2():
    img, d = new_frame(NAME, "planning")
    front(d, 1220)
    base(d)
    heat_bar(d, 60, 22, 340, 51)
    countdown_big(d, 2)
    for k in NOTCH:
        gauge(d, k, RV1[k] if k != "PROXY" else R0[k], add=6 if k == "PROXY" else 0)
    px, py = XF.p("PROXY")
    dashed(d, (130, 600), (px + 49, py - 20), CELL, 3)
    label_tag(d, (px + 66, py - 50), "+2 +2 +2", BG, CELL, 15)
    pool(d, 0)
    hard_calls(d)
    result_box(d, RV1)
    header(d, NAME, 2, "Planning, HQ visit 1 of 2: 3 crew-hours dragged into PROXY's gauge (+6); hard calls as icon cards: evacuate PROXY (TAKEN, +5) or go dark (+1 netrun, +4 Heat, +3 crew)")
    return img


def f3():
    img, d = new_frame(NAME, "forecast")
    front(d, 1080)
    base(d)
    heat_bar(d, 60, 22, 340, 53)
    countdown_big(d, 1)
    for k in NOTCH:
        gauge(d, k, RP1[k])
    tags(d, RP1)
    for n, items in PLAN1.items():
        x, y = XF.p(n)
        for i, a in enumerate(k for k in items if k != "HOUR"):
            d.ellipse((x - 58, y + 6 + i * 26, x - 32, y + 32 + i * 26), fill=(50, 46, 30), outline=CELL, width=2)
            asset_icon(d, (x - 45, y + 19 + i * 26), a, 8, HOLD if a == "ICE" else CELL)
    result_box(d, RP1, label="1")
    result_box(d, RP2, y=216, label="2")
    pool(d, 0)
    header(d, NAME, 3, "Forecast, HQ visit 2 (1 netrun left, front closer): plan 1 holds every node (home -11) vs plan 2 shields home but evacuates PROXY (+5 refund)")
    return img


def f4():
    img, d = new_frame(NAME, "resolution")
    r = RP1
    hit = ORDER.index("VAULT")
    fx = int(XF.p("VAULT")[0]) + 40
    base(d)
    front(d, fx)
    heat_bar(d, 60, 22, 340, 55)
    step_track(d, 470, 70, 340, len(ORDER), hit + 1, "BEAT")
    for k in ORDER[:hit]:
        gauge(d, k, r[k], drained=True)
        mark2(d, XF, k, {"outcome": r[k]["outcome"], "before": r[k]["before"], "after": r[k]["after"]})
    for k in ORDER[hit + 1:]:
        gauge(d, k, r[k])
    gauge(d, "VAULT", r["VAULT"])
    vx, vy = XF.p("VAULT")
    threat(d, (vx + 40, vy - 70), "AUDITOR", 20)
    arrow(d, (vx + 40, vy - 50), (vx + 49, vy - 10), THREAT, 5, 12, shorten=0)
    dmg_badge(d, (vx - 48, vy - 40), r["VAULT"]["short"])
    text(d, (640, 96), "AUTO", 13, DIM, anchor="ma")
    speed_controls(d, 1060, 660)
    header(d, NAME, 4, "Resolution: the front crosses node by node (beat 3 of 5): the Auditor slams VAULT's gauge, the shortfall (9) lands; earlier nodes already tagged")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    r = RP1
    base(d, r, end=True)
    front(d, 1220)
    heat_bar(d, 60, 22, 340, 55, raid_at=75)
    tags(d, r)

    class _R:
        home_before = 50
        home_after = r["HOME"]["after"]
        clean = False
        breached = False
        nodes = {k: {"outcome": v["outcome"]} for k, v in r.items()}
    stamp_losses(img, d, (980, 200), _R)
    panel(d, (20, 560, 640, 700))
    asset_icon(d, (60, 600), "TURRET", 14)
    text(d, (84, 588), "10", 20, INK, "mono")
    asset_icon(d, (180, 600), "ICE", 14, DIM)
    text(d, (204, 588), "0", 20, DIM, "mono")
    node_icon(d, (330, 600), "HOME", 34, CELL)
    text(d, (354, 588), "-11", 20, DMG, "mono")
    coin(d, (430, 600), 10)
    text(d, (446, 588), "11", 20, INK, "mono")
    flame(d, (60, 660), 10, HEAT)
    text(d, (80, 648), "NEXT AT 75", 20, HEAT, "mono")
    button(d, (1090, 640, 1265, 690), "BACK TO HQ")
    header(d, NAME, 5, "Aftermath: stamp shows home -11; scuffed nodes keep -N; patch cost 11; the front pulls back to the edge; next strike at Heat 75")
    return img


FRAMES = [f1, f2, f3, f4, f5]

if __name__ == "__main__":
    for nm, r in (("R0", R0), ("V1", RV1), ("P1", RP1), ("P2", RP2)):
        print(nm, {k: (v["notch"], v["fill"], v["outcome"], v["after"]) for k, v in r.items()})
