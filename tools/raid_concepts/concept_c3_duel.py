"""Concept C, round 3: STRENGTH DUEL under the package (fixed declared paths, 3-of-5 draft, one clean definition,
SCUFFED priced 1 per point). Numbers from c3_rules.duel(); presentation reuses round 2's banners, with the R2 defects
fixed (no hard-coded clean; SCUFFED drawn apart from HOLDS; multipliers as the x-sign glyph)."""

from __future__ import annotations

from r2_kit import *  # noqa: F403

import concept_c2_duel as C
from c3_rules import DECL, POOL, clean, duel, price

NAME = "C STRENGTH DUEL r3"
XF = C.XF
BARE = duel({}, None)
STEP = duel({"RAILGUN": "HOME"}, "VAULT")
PLAN = duel({"ICE": "PROXY", "DECOY": "RELAY", "RAILGUN": "HOME"}, "VAULT")
ALT = duel({"TURRET": "PROXY", "ICE": "PROXY", "RAILGUN": "HOME"}, "SAFE")
PLAN_PIECES = {"PROXY": ["ICE"], "RELAY": ["DECOY"], "HOME": ["RAILGUN"], "VAULT": ["CREW"]}


def banner(d, key, b, sel=False):
    b2 = dict(b)
    b2["bonus"] = [("TURRET" if k in ("SENTRY", "RAILGUN") else k, v) for k, v in b["bonus"]]
    C.banner(d, key, b2, sel)
    if b["outcome"] == "scuffed":
        x, y = XF.p(key)
        target = any(s > 1 for _, s, _ in b["lines"])
        w, h = (150, 74) if target else (104, 46)
        bx, by = x - w / 2, y - h - 40
        d.polygon([(bx + w, by), (bx + w, by + 14), (bx + w - 14, by)], fill=DMG)


def base(d, res=None):
    C.base(d, res)


def routes(d, faint=False):
    for tid, p in DECL.items():
        arrow_path(d, XF, p, (44, 70, 170) if faint else THREAT, 4, dash_line=faint)


def pieces_on_map(d, pp):
    for n, aa in pp.items():
        x, y = XF.p(n)
        for i, a in enumerate(aa):
            d.ellipse((x - 58, y + 6 + i * 26, x - 32, y + 32 + i * 26), fill=(50, 46, 30), outline=CELL, width=2)
            asset_icon(d, (x - 45, y + 19 + i * 26), "TURRET" if a in ("SENTRY", "RAILGUN") else a, 8, HOLD if a == "ICE" else CELL)


def summary_box(d, res, x=990, y=110, label=None, on=True):
    cl = clean(res)
    lost = sum(1 for b in res.values() if b["outcome"] in ("down", "taken"))
    home = res.get("HOME", {"loss": 0})["loss"]
    panel(d, (x, y, x + 278, y + 100), edge=STAMP_CLEAN if cl else STAMP_HOLD, width=3 if on else 1)
    if label:
        text(d, (x + 12, y + 8), label, 22, CELL if on else DIM, "mono")
    node_icon(d, (x + 60, y + 30), "HOME", 28, CELL)
    text(d, (x + 78, y + 18), f"-{home}", 20, DMG if home else HOLD, "mono")
    flag(d, (x + 150, y + 30), 9, THREAT_LIGHT)
    text(d, (x + 166, y + 18), str(lost), 20, INK, "mono")
    coin(d, (x + 210, y + 30), 9)
    text(d, (x + 226, y + 18), str(price(res)), 20, INK, "mono")
    if cl:
        flame(d, (x + 30, y + 74), 9, HEAT)
        text(d, (x + 44, y + 62), "+5", 20, INK, "mono")
        coin(d, (x + 100, y + 72), 9)
        text(d, (x + 114, y + 62), "+12", 20, INK, "mono")
        check(d, (x + 250, y + 72), 9, STAMP_CLEAN)
    tight = min((b["margin"], k) for k, b in res.items())
    node_icon(d, (x + 186, y + 72), tight[1], 22, CELL)
    text(d, (x + 202, y + 62), str(tight[0]), 18, STAMP_HOLD, "mono")


def f1():
    img, d = new_frame(NAME, "warning")
    base(d)
    C.hud(d)
    why_chain(d, 560, 52)
    routes(d, faint=True)
    for k, b in BARE.items():
        banner(d, k, b)
    summary_box(d, BARE)
    header(d, NAME, 1, "Warning: fixed declared paths; a big banner on each target, small ones on nodes passed; outcome now: home -15, PROXY TAKEN")
    return img


