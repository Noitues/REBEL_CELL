"""Concept P, round 6: STAKES, what will you give up? (each rule a designer decision)
- Every node has a distinct JOB in the run, drawn on the node:
  VAULT = +3 Schematics per netrun; RELAY = one more branch on each netrun map; SAFEHOUSE = where the crew stations
  (lost: no crew next raid); FIREWALL = home's built-in gun (lost: no gun next raid); PROXY = intel (while it holds,
  the next raid is telegraphed one netrun earlier).
  A DOWN or TAKEN node loses its job until it is repaired or reclaimed.
- Threats that survive the raid fall back to their corp site and JOIN THE NEXT RAID (kills deny reinforcements).
- The forecast does not fold this into one number. It shows the FRONT: the plans that no other plan beats on every count
  at once (home, each job, survivors, patch). Each card says what it gives up. You choose by your run, not by a score.
Numbers: sim.py with the round-5 package; G's plan space (3 of 5, crew); the raid is depth_harness scenario 7
(Collector from C1, Bailiff and Enforcer from C2)."""
from __future__ import annotations

from r2_kit import *  # noqa: F403
from sim import Plan, run, summary

import concept_g3_merged as G3
import concept_g4_merged as G4
import concept_g5_merged as G5
from concept_g4_merged import dial, piece, skull
from depth_harness import CONCEPTS, scenarios

NAME = "P STAKES r6"
MOMENTS = ["1_warning", "2_planning", "3_front", "4_resolution", "5_aftermath", "6_next_raid"]
XF, SHADE, OFF = G3.XF, G3.SHADE, G3.OFF
SCEN = scenarios()[7]
JOBS = ["VAULT", "RELAY", "SAFE", "FW", "PROXY"]
SPACE, RULE = CONCEPTS["G"]


def survivors(r) -> list[str]:
    dead = {t for ev in r.steps for t, _ in ev["kills"]}
    return [t for t in r.routes if t not in dead]


def lostjobs(r) -> tuple:
    return tuple(k for k in JOBS if r.nodes[k]["outcome"] in ("down", "taken"))


def patch(r) -> int:
    return sum(v["before"] - v["after"] for k, v in r.nodes.items() if v["outcome"] == "scuffed")


def vec(r):
    lv = {"holds": 0, "scuffed": 0, "down": 1, "taken": 2, "breached": 2}
    return tuple([r.home_before - r.home_after] + [lv[r.nodes[k]["outcome"]] for k in JOBS] + [len(survivors(r)), patch(r)])


def build_front():
    seen = {}
    for pick, (place, crew), plan in SPACE(RULE):
        r = run(plan, threats=list(SCEN))
        if r.breached or r.home_after < r.home_before:
            continue
        v = vec(r)
        if v not in seen:
            seen[v] = (pick, place, crew, plan, r)
    vs = list(seen)
    front = [v for v in vs if not any(all(a <= b for a, b in zip(w, v)) and w != v for w in vs)]
    best_per_set = {}
    for v in front:
        pick, place, crew, plan, r = seen[v]
        key = lostjobs(r)
        cand = (len(survivors(r)), patch(r), pick, place)
        if key not in best_per_set or cand < best_per_set[key][0]:
            best_per_set[key] = (cand, pick, plan, r)
    cards = sorted(best_per_set.items(), key=lambda kv: (len(kv[0]), kv[1][0]))
    return front, [(k, pick, plan, r) for k, (c, pick, plan, r) in cards]


FRONT, CARDS = build_front()
BARE = run(Plan({}, "SAFE", dict(RULE)), threats=list(SCEN))
_WANT = [(), ("PROXY",), ("SAFE", "PROXY"), ("VAULT",)]   # a spread: nothing lost / cheap single / free double / a survivors trade
SHOW = [c for w in _WANT for c in CARDS if c[0] == w] or CARDS[:4]
CHOSEN = 1 if len(SHOW) > 1 else 0


# ---------- glyphs ----------
def eye(d, c, r, col=INK) -> None:
    x, y = c
    d.ellipse((x - r, y - r * 0.55, x + r, y + r * 0.55), outline=col, width=2)
    d.ellipse((x - r * 0.3, y - r * 0.3, x + r * 0.3, y + r * 0.3), fill=col)


def job_icon(d, c, k: str, r=9, col=INK, struck=False) -> None:
    x, y = c
    if k == "VAULT":
        coin(d, c, r * 0.8, col)
        text(d, (x + r, y - r), "+3", int(r * 1.3), col, "mono")
    elif k == "RELAY":
        G4.netrun_hex(d, c, r, col)
        text(d, (x + r, y - r), "+1", int(r * 1.3), col, "mono")
    elif k == "SAFE":
        asset_icon(d, c, "CREW", r, col)
    elif k == "FW":
        piece(d, c, "TURRET", r * 0.9, col)
    elif k == "PROXY":
        eye(d, c, r, col)
    if struck:
        d.line([(x - r - 2, y + r + 2), (x + r + 2, y - r - 2)], fill=DMG, width=3)


