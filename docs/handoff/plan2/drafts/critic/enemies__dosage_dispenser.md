<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__dosage_dispenser; status ok; tokens in 5928 cache-write 0 cache-read 32585 out 1864; cost $0.019. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/dosage_dispenser

**Verdict:** FIX

## Issues

1. **BLOCKER, R2 phase budget / §4:** The HP table ignores the player's wheel. Budget = dpt × 3.5 × needles, minus sustain × 3.5. The draft sets HP to the raw dpt × 3.5 and says BLOCK "is on me, not its HP" and leaves it out. The same draft then says BLOCK absorbs the player's hits. Under R2, block counts as sustain and must be subtracted. The "+0.3 turn drift" is unsupported.
2. **BLOCKER, §2 hub rule / R9 / N6:** Standing Prescription is not data-only. It needs an end-of-resolve hook on the enemy's own state (N6 covers player-action listeners and ON_HIT_DEALT) and random target picks. Random target picks already exist as SlicePick.RANDOM_NON_NULL, so the hub should reuse that rather than a new "combat RNG stream". The draft invents the stream name and says "data-only" and "N6-style" in the same sentence. It also contradicts its own fallback, which says the hub is dropped if it is unavailable.
3. **MAJOR, §3 intake:** The draft treats the Dose A damage as FLAT 3 and Shim as 5, but §9 says Shim 6 → 5 and Defrag 5 → 6. That is a nerf to Shim made for no stated reason. The intake math also omits the hub dose. At T2–T4 the "×1.3 / ×1.69 / ×2.2" scaling is applied to the T1 result. It should scale only the flat damage, which it does, but the RAM tax is not quantified. The one stated RAM figure ("3 of 5 non-NULL slices by turn 3") is not derived.
4. **MAJOR, §2 vs §1:** The one-question design leans on a "guaranteed 1 per turn" hub dose, so the Dose slices are redundant. P(Dose resolves) = 23 %, yet the hub stamps unconditionally. The wheel then asks no steering question, because the needle position can't avoid the dose. This undercuts counterplay ("steer its needle onto Null"). The draft also contradicts itself: it says the hub doses "if no Dose slice resolved this turn", but §3 says "≈ 1.2 stamps per turn".
5. **MAJOR, §10:** The baseline cited ("2.5 turns, 100 %", "8.0 at T4") is not in the supplied facts. Only "0.05 damage per turn" is. These are invented numbers. The prediction of 3.2 turns at T1 also contradicts the draft's own claim that the damage is "a rounding error". With a 32 HP budget and 9 dpt, 3.5 turns is the design, so say so.
6. **NIT, §2:** The "Standing Prescription" is a name, not a rule, and the text says it should be a placeholder. The Dose B note says "1 tick wide for Perfect… no sub-tick WEAK edge". That is correct for a 3-tick slice (G P G), but it is not a steering problem.
7. **NIT, §4:** "Current hp 38" is stated without a source.

## Concrete fixes

**Fix 1 (HP with sustain).** Expected BLOCK absorbed on the player's hits is 20 % × 6 × factor per turn, which is 1.2 at T1 and 2.64 at T4. Subtract it from the player's damage:

| Tier | Budget (dpt − sustain) × 3.5 | HP |
|---|---|---|
| T1 | (9 − 1.2) × 3.5 = 27.3 | 28 |
| T2 | (11 − 1.6) × 3.5 = 32.9 | 34 |
| T3 | (14 − 2.0) × 3.5 = 42 | 44 |
| T4 | (18 − 2.6) × 3.5 = 53.9 | 56 |

These are the bottom of the band, so sustain makes the enemy weaker, not stronger. Delete "+0.3 turn drift".

**Fix 2 (hub).** Drop the hub rule. Use the fallback as primary: replace the 7-tick Null with Dose C (CORRUPTED FLAT 1, no damage) and shrink: Dose A 4 · Shim 5 · Dose B 3 · Defrag 6 · Shim 5 · Dose C 4 · Null 3 = 30. That is seven slices, which cannot exist under the 6-slice wheel and needs the lifted cap in N12. If the cap holds, use Dose A 5 · Shim 5 · Dose B 4 · Defrag 6 · Shim 5 · Null 5 = 30. P(Dose) = 30 % and the damage stays above zero.

**Fix 5 (baseline).** Replace the baseline column with "today: 0.05 damage per turn" and remove the unsourced turn and win figures.

## Keep
- The one question (corruption as a RAM tax) is clear, and the "you can only lose economically" framing is a good teacher.
- The expected-intake arithmetic by slice size is the right method.
- The explicit fallback table in §8 is good.

## Q:
Q: With the hub dropped, is 30 % Dose odds enough to keep intake meaningful at T1?
Q: Should the enemy slice vocabulary stay six slices or use the lifted cap?
Q: Does a corrupted-slice RAM tax read at L1–2 without a tutorial tooltip?
