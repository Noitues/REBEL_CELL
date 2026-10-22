"""Concept G, round 5: G4 with the critic-R4 findings fixed (see BARRIERS_R5.md; each rule change a designer decision).
- sim rounding = GDScript roundi (a crew-boosted Sentry deals 5, not 4).
- Patching is a per-node choice in the aftermath. The forecast's net assumes the full repair bill. The aftermath shows,
  per choice, the next raid's projection: the Heat-75 roster (Lockdown Unit added, it freezes a home link) and the same
  pieces left in place.
- The draft preview is the card's marginal value: best net with the card minus best net without it (r5_marginal.json,
  the full 12,960-plan sweep).
- Per-raid corp trait (designer decision): the Heat-75 Solace raid brings PLATING (the Enforcer ignores single shots of
  8+). It moves the key piece from the Railgun to the Sentry, so the draft answer changes between raids.
- Gun cards show their targeting (house = threat nearest home; heavy silhouette = the hardest hitter).
- The tie-break glyph is drawn where a route actually forked. The forecast lists the attack order. The playout clock
  includes kill-cams. HOLDS has its own stamp. Lost nodes are drawn as node silhouettes, and the only currency icon is
  the coin.
Every number is sim.py output."""

from __future__ import annotations

import json
from pathlib import Path

from r2_kit import *  # noqa: F403
from sim import ADJ, INSTALL, NODE_HP as SIM_HP, ROSTER_50, ROSTER_75, Plan, bfs, run, summary

import concept_g3_merged as G3
import concept_g4_merged as G4
from concept_g4_merged import (CLEAN_BONUS, KILLCAM_S, BEAT_S, CAP_S, SALVAGE, beats, chevron, dial, kills, lost, net,
                               netrun_hex, payout, piece, place_assets, price, record, skull, struck, xsign)

NAME = "G MERGED r5"
MOMENTS = G4.MOMENTS
RULE = dict(G4.RULE)
RULE_75 = dict(RULE, plating=True)
POOL = G4.POOL
P, R, PICK = G4.P, G4.R, G4.PICK
XF, SHADE, OFF = G4.XF, G4.SHADE, G4.OFF
MARG = json.loads((Path(__file__).parent / "r5_marginal.json").read_text(encoding="utf-8"))
TARGETING = {"TURRET": "first", "SENTRY": "first", "RAILGUN": "high"}


def end_hp(r, patched: set) -> dict:
    hp = dict(SIM_HP)
    for k, v in r.nodes.items():
        if k in patched or v["outcome"] == "holds":
            continue
        hp[k] = 0 if v["outcome"] == "taken" else v["after"]
    return hp


def projection(plan_key: str, patched: set):
    """Next raid (Heat 75 roster, Solace plating) with the same pieces left in place, from the chosen patch state."""
    p = P[plan_key]
    return run(Plan(dict(p.assets), p.crew, dict(RULE_75)), threats=list(ROSTER_75), start_hp=end_hp(R[plan_key], patched))


def scuffed(r) -> list[str]:
    return [k for k, v in r.nodes.items() if v["outcome"] == "scuffed" and k != "HOME"]


def patch_cost(r, nodes) -> int:
    return sum(r.nodes[k]["before"] - r.nodes[k]["after"] for k in nodes)


SC1 = scuffed(R["P1"])
CHOICES = [("all", set(SC1)), ("skip RELAY", set(SC1) - {"RELAY"}), ("none", set())]
PROJ = {name: projection("P1", s) for name, s in CHOICES}
NEXT_BARE = run(Plan({}, "SAFE", dict(RULE_75)), threats=list(ROSTER_75))


def forks(r, start_hp=None) -> list[tuple[str, str]]:
    """(threat, node) where the fixed route had two equal-length next hops (the weaker-node tie-break chose)."""
    hp = dict(SIM_HP if start_hp is None else start_hp)
    out = []
    for tid, path in r.routes.items():
        tgt = path[-1]
        for cur in path[:-1]:
            blocked = frozenset({"HOME"}) if tgt != "HOME" and cur != "HOME" else frozenset()
            dt = bfs(tgt, blocked)
            if cur not in dt:
                continue
            c = [m for m in ADJ[cur] if m in dt and dt[m] == dt[cur] - 1]
            if len(c) > 1:
                out.append((tid, cur))
    return out


# ---------- glyphs ----------
def target_glyph(d, c, kind: str, col=INK) -> None:
    if kind == "first":
        node_icon(d, c, "HOME", 16, col)
    else:
        threat(d, c, "ENFORCER", 6, show_hp=False, col=THREAT)