def f2():
    img, d = new_frame(NAME, "draft + planning")
    base(d, STEP)
    C.hud(d)
    routes(d)
    for k, b in STEP.items():
        banner(d, k, b, sel=k == "PROXY")
    pieces_on_map(d, {"HOME": ["RAILGUN"], "VAULT": ["CREW"]})
    hx, hy = XF.p("HOME")
    for k in ("FW", "VAULT", "SAFE", "RELAY", "PROXY"):
        x, y = XF.p(k)
        d.ellipse((x - 38, y - 38, x + 38, y + 38), outline=CELL, width=2)
    import concept_g3_merged as Gm
    for i, a in enumerate(POOL):
        Gm.card(d, 20, 120 + i * 116, a, sel=a in ("ICE", "DECOY", "RAILGUN"), used=a == "RAILGUN")
    header(d, NAME, 2, f"Draft + planning: ICE, DECOY, RAILGUN drafted; the railgun on HOME reaches every banner within 2 hops and backs the biggest (PROXY {STEP['PROXY']['atk']} : {STEP['PROXY']['def']}, now DOWN not TAKEN)")
    return img


def f3():
    img, d = new_frame(NAME, "forecast")
    base(d, PLAN)
    C.hud(d)
    arrow_path(d, XF, ["C1", "RELAY"], THREAT, 4)
    arrow_path(d, XF, ["C2", "PROXY", "VAULT"], THREAT, 4)
    for k, b in PLAN.items():
        banner(d, k, b)
    pieces_on_map(d, PLAN_PIECES)
    summary_box(d, PLAN, label="1")
    summary_box(d, ALT, y=222, label="2", on=False)
    button(d, (1090, 640, 1265, 690), "START")
    tight = min((b["margin"], k) for k, b in PLAN.items())
    header(d, NAME, 3, f"Forecast: decoy on RELAY stops the Collector there; ICE + railgun + crew hold PROXY: CLEAN, patch {price(PLAN)}; tightest margin {tight[0]} on {tight[1]}; plan 2 compared")
    return img


def f4():
    img, d = new_frame(NAME, "resolution")
    base(d)
    heat_bar(d, 470, 22, 340, 51)
    order = sorted(PLAN, key=lambda k: (k == "HOME", -PLAN[k]["atk"], k))
    step_track(d, 470, 70, 340, len(order), 1, "DUEL")
    for k in order[1:]:
        banner(d, k, PLAN[k])
    k = order[0]
    b = PLAN[k]
    x, y = XF.p(k)
    y = max(y, 330)
    x = min(max(x, 220), 800)
    panel(d, (x - 190, y - 220, x + 190, y - 60), fill=(16, 18, 36), edge=CELL, width=3)
    tid = max(b["lines"], key=lambda l: l[1] * l[2])[0]
    threat(d, (x - 140, y - 150), tid, 28)
    node_icon(d, (x + 140, y - 150), k, 64, CELL)
    done = b["atk"] * 2 // 3
    d.rectangle((x - 100, y - 110, x + 100, y - 94), fill=CELL)
    d.rectangle((x - 100, y - 110, x - 100 + 200 * done / (b["atk"] + b["def"]), y - 94), fill=THREAT)
    text(d, (x - 100, y - 88), f"{done}/{b['atk']}", 16, THREAT_LIGHT, "mono")
    text(d, (x + 100, y - 88), str(b["def"]), 16, CELL, "mono", anchor="ra")
    speed_controls(d, 1060, 660)
    header(d, NAME, 4, f"Resolution: duels one by one, biggest first ({k}), home last; strike 2 of 3 fills against defense; no input")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    base(d, PLAN)
    heat_bar(d, 470, 22, 340, 56, raid_at=None)
    C.tags(d, PLAN)

    class _R:
        home_before = 50
        home_after = 50 - PLAN.get("HOME", {"loss": 0})["loss"]
        clean = clean(PLAN)
        breached = False
        nodes = {k: {"outcome": v["outcome"]} for k, v in PLAN.items()}
    stamp_losses(img, d, (1000, 200), _R)
    panel(d, (20, 560, 700, 700))
    i = 0
    for k, b in PLAN.items():
        if b["outcome"] != "scuffed":
            continue
        x = 40 + i * 220
        node_icon(d, (x + 20, 610), k, 34, CELL)
        text(d, (x + 44, 598), f"-{b['loss']}", 20, DMG, "mono")
        arrow(d, (x + 84, 610), (x + 114, 610), INK, 3, 8, shorten=0)
        coin(d, (x + 134, 610), 10)
        text(d, (x + 150, 598), str(b["loss"]), 20, INK, "mono")
        i += 1
    button(d, (1090, 640, 1265, 690), "BACK TO HQ")
    header(d, NAME, 5, "Aftermath: CLEAN stamp with its payout; each scuffed node and its patch price (1 per point)")
    return img


FRAMES = [f1, f2, f3, f4, f5]

if __name__ == "__main__":
    for nm, r in (("BARE", BARE), ("STEP", STEP), ("PLAN", PLAN), ("ALT", ALT)):
        print(nm, clean(r), price(r), {k: (v["atk"], v["def"], v["outcome"]) for k, v in r.items()})
