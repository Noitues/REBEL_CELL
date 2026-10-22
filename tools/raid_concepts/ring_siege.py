"""Pitch 1, RING SIEGE (designer 2026-10-22): the raid is a wheel. Prototype rules (each a designer decision).

Board: HQ is the hub. RINGS concentric rings (outer = ring 0) of the locked anatomy (30 ticks, 6 slices of 5; slice i is
centred on tick 5i). SPOKES fixed pointers at ticks 0 / 10 / 20: each threat comes down its own spoke (its path).
Planning: stock the 18 slice positions from the run's slice pool (the rest are NULL holes) and set each ring's speed
(ticks per beat, -2..+2). Execution (hands-off), per beat:
 1. every ring turns by its speed;
 2. for each spoke, the front threat on its ring faces the slice under the spoke (tick = (rotation + spoke) mod 30;
    precision: offset 0/+-1 = x1.0, +-2 = WEAK x0.5, the combat math of GDD 2.3-2.4):
    SHIM hits it for 4, OVERFLOW for 8 (x precision); DEFRAG blocks its strike this beat (WEAK: halves it);
    DETOUR shunts it to the next spoke clockwise (once per threat; Perfect/Good only); SANDBOX has 20 integrity
    (others 10); NULL or a broken slice lets it bore through to the next ring;
 3. a threat not killed strikes the facing slice (integrity -= damage); at 0 the slice breaks (NULL for the rest of
    the raid);
 4. a threat on the hub strikes home each beat; the hub's gun hits it for 3.
Threats on one spoke queue: only the front one engages. Cap 30 beats; threats still in the rings then retreat
(survivors). Net = 4 salvage per kill + 6 if CLEAN (home untouched) - home loss - 2 per broken slice.
Measurement (python ring_siege.py): on depth_harness's 10 scenarios, 12 independent hill climbs per scenario from
seeded random plans; reports best net, the number of DISTINCT local optima within NEAR of the best (structural
choices: different slice layouts and speeds), and whether the best plans share one shape."""
from __future__ import annotations

import json
import random
import sys
from dataclasses import dataclass, field

sys.path.insert(0, r"D:/Godot/rebel_cell/.claude/worktrees/raid-design-lab-2d2e2e/tools/raid_concepts")
from sim import THREAT_DEF  # noqa: E402
from depth_harness import scenarios  # noqa: E402

RINGS, SLICES, TICKS, SPOKES, CAP = 3, 6, 30, (0, 10, 20), 30
DMG = {"SHIM": 4, "OVERFLOW": 8}
INTEG = {"SANDBOX": 20}
POOL = ["SHIM"] * 5 + ["OVERFLOW"] * 2 + ["DEFRAG"] * 2 + ["SANDBOX"] * 2 + ["DETOUR"]
SPEEDS = (-2, -1, 0, 1, 2)
HUB_GUN, HOME_HP, SALVAGE, BONUS, BREAK_COST, NEAR = 3, 50, 4, 6, 2, 3
SURVIVOR_COST = 0   # round 9 (--survivors): each survivor rejoins the next raid, priced per survivor


@dataclass
class SiegePlan:
    layout: list  # RINGS x SLICES slice types ("NULL" = hole)
    speeds: tuple

    def key(self):
        return (tuple(tuple(r) for r in self.layout), self.speeds)


@dataclass
class SiegeResult:
    beats: list = field(default_factory=list)
    home_after: int = HOME_HP
    kills: list = field(default_factory=list)
    survivors: list = field(default_factory=list)
    broken: int = 0

    @property
    def clean(self):
        return self.home_after == HOME_HP


def facing(rotation: int, spoke: int):
    tick = (rotation + spoke) % TICKS
    idx = round(tick / 5)
    off = tick - 5 * idx
    return idx % SLICES, (0.5 if abs(off) == 2 else 1.0)


