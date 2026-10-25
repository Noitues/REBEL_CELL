"""Concept C, round 2: STRENGTH DUEL with geography. R2 changes:
- Threats declare a target and a path; every node they pass gets a small "passing" banner (one strike), so the map matters.
- Pieces have reach: a turret adds +8 to its node, or +4 to each adjacent banner if placed on a link (split mode);
  crew adds +3 to its node and each neighbour; ICE cancels one strike at its node; DECOY re-targets one attacker.
- One consistent rule, computed below: ATK = strikes x damage; DEF = integrity + bonus; loss = max(0, ATK - bonus).
  HOLDS if loss < integrity (SCUFFED if loss > 0), DOWN if loss >= integrity, TAKEN if loss >= 2 x integrity.
- Itemised lines on every banner, icons for the verdict, countdown + routes on the warning, loss icons in the stamp.
"""

from __future__ import annotations

from r2_kit import *  # noqa: F403

NAME = "C STRENGTH DUEL r2"
XF = MapXf(270, 130, 0.8)
STRIKES_AT_TARGET = 3
DECL = {"COLLECTOR": ["C1", "RELAY", "FW", "HOME"], "AUDITOR": ["C2", "PROXY", "VAULT"], "ENFORCER": ["C2", "PROXY"]}
BUILT = {"FW": 3}


def duel(plan: dict) -> dict:
    """plan: {"turret": node, "ice": node, "decoy": node, "crew": node}. Returns node -> banner data."""
    decl = {k: list(v) for k, v in DECL.items()}
    if plan.get("decoy"):
        # The decoy re-targets the attacker whose target is nearest (Enforcer on PROXY in this scenario): it walks on.
        dn = plan["decoy"]
        decl["COLLECTOR"] = ["C1", "RELAY", dn] if dn in ("FW", "VAULT") else decl["COLLECTOR"]
    atk: dict[str, list] = {}
    for tid, path in decl.items():
        dmg = THREATS[tid][2]
        for i, n in enumerate(path[1:], 1):
            strikes = STRIKES_AT_TARGET if i == len(path) - 1 else 1
            atk.setdefault(n, []).append((tid, strikes, dmg))
    out = {}
    for n, lines in atk.items():
        bonus = []
        if n in BUILT:
            bonus.append(("FWGUN", BUILT[n]))
        if plan.get("turret") == n:
            bonus.append(("TURRET", 8))
        if plan.get("crew") and (plan["crew"] == n or n in ADJ_N[plan["crew"]]):
            bonus.append(("CREW", 3))
        a = sum(s * d for _, s, d in lines)
        if plan.get("ice") == n:
            biggest = max(lines, key=lambda l: l[2])
            a -= biggest[2]
            bonus.append(("ICE", -biggest[2]))
        b = sum(v for k, v in bonus if k != "ICE")
        integ = NODE_HP[n]
        loss = max(0, a - b)
        if n == "HOME":
            out_s = "breached" if loss >= integ else ("scuffed" if loss else "holds")
        else:
            out_s = "taken" if loss >= 2 * integ else ("down" if loss >= integ else ("scuffed" if loss else "holds"))
        out[n] = {"lines": lines, "bonus": bonus, "atk": a, "def": integ + b, "loss": loss, "outcome": out_s,
                  "margin": integ + b - a, "before": integ, "after": max(0, integ - loss)}
    return out


ADJ_N: dict[str, set] = {}
for a_, b_ in LINKS:
    ADJ_N.setdefault(a_, set()).add(b_)
    ADJ_N.setdefault(b_, set()).add(a_)

BARE = duel({})
WITH_TURRET = duel({"turret": "PROXY"})
PLAN = duel({"turret": "PROXY", "ice": "PROXY", "crew": "SAFE", "decoy": "FW"})


