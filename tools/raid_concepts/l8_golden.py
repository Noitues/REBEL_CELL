"""Parity golden for the L8 city-raid lab (tools/raid_lab_city): sweep_l8.py rules (L9: decay before each capture;
L11: MAX_PLACED cap, DEPLOY response, lost districts return their sentry, safe_next; L13: sealed hunter street
(hunter_cands / hunter_real, hunt after cand), SACRIFICE response, Heat bands, intensity perks with extra_capture).
Legs 0, 3, 5, 8: leg data and the greedy and naive lines step by step (state before, state after decay, capture list,
state after capture, place, response, real candidate, real hunter street, trace with beams, tier, after the raid,
between choice, safe_next per intensity for the chosen repair and build, after, score), plus random raids (responses
from response_options, so DEPLOY and SACRIFICE included; hunt from rng.randrange(2)), between steps and capture checks
reached by random legal play. Writes tools/raid_lab_city/data/l8_golden.json.
    python tools/raid_concepts/l8_golden.py"""
from __future__ import annotations

import dataclasses
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
                       "hunter_type": r.hunter_type, "hunter_cands": list(r.hunter_cands),
                       "hunter_real": r.hunter_real} for r in leg.raids]}


def place_json(place):
    sent, ghost = place
    return {"sentries": [[c[0], c[1], t] for c, t in sorted(dict(sent).items(), key=lambda x: S.ck(x[0]))], "ghost": cj(ghost)}


def resp_json(r):
    r = S.norm_response(r)
    if r[0] == "REDEPLOY":
        return [r[0], cj(r[1]), cj(r[2])]
    if r[0] == "DEPLOY":
        return [r[0], r[1], cj(r[2])]
    if r[0] == "SACRIFICE":
        return [r[0], cj(r[1])]
    return [r[0]]


def trace_json(tr):
    return [[b, cj(c), k] for b, c, k in tr]


def is_cell(c):
    return isinstance(c, (tuple, list)) and len(c) == 2 and all(isinstance(v, int) for v in c)


def caps_of(c):
    """A logged capture as a list of 0 to 2 cells (accepts None, a single cell or a list of cells)."""
    if c is None:
        return []
    if is_cell(c):
        return [tuple(c)]
    return [tuple(x) for x in c]


def clear_extra(st):
    """CAPTURE clears extra_capture once the phase is over (even if the second capture had no option)."""
    return dataclasses.replace(st, extra_capture=0) if st.extra_capture else st


def capture_phase(leg, st, cells):
    """Replay a capture list: capture, capture again if extra_capture was set, then clear the flag."""
    for c in cells:
        st = S.capture(leg, st, c)
    return clear_extra(st)


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


def raid_rec(leg, i, st, place, k, hunt, resp):
    ns, _ = S.resolve(leg, i, st, k, hunt, place, resp)
    tr = S.trace(leg, i, st, k, hunt, place, resp)
    touches = [(c, kk) for _, c, kk in tr]
    hl = S.hunter_line(leg, i, st, k, hunt, place, resp)
    return ns, {"before": sj(st), "place": place_json(place), "cand": k, "hunt": hunt, "response": resp_json(resp),
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
        cells = caps_of(x["capture"])
        rec["capture"] = [cj(c) for c in cells]
        st = capture_phase(leg, st, cells)
        place = (dict(x["place"]["sentries"]), x["place"]["ghost"])
        resp = S.norm_response(x["response"])
        hunt = leg.raids[i].hunter_real
        ns, rr = raid_rec(leg, i, st, place, x["cand_real"], hunt, resp)
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
            n_caps = 1 + (1 if st.extra_capture > 0 else 0)
            for _ in range(n_caps):
                opts = S.capture_options(leg, st)
                if len(captures) < n_capture:
                    captures.append({"leg": leg.seed, "state": sj(st), "options": [cj(c) for c in opts]})
                if not opts:
                    break
                st = S.capture(leg, st, rng.choice(opts))
            st = clear_extra(st)
            pls = list(S.placements(leg, st))
            place = rng.choice(pls)
            k = rng.randrange(len(leg.raids[i].cands))
            hunt = rng.randrange(2)
            resp = rng.choice(S.response_options(leg, i, st, k, place))
            ns, rr = raid_rec(leg, i, st, place, k, hunt, resp)
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
