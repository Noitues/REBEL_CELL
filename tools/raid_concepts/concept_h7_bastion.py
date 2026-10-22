"""Concept H, round 7: BASTION with the round-6 critics' fixes (rules in h7_campaign.py; each a designer decision).
- The fortress persists; buy up to 2 pieces per visit. The forecast runs YOUR leg plan: this visit's buys (solid) and
  the buys you queue for later visits (ghost, numbered by visit). No solver hints: the game never suggests a plan.
  Here "your plan" is leg 0's planned line and "plan B" is the one-raid-at-a-time line (h7_leg0.json).
- Node jobs: Vault +3 and Relay +2 income per visit, Safehouse = crew station, Firewall = home's gun, Proxy = intel (see
  two raids ahead). A TAKEN node loses its job for the leg and becomes a corp foothold.
- Corp adaptation, shown at the telegraph: the toughest threat counters your most-invested piece type.
- Survivors rejoin the next raid. CLEAN heals scuffs free, so a CLEAN raid never nets negative. Crew = +2 per shot.
- Glyphs: the BANK is a strongbox; the per-raid NET is a coin with a sign. Every threat effect is cobalt (the Lockdown
  freeze included); red only marks loss; teal only the Cell's checks.
Every number is sim.py output through h7_campaign.py."""
from __future__ import annotations

import json
from pathlib import Path

from r2_kit import *  # noqa: F403
from sim import summary

import concept_g3_merged as G3
import concept_g4_merged as G4
import concept_g5_merged as G5
import concept_h6_bastion as H
import concept_p6_stakes as P
from concept_g4_merged import dial, piece
from h7_campaign import (BASE_INCOME, BONUS, COST, COUNTER, RELAY_INC, SALVAGE, START, VAULT_INC, State, invested,
                         raid_result, roster_for, settle)

NAME = "H7 BASTION r7"
MOMENTS = ["0_leg", "1_shop", "2_forecast", "3_resolution", "4_aftermath", "5_visit2", "6_visit3", "7_record"]
XF, SHADE, OFF = G3.XF, G3.SHADE, G3.OFF
DATA = json.loads((Path(__file__).parent / "h7_leg0.json").read_text(encoding="utf-8"))
LEG = [[tuple(t) for t in raid] for raid in DATA["leg"]]
HEATS = (26, 51, 76)
NETRUNS = (2, 3, 3)   # projected netruns before each raid (Heat per netrun, campaign config)


def replay(line):
    """Re-run a cached line through the H7 rules; per raid: (state before, roster, result, fortress, state after, net)."""
    st = State()
    rows = []
    for x in line:
        i = x["raid"]
        roster = roster_for(LEG, i, st)
        fort, r = raid_result(st, tuple(x["buy"]), tuple(x["place"]), x["crew"], roster)
        ns, raid_net = settle(st, {k: list(v) for k, v in fort.items()}, r, roster, i,
                              (tuple(x["buy"]), tuple(x["place"]), x["crew"]), len(LEG))
        rows.append({"before": st, "roster": roster, "r": r, "fort": fort, "after": ns, "net": raid_net, "x": x})
        st = ns
    return rows


MINE, PLAN_B = replay(DATA["planned"]), replay(DATA["greedy"])


def income(st: State) -> int:
    return BASE_INCOME + (VAULT_INC if "VAULT" not in st.lost else 0) + (RELAY_INC if "RELAY" not in st.lost else 0)


# ---------- glyphs ----------
def strongbox(d, c, r=11, col=INK) -> None:
    x, y = c
    d.rounded_rectangle((x - r, y - r * 0.7, x + r, y + r * 0.8), radius=3, outline=col, width=3)
    d.line([(x - r, y - r * 0.1), (x + r, y - r * 0.1)], fill=col, width=2)
    d.rectangle((x - r * 0.2, y - r * 0.3, x + r * 0.2, y + r * 0.15), fill=col)


def signed_coin(d, xy, n: int, size=20) -> None:
    x, y = xy
    coin(d, (x, y + size * 0.55), size * 0.45)
    text(d, (x + size * 0.7, y), f"{n:+d}", size, STAMP_CLEAN if n > 0 else DMG if n < 0 else DIM, "mono")


def trait_glyph(d, c, trait: str, r=8) -> None:
    """The counter trait, drawn on the threat: a cobalt shield with the countered piece struck through."""
    x, y = c
    shield(d, (x, y), r, THREAT, outline=INK)
    piece_for = {"PLATED": "RAILGUN", "ARMORED": "TURRET", "FROSTPROOF": "ICE", "BLIND": "DECOY"}[trait]
    piece(d, (x + r * 2.2, y), piece_for, r * 0.8, INK)
    d.line([(x + r * 1.2, y + r), (x + r * 3.2, y - r)], fill=THREAT, width=3)


