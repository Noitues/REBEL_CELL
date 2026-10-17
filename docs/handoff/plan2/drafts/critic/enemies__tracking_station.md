<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__tracking_station; status ok; tokens in 4859 cache-write 0 cache-read 32585 out 1697; cost $0.017. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/tracking_station

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 geometry / R11 / R10.** The draft's own centre list contradicts the layout and the "needle 11 sits on the Flare's Perfect-centre" claim. Boundaries from the table: Ping 0-3, Lock-On 4-8, Flare 9-13, Dish 14-17, Ping 18-23, Null 24-29. The Flare is 5 ticks (9-13), centre 11, so the claim holds. But tick 0 is not "Ping's WEAK edge": the Ping spans 0-3 (4 ticks, W G G W), so tick 0 is its WEAK edge only by coincidence. The text also leaves a stray "2, 6.5→ computed" fragment. The claim "no rotation where both needles are harmless" is asserted, not shown. A Null (6 ticks) and a Dish (4) are 9-10 ticks apart in the layout, so needles 11 apart land on Null + a Ping/Dish edge at some rotations. Verify and show the table.
2. **BLOCKER, §2 vs §1 (Flare on needle 11).** The Flare needle starts on a Perfect landing of the status slice, but §1 calls the Flare the "dangerous" needle. Fine, but the effect is undefined: "your slice under the pointer" is ambiguous between your pointer and the enemy needle. Spell it out.
3. **BLOCKER, §3 arithmetic.** Intake sum: 20+60+10+0+30+0 = 120, /30 = 4.0. OK. But the draft says T3 uses ×1.69 and then gives T3 "~8-10", while 8.0 × 1.69 = 13.5 unsteered. T4 (×2.2) would be 17.6, not 13. The numbers are inconsistent, so the §10 win-rate reasoning (T4 13 × 3.8 = 49) is unsupported.
4. **MAJOR, §3 sustain.** "0 of 9" is meaningless; just say 0 %, with no heal source.
5. **MAJOR, §4 phase budget.** The formula requires multiplying by "needles the player's hits land on". The draft never settles it ("conservative factor 1.0"), and the pointer rule (GDD 2.7) says the player's hit lands once per *enemy* needle: 2 needles = 2×. HP of 9 × 3.5 × 2 = 63 at T1 would exceed the band. The draft's HP values work only if the multiplier is 1. State plainly that HP follows the band, since a 1-phase normal's band already covers 2 hits, and drop the pseudo-derivation. T4 = 63 is within 56-70.
6. **MAJOR, §8 fallback.** The fallback is "keep hp = 50" and the "OVERCLOCKED" substitute is not data-only for a normal (it burns into CORRUPTED, which R9 now makes a RAM tax). Use a PARASITE status, which exists.
7. **NIT, §1.** The siblings paragraph is filler. The layer claim is "L3-5", while the brief names L1-2 teaching / L5-6 pressure; a normal that teaches uneven needles belongs in L1-2.

## Concrete fixes

- **§2:** replace the geometry paragraph with: "Boundaries: Ping 0-3 (c 1.5, no Perfect), Lock-On 4-8 (c 6), Flare 9-13 (c 11), Dish 14-17 (c 15.5), Ping 18-23 (c 20.5), Null 24-29 (c 26.5). Needles 0 / 11: rotation 0 reads Ping-W + Flare-Perfect; rotation +6 reads Lock-On-P + Dish; rotation −3 reads Null + Lock-On. Worst safe pair: Null + Dish-edge (cost 1 nudge)." Verify with the sim.
- **§2 Flare:** "Flare: 2 damage + OUTPUT_DOWN ×1 on the player's slice under the matching pointer."
- **§3:** T1 8.0, T2 10.4, T3 13.5, T4 17.6 unsteered per turn; steered ≈ 40 %. Then redo §10 (T4 win likely below 88 %; lower Lock-On to 10).
- **§4:** "Normal band applies; no needle multiplier."
- **§8 fallback:** the PARASITE status.
- **§1:** change the layers to "L1-2 teaching".

## Keep

The uneven 0/11 needles over a layout with a Perfect-centred status slice is a real question, not attrition. The no-sustain, no-enrage framing is correct, and the 4-tick no-Perfect Ping uses R11 well.

## Q:

1. Does the unsteered intake at T3-T4 (13-18) breach a 90 % win target without a Lock-On cut?
2. Should the Flare use TIER_DOWN to better suit the "tracking" theme?
