"""Concept E, round 3: COUNTDOWN + ALLOCATION under the RULES_PROPOSAL package.
- Fixed routes with the weaker-node tie-break: the Collector walks C1 > RELAY > VAULT > HOME (VAULT 20 is weaker than
  FW 30), so its notches sit on RELAY, VAULT and HOME. Home is never a corridor.
- 3-of-5 draft: TURRET 6, SENTRY 6 (2 x 3), ICE 5 (blocks a strike), RAILGUN 8 on the biggest shortfall within 2 hops,
  DECOY moves the Collector's home notch onto the decoy node (plan time, it shows on the gauges at once).
- Crew-hours 2 each, 3 per HQ visit, 2 visits.
- One clean definition (home untouched, nothing DOWN or TAKEN); SCUFFED priced 1 per point; DOWN at half install.
- R2 defects fixed: no letter multipliers (the x-sign is a drawn glyph), the gauge rule is the only rule.
"""

from __future__ import annotations

import itertools

from r2_kit import *  # noqa: F403

import concept_e2_countdown as E
from sim import INSTALL

NAME = "E COUNTDOWN r3"
XF = E.XF
POOL = ["TURRET", "ICE", "DECOY", "SENTRY", "RAILGUN"]
VALUE = {"FWGUN": 3, "TURRET": 6, "SENTRY": 6, "ICE": 5, "HOUR": 2}
BASE_NOTCH = {"HOME": [("COLLECTOR", 15)], "RELAY": [("COLLECTOR", 5)],
              "VAULT": [("COLLECTOR", 5), ("AUDITOR", 9)], "PROXY": [("ENFORCER", 27), ("AUDITOR", 3)]}
ORDER = ["PROXY", "RELAY", "VAULT", "HOME"]
NEAR = {"HOME": {"HOME", "FW", "VAULT", "SAFE", "RELAY", "PROXY"}, "FW": {"FW", "HOME", "RELAY", "VAULT", "SAFE"},
        "VAULT": {"VAULT", "HOME", "RELAY", "PROXY", "FW", "SAFE"}, "SAFE": {"SAFE", "HOME", "PROXY", "FW", "VAULT"},
        "RELAY": {"RELAY", "FW", "VAULT", "HOME", "PROXY"}, "PROXY": {"PROXY", "VAULT", "SAFE", "HOME", "RELAY"}}


def notches(pieces: dict) -> dict:
    n = {k: list(v) for k, v in BASE_NOTCH.items()}
    dn = pieces.get("DECOY")
    if dn and dn != "HOME":
        n["HOME"] = []
        n.setdefault(dn, []).append(("COLLECTOR", 15))
    return n


def outcome(pieces: dict, hours: dict) -> dict:
    """pieces: piece -> node; hours: node -> crew-hours. node -> gauge result."""
    nt = notches(pieces)
    fill = {k: (VALUE["FWGUN"] if k == "FW" else 0) + VALUE["HOUR"] * hours.get(k, 0) for k in nt}
    for p, k in pieces.items():
        if p in VALUE and k in fill:
            fill[k] += VALUE[p]
    if "RAILGUN" in pieces:
        cand = [(sum(v for _, v in nt[k]) - fill[k], k) for k in nt if k in NEAR[pieces["RAILGUN"]]]
        short, k = max(cand, key=lambda t: (t[0], -NODE_HP[t[1]], t[1]))
        fill[k] += 8
    out = {}
    for k, atk in nt.items():
        notch = sum(v for _, v in atk)
        if not atk:
            continue
        short = notch - fill[k]
        integ = NODE_HP[k]
        if short <= 0:
            o, loss = "holds", 0
        elif k == "HOME":
            o, loss = ("breached" if short >= integ else "scuffed"), short
        elif short >= 2 * integ:
            o, loss = "taken", integ
        elif short >= integ:
            o, loss = "down", integ
        else:
            o, loss = "scuffed", short
        out[k] = {"notch": notch, "fill": fill[k], "short": short, "outcome": o, "before": integ,
                  "after": max(0, integ - loss), "atk": atk}
    return out


def clean(r) -> bool:
    return all(v["outcome"] in ("holds", "scuffed") for v in r.values()) and r.get("HOME", {"short": 0})["short"] <= 0


def price(r) -> int:
    c = 0
    for k, v in r.items():
        if v["outcome"] == "scuffed" or k == "HOME":
            c += v["before"] - v["after"]
        elif v["outcome"] == "down":
            c += INSTALL[k] // 2
    return c