def frozen_link(d, a, b) -> None:
    pa, pb = XF.p(a), XF.p(b)
    d.line([pa, pb], fill=THREAT, width=6)
    m = lerp(pa, pb, 0.5)
    d.rounded_rectangle((m[0] - 11, m[1] - 9, m[0] + 11, m[1] + 11), radius=3, fill=BG, outline=THREAT, width=2)
    d.arc((m[0] - 6, m[1] - 18, m[0] + 6, m[1] - 2), 180, 360, fill=THREAT, width=3)


def raid_panel(d, x, y, roster, i, known=True, w=200) -> None:
    """One telegraphed raid: Heat, projected netruns, the threats (survivors outlined, traits drawn)."""
    panel(d, (x, y, x + w, y + 84), edge=THREAT if known else PANEL_EDGE)
    flame(d, (x + 14, y + 16), 7, HEAT)
    text(d, (x + 26, y + 5), str(HEATS[i]), 15, HEAT, "mono")
    G4.netrun_hex(d, (x + 76, y + 16), 8, INK)
    text(d, (x + 88, y + 5), str(NETRUNS[i]), 15, INK, "mono")
    if not known:
        G5.eye(d, (x + w / 2, y + 52), 12, DIM) if hasattr(G5, "eye") else P.eye(d, (x + w / 2, y + 52), 12, DIM)
        d.line([(x + w / 2 - 16, y + 66), (x + w / 2 + 16, y + 38)], fill=DIM, width=3)
        return
    for j, t in enumerate(roster[:6]):
        tid, e = t[0], t[1]
        traits = t[2] if len(t) > 2 else ()
        cx = x + 22 + j * 30
        threat(d, (cx, y + 52), tid.split("#")[0], 9, show_hp=False, ghost="#" in tid)
        if traits:
            trait_glyph(d, (cx - 4, y + 74), traits[0], 5)


def leg_bar(d, rows, now: int, y=24) -> None:
    """The leg: raids telegraphed while the Proxy holds (two ahead), else only the next."""
    st = rows[now]["before"] if now < len(rows) else rows[-1]["after"]
    ahead = 2 if "PROXY" not in st.lost else 1
    for i in range(3):
        known = i < now or i <= now + ahead - 1
        roster = rows[i]["roster"] if i < len(rows) else LEG[i]
        raid_panel(d, 300 + i * 220, y, roster, i, known=known)
        if i < now:
            d.rectangle((300 + i * 220, y, 500 + i * 220, y + 84), outline=(60, 70, 110), width=2)
            check(d, (480 + i * 220, y + 14), 6, STAMP_CLEAN if rows[i]["r"].clean else STAMP_HOLD)


def place_plan(d, fort: dict, crew, new=(), queued=()) -> None:
    H.place_fort(d, fort, crew, new={n: [b] for b, n in new} if new else None)
    for k, (v, b, n) in enumerate(queued):
        x, y = XF.p(n)
        px, py = x - 50, y - 26 - k * 0
        d.ellipse((px - 14, py - 14, px + 14, py + 14), outline=DIM, width=2)
        piece(d, (px, py), b, 7, DIM)
        text(d, (px + 12, py - 20), str(v), 13, DIM, "mono")


def forecast_rows(d, x, y, rows, label, on=True, w=616) -> None:
    d.rounded_rectangle((x, y, x + w, y + 92), radius=6, fill=(50, 46, 30) if on else BG2,
                        outline=CELL if on else PANEL_EDGE, width=3 if on else 1)
    text(d, (x + 10, y + 6), label, 22, CELL if on else DIM, "mono")
    cw = (w - 40) // 3
    for j, row in enumerate(rows):
        cx = x + 36 + j * cw
        r = row["r"]
        flame(d, (cx + 10, y + 18), 7, HEAT)
        text(d, (cx + 22, y + 7), str(HEATS[j]), 14, HEAT, "mono")
        if r.clean:
            check(d, (cx + 70, y + 18), 7, STAMP_CLEAN)
        G5.lost_nodes(d, cx + 96, y + 18, r, 14)
        signed_coin(d, (cx + 6, y + 36), row["net"], 17)
        strongbox(d, (cx + 16, y + 74), 8)
        text(d, (cx + 30, y + 64), str(row["after"].bank), 16, INK, "mono")


def job_income(d, x, y, st: State) -> None:
    """Income breakdown by job: base + Vault + Relay = income."""
    G4.netrun_hex(d, (x + 10, y + 12), 9, INK)
    text(d, (x + 24, y), f"+{BASE_INCOME}", 20, INK, "mono")
    for j, (k, v) in enumerate((("VAULT", VAULT_INC), ("RELAY", RELAY_INC))):
        lost_ = k in st.lost
        cx = x + 90 + j * 90
        node_icon(d, (cx, y + 12), k, 20, DOWN_GREY if lost_ else CELL)
        text(d, (cx + 16, y), f"+{0 if lost_ else v}", 20, DIM if lost_ else INK, "mono")
    text(d, (x + 280, y), "=", 20, DIM, "mono")
    strongbox(d, (x + 312, y + 12), 9)
    text(d, (x + 328, y), f"+{income(st)}", 20, INK, "mono")


