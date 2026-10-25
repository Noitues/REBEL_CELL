"""Concept C round 3: the duel rule with the 3-of-5 draft (prototype only; one function, used by every frame).

ATK = strikes x damage along each threat's declared (fixed) path: 1 strike on each node passed, 3 on the target.
Bonus: FW gun +3; TURRET +8 on its node; SENTRY +6 on its node; RAILGUN +8 on the biggest banner within 2 hops;
CREW +3 on its node and each neighbour; ICE cancels the biggest single strike at its node; DECOY sends the Collector
to the decoy node instead of home. loss = max(0, ATK - bonus): 0 HOLDS, < integrity SCUFFED, >= integrity DOWN,
>= 2 x integrity TAKEN; home loses `loss` (0 = BREACHED). CLEAN = home loss 0 and nothing DOWN or TAKEN.
"""
from __future__ import annotations

NODE_HP = {"HOME": 50, "FW": 30, "VAULT": 20, "SAFE": 20, "RELAY": 15, "PROXY": 15}
LINKS = [("HOME", "FW"), ("HOME", "VAULT"), ("HOME", "SAFE"), ("FW", "RELAY"), ("VAULT", "RELAY"),
         ("VAULT", "PROXY"), ("SAFE", "PROXY"), ("RELAY", "C1"), ("PROXY", "C2")]
ADJ: dict[str, set] = {}
for a, b in LINKS:
    ADJ.setdefault(a, set()).add(b)
    ADJ.setdefault(b, set()).add(a)
DMG = {"COLLECTOR": 5, "AUDITOR": 3, "ENFORCER": 9}
DECL = {"COLLECTOR": ["C1", "RELAY", "VAULT", "HOME"], "AUDITOR": ["C2", "PROXY", "VAULT"], "ENFORCER": ["C2", "PROXY"]}
POOL = ["TURRET", "ICE", "DECOY", "SENTRY", "RAILGUN"]


def hops(a: str, b: str) -> int:
    seen, q = {a: 0}, [a]
    while q:
        n = q.pop(0)
        for m in ADJ[n]:
            if m not in seen:
                seen[m] = seen[n] + 1
                q.append(m)
    return seen.get(b, 99)


def duel(pieces: dict[str, str], crew: str | None) -> dict:
    """pieces: piece -> node. Returns node -> banner."""
    decl = {k: list(v) for k, v in DECL.items()}
    if "DECOY" in pieces:
        dn = pieces["DECOY"]
        if dn in ("RELAY", "VAULT", "FW"):
            decl["COLLECTOR"] = ["C1", "RELAY"] + ([dn] if dn != "RELAY" else [])
    atk: dict[str, list] = {}
    for tid, path in decl.items():
        for i, n in enumerate(path[1:], 1):
            atk.setdefault(n, []).append((tid, 3 if i == len(path) - 1 else 1, DMG[tid]))
    out = {}
    for n, lines in atk.items():
        bonus = []
        if n == "FW":
            bonus.append(("FWGUN", 3))
        if pieces.get("TURRET") == n:
            bonus.append(("TURRET", 8))
        if pieces.get("SENTRY") == n:
            bonus.append(("SENTRY", 6))
        if crew and (crew == n or n in ADJ[crew]):
            bonus.append(("CREW", 3))
        a = sum(s * d for _, s, d in lines)
        if pieces.get("ICE") == n:
            big = max(d for _, _, d in lines)
            a -= big
            bonus.append(("ICE", -big))
        out[n] = {"lines": lines, "bonus": bonus, "atk": a}
    if "RAILGUN" in pieces:
        rn = pieces["RAILGUN"]
        inreach = [n for n in out if hops(rn, n) <= 2]
        if inreach:
            tgt = max(inreach, key=lambda n: (out[n]["atk"], n))
            out[tgt]["bonus"].append(("RAILGUN", 8))
    for n, b in out.items():
        bon = sum(v for k, v in b["bonus"] if k != "ICE")
        integ = NODE_HP[n]
        loss = max(0, b["atk"] - bon)
        if n == "HOME":
            o = "breached" if loss >= integ else ("scuffed" if loss else "holds")
        else:
            o = "taken" if loss >= 2 * integ else ("down" if loss >= integ else ("scuffed" if loss else "holds"))
        b.update({"def": integ + bon, "loss": loss, "outcome": o, "margin": integ + bon - b["atk"], "before": integ,
                  "after": max(0, integ - loss)})
    return out


def clean(res: dict) -> bool:
    return res.get("HOME", {"loss": 0})["loss"] == 0 and not any(b["outcome"] in ("down", "taken", "breached") for b in res.values())


def price(res: dict) -> int:
    return sum(b["loss"] for b in res.values() if b["outcome"] == "scuffed")


if __name__ == "__main__":
    import itertools
    nodes = list(NODE_HP)
    rows = []
    for pick in itertools.combinations(POOL, 3):
        for place in itertools.product(nodes, repeat=3):
            pieces = dict(zip(pick, place))
            for crew in nodes:
                r = duel(pieces, crew)
                lost = sum(1 for b in r.values() if b["outcome"] in ("down", "taken"))
                rows.append((not clean(r), lost, r.get("HOME", {"loss": 0})["loss"], price(r), pick, place, crew))
    rows.sort()
    print("clean", sum(1 for r in rows if not r[0]), "/", len(rows))
    for r in rows[:6]:
        print(r)
    print("bare", {k: (v["atk"], v["def"], v["outcome"]) for k, v in duel({}, None).items()})