def resolve(plan: SiegePlan, roster, brake=None) -> SiegeResult:
    """brake = (beat, ring): round 9's one-press BRAKE: that ring does not turn on that beat."""
    integ = [[INTEG.get(s, 10) if s != "NULL" else 0 for s in ring] for ring in plan.layout]
    kind = [list(r) for r in plan.layout]
    rot = [0] * RINGS
    T = []
    for i, t in enumerate(roster):
        tid = t[0]
        hp, dmg, *_ = THREAT_DEF[tid.split("#")[0]]
        T.append({"id": tid, "hp": hp, "dmg": dmg, "spoke": i % len(SPOKES), "ring": 0, "detoured": False, "order": i})
    res = SiegeResult()
    home = HOME_HP
    for beat in range(1, CAP + 1):
        ev = {"beat": beat, "hits": [], "strikes": [], "moves": [], "kills": [], "rot": None}
        for k in range(RINGS):
            if brake is not None and tuple(brake[:2]) == (beat, k):
                rot[k] = (rot[k] + (brake[2] if len(brake) > 2 else 0)) % TICKS   # (beat, ring[, snap ticks])
            else:
                rot[k] = (rot[k] + plan.speeds[k]) % TICKS
        ev["rot"] = list(rot)
        alive = [t for t in T if t["hp"] > 0 and t["ring"] is not None]
        if not alive:
            break
        # front threat per (spoke, ring): the earliest by order
        fronts = {}
        for t in sorted(alive, key=lambda t: t["order"]):
            fronts.setdefault((t["spoke"], t["ring"]), t)
        for (sp, ring), t in sorted(fronts.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            if ring == RINGS:   # on the hub
                t["hp"] -= HUB_GUN
                ev["hits"].append((t["id"], "HUB", HUB_GUN))
                if t["hp"] <= 0:
                    ev["kills"].append(t["id"])
                    continue
                home = max(0, home - t["dmg"])
                ev["strikes"].append((t["id"], "HOME", t["dmg"]))
                continue
            si, mult = facing(rot[ring], SPOKES[sp])
            s = kind[ring][si]
            if s == "NULL" or integ[ring][si] <= 0:
                t["ring"] = ring + 1
                ev["moves"].append((t["id"], ring, ring + 1))
                continue
            strike = t["dmg"]
            if s in DMG:
                d = int(DMG[s] * mult + 0.5)
                t["hp"] -= d
                ev["hits"].append((t["id"], (ring, si, s), d))
                if t["hp"] <= 0:
                    ev["kills"].append(t["id"])
                    continue
            elif s == "DEFRAG":
                strike = 0 if mult == 1.0 else strike // 2
            elif s == "DETOUR" and mult == 1.0 and not t["detoured"]:
                t["detoured"] = True
                t["spoke"] = (t["spoke"] + 1) % len(SPOKES)
                ev["moves"].append((t["id"], "spoke", t["spoke"]))
                continue
            integ[ring][si] -= strike
            ev["strikes"].append((t["id"], (ring, si, s), strike))
            if integ[ring][si] <= 0:
                kind[ring][si] = "NULL"
                res.broken += 1
        ev["pos"] = [(t["id"], t["spoke"], t["ring"], t["hp"]) for t in T]
        ev["integ"] = [list(r) for r in integ]
        res.beats.append(ev)
        if home <= 0:
            break
    res.home_after = home
    res.kills = [t["id"] for t in T if t["hp"] <= 0]
    res.survivors = [t["id"] for t in T if t["hp"] > 0]
    return res


def net(r: SiegeResult) -> int:
    return (SALVAGE * len(r.kills) + (BONUS if r.clean else 0) - (HOME_HP - r.home_after) - BREAK_COST * r.broken
            - SURVIVOR_COST * len(r.survivors))


def random_plan(rng: random.Random, pool=None) -> SiegePlan:
    pool = pool or POOL
    cells = pool + ["NULL"] * (RINGS * SLICES - len(pool))
    rng.shuffle(cells)
    return SiegePlan([cells[k * SLICES:(k + 1) * SLICES] for k in range(RINGS)], tuple(rng.choice(SPEEDS) for _ in range(RINGS)))


def neighbors(p: SiegePlan):
    flat = [s for r in p.layout for s in r]
    n = len(flat)
    for a in range(n):
        for b in range(a + 1, n):
            if flat[a] != flat[b]:
                f = list(flat)
                f[a], f[b] = f[b], f[a]
                yield SiegePlan([f[k * SLICES:(k + 1) * SLICES] for k in range(RINGS)], p.speeds)
    for k in range(RINGS):
        for s in SPEEDS:
            if s != p.speeds[k]:
                sp = list(p.speeds)
                sp[k] = s
                yield SiegePlan([list(r) for r in p.layout], tuple(sp))


def climb(p: SiegePlan, roster, cache):
    def val(q):
        k = q.key()
        if k not in cache:
            cache[k] = net(resolve(q, roster))
        return cache[k]
    cur, cv = p, val(p)
    while True:
        best, bv = None, cv
        for q in neighbors(cur):
            v = val(q)
            if v > bv:
                best, bv = q, v
        if best is None:
            return cur, cv
        cur, cv = best, bv


def shape(p: SiegePlan) -> tuple:
    """Structural signature: per ring, how many damage / block / hole slices, and its speed."""
    sig = []
    for k, ring in enumerate(p.layout):
        sig.append((sum(s in DMG for s in ring), sum(s in ("DEFRAG", "SANDBOX") for s in ring), ring.count("NULL"), p.speeds[k]))
    return tuple(sig)


if __name__ == "__main__":
    out = []
    for si, sc in enumerate(scenarios()):
        rng = random.Random(100 + si)
        cache: dict = {}
        optima = {}
        for _ in range(12):
            q, v = climb(random_plan(rng), sc, cache)
            optima[q.key()] = (v, q)
        vals = sorted((v for v, _ in optima.values()), reverse=True)
        best = vals[0]
        near = [(v, q) for v, q in optima.values() if v >= best - NEAR]
        shapes = {shape(q) for _, q in near}
        rec = {"threats": sc, "best": best, "optima": len(optima), "near_optima": len(near), "near_shapes": len(shapes),
               "evaluated": len(cache)}
        out.append(rec)
        print(json.dumps(rec), flush=True)
    summ = {"mean_best": round(sum(r["best"] for r in out) / len(out), 1),
            "mean_near_shapes": round(sum(r["near_shapes"] for r in out) / len(out), 2),
            "share_2plus_shapes": sum(r["near_shapes"] >= 2 for r in out) / len(out)}
    print("SUMMARY", summ, flush=True)
    json.dump({"summary": summ, "per": out}, open(r"D:/rc_tmp/raid_design_lab/ring_siege.json", "w"), indent=1)
