"""Mockup simulator: a small Python mirror of scripts/core/raid_resolver.gd for the shared lab scenario, so every number a
mockup shows comes from one consistent run (critic R1: "generate mockups from one consistent simulation").

Mirrors per step: threats enter (step 1), move (edges_per_step, stop on a live node or home; DECOY pull overrides the
target; WEAKEST re-evaluated each step), ICE Locks hold (once per lock, delay steps), guns fire (built-in, then deployed;
reach in hops; first-in-path = nearest to home, ties by content id), threats damage their node (home: hit once, threat
spent; a DOWN node hit again is TAKEN; 0 integrity = DOWN, 50 % of the excess cascades to live neighbours). Ends when no
threat is active; threats still on a node at the cap TAKE it. Prototype only: never imported by the game.
"""

from __future__ import annotations

import math

import copy
from dataclasses import dataclass, field

LINKS = [("HOME", "FW"), ("HOME", "VAULT"), ("HOME", "SAFE"), ("FW", "RELAY"), ("VAULT", "RELAY"),
         ("VAULT", "PROXY"), ("SAFE", "PROXY"), ("RELAY", "C1"), ("PROXY", "C2")]
NODE_HP = {"HOME": 50, "FW": 30, "VAULT": 20, "SAFE": 20, "RELAY": 15, "PROXY": 15}
INSTALL = {"FW": 16, "VAULT": 16, "SAFE": 12, "RELAY": 8, "PROXY": 10}   # repair = half
PRIORITY = {"VAULT": 3, "FW": 1, "SAFE": 1, "RELAY": 1, "PROXY": 1}
BUILT_IN = {"FW": [("FWGUN", 3, 0)]}  # name, damage, reach
ASSET = {"TURRET": (4, 1), "ICE": 2, "DECOY": 3}
# Gun stats from content/assets/*.tres: damage, reach (hops), shots per step, targeting (first = nearest home, high = highest damage).
GUNS = {"TURRET": (4, 1, 1, "first"), "SENTRY": (3, 0, 2, "first"), "RAILGUN": (8, 2, 1, "high")}
HOLDERS = {"ICE": 2, "TARPIT": 3}
# Round-3 rule options (each a designer decision; the defaults are today's resolver):
#   avoid_home: a threat whose target is not home never routes through home.
#   tiebreak: "id" (today: alphabetical) or "weakest" (equal-length routes go through the lower-integrity node, then id).
#   target_lock: a threat keeps the target it picked until that target falls (today: re-picked every step).
#   decoy_radius: a decoy pulls only threats within `pull` hops of it (today: every threat that can reach it).
#   ice_blocks: a held threat does not strike (today: it is held but still strikes, except at home).
#   fixed_routes: each threat's target and whole route are set once, when the raid starts (the telegraph IS the route);
#     it walks that route, strikes its target until it is TAKEN, then leaves. No mid-raid re-targeting.
#   plating (round 5, a per-raid corp trait): the Enforcer ignores any single shot of 8 or more (the Railgun's).
#   no_cascade (round 4): a node going DOWN does not spill damage onto its neighbours.
#   auditor_hunts (round 4): the Auditor targets the node holding the most deployed pieces (ties: value, then id),
#     so stacking draws it; with fixed_routes it is decided at plan time and drawn live.
RULES = {"avoid_home": False, "tiebreak": "id", "target_lock": False, "decoy_radius": False, "ice_blocks": False,
         "fixed_routes": False, "no_cascade": False, "auditor_hunts": False}
CREW_MULT = 1.5   # Breaker: assets on its node deal x1.5
STEP_CAP = 30
THREAT_DEF = {  # id: hp, dmg, speed, routing, entry
    "AUDITOR": (8, 3, 2, "value", "C2"),
    "COLLECTOR": (12, 5, 1, "home", "C1"),
    "ENFORCER": (25, 9, 1, "weakest", "C2"),
    # Heat-75 roster adds the Lockdown Unit (content/threats/lockdown_unit.tres): before the raid it freezes the link
    # between home and the home neighbour holding the most deployed assets (ties by id), as RaidResolver._prepare_links.
    "LOCKDOWN": (18, 6, 1, "weakest", "C1"),
}
ROSTER_50 = ["AUDITOR", "COLLECTOR", "ENFORCER"]
ROSTER_75 = ["AUDITOR", "COLLECTOR", "ENFORCER", "LOCKDOWN"]
FROZEN: set = set()   # frozen links for the raid being run (nothing routes or shoots across them)

