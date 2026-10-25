"""G4 R-D: the street Bloom's catch chance for one Solace netrun, from the real BloomRules numbers (g4_real.REAL), as a
function of the INFECTED cards in the defense deck. Python 3 stdlib only, seeded.

Rule (designer R-D, 2026-10-25): each INFECTED card starts the street virus front one STEP closer. A step is one node
entry's front advance (BloomRules.entry_pace at the netrun's tier and Heat band, Virus key applied): the unit the Intel
ladder preview counts in (ladder_gaps). So the start gap is bloom_start_gap_milli_by_tier[tier] - n * entry_pace.

The netrun itself is ASSUMED (the GDScript CampaignSimulator plays real netruns but needs Godot; G4 does not run it):
- 7 layers (map_layers), one node entered per layer: layer 1 router fight, 2 fight, 3 Mainframe (shop, no fight),
  4 Server Rack fight, 5 a fight half the time (else a Terminal), 6 elite fight, 7 Server Rack fight (about 5 combats,
  GDD 4.2).
- Fight turns: a one-phase fight 3..5 turns, a two-phase fight (rack, elite) 5..9 turns (target_turns_per_phase 3.5),
  uniform. The front advances by the scaled per-turn pace (Intel key halves it) at each fight end.
- Doses: the netrunner buys one dose at the Mainframe (bloom_dose_price, Cycles assumed sufficient) when the front would
  otherwise catch it before layer 7 with the mean fight lengths, and uses a held dose before any entry or fight the
  front would catch it in (push bloom_dose_push_milli, clamped to bloom_max_gap_milli).
- Caught (gap <= 0) = the operative dies (NetrunSession._bloom_caught -> _die).

Output: data/g4_bloom_curve.json: catch[tier 1..3][band 0..4][keys 0..7][n 0..N_MAX] (keys bit 1 Virus, 2 Intel,
4 Breach), TRIALS netruns per cell.
    python tools/raid_concepts/g4_bloom.py"""
from __future__ import annotations

import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g4_real import REAL as R    # noqa: E402

N_MAX = 16
TRIALS = int(os.environ.get("G4_BLOOM_TRIALS", 2000))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "g4_bloom_curve.json")
# layer -> fight kind: 0 none, 1 one-phase, 2 two-phase, 3 one-phase half the time
LAYER_FIGHT = {1: 1, 2: 1, 3: 0, 4: 2, 5: 3, 6: 2, 7: 2}
ONE_PHASE, TWO_PHASE = (3, 5), (5, 9)


def scaled(base: int, heat_pct: int, virus: bool, intel_turn: bool) -> int:
    """BloomRules._scaled: floor(base x heat% [x virus%] [x intel%] / 100^n), minimum 1."""
    if base <= 0:
        return base
    num, den = base * heat_pct, 100
    if virus:
        num *= R["bloom_virus_pace_pct"]
        den *= 100
    if intel_turn:
        num *= R["bloom_intel_turn_pct"]
        den *= 100
    return max(1, num // den)


def entry_pace(tier: int, band: int, keys: int) -> int:
    return scaled(R["bloom_pace_node_milli_by_tier"][tier - 1], R["bloom_pace_heat_pct_by_band"][band], bool(keys & 1),
                  False)


def turn_pace(band: int, keys: int) -> int:
    return scaled(R["bloom_pace_turn_milli"], R["bloom_pace_heat_pct_by_band"][band], bool(keys & 1), bool(keys & 2))


def one_netrun(tier: int, band: int, keys: int, n_inf: int, rng: random.Random) -> bool:
    """True when the Bloom catches the operative."""
    ep, tp = entry_pace(tier, band, keys), turn_pace(band, keys)
    front = -(R["bloom_start_gap_milli_by_tier"][tier - 1] - n_inf * ep)
    setback = R["bloom_breach_setback_milli"] if keys & 4 else 0
    doses = 0
    mean_turns = {1: sum(ONE_PHASE) / 2, 2: sum(TWO_PHASE) / 2, 3: sum(ONE_PHASE) / 4}

    def push(front, layer):
        gap = min(layer * 1000 - front + R["bloom_dose_push_milli"], R["bloom_max_gap_milli"])
        return layer * 1000 - gap

    layer = 0
    for nxt in range(1, R["map_layers"] + 1):
        adv = ep - setback
        if nxt * 1000 - (front + adv) <= 0 and doses:
            doses -= 1
            front = push(front, layer)
        front += adv
        setback = 0
        layer = nxt
        if layer * 1000 - front <= 0:
            return True
        kind = LAYER_FIGHT[nxt]
        if kind == 3:
            kind = 1 if rng.random() < 0.5 else 0
        if kind == 0:
            if nxt == 3:        # Mainframe: buy a dose when the rest of the run would catch on mean fights
                rest = front
                for l2 in range(4, R["map_layers"] + 1):
                    rest += ep + int(tp * mean_turns[LAYER_FIGHT[l2]])
                    if l2 * 1000 - rest <= 0:
                        doses += 1
                        break
            continue
        turns = rng.randint(*(ONE_PHASE if kind == 1 else TWO_PHASE))
        adv = tp * turns
        if layer * 1000 - (front + adv) <= 0 and doses:
            doses -= 1
            front = push(front, layer)
        front += adv
        if layer * 1000 - front <= 0:
            return True
    return False


def build() -> dict:
    catch = {}
    for tier in (1, 2, 3):
        for band in range(5):
            for keys in range(8):
                row = []
                for n in range(N_MAX + 1):
                    rng = random.Random("bloom:%d:%d:%d:%d" % (tier, band, keys, n))
                    p = round(sum(one_netrun(tier, band, keys, n, rng) for _ in range(TRIALS)) / TRIALS, 4)
                    # monotone envelope: the dose heuristic buys a dose only when it sees the catch coming, which
                    # makes the raw curve dip; the published curve never falls as n rises
                    row.append(max(p, row[-1]) if row else p)
                catch["%d:%d:%d" % (tier, band, keys)] = row
    return {"trials": TRIALS, "n_max": N_MAX, "catch": catch,
            "entry_pace": {"%d:%d:%d" % (t, b, k): entry_pace(t, b, k) for t in (1, 2, 3) for b in range(5)
                           for k in range(8)}}


if __name__ == "__main__":
    d = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(d, f, indent=0, sort_keys=True)
    for tier in (1, 2, 3):
        for band in range(5):
            print("T%d band %d keys0" % (tier, band), d["catch"]["%d:%d:0" % (tier, band)][:9],
                  "keys7", d["catch"]["%d:%d:7" % (tier, band)][:9])
    print("->", OUT)