def jobs_on_map(d, r=None) -> None:
    for k in JOBS:
        x, y = XF.p(k)
        lost_ = r is not None and r.nodes[k]["outcome"] in ("down", "taken")
        d.rounded_rectangle((x + 26, y - 50, x + 74, y - 26), radius=5, fill=BG2, outline=DMG if lost_ else PANEL_EDGE, width=2)
        job_icon(d, (x + 40, y - 38), k, 8, DIM if lost_ else INK, struck=lost_)


def survivor_chips(d, x, y, r, scale=0.45, gap=56) -> None:
    for i, t in enumerate(survivors(r)):
        threat_chip(d, (x + i * gap, y), t, scale=scale)
        arrow(d, (x + i * gap + 14, y + 22), (x + i * gap + 24, y + 34), THREAT, 2, 6, shorten=0)


def plan_card(d, x, y, lost_, pick, r, on=False, w=300, h=170) -> None:
    d.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=(50, 46, 30) if on else PANEL,
                        outline=CELL if on else PANEL_EDGE, width=3 if on else 2)
    for i, a in enumerate(pick):
        piece(d, (x + 24 + i * 30, y + 22), a, 9)
    if not lost_:
        check(d, (x + w - 24, y + 22), 8, STAMP_CLEAN)
    # what it gives up: the jobs, struck
    for i, k in enumerate(JOBS):
        job_icon(d, (x + 28 + i * 54, y + 66), k, 10, DIM if k in lost_ else INK, struck=k in lost_)
    # who comes back next raid
    sv = survivors(r)
    if sv:
        for i, t in enumerate(sv):
            threat(d, (x + 28 + i * 34, y + 118), t, 10, show_hp=False)
        arrow(d, (x + 30 + len(sv) * 34, y + 118), (x + 66 + len(sv) * 34, y + 118), THREAT, 3, 8, shorten=0)
        G4.netrun_hex(d, (x + 82 + len(sv) * 34, y + 118), 9, THREAT)
    else:
        # nobody comes back: an empty return arrow into the next raid's hex
        threat(d, (x + 28, y + 118), "COLLECTOR", 10, show_hp=False, ghost=True)
        pencil_x(d, (x + 28, y + 118), 12, seed=5)
        arrow(d, (x + 46, y + 118), (x + 82, y + 118), DIM, 3, 8, shorten=0)
        G4.netrun_hex(d, (x + 98, y + 118), 9, DIM)
    coin(d, (x + w - 70, y + 146), 9)
    text(d, (x + w - 56, y + 134), f"-{patch(r)}", 20, INK, "mono")


# ---------- frames ----------
def f1():
    img, d = new_frame(NAME, "warning")
    G4.base(d, BARE)
    heat_bar(d, 470, 22, 340, 51)
    dial(d, (70, 70), 2)
    G5.routes(d, BARE)
    G4.tags(d, BARE)
    jobs_on_map(d, BARE)
    panel(d, (930, 110, 1268, 300))
    for i, (t, e) in enumerate(SCEN):
        threat_chip(d, (980 + i * 100, 170), t, scale=0.7)
    header(d, NAME, 1, f"Warning: every node shows its job (Vault +3/netrun, Relay +1 branch, Safehouse = crew, Firewall gun, Proxy intel); the raid as it stands loses {', '.join(lostjobs(BARE)) or 'nothing'}")
    return img


def f2():
    lost_, pick, plan, r = SHOW[0]
    img, d = new_frame(NAME, "planning")
    G4.base(d, r)
    heat_bar(d, 470, 22, 340, 51)
    dial(d, (70, 70), 2)
    G5.routes(d, r)
    G4.tags(d, r)
    jobs_on_map(d, r)
    G4.place_assets(d, plan)
    panel(d, (250, 520, 1030, 704), edge=CELL)
    for i, a in enumerate(G4.POOL):
        G4.card(d, 266 + i * 116, 536, a, sel=a in pick, preview=False, h=100)
    header(d, NAME, 2, f"Planning: draft 3 of 5 and place; the map shows which jobs hold; {len(FRONT)} plans sit on the front for this raid")
    return img


