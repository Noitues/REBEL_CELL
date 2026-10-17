<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__parking_warden; status ok; tokens in 5196 cache-write 0 cache-read 32585 out 1844; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/parking_warden

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 layout, tick sizes.** The table lists 7 slices (5, 4, 5, 4, 5, 3, 4), which sum to 30. The 5-tick slices carry W G P G W and the 3-tick slice carries G P G, so those maps are right. But the fallback in §8 ("6 slices, drop the second Shim into Null") is a separate layout and is not specified, so it cannot be checked. Also, with a single needle at tick 0, the 3-tick Citation is the only slice with a Perfect that matters for stamping; the draft says the stamp is "never precisely delivered" only for slice 2. This is a nit, not an error.
2. **BLOCKER, §3 intake arithmetic.** The tick-share chances are right: 10/30 × 6 = 2.0, 7/30 × 3 = 0.7, 4/30 × 10 = 1.33, total 4.0. But "~3.5 after Overflow edge halving" is wrong. The Overflow slice is W G G W, so half its landings (2 of 4 ticks) are WEAK at 0.5×: 1.33 × 0.75 = 1.0, and Shim edges (W on 2 of 5 ticks) also drop. The 3.5 figure is unshown, so show it or drop it. The T4 intake of 8.8 also double-counts: R2 scales flat amounts by the tier damage factor, so 4.0 × 2.2 = 8.8 is correct, and the number should not be called "before weighting".
3. **MAJOR, §4 HP.** The budget is miscomputed. R2 subtracts sustain per turn × 3.5. Here sustain is declared "0", yet the table subtracts 3.5 ("credit the BLOCK as ~1/turn"). Block is not sustain in R2 terms, and the draft contradicts itself (§3 says 0). It also says "round up to the band" from 28 to 32, which is unjustified. Fix the arithmetic and the contradiction.
4. **MAJOR, §2 hub.** The hub row contains a muddled "Ticket Book (listener, N6) … Keep it simple: no hub." This is leftover drafting. Delete it. §1 also mentions a "ticket counter (see the hub below)" that does not exist.
5. **MAJOR, §8 systems.** N8 and N9 are listed, but OUTPUT_DOWN ×1 is a stack count of one, and the fallback keeps PARASITE (halve), which is the old rule, not the one R8 describes. State that N8 is not strictly needed for a single stack (N9 only). The N12 fallback is underspecified as noted above.
6. **MAJOR, design quality.** The random Citation (slice 2) has no counter besides Cleanse, which is not guaranteed in L1-2. The Q about Cleanse availability confirms this. A teaching enemy should not present an unavoidable cost. The OUTPUT_DOWN ×1 at −25 % for roughly "1-2 damage per turn" is also unquantified.
7. **NIT, §3.** The statement "Over 3.5 turns ≈ 12-14 HP lost" is inconsistent with 4.0 × 3.5 = 14 only at the top end. Say 14.
8. **NIT, §7.** "Killing in 3 turns requires roughly 11 average at T1" fits 32 HP / 3 = 10.7. Fine.

## Concrete fixes

- **§2 hub row:** `Hub rule | none (pure wheel; L1-2 baseline)`. Delete the "ticket counter" mention in §1.
- **§3 intake:** replace the WEAK note with: "Expected after tier weighting (Shim edge 2/5 WEAK, Overflow edge 2/4 WEAK): Shim 2.0 × 0.8 = 1.6; Overflow 1.33 × 0.75 = 1.0; Citation 0.7; total ≈ 3.3 at T1; ×1.3 / ×1.69 / ×2.2 → 4.3 / 5.6 / 7.3."
- **§4:** set sustain to 0 and reduce the BLOCK line to "BLOCK is not sustain." Budget: T1 9×3.5 = 31.5 → **32**; T2 38.5 → **38**; T3 49 → **48**; T4 63 → **62**. All are inside the R2 band.
- **§8:** "N9 (OUTPUT_DOWN); N8 only if stacks above 1 are ever used. Fallback: keep 6 × 5-tick slices as Shim, Citation, Defrag, Overflow, Shim, Null; PARASITE as the Citation."
- **§2 slice 2:** make it a lone ENCRYPTED-immune path? Simpler: change slice 2 to UNDER_POINTER as well and drop the random stamp, so every Citation is readable.

## Keep

- Under-pointer Citation as a readable "steer the stamp" question.
- Shorter, Perfect-less Overflow as the reward for nudging its needle.
- No enrage, no heal, and a clear weak-player failure mode.

## Q:

- Q: Should the Warden's Citation ever use RANDOM_NON_NULL in L1-2, given Cleanse is not guaranteed?
- Q: Does a WEAK landing on a Citation still apply its status (R8 Q11)?
