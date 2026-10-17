<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__short_circuit; status ok; tokens in 5126 cache-write 0 cache-read 32585 out 1144; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: short_circuit

1. **Role:** The neutral answer to a Hub, in the same slot as Hub Breach but at a higher price. It disables a Hub for 2 turns once per combat, so the player can plan a burst window around a resistance or sustain Hub.

2. **Upgraded card: Short Circuit+** (one level is enough; a second level would only be a bigger number).
- RAM cost: 3 → 2.
- Cycle cost multiplier: ×1.4 (75 → 105). The RAM cut is worth more than it looks, because a 3-RAM card competes with a full turn of income.
- Text: "Disable the target Hub for 2 turns. Take no damage from the Hub's passive... " is *not* used. Final text: "Disable the target Hub for 2 turns. Exhaust. The Hub also loses 2 resistance, permanently." No wait, keep it simple and keep the exhaust:
  **"Disable the target Hub for 2 turns and strip 2 resistance. Exhaust."**
- Effects (in order):
  1. HUB_BREACH, target TARGET_WHEEL, amount 2, ring_scope OUTER (unchanged).
  2. MODIFY_RESISTANCE, target TARGET_WHEEL, amount −2, FLAT, ring_scope WHOLE_WHEEL. The resistance is removed from the wheel's trait resistance too, not only the Hub's. It is permanent for the combat, the same as Strip (so it is restored at the start of each turn only if the trait refreshes).
- Exhaust: true (unchanged).
- wheel_target: ENEMY (1, unchanged).

**Why this and not a pure discount:** the rider is a sidegrade. Hub Breach is cheaper still (2 RAM, 1 turn), and Shatter gives 1 turn plus 1 strip, so the + version is the best 2-RAM Hub answer but still Exhaust and still a one-shot. It does not dominate Deep Strip against a trait-only resistance, because it only strips what the same card's Hub carried first (see Q).

3. **Interplay:** against the Genome Core, it turns off one buff-derived Hub rule such as Metabolism for two phases' worth of turns, but it does not replace the Exploit. Phase transitions with `hub_override` (R6) replace the Hub, so check whether the breach carries over (see Q). Corruption as a double RAM cost makes the 2-RAM version much more reliable than the 3-RAM one, because a corrupted slice at the player's pointer would otherwise push the old card to 6.

4. **Data:** changes against the .tres:
- `ram_cost` 3 → 2.
- `cycle_cost` 75 → 105.
- `description` replaced.
- One added sub-resource: MODIFY_RESISTANCE (type 10, target 2, amount −2, ring_scope 2).
- `effects` array extended to two entries.
- No new system. Under N1, the amount mode is FLAT (the default).

5. **Q:**
- Q: Should a Hub breach survive a boss `hub_override` at a phase change (R6 covers statuses, not Hub state)? If not, the card should say "this phase" so players do not waste it.
- Q: Does MODIFY_RESISTANCE with a negative amount remove Hub-sourced and trait-sourced resistance equally, or only the active source?
