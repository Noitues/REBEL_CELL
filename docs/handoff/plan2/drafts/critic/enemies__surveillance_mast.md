<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__surveillance_mast; status ok; tokens in 5306 cache-write 0 cache-read 32585 out 1761; cost $0.017. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/surveillance_mast
**Verdict:** FIX

## Issues
1. **MAJOR, R2 / §4 / intake math.** HP is computed as dpt × 3.5 × 0.85 and then "clamped to the band floor", but the table values (30, 36, 46, 58) are neither the discounted numbers nor all at the floor. The 0.85 "uptime discount" is invented. R2 gives the formula dpt × turns × needles landed, minus sustain. The result is still in band, but the arithmetic as shown doesn't produce the numbers. T4 raw 63 sits in band (56–70), so the discount is unnecessary.
2. **MAJOR, §3 intake.** Intake is computed as if the enemy needle landed on a random slice "per turn" from tick 0. The draft's own text says the orbit is known and steerable, so the landing is not a 4/30 lottery. The probabilities (5/30 × 9 × 0.8 = 1.2) mix the weights wrongly: a 5-tick slice with W G P G W gives a mean multiplier of (0.5+1+1+1+0.5)/5 = 0.8, which is fine, but "4/30 × 14 × 0.75" for a 4-tick W G G W slice should be 0.75. The Citation "tax ~1.5–2" is unquantified. The T2–T4 intake uses 1.3 steps (3.4, 4.4, 5.7) instead of the R2 table [1.0, 1.3, 1.69, 2.2], so T3 and T4 are wrong (4.4 and 5.7). Replace with 2.6 × 1.69 = 4.4 and 2.6 × 2.2 = 5.7. Those are actually right; the T2 figure 3.4 is also correct. The real gap: the sentence says "×1.3 table", which names the wrong table.
3. **MAJOR, §1 / R10 / N11.** "N11: not needed", yet the stated mechanic is an orbiting needle. Orbit already exists (GDD 2.11), so that holds. But §1 says "its pointer moves after the start-of-turn respin", which contradicts GDD 2.2 (every wheel respins at turn start and the orbit then applies). It also says layers L3-4, which fits neither "L1-2 teaching" nor "L5-6 pressure" in the template. Pick one.
4. **MAJOR, design quality.** Defense is a two-Detour 33 % gate plus a 3.5-turn fight. The "answer that shortens the fight" is hard to tell apart from simply attacking on a turn when the Detour is off the needle; that is mostly a single-turn timing check, not a question that lasts 3–4 turns. Detour ticks (4 + 6 = 10) also create an uneven risk: the player cannot know which Detour will be read without reading the trail, but the draft doesn't say the trail shows slice identity.
5. **MAJOR, R8 / §2.** Citation is described as OUTPUT_DOWN ×2 on a random non-NULL slice, while §11 Q1 proposes UNDER_POINTER. A random pick leaves the player no deterministic counter, and the preview must equal the result, so RANDOM_NON_NULL needs a named RNG stream at a checkpoint. Say which stream.
6. **NIT, R11.** The 6-tick slice is labeled "W W G G W W". R11 gives the 6-tick default map as W W G G W W; correct. The 4-tick Overflow with no Perfect is a deliberate choice, but it is not a "Weak edges halve it" case: halving applies to W only.
7. **NIT, R13.** The draft states Detour as "SANDBOX" in the table while the enum remains DETOUR; fine, but keep the display-name note.
8. **NIT, §9.** "Today's 44" is asserted without a file check.

## Concrete fixes
- §4: replace the table with raw values: T1 9×3.5 = 31.5 → **32**; T2 38.5 → **38**; T3 49 → **48**; T4 63 → **60**. Delete the 0.85 factor and the clamp sentence. All values are in band.
- §3: state "damage factors [1.0, 1.3, 1.69, 2.2]" and give the Citation tax as OUTPUT_DOWN ×2 = −50 % on one of 5 non-NULL slices, about 10 % of total output per landing.
- §1: set layers to "L2-4 teaching, L5-6 pressure at tier HP"; drop "moves after the respin", say "orbits +2 at end of turn after the turn-start respin".
- §2: Citation = APPLY_STATUS OUTPUT_DOWN ×2 on the slice under your pointer (UNDER_POINTER). This is deterministic, and the preview shows it.

## Keep
- A single orbiting needle with a visible trail is a clean, readable question with no new systems.
- The uneven Detour spacing and wide Null give a legible safe stretch.
- A full data-only fallback is listed per dependency.

## Q:
1. Does the trail show the identity of the slice the needle will read, or only its tick?
2. Should the Detour (SANDBOX) at WEAK tier still negate fully?
