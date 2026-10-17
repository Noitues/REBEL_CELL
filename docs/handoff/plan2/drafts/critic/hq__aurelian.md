<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__hq__aurelian; status ok; tokens in 9791 cache-write 0 cache-read 32585 out 1956; cost $0.023. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: hq/aurelian

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 arithmetic and layer map.** The table totals 6+5+4+3+1 = 19, but the draft says the art has 18 rooms plus the Rostrum, and the rings it assigns are 6/5/4/3. Ring 4 has 3 nodes (L7: 2, L8: 1), yet L8 is the Grand Stand puzzle, so only 2 rooms are real ring-4 rooms. The map also lists ring 1 as a1–a3 and b1–b3, which is 6 correct, and ring 2 as c1–c3 and d1–d2, which is 5 correct, so only the ring 4/Grand Stand mapping is inconsistent. State whether the Grand Stand takes the ring-4 slot, and fix the "18 + Rostrum" sentence.

2. **BLOCKER, §3.1 spine fails on its own premise.** Every move completes a node, which triggers a step. Descending is therefore only possible from the last layer of a ring. The rule "powered only when a gate overlaps at the moment you leave" depends on where you are after n steps, and at most 2 nodes per ring are descent-capable. The §2 "guarantee within 4 steps" is unproven, and the Q2 "checker" is deferred. Because ring 3 has 2 rooms at L6 and 2 gates, an unreachable-gate softlock is plausible. The draft also says "one-way graph hop", yet along-ring moves cost a node. That contradicts "wait" in Q1 and conflicts with R1-style node counts (sideways nodes are fights).

3. **MAJOR, §3.2 VERDICT.** The "house rule" is not defined in the draft, which says "Needs the VERDICT rule" and "listed in §8", but §8 has no rule text. It marks a slice at every fight start. "WEAK CORRUPTED, Perfect OVERCLOCKED" is a status outcome with no stated trigger. Under R9, CORRUPTED is a double RAM cost, which is never mentioned. It is also listed under N6 although it is a status rider, so tag it NEW: VERDICT rule.

4. **MAJOR, §3.3/§3.4 dominated choice and perverse incentive.** Favor rewards Perfects on marked slices, but a Perfect becomes OVERCLOCKED (it burns out into CORRUPTED), so it is both +1 and a later RAM tax. The draft never says what happens at Favor 2–3 versus 0. "Breach adds +1 Favor" is invented. Q4 already flags the conflict with the boss VERDICT.

5. **MAJOR, §5 HP budget.** Intake of 5–8 per phase for normals in a 3–4-turn fight gives "8–12 HP", but the draft later claims 110–140 total, which does not follow from its own table. With 7–8 Routers at about 10, 2–3 Elites at about 18, and a Cache at about 18, the sum is about 140. A 60-HP operative needs about 100 HP of healing, but the sources listed (2 Rests at 25% ≈ 30 HP) sum to far less. A reference arrival at "50–60 % HP" is therefore unreachable.

6. **MAJOR, §4 invented content.** Named enemies (Lictor, Legionary drone, Tax Farmer, Lanista, Vestal Firewall, Praetorian, Censor) are not in the enemy inventory. The Circus clock vs N16: N16 covers future-fight overrides, so the Jeered and Grand Stand effects work through N16, but the draft says "None; needs N16" without a data fallback.

7. **NIT, §3.1 vs §4.** Intel is said to show 4 steps, while §9 uses `telegraph_depth`. A "Cache" is also a Server Rack variant, while the D4 ruling calls Cache an event mini-puzzle.

## Concrete fixes

- Replace the layer table total with: "Ring 4 = L7 (2 rooms) + L8 Grand Stand (1) = 3 slots; 18 rooms + Rostrum = 19."
- Add to §3.1: "Descent is allowed only from the last layer of a ring. Each ring-last-layer room has its own `open_on_steps` list authored so that every room opens at least once in any 3 consecutive steps. Validated by a lint test, not the generator."
- Replace the Favor rule: "+1 on a win with no CORRUPTED slice created this fight; −1 if the Rostrum VERDICT burned a Perfect. Thumbs Up at 3+ holds the gate one step; no Breach bonus."
- Replace the §5 heal budget with: "Rests 25% ×2 plus Mainframe heals ≈ 55 HP; cut Routers to 6–7, or start HQ runs healed."
- Define VERDICT in §3.2: "Mark on a slice: Perfect → OVERCLOCKED; GOOD → mark stays; WEAK → CORRUPTED (R9 double RAM). Tag NEW: VERDICT rule; fallback: APPLY_STATUS at combat start."
- Replace named enemies with "Aurelian pool, enemy drafts" until ids exist.

## Keep

- The deterministic gate clock is a unique, paper-solvable timing puzzle and fits the art's yellow telegraph.
- The data-only `open_on_steps` fallback and the per-frame art hook list are solid.

## Q:

Q: Can the player pass a step without a fight (R1 pacing), or only move sideways?
Q: Is the Grand Stand a ring-4 room or a separate L8 beat?
Q: Should Favor exist at all, given it conflicts with the boss VERDICT?
