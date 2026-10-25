"""Concept S, round 9: THE SPINNER (the designer's ring idea, pitch 1 Ring Siege) with one BRAKE press. Each rule is a
designer decision (rules in ring_siege.py, press in ring_brake.py):
- The raid is a wheel. HQ is the hub; 3 concentric rings (outer to inner) of the locked anatomy (30 ticks, 6 slices of
  5) are the defense layers, stocked from the run's slice pool (SHIM, OVERFLOW hit; DEFRAG, SANDBOX absorb; DETOUR
  shunts to the next spoke; NULL is a hole).
- Each corp entry is a SPOKE (ticks 0 / 10 / 20): its threats queue on the rim there and bore inward one ring at a time.
- Each ring turns at its own speed (-2..+2 ticks a beat, chevrons). The slice under a spoke strikes the front threat
  (GDD 2.3 precision: offset 0/+-1 full, +-2 WEAK half); a slice that takes its integrity in strikes breaks.
- The forecast is the game's own tick math: per threat, each contact as (ring, beat, slice, damage) and its fate.
- ONE SNAP per raid (one input, breaks zero-input execution): press during the playout to jump one ring a slice
  (+-5 ticks) on that beat. The pool is scarce (9 slices for 18 positions), so the plan cannot cover every spoke. The plan names the press it intends; the forecast shows landed and missed.
- Net = 4 per kill + 6 if CLEAN - home loss - 2 per broken slice; broken slices stay broken until restocked.
Every number is ring_siege.py output."""
from __future__ import annotations

import math
import random

from r2_kit import *  # noqa: F403
from concept_h7_bastion import signed_coin
import ring_siege as RS
from depth_harness import scenarios
from ring_brake import POOL9

NAME = "S9 SPINNER r9"
MOMENTS = ["1_warning", "2_stock", "3_forecast", "4_playout", "5_aftermath", "6_next"]
SCENARIO = 6
RS.SURVIVOR_COST = 3   # survivors rejoin the next raid (ring_brake --survivors)
SNAPS = [(b, k, dt) for b in range(1, RS.CAP + 1) for k in range(RS.RINGS) for dt in (-5, 5)]
SC = scenarios()[SCENARIO] + [("BAILIFF", "C1"), ("HAULER", "C2"), ("ENFORCER#2", "C1")]


def _best():
    rng = random.Random(300 + SCENARIO)
    cache: dict = {}
    best = None
    for _ in range(8):
        q, v = RS.climb(RS.random_plan(rng, POOL9), SC, cache)
        if best is None or v > best[1]:
            best = (q, v)
    return best


PLAN, NOBRAKE = _best()
_bb = sorted(((RS.net(RS.resolve(PLAN, SC, br)), br) for br in SNAPS), key=lambda x: -x[0])
BRAKE = _bb[0][1]
PRESS_OPTIONS = sum(1 for v, _ in _bb if v >= _bb[0][0] - 1)
LANDED = RS.resolve(PLAN, SC, BRAKE)
MISSED = RS.resolve(PLAN, SC)
CX, CY = 380, 404
RAD = [(250, 198), (190, 138), (130, 80)]   # ring k: outer, inner radius
HUB = 70
SPOKE_ANG = {0: -90, 10: 30, 20: 150}
SLICE_COL = {"SHIM": (255, 210, 63), "OVERFLOW": (255, 150, 40), "DEFRAG": (90, 220, 200), "SANDBOX": (60, 170, 160),
             "DETOUR": (190, 140, 255), "NULL": (22, 24, 40)}


def ang(tick):
    return -90 + tick * 12


def pol(r, a):
    return CX + r * math.cos(math.radians(a)), CY + r * math.sin(math.radians(a))


def slice_glyph(d, c, kind, r=11):
    x, y = c
    if kind == "SHIM":
        bolt(d, c, r, BG)
    elif kind == "OVERFLOW":
        bolt(d, (x - r * 0.5, y), r * 0.9, BG)
        bolt(d, (x + r * 0.5, y), r * 0.9, BG)
    elif kind == "DEFRAG":
        d.polygon([(x - r, y - r), (x + r, y - r), (x + r, y), (x, y + r * 1.3), (x - r, y)], outline=BG, width=3)
    elif kind == "SANDBOX":
        d.rectangle((x - r, y - r, x + r, y + r), outline=BG, width=4)
    elif kind == "DETOUR":
        d.arc((x - r, y - r, x + r, y + r), 180, 450, fill=BG, width=3)
        d.polygon([(x + r, y - 4), (x + r + 6, y + 4), (x + r - 6, y + 4)], fill=BG)