def lost_nodes(d, x, y, r, size=20) -> None:
    """Lost nodes as silhouettes: grey for DOWN, a grease-pencil X for TAKEN; a teal check when none."""
    lo = [(k, v["outcome"]) for k, v in r.nodes.items() if v["outcome"] in ("down", "taken")]
    if not lo:
        check(d, (x + 8, y), 7, STAMP_CLEAN)
        return
    for i, (k, o) in enumerate(lo):
        cx = x + i * (size + 10)
        node_icon(d, (cx + 8, y), k, size, DOWN_GREY if o == "down" else CELL)
        if o == "taken":
            pencil_x(d, (cx + 8, y), size * 0.45, seed=3)
        else:
            bolt(d, (cx + 16, y + 8), 5)


def frozen_link(d, xf, a, b) -> None:
    pa, pb = xf.p(a), xf.p(b)
    d.line([pa, pb], fill=HOLD, width=6)
    m = lerp(pa, pb, 0.5)
    d.rounded_rectangle((m[0] - 11, m[1] - 9, m[0] + 11, m[1] + 11), radius=3, fill=BG, outline=HOLD, width=2)
    d.arc((m[0] - 6, m[1] - 18, m[0] + 6, m[1] - 2), 180, 360, fill=HOLD, width=3)


def trait_chip(d, x, y) -> None:
    """Solace plating: the Enforcer with a shield, and an 8+ shot struck through."""
    panel(d, (x, y, x + 150, y + 50), edge=THREAT)
    threat(d, (x + 26, y + 26), "ENFORCER", 11, show_hp=False)
    shield(d, (x + 52, y + 26), 9, HOLD, outline=INK)
    swords(d, (x + 86, y + 26), 7, DMG)
    text(d, (x + 98, y + 12), "8+", 18, INK, "mono")
    d.line([(x + 76, y + 42), (x + 140, y + 10)], fill=DMG, width=3)


def card(d, x, y, aid: str, marg: dict, sel=False, used=False, w=104, h=132) -> None:
    G4.card(d, x, y, aid, sel=sel, used=used, w=w, h=h, preview=False)
    if aid in TARGETING:
        target_glyph(d, (x + w - 16, y + 16), TARGETING[aid])
    d.line([(x + 8, y + 92), (x + w - 8, y + 92)], fill=PANEL_EDGE)
    v = marg[aid]
    coin(d, (x + 24, y + 112), 9)
    text(d, (x + 38, y + 99), f"{v:+d}", 22, STAMP_CLEAN if v > 0 else DMG if v < 0 else DIM, "mono")


def plan_row(d, x, y, label, r, on, pick) -> None:
    d.rounded_rectangle((x, y, x + 248, y + 84), radius=6, fill=(50, 46, 30) if on else BG2,
                        outline=CELL if on else PANEL_EDGE, width=3 if on else 1)
    text(d, (x + 10, y + 6), label, 22, CELL if on else DIM, "mono")
    for i, a in enumerate(pick):
        piece(d, (x + 50 + i * 30, y + 20), a, 8)
    coin(d, (x + 186, y + 20), 9)
    n = net(r)
    text(d, (x + 198, y + 8), f"{n:+d}", 20, STAMP_CLEAN if n > 0 else DMG, "mono")
    node_icon(d, (x + 22, y + 58), "HOME", 22, CELL)
    hl = r.home_before - r.home_after
    text(d, (x + 36, y + 47), f"-{hl}", 17, DMG if hl else HOLD, "mono")
    lost_nodes(d, x + 92, y + 58, r)
    for i, k in enumerate(scuffed(r)[:3]):
        node_icon(d, (x + 172 + i * 28, y + 58), k, 18, CELL)
        d.polygon([(x + 181 + i * 28, y + 49), (x + 181 + i * 28, y + 57), (x + 173 + i * 28, y + 49)], fill=DMG)


def order_panel(d, r, x=300, y=600, maxn=8) -> None:
    """Attack order: one chip per shot in resolver order: step, gun, target, damage."""
    shots = [(ev["step"], s) for ev in r.steps for s in ev["shots"]]
    panel(d, (x, y, x + 86 * min(maxn, len(shots)) + 10, y + 90))
    for i, (st, (site, gun, tid, dmg, left)) in enumerate(shots[:maxn]):
        cx = x + 10 + i * 86
        order_badge(d, (cx + 12, y + 18), i + 1, CELL)
        text(d, (cx + 30, y + 8), str(st), 13, DIM, "mono")
        piece(d, (cx + 18, y + 54), gun if gun in G4.GUN_DMG else "TURRET", 8)
        arrow(d, (cx + 30, y + 54), (cx + 46, y + 54), INK, 2, 6, shorten=0)
        threat(d, (cx + 58, y + 54), tid, 7, show_hp=False)
        text(d, (cx + 70, y + 64), f"-{dmg}", 14, CELL, "mono")
        if left <= 0:
            skull(d, (cx + 76, y + 42), 6)


