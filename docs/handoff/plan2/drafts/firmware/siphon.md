<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__siphon; status ok; tokens in 2559 cache-write 0 cache-read 32585 out 1377; cost $0.013. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: siphon

**Verdict:** CHANGE

1. **What it does today:** A SHIM slice heals you 2 on Good or better (trigger 5 = ON_SLICE_TRIGGER, min_tier GOOD, HEAL flat 2). It is the only sustain chip in the pool. Every class runs SHIM slices (Breaker has three), so it is a generic pick. It rewards precision modestly and acts as a mini-lifesteal for a long fight.

2. **Under the new rules:**
   - **Flat 2 is weak.** Player HP is 45–60, so 2 per trigger is about 4%. R1 fights are 3–4 turns per phase, which makes this nearly irrelevant, and "Good or better" is trivial to hit.
   - **Sub-tick quality.** On a 2-tick slice (G G) and a 3-tick slice (G P G) the min_tier GOOD gate never fails. On a 4-tick slice (W G G W) and a 6-tick slice (W W G G W W) it is a real gate. The chip reads as free on small slices and as a precision test on large ones, which is acceptable and even good.
   - **Statuses.** OUTPUT_DOWN scales the damage but not the heal, because the heal is a separate effect. TIER_DOWN makes Perfect read as Good and Good as WEAK, so Siphon fails against it. That is the right anti-firmware interaction. Say so on the chip. CORRUPTED doubles the RAM cost of acting there but does not touch the heal.
   - **Parasites.** A Parasite that cuts damage to the boss leaves the heal untouched. That is a feature, since Siphon is a counter to attrition parasites.
   - **Degenerate risks.** Multi-hit riders (N20 `hits`) could fire once per slice trigger, not per hit, so there is no loop. Retrigger effects (Breaker's Perfect hook, Mirror) would double the heal. That is fine at 2 flat but dangerous as PERCENT, so cap it.
   - **Phase parking (R3).** Heal is not blocked while the enemy is parked. A player could sit at a floor and farm sustain against an enemy without a damage clock, but enrage (R4) stops that.

3. **Proposed spec:**
   - **Description:** "SHIM slice heals you 4% of max HP on Good or better (Perfect: 6%). Once per slice resolution."
   - amount_mode PERCENT: 4% on Good, 6% on Perfect (two triggered effects, min_tier GOOD and PERFECT, the Perfect one replacing the Good one). Round up, minimum 2.
   - On a 60 HP operative this is 3 per trigger, 4 on Perfect, so about 5–7% across a turn of two SHIMs. That stays under the 30% sustain limit (R1 question 3).
   - Rarity 0 → 1 (uncommon), Cycle cost 100 → 110.
   - allowed_slice_types stays [0].
   - Heal is capped at once per resolution, so a Mirror or retrigger copy does not stack it. Heals are never scaled by tier (percent, per R2).
   - **Reads on the slice:** a heart pip on the slice. The Good/Perfect tiers show in the tick map. On slices smaller than 4 ticks a small note says "always Good".

4. **Data:** `triggered_effects` gets a second TriggeredEffectData (min_tier 2) and `amount_mode` PERCENT on both effects (N1, S). The once-per-resolution cap is a `max_per_resolution` field on TriggeredEffectData (NEW: small trigger cap, S). The fallback is to drop the cap and keep FLAT 3 / 5, which is data-only.

5. **Q:** Should a heal-on-hit chip be allowed to heal while an R3 floor holds the enemy, or should healing pause while the boss is parked?
**Q:** Is 2-tick "always Good" intended as a cheap discount for tiny slices, or should Siphon be disallowed on slices under 4 ticks?
