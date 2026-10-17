<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__handler_proxy; status ok; tokens in 4303 cache-write 0 cache-read 32585 out 1721; cost $0.016. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/handler_proxy

**Verdict:** FIX

## Issues
1. **BLOCKER, R2 / §2 slice sizes:** layout is 5+5+4+6+4+6 = **30**, so the sum is fine. But the wheel has 6 slots, with 4-tick slices (W G G W, no Perfect) and one 6-tick. The Overflow "W W G G W W" claim is wrong: R11 gives 6-tick as W W G G W W, which has **no Perfect at all**, not "2 of 6 Perfect-quality". The text contradicts itself and the readability argument.
2. **BLOCKER, §4 HP arithmetic:** the budget is `dpt × 3.5 × needles` minus sustain, giving 31.5 / 38.5 / 49 / 63. Chosen values (34/42/52/66) are all above budget. Tolerance "for block/shield" is unquantified. Defense slices are only 9/30 of landings, soaking about 0.9 dmg per turn at T1, which is under 1 HP over 3.5 turns. Rounding up 2-3 HP is not justified.
3. **MAJOR, §3 intake math:** (5×5 + 13.5×5 + 23.7×6)/30 = (25 + 67.5 + 142.2)/30 = **7.8**, correct. But Shim 8×1.69 = 13.5 and Overflow 14×1.69 = 23.7 are damage, while Leash 3×1.69 = 5.07, ok. T1 "≈4.6": (3×5 + 8×5 + 14×6)/30 = 4.6, correct. T2 (×1.3): 6.0, correct. T4 (×2.2): 10.3, correct. Yet intake of 7.8/turn at T3 against a 3.5-turn fight is about 27 HP, and Overflow alone at 23.7 per hit is a near-lethal spike for a *normal*. At T4, 14×2.2 = 30.8 per hit. That is harsh for a teaching enemy and likely breaks the ≥90 % win bar, which the draft admits at T4 (88 %).
4. **MAJOR, §1 and §7 resistance contradiction:** "Move yours, not its wheel" is fine, but §7 says "Steers its needle off Overflow using Resistance-free nudges on *its own* wheel (their own wheel...)". It is garbled, and "Ghost-class ignore" is correct only for the first nudge.
5. **MAJOR, §7 Leash math:** OUTPUT_DOWN ×1 = −25 %, so "0.75×" is correct. But the Leash targets "the slice under your pointer" at resolve time, so the free nudge only dodges it if the preview shows it, and the result must equal the preview. Not stated.
6. **MAJOR, §8 fallback:** the PARASITE fallback is "stronger, so Leash damage drops to 2". The flat 3 → 2 change is unexplained, and PARASITE halves output (−50 %), which is a different rule.
7. **NIT, §2:** "Defrag/Sandbox" names are old types. R13 names are BLOCK/SHIELD/SANDBOX, and the table calls slice 5 "Sandbox" but gives it SHIELD 5, which confuses the new SANDBOX rule.
8. **NIT, §4:** "T-less value" wording is unclear. The sim row is "no baseline", so ask the sim for it.

## Concrete fixes
- **Overflow slice:** make it 5 ticks (W G P G W) so a Perfect exists, and take the missing tick from Null: Null 5. Sizes: 5+5+4+5+4+5 = 28. Needs +2: Leash 6 (W W G G W W is Perfect-less, acceptable as "weak to read") and Shim 6. Final: Leash 5, Shim 6, Block 4, Overflow 5, Shield 4, Null 6 = **30**.
- **HP:** set hp_by_tier **32 / 38 / 48 / 62** (budget rounded down for the ~1 HP block soak).
- **Overflow:** 14 → **10 FLAT** (T3 16.9, T4 22), and drop the "may need Overflow at 12" note.
- **Fallback PARASITE:** keep Leash 3 damage and say "stronger, accept for the fallback".
- **Rename** slice 3 to BLOCK 6, slice 5 to SHIELD 5.
- **§7:** replace the garbled line with "Use the free nudge on your own wheel (no resistance) to dodge the Leash preview or Overflow."

## Keep
The single-question concept (a status planted on your own pointer slice) is clean, distinct from the mirror siblings, and data-light. The intake math is arithmetically correct. The no-sustain, no-enrage handling is right.

## Q:
- Should the Leash read the slice your pointer is on at resolve (previewable) rather than a "best slice" (opaque)? Choose the former.
- Is a 10-damage Overflow too spiky for L1-2 teaching?
