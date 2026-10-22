"""Concept F, round 2: PLAN LEDGER, built from sim.py's step trace (today's resolver rules, no ICE-on-a-cell rule).
R2 changes: icon-only cells (where, what it hits, HP bar, skull on death, house when spent at home, teal hatch when
held); totals row with loss icons; defenses drop on the map, not the sheet; the playout is the big map with the
ledger as a strip and a cursor; the receipt lives on the map (TAKEN = new entry arrows)."""

from __future__ import annotations

from r2_kit import *  # noqa: F403
from r2_kit import RUNS as RR

NAME = "F PLAN LEDGER r2"
GX, GY, CW, CH = 120, 92, 82, 64
TIDS = ["COLLECTOR", "AUDITOR", "ENFORCER"]


def cells(r) -> dict:
    """tid -> list per step of None or {site, hp, dmg, held, killed, spent}."""
    out = {t: [] for t in TIDS}
    gone = {t: False for t in TIDS}
    for ev in r.steps:
        for t in TIDS:
            if gone[t]:
                out[t].append(None)
                continue
            site, hp, alive, hold = ev["threats"][t]
            dmg = sum(h[2] for h in ev["hits"] if h[0] == t)
            held = any(h[0] == t for h in ev["holds"])
            killed = any(k[0] == t for k in ev["kills"])
            spent = (not alive) and not killed
            out[t].append({"site": site, "hp": hp, "dmg": dmg, "held": held, "killed": killed, "spent": spent})
            if not alive:
                gone[t] = True
    return out


def skull(d, c, r, col) -> None:
    x, y = c
    d.ellipse((x - r, y - r, x + r, y + r * 0.6), fill=col)
    d.rectangle((x - r * 0.55, y + r * 0.3, x + r * 0.55, y + r), fill=col)
    d.ellipse((x - r * 0.6, y - r * 0.3, x - r * 0.1, y + r * 0.2), fill=BG)
    d.ellipse((x + r * 0.1, y - r * 0.3, x + r * 0.6, y + r * 0.2), fill=BG)


def ledger(d, r, cursor: int | None = None, gx=GX, gy=GY, cw=CW, ch=CH) -> None:
    c = cells(r)
    n = len(r.steps)
    for s in range(n):
        x = gx + s * cw
        text(d, (x + cw / 2, gy - 22), str(s + 1), 16, CELL if cursor == s + 1 else DIM, "mono", anchor="ma")
    for i, t in enumerate(TIDS):
        y = gy + i * ch
        threat(d, (gx - 50, y + ch / 2 - 6), t, 16)
        for s in range(n):
            x = gx + s * cw
            box = (x + 2, y + 2, x + cw - 2, y + ch - 2)
            cell = c[t][s]
            on = cursor == s + 1
            if cell is None:
                d.rectangle(box, fill=(16, 18, 32), outline=CELL if on else None, width=2)
                continue
            fill = (42, 22, 26) if cell["dmg"] else PANEL
            d.rectangle(box, fill=fill, outline=CELL if on else PANEL_EDGE, width=3 if on else 1)
            if cell["held"]:
                for sx in range(0, cw, 11):
                    d.line([(x + sx, y + ch - 4), (x + sx + 16, y + 4)], fill=(40, 100, 110), width=2)
            node_icon(d, (x + 22, y + 22), cell["site"], 26, CELL if not cell["site"].startswith("C") else THREAT_LIGHT) \
                if not cell["site"].startswith("C") else shield(d, (x + 22, y + 22), 9, CORP)
            if cell["killed"]:
                skull(d, (x + cw - 22, y + 22), 11, DMG)
            elif cell["dmg"]:
                text(d, (x + cw - 8, y + 10), f"-{cell['dmg']}", 18, DMG, "mono", anchor="ra")
            elif cell["held"]:
                asset_icon(d, (x + cw - 22, y + 22), "ICE", 9, HOLD)
            mhp = THREATS[t][1]
            d.rectangle((x + 8, y + ch - 16, x + cw - 8, y + ch - 8), outline=(60, 70, 110))
            if cell["hp"] > 0:
                d.rectangle((x + 8, y + ch - 16, x + 8 + (cw - 16) * cell["hp"] / mhp, y + ch - 8), fill=THREAT_LIGHT)


