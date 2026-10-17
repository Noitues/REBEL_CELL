<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__double_jam; status ok; tokens in 5140 cache-write 0 cache-read 32585 out 1222; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: double_jam

1. **Role**: A neutral, expensive (3 RAM) precision tool that moves an enemy needle by 2 ticks and ignores resistance. It is the answer to Compliance Lock and Weight, and it can turn an enemy Perfect into a WEAK landing or move a needle onto a Null slice.

2. **Upgraded card: "Double Jam+"** (one level, since a single + is enough)
- **RAM cost:** 3 → 2.
- **Cycle cost multiplier:** ×1.5 (70 → 105).
- **Text:** "Nudge an enemy wheel ±1 twice, ignoring resistance. The second nudge may go either direction, and may land on a different ring."
- **Rarity, exhaust and wheel_target:** unchanged (UNCOMMON, no exhaust, ENEMY).
- **Effect list** (both EffectData are NUDGE, target TARGET_WHEEL, amount 1, ring_scope OUTER, no status, duration 0):
  - fx0: NUDGE, TARGET_WHEEL, amount 1, ring_scope OUTER. This is the current effect, unchanged.
  - fx1: NUDGE, TARGET_WHEEL, amount 1, ring_scope INNER.
- **Why this is a sidegrade-leaning upgrade:**
  - The cost drop is the main gain. The extra ring is optional, so a player who wants both nudges on the outer ring still gets today's card.
  - It does not strictly dominate at the card level. On the outer ring it moves the needle 2 ticks, exactly as today, and it never moves it 3. A player who wants ±3 or more still needs Ghost Step, Tap Tap or a spin.
  - The gain is flexibility: the outer nudge fixes the action and the inner nudge fixes the modifier, so one card sets both.

3. **Interplay**
- **Sub-tick quality (R11):** with variable slice sizes the 2-tick nudge matters more. On a 4-tick enemy slice (W G G W) it turns GOOD into WEAK and never into Perfect, and on a 3-tick slice (G P G) it turns Perfect into GOOD.
- **Resistance:** it ignores resistance, so it still beats Compliance Lock. Unlike a spin, it does not trigger Compliance Lock's flip and respin block.
- **Inner ring:** it has no use on an enemy wheel without an inner ring, which is why the effect is optional-targeting data and not new behaviour. Per G1, enemy inner rings are rare, so the fx1 value depends on the inner ring redesign.

4. **Data**
- Changes to `double_jam.tres`:
  - `ram_cost` 3 → 2.
  - `cycle_cost` 70 → 105.
  - Add one `EffectData` sub_resource for fx1.
  - Update `description`.
- The effect list becomes `[fx0, fx1]`.
- No new system. This uses only existing NUDGE fields. If a "+" id is needed, add `double_jam_plus` as a separate `CardData` with `offered = false` until the upgrade pass wires it in.
- **Dependency:** the card-upgrade pass itself (NEW: card upgrade link field, e.g. `upgrade_id`).

5. **Q:**
- Q: Does the fx1 inner-ring nudge need a fallback when the target has no inner ring (refund 1 RAM, or fall back to the outer ring)?
- Q: Should the upgraded Cycle cost multiplier be one value for all cards (×1.5) or priced per card?