def banner(d, key: str, b: dict, sel: bool = False, compact: bool = True) -> None:
    x, y = XF.p(key)
    target = any(s > 1 for _, s, _ in b["lines"])
    w, h = (150, 74) if target else (104, 46)
    bx, by = x - w / 2, y - h - 40
    oc = {"holds": HOLD, "scuffed": HOLD, "down": INK, "taken": THREAT_LIGHT, "breached": STAMP_BREACH}[b["outcome"]]
    panel(d, (bx, by, bx + w, by + h), fill=(20, 22, 44), edge=CELL if sel else oc, width=3 if sel else 2)
    # attacker line(s): silhouettes x strikes
    for i, (tid, s, dmg) in enumerate(b["lines"][:2]):
        threat(d, (bx + 14 + i * 30, by + 16), tid, 8, show_hp=False)
        if s > 1:
            text(d, (bx + 24 + i * 30, by + 6), f"x{s}", 11, INK, "mono")
    text(d, (bx + w - 10, by + 4), str(b["atk"]), 20, THREAT_LIGHT, "mono", anchor="ra")
    if target:
        icons = [k for k, v in b["bonus"]]
        for i, k in enumerate(icons):
            ix = bx + 14 + i * 24
            if k == "FWGUN":
                node_icon(d, (ix, by + 42), "FW", 18, CELL)
            else:
                asset_icon(d, (ix, by + 42), k, 7, HOLD if k == "ICE" else CELL)
        text(d, (bx + w - 10, by + 32), str(b["def"]), 20, CELL, "mono", anchor="ra")
    tot = b["atk"] + b["def"]
    yb = by + h - 12
    d.rectangle((bx + 8, yb, bx + w - 8, yb + 6), fill=CELL)
    d.rectangle((bx + 8, yb, bx + 8 + (w - 16) * b["atk"] / max(1, tot), yb + 6), fill=THREAT)
    d.line([(x, by + h), (x, y - 32)], fill=oc, width=2)
    vx, vy = bx + w + 2, by - 2
    d.ellipse((vx - 12, vy - 12, vx + 12, vy + 12), fill=BG, outline=oc, width=2)
    if b["outcome"] in ("holds", "scuffed"):
        check(d, (vx, vy), 6, HOLD)
    elif b["outcome"] == "down":
        bolt(d, (vx, vy), 9)
    else:
        flag(d, (vx, vy), 7, THREAT_LIGHT)


def base(d, res=None) -> None:
    draw_links(d, XF)
    for k in NODES:
        if res and k in res:
            st = {"down": "down", "taken": "taken"}.get(res[k]["outcome"], "ok")
            node(d, XF, k, st, res[k]["before"], res[k]["loss"] if st == "ok" else 0)
        else:
            node(d, XF, k)


def tags(d, res) -> None:
    for k, b in res.items():
        mark2(d, XF, k, {"outcome": b["outcome"] if b["outcome"] != "breached" else "down", "before": b["before"], "after": b["after"]})


def hud(d, n=2) -> None:
    heat_bar(d, 470, 22, 340, 51)
    countdown(d, (70, 70), n)


def tray(d, used=(), sel=None) -> None:
    for i, a in enumerate(("TURRET", "ICE", "DECOY", "CREW")):
        asset_card2(d, 20, 150 + i * 118, a, selected=a == sel, used=a in used)


def f1():
    img, d = new_frame(NAME, "warning")
    base(d)
    hud(d)
    why_chain(d, 560, 52)
    for tid, p in DECL.items():
        arrow_path(d, XF, p, (44, 70, 170), 4, dash_line=True)
    for k, b in BARE.items():
        banner(d, k, b)
    header(d, NAME, 1, "Warning: declared paths; a big banner on each target (attack vs defense) and small ones on nodes passed; countdown; Heat cause")
    return img


