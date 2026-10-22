"""Round 6, concept H (BASTION): the defense persists across the campaign. Is there depth ACROSS raids?
Rules (prototype; each a designer decision):
- No per-raid draft. Pieces you buy stay where you put them, raid after raid.
- Each HQ visit before a raid: buy up to 2 pieces (TURRET 6, SENTRY 7, RAILGUN 10, ICE 5, DECOY 4) and place them, and
  station the crew. The next raids' rosters are telegraphed (all three are known here).
- After a raid: payout (+4 salvage per kill, +6 if CLEAN), then the full repair bill is paid. A TAKEN node's pieces
  are destroyed. Income between raids: +INCOME (the netruns).
- Breach (home at 0) ends the campaign at BREACH_SCORE.
Score = the final Schematics bank. GREEDY picks, at each visit, the action with the best bank after THIS raid;
PLANNED is a beam search on the final bank. Regret = planned - greedy. First-visit divergence = they buy different
pieces at visit 1 (the investment decision). Seeded scenarios (3 raids of 2 / 3 / 4 threats, random entries)."""
from __future__ import annotations

import itertools
import json
import random
import sys

sys.path.insert(0, r"D:/Godot/rebel_cell/.claude/worktrees/raid-design-lab-2d2e2e/tools/raid_concepts")
from sim import NODE_HP, RULES, Plan, run  # noqa: E402
from depth_harness import PKG, THREAT_POOL, net, price  # noqa: E402

COST = {"TURRET": 6, "SENTRY": 7, "RAILGUN": 10, "ICE": 5, "DECOY": 4}
START, INCOME, BREACH_SCORE, BEAM = 14, 12, -100, 8
NODES = list(NODE_HP)
RULE = dict(RULES, **PKG)


def campaigns(n=5, seed=8):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        out.append([[(t, rng.choice(["C1", "C2"])) for t in rng.sample(THREAT_POOL, k)] for k in (2, 3, 4)])
    return out


def actions(bank: int):
    """(buys, placements): up to 2 pieces the bank can afford, each on a node."""
    yield (), ()
    types = list(COST)
    for k in (1, 2):
        for buy in itertools.combinations_with_replacement(types, k):
            if sum(COST[b] for b in buy) > bank:
                continue
            for place in itertools.product(NODES, repeat=k):
                yield buy, place


def step(state, buy, place, crew, roster):
    """state = (bank, assets {node: [pieces]}). Returns (new_state, result)."""
    bank, assets = state
    a = {k: list(v) for k, v in assets.items()}
    for b, n in zip(buy, place):
        a.setdefault(n, []).append(b)
    bank -= sum(COST[b] for b in buy)
    r = run(Plan(a, crew, dict(RULE)), threats=list(roster))
    if r.breached:
        return (BREACH_SCORE, {}), r
    bank += net(r)
    for k, v in r.nodes.items():
        if v["outcome"] == "taken":
            a.pop(k, None)
    return (bank, a), r


def options(state, roster):
    bank, assets = state
    for buy, place in actions(bank):
        crews = sorted(set(place) | set(assets) | {"SAFE"})
        for crew in crews:
            yield (buy, place, crew), step(state, buy, place, crew, roster)


def greedy(camp):
    state = (START, {})
    log = []
    for i, roster in enumerate(camp):
        best = max(options(state, roster), key=lambda o: (o[1][0][0], -sum(COST[b] for b in o[0][0])))
        act, (state, r) = best
        log.append({"raid": i + 1, "buy": act[0], "place": act[1], "crew": act[2], "bank": state[0], "clean": r.clean})
        if state[0] == BREACH_SCORE:
            break
        if i < len(camp) - 1:
            state = (state[0] + INCOME, state[1])   # netrun income between raids (none after the last)
    return state[0], log


def planned(camp, greedy_log=None):
    """Beam search on the final bank; the greedy line is always kept in the beam, so planned >= greedy."""
    beam = [((START, {}), [])]
    for i, roster in enumerate(camp):
        nxt = []
        g_act = None
        if greedy_log and i < len(greedy_log):
            g = greedy_log[i]
            g_act = (g["buy"], g["place"], g["crew"])
        for state, log in beam:
            if state[0] == BREACH_SCORE:
                nxt.append((state, log))
                continue
            for act, (s2, r) in options(state, roster):
                s3 = (s2[0] + (INCOME if s2[0] != BREACH_SCORE else 0), s2[1])
                nxt.append((s3, log + [{"raid": i + 1, "buy": act[0], "place": act[1], "crew": act[2], "bank": s2[0],
                                         "clean": r.clean}]))
        # keep the best by bank plus a crude value for installed pieces (they keep paying), then diversify by buys
        nxt.sort(key=lambda x: -(x[0][0] + 0.5 * sum(COST[p] for v in x[0][1].values() for p in v)))
        seen, keep = set(), []
        if g_act is not None:
            for s_, lg in nxt:
                if [(x["buy"], x["place"], x["crew"]) for x in lg] == [(x["buy"], x["place"], x["crew"]) for x in greedy_log[:i + 1]]:
                    keep.append((s_, lg))
                    seen.add(tuple(sorted((k, tuple(sorted(v))) for k, v in s_[1].items())))
                    break
        for s, lg in nxt:
            sig = tuple(sorted((k, tuple(sorted(v))) for k, v in s[1].items()))
            if sig in seen:
                continue
            seen.add(sig)
            keep.append((s, lg))
            if len(keep) >= BEAM:
                break
        beam = keep
    best = max(beam, key=lambda x: x[0][0])
    return best[0][0] - INCOME, best[1]


if __name__ == "__main__":
    out = []
    for c in campaigns():
        g, gl = greedy(c)
        p, pl = planned(c, gl)
        rec = {"rosters": c, "greedy": g, "planned": p, "regret": p - g, "greedy_log": gl, "planned_log": pl,
               "first_visit_differs": gl[0]["buy"] != pl[0]["buy"]}
        out.append(rec)
        print(json.dumps({k: rec[k] for k in ("greedy", "planned", "regret", "first_visit_differs")}),
              [(x["buy"], x["place"], x["bank"]) for x in gl], [(x["buy"], x["place"], x["bank"]) for x in pl], flush=True)
    summ = {"mean_regret": sum(r["regret"] for r in out) / len(out),
            "first_visit_differs_share": sum(r["first_visit_differs"] for r in out) / len(out)}
    print("SUMMARY", summ, flush=True)
    json.dump({"summary": summ, "campaigns": out}, open(r"D:/rc_tmp/raid_design_lab/bastion.json", "w"), indent=1)
