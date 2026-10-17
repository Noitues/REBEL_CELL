<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__twist; status ok; tokens in 5087 cache-write 0 cache-read 32585 out 1133; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: twist

**Level note:** one + version is enough. Twist is a 1-RAM filler, so a second level would only inflate it.

1. **Role.** Twist is the cheap, mid-size clockwise spin. It sits between Jolt (3) and Brute Spin (6) and lets any deck re-aim a wheel for 1 RAM. It is neutral, so Botnet and Hivemind use it to line up a slice without spending nudges.

2. **Upgraded card: Twist+**
- **Name:** Twist+
- **RAM cost:** 1 (unchanged)
- **Cycle cost multiplier:** ×1.5, so 75 Cycles (base 50)
- **Text:** "Spin a wheel 4 ticks clockwise. Your next nudge this turn is free."
- **wheel_target:** ANY (unchanged, value 2)
- **exhaust:** false
- **Effects:**
  1. SPIN, target TARGET_WHEEL (2), ring_scope WHOLE_WHEEL, amount 4. Unchanged.
  2. CUSTOM rider "next nudge free", target SELF, amount 1 (see §4).

**Why this rider:** the spin gets you near the slice, and the free nudge pays for the last tick or two. That is a wider reach for the same role. It is a sidegrade against Calibrate and Torque Wrench because it grants only one free nudge and needs a spin. It does not dominate at every cost point. It does nothing if the free nudge is already unspent, and Twist at 1 RAM remains the better pick on a wheel that needs only the spin. It is also weaker than Torque Wrench (5 ticks, 1 RAM, class-locked) in raw reach.

3. **Interplay**
- **Tick quality / variable sizes:** with 4-tick slices (no Perfect) or 3-tick slices (G P G), a single-tick correction decides the tier. That makes a free nudge worth more than the spin itself.
- **Corrupted slices:** a nudge made while the pointer reads a CORRUPTED slice costs 2× RAM. A free nudge there is worth 2 RAM, so Twist+ is a quiet counter to the corruption tax. It must not make the free nudge a refund of the doubled cost, only waive it.
- **Blocked or locked wheels:** if the nudge is locked (N7), the rider is wasted. The preview should say so.

4. **Data**
- Changed: `id twist_plus` (a separate resource), `display_name`, `description`, `cycle_cost = 75`, and one added effect.
- **Dependency:** the rider can reuse the logic behind Calibrate's "free nudges" with count 1. **Data-only fallback:** reuse Calibrate's existing effect type with `amount = 1`. If Calibrate is a CUSTOM handler, point `custom_handler` at it with `amount 1`. The fallback needs no N#. The free-nudge counter must be rewind-clean (an undo restores it) so preview = result.
- No new randomness.

5. **Q:**
- Q: Should the free nudge be restricted to your own wheel (so it can't undo an enemy-wheel spin), or does "next nudge" cover any wheel?
- Q: Does the free nudge stack with the turn's free nudge (a second one) or only fill the turn's first free slot when it is already used?