def f2():
    img, d = new_frame(NAME, "planning")
    base(d, BARE)
    hud(d)
    for k, b in WITH_TURRET.items():
        banner(d, k, b, sel=k == "PROXY")
    tray(d, used=("TURRET",), sel="ICE")
    # Duel card for PROXY: every line, before vs with the ICE being dragged.
    b = WITH_TURRET["PROXY"]
    w = duel({"turret": "PROXY", "ice": "PROXY"})["PROXY"]
    panel(d, (990, 110, 1268, 470), edge=CELL)
    node_icon(d, (1020, 140), "PROXY", 34, CELL)
    y = 180
    for tid, s, dmg in b["lines"]:
        threat(d, (1016, y + 10), tid, 10, show_hp=False)
        text(d, (1036, y), f"{s} x {dmg}", 18, THREAT_LIGHT, "mono")
        text(d, (1254, y), f"{s * dmg}", 18, THREAT_LIGHT, "mono", anchor="ra")
        y += 32
    d.line([(1004, y), (1254, y)], fill=PANEL_EDGE)
    y += 8
    node_icon(d, (1016, y + 10), "PROXY", 22, CELL)
    text(d, (1254, y), "15", 18, CELL, "mono", anchor="ra")
    y += 30
    asset_icon(d, (1016, y + 10), "TURRET", 8)
    text(d, (1254, y), "+8", 18, CELL, "mono", anchor="ra")
    y += 30
    asset_icon(d, (1016, y + 10), "ICE", 8, HOLD)
    text(d, (1040, y), "drag", 14, DIM)
    text(d, (1254, y), f"-{THREATS['ENFORCER'][2]}", 18, HOLD, "mono", anchor="ra")
    y += 40
    text(d, (1004, y), f"{b['atk']} : {b['def']}", 22, INK, "mono")
    if b["outcome"] == "down":
        bolt(d, (1120, y + 12), 10)
    else:
        flag(d, (1120, y + 12), 9, THREAT_LIGHT)
    arrow(d, (1136, y + 12), (1170, y + 12), INK, 3, 8, shorten=0)
    if w["outcome"] == "down":
        bolt(d, (1186, y + 12), 10)
    else:
        check(d, (1186, y + 12), 7, HOLD)
    text(d, (1004, y + 34), f"{w['atk']} : {w['def']}", 22, CELL, "mono")
    header(d, NAME, 2, f"Planning: turret on PROXY moves it TAKEN > DOWN ({b['atk']}:{b['def']}); dragging ICE cancels one Enforcer strike: {w['atk']}:{w['def']} = {'HOLDS' if w['outcome'] in ('holds', 'scuffed') else w['outcome'].upper()}")
    return img


def f3():
    img, d = new_frame(NAME, "forecast")
    base(d, PLAN)
    hud(d)
    for tid, p in DECL.items():
        pass
    arrow_path(d, XF, ["C1", "RELAY", "FW"], THREAT, 4)
    arrow_path(d, XF, ["C2", "PROXY", "VAULT"], THREAT, 4)
    for k, b in PLAN.items():
        banner(d, k, b)
    for n, a in (("PROXY", "TURRET"), ("PROXY", "ICE"), ("SAFE", "CREW"), ("FW", "DECOY")):
        x, y = XF.p(n)
        off = 26 if a == "ICE" else 0
        d.ellipse((x - 58, y + 6 + off, x - 32, y + 32 + off), fill=(50, 46, 30), outline=CELL, width=2)
        asset_icon(d, (x - 45, y + 19 + off), a, 8, HOLD if a == "ICE" else CELL)
    tray(d, used=("TURRET", "ICE", "DECOY", "CREW"))
    clean = all(b["outcome"] in ("holds", "scuffed") for b in PLAN.values()) and PLAN.get("HOME", {"loss": 0})["loss"] == 0
    tight = min((b["margin"], k) for k, b in PLAN.items())
    panel(d, (990, 110, 1268, 330), edge=STAMP_CLEAN if clean else STAMP_HOLD)
    text(d, (1004, 120), "CLEAN DEFENSE" if clean else "CELL HOLDS", 28, STAMP_CLEAN if clean else STAMP_HOLD, "stamp")
    flame(d, (1014, 182), 9, HEAT)
    text(d, (1030, 170), "+5", 20, INK, "mono")
    coin(d, (1090, 180), 9)
    text(d, (1106, 170), "+12", 20, INK, "mono")
    node_icon(d, (1016, 236), tight[1], 28, CELL)
    text(d, (1040, 222), "MARGIN", 14, DIM)
    text(d, (1040, 240), str(tight[0]), 26, STAMP_HOLD, "mono")
    button(d, (1090, 640, 1265, 690), "START")
    header(d, NAME, 3, f"Forecast: decoy pulls the Collector onto FIREWALL; turret + ICE + crew hold PROXY; every banner holds: clean (+5, +12); tightest margin {tight[0]} on {tight[1]}")
    return img