def wheel(d, layout, rot, integ=None, broken=(), stocked=None):
    for k, (ro, ri) in enumerate(RAD):
        for i, kind in enumerate(layout[k]):
            if stocked is not None and (k, i) not in stocked:
                kind = "NULL"
            t0 = 5 * i - rot[k] - 2.5
            a0, a1 = ang(t0), ang(t0 + 5)
            col = SLICE_COL[kind]
            dead = (k, i) in broken or (integ is not None and kind != "NULL" and integ[k][i] <= 0)
            if dead:
                col = (60, 30, 36)
            d.pieslice((CX - ro, CY - ro, CX + ro, CY + ro), a0, a1, fill=col, outline=BG, width=3)
            d.pieslice((CX - ri, CY - ri, CX + ri, CY + ri), a0, a1, fill=BG)
            if kind != "NULL" and not dead:
                slice_glyph(d, pol((ro + ri) / 2, (a0 + a1) / 2), kind)
            if dead:
                pencil_x(d, pol((ro + ri) / 2, (a0 + a1) / 2), 14, DMG)
        for t in range(30):
            a = ang(t - rot[k])
            d.line([pol(ro - 4, a), pol(ro, a)], fill=BG, width=1)
    d.ellipse((CX - HUB, CY - HUB, CX + HUB, CY + HUB), fill=PANEL, outline=CELL, width=4)
    node_icon(d, (CX, CY), "HOME", 26, CELL)
    for tick, a in SPOKE_ANG.items():
        d.line([pol(HUB, a), pol(276, a)], fill=THREAT_LIGHT, width=2)
        p = pol(318, a)
        d.polygon([pol(254, a), pol(272, a - 4), pol(272, a + 4)], fill=THREAT_LIGHT)


def speeds(d, plan):
    for k, (ro, ri) in enumerate(RAD):
        s = plan.speeds[k]
        a = -48 + k * 7
        for j in range(abs(s)):
            c = pol((ro + ri) / 2, a + (j * 6 if s > 0 else -j * 6))
            dirn = 1 if s > 0 else -1
            x, y = c
            d.polygon([(x - 6 * dirn, y - 7), (x + 6 * dirn, y), (x - 6 * dirn, y + 7)], fill=INK)
        if s == 0:
            x, y = pol((ro + ri) / 2, a)
            d.rectangle((x - 6, y - 6, x + 6, y + 6), outline=INK, width=2)


def queues(d, pos=None):
    """Threats on the rim (queued) or on their ring; pos = (id, spoke, ring, hp) per threat."""
    if pos is None:
        pos = [(t[0], i % 3, 0, None) for i, t in enumerate(SC)]
    slots: dict = {}
    for tid, sp, ring, hp in pos:
        if hp is not None and hp <= 0:
            continue
        a = SPOKE_ANG[RS.SPOKES[sp]]
        n = slots.get((sp, ring), 0)
        slots[(sp, ring)] = n + 1
        if ring == RS.RINGS:
            r = HUB + 14 + n * 30
        elif hp is None or n > 0 or ring == 0:
            r = (RAD[ring][0] + 30 + n * 34) if ring == 0 else (RAD[ring][0] + RAD[ring][1]) / 2
        else:
            r = (RAD[ring][0] + RAD[ring][1]) / 2
        threat(d, pol(r, a + (0 if n == 0 or ring == 0 else 8 * n)), tid.split("#")[0], 15, hp=hp, show_hp=hp is not None)


def rejoin(d, c, r=9, col=THREAT_LIGHT):
    """A survivor: it retreats and rejoins the next raid (a U-turn arrow)."""
    x, y = c
    d.arc((x - r, y - r, x + r, y + r), 180, 360, fill=col, width=3)
    d.line([(x - r, y), (x - r, y + r)], fill=col, width=3)
    d.polygon([(x + r - 5, y), (x + r + 5, y), (x + r, y + 7)], fill=col)


def contacts(res):
    out = {}
    for ev in res.beats:
        for tid, where, dmg in ev["hits"]:
            out.setdefault(tid, []).append(("hit", ev["beat"], where, dmg))
        for tid, where, dmg in ev["strikes"]:
            out.setdefault(tid, []).append(("strike", ev["beat"], where, dmg))
    return out


