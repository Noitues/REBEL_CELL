<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__spin_cycle; status ok; tokens in 5128 cache-write 0 cache-read 32585 out 1142; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: spin_cycle

1. **Role:** The big-rotation tool. For 3 RAM it moves a wheel half a rotation (12 of 30 ticks), usually to carry a dangerous slice off an enemy pointer or a good slice onto yours. It is the most expensive plain spin in the pool and the most overshoot-prone.

2. **Upgraded card: Spin Cycle+** (one level is enough; no ladder needed)
   - **RAM cost:** 2 (was 3).
   - **Cycle cost multiplier:** ×1.5 (65 → ~98).
   - **Text:** "Spin a wheel 12 ticks in a direction you choose. Does not move your inner ring."
   - **Effects:** one EffectData:
     - type SPIN
     - target TARGET_WHEEL (wheel_target ANY, the same chooser as today)
     - amount 12, with sign chosen at play (±12)
     - ring_scope WHOLE_WHEEL
     - no status, no duration
   - **Exhaust:** false. **wheel_target:** ANY, unchanged.
   - **Rider:** a free direction choice, plus a 1 RAM discount. The direction choice is the "wider target" lever.
   - **Why not strictly dominant:** the + version drops the inner-ring lock, so it is a sidegrade for inner-ring users. Today's version moves the inner ring along with the wheel. Make the + variant the same SPIN with ring_scope WHOLE_WHEEL as before, and drop the inner-ring clause from the text. Simplest honest version: keep the inner ring moving as today; the cost is the Cycle price and the loss of nothing. It then dominates at every cost point except Cycles, and the price multiplier is the deliberate trade-off. The text above is therefore revised to: **"Spin a wheel 12 ticks, either direction."**

3. **Interplay:**
   - Variable slice sizes make a fixed 12-tick spin land less predictably, so the direction choice matters more. On a wheel with uneven sizes, choosing ±12 gives two different landing slices, so it is a real decision rather than a cosmetic one.
   - A 2 RAM cost matters under corruption: a corrupted slice under the acting pointer doubles it to 4 RAM, the same as the base card on a clean slice.

4. **Data:**
   - `ram_cost` 3 → 2.
   - `cycle_cost` 65 → 98.
   - `description` updated.
   - `effects[0].amount` stays 12; direction is chosen at play.
   - **New system:** a signed, player-chosen spin direction. This is **NEW: choose-direction spin** (a play-time choice, like SlicePick.CHOSEN). It reuses the existing CHOSEN selection UI. Fallback: data-only, with the + version at 2 RAM and ×1.5 Cycles and clockwise only. That is a pure cost reduction, which remains a valid upgrade.
   - The preview must show both landings so preview equals result. The choice is staged and undoable, with no randomness.

5. **Q:**
   - Is a pure discount (3 → 2 RAM) enough, or should direction choice be a required part of the + version, given the extra UI?
   - Should Spin Cycle+ be priced above Heavy Spin (9 ticks, 2 RAM), which becomes nearly the same card?