def routes(d, r, faint=False, start_hp=None) -> None:
    """G4's routes, with the tie-break glyph only where a route really forked."""
    for tid, path in r.routes.items():
        col = (44, 60, 120) if faint else SHADE[tid]
        k = OFF[tid]
        pts = [(XF.p(n)[0] + k, XF.p(n)[1] + k) for n in path]
        for a, b in zip(pts, pts[1:]):
            arrow(d, a, b, col, 6, 13, shorten=30)
            if not faint:
                L = max(1, ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5)
                d.line([lerp(a, b, 30 / L), lerp(b, a, 44 / L)], fill=(235, 240, 255), width=2)
        if not faint:
            threat(d, (pts[0][0] - 26, pts[0][1] - 20), tid, 10, show_hp=False)
            for ev in r.steps:
                for kt, site in ev["kills"]:
                    if kt == tid:
                        x, y = XF.p(site)
                        skull(d, (x + k * 2 + 30, y - 24 + k * 2), 9)
    if not faint:
        for tid, n in forks(r, start_hp):
            x, y = XF.p(n)
            route_glyph(d, (x - 40 + OFF[tid], y + 34), "ENFORCER", 7, CELL)


def stamp_box(img, d, c, r, patched=None, size=60) -> None:
    if r.breached:
        word, col, ang = "BREACHED", STAMP_BREACH, -8
    elif r.clean:
        word, col, ang = "CLEAN", STAMP_CLEAN, -5
    else:
        word, col, ang = "HOLDS", STAMP_HOLD, 4
    stamp(img, c, word, col, size, ang)


def net_box(d, x, y, r, patch: int, w=248) -> None:
    panel(d, (x, y, x + w, y + 104), edge=STAMP_CLEAN if r.clean else STAMP_HOLD, width=2)
    skull(d, (x + 18, y + 22), 8)
    xsign(d, (x + 36, y + 22), 4)
    text(d, (x + 46, y + 10), str(kills(r)), 20, INK, "mono")
    coin(d, (x + 82, y + 22), 8)
    text(d, (x + 94, y + 10), f"+{SALVAGE * kills(r)}", 20, INK, "mono")
    d.ellipse((x + 146, y + 8, x + 172, y + 34), fill=(20, 60, 60) if r.clean else BG2,
              outline=STAMP_CLEAN if r.clean else DIM, width=2)
    check(d, (x + 159, y + 21), 6, STAMP_CLEAN if r.clean else DIM)
    text(d, (x + 180, y + 10), f"+{CLEAN_BONUS if r.clean else 0}", 20, INK if r.clean else DIM, "mono")
    coin(d, (x + 18, y + 62), 8, DIM)
    text(d, (x + 30, y + 50), f"-{patch}", 20, DMG, "mono")
    d.line([(x + 96, y + 46), (x + 96, y + 80)], fill=PANEL_EDGE, width=2)
    coin(d, (x + 124, y + 64), 12)
    n = payout(r) - patch
    text(d, (x + 142, y + 46), f"{n:+d}", 30, STAMP_CLEAN if n > 0 else DMG, "mono")


# ---------- frames ----------
def f0():
    img = G4.f0()
    d = ImageDraw.Draw(img)
    hx, hy = 1060, 380
    # landing point: the raid lands on the return to this node (cobalt ring with a down arrow)
    d.ellipse((hx - 58, hy - 58, hx + 58, hy + 58), outline=THREAT, width=4)
    arrow(d, (hx + 70, hy - 90), (hx + 40, hy - 46), THREAT, 4, 10, shorten=0)
    header(d, NAME, 0, "Netrun map: dial = 2 netruns until home; the cobalt ring = where the raid lands (on the return); raid size per Heat tier; record")
    return img