def forecast_panel(d, x, y, res, title):
    panel(d, (x, y, x + 520, y + 300))
    text(d, (x + 14, y + 10), title, 15, DIM)
    cs = contacts(res)
    for row, (tid, *_r) in enumerate(SC):
        yy = y + 44 + row * 40
        threat(d, (x + 30, yy + 10), tid.split("#")[0], 12, show_hp=False)
        xx = x + 60
        for kind, beat, where, dmg in [c for c in cs.get(tid, []) if c[0] == "hit"][:6]:
            if where == "HUB":
                node_icon(d, (xx + 12, yy + 10), "HOME", 10, CELL)
            else:
                ring, si, s = where
                d.rectangle((xx, yy, xx + 24, yy + 20), fill=SLICE_COL[s])
                text(d, (xx + 3, yy + 22), f"{ring + 1}", 11, DIM, "mono")
            text(d, (xx + 27, yy + 2), f"{dmg}", 14, INK, "mono")
            xx += 52
        dead = tid in res.kills
        if dead:
            pencil_x(d, (x + 495, yy + 10), 11, STAMP_CLEAN)
        elif any(t == tid for t, *_ in []) or res.home_after < RS.HOME_HP and tid not in res.survivors:
            node_icon(d, (x + 495, yy + 10), "HOME", 11, DMG)
        else:
            rejoin(d, (x + 495, yy + 10))


def brake_mark(d, br, col=CELL):
    beat, k = br[0], br[1]
    ro, ri = RAD[k]
    x, y = pol((ro + ri) / 2, -132)
    d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=col)
    d.rectangle((x - 7, y - 7, x - 2, y + 7), fill=BG)
    d.rectangle((x + 2, y - 7, x + 7, y + 7), fill=BG)
    text(d, (x + 20, y - 10), f"{beat}", 17, col, "mono")


def rot_at(plan, beat, br=None):
    rot = [0] * RS.RINGS
    for b in range(1, beat + 1):
        for k in range(RS.RINGS):
            if br is not None and (br[0], br[1]) == (b, k):
                rot[k] = (rot[k] + br[2]) % RS.TICKS
            else:
                rot[k] = (rot[k] + plan.speeds[k]) % RS.TICKS
    return rot


def _top(d, heat=51):
    heat_bar(d, 60, 24, 420, heat)