ADJ: dict[str, list[str]] = {}
for a, b in LINKS:
    ADJ.setdefault(a, []).append(b)
    ADJ.setdefault(b, []).append(a)
for k in ADJ:
    ADJ[k].sort()


def bfs(src: str, blocked=frozenset()) -> dict[str, int]:
    dist = {src: 0}
    q = [src]
    while q:
        n = q.pop(0)
        for m in ADJ[n]:
            if frozenset((n, m)) in FROZEN:
                continue
            if m not in dist and m not in blocked:
                dist[m] = dist[n] + 1
                q.append(m)
    return dist


def next_hop(cur: str, target: str, hp: dict | None = None, rules: dict | None = None) -> str:
    rules = rules or RULES
    blocked = frozenset({"HOME"}) if rules.get("avoid_home") and target != "HOME" and cur != "HOME" else frozenset()
    dt = bfs(target, blocked)
    if cur not in dt:
        dt = bfs(target)
    cands = [m for m in ADJ[cur] if m in dt and dt[m] == dt[cur] - 1]
    if not cands:
        return cur
    if rules.get("tiebreak") == "weakest" and hp is not None:
        cands.sort(key=lambda m: (hp.get(m, 999), m))
    else:
        cands.sort()
    return cands[0]


@dataclass
class Plan:
    assets: dict[str, list[str]] = field(default_factory=dict)   # node -> ["TURRET", "ICE", "DECOY", "SENTRY", ...]
    crew: str | None = "SAFE"                                     # node where the Breaker is stationed
    rules: dict = field(default_factory=lambda: dict(RULES))


@dataclass
class Result:
    steps: list[dict]
    paths: dict
    nodes: dict[str, dict]
    home_before: int
    home_after: int
    killed: list[str]
    reached_home: list[str]
    clean: bool
    breached: bool