def f1():
    img, d = new_frame(NAME, "warning")
    r = R["BARE"]
    G4.base(d)
    G4.hud(d)
    why_chain(d, 560, 52)
    routes(d, r)
    panel(d, (930, 100, 1268, 330))
    for i, t in enumerate(("COLLECTOR", "AUDITOR", "ENFORCER")):
        y = 118 + i * 70
        threat_chip(d, (972, y + 22), t, scale=0.6)
        for j, n in enumerate(r.routes[t][1:]):
            x = 1024 + j * 52
            node_icon(d, (x, y + 22), n, 30, CELL)
            if j:
                arrow(d, (x - 40, y + 22), (x - 14, y + 22), SHADE[t], 3, 7, shorten=0)
    G4.tags(d, r)
    plan_row(d, 1020, 350, "0", r, False, ())
    record(d, 960, 470, 1, 1)
    fk = ", ".join(f"{t} at {n}" for t, n in forks(r)) or "none in this raid"
    header(d, NAME, 1, f"Warning: fixed routes, white core; fork glyph only where a tie was broken ({fk}); the bare raid nets {net(r):+d} after the full repair bill")
    return img


def f2():
    img, d = new_frame(NAME, "draft")
    r = R["BARE"]
    G4.base(d, r)
    G4.hud(d)
    routes(d, r, faint=True)
    G4.tags(d, r)
    m = MARG["heat50"]["marginal"]
    panel(d, (250, 496, 1030, 704), edge=CELL)
    for i, a in enumerate(POOL):
        card(d, 266 + i * 116, 512, a, m, sel=a in PICK["P1"])
    for i in range(3):
        d.rounded_rectangle((870, 520 + i * 56, 1014, 564 + i * 56), radius=6, fill=CELL)
        piece(d, (942, 542 + i * 56), PICK["P1"][i], 10, BG)
    best = MARG["heat50"]["best"][0]
    header(d, NAME, 2, f"Draft: each card's coin = best net with it minus best net without it ({', '.join(f'{k} {v:+d}' for k, v in m.items())}); top-right = what the gun aims at")
    return img


def f3():
    img = G4.f3()
    d = ImageDraw.Draw(img)
    header(d, NAME, 3, f"Planning: railgun on RELAY rings its reach; what-if lost {lost(R['BARE'])} > {lost(R['RAIL'])}, net {net(R['BARE']):+d} > {net(R['RAIL']):+d}; effective numbers on pieces")
    return img


def f4():
    img, d = new_frame(NAME, "forecast")
    r = R["P1"]
    G4.base(d, r)
    G4.hud(d)
    routes(d, r)
    G4.tags(d, r)
    place_assets(d, P["P1"])
    panel(d, (1012, 96, 1272, 380))
    plan_row(d, 1018, 104, "1", R["P1"], True, PICK["P1"])
    plan_row(d, 1018, 196, "2", R["P2"], False, PICK["P2"])
    plan_row(d, 1018, 288, "3", R["P3"], False, PICK["P3"])
    net_box(d, 1018, 400, r, price(r))
    G3.threat_strip(d, r, "ENFORCER", 20, 600)
    order_panel(d, r, 330, 600, 7)
    button(d, (1060, 640, 1268, 690), "START RAID")
    header(d, NAME, 4, f"Forecast: nets {net(R['P1']):+d} / {net(R['P2']):+d} / {net(R['P3']):+d} after the full repair bill; lost nodes as silhouettes; attack order chips (step, gun, target, damage)")
    return img


def f5():
    img, d = new_frame(NAME, "resolution")
    r = R["P1"]
    s = 2
    bt = beats(r)
    now_b = sum(1 for b in bt if b[0] < s) + 2
    k_before = sum(len(ev["kills"]) for ev in r.steps if ev["step"] < s)
    now_s = now_b * BEAT_S + k_before * KILLCAM_S
    secs = min(CAP_S, len(bt) * BEAT_S + kills(r) * KILLCAM_S)
    img4 = G4.f5()
    img.paste(img4)
    d = ImageDraw.Draw(img)
    d.rectangle((560, 96, 720, 122), fill=BG)
    text(d, (640, 104), f"0:{int(now_s):02d} / 0:{int(secs):02d}", 16, DIM, "mono", anchor="ma")
    d.rectangle((0, H - 26, W, H), fill=BG)
    header(d, NAME, 5, f"Resolution, no input: {len(bt)} beats (~1 s each) + {kills(r)} kill-cams (2 s) = {int(secs)} s; the clock counts both; numbered shots")
    return img


