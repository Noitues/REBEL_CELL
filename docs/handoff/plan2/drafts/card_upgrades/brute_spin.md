<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__brute_spin; status ok; tokens in 5144 cache-write 0 cache-read 32585 out 1091; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: brute_spin

1. **Role**: A mid-cost, fixed-size clockwise spin (6 ticks, +1 for Breaker) that aims at a destination slice. It sits between Whirl (7, RAM 2) and Heavy Spin (9, RAM 2), and is the bread-and-butter "get to the slice two over" card.

2. **Upgraded card**: Brute Spin+ (one level is enough; the card is a plain spin).
   - RAM cost: 1 (was 2). Cycle cost multiplier: ×1.5 (90).
   - Text: "Spin a wheel 6 ticks clockwise. Gain 1 free nudge this turn."
   - wheel_target: ANY (was 2, which is ENEMY by enum order OWN/ENEMY/ANY/SATELLITE... see Data; keep the current value, 2 = ANY).
   - Effects:
     1. SPIN, target TARGET_WHEEL (unchanged, 2), ring_scope WHOLE_WHEEL, amount 6.
     2. Rider: grant one free nudge this turn (the Torque Wrench effect: reuse whatever handler it uses for "gain a free nudge"), amount 1, target SELF.
   - Exhaust: false.

   Why this shape: the cost cut alone would make it a strictly better Whirl-class card. The free-nudge rider makes the spin land precisely: spin 6 gets you near a slice, the free nudge makes it Perfect. That is the card's job, sharpened. It stays a sidegrade against Torque Wrench (Rigger: spin 5 + free nudge at RAM 1) because Brute Spin+ is neutral and moves 6 (7 for Breaker) rather than 5. It does not dominate Heavy Spin or Spin Cycle: the distances differ, and distance is the main reason to choose between spins.

3. **Interplay**: With variable slice sizes (N12), 4-tick slices have no Perfect, so the free nudge matters more there: it moves you off a WEAK edge onto a GOOD tick. The rider is placed after the spin so resistance absorption applies to the spin only, never to the free nudge.

4. **Data**: Changes against the current .tres: `ram_cost` 2 → 1, `cycle_cost` 60 → 90, `description` updated, and one appended EffectData for the free nudge. If the Torque Wrench free-nudge effect is a custom handler or a CUSTOM effect type, reuse it. No new system. If it is only expressed inside a Rigger-specific card text without a reusable effect, the data-only fallback is to reuse that same EffectData shape. Otherwise this needs a small NEW: grant-free-nudge effect (the same one Calibrate uses). Verify before building.
   The note above on wheel_target is only a reminder that it stays at its current value; I'm changing nothing there.

5. **Q:**
   - Q: Should the free nudge be restricted to your own wheel when the spin targets the enemy wheel? (It currently would be unrestricted: it is a turn-level budget item.)
   - Q: Is Breaker's +1 spin bonus (7) enough to want a separate Breaker version, or is the neutral + fine?
