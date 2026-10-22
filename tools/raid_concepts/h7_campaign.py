"""Round 7: H7 = Bastion + node jobs + carry + corp adaptation (each rule a designer decision). One campaign leg of 3 raids.

Rules
- The fortress persists. Each HQ visit: buy up to 2 pieces (TURRET 6, SENTRY 7, RAILGUN 10, ICE 5, DECOY 4), place
  them on held nodes, station the crew (only while the SAFEHOUSE holds). The crew adds +2 to each shot from its node.
- Node jobs (lost only when the node is TAKEN; a TAKEN node stays lost for the leg and becomes a corp foothold):
  VAULT +3 income per visit; RELAY +2 income per visit; SAFEHOUSE = the crew can station; FIREWALL = home's gun;
  PROXY = intel: while it holds you see TWO raids ahead, otherwise only the next one.
- Income per visit after the first: BASE_INCOME + jobs.
- Threats that survive a raid (alive at its end) rejoin the next raid ("#n").
- A TAKEN node is a foothold: in later raids, the first threat (by id) of the corp's own roster enters there.
- Corp adaptation, shown when a raid is telegraphed: the raid's toughest threat (most HP, then id) gains the trait that
  counters your most-invested piece type (by total price): RAILGUN > PLATED, TURRET/SENTRY > ARMORED, ICE >
  FROSTPROOF, DECOY > BLIND. Ties by type id.
- Payout: +4 salvage per kill, +6 if CLEAN; repair bill = home loss + SCUFFED points + DOWN at half install; after a
  CLEAN raid, scuffs heal free (so CLEAN never nets negative). TAKEN costs no coins: it costs the node.
- Breach (home 0) ends the leg at BREACH_SCORE.
Measurement (python h7_campaign.py [N]): N seeded legs. Baselines:
- AMORTIZED GREEDY: each visit takes the action with the best (this raid's net + half the price of pieces bought,
  as they persist) - the fair myopic player;
- PLANNED: a beam search on the final bank (the greedy line is kept in the beam, so planned >= greedy).
Reports regret, first-visit divergence, and how often the planned line ends with a different fortress shape than the
greedy one."""
from __future__ import annotations

import itertools
import json
import random
import sys

sys.path.insert(0, r"D:/Godot/rebel_cell/.claude/worktrees/raid-design-lab-2d2e2e/tools/raid_concepts")
from sim import INSTALL, NODE_HP, RULES, Plan, run  # noqa: E402
from depth_harness import PKG, THREAT_POOL  # noqa: E402

COST = {"TURRET": 6, "SENTRY": 7, "RAILGUN": 10, "ICE": 5, "DECOY": 4}
COUNTER = {"RAILGUN": "PLATED", "TURRET": "ARMORED", "SENTRY": "ARMORED", "ICE": "FROSTPROOF", "DECOY": "BLIND"}
START, BASE_INCOME, VAULT_INC, RELAY_INC, BREACH_SCORE, BEAM = 14, 8, 3, 2, -100, 8
SALVAGE, BONUS = 4, 6
NODES = list(NODE_HP)
RULE = dict(RULES, **PKG, crew_flat=True)
HP0 = {"COLLECTOR": 12, "AUDITOR": 8, "ENFORCER": 25, "LOCKDOWN": 18, "COURIER": 8, "INSPECTOR": 10, "BAILIFF": 30,
       "HAULER": 28}


def legs(n=30, seed=8):
    rng = random.Random(seed)
    return [[[(t, rng.choice(["C1", "C2"])) for t in rng.sample(THREAT_POOL, k)] for k in (2, 3, 4)] for _ in range(n)]


class State:
    __slots__ = ("bank", "fort", "lost", "surv", "log")

    def __init__(self, bank=START, fort=None, lost=(), surv=(), log=()):
        self.bank, self.fort, self.lost, self.surv, self.log = bank, fort or {}, tuple(lost), tuple(surv), tuple(log)

    def key(self):
        return (tuple(sorted((k, tuple(sorted(v))) for k, v in self.fort.items())), self.lost, self.surv)