def search():
    nodes = list(NODE_HP)
    best = []
    for pick in itertools.combinations(POOL, 3):
        for place in itertools.product(nodes, repeat=3):
            pc = dict(zip(pick, place))
            for split in itertools.product(range(7), repeat=2):
                if sum(split) > 6:
                    continue
                hours = {}
                for k, h in zip(("PROXY", "VAULT"), split):
                    if h:
                        hours[k] = h
                hours["HOME"] = 6 - sum(split)
                r = outcome(pc, hours)
                best.append((not clean(r), price(r), pc, hours))
    best.sort(key=lambda t: (t[0], t[1], sorted(t[2].items()), sorted(t[3].items())))
    return best


PLAN1 = ({"ICE": "HOME", "SENTRY": "HOME", "RAILGUN": "HOME"}, {"PROXY": 4, "HOME": 2})
PLAN2 = ({"ICE": "RELAY", "DECOY": "PROXY", "RAILGUN": "FW"}, {"PROXY": 3, "VAULT": 3})
VISIT1 = ({}, {"PROXY": 3})
R0 = outcome({}, {})
RV1 = outcome(*VISIT1)
RP1, RP2 = outcome(*PLAN1), outcome(*PLAN2)


def gauge(d, key: str, r: dict, add: int = 0, drained: bool = False) -> None:
    x, y = XF.p(key)
    gx, gy = x + 40, y + 34
    sc = E.SCALE
    hmax = 32 * sc
    d.rectangle((gx, gy - hmax, gx + 18, gy), fill=BG2, outline=PANEL_EDGE, width=2)
    f = min(r["fill"], 32)
    if f > 0 and not drained:
        d.rectangle((gx + 2, gy - f * sc, gx + 16, gy - 2), fill=CELL)
    if add:
        d.rectangle((gx + 2, gy - min(f + add, 32) * sc, gx + 16, gy - f * sc), fill=(255, 240, 160))
    ny = gy - min(r["notch"], 32) * sc
    d.line([(gx - 4, ny), (gx + 22, ny)], fill=THREAT, width=4)
    for i, (tid, v) in enumerate(r["atk"]):
        threat(d, (gx + 34 + i * 22, ny), tid, 8, show_hp=False)
    text(d, (gx + 26 + 22 * len(r["atk"]), ny - 10), str(r["notch"]), 15, THREAT_LIGHT, "mono")
    if r["short"] > 0 and (drained or add == 0) and gy - f * sc > ny:
        d.rectangle((gx + 2, ny, gx + 16, gy - f * sc), outline=DMG, width=2)


def countdown_big(d, n: int, of: int = 2) -> None:
    """The netrun dial without the round-2 letter: n netrun hexes left, drawn as hexes."""
    x, y = 640, 92
    d.ellipse((x - 46, y - 46, x + 46, y + 46), fill=(16, 22, 52), outline=THREAT, width=5)
    for i in range(of):
        a0, a1 = -90 + i * 360 / of + 6, -90 + (i + 1) * 360 / of - 6
        d.arc((x - 56, y - 56, x + 56, y + 56), a0, a1, fill=THREAT if i < n else (40, 46, 80), width=9)
    text(d, (x, y - 30), str(n), 48, INK, "mono", anchor="ma")
    for i in range(n):
        d.regular_polygon((x - 70 + i * 20, y + 52, 8), 6, outline=THREAT_LIGHT, width=2)


def xsign(d, c, r=6, col=INK) -> None:
    x, y = c
    d.line([(x - r, y - r), (x + r, y + r)], fill=col, width=3)
    d.line([(x - r, y + r), (x + r, y - r)], fill=col, width=3)


def tags(d, r) -> None:
    for k, v in r.items():
        mark2(d, XF, k, {"outcome": v["outcome"] if v["outcome"] != "breached" else "down", "before": v["before"],
                         "after": v["after"]})


