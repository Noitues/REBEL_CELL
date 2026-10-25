"""Round-2 additions to the drawing kit, all fed by sim.py (one consistent run per plan)."""

from __future__ import annotations

import math

import rc_draw as R
from rc_draw import *  # noqa: F403
from sim import INSTALL, NODE_HP as SIM_HP, Plan, run

PLANS = {
    "BARE": Plan({}, "SAFE"),
    "DECOY_ONLY": Plan({"FW": ["DECOY"]}, "SAFE"),
    "LURE": Plan({"HOME": ["TURRET", "ICE"], "FW": ["DECOY"]}, "SAFE"),
    "SHIELD": Plan({"HOME": ["TURRET", "ICE"], "PROXY": ["DECOY"]}, "SAFE"),
}
RUNS = {k: run(p) for k, p in PLANS.items()}
ROUTE_KIND = {"COLLECTOR": "home", "AUDITOR": "value", "ENFORCER": "weakest", "LOCKDOWN": "weakest", "COURIER": "value", "INSPECTOR": "value",
              "BAILIFF": "weakest", "HAULER": "weakest"}


def losses(r) -> dict:
    out = {"down": [], "taken": [], "scuffed": []}
    for k, v in r.nodes.items():
        if k == "HOME":
            continue
        if v["outcome"] in out:
            out[v["outcome"]].append(k)
    return out