def adapt_chip(d, x, y, st: State, roster) -> None:
    """Why the corp adapted: your top investment, and the trait it gave the toughest threat."""
    top = invested(st.fort)
    if not top:
        return
    tr = COUNTER[top]
    panel(d, (x, y, x + 260, y + 50), edge=THREAT)
    piece(d, (x + 24, y + 25), top, 10)
    arrow(d, (x + 44, y + 25), (x + 80, y + 25), THREAT, 3, 8, shorten=0)
    tough = next(t for t in roster if len(t) > 2 and t[2])
    threat(d, (x + 104, y + 25), tough[0].split("#")[0], 11, show_hp=False)
    trait_glyph(d, (x + 140, y + 25), tr, 9)


# ---------- frames ----------
def f0():
    img, d = new_frame(NAME, "leg")
    G4.base(d)
    heat_bar(d, 300, 116, 640, 26, raid_at=None)
    leg_bar(d, MINE, 0)
    P.jobs_on_map(d)
    strongbox(d, (60, 170), 13)
    text(d, (80, 156), str(START), 28, INK, "mono")
    header(d, NAME, 0, "The leg: raid 1 and raid 2 telegraphed (the Proxy's intel shows two ahead), raid 3 hidden; netruns before each; jobs on the nodes; bank 14 (strongbox)")
    return img


def f1():
    img, d = new_frame(NAME, "shop")
    row = MINE[0]
    G4.base(d)
    leg_bar(d, MINE, 0)
    G5.routes(d, row["r"])
    P.jobs_on_map(d)
    x0 = row["x"]
    queued = [(v + 1, b, n) for v, rr in enumerate(MINE[1:], start=1) for b, n in zip(rr["x"]["buy"], rr["x"]["place"])]
    place_plan(d, row["fort"], x0["crew"], new=list(zip(x0["buy"], x0["place"])), queued=queued)
    H.shop(d, 20, 560, sel=tuple(x0["buy"]), bank=START - sum(COST[b] for b in x0["buy"]))
    panel(d, (636, 506, 1272, 704))
    forecast_rows(d, 646, 512, MINE, "1", True)
    forecast_rows(d, 646, 608, PLAN_B, "2", False)
    header(d, NAME, 1, f"Visit 1 shop: buy turret + decoy at the Firewall now, queue later buys (ghosts, numbered by visit); the forecast runs YOUR plan: bank {[r_['after'].bank for r_ in MINE]} vs plan B {[r_['after'].bank for r_ in PLAN_B]}")
    return img


def f2():
    row = MINE[0]
    r = row["r"]
    img, d = new_frame(NAME, "forecast")
    G4.base(d, r)
    leg_bar(d, MINE, 0)
    G5.routes(d, r)
    G4.tags(d, r)
    P.jobs_on_map(d, r)
    H.place_fort(d, row["fort"], row["x"]["crew"])
    panel(d, (1012, 130, 1270, 230), edge=STAMP_CLEAN if r.clean else STAMP_HOLD)
    signed_coin(d, (1030, 146), row["net"], 30)
    strongbox(d, (1036, 206), 10)
    text(d, (1054, 194), str(row["after"].bank), 22, INK, "mono")
    nxt = MINE[1]
    adapt_chip(d, 1010, 250, MINE[1]["before"], nxt["roster"])
    button(d, (1060, 640, 1268, 690), "START RAID")
    header(d, NAME, 2, f"Raid 1 forecast: CLEAN, net {row['net']:+d} (scuffs heal free after CLEAN); the chip shows how Solace will adapt to your top piece next raid")
    return img


def f3():
    row = MINE[0]
    r = row["r"]
    img, d = new_frame(NAME, "resolution")
    s = min(2, len(r.steps))
    G4.base(d, r, step=s)
    leg_bar(d, MINE, 0)
    G5.routes(d, r, faint=True)
    H.place_fort(d, row["fort"], row["x"]["crew"])
    ev = r.steps[s - 1]
    pos = {}
    for tid, (site, hp, alive, hold) in ev["threats"].items():
        dead = any(k[0] == tid for k in ev["kills"])
        if not alive and not dead:
            continue
        x, y = XF.p(site)
        p = (x + 44, y - 8 + OFF.get(tid.split("#")[0], 0) * 3)
        pos[tid] = p
        threat(d, p, tid.split("#")[0], 15, hp=hp, ghost=dead)
        if dead:
            pencil_x(d, p, 16, seed=4)
    for i, (site, gun, tid, dmg, left) in enumerate(ev["shots"]):
        sx, sy = XF.p(site)
        if tid in pos:
            d.line([(sx, sy), pos[tid]], fill=CELL, width=4)
            order_badge(d, lerp((sx, sy), pos[tid], 0.5), i + 1, CELL)
            text(d, (pos[tid][0] + 18, pos[tid][1] - 44), f"-{dmg}", 22, CELL, "mono")
    speed_controls(d, 1060, 660)
    header(d, NAME, 3, f"Raid 1 playout, no input (step {s} of {len(r.steps)}): the decoy pulls threats into the Firewall's guns; numbered shots")
    return img


