<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__feather_touch; status ok; tokens in 5116 cache-write 0 cache-read 32585 out 1130; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: feather_touch

1. **Role:** A free, precise ±1 nudge. It is the cheapest fine-tuning tool in the shared pool, and it fixes a WEAK or GOOD landing into a better one.

2. **Upgraded card: "Feather Touch+"** (one + level is enough; the card is too small for a second)
- RAM cost: 0 (unchanged).
- Cycle cost multiplier: ×1.5 (50 → 75), because the + version is a strict superset at the same RAM.
- Text: "One ±1 nudge. Then, if your pointer reads GOOD or WEAK, a second ±1 nudge on the same ring." (see "Do not dominate" below)
- Simpler fallback that needs no conditional: **"Two ±1 nudges on one ring. Exhaust."** This is just Micro-Adjust at 0 RAM, which makes it a different card, so I reject it.
- **Chosen version: "Feather Touch+": the nudge may be taken on either ring.**
  - Text: "One ±1 nudge on the outer ring OR the inner ring. Retain." The inner-ring choice and Retain are the sidegrade.
  - Retain is not an existing flag, so drop it. Final text: **"One ±1 nudge, and it refunds your free nudge: gain 1 free nudge this turn."**
- Effect list:
  1. NUDGE, target OWN_WHEEL (via `wheel_target` = ANY), amount 1, ring_scope OUTER, as today.
  2. CUSTOM-free rider: a free-nudge grant. Use the existing mechanic behind Torque Wrench and Calibrate ("gain a free nudge"). It is an EffectData of the Calibrate type, amount 1.
- Exhaust: false. `wheel_target`: ANY (2), unchanged.
- **Do not dominate:** the card nets a free nudge back, so it costs 0 RAM and no nudge budget. That is strong but capped: the free nudge only applies to later nudges this turn, and it doesn't draw or refund RAM. The sidegrade is that the base card has no card-slot cost either. The + version's cost is 25 more Cycles, and a free-nudge reserve is only worth it in decks that nudge often.

3. **Interplay:** a free nudge matters more under corruption as 2× RAM, since a nudge on a CORRUPTED slice costs double and the refund makes the next one free. On 4-tick slices (no Perfect) and uneven needles, one tick is often the whole fix, so the refund lets you retune both pointers.

4. **Data:** against the current .tres:
- add a second sub_resource `fx1` with the existing free-nudge EffectData (same type as Calibrate, amount 1);
- `effects = [fx0, fx1]`;
- `cycle_cost` 50 → 75;
- `description` updated.
- No new system. Name and id: `feather_touch_plus`, with the upgrade link on the card (an upgrade field is not yet in the schema, so NEW: card upgrade link).

5. **Q:** Is "free nudge" an EffectData type today, or only a Calibrate custom handler? If it is a handler, this card needs a CUSTOM effect.
Q: Should the + version be restricted to one use per turn to prevent chaining several copies into unlimited free nudges?