def repair_cost(r) -> int:
    lo = losses(r)
    return sum(INSTALL[k] // 2 for k in lo["down"]) + (r.home_before - r.home_after)


# --- glyphs -----------------------------------------------------------------------------------------

def coin(d, c, r, col=CELL) -> None:
    x, y = c
    d.ellipse((x - r, y - r, x + r, y + r), outline=col, width=3)
    d.line([(x, y - r * 0.55), (x, y + r * 0.55)], fill=col, width=3)


def cracked_shield(d, c, r, col=INK) -> None:
    x, y = c
    d.polygon([(x - r, y - r), (x + r, y - r), (x + r, y), (x, y + r * 1.3), (x - r, y)], outline=col, width=3)
    d.line([(x - r * 0.2, y - r), (x + r * 0.2, y - r * 0.2), (x - r * 0.2, y + r * 0.4), (x + r * 0.1, y + r)], fill=col, width=3)


def route_glyph(d, c, tid: str, r: float = 8, col=INK) -> None:
    """Why it goes there, without words: house = shortest to home, coin = richest node, cracked shield = weakest node."""
    k = ROUTE_KIND[tid]
    x, y = c
    d.ellipse((x - r - 5, y - r - 5, x + r + 5, y + r + 5), fill=BG, outline=col, width=2)
    if k == "home":
        node_icon(d, c, "HOME", r * 2.2, col)
    elif k == "value":
        coin(d, c, r * 0.8, col)
    else:
        cracked_shield(d, (x, y - 2), r * 0.7, col)


def disc(d, c, n: int, col, r: int = 15, size: int = 17) -> None:
    x, y = c
    d.ellipse((x - r, y - r, x + r, y + r), fill=col, outline=INK, width=2)
    text(d, (x, y - size / 2 - 1), str(n), size, INK, "mono", anchor="ma")


def threat_chip(d, c, tid: str, hp: int | None = None, scale: float = 1.0) -> None:
    """Two-number threat token (auto-battler convention): silhouette, HP disc (cobalt), damage disc (red), route glyph."""
    name, mhp, dmg, spd, *_ = THREATS[tid]
    x, y = c
    s = scale
    d.rounded_rectangle((x - 34 * s, y - 30 * s, x + 34 * s, y + 30 * s), radius=8, fill=(18, 26, 64), outline=THREAT, width=3)
    threat(d, (x, y - 4 * s), tid, 15 * s, show_hp=False)
    disc(d, (x - 32 * s, y + 28 * s), mhp if hp is None else hp, THREAT, int(14 * s), int(16 * s))
    disc(d, (x + 32 * s, y + 28 * s), dmg, DMG, int(14 * s), int(16 * s))
    route_glyph(d, (x + 32 * s, y - 28 * s), tid, 6 * s)
    for i in range(spd):
        px = x - 30 * s + i * 9 * s
        d.polygon([(px, y - 26 * s), (px + 7 * s, y - 20 * s), (px, y - 14 * s)], fill=INK)


def mark2(d, xf: MapXf, key: str, info: dict, r: float = 30) -> None:
    """End-of-raid tag from a sim node: HOLDS (check), SCUFFED (check + red -N: damaged, still up), DOWN (bolt), TAKEN (flag + X)."""
    out = info["outcome"]
    x, y = xf.p(key)
    ty = y - r - 30
    loss = info["before"] - info["after"]
    if key == "HOME":
        col = HOLD if loss == 0 else STAMP_HOLD
        w = 44 if loss == 0 else 64
        d.rounded_rectangle((x - w / 2, ty, x + w / 2, ty + 22), radius=5, fill=BG2, outline=col, width=2)
        if loss == 0:
            check(d, (x - w / 2 + 12, ty + 11), 6, HOLD)
        if loss:
            text(d, (x, ty + 2), f"-{loss}", 17, DMG, "mono", anchor="ma")
        else:
            text(d, (x + 8, ty + 2), "0", 17, HOLD, "mono", anchor="ma")
        return
    if out == "holds":
        d.rounded_rectangle((x - 18, ty, x + 18, ty + 22), radius=5, fill=(20, 60, 60), outline=HOLD, width=2)
        check(d, (x, ty + 11), 7, HOLD)
    elif out == "scuffed":
        d.rounded_rectangle((x - 32, ty, x + 32, ty + 22), radius=5, fill=(20, 60, 60), outline=HOLD, width=2)
        check(d, (x - 18, ty + 11), 6, HOLD)
        d.polygon([(x + 32, ty), (x + 32, ty + 10), (x + 22, ty)], fill=DMG)
        text(d, (x + 10, ty + 2), f"-{loss}", 16, DMG, "mono", anchor="ma")
    elif out == "down":
        R.mark(d, xf, key, "DOWN", r)
    elif out == "taken":
        R.mark(d, xf, key, "TAKEN", r)


def node_states(r, step: int | None = None) -> tuple[dict, dict]:
    """Node state and hp after `step` (None = the end of the raid)."""
    if step is None:
        st = {k: ("down" if v["outcome"] == "down" else ("taken" if v["outcome"] == "taken" else "ok")) for k, v in r.nodes.items()}
        return st, {k: v["after"] for k, v in r.nodes.items()}
    ev = r.steps[step - 1]
    st = {k: ("ok" if c == "ok" else c) for k, c in ev["cond"].items()}
    return st, dict(ev["hp"])


def stamp_losses(img, d, c, r, size: int = 64) -> None:
    """Verdict stamp with the loss icons inside it: house -N, bolt xN, flag xN (the stamp says what was lost, without words)."""
    lo = losses(r)
    home_loss = r.home_before - r.home_after
    clean = r.clean
    if r.breached:
        word, col = "BREACHED", STAMP_BREACH
    elif clean:
        word, col = "CLEAN DEFENSE", STAMP_CLEAN
    else:
        word, col = "CELL HOLDS", STAMP_HOLD
    stamp(img, c, word, col, size, -5)
    x, y = c
    y += size * 0.9
    items = []
    if home_loss:
        items.append(("HOME", f"-{home_loss}"))
    if lo["down"]:
        items.append(("DOWN", f"x{len(lo['down'])}"))
    if lo["taken"]:
        items.append(("TAKEN", f"x{len(lo['taken'])}"))
    if clean:
        items = [("HEAT", "+5"), ("SCH", "+12")]
    w = 110 * len(items)
    x0 = x - w / 2
    d.rounded_rectangle((x0 - 10, y, x0 + w + 10, y + 46), radius=8, fill=(20, 20, 34), outline=col, width=3)
    for i, (k, s) in enumerate(items):
        cx = x0 + i * 110 + 30
        if k == "HOME":
            node_icon(d, (cx, y + 23), "HOME", 34, CELL)
        elif k == "DOWN":
            d.ellipse((cx - 15, y + 8, cx + 15, y + 38), fill=(48, 50, 58), outline=DOWN_GREY, width=2)
            bolt(d, (cx, y + 23), 12)
        elif k == "TAKEN":
            flag(d, (cx, y + 23), 12, THREAT_LIGHT)
        elif k == "HEAT":
            flame(d, (cx, y + 25), 11, HEAT)
        elif k == "SCH":
            coin(d, (cx, y + 23), 11)
        text(d, (cx + 22, y + 10), s, 22, DMG if s.startswith("-") else INK, "mono")


def countdown(d, c, n: int, of: int = 3) -> None:
    """When: a segmented dial; each segment is one netrun map node left before you are home (house in the middle)."""
    x, y = c
    d.ellipse((x - 40, y - 40, x + 40, y + 40), fill=(16, 22, 52), outline=THREAT, width=3)
    for i in range(of):
        a0 = -90 + i * 360 / of + 8
        a1 = -90 + (i + 1) * 360 / of - 8
        d.arc((x - 50, y - 50, x + 50, y + 50), a0, a1, fill=THREAT if i < n else (40, 46, 80), width=9)
    node_icon(d, (x, y - 8), "HOME", 40, CELL)
    shield(d, (x + 20, y - 22), 7, THREAT)
    text(d, (x, y + 8), str(n), 24, INK, "mono", anchor="ma")


def why_chain(d, x, y, heat: int = 51, at: int = 50) -> None:
    flame(d, (x + 10, y + 12), 10, HEAT)
    text(d, (x + 24, y), f"{heat}", 22, HEAT, "mono")
    text(d, (x + 56, y + 2), ">", 18, DIM, "mono")
    d.line([(x + 76, y - 2), (x + 76, y + 26)], fill=INK, width=3)
    text(d, (x + 82, y), f"{at}", 22, INK, "mono")
    arrow(d, (x + 112, y + 12), (x + 152, y + 12), INK, 3, 9, shorten=0)
    shield(d, (x + 168, y + 10), 11, THREAT)


def asset_card2(d, x, y, aid: str, w: int = 96, h: int = 112, selected: bool = False, used: bool = False) -> None:
    """Asset card whose stats are glyphs + digits: turret = 4 dmg, reach ring 1; ICE = hold 2 steps; DECOY = pull; crew = x1.5."""
    edge = CELL if selected else PANEL_EDGE
    fill = (50, 46, 30) if selected else PANEL
    if used:
        fill, edge = (24, 26, 40), (50, 54, 70)
    col = CELL if not used else DIM
    d.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=fill, outline=edge, width=3 if selected else 2)
    asset_icon(d, (x + w / 2, y + 36), aid, 18, col)
    sy = y + 76
    if aid == "TURRET":
        swords(d, (x + 22, sy + 10), 7, DMG)
        text(d, (x + 34, sy), "4", 20, INK, "mono")
        d.ellipse((x + 56, sy + 1, x + 76, sy + 21), outline=col, width=2)
        text(d, (x + 82, sy), "1", 20, INK, "mono")
    elif aid == "ICE":
        for i in range(2):
            d.rectangle((x + 24 + i * 22, sy + 2, x + 40 + i * 22, sy + 20), outline=HOLD, width=2)
        text(d, (x + 72, sy), "2", 20, INK, "mono")
    elif aid == "DECOY":
        for i in range(3):
            arrow(d, (x + 14 + i * 4, sy + 10), (x + 50, sy + 10), col, 2, 7, shorten=0)
        d.ellipse((x + 62, sy + 3, x + 78, sy + 19), fill=col)
    elif aid == "CREW":
        asset_icon(d, (x + 30, sy + 8), "TURRET", 7, col)
        text(d, (x + 44, sy), "x1.5", 18, INK, "mono")


