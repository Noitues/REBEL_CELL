# Round 8 measurements: the pitch critic's kill tests

This round ran the cheapest experiment the pitch critic set for each of its top three pitches (review:
`_reviews/REVIEW_PITCHES_R8.md`). The scripts are all in `tools/raid_concepts/`, and each one writes its results
JSON to `D:/rc_tmp/raid_design_lab/`.

## Ring Siege (pitch 1): `ring_siege.py`, `ring_gap.py`
**Setup:** 3 rings × 6 slices, 3 spokes, a pool of 12 slices and ring speeds from −2 to +2, run on depth_harness's 10
raids.

**Results:**
- About 9.5 distinct near-best layouts per raid; every raid has 2 or more.
- The best layout beats the median random stocking by about 53.
- In 9 of 10 raids, only 0.2–1% of random stockings land within 3 of the best.

**Verdict:** it passes "naive stocking is not within 5% of the best", with a large skill gap. It sits at the edge of
the "fewer than 1% hold" puzzle line. Exact tuning is punishing, so speeds must be few and costly, as the critic said.

## Pursuit (pitch 2): `pursuit.py`, `pursuit_sweep.py`
**Setup:** a 10 × 3 City Grid, a Heat-driven front with 3 speed tables, 13 or 16 netruns, 2 catch costs, then v2
rules (laying low holds position, the core needs a Schematics key). 50 + 20 seeds; a beam-search planner against
shortest-path and greedy play.

**Routing passes on every config:**
- The shortest path is within 5% of the best on 0% of seeds; the kill line was above 70%.
- 4–21 near-optimal routes per grid; at least 3 on 88% of grids.
- The best line beats the shortest path by about 28 and greedy play by about 12.

**Catches fail on every config:**
- The best line averages 0–1.4 catches per campaign; the target was 3–5.
- They reach 1.2–1.4 only with a fast front plus a cheap catch or a high key.
- Cause: a catch is a pure cost the player can route around, so the optimum avoids it. FTL's fleet works the same way:
  it is a timer, not the source of fights.

**Verdict:** keep Pursuit as the campaign layer (route depth is real), but a catch cannot be what triggers a raid.
Raid cadence has to be guaranteed (Heat thresholds as today, or one catch per sector at a fixed beat). The route then
decides **where you are and what you carry** when the catch lands.

## Ghost Protocol (pitch 11): `ghost.py`
**Setup:** a 4 × 3 network with 6 assets and a 3-beam sweep (the third beam hunts the column of the first find).
Levers: 2 ghost slots, decoys at 3 Schematics each, and going dark (costs a netrun's income). Each of 30 networks is
fully enumerated.

**Results:**
- The best allocation beats the median by about 22.
- The greedy rule (ghost the two biggest assets, go dark on the exposed ones) is best on 13% of networks and loses
  about 7 on average.
- Decoys appear in near-best plans on 77% of networks.
- The best allocation is unique on 30% of networks.
- Near-best allocations are 0.05% of all allocations.

**Verdict:** passes. The critic's kill line was "a unique, greedy-obvious best on most seeds", and this is the
opposite. The levers interact: decoys redirect the hunter. Risk: the right answer is a needle, and the planner
needs a live preview.

## What this says for the merge (Manhunt = Pursuit + Ghost)
**The shape the numbers support:**
- **Campaign layer:** the Pursuit front, with depth in the route.
- **Cadence:** raids arrive at guaranteed beats, not at avoidable catches.
- **The raid itself:** a Ghost sweep of the network you have built. Depth comes from scarce hiding levers; graded losses
  are stamped on the nodes.
- **Last stand:** Ring Siege as the HQ fight when the front reaches HQ (Heat 100).

The cadence rule is a **designer decision**: guaranteed catches against threshold raids.

## Round 9: suspense levers (`ghost2.py`, `ring_brake.py`)

**Sealed beam / spoof press / both**, 30 networks, full lever set against scarce levers (1 ghost, 1 decoy):

| Measure | Full levers | Scarce |
|---|---|---|
| Sealed: the reveal changes the outcome | 23% | 53% |
| Spoof: land vs miss swing | 2.1 | 5.7 |
| Spoof: planning around the press changes the allocation | 20% | 50% |
| Both: reacting after the reveal beats committing in advance | 37% | 60% |

**Spinner (one press):**
- A one-tick BRAKE does nothing: gain 0.1, even on 6-threat raids.
- A one-slice SNAP with a 9-slice pool helps on 50% of raids. When it matters, there is usually exactly one right
  moment, and the stakes are about +2.
- Unpriced survivors made a stall-only defense optimal. Pricing survivors at 3 each is now the rule.

**Finding:** a hidden element or a press adds suspense only when the plan cannot cover everything. Scarcity is the
precondition.

## Round 10: the Invisible, Inc. alarm (`ghost3.py`)

**Setup:**
- Beams known in full.
- An alarm (found count, optionally pre-filled by Heat) trips a hidden reinforcement beam.

**Result:** the best plan never trips it from 0. From a Heat pre-fill of 1, it evades completely on 83% of networks,
and the outcome never varies.

**Finding:**
- Certain local information plus an escalation you can see coming is avoidable, so it adds no suspense.
- The unknown must touch even the best plan, as the sealed beam does.
- Round 10 keeps the M9c rules (sealed beam + reactive spoof). It changes the forecast to local (which nodes each line
  finds) and fixes the presentation.
