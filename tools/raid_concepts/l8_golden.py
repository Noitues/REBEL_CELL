"""Parity golden for the L8 city-raid lab (tools/raid_lab_city): sweep_l8.py rules (L9: decay before each capture;
L11: MAX_PLACED cap, DEPLOY response, lost districts return their sentry, safe_next).
Legs 0, 3, 5, 8: leg data and the greedy and naive lines step by step (state before, state after decay, capture, state
after capture, place, response, real candidate, trace with beams, tier, after the raid, between choice, safe_next per
intensity for the chosen repair and build, after, score), plus random raids (responses from response_options, so
DEPLOY included), between steps and capture checks reached by random legal play. Writes
tools/raid_lab_city/data/l8_golden.json.
    python tools/raid_concepts/l8_golden.py"""
from __future__ import annotations

import json
import random
from pathlib import Path

import sweep_l8 as S

OUT = Path(__file__).resolve().parents[1] / "raid_lab_city" / "data" / "l8_golden.json"
LEGS = (0, 3, 5, 8)
cj, sj = S.cell_json, S.state_json


def line_json(ln):
    return {"kind": ln.kind, "index": ln.index, "cells": [cj(c) for c in ln.cells], "type": ln.type, "home": ln.home}


def leg_json(leg):
    return {"seed": leg.seed, "values": [[c[0], c[1], v] for c, v in leg.values], "exploits": [cj(c) for c in leg.exploits],
            "start": [cj(c) for c in leg.start],
            "raids": [{"b1": line_json(r.b1), "extra1": line_json(r.extra1), "extra2": line_json(r.extra2),
                       "perm": list(r.perm), "cands": [line_json(c) for c in r.cands], "real": r.real,
                       "hunter_type": r.hunter_type, "hunter_street": r.hunter_street} for r in leg.raids]}


def place_json(place):
    sent, ghost = place
    return {"sentries": [[c[0], c[1], t] for c, t in sorted(dict(sent).items(), key=lambda x: S.ck(x[0]))], "ghost": cj(ghost)}


def resp_json(r):
    r = S.norm_response(r)
    if r[0] == "REDEPLOY":
        return [r[0], cj(r[1]), cj(r[2])]
    if r[0] == "DEPLOY":
        return [r[0], r[1], cj(r[2])]
    return [r[0]]


def trace_json(tr):
    return [[b, cj(c), k] for b, c, k in tr]


def intensities(leg, st):
    """Intensity names in the Python between_options order (first appearance)."""
    return list(dict.fromkeys(o[2] for o in S.between_options(leg, st)))


def safe_next_json(leg, i, ns, repair, build):
    """{intensity: safe_next(leg, i + 1, decay(between(ns, repair, build, intensity)))} for the chosen repair/build."""
    out = {}
    for inten in intensities(leg, ns):
        after = S.between(leg, ns, repair, build, inten)
        out[inten] = bool(S.safe_next(leg, i + 1, S.decay(leg, after)))
    return out


def raid_rec(leg, i, st, place, k, resp):
    ns, _ = S.resolve(leg, i, st, k, place, resp)
    tr = S.trace(leg, i, st, k, place, resp)
    touches = [(c, kk) for _, c, kk in tr]
    hl = S.hunter_line(leg, i, st, k, place, resp)
    return ns, {"before": sj(st), "place": place_json(place), "cand": k, "response": resp_json(resp),
                "trace": trace_json(tr), "hunter": None if hl is None else line_json(hl),
                "tier": S.tier(st, ns, touches), "after_raid": sj(ns), "score_raid": S.score(leg, ns)}


def replay(leg, log):
    st = S.initial(leg)
    steps = []
    for x in log:
        i = x["raid"]
        rec = {"raid": i, "before_capture": sj(st)}
        if i > 0:
            st = S.decay(leg, st)
        rec["after_decay"] = sj(st)
        rec["capture"] = cj(x["capture"])
        st = S.capture(leg, st, x["capture"]) if x["capture"] is not None else st
        place = (dict(x["place"]["sentries"]), x["place"]["ghost"])
        resp = S.norm_response(x["response"])
        ns, rr = raid_rec(leg, i, st, place, x["cand_real"], resp)
        rec.update(rr)
        b = x["between"]
        after = S.between(leg, ns, b["repair"], b["build"], b["intensity"]) if b else ns
        rec["between"] = {"repair": cj(b["repair"]), "build": b["build"], "intensity": b["intensity"]} if b else None
        if b:
            rec["safe_next"] = safe_next_json(leg, i, ns, b["repair"], b["build"])
        rec["after"] = sj(after)
        rec["score_after"] = S.score(leg, after)
        steps.append(rec)
        st = after
        if ns.home_hp <= 0:
            break
    return steps


def randoms(n_raid=200, n_between=100, n_capture=100):
    rng = random.Random(97)
    raids, betweens, captures = [], [], []
    while len(raids) < n_raid or len(betweens) < n_between or len(captures) < n_capture:
        leg = S.make_leg(rng.choice(LEGS))
        st = S.initial(leg)
        for i in range(S.RAIDS):
            if i > 0:
                st = S.decay(leg, st)
            opts = S.capture_options(leg, st)
            if len(captures) < n_capture:
                captures.append({"leg": leg.seed, "state": sj(st), "options": [cj(c) for c in opts]})
            if opts:
                st = S.capture(leg, st, rng.choice(opts))
            pls = list(S.placements(leg, st))
            place = rng.choice(pls)
            k = rng.randrange(len(leg.raids[i].cands))
            resp = rng.choice(S.response_options(leg, i, st, k, place))
            ns, rr = raid_rec(leg, i, st, place, k, resp)
            if len(raids) < n_raid:
                raids.append({"leg": leg.seed, "raid": i, **rr})
            if ns.home_hp <= 0 or i == S.RAIDS - 1:
                break
            r, b, inten = rng.choice(list(S.between_options(leg, ns)))
            after = S.between(leg, ns, r, b, inten)
            if len(betweens) < n_between:
                betweens.append({"leg": leg.seed, "before": sj(ns), "repair": cj(r), "build": b, "intensity": inten,
                                 "after": sj(after)})
            st = after
    return raids, betweens, captures


if __name__ == "__main__":
    legs = []
    for s in LEGS:
        leg = S.make_leg(s)
        _, glog = S.greedy_leg(leg)
        _, nlog = S.naive_leg(leg)
        legs.append({"seed": s, "leg": leg_json(leg), "greedy": replay(leg, glog), "naive": replay(leg, nlog)})
        print("leg", s, flush=True)
    rr, bb, cc = randoms()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"config": S.config(), "legs": legs, "random_raids": rr, "random_betweens": bb,
                               "random_captures": cc}, indent=1), encoding="utf-8")
    print("wrote", OUT)