def arrow_path(d, xf: MapXf, keys: list[str], col=THREAT, width: int = 5, dash_line: bool = False, offset=(0, 0)) -> None:
    pts = [(xf.p(k)[0] + offset[0], xf.p(k)[1] + offset[1]) for k in keys]
    for a, b in zip(pts, pts[1:]):
        arrow(d, a, b, col, width, 14, dash_line=dash_line, shorten=28)


def step_cells(d, x0, y0, r, now, all_lit: bool = False) -> None:
    """Scrubber: an ALL cell (the whole raid at once), then one cell per step with the silhouettes that strike in it."""
    n = len(r.steps)
    cw = min(52, int(560 / (n + 1)))
    lit = all_lit
    d.rounded_rectangle((x0, y0, x0 + cw + 18, y0 + 42), radius=5, fill=(50, 46, 30) if lit else PANEL,
                        outline=CELL if lit else PANEL_EDGE, width=3 if lit else 1)
    text(d, (x0 + (cw + 18) / 2, y0 + 4), "ALL", 13, CELL if lit else DIM, anchor="ma")
    d.line([(x0 + 8, y0 + 30), (x0 + cw + 10, y0 + 30)], fill=CELL if lit else DIM, width=3)
    for i, ev in enumerate(r.steps):
        x = x0 + cw + 26 + i * (cw + 4)
        on = (now == i + 1) and not all_lit
        d.rounded_rectangle((x, y0, x + cw, y0 + 42), radius=5, fill=(50, 46, 30) if on else PANEL,
                            outline=CELL if on else PANEL_EDGE, width=3 if on else 1)
        text(d, (x + 4, y0 + 2), str(i + 1), 11, CELL if on else DIM, "mono")
        hitters = [h[0] for h in ev["hits"] if h[0] != "CASCADE"]
        for j, t in enumerate(hitters[:3]):
            threat(d, (x + 12 + j * 13, y0 + 28), t, 5.5, show_hp=False)
        if ev["down"] or ev["taken"]:
            d.rectangle((x + cw - 9, y0 + 3, x + cw - 3, y0 + 9), fill=DMG)
