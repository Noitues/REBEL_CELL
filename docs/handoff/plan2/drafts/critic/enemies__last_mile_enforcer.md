<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__last_mile_enforcer; status ok; tokens in 5854 cache-write 0 cache-read 32585 out 1996; cost $0.019. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/last_mile_enforcer

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 P2 layout arithmetic.** Ticks are 7+3+4+4+5+4+3 = 30, which is correct. But the 7-tick Overflow is centred where the P2 needle sits (needle at 0 on a 7-tick slice's centre) and is a guaranteed Perfect. The "Perfect ×1" note is meaningless, and the 16-damage Overflow gets a Perfect on needle 0 at turn start. Slice centres are also never stated, so "boundary between Shim and Defrag" for tick 12 cannot be checked (7+3 = 10, Shim spans 10-13, so tick 12 is inside the Shim, not a boundary).
2. **BLOCKER, §2 P1 layout arithmetic.** 5+4+5+4+6+6 = 30, fine. But the claim that "most needle ticks fall on the WEAK edge" of the 4-tick Overflow is false: a 4-tick slice is W G G W, so only 2 of 4 ticks are WEAK. Also, "visits a damaging slice about 4 of 6 turns" is wrong: three damaging slices (Shim, Shim, Overflow) of six, and by tick share 13/30.
3. **BLOCKER, R2 phase budget (§4).** The sums are 63 at T1 but the HP column is 64, which is acceptable. T4 is 126 − 8 = 118, yet the table says 128. T3 is 98 − 8 = 90, not 100. T2 is 77 − 8 = 69, not 78. HP is inflated above the shown arithmetic. Also, P2 has 2 needles, and R2 gives more HP for more *enemy* needles only if the player's hits land on them. The draft says "no adjustment", which contradicts the R2 rule that more needles on the enemy wheel get proportionally more HP.
4. **MAJOR, R1/R3 phase length and the threshold.** P2 is a 50 % phase with the same budget as P1, but the "Perfect-block" listener is ruled sustain-adjacent and is subtracted without being capped per turn consistently (8 per resolve vs 2.3/turn). Also, the cap check divides by DPT 14 at T3, and 2.3/14 = 16 %, fine, but the listener is not applied in P1.
5. **MAJOR, R8/N10, Cite.** "Parcel Hold: OUTPUT_DOWN" is a status, fine. But §1 says P2's needle "latches onto the first slice it lands on" and "every escort kill or Perfect redirects it", while §2 says needles are fixed with no latch and no escort in P2. This is internally contradictory, so the P2 question is undefined. The transition's "pointer_orbit_per_turn = 0" is an invented field (the existing field is the PointerBehavior enum).
5b. **MAJOR, "SANDBOX scarce".** §9 removes a "Sandbox 8 slice in P2" that is not in the draft. The current .tres is not shown, so this is an unverifiable claim.
6. **MAJOR, §8 N# tagging.** The escort drone is existing satellite content. A "respawns every 3rd turn" is a new system with no N# or NEW tag (the N13 satellite rules cover fixed and replaced, not respawn). `max_active` is also invented. "Intake above zero" for P1 mixes raw and post-block figures.
7. **MAJOR, §9.** The heat_effects decision is hedged ("if the live file carries any"). The brief demands a decision. "R2 buffs are tier-independent" is also a misquote.
8. **NIT, §7.** "Flip" is blocked by resistance only, so it is fine. "Cleanse stacked OUTPUT_DOWN" is OK. Section 10 says "132 HP is ~9.4 turns", which is consistent.

## Concrete fixes

- **P2 layout:** reorder so the needles at 0 and 12 land on different value slices: Overflow 5 (ticks −2…2, centre 0, still Perfect at 0, so instead put Shim 4 first). Replace the table: Shim 4 · Overflow 6 · Cite 3 · Defrag 4 · Null 4 · Overflow 5 · Shim 4 = 30. Centres are 2 / 7 / 11 / 15 / 19 / 23.5 / 27. Needle 0 reads Shim, WEAK edge, and needle 12 reads the Cite, WEAK. State the centres in the table.
- **P1 text:** "an Overflow of 4 ticks has no Perfect; 2 of its 4 ticks are WEAK. Damaging slices cover 13 of 30 ticks."
- **HP:** the arithmetic gives T1 63−8 = 55 → use 58 (band 56-72), T2 77−8 = 69 → 70, T3 98−8 = 90 → 92, T4 126−8 = 118 → 120. For P2 with 2 needles, add 15 % to P2's share and show it.
- **Latch contradiction:** delete "latch" from §1 and the transition. P2 question: "Which of the two needles takes the Overflow?"
- **Escort:** tag "respawn" as NEW: satellite respawn, fallback: no respawn (P1 escort fixed once, N13).
- **heat_effects:** "Retire. Heat already acts through the global modifiers."

## Keep

The orbit readable-ahead P1 and the uneven two-needle P2 are distinct from other Meridian elites and ask different questions. The anti-Perfect pressure in P2 is a good idea. The fallback ladder in §8 is honest.

## Q:

Q: Should the Perfect-block listener count its cap per turn or per resolve?
Q: Does the escort survive the P1 to P2 override or get dropped?