def totals(d, r, x0=GX, y0=300, w=140) -> None:
    for i, k in enumerate(["HOME", "FW", "VAULT", "SAFE", "RELAY", "PROXY"]):
        v = r.nodes[k]
        x = x0 + i * w
        o = v["outcome"]
        col = {"holds": HOLD, "scuffed": HOLD, "down": INK, "taken": THREAT_LIGHT, "breached": STAMP_BREACH}[o]
        d.rectangle((x + 3, y0, x + w - 3, y0 + 62), fill=BG2, outline=col, width=2)
        node_icon(d, (x + 24, y0 + 31), k, 30, CELL if o not in ("down", "taken") else (DOWN_GREY if o == "down" else THREAT_LIGHT))
        text(d, (x + 46, y0 + 8), f"{v['before']}>{v['after']}", 17, INK, "mono")
        ix, iy = x + 62, y0 + 44
        if o in ("holds", "scuffed"):
            check(d, (ix, iy), 7, HOLD)
        elif o == "down":
            bolt(d, (ix, iy), 10)
        elif o == "taken":
            flag(d, (ix, iy), 8, THREAT_LIGHT)
        if o == "taken":
            pencil_x(d, (x + 24, y0 + 31), 16, seed=i)


MINI = MapXf(30, 400, 0.52)


def mini_map(d, r=None, plan=None, xf=MINI, big=False) -> None:
    for a, b in LINKS:
        d.line([xf.p(a), xf.p(b)], fill=CELL_DIM, width=3)
    rad = 26 if big else 16
    for k in NODES:
        x, y = xf.p(k)
        if k.startswith("C"):
            shield(d, (x, y), rad * 0.5, CORP)
            continue
        o = r.nodes[k]["outcome"] if r else "holds"
        col = DOWN_GREY if o == "down" else (THREAT_LIGHT if o == "taken" else CELL)
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(34, 36, 58), outline=col, width=3)
        node_icon(d, (x, y), k, rad * 1.4, col)
        if o == "down":
            bolt(d, (x, y), rad * 0.7)
        if o == "taken":
            pencil_x(d, (x, y), rad * 0.8, seed=7)
    if plan:
        for n, aa in plan.assets.items():
            x, y = xf.p(n)
            for i, a in enumerate(aa):
                ax, ay = x - rad - 12, y + i * 22 - 6
                d.ellipse((ax - 10, ay - 10, ax + 10, ay + 10), fill=(50, 46, 30), outline=CELL, width=2)
                asset_icon(d, (ax, ay), a, 6, HOLD if a == "ICE" else CELL)


def hud(d, n=2) -> None:
    heat_bar(d, 470, 18, 340, 51)
    countdown(d, (1210, 60), n)


def guaranteed(d, r, x=990, y=400, alt=None) -> None:
    lo = losses(r)
    panel(d, (x, y, x + 278, y + 200), edge=STAMP_HOLD)
    text(d, (x + 14, y + 10), "CELL HOLDS" if not r.breached else "BREACHED", 28, STAMP_HOLD, "stamp")
    node_icon(d, (x + 30, y + 74), "HOME", 30, CELL)
    hl = r.home_before - r.home_after
    text(d, (x + 50, y + 62), f"-{hl}", 22, DMG if hl else HOLD, "mono")
    bolt(d, (x + 130, y + 74), 10)
    text(d, (x + 146, y + 62), str(len(lo["down"])), 22, INK, "mono")
    flag(d, (x + 194, y + 74), 10, THREAT_LIGHT)
    text(d, (x + 210, y + 62), str(len(lo["taken"])), 22, INK, "mono")
    if alt is not None:
        la = losses(alt)
        d.line([(x + 14, y + 104), (x + 264, y + 104)], fill=PANEL_EDGE)
        text(d, (x + 14, y + 112), "1", 18, DIM, "mono")
        node_icon(d, (x + 50, y + 124), "HOME", 24, DIM)
        text(d, (x + 64, y + 112), f"-{alt.home_before - alt.home_after}", 18, DMG, "mono")
        bolt(d, (x + 130, y + 124), 8)
        text(d, (x + 144, y + 112), str(len(la["down"])), 18, DIM, "mono")
        flag(d, (x + 194, y + 124), 8, DIM)
        text(d, (x + 208, y + 112), str(len(la["taken"])), 18, DIM, "mono")
    button(d, (x + 14, y + 150, x + 264, y + 190), "SIGN ORDERS", True, 18)