def result_box(d, r, x=990, y=110, label=None, on=True) -> None:
    cl = clean(r)
    hl = r["HOME"]["before"] - r["HOME"]["after"] if "HOME" in r else 0
    panel(d, (x, y, x + 278, y + 96), edge=STAMP_CLEAN if cl else STAMP_HOLD, width=3 if on else 1)
    if label:
        text(d, (x + 12, y + 8), label, 22, CELL if on else DIM, "mono")
    node_icon(d, (x + 60, y + 30), "HOME", 30, CELL)
    text(d, (x + 80, y + 18), f"-{hl}", 22, DMG if hl else HOLD, "mono")
    flag(d, (x + 150, y + 30), 10, THREAT_LIGHT)
    text(d, (x + 166, y + 18), str(sum(1 for v in r.values() if v["outcome"] == "taken")), 22, INK, "mono")
    bolt(d, (x + 204, y + 30), 10)
    text(d, (x + 218, y + 18), str(sum(1 for v in r.values() if v["outcome"] == "down")), 22, INK, "mono")
    sc = sum(1 for k, v in r.items() if v["outcome"] == "scuffed" and k != "HOME")
    d.ellipse((x + 50, y + 58, x + 74, y + 82), fill=(20, 60, 60), outline=HOLD, width=2)
    check(d, (x + 62, y + 70), 6, HOLD)
    d.polygon([(x + 74, y + 58), (x + 74, y + 66), (x + 66, y + 58)], fill=DMG)
    xsign(d, (x + 90, y + 70), 5)
    text(d, (x + 102, y + 58), str(sc), 20, INK, "mono")
    coin(d, (x + 160, y + 70), 9)
    text(d, (x + 174, y + 58), str(price(r)), 20, INK, "mono")
    if cl:
        check(d, (x + 250, y + 70), 10, STAMP_CLEAN)


def pieces_on_map(d, pieces: dict) -> None:
    per: dict[str, list] = {}
    for p, k in pieces.items():
        per.setdefault(k, []).append(p)
    for k, aa in per.items():
        x, y = XF.p(k)
        for i, a in enumerate(aa):
            d.ellipse((x - 58, y + 6 + i * 26, x - 32, y + 32 + i * 26), fill=(50, 46, 30), outline=CELL, width=2)
            asset_icon(d, (x - 45, y + 19 + i * 26), "TURRET" if a in ("SENTRY", "RAILGUN") else a, 8,
                       HOLD if a == "ICE" else CELL)
            if a == "RAILGUN":
                d.line([(x - 55, y + 19 + i * 26), (x - 35, y + 19 + i * 26)], fill=CELL, width=3)


def rail_ring(d, at: str) -> None:
    for k in NEAR[at]:
        if k in ("HOME", "RELAY", "VAULT", "PROXY"):
            x, y = XF.p(k)
            d.ellipse((x - 38, y - 38, x + 38, y + 38), outline=CELL, width=2)


def cards(d, sel=(), used=(), x=250, y=596) -> None:
    import concept_g3_merged as Gm
    for i, a in enumerate(POOL):
        Gm.card(d, x + i * 104, y, a, sel=a in sel, used=a in used)


def f1():
    img, d = new_frame(NAME, "warning")
    E.front(d, 1220)
    E.base(d)
    heat_bar(d, 60, 22, 340, 51)
    why_chain(d, 60, 52)
    countdown_big(d, 2)
    for k in R0:
        gauge(d, k, R0[k])
    for tid, p in (("COLLECTOR", ["C1", "RELAY", "VAULT", "HOME"]), ("AUDITOR", ["C2", "PROXY", "VAULT"]),
                   ("ENFORCER", ["C2", "PROXY"])):
        arrow_path(d, XF, p, (44, 70, 170), 3, dash_line=True)
    tags(d, R0)
    result_box(d, R0)
    header(d, NAME, 1, f"Warning: 2 netruns to the strike; fixed routes (faint) set each gauge's cobalt notch; outcome now: home -{R0['HOME']['short']}, PROXY TAKEN")
    return img


def f2():
    img, d = new_frame(NAME, "draft + planning")
    E.front(d, 1220)
    E.base(d)
    heat_bar(d, 60, 22, 340, 51)
    countdown_big(d, 2)
    for k in RV1:
        gauge(d, k, RV1[k] if k != "PROXY" else R0[k], add=6 if k == "PROXY" else 0)
    px, py = XF.p("PROXY")
    dashed(d, (130, 600), (px + 49, py - 20), CELL, 3)
    label_tag(d, (px + 66, py - 50), "+2 +2 +2", BG, CELL, 15)
    E.pool(d, 0)
    cards(d, sel=("ICE", "SENTRY", "RAILGUN"))
    result_box(d, RV1)
    header(d, NAME, 2, "Draft + planning, HQ visit 1 of 2: ICE, sentry, railgun drafted (3 of 5); 3 crew-hours dragged into PROXY's gauge (+6)")
    return img


