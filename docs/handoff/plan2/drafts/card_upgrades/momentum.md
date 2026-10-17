<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__momentum; status ok; tokens in 5156 cache-write 0 cache-read 32585 out 1215; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: momentum

1. **Role:** Cheap combo spin for a shared pool. It is a small spin alone and a big spin (5) after any earlier spin this turn. It rewards sequencing spins and nudging into place with a cheap action.

2. **Upgraded card: Momentum+** (one level only; no further levels needed)
- **RAM cost:** 1 (unchanged)
- **Cycle cost multiplier:** ×1.5 (55 → 83)
- **Text:** "Spin 3 ticks clockwise; spin 6 instead if you already spun this turn. The first time this turn this card is played after a spin, refund 1 RAM."
- **Effects:** one CUSTOM effect (same `momentum_handler`).
  - type CUSTOM, target TARGET_WHEEL (2, unchanged), ring_scope WHOLE_WHEEL
  - amount = 3 (base spin)
  - multiplier is unused by the handler's math; keep it for the combo ratio, 2.0 (6 ÷ 3). The handler reads amount × multiplier as the combo spin: 3 × 2.0 = 6.
  - New field `refund_ram` = 1, applied only on the combo branch. This needs a handler param, not a new EffectType. If the handler cannot take params, use a second effect: GAIN_RAM, target SELF, amount 1, gated by the handler's combo flag.
  - status NONE, duration_turns 0, no amount mode (all values are flat ticks).
- **exhaust:** false
- **wheel_target:** 2 (unchanged)

**Why not strictly dominant:** the base spin (3) and the combo spin (6) are only +1 tick each over today's 2 / 5. The refund makes a combo chain nearly free, but only on the second and later plays. Played alone it is a 1 RAM spin 3, the same as Jolt. The costlier Cycle price is a real tradeoff, and a 6-tick spin loses the 5-tick granularity (5 is exactly one slice on a standard wheel). That makes it a sidegrade for players who need the 5-tick spin to land a slice centre.

3. **Interplay:**
- **Variable slice sizes (N12):** fixed 5-tick spins stop mapping to one slice. A 6-tick combo lines up with 6-size slices, and the 3-tick base lines up with 3-size slices.
- **Corrupted RAM:** the refund offsets the 2× RAM on a CORRUPTED slice, so it gives some relief when the slice is taxed.
- **Resistance:** the larger spin gets more past resistance, since the first R ticks are absorbed.

4. **Data:**
- `id`: `momentum_plus` (new file; the base file stays)
- `display_name`: "Momentum+"
- `description`: as above
- `cycle_cost`: 83
- effect `amount` 2 → 3, `multiplier` 2.5 → 2.0
- plus the refund (handler param, or a second GAIN_RAM effect)
- `rarity` and `offered` are unchanged; the + version is not offered in rewards (upgrade only).
- **Systems:** none new for the spin. The refund rider needs a small handler change (data-only fallback: drop the refund and keep only 3 / 6, which is a pure bigger-number upgrade).

5. **Q:**
- Should the refund apply to the first spin of the turn too, or only the combo?
- Does a Spin granted by a Firmware/Daemon (e.g. `+1 spin on all cards`, the Breaker Hub Core) count as "already spun" for the combo?
