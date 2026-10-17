<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__station_commander; status ok; tokens in 6125 cache-write 0 cache-read 32585 out 1956; cost $0.019. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/station_commander

**Verdict:** FIX

## Issues

1. **BLOCKER, R2 phase budget / §4.** The HP table never computes the P1 budget the way R2 says. The draft invents a "×1.5 two-needle factor" instead of "needles the player's hits land on". Its totals (79/96/122/157) exceed the band, and it then clips to the band top "accepting a faster fight". The band, not the sum, is the authority; the sum should be shown to land in the band. The 36/44/55/70 split is also wrong: the HP floor is 50 % of max, so both phases hold equal HP, yet P1 supposedly has the double-needle weighting. Phase shares and budgets contradict each other.

2. **BLOCKER, slice sizes / §2.** P1 layout: "Shim 12 (5) · Defrag (6) · Overflow 16 (4) · Solar Flare (5) · Shim 8 (4) · Null (6)". Sum = 30, but the Shim values are 12 and 8 in the layout and 8 in the table. P2 sizes 6+4+5+6+4+5 = 30, OK. Section 2 says "Shim 12" in the layout and "8 damage" in the table, and §9 says Shim 12 → 8. Fix the layout label.

3. **BLOCKER, R10 and N-tags / §8.** "N11 … fallback: use the existing 0 / 15". Fine. But 4-tick slices "have no Perfect", while Overflow is described as a "readable window" that "never lands as Perfect". Meanwhile P1 Defrag at 6 ticks has a Perfect only at the centre, and the draft's intake math ignores tick quality (WEAK = 0.5×). The intake figures are unreliable.

4. **MAJOR, R9 / R8 consistency.** Detonate is a damage effect keyed to OVERCLOCKED, fine. But OVERCLOCKED also burns out into CORRUPTED, which is now a double-RAM tax. The draft never says that unfired overclocks decay. It also says Detonate "cleanses OVERCLOCKED", while Q2 asks whether it should. Decide.

5. **MAJOR, §3 intake.** The P2 intake arithmetic is wrong. "6+6 ticks × ~4 × 1.5 overclocks ≈ 6 per ground tick → 72" mixes ticks and damage. Correct: Detonate covers 12/30 = 0.4 of reads × (4 × 1.5 = 6) = 2.4. Shim 8×4/30 = 1.07, Overflow 16×4/30 = 2.13. Total ≈ 5.6 coincidentally, but the derivation is invalid. The P1 two-needle intake is not 6.4 either: (8×5 + 14×4)/30 = 3.2 per needle, so about 6.4 is right, but Defrag and Null contribute 0.

6. **MAJOR, hub rule / R4.** P2 "Flare Feed" overclocks a slice every turn at turn start, which means Detonate always has ≥1 hit and the player can never reach zero overclocks, so "cleanse them" is not a stable answer. Say so, or state the Detonate floor.

7. **MAJOR, enemy-owned pointer "Solar Flare random slice".** The random pick should name its RNG stream and the checkpoint; "SlicePick.RANDOM_NON_NULL stream" is not a named stream.

8. **NIT, heat_effects.** "The file has none" is unverified. State that it was not checked, or check it. P1 question text ("Flares overclock your slice") is fine.

9. **NIT, Q section.** Q count is 5; OK. Q4 and Q5 are answerable in the draft.

## Concrete fixes

- **§4 table (R2, equal-HP phases, floor 50 %):** HP T1 64 / T2 78 / T3 100 / T4 128. Budget check: P1 at 2 needles lets hits land twice, so P1 half = 32/39/50/64 and P2 half is the same. At T3: 14 × 3.5 = 49 ≈ 50 ✓. At T4: 18 × 3.5 = 63 ≈ 64 ✓. At T1: 9 × 3.5 = 31.5 ≈ 32 ✓. At T2: 11 × 3.5 = 38.5 ≈ 39 ✓. Drop the ×1.5 factor. Floors are 32/39/50/64.
- **§2 P1 layout:** "Shim (5) · Defrag (6) · Overflow (4) · Solar Flare (5) · Shim (4) · Null (6)", with Shim = 8 FLAT.
- **§3 P2 intake:** Shim 1.07 + Overflow 2.13 + Detonate 0.4 × (4 × k) (k = overclocked count ≥ 1 from Flare Feed; 1.6 at k = 1, 4.8 at k = 3) ≈ 4.8–8 per turn.
- **§2 Detonate:** "consumes the OVERCLOCKED stacks it counts (the 1.5× is lost, so firing first is the answer)."

## Keep

- The two uneven needles (0 / 11) with "one dangerous, one safe" is a good P1 question.
- The overclock-fuel phase link (statuses surviving, no cleanse) is a distinct P2 question.
- Zero sustain and a readable Detonate count.

## Q:
Q: Should Flare Feed be skipped when the player holds ≥3 overclocks, to avoid a runaway?
Q: Does Detonate consume overclocks, or is the damage the only cost?
Q: Is T4 win 80 % acceptable, or should Detonate be 3 per hit?
