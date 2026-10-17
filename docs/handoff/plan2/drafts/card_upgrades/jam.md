<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__jam; status ok; tokens in 5101 cache-write 0 cache-read 32585 out 1234; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: jam

1. **Role:** Jam is the precision tool for enemy wheels. It spends 2 RAM to move one enemy needle one tick, ignoring resistance, usually to push a landing off a Perfect or a dangerous slice. It is the answer to Compliance Lock and Weight.

2. **Upgraded card: Jam+** (a single + level is enough).
- **RAM cost:** 1 (was 2). The upgrade is a cost cut. Jam at 2 RAM competes with a paid nudge at 1 RAM, so Jam only wins on the resistance bypass.
- **Cycle cost multiplier:** ×1.5 (90 Cycles).
- **Text:** "Nudge an enemy wheel ±1, ignoring resistance. Sandbox-proof: the move also ignores Freeze-locks. Exhaust: no."
  - Simplified, final text: "Nudge an enemy wheel ±1, ignoring resistance and nudge locks."
- **Effects (EffectData):**
  1. NUDGE, target TARGET_WHEEL, ring_scope OUTER, amount 1, multiplier 0, status NONE, duration 0. This is unchanged from the current effect.
- **Rider:** the card's own nudge is not refused by `nudge_locked` (N7). This is a flag on the card effect only. Cards already work under Curfew-style locks, so the practical rider is that it also bypasses the enemy listeners' "paid nudge" taxes (Late Fee). It is not a free nudge for ON_NUDGE listeners (N6).
- **Exhaust:** false.
- **wheel_target:** ENEMY (1), unchanged.
- **Why not strictly dominant:** Jam+ stays at ±1 and a single move. Double Jam (3 RAM, two moves) and Ghost Step remain the multi-tick options. Jam+ is cheaper but no stronger per use, so it is a cost-efficiency upgrade, not a reach upgrade.

3. **Interplay:**
- With uneven slice sizes (R11), a 1-tick move often decides a Perfect against a 3- or 5-tick slice. That makes the cheaper Jam+ a strong tempo tool against a narrow Medicine window.
- Against a Compliance Lock (resistance 2) it keeps the full advantage: 1 RAM for what a paid nudge cannot do.
- Corrupted-RAM doubling (R9) applies only to your own slices. Jam+ acts on an enemy wheel, so it is unaffected.

4. **Data:**
- `ram_cost` 2 → 1 and `cycle_cost` 60 → 90.
- `description` changes.
- The `fx` sub-resource is unchanged.
- The "ignores nudge locks" part needs N7 (`nudge_locked`) with a per-effect `ignores_lock` bool (NEW: EffectData.ignores_lock, S).
- **Data-only fallback:** drop the lock-bypass text. The card is then a pure 1-RAM Jam, which is the minimum viable upgrade and still a valid sidegrade.
- Class files `ghost` and `phantom` reference the card id. Add a separate id (`jam_plus`) and keep upgrade mapping outside the class lists.

5. **Q:**
- Q: Should the lock-bypass rider ship at all, since cards already work under nudge locks? Dropping it leaves a pure cost cut.
- Q: At 1 RAM, does Jam+ cannibalise Feather Touch and Ghost Step in the Ghost deck, and should Ghost Step move to 2 RAM when it does?