def f1():
    img, d = new_frame(NAME, "warning")
    hud(d)
    why_chain(d, 470, 46)
    r = RR["BARE"]
    panel(d, (260, 100, 1000, 380), fill=(232, 226, 205), edge=(120, 110, 90))
    for i, t in enumerate(TIDS):
        y = 130 + i * 82
        threat_chip(d, (330, y + 24), t, scale=0.8)
        path = r.paths[t]
        for j, k in enumerate(path):
            x = 420 + j * 110
            if k.startswith("C"):
                shield(d, (x, y + 22), 13, CORP)
            else:
                node_icon(d, (x, y + 22), k, 40, (40, 40, 50))
            if j < len(path) - 1:
                arrow(d, (x + 20, y + 22), (x + 90, y + 22), THREAT, 4, 10, shorten=0)
    stamp(img, (900, 90), "DECRYPTED", (40, 140, 90), 26, -8)
    mini_map(d)
    for t, p in r.paths.items():
        arrow_path(d, MINI, p, (44, 70, 170), 3, dash_line=True)
    header(d, NAME, 1, "Warning: the intercepted strike order as icon rows (who, two numbers, route glyph, full path); countdown and Heat cause; routes on the map")
    return img


def f2():
    img, d = new_frame(NAME, "planning")
    hud(d)
    r = RR["BARE"]
    ledger(d, r)
    totals(d, r)
    mini_map(d, r)
    for i, a in enumerate(("TURRET", "ICE", "DECOY", "CREW")):
        asset_card2(d, 470 + i * 104, 420, a, selected=a == "DECOY")
    fx, fy = MINI.p("FW")
    dashed(d, (730, 470), (fx + 20, fy), CELL, 3)
    w = RR["DECOY_ONLY"]
    tag_x, tag_y = 470, 560
    d.rounded_rectangle((tag_x, tag_y, tag_x + 400, tag_y + 60), radius=6, fill=CELL)
    node_icon(d, (tag_x + 24, tag_y + 30), "HOME", 28, BG)
    text(d, (tag_x + 44, tag_y + 16), f"-{r.home_before - r.home_after} > -{w.home_before - w.home_after}", 22, BG, "mono")
    bolt(d, (tag_x + 200, tag_y + 30), 10, BG)
    flag(d, (tag_x + 220, tag_y + 30), 9, BG)
    lb, lw = losses(r), losses(w)
    text(d, (tag_x + 236, tag_y + 16), f"{len(lb['down']) + len(lb['taken'])} > {len(lw['down']) + len(lw['taken'])}", 22, BG, "mono")
    text(d, (tag_x + 330, tag_y + 16), "FW", 18, BG)
    header(d, NAME, 2, "Planning: the ledger is the raid as it stands (home -20, 3 DOWN, 1 TAKEN); dragging DECOY onto FIREWALL on the map previews home -20 > -12, lost 4 > 0")
    return img


def f3():
    img, d = new_frame(NAME, "forecast")
    hud(d)
    r = RR["SHIELD"]
    ledger(d, r)
    totals(d, r)
    mini_map(d, r, PLANS["SHIELD"])
    for i, a in enumerate(("TURRET", "ICE", "DECOY", "CREW")):
        asset_card2(d, 470 + i * 104, 420, a, used=a != "CREW")
    guaranteed(d, r, alt=RR["LURE"])
    header(d, NAME, 3, "Forecast: plan 2 (shield home) rewrites every cell: held cells hatched, skulls where threats die; totals: home 0, 2 DOWN, 2 TAKEN; plan 1 kept below")
    return img


