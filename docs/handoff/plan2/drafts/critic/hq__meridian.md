<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__hq__meridian; status ok; tokens in 10304 cache-write 0 cache-read 32585 out 1959; cost $0.023. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: hq/meridian

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 vs §3.1 (clock arithmetic).** The swaps are claimed to fall on L2, L4, L6, L8 and L10, with the train away at L4-5 and L8-9 and present at L6-7 and L10-11. With T = layer + H, P = floor((T+p0)/2), and the train present when P is odd, L4-5 (P=2 at p0=0) is away, L6-7 (P=3) is present, and L8-9 (P=4) is away. That matches for p0=0. But then P changes at L6, L8 and L10 and not at L2 or L4 (L2-3 is P=1, L4 is P=2, so L4 is a swap). That is consistent only for p0=0. For p0=1 every swap lands on odd layers, so every fixed-layer claim (Rack car at L6, the Siding at L4-5, the Direct Lift train state) breaks. The Rack car would be absent in half of all seeds even without a Dwell, which contradicts "Dwell can cost you the Rack".
2. **BLOCKER, §2 Act II edges.** The L7→L8 rule is ambiguous: "indices 1-2 go to LegW and indices 3-4 go to LegE, and indices 2-3 reach both" makes indices 2 and 3 connect to both legs, contradicting the first two clauses. L8 has 2 nodes, not the 4 slots. The rule also leaves index 4 (RAIL) unable to reach LegE if it is not listed. L9→L10 is not defined at all.
3. **MAJOR, node count.** The layout is stated as "36 nodes". Count: L1-3 are 3 each = 9, L4-7 are 4 each = 16, L8 = 2, L9 = 3, L10 = 3, L11 = 3, L12 = 1. That totals 37, not 36. The EXP10 landing adds 1 more.
4. **MAJOR, R1/R2 (HQ fights).** Pacing counts 7 normals plus 2 elites, but the map has many more Routers: 3 in L1-L2, 2 in L3, 3 in L4-L7, 3 in L8-L10. A path takes one node per layer, so a typical path of 11 nodes holds about 10 non-boss nodes. The table lists only 7+2+3 = 12 nodes, which includes the boss, so total time and HP pressure are underestimated.
5. **MAJOR, R4.** The Car enrage "start 4, every 3" overrides the class default for normals, which is off. Allowed via `combat_overrides`, but a 3-4 turn normal rarely reaches turn 4. It is a near-dead tag, and the "train departs" timer never bites.
6. **MAJOR, R3 and phases.** The Hoisted ORBIT 1 tick (shifting enemy pointers) interacts with the normal one-needle design, but the draft never checks that the Hoist is readable (the preview shows orbit trails per GDD 2.11). Flagging it as untested is the minimum.
7. **MAJOR, §3.3 Direct Lift.** The penalty and bonus are tied to the boss start RAM, but a negative RAM start (−2) when the run only begins with 6 RAM is a heavy hit, and the draft makes the free Rest stair compete with it. Fine as a choice, but "the first card costs 0" is a new rule not in N1-N20. It should be tagged NEW.
8. **NIT, §3.2.** The Reach sector is described with a permuted order but §2 uses the default, and the sectors for the Act I nodes are never specified with the permuted order.
9. **NIT, spelling.** "Defense" and US forms are fine. "Siding" is fine. No Site names appear.

## Concrete fixes

1. Set p0 fixed to the schedule: define P = floor((T + 1)/2) with p0 removed, or constrain p0 to be applied to the layer-L6 Rack car explicitly. Replace the Rack rule with "the Rack car is present at the L6 phase for H=0 and p0=0 or 1 by authored p0 choice." Paste: *"p0 is drawn from {0, 1}; generation rejects seeds where the L6 RAIL slot is a Siding at H=0."*
2. Replace the L7→L8 rule: *"L7 idx1, idx2 → LegW; idx2, idx3 → LegW and LegE; idx3, idx4 → LegE. L8 LegW → CAB, LegW; LegE → CAB, LegE. L9: all → SpanC and the same-side span node."*
3. Change "36 nodes" to "37 nodes (38 with EXP10)".
4. Pacing table: normals 8, elites 2 (3 with the L5 or L7 elite), non-fight 3. Recompute the total to about 40 min and HP to about 120 %.
5. Car enrage: "Car: enemy damage +25 % from turn 3" (a data-only EnrageData override).
7. Tag the free first card as *NEW: boss start modifier (data field on `next_combat_overrides`, N16)*, with a fallback of "RAM ±2 only".

## Keep

- The visible, deterministic timetable: all of the map's uncertainty is in routing.
- Dwell as a Heat-priced steering tool that risks the Rack.
- The Exploit buildings that each add a distinct clock action.
- The data-only fallback of prebaked edge tables per H.

## Q:

Q: Should p0 stay seeded, or should the schedule be authored so the Rack car is guaranteed reachable?
Q: Should Hoisted fights always show the ORBIT trail in the preview?
Q: Is a negative start RAM acceptable, or should the penalty be a lost card draw instead?