def f3():
    img, d = new_frame(NAME, "front")
    heat_bar(d, 470, 22, 340, 51)
    dial(d, (70, 70), 2)
    for i, (lost_, pick, plan, r) in enumerate(SHOW):
        x = 20 + (i % 2) * 320
        y = 120 + (i // 2) * 190
        plan_card(d, x, y, lost_, pick, r, on=i == CHOSEN)
        text(d, (x + 10, y - 2), str(i + 1), 20, CELL if i == CHOSEN else DIM, "mono")
    lost_, pick, plan, r = SHOW[CHOSEN]
    mini = MapXf(700, 110, 0.62)
    draw_links(d, mini)
    for k in NODES:
        node(d, mini, k, "down" if k in lost_ else "ok", show_hp=False)
    button(d, (1060, 640, 1268, 690), "START RAID")
    desc = "; ".join(f"{i + 1}: gives up {', '.join(l) or 'nothing'}, {len(survivors(rr))} return, patch {patch(rr)}" for i, (l, p_, pl, rr) in enumerate(SHOW))
    header(d, NAME, 3, f"The front (no plan beats another on every count): {desc}")
    return img


def f4():
    lost_, pick, plan, r = SHOW[CHOSEN]
    img, d = new_frame(NAME, "resolution")
    s = min(2, len(r.steps))
    G4.base(d, r, step=s)
    heat_bar(d, 470, 22, 340, 51)
    G5.routes(d, r, faint=True)
    G4.place_assets(d, plan)
    jobs_on_map(d)
    ev = r.steps[s - 1]
    for tid, (site, hp, alive, hold) in ev["threats"].items():
        dead = any(k[0] == tid for k in ev["kills"])
        if not alive and not dead:
            continue
        x, y = XF.p(site)
        p = (x + 44, y - 8 + OFF.get(tid, 0) * 3)
        threat(d, p, tid, 15, hp=hp, ghost=dead)
        if dead:
            pencil_x(d, p, 16, seed=4)
    speed_controls(d, 1060, 660)
    header(d, NAME, 4, f"Resolution, no input: plan {CHOSEN + 1} plays out (step {s} of {len(r.steps)})")
    return img


def f5():
    lost_, pick, plan, r = SHOW[CHOSEN]
    img, d = new_frame(NAME, "aftermath")
    G4.base(d, r)
    heat_bar(d, 470, 22, 340, 51, raid_at=None)
    G4.tags(d, r)
    jobs_on_map(d, r)
    G5.stamp_box(img, d, (1010, 150), r)
    panel(d, (20, 520, 1268, 704))
    for i, k in enumerate(JOBS):
        x = 50 + i * 160
        node_icon(d, (x, 560), k, 30, DOWN_GREY if k in lost_ else CELL)
        job_icon(d, (x + 46, 560), k, 10, DIM if k in lost_ else INK, struck=k in lost_)
    survivor_chips(d, 70, 640, r)
    coin(d, (1100, 640), 10)
    text(d, (1116, 628), f"-{patch(r)}", 22, INK, "mono")
    sv = survivors(r)
    header(d, NAME, 5, f"Aftermath: jobs lost until repaired: {', '.join(lost_) or 'none'}; {len(sv)} threat(s) fall back to their corp site and join the next raid")
    return img


def f6():
    lost_, pick, plan, r = SHOW[CHOSEN]
    img, d = new_frame(NAME, "next raid")
    G4.base(d)
    heat_bar(d, 470, 22, 340, 76, raid_at=75)
    why_chain(d, 560, 52, 76, 75)
    proxy_ok = "PROXY" not in lost_
    dial(d, (70, 70), 3 if proxy_ok else 2, of=3)
    eye(d, (70, 150), 12, INK if proxy_ok else DIM)
    if not proxy_ok:
        d.line([(56, 162), (84, 138)], fill=DMG, width=3)
    jobs_on_map(d, r)
    panel(d, (900, 110, 1268, 330))
    for i, t in enumerate(survivors(r)):
        threat_chip(d, (950 + i * 90, 170), t, scale=0.7)
        G4.netrun_hex(d, (950 + i * 90, 230), 8, THREAT)
    for i, t in enumerate(("COURIER", "INSPECTOR")):
        threat_chip(d, (950 + i * 90, 280), t, scale=0.6)
    # inset: the same next raid after plan 4 (it let threats live)
    l4, p4, pl4, r4 = SHOW[-1]
    panel(d, (900, 350, 1268, 470), edge=PANEL_EDGE)
    text(d, (912, 356), str(len(SHOW)), 20, DIM, "mono")
    for i, t in enumerate(survivors(r4) + ["COURIER", "INSPECTOR"]):
        threat_chip(d, (950 + i * 76, 420), t, scale=0.5)
    header(d, NAME, 6, f"Next raid: survivors ({', '.join(survivors(r)) or 'none'}) rejoin the Heat-75 roster; the dial starts at {3 if proxy_ok else 2} because PROXY {'held' if proxy_ok else 'fell'} (intel); inset: after plan {len(SHOW)}, {len(survivors(SHOW[-1][3]))} survivors rejoin")
    return img


FRAMES = [f1, f2, f3, f4, f5, f6]

if __name__ == "__main__":
    print("BARE", summary(BARE), lostjobs(BARE), survivors(BARE))
    print("front", len(FRONT))
    for lost_, pick, plan, r in CARDS:
        print(lost_, pick, plan.assets, plan.crew, "survivors", survivors(r), "patch", patch(r))
