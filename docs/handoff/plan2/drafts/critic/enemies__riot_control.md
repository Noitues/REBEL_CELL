<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__riot_control; status ok; tokens in 5226 cache-write 0 cache-read 32585 out 1724; cost $0.017. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/riot_control

**Verdict:** FIX

## Issues

1. **BLOCKER, R2/§4 arithmetic.** The draft's HP lands above the sums it shows (T1 64 vs ~60, T3 100 vs ~93, T4 128 vs ~120), and the "above the sum so block tax doesn't…" rationale is circular. It also says "needles my hits land on = 2" while the draft's rows (31.5 = 9×3.5) don't use the factor of 2. The formula is applied inconsistently. Either the multiplier is 1 (and the R2 band is the authority) or HP should be roughly double.
2. **BLOCKER, R11/§2 P1 layout.** Barrier 6 + Baton 4 + Barrier 6 + Baton 4 + (nothing) + Null 5 + Shove 5 = 30, but "Citation-lite none" is a phantom slot, and the pointers at 0/15 depend on slice centres that were never listed. The P2 layout (5+4+6+5+4+6) = 30 is OK. The P1 slice list has 6 real slices; state them cleanly with centres.
3. **MAJOR, R2 "flat × tier factor" + §3 intake.** The intake figures are at T1, but the HP and win% claims are for T3/T4. The "7 × tier factor" Baton and "14 × factor" Shove at T4 (2.2) are 15 and 31. The draft cites 31 per hit as dangerous without computing the intake at T4 or the player HP.
4. **MAJOR, R3/R6 transition.** "Enemy block is cleared" has no R-rule basis. BLOCK expires at the start of its owner's turn already. `MULTIPLY`-style needle move "is a pointer re-seat" is vague; specify a `wheel_override` setting the needles to (0, 11).
5. **MAJOR, R8/R9.** Citation is described as both "today's PARASITE becoming ×2 OUTPUT_DOWN" and "authored ×1". Pick one. The random slice pick is a named-RNG question (Q3); resolve it, don't leave it as an open question. Also, "−25 % per stack" is OK, but the draft's "×3" claim is unsupported.
6. **MAJOR, §3 sustain.** Calling Barrier "sustain" and then computing a 30 % cap on block is a category confusion. R2 sustain means heal. State plainly: sustain = 0. The block tax belongs only in the HP budget.
7. **MAJOR, N6 listener.** Riot Response (+6 BLOCK on a player Perfect) conflicts with P2's "no block anywhere", is undefined for a preview (block 6 FLAT × factor?), and punishes the skill the game rewards (Perfect). It is also a dominated choice: never Perfect → no threat.
8. **MAJOR, §9 heat_effects.** "The file shows no heat_effects" is unverifiable from the draft and contradicts "retire". Decide: keep none; state the current data.
9. **NIT.** §1 invents Zoning Board's theme. The "Hold the line." phase line is fine. §10 ignores the baseline. "Elite 142" (R2 table says 271–287 at T3 today) is inconsistent.

## Concrete fixes

- **HP (resolves 1):** use multiplier 1 for the enemy's own needles and say so. Keep 64 / 78 / 100 / 128 as band-inside values; budget text: "T3: P1 14×3.5=49−block tax 5=44; P2 49; sum 93, set 100 (band 88–112)." State that the extra ~7 HP is slack for the 3-turn minimum.
- **P1 layout:** Barrier 6 (c0) · Baton 4 (c8) · Shove 5 (c13) · Barrier 6 (c18)? Rewrite as: Barrier 6 · Baton 4 · Shove 5 · Barrier 6 · Baton 4 · Null 5 = 30. Needles 0/15 land on distinct slices.
- **Sustain:** "Sustain: 0 (no heal). Barrier is defense only; its cost is already inside the P1 budget."
- **Listener:** replace with ON_NUDGE: each paid nudge on its wheel gives the enemy +4 FLAT BLOCK (×factor). That is a RAM-economy question, not a punishment for Perfects.
- **Citation:** author OUTPUT_DOWN ×1 on the slice under the pointer (SlicePick UNDER_POINTER), which is deterministic and previewable.
- **heat_effects:** "Retire; none are carried."

## Keep
- The P1→P2 flip of question (which needle, then which slice to protect).
- The uneven 0/11 needles in P2 and the fallback chain.
- The enrage reasoning (it never fires for a competent player).

## Q:
Q: Is the factor of 2 for "needles my hits land on" meant for enemy needles or the player's wheel?
Q: Should P2 keep resistance 1 at all, given the new nudge listener?
