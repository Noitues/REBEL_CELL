"""Concept D round 2: the lane sim (auto-battler rules, consistent; prototype only).

Lanes: each threat fights the node it targets. Per tick (1..6): frozen threats skip; our guns fire (turret 4, +2 if a
Breaker is on that node or a map-adjacent node; the Firewall's own gun 3); then a live, unfrozen threat strikes: a
Decoy in the lane soaks the hit while it has integrity, else the node loses the damage. ICE freezes the threat for
2 ticks from tick 1 (+1 with a Breaker on or next to the node). A Breaker slotted in a lane also fights (3 a tick).
End: a threat still alive TAKES the node (home: it only loses integrity; 0 = BREACHED); a node at 0 is DOWN.
"""
from __future__ import annotations

LANES = [("HOME", "COLLECTOR"), ("VAULT", "AUDITOR"), ("PROXY", "ENFORCER")]
HP = {"HOME": 50, "VAULT": 20, "PROXY": 15}
T = {"COLLECTOR": (12, 5), "AUDITOR": (8, 3), "ENFORCER": (25, 9)}
ADJ = {"HOME": {"FW", "VAULT", "SAFE"}, "VAULT": {"HOME", "RELAY", "PROXY"}, "PROXY": {"VAULT", "SAFE", "C2"}}
TICKS = 6


def lane(node: str, tid: str, slots: list[str], crew_at: str | None) -> dict:
    thp, dmg = T[tid]
    nhp = HP[node]
    boosted = crew_at is not None and (crew_at == node or crew_at in ADJ[node])
    frozen = 0
    decoy = 12 if "DECOY" in slots else 0
    if "ICE" in slots:
        frozen = 2 + (1 if boosted else 0)
    ev = []
    for t in range(1, TICKS + 1):
        if thp <= 0:
            break
        for s in slots:
            if s in ("TURRET", "CREW"):
                d = 4 + (2 if boosted and s == "TURRET" else 0) if s == "TURRET" else 3
                thp -= d
                ev.append((t, "us", d))
        if thp <= 0:
            ev.append((t, "kill", 0))
            break
        if frozen > 0:
            frozen -= 1
            ev.append((t, "frozen", 0))
            continue
        if decoy > 0:
            decoy -= dmg
            ev.append((t, "soak", dmg))
        else:
            nhp -= dmg
            ev.append((t, "them", dmg))
    if node == "HOME":
        out = "breached" if nhp <= 0 else ("scuffed" if nhp < HP[node] else "holds")
    elif thp > 0:
        out = "taken"
    elif nhp <= 0:
        out = "down"
    elif nhp < HP[node]:
        out = "scuffed"
    else:
        out = "holds"
    return {"node": node, "tid": tid, "events": ev, "node_after": max(0, nhp), "threat_after": max(0, thp), "outcome": out,
            "decoy_after": max(0, decoy) if "DECOY" in slots else None}


def run(slots: dict[str, list[str]], crew_at: str | None) -> dict:
    return {n: lane(n, t, slots.get(n, []), crew_at) for n, t in LANES}


if __name__ == "__main__":
    import itertools
    pieces = ["TURRET", "ICE", "DECOY", "CREW"]
    best = []
    for assign in itertools.product(["HOME", "VAULT", "PROXY", None], repeat=4):
        slots: dict[str, list[str]] = {}
        for p, n in zip(pieces, assign):
            if n:
                slots.setdefault(n, []).append(p)
        if any(len(v) > 2 for v in slots.values()):
            continue
        for crew in (None,):
            crew = next((n for n, v in slots.items() if "CREW" in v), None)
            r = run(slots, crew)
            lost = sum(1 for v in r.values() if v["outcome"] in ("down", "taken"))
            dmg = sum(HP[n] - v["node_after"] for n, v in r.items())
            best.append((lost, dmg, slots, crew, {n: (v["outcome"], v["node_after"]) for n, v in r.items()}))
    best.sort(key=lambda b: (b[0], b[1]))
    for b in best[:10]:
        print(b)
    print("bare", run({}, "SAFE"))