def f4():
    row = MINE[0]
    r = row["r"]
    img, d = new_frame(NAME, "aftermath")
    G4.base(d, r)
    leg_bar(d, MINE, 1)
    G4.tags(d, r)
    P.jobs_on_map(d, r)
    H.place_fort(d, row["fort"], row["x"]["crew"])
    G5.stamp_box(img, d, (1010, 170), r)
    panel(d, (20, 560, 860, 700))
    signed_coin(d, (40, 580), row["net"], 24)
    job_income(d, 200, 584, row["after"])
    strongbox(d, (60, 660), 11)
    text(d, (78, 646), str(row["after"].bank), 24, INK, "mono")
    header(d, NAME, 4, f"Raid 1 aftermath: CLEAN, net {row['net']:+d}; income by job: base {BASE_INCOME} + Vault {VAULT_INC} + Relay {RELAY_INC}; bank {row['after'].bank} (strongbox)")
    return img


def visit(n: int):
    row = MINE[n]
    r = row["r"]
    img, d = new_frame(NAME, f"visit {n + 1}")
    G4.base(d, r)
    leg_bar(d, MINE, n)
    for a, b in getattr(r, "frozen", []):
        frozen_link(d, a, b)
    G5.routes(d, r)
    G4.tags(d, r)
    P.jobs_on_map(d, r)
    x0 = row["x"]
    H.place_fort(d, row["fort"], x0["crew"], new={pl: [b] for b, pl in zip(x0["buy"], x0["place"])})
    H.shop(d, 20, 560, sel=tuple(x0["buy"]), bank=row["before"].bank - sum(COST[b] for b in x0["buy"]))
    forecast_rows(d, 636, 600, MINE[n:], str(n + 1), True, w=420)
    adapt_chip(d, 1010, 520, row["before"], row["roster"])
    panel(d, (1012, 130, 1270, 230), edge=STAMP_CLEAN if r.clean else STAMP_HOLD)
    signed_coin(d, (1030, 146), row["net"], 30)
    return img, d, row


def f5():
    img, d, row = visit(1)
    tr = [t for t in row["roster"] if len(t) > 2 and t[2]]
    header(d, NAME, 5, f"Visit 2 (Heat 51): Solace adapted to your top piece ({invested(row['before'].fort)} > {tr[0][2][0] if tr else '-'}); buy turret + ICE; raid 2 CLEAN, net {row['net']:+d}")
    return img


def f6():
    img, d, row = visit(2)
    fz = ", ".join(f"{a}-{b}" for a, b in row["r"].frozen) or "none"
    header(d, NAME, 6, f"Visit 3 (Heat 76, 4 threats; Lockdown freezes {fz}, drawn cobalt): buy sentry + ICE at the Proxy; raid 3 net {row['net']:+d}")
    return img


def f7():
    row = MINE[-1]
    r = row["r"]
    img, d = new_frame(NAME, "record")
    G4.base(d, r)
    G4.tags(d, r)
    P.jobs_on_map(d, r)
    H.place_fort(d, row["fort"], row["x"]["crew"])
    leg_bar(d, MINE, 3)
    s1 = [START] + [x["after"].bank for x in MINE]
    s2 = [START] + [x["after"].bank for x in PLAN_B]
    H.bank_line(d, 760, 420, 500, 270, [s1, s2], [CELL, DIM])
    strongbox(d, (790, 446), 9)
    G4.record(d, 60, 640, 3, sum(1 for x in MINE if x["r"].clean))
    header(d, NAME, 7, f"Leg record (strongbox = bank): your plan {s1}, plan B (one raid at a time, railguns late) {s2}")
    return img


FRAMES = [f0, f1, f2, f3, f4, f5, f6, f7]

if __name__ == "__main__":
    for nm, rows in (("MINE", MINE), ("PLAN_B", PLAN_B)):
        for row in rows:
            print(nm, [t[0] + (f"/{t[2][0]}" if len(t) > 2 and t[2] else "") for t in row["roster"]],
                  summary(row["r"])[:110], "net", row["net"], "bank", row["after"].bank, "lost", row["after"].lost)
