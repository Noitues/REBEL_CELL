<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__hq__halcyon; status ok; tokens in 9967 cache-write 0 cache-read 32585 out 2197; cost $0.024. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: hq/halcyon
**Verdict:** FIX

## Issues
1. **BLOCKER, §2 Layer map vs. guarantees.** L1–L13 are listed, but the guarantee text says "Rests at L5, L9 and L11" and "Elite in every layer 4–10". The table has no Elite at L5, L8 or L9, and L5 and L9 carry the Maintenance Bay in place of a fight. The guarantee contradicts the table. "Total: 30 nodes" also doesn't match the table: 3+2+3+2+3+3+2+3+2+3+2+1+1 = 30 base nodes, and the Annex nodes come on top. "13 fights at most" is wrong, because the table has only about 9 fight-capable layers.
2. **BLOCKER, §3.1 vs. §3.4 fairness.** The solver checks the climb offsets +2 and +4. A climb adds 2 steps, but only one climb at +2 is modeled for the other layers, and the arrival check uses `step+2`. A climb that fails on the beam ("sent back down… with the loss of the climb") is a trap, yet 3.4 says "the check is a plan, not a gamble". Climb A also skips L4–L9, not "6 layers" with an arrival at L10, and the solver isn't shown to check the arrival node. Add arrival validity to the solver.
3. **MAJOR, R1/R4, §3.2.** "Normal fights otherwise have no enrage"; the draft gives normals an enrage at turn 5. R4 sets Normal to "off". Also a 1-phase normal gets +0.7 turns, giving 4.2 turns against the 3–4 target. This is a stated overshoot, but the Enforcer's 12 HP adds on top of the R2 band, and the draft claims the enemy HP is unchanged. The Enforcer is a satellite with its own HP.
4. **MAJOR, §3.2 Blade, R8/R11.** TIER_DOWN is applied "for that turn's resolve", not stored. The fallback "PARASITE halves output" is not "reads the same": it is a different rule (an output cut, not a tier cut). The Blade is also a hit on every Spotted turn, so for the reference player it is intake with no counter on a given slice (see 4).
5. **MAJOR, §3.2, N-tags.** The Enforcer's flat amounts (3 and 3, "×2.2") are fine. But "N4 data-only if class defaults exist" is wrong: N4 is a new system (`EnrageData`), so there is no data-only path.
6. **MAJOR, §3.3 Boss tie-in.** Enrage turn "10 − (Alert − 1), minimum 6" is undefined at Alert 1 (formula gives 10, fine) but it edits R4 per fight, and this is a boss-draft decision. The HQ draft shouldn't set it. Mark it as an input only.
7. **MAJOR, §3.3 Lockdown.** "Alert resets to 2" combined with "+2 per Stall" and the Alert floor on retry (up to 3) gives a Warden fight on nearly every run. Elite-strength fights at +1 Alert each can chain.
8. **MAJOR, §8.** "NEW: node access rules" is a new system without justification as separate from N16/`map_graph`. The Alert floor carries across runs and needs a profile or campaign field, with no tag.
9. **NIT, §1.** "Climbs run straight up the outside of a face" and a "blade line" are art terms, but a Spotted fight is a different mechanic from the art blade.
10. **NIT, §5.** HP total (35+24+14+9=82, plus 16 for the Antechamber = 98) is consistent. But §5's "Normal fights 5" doesn't match the table (typically 4 Routers on a path).
11. **NIT, §3.1.** The shuttered Terminal and Mainframe mean the run can lose all healing (L5, L9, L11). The solver checks only "one unblocked option", not that a rest remains reachable.

## Concrete fixes
- **#1:** Replace the guarantee line with: "Rests: L5, L9, L11. Elite: L4, L6, L7, L10 (L5, L8, L9, L11 are non-Elite by table)." Fix the totals to "30 nodes base (33 with all three Annexes); at most 10 fight-capable layers (L1–L4, L6, L7, L8, L9, L10, L11) plus the Antechamber and the boss".
- **#2:** Add to the solver: "A phase is valid only if each climb's arrival node at `step+2` is neither BLOCKED nor the only kind it must be (shuttered) and a fight arrival is allowed; a climb whose arrival fails at build is not drawn." Replace the failure rule with: a climb is never offered if its arrival is ON THE BEAM, so a failed climb can't happen.
- **#3:** "Spotted normals: enrage Start 5, Every 5, Step 25 %. This is a Spotted-fight rider, an explicit exception to the R4 class default, and the draft must say so." Add: "Enforcer HP is part of the phase budget; the normal's HP is trimmed by the Enforcer's 12 so the total stays in the 56–70 band."
- **#4:** State the fallback honestly: "PARASITE ×1 is a fallback with a different rule (−50 % output); an N8/N9 migration is needed for TIER_DOWN".
- **#5:** "N4: no data-only fallback; without it, Spotted enrage is dropped."
- **#6:** "Output to the boss draft: `starting_alert` only. The boss draft decides its enrage effect."
- **#7:** "Alert resets to 0 after a Warden fight; Stall costs +1; the retry floor is capped at 2."
- **#8:** "Alert floor: NEW: profile field `hq_alert_floor`; node access: part of N16 `map_edits`".

## Keep
- A gaze that is a pure function of (phase, step): previews equal results, and the solver is exact.
- The consequence split (spotted / shuttered / blocked) that gives every node a clear state.
- The Annex-per-Exploit design that gives each Exploit a use inside the HQ.

## Q:
- Should an Alert-driven boss enrage live in the HQ or the boss draft?
- Is the retry Alert floor compatible with "fresh route each retry"?
- Do shuttered rests risk a no-heal path that the solver must also prevent?
