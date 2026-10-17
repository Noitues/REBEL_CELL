<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__hq__orbital; status ok; tokens in 10054 cache-write 0 cache-read 32585 out 1855; cost $0.023. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: hq/orbital

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 vs §10/§5, structure arithmetic.** The table says "Total 12 layers" but also "4 circuits' worth"; the extra circuit makes 15 layers. The L11 fork row says "2" nodes, but the branch "ANT top room → Retarget 4 → LAUNCH CONTROL" is 2 more layers, so the extra route is 13 or 14, not 15. The layer map and the table disagree on the Circuit 1 node counts (the table has 2,3,3,2,1; the map shows L4 as 2 nodes with L2 at 2). Layers 2→3→4 edges are inconsistent.
2. **BLOCKER, R3/R1, Silo Sabotage.** "2 phases (mini-boss class budget at T4 via the band analog)": the R2 mini-boss table has "n/a" at T4, so no HP is given. No HP, thresholds or per-phase arithmetic appear for the elites, Launch Guard or sabotage. "Phase 1 asks…" is stated for elites with no numbers. This is a hard rule gap.
3. **BLOCKER, R4/R1, Pressure.** Pressure (+10 %/turn from turn 1) duplicates enrage and conflicts with "normals: enrage off" and the 3-4 turns per phase. At +10 % per turn, a 7-turn elite reaches ×1.6+, harsher than the boss default (turn 10 start). Doors SHUT also hits sabotage twice per lap. The draft itself asks this in its Q.
4. **MAJOR, R9/R6, Fallout.** The text says "all your slices' statuses CORRUPTED on 2 random slices" (garbled). It also claims "preview shows which slices only after the draw", but the draw happens at entry. This violates previews equal results unless the preview is explicit. The flat 2-slice count should use R5 amount modes.
5. **MAJOR, §3.2, systems.** Venting "uses the existing `hits` rider, N20", but N20 is not in §8. "Solar Flares unavailable" invents a rule. "NEW: Doors rule modifier" duplicates N4/N6 territory.
6. **MAJOR, N# tags.** §8 omits N12 (variable sizes, needed for any sizes in the guard fights), N10 and N7. The Dish Link nudge on enemy wheels with "aim" is a NEW action with a vague fallback. N16 is mislabeled: "Crossed Wires/Fuel Leak" don't alter future fights.
7. **MAJOR, G11/§6 and §7.** DOWN is "a source for no one" (a node state), not a sink for Orbital Sites. The campaign-level strike tally is invented scope and affects the raid pass. The retry text keeps the dial from a failed run, which contradicts "new seed" and the Tribute rule.
8. **MAJOR, R7/§3.3.** "Each cleared ring station disables one buff" bypasses the Exploit-subset rule (R7). Skipping P1 also bypasses the "damage parks" threshold logic, and it conflicts with the corp-draft ownership of the boss. Breach "skips 2nd needle" likewise rewrites the boss.
9. **NIT, RNG streams.** `hq_rewards`/`hq_fallout` need checkpointed stream names registered. "Silo rim" elements and the art-slot names are fine.
10. **NIT, §3.1.** "Salvo: −15 % HP" ignores parking and the R2 band, and "Jam" adds a skip-resolve effect that is not a listed system.

## Concrete fixes

- **Structure:** state "12 layers (override) / 14 layers (extra circuit: L11 NW dish, L12 top room + Retarget 4, L13 LAUNCH CONTROL)". Fix the table to L1 PAD(1), L2 (2), L3 (3), L4 (2), L5 (1), and make the map match.
- **HP table (T4, R2 arithmetic):** elite 2 phases: 2×(18−0)×3.5 = 126, within 112-144. Use thresholds 0.5, HP 126. Sabotage: the Launch Guard is an elite (2 phases, 126 HP, parked at 0.5), minus satellite sustain.
- **Pressure:** replace it with the elite default enrage (start 8, every 5, +25 %). Shut doors instead set `enrage start_turn = 6` for the antenna elites only.
- **Fallout:** "On boss entry, 2 non-NULL slices become CORRUPTED (stream `hq_fallout`, drawn at the pre-boss checkpoint; the fork card shows the exact slices after a one-time draw on viewing, locked in)." 
- **Strike tally:** cut §6's raid effect. Replace it with "+Schematics per retarget" until the raid pass.
- **§8:** add N12, N20, N7; mark Dish Link as NEW with a card fallback.

## Keep

The retarget loop with echo nodes and a price-for-speed fork is distinctive. The Intel/Breach/Virus payoffs as convenience only, and the art-state hooks, are clean.

## Q:

Q: Should the override skip phase 1 or only reduce the buff set?
Q: Is the 14-layer route within the D10 allowance?
Q: Will Dish Link nudges respect enemy resistance during preview?