def f3():
    img, d = new_frame(NAME, "forecast")
    E.front(d, 1080)
    E.base(d)
    heat_bar(d, 60, 22, 340, 53)
    countdown_big(d, 1)
    for k in RP1:
        gauge(d, k, RP1[k])
    tags(d, RP1)
    pieces_on_map(d, PLAN1[0])
    rail_ring(d, PLAN1[0]["RAILGUN"])
    result_box(d, RP1, label="1")
    result_box(d, RP2, y=216, label="2", on=False)
    E.pool(d, 0)
    cards(d, sel=("ICE", "SENTRY", "RAILGUN"), used=("ICE", "SENTRY", "RAILGUN"))
    header(d, NAME, 3, f"Forecast, HQ visit 2: plan 1 (ICE+sentry on HOME, railgun on HOME backs PROXY 2 hops out) is CLEAN, patch {price(RP1)}; plan 2 (decoy on PROXY) gives PROXY up: TAKEN, patch {price(RP2)}")
    return img


def f4():
    img, d = new_frame(NAME, "resolution")
    r = RP1
    hit = ORDER.index("VAULT")
    fx = int(XF.p("VAULT")[0]) + 40
    E.base(d)
    E.front(d, fx)
    heat_bar(d, 60, 22, 340, 55)
    step_track(d, 470, 70, 340, len(ORDER), hit + 1, "BEAT")
    for k in ORDER[:hit]:
        gauge(d, k, r[k], drained=True)
        mark2(d, XF, k, {"outcome": r[k]["outcome"], "before": r[k]["before"], "after": r[k]["after"]})
    for k in ORDER[hit + 1:]:
        gauge(d, k, r[k])
    gauge(d, "VAULT", r["VAULT"])
    pieces_on_map(d, PLAN1[0])
    vx, vy = XF.p("VAULT")
    threat(d, (vx + 40, vy - 70), "AUDITOR", 20)
    arrow(d, (vx + 40, vy - 50), (vx + 49, vy - 10), THREAT, 5, 12, shorten=0)
    if r["VAULT"]["short"] > 0:
        dmg_badge(d, (vx - 48, vy - 40), r["VAULT"]["short"])
    text(d, (640, 96), "AUTO", 13, DIM, anchor="ma")
    speed_controls(d, 1060, 660)
    header(d, NAME, 4, f"Resolution: the front crosses node by node (beat {hit + 1} of {len(ORDER)}): VAULT's attackers slam its gauge; shortfall {r['VAULT']['short']} lands (SCUFFED); zero input")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    r = RP1
    E.base(d, r, end=True)
    E.front(d, 1220)
    heat_bar(d, 60, 22, 340, 56, raid_at=75)
    tags(d, r)

    class _R:
        home_before = 50
        home_after = r["HOME"]["after"]
        clean = clean(r)
        breached = False
        nodes = {k: {"outcome": v["outcome"]} for k, v in r.items()}
    stamp_losses(img, d, (980, 200), _R)
    panel(d, (20, 560, 700, 700))
    i = 0
    for k, v in r.items():
        if v["outcome"] != "scuffed" or k == "HOME":
            continue
        x = 40 + i * 220
        loss = v["before"] - v["after"]
        node_icon(d, (x + 20, 610), k, 34, CELL)
        text(d, (x + 44, 598), f"-{loss}", 20, DMG, "mono")
        arrow(d, (x + 84, 610), (x + 114, 610), INK, 3, 8, shorten=0)
        coin(d, (x + 134, 610), 10)
        text(d, (x + 150, 598), str(loss), 20, INK, "mono")
        i += 1
    flame(d, (60, 670), 10, HEAT)
    text(d, (80, 658), "75", 20, HEAT, "mono")
    button(d, (1090, 640, 1265, 690), "BACK TO HQ")
    header(d, NAME, 5, f"Aftermath: CLEAN stamp with its payout (+5 Heat, +12); scuffed nodes and their patch price ({price(r)}); next strike at Heat 75")
    return img


FRAMES = [f1, f2, f3, f4, f5]

if __name__ == "__main__":
    for nm, r in (("R0", R0), ("V1", RV1), ("P1", RP1), ("P2", RP2)):
        print(nm, clean(r), price(r), {k: (v["notch"], v["fill"], v["outcome"], v["after"]) for k, v in r.items()})
    b = search()
    n_clean = sum(1 for t in b if not t[0])
    print("clean", n_clean, "of", len(b))
    for t in b[:8]:
        print(t)
