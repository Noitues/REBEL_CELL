"""Concept D round 3: lane sim with the 3-of-5 draft (prototype only; one rule for every frame).

Lanes tick together, 6 ticks. Per tick: (1) frozen threats skip; (2) pieces fire: TURRET 4 (+2 if a Breaker is on its
node or a map-adjacent node), SENTRY 3 twice, a Breaker in a slot 3, all in their own lane; the RAILGUN fires 8 once at
the highest-damage live threat in any lane whose node is within 2 hops; (3) live, unfrozen threats strike: a Decoy in
the lane soaks the hit while it has integrity (12), else the node takes it. ICE freezes the lane's threat for 2 ticks
(+1 with a boosting Breaker). End: a live threat TAKES its node (home only loses integrity; 0 = BREACHED); a node at 0 is
DOWN. CLEAN = home untouched and nothing DOWN or TAKEN.
"""
from __future__ import annotations

LANES = [("HOME", "COLLECTOR"), ("VAULT", "AUDITOR"), ("PROXY", "ENFORCER")]
HP = {"HOME": 50, "VAULT": 20, "PROXY": 15}
T = {"COLLECTOR": (12, 5), "AUDITOR": (8, 3), "ENFORCER": (25, 9)}
ADJ = {"HOME": {"FW", "VAULT", "SAFE"}, "VAULT": {"HOME", "RELAY", "PROXY"}, "PROXY": {"VAULT", "SAFE", "C2"},
       "FW": {"HOME", "RELAY"}, "SAFE": {"HOME", "PROXY"}, "RELAY": {"FW", "VAULT"}}
HOPS = {("HOME", "VAULT"): 1, ("HOME", "PROXY"): 2, ("VAULT", "PROXY"): 1}
POOL = ["TURRET", "ICE", "DECOY", "SENTRY", "RAILGUN"]
TICKS = 6


def hops(a, b):
    return 0 if a == b else HOPS.get((a, b), HOPS.get((b, a), 9))


def run(slots: dict[str, list[str]]) -> dict:
    crew = next((n for n, v in slots.items() if "CREW" in v), None)
    st = {}
    for n, tid in LANES:
        s = slots.get(n, [])
        boosted = crew is not None and (crew == n or crew in ADJ[n])
        st[n] = {"tid": tid, "thp": T[tid][0], "dmg": T[tid][1], "nhp": HP[n], "frozen": (2 + (1 if boosted else 0)) if "ICE" in s else 0,
                 "decoy": 12 if "DECOY" in s else 0, "boost": boosted, "slots": s, "events": [], "killed_at": None}
    for t in range(1, TICKS + 1):
        for n, L in st.items():
            if L["thp"] <= 0:
                continue
            for p in L["slots"]:
                if p == "TURRET":
                    shots = [4 + (2 if L["boost"] else 0)]
                elif p == "SENTRY":
                    shots = [3, 3]
                elif p == "CREW":
                    shots = [3]
                else:
                    shots = []
                for dmg in shots:
                    if L["thp"] > 0:
                        L["thp"] -= dmg
                        L["events"].append((t, "us", dmg))
            if "RAILGUN" in L["slots"]:
                cands = [m for m, M in st.items() if M["thp"] > 0 and hops(n, m) <= 2]
                if cands:
                    m = max(cands, key=lambda m: (st[m]["dmg"], m))
                    st[m]["thp"] -= 8
                    st[m]["events"].append((t, "rail", 8))
        for n, L in st.items():
            if L["thp"] <= 0:
                if L["killed_at"] is None:
                    L["killed_at"] = t
                    L["events"].append((t, "kill", 0))
                continue
            if L["frozen"] > 0:
                L["frozen"] -= 1
                L["events"].append((t, "frozen", 0))
                continue
            if L["decoy"] > 0:
                L["decoy"] -= L["dmg"]
                L["events"].append((t, "soak", L["dmg"]))
            else:
                L["nhp"] -= L["dmg"]
                L["events"].append((t, "them", L["dmg"]))
    out = {}
    for n, L in st.items():
        if n == "HOME":
            o = "breached" if L["nhp"] <= 0 else ("scuffed" if L["nhp"] < HP[n] else "holds")
        elif L["thp"] > 0:
            o = "taken"
        elif L["nhp"] <= 0:
            o = "down"
        else:
            o = "scuffed" if L["nhp"] < HP[n] else "holds"
        out[n] = {"node": n, "tid": L["tid"], "events": L["events"], "node_after": max(0, L["nhp"]),
                  "threat_after": max(0, L["thp"]), "outcome": o, "decoy_after": max(0, L["decoy"]) if "DECOY" in L["slots"] else None}
    return out


def clean(r):
    return r["HOME"]["node_after"] == HP["HOME"] and not any(v["outcome"] in ("down", "taken") for v in r.values())


def price(r):
    return sum(HP[n] - v["node_after"] for n, v in r.items() if v["outcome"] == "scuffed")


if __name__ == "__main__":
    import itertools
    rows = []
    for pick in itertools.combinations(POOL, 3):
        for place in itertools.product(["HOME", "VAULT", "PROXY"], repeat=4):
            slots = {}
            for p, n in zip(pick + ("CREW",), place):
                slots.setdefault(n, []).append(p)
            if any(len(v) > 2 for v in slots.values()):
                continue
            r = run(slots)
            lost = sum(1 for v in r.values() if v["outcome"] in ("down", "taken"))
            rows.append((not clean(r), lost, HP["HOME"] - r["HOME"]["node_after"], price(r), pick, slots))
    rows.sort(key=lambda x: x[:4])
    print("clean", sum(1 for r in rows if not r[0]), "/", len(rows))
    for r in rows[:8]:
        print(r)