# ---------- frames ----------
def f1():
    img, d = new_frame(NAME, "warning")
    _top(d)
    wheel(d, PLAN.layout, [0, 0, 0], stocked=set())
    queues(d)
    panel(d, (760, 90, 1240, 420))
    text(d, (780, 104), "INBOUND", 15, DIM)
    for i, (tid, _e) in enumerate(SC):
        sp = i % 3
        threat(d, (800 + (i // 3) * 220, 160 + (i % 3) * 80), tid.split("#")[0], 18)
        disc(d, (860 + (i // 3) * 220, 150 + (i % 3) * 80), sp + 1, THREAT)
    header(d, NAME, 1, f"Heat 51 crossed 50: {len(SC)} threats queue on 3 spokes (cobalt discs = spoke); the wheel is empty")
    return img


def f2():
    img, d = new_frame(NAME, "stock")
    _top(d)
    half = {(k, i) for k in range(RS.RINGS) for i in range(RS.SLICES) if k == 0 or i < 3}
    wheel(d, PLAN.layout, [0, 0, 0], stocked=half)
    speeds(d, PLAN)
    queues(d)
    panel(d, (760, 90, 1240, 420))
    text(d, (780, 104), "POOL", 15, DIM)
    left = [s for k in range(RS.RINGS) for i, s in enumerate(PLAN.layout[k]) if (k, i) not in half and s != "NULL"]
    for j, s in enumerate(left):
        x, y = 800 + (j % 6) * 70, 160 + (j // 6) * 80
        d.rounded_rectangle((x - 24, y - 24, x + 24, y + 24), radius=6, fill=SLICE_COL[s])
        slice_glyph(d, (x, y), s)
    header(d, NAME, 2, "Stock: drag slices from the pool onto rings; set each ring's speed (chevrons, -2..+2)")
    return img


def f3():
    img, d = new_frame(NAME, "forecast")
    _top(d)
    wheel(d, PLAN.layout, [0, 0, 0])
    speeds(d, PLAN)
    queues(d)
    brake_mark(d, BRAKE)
    forecast_panel(d, 740, 70, LANDED, "SNAP LANDED")
    panel(d, (740, 390, 1260, 470))
    signed_coin(d, (770, 410), RS.net(LANDED), 30)
    text(d, (900, 414), "vs", 22, DIM)
    signed_coin(d, (960, 410), RS.net(MISSED), 30)
    text(d, (1090, 414), "missed", 16, DIM)
    header(d, NAME, 3, f"Forecast (exact tick math): each threat's contacts (ring, damage) and fate; snap ring {BRAKE[1] + 1} on beat {BRAKE[0]}: net {RS.net(LANDED):+d} landed, {RS.net(MISSED):+d} missed")
    return img


def f4():
    img, d = new_frame(NAME, "playout")
    beat = max(1, BRAKE[0])
    ev = LANDED.beats[min(beat, len(LANDED.beats)) - 1]
    wheel(d, PLAN.layout, rot_at(PLAN, beat, BRAKE), integ=ev["integ"])
    speeds(d, PLAN)
    queues(d, ev["pos"])
    brake_mark(d, BRAKE, STAMP_CLEAN)
    step_track(d, 760, 120, 420, min(RS.CAP, len(LANDED.beats)), beat, "BEAT")
    d.rounded_rectangle((760, 200, 1180, 260), radius=10, fill=(40, 44, 70), outline=CELL, width=3)
    d.rectangle((760 + 180, 204, 760 + 240, 256), fill=(90, 220, 200))
    text(d, (970, 214), "SPACE", 22, BG, anchor="ma")
    speed_controls(d, 760, 300)
    header(d, NAME, 4, f"Playout (one press): beat {beat}, the snap window (teal) on ring {BRAKE[1] + 1}; landed = the ring jumps one slice {'back' if BRAKE[2] < 0 else 'ahead'}")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    last = LANDED.beats[-1]
    wheel(d, PLAN.layout, rot_at(PLAN, len(LANDED.beats), BRAKE), integ=last["integ"])
    queues(d, last["pos"])
    ok = LANDED.home_after > 0
    stamp(img, (1000, 170), "CELL HOLDS" if ok else "BREACHED", STAMP_CLEAN if LANDED.clean else STAMP_HOLD if ok else STAMP_BREACH, 56,
          sub="CLEAN" if LANDED.clean else f"HOME -{RS.HOME_HP - LANDED.home_after}")
    signed_coin(d, (930, 300), RS.net(LANDED), 40)
    text(d, (930, 380), f"x{len(LANDED.kills)}", 26, STAMP_CLEAN, "mono")
    pencil_x(d, (900, 394), 12, STAMP_CLEAN)
    text(d, (930, 430), f"x{LANDED.broken}", 26, DMG, "mono")
    pencil_x(d, (900, 444), 12, DMG)
    rejoin(d, (900, 494), 11)
    text(d, (930, 480), f"x{len(LANDED.survivors)}", 26, THREAT_LIGHT, "mono")
    header(d, NAME, 5, f"Aftermath: {len(LANDED.kills)} kills, {len(LANDED.survivors)} survivors rejoin the next raid (-{RS.SURVIVOR_COST} each), {LANDED.broken} slices broken (red X, they stay broken), home {LANDED.home_after}/{RS.HOME_HP}; net {RS.net(LANDED):+d}")
    return img


def f6():
    img, d = new_frame(NAME, "next")
    last = LANDED.beats[-1]
    wheel(d, PLAN.layout, [0, 0, 0], integ=last["integ"])
    panel(d, (760, 90, 1240, 420))
    text(d, (780, 104), "RESTOCK", 15, DIM)
    coin(d, (800, 170), 14)
    text(d, (824, 156), f"{2 * LANDED.broken}", 26, INK, "mono")
    heat_bar(d, 780, 260, 380, 51, raid_at=75)
    header(d, NAME, 6, "Next raid: broken slices stay as holes until restocked (2 each); the next threshold (75) adds a fourth spoke threat")
    return img


FRAMES = [f1, f2, f3, f4, f5, f6]

if __name__ == "__main__":
    print("press options", PRESS_OPTIONS)
    print("plan", PLAN.layout, PLAN.speeds, "nobrake", NOBRAKE, "brake", BRAKE, RS.net(LANDED), RS.net(MISSED))
    print("kills", LANDED.kills, "home", LANDED.home_after, "broken", LANDED.broken, "beats", len(LANDED.beats))
