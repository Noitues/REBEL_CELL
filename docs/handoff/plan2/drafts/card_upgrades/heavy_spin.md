<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__heavy_spin; status ok; tokens in 5096 cache-write 0 cache-read 32585 out 1226; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: heavy_spin

1. **Role:** A mid-size whole-wheel spin (9 ticks, 2 RAM) for repositioning a landing across half the wheel in one card. It sits between Whirl (7) and Spin Cycle (12), and it needs no nudge budget.

2. **Upgraded card: Heavy Spin+** (one level is enough; spin cards are cheap and plentiful, so a second level isn't needed)
- **RAM cost:** 1 (was 2).
- **Cycle cost multiplier:** ×1.25 (60 → 75). The RAM cut is the upgrade, so it is priced as one.
- **Text:** "Spin a wheel 9 ticks, either direction."
- **Effect list** (the single `fx` is kept, with one new field):
  - type SPIN, target TARGET_WHEEL (target = 2 stays), ring_scope WHOLE_WHEEL, amount 9, direction CHOSEN_AT_PLAY (clockwise or counter-clockwise).
- **Exhaust:** false. **wheel_target:** ANY (was 2; the current value is unchanged, so the existing target choice is preserved).

*Why this:* the card's weakness is that it is rigid. At 9 ticks, clockwise-only means the same move can't be reached as 21 ticks counter-clockwise, and Backspin (9 CCW) is a separate card. The + gives both directions for 1 RAM, which makes it a Heavy Spin plus Backspin in one slot, and it adds no damage and no new effect.

*Sidegrade, not strict dominance:* the + is slightly worse as a pure deck-thinning pick, since it makes Backspin redundant (that is the point). The 25 % Cycle premium and the loss of the 2-RAM "weight" matter to RAM-starved classes. The + never beats Spin Cycle's range (12), so it doesn't replace the top-end spin.

3. **Interplay:**
- **Variable slice sizes (N12):** 9 ticks no longer maps to a fixed 2-slice hop on a mixed wheel. Choosing a direction lets the player pick whichever landing hits the better sub-tick (Perfect on a 3-tick or 5-tick slice) without spending nudges.
- **Corruption (R9):** a corrupted slice under the acting pointer doubles the cost, so the + goes from 2 to 4 RAM on one. The cost cut therefore matters more than it does for a normal card.
- **Resistance:** the + is still absorbed by the first R ticks, and the direction choice doesn't bypass it.

4. **Data:**
- `ram_cost` 2 → 1.
- `cycle_cost` 60 → 75.
- `wheel_target` stays.
- Description changes.
- Add `direction` to the SPIN effect. **NEW: spin direction choice** (a small field on `EffectData`, e.g. `choose_direction: bool`; `amount` stays positive and the sign is picked at play). It is the same machinery as Backspin's negative amount with a prompt. **Data-only fallback:** author two cards and merge them into one reward in the shop. This is not equivalent, because it keeps two slots in the deck.
- The preview must show both landings; the pick is made before commit, so determinism holds.

5. **Q:**
- Q: Should direction choice become the + standard for the whole spin family (Whirl, Spin Cycle), or is it a special upgrade only for Heavy Spin?
- Q: Does Backspin remain a reward-pool card once Heavy Spin+ exists, or does it become the "base" upgrade path for the same family?