def invested(fort) -> str | None:
    tot: dict[str, int] = {}
    for v in fort.values():
        for p in v:
            tot[p] = tot.get(p, 0) + COST[p]
    if not tot:
        return None
    return sorted(tot.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def roster_for(leg, i, st: State):
    """The raid as telegraphed: corp roster (+foothold entry, +adaptation trait) and the survivors who rejoin."""
    base = [list(t) for t in leg[i]]
    if st.lost:
        first = sorted(range(len(base)), key=lambda j: base[j][0])[0]
        base[first][1] = sorted(st.lost)[0]
    top = invested(st.fort)
    trait = COUNTER[top] if top else None
    tough = sorted(range(len(base)), key=lambda j: (-HP0[base[j][0]], base[j][0]))[0]
    out = []
    for j, (tid, e) in enumerate(base):
        out.append((tid, e, (trait,) if (trait and j == tough) else ()))
    for s_ in st.surv:
        out.append(s_)
    return out


def raid_result(st: State, buy, place, crew, roster):
    fort = {k: list(v) for k, v in st.fort.items()}
    for b, n in zip(buy, place):
        fort.setdefault(n, []).append(b)
    if "SAFE" in st.lost:
        crew = None
    r = run(Plan(fort, crew, dict(RULE)), threats=list(roster), start_taken=set(st.lost))
    return fort, r


def settle(st: State, fort, r, roster, i, act, n_raids):
    kills = {t for ev in r.steps for t, _ in ev["kills"]}
    pay = SALVAGE * len(kills) + (BONUS if r.clean else 0)
    bill = r.home_before - r.home_after
    for k, v in r.nodes.items():
        if k == "HOME" or k in st.lost:
            continue
        if v["outcome"] == "scuffed" and not r.clean:
            bill += v["before"] - v["after"]
        elif v["outcome"] == "down":
            bill += INSTALL[k] // 2
    spend = sum(COST[b] for b in act[0])
    bank = st.bank - spend + pay - bill
    if r.breached:
        return State(BREACH_SCORE, {}, st.lost, (), st.log + ((i, act, BREACH_SCORE, r.clean),)), pay - bill
    lost = set(st.lost) | {k for k, v in r.nodes.items() if v["outcome"] == "taken" and k != "HOME"}
    for k in lost:
        fort.pop(k, None)
    surv = []
    for tid in r.routes:
        if tid not in kills:
            base = tid.split("#")[0]
            surv.append((f"{base}#{i + 2}", next(e for t, e, *_ in roster if t == tid)
                         if any(t == tid for t, *_ in roster) else "C1"))
    if i < n_raids - 1:
        bank += BASE_INCOME + (VAULT_INC if "VAULT" not in lost else 0) + (RELAY_INC if "RELAY" not in lost else 0)
    return State(bank, fort, tuple(sorted(lost)), tuple(surv), st.log + ((i, act, bank, r.clean),)), pay - bill


def actions(st: State):
    yield (), ()
    held = [n for n in NODES if n not in st.lost]
    for k in (1, 2):
        for buy in itertools.combinations_with_replacement(list(COST), k):
            if sum(COST[b] for b in buy) > max(st.bank, 0) + 0:
                continue
            for place in itertools.product(held, repeat=k):
                yield buy, place


def options(st: State, leg, i):
    roster = roster_for(leg, i, st)
    for buy, place in actions(st):
        crews = sorted({n for n in set(place) | set(st.fort) | {"SAFE"} if n not in st.lost})
        for crew in crews:
            fort, r = raid_result(st, buy, place, crew, roster)
            ns, raid_net = settle(st, fort, r, roster, i, (buy, place, crew), len(leg))
            yield (buy, place, crew), ns, raid_net


def greedy(leg):
    st = State()
    for i in range(len(leg)):
        best = max(options(st, leg, i), key=lambda o: (o[2] + 0.5 * sum(COST[b] for b in o[0][0]), -len(o[0][0])))
        st = best[1]
        if st.bank == BREACH_SCORE:
            break
    return st


def planned(leg, g: State):
    beam = [State()]
    for i in range(len(leg)):
        nxt = []
        for st in beam:
            if st.bank == BREACH_SCORE:
                nxt.append(st)
                continue
            for act, ns, _ in options(st, leg, i):
                nxt.append(ns)
        nxt.sort(key=lambda s: -(s.bank + 0.5 * sum(COST[p] for v in s.fort.values() for p in v)))
        keep, seen = [], set()
        gl = g.log[:i + 1]
        for s_ in nxt:
            if [x[1] for x in s_.log] == [x[1] for x in gl]:
                keep.append(s_)
                seen.add(s_.key())
                break
        for s_ in nxt:
            if s_.key() in seen:
                continue
            seen.add(s_.key())
            keep.append(s_)
            if len(keep) >= BEAM:
                break
        beam = keep
    return max(beam, key=lambda s: s.bank)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    out = []
    for leg in legs(n):
        g = greedy(leg)
        p = planned(leg, g)
        rec = {"leg": leg, "greedy": g.bank, "planned": p.bank, "regret": p.bank - g.bank,
               "first_differs": g.log[0][1][0] != p.log[0][1][0],
               "greedy_log": [list(map(str, x)) for x in g.log], "planned_log": [list(map(str, x)) for x in p.log]}
        out.append(rec)
        print(json.dumps({k: rec[k] for k in ("greedy", "planned", "regret", "first_differs")}), flush=True)
    summ = {"legs": n, "mean_regret": round(sum(r["regret"] for r in out) / n, 1),
            "median_regret": sorted(r["regret"] for r in out)[n // 2],
            "share_regret_ge_10": round(sum(r["regret"] >= 10 for r in out) / n, 2),
            "first_differs_share": round(sum(r["first_differs"] for r in out) / n, 2),
            "greedy_breaches": sum(r["greedy"] == BREACH_SCORE for r in out),
            "planned_breaches": sum(r["planned"] == BREACH_SCORE for r in out)}
    print("SUMMARY", summ, flush=True)
    json.dump({"summary": summ, "legs": out}, open(r"D:/rc_tmp/raid_design_lab/h7_campaign.json", "w"), indent=1)
