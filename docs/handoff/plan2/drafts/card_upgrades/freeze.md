<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__freeze; status ok; tokens in 5081 cache-write 0 cache-read 32585 out 1232; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: freeze

1. **Role**: A neutral, exhausting, 3-RAM tempo tool. It cancels one enemy respin, so the enemy wheel stays where the player last left it and the player's setup holds for the next turn.

2. **Upgraded card: Freeze+** (one level only; no Level II needed)
- **RAM cost:** 2 (was 3).
- **Cycle cost multiplier:** ×1.4 (75 → 105).
- **Text:** "Target wheel skips its next respin. Exhaust. If the target is an enemy, its next pointer resolution is still shown by the preview." This text is only flavor; the real rider is below.
- **Chosen rider (decisive):** "Target wheel skips its next respin and takes 1 free tick of its resistance (−1). Exhaust." Rider rationale: a cost cut alone is a pure improvement, and a status rider overlaps Blind Spot (Ghost) too much. So the choice is cost cut plus a small wider-target rider: when played with wheel_target ENEMY it also applies to all satellites docked on that wheel (they skip their respin too).
- **Final effect list:**
  1. FREEZE, target TARGET_WHEEL, ring_scope WHOLE_WHEEL, amount 0 (unchanged, matches the current type 9 / target 2 / ring_scope 2).
  2. FREEZE, target TARGET_WHEEL, ring_scope WHOLE_WHEEL, `wheel_target` SATELLITE, applied to every docked satellite of the chosen wheel.
- **exhaust:** true (kept). **wheel_target:** ANY (was ENEMY; ENEMY stays the default pick, ANY lets it hold your own wheel, e.g. to keep a Perfect through next turn).

Sidegrade justification: it is not strictly dominant, because ANY adds a real choice (hold your own setup vs freeze the enemy) and the exhaust is kept. The cost drop of 1 RAM is the main buff; the Cycle price rises to match.

3. **Interplay**
- **Variable slice sizes and uneven needles:** freezing keeps the enemy's tick-quality read stable, so a narrow 3-tick Perfect window you nudged around stays valid. This is strongest against R10 uneven needles.
- **Corruption as double RAM:** a corrupted slice costs 2× RAM only for cards played where your pointer reads it, so the 2-RAM cost can double to 4. Plan the order of play.
- **Satellites (R12):** fixed satellites rotate with the host, so freezing the host and its satellites together locks guards in place.

4. **Data**
- `ram_cost` 3 → 2; `cycle_cost` 75 → 105; `wheel_target` 1 (ENEMY) → 3 (ANY).
- Add a second EffectData (FREEZE aimed at docked satellites).
- New system: no N# required if FREEZE already accepts a satellite target through `WheelTarget.SATELLITE`. If it does not, the fallback is data-only: drop effect 2 and ship the cost cut plus ANY. NEW: freeze-satellite handling (S) if wanted.
- Add `id = &"freeze_plus"`, `display_name = "Freeze+"`, `description` as above.

5. **Q:**
- Q: Should Freeze+ on an enemy phase-change wheel survive the `_apply_wheel_override`, or should phase entry clear the freeze?
- Q: Is ANY target too permissive for a cheap exhaust card, or should it stay ENEMY with only the cost cut and the satellite rider?
