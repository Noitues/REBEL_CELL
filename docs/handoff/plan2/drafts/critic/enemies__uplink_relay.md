<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__uplink_relay; status ok; tokens in 4734 cache-write 0 cache-read 32585 out 1759; cost $0.017. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/uplink_relay

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 arithmetic.** Layout "Flare 6 · Shim 5 · Flare 4 · Overflow 4 · Shim 5 · Null 6" sums to 6+5+4+4+5+6 = 30, so the sum is OK. The effect text is wrong, though: it says "6 ticks per Flare/Null and 4-5 per other slice", but the intake math uses Shim 10/30 and Overflow 4/30. That leaves 16 ticks for Flare+Null, which is correct. The real defect is that the overclock "gift" never fires. See issue 2.
2. **BLOCKER, §1/§2 design.** The Flare is a pure gift-then-tax with no cost-free answer, and the "cash in" plan is mostly illusory. Flare picks a random non-NULL slice (Shim, Overflow, Defrag, Trojan, etc.), so the player cannot plan to land it. The question reads as luck, not a decision. The weak-player case ("Defrag at 1.5× wasted") also contradicts §2: the Relay's slice-pick is random but it is the player's own wheel. The random pick is not a decision either way (see Q1).
3. **MAJOR, §3 intake and the spec.** Intake is computed as if landing were uniform, but the needle orbits +1 per turn from tick 0 and the player steers, so the "unsteered" figure is not what the reference player sees. The T2–T4 factors 1.3/1.69/2.2 are applied to a base already lowered to Shim 7, which is fine. Flare turns (10/30) cost no HP, so the real intake at T1 is lower than 3.9 if the player ever lands on Flare or Null. Keep the number, but state the assumption.
4. **MAJOR, §4 HP vs R2.** HP is "lower-mid" of the band on the grounds of low threat, but R2 sets HP from reference damage × needles. Using 32/38/48/62 is acceptable (inside bands: 28–36, 34–44, 44–56, 56–70, correct arithmetic: 31.5, 38.5, 49, 63). The justification should be the budget, not threat.
5. **MAJOR, §8 fallbacks.** N1 fallback says `output_scale` does it "today". The R2 fix is the new damage table (N2), so say so. "N9 fallback: Flare is a harsher trap" contradicts the design (old CORRUPTED self-damage would punish the gift). The N12 fallback loses the layout, which is the core of the design.
6. **MAJOR, §9.** "New slice file needed: shim_7.tres, overflow_12.tres" invents content ids without checking existing slice files. Also "Defrag 6 is removed" and "Flare is now two slices" mean the wheel has no defensive slot, but §1 claims no relation to shields. Fine, but verify.
7. **NIT, §2.** "Why these sizes" claims a one-tick nudge moves a 4-tick Overflow onto Null. A 4-tick slice has ticks W G G W, so one tick of nudge only changes the tier. It does not change the slice unless the needle sits on the edge. Rewrite.
8. **NIT, §1.** "Debris Guard" is not a sibling in the inventory (it's orbital_debris). The appearance split between L1-2 and L5-6 is fine.

## Concrete fixes

- **Issue 2:** make the Flare deterministic and chosen, not random. Replace the Flare effect with: "APPLY_STATUS OVERCLOCKED to the slice **opposite** your pointer's current slice (`slice_pick = UNDER_POINTER` on the player wheel, resolved after the nudge window). The preview shows the flared slice before End Turn." Then the cash-in is a real plan: one nudge decides whether to take 1.5× next turn or cleanse. Data-only if the existing `SlicePick` is used; otherwise NEW: slice_pick OPPOSITE_POINTER (size S).
- **Issue 5:** N1/N2 fallback text: "Fallback: enemy `output_scale` per tier until N2 lands." N9 fallback: "Without N9, drop Flare's burn-out to the existing CORRUPTED rule and mark the design provisional." N12 fallback: "Six 5-tick slices; Overflow/Shim question remains, size contrast lost."
- **Issue 7:** "A 4-tick Overflow has no Perfect, and a 1-tick nudge only moves the tier; it takes two ticks to leave it."

## Keep

- The one question (cash in or cleanse) is a clean, teachable L1-2 idea.
- Single phase, no sustain, no enrage, and HP inside each tier band.
- Orbit of +1 per turn gives a readable look-ahead.

## Q:

- Should the Flare target be the player's choice via nudge, rather than random, so the question is a decision?
- Does a flared slice that expires to CORRUPTED still count as "cashed in" if the player lands it on a WEAK edge?
- Is 3.9 intake at T1 enough threat for a teaching enemy?