def f4():
    img, d = new_frame(NAME, "resolution")
    heat_bar(d, 470, 18, 340, 51)
    r = RR["SHIELD"]
    s = 5
    ledger(d, r, cursor=s, gx=120, gy=70, cw=60, ch=40)
    big = MapXf(180, 230, 0.95)
    ev = r.steps[s - 1]
    for a, b in LINKS:
        d.line([big.p(a), big.p(b)], fill=CELL_DIM, width=4)
    for k in NODES:
        x, y = big.p(k)
        if k.startswith("C"):
            shield(d, (x, y), 16, CORP)
            continue
        c = ev["cond"][k]
        col = DOWN_GREY if c == "down" else (THREAT_LIGHT if c == "taken" else CELL)
        d.ellipse((x - 30, y - 30, x + 30, y + 30), fill=(34, 36, 58), outline=col, width=4)
        node_icon(d, (x, y), k, 30, col)
        if c == "down":
            bolt(d, (x, y), 22)
        hp_pips(d, x, y + 36, ev["hp"][k], NODE_HP[k], w=6 if NODE_HP[k] > 30 else 8)
    for t, (site, hp, alive, hold) in ev["threats"].items():
        if not alive:
            continue
        x, y = big.p(site)
        threat(d, (x + 44, y - 10), t, 16, hp=hp)
        if hold:
            asset_icon(d, (x + 70, y - 30), "ICE", 8, HOLD)
    for site, gun, t, dmg, left in ev["shots"]:
        sx, sy = big.p(site)
        tx, ty = big.p(ev["threats"][t][0])
        d.line([(sx, sy), (tx + 44, ty - 10)], fill=CELL, width=4)
    for t, site, dmg, left in ev["hits"]:
        x, y = big.p(site)
        dmg_badge(d, (x - 46, y - 40), dmg)
    speed_controls(d, 1060, 660)
    header(d, NAME, 4, "Resolution: the big map replays the signed ledger (cursor at step 5 of 10): the Auditor held and shot at home, the Enforcer hits the Relay; no input")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    heat_bar(d, 470, 18, 340, 51, raid_at=None)
    r = RR["SHIELD"]
    big = MapXf(120, 110, 0.95)
    mini_map(d, r, xf=big, big=True)
    lo = losses(r)
    for k in lo["taken"]:
        arrow(d, big.p(k), big.p("HOME"), THREAT, 4, 12, dash_line=True)
    stamp_losses(img, d, (1000, 160), r)
    panel(d, (860, 330, 1268, 650))
    for i, k in enumerate(lo["taken"] + lo["down"]):
        y = 350 + i * 70
        taken = k in lo["taken"]
        node_icon(d, (900, y + 24), k, 34, THREAT_LIGHT if taken else DOWN_GREY)
        if taken:
            flag(d, (926, y + 12), 7, THREAT_LIGHT)
        else:
            bolt(d, (926, y + 14), 8)
        arrow(d, (944, y + 24), (990, y + 24), INK, 3, 9, shorten=0)
        if taken:
            d.regular_polygon((1014, y + 24, 14), 6, outline=CELL, width=3)
            arrow(d, (1034, y + 24), (1070, y + 24), THREAT, 3, 8, shorten=0)
            node_icon(d, (1096, y + 24), "HOME", 26, CELL)
            text(d, (1114, y + 12), "1", 20, THREAT_LIGHT, "mono")
        else:
            coin(d, (1014, y + 24), 11)
            text(d, (1032, y + 12), str(INSTALL[k] // 2), 20, INK, "mono")
    button(d, (1090, 660, 1265, 705), "BACK TO HQ")
    header(d, NAME, 5, "Aftermath: the receipt is on the map: TAKEN nodes keep the X and now point at home (1 hop); each loss and its fix (netrun hex or coins)")
    return img


FRAMES = [f1, f2, f3, f4, f5]