def f6():
    img, d = new_frame(NAME, "aftermath")
    r = R["P1"]
    G4.base(d, r)
    heat_bar(d, 470, 22, 340, 51, raid_at=None)
    G4.tags(d, r)
    stamp_box(img, d, (1010, 150), r)
    chosen = CHOICES[0]
    net_box(d, 886, 210, r, patch_cost(r, chosen[1]) + (r.home_before - r.home_after))
    # per-node patch choice, each with the next raid's projection (Heat 75 roster, plating, same pieces)
    panel(d, (20, 470, 860, 704))
    for i, (name, patched) in enumerate(CHOICES):
        y = 484 + i * 72
        on = i == 0
        d.rounded_rectangle((32, y, 848, y + 62), radius=6, fill=(50, 46, 30) if on else BG2,
                            outline=CELL if on else PANEL_EDGE, width=3 if on else 1)
        for j, k in enumerate(SC1):
            cx = 70 + j * 120
            node_icon(d, (cx, y + 31), k, 30, CELL)
            if k in patched:
                coin(d, (cx + 30, y + 31), 8)
                text(d, (cx + 42, y + 19), str(r.nodes[k]["before"] - r.nodes[k]["after"]), 18, INK, "mono")
                check(d, (cx + 70, y + 31), 7, STAMP_CLEAN)
            else:
                text(d, (cx + 24, y + 19), f"-{r.nodes[k]['before'] - r.nodes[k]['after']}", 18, DMG, "mono")
        coin(d, (330, y + 31), 10)
        text(d, (346, y + 19), f"-{patch_cost(r, patched)}", 20, INK, "mono")
        arrow(d, (410, y + 31), (450, y + 31), DIM, 3, 8, shorten=0)
        flame(d, (472, y + 33), 8, HEAT)
        text(d, (484, y + 19), "75", 18, HEAT, "mono")
        pr = PROJ[name]
        node_icon(d, (548, y + 31), "HOME", 24, CELL)
        hl = pr.home_before - pr.home_after
        text(d, (562, y + 19), f"-{hl}", 18, DMG if hl else HOLD, "mono")
        lost_nodes(d, 620, y + 31, pr, 22)
        coin(d, (790, y + 31), 9)
        text(d, (802, y + 19), f"{net(pr):+d}", 18, STAMP_CLEAN if net(pr) > 0 else DMG, "mono")
    flame(d, (900, 360), 10, HEAT)
    text(d, (916, 348), "51 = 51", 20, HEAT, "mono")
    record(d, 905, 400, 2, 2)
    button(d, (1090, 640, 1265, 690), "BACK TO HQ")
    p_all, p_skip, p_none = (PROJ[n] for n, _ in CHOICES)
    header(d, NAME, 6, f"Aftermath: patch choice per node, each with the next raid (Heat 75, same pieces): patch all {lost(p_all)} lost, skip RELAY {lost(p_skip)}, skip all {lost(p_none)}")
    return img


def f7():
    img, d = new_frame(NAME, "next raid")
    r = NEXT_BARE
    G4.base(d)
    heat_bar(d, 470, 22, 340, 76, raid_at=75)
    why_chain(d, 560, 52, 76, 75)
    dial(d, (70, 70), 2)
    for a, b in r.frozen:
        frozen_link(d, XF, a, b)
    routes(d, r)
    G4.tags(d, r)
    trait_chip(d, 940, 100)
    panel(d, (930, 170, 1268, 330))
    for i, t in enumerate(ROSTER_75):
        threat_chip(d, (972 + (i % 2) * 150, 210 + (i // 2) * 70), t, scale=0.6)
    m50, m75 = MARG["heat50"]["marginal"], MARG["heat75 +plating"]["marginal"]
    panel(d, (250, 520, 1030, 704), edge=CELL)
    for i, a in enumerate(POOL):
        card(d, 266 + i * 116, 536, a, m75)
        struck(d, (266 + i * 116 + 62, 636), m50[a], m75[a], 14, INK)
    fz = ", ".join(f"{a}-{b}" for a, b in r.frozen)
    header(d, NAME, 7, f"Next raid, Heat 76: 4 threats (Lockdown freezes {fz}), Solace plating (Enforcer ignores 8+): draft values move (railgun {m50['RAILGUN']:+d} > {m75['RAILGUN']:+d}, sentry {m50['SENTRY']:+d} > {m75['SENTRY']:+d})")
    return img


FRAMES = [f0, f1, f2, f3, f4, f5, f6, f7]

if __name__ == "__main__":
    for k, r in R.items():
        print(k, summary(r), "net", net(r))
    for n, r in PROJ.items():
        print("PROJ", n, summary(r), "lost", lost(r), "net", net(r), r.frozen)
    print("NEXT_BARE", summary(NEXT_BARE), NEXT_BARE.frozen, NEXT_BARE.routes)
    print("forks", forks(R["BARE"]), forks(R["P1"]))
    print(MARG)
