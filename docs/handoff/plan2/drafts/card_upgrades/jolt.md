<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__jolt; status ok; tokens in 5218 cache-write 0 cache-read 32585 out 1190; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: jolt

1. **Role:** Cheap, small whole-wheel spin. It is the fine-tuning tool for landing a pointer when a nudge is not enough, and it is cheaper than Twist (4) or Brute Spin (6). It works on either wheel (wheel_target ANY).

2. **Upgraded card: Jolt+** (one + level is enough; it's a 1-RAM filler, so a second level adds nothing)
- **RAM cost:** 1 (unchanged).
- **Cycle cost multiplier:** ×1.5 (50 → 75), because the rider has real value.
- **Text:** "Spin a wheel 3 ticks in a direction of your choice."
- **Effects:** one EffectData.
  - type SPIN, target TARGET_WHEEL, ring_scope WHOLE_WHEEL, amount 3, no status, no duration.
  - New field on SPIN: `direction_choice` = true. The player picks clockwise or counter-clockwise. The amount stays 3.
- **Exhaust:** false.
- **wheel_target:** ANY (unchanged).

**Why a rider and not a bigger number:** a bigger number would erase the line between Jolt and Twist. Choosing the direction gives it reach: 3 CW or 3 CCW (= 27 CW), which covers many more landings than the base card. It is not strictly better in every spot. It adds no raw movement, and it doesn't beat Counter-Spin (5 CCW, 1 RAM) when you need 5 or more. Base Jolt keeps one use: a wheel under a Flip or direction lock with no choice would be identical, so the + is never worse, but the ×1.5 Cycle price is the tradeoff.

3. **Interplay:**
- **Variable slice sizes / tick quality:** with 2–4 tick slices and no-Perfect maps, a precise 3-tick move in either direction matters more. It also helps the player land on the single Perfect tick of an uneven wheel.
- **Corruption (R9):** a spin is a card, so it costs 2 RAM if the acting pointer reads a CORRUPTED slice. That makes the + less efficient there.
- **Resistance:** unchanged. The first R ticks are absorbed, so 3 ticks against resistance 2 moves 1.

4. **Data:**
- Changes to `jolt.tres`: new `upgraded` variant file `jolt_plus.tres` (id `jolt_plus`), `cycle_cost = 75`, description updated, and the effect carries `direction_choice = true`.
- **New system:** a `direction_choice` bool on `EffectData` for SPIN. This is NEW: choosable spin direction. It needs a UI prompt on play (the same pattern as the CHOSEN slice pick), and the preview must show both outcomes. It is deterministic, since the player picks it and there is no RNG.
- **Fallback (data-only):** two sign variants as two effects. That doesn't fit because only one should apply. A data-only alternative is the amount −3 (CCW) as a separate card, which is a different card. There is no clean fallback.
- The upgrade link from base to + needs the upgrade-pass field (the card-upgrade pass, not N#).

5. **Q:**
- Q: Should direction choice become a general SPIN rider for the whole spin family (Twist+, Whirl+) rather than a one-off here?
- Q: Should the + keep ×1.5 Cycle, or sit at ×1.25 given Jolt is a 50-Cycle card?