def run(plan: Plan, threats=None, start_hp=None) -> Result:
    threats = threats or list(ROSTER_50)
    hp = dict(NODE_HP if start_hp is None else start_hp)
    FROZEN.clear()
    if "LOCKDOWN" in threats:
        nb = sorted(ADJ["HOME"], key=lambda n: (-len(plan.assets.get(n, [])), n))
        FROZEN.add(frozenset(("HOME", nb[0])))
    cond = {k: "ok" for k in hp}
    held_by: dict[str, set] = {t: set() for t in threats}
    T = {}
    for t in threats:
        h, d, s, r, e = THREAT_DEF[t]
        T[t] = {"id": t, "hp": h, "max": h, "dmg": d, "spd": s, "route": r, "site": e, "hold": 0, "home": False, "path": [e]}
    log = []
    down_now, taken_now = [], []
    damaged = set()

    def live(n):
        return n in hp and cond[n] == "ok" and n != "HOME"

    def active():
        return [T[t] for t in sorted(T) if T[t]["hp"] > 0 and not T[t]["home"]]

    def target_of(t):
        if plan.rules.get("target_lock") and t.get("locked") and (live(t["locked"]) or t["locked"] == "HOME"):
            return t["locked"]
        tg = _pick(t)
        t["locked"] = tg
        return tg

    def _pick(t):
        decoys = [n for n, a in plan.assets.items() if "DECOY" in a and live(n)]
        if plan.rules.get("decoy_radius"):
            decoys = [n for n in decoys if bfs(t["site"]).get(n, 99) <= ASSET["DECOY"]]
        if decoys:
            return sorted(decoys)[0]
        if t["route"] == "value" and plan.rules.get("auditor_hunts"):
            def _n(n):
                return len(plan.assets.get(n, [])) + (1 if plan.crew == n else 0)
            c = sorted([n for n in hp if live(n)], key=lambda n: (-_n(n), -PRIORITY[n] * 1000 - INSTALL[n], n))
            return c[0] if c else "HOME"
        if t["route"] == "value":
            c = sorted([n for n in hp if live(n)], key=lambda n: (-PRIORITY[n] * 1000 - INSTALL[n], n))
            return c[0] if c else "HOME"
        if t["route"] == "weakest":
            c = sorted([n for n in hp if live(n)], key=lambda n: (hp[n], n))
            return c[0] if c else "HOME"
        return "HOME"

    step = 0
    while step < STEP_CAP:
        step += 1
        ev = {"step": step, "moves": [], "holds": [], "shots": [], "hits": [], "down": [], "taken": [], "kills": [], "targets": {}}
        if not active():
            step -= 1
            break
        # move
        if step == 1 and plan.rules.get("fixed_routes"):
            for t in active():
                tgt = _pick(t)
                t["locked"] = tgt
                route_ = [t["site"]]
                while route_[-1] != tgt:
                    nx = next_hop(route_[-1], tgt, hp, plan.rules)
                    if nx == route_[-1]:
                        break
                    route_.append(nx)
                t["route_fixed"] = route_
        for t in active():
            if plan.rules.get("fixed_routes"):
                tgt = t["locked"]
                ev["targets"][t["id"]] = tgt
                if tgt != "HOME" and cond.get(tgt) == "taken":
                    t["home"] = True  # its target is already TAKEN: it leaves
                    t["left"] = True
                    continue
                if t["hold"] > 0:
                    t["hold"] -= 1
                    ev["holds"].append((t["id"], t["site"], t["hold"]))
                    continue
                rf = t["route_fixed"]
                i = rf.index(t["site"]) if t["site"] in rf else len(rf) - 1
                frm = t["site"]
                moved = 0
                while moved < t["spd"] and i < len(rf) - 1:
                    i += 1
                    t["site"] = rf[i]
                    t["path"].append(rf[i])
                    moved += 1
                    if rf[i] == "HOME" or live(rf[i]):
                        break
                if moved:
                    ev["moves"].append((t["id"], frm, t["site"]))
                continue
            tgt = target_of(t)
            ev["targets"][t["id"]] = tgt
            if t["hold"] > 0:
                t["hold"] -= 1
                ev["holds"].append((t["id"], t["site"], t["hold"]))
                continue
            if t["site"] == tgt and live(tgt):
                continue
            frm = t["site"]
            moved = 0
            while moved < t["spd"] and t["site"] != tgt:
                nxt = next_hop(t["site"], tgt, hp, plan.rules)
                if nxt == t["site"]:
                    break
                t["site"] = nxt
                t["path"].append(nxt)
                moved += 1
                if nxt == "HOME" or live(nxt):
                    break
            if moved:
                ev["moves"].append((t["id"], frm, t["site"]))
        # hold (ICE on a node holds an arriving threat once)
        for t in active():
            s = t["site"]
            if not (s in hp and (live(s) or s == "HOME")) or t["hold"] > 0:
                continue
            for hname, hsteps in HOLDERS.items():
                key = s + "#" + hname
                if hname in plan.assets.get(s, []) and key not in held_by[t["id"]]:
                    held_by[t["id"]].add(key)
                    t["hold"] = hsteps
                    ev["holds"].append((t["id"], s, t["hold"]))
                    break
        # fire
        for site in sorted(hp):
            if not (live(site) or site == "HOME"):
                continue
            guns = [(n, dm, rc, 1, "first") for n, dm, rc in BUILT_IN.get(site, [])]
            for a in plan.assets.get(site, []):
                if a in GUNS:
                    guns.append((a,) + GUNS[a])
            mult = CREW_MULT if plan.crew == site else 1.0
            dist = bfs(site)
            dh = bfs("HOME")
            for name, dmg, reach, shots, tg in guns:
                for _ in range(shots):
                    cands = [t for t in active() if dist.get(t["site"], 99) <= reach]
                    if not cands:
                        break
                    if tg == "high":
                        cands.sort(key=lambda t: (-t["dmg"], dh.get(t["site"], 99), t["id"]))
                    else:
                        cands.sort(key=lambda t: (dh.get(t["site"], 99), t["id"]))
                    t = cands[0]
                    d = int(math.floor(dmg * mult + 0.5))   # GDScript roundi: halves away from zero
                    if plan.rules.get("plating") and t["id"] == "ENFORCER" and d >= 8:
                        ev["shots"].append((site, name, t["id"], 0, t["hp"]))
                        continue
                    t["hp"] -= d
                    ev["shots"].append((site, name, t["id"], d, max(0, t["hp"])))
                    if t["hp"] <= 0:
                        ev["kills"].append((t["id"], t["site"]))
        # damage
        for t in active():
            s = t["site"]
            if t["hold"] > 0 and plan.rules.get("ice_blocks"):
                continue
            if s == "HOME":
                if t["hold"] > 0:
                    continue
                hp["HOME"] = max(0, hp["HOME"] - t["dmg"])
                t["home"] = True
                ev["hits"].append((t["id"], "HOME", t["dmg"], hp["HOME"]))
                continue
            if s not in hp:
                continue
            if cond[s] == "down":
                cond[s] = "taken"
                taken_now.append(s)
                ev["taken"].append(s)
                if plan.rules.get("fixed_routes"):
                    t["home"] = True  # done: leaves the raid
                    t["left"] = True
                continue
            if cond[s] == "taken":
                continue
            hp[s] -= t["dmg"]
            damaged.add(s)
            ev["hits"].append((t["id"], s, t["dmg"], max(0, hp[s])))
            if hp[s] <= 0:
                excess = -hp[s]
                hp[s] = 0
                cond[s] = "down"
                down_now.append(s)
                ev["down"].append(s)
                c = 0 if plan.rules.get("no_cascade") else int(excess * 0.5)
                for n in ADJ[s]:
                    if c and n in hp and (live(n) or n == "HOME"):
                        hp[n] = max(0, hp[n] - c)
                        ev["hits"].append(("CASCADE", n, c, hp[n]))
                        ev.setdefault("cascades", []).append((s, n, c))
        ev["threats"] = {k: (v["site"], max(0, v["hp"]), v["hp"] > 0 and not v["home"], v["hold"]) for k, v in T.items()}
        ev["hp"] = dict(hp)
        ev["cond"] = dict(cond)
        log.append(ev)
        if hp["HOME"] <= 0:
            break
    for t in active():
        if t["site"] in hp and t["site"] != "HOME" and cond[t["site"]] != "taken":
            cond[t["site"]] = "taken"
            taken_now.append(t["site"])
    nodes = {}
    for k in NODE_HP:
        before = NODE_HP[k] if start_hp is None else start_hp[k]
        out = cond[k] if k != "HOME" else ("breached" if hp["HOME"] <= 0 else "holds")
        if out == "ok":
            out = "scuffed" if hp[k] < before else "holds"
        if k == "HOME" and out == "holds" and hp[k] < before:
            out = "scuffed"
        nodes[k] = {"before": before, "after": hp[k], "outcome": out}
    clean = hp["HOME"] >= (NODE_HP["HOME"] if start_hp is None else start_hp["HOME"]) and not down_now and not taken_now
    res = Result(log, {k: v["path"] for k, v in T.items()}, nodes, NODE_HP["HOME"], hp["HOME"], [t for t in T if T[t]["hp"] <= 0],
                  [t for t in T if T[t]["home"] and not T[t].get("left")], clean, hp["HOME"] <= 0)
    res.routes = {k: v.get("route_fixed", v["path"]) for k, v in T.items()}
    res.frozen = [tuple(sorted(f)) for f in FROZEN]
    return res


def summary(r: Result) -> str:
    parts = [f"{k}:{v['before']}>{v['after']} {v['outcome']}" for k, v in r.nodes.items()]
    return f"steps={len(r.steps)} clean={r.clean} killed={r.killed} home={r.reached_home} | " + " ".join(parts)


if __name__ == "__main__":
    import itertools
    print("BARE", summary(run(Plan())))
    nodes = list(NODE_HP)
    results = []
    for tn, ic, dc in itertools.product(nodes + [None], nodes + [None], nodes[1:] + [None]):
        a: dict[str, list[str]] = {}
        for n, x in ((tn, "TURRET"), (ic, "ICE"), (dc, "DECOY")):
            if n:
                a.setdefault(n, []).append(x)
        for crew in ("SAFE", None):
            r = run(Plan(a, crew))
            score = (r.clean, -sum(1 for v in r.nodes.values() if v["outcome"] in ("down", "taken")), r.home_after)
            results.append((score, tn, ic, dc, crew, summary(r)))
    results.sort(key=lambda r: r[0], reverse=True)
    for row in results[:12]:
        print(row[1:5], row[5])
    print("clean plans:", sum(1 for r in results if r[0][0]), "of", len(results))