def f4():
    img, d = new_frame(NAME, "resolution")
    base(d)
    heat_bar(d, 470, 22, 340, 51)
    order = sorted(PLAN, key=lambda k: (k == "HOME", -PLAN[k]["atk"]))
    step_track(d, 470, 70, 340, len(order), 2, "DUEL")
    for k in order[2:]:
        banner(d, k, PLAN[k])
    for k in order[:1]:
        mark2(d, XF, k, {"outcome": PLAN[k]["outcome"], "before": PLAN[k]["before"], "after": PLAN[k]["after"]})
    k = order[1]
    b = PLAN[k]
    x, y = XF.p(k)
    y = max(y, 330)
    x = min(max(x, 220), 800)
    panel(d, (x - 190, y - 220, x + 190, y - 60), fill=(16, 18, 36), edge=CELL, width=3)
    tid = max(b["lines"], key=lambda l: l[1] * l[2])[0]
    threat(d, (x - 140, y - 150), tid, 28)
    node_icon(d, (x + 140, y - 150), k, 64, CELL)
    d.rectangle((x - 100, y - 110, x + 100, y - 94), fill=CELL)
    d.rectangle((x - 100, y - 110, x - 100 + 200 * (b["atk"] * 2 / 3) / (b["atk"] + b["def"]), y - 94), fill=THREAT)
    text(d, (x - 100, y - 88), f"{b['atk'] * 2 // 3}/{b['atk']}", 16, THREAT_LIGHT, "mono")
    text(d, (x + 100, y - 88), str(b["def"]), 16, CELL, "mono", anchor="ra")
    speed_controls(d, 1060, 660)
    header(d, NAME, 4, "Resolution: duels play one by one on their node, biggest first, home last; strike 2 of 3 fills against defense; no input")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    base(d, PLAN)
    heat_bar(d, 470, 22, 340, 56, raid_at=None)
    tags(d, PLAN)

    class _R:  # a stamp-compatible view of the duel result
        home_before = 50
        home_after = 50
        clean = True
        breached = False
        nodes = {k: {"outcome": v["outcome"]} for k, v in PLAN.items()}
    stamp_losses(img, d, (1000, 200), _R)
    panel(d, (20, 560, 640, 700))
    asset_icon(d, (60, 600), "DECOY", 14)
    text(d, (86, 588), "12 > 0", 20, INK, "mono")
    asset_icon(d, (250, 600), "ICE", 14, DIM)
    text(d, (276, 588), "0", 20, DIM, "mono")
    flame(d, (60, 660), 10, HEAT)
    text(d, (80, 648), "51 > 56   NEXT 75", 20, HEAT, "mono")
    button(d, (1090, 640, 1265, 690), "BACK TO HQ")
    header(d, NAME, 5, "Aftermath: clean stamp with its payout as icons; scuffed nodes keep their -N; the spent decoy and ICE listed; Heat 51 > 56")
    return img


FRAMES = [f1, f2, f3, f4, f5]

if __name__ == "__main__":
    for nm, res in (("BARE", BARE), ("TURRET", WITH_TURRET), ("PLAN", PLAN)):
        print(nm, {k: (v["atk"], v["def"], v["loss"], v["outcome"]) for k, v in res.items()})
